"""Installer regression checks using disposable files only."""
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("manage", Path(__file__).with_name("manage.py"))
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)

class InstallerTests(unittest.TestCase):
    def test_config_preservation_and_idempotence(self):
        for original in (b"", b'model = "test-model"\n[agents]\ninterrupt_message = false\n[tui]\nfoo = true\n', b'[agents]\nenabled = true\n'):
            with self.subTest(original=original):
                merged = manage.config_text(original)
                self.assertEqual(manage.config_text(merged), merged)

    def test_legacy_markers_migrate(self):
        original = b'model = "test-model"\n[tui]\nfoo = true\n'
        legacy = manage.config_text(original).replace(b'ai-config', b'codex-config')
        migrated = manage.config_text(legacy)
        self.assertNotIn(b'codex-config', migrated)
        self.assertIn(b'# BEGIN ai-config root', migrated)
        self.assertEqual(manage.config_text(migrated), migrated)
        self.assertEqual(manage.tomllib.loads(migrated.decode())['tui'], {'foo': True})

    def test_claude_rule_preservation_and_idempotence(self):
        original = b'# Personal rules\nNever commit; the user runs Git commits.\n'
        merged = manage.claude_text(original)
        self.assertIn(original.rstrip(), merged)
        self.assertIn((manage.ROOT/'global/AGENTS.md').read_bytes().rstrip(), merged)
        self.assertEqual(manage.claude_text(merged), merged)
        self.assertEqual(merged.count(b'<!-- BEGIN shared-agent-setup -->'), 1)
        with self.assertRaises(ValueError):
            manage.claude_text(b'<!-- BEGIN shared-agent-setup -->')

    def test_claude_roles_and_skill_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            with patch.object(manage, 'CODEx', base/'codex'), patch.object(manage, 'CLAUDE', base/'custom-claude'), patch.object(manage, 'SHARED_SKILLS', base/'skills'):
                targets = manage.desired(None, b'Personal instructions\n')
                for name in ('frontend','backend','infra','qa','planner','reviewer'):
                    content = targets[manage.CLAUDE/'agents'/f'{name}.md'].decode()
                    self.assertTrue(content.startswith('---\nname: "'+name+'"\n'))
                    self.assertIn('model: inherit\n', content)
                    canonical = manage.tomllib.loads((manage.ROOT/'agents'/f'{name}.toml').read_text())
                    self.assertIn(canonical['developer_instructions'].strip(), content)
                for name in ('project-kickoff','change-verification'):
                    self.assertEqual(targets[manage.CLAUDE/'skills'/name/'SKILL.md'], targets[manage.SHARED_SKILLS/name/'SKILL.md'])
                self.assertIn(b'Personal instructions', targets[manage.CLAUDE/'CLAUDE.md'])
                for home in (manage.SHARED_SKILLS, manage.CLAUDE/'skills'):
                    pointer = json.loads(targets[home/'feedback-reflection/source.json'])
                    self.assertEqual(pointer, {'repository': str(manage.ROOT)})

    def test_claude_secret_rules_preserve_settings_and_are_idempotent(self):
        original = {
            'theme': 'dark',
            'permissions': {'allow': ['Bash(npm test)'], 'deny': ['Read(//private/**)']},
            'sandbox': {'enabled': False, 'allowUnsandboxedCommands': True,
                        'filesystem': {'allowRead': ['/workspace'], 'denyRead': ['/private']}},
        }
        merged = manage.claude_settings_text(json.dumps(original).encode())
        parsed = json.loads(merged)
        self.assertEqual(manage.claude_settings_text(merged), merged)
        self.assertEqual(parsed['theme'], original['theme'])
        self.assertEqual(parsed['permissions']['allow'], original['permissions']['allow'])
        self.assertEqual(parsed['permissions']['deny'][0], 'Read(//private/**)')
        self.assertIn('Read(//**/.env*)', parsed['permissions']['deny'])
        self.assertIn('Edit(//**/*.env)', parsed['permissions']['deny'])
        self.assertFalse(parsed['sandbox']['enabled'])
        self.assertTrue(parsed['sandbox']['allowUnsandboxedCommands'])
        self.assertEqual(parsed['sandbox']['filesystem']['allowRead'], ['/workspace'])
        self.assertEqual(parsed['sandbox']['filesystem']['denyRead'][0], '/private')
        self.assertIn('/**/.env*', parsed['sandbox']['filesystem']['denyRead'])
        fresh = json.loads(manage.claude_settings_text(None))
        self.assertNotIn('enabled', fresh['sandbox'])
        self.assertNotIn('allowUnsandboxedCommands', fresh['sandbox'])

    def test_claude_secret_rules_refuse_malformed_settings(self):
        for original in (b'{', b'[]', b'null', b'{"permissions": []}',
                         b'{"permissions": {"deny": "Read(*)"}}',
                         b'{"sandbox": {"filesystem": {"denyRead": [1]}}}',
                         b'{"sandbox": null}', b'{"sandbox": {"filesystem": []}}',
                         b'{"permissions": {}, "permissions": {}}'):
            with self.subTest(original=original), self.assertRaises(ValueError):
                manage.claude_settings_text(original)

    def test_claude_settings_target_restore_and_stale_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            with patch.object(manage, 'CODEx', base/'codex'), patch.object(manage, 'CLAUDE', base/'claude'), patch.object(manage, 'SHARED_SKILLS', base/'skills'):
                target = manage.CLAUDE/'settings.json'
                target.parent.mkdir()
                original = b'{"theme":"dark"}\n'
                target.write_bytes(original)
                desired = manage.desired(None, None, original)[target]
                manage.apply({target: desired}, {target: original})
                backup = next((manage.CODEx/'setup-backups').iterdir())
                manage.restore(backup)
                self.assertEqual(target.read_bytes(), original)
                target.write_bytes(b'{"theme":"light"}\n')
                with self.assertRaises(ValueError):
                    manage.apply({target: desired}, {target: original})
                self.assertEqual(target.read_bytes(), b'{"theme":"light"}\n')

    def test_selective_policy_install_preserves_unrelated_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            with patch.object(manage, 'CODEx', base/'codex'), patch.object(manage, 'CLAUDE', base/'claude'), patch.object(manage, 'SHARED_SKILLS', base/'skills'):
                manage.CODEx.mkdir()
                manage.CLAUDE.mkdir()
                config = manage.CODEx/'config.toml'
                settings = manage.CLAUDE/'settings.json'
                config.write_bytes(b'sandbox_mode = "read-only"\n')
                settings.write_bytes(b'{malformed but unrelated')
                with patch.object(sys, 'argv', ['manage.py', '--only', 'policy', '--apply']):
                    manage.main()
                self.assertEqual(config.read_bytes(), b'sandbox_mode = "read-only"\n')
                self.assertEqual(settings.read_bytes(), b'{malformed but unrelated')
                self.assertEqual((manage.CODEx/'AGENTS.md').read_bytes(), (manage.ROOT/'global/AGENTS.md').read_bytes())
                self.assertFalse((manage.CODEx/'agents').exists())
                self.assertFalse(manage.SHARED_SKILLS.exists())
                self.assertFalse((manage.CLAUDE/'skills').exists())
                with patch.object(sys, 'argv', ['manage.py', '--only', 'policy', '--check']):
                    manage.main()
                with patch.object(sys, 'argv', ['manage.py', '--only', 'secret-access', '--apply']), self.assertRaises(ValueError):
                    manage.main()
                self.assertEqual(settings.read_bytes(), b'{malformed but unrelated')

    def test_selective_install_targets(self):
        groups = {
            'policy': lambda path: path in (manage.CODEx/'AGENTS.md', manage.CLAUDE/'CLAUDE.md'),
            'roles': lambda path: path.parent in (manage.CODEx/'agents', manage.CLAUDE/'agents'),
            'skills': lambda path: path.is_relative_to(manage.SHARED_SKILLS) or path.is_relative_to(manage.CLAUDE/'skills'),
            'secret-access': lambda path: path == manage.CLAUDE/'settings.json',
        }
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            with patch.object(manage, 'CODEx', base/'codex'), patch.object(manage, 'CLAUDE', base/'claude'), patch.object(manage, 'SHARED_SKILLS', base/'skills'):
                for group, accepts in groups.items():
                    with self.subTest(group=group):
                        targets = manage.desired(b'invalid TOML', only=[group])
                        self.assertTrue(targets)
                        self.assertTrue(all(accepts(path) for path in targets))
                        self.assertNotIn(manage.CODEx/'config.toml', targets)

    def test_claude_restore_and_stale_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            with patch.object(manage, 'CODEx', base/'codex'), patch.object(manage, 'CLAUDE', base/'custom-claude'):
                target = manage.CLAUDE/'CLAUDE.md'
                target.parent.mkdir()
                target.write_bytes(b'personal')
                manage.apply({target: b'shared'}, {target: b'personal'})
                backup = next((manage.CODEx/'setup-backups').iterdir())
                manage.restore(backup)
                self.assertEqual(target.read_bytes(), b'personal')
                target.write_bytes(b'concurrent edit')
                with self.assertRaises(ValueError):
                    manage.apply({target: b'stale'}, {target: b'personal'})
                self.assertEqual(target.read_bytes(), b'concurrent edit')

    def test_unmanaged_conflicts_are_refused(self):
        with self.assertRaises(ValueError):
            manage.config_text(b'sandbox_mode = "read-only"\n')
        with self.assertRaises(ValueError):
            manage.config_text(b'[agents]\nmax_threads = 8\n')

    def test_restore_preserves_later_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(manage, "CODEx", (Path(directory)/".codex").resolve()):
                target = manage.CODEx / "AGENTS.md"
                target.parent.mkdir()
                target.write_bytes(b"original")
                new = manage.CODEx / "agents/new.toml"
                manage.apply({target: b"installed", new: b"new"})
                backup = next((manage.CODEx/"setup-backups").iterdir())
                target.write_bytes(b"user edit")
                with self.assertRaises(ValueError):
                    manage.restore(backup)
                self.assertTrue(new.exists())
                target.write_bytes(b"installed")
                manage.restore(backup)
                self.assertEqual(target.read_bytes(), b"original")
                self.assertFalse(new.exists())

    def test_install_refuses_stale_config_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(manage, "CODEx", (Path(directory)/".codex").resolve()):
                target = manage.CODEx / "config.toml"
                target.parent.mkdir()
                target.write_bytes(b"concurrent edit")
                with self.assertRaises(ValueError):
                    manage.apply({target: b"stale replacement"}, {target: b"original"})
                self.assertEqual(target.read_bytes(), b"concurrent edit")

if __name__ == "__main__":
    unittest.main()

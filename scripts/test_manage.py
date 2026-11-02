"""Installer regression checks using disposable files only."""
import importlib.util
from pathlib import Path
import tempfile
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

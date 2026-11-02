#!/usr/bin/env python3
"""Preview, install, check, or restore the shared Codex and Claude baseline. Python 3.11+."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CODEx = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).expanduser().resolve()
CLAUDE = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home() / '.claude'))).expanduser().resolve()
SHARED_SKILLS = Path.home() / '.agents/skills'

def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None

def current(path):
    if path.is_symlink():
        raise ValueError(f'Refusing to replace symlink: {path}')
    return path.read_bytes() if path.exists() else None

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(data)
    try:
        temp.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o600)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)

def config_text(original):
    # Root values and the agents table need distinct blocks to preserve TOML scope.
    body = original.decode() if original else ''
    for section in ('root', 'agents'):
        for marker in ('codex-config', 'ai-config'):
            body = re.sub(r'(?m)^# BEGIN '+marker+' '+section+r'\n.*?^# END '+marker+' '+section+r'\n?', '', body, flags=re.S)
    parsed = tomllib.loads(body)
    defaults = tomllib.loads((ROOT / 'config.defaults.toml').read_text())
    root_lines = []
    for key, value in defaults.items():
        if key == 'agents':
            continue
        if key in parsed and parsed[key] != value:
            raise ValueError(f'Existing unmanaged {key}; review before changing it.')
        if key not in parsed:
            root_lines.append(f'{key} = {json.dumps(value)}')
    agent_lines = []
    for key, value in defaults['agents'].items():
        existing = parsed.get('agents', {})
        if key == 'max_concurrent_threads_per_session' and 'max_threads' in existing:
            raise ValueError('Existing agents.max_threads alias requires manual review.')
        if key in existing and existing[key] != value:
            raise ValueError(f'Existing unmanaged agents.{key} requires manual review.')
        if key not in existing:
            agent_lines.append(f'{key} = {json.dumps(value)}')
    def block(section, lines):
        return '# BEGIN ai-config '+section+'\n'+'\n'.join(lines)+'\n# END ai-config '+section+'\n'
    if agent_lines:
        header = re.search(r'(?m)^\[agents\][ \t]*(?:#.*)?$', body)
        if header:
            point = header.end()
            body = body[:point]+'\n'+block('agents', agent_lines)+body[point:].lstrip('\n')
        elif 'agents' in parsed:
            raise ValueError('Inline or implicit agents table requires manual review.')
        else:
            body = body.rstrip()+'\n\n'+block('agents', ['[agents]']+agent_lines)
    if root_lines:
        body = block('root', root_lines)+'\n'+body.lstrip('\n')
    result = body.encode()
    final = tomllib.loads(body)
    for key, value in parsed.items():
        if key != 'agents' and final.get(key) != value:
            raise ValueError(f'Config preservation check failed: {key}')
    for key,value in parsed.get('agents', {}).items():
        if final['agents'].get(key) != value:
            raise ValueError(f'Agent config preservation failed: {key}')
    return result

def claude_text(original):
    """Preserve personal Claude instructions and replace only our marked block."""
    body = original.decode() if original else ''
    start = '<!-- BEGIN shared-agent-setup -->'
    end = '<!-- END shared-agent-setup -->'
    if body.count(start) != body.count(end) or body.count(start) > 1:
        raise ValueError('Malformed managed block in Claude instructions; review before changing it.')
    body = re.sub(re.escape(start)+r'.*?'+re.escape(end)+r'\n?', '', body, flags=re.S).rstrip()
    shared = (ROOT / 'global/AGENTS.md').read_text().rstrip()
    note = ('# Shared development baseline\n\n'
            'The shared baseline below applies alongside personal instructions above. '
            'Where existing personal rules are stricter, keep those restrictions.\n\n')
    return ((body+'\n\n' if body else '')+start+'\n'+note+shared+'\n'+end+'\n').encode()

def claude_settings_text(original):
    """Add environment-file denies without replacing personal permissions or sandbox mode."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate key in Claude settings; review before changing it.')
            result[key] = value
        return result

    try:
        settings = json.loads(original.decode(), object_pairs_hook=unique_object) if original else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError('Invalid Claude settings JSON; review before changing it.') from None
    if not isinstance(settings, dict):
        raise ValueError('Claude settings must be a JSON object.')

    def table(parent, key):
        value = parent.setdefault(key, {})
        if not isinstance(value, dict):
            raise ValueError(f'Claude settings {key} must be an object.')
        return value

    def append_rules(parent, key, rules):
        values = parent.setdefault(key, [])
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise ValueError(f'Claude settings {key} must be a list of strings.')
        for rule in rules:
            if rule not in values:
                values.append(rule)

    patterns = ('**/.env*', '**/*.env', '**/*.env.*')
    permissions = table(settings, 'permissions')
    append_rules(permissions, 'deny', [f'{tool}(//{pattern})' for tool in ('Read', 'Edit') for pattern in patterns])
    filesystem = table(table(settings, 'sandbox'), 'filesystem')
    append_rules(filesystem, 'denyRead', ['/'+pattern for pattern in patterns])
    return (json.dumps(settings, indent=2, ensure_ascii=False)+'\n').encode()

def claude_agent(data):
    """Convert the common role into Claude's native Markdown/frontmatter format."""
    # Provider-specific model IDs are intentionally not copied between clients.
    return ('---\nname: '+json.dumps(data['name'])+'\ndescription: '+json.dumps(data['description'])+
            '\nmodel: inherit\n---\n\n'+data['developer_instructions'].strip()+'\n').encode()

def desired(config_original, claude_original=None, claude_settings_original=None, only=None):
    selected = set(only) if only is not None else {'policy', 'roles', 'skills', 'secret-access'}
    if not selected <= {'policy', 'roles', 'skills', 'secret-access'}:
        raise ValueError('Unknown installation group.')
    override = CODEx / 'AGENTS.override.md'
    if override.exists() and override.read_text().strip():
        raise ValueError(f'Global override would hide these rules: {override}')
    result = {}
    if 'policy' in selected:
        result[CODEx / 'AGENTS.md'] = (ROOT / 'global/AGENTS.md').read_bytes()
        result[CLAUDE / 'CLAUDE.md'] = claude_text(claude_original)
    if 'secret-access' in selected:
        result[CLAUDE / 'settings.json'] = claude_settings_text(claude_settings_original)
    if 'roles' in selected:
        for source in (ROOT / 'agents').glob('*.toml'):
            data = tomllib.loads(source.read_text())
            assert data['name'] == source.stem
            assert data['description'] and data['developer_instructions']
            result[CODEx / 'agents' / source.name] = source.read_bytes()
            result[CLAUDE / 'agents' / (source.stem+'.md')] = claude_agent(data)
    if 'skills' in selected:
        for source in (ROOT / 'skills').rglob('*'):
            if source.is_file() and source.name != '.DS_Store':
                relative = source.relative_to(ROOT / 'skills')
                result[SHARED_SKILLS / relative] = source.read_bytes()
                # Codex UI metadata is harmless to Claude but not needed for skill discovery.
                if 'agents' not in relative.parts:
                    result[CLAUDE / 'skills' / relative] = source.read_bytes()
        if (ROOT / 'skills/feedback-reflection/SKILL.md').is_file():
            pointer = (json.dumps({'repository': str(ROOT)}, indent=2)+'\n').encode()
            for home in (SHARED_SKILLS, CLAUDE / 'skills'):
                result[home / 'feedback-reflection/source.json'] = pointer
    if only is None:
        result[CODEx / 'config.toml'] = config_text(config_original)
    return result

def apply(changes, originals=None):
    backup = CODEx / 'setup-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    entries = []
    for path, content in changes.items():
        old = originals[path] if originals is not None else current(path)
        entries.append({'path': str(path), 'before': base64.b64encode(old).decode() if old is not None else None,
                        'before_hash': digest(old), 'after_hash': digest(content)})
    backup.mkdir(parents=True, exist_ok=False)
    write(backup / 'manifest.json', (json.dumps(entries, indent=2)+'\n').encode())
    completed = []
    try:
        for entry in entries:
            path = Path(entry['path'])
            if digest(current(path)) != entry['before_hash']:
                raise ValueError(f'File changed during installation: {path}')
            write(path, changes[path])
            completed.append(entry)
    except Exception:
        for entry in reversed(completed):
            path = Path(entry['path'])
            if entry['before'] is None:
                path.unlink()
            else:
                write(path, base64.b64decode(entry['before']))
        raise
    print('Backup:', backup)

def restore(directory):
    directory = Path(directory).expanduser().resolve()
    directory.relative_to(CODEx / 'setup-backups')
    entries = json.loads((directory / 'manifest.json').read_text())
    for entry in entries:
        path = Path(entry['path'])
        if not any(path.is_relative_to(root) for root in (CODEx, CLAUDE, SHARED_SKILLS)):
            raise ValueError(f'Unexpected restore path: {path}')
        if digest(current(path)) != entry['after_hash']:
            raise ValueError(f'Changed since installation; will not overwrite: {path}')
    for entry in reversed(entries):
        path = Path(entry['path'])
        if entry['before'] is None:
            path.unlink()
        else:
            write(path, base64.b64decode(entry['before']))
    print('Restored', len(entries), 'files from', directory)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--check', action='store_true')
    group.add_argument('--restore', metavar='BACKUP_DIRECTORY')
    parser.add_argument('--only', nargs='+', choices=('policy', 'roles', 'skills', 'secret-access'),
                        help='Preview/install/check selected groups, preserving unrelated settings; excludes Codex config.')
    args = parser.parse_args()
    if args.restore and args.only:
        parser.error('--only cannot be combined with --restore')
    if args.restore:
        restore(args.restore)
        return
    config_path = CODEx / 'config.toml'
    config_original = current(config_path) if args.only is None else None
    claude_path = CLAUDE / 'CLAUDE.md'
    claude_original = current(claude_path) if args.only is None or 'policy' in args.only else None
    settings_path = CLAUDE / 'settings.json'
    settings_original = current(settings_path) if args.only is None or 'secret-access' in args.only else None
    targets = desired(config_original, claude_original, settings_original, only=args.only)
    snapshots = {config_path: config_original, claude_path: claude_original, settings_path: settings_original}
    originals = {path: snapshots[path] if path in snapshots else current(path) for path in targets}
    changes = {path: data for path, data in targets.items() if originals[path] != data}
    for path in changes:
        print('Would update:', path)
    if args.check:
        if changes:
            raise SystemExit('Installed setup differs from source.')
        print('Selected managed files match.' if args.only else 'All managed files match; TOML and config preservation checks passed.')
    elif args.apply and changes:
        apply(changes, originals)
        print('Installed', len(changes), 'files. Start fresh Codex and Claude sessions.')
    else:
        print(len(changes), 'files differ. Use --apply to install.' if changes else 'No changes needed.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, AssertionError) as error:
        raise SystemExit(str(error))

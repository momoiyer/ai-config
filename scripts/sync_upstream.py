#!/usr/bin/env python3
"""Install pinned upstream skills and copy verified entries to Claude with backups."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import manage

def main():
    sources=json.loads((manage.ROOT/'sources.json').read_text())['skills']
    installer=manage.CODEx/'skills/.system/skill-installer/scripts/install-skill-from-github.py'
    if not installer.exists():raise SystemExit('Codex bundled skill installer missing. Install Codex and its system skills first.')
    changes={};originals={}
    for source in sources:
        folder=manage.CODEx/'skills'/source['name']
        if not folder.exists():
            subprocess.run([sys.executable,str(installer),'--repo',source['repo'],'--ref',source['ref'],'--path',source['path']],check=True)
        entry=folder/'SKILL.md';expected=source.get('sha256')
        if entry.is_symlink() or not entry.is_file():
            raise SystemExit(f'{entry} must be a regular reviewed file; refusing a symlink or missing entry.')
        if not expected or hashlib.sha256(entry.read_bytes()).hexdigest()!=expected:
            raise SystemExit(f'{entry} differs from the reviewed revision; review before copying.')
        # These two selected skills are instruction-only, with an optional license file.
        for name in ('SKILL.md','LICENSE.txt'):
            path=folder/name
            if path.is_file() and not path.is_symlink():
                target=manage.CLAUDE/'skills'/source['name']/name
                originals[target]=manage.current(target)
                if originals[target]!=path.read_bytes():changes[target]=path.read_bytes()
    if changes:manage.apply(changes,originals)
    print('Both clients have the selected pinned upstream skills. Start fresh sessions.')

if __name__=='__main__':main()

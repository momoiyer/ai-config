"""Portable setup edge cases; no installed files or live services are changed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sync_upstream

class PortabilityTests(unittest.TestCase):
    def test_upstream_symlink_entry_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);codex=root/"codex";installer=codex/"skills/.system/skill-installer/scripts/install-skill-from-github.py"
            installer.parent.mkdir(parents=True);installer.write_text("")
            source={"name":"example","repo":"owner/repo","ref":"revision","path":"skills/example","sha256":"ignored"}
            (root/"sources.json").write_text(json.dumps({"skills":[source]}))
            folder=codex/"skills/example";folder.mkdir();(root/"entry.md").write_text("test");(folder/"SKILL.md").symlink_to(root/"entry.md")
            with patch.object(sync_upstream.manage,"ROOT",root),patch.object(sync_upstream.manage,"CODEx",codex),patch.object(sync_upstream.manage,"apply") as apply:
                with self.assertRaises(SystemExit):sync_upstream.main()
                apply.assert_not_called()

if __name__=="__main__":unittest.main()

# AI Config repository

This project owns shared development policy, agent roles, skills, and native Codex/Claude installation. Read README.md and docs/USAGE.md. Activity tracking is a separate project, orca-agent-tracker; do not add dashboard, telemetry, hooks, or login-service code here.

- Canonical policy: global/AGENTS.md. Canonical roles: agents/*.toml. Generate native client files with scripts/manage.py instead of maintaining duplicated role instructions.
- Python 3.11+ and standard library only. Run python3 -m unittest discover -s scripts -p 'test_*.py' for installer changes.
- Preview installers before activation. Preserve user settings, original snapshots, backup/restore behavior, and client-specific formats.
- Never add authentication, personal client settings, backups, local activity, or real project/task metadata to Git.
- Keep instructions short, stack-neutral, and task-specific. Add a new skill only for a demonstrated recurring workflow; review upstream instructions and pin versions before installation.
- Document supported clients and verification limits. Instructions guide behavior; tests, CI, permissions, and review provide independent checks.

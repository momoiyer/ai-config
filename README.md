# AI Config

Portable development rules, specialist agents, and focused skills for **Codex and Claude Code**. One shared source, installed in each client's native format. This repository configures how agents work; the separate **orca-agent-tracker** project observes their activity.

## What you get

- A shared working policy: investigate before assuming, clarify consequential decisions, complete authorized local work, verify outcomes, and report evidence honestly.
- Six specialist roles: frontend, backend, infrastructure, QA, planner, and reviewer. Models inherit the parent session rather than copying incompatible model IDs between providers.
- Three local workflows: project-kickoff (including suitable new-repository CI), change-verification, and feedback-reflection for reusable corrections across projects.
- Two reviewed upstream skills: Anthropic frontend-design and Vercel web-design-guidelines, with pinned revisions and entry checksums.
- A reversible installer that preserves unrelated client configuration and existing Claude personal rules.

## Install on another laptop

Install and authenticate Codex and Claude Code normally. Use **Python 3.11 or newer**. This Mac's compatible interpreter is `/opt/homebrew/bin/python3.13`; its system `python3` may be older. The installers use the Python standard library and no extra packages.

Clone this repository, enter its directory, and run:

```sh
python3 --version
python3 scripts/manage.py
python3 scripts/manage.py --apply
python3 scripts/sync_upstream.py
python3 scripts/manage.py --check
```

The first installer command is a preview. `sync_upstream.py` needs network access and Codex's bundled skill installer. It installs the exact revisions in `sources.json`, rejects a mismatched existing entry, and copies the selected skills to Claude. Existing skill folders are not silently replaced. Start **new sessions in both clients** after installation.

Orca is optional: these rules work when you launch either CLI directly or through Orca using the same client home. AI Config does not install tracking hooks or a background service. Install orca-agent-tracker separately if wanted; that project's README owns its setup and handoff.

## Installed locations

| Source | Codex | Claude Code |
|---|---|---|
| `global/AGENTS.md` | `~/.codex/AGENTS.md` | Marked block in `~/.claude/CLAUDE.md` |
| `agents/*.toml` | `~/.codex/agents/*.toml` | Generated `~/.claude/agents/*.md` |
| Local `skills/` | `~/.agents/skills/` | `~/.claude/skills/` |
| Selected upstream skills | `~/.codex/skills/` | `~/.claude/skills/` |
| Generated secret-file deny rules | No legacy-sandbox read deny; see access limits below | Additive rules in `~/.claude/settings.json` |
| `config.defaults.toml` | Managed blocks in `~/.codex/config.toml` | No direct TOML translation |

`CODEX_HOME` and `CLAUDE_CONFIG_DIR` override the client-home defaults. Local shared Codex skills use `~/.agents/skills`. Existing global Codex `AGENTS.override.md` stops installation because it would hide the shared policy. Repository instructions can add more specific requirements. Claude personal text outside our block remains intact; review conflicting or stricter personal rules deliberately.

Codex defaults use workspace-write, on-request approvals, live web search, and up to three concurrent subagents. Claude preserves existing permission and sandbox settings while adding environment-file deny lists. Equivalent working guidance does **not** mean the clients have identical permission systems. No cloud-provider credentials, paid integrations, or provider-specific stack assumptions are added.

## Everyday use

Describe the desired outcome, constraints, and what a successful result looks like. You do not need to assign every role manually. Relevant skills and bounded delegation are selected when useful; simple work stays with the main agent.

- New repository: use `$project-kickoff` in Codex or `/project-kickoff` in Claude.
- Feature: state the user flow and acceptance criteria; let the agent inspect existing patterns.
- Bug: provide the observed failure and reproduction details; expect a cause, fix, and relevant regression evidence.
- QA handoff: use `$change-verification` or `/change-verification` and name the behavior to verify.
- Review: ask for reviewer on a specific diff, with concrete correctness/security findings.

[The usage guide](docs/USAGE.md) explains planning, agent selection, project onboarding, frontend/backend/infra validation, Git boundaries, maintenance, and troubleshooting.

## Verify and maintain

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/manage.py --check
```

Tests use temporary fixtures. The check detects changes to installed managed files; it does not prove future model behavior. Validated user feedback authorizes narrow automatic local maintenance of this repository through feedback-reflection. Review the diff, run relevant checks, preview, and install only affected managed files with backups. Commits and publishing stay with the user. Do not blindly sync upstream skills or overwrite unrelated configuration drift.

To preview only policies, roles, skills, and Claude secret-access rules while preserving unrelated Codex settings drift:

```sh
python3 scripts/manage.py --only policy roles skills secret-access
```

Add `--apply` after reviewing every listed difference. Select only relevant groups for a narrow correction; a group selector includes all targets in that group, so defer activation if unrelated changes appear. Full `--check` still reports any unrelated settings drift.

Each apply creates a private backup manifest under the selected Codex home's `setup-backups/`. Restore a printed backup directory with:

```sh
python3 scripts/manage.py --restore BACKUP_DIRECTORY
```

Restore refuses to overwrite files changed after installation. Restore dependent installs in reverse order. Copied Claude upstream files are backed up by sync; downloaded Codex upstream folders are separate and are not removed by restore. Authentication, personal activity, and unrelated settings are not part of this repository.

## Privacy and feedback limits

Agents must never read environment files, including examples or variants, or expose private local data through tools, Git, or shared feedback. Ignore rules and instructions are not access control. The installer adds Claude file-tool and sandbox deny lists, preserving sandbox enablement; the legacy Codex sandbox still permits reads. For enforced no-access, use a secret-free isolated workspace or separately validated native restrictions. See [secret access boundaries](docs/SECRET-ACCESS.md) for exact controls, opt-in migration, and verification limits. No actual environment files are read for validation.

feedback-reflection receives current-session feedback or explicitly supplied safe evidence. It updates canonical rules/roles/skills when the source checkout is available and writable. A generated `source.json` alongside the installed skill points to that local checkout; it is machine-local metadata, not committed activity. It does not watch other projects, read transcripts, run in the background, or bypass filesystem permissions. Start fresh client sessions after activation.

## Project-specific guidance

Use `templates/AGENTS.md` as a starting outline for verified setup/test commands, architectural boundaries, and known pitfalls. Preserve existing project instructions. `templates/CLAUDE.md` imports the project AGENTS.md where a Claude wrapper is needed. Never fill templates with invented commands or automatically overwrite another project's guidance.

## Supported clients and limits

Validated with Codex CLI 0.166.0 and Claude Code 2.1.316 on macOS. Tests also exercise portable installer behavior; new client releases can require revalidation. Hosted sessions, different client homes, other coding tools, and other laptops require separate provisioning. This setup currently installs for Codex and Claude, not every possible AI application.

Persistent instructions improve consistency but cannot guarantee correctness, automatic skill selection, or flawless agreement across models. Keep meaningful tests, repository CI, scoped permissions, and human review for consequential changes.

## GitHub and separation

Publish this directory as `ai-config`, and publish the sibling tracker directory as `orca-agent-tracker`, each with its own Git history and remote. Neither requires the other's checkout. Do not publish personal settings, credentials, activity databases, logs, or backups.

On the original laptop, `codex-config` remains a compatibility symlink to this directory for older sessions; it is not part of the portable repository. The tracker service and hooks now belong to the tracker checkout. This chat's ongoing focus is the shared AI setup; tracker work continues independently.

## Sources and selection

[Codex global guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), and [native agents](https://learn.chatgpt.com/docs/agent-configuration/subagents); [Claude memory](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills), and [subagents](https://code.claude.com/docs/en/sub-agents) document the supported formats.

Selected upstream skills come from [Anthropic](https://github.com/anthropics/skills) and [Vercel](https://github.com/vercel-labs/agent-skills). [Superpowers](https://github.com/obra/superpowers) was reviewed but not installed because its mandatory process is more prescriptive than this baseline. The old [OpenAI skills catalog](https://github.com/openai/skills) is deprecated in favor of plugins. Add stack-specific skills after identifying an actual need and inspecting their sources.

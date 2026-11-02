# Secret-file access boundaries

Agents must never read environment files, including `.env`, `.env.*`, `.envrc`, and names such as `service.env`. Do not open, source, search, copy, or upload them through a shell, file tool, hook, MCP server, browser, or delegated agent. Use documented variable names and synthetic values in a differently named example file. Never dump the process environment or credentials when diagnosing configuration.

Instructions and `.gitignore` do not enforce a filesystem boundary. The strongest portable option is a secret-free workspace: keep real secrets outside the agent process and unmounted from its container or separate OS identity. Do not pass credential-bearing environment variables to that process. Git ignores do not remove files already tracked; stop publication if sensitive paths are tracked and have the user handle rotation and any history cleanup without printing their contents.

## Selective installation

Preview a focused update without modifying or parsing unrelated Codex settings:

```sh
python3 scripts/manage.py --only policy roles skills secret-access
python3 scripts/manage.py --only policy roles skills secret-access --apply
python3 scripts/manage.py --only policy roles skills secret-access --check
```

Select only the groups required; `secret-access` merges Claude deny lists, `policy` updates shared instructions, `roles` updates native agents, and `skills` includes generated source-location pointers. Every selective run excludes Codex `config.toml`. Omitting `--only` retains the full installation behavior. Restore uses the printed private backup directory and cannot be combined with `--only`.

## Installed Claude protection

The installer adds absolute `Read` and `Edit` deny rules for `//**/.env*`, `//**/*.env`, and `//**/*.env.*` to the selected Claude home's `settings.json`. It also adds corresponding absolute `sandbox.filesystem.denyRead` patterns. It preserves existing permission lists, sandbox enablement, retry policy, and unrelated settings; invalid JSON or settings shapes stop installation. The normal private backup, stale-snapshot protection, and restore apply to this file.

These are complementary controls. File-tool denies do not reliably constrain arbitrary subprocesses. Sandbox deny-read entries apply only to sandboxed commands with filesystem isolation enabled; they do not activate the sandbox. Unsandboxed retries, excluded commands, a disabled filesystem layer, more specific allow rules, hooks, MCP servers, IDE context, and external tools can have separate access. Check the effective settings and sandbox status in a fresh client. This installer does not promise an enforced boundary for every tool or install ad hoc command-matching hooks.

For stronger shell isolation, review enabling the sandbox with `failIfUnavailable: true` and `allowUnsandboxedCommands: false`, removing excluded commands and conflicting read allowances. These change runtime behavior and platform requirements; the installer does not silently enable them. Native Windows needs a supported isolation environment such as WSL2. See [Claude permission rules](https://code.claude.com/docs/en/permissions) and [sandbox scope and limitations](https://code.claude.com/docs/en/sandboxing).

## Codex: explicit migration required

The existing Codex baseline uses `sandbox_mode = "workspace-write"`. It permits reads and does not itself block environment files. Current [Codex permissions documentation](https://learn.chatgpt.com/docs/permissions) describes beta named profiles with deny-read rules. The installer does not automatically replace the existing sandbox configuration with that beta mechanism.

After verifying installed-client support, a candidate configuration for a separate migration is:

```toml
default_permissions = "ai-config-project"

[permissions.ai-config-project]
extends = ":workspace"

[permissions.ai-config-project.filesystem]
glob_scan_max_depth = 12

[permissions.ai-config-project.filesystem.":workspace_roots"]
"**/.env*" = "deny"
"**/*.env" = "deny"
"**/*.env.*" = "deny"
```

Remove legacy `sandbox_mode` and `sandbox_workspace_write` settings from every loaded config layer and selected profile before selecting the new mechanism; passing `--sandbox` also selects the old mechanism. Do not paste this into the existing managed block: prepare a reviewed installer migration instead, or the next apply will restore the legacy default. Preserve unrelated client settings and administrator requirements. These workspace-relative rules do not protect secrets outside the effective workspace roots.

On Linux, WSL, and applicable native Windows sandboxes, glob matches are expanded when each sandboxed process starts and bounded by the scan depth. Files created afterward or beyond the bound may remain accessible to that process. Exact denied secret directories or a secret-free isolated workspace provide a clearer boundary. An escalated command can also run outside the normal sandbox. Client settings are not proof of enforcement.

## Verify without exposing real secrets

The user or a separate security test harness should verify a fresh client against disposable fixtures only. Agents must not test by reading existing secret files.

1. Create an isolated temporary workspace with a harmless source file and synthetic environment-file fixtures at the root and in nested directories. Include `.env`, `.env.local`, `.envrc`, `service.env`, and `service.env.local`; use only a recognizable non-secret marker.
2. Confirm ordinary source reads still work. Exercise each intended access surface against the fixtures: native file tools and sandboxed shell subprocesses. Check that denied reads fail without returning the marker. Include absolute paths, a symlink alias, and a file created after a long-running process starts.
3. Check the effective sandbox/profile and any excluded, escalated, hook, IDE, or MCP access separately. A tool denial alone does not establish shell isolation. Never accept an unsandboxed retry as verification.
4. Record client/platform versions, the cases tested, failures, and unresolved surfaces. If any intended secret path is readable, use a secret-free workspace until the boundary is corrected.

Repository unit tests validate safe settings merging and restoration using synthetic JSON only. They do not exercise live client enforcement, access real environment files, or prove that future sessions cannot expose secrets.

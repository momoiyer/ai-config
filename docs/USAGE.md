# Working with your AI setup

## Start with the outcome

A useful task brief contains the problem, observable success criteria, constraints, and relevant evidence. Add a design reference, failing command, issue description, or example request where it matters. You do not need to restate the shared working rules.

Example: “Fix the checkout failure when the cart contains a discounted item. Preserve the existing API response. Reproduce the failure, add a regression check, and validate the checkout flow.”

For a substantial feature, ask for acceptance criteria and a short plan. Ask for an approval gate before implementation when you want one; ordinary reversible implementation and testing otherwise proceed within scope. Clarify business rules, cost, security, and irreversible choices rather than guessing them.

## What each role does

| Role | Best use | Expected output |
|---|---|---|
| Planner | Ambiguous requirements or multi-stage delivery | Acceptance criteria, smallest useful slice, dependencies, risks |
| Frontend | UI implementation and interaction | Existing design-system conventions, accessible states, browser evidence |
| Backend | APIs, data, jobs, integrations | Contract changes, authorization/error-path checks, migration concerns |
| Infra | Containers, CI/CD, deployment configuration | Validation and plan/diff, impact, permissions, rollback |
| QA | Reproduction and behavior validation | Exact steps/commands, observed results, defects, untested areas |
| Reviewer | Independent diff review | Evidence-backed risks with file references and consequences |

A role definition is a capability, not an always-running worker. The main agent coordinates and remains accountable. Use one or two independent specialists where useful. Avoid several agents editing the same files; use disjoint ownership or isolated workspaces. An agent review supports, but does not replace, executable tests.

## Skills versus rules versus agents

- Global rules express durable preferences across projects.
- Project AGENTS.md/CLAUDE.md records repository facts and more specific constraints.
- Skills provide reusable task workflows, loaded when relevant.
- Agents provide bounded contexts and responsibilities for delegated work.

Use project-kickoff for unfamiliar repositories or substantial features. Use change-verification for material changes and QA. Use frontend-design when a new visual direction is needed; preserve established design systems. Use web-design-guidelines for a requested UI/accessibility review. The latter fetches current guidelines, so its pinned skill file does not freeze the remotely fetched document.

Do not load every skill or launch every role for every task. If a skill misfires repeatedly, narrow its description or remove it after reviewing the failure. New skills should solve a demonstrated recurring need. Inspect executable content and dependencies before installing anything globally.

## Onboard a project once

Ask the agent to inspect the relevant manifests, CI, existing instructions, and architectural boundaries. Have it record verified run/test commands and project-specific pitfalls in the existing instruction file when you request onboarding. Keep personal preferences in this repository. Keep changing architecture details in repository-native docs and link to them.

A reasonable project guide names the package manager, development command, affected test commands, required CI checks, important module/API boundaries, generated files, and any migration/deployment procedure that is actually known. Unknown commands remain unverified. Do not create a large planning-document tree for a small change.

## Verification by domain

For frontend work, check the running journey, relevant loading/error/empty states, keyboard focus, and narrow screens. Screenshots support visual review; assertions establish behavior. Prefer the repository's browser framework and condition-based waits.

For backend work, check the changed contract, validation, authorization and tenant isolation, error behavior, integration boundaries, and transaction/idempotency risks where relevant. Use disposable fixtures and safe local test services.

For infrastructure, identify the target environment and state backend, validate configuration, and review the plan/diff. Check privilege, exposure, cost, availability, and rollback implications. Preparing a plan does not authorize an apply or production deployment.

For bugs, establish a reproduction or concrete evidence, trace the cause, and add meaningful regression coverage where practical. Do not weaken tests or accept repeated speculative patches as proof of a fix.

At handoff, expect what changed and why, the checks that actually ran and their results, remaining blockers, and unverified behavior. A proposed check is not a passing check. Investigate unrelated failures separately instead of silently ignoring them or expanding the task without reason.

## Autonomy and Git

Routine reversible local investigation, edits, and relevant tests are authorized by a development task. Production deployment, destructive data changes, infrastructure applies, paid resources, publishing, and external messages need authorization for that action.

Your current preference is that you perform Git commits, pushes, merges, and PR creation. Agents may stage and prepare copy-paste-ready commands. To make an exception for a specific task, authorize it explicitly in that conversation. Do not enable blanket permission bypasses to reduce ordinary prompts.

Use a task branch for features/fixes without discarding unfinished work or automatically pulling just to create a branch. Branch and workspace ownership matter when several agents work simultaneously. Expect a timely branch reminder for new independent work and a commit reminder when a coherent milestone passes its checks.

Agents prepare logical commit groups with exact paths and ready-to-use messages, plus a PR title and description with the problem, behavior, actual validation, and risks. You run the commits, pushes, merges, and PR creation. Each PR should deliver one reviewable outcome. Agents watch scope during the work and recommend independently testable PRs before a diff grows into hundreds of files, starting around 100 changed files; dependent PRs need an explicit order and base. File count is a warning signal, not a substitute for judging review effort. Also flag commits approaching 100 files; do not make one commit per file. Keep changes grouped by purpose with related tests. Follow repository conventions, using a short imperative subject and a rationale body when useful; Conventional Commits is optional unless already required. See [Git contributor guidance](https://git-scm.com/docs/SubmittingPatches) for the rationale, not universal Git syntax requirements.

## PR descriptions

Use **Summary**, **Changes**, **Tests**, and **Notes** as the default structure, respecting an existing repository template. Summary gives the problem or need, motivation, and resulting behaviour in 1–3 sentences. Changes uses short bullets grouped by purpose and explains important decisions. Tests records actual commands/results, relevant manual checks, and unverified areas. Notes contains meaningful limitations, risks, migrations, dependencies, or reviewer focus; use `None` when there are no relevant notes.

Keep the description useful without making it a process document: no exhaustive file inventory, duplicated roadmap, empty boilerplate, or unsupported claims that configured tests/CI passed. A docs-only PR can simply name the documentation review/checks. Update the text when the final scope changes. Repository-specific details stay in the project, not the shared policy.

This format follows the context and rationale principles in [GitHub's review guidance](https://docs.github.com/en/pull-requests/concepts/helping-others-review-your-changes) and [Google's change-description guidance](https://google.github.io/eng-practices/review/developer/cl-descriptions.html). The four section names are our default, not a universal requirement from those sources.

## Reflection and preferences

At task start, agents review available preferences, project standards, and relevant corrections. Before handoff and after feedback, they check alignment and apply useful adjustments. Delegated agents receive the same expectations. Reflection stays brief and practical; agents cannot claim to remember sessions they cannot access. Explicit durable preferences belong in the shared policy, verified repository standards in the project guide, and uncertain inferences need confirmation before becoming persistent rules.

Use `$feedback-reflection` in Codex or `/feedback-reflection` in Claude when a correction should improve future work. Agents should also select it after meaningful feedback. Validated reusable feedback authorizes a minimal automatic local update to this repository and targeted backed-up activation; agents still respect permissions, preserve concurrent work, and leave commits and publishing to you. Its installed `source.json` supplies the local checkout location. If the checkout is missing, read-only, or conflicting, expect a specific blocker and proposed correction, not a claim that the update was saved. No background monitoring or conversation collection is installed.

Each role now has guidance for task-specific skills and official-source research. Prefer independent agents when work can proceed in parallel; this works with native subagents and does not require Orca. Orca is useful when separate client workspaces or another client are needed. Avoid parallel edits to shared files. Consider a security/privacy specialist for recurring security reviews; extend the existing infra role for CI instead of adding an overlapping release role. Repeated procedures normally become skills, while small deterministic lifecycle checks can become reviewed hooks.

## Private files and new repositories

Never ask an agent to inspect an environment file, including `.env.example`, or dump secret values. Use a separately named sanitized schema for variable names and synthetic examples. Agents inspect safe filenames and selected diffs, add relevant ignores early, and flag tracked sensitive paths without opening them. `.gitignore` does not untrack files or remove history. [Secret-file access boundaries](SECRET-ACCESS.md) describes installed Claude deny lists, the remaining Codex legacy-sandbox gap, and stronger isolation options. No real secret file was accessed to test these changes.

When creating a suitable GitHub repository, project-kickoff uses its repository-baseline reference to add verified tests/build checks and applicable Dependabot configuration. CI uses read-only permissions, immutable action pins, timeouts and cancellation; no default deploy, release, or auto-merge. Dependency review and CodeQL depend on stack and eligibility. Secret scanning, push protection and branch rules need separate remote activation; a configuration file is not evidence that they are active. This repository demonstrates the small CI/Dependabot baseline; hosted runs still require a push by you.

## Keep longer work grounded

For work spanning sessions, preserve a compact progress record where useful: goal, acceptance criteria, relevant decisions, completed changes, evidence, next steps, and blockers. Avoid duplicating the same facts across multiple files. When changing requirements, update the current plan rather than piling on contradictory amendments.

A new session should read relevant project guidance and current state. Review agents' final evidence, not only their confidence or agreement. Challenge a bad assumption once with evidence, then reassess when corrected.

## Troubleshooting

- Rules seem absent: start a fresh session, check client-home environment overrides, and run manage.py --check. A Codex AGENTS.override.md can hide the normal global file.
- Claude behaves differently: review its preserved personal instructions and project guidance. Matching shared policy does not make client tools or permission behavior identical.
- Skills/roles are missing: verify native installation paths in README, check supported client versions, and start a new session. Claude uses Markdown role files; Codex uses TOML.
- The installer refuses a setting or skill: inspect the conflicting value/revision and decide which behavior you want. Do not silently overwrite it.
- The AI keeps asking for the same fact: put a stable preference here or a verified repository fact in that project's guide. Do not store secrets in instructions or memory.
- Tracking is missing: consult the separate orca-agent-tracker README. AI Config does not collect activity or run a dashboard.

## Add another coding tool

The shared policy and role descriptions are reusable source material, but only Codex and Claude currently have implemented installers. Verify the new tool's documented instruction/skill/agent formats, create a native adapter with backup and restore, test discovery, and document its permission differences. Do not copy provider-specific model IDs or claim support before validation.

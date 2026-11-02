---
name: project-kickoff
description: Bootstrap working context for an unfamiliar repository or plan a substantial new feature. Skip for small, understood edits.
---

Inspect applicable instructions, repository status, relevant manifests, CI, and architecture near the task. Establish the actual stack, package manager, run/test commands, and existing contracts without scanning the whole repository by default.

For a new feature, define observable acceptance criteria, constraints, and the smallest useful delivery slice. Separate facts from assumptions. Ask the user only about consequential unresolved choices; keep independent investigation moving.

Choose relevant skills and bounded agent work. Delegate independent investigation or focused review when useful, with concrete questions and file ownership. Keep implementation steps that depend on each other sequential.

For an unfamiliar repository, propose only verified project-specific instructions: setup/run/test commands, important boundaries, and known pitfalls. When the user asks to onboard or initialize project guidance, create or update AGENTS.md without overwriting existing rules. Otherwise report the findings in chat. Do not create generic planning artifacts unless useful for long work or requested. Use the repository's issue tracker only when requested and connected; do not claim tickets exist from a chat plan.

For multi-session work, keep a short repository-native progress record when justified: goal, acceptance criteria, completed work, evidence, next steps, and open decisions. Record important decisions once rather than duplicating them across documents.

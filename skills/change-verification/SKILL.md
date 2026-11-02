---
name: change-verification
description: Validate a material code or infrastructure change before handoff, or perform an explicitly requested QA or release-readiness check.
---

Derive the checks from the acceptance criteria, changed paths, and repository CI. State the likely failure modes and choose evidence that can detect them. Reuse existing tools and test environments. Do not introduce a new test framework solely to perform this check.

- UI: exercise the changed journey, relevant states, keyboard/focus, and narrow viewport; inspect console/network errors when relevant. Use semantic locators, auto-waiting assertions, and explicit readiness signals. Do not use arbitrary sleeps or networkidle as universal readiness. Capture screenshots for visual issues; test functionality with assertions.
- Backend: verify the changed contract and relevant validation, authorization/tenant isolation, error paths, integration boundaries, transactions, and idempotency.
- Infrastructure: validate configuration and inspect the target environment and proposed plan/diff. Identify state, privilege, availability, cost, and rollback implications. Applying changes requires authorization for that action.

Run focused checks, fix task-caused failures, then run required broader checks. Investigate existing failures before attributing them. Do not silently skip failures, replace behavioral assertions with snapshots, or weaken checks to get a green result.

For risky or cross-cutting changes, delegate a bounded independent review. Give the reviewer acceptance criteria and the actual diff; reconcile findings against evidence. If delegation is unavailable, do the review directly and disclose the limitation when it matters.

Inspect the final diff for scope and accidental files. Report what was checked, exact commands and outcomes, observed defects, blockers, and unverified areas. Separate ready for review from ready for production. A checklist, agent approval, or proposed test is not proof that the test ran.

Before handoff, review tracked/staged filenames and only safe explicit content paths; never read secret files or environment values. Verify relevant ignore rules without opening the ignored files. Check commit/PR grouping against review effort and report any sensitive tracked paths without their contents. Distinguish local configuration from remotely enabled CI or security controls. Feed validated reusable corrections into feedback-reflection rather than exporting project evidence.

# Skills and automation review

Reviewed 2026-11-02 against official source entries and the [skills.sh directory](https://skills.sh/). Popularity aids discovery but does not establish correctness or safety. These are recommendations, not new installations; recheck source, license, helper scripts, supported tool versions, immutable revision, and checksums before adding anything to sources.json.

| Candidate | Fit and decision |
|---|---|
| [Vercel React best practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) | Official React/Next performance guidance; entry reviewed. Strong next candidate for recurring React/Next work, unnecessary in stack-neutral projects. Review referenced rules and pin before installation. |
| [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Official Playwright workflow; entry reviewed. Do not install unchanged: blanket network-idle waits and running helpers before reading their source conflict with our verification/supply-chain preferences. Helpers still require review. |
| [Microsoft playwright-cli](https://github.com/microsoft/playwright-cli) | Evaluate if existing browser tools are insufficient. Source repository identified; executable content not reviewed or approved for installation. |
| Existing frontend-design / web-design-guidelines | Already pinned and installed; preserve their narrow purpose instead of adding a duplicate broad frontend bundle. |

Do not install every popular skill or auto-upgrade pinned sources. Recommend a current stable proven tool when a task demonstrates a gap, explain compatibility and maintenance implications, and research unfamiliar/changing details using primary documentation.

For additional roles, a bounded security/privacy reviewer is the clearest candidate if security reviews recur. Infra already owns CI; QA already owns behavior verification. Start with task-specific assignments before multiplying permanent roles. A reflection procedure belongs in a skill, not a background agent with unrestricted cross-project access.

## GitHub baseline rationale

[GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use) supports limited token permissions and immutable action pins. Official stable releases resolved during this review: checkout v7.0.1 (`3d3c42e5aac5ba805825da76410c181273ba90b1`) and setup-python v7.1.0 (`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`). Local CI now uses these pins, a timeout, cancellation, and existing unit tests. Hosted execution has not been observed here.

[Dependabot](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates) can maintain GitHub Actions pins. This standard-library-only repository needs the github-actions ecosystem, not an invented Python dependency manifest. Weekly scheduling and three open PRs are local noise-control choices.

[Dependency review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review) and CodeQL require suitability and eligibility checks. [Secret scanning and push protection](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository) are remote settings with availability limits; local YAML does not enable them. [Git ignores](https://git-scm.com/docs/gitignore) affect untracked files, not existing history. Do not promise scanners catch all sensitive local data.

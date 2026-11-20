---
name: es-release
description: "DTC engineering standards, part es-release: dependencies, CHANGELOG, repo hygiene, git. Preloaded by the team agents that need it. Use when designing, coding, testing or reviewing DTC Java/Spring Boot service code."
---

# Engineering standards: dependencies, CHANGELOG, repo hygiene, git

Part of the engineering standards, split by role (skills `es-core`, `es-code`, `es-config`, `es-release`, `es-tests`). Each agent loads only the parts it needs.

## Dependencies

For every new or bumped dependency:
- Run `mvn dependency:tree -Dincludes=<group>` and check the transitive versions too.
- Pick the latest patch release that Artifactory has. Never pick a version because it is in local `~/.m2`.
- Check advisories (GitHub Advisory / NVD) for the exact version you propose, before you propose it. Record the version,
  the advisories checked, and the result.
- A known CVE in the chosen version is a finding, unless there is no fixed release; then name it for security sign-off.

## Versioning and CHANGELOG

- Each task gets its own new version section in `CHANGELOG.md`. Increment only the last number; the first two stay
  the same (`x.y.z` -> `x.y.z+1`, next task `x.y.z+2`). Use the repo's existing format. Never add to an already
  released section.
- Entries are a short summary for readers of the release, not a change log of the work:
  - 1-2 bullets per task, 3 at most. Only changes worth mentioning: new behavior, changed behavior, new config,
    removed features. No refactors, test-only changes, file lists or rework history.
  - Every bullet is `* [<Story ID>] - <summary>`, e.g. `* [EFFIE-12345] - Add file download for the partner recon job.`
  - Plain words, one sentence each, under the repo's existing heading (`### Added`, `### Changed`, `### Fixed`).
  - Typical shape: one bullet for the goal of the change, one for docs or config if they changed.
  - Rework later in the task updates the same bullets. It never adds new ones.
- Never edit `<version>` in `pom.xml`: CI bumps it.

## Repo hygiene

No internal IDs (AC, TC, G, RV, R) in anything that lands in a repo: code, test names, `@DisplayName`, feature files,
comments, docs, CHANGELOG, commit messages, branch names other than `T<n>`. IDs stay in `<work>`. The test-to-TC map
lives in the developer notes. A `commit-msg` hook (`~/.claude/scripts/git-hooks/commit-msg`) rejects IDs in commit
messages in every task worktree.

## Git

- Commit messages: `[TICKET] short imperative message`.
- One logical unit per commit, and every commit compiles.
- Commit the failing test before the code that makes it pass: one RED commit, then the GREEN commit. A test and its
  code in one commit is a finding. The RED commit may add empty stubs (signature only, `throw new
  UnsupportedOperationException()`) so it compiles; the test then fails at run time.
- RED/GREEN commits are working history inside `<work>` only. Before the first push, the lead squashes the whole
  task into **one commit per repo** (`[<Story ID>] <summary>`). Later rounds on a pushed MR add one commit per round;
  pushed history is never rewritten without the user's word.
- Never commit generated files, IDE settings, `.DS_Store` or secrets.
- A fix commit says the cause in the message, e.g. `[<Story ID>] Fix NPE on add when the customer has no record yet`.
- MR description: Summary (what and why, removed items named), Root cause (fixes), the sibling it copies
  (`matching how <SiblingClass> handles this`), Behavior changes, Rollout prerequisites (config MR, topics,
  dashboards), Test plan with real counts (`<n> tests, 0 failures, <n> Cucumber`). CHANGELOG in every MR.

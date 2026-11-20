# Migration rules (V1 to V2) — only when the requirement says it is a migration

Read this file only when `requirement.md` or the task overview says the work is a migration (port, V1 to V2, rewrite of
an existing service). The planning-lead marks it in `requirement.md` as `Migration: yes (<V1 repo>)`. Otherwise these
rules do not apply. Every agent reads it in that case, in addition to the engineering standards.

## Parity is the default

- V1 behavior is the default: config values, security settings, file handling, error handling, deploy files.
- Any change from V1, even one that looks better, is a user decision. Raise it at planning or at G1 with the V1
  `path:line`, the options and a recommendation. Never decide it yourself.
- A parity choice that is a known weakness gets a `// shortcut:` comment (engineering standards, "Code rules") and a
  row in `plan.md` Follow-ups.

## Per role

- **Planning:** every known V1 deviation is an open question with V1 `path:line`. Every task states its deploy-file
  impact, compared with the V1 service's deploy files.
- **Architect:** copy the V1 class and method shape (names, order, flow) unless an AC says otherwise.
- **Security in code:** follow the V1 service's pattern if the V2 repo has none. No pattern in either: ask the user.
- **Deploy files:** compare `values*.yaml` (`extraEnv`, `extraVolumes`, secret mounts, partner lists) with V1.
- **Config:** values match V1, per profile.
- **Review:** apply `~/.kiro/skills/code-review-standards/references/migration.md` (read it; it is not loaded by default).

# Engineering standards: config, compatibility, deploy files

Part of the engineering standards, split by role (`~/.kiro/steering/team/standards/es-*.md`). Each agent loads only the parts it needs.

## Configuration (the config repo)

**The config repo** = where the application's runtime config lives:
- a DTC service that reads Spring Cloud Config: `dtc-centralized-app-configs`
  (`~/Desktop/projects/dtc-centralized-app-configs`), files under its application's folder;
- anything else (a library, a plugin, a tool, a service without Config Server): its own `application*.yml` /
  properties in the same repo, if it has any.

Config work exists **only when the task's code reads a new, changed or removed property**. A library or plugin change
never adds work in `dtc-centralized-app-configs`, unless a consuming service's task needs a key for it; that is the
consumer's task. Never create config files, keys or a config task "just in case".

**A config change is part of the task that needs it**, never a separate task and never "later":
- Any new, changed or removed property that the task's code reads goes into the config repo, as one more repo of the
  same task. The code and its config are designed, tested, reviewed and pushed together.
- Follow the repo's existing layout: the same file naming per application and profile, the same key style, and the same
  ordering and comments. Find the application's existing files and copy their shape. Never invent a new layout.
- Cover **every profile or environment file the application has**. A key added to one environment but missing from
  another is a defect, unless the design says why.
- No secrets or credentials in plain text. Use the placeholder or encryption mechanism the repo already uses.
- The code binds new keys the way the repo already does (for example `@ConfigurationProperties`), with a safe default
  or a clear startup failure, as the siblings do.
- Changes must be safe in any order. Adding a key is safe. Renaming or removing a key that running code still reads is
  not. Do it in two steps (add the new key and switch the code; remove the old key later), unless an AC says otherwise.
- If the task needs no config change, say so explicitly: `Config: none (reason)`.

## Compatibility

REST APIs, Kafka/SQS messages, documents, config schemas and shared-lib public methods change without breaking existing
consumers, unless an acceptance criterion says otherwise.

**Migration tasks only.** When `requirement.md` says `Migration: yes`, also read and follow
`~/.kiro/team/migration-rules.md` (V1 parity, V1 shape, V1 deploy and config compare). Otherwise ignore V1.

## Deploy files

The task also covers the service's own deploy files (`values*.yaml`, Helm/chart values): `extraEnv`, `extraVolumes`,
secret mounts, partner or feature lists. Every new config path that points at a mount (key files, secrets) needs its
mount. If nothing changes, write `Deploy: none (reason)`.

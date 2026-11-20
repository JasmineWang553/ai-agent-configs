# Architecture: T<n> — <title>

Status: not started | draft | gate passed | approved
Round: <n> | Versions (from pom.xml): Java <x>, Spring Boot <y>, <key libs>

## Summary

<3-5 bullets: the approach in plain words. A reader who stops here knows what will be built.>

## Flow

```
<ASCII diagram: entry point -> components -> external systems>
```

## Acceptance criteria -> components

| Acceptance criterion | Component(s) (file#method) |
|---|---|
| T<n>-AC1 | |

## Patterns followed

| New / changed component | Sibling it copies (`path:line`) | Matched on | Deviation (reason) |
|---|---|---|---|

## Changes

### Existing files
| Repo | File (`path:line`) | Change |
|---|---|---|

### New files
| Repo | Full path | Purpose |
|---|---|---|

## Signatures

```java
// every new or changed class, public method, constant, exception — no bodies
```

## Skeleton (non-obvious logic only)

```java
// short outline, not the full code
```

## Failure paths

| Failure | Behavior | Where handled |
|---|---|---|
| bad input | | |
| dependency down / timeout | | |
| duplicate / replayed message | | |

## Config (the config repo, only if the code reads a new, changed or removed key)

`Config: none (reason)`, or:

| Key | File per profile (existing layout) | Value / placeholder | Default in code | Bound by |
|---|---|---|---|---|

Order safety: <additive, or the two-step plan for a rename/removal>

## Cross-repo contracts

<What one repo of this task produces that another consumes (message, API, shared-lib method, config key), and how both
sides match. `n/a` for a single-repo task.>

## Compatibility

<API / message / document / config changes and why old consumers still work, or `n/a (reason)`.>

## Work split

| Developer | Repo | Files (sole owner) | Depends on | Order |
|---|---|---|---|---|
| dev-a | | | |
| dev-b | | | |

Shared files (`pom.xml`, `CHANGELOG.md`, shared constants) have exactly one owner.

## Design decisions

| Decision | Options considered | Chosen because | Upgrade trigger |
|---|---|---|---|

## Rework log

| Round | Item | Answer |
|---|---|---|

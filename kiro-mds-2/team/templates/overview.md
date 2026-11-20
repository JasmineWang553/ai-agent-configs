# T<n> — <title>

| Field | Value |
|---|---|
| Ticket | |
| Depends on | <none / T<m> (reason)> |
| Size | S / M / L |
| Risk | low / medium / high — <why> |
| Design review by reviewer | yes (risk high) / no |
| Verification | standard (unit + cucumber) / integration — <infra: kafka, sqs, mongo> — <reason> |
| Architect | yes / no — <reason> (no only if: size S, one repo, one developer, no new class, public signature, config key, message/API/document contract, DB query or external call) |
| Status | planned |

## Repos

| Repo | What changes | Base branch | Merge order |
|---|---|---|---|
| <service-repo> | | | 2 |
| <config repo, if needed> | <application, profiles, keys> — or drop this row and write `Config: none (reason)` | | 1 |

## Goal

<2-3 sentences: what changes and why it matters.>

## Scope

**In:**
- 

**Out (explicitly not in this task):**
- 

## Acceptance criteria

| ID | Criterion (Given / When / Then, or measurable) | Verified by |
|---|---|---|
| T<n>-AC1 | | unit / cucumber / both |

## Context from the code

- `path:line` — what is there and why it matters

## Existing patterns to follow

- `path:line` — closest sibling for <component kind>, follow because <reason>

(`Architect: no`: this list and the touch points are the whole design. Name the exact file and method to change.)

## Risks and open questions

- 

## Change log

| Date | Change | Why / approved by |
|---|---|---|

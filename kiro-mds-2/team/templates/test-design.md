# Test design: T<n> — <title>

Status: not started | draft | gate passed | approved
Round: <n> | Source: overview.md (T<n>-AC1..ACk)

## Summary

| Layer | Positive | Negative | Destructive | Security | Contract | Total |
|---|---|---|---|---|---|---|
| unit | | | | | | |
| cucumber | | | | | | |
| integration (only if Verification: integration) | | | | | | |

`n/a` lines (with reason): Destructive: … | Security: … | Contract: …

## Coverage map

| Acceptance criterion | Test cases |
|---|---|
| T<n>-AC1 | T<n>-TC01, T<n>-TC04 |

## Test cases (TDD order)

### T<n>-TC01 <behavior in plain words>
- Type / Kind: Positive / happy
- Layer: unit | cucumber | integration
- Target: <existing class#method or endpoint `path:line`> | `new: <purpose>`
- Preconditions:
- Steps:
- Expected result: <exact values>
- Gherkin (cucumber only):
  ```gherkin
  Scenario: …
    Given …
    When …
    Then …
  ```
  Feature file: <existing path | new name> · New steps: <none | `new step: <text>`>
- TDD order: 1

## Open questions

## Rework log

| Round | Item | Answer |
|---|---|---|

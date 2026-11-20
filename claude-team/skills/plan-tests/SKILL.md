---
name: plan-tests
description: Generate specific, executable test points covering normal, exception, edge, and state-transition cases, risk-first. Use when the user asks to plan tests, design test cases, or list test points.
---

# Plan Tests

> Not for team runs: the `test-designer` agent follows skill `engineering-standards` and the
> `test-design.md` template instead. Use this skill only for ad-hoc test planning in a direct chat.

Write specific, executable test points. No vague text. Keep each test case description short.

## Cover (all required)
- Normal: standard input -> expected result; main user paths.
- Exception: bad input, business rule blocks, system faults (API fail, timeout, retry).
- Edge: length min/max, count limits, time (expiry, delay, concurrency).
- State: multi-step flows (create -> modify -> delete); check valid and illegal transitions.

## Risk order
1. Core flows (login, payment, submit)
2. Security (privilege, bypass)
3. Data (dup submit, concurrent write)
4. State (dirty/corrupt data)
5. UI and text

## Each test point format
```
[Name]
Preconditions:
Steps:
Expected result:
```
- Reproducible and pass/fail verifiable.
- No duplicates, no abstract text, no non-executable steps.
- Keep the description short.

## Self-check
- Complete: normal + exception + edge?
- Relevant: core business, not trivia?
- Executable: ready for test or automation?
- Clear: no ambiguity?

$ARGUMENTS

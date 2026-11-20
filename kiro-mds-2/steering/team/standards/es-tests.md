# Engineering standards: test design rules and test code

Part of the engineering standards, split by role (`~/.kiro/steering/team/standards/es-*.md`). Each agent loads only the parts it needs.

## Test design rules

Each test case has exactly one Type and one Kind, and tests exactly one behavior:

| Type | Kind | What it covers |
|---|---|---|
| Positive | happy | Normal input, main flows, valid state transitions |
| Positive | boundary | Valid limits: min, max, at the edge, empty-but-allowed |
| Negative | sad | Bad input, null, wrong format, a rule that blocks, illegal transitions |
| Negative | boundary | Just below min, just above max, over length |
| Destructive | fault | Dependency down, timeout, retry, partial failure, duplicate or replayed message, concurrent write, corrupt data |
| Non-functional | security | Missing or wrong auth is denied, injection, no PII or secrets in logs or responses |
| Non-functional | contract | Old message/document still reads, a missing optional field is OK, a missing required field fails clearly, the public API is unchanged unless an AC says so, new config keys bind and a missing required key fails clearly (or the default applies) |

Coverage:
- Every acceptance criterion gets at least 1 Positive and 1 Negative test case.
- **Destructive:** required when the code calls anything external or keeps state. Otherwise write `n/a (reason)`.
- **Security:** required when the change touches an endpoint, auth, a partner/customer key, outside input, or logging of
  customer data. Otherwise write `n/a (reason)`.
- **Contract:** required when the change touches a REST API, a Kafka/SQS message, a document shape, config properties,
  or a shared-lib public method. Otherwise write `n/a (reason)`.
- No performance tests.

**Layers (hard rule): every task has both `unit` and `cucumber` test cases.**
- Per AC, `cucumber: n/a (pure logic: <reason>)` is allowed only for an AC that is pure logic: no I/O, no external call,
  no state, no config, no flow a caller sees (e.g. a parser, a mapper, a comparator). Unit tests then cover it fully.
- Every other AC gets Cucumber scenarios as below. A task with zero Cucumber test cases is a FAIL.
- Unit tests cover the logic branches.
- Cucumber covers the flow:
  - at least 1 Positive and 1 Negative scenario per AC;
  - a Destructive scenario when the flow calls a DB, Kafka, SQS, S3, SFTP or HTTP;
  - full Gherkin with exact data;
  - existing step text quoted exactly, and new steps marked `new step: <text>`;
  - no scenario that only repeats a unit case.
- If the repo has no Cucumber setup at all, the user decides. Nobody passes it on their own.
- **Integration (only when the overview says `Verification: integration`):** Destructive and contract behavior of the
  message or data flow, proved against real infrastructure in Testcontainers (Kafka, LocalStack SQS/S3, MongoDB):
  send a real message, assert the stored result, then the retry, the duplicate or replayed message, and the DLT/DLQ
  path. Layer `integration`, at least one per risky AC. How: `~/.kiro/team/verification.md`.
- **Config-only repo** (the config repo when it has no test setup): no unit or Cucumber test cases. Instead, one
  binding proof: a throwaway check in `<work>` that binds the changed files with the real service code (per profile)
  and prints the bound values.

Precision:
- Use exact inputs and exact expected values: the status, exception type, message key and resulting state. Never
  "returns an error".
- The target is a public entry point: an existing `class#method` or endpoint with `path:line`, or `new: <purpose>`
  (the architect names new classes).

TDD order: the simplest Positive happy case first, then Positive boundary, Negative, Destructive, Non-functional.
Cucumber scenarios come last for each AC.

## Test code

- JUnit 5 and Mockito, plus AssertJ, WireMock and Testcontainers where the repo uses them.
- `@DisplayName` on test classes and methods. Structure each test as `// given // when // then`.
- For parameterized tests, use `@CsvSource` with `|` as the delimiter.
- Reuse existing fixtures, builders and Cucumber steps before writing new ones. Custom test infrastructure (a fake
  server, a new test base class) needs a written reason why an existing tool (Testcontainers image, WireMock) does not
  fit. YAGNI applies to tests too.
- One change over N enum variants: `@ParameterizedTest` + `@EnumSource` / `@MethodSource`, not N copies.
- Build the class under test with real collaborators where cheap; mock only the boundary (`KafkaTemplate`, HTTP client).
- Use real infrastructure where the repo does: `@EmbeddedKafka`, LocalStack, WireMock, Testcontainers.
- Mock only at boundaries. Never mock the class under test.
- Assert behavior, not implementation.

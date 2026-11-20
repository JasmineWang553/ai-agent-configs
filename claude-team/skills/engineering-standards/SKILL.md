---
name: engineering-standards
description: The team definition of good work for DTC Java/Spring Boot services (pattern conformance, code rules, framework checks, config, compatibility, dependencies, CHANGELOG, repo hygiene, test design rules, test code, git). Preloaded by the team agents. Use when designing, coding, testing or reviewing DTC service code.
---

# Engineering standards

The one definition of good work. The architect designs to it, developers code to it, the test designer tests to it,
and the lead and the reviewer check against it.

**The codebase wins.** Where a repo already does something one consistent way, follow the repo, even if this file says
otherwise. Note the difference in your output instead of "fixing" it.

## Stack and sources to read first

Java 21/25, Spring Boot / Spring Cloud, Kafka, SQS, MongoDB / DocumentDB, DynamoDB, Maven, JUnit 5, Mockito, AssertJ,
WireMock, Testcontainers, Cucumber. Services live in `~/Desktop/projects/*`.

Read these before you design, code or review:
- `pom.xml` (the module and its parent) for the Java, Spring Boot and library versions. Never assume a version, and use
  only APIs those versions have.
- Architecture docs, if they exist: `~/Desktop/ai-stuff/dtc-architecture/DTC_V2_ARCHITECTURE.md`, the repo's
  `ARCHITECTURE.md`, `docs/`, and ADRs. Record what you read, or `none found`.
- The closest existing siblings (see Pattern conformance).

To build behind Charter Artifactory: follow `~/.claude/rules/maven-charter-cert.md` (loaded from CLAUDE.md). Otherwise use `./mvnw` if the repo has it, else `mvn`.

## Pattern conformance (the most important rule)

For every component you add or change, find its closest existing sibling. That means the same layer and the same kind:
listener, controller, service, repository, mapper, config, exception, step definition, or feature file. Look in the same
repo first, then in sibling services.

Match the sibling on:
- package placement and naming;
- dependency-injection style;
- exception types and error handling;
- logging;
- config binding;
- retry and idempotency handling;
- mapping;
- test layout.

Cite the sibling as `path:line`. A deliberate deviation needs a written reason.

Copy the sibling's shape, not its defect. If the sibling has a bug or a known weakness, do not copy it silently: flag
it in your output (`path:line`, what is wrong) and let the lead decide.

## Design principles

- Build the smallest complete solution, and reuse before you add. Smallest doesn't mean sloppiest: no copy-paste, no
  hard-coded values, no giant methods.
- One class, one job. Follow the existing layers. No business logic in controllers or listeners.
- Add an extension point only where the requirement names a likely change. Don't add one for a guess (YAGNI).
- Inject dependencies, and keep logic reachable by a unit test.
- Two checks: will a new developer understand this in 6 months? Would one new requirement force a rewrite?

## Code rules

- Constructor injection with final fields; Lombok `@RequiredArgsConstructor` where the repo uses it. No field injection.
- `var` where the type is obvious. Import classes rather than writing fully qualified names inline.
- No magic strings or numbers: use constants or enums (`HttpStatus.TOO_MANY_REQUESTS`, not `429`). A one-use local
  index or name (array index, a map key read once, a log label) stays inline; no constant for it.
- Config values (URLs, paths, timeouts) go in properties, bound the way the repo already does it.
- Build URLs and paths with builders (`UriComponentsBuilder`, `Path.of`), not string concatenation.
- Use existing exception types first. Error messages carry context (ids, not payloads) and match the repo's wording,
  e.g. `"<operation> failed status=%s <entity>Id=%s".formatted(status, id)`.
- Javadoc on new classes and public methods: one line, at most two sentences, of why or contract. Add tags only when
  they add information.
- Records for DTOs, value objects and private helper tuples. Put derived values on the record
  (for example a `nextAttempt()` method on a retry record) instead of loose strings or maps.
- Modern Java the `pom.xml` version supports: pattern matching `instanceof`, arrow `switch`, `sealed` where it fits.
  `Optional` / fluent results instead of null checks inside the code.
- Keep layers thin and uniform: a controller or listener only delegates. Every method of a client wrapper has the
  same shape: build request -> get token -> log -> call -> check status.
- Prefer deleting a branch, filter or rule over adding a new one when that is the fix.
- Inject `Clock` for anything time-based. No `System.currentTimeMillis()` / `Instant.now()` in logic.
- Comments only for a non-obvious why or a constraint. No process notes in code ("parity", "user decision",
  ticket or review refs); those go in `<work>` files.
- A known risk or limit in code gets one line: `// shortcut: <the risk or limit>, <when to upgrade>`. State the
  risk, not who decided it (e.g. `// shortcut: accepts any host key (MITM risk), pin it once the host key is known`).
  Each shortcut also gets a row in `plan.md` Follow-ups.
- Keep PII, secrets and full payloads out of logs. Log levels match the repo.
- No unrelated refactors, and no reformatting of code you didn't touch.

## Framework checks

- **Beans:** the right stereotype, no circular dependencies, and profiles/conditions as the repo uses them.
- **Config:** `@ConfigurationProperties` (or the repo's equivalent) instead of scattered `@Value`. `@Validated` with
  bounds (`@DurationMin` / `@DurationMax`) and defaults (`@Builder.Default`). Fail fast only when the feature is enabled.
- **Transactions:** `@Transactional` only where the repo uses it, on public methods, and never self-invoked.
- **Kafka / SQS:**
  - listener error handling, retry with backoff, and a dead-letter queue (DLQ);
  - idempotency for replayed messages;
  - acknowledgement mode (manual or auto) as the repo does it;
  - backward-compatible message schemas;
  - classify every failure once as RETRYABLE or NON_RETRYABLE through a typed exception (one private method maps HTTP
    status: 5xx -> retryable, else non-retryable);
  - Kafka: failed records go to `<topic>-retry` / `<topic>-dlt` keyed by the entity id; ack only after that publish
    succeeds; back off with `Acknowledgment.nack(Duration)`, never by blocking the poll thread;
  - catch I/O exceptions separately (`TimeoutException`, `ExecutionException` unwrapped) and restore the interrupt flag
    on `InterruptedException`;
  - one metric per terminal outcome (success, retried, sent to DLT), and one log point per failed attempt with ids and
    the attempt number.
- **Mongo / DocumentDB / DynamoDB:**
  - an index for every new query, and no unbounded scans;
  - optimistic locking where concurrent writes can happen;
  - old documents still read (new fields optional).
- **HTTP clients:** timeouts set, retries bounded, and errors mapped to the repo's exception types.
- **Deprecation:** no deprecated API for the `pom.xml` version when a supported replacement exists.
- **Files and batch (SFTP, S3, local files, scheduled jobs):**
  - never move, archive or delete a file you did not process; a file that arrives during the run stays where it is;
  - a rerun after a partial failure gives the same result (idempotent rerun);
  - two runs at once do not corrupt each other: one session or lock per run;
  - write down the partial-failure result: what is done, what is not, what the caller or the next run sees;
  - delete temp files in `finally`; no `deleteOnExit()` in a long-running service;
  - never load an unbounded file into memory: stream it.
- **Security in code** (host-key and certificate checks, file names from outside in paths, input checks, auth): follow
  the pattern the repo already uses, cited as `path:line`. If there is no pattern to follow, do not
  pick one: ask the user (`NEEDS_DECISION` with options and a recommendation).

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
`~/.claude/team/migration-rules.md` (V1 parity, V1 shape, V1 deploy and config compare). Otherwise ignore V1.

## Deploy files

The task also covers the service's own deploy files (`values*.yaml`, Helm/chart values): `extraEnv`, `extraVolumes`,
secret mounts, partner or feature lists. Every new config path that points at a mount (key files, secrets) needs its
mount. If nothing changes, write `Deploy: none (reason)`.

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

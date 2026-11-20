---
name: es-code
description: "DTC engineering standards, part es-code: code rules and framework checks. Preloaded by the team agents that need it. Use when designing, coding, testing or reviewing DTC Java/Spring Boot service code."
---

# Engineering standards: code rules and framework checks

Part of the engineering standards, split by role (skills `es-core`, `es-code`, `es-config`, `es-release`, `es-tests`). Each agent loads only the parts it needs.

## Code rules

**Enforced by checks** (`~/.claude/checks/rules.tsv`, run by `rule-check.sh` on added lines; run it yourself before you
finish): no `@Autowired`, no `System.out`/`printStackTrace`, no `now()` without a `Clock`, no `deleteOnExit()`, no star
imports, no empty catch, no TODO/FIXME, no plain-text secrets in config; warnings for ticket refs, process notes and
commented-out code in comments. The bullets below are the rules a check can't decide.

- Constructor injection with final fields; Lombok `@RequiredArgsConstructor` where the repo uses it.
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
  - delete temp files in `finally`;
  - never load an unbounded file into memory: stream it.
- **Security in code** (host-key and certificate checks, file names from outside in paths, input checks, auth): follow
  the pattern the repo already uses, cited as `path:line`. If there is no pattern to follow, do not
  pick one: ask the user (`NEEDS_DECISION` with options and a recommendation).

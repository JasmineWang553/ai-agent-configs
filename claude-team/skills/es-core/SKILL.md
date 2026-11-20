---
name: es-core
description: "DTC engineering standards, part es-core: core: stack, pattern conformance, design principles. Preloaded by the team agents that need it. Use when designing, coding, testing or reviewing DTC Java/Spring Boot service code."
---

# Engineering standards: core: stack, pattern conformance, design principles

Part of the engineering standards, split by role (skills `es-core`, `es-code`, `es-config`, `es-release`, `es-tests`). Each agent loads only the parts it needs.

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

To build: read `~/.claude/rules/maven-charter-cert.md` before your first `mvn` run (it is not preloaded). Otherwise use `./mvnw` if the repo has it, else `mvn`.

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

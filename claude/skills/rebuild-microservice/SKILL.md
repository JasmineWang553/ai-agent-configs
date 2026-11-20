---
name: rebuild-microservice
description: Rebuild an existing Charter DTC Java/Spring Boot microservice from zero in ~/Desktop/rebuild/rebuild-<service>, one layer at a time, in dependency order. Each layer has real code, 2 JUnit 5 tests (happy + negative), "Only in rebuild:" logs, IntelliJ run configs and a git commit. Use when the user says "rebuild <service>", wants to learn an undocumented service by rebuilding and running it, or says "next" during a rebuild.
---

# Rebuild a DTC Microservice Layer by Layer

## Purpose
- The user learns an undocumented DTC service.
- You rebuild it from zero in a new folder.
- You add one layer at a time, in dependency order.
- Each layer must build, pass its tests and run before the next layer.

Follow the short-answer rules (`~/.claude/rules/short.md`, loaded from CLAUDE.md) for all text to the user.

## Step 1: Get the inputs
Ask only for what you cannot find:

| # | Item | Default |
|---|---|---|
| 1 | Service name | — (required) |
| 2 | Real repo | `~/Desktop/projects/<service>` |
| 3 | Rebuild folder | `~/Desktop/rebuild/rebuild-<service>` |
| 4 | Docker running | check with `docker info` |

Then read the real repo. Report in one table:
- Java version (`java.version` / `maven.compiler.release` in `pom.xml`)
- Spring Boot and Spring Cloud versions
- Charter libs (`dtc-*`, `effie-*`) from the pom
- Datastores and messaging: DocumentDB/Mongo, Kafka, SQS, DynamoDB
- Test stack: JUnit 5, Mockito, AssertJ, WireMock, Testcontainers, Cucumber
- `server.servlet.context-path`

Use only language features the pom's Java version supports.

## Step 2: Make the layer plan
Map the real code into these layers. Each layer uses only the layers below it.

| # | Layer | DTC contents | Proof |
|---|---|---|---|
| 0 | Basics | `pom.xml`, `Application`, `application.yml`, actuator, `.run/` configs | `curl .../actuator/health` gives `UP` |
| 1 | Core config | `@Configuration` beans: Mongo, Kafka, SQS, DynamoDB, `RestClient`, Jackson | the log shows each bean or connection |
| 2 | Entry points | `@RestController`, `@KafkaListener`, `@SqsListener`, `@Scheduled`. Return fixed data. | `curl` or a sent message gives a log/response |
| 3 | Models | `@Document` classes, DTOs, records, enums, shared-domain types | a model round-trips through Jackson |
| 4 | Foundation | repositories, `MongoTemplate` queries, API clients (read-api, write-api, partner) | a doc goes into Mongo and comes back |
| 5 | Business logic | services, comparators, rules, status changes | a request makes a rule run |
| 6 | Cross-cutting | `@ControllerAdvice`, validation, retry + DLT, idempotency, version-conflict handling, Micrometer | bad input gives the correct error |

- If the repo has a different shape, change the layers to match it and say why.
- Split a large layer into sub-steps: one entry point or one concept each.
- Show the plan as a table with the real files for each layer.
- Write the plan to `REBUILD.md` in the rebuild folder.

## Step 3: Do each layer
1. Read the real code for the layer.
2. Write the layer in the rebuild folder.
   - Use the same package names, file names and class names as the real repo.
   - Write the core of the real code. Remove what this layer does not need.
   - Use the repo's conventions: constructor injection via `final` fields + Lombok, its exception types, its comment style.
   - At the top of each file: `// Rebuild of: <real file path>`.
3. Add the logs. See "Logging rules".
4. Write 2 unit tests. See "Test rules".
5. Build and run the tests (see "Build"). Show the real output.
6. Start the service and send a request, if the layer has one. Show the real output.
7. Show a short summary:
   - a table of new files, one line each
   - a small diagram of the flow so far
   - the commands to run the service and the tests
   - the breakpoint for each test (`Class:line`)
8. Commit in the rebuild folder: `Layer <N>: <name>`. This skill is the user's permission to commit there.
9. Mark the layer done in `REBUILD.md`.
10. Stop. Wait for the user to say "next".

## Build
Follow `~/.claude/rules/maven-charter-cert.md` (read it first; it is not preloaded) before every `mvn` run:
- Set `JAVA_HOME` to the JDK that matches the pom.
- Use the per-JDK trust store for `artifactory.se-charter.net`.
- Build: `mvn -Djavax.net.ssl.trustStore=... -Djavax.net.ssl.trustStorePassword=changeit clean verify`
- Run: `mvn ... spring-boot:run -Dspring-boot.run.profiles=local`
- Stop a hung command after 2 minutes. Show the error.

## Logging rules
- Use Lombok `@Slf4j`.
- Log where data moves between layers.
- Start each line with `Only in rebuild: `.

| Tag | Where |
|---|---|
| `[ENTRY]` | a request or message comes in: method, path or topic, body |
| `[→LOGIC]` | the handler calls the service, with the data |
| `[RULE]` | a business rule runs, with its result |
| `[STATE]` | a status changes: old → new |
| `[→DB]` | data goes to or comes from Mongo/DynamoDB |
| `[→SVC]` | a call to another service, with the response status |
| `[→QUEUE]` | a message goes to or comes from Kafka/SQS |
| `[EXIT]` | the response goes out: status, body |

- Example: `Only in rebuild: [STATE] TEST.6767/6767... ELIGIBLE → CANCELED`
- Show passwords, tokens, emails, names and addresses as `***`.

## Test rules
- 2 tests per layer:
  - happy path: correct input gives the correct result
  - negative path: bad input gives the correct error
- JUnit 5 + Mockito + AssertJ, in the same `src/test/java` package as the class.
- Reuse the real repo's test helpers and builders when they exist.
- Docker running: use Testcontainers (`MongoDBContainer`, `KafkaContainer`, LocalStack for SQS/DynamoDB).
- No Docker: use Mockito fakes. Add Testcontainers in a later layer.
- Tests must run from the IntelliJ gutter and in debug.

## IntelliJ (Layer 0)
Add to `.run/` (commit them):
- `Application.run.xml`: Spring Boot config, main class, active profile `local`.
- `All tests.run.xml`: JUnit config for the whole module.
Tell the user to open the rebuild folder as a Maven project.

## Safety rules
- Do not change the real repo. Only read it.
- Do not copy secrets. Put local values in `application-local.yml` (git-ignored) and commit `application-local.example.yml` with fake values.
- Do not connect to shared dev or UAT datastores from the rebuild unless the user asks.
- Do not say a test passed if you did not run it. Show the real output.
- If a build or test fails, show the error, then fix it.
- Local git only. Do not add a remote or push.

## Optional: git history
If the user asks, find the commit in the real repo where a part was first added:
`git log --diff-filter=A --format='%h %ad %s' --date=short -- <file>`. Show one line.

## Continue in a new session
1. Read `REBUILD.md` in the rebuild folder.
2. Run `git log --oneline` there.
3. Show the status in one table.
4. Continue with the next layer.

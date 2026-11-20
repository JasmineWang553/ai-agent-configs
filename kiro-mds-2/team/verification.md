# Verification against real infrastructure (`Verification: integration`)

Read on demand by the test-designer and developers when a task's overview says `Verification: integration`.
Goal: prove the message or data flow works against a real broker or store, inside `mvn verify`, with no shared
environment and nothing to start by hand except Docker.

## 1. No config server: read the config repo files

The task worktrees already hold the config repo (`wt/T<n>/<config-repo>`). In the integration test, turn the config
client off and import the files of the profile you test, so the task's config change is tested too:

```java
@SpringBootTest(properties = {
    "spring.cloud.config.enabled=false",
    "spring.config.import=optional:file:${config.repo.dir}/<app>.yml,optional:file:${config.repo.dir}/<app>-<profile>.yml"
})
```

Pass `config.repo.dir` from Maven (`-Dconfig.repo.dir=<work>/wt/T<n>/<config-repo>`), or fall back to a copy under
`src/test/resources/config/` if the repo already does that. Values that come from Vault or other secret sources get
dummy values in the test (`@DynamicPropertySource` or `application-it.yml`), never real ones.

## 2. Snapshot dependencies from the GitLab package registry

- **Normal case:** `~/.m2/settings.xml` has the GitLab registry as a `<server>` with an `httpHeaders` entry
  `Private-Token` (your personal access token, `read_api` scope). After one build the snapshots sit in `~/.m2`;
  `mvn -o` then works offline.
- **The task also changes that dependency:** don't pull it. `g2-check.sh` builds repos in merge order with
  `clean install`, so the consumer builds against the fresh local version. Developers do the same by hand:
  `mvn -B -q install -DskipTests` in the dependency's worktree first.
- A snapshot that isn't in the registry and isn't in the task: `BLOCKED` with the coordinates. Don't vendor jars.

## 3. Infrastructure with Testcontainers

Use the Testcontainers version the repo or its BOM already has. Adding Testcontainers to a repo that has none is a new
dependency ("Dependencies" rule) and needs the architect's or the user's yes.

| Need | Container | Notes |
|---|---|---|
| Kafka | `org.testcontainers:kafka` (`KafkaContainer`, `ConfluentKafkaContainer` on newer versions) | Create the topics and their `-retry` / `-dlt` topics in the test setup |
| SQS, S3 | `org.testcontainers:localstack` | Point the AWS client at `localstack.getEndpoint()`; create queues and DLQs in setup |
| DocumentDB | `org.testcontainers:mongodb` | Close, not identical: DocumentDB lacks some operators, index types and transaction behavior. Keep DocumentDB-only behavior as a reviewer check (aspect E) |
| HTTP partners | WireMock (already in most repos) | Not a container |

Wire them with `@DynamicPropertySource` (or `@ServiceConnection` where the repo's Spring Boot version and style use it).
One container per type per test class, `static`, so the class starts them once.

## 4. What an integration test proves

For each risky AC (the test design names them):
1. **Happy path:** publish a real message, wait for the effect (stored document, outgoing message) with a bounded
   wait (Awaitility, at most a few seconds), assert exact values.
2. **Retry:** make the dependency fail (WireMock 5xx, stop nothing else), assert the record goes to `<topic>-retry`
   with the attempt number, then succeeds when the dependency recovers.
3. **Duplicate / replay:** publish the same message twice, assert one effect (idempotency).
4. **Dead letter:** a non-retryable failure lands in `<topic>-dlt` / the DLQ, keyed by the entity id, and the offset
   is acked only after that publish.

Name the class `<Thing>IT` if the repo runs failsafe, otherwise follow the repo's existing integration-test naming
and tags. No `Thread.sleep`; no shared state between test methods.

## 5. Docker

Docker Desktop must be running. `g2-check.sh` fails fast with "Docker is not running" when a repo uses Testcontainers.
If Docker can't run on the machine, the planning-lead sets `Verification: standard` instead; nobody skips the
integration cases on their own.

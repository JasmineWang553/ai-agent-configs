---
name: code-review-standards
description: Steve's code review standards for DTC MRs. Use when the user says "Review <JIRA> <MR url>", "Migration Review <JIRA> <MR url>", asks to review a merge request, or asks to post review comments. Covers the 6-dimension review, pre-review setup, comment style and the approval-before-posting rule. Migration reviews also read references/migration.md.
---

> Source: Steve's `code-review-standards.md` (v1.6) and `v1-v2-migration-review-standards.md` (v1.2). Text is kept as written.

## Local setup (this machine)
- Run `glab` and `curl` to GitLab through `zsh -ic '...'` so `$GITLAB_TOKEN` loads from `~/.zshrc`. Never print the token. See skill `gitlab-glab`.
- Repos are in `~/Desktop/projects/<name>`.
- Global engineering standards: `~/Desktop/projects/dtc-kiro-agent/.kiro/steering/global-engineering-standards.md`. Read it at the start of a review.
- Architecture file: `~/Desktop/ai-stuff/dtc-architecture/DTC_V2_ARCHITECTURE.md`. Read it at the start of every review. If it is missing, say so and ask the user. Do not guess its rules.
- JIRA: no JIRA tool is set up. Steps that need JIRA (read ticket, assign validator) are manual. Ask the user for the ticket text and tell the user which JIRA step to do.
- For a "Migration Review", also read `references/migration.md` before the analysis.

# Code Review Standards

Standards for thorough code reviews across all DTC projects. Builds on the Global Engineering Standards (https://gitlab.spectrumflow.net/effie-dev/dtc-kiro-agent/-/blob/main/.kiro/steering/global-engineering-standards.md), which apply to ALL code generated or modified by AI.

---

## 🎯 Review Process Rules

### Critical Process Requirements
- **NO COMMENTS WITHOUT APPROVAL**: Never post any review comments without explicit user approval first
- **Individual Comment Approval**: Present each proposed comment individually for approval before posting
- **ALL COMMENTS ARE BLOCKING**: All review comments (including positive feedback) must be blocking inline comments to prevent merge until resolved
- **MANDATORY INLINE COMMENTS**: ALL comments must be posted as inline comments on specific lines. No general/top-level comments allowed
- **NEVER EDIT CODE**: Review only - never modify or edit the code being reviewed
- **SYSTEMATIC ANALYSIS**: Complete thorough analysis first, then present findings for approval
- **VERIFY DON'T ASSUME**: Never use tentative language like "might", "could", or "possibly" when you can research and verify the actual facts
- **NO SHORTCUTS WITHOUT PERMISSION**: Never skip or shortcut any part of the systematic review process without explicit user approval
- **ASK BEFORE DEVIATING**: If you want to deviate from the established review process, ask for permission first - never assume it's okay
- **COMPLETE BEFORE CONCLUDING**: Never declare something "looks good" or "ready to merge" until ALL systematic review steps are verifiably complete
- **EXPLICIT COMPLETION TRACKING**: Must explicitly verify and document completion of each review dimension before moving to the next

### Review Workflow
1. **Analyze**: Complete comprehensive review analysis
2. **Present**: Show each proposed comment individually for approval
3. **Approve**: Wait for explicit approval of each comment
4. **Post**: Only post comments after approval received
5. **Verify**: Confirm comments posted correctly as blocking inline comments

### Systematic Execution Guardrails
- **MANDATORY DIMENSION COMPLETION**: Must explicitly complete and verify EACH review dimension:
  1. ✅ Correctness (logic bugs, error handling, thread-safety)
  2. ✅ Simplicity (minimal code, no speculative abstractions)
  3. ✅ DRY (duplicated logic, copy-pasted code)
  4. ✅ YAGNI (unused fields/methods, premature flexibility)
  5. ✅ Documentation (README, CHANGELOG, Javadoc)
  6. ✅ Tests (unit + integration coverage, positive + negative cases)
- **NO EARLY CONCLUSIONS**: Cannot say "looks good", "ready to merge", or similar until ALL 6 dimensions verified
- **EXPLICIT EVIDENCE REQUIRED**: For each dimension, must cite specific examples from code/tests as evidence. Report each dimension in one line: `Dimension: OK|issues - file:line evidence`. Keep the whole review summary short.
- **NO ASSUMPTION STATEMENTS**: Replace "appears to", "seems like", "probably" with verified facts
- **ASK FOR GUIDANCE**: If unsure about scope, priorities, or process - ASK instead of assuming
- **DOCUMENT COMPLETION**: Mark each dimension complete with evidence before proceeding to next

### GitLab API Comment Posting
When posting approved inline comments via GitLab API:
- **Use Environment Token**: Always use `$GITLAB_TOKEN` environment variable for authentication
- **Inline Comment Format**: Use proper position object with base_sha, start_sha, head_sha, and line_code
- **Project Path**: Use URL-encoded project path (e.g., `effie-dev%2Fdata-share-service`)
- **CHANGELOG Fallback**: When the issue file is not in the MR diff, post inline comment on CHANGELOG.md referencing the specific file and line numbers

### Inline Comment Strategy
- **MANDATORY INLINE ONLY**: ALL comments must be posted as inline comments on specific lines - NO exceptions
- **Files in Diff**: Post inline comments on actual changed lines when the issue relates to those lines
- **Files Not in Diff**: When the issue is in a file not modified by the MR, post the inline comment on a changed line in CHANGELOG.md that references the specific file path and line numbers needing cleanup
- **Always Blocking**: Ensure all comments prevent merge until addressed
- **Line-Level Precision**: Comments must reference specific line numbers and file paths for issues outside the diff

### Comment Style Guidelines
- **Short and direct (ultracave)**: One finding per comment. Max 2 short lines: problem, then fix. No greeting, no softening, no recap, no hedging. Example: `Dup of lines 40-52. Extract to a helper.` Do not pad comments to sound friendly or human.
- **Minor Issues**: Start minor/stylistic comments with "nit: "
- **No Issue Numbering**: Never use "Issue #1", "Issue #2" etc. in review comments - use natural descriptive language
- **Complete Analysis**: Present ALL findings (minor and major) for user review - never selectively filter issues
- **No Positive Comments**: Skip "this is great" type comments - focus on issues and improvements only
- **No Assumptions About Developers**: Never ask "is this variable still used?" - verify yourself
- **No Assumptions About Requirements**: If unclear about software behavior or requirements, ask for clarification rather than assuming
- **Research Before Claiming**: Always verify facts through code search, documentation review, or testing before making claims. Replace tentative language like "might", "could", "possibly" with verified findings

---

## 🚀 Command Pattern Recognition

### Automatic Review Trigger Patterns

When these patterns are detected in user input, automatically initiate the full systematic review process:

#### **Standard Code Review Pattern**
```
"Review <JIRA-TICKET> <MR-URL>"
```
**Example**: `Review EFFIE-12345 https://gitlab.spectrumflow.net/effie-dev/dtc-write-api/-/merge_requests/146`

**Auto-loads Context**:
- global-engineering-standards.md
- code-review-standards.md
- DTC_V2_ARCHITECTURE.md

**Process**:
1. Parse JIRA ticket and MR URL from command
2. Execute pre-review setup (repo, JIRA, CHANGELOG, pipeline verification)
3. Perform 6-dimension systematic analysis
4. Present findings for discussion and approval
5. Post approved comments only as blocking inline comments

#### **V1→V2 Migration Review Pattern**
```
"Migration Review <JIRA-TICKET> <MR-URL>"
```
**Example**: `Migration Review EFFIE-13753 https://gitlab.spectrumflow.net/effie-dev/dtc-boku-outbound-lib/-/merge_requests/2`

**Auto-loads Context**:
- global-engineering-standards.md
- code-review-standards.md
- DTC_V2_ARCHITECTURE.md
- v1-v2-migration-review-standards.md

**Process**:
1. Parse command and load migration-specific context
2. Execute enhanced pre-review setup with migration context
3. Perform 8-area migration analysis framework
4. Present findings for discussion and approval
5. Post approved comments only as blocking inline comments

### Implementation Rules
- **Pattern Detection**: Match these exact patterns (case-insensitive) to trigger automatic review process
- **Context Loading**: Rely on CLAUDE.md and the preloaded skills for context - no manual reference needed
- **Process Execution**: Follow established systematic review workflow
- **Standards Compliance**: Maintain NO COMMENTS WITHOUT APPROVAL rule throughout

---

## 📋 Comprehensive Review Framework

### 6-Dimension Review Analysis
Assess each changed area across these core dimensions:

1. **Correctness** — logic bugs, null/NPE risk, error handling, resource leaks, thread-safety, silent failures
2. **Simplicity** — minimum code, no speculative abstractions or unneeded configurability  
3. **DRY** — duplicated logic, copy-pasted classes/config
4. **YAGNI** — unused fields/params/methods, flexibility added before it's needed
5. **Documentation** — README, docs/, CHANGELOG, and Javadoc on new/changed public API
6. **Tests** — unit and integration/BDD coverage of new behavior, edge cases, and negative paths

### Pre-Review Setup Process
**CRITICAL**: Complete ALL setup steps before starting any code analysis:

1. **Repository Setup**:
   - Ensure repo is pulled locally and exists
   - Run `git fetch origin` to get all latest changes
   - Identify correct branch from JIRA ticket (e.g., `feature/EFFIE-12345-description`)
   - Checkout the feature branch: `git checkout feature/EFFIE-12345-description`
   - Rebase to origin: `git rebase origin/feature/EFFIE-12345-description`
   - **Check branch currency**: Ensure feature branch is up-to-date with destination branch (usually `main`)
   - **Verify no merge conflicts**: Confirm clean merge status before reviewing

2. **Context Gathering**:
   - **Pull JIRA ticket**: Read the full ticket description, acceptance criteria, and comments
   - **Assign validator**: Add current user as "assigned validator" on the JIRA ticket (use `customfield_14701` with format `{"name": "USERNAME"}`)
   - **Review MR summary**: Check MR title and description against JIRA ticket
   - **Verify CHANGELOG**: Ensure CHANGELOG.md is updated and matches JIRA ticket scope
   - **Validate version increment**: Check semantic versioning (1.X.Y) matches change type - minor for features, patch for bug fixes
   - **Identify discrepancies**: Note any differences between JIRA requirements and MR scope
   - **Read existing discussions**: Review all existing MR threads to avoid duplication

3. **Code Analysis Preparation**:
   - **Read full source**: Review complete files, not just diff hunks, for proper context
   - **Verify every finding**: Confirm each issue against actual source before proposing comments
   - **Check pipeline status**: Verify CI pipeline passes (build + tests) before reviewing - don't review broken code
   - **Note pipeline failures**: If pipeline fails, identify if failures are related to the changes or environmental issues

### 1. Platform Architecture Compliance
- **Service Ownership Boundaries**: Verify changes don't violate service responsibilities
- **Data Layer Protection**: Ensure proper API usage, no direct DB mutations outside designated services
- **Integration Patterns**: Follow established platform integration standards
- **Command Flow Integrity**: Validate proper messaging patterns and ordering
- **Configuration Management**: Proper externalization and environment handling

### 2. Data Safety & Consistency
- **Concurrency Safety**: Thread-safe operations for shared/mutable state
- **Idempotency**: Proper handling of at-least-once delivery scenarios
- **Ordering Requirements**: Correct ordering mechanisms (Kafka offsets, not timestamps)
- **Backward Compatibility**: Schema evolution without breaking existing consumers
- **Transaction Integrity**: Proper transaction boundaries and rollback scenarios

### 3. Configuration & Deployment Safety
- **Required Properties**: No defaults for environment-specific config (DB hosts, URLs, credentials)
- **Configuration Validation**: Use @ConfigurationProperties with @Validated and @NotNull/@NotBlank annotations
- **Secrets Handling**: No hardcoded credentials, proper externalization to secrets management
- **Environment Isolation**: Changes properly scoped to target environments
- **Rollback Safety**: Reversible changes or clear rollback procedures documented
- **Fail-Fast Behavior**: Application must fail to start with clear error if critical configuration missing

### 4. Testing & Verification Standards
- **Build Verification**: `mvn clean verify` passes before review completion
- **Complete Test Coverage**: Strive for 100% test coverage with comprehensive scenarios
- **Happy Path Coverage**: All positive/success scenarios thoroughly tested
- **Negative Case Coverage**: All failure modes, edge cases, error conditions covered
- **Integration Test Coverage**: End-to-end scenario testing where appropriate
- **Unit Test Quality**: Proper given/when/then structure, meaningful assertions
- **Test Infrastructure**: Proper TestContainers or mock setup for external dependencies
- **Test Configuration Completeness**: Verify all properties referenced in code have corresponding test configuration - check for NPEs caused by missing config
- **Mock Setup Validation**: Ensure all required mocks are properly configured to prevent null pointer exceptions

### 5. Observability & Operations
- **Logging Standards**: INFO-level lifecycle events with full context (IDs, keys, counts)
- **Metrics Registration**: Proper metrics integration with monitoring systems
- **Health Indicators**: Actuator endpoints for external dependencies
- **Error Handling**: Specific exceptions with context, no swallowed errors
- **Monitoring Integration**: Proper alerting and dashboard integration

### 6. Documentation & Traceability
- **CHANGELOG Updates**: Version bumps with clear change descriptions
- **Ticket Alignment**: Implementation matches acceptance criteria and scope
- **Code Documentation**: Javadoc for public APIs, complex business logic
- **Architecture Decisions**: Document significant design choices and trade-offs
- **README Updates**: Keep documentation current with implementation changes

### 7. Security & Compliance
- **Input Validation**: Proper sanitization of external data
- **Injection Prevention**: Parameterized queries, no string concatenation for SQL/NoSQL
- **Dependency Scanning**: No vulnerable or suspicious dependencies
- **Secret Exposure**: No credentials in logs, responses, error messages, or version control
- **Authentication/Authorization**: Proper security controls for sensitive operations

---

## ⚠️ Code Quality Focus Areas

### DRY Principle Enforcement
- **Duplicated Code Blocks**: Look for repeated code, even with minor variations
- **Extract Common Methods**: Identify opportunities to consolidate similar logic
- **Shared Utilities**: Check for repeated patterns that should become utilities
- **Configuration Duplication**: Repeated configuration patterns across environments
- **Similar Class Structures**: Multiple classes with similar responsibilities

### String and Constant Management
- **Repeated String Literals**: Extract to constants or configuration
- **Magic Numbers**: Replace with named constants or configuration properties
- **Hardcoded Values**: Identify values that should come from configuration
- **URL/Path Construction**: Use proper builders vs string concatenation
- **Error Messages**: Consistent, meaningful error messages with context

### Dependency Management
- **Snapshot Versions**: Flag snapshot/timestamped dependency versions (e.g., `1.0.0-20260814.215733-4`) with nit comments reminding developer to update to final release version when available
- **Version Consistency**: Ensure related dependencies use compatible versions
- **Vulnerability Scanning**: No known vulnerable dependency versions
- **Project Version Management**: Do NOT flag project version in pom.xml (e.g., `<version>0.1.0-SNAPSHOT</version>`) - this is managed by CI/CD pipelines and should not be manually changed

### Enum Usage and Type Safety
- **Raw Values vs Enums**: Use enum constants instead of raw values
  - ❌ `statusCode == 429`
  - ✅ `httpStatusCode == HttpStatusCode.TOO_MANY_REQUESTS`
- **String Constants**: Consider enums for fixed sets of string values
- **Type Safety**: Strong typing over primitive types where appropriate

### Java 25 Best Practices
- **Use var**: Prefer `var` for local variable declarations where type is clear
- **Optional Usage**: Target Optional instead of null checks everywhere
- **Modern Language Features**: Leverage Java 25 language improvements and patterns
- **Type Inference**: Use var to reduce verbosity while maintaining readability

### Null Safety and Defensive Programming
- **Optional First**: Prefer Optional over null checks for potentially missing values
- **Defensive Programming**: Defensive programming for external service responses
- **Collection Safety**: Empty collections instead of null returns
- **Input Validation**: Validate inputs at boundaries
- **Null Checking**: When null checks are needed, ensure proper handling of nested object access

### Refactoring Opportunities
- **Method Length**: Break down overly long methods
- **Class Responsibilities**: Single Responsibility Principle adherence
- **Abstraction Levels**: Consistent abstraction levels within methods
- **Pattern Consistency**: Use established patterns consistently across codebase
- **Interface Design**: Clean, minimal interfaces
- **Open-Closed Principle**: Classes and modules should be open for extension but closed for modification. Design with interfaces, strategy patterns, and composition so new behavior can be added without changing existing working code. When adding a new variant (e.g., a new partner type, a new index strategy), extend — don't edit the core logic.

### Performance and Resource Management
- **Resource Cleanup**: Proper try-with-resources or explicit cleanup
- **Connection Pooling**: Appropriate connection pool configuration
- **Caching Strategy**: Effective caching without over-caching
- **Query Optimization**: Efficient database queries and indexes
- **Memory Usage**: Avoid memory leaks and excessive object creation

### Thread Safety Analysis
- **Concurrent Access Safety**: Any state that can be accessed by multiple threads (scheduled tasks, async methods, shared caches, singletons with mutable state) must be thread-safe
- **Atomic Operations**: Prefer AtomicBoolean, AtomicReference, ConcurrentHashMap over manual synchronization
- **Immutable by Default**: Prefer immutable objects and unmodifiable collections
- **Shared Mutable State**: Avoid shared mutable static state; use atomic types when unavoidable
- **Documentation**: Document thread safety contracts in Javadoc

---

## 🔍 Implementation Detail Reviews

### HTTP Client Patterns
- **Configuration Consistency**: Similar timeout, retry, and connection settings
- **Error Handling**: Consistent error mapping and exception handling
- **Response Processing**: Standardized response parsing and validation
- **Authentication**: Proper credential handling and rotation support

### Database Access Patterns
- **Connection Management**: Proper connection lifecycle management
- **Query Patterns**: Consistent query construction and parameterization
- **Transaction Boundaries**: Clear transaction scope and rollback handling
- **Schema Evolution**: Backward-compatible schema changes

### Messaging Patterns
- **Producer Configuration**: Consistent producer settings and error handling
- **Consumer Configuration**: Proper consumer group management and offset handling
- **Message Serialization**: Consistent serialization patterns
- **Dead Letter Handling**: Proper DLQ configuration and processing

### Configuration Patterns
- **Property Binding**: Use @ConfigurationProperties over @Value for complex config
- **Validation**: Required vs optional properties with proper validation
- **Profile Management**: Clean profile-specific configuration
- **Externalization**: Proper externalization of environment-specific values

---

## 📊 Quality Gates

### Before Posting Comments
- [ ] Completed systematic analysis across all review categories
- [ ] Identified specific file paths and line numbers for issues
- [ ] Prepared clear, actionable comment text
- [ ] Ready to present each comment individually for approval

### Code Quality Checklist
- [ ] No duplicated code blocks or similar logic
- [ ] String literals extracted to constants or configuration
- [ ] Proper enum usage instead of raw values
- [ ] Defensive programming for external dependencies
- [ ] Consistent error handling and logging patterns
- [ ] Proper resource management and cleanup
- [ ] Clear method and class responsibilities

### Architecture Checklist
- [ ] Service boundaries respected
- [ ] Configuration properly externalized
- [ ] Security controls in place
- [ ] Observability standards met
- [ ] Testing coverage adequate
- [ ] Documentation updated

---

## 🚀 Continuous Improvement

### Learning from Reviews
- **Pattern Recognition**: Note recurring issues for future reviews
- **Standard Updates**: Update this file when new patterns emerge
- **Team Alignment**: Share learnings with team for consistent standards
- **Tool Integration**: Consider automated checks for common issues

### Review Quality Metrics
- **Issue Detection Rate**: Track types of issues found over time
- **False Positive Rate**: Monitor accuracy of review comments
- **Time to Resolution**: Track how quickly issues are addressed
- **Repeat Issues**: Identify patterns that need better prevention

---

## 📝 Version History

- **v1.0 (2026-09-11)**: Initial comprehensive review standards combining process rules, quality focus areas, and systematic review framework
- **v1.1 (2026-09-11)**: Enhanced with dtc-mr-review skill patterns: 6-dimension framework, question-based comments, pre-review discussion checks; added global engineering standards reference, thread safety analysis, Open-Closed Principle
- **v1.2 (2026-09-11)**: Mandatory inline comments requirement - all comments must be inline, use CHANGELOG.md for issues outside the diff. Added "verify don't assume" principle requiring research instead of tentative language.
- **v1.3 (2026-09-16)**: **CRITICAL**: Added systematic execution guardrails to prevent shortcuts and ensure complete dimension analysis. No early conclusions allowed until ALL 6 dimensions verified with evidence. Must ask before deviating from process.
- **v1.4 (2026-09-16)**: Added CI/CD version management exclusion - project version in pom.xml should not be flagged. Enhanced requirement to present ALL findings (minor and major) without filtering.
- **v1.5 (2026-09-18)**: Added DTC_V2_ARCHITECTURE.md to auto-loaded context for both standard and migration reviews to ensure architectural compliance.
- **v1.6 (2026-09-21)**: Added JIRA validator assignment step - current user must be added as "assigned validator" during pre-review setup. Updated with correct field format: `customfield_14701` with `{"name": "USERNAME"}`.

---

## 🎯 Usage Guidelines

### For Each Review
1. **Load Context**: Reference this file before starting any code review
2. **Systematic Analysis**: Work through each section methodically
3. **Document Findings**: Prepare specific, actionable comments
4. **Seek Approval**: Present each proposed comment for approval
5. **Post Approved Comments**: Only post comments after explicit approval

### For Continuous Improvement
1. **Note Patterns**: Document new issues or patterns discovered
2. **Update Standards**: Propose updates to this file based on learnings
3. **Share Knowledge**: Communicate findings with team
4. **Refine Process**: Continuously improve review effectiveness
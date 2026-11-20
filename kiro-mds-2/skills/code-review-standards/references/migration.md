# V1→V2 Migration Review Standards

This file defines comprehensive review standards for DTC V1→V2 migration implementations, specifically for partner integration library extraction (e.g., Boku, NBC outbound libraries).

**Base Standards**: This file extends the [Code Review Standards](../SKILL.md). All base review processes, quality focus areas, and systematic review framework from that file apply here, plus the migration-specific additions below.

**Architecture Reference**: All migration reviews must comply with DTC V2 Architecture (`~/Desktop/ai-stuff/dtc-architecture/DTC_V2_ARCHITECTURE.md`) platform rules and service ownership boundaries.

---

## 🎯 Migration Context

### V1→V2 Migration Pattern
- **Source**: Existing partner logic in dedicated services (e.g., dtc-nbc-service)
- **Target**: Extracted partner integration libraries following established patterns
- **Reference Libraries**: dtc-amazon-outbound-lib, dtc-bango-entitlement-api-client, dtc-wbd-entitlement-api-client
- **Standards**: Follow dtc-partner-integration-playbook for integration patterns
- **Version**: V1 implementation (initial library version)

### Migration Goals
- **Partner Logic Isolation**: Move partner-specific logic from core services to dedicated libraries
- **Pattern Consistency**: Align with established Amazon/Bango/WBD library patterns  
- **Functionality Preservation**: Ensure existing V1 functionality is preserved
- **Service Extraction**: Proper separation from original service implementations

### **MANDATORY V1 Comparison Process**
- **Locate V1 Implementation**: Always identify and examine the existing V1 code in source services (e.g., direct-to-customer, dtc-*-service)
- **Compare All Interfaces**: Verify that all V1 service interfaces, methods, and capabilities are preserved in V2
- **Configuration Migration**: Ensure V1 configuration properties are properly migrated or equivalent alternatives provided
- **HTTP Client Patterns**: V1 uses reactive WebClient (legacy Spring standard), V2 should use RestClient with Java 25 virtual threads (current Spring Boot 4.x standard) - this architectural evolution is expected and correct
- **Error Handling**: Verify V1 error handling patterns are preserved or improved
- **Document Differences**: Explicitly document any architectural or behavioral changes from V1

---

## 📋 Enhanced Critical Review Checklist

### Migration-Specific Architecture Compliance
- **Service Ownership Boundaries**: Verify changes don't violate DTC v2 service responsibilities
- **Write API Protection**: Ensure no direct DocumentDB mutations outside Write API
- **Partner Logic Isolation**: Check that partner-specific logic stays in integration libraries
- **Command Flow Integrity**: Validate proper Kafka topic usage and ordering
- **Integration Playbook Compliance**: Follow documented partner integration standards

### Migration Data Safety & Consistency
- **Migration Safety**: Ensure existing V1 functionality is preserved during extraction
- **Backward Compatibility**: Schema evolution without breaking existing consumers
- **Watermark Ordering**: Proper Kafka offset-based ordering (not timestamps)
- **Idempotency**: At-least-once delivery handling in command processing

### Migration Testing Standards
- **Build Verification**: `mvn clean verify` passes before review completion
- **Coverage Target**: Striving for 100% test coverage
- **Integration Test Coverage**: Cucumber tests for end-to-end scenarios
- **TestContainers Setup**: Proper Kafka/Docker test infrastructure usage

---

## ⚠️ Migration-Specific Code Quality Focus

### Critical Code Quality Patterns
- **DRY Principle**: Extract common logic into reusable methods
  - Look for duplicated JsonNode navigation patterns
  - Extract null-safe utility methods for repeated operations
  - Consolidate similar error handling patterns

- **Partner API Patterns**: Look for duplicated logic that can be extracted into utilities
  - HTTP client configuration patterns
  - Response parsing and validation
  - Error mapping and exception handling

### Field Validation Patterns
- **Cross-Repository Field Verification**: When reviewing field additions (e.g., PatchableField enum updates):
  - Compare partner library field definitions against consuming service field enums
  - Verify ALL fields from library properties classes are represented in service enums
  - Distinguish between transient fields (prepare-phase only) vs persistent fields (stored in DB)
  - Cross-check latest versions of shared libraries (dtc-shared-domain-v2, dtc-schema) for field definitions

- **Transient vs Persistent Field Analysis**: 
  - **Transient fields**: Used temporarily during command processing (e.g., `ORIGINAL_PRODUCT_STATUS`)
  - **Persistent fields**: Stored in integrator properties and require PatchableField enum entries
  - **Validation method**: Check if field appears in `integratorUpdates` return values - if not, it's likely transient

- **Library Usage Investigation**: When field mismatches are found:
  - Read the actual library code to understand field usage context
  - Check if fields are used in `props.put()` temporarily vs `PropertyUpdates.set()` for persistence
  - Verify field usage patterns align with persistence requirements

---

## 📚 Documentation Standards

### Reference Documentation
- **Standard Template**: Use first outbound lib MR documentation as baseline
- **Review Process Context**: Reference back-and-forth from initial MR to understand expectations
- **V1 Code Cross-Reference**: Compare against existing V1 code to ensure completeness

### Documentation Scrutiny Checklist
- **Modification Review**: If documentation was changed, verify changes make sense and are accurate
- **Gap Analysis**: Identify holes where documentation should have been updated but wasn't
- **Code-Doc Alignment**: Ensure documentation matches actual implementation
- **Completeness Check**: All new features, APIs, configurations properly documented
- **Migration Coverage**: Document what was migrated from V1 and any changes made

### Required Documentation Elements
- **API Documentation**: All public methods, classes, and interfaces
- **Configuration Guide**: Required properties, environment setup
- **Integration Examples**: How to use the library in consuming services
- **Error Handling**: Expected exceptions and handling patterns
- **Testing Guide**: How to test integrations using the library

### Documentation Quality Checks
- **README Template Detection**: Flag when README.md is still the default GitLab template - requires replacement with proper library documentation
- **Cross-Library Consistency**: New libraries must follow established documentation patterns from reference libraries (e.g., dtc-amazon-outbound-lib/README.md)
- **JIRA Alignment**: Verify documentation requirements from JIRA tickets are fulfilled

---

## 🔄 Migration-Specific Reviews

### V1 Code Preservation Check
- **Feature Completeness**: All V1 functionality migrated to library
- **Business Logic Integrity**: No loss of business rules during extraction
- **Configuration Migration**: All necessary config moved from service to library
- **Error Handling Preservation**: Existing error patterns maintained or improved

### Library Pattern Consistency
- **Amazon Library Alignment**: Follow established patterns from dtc-amazon-outbound-lib
- **Bango Library Alignment**: Match patterns from dtc-bango-entitlement-api-client
- **WBD Library Alignment**: Consistent with dtc-wbd-entitlement-api-client patterns
- **Integration Playbook**: Adherence to documented partner integration standards

### Service Extraction Verification
- **Clean Separation**: Partner logic properly extracted from original service
- **Dependency Management**: Appropriate dependencies moved to library
- **Interface Design**: Clean API between service and library
- **Responsibility Boundaries**: Clear ownership of functionality

---

## 🚀 How to Use This File

### During MR Reviews
1. **Load Context**: Reference this file at start of V1→V2 migration reviews
2. **Systematic Check**: Go through each section of the checklist
3. **Cross-Reference**: Compare against reference implementations (Amazon/Bango/WBD)
4. **Document Gaps**: Note any missing elements for follow-up

### For Future Migrations
1. **Template Usage**: Use as starting point for other partner library extractions
2. **Standards Evolution**: Update based on lessons learned from each migration
3. **Team Alignment**: Share with team to ensure consistent review standards

### Review Process Integration
1. **Pre-Review**: Load context from this file
2. **During Review**: Apply systematic checklist approach
3. **Post-Review**: Update file if new patterns or issues are discovered

---

## 📝 Version History

- **v1.0 (2026-09-10)**: Initial creation for Boku outbound library migration review
- **v1.1 (2026-09-16)**: Added mandatory V1 comparison process requirement. All migration reviews must compare against existing V1 implementation to verify functionality preservation and document architectural changes.
- **v1.2 (2026-09-18)**: Added explicit DTC V2 Architecture reference requirement to ensure migration reviews comply with platform rules and service ownership boundaries.
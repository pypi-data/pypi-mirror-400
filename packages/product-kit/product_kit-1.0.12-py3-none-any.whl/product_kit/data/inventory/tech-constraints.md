# 🚧 [PRODUCT_NAME] Technical Constraints
<!-- Example: Product Kit Technical Constraints, TaskFlow Technical Constraints, etc. -->

> "[TAGLINE]"
<!-- Example: "Know the limits before you design." -->

## Purpose
This document catalogs all known technical limitations, platform constraints, and dependencies. Use this to ensure new feature designs are technically feasible and don't violate system boundaries.

---

## 1. Platform Limitations
*Constraints imposed by the platforms we support.*

### [PLATFORM_1_ICON] [PLATFORM_1_NAME]
<!-- Example: 📱 Mobile App -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]
-   **Workaround**: [WORKAROUND_SOLUTION]

<!-- Example:
### 📱 Mobile App
-   **Constraint**: The mobile app is a wrapper (React Native) around the web view for some pages.
-   **Impact**: Complex interactions (like drag-and-drop) feel janky on mobile.
-   **Workaround**: Use "Tap to Move" menus instead of drag-and-drop on mobile. Consider native implementation for critical flows.
-->

### [PLATFORM_2_ICON] [PLATFORM_2_NAME]
<!-- Example: 🌐 Browser Support -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]
-   **Policy**: [POLICY_STATEMENT]

<!-- Example:
### 🌐 Browser Support
-   **Constraint**: We do NOT support Internet Explorer 11 or legacy Edge.
-   **Impact**: Enterprise clients on legacy systems cannot use the app.
-   **Policy**: Support last 2 versions of Chrome, Firefox, Safari, and Chromium Edge only.
-->

### [PLATFORM_3_ICON] [PLATFORM_3_NAME]
<!-- Example: 💻 Desktop App -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]

<!-- Example:
### 💻 Desktop App
-   **Constraint**: Electron app size is 200MB+ due to bundled runtime.
-   **Impact**: Slow downloads and storage concerns for users with limited bandwidth/disk space.
-->

---

## 2. Performance Limits
*Technical boundaries that affect user experience.*

### [PERFORMANCE_AREA_1_ICON] [PERFORMANCE_AREA_1_NAME]
<!-- Example: 📊 Data Volume -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Reason**: [TECHNICAL_REASON]
-   **Error Handling**: [ERROR_MESSAGE_OR_BEHAVIOR]

<!-- Example:
### 📊 Data Volume
-   **Constraint**: A project cannot have more than 10,000 tasks.
-   **Reason**: Frontend rendering performance degrades significantly beyond this limit (virtual scrolling not implemented).
-   **Error Handling**: Show error: "Project limit reached. Please archive old tasks or split into multiple projects."
-->

### [PERFORMANCE_AREA_2_ICON] [PERFORMANCE_AREA_2_NAME]
<!-- Example: ⏱️ Real-time Updates -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]
-   **Workaround**: [WORKAROUND_SOLUTION]

<!-- Example:
### ⏱️ Real-time Updates
-   **Constraint**: Updates are not instant (polling every 30s, not WebSocket-based).
-   **Impact**: Two users editing the same task might overwrite each other's changes.
-   **Workaround**: "Last write wins" strategy. Show warning when conflict detected. WebSocket upgrade planned for Q3.
-->

### [PERFORMANCE_AREA_3_ICON] [PERFORMANCE_AREA_3_NAME]
<!-- Example: 🔍 Search Performance -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Reason**: [TECHNICAL_REASON]

<!-- Example:
### 🔍 Search Performance
-   **Constraint**: Full-text search is limited to 1,000 results.
-   **Reason**: Elasticsearch query timeout set to 5 seconds to prevent resource exhaustion.
-->

---

## 3. Third-Party Dependencies
*External services and their limitations.*

### [SERVICE_1_ICON] [SERVICE_1_NAME] ([VENDOR_NAME])
<!-- Example: 📧 Email (SendGrid) -->
-   **Constraint**: [RATE_LIMIT_OR_CONSTRAINT]
-   **Impact**: [IMPACT_DESCRIPTION]
-   **Mitigation**: [MITIGATION_STRATEGY]

<!-- Example:
### 📧 Email (SendGrid)
-   **Constraint**: Max 100 emails/minute per workspace (tier-based).
-   **Impact**: Bulk invites might be delayed or queued.
-   **Mitigation**: Implement email queue with rate limiting. Show progress indicator to users.
-->

### [SERVICE_2_ICON] [SERVICE_2_NAME] ([VENDOR_NAME])
<!-- Example: ☁️ File Storage (AWS S3) -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]
-   **Policy**: [POLICY_STATEMENT]

<!-- Example:
### ☁️ File Storage (AWS S3)
-   **Constraint**: Max file size upload is 25MB per file.
-   **Impact**: Users cannot upload large video files or high-res design files.
-   **Policy**: Reject files > 25MB with clear error message suggesting compression or alternative sharing methods.
-->

### [SERVICE_3_ICON] [SERVICE_3_NAME] ([VENDOR_NAME])
<!-- Example: 💳 Payment Processing (Stripe) -->
-   **Constraint**: [CONSTRAINT_DESCRIPTION]
-   **Impact**: [IMPACT_DESCRIPTION]

<!-- Example:
### 💳 Payment Processing (Stripe)
-   **Constraint**: Webhooks may be delayed up to 30 seconds under high load.
-   **Impact**: Account upgrade/downgrade may not be instant.
-->

---

## 4. Infrastructure Constraints
*Hosting and infrastructure limitations.*

### Database
-   **Type**: [DATABASE_TYPE]
-   **Constraints**:
    -   [CONSTRAINT_1]
    -   [CONSTRAINT_2]

<!-- Example:
### Database
-   **Type**: PostgreSQL 15
-   **Constraints**:
    -   Max connection pool: 100 connections
    -   Query timeout: 30 seconds
    -   Max row size: 8KB (TOAST storage for larger fields)
    -   No full-text search on encrypted fields
-->

### API Rate Limits
-   **Rate Limit**: [RATE_LIMIT_DESCRIPTION]
-   **Enforcement**: [ENFORCEMENT_METHOD]
-   **Exemptions**: [EXEMPTION_RULES]

<!-- Example:
### API Rate Limits
-   **Rate Limit**: 1,000 requests per hour per API key (10,000 for Enterprise)
-   **Enforcement**: HTTP 429 with Retry-After header
-   **Exemptions**: Internal services and webhooks are exempt
-->

### Storage Quotas
-   **Free Tier**: [FREE_QUOTA]
-   **Paid Tiers**: [PAID_QUOTA]
-   **Overage**: [OVERAGE_HANDLING]

<!-- Example:
### Storage Quotas
-   **Free Tier**: 1GB per workspace
-   **Paid Tiers**: Pro (50GB), Enterprise (Unlimited)
-   **Overage**: Block new uploads, show upgrade prompt
-->

---

## 5. Security & Compliance Constraints
*Regulatory and security requirements.*

### Data Residency
-   **Constraint**: [RESIDENCY_REQUIREMENT]
-   **Regions**: [SUPPORTED_REGIONS]

<!-- Example:
### Data Residency
-   **Constraint**: GDPR compliance requires EU customer data to stay in EU data centers.
-   **Regions**: US (default), EU (opt-in), Asia-Pacific (planned)
-->

### Authentication
-   **Constraint**: [AUTH_CONSTRAINT]
-   **Impact**: [IMPACT_DESCRIPTION]

<!-- Example:
### Authentication
-   **Constraint**: SSO (SAML/OIDC) only available for Enterprise tier.
-   **Impact**: Mid-market customers cannot use company IdP, must use email/password or OAuth.
-->

### Data Encryption
-   **At Rest**: [ENCRYPTION_METHOD]
-   **In Transit**: [ENCRYPTION_METHOD]
-   **Limitations**: [LIMITATIONS]

<!-- Example:
### Data Encryption
-   **At Rest**: AES-256 (database-level encryption)
-   **In Transit**: TLS 1.3
-   **Limitations**: Cannot perform full-text search on encrypted fields; requires decryption first
-->

---

## 6. Known Technical Debt
*Existing issues that limit future development.*

### [DEBT_ITEM_1]
-   **Issue**: [ISSUE_DESCRIPTION]
-   **Impact**: [IMPACT_ON_FEATURES]
-   **Planned Resolution**: [RESOLUTION_PLAN]

<!-- Example:
### Legacy Permissions System
-   **Issue**: Current ACL system uses JSONB field, making queries slow and complex.
-   **Impact**: Cannot implement fine-grained permissions or role inheritance without major refactor.
-   **Planned Resolution**: Q2 2026 - Migrate to graph-based permissions model
-->

### [DEBT_ITEM_2]
-   **Issue**: [ISSUE_DESCRIPTION]
-   **Impact**: [IMPACT_ON_FEATURES]

<!-- Example:
### Monolithic Codebase
-   **Issue**: All features in single repository makes CI/CD slow (20+ min builds).
-   **Impact**: Slows down development velocity and makes feature flags complex.
-->

---

## 7. Deprecated Technologies
*Technologies being phased out.*

### ~~[DEPRECATED_TECH_1]~~
-   **Status**: [DEPRECATION_STATUS]
-   **Replacement**: [REPLACEMENT_TECH]
-   **Timeline**: [SUNSET_TIMELINE]

<!-- Example:
### ~~REST API v1~~
-   **Status**: Deprecated since 2025-06-01
-   **Replacement**: GraphQL API
-   **Timeline**: Complete shutdown by 2026-06-01. All integrations must migrate.
-->

---

## 8. Future Constraints (Anticipated)
*Known limitations we'll face soon.*

-   **[FUTURE_CONSTRAINT_1]**: [DESCRIPTION]
-   **[FUTURE_CONSTRAINT_2]**: [DESCRIPTION]

<!-- Example:
-   **Database Scaling**: Current single-instance Postgres will hit limits at ~100k active workspaces (estimated Q3 2026). Need sharding strategy.
-   **CDN Costs**: File serving costs will exceed $10k/month at current growth rate by Q4 2026. Consider CloudFlare R2 migration.
-->

---

**Version**: [CONSTRAINTS_VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Version: 3.0.0 | Last Updated: 2026-01-02 -->

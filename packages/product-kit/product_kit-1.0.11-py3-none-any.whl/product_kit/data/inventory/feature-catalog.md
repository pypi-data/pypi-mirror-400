# 📚 [PRODUCT_NAME] Feature Catalog
<!-- Example: Product Kit Feature Catalog, TaskFlow Feature Catalog, etc. -->

> "[TAGLINE]"
<!-- Example: "The encyclopedia of 'How it works today'." -->

## Purpose
This document catalogs all existing features and their current business logic. Use this to prevent new requirements from conflicting with existing functionality and to identify opportunities for consolidation or deprecation.

---

## 1. [MODULE_1_NAME]
<!-- Example: Authentication Module -->

### [FEATURE_1_ICON] [FEATURE_1_NAME]
<!-- Example: 🔐 Login -->
-   **Description**: [FEATURE_DESCRIPTION]
-   **Logic**:
    -   [LOGIC_POINT_1]
    -   [LOGIC_POINT_2]
    -   [LOGIC_POINT_3]
-   **Dependencies**: [DEPENDENCIES]
-   **Known Issues**: [KNOWN_ISSUES]

<!-- Example:
### 🔐 Login
-   **Description**: Allows users to access their account.
-   **Logic**:
    -   Supports Email/Password and Google OAuth.
    -   Locks account after 5 failed attempts (30 min cooldown).
    -   Session timeout: 7 days.
-   **Dependencies**: Redis for session storage
-   **Known Issues**: OAuth sometimes fails on Safari private mode
-->

### [FEATURE_2_ICON] [FEATURE_2_NAME]
<!-- Example: 🔑 Password Reset -->
-   **Description**: [FEATURE_DESCRIPTION]
-   **Logic**:
    -   [LOGIC_POINT_1]
    -   [LOGIC_POINT_2]
-   **Dependencies**: [DEPENDENCIES]

<!-- Example:
### 🔑 Password Reset
-   **Description**: Self-serve password recovery.
-   **Logic**:
    -   Sends a magic link (valid for 1 hour).
    -   Link is one-time use only.
-   **Dependencies**: SendGrid for email delivery
-->

---

## 2. [MODULE_2_NAME]
<!-- Example: Billing Module -->

### [FEATURE_3_ICON] [FEATURE_3_NAME]
<!-- Example: 💳 Subscription Management -->
-   **Description**: [FEATURE_DESCRIPTION]
-   **Logic**:
    -   **[SUB_FEATURE_1]**: [SUB_FEATURE_DESCRIPTION]
    -   **[SUB_FEATURE_2]**: [SUB_FEATURE_DESCRIPTION]
-   **Edge Cases**: [EDGE_CASES]

<!-- Example:
### 💳 Subscription Management
-   **Description**: Upgrade/Downgrade plans.
-   **Logic**:
    -   **Proration**: Upgrades are charged immediately (prorated). Downgrades take effect at the end of the cycle.
    -   **Failed Payments**: Retry 3 times over 7 days, then lock account.
-   **Edge Cases**: If user downgrades and exceeds new tier limits, features are soft-disabled with warning banner
-->

---

## 3. [MODULE_3_NAME]
<!-- Example: Core Features -->

### [FEATURE_4_ICON] [FEATURE_4_NAME]
<!-- Example: 📝 Task Management -->
-   **Description**: [FEATURE_DESCRIPTION]
-   **Logic**:
    -   **[FIELD_1]**: [FIELD_CONSTRAINTS]
    -   **[FIELD_2]**: [FIELD_CONSTRAINTS]
    -   **[FIELD_3]**: [FIELD_CONSTRAINTS]
-   **Permissions**: [PERMISSION_RULES]
-   **Validation**: [VALIDATION_RULES]

<!-- Example:
### 📝 Task Management
-   **Description**: Create, edit, and move tasks.
-   **Logic**:
    -   **Task Title**: Max 140 chars, required.
    -   **Description**: Markdown supported, max 10,000 chars.
    -   **Assignee**: Must be a member of the workspace.
    -   **Due Date**: Cannot be in the past.
-   **Permissions**: Only Owners and Members can edit. Viewers are read-only.
-   **Validation**: Title cannot be empty or contain only whitespace
-->

### [FEATURE_5_ICON] [FEATURE_5_NAME]
<!-- Example: 🔔 Notifications -->
-   **Description**: [FEATURE_DESCRIPTION]
-   **Logic**:
    -   **Triggered when**: [TRIGGER_CONDITIONS]
    -   **[BEHAVIOR_ASPECT]**: [BEHAVIOR_DESCRIPTION]
-   **User Preferences**: [PREFERENCE_OPTIONS]

<!-- Example:
### 🔔 Notifications
-   **Description**: In-app and email alerts.
-   **Logic**:
    -   **Triggered when**: Assigned to a task, Mentioned in a comment, Task due date approaching.
    -   **Batching**: Email notifications are batched every 15 mins to prevent spam.
-   **User Preferences**: Users can disable per-event-type or globally
-->

---

## 4. Feature Status
*Track feature maturity and deprecation plans.*

| Feature | Status | GA Date | Deprecation Date | Notes |
| :--- | :--- | :--- | :--- | :--- |
| [FEATURE_NAME] | [STATUS] | [GA_DATE] | [DEPRECATION_DATE] | [NOTES] |

<!-- Example:
| Feature | Status | GA Date | Deprecation Date | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Login (OAuth) | GA | 2024-03-15 | - | Stable |
| Old Dashboard | Deprecated | 2023-01-20 | 2026-06-30 | Replaced by New Dashboard |
| Task Templates | Beta | 2025-11-01 | - | Collecting feedback |
| CSV Export | Alpha | 2025-12-15 | - | Internal only |

Status values: Alpha, Beta, GA (Generally Available), Deprecated, Sunset
-->

---

## 5. Feature Dependencies Map
*Which features rely on each other.*

```
[FEATURE_A]
├── depends on [FEATURE_B]
├── depends on [FEATURE_C]
└── [FEATURE_D] depends on this
```

<!-- Example:
```
Task Management
├── depends on Authentication (user context)
├── depends on Workspace Management (project context)
└── Notifications depend on this
    └── Email Delivery depends on this
```
-->

---

## 6. Deprecated Features
*Features that are being phased out.*

### ~~[DEPRECATED_FEATURE_NAME]~~
-   **Deprecated On**: [DEPRECATION_DATE]
-   **Reason**: [DEPRECATION_REASON]
-   **Migration Path**: [MIGRATION_INSTRUCTIONS]
-   **Sunset Date**: [SUNSET_DATE]

<!-- Example:
### ~~Classic Editor~~
-   **Deprecated On**: 2025-09-01
-   **Reason**: Poor mobile experience, difficult to maintain
-   **Migration Path**: Users automatically migrated to New Editor. Old data compatible.
-   **Sunset Date**: 2026-03-01 (all API endpoints will be removed)
-->

---

**Version**: [CATALOG_VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Version: 4.1.0 | Last Updated: 2026-01-02 -->

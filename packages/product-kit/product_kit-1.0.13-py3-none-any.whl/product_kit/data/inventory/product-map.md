# 🗺️ [PRODUCT_NAME] Product Map
<!-- Example: Product Kit Product Map, TaskFlow Product Map, etc. -->

> "[TAGLINE]"
<!-- Example: "A bird's eye view of the entire application." -->

## Purpose
This document maps the product's navigation structure, user flows, and module organization. Use this to understand how features connect and where new functionality should be placed in the information architecture.

---

## 1. Site Map (Navigation Structure)
*High-level view of the application's pages and hierarchy.*

### [SECTION_1_ICON] [SECTION_1_NAME]
<!-- Example: 🏠 Home / Dashboard -->
-   **[COMPONENT_1]**: [COMPONENT_DESCRIPTION]
-   **[COMPONENT_2]**: [COMPONENT_DESCRIPTION]
-   **[COMPONENT_3]**: [COMPONENT_DESCRIPTION]

<!-- Example:
### 🏠 Home / Dashboard
-   **Overview Widget**: Summary of key metrics (active tasks, upcoming deadlines).
-   **Recent Activity**: List of latest actions (last 10 items).
-   **Quick Actions**: "Create New Project", "Invite Member", "View Reports".
-->

### [SECTION_2_ICON] [SECTION_2_NAME]
<!-- Example: 📂 Projects -->
-   **[VIEW_1]**: [VIEW_DESCRIPTION]
-   **[VIEW_2]**: [VIEW_DESCRIPTION]
    -   **[SUB_VIEW_1]**: [SUB_VIEW_DESCRIPTION]
    -   **[SUB_VIEW_2]**: [SUB_VIEW_DESCRIPTION]
    -   **[SUB_VIEW_3]**: [SUB_VIEW_DESCRIPTION]

<!-- Example:
### 📂 Projects
-   **Project List**: Table view of all projects with filters (status, owner, date).
-   **Project Detail**:
    -   **Kanban View**: Drag-and-drop tasks across columns.
    -   **List View**: Sortable table with advanced filters.
    -   **Timeline View**: Gantt-style calendar view.
    -   **Settings**: Rename, Archive, Delete project.
-->

### [SECTION_3_ICON] [SECTION_3_NAME]
<!-- Example: ⚙️ Settings -->
-   **[SETTINGS_CATEGORY_1]**: [SETTINGS_DESCRIPTION]
-   **[SETTINGS_CATEGORY_2]**: [SETTINGS_DESCRIPTION]
-   **[SETTINGS_CATEGORY_3]**: [SETTINGS_DESCRIPTION]

<!-- Example:
### ⚙️ Settings
-   **Profile**: Change password, update avatar, notification preferences.
-   **Billing**: View invoices, update credit card, manage subscription.
-   **Team**: Manage members and permissions, invite/remove users.
-   **Integrations**: Connect third-party tools (Slack, GitHub, etc.).
-->

---

## 2. User Flows
*Step-by-step journeys through key features.*

### [FLOW_1_ICON] [FLOW_1_NAME]
<!-- Example: 🟢 Onboarding Flow -->
1.  **[STEP_1]** -> [ACTION_1]
2.  **[STEP_2]** -> [ACTION_2]
3.  **[STEP_3]** -> [ACTION_3]
4.  **[STEP_4]** -> [ACTION_4] -> [OUTCOME]

<!-- Example:
### 🟢 Onboarding Flow
1.  **Landing Page** -> Click "Sign Up".
2.  **Signup Form** -> Enter Email/Password -> Submit.
3.  **Email Verification** -> Click link in email.
4.  **Setup Wizard** -> Name Workspace -> Choose Template -> Invite Team -> Done.
5.  **Dashboard** -> Show success message and tutorial tooltip.
-->

### [FLOW_2_ICON] [FLOW_2_NAME]
<!-- Example: 🔵 Create Project Flow -->
1.  **[STEP_1]** -> [ACTION_1]
2.  **[STEP_2]** -> [ACTION_2]
3.  **[STEP_3]** -> [OUTCOME]

<!-- Example:
### 🔵 Create Project Flow
1.  **Dashboard** -> Click "New Project" button.
2.  **Modal** -> Enter Project Name -> Select Template (or start blank) -> Confirm.
3.  **Project View** -> Redirect to empty project with onboarding tips.
-->

### [FLOW_3_ICON] [FLOW_3_NAME]
<!-- Example: 🟡 Task Assignment Flow -->
1.  **[STEP_1]** -> [ACTION_1]
2.  **[STEP_2]** -> [ACTION_2]
3.  **[STEP_3]** -> [OUTCOME]

<!-- Example:
### 🟡 Task Assignment Flow
1.  **Task Detail** -> Click "Assign" dropdown.
2.  **Member Picker** -> Search or select from list -> Confirm.
3.  **Notification** -> Assignee receives in-app + email notification.
-->

---

## 3. Information Architecture
*Content organization and grouping.*

```
[APP_NAME]
├── [SECTION_1]
│   ├── [SUBSECTION_1_1]
│   ├── [SUBSECTION_1_2]
│   └── [SUBSECTION_1_3]
├── [SECTION_2]
│   ├── [SUBSECTION_2_1]
│   └── [SUBSECTION_2_2]
└── [SECTION_3]
    ├── [SUBSECTION_3_1]
    ├── [SUBSECTION_3_2]
    └── [SUBSECTION_3_3]
```

<!-- Example:
```
App
├── Dashboard
│   ├── Overview Metrics
│   ├── Recent Activity Feed
│   └── Quick Actions Panel
├── Projects
│   ├── All Projects List
│   └── Project Detail
│       ├── Kanban View
│       ├── List View
│       ├── Timeline View
│       └── Project Settings
├── Team
│   ├── Members List
│   ├── Invitations Pending
│   └── Roles & Permissions
└── Settings
    ├── Personal Profile
    ├── Workspace Settings
    ├── Billing & Plans
    └── Integrations
```
-->

---

## 4. Navigation Patterns
*How users move through the app.*

### Primary Navigation
-   **Type**: [NAV_TYPE]
-   **Location**: [NAV_LOCATION]
-   **Items**: [NAV_ITEMS]

<!-- Example:
-   **Type**: Persistent sidebar (collapsible on mobile)
-   **Location**: Left side of screen
-   **Items**: Dashboard, Projects, Team, Settings, Help
-->

### Secondary Navigation
-   **Type**: [NAV_TYPE]
-   **Context**: [NAV_CONTEXT]

<!-- Example:
-   **Type**: Breadcrumbs
-   **Context**: Shows hierarchy (Workspace > Project > Task)
-->

### Tertiary Navigation
-   **Type**: [NAV_TYPE]
-   **Context**: [NAV_CONTEXT]

<!-- Example:
-   **Type**: Tabs
-   **Context**: Within Project Detail (Kanban / List / Timeline)
-->

---

## 5. Module Ownership
*Who owns what? Useful for cross-functional alignment.*

| Module | Product Owner | Tech Lead | Design Owner |
| :--- | :--- | :--- | :--- |
| **[MODULE_1]** | [NAME] | [NAME] | [NAME] |
| **[MODULE_2]** | [NAME] | [NAME] | [NAME] |
| **[MODULE_3]** | [NAME] | [NAME] | [NAME] |

<!-- Example:
| Module | Product Owner | Tech Lead | Design Owner |
| :--- | :--- | :--- | :--- |
| **Auth & Onboarding** | Sarah Chen | David Kumar | Emily Wong |
| **Core Experience (Projects)** | Michael Brown | Lisa Park | Emily Wong |
| **Billing & Settings** | Sarah Chen | James Wilson | Alex Thompson |
| **Notifications** | Michael Brown | David Kumar | Alex Thompson |
-->

---

## 6. Page Inventory
*Complete list of all pages/views in the application.*

| Page Path | Purpose | Access Level | Status |
| :--- | :--- | :--- | :--- |
| [PAGE_PATH] | [PURPOSE] | [ACCESS_LEVEL] | [STATUS] |

<!-- Example:
| Page Path | Purpose | Access Level | Status |
| :--- | :--- | :--- | :--- |
| `/` | Marketing landing page | Public | Live |
| `/dashboard` | User home | Authenticated | Live |
| `/projects` | Project list | Member+ | Live |
| `/projects/:id` | Project detail | Member+ | Live |
| `/settings/billing` | Billing management | Owner only | Live |
| `/admin` | Admin panel | Admin only | Beta |
| `/reports` | Analytics dashboard | Pro plan+ | Planned Q2 |
-->

---

**Version**: [PRODUCT_MAP_VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Version: 2.3.0 | Last Updated: 2026-01-02 -->

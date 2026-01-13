# 📜 [PRODUCT_NAME] Constitution
<!-- Example: Product Kit Constitution, TaskFlow Product Constitution, etc. -->

> "[TAGLINE]"
<!-- Example: "The code is the law, but this document is the spirit." -->

## 🎯 Purpose
This document serves as the **single source of truth** for our product principles, non-negotiable standards, and decision-making frameworks.

It works in tandem with **`context/product-vision.md`**:
- **Product Vision**: Defines **WHAT** we are building (Strategy & Objectives).
- **Constitution**: Defines **HOW** we build it (Quality, Standards, & Principles).

It is used by the AI to "lint" new requirements and ensure consistency across all PRDs and Epics.

---

## 🧠 Core Principles
*Guiding values that influence every product decision.*

### [PRINCIPLE_1_NAME]
<!-- Example: User-Centricity First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: We solve real user problems, not just build features. Every PRD must start with a validated user need. -->

### [PRINCIPLE_2_NAME]
<!-- Example: Simplicity over Complexity -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: If a feature requires a 3-page manual, it's too complex. Default to "less is more." -->

### [PRINCIPLE_3_NAME]
<!-- Example: Data-Informed, Not Data-Driven -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: We use data to guide us, but we also rely on product intuition and qualitative feedback. -->

### [PRINCIPLE_4_NAME]
<!-- Example: Accessibility is Mandatory -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: All new UI components must meet WCAG 2.1 AA standards. -->

### [PRINCIPLE_5_NAME]
<!-- Example: Performance is a Feature -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: No page load should exceed 2 seconds on 4G networks. -->

---

## 🛡️ Non-Negotiable Standards
*Hard rules that every feature must obey. The AI will flag violations.*

### [STANDARD_CATEGORY_1]
<!-- Example: UX/UI Standards -->

#### [STANDARD_1_1_NAME]
<!-- Example: Mobile Responsiveness -->
[STANDARD_1_1_DESCRIPTION]
<!-- Example: All views must be fully functional on mobile devices (320px width min). -->

#### [STANDARD_1_2_NAME]
<!-- Example: Error States -->
[STANDARD_1_2_DESCRIPTION]
<!-- Example: Every input field and API interaction must have a defined error state. -->

#### [STANDARD_1_3_NAME]
<!-- Example: Empty States -->
[STANDARD_1_3_DESCRIPTION]
<!-- Example: Every list or dashboard must have a designed "zero data" state. -->

### [STANDARD_CATEGORY_2]
<!-- Example: Design & Content Standards -->

#### [STANDARD_2_1_NAME]
<!-- Example: Copywriting Style -->
[STANDARD_2_1_DESCRIPTION]
<!-- Example:
    - **Voice**: Professional, human, and concise. Avoid robot-speak (e.g., use "We couldn't find that" instead of "404 Error: Object not found").
    - **Action-Oriented**: Use active verbs for buttons (e.g., "Save Profile" vs "Submit").
-->

#### [STANDARD_2_2_NAME]
<!-- Example: Color Semantics -->
[STANDARD_2_2_DESCRIPTION]
<!-- Example:
    - **Primary**: Key actions (Submit, Continue).
    - **Destructive**: Irreversible actions (Delete, Cancel).
    - **Neutral**: Secondary actions, borders, backgrounds.
-->

#### [STANDARD_2_3_NAME]
<!-- Example: UI Representation (ASCII) -->
[STANDARD_2_3_DESCRIPTION]
<!-- Example: To keep specs version-controllable and focused on *structure* over *pixels*, use **Text-based UI (ASCII)** for wireframes.

    *Example:*
    ```text
    __________________________________________________________
    |                                                        |
    |  [🏠] Home    [👤] Profile    [⚙️] Settings    [🔍] ____ |
    |________________________________________________________|
    |                                                        |
    |  Account Information                                   |
    |  -------------------                                   |
    |                                                        |
    |  Username:   |____________________________|            |
    |                                                        |
    |  Password:   |****************************|            |
    |                                                        |
    |  Role:       [ Editor            v ]                   |
    |                                                        |
    |              [  CANCEL  ]    [** SAVE **]              |
    |________________________________________________________|
    ```
-->

### [STANDARD_CATEGORY_3]
<!-- Example: Technical Standards -->

#### [STANDARD_3_1_NAME]
<!-- Example: Offline Mode -->
[STANDARD_3_1_DESCRIPTION]
<!-- Example: Critical user flows (e.g., viewing saved data) must work without an internet connection. -->

#### [STANDARD_3_2_NAME]
<!-- Example: Security -->
[STANDARD_3_2_DESCRIPTION]
<!-- Example: No PII (Personally Identifiable Information) shall be logged in plain text. -->

#### [STANDARD_3_3_NAME]
<!-- Example: Scalability -->
[STANDARD_3_3_DESCRIPTION]
<!-- Example: Features must be designed to handle 10x current traffic volume. -->

### [STANDARD_CATEGORY_4]
<!-- Example: Process Standards -->

#### [STANDARD_4_1_NAME]
<!-- Example: Success Metrics -->
[STANDARD_4_1_DESCRIPTION]
<!-- Example: No Epic can be started without defined Success Metrics (e.g., "Increase conversion by 5%"). -->

#### [STANDARD_4_2_NAME]
<!-- Example: Analytics -->
[STANDARD_4_2_DESCRIPTION]
<!-- Example: Every user interaction (click, view, submit) must have a tracking event defined. -->

#### [STANDARD_4_3_NAME]
<!-- Example: Rollout Plan -->
[STANDARD_4_3_DESCRIPTION]
<!-- Example: Every feature must have a phased rollout strategy (Internal -> Beta -> Public). -->

---

## ⚖️ Decision Frameworks
*How we make trade-offs.*

### [FRAMEWORK_1_NAME]
<!-- Example: RICE Scoring (Prioritization) -->
[FRAMEWORK_1_DESCRIPTION]
<!-- Example:
-   **Reach**: How many users will this impact?
-   **Impact**: How much will this move the needle?
-   **Confidence**: How sure are we about our estimates?
-   **Effort**: How many person-weeks will this take?
-->

### [FRAMEWORK_2_NAME]
<!-- Example: Build vs. Buy -->
[FRAMEWORK_2_DESCRIPTION]
<!-- Example:
-   If it's a core differentiator -> **Build**.
-   If it's a commodity (e.g., chat, payments) -> **Buy/Integrate**.
-->

---

## 🔄 Governance & Review

### Review Cycle
[REVIEW_CYCLE_DESCRIPTION]
<!-- Example:
-   **Last Updated**: [Date]
-   **Review Frequency**: Quarterly
-   **Owner**: Head of Product
-->

### Constitution Authority
[AUTHORITY_RULES]
<!-- Example:
- This Constitution supersedes all other product practices and guidelines.
- Amendments require: Documentation of change, Approval from product leadership, Migration plan for affected in-flight work.
- All PRDs/Epics must verify compliance with this Constitution.
-->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 1.0.0 | Ratified: 2025-01-15 | Last Amended: 2026-01-02 -->

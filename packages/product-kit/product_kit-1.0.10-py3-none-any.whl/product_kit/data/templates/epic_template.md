# 🚩 Epic Template
<!-- Document Title: [EPIC NAME] -->
<!-- 
📁 File Location Convention for Multiple Epics per BRD:
Save this file as: requirements/XXX-feature-name/epic-NNN-epic-title.md

Examples for a single BRD split into multiple epics:
  requirements/001-payment-system/epic-001-core-payments.md
  requirements/001-payment-system/epic-002-payment-methods.md
  requirements/001-payment-system/epic-003-refund-workflow.md
  
  requirements/042-user-dashboard/epic-001-dashboard-foundation.md
  requirements/042-user-dashboard/epic-002-analytics-widgets.md

Why multiple epics per BRD?
- Keeps each epic focused and manageable (typically 2-4 weeks per epic)
- Allows parallel team execution
- Enables incremental delivery and faster feedback
- Easier to track progress and dependencies
- Prevents epic scope creep

When to split a BRD into multiple epics:
✅ Estimated effort > 6 weeks
✅ Multiple distinct user workflows involved
✅ Can be delivered in sequential phases with independent value
✅ Multiple teams or specializations needed
✅ Clear boundaries between technical components

Epic naming pattern: epic-NNN-[phase/component]-[focus].md
-->

| Metadata | Details |
| :--- | :--- |
| **Epic Name** | [EPIC_NAME] |
| **Epic ID** | [EPIC_ID] |
| **BRD Reference** | [Link to parent BRD](../XXX-feature-name/brd.md) |
| **Epic Sequence** | [EPIC_NUMBER] of [TOTAL_EPICS] |
| **Owner** | [OWNER_NAME] |
| **Status** | [STATUS] |
| **Quarter** | [TARGET_QUARTER] |
| **Start Date** | [START_DATE] |
| **Target Completion** | [TARGET_DATE] |

<!-- Example:
| **Epic Name** | Payment Core Infrastructure |
| **Epic ID** | EPIC-001.1 |
| **BRD Reference** | [Payment System BRD](../001-payment-system/brd.md) |
| **Epic Sequence** | 1 of 3 |
| **Owner** | Sarah Chen |
| **Status** | `Planning` / `In Progress` / `Done` / `On Hold` |
| **Quarter** | Q2 2026 |
| **Start Date** | 2026-04-01 |
| **Target Completion** | 2026-04-30 |
-->

### Related Epics
*Other epics in this BRD (for context and sequencing)*

| Epic | Status | Dependencies | Target Date |
| :--- | :--- | :--- | :--- |
| [RELATED_EPIC_1] | [STATUS_1] | [DEPENDENCIES_1] | [DATE_1] |
| [RELATED_EPIC_2] | [STATUS_2] | [DEPENDENCIES_2] | [DATE_2] |

<!-- Example:
| Epic | Status | Dependencies | Target Date |
| :--- | :--- | :--- | :--- |
| [Epic 1: Core Payment Infrastructure](epic-001-core-payments.md) | ✅ Done | None | 2026-04-30 |
| **[Epic 2: Payment Methods (This Epic)](epic-002-payment-methods.md)** | 🟡 In Progress | Epic 1 | 2026-05-31 |
| [Epic 3: Refund Workflow](epic-003-refund-workflow.md) | ⚪ Not Started | Epic 2 | 2026-06-30 |
-->

---

## 1. Overview
*A focused summary of this specific epic (not the entire BRD).*

### 1.1 Epic Scope
*What does THIS epic specifically cover? How does it fit into the larger BRD?*

[EPIC_SCOPE_DESCRIPTION]

<!-- Example: \"This epic (1 of 3) establishes the core payment infrastructure including the payment gateway integration, transaction processing, and basic payment logging. It provides the foundation for subsequent epics covering payment methods and refund workflows.\" -->

### 1.2 Objective
*What is the specific goal of THIS epic?*

[OBJECTIVE_DESCRIPTION]

<!-- Example: \"Build the foundational payment processing system that can handle credit card transactions with 99.9% uptime and process payments within 3 seconds.\" -->

### 1.3 Hypothesis
*If we do X (in this epic), then Y will happen.*

[HYPOTHESIS_STATEMENT]

<!-- Example: \"If we integrate with Stripe as our primary payment gateway and implement proper error handling, we can process credit card payments reliably and reduce payment failures from the current 15% (manual process) to under 2%.\" -->

### 1.4 Strategic Alignment
*How does this epic support the overall BRD objective and Product Vision?*

-   **BRD Objective**: [BRD_OBJECTIVE]
-   **Strategic Pillar**: [STRATEGIC_PILLAR]
-   **Business Goal**: [BUSINESS_GOAL]
-   **Persona Impact**: [PERSONA_IMPACT]

<!-- Example:
-   **BRD Objective**: Enable seamless payment processing for all subscription tiers
-   **Strategic Pillar**: Revenue Growth & Monetization
-   **Business Goal**: Process $1M in transactions monthly by Q3 2026
-   **Persona Impact**: Primary focus on \"The Startup Founder\" who needs reliable payment processing
-->

---

## 2. Scope & Phasing
*What's included in THIS epic only. Keep it focused and deliverable in 2-4 weeks.*

### 2.1 In Scope for This Epic
*The specific features/capabilities delivered by THIS epic.*

-   [ ] [IN_SCOPE_ITEM_1]
-   [ ] [IN_SCOPE_ITEM_2]
-   [ ] [IN_SCOPE_ITEM_3]
-   [ ] [IN_SCOPE_ITEM_4]

<!-- Example for Epic 1 (Core Payment Infrastructure):
-   [ ] Stripe payment gateway integration
-   [ ] Credit card payment processing API
-   [ ] Transaction status tracking (pending, success, failed)
-   [ ] Basic payment logging and audit trail
-   [ ] Webhook handling for payment confirmations
-->

### 2.2 Out of Scope for This Epic
*What we're explicitly NOT doing in this epic (but might be in other epics).*

-   [OUT_OF_SCOPE_1] - [WHICH_EPIC_HANDLES_THIS]
-   [OUT_OF_SCOPE_2] - [WHICH_EPIC_HANDLES_THIS]
-   [OUT_OF_SCOPE_3] - [WHICH_EPIC_HANDLES_THIS]

<!-- Example:
-   Multiple payment methods (PayPal, bank transfer) - Covered in Epic 2: Payment Methods
-   Refund processing - Covered in Epic 3: Refund Workflow
-   Recurring payments/subscriptions - Future epic (not in current BRD scope)
-   Invoice generation - Not required for MVP
-->

### 2.3 Internal Phases (Optional)
*If this epic needs sub-phases, list them here. Otherwise, remove this section.*

**Phase 1: Foundation (Week 1-2)**
-   [ ] [PHASE_1_ITEM_1]
-   [ ] [PHASE_1_ITEM_2]

**Phase 2: Core Features (Week 2-3)**
-   [ ] [PHASE_2_ITEM_1]
-   [ ] [PHASE_2_ITEM_2]

**Phase 3: Polish & Testing (Week 3-4)**
-   [ ] [PHASE_3_ITEM_1]
-   [ ] [PHASE_3_ITEM_2]

<!-- Example:
**Phase 1: Foundation (Week 1-2)**
-   [ ] Stripe API integration setup
-   [ ] Payment model and database schema

**Phase 2: Core Features (Week 2-3)**
-   [ ] Payment processing endpoint
-   [ ] Webhook handling
-   [ ] Transaction logging

**Phase 3: Polish & Testing (Week 3-4)**
-   [ ] Error handling and retry logic
-   [ ] Load testing
-   [ ] Security audit
-->

---

## 3. Key User Stories (The "What")
*Link to individual PRDs or list high-level stories.*

| ID | User Story | Priority | Related PRD |
| :--- | :--- | :--- | :--- |
| [STORY_ID_1] | As a [PERSONA], I want to [ACTION], so that [BENEFIT]. | [PRIORITY_1] | [PRD_LINK_1] |
| [STORY_ID_2] | As a [PERSONA], I want to [ACTION], so that [BENEFIT]. | [PRIORITY_2] | [PRD_LINK_2] |
| [STORY_ID_3] | As a [PERSONA], I want to [ACTION], so that [BENEFIT]. | [PRIORITY_3] | [PRD_LINK_3] |

<!-- Example:
| ID | User Story | Priority | Related PRD |
| :--- | :--- | :--- | :--- |
| US-001 | As a new user, I want to sign up with one click using Google, so I can get started fast. | P0 | prd-social-login.md |
| US-002 | As a new user, I want to see a progress indicator, so I know how far along I am in setup. | P0 | prd-onboarding-flow.md |
| US-003 | As a PM, I want to track drop-off at each onboarding step, so I can optimize the funnel. | P1 | prd-analytics.md |
| US-004 | As a new user, I want contextual help tips, so I understand what to do next. | P1 | prd-onboarding-flow.md |
-->

---

## 4. Success Metrics
*How do we measure the success of THIS epic specifically?*

### 4.1 Epic-Specific Metrics

| Metric | Definition | Current Baseline | Target | Timeline |
| :--- | :--- | :--- | :--- | :--- |
| [EPIC_METRIC_1] | [DEFINITION_1] | [BASELINE_1] | [TARGET_1] | [TIMELINE_1] |
| [EPIC_METRIC_2] | [DEFINITION_2] | [BASELINE_2] | [TARGET_2] | [TIMELINE_2] |

<!-- Example for Epic 1 (Core Payment Infrastructure):
| Metric | Definition | Current Baseline | Target | Timeline |
| :--- | :--- | :--- | :--- | :--- |
| **Payment Success Rate** | % of credit card transactions that complete successfully | 0% (no system) | 98%+ | 2 weeks post-launch |
| **Transaction Processing Time** | Avg time from payment initiation to confirmation | N/A | < 3 seconds | 2 weeks post-launch |
| **System Uptime** | % of time payment system is operational | N/A | 99.9% | 1 month post-launch |
-->

### 4.2 Contribution to BRD Metrics
*How does this epic contribute to the overall BRD goals?*

-   **BRD North Star Metric**: [BRD_METRIC]
-   **This Epic's Contribution**: [CONTRIBUTION_DESCRIPTION]

<!-- Example:
-   **BRD North Star Metric**: Process $1M in monthly transactions by Q3 2026
-   **This Epic's Contribution**: Enables credit card payment processing (expected to be 80% of transaction volume). Without this epic, no transactions can be processed.
-->

### 4.3 Success Criteria (Definition of Done)

-   [ ] [SUCCESS_CRITERIA_1]
-   [ ] [SUCCESS_CRITERIA_2]
-   [ ] [SUCCESS_CRITERIA_3]
-   [ ] [SUCCESS_CRITERIA_4]

<!-- Example:
-   [ ] Successfully process 100 test transactions with 0 failures
-   [ ] Payment processing time consistently under 3 seconds (p95)
-   [ ] All critical security requirements met (PCI compliance basics)
-   [ ] 95% unit test coverage for payment processing code
-   [ ] Documentation complete for integration
-->

---

## 5. Dependencies & Risks

### 5.1 Dependencies
*What needs to be completed before or during THIS epic?*

| Dependency | Type | Owner | Status | Impact if Delayed | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [DEPENDENCY_1] | [TYPE_1] | [OWNER_1] | [STATUS_1] | [IMPACT_1] | [NOTES_1] |
| [DEPENDENCY_2] | [TYPE_2] | [OWNER_2] | [STATUS_2] | [IMPACT_2] | [NOTES_2] |

<!-- Example:
| Dependency | Type | Owner | Status | Impact if Delayed | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Stripe account setup & API keys | External | Finance Team | ✅ Complete | Blocker | Account created, keys in vault |
| Payment data model design | Technical | Data Team | 🟡 In Progress | High - blocks dev | Review scheduled Jan 10 |
| PCI compliance review | Legal | Compliance | ⚪ Not Started | Medium - can launch internal beta | Required before public launch |

Types: Technical, External Team, Data/Research, Design, Legal/Compliance, Previous Epic
-->

### 5.2 Cross-Epic Dependencies
*Dependencies on other epics in this BRD.*

| Dependency Epic | Relationship | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| [EPIC_NAME] | [BLOCKS/BLOCKED_BY] | [IMPACT] | [MITIGATION] |

<!-- Example:
| Dependency Epic | Relationship | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Epic 2: Payment Methods | BLOCKS - Epic 2 can't start until this completes | High | Ensure this epic finishes on time; keep Epic 2 team informed |
| Epic 3: Refund Workflow | BLOCKS - Epic 3 needs payment logging from this epic | Medium | Clearly document payment logging API for Epic 3 team |
-->

### 5.3 Risks

| Risk | Impact | Probability | Mitigation | Owner |
| :--- | :--- | :--- | :--- | :--- |
| [RISK_1] | [IMPACT_1] | [PROBABILITY_1] | [MITIGATION_1] | [OWNER_1] |
| [RISK_2] | [IMPACT_2] | [PROBABILITY_2] | [MITIGATION_2] | [OWNER_2] |

<!-- Example:
| Risk | Impact | Probability | Mitigation | Owner |
| :--- | :--- | :--- | :--- | :--- |
| Stripe API changes during development | High | Low | Monitor Stripe API changelog; use stable API version | Engineering Lead |
| Payment processing time exceeds 3s target | Medium | Medium | Load test early; optimize database queries; use caching | Engineering Lead |
| Scope creep from stakeholders requesting additional payment methods | Medium | High | Clearly document Epic 1 scope; defer to Epic 2; PM to manage expectations | Product Owner |
-->

### 5.4 Assumptions
*What are we assuming to be true for THIS epic?*

-   [ASSUMPTION_1]
-   [ASSUMPTION_2]
-   [ASSUMPTION_3]

<!-- Example:
-   Stripe is the right payment gateway (decision already validated in BRD)
-   Credit card processing is sufficient for Epic 1 (other methods in Epic 2)
-   Current transaction volume estimates (1000/month) are accurate
-   Engineering team has 3 FTE for full 4 weeks
-->

---

## 6. Stakeholders & Team

### 6.1 Core Team

| Role | Name | Responsibility |
| :--- | :--- | :--- |
| **Product Owner** | [NAME] | [RESPONSIBILITY] |
| **Engineering Lead** | [NAME] | [RESPONSIBILITY] |
| **Design Lead** | [NAME] | [RESPONSIBILITY] |
| **QA Lead** | [NAME] | [RESPONSIBILITY] |

<!-- Example:
| Role | Name | Responsibility |
| :--- | :--- | :--- |
| **Product Owner** | Sarah Chen | Overall Epic success, requirements, prioritization |
| **Engineering Lead** | David Kumar | Technical architecture, team coordination |
| **Design Lead** | Emily Wong | UX flows, visual design, user testing |
| **QA Lead** | Michael Brown | Test strategy, quality gates |
-->

### 6.2 Stakeholders

-   **[STAKEHOLDER_ROLE_1]**: [NAME_1] - [INVOLVEMENT_1]
-   **[STAKEHOLDER_ROLE_2]**: [NAME_2] - [INVOLVEMENT_2]
-   **[STAKEHOLDER_ROLE_3]**: [NAME_3] - [INVOLVEMENT_3]

<!-- Example:
-   **Marketing**: Lisa Park - Landing page updates, launch campaign
-   **Sales**: James Wilson - Lead quality validation, feedback on progressive profiling
-   **Customer Success**: Amanda Lee - Onboarding best practices input
-   **Data Analytics**: Robert Kim - Metrics tracking, dashboard setup
-->

---

## 7. Timeline & Milestones

| Milestone | Target Date | Status | Deliverables |
| :--- | :--- | :--- | :--- |
| [MILESTONE_1] | [DATE_1] | [STATUS_1] | [DELIVERABLES_1] |
| [MILESTONE_2] | [DATE_2] | [STATUS_2] | [DELIVERABLES_2] |
| [MILESTONE_3] | [DATE_3] | [STATUS_3] | [DELIVERABLES_3] |

<!-- Example:
| Milestone | Target Date | Status | Deliverables |
| :--- | :--- | :--- | :--- |
| Discovery Complete | 2026-04-15 | ✅ Done | User research findings, competitive analysis |
| Design Review | 2026-04-30 | 🟡 In Progress | Figma mockups, prototype |
| Phase 1 Dev Complete | 2026-05-31 | ⚪ Not Started | Working MVP in staging |
| Phase 1 Launch | 2026-06-15 | ⚪ Not Started | 100% rollout, docs updated |
| Success Validation | 2026-08-15 | ⚪ Not Started | Metrics hit targets |
-->

---

## 8. Resources & Budget

### 8.1 Team Allocation (for this epic only)
-   **Engineering**: [ALLOCATION]
-   **Design**: [ALLOCATION]
-   **QA**: [ALLOCATION]

<!-- Example:
-   **Engineering**: 3 FTE for 4 weeks (backend focus)
-   **Design**: 0.5 FTE for 1 week (basic UI for payment status)
-   **QA**: 1 FTE for 2 weeks (integration & security testing)
-->

### 8.2 External Costs (for this epic only)
-   [COST_1]
-   [COST_2]

<!-- Example:
-   Stripe sandbox testing: $0 (free tier)
-   Security audit consultation: $2,000
-   Load testing tools: $200
-->

---

## 9. Epic Breakdown Best Practices

### ✅ Good Epic Size Indicators:
-   Can be completed in 2-4 weeks by a focused team
-   Has clear, measurable success criteria
-   Delivers independent user value (or technical foundation)
-   Has <15 user stories or tasks
-   Single team can own it
-   Clear start and end points

### ⚠️ Signs Your Epic is Too Large:
-   Estimated > 6 weeks of work
-   Multiple teams need to coordinate extensively
-   Too many dependencies to track
-   Success metrics are vague or too broad
-   Scope keeps expanding during planning
-   → **Solution**: Split into multiple sequential epics

### 💡 How to Split a BRD into Multiple Epics:

**Option 1: Sequential Phases**
- Epic 1: Foundation/Infrastructure
- Epic 2: Core Features
- Epic 3: Advanced Features

**Option 2: By User Journey**
- Epic 1: User Acquisition Flow
- Epic 2: Activation Flow
- Epic 3: Retention Features

**Option 3: By Technical Layer**
- Epic 1: Backend API
- Epic 2: Frontend UI
- Epic 3: Integration & Testing

**Option 4: By Feature Set**
- Epic 1: Payment Method A (Credit Card)
- Epic 2: Payment Method B (PayPal)
- Epic 3: Refunds & Disputes

---

**Epic Version**: [EPIC_VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Epic Version: 1.0.0 | Last Updated: 2026-01-05 -->

# 📝 User Story Template
<!-- Document Title: [USER STORY TITLE] -->
<!-- 
📁 File Location Convention:
Save this file as: requirements/XXX-feature-name/stories/us-NNN-story-title.md

Examples:
  requirements/001-payment-system/stories/us-001-process-credit-card.md
  requirements/001-payment-system/stories/us-002-view-payment-status.md
  requirements/042-user-dashboard/stories/us-001-view-key-metrics.md

Why User Stories?
- Breaks down PRD/Epic into small, testable increments
- Focuses on user value and outcomes (not just features)
- Provides clear acceptance criteria for development
- Enables better estimation and sprint planning
- Creates shared understanding between PM, Design, and Engineering

When to create User Stories:
✅ After PRD is approved and Epic is defined
✅ During sprint planning to break down Epic work
✅ When acceptance criteria needs to be crystal clear
✅ For tracking individual dev tasks and testing

Story naming pattern: us-NNN-[action]-[object].md
-->

---

## Story Metadata

| Metadata | Details |
| :--- | :--- |
| **Story ID** | [STORY_ID] |
| **Story Title** | [STORY_TITLE] |
| **Related PRD** | [Link to PRD](../prd.md) |
| **Related Epic** | [Link to Epic](../epic-NNN-epic-title.md) |
| **Story Points** | [STORY_POINTS] |
| **Priority** | [PRIORITY] |
| **Status** | [STATUS] |
| **Assignee** | [ASSIGNEE_NAME] |
| **Sprint** | [SPRINT_NUMBER] |

<!-- Example:
| **Story ID** | US-001.1.1 |
| **Story Title** | Process Credit Card Payment |
| **Related PRD** | [Payment System PRD](../prd.md) |
| **Related Epic** | [Epic 1: Core Payment Infrastructure](../epic-001-core-payments.md) |
| **Story Points** | 5 |
| **Priority** | P0 (Must Have) |
| **Status** | `Ready` / `In Progress` / `In Review` / `Done` |
| **Assignee** | Alex Kumar |
| **Sprint** | Sprint 23 (Jan 8-21, 2026) |
-->

---

## User Story

### As a [Role]...
**Role**: [USER_ROLE]

<!-- Example: "Premium Subscriber" / "First-time Customer" / "Account Administrator" / "Mobile App User" -->

### I want to [Action]...
**Action**: [DESIRED_ACTION]

<!-- Example: "process a credit card payment for my subscription" / "view the status of my recent payment" / "receive a confirmation email after successful payment" -->

### So that [Goal]...
**Goal**: [USER_BENEFIT]

<!-- Example: "I can unlock premium features immediately" / "I know my payment was successful and when I'll be charged next" / "I have a record for my accounting" -->

---

## Full Story Statement

> **As a** [ROLE],  
> **I want to** [ACTION],  
> **So that** [GOAL].

<!-- Example:
> **As a** premium subscriber,  
> **I want to** process a credit card payment for my subscription,  
> **So that** I can unlock premium features immediately and start using the platform.
-->

---

## Description

### Context
*Background information and why this story matters.*

[CONTEXT_DESCRIPTION]

<!-- Example:
Currently, users must manually contact sales to set up payment, which takes 24-48 hours. This creates friction and leads to 30% drop-off between signup and activation. This story enables instant self-service payment processing, removing the biggest barrier to activation.
-->

### Current Behavior (If Applicable)
*What happens today?*

[CURRENT_BEHAVIOR]

<!-- Example:
Users complete signup → See "Contact Sales" message → Fill out form → Wait for sales rep → Receive invoice → Manual payment setup → Account activated (2 days later)
-->

### Desired Behavior
*What should happen after this story is implemented?*

[DESIRED_BEHAVIOR]

<!-- Example:
Users complete signup → See pricing page → Enter credit card details → Click "Subscribe" → Payment processed in 3 seconds → Account immediately activated → Confirmation email sent
-->

---

## Acceptance Criteria

### Must Have (Definition of Done)

- [ ] **Given** [PRECONDITION_1], **When** [ACTION_1], **Then** [EXPECTED_RESULT_1]
- [ ] **Given** [PRECONDITION_2], **When** [ACTION_2], **Then** [EXPECTED_RESULT_2]
- [ ] **Given** [PRECONDITION_3], **When** [ACTION_3], **Then** [EXPECTED_RESULT_3]
- [ ] **Given** [PRECONDITION_4], **When** [ACTION_4], **Then** [EXPECTED_RESULT_4]

<!-- Example:
- [ ] **Given** I am on the payment page with valid subscription selected, **When** I enter valid credit card details (number, expiry, CVV) and click "Pay Now", **Then** payment is processed within 3 seconds and I see a success message
- [ ] **Given** payment is successful, **When** transaction completes, **Then** my account is immediately upgraded to premium tier and all premium features are unlocked
- [ ] **Given** payment is successful, **When** transaction completes, **Then** I receive a confirmation email within 1 minute with receipt and transaction ID
- [ ] **Given** I enter invalid card details, **When** I click "Pay Now", **Then** I see a clear error message explaining the issue (e.g., "Card declined - insufficient funds") and payment is not processed
- [ ] **Given** payment processing takes longer than expected, **When** waiting, **Then** I see a loading indicator and the page doesn't timeout before 30 seconds
-->

### Nice to Have (Optional Enhancements)

- [ ] [OPTIONAL_CRITERIA_1]
- [ ] [OPTIONAL_CRITERIA_2]

<!-- Example:
- [ ] Save card details for future payments (with user consent)
- [ ] Show estimated processing time on the payment button
- [ ] Support multiple currencies
-->

### Edge Cases & Error Handling

- [ ] **When** [ERROR_SCENARIO_1], **Then** [ERROR_HANDLING_1]
- [ ] **When** [ERROR_SCENARIO_2], **Then** [ERROR_HANDLING_2]

<!-- Example:
- [ ] **When** Stripe API is down or times out, **Then** show user-friendly error message "Payment service temporarily unavailable, please try again in a few minutes" and log error for monitoring
- [ ] **When** user clicks "Pay Now" multiple times rapidly, **Then** prevent duplicate payment submissions (button disabled after first click)
- [ ] **When** network connection is lost during payment, **Then** show "Connection lost" message and allow retry without losing form data
-->

---

## Technical Notes

### API Endpoints
*What APIs are involved?*

- [ENDPOINT_1]: [PURPOSE_1]
- [ENDPOINT_2]: [PURPOSE_2]

<!-- Example:
- `POST /api/v1/payments` - Process payment transaction
- `GET /api/v1/payments/{id}` - Retrieve payment status
- `POST /api/v1/webhooks/stripe` - Handle Stripe webhooks
-->

### Data Model
*What data needs to be stored or retrieved?*

[DATA_MODEL_DESCRIPTION]

<!-- Example:
Payment record must include:
- transaction_id (unique, indexed)
- user_id (foreign key)
- amount, currency
- status (pending/success/failed)
- payment_method (last 4 digits, type)
- created_at, updated_at
- stripe_payment_intent_id
-->

### Dependencies
*What technical dependencies does this story have?*

- [DEPENDENCY_1]
- [DEPENDENCY_2]

<!-- Example:
- Stripe SDK integration completed
- Payment database schema created and migrated
- User authentication system functional
- Email service configured for confirmations
-->

### Performance Requirements
*Any specific performance criteria?*

- [PERFORMANCE_REQ_1]
- [PERFORMANCE_REQ_2]

<!-- Example:
- Payment processing must complete within 3 seconds (p95)
- Payment page must load within 1 second
- Support 100 concurrent payment transactions
-->

### Security Considerations
*Security requirements for this story.*

- [SECURITY_REQ_1]
- [SECURITY_REQ_2]

<!-- Example:
- Never store full credit card numbers (use Stripe tokens only)
- All payment data transmitted over HTTPS
- Implement CSRF protection on payment form
- Log all payment attempts for fraud detection
-->

---

## Design & UX

### UI/UX Requirements
*Key design requirements or mockup links.*

- [UI_REQUIREMENT_1]
- [UI_REQUIREMENT_2]
- **Design Mockups**: [FIGMA_LINK]

<!-- Example:
- Payment form must be mobile-responsive
- Show real-time validation on card number input
- Display security badges (SSL, payment provider logos)
- Success state should be clear with checkmark icon
- **Design Mockups**: [Figma: Payment Flow](https://figma.com/file/xyz)
-->

### User Flow
*Step-by-step flow for this story.*

1. [STEP_1]
2. [STEP_2]
3. [STEP_3]
4. [STEP_4]

<!-- Example:
1. User lands on payment page with pre-selected plan (from previous step)
2. User enters credit card details (fields auto-format as they type)
3. User clicks "Pay Now" button
4. Loading indicator shows for 1-3 seconds
5. Success screen appears with confirmation and next steps
6. Confirmation email arrives within 1 minute
-->

---

## Test Cases

### Manual Test Scenarios

| Test Case | Steps | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| [TEST_CASE_1] | [STEPS_1] | [EXPECTED_1] | [STATUS_1] |
| [TEST_CASE_2] | [STEPS_2] | [EXPECTED_2] | [STATUS_2] |

<!-- Example:
| Test Case | Steps | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| Happy path - valid card | 1. Enter test card 4242 4242 4242 4242<br>2. Enter future expiry<br>3. Enter any 3-digit CVV<br>4. Click "Pay Now" | Payment succeeds, account upgraded, email sent | ⚪ Not Tested |
| Declined card | 1. Enter test card 4000 0000 0000 0002<br>2. Complete form<br>3. Click "Pay Now" | Error message: "Card declined", no charge made | ⚪ Not Tested |
| Network timeout | 1. Throttle network to 2G<br>2. Submit payment<br>3. Wait 30 seconds | Loading indicator shows, timeout handled gracefully | ⚪ Not Tested |
-->

### Automated Test Requirements

- [ ] Unit tests for payment processing logic
- [ ] Integration tests with Stripe test mode
- [ ] E2E test for complete payment flow
- [ ] Error handling tests for edge cases

---

## Definition of Ready

*Checklist before development can start:*

- [ ] Story is sized and pointed (story points assigned)
- [ ] Acceptance criteria are clear and testable
- [ ] Design mockups approved (if UI changes)
- [ ] Technical dependencies identified and available
- [ ] API contracts defined (if new endpoints)
- [ ] Security requirements reviewed
- [ ] Test data/environment available

---

## Definition of Done

*Checklist before story can be closed:*

- [ ] All acceptance criteria met and verified
- [ ] Code reviewed and approved
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Manual QA testing completed
- [ ] Security review completed (if applicable)
- [ ] Documentation updated (API docs, user docs)
- [ ] Deployed to staging environment
- [ ] Product Owner sign-off received

---

## Notes & Comments

### Questions / Blockers
*Any open questions or blockers?*

- [QUESTION_1]
- [QUESTION_2]

<!-- Example:
- ❓ Do we need to support American Express cards in MVP? (Answer: No, Visa/Mastercard only)
- ⚠️ BLOCKER: Waiting for Stripe API keys from Finance team
-->

### Related Stories
*Links to related or dependent user stories.*

- **Depends on**: [DEPENDENCY_STORY]
- **Blocks**: [BLOCKED_STORY]
- **Related**: [RELATED_STORY]

<!-- Example:
- **Depends on**: [US-001.0.1: Set up Stripe integration](us-001-stripe-setup.md)
- **Blocks**: [US-001.1.2: Display payment history](us-002-payment-history.md)
- **Related**: [US-001.1.3: Send payment confirmation email](us-003-payment-email.md)
-->

---

## Story Breakdown Tips

### ✅ Good User Story Characteristics:
- **Independent**: Can be developed and tested separately
- **Negotiable**: Details can be refined through conversation
- **Valuable**: Delivers clear user or business value
- **Estimable**: Team can size it (typically 1-8 story points)
- **Small**: Completable within one sprint (1-2 weeks)
- **Testable**: Clear acceptance criteria that can be verified

### ⚠️ Signs Your Story is Too Large:
- Estimated > 8 story points
- Takes longer than 1 sprint to complete
- Has > 10 acceptance criteria
- Involves multiple systems or teams
- Hard to describe in one sentence
- → **Solution**: Split into multiple smaller stories

### 💡 How to Split Large Stories:

**By Workflow Steps**: Separate create, read, update, delete operations  
**By Data**: Handle different data types or user segments separately  
**By Operations**: Split by CRUD operations  
**By Business Rules**: Simple rules first, complex rules later  
**By Happy/Sad Path**: Success cases first, error handling later  
**By Priority**: Must-have vs. nice-to-have features  

---

**Story Version**: [VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Story Version: 1.0.0 | Last Updated: 2026-01-05 -->

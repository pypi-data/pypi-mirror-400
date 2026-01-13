---
title: User Story Creator
description: Break down PRD/Epic into detailed, testable user stories with acceptance criteria
handoffs:
  - label: View Parent PRD
    agent: productkit.prd
    prompt: Show me the PRD for context
  - label: View Parent Epic
    agent: productkit.epic
    prompt: Show me the Epic for context
---

# User Story Creator

Creates detailed user stories from PRDs and Epics following Product Kit standards with clear acceptance criteria, test cases, and technical specifications ready for sprint planning and development.

## Outline

### 1. Load Context & Understand Requirements
1. **Load Constitution**: Read `constitution.md`
   - Reference UX/UI Standards for user-facing stories
   - Apply Technical Standards for implementation requirements
   - Check Process Standards for Definition of Done
   - Use Decision Frameworks for prioritization
2. **Load Parent Documents**:
   - **PRD**: Read the related PRD from `requirements/XXX-feature-name/prd.md`
     - Understand overall feature scope and business goals
     - Extract functional requirements relevant to this story
     - Identify which user stories have been defined
     - Note non-functional requirements (performance, security)
   - **Epic** (if applicable): Read related Epic from `requirements/XXX-feature-name/epic-NNN-title.md`
     - Understand epic scope and how this story fits
     - Check dependencies on other stories in the epic
     - Verify story aligns with epic success metrics
3. **Load Personas**: Read `context/personas.md`
   - Identify the specific persona for this story
   - Reference their goals, pain points, and behavioral patterns
   - Use authentic language from persona profiles
4. **Load Glossary**: Read `context/glossary.md`
   - Use consistent terminology in story description
   - Ensure technical terms are properly defined

### 2. Validate Against Inventory & Constraints
1. **Review Feature Catalog**: Check `inventory/feature-catalog.md`
   - Identify existing features this story interacts with
   - Note any features being modified or extended
   - Check for potential conflicts or dependencies
2. **Check Technical Constraints**: Review `inventory/tech-constraints.md`
   - Platform limitations affecting implementation
   - Performance boundaries to consider
   - Third-party service constraints (rate limits, quotas)
   - Security and compliance requirements
3. **Verify Data Model**: Check `inventory/data-model.md`
   - Identify entities used in this story
   - Understand required data fields and relationships
   - Note any schema changes needed
   - Verify data validation rules

### 3. Generate User Story
1. **Use Template**: Load `templates/user_story_template.md`

2. **Story Metadata**:
   - Story ID: Follow convention (e.g., US-001.1.1 for Epic 1, Story 1, Sub-story 1)
   - Link to parent PRD and Epic
   - Estimate story points (1-8 range, use Fibonacci)
   - Set priority (P0/P1/P2 based on PRD)
   - Sprint assignment if known

3. **Core Story Statement** (Role, Action, Goal):
   - **Role**: Specific persona from personas.md (e.g., "Premium Subscriber", "Account Admin")
   - **Action**: Clear, specific action the user wants to perform
   - **Goal**: The benefit or outcome the user expects
   - Format: "As a [Role], I want to [Action], so that [Goal]"
   - Example: "As a premium subscriber, I want to process a credit card payment for my subscription, so that I can unlock premium features immediately"

4. **Description**:
   - **Context**: Why this story matters, background information
   - **Current Behavior**: What happens today (if applicable)
   - **Desired Behavior**: What should happen after implementation
   - Include relevant metrics or data from PRD

5. **Acceptance Criteria** (Critical Section):
   - **Must Have**: Use Given-When-Then format
     - Given [precondition/context]
     - When [action/trigger]
     - Then [expected result/outcome]
   - Write 3-7 core acceptance criteria covering:
     - Happy path (primary success scenario)
     - Key user interactions
     - Data validation and business rules
     - Immediate feedback to user
     - System state changes
   - **Nice to Have**: Optional enhancements that add value
   - **Edge Cases & Error Handling**:
     - Network failures, timeouts
     - Invalid input handling
     - Permission denied scenarios
     - System unavailability
     - Concurrent user actions
   - Ensure criteria are TESTABLE and VERIFIABLE

6. **Technical Notes**:
   - **API Endpoints**: List relevant endpoints with HTTP methods
   - **Data Model**: Fields and entities involved
   - **Dependencies**: Technical dependencies required before development
   - **Performance Requirements**: Response times, load requirements
   - **Security Considerations**: Authentication, authorization, data protection
   - Note: These are initial specs to be validated/refined by engineering

7. **Design & UX**:
   - Link to Figma mockups or design specs
   - Key UI/UX requirements (mobile-responsive, accessibility)
   - User flow: Step-by-step interaction sequence
   - Reference constitution UX standards:
     - Mobile-first responsive design
     - Error states with clear messages
     - Loading states and feedback
     - Empty states when applicable

8. **Test Cases**:
   - **Manual Test Scenarios**: Create test case table with:
     - Test case name
     - Steps to execute
     - Expected result
     - Status (not tested/pass/fail)
   - Cover happy path, error cases, and edge cases
   - **Automated Test Requirements**:
     - Unit tests needed
     - Integration tests needed
     - E2E test scenarios
     - Test data requirements

9. **Definition of Ready**:
   - Checklist before development can start:
     - Story sized and estimated
     - Acceptance criteria clear and testable
     - Design mockups available (if UI changes)
     - Technical dependencies identified
     - API contracts defined
     - Security requirements reviewed
     - Test environment ready

10. **Definition of Done**:
    - Checklist before story can be closed:
      - All acceptance criteria met and verified
      - Code reviewed and merged
      - Unit tests written and passing (>80% coverage)
      - Integration tests passing
      - Manual QA completed
      - Security review done (if applicable)
      - Documentation updated
      - Deployed to staging
      - Product Owner sign-off

11. **Notes & Questions**:
    - Open questions requiring clarification
    - Known blockers or risks
    - Related stories (dependencies, blocks, related)
    - Follow-up items

### 4. Story Sizing & Estimation
1. **Evaluate Story Size**:
   - **Target**: 1-8 story points (completable in 1 sprint)
   - Consider: Complexity, uncertainty, effort, risk
   - Use Fibonacci sequence: 1, 2, 3, 5, 8
   - If > 8 points, recommend splitting

2. **Splitting Criteria** (if story is too large):
   - By workflow steps (separate create, read, update, delete)
   - By happy/sad path (success cases first, error handling later)
   - By data or user types (simple cases first, complex later)
   - By CRUD operations
   - By business rules (simple rules first, complex rules later)
   - By UI layers (backend API first, frontend UI later)
   - By priority (must-have vs. nice-to-have)

3. **INVEST Check** (Good Story Criteria):
   - ✅ **Independent**: Can be developed and deployed separately
   - ✅ **Negotiable**: Details can be refined through conversation
   - ✅ **Valuable**: Delivers clear value to user or business
   - ✅ **Estimable**: Team can reasonably estimate effort
   - ✅ **Small**: Fits within one sprint (1-2 weeks)
   - ✅ **Testable**: Has clear, verifiable acceptance criteria

### 5. Quality Assurance
1. **Traceability Check**:
   - Story clearly links to parent PRD
   - Story clearly links to parent Epic (if applicable)
   - Story contributes to PRD/Epic success metrics
   - Story aligns with product vision and persona needs

2. **Completeness Check**:
   - All required sections filled out
   - Acceptance criteria are specific and testable
   - Edge cases and error handling covered
   - Technical dependencies identified
   - Test cases defined

3. **Clarity Check**:
   - Story title is clear and descriptive
   - Role, Action, Goal are unambiguous
   - Acceptance criteria use precise language
   - No jargon without glossary reference
   - Examples provided where helpful

4. **Constitution Compliance**:
   - Mobile-first responsive design considered
   - Accessibility requirements included (WCAG 2.1 AA)
   - Error states and messages defined
   - Loading and empty states addressed
   - Security and privacy requirements noted
   - Performance requirements specified

### 6. File Management
1. **Naming Convention**: `requirements/XXX-feature-name/stories/us-NNN-brief-title.md`
   - Example: `requirements/001-payment-system/stories/us-001-process-credit-card.md`
   - Numbering sequence within the feature folder
   - Use kebab-case for readability

2. **Folder Structure**:
   ```
   requirements/
     XXX-feature-name/
       brd.md
       prd.md
       epic-001-title.md
       epic-002-title.md
       stories/
         us-001-story-one.md
         us-002-story-two.md
         us-003-story-three.md
   ```

3. **Version Control**:
   - Add version number and last updated date
   - Track changes in story status
   - Document major revisions

## Interaction Guidelines

### When to Create User Stories
- After PRD is approved and ready for development
- During sprint planning to break down Epic/PRD work
- When acceptance criteria needs to be crystal clear
- For tracking individual dev tasks and testing
- When team needs better estimation granularity

### When NOT to Create User Stories
- For simple bug fixes (use bug template)
- For technical chores without user value (use tech task template)
- When PRD/Epic is still in draft or under review
- For features already in development (update existing story)

### Collaboration Points
- **With PM**: Clarify acceptance criteria, priorities, business rules
- **With Design**: Validate UX requirements, review mockups, user flows
- **With Engineering**: Refine technical specs, estimate effort, identify dependencies
- **With QA**: Define test cases, edge cases, error scenarios

### Common Pitfalls to Avoid
- ❌ Writing implementation details instead of user outcomes
- ❌ Making acceptance criteria vague or untestable
- ❌ Creating stories that depend on too many other stories
- ❌ Mixing multiple user roles or actions in one story
- ❌ Forgetting error handling and edge cases
- ❌ Ignoring non-functional requirements (performance, security)
- ❌ Making story too large (>8 story points)

## Output Format

Save the completed user story as a markdown file following the template structure. Ensure all sections are filled out with relevant, specific information. Use examples from the template as guidance for the level of detail expected.

Reference constitution, personas, and inventory files using relative links for easy navigation.

Mark any assumptions, open questions, or blockers clearly for team visibility.

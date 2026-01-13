---
title: Product Requirements Document Creator
description: Create a Product Requirements Document (PRD) with detailed specifications and acceptance criteria
handoffs:
  - label: Create Business Case First
    agent: productkit.brd
    prompt: Create a BRD for strategic context before this PRD
  - label: Break Down into User Stories
    agent: productkit.user-story
    prompt: Create user stories from this PRD for sprint planning
---

# Product Requirements Document Creator

Creates a comprehensive PRD following Product Kit standards with detailed specifications ready for engineering handoff.

## Outline

### 1. Load Context & Validation
1. **Load Constitution**: Read `constitution.md` for quality standards
   - Reference UX/UI Standards (mobile, error states, empty states)
   - Check Design Standards (copywriting, color semantics, ASCII wireframes)
   - Verify Technical Standards (offline, security, scalability)
   - Apply Process Standards (success metrics, analytics, rollout)
2. **Load Product Vision**: Read `context/product-vision.md`
   - Validate alignment with Strategic Pillars
   - Confirm supports Business Objectives
   - Check against High-Level Roadmap themes
3. **Load Personas**: Read `context/personas.md`
   - Identify primary and secondary personas affected
   - Reference goals, pain points, and quotes
   - Consider anti-personas to exclude
4. **Load Glossary**: Read `context/glossary.md`
   - Use consistent terminology
   - Avoid deprecated terms

### 2. Validate Against Inventory
1. **Review Existing Features**: Check `inventory/feature-catalog.md`
   - Identify related features and dependencies
   - Avoid duplicating existing functionality
   - Note any features that need modification
2. **Check Technical Constraints**: Review `inventory/tech-constraints.md`
   - Platform limitations (mobile, browser, desktop)
   - Performance limits (data volume, real-time updates)
   - Third-party dependencies (rate limits, quotas)
   - Infrastructure constraints (database, API, storage)
3. **Verify Data Model**: Check `inventory/data-model.md`
   - Identify entities affected
   - Plan schema changes if needed
   - Ensure data lifecycle compliance
4. **Map to Product**: Reference `inventory/product-map.md`
   - Determine where feature fits in navigation
   - Identify affected user flows
   - Plan information architecture updates

### 3. Generate PRD
1. **Use Template**: Load `templates/prd_template.md`

2. **Context & Goal** (Section 1):
   - Problem: User pain point with evidence (research, metrics, support tickets)
   - Solution: Feature description with key capabilities
   - User Value: Jobs-to-be-Done framing
   - Business Value: Revenue, retention, strategic impact

3. **User Stories** (Section 2):
   - Format: As a [Persona], I want to [Action], so that [Benefit]
   - Include Priority (P0/P1/P2)
   - Detailed Acceptance Criteria for each story

4. **Functional Requirements** (Section 3):
   - Use SHALL (mandatory), SHOULD (recommended), MAY (optional)
   - Organize by category (layout, logic, visualization, etc.)
   - Detail all business rules and validation logic
   - Specify permissions and access control

5. **Design & UX** (Section 4):
   - Link to Figma designs
   - Responsive behavior (desktop, tablet, mobile)
   - Accessibility requirements (WCAG 2.1 AA per constitution)
   - Optional: ASCII wireframes for version control

6. **Technical Specifications** (Section 5):
   - API endpoints (to be validated by engineering)
   - Database changes required
   - Performance requirements (load time, response time)
   - Security & privacy considerations

7. **Analytics & Tracking** (Section 6):
   - Event names and properties
   - Trigger conditions
   - Priority for instrumentation

8. **Edge Cases & Error Handling** (Section 7):
   - Error states with messages (per constitution)
   - Edge cases with handling strategy
   - Network failures, timeout scenarios

9. **Launch Plan** (Section 8):
   - Rollout strategy (phased approach)
   - Success criteria (go/no-go)
   - Rollback plan

10. **Open Questions** (Section 9):
    - Track unresolved items
    - Assign owners and deadlines

### 4. Constitution Compliance Check
Validate PRD against constitution:
- [ ] **UX/UI Standards**:
  - [ ] Mobile responsive (320px min per constitution)
  - [ ] Error states defined for all inputs/APIs
  - [ ] Empty states designed for all lists
- [ ] **Design Standards**:
  - [ ] Copy follows voice guidelines (professional, human, concise)
  - [ ] Actions use active verbs
  - [ ] Color semantics correct (primary, destructive, neutral)
- [ ] **Technical Standards**:
  - [ ] Critical flows work offline (if applicable)
  - [ ] No PII in logs
  - [ ] Scales to 10x traffic
- [ ] **Process Standards**:
  - [ ] Success metrics defined
  - [ ] Analytics events specified
  - [ ] Rollout plan documented

### 5. Cross-Reference Validation
- [ ] **Feature Catalog**: No conflicts with existing features
- [ ] **Tech Constraints**: Respects all limitations
- [ ] **Data Model**: Schema changes documented
- [ ] **Product Map**: Placement in navigation clear
- [ ] **Product Vision**: Aligns with strategic pillars
- [ ] **Personas**: Solves primary persona's problem
- [ ] **Glossary**: Uses correct terminology

### 6. Output & Next Steps
1. Save PRD to appropriate location (suggest `specs/` or `prds/` folder)
2. Add metadata (version, date, status, owners)
3. Generate summary of what was included
4. Suggest next steps:
   - **Option A**: Create technical plan (`/productkit.plan`)
   - **Option B**: Break into tasks (`/productkit.tasks`)
   - **Option C**: Request engineering review
   - **Option D**: Refine with clarification (`/productkit.clarify`)

## Example Usage

**User**: "Create PRD for in-app analytics dashboard"

**Agent**:
1. Loads constitution → identifies all UI, design, and technical standards
2. Loads personas → "Busy Manager" wants quick insights, "Power User" wants deep analysis
3. Checks feature-catalog → existing CSV export to be replaced
4. Checks tech-constraints → frontend can handle 10k data points per chart
5. Generates PRD with:
   - User Stories: Filter by date range (P0), Export PDF (P1), Save views (P2)
   - Functional Requirements: Dashboard layout, filtering logic, chart types
   - Design: Responsive grid, accessibility compliance, ASCII wireframe
   - Technical: API endpoints, database indexes, performance targets
   - Analytics: dashboard_viewed, filter_applied, export_clicked events
   - Edge Cases: Network failure, massive data, empty states
   - Launch: Internal → 10% beta → 100% rollout

## Key Files Referenced

- **Constitution**: `/constitution.md`
- **Context**: `/context/*.md` (vision, personas, market, glossary)
- **Inventory**: `/inventory/*.md` (features, constraints, data, map)
- **Template**: `/templates/prd_template.md`

## Handoff Commands

Before or after PRD:
- `/productkit.brd` - Create BRD for strategic context first
- `/productkit.plan` - Create technical implementation plan
- `/productkit.tasks` - Break into development tasks
- `/productkit.clarify` - Ask clarifying questions

---
title: Epic Planning Document Creator
description: Create an Epic document to plan a multi-phase initiative with user stories and success metrics
next_steps:
  - "Document business case: Use /productkit.brd for the initiative"
  - "Detail each phase: Use /productkit.prd for individual phase specifications"
  - "Break into sprints: Convert Epic into sprint-ready tasks"
---

# Epic Planning Document Creator

Creates a comprehensive Epic following Product Kit standards for planning multi-phase initiatives.

## Outline

### 1. Load Context & Strategic Alignment
1. **Load Constitution**: Read `constitution.md`
   - Reference Core Principles for decision-making
   - Apply Decision Frameworks (RICE scoring)
   - Verify Process Standards compliance
2. **Load Product Vision**: Read `context/product-vision.md`
   - **CRITICAL**: Validate alignment with Strategic Pillars
   - Confirm supports Business Objectives and Mission
   - Check against High-Level Roadmap themes
   - Ensure contributes to North Star Metric
3. **Load Personas**: Read `context/personas.md`
   - Identify which personas benefit (primary, secondary)
   - Reference their goals and pain points
   - Ensure not building for anti-personas
4. **Load Market Research**: Read `context/market-research.md`
   - Consider competitive landscape
   - Validate against market trends
   - Support differentiation strategy

### 2. Assess Current State
1. **Review Feature Catalog**: Check `inventory/feature-catalog.md`
   - List related existing features
   - Identify features to modify or deprecate
   - Map feature dependencies
2. **Check Constraints**: Review `inventory/tech-constraints.md`
   - Platform limitations affecting scope
   - Performance boundaries
   - Third-party dependencies
   - Technical debt to address
3. **Verify Data Model**: Check `inventory/data-model.md`
   - Entities involved
   - Schema changes needed across phases
4. **Map Product Impact**: Reference `inventory/product-map.md`
   - User flows affected
   - Navigation changes required
   - Module ownership

### 3. Generate Epic
1. **Use Template**: Load `templates/epic_template.md`

2. **Overview** (Section 1):
   - **Objective**: Big goal, measurable outcome
   - **Hypothesis**: "If we do X, then Y will happen" with rationale
   - **Strategic Alignment**: Which pillar, business goal, persona impact

3. **Scope & Phasing** (Section 2):
   - **Phase 1 (MVP)**: Bare minimum to ship value
   - **Phase 2 (Enhanced)**: Fast follows adding significant value
   - **Phase 3 (Delight)**: Nice-to-haves
   - **Out of Scope**: Explicitly NOT doing

4. **Key User Stories** (Section 3):
   - High-level user stories (will link to PRDs)
   - Format: As a [Persona], I want to [Action], so that [Benefit]
   - Assign to phases with priority

5. **Success Metrics** (Section 4):
   - **Primary Metrics**: North Star for this Epic
     - Define metric, baseline, target, timeline
   - **Secondary Metrics**: Supporting indicators
   - **Leading Indicators**: Early signals of success

6. **Dependencies & Risks** (Section 5):
   - **Dependencies**: What needs to be done first (technical, external teams, data/research)
   - **Risks**: Impact, probability, mitigation, owner
   - **Assumptions**: What we're assuming to be true

7. **Stakeholders & Team** (Section 6):
   - Core team (Product, Engineering, Design, QA)
   - Stakeholders (Marketing, Sales, CS, Analytics)
   - Responsibilities for each

8. **Timeline & Milestones** (Section 7):
   - Key milestones with dates and deliverables
   - Phases mapped to calendar quarters

9. **Resources & Budget** (Section 8):
   - Team allocation (FTE and duration)
   - External costs

### 4. Constitution Compliance Check
Validate Epic against constitution:
- [ ] **Core Principles**: Aligns with product values
- [ ] **Process Standards**: 
  - [ ] Success Metrics defined (required per constitution)
  - [ ] Analytics approach planned
  - [ ] Rollout strategy included
- [ ] **Decision Frameworks**: 
  - [ ] RICE score calculated (Reach × Impact × Confidence / Effort)
  - [ ] Build vs Buy decision documented

### 5. Strategic Validation
**CRITICAL**: Epic MUST align with Product Vision
- [ ] Supports one or more Strategic Pillars
- [ ] Contributes to Business Objectives
- [ ] Moves North Star Metric
- [ ] Fits High-Level Roadmap theme
- [ ] Targets correct personas
- [ ] Addresses competitive landscape

**If Epic does NOT align → FLAG for review before proceeding**

### 6. Cross-Reference Validation
- [ ] **Feature Catalog**: Impact on existing features documented
- [ ] **Tech Constraints**: All limitations considered in phasing
- [ ] **Data Model**: Schema evolution plan clear
- [ ] **Product Map**: Navigation and flow changes mapped
- [ ] **Personas**: Primary persona will benefit significantly
- [ ] **Market Research**: Competitive positioning clear
- [ ] **Glossary**: Consistent terminology used

### 7. Output & Next Steps
1. Save Epic to appropriate location (suggest `epics/` folder)
2. Add metadata (version, date, status, owner)
3. Generate summary:
   - Objective and hypothesis
   - Success metrics
   - Timeline and resource needs
4. Suggest next steps:
   - **Option A**: Create BRD for executive buy-in (`/productkit.brd`)
   - **Option B**: Create PRDs for each phase (`/productkit.prd`)
   - **Option C**: Break into development tasks (`/productkit.tasks`)
   - **Option D**: Request stakeholder review

## Example Usage

**User**: "Plan Epic for revamping user onboarding"

**Agent**:
1. Loads product-vision → aligns with "Growth & User Acquisition" pillar
2. Loads personas → targets "Busy Manager" (wants speed and simplicity)
3. Checks feature-catalog → current signup has 8 fields, 45% drop-off
4. Checks tech-constraints → OAuth integration available, 2-sprint effort
5. Generates Epic with:
   - Objective: Increase activation rate 30% → 40%, reduce time-to-value 15min → 5min
   - Hypothesis: Simplify form (8 → 2 fields) + progress indicator → more completions
   - Strategic Alignment: Growth pillar, supports "Increase MAU by 25%" goal
   - Phase 1 MVP: Simplified form, progress bar, welcome email
   - Phase 2: Social login, interactive tour
   - Phase 3: Gamification
   - Success Metrics: Activation rate (30% → 40%), Time-to-value (15min → 5min)
   - Dependencies: Marketing landing page update, OAuth provider setup
   - Risks: Lead quality may decrease (mitigation: add progressive profiling later)
   - Timeline: 8 weeks (Q2 2026)

## Key Files Referenced

- **Constitution**: `/constitution.md`
- **Context**: `/context/*.md` (vision, personas, market, glossary)
- **Inventory**: `/inventory/*.md` (features, constraints, data, map)
- **Template**: `/templates/epic_template.md`

## Handoff Commands

Before or after Epic:
- `/productkit.brd` - Create BRD for business case
- `/productkit.prd` - Create PRDs for each phase
- `/productkit.tasks` - Break Epic into tasks
- `/productkit.clarify` - Ask clarifying questions

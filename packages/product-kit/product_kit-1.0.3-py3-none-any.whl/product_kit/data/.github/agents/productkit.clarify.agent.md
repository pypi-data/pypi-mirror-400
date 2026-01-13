---
title: Requirements Clarification
description: Ask clarifying questions to refine requirements before creating BRD, PRD, or Epic
next_steps:
  - "For strategic decisions: Use /productkit.brd to create Business Requirements"
  - "For detailed specs: Use /productkit.prd to create Product Requirements"
  - "For multi-phase work: Use /productkit.epic to plan the initiative"
---

# Requirements Clarification Agent

Asks intelligent questions to gather complete requirements before creating formal documents.

## Outline

### 1. Load Context for Question Generation
1. **Load Constitution**: Read `constitution.md`
   - Identify what standards require definition (metrics, analytics, rollout)
   - Note decision frameworks to apply (RICE, Build vs Buy)
2. **Load Product Vision**: Read `context/product-vision.md`
   - Understand Strategic Pillars for alignment questions
   - Know Business Objectives to validate against
3. **Load Personas**: Read `context/personas.md`
   - Ask which personas this serves
   - Validate against their goals and pain points
4. **Load Glossary**: Read `context/glossary.md`
   - Clarify terminology
   - Avoid deprecated terms

### 2. Analyze User Input
1. Parse the initial request
2. Identify what's missing for complete requirements
3. Check what context is already available in inventory

### 3. Generate Clarifying Questions

**Category 1: Problem & User Value**
- What specific problem are we solving?
- Which persona(s) face this problem?
- What evidence do we have? (research, metrics, support tickets)
- What's the impact of NOT solving this? (business cost, user pain)

**Category 2: Solution Approach**
- What's the proposed solution?
- Are there alternative approaches? Why this one?
- What's the minimum viable version?
- What's out of scope explicitly?

**Category 3: Success Metrics** (Required by Constitution)
- What metrics will indicate success?
- What's the current baseline?
- What's the target goal?
- When should we measure? (timeframe)

**Category 4: Strategic Alignment**
- Which Strategic Pillar does this support?
- How does it move the North Star Metric?
- Which Business Objective does this serve?

**Category 5: Technical Feasibility**
- Check `inventory/tech-constraints.md`:
  - Any platform limitations?
  - Performance concerns?
  - Third-party dependencies?
- Check `inventory/feature-catalog.md`:
  - Any conflicts with existing features?
  - Features to modify or deprecate?
- Check `inventory/data-model.md`:
  - Data/entities involved?
  - Schema changes needed?

**Category 6: Scope & Phasing**
- What must be in Phase 1 (MVP)?
- What can wait for Phase 2?
- What dependencies exist?
- What resources are needed? (team, time, budget)

**Category 7: Risks & Constraints**
- What could go wrong?
- What assumptions are we making?
- What's the rollback plan?

**Category 8: Analytics & Tracking** (Required by Constitution)
- What user actions need tracking?
- What properties should be captured?
- What triggers the events?

### 4. Ask Questions Iteratively
1. Start with high-level questions (problem, personas, value)
2. Move to solution approach
3. Dig into details (scope, metrics, technical)
4. Validate against context files
5. Fill gaps progressively
6. Confirm understanding with summary

### 5. Validate Completeness
Before handoff to BRD/PRD/Epic, ensure we have:
- [ ] Clear problem statement with evidence
- [ ] Target personas identified
- [ ] Proposed solution approach
- [ ] Success metrics defined (baseline, target, timeframe)
- [ ] Strategic alignment confirmed
- [ ] Technical feasibility validated
- [ ] Scope and phasing clear
- [ ] Analytics events specified
- [ ] Risks and mitigation identified

### 6. Output & Handoff
1. Summarize gathered requirements
2. Highlight any gaps or assumptions
3. Suggest appropriate next step:
   - **High-level initiative** → Create Epic (`/productkit.epic`)
   - **Business stakeholders** → Create BRD (`/productkit.brd`)
   - **Engineering team** → Create PRD (`/productkit.prd`)

## Example Usage

**User**: "We should add Apple Pay"

**Agent**:
1. Loads constitution → identifies need for metrics, analytics, rollout plan
2. Loads personas → needs to know which persona wants this
3. Checks tech-constraints → Stripe integration, mobile app considerations
4. Asks questions:
   - *Problem*: "What's driving this request? User feedback? Drop-off data?"
   - *Evidence*: "Do we have data on how many users want digital wallets?"
   - *Personas*: "Which personas will benefit most? Mobile users? Busy managers?"
   - *Metrics*: "What success looks like? Increase conversion rate? By how much?"
   - *Scope*: "Just Apple Pay, or also Google Pay? What about Samsung Pay?"
   - *Technical*: "Do we need mobile app updates? What's Stripe account status?"
   - *Analytics*: "What events to track? Payment method selected? Success/failure?"
   - *Timeline*: "When do we need this? Any hard deadlines?"
5. User provides answers
6. Agent summarizes complete requirements
7. Suggests: "Ready to create BRD? Or should we dive into PRD with detailed specs?"

## Key Files Referenced

- **Constitution**: `/constitution.md`
- **Context**: `/context/*.md` (vision, personas, market, glossary)
- **Inventory**: `/inventory/*.md` (features, constraints, data, map)

## Handoff Commands

After clarification:
- `/productkit.brd` - Create BRD with gathered requirements
- `/productkit.prd` - Create PRD with detailed specs
- `/productkit.epic` - Plan as Epic with phasing

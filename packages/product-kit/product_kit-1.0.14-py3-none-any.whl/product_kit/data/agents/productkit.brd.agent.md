---
title: Business Requirements Document Creator
description: Create a Business Requirements Document (BRD) with strategic alignment and ROI analysis
handoffs:
  - label: Generate Detailed PRD
    agent: productkit.prd
    prompt: Create a PRD based on this BRD
  - label: Plan as Epic
    agent: productkit.epic
    prompt: Break this BRD down into phases and user stories
---

# Business Requirements Document Creator

Creates a comprehensive BRD following Product Kit standards and best practices.

## Outline

### 1. Load Context & Validation
1. **Load Constitution**: Read `constitution.md` for non-negotiable standards
2. **Load Product Vision**: Read `context/product-vision.md` for strategic alignment
3. **Load Personas**: Read `context/personas.md` to identify target audience
4. **Load Market Research**: Read `context/market-research.md` for competitive context
5. **Check Glossary**: Reference `context/glossary.md` for consistent terminology

### 2. Validate Against Inventory
1. **Check Existing Features**: Review `inventory/feature-catalog.md` for conflicts
2. **Verify Technical Feasibility**: Consult `inventory/tech-constraints.md` for limitations
3. **Review Data Model**: Check `inventory/data-model.md` for data requirements
4. **Map to Product Structure**: Reference `inventory/product-map.md` for placement

### 3. Generate BRD
1. **Use Template**: Load `templates/brd_template.md`
2. **Gather Requirements**:
   - Problem statement with evidence
   - Proposed solution approach
   - Business value and ROI calculation
   - Target personas (primary, secondary, anti-persona)
   - Success metrics with baseline and targets
3. **Define Scope**:
   - In-scope deliverables (must-haves)
   - Out-of-scope items (explicitly)
   - Dependencies on other teams/systems
4. **Specify Requirements**:
   - Functional requirements (what it must do)
   - Non-functional requirements (performance, security, compliance)
5. **Plan Launch**:
   - Go-to-market strategy
   - Marketing, sales, and support enablement
   - Phased rollout plan
6. **Assess Risks**:
   - Identify risks with probability and impact
   - Mitigation strategies for each
7. **Create Timeline**:
   - Key milestones with target dates
   - Resource allocation (team, budget)

### 4. Constitution Compliance Check
Validate the BRD against constitution requirements:
- [ ] Aligns with Core Principles (User-Centricity, Simplicity, etc.)
- [ ] Follows Non-Negotiable Standards (UX/UI, Design, Technical, Process)
- [ ] Uses appropriate Decision Frameworks (RICE, Build vs Buy)
- [ ] Includes Success Metrics (as required by Process Standards)
- [ ] Defines Analytics tracking (per Process Standards)
- [ ] Has Rollout Plan (per Process Standards)

### 5. Cross-Reference Validation
- [ ] Feature doesn't conflict with `feature-catalog.md`
- [ ] Respects constraints in `tech-constraints.md`
- [ ] Aligns with strategic pillars in `product-vision.md`
- [ ] Targets correct personas from `personas.md`
- [ ] Uses correct terminology from `glossary.md`
- [ ] Considers competitive landscape from `market-research.md`

### 6. Output & Next Steps
1. Save BRD to appropriate location
2. Add metadata (version, date, status)
3. Suggest next steps:
   - **Option A**: Create detailed PRD (`/productkit.prd`)
   - **Option B**: Plan as Epic (`/productkit.epic`)
   - **Option C**: Request clarification (`/productkit.clarify`)

## Example Usage

**User**: "We need to add Apple Pay to our checkout"

**Agent**:
1. Loads constitution → identifies Process Standards requiring metrics
2. Loads product-vision → aligns with "Modernizing Payment Stack" pillar
3. Loads personas → targets "Busy Manager" (wants speed)
4. Checks tech-constraints → verifies Stripe supports Apple Pay
5. Generates BRD with:
   - Problem: 40% checkout drop-off, users want digital wallets
   - Solution: Integrate Apple Pay + Google Pay
   - ROI: +$150k MRR, -$20k support costs
   - Metrics: Conversion 2.5% → 3.0%, Digital wallet usage 0% → 20%
   - Risks: API downtime (Low/High) → circuit breaker mitigation

## Key Files Referenced

- **Constitution**: `/constitution.md`
- **Context**: `/context/*.md` (vision, personas, market, glossary)
- **Inventory**: `/inventory/*.md` (features, constraints, data, map)
- **Template**: `/templates/brd_template.md`

## Handoff Commands

After BRD is complete:
- `/productkit.prd` - Create detailed PRD
- `/productkit.epic` - Plan as Epic
- `/productkit.clarify` - Ask clarifying questions

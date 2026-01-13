# Product Kit - Copilot Instructions

You are assisting with **[PRODUCT_NAME]**, a framework for Requirement-Driven Design (RDD) that treats product requirements like code: structured, version-controlled, and AI-executable.

## Core Principles

1. **Load Context First**: Always read relevant context files before generating requirements
2. **Validate Against Constitution**: Check `constitution.md` for standards and principles
3. **Cross-Reference Inventory**: Verify against existing features, constraints, and data models
4. **Use Templates**: Follow structured templates for consistency
5. **Strategic Alignment**: Validate against product vision and strategic pillars

## Available Slash Commands

### `/productkit.clarify` - Requirements Clarification
**Purpose**: Ask clarifying questions to refine requirements before creating formal documents

**When to use**:
- User provides vague or incomplete requirements
- Need to gather evidence and metrics
- Want to validate strategic alignment
- Unsure which document type to create

**Agent File**: `agents/productkit.clarify.agent.md`

**Context Files to Load**:
- `constitution.md` - Standards and decision frameworks
- `context/product-vision.md` - Strategic pillars and objectives
- `context/personas.md` - User needs and goals
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations
- `inventory/data-model.md` - Data structures
- `inventory/product-map.md` - Navigation structure

**Workflow**:
1. Load all context files
2. Analyze user input for gaps
3. Ask targeted questions in categories:
   - Problem & User Value
   - Solution Approach
   - Success Metrics (required)
   - Strategic Alignment
   - Technical Feasibility
   - Scope & Phasing
   - Risks & Constraints
   - Analytics & Tracking (required)
4. Validate completeness
5. Suggest next steps (BRD, PRD, or Epic)

---

### `/productkit.brd` - Business Requirements Document
**Purpose**: Create a Business Requirements Document with strategic alignment and ROI

**When to use**:
- Need executive buy-in
- Pitching to stakeholders
- Defining business value and ROI
- Planning go-to-market strategy

**Agent File**: `agents/productkit.brd.agent.md`

**Context Files to Load**:
- `constitution.md` - Standards and principles
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - Target audience
- `context/market-research.md` - Competitive context
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical feasibility

**Template**: `templates/brd_template.md`

**Workflow**:
1. Load context files
2. Follow BRD template structure:
   - Executive Summary
   - Problem Statement
   - Business Value & ROI
   - Target Personas
   - Success Metrics
   - Strategic Alignment
   - Go-to-Market Strategy
   - Risks & Assumptions
3. Validate against constitution
4. Suggest handoff to PRD or Epic

---

### `/productkit.prd` - Product Requirements Document
**Purpose**: Create a Product Requirements Document with detailed specifications for engineering

**When to use**:
- Ready for engineering handoff
- Need detailed specifications
- Defining user stories and acceptance criteria
- Planning technical implementation

**Agent File**: `agents/productkit.prd.agent.md`

**Context Files to Load**:
- `constitution.md` - Quality standards
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - User needs
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations
- `inventory/data-model.md` - Data structures
- `inventory/product-map.md` - Navigation

**Template**: `templates/prd_template.md`

**Workflow**:
1. Load context files
2. Follow PRD template structure:
   - Feature Overview
   - User Stories & Acceptance Criteria
   - UX/UI Specifications
   - Technical Requirements
   - Success Metrics
   - Analytics Tracking
   - Rollout Plan
3. Validate against constitution
4. Create implementation checklist

---

### `/productkit.epic` - Epic Planning Document
**Purpose**: Create an Epic document to plan a multi-phase initiative with user stories and success metrics

**When to use**:
- Planning large initiatives
- Need to break work into phases
- Defining success metrics for initiative
- Coordinating multiple teams

**Agent File**: `agents/productkit.epic.agent.md`

**Context Files to Load**:
- `constitution.md` - Standards and principles
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - User needs
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations

**Template**: `templates/epic_template.md`

**Workflow**:
1. Load context files
2. Follow Epic template structure:
   - Initiative Overview
   - Success Metrics
   - Phased Approach
   - User Stories per Phase
   - Dependencies & Risks
   - Timeline & Milestones
3. Break down into manageable PRDs
4. Create tracking dashboard

---

## File Organization

### Context Files (Background Knowledge)
- `constitution.md` - Core principles and standards
- `context/product-vision.md` - Vision, pillars, objectives
- `context/personas.md` - User personas
- `context/market-research.md` - Market analysis
- `context/glossary.md` - Terminology

### Inventory Files (Current State)
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations
- `inventory/data-model.md` - Data structures
- `inventory/product-map.md` - Navigation structure

### Templates (Document Schemas)
- `templates/brd_template.md` - BRD structure
- `templates/prd_template.md` - PRD structure
- `templates/epic_template.md` - Epic structure

### Agent Files (AI Instructions)
- `agents/productkit.clarify.agent.md`
- `agents/productkit.brd.agent.md`
- `agents/productkit.prd.agent.md`
- `agents/productkit.epic.agent.md`

---

## Quick Reference

| Command | Purpose | Output | Key Context Files |
|---------|---------|--------|------------------|
| `/productkit.clarify` | Ask questions | Refined requirements | All context + inventory |
| `/productkit.brd` | Business case | BRD document | Vision, personas, market |
| `/productkit.prd` | Engineering specs | PRD document | Constitution, inventory |
| `/productkit.epic` | Initiative plan | Epic document | Vision, constraints, phases |

---

## Best Practices

1. **Always Start with Context**: Read relevant files before generating content
2. **Follow Templates**: Use the structured templates for consistency
3. **Validate Early**: Check against constitution and constraints upfront
4. **Be Specific**: Use concrete metrics, not vague goals
5. **Cross-Reference**: Link to related inventory items
6. **Think Phases**: Break large work into manageable chunks
7. **Track Analytics**: Define what and how to measure
8. **Document Assumptions**: Make implicit decisions explicit
9. **Plan Rollout**: Include gradual rollout strategy (Constitution requirement)
10. **Provide Checklists**: Help validate completeness

---

## Common Pitfalls to Avoid

❌ **Don't** skip loading context files  
✅ **Do** read constitution and relevant inventory before generating

❌ **Don't** create requirements without strategic alignment  
✅ **Do** validate against Strategic Pillars from product vision

❌ **Don't** forget success metrics  
✅ **Do** define metrics, baselines, and targets (Constitution requirement)

❌ **Don't** ignore technical constraints  
✅ **Do** check tech-constraints.md for limitations

❌ **Don't** create standalone documents  
✅ **Do** cross-reference related features and documents

❌ **Don't** assume persona needs  
✅ **Do** validate against defined personas from context

❌ **Don't** skip analytics planning  
✅ **Do** define tracking events and properties (Constitution requirement)

❌ **Don't** propose big-bang launches  
✅ **Do** include gradual rollout plan (Constitution requirement)

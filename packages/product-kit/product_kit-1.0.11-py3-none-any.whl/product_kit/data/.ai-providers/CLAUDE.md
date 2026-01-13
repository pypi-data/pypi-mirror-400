# [PRODUCT_NAME] - Product Kit Custom Instructions

You are assisting with **[PRODUCT_NAME]**, a product using the Product Kit framework for Requirement-Driven Design (RDD) that treats product requirements like code: structured, version-controlled, and AI-executable.

## Core Principles

1. **Load Context First**: Always read relevant context files before generating requirements
2. **Validate Against Constitution**: Check `constitution.md` for standards and principles
3. **Cross-Reference Inventory**: Verify against existing features, constraints, and data models
4. **Use Templates**: Follow structured templates for consistency
5. **Strategic Alignment**: Validate against product vision and strategic pillars

## Available Commands

### Requirements Clarification
**Purpose**: Ask clarifying questions to refine requirements before creating formal documents

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

---

### Business Requirements Document (BRD)
**Purpose**: Create a Business Requirements Document with strategic alignment and ROI

**Agent File**: `agents/productkit.brd.agent.md`
**Template**: `templates/brd_template.md`

**Context Files to Load**:
- `constitution.md` - Standards and principles
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - Target audience
- `context/market-research.md` - Competitive context
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical feasibility

---

### Product Requirements Document (PRD)
**Purpose**: Create a Product Requirements Document with detailed specifications for engineering

**Agent File**: `agents/productkit.prd.agent.md`
**Template**: `templates/prd_template.md`

**Context Files to Load**:
- `constitution.md` - Quality standards
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - User needs
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations
- `inventory/data-model.md` - Data structures
- `inventory/product-map.md` - Navigation

---

### Epic Planning Document
**Purpose**: Create an Epic document to plan a multi-phase initiative with user stories and success metrics

**Agent File**: `agents/productkit.epic.agent.md`
**Template**: `templates/epic_template.md`

**Context Files to Load**:
- `constitution.md` - Standards and principles
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - User needs
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical limitations

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

### Agent Files (Detailed Instructions)
- `agents/productkit.clarify.agent.md` - Requirements clarification workflow
- `agents/productkit.brd.agent.md` - BRD creation workflow
- `agents/productkit.prd.agent.md` - PRD creation workflow
- `agents/productkit.epic.agent.md` - Epic planning workflow
- `agents/productkit.constitution.agent.md` - Constitution generator
- `agents/productkit.update-context.agent.md` - Context file updates
- `agents/productkit.update-inventory.agent.md` - Inventory file updates

---

## Workflow Patterns

### Pattern 1: Discovery → Clarification → Document
```
User: "Users want better analytics"
→ Follow agents/productkit.clarify.agent.md
→ Gather requirements through questions
→ Follow agents/productkit.brd.agent.md or productkit.prd.agent.md
```

### Pattern 2: Direct to PRD (Well-Defined Requirements)
```
User: "Create PRD for PDF export feature"
→ Follow agents/productkit.prd.agent.md
→ Generate complete PRD with context
```

### Pattern 3: Large Initiative Planning
```
User: "Plan onboarding revamp"
→ Follow agents/productkit.epic.agent.md
→ Break into phases
→ Follow agents/productkit.prd.agent.md for Phase 1
```

---

## Validation Rules

Always validate against:

1. **Constitution Compliance**:
   - Standards must be followed
   - Decision frameworks must be applied
   - Required elements must be present (Metrics, Analytics, Rollout Plans)

2. **Strategic Alignment**:
   - Must map to Strategic Pillars (from `context/product-vision.md`)
   - Must support North Star Metric
   - Must serve Business Objectives

3. **Technical Feasibility**:
   - Check against `inventory/tech-constraints.md`
   - Verify data model compatibility
   - Validate against existing feature catalog

4. **Persona Validation**:
   - Must serve defined personas
   - Must address their goals and pain points
   - Must align with their behaviors

5. **Completeness**:
   - Problem statement with evidence
   - Success metrics with baselines and targets
   - Analytics tracking defined
   - Risks and assumptions documented

---

## Best Practices

1. **Always Start with Context**: Read relevant files before generating content
2. **Follow Agent Instructions**: Each agent file contains detailed workflows
3. **Follow Templates**: Use the structured templates for consistency
4. **Validate Early**: Check against constitution and constraints upfront
5. **Be Specific**: Use concrete metrics, not vague goals
6. **Cross-Reference**: Link to related inventory items
7. **Think Phases**: Break large work into manageable chunks
8. **Track Analytics**: Define what and how to measure
9. **Document Assumptions**: Make implicit decisions explicit
10. **Plan Rollout**: Include gradual rollout strategy

---

## Common Pitfalls to Avoid

❌ **Don't** skip loading context files  
✅ **Do** read constitution and relevant inventory before generating

❌ **Don't** create requirements without strategic alignment  
✅ **Do** validate against Strategic Pillars from product vision

❌ **Don't** forget success metrics  
✅ **Do** define metrics, baselines, and targets

❌ **Don't** ignore technical constraints  
✅ **Do** check tech-constraints.md for limitations

❌ **Don't** create standalone documents  
✅ **Do** cross-reference related features and documents

❌ **Don't** assume persona needs  
✅ **Do** validate against defined personas from context

❌ **Don't** skip analytics planning  
✅ **Do** define tracking events and properties

❌ **Don't** propose big-bang launches  
✅ **Do** include gradual rollout plan

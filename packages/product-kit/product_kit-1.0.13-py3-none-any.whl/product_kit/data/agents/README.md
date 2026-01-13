# Product Kit Agents

AI-powered agents for creating product requirements following Product Kit methodology.

## Available Agents

### � `/productkit.constitution`
**Purpose**: Create a comprehensive constitution.md with principles, standards, and decision frameworks

**Use When**:
- Setting up Product Kit for the first time
- Defining product principles and values
- Establishing non-negotiable quality standards
- Creating decision-making frameworks

**Context Files Used**: None (creates foundational document)

**Handoffs**: → Update context/inventory, then start requirements

---

### 🔄 `/productkit.update-context`
**Purpose**: Add or update context files (glossary, market research, personas, product vision)

**Use When**:
- Adding new terminology to glossary
- Documenting market research findings
- Creating or updating user personas
- Refining product vision and strategy

**Files Updated**:
- `context/glossary.md`
- `context/market-research.md`
- `context/personas.md`
- `context/product-vision.md`

**Handoffs**: → Update inventory, then create requirements

---

### 📦 `/productkit.update-inventory`
**Purpose**: Add or update inventory files (data model, feature catalog, product map, tech constraints)

**Use When**:
- Adding database entities or schema changes
- Documenting new features or deprecating old ones
- Updating navigation structure
- Recording technical constraints or limitations

**Files Updated**:
- `inventory/data-model.md`
- `inventory/feature-catalog.md`
- `inventory/product-map.md`
- `inventory/tech-constraints.md`

**Handoffs**: → Create requirements with updated inventory

---

### �📋 `/productkit.clarify`
**Purpose**: Ask clarifying questions before creating formal documents

**Use When**:
- User provides vague or incomplete requirements
- Need to gather evidence and metrics
- Want to validate strategic alignment
- Unsure which document type to create

**Context Files Used**: All context + inventory

**Handoffs**: → BRD, PRD, or Epic

---

### 💼 `/productkit.brd`
**Purpose**: Create Business Requirements Document

**Use When**:
- Need executive buy-in
- Pitching to stakeholders
- Defining business value and ROI
- Planning go-to-market strategy

**Context Files Used**:
- `constitution.md` - Standards and principles
- `context/product-vision.md` - Strategic alignment
- `context/personas.md` - Target audience
- `context/market-research.md` - Competitive context
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Existing features
- `inventory/tech-constraints.md` - Technical feasibility

**Template**: `templates/brd_template.md`

**Handoffs**: → PRD, Epic

---

### 📝 `/productkit.prd`
**Purpose**: Create Product Requirements Document

**Use When**:
- Ready for engineering handoff
- Need detailed specifications
- Defining user stories and acceptance criteria
- Planning technical implementation

**Context Files Used**:
- `constitution.md` - Quality standards (UX/UI, Design, Technical, Process)
- `context/product-vision.md` - Strategic validation
- `context/personas.md` - User needs and behaviors
- `context/glossary.md` - Consistent terminology
- `inventory/feature-catalog.md` - Feature conflicts
- `inventory/tech-constraints.md` - Technical limitations
- `inventory/data-model.md` - Data requirements
- `inventory/product-map.md` - Navigation placement

**Template**: `templates/prd_template.md`

**Handoffs**: → Development tasks

---

### 🚩 `/productkit.epic`
**Purpose**: Create Epic for multi-phase initiatives

**Use When**:
- Planning large initiatives
- Need to break work into phases
- Defining success metrics for initiative
- Coordinating multiple teams

**Context Files Used**:
- `constitution.md` - Decision frameworks (RICE)
- `context/product-vision.md` - **CRITICAL** Strategic Pillars alignment
- `context/personas.md` - Persona impact
- `context/market-research.md` - Market validation
- `context/glossary.md` - Terminology
- `inventory/feature-catalog.md` - Related features
- `inventory/tech-constraints.md` - Phasing constraints
- `inventory/data-model.md` - Schema evolution
- `inventory/product-map.md` - Product impact

**Template**: `templates/epic_template.md`

**Handoffs**: → BRD or PRD for phases

---

## Workflow Patterns

### Pattern 0: Initial Setup
```
User: Setting up Product Kit
→ /productkit.constitution (create constitution.md)
→ /productkit.update-context (add vision, personas, glossary)
→ /productkit.update-inventory (add constraints, features)
→ Ready to create requirements!
```

### Pattern 1: Start with Clarification
```
User: "We need better analytics"
→ /productkit.clarify (gather complete requirements)
→ Agent suggests: /productkit.brd or /productkit.prd
→ User chooses based on audience
```

### Pattern 2: Business Case First
```
User: "Need executive approval for new feature"
→ /productkit.brd (strategic justification, ROI)
→ Stakeholder review and approval
→ /productkit.prd (detailed specs for engineering)
```

### Pattern 3: Large Initiative
```
User: "Planning Q2 product overhaul"
→ /productkit.epic (break into phases)
→ /productkit.brd (business case for Phase 1)
→ /productkit.prd (specs for Phase 1)
→ Repeat for Phase 2, 3...
```

### Pattern 4: Direct to Specs
```
User: "Quick feature, team aligned"
→ /productkit.prd (full specification)
→ Engineering starts immediately
```

### Pattern 5: Keeping Context Fresh
```
User: "New competitor launched" or "User research complete"
→ /productkit.update-context (add market research, update personas)
→ /productkit.update-inventory (add new constraints or features)
→ Continue with requirements
```

---

## How It Works

### Context Awareness
Agents explicitly reference file locations:
```markdown
1. Load Constitution: Read `constitution.md`
2. Load Product Vision: Read `context/product-vision.md`
3. Check Constraints: Review `inventory/tech-constraints.md`
```

### Automatic Validation
Every document is checked against:
- ✅ Constitution standards (UX/UI, Design, Technical, Process)
- ✅ Strategic alignment (Product Vision pillars)
- ✅ User needs (Personas goals)
- ✅ Technical feasibility (Tech Constraints)
- ✅ Feature conflicts (Feature Catalog)

### Smart Handoffs
Agents suggest next steps:
```yaml
handoffs:
  - label: Create PRD
    agent: productkit.prd
    prompt: Generate detailed specs based on this BRD
```

---

## Constitution Requirements

All agents enforce these standards from `constitution.md`:

### UX/UI Standards
- Mobile responsive design
- Error states defined
- Empty states documented
- Loading states specified
- Accessibility requirements

### Design Standards
- Visual consistency
- Component reuse
- Design system compliance

### Technical Standards
- API contracts defined
- Error handling specified
- Security requirements
- Performance criteria

### Process Standards
- Success metrics defined
- Analytics events specified
- Rollout plan documented
- Acceptance criteria clear

---

## Getting Started

### First Time Setup
1. **Create Foundation**: Run `/productkit.constitution` to establish principles and standards
2. **Add Context**: Use `/productkit.update-context` to add vision, personas, and terminology
3. **Document Inventory**: Use `/productkit.update-inventory` to record features, constraints, and data model
4. **Start Building**: Run `/productkit.clarify` with your first feature idea

### Regular Usage
1. **Keep Context Current**: Regularly update context/inventory with `/productkit.update-context` and `/productkit.update-inventory`
2. **Create Requirements**: Use `/productkit.clarify`, `/productkit.brd`, `/productkit.prd`, or `/productkit.epic`
3. **Validate**: All documents automatically checked against constitution and inventory

### Quick Commands Reference
- `/productkit.constitution` - Create constitution.md
- `/productkit.update-context` - Update glossary, personas, vision, market research
- `/productkit.update-inventory` - Update features, constraints, data model, product map
- `/productkit.clarify` - Ask clarifying questions for requirements
- `/productkit.brd` - Create Business Requirements Document
- `/productkit.prd` - Create Product Requirements Document  
- `/productkit.epic` - Create Epic for large initiatives

See [Quick Start Guide](../../QUICKSTART.md) for detailed walkthrough.

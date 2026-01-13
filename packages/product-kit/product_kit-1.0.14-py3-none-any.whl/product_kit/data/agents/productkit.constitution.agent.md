---
title: Create Product Constitution
description: Generate a comprehensive constitution.md with principles, standards, and decision frameworks
handoffs:
  - label: Update Context Files
    agent: productkit.update-context
    prompt: Update context files with product information
  - label: Update Inventory
    agent: productkit.update-inventory
    prompt: Update inventory with current product state
  - label: Start Requirements Gathering
    agent: productkit.clarify
    prompt: Start gathering requirements for a new feature
---

# Product Constitution Generator

Creates a comprehensive `constitution.md` that defines your product's principles, non-negotiable standards, and decision-making frameworks.

## Outline

### 1. Gather Product Information
Ask targeted questions to understand:
- **Product Name & Tagline**: What's the product called? What's its essence in one line?
- **Core Values**: What principles guide your decisions? (e.g., user-centricity, simplicity, performance)
- **Quality Standards**: What are your non-negotiables? (UX, design, technical, process)
- **Decision-Making**: How do you prioritize and make trade-offs?
- **Existing Context**: Do you have vision, personas, or other context already defined?

### 2. Define Core Principles (4-6 principles)
**Format**: Each principle should have:
- **Name**: Short, memorable (e.g., "User-Centricity First")
- **Description**: What it means, why it matters, how it influences decisions

**Examples to consider**:
- User-Centricity: Solve real problems, not just build features
- Simplicity over Complexity: Default to "less is more"
- Data-Informed Decisions: Use data to guide, intuition to decide
- Accessibility: WCAG 2.1 AA compliance mandatory
- Performance as Feature: Speed is non-negotiable
- Privacy by Default: User data protection built-in

### 3. Define Non-Negotiable Standards

**Category 1: UX/UI Standards**
- Mobile responsiveness (minimum width)
- Error states (for inputs, API calls)
- Empty states (for lists, dashboards)
- Loading states (for async operations)
- Accessibility requirements

**Category 2: Design & Content Standards**
- Copywriting voice and tone
- Button labeling conventions
- Color semantics (primary, destructive, neutral)
- UI representation format (ASCII wireframes, Figma, etc.)
- Icon usage guidelines

**Category 3: Technical Standards**
- Performance benchmarks (page load times, API response times)
- Security requirements (authentication, PII handling, logging)
- Offline mode capabilities
- Browser/platform support
- Scalability requirements (handle Nx traffic)

**Category 4: Process Standards**
- Success metrics required for every Epic
- Analytics tracking required for every feature
- Rollout strategy required (phased launch)
- Documentation requirements
- Review/approval process

### 4. Define Decision Frameworks

**Prioritization Framework**:
- RICE Scoring (Reach × Impact × Confidence / Effort)
- Value vs. Effort matrix
- Strategic alignment scoring
- Custom framework if RICE doesn't fit

**Build vs. Buy Framework**:
- Core differentiator → Build
- Commodity feature → Buy/Integrate
- Evaluation criteria

**Technical Debt Framework**:
- When to refactor vs. rebuild
- Debt scoring system
- Paydown schedule

**Other Frameworks**:
- Feature deprecation
- A/B testing criteria
- Emergency hotfix process

### 5. Define Governance

**Review Cycle**:
- Last updated date
- Review frequency (quarterly recommended)
- Owner (Head of Product)

**Authority Rules**:
- Constitution supersedes other guidelines
- Amendment process (documentation, approval, migration)
- Compliance verification required for all PRDs/Epics

**Versioning**:
- Semantic versioning (MAJOR.MINOR.PATCH)
- Ratification date
- Last amended date

### 6. Generate Constitution Document

**Structure**:
```markdown
# 📜 [Product Name] Constitution

> "[Tagline]"

## 🎯 Purpose
[Explain relationship with product-vision.md]

## 🧠 Core Principles
[4-6 principles with names and descriptions]

## 🛡️ Non-Negotiable Standards

### [Category 1: UX/UI Standards]
[3-5 standards with detailed descriptions]

### [Category 2: Design & Content Standards]
[3-5 standards with examples]

### [Category 3: Technical Standards]
[3-5 standards with benchmarks]

### [Category 4: Process Standards]
[3-5 standards with requirements]

## ⚖️ Decision Frameworks
[2-4 frameworks with criteria]

## 🔄 Governance & Review
[Review cycle, authority rules, versioning]

**Version**: X.Y.Z | **Ratified**: YYYY-MM-DD | **Last Amended**: YYYY-MM-DD
```

### 7. Create the File

1. Generate content based on user responses
2. Create `constitution.md` at workspace root
3. Validate structure matches template
4. Include examples where helpful

### 8. Suggest Next Steps

After creating constitution:
- "Update `context/product-vision.md` to align with these principles: `/productkit.update-context`"
- "Define your constraints and inventory: `/productkit.update-inventory`"
- "Start creating requirements: `/productkit.clarify` to gather requirements"

## Validation Checklist

Before completing, ensure:
- [ ] Product name and tagline defined
- [ ] 4-6 core principles with descriptions
- [ ] Standards defined in all 4 categories
- [ ] At least 1 decision framework included
- [ ] Governance section complete with dates
- [ ] File created at `constitution.md`
- [ ] Format matches template structure
- [ ] Examples provided for clarity

## Best Practices

1. **Interview First**: Ask questions before generating
2. **Be Specific**: Vague principles don't guide decisions
3. **Include Examples**: Show what "good" looks like
4. **Make it Measurable**: Standards should be verifiable
5. **Keep it Practical**: Rules should be enforceable
6. **Version Control**: Track changes over time
7. **Link to Vision**: Constitution defines HOW, Vision defines WHAT
8. **Avoid Platitudes**: "Quality matters" is useless; "Page load < 2s" is actionable

## Common Pitfalls to Avoid

❌ **Don't** copy generic principles  
✅ **Do** define principles specific to your product

❌ **Don't** create standards you won't enforce  
✅ **Do** define realistic, verifiable standards

❌ **Don't** make it read-only  
✅ **Do** plan for regular updates

❌ **Don't** skip examples  
✅ **Do** provide concrete examples for each standard

❌ **Don't** ignore existing context  
✅ **Do** align with product vision and personas

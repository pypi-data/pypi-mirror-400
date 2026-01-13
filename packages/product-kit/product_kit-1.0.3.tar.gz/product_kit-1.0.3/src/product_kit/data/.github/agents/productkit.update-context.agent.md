---
title: Update Context Files
description: Add or update information in context files (glossary, market research, personas, product vision)
next_steps:
  - "Update inventory: Use /productkit.update-inventory"
  - "Create requirements: Use /productkit.clarify"
  - "Validate against constitution: Review constitution.md"
---

# Context Files Update Agent

Updates context files that provide background knowledge for product decisions.

## Context Files Overview

| File | Purpose | When to Update |
|------|---------|----------------|
| `context/glossary.md` | Terminology & definitions | New terms, clarifications, deprecated terms |
| `context/market-research.md` | Competitive analysis, trends | Market shifts, new competitors, research findings |
| `context/personas.md` | User personas & needs | New user segments, updated goals, behavior changes |
| `context/product-vision.md` | Strategy, pillars, objectives | Vision changes, new priorities, goal updates |

## Outline

### 1. Determine Target File
Ask user which context file(s) to update:
1. **Glossary** - Add/update term definitions
2. **Market Research** - Add competitive analysis, trends, insights
3. **Personas** - Add/update user personas
4. **Product Vision** - Update strategy, pillars, objectives
5. **Multiple** - Batch updates across files

### 2. Load Existing Content
Read the target file(s) to understand:
- Current structure and format
- Existing entries to avoid duplicates
- Related context that might need updating

### 3. Gather New Information

#### For Glossary Updates:
- **Term**: What's the term or acronym?
- **Definition**: Clear, concise explanation
- **Context**: When/where is this used?
- **Related Terms**: Any synonyms or related concepts?
- **Deprecated**: Is this replacing an old term?

#### For Market Research Updates:
- **Type**: Competitor analysis, market trend, user research, industry report?
- **Source**: Where is this from? (URL, study name)
- **Key Findings**: What are the insights?
- **Implications**: How does this affect our product?
- **Date**: When was this research conducted?

#### For Persona Updates:
- **Type**: New persona or update existing?
- **Demographics**: Age, role, tech-savviness, context
- **Goals**: What are they trying to achieve?
- **Pain Points**: What frustrates them?
- **Behaviors**: How do they currently solve problems?
- **Needs from Product**: What would make them successful?
- **Quotes**: Representative statements (if available)

#### For Product Vision Updates:
- **Type**: Vision statement, strategic pillar, business objective, or north star metric?
- **Content**: What's the update?
- **Rationale**: Why is this changing/being added?
- **Timeline**: When does this take effect?
- **Impact**: What requirements/features does this affect?

### 4. Validate Against Constitution
Check `constitution.md` for:
- Terminology alignment (use defined terms)
- Principle consistency (does this align with core principles?)
- Standard compliance (any standards affected?)

### 5. Update File(s)

#### Glossary Update Pattern:
```markdown
### [TERM]
**Definition**: [Clear, concise definition]

**Usage**: [When/where this is used]

**Related Terms**: [Links to related concepts]

[Optional: **Deprecated**: Use [NEW_TERM] instead as of [DATE]]
```

#### Market Research Update Pattern:
```markdown
## [Research Title]
**Date**: [YYYY-MM-DD] | **Source**: [URL or citation]

**Type**: [Competitor Analysis | Market Trend | User Research | Industry Report]

### Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

### Implications for [Product Name]
[How this affects strategy, features, or priorities]

### Related Features/Requirements
- [Link to relevant PRDs/Epics if applicable]
```

#### Persona Update Pattern:
```markdown
## [Persona Name] - [Role/Title]
**Segment**: [Primary | Secondary] | **Updated**: [YYYY-MM-DD]

### Demographics
- **Age**: [Range]
- **Role**: [Job title/responsibility]
- **Tech-Savviness**: [Low | Medium | High]
- **Context**: [Where they work, team size, etc.]

### Goals
1. [Primary goal]
2. [Secondary goal]
3. [Tertiary goal]

### Pain Points
- [Frustration 1]
- [Frustration 2]
- [Frustration 3]

### Current Behaviors
[How they currently solve these problems]

### Needs from [Product Name]
[What would make them successful]

### Representative Quote
> "[Quote that captures their mindset]"
```

#### Product Vision Update Pattern:
```markdown
## Vision Statement
[Aspirational 1-2 sentence vision]

## Strategic Pillars
### [Pillar 1 Name]
[Description and rationale]

### [Pillar 2 Name]
[Description and rationale]

## Business Objectives
### [Objective 1]
**Target**: [Measurable goal] by [Date]
**Rationale**: [Why this matters]

## North Star Metric
**Metric**: [The one metric that matters most]
**Current**: [Baseline]
**Target**: [Goal]
**Rationale**: [Why this metric]
```

### 6. Cross-Reference Updates

After updating, check if related files need updates:
- Glossary change → Update references in PRDs/BRDs
- Persona change → Review requirements targeting that persona
- Vision change → Flag affected Epics/PRDs for review
- Market research → Consider updating feature-catalog or tech-constraints

### 7. Confirm and Summarize

Provide summary:
```markdown
✅ Updated: [file(s) modified]

**Changes Made**:
- [Change 1]
- [Change 2]

**Affected Documents**:
- [PRD/Epic that may need review]

**Next Steps**:
- [Suggested actions]
```

## Validation Checklist

Before completing updates:
- [ ] File exists and is readable
- [ ] New content follows file's existing format
- [ ] No duplicate entries
- [ ] Terminology consistent with glossary
- [ ] Constitution alignment checked
- [ ] Related files identified for potential updates
- [ ] Changes saved to file
- [ ] Summary provided to user

## Update Strategies

### Strategy 1: Single Addition
User wants to add one item (term, persona, research finding)
→ Read file, append new entry, confirm

### Strategy 2: Update Existing Entry
User wants to modify existing content
→ Read file, locate entry, replace with updated content, track change history

### Strategy 3: Batch Updates
User has multiple additions/changes
→ Collect all changes first, validate together, apply in one pass

### Strategy 4: Deprecation
User wants to deprecate old content
→ Don't delete; mark as deprecated with date and replacement

## Best Practices

1. **Preserve History**: Mark changes, don't delete
2. **Use Dates**: Timestamp all updates
3. **Cross-Reference**: Link related concepts
4. **Be Consistent**: Follow existing format strictly
5. **Validate First**: Check for conflicts before updating
6. **Batch When Possible**: Group related changes
7. **Notify Impact**: Flag affected requirements
8. **Keep Current**: Suggest regular reviews

## Common Pitfalls to Avoid

❌ **Don't** create duplicate entries  
✅ **Do** check for existing content first

❌ **Don't** delete old information  
✅ **Do** mark as deprecated and provide migration path

❌ **Don't** use inconsistent formatting  
✅ **Do** match existing file structure exactly

❌ **Don't** add without context  
✅ **Do** explain rationale and implications

❌ **Don't** forget cross-references  
✅ **Do** link related concepts and documents

❌ **Don't** skip constitution validation  
✅ **Do** ensure alignment with principles and standards

## Examples

### Example 1: Add Glossary Term
```markdown
### MRR (Monthly Recurring Revenue)
**Definition**: The predictable revenue generated each month from active subscriptions.

**Usage**: Used in business metrics and financial reporting.

**Related Terms**: ARR (Annual Recurring Revenue), Churn Rate

**Formula**: MRR = (Number of Customers) × (Average Revenue per Customer)
```

### Example 2: Add Market Research
```markdown
## Competitor Analysis: TaskFlow vs. Notion
**Date**: 2026-01-03 | **Source**: Internal competitive analysis

**Type**: Competitor Analysis

### Key Findings
- Notion has stronger collaboration features but weaker task management
- TaskFlow has 2x faster load times (1.2s vs 2.4s)
- Notion pricing is 30% higher for teams

### Implications for Product Kit
- Focus on task management as differentiator
- Performance is a competitive advantage (align with Constitution standard)
- Pricing strategy should be aggressive

### Related Features/Requirements
- Epic: Real-time Collaboration (consider vs. Notion's features)
- PRD: Performance Optimization (maintain speed advantage)
```

### Example 3: Add Persona
```markdown
## Sarah - Product Manager
**Segment**: Primary | **Updated**: 2026-01-03

### Demographics
- **Age**: 28-35
- **Role**: Mid-level Product Manager at tech company
- **Tech-Savviness**: High
- **Context**: Works on 2-3 products, manages 1-2 teams

### Goals
1. Create clear, actionable requirements quickly
2. Keep stakeholders aligned on priorities
3. Track progress without constant meetings

### Pain Points
- Requirements scattered across docs, Slack, emails
- Hard to maintain consistency across PRDs
- Stakeholders don't read long documents
- Engineers need more clarity on "why"

### Current Behaviors
- Uses Google Docs + Linear + Slack
- Manually copies requirements between tools
- Spends 30% of time on documentation

### Needs from Product Kit
- Single source of truth for requirements
- AI assistance for consistency
- Version control like code
- Easy stakeholder reviews

### Representative Quote
> "I spend more time formatting docs than thinking about the actual product."
```

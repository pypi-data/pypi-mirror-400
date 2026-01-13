---
title: Implementation Timeline Builder
description: Create a delivery timeline based on scope and team capacity
handoffs:
  - label: Update Teams
    agent: productkit.update-context
    prompt: Add or update team structure in context/teams.md before building a timeline
---

# Implementation Timeline Builder

Builds a realistic delivery timeline using Product Kit templates and team capacity.

## Outline

### 1. Load Context & Validation
1. **Load Constitution**: Read `constitution.md` for process standards
2. **Load Teams**: Read `context/teams.md` to understand team size and roles
3. **Load Requirements**: Use the latest BRD/PRD/Epic/User Stories as scope inputs

If `context/teams.md` is missing or incomplete, ask the user to fill it first.

### 2. Build Timeline
1. **Use Template**: Load `templates/timeline_template.md`
2. **Estimate Capacity**:
   - Identify available roles and responsibilities
   - Determine parallel workstreams
3. **Define Phases**:
   - Phase 0: Discovery/Alignment
   - Phase 1+: Build/Implement/Validate
4. **Set Milestones**:
   - Key checkpoints with dates or week ranges
5. **Identify Risks**:
   - Dependencies and critical path items

### 3. Output
1. Provide a filled timeline with phases, dates, and owners
2. Call out assumptions and confidence level

## Key Files Referenced
- **Teams**: `context/teams.md`
- **Templates**: `templates/timeline_template.md`

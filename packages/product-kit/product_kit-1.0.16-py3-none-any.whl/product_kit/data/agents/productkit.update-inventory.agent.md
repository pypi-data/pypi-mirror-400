---
title: Update Inventory Files
description: Add or update information in inventory files (data model, feature catalog, product map, tech constraints)
handoffs:
  - label: Start Requirements Gathering
    agent: productkit.clarify
    prompt: Start gathering requirements for a new feature
---

# Inventory Files Update Agent

Updates inventory files that track the current state of your product (features, constraints, data, navigation).

## Inventory Files Overview

| File | Purpose | When to Update |
|------|---------|----------------|
| `inventory/data-model.md` | Database schema, entities | New tables/fields, schema changes, relationships |
| `inventory/feature-catalog.md` | Existing features & capabilities | New features launched, features deprecated |
| `inventory/product-map.md` | Navigation structure, IA | New pages/sections, navigation changes |
| `inventory/tech-constraints.md` | Technical limitations, dependencies | Platform changes, new constraints, resolved limitations |

## Outline

### 1. Determine Target File
Ask user which inventory file(s) to update:
1. **Data Model** - Add/update entities, fields, relationships
2. **Feature Catalog** - Add/update features, capabilities
3. **Product Map** - Add/update pages, navigation, information architecture
4. **Tech Constraints** - Add/update limitations, platform constraints
5. **Multiple** - Batch updates across files

### 2. Load Existing Content
Read the target file(s) to understand:
- Current structure and format
- Existing entries to avoid conflicts
- Related entries that might be affected

### 3. Load Related Context
Read for validation:
- `constitution.md` - Standards and constraints
- `context/product-vision.md` - Strategic alignment
- Related inventory files - Cross-references

### 4. Gather New Information

#### For Data Model Updates:
- **Type**: New entity, new field, relationship change, or schema migration?
- **Entity Name**: What's the table/model called?
- **Fields**: What data does it store? (name, type, constraints, default)
- **Relationships**: How does it relate to other entities?
- **Indexes**: Any performance indexes needed?
- **Constraints**: Foreign keys, unique constraints, validations?
- **Migration**: Is this breaking or additive?
- **Privacy**: Any PII (check Constitution security standards)?

#### For Feature Catalog Updates:
- **Type**: New feature, update existing, or deprecate?
- **Feature Name**: Clear, user-facing name
- **Category**: Core, Premium, Admin, Integration, etc.
- **Description**: What does it do?
- **User Value**: Why does this exist? What problem does it solve?
- **Status**: Planned, In Development, Beta, Live, Deprecated
- **Availability**: All users, specific plans, specific personas?
- **Dependencies**: What features or systems does it depend on?
- **Related**: What other features is it related to?
- **Launched**: When did/will it go live?
- **Metrics**: How is success measured?
- **PRD/Epic**: Link to requirements document

#### For Product Map Updates:
- **Type**: New page/section, update existing, or restructure?
- **Page/Section Name**: What's it called in the UI?
- **Location**: Where in the navigation hierarchy?
- **Path/URL**: What's the route?
- **Purpose**: What can users do here?
- **Access**: Who can see this? (role/permission)
- **Parent**: What's the parent page/section?
- **Children**: Any sub-pages?
- **Features**: What features are available here?
- **Entry Points**: How do users get here?

#### For Tech Constraints Updates:
- **Type**: Platform limitation, third-party dependency, performance constraint, security requirement?
- **Constraint Name**: Short identifier
- **Description**: What's the limitation?
- **Impact**: What can't we do? What workarounds exist?
- **Platform/Dependency**: What system causes this?
- **Version**: Is this version-specific?
- **Workaround**: Any ways to mitigate?
- **Status**: Permanent, Temporary (until when?), Resolved
- **Affects**: What features/requirements are blocked?
- **Severity**: Blocker, High, Medium, Low

### 5. Validate Update

#### Data Model Validation:
- Check for naming conflicts
- Validate against Constitution security standards (PII handling)
- Ensure relationships are bidirectional
- Check migration strategy (additive vs. breaking)

#### Feature Catalog Validation:
- No duplicate feature names
- Status is clear and up-to-date
- Dependencies exist in catalog
- Metrics defined (Constitution requirement)
- Links to PRD/Epic

#### Product Map Validation:
- No conflicting paths/URLs
- Parent-child relationships valid
- Access control defined
- Features in catalog

#### Tech Constraints Validation:
- Severity assessed
- Workarounds explored
- Affected features identified
- Timeline for resolution (if temporary)

### 6. Update File(s)

#### Data Model Update Pattern:
```markdown
## [Entity Name]
**Type**: [Core | Reference | Transaction | Analytics]

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique identifier |
| `field_name` | [Type] | [Constraints] | [Purpose] |

**Relationships**:
- Belongs to: [`RelatedEntity`] via `foreign_key_id`
- Has many: [`ChildEntity`] via `parent_id`

**Indexes**:
- `idx_field_name` on (`field_name`) - [Reason for index]

**Privacy**:
- [X] Contains PII: [field1, field2] - [Handling strategy]
- [ ] No PII

**Created**: [YYYY-MM-DD] | **Last Modified**: [YYYY-MM-DD]
```

#### Feature Catalog Update Pattern:
```markdown
## [Feature Name]
**Category**: [Core | Premium | Admin | Integration] | **Status**: [Planned | In Dev | Beta | Live | Deprecated]

**Description**:
[What this feature does in 1-2 sentences]

**User Value**:
[Why this exists, what problem it solves]

**Availability**:
- **Plans**: [Free | Pro | Enterprise | All]
- **Personas**: [Primary personas who use this]

**Key Capabilities**:
- [Capability 1]
- [Capability 2]
- [Capability 3]

**Dependencies**:
- [Required Feature/System 1]
- [Required Feature/System 2]

**Related Features**:
- [Related Feature 1] - [How they relate]
- [Related Feature 2] - [How they relate]

**Success Metrics**:
- [Metric 1]: [Baseline → Target]
- [Metric 2]: [Baseline → Target]

**Timeline**:
- **Launched**: [YYYY-MM-DD] or [Planned: Q2 2026]
- **Last Updated**: [YYYY-MM-DD]

**Documentation**:
- [PRD]: [Link to PRD]
- [Epic]: [Link to Epic]
- [User Docs]: [Link to help docs]
```

#### Product Map Update Pattern:
```markdown
## [Page/Section Name]

**Path**: `/path/to/page`

**Hierarchy**: [Parent] > [Current Page] > [Children]

**Purpose**:
[What users can do on this page]

**Access Control**:
- **Roles**: [Admin | Editor | Viewer | All]
- **Permissions**: [Specific permissions required]

**Available Features**:
- [Feature 1] - [What it does here]
- [Feature 2] - [What it does here]

**Entry Points**:
- [Navigation menu item]
- [Deep link from X]
- [Redirect from Y]

**Sub-Pages**:
1. [Sub-page 1] - `/path/to/subpage1`
2. [Sub-page 2] - `/path/to/subpage2`

**Last Updated**: [YYYY-MM-DD]
```

#### Tech Constraints Update Pattern:
```markdown
## [Constraint Name]
**Type**: [Platform Limitation | Dependency | Performance | Security] | **Severity**: [Blocker | High | Medium | Low]

**Description**:
[What's the constraint/limitation]

**Impact**:
[What we can't do, what's blocked]

**Platform/Dependency**:
- **System**: [What causes this]
- **Version**: [Version if applicable]

**Workaround**:
[If any workaround exists, describe it]

**Status**:
- [ ] Permanent
- [X] Temporary (Expected resolution: [Date])
- [ ] Resolved on [Date]

**Affects**:
- [Feature/Requirement 1]
- [Feature/Requirement 2]

**Related PRDs/Epics**:
- [Document that needs to account for this]

**Last Updated**: [YYYY-MM-DD]
```

### 7. Cross-Reference Updates

After updating, identify related changes needed:
- Data Model change → Update affected features in catalog
- Feature Catalog update → Ensure it's in product map
- Product Map change → Validate features exist in catalog
- Tech Constraint update → Flag affected PRDs/Epics

### 8. Confirm and Summarize

Provide summary:
```markdown
✅ Updated: [file(s) modified]

**Changes Made**:
- [Change 1]
- [Change 2]

**Impact**:
- [Affected features/pages/constraints]

**Action Items**:
- [ ] Update [Related File]
- [ ] Review [Affected PRD/Epic]
- [ ] Notify [Team] of constraint

**Next Steps**:
- [Suggested actions]
```

## Validation Checklist

Before completing updates:
- [ ] File exists and is readable
- [ ] New content follows file's existing format
- [ ] No duplicate entries or conflicts
- [ ] Naming conventions consistent
- [ ] Relationships/dependencies validated
- [ ] Constitution standards met
- [ ] Cross-references updated
- [ ] Status and dates included
- [ ] Changes saved to file
- [ ] Summary provided to user

## Update Strategies

### Strategy 1: Additive Change
Adding new entity/feature/page without affecting existing
→ Append to file, validate no conflicts

### Strategy 2: Modification
Updating existing entry
→ Locate entry, update in place, track "Last Updated" date

### Strategy 3: Breaking Change
Schema change, feature deprecation, page removal
→ Mark old as deprecated, create migration plan, update dependents

### Strategy 4: Batch Update
Multiple related changes across files
→ Collect all changes, validate together, apply atomically

## Best Practices

1. **Keep Status Current**: Update status fields regularly
2. **Link Bidirectionally**: If A depends on B, note it in both entries
3. **Track History**: Use "Last Updated" dates
4. **Be Specific**: Avoid vague descriptions
5. **Validate Constraints**: Check Constitution standards
6. **Cross-Reference**: Link to PRDs/Epics
7. **Plan Migrations**: For breaking changes, document migration
8. **Monitor Dependencies**: Track what's affected by changes

## Common Pitfalls to Avoid

❌ **Don't** forget to update related files  
✅ **Do** cross-reference and update dependents

❌ **Don't** leave status undefined  
✅ **Do** clearly mark Planned/In Dev/Live/Deprecated

❌ **Don't** create duplicate entries  
✅ **Do** check for existing before adding

❌ **Don't** ignore constraints  
✅ **Do** validate against Constitution and tech constraints

❌ **Don't** forget PII handling  
✅ **Do** mark PII fields and handling strategy (Constitution security standard)

❌ **Don't** break relationships  
✅ **Do** ensure bidirectional references are valid

## Examples

### Example 1: Add Data Model Entity
```markdown
## User
**Type**: Core

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| `name` | VARCHAR(255) | NOT NULL | Full name |
| `role` | ENUM | NOT NULL, DEFAULT 'viewer' | User role (admin, editor, viewer) |
| `created_at` | TIMESTAMP | NOT NULL | Account creation date |
| `last_login` | TIMESTAMP | NULL | Last login timestamp |

**Relationships**:
- Has many: [`Project`] via `owner_id`
- Has many: [`Task`] via `assignee_id`

**Indexes**:
- `idx_email` on (`email`) - Fast lookup by email for authentication
- `idx_role` on (`role`) - Filter users by role

**Privacy**:
- [X] Contains PII: `email`, `name` - Encrypted at rest, masked in logs

**Created**: 2026-01-03 | **Last Modified**: 2026-01-03
```

### Example 2: Add Feature to Catalog
```markdown
## PDF Export
**Category**: Premium | **Status**: Live

**Description**:
Allows users to export requirements documents (BRD, PRD, Epic) as formatted PDF files with custom branding.

**User Value**:
Enables sharing requirements with stakeholders who don't have platform access. Provides professional, printable format for offline reviews.

**Availability**:
- **Plans**: Pro, Enterprise
- **Personas**: Product Managers, Business Analysts, Stakeholders

**Key Capabilities**:
- Export BRD/PRD/Epic as PDF
- Custom cover page with logo
- Table of contents with hyperlinks
- Preserve formatting and diagrams

**Dependencies**:
- Document Versioning (must export specific version)
- Permission System (respects document access)

**Related Features**:
- Markdown Editor - Source format for exports
- Version Control - Determines which version to export

**Success Metrics**:
- Exports per user: 0 → 3/month average
- Stakeholder engagement: 40% → 60% review completion

**Timeline**:
- **Launched**: 2025-12-15
- **Last Updated**: 2026-01-03

**Documentation**:
- [PRD]: `requirements/prd-pdf-export.md`
- [User Docs]: `docs.productkit.io/features/pdf-export`
```

### Example 3: Add Tech Constraint
```markdown
## Mobile Browser PDF Generation Limitation
**Type**: Platform Limitation | **Severity**: Medium

**Description**:
iOS Safari and Chrome on Android have limited support for client-side PDF generation. Libraries like jsPDF have rendering issues with complex layouts.

**Impact**:
- PDF export feature works inconsistently on mobile browsers
- Complex documents may render incorrectly or fail to generate
- Users must use desktop or request server-side generation

**Platform/Dependency**:
- **System**: iOS Safari 15+, Chrome Android 90+
- **Version**: All current versions affected

**Workaround**:
Implement server-side PDF generation using Puppeteer/headless Chrome. Mobile users automatically route to server generation. Adds 2-3s latency vs. client-side.

**Status**:
- [X] Permanent (until mobile browsers improve)
- [ ] Temporary
- [ ] Resolved

**Affects**:
- PDF Export feature (mobile users only)
- PRD: PDF Export (must document mobile experience)

**Related PRDs/Epics**:
- `requirements/prd-pdf-export.md` (Section 7: Technical Constraints)

**Last Updated**: 2026-01-03
```

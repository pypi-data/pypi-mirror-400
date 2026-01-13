# 🎯 [PRODUCT_NAME] Vision & Business Overview
<!-- Example: Product Kit Vision, TaskFlow Vision & Business Overview, etc. -->

## Purpose
This document defines the strategic direction and business context for the product. It serves as the "North Star" for all product decisions and provides the AI agent with context to evaluate feature proposals against business objectives.

---

## 1. Executive Summary
*One-sentence "North Star" statement explaining why this product exists and the core value it delivers.*

[EXECUTIVE_SUMMARY]

<!-- Example: "We enable mid-market companies to make data-driven decisions in minutes, not months, by providing enterprise-grade analytics with startup-level simplicity." -->

---

## 2. Business Objectives & Strategy

### Mission
*What are we trying to achieve in the next 1–3 years?*

[MISSION_STATEMENT]

<!-- Example: "Become the default analytics platform for mid-market SaaS companies by 2028, serving 10,000+ active workspaces with best-in-class user experience and reliability." -->

### Strategic Pillars (Current Year: [CURRENT_YEAR])
*The 3–5 key areas of focus. These help the AI prioritize features.*

1. **[PILLAR_1_NAME]:** [PILLAR_1_DESCRIPTION]
2. **[PILLAR_2_NAME]:** [PILLAR_2_DESCRIPTION]
3. **[PILLAR_3_NAME]:** [PILLAR_3_DESCRIPTION]
4. **[PILLAR_4_NAME]:** [PILLAR_4_DESCRIPTION]

<!-- Example:
1. **Growth & User Acquisition:** Reduce time-to-value to under 5 minutes. Increase viral coefficient through sharing features.
2. **Operational Efficiency:** Reduce support tickets by 30% through better UX and self-service documentation.
3. **Market Compliance/Security:** Achieve SOC 2 Type II and GDPR compliance by Q3.
4. **Platform Stability:** Maintain 99.9% uptime and sub-second query response times.
-->

---

## 3. The Problem & Solution

### Problem Statement
*Describe the pain points of the current market or the specific gaps we are filling.*

[PROBLEM_STATEMENT]

<!-- Example: "Mid-market companies are trapped between expensive enterprise tools that take months to implement and oversimplified startup tools that don't scale. They need a solution that combines enterprise features with startup simplicity, but no existing platform addresses this gap effectively." -->

### Value Proposition
*How exactly does our product solve these problems better than anyone else?*

[VALUE_PROPOSITION]

<!-- Example: "We provide enterprise-grade analytics infrastructure with a 5-minute setup, intuitive UI that requires zero training, and pricing that scales with your business—not against it. Our proprietary data compression reduces costs by 10x compared to competitors." -->

---

## 4. Market & Audience

### Target Market
*Industry, geography, and segment (e.g., "SME Retailers in Southeast Asia").*

-   **Industry**: [TARGET_INDUSTRIES]
-   **Geography**: [TARGET_GEOGRAPHIES]
-   **Company Size**: [COMPANY_SIZE_RANGE]
-   **Customer Profile**: [CUSTOMER_PROFILE_DESCRIPTION]

<!-- Example:
-   **Industry**: SaaS, E-commerce, FinTech, HealthTech
-   **Geography**: North America (primary), Europe (secondary)
-   **Company Size**: 50-500 employees, $5M-$50M ARR
-   **Customer Profile**: Data-aware companies with dedicated analytics teams but limited engineering resources
-->

### Key Personas
*Reference files in `context/personas.md`.*

* **Primary Persona:** [PRIMARY_PERSONA_NAME] - [PRIMARY_PERSONA_ROLE]
* **Secondary Persona:** [SECONDARY_PERSONA_NAME] - [SECONDARY_PERSONA_ROLE]

<!-- Example:
* **Primary Persona:** The Busy Manager - Marketing/Operations Manager
* **Secondary Persona:** The Power User - Data Analyst
-->

---

## 5. Business & Revenue Model

### Revenue Streams
*How does this product sustain itself? (e.g., Subscription tiers, Transaction fees, API licensing).*

[REVENUE_STREAMS_DESCRIPTION]

<!-- Example:
- **Subscription Tiers**: Free (up to 1M events), Pro ($99/mo), Enterprise (Custom pricing)
- **Usage-Based**: Overage charges for events beyond plan limits
- **Professional Services**: Implementation and training packages
-->

### Success Metrics (North Star Metric)
*What is the #1 metric that defines the health of this product? (e.g., Monthly Active Users, Total Transaction Volume).*

**North Star Metric**: [NORTH_STAR_METRIC]

**Supporting Metrics**:
-   [SUPPORTING_METRIC_1]
-   [SUPPORTING_METRIC_2]
-   [SUPPORTING_METRIC_3]

<!-- Example:
**North Star Metric**: Weekly Active Workspaces (WAW)

**Supporting Metrics**:
-   Time to First Insight (TTFI): < 5 minutes
-   Customer Retention Rate: > 90%
-   Net Revenue Retention: > 120%
-->

---

## 6. Competitive Landscape

### Direct Competitors
*Reference `context/market_research.md` for detailed analysis.*

* **[COMPETITOR_1]**: [BRIEF_COMPARISON]
* **[COMPETITOR_2]**: [BRIEF_COMPARISON]
* **[COMPETITOR_3]**: [BRIEF_COMPARISON]

<!-- Example:
* **Competitor A**: Strong in enterprise but slow and expensive. We win on speed and UX.
* **Competitor B**: Great for startups but doesn't scale. We win on reliability and governance.
* **Competitor C**: Feature-rich but complex. We win on simplicity and time-to-value.
-->

### Our Competitive Moat
*What makes us "un-copyable"? (e.g., Proprietary data, Network effect, Speed of execution).*

[COMPETITIVE_MOAT_DESCRIPTION]

<!-- Example: "Our proprietary data compression algorithm reduces infrastructure costs by 10x, enabling us to offer enterprise features at startup prices. This technology advantage, combined with our 3-year head start and growing network effects, creates a defensible moat." -->

---

## 7. High-Level Roadmap Themes
*Non-specific timeline of where the product is heading.*

* **Phase 1 (Current - [PHASE_1_TIMEFRAME]):** [PHASE_1_THEME]
* **Phase 2 (Next - [PHASE_2_TIMEFRAME]):** [PHASE_2_THEME]
* **Phase 3 (Future - [PHASE_3_TIMEFRAME]):** [PHASE_3_THEME]

<!-- Example:
* **Phase 1 (Current - Q1-Q2 2026):** Core Stability / Feature Parity with top competitors
* **Phase 2 (Next - Q3-Q4 2026):** AI Integration / Predictive analytics
* **Phase 3 (Future - 2027):** Ecosystem / Platform Play with partner integrations
-->

---

## 8. Constraints & Dependencies

### Known Limitations
-   [CONSTRAINT_1]
-   [CONSTRAINT_2]

<!-- Example:
-   Technical: Current architecture limits us to 100M events/day per workspace
-   Business: Compliance requirements limit our addressable market to specific regions
-->

### Critical Dependencies
-   [DEPENDENCY_1]
-   [DEPENDENCY_2]

<!-- Example:
-   Partnership with cloud providers for infrastructure scaling
-   Integration with major data warehouses (Snowflake, BigQuery, Redshift)
-->

---

> **📌 Note to AI Agent:** 
> 
> Reference this document whenever creating a PRD or evaluating feature proposals. If a proposed feature in the requirements does not align with the **Strategic Pillars**, **Value Proposition**, or **North Star Metric** defined here, flag it for review before proceeding with specification.
>
> Cross-reference with:
> - `constitution.md` for quality standards
> - `context/personas.md` for user validation
> - `context/market_research.md` for competitive context
> - `inventory/` for technical feasibility

---

**Version**: [VISION_VERSION] | **Last Updated**: [LAST_UPDATED_DATE]
<!-- Example: Version: 2.1.0 | Last Updated: 2026-01-02 -->
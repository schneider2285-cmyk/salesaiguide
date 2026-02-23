# SalesAIGuide: Decision Engine Specification v1.0

**Internal document — not published to site.**
**Last updated:** February 2026

---

## 1. What "Operator-Filtered Decision Engine" Means

SalesAIGuide is a **dual-lens decision engine** that evaluates AI sales tools through two personas:

- **Org Fit** (0–100): Team-level buyer evaluating integration depth, scalability, admin overhead, security posture
- **Individual Rep Value** (0–100): Individual contributor evaluating daily-use UX, speed-to-value, personal ROI

Every tool page delivers structured decision guidance — not reviews, not rankings. The output is designed so an operator can make a buy/skip/shortlist decision without visiting any other site.

---

## 2. Official Source Universe

Sources are organized into five tiers. Tier D (Vendor Artifacts) is **mandatory** for every tool page.

### Tier A — Review Platforms
- G2, TrustRadius, Capterra, GetApp, Software Advice
- Used for: sentiment patterns, rating trends, praise/complaint clustering

### Tier B — Practitioner Communities
- Reddit (r/sales, r/salesops, r/coldemail), LinkedIn, RevGenius, Pavilion
- Used for: real-world workflows, candid opinions, implementation reality

### Tier C — Public Video
- YouTube practitioner demos, vendor walkthroughs
- Used for: UX verification, feature confirmation, workflow demonstrations

### Tier D — Vendor Artifacts (Mandatory)
- Official documentation, pricing pages, security/trust pages, integration directories, changelogs
- Used for: feature verification, pricing accuracy, integration confirmation

### Tier E — Ecosystem Signals
- Salesforce AppExchange, HubSpot Marketplace, Zapier, Chrome Web Store
- Podcasts and interviews (revenue and sales podcasts)
- Social signal (LinkedIn posts/comments, X/Twitter threads)
- Job posting signals (stack co-occurrence patterns)
- Used for: adoption indicators, ecosystem fit, emerging sentiment

---

## 3. Tool Inclusion Standard

A tool qualifies for a full Decision Module page when **all** of the following are met:

1. Minimum 50 public reviews on at least one Tier A platform
2. Active vendor documentation with current pricing
3. Evidence of real-world practitioner usage (Tier B or C)
4. Relevance to at least one SalesAIGuide category

---

## 4. Evidence Stack Minimum Coverage

Every tool page must show evidence from at least **3 of the 5 tiers**. The Evidence Signals section must include:

- **Review sentiment** (Tier A) — praise and complaint patterns
- **Community workflows** (Tier B) — real-world usage patterns
- **Demo-verified** (Tier C) — features confirmed through video
- **Docs verified** (Tier D, mandatory) — pricing, integrations, API docs

---

## 5. Confidence Model

Each tool page carries an **Evidence Confidence** label based on source coverage and consistency.

### High Confidence
- 4+ source tiers with consistent data
- Recent data (within 6 months)
- No major contradictions between sources

### Medium Confidence
- 3 source tiers with mostly consistent data
- Data moderately recent
- Minor contradictions noted

### Low Confidence
- Fewer than 3 source tiers
- Data potentially outdated
- Significant gaps or contradictions

---

## 6. Governance Rules

### Recency
- All tool pages show "Last verified: [Month Year]"
- Pages should be reverified at least quarterly
- Pricing and feature data should be checked against vendor sites

### Anti-Plagiarism
- Never reproduce review text verbatim
- Synthesize patterns, don't copy individual opinions
- All content is AI-assisted and disclosed as such

### Anti-Bias
- Affiliate relationships do not influence scores or rankings
- Every tool page shows limitations and "Who Should NOT Buy"
- No pay-to-rank; no sponsored placement in scores

### Score Integrity
- Scores are derived from the 6-dimension methodology
- Sub-scores (0–10) roll up to composite Org Fit and Individual Rep Value scores (0–100)
- Scoring dimensions: Enterprise Fit, Ease of Adoption, AI Depth, Integration Depth, Pricing Transparency, Scalability

---

## 7. Tool Page Output Contract — 15 Sections

Every tool page in the Decision Module must include exactly these 15 sections:

| # | Section | Required Content |
|---|---------|-----------------|
| 1 | Quick Verdict | Best For, Avoid If, Bottom Line + CTA |
| 2 | Org vs Individual Score | Dual scores (0–100) + 6 sub-score chips |
| 3 | Decision Snapshot | 6-dimension table with scores and notes |
| 4 | Evidence Signals | Confidence badge, 4 signal items, strength themes, limitation themes, where sources disagree, last verified date |
| 5 | Screenshots | 2–6 interface screenshots (placeholder OK for v1) |
| 6 | Pricing Breakdown | TL;DR + pricing gotchas |
| 7 | What [Tool] Is Great At | ≤5 bullet strengths |
| 8 | Where [Tool] Breaks at Scale | ≤5 bullet limitations |
| 9 | Who Should NOT Buy | 3–4 anti-personas |
| 10 | Implementation Reality | 5 stat cards (Time to Value, Setup Complexity, RevOps Lift, Training Required, Data Migration) |
| 11 | Who This Is For | Org persona + Individual persona split |
| 12 | Common Stack Pairings | ≤6 pairings + example stack |
| 13 | Best Real Demos | ≤3 video slots (placeholder OK for v1) |
| 14 | Alternatives | Comparison table with 4–5 alternatives |
| 15 | FAQ | 3 most essential questions |

Footer metadata: Last verified date + methodology link + disclosure link.

---

## 8. Hard Limits

| Element | Maximum |
|---------|---------|
| Strengths ("Great At") | 5 |
| Limitations ("Breaks at Scale") | 5 |
| Stack Pairings | 6 |
| Video Demos | 3 |
| Screenshots | 6 |
| FAQ Questions | 3 |
| Page word count | ~3,000 |

---

## 9. V1 Done Definition

The site is V1 compliant when:

- [ ] All 10 tool pages have the full 15-section Decision Module
- [ ] Every tool page has an Evidence Confidence label (High/Medium/Low)
- [ ] Every tool page has 3 strength themes + 3 limitation themes in Evidence Signals
- [ ] Every tool page has a "Where sources disagree" subsection
- [ ] Every tool page has a Screenshot Gallery section (placeholders OK)
- [ ] "What [Tool] Is Great At" has ≤5 bullets on every page
- [ ] FAQ trimmed to 3 questions on every page
- [ ] about.html contains zero instances of "aggregator" or "directory"
- [ ] index.html button reads "Browse Tools"
- [ ] editorial-policy lists all 8 source categories
- [ ] This spec doc exists at /docs/decision-engine-spec.md
- [ ] No URL changes, no canonical changes, no schema removal
- [ ] Site-wide consistent "decision engine" positioning (homepage, about, footer, methodology)

---

## 10. Categories

The site covers these categories:

1. Cold Outreach
2. Lead Prospecting
3. Data Enrichment
4. Conversation Intelligence
5. Sales Engagement
6. CRM & Pipeline
7. Sales Content
8. Revenue Intelligence
9. Dialers & Calling
10. Meeting Schedulers
11. AI SDRs
12. Intent Data
13. Sales Coaching
14. Sales Enablement

---

*End of specification.*

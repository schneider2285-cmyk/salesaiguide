# SalesAIGuide — Project Brief

> **Source of Truth** for the SalesAIGuide project.
> Last updated: February 21, 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Strategic Decisions](#2-strategic-decisions)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Current State (Feb 2026)](#4-current-state-feb-2026)
5. [Airtable Schema](#5-airtable-schema)
6. [Agent Specifications](#6-agent-specifications)
7. [Content Agent Prompts](#7-content-agent-prompts)
8. [File Structure](#8-file-structure)
9. [Affiliate Link Structure](#9-affiliate-link-structure)
10. [Credentials & Access](#10-credentials--access)
11. [Design System](#11-design-system)
12. [Weekly Workflow](#12-weekly-workflow)
13. [Revenue Projections](#13-revenue-projections)
14. [Success Metrics](#14-success-metrics)
15. [GitHub Secrets Required](#15-github-secrets-required)
16. [Contact](#16-contact)

---

## 1. Executive Summary

**SalesAIGuide** is an AI-automated affiliate directory for sales AI tools, live at [salesaiguide.com](https://salesaiguide.com).

| Field | Detail |
|---|---|
| **Owner** | Matt — Enterprise Sales Executive at Toptal |
| **Entity** | MadBrook Digital LLC |
| **Goal** | $1–3K/month passive revenue within 12 months |
| **Time Budget** | 30–60 minutes per week maintenance |
| **Domain** | salesaiguide.com |
| **Business Model** | Curated AI-tool directory monetized via affiliate links, paid listings, and sponsorships |

The core thesis is simple: sales professionals are overwhelmed by the explosion of AI tools. SalesAIGuide provides a curated, always-current directory with honest comparisons — built and maintained almost entirely by AI agents, with Matt providing final editorial approval.

---

## 2. Strategic Decisions

### 2.1 Business Model: Curated Directory, Not Review Site

SalesAIGuide is a **directory** that aggregates publicly available data (G2 ratings, Capterra reviews, Product Hunt launches), enriches it with AI-generated descriptions, and auto-publishes comparison pages. It is **not** a traditional review site that requires hands-on product testing.

Key advantages:

- Scales to 500+ tool listings without manual reviews
- AI agents handle data collection and content generation
- Matt's time is spent on approval, not creation

### 2.2 Hybrid Content Strategy

| Content Type | Source | Scale | Effort |
|---|---|---|---|
| **Tool Listings** | AI-generated from scraped G2/Capterra/PH data | 500+ potential | Automated |
| **Comparison Pages** | AI-generated verdicts (Tool A vs Tool B) | 2,000+ potential | Automated |
| **Editorial "Matt's Take"** | Optional human-written insights | Selective | Manual (optional) |
| **"Best X" Listicles** | AI-generated monthly roundups | Monthly | Automated |

### 2.3 Automation-First Pipeline

The entire content pipeline is designed around three AI agents:

1. **Data Agent** finds and enriches new tools
2. **Content Agent** writes descriptions and comparison verdicts
3. **Matt approves** in Airtable (single checkbox)
4. **Publish Agent** deploys approved content to the live site

### 2.4 Revenue Streams

| Stream | Priority | % of Revenue |
|---|---|---|
| **Affiliate commissions** | Primary | ~80% |
| **Paid / featured listings** | Secondary | ~10% |
| **Newsletter sponsorships** | Tertiary | ~5% |
| **Consulting / advisory** | Opportunistic | ~5% |

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SalesAIGuide Architecture                        │
└─────────────────────────────────────────────────────────────────────────┘

  DATA SOURCES                 PROCESSING                  DELIVERY
  ───────────                  ──────────                  ────────

  ┌──────────┐
  │   G2     │
  ├──────────┤     ┌─────────────────┐     ┌──────────────────────┐
  │ Capterra │────▶│   Data Agent    │────▶│      Airtable        │
  ├──────────┤     │  (Make.com)     │     │                      │
  │  Product │     │  NOT BUILT      │     │  Base: appzCII2ZxjE  │
  │   Hunt   │     │  Weekly Mon 6am │     │                      │
  └──────────┘     └─────────────────┘     │  Tables:             │
                                           │  ├─ Tools (30)       │
                                           │  ├─ Categories (10)  │
                                           │  └─ Comparisons (10+)│
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   Content Agent      │
                                           │   (Make.com)         │
                                           │   WORKING - Hourly   │
                                           │   Claude API         │
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   Matt Approves      │
                                           │   (Airtable UI)      │
                                           │   Status → Approved  │
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   Publish Agent      │
                                           │   GitHub Actions +   │
                                           │   scripts/publish.js │
                                           │   WORKING - Every 2h │
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   GitHub Repo        │
                                           │   schneider2285-cmyk │
                                           │   /salesaiguide      │
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   GitHub Actions     │
                                           │   Auto Deploy        │
                                           └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │   Netlify            │
                                           │   salesaiguide.com   │
                                           │   LIVE               │
                                           └──────────────────────┘
```

---

## 4. Current State (Feb 2026)

### Completed

- [x] Domain `salesaiguide.com` live and serving traffic
- [x] Netlify hosting configured and deploying
- [x] GitHub repository (`schneider2285-cmyk/salesaiguide`) set up
- [x] Airtable base created with Tools, Categories, and Comparisons tables
- [x] Content Agent working in Make.com (hourly schedule)
- [x] 31 pages live on the site
- [x] Google Search Console verified
- [x] 3 affiliate program applications submitted

### Not Completed

- [ ] **Data Agent** — not built; new tools are added manually to Airtable
- [ ] **Google Analytics** — blocked by a setup error; no traffic data yet
- [ ] **Browse AI scraper** — not configured; needed for the Data Agent pipeline

---

## 5. Airtable Schema

**Base ID:** `appzCII2ZxjERaF60`

### 5.1 Tools Table (30 records)

| Field | Type | Notes |
|---|---|---|
| Name | Single line text | e.g., "Apollo.io" |
| Slug | Single line text | e.g., "apollo-io" |
| Website | URL | Tool's homepage |
| Tagline | Single line text | One-sentence pitch |
| Category | Linked record → Categories | Can belong to multiple categories |
| Pricing Model | Single select | Free, Freemium, Paid, Enterprise |
| Starting Price | Currency | Lowest tier monthly price |
| G2 Rating | Number (1 decimal) | e.g., 4.7 |
| G2 Reviews | Number | Total G2 review count |
| Capterra Rating | Number (1 decimal) | e.g., 4.5 |
| Capterra Reviews | Number | Total Capterra review count |
| Best For | Single line text | e.g., "Mid-market outbound teams" |
| Status | Single select | Draft / Review / Published / Archived |
| Description | Long text | AI-generated, 150–200 words |
| Affiliate Link | URL | `/go/[slug]` redirect target |

### 5.2 Categories Table (10 records)

| Field | Type | Notes |
|---|---|---|
| Name | Single line text | Display name |
| Slug | Single line text | URL slug |
| Icon | Single line text | Emoji or icon class |
| Description | Long text | Category overview |
| Display Order | Number | Sort order on site |
| Tools | Linked record → Tools | Back-link to tools in this category |

**Categories:**

1. Cold Outreach
2. Lead Prospecting
3. Data Enrichment
4. Conversation Intelligence
5. Sales Engagement
6. CRM & Pipeline
7. Sales Content
8. Sales Analytics
9. Dialers & Calling
10. Meeting Schedulers

### 5.3 Comparisons Table (10+ records)

| Field | Type | Notes |
|---|---|---|
| Tool A | Linked record → Tools | First tool |
| Tool B | Linked record → Tools | Second tool |
| Title | Formula | Auto: `{Tool A} vs {Tool B}` |
| Slug | Formula | Auto: `{Tool A slug}-vs-{Tool B slug}` |
| Verdict | Long text | AI-generated, 200–300 words |
| Status | Single select | Draft / Review / Approved / Published |
| Published | Checkbox | Set by Publish Agent after deploy |
| Date Published | Date | Set by Publish Agent |
| Auto Generated | Checkbox | Whether created by Data Agent or manually |

---

## 6. Agent Specifications

### 6.1 Data Agent

| Property | Value |
|---|---|
| **Status** | NOT BUILT |
| **Platform** | Make.com (planned) |
| **Schedule** | Weekly — Monday 6:00 AM EST |
| **Dependencies** | Browse AI (not configured) |

**Pipeline:**

1. Browse AI scrapes G2, Capterra, and Product Hunt for sales AI tools
2. Make.com scenario filters for tools not already in Airtable
3. Enriches new tools with ratings, pricing, tagline, category
4. Adds new tools to Airtable with `Status = "Review"`
5. Sends Matt a summary email with new tools found

### 6.2 Content Agent

| Property | Value |
|---|---|
| **Status** | WORKING |
| **Platform** | Make.com |
| **Schedule** | Hourly |
| **AI Model** | Claude claude-sonnet-4-20250514 (max 1,024 tokens) |

**Pipeline — Tool Descriptions:**

1. Queries Airtable for tools where `Status = "Draft"` AND `Description` is empty
2. Sends tool metadata (name, tagline, category, pricing, ratings) to Claude API
3. Claude generates a 150–200 word description
4. Writes description back to Airtable

**Pipeline — Comparison Verdicts:**

1. Queries Airtable for comparisons where `Status = "Draft"` AND `Verdict` is empty
2. Fetches both linked tool records for context
3. Sends tool data to Claude API
4. Claude generates a 200–300 word comparison verdict
5. Writes verdict back to Airtable

### 6.3 Publish Agent

| Property | Value |
|---|---|
| **Status** | WORKING |
| **Platform** | GitHub Actions + Node.js |
| **Script** | `scripts/publish.js` |
| **Schedule** | Every 2 hours + manual dispatch |
| **Trigger** | GitHub Actions cron or `workflow_dispatch` |

**Pipeline:**

1. Queries Airtable for comparisons where `Status = "Approved"`
2. Fetches full tool details for both tools in each comparison
3. Generates static HTML comparison pages using the site template
4. Writes HTML files to the repository (`/comparisons/` directory)
5. Updates `sitemap.xml` with new page URLs
6. Marks comparison as `Published = true` and sets `Date Published` in Airtable
7. GitHub Actions commits changes and pushes to the repository
8. Push triggers Netlify auto-deploy to `salesaiguide.com`

---

## 7. Content Agent Prompts

### 7.1 Tool Description Prompt

```
You are a sales technology expert writing for SalesAIGuide.com, a directory
of AI-powered sales tools.

Write a compelling 150-200 word description for this tool:

Tool: {{Name}}
Tagline: {{Tagline}}
Category: {{Category}}
Pricing: {{Pricing Model}} - Starting at {{Starting Price}}/mo
G2 Rating: {{G2 Rating}} ({{G2 Reviews}} reviews)
Capterra Rating: {{Capterra Rating}} ({{Capterra Reviews}} reviews)
Best For: {{Best For}}

Requirements:
- Write in third person, professional but accessible tone
- First sentence should clearly state what the tool does
- Include who it's best for
- Mention key differentiators
- Reference the ratings naturally (don't just list them)
- End with a subtle call-to-action
- Do NOT use phrases like "game-changer" or "revolutionize"
- Do NOT make claims you can't support with the provided data
- Keep to 150-200 words
```

### 7.2 Comparison Verdict Prompt

```
You are a sales technology expert writing for SalesAIGuide.com.

Write a 200-300 word comparison verdict for these two tools:

TOOL A: {{Tool A Name}}
- Category: {{Tool A Category}}
- Pricing: {{Tool A Pricing Model}} - {{Tool A Starting Price}}/mo
- G2: {{Tool A G2 Rating}} ({{Tool A G2 Reviews}} reviews)
- Capterra: {{Tool A Capterra Rating}} ({{Tool A Capterra Reviews}} reviews)
- Best For: {{Tool A Best For}}
- Description: {{Tool A Description}}

TOOL B: {{Tool B Name}}
- Category: {{Tool B Category}}
- Pricing: {{Tool B Pricing Model}} - {{Tool B Starting Price}}/mo
- G2: {{Tool B G2 Rating}} ({{Tool B G2 Reviews}} reviews)
- Capterra: {{Tool B Capterra Rating}} ({{Tool B Capterra Reviews}} reviews)
- Best For: {{Tool B Best For}}
- Description: {{Tool B Description}}

Requirements:
- Start with a one-sentence verdict (which tool wins and why)
- Compare on 3-4 key dimensions (features, pricing, ease of use, ratings)
- Be specific about who should choose which tool
- Use the actual rating numbers to support your points
- Maintain a balanced, fair tone — don't trash either tool
- End with a clear recommendation
- Do NOT use "game-changer," "revolutionize," or similar hype words
- Keep to 200-300 words
```

---

## 8. File Structure

```
salesaiguide/
├── .github/
│   └── workflows/
│       └── publish.yml              # GitHub Actions: runs publish.js every 2h
├── comparisons/
│   ├── apollo-vs-zoominfo.html      # Generated comparison pages
│   ├── outreach-vs-salesloft.html
│   └── ...                          # More comparison HTML files
├── css/
│   └── styles.css                   # Global styles (dark theme)
├── docs/
│   ├── project-brief.md             # THIS FILE — project source of truth
│   └── ...                          # Additional documentation
├── go/
│   └── (handled via _redirects)     # Affiliate redirect pattern
├── images/
│   ├── og-image.png                 # Social sharing image
│   └── ...                          # Tool logos, category icons
├── scripts/
│   ├── publish.js                   # Node.js: fetch Airtable → generate HTML
│   └── package.json                 # Node dependencies (airtable, etc.)
├── tools/
│   └── [tool-slug].html             # Individual tool listing pages
├── _redirects                       # Netlify redirects (affiliate /go/ links)
├── categories.html                  # Category browse page
├── index.html                       # Homepage
├── robots.txt                       # Search engine directives
├── sitemap.xml                      # Auto-updated by publish.js
├── netlify.toml                     # Netlify configuration
└── README.md                        # Repository readme
```

---

## 9. Affiliate Link Structure

All affiliate links use the pattern:

```
https://salesaiguide.com/go/[tool-slug]
```

These are configured as **Netlify `_redirects`** entries:

```
/go/apollo-io          https://www.apollo.io/?utm_source=salesaiguide    302
/go/zoominfo           https://www.zoominfo.com/?utm_source=salesaiguide 302
/go/outreach           https://www.outreach.io/?utm_source=salesaiguide  302
...
```

**Current state:**

- 30 tools have `/go/` redirect entries
- Placeholder links use `?utm_source=salesaiguide` query parameter until real affiliate tracking links are approved
- Once an affiliate program approves SalesAIGuide, the redirect target is updated to include the affiliate tracking ID
- 302 (temporary) redirects are used so link equity is not passed, and the target can be updated without cache issues

---

## 10. Credentials & Access

> **IMPORTANT:** No actual secrets or tokens are stored in this document. All sensitive values are stored as GitHub repository secrets or within Make.com's encrypted credential store.

| Service | Identifier | Secret Storage |
|---|---|---|
| **Airtable** | Base ID: `appzCII2ZxjERaF60` | Token stored as `AIRTABLE_TOKEN` GitHub secret |
| **GitHub** | Repo: `schneider2285-cmyk/salesaiguide` | PAT stored as `PAT_TOKEN` GitHub secret — expires **May 22, 2026** |
| **Netlify** | Site ID: `c79f346d-e91d-42cf-80e2-295f8d7095e9` | Token stored as `NETLIFY_AUTH_TOKEN` GitHub secret |
| **Anthropic (Claude)** | Claude API | Key stored in Make.com credential store — ~$7.31 credits remaining |
| **Make.com** | Content Agent scenario | Running hourly; Publish Agent replaced by GitHub Actions |
| **Google Search Console** | salesaiguide.com | Verified via DNS; connected to Google account |
| **Google Analytics** | salesaiguide.com | **Not set up** — blocked by configuration error |

### Token Expiration Reminders

| Token | Expires | Action Required |
|---|---|---|
| GitHub PAT (`PAT_TOKEN`) | May 22, 2026 | Regenerate and update GitHub secret before expiry |
| Anthropic credits | When depleted (~$7.31 remaining) | Add credits to Anthropic account |

---

## 11. Design System

### Color Palette

| Name | Hex | Usage |
|---|---|---|
| Navy Dark | `#0a192f` | Page background |
| Navy Medium | `#112240` | Card backgrounds, sections |
| Electric Blue | `#00d9ff` | Accent highlights, hover states |
| Link Blue | `#3b82f6` | Hyperlinks |
| Green | `#10b981` | Positive indicators, CTAs |
| Star Yellow | `#fbbf24` | Star ratings |
| Slate | `#94a3b8` | Body text, secondary content |

### Typography

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;
```

System font stack — no custom font loading, fastest possible rendering.

### Layout

| Property | Value |
|---|---|
| Max content width | `900px` |
| Theme | Dark |
| Responsive | Mobile-first, fully responsive |
| Card style | Rounded corners, subtle border, navy medium background |

---

## 12. Weekly Workflow

**When:** Friday morning
**Time budget:** 30–60 minutes

| Step | Task | Time | Details |
|---|---|---|---|
| 1 | **Check Airtable — Tools** | 5 min | Review any tools with `Status = "Review"`. Read AI-generated descriptions. Approve (set to Draft/Published) or edit. |
| 2 | **Check Airtable — Comparisons** | 10 min | Review comparisons with `Status = "Review"`. Read AI verdicts. Set status to `Approved` to trigger publish. |
| 3 | **Check Make.com** | 5 min | Open Make.com dashboard. Check Content Agent scenario for failed runs. Fix any errors. |
| 4 | **Check Search Console** | 5 min | Review new pages indexed. Check for crawl errors or coverage issues. |
| 5 | **Optional: Add comparison pairs** | 10 min | Manually add new Tool A / Tool B rows in the Comparisons table with `Status = "Draft"`. Content Agent will generate verdicts on next hourly run. |

**Total: 25–35 minutes typical, 60 minutes maximum**

---

## 13. Revenue Projections

### Traffic & Revenue Ramp

| Timeline | Monthly Visitors | Estimated Revenue | Notes |
|---|---|---|---|
| Month 1 | 0–50 | $0 | Site launch, indexing, no organic traffic |
| Month 2–3 | 50–500 | $0 | Pages indexing, building domain authority |
| Month 4–6 | 500–2,000 | $50–$200 | First organic rankings, early conversions |
| Month 6–12 | 2,000–10,000 | $200–$1,000 | Compound growth, more comparisons ranking |
| Year 2 | 10,000–50,000 | $1,000–$3,000 | Target steady state |

### Monthly Operating Costs

| Service | Monthly Cost |
|---|---|
| Make.com | $9 |
| Browse AI | $19 |
| Claude API | $5–$10 |
| Airtable | $10 |
| **Total** | **$43–$48** |

### Breakeven Analysis

- Average affiliate commission: $15–$50 per conversion (varies by program)
- **Breakeven: 3–5 conversions per month** (covers $43–$48 operating costs)
- At 2% conversion rate: need 150–250 visitors/month to affiliate links
- At 5,000 sessions/month with 10% click-through to affiliate links = 500 clicks → 10 conversions → $150–$500/month

---

## 14. Success Metrics

### Month 1 Milestones

- [x] Site live at salesaiguide.com
- [x] Pages indexed in Google
- [x] Content Agent generating descriptions and verdicts
- [x] Affiliate program applications submitted

### Month 3 Milestones

- [ ] Publish Agent deploying comparison pages automatically
- [ ] 50+ comparison pages live
- [ ] First organic search traffic recorded
- [ ] 1+ affiliate program approved

### Month 6 Milestones

- [ ] 100+ pages indexed in Google
- [ ] 1,000+ monthly sessions
- [ ] First affiliate conversion
- [ ] $100+/month revenue

### Month 12 Milestones

- [ ] 200+ pages indexed in Google
- [ ] 5,000+ monthly sessions
- [ ] $500–$1,000/month revenue
- [ ] Less than 1 hour/week maintenance

---

## 15. GitHub Secrets Required

The following secrets must be configured in the GitHub repository settings (`schneider2285-cmyk/salesaiguide` → Settings → Secrets and variables → Actions):

| Secret Name | Purpose | Notes |
|---|---|---|
| `AIRTABLE_TOKEN` | Airtable API access | Used by `publish.js` to read/write Airtable records |
| `NETLIFY_AUTH_TOKEN` | Netlify deploy API | Used if deploying via Netlify CLI (optional with Git-based deploys) |
| `NETLIFY_SITE_ID` | Identifies the Netlify site | Value: `c79f346d-e91d-42cf-80e2-295f8d7095e9` |
| `PAT_TOKEN` | GitHub Personal Access Token | Used by GitHub Actions to push commits back to the repo — **expires May 22, 2026** |

---

## 16. Contact

| Field | Value |
|---|---|
| **Owner** | Matt |
| **Email** | alexsworkemailatlas@gmail.com |
| **Entity** | MadBrook Digital LLC |
| **Role** | Enterprise Sales Executive at Toptal |

---

*This document is the single source of truth for the SalesAIGuide project. Update it whenever architecture, credentials, or strategy changes.*

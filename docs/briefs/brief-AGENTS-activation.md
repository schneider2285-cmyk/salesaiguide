# Agent Activation Brief — 8 Permanent Monitoring Agents

**For Manus | Internal reference document**
**Status:** Ready to activate — all 5 build phases complete

---

## Overview

The SalesAIGuide permanent agent system consists of 8 agents that run on fixed schedules. Manus coordinates all 8 agents and compiles their outputs into a single Monday Morning Brief for Matt. This document defines exactly what each agent does, what it reads, what it writes, and what triggers a Claude Code brief.

All agent output files live in the `coordination/` directory in the repo. This directory is gitignored for the public site but committed to the private branch.

---

## Directory Structure

```
coordination/
  validation-reports/        ← Agent 1 daily output
  evidence-updates/          ← Agent 2 weekly output
  affiliate-health/          ← Agent 3 daily output
  seo-reports/               ← Agent 4 weekly output
  competitor-reports/        ← Agent 5 weekly output
  new-tool-scout/            ← Agent 6 weekly output
  revenue-reports/           ← Agent 7 weekly output
  growth-strategy/           ← Agent 8 monthly output
  monday-briefs/             ← Compiled Monday Brief (Matt reads this)
  claude-code-queue/         ← Active briefs waiting for Claude Code
```

---

## Agent 1: Site Validator

**Schedule:** Daily at 8:00 AM  
**Status:** Ready to activate

**What Manus does each day:**

1. Navigate to `https://salesaiguide.com/sitemap.xml` and extract all page URLs
2. For each URL, check:
   - HTTP status is 200
   - Page contains `journey-bar` class (all tool review pages)
   - Page contains `dm-score-number` class (all tool review pages)
   - Page contains `evidence-drawer` class (all tool review pages)
   - No `undefined` or `null` text visible in the rendered content
3. Write output to `coordination/validation-reports/YYYY-MM-DD.md`

**Output format:**
```markdown
# Site Validation Report — YYYY-MM-DD

## Summary
- Pages checked: X
- Pages passing: X
- Pages failing: X

## Failures
| Page | Check Failed | Details |
|---|---|---|
| /tools/clay-review.html | journey-bar missing | ... |

## Action Required
- [If any failures] Brief generated: coordination/claude-code-queue/fix-[date]-[slug].md
```

**What triggers a Claude Code brief:** Any page failing 2+ checks on consecutive days. Brief format: list the failing checks, the expected HTML, and the current HTML.

**Current baseline:** All 10 tool pages, 32 comparison pages, 14 category pages, 3 persona pages, and homepage should pass all checks. Run once manually to establish baseline before scheduling.

---

## Agent 2: Evidence Refresher

**Schedule:** Every Monday at 9:00 AM  
**Status:** Ready to activate (does not require Search Console)

**What Manus does each Monday:**

For each of the 10 tool JSON files in `_data/tools/`:

1. Check the `evidenceSignals.freshness.lastVerified` date — flag if older than 30 days
2. Navigate to the tool's G2 page (URL in `sidebar.externalReviews[0].url`) and record:
   - Current star rating
   - Current review count
   - Compare to `jsonLd.softwareApplication.aggregateRating` values in the JSON
3. Navigate to the tool's pricing page (URL in `pricing.tiers[0].ctaUrl` or vendor homepage) and check:
   - Starting price still matches `pricing.tiers[0].price`
   - Tier names still match
4. Write output to `coordination/evidence-updates/YYYY-MM-DD.md`

**Output format:**
```markdown
# Evidence Update Report — YYYY-MM-DD

## Fields Changed
| Tool | Field | Old Value | New Value | Action |
|---|---|---|---|---|
| Clay | aggregateRating.reviewCount | 156 | 183 | Update JSON |
| Apollo | pricing.tiers[0].price | $49/mo | $59/mo | Update JSON + brief |

## Fields Expiring (within 7 days)
| Tool | Field | Last Verified | Expires |
|---|---|---|---|

## Fields Expired
| Tool | Field | Last Verified | Days Overdue |
|---|---|---|---|

## Score Review Flags
(List any tool where 3+ fields changed — may warrant score recalculation)
```

**Critical rule:** Scores are NEVER updated automatically. If evidence changes suggest a score should change, flag it for Manus manual review. Write: "Score review recommended: [tool] [dimension] — [reason]."

**What triggers a Claude Code brief:** Any tool with 3+ changed or expired fields gets a pre-filled JSON diff brief. Manus writes the exact JSON changes needed; Claude Code applies them in one commit.

---

## Agent 3: Affiliate Health Monitor

**Schedule:** Daily at 10:00 AM  
**Status:** Partially active (Clay redirect live; Apollo, Instantly, HubSpot pending affiliate approval)

**What Manus does each day:**

Test every `/go/[tool]` redirect in `_redirects`:

1. Navigate to `https://salesaiguide.com/go/[tool]` for each tool
2. Verify final destination URL:
   - Resolves with 200 status
   - Contains the expected affiliate domain (not the homepage)
   - Contains `?ref=salesaiguide` or equivalent affiliate parameter
   - No redirect chain longer than 2 hops
3. Write output to `coordination/affiliate-health/YYYY-MM-DD.md`

**Current redirect inventory:**

| Tool | `/go/` URL | Affiliate URL | Status |
|---|---|---|---|
| Clay | `/go/clay` | `https://clay.com/?via=salesaiguide` | Active |
| Apollo | `/go/apollo` | TBD — pending Matt's application | Pending |
| Instantly | `/go/instantly` | TBD — pending Matt's application | Pending |
| HubSpot | `/go/hubspot` | TBD — pending LinkedIn verification | Pending |
| Gong | `/go/gong` | `https://gong.io` (placeholder) | Placeholder |
| Outreach | `/go/outreach` | `https://outreach.io` (placeholder) | Placeholder |
| Salesloft | `/go/salesloft` | `https://salesloft.com` (placeholder) | Placeholder |
| ZoomInfo | `/go/zoominfo` | `https://zoominfo.com` (placeholder) | Placeholder |
| Lavender | `/go/lavender` | `https://lavender.ai` (placeholder) | Placeholder |
| Smartlead | `/go/smartlead` | `https://smartlead.ai` (placeholder) | Placeholder |

**What triggers a Claude Code brief:** Any broken redirect (non-200, wrong destination, missing affiliate parameter) gets an immediate fix brief. Target: zero broken redirects at all times.

**When Matt provides affiliate URLs:** Manus updates `_redirects` directly and marks the redirect as Active in the inventory above.

---

## Agent 4: SEO Performance Monitor

**Schedule:** Every Friday at 9:00 AM  
**Status:** Waiting on Matt to connect Google Search Console

**Activation prerequisite:** Matt must connect `salesaiguide.com` to Google Search Console and grant Manus API access. Once connected, Manus can pull data via the Search Console API.

**What Manus does each Friday (once Search Console is connected):**

1. Pull Search Console data for the past 7 days via API
2. For each page, record: impressions, clicks, CTR, average position
3. Compare to previous week — flag drops of 5+ positions
4. Identify new keyword opportunities: queries where the site appears in positions 11–20 with 500+ impressions
5. Write output to `coordination/seo-reports/YYYY-MM-DD.md`

**Output format:**
```markdown
# SEO Report — Week of YYYY-MM-DD

## Top Pages by Clicks
| Page | Clicks | Impressions | CTR | Avg Position |
|---|---|---|---|---|

## Ranking Drops (5+ positions)
| Page | Keyword | Last Week | This Week | Action |
|---|---|---|---|---|

## New Keyword Opportunities
| Keyword | Impressions | Avg Position | Recommended Action |
|---|---|---|---|

## Pages to Index (if any new pages published this week)
```

**Until Search Console is connected:** Run manual spot-checks using Google Search (`site:salesaiguide.com`) and record approximate positions for the 9 priority URLs.

**Priority URLs to track:**
1. `/tools/clay-review.html` — "clay review"
2. `/tools/apollo-review.html` — "apollo.io review"
3. `/compare/clay-vs-apollo.html` — "clay vs apollo"
4. `/guides/best-cold-email-tools.html` — "best cold email tools"
5. `/guides/best-ai-sdr-tools.html` — "best ai sdr tools"
6. `/categories/best-ai-prospecting-tools.html` — "best ai prospecting tools"
7. `/for-sales-reps/` — "best sales tools for reps"
8. `/guides/best-data-enrichment-tools.html` — "best data enrichment tools"
9. `/compare/instantly-vs-smartlead.html` — "instantly vs smartlead"

---

## Agent 5: Competitor Intelligence Monitor

**Schedule:** Every Friday at 10:00 AM  
**Status:** Ready to activate

**What Manus does each Friday:**

Monitor these 5 competitor sources:
1. **ColdIQ** (`coldiq.com/blog`) — new posts in the past 7 days
2. **Lemlist Blog** (`lemlist.com/blog`) — new posts in the past 7 days
3. **Apollo Blog** (`apollo.io/blog`) — new posts in the past 7 days
4. **G2 category pages** — check the top 3 SalesAIGuide category equivalents for new tools
5. **Top-ranking pages** — Google the top 5 SalesAIGuide target keywords and check if any competitor has displaced us

For each competitor source:
- List new pages published this week
- Note any that target keywords SalesAIGuide is also targeting
- Check if any competitor page now outranks a SalesAIGuide page

Write output to `coordination/competitor-reports/YYYY-MM-DD.md`

**Output format:**
```markdown
# Competitor Intelligence Report — YYYY-MM-DD

## New Competitor Content
| Source | Title | URL | Target Keyword | Competes With |
|---|---|---|---|---|

## Ranking Changes
| Keyword | Our Page | Our Position | Competitor | Their Position | Change |
|---|---|---|---|---|---|

## Coverage Gaps (tools they review that we don't)
| Tool | Reviewed By | Estimated Search Volume | Priority |
|---|---|---|---|

## Recommended Responses
1. [Action] — [Reason] — [Priority: High/Medium/Low]
```

**What triggers a Manus brief:** Any competitor page outranking a SalesAIGuide page on a keyword with 500+ monthly searches gets a "Competitive Response Brief" — specific content improvements to recapture the ranking.

---

## Agent 6: New Tool Scout

**Schedule:** Every Wednesday at 9:00 AM  
**Status:** Ready to activate

**What Manus does each Wednesday:**

1. Check Product Hunt (`producthunt.com/topics/sales`) for new launches in the past 7 days with 50+ upvotes
2. Search Reddit: `site:reddit.com/r/sales OR r/saleshacking OR r/outbound "[new tool name]"` for any tool mentioned in 3+ threads this week
3. Check LinkedIn (search "new AI sales tool" filtered to past week) for tools with significant engagement
4. For each candidate tool, check:
   - Does SalesAIGuide already have a page for it?
   - Is it in a category SalesAIGuide covers?
   - Does it have a G2 listing?
   - What is the estimated monthly search volume for "[tool name] review"?

Write output to `coordination/new-tool-scout/YYYY-MM-DD.md`

**Output format:**
```markdown
# New Tool Scout Report — YYYY-MM-DD

## Candidates
| Tool | Source | Upvotes/Mentions | Category | G2 Listed | Est. Search Volume | Recommendation |
|---|---|---|---|---|---|---|

## Recommended for Immediate Page Build
(Tools with 100+ PH upvotes OR 3+ Reddit threads)

## Watch List
(Tools to monitor for 2 more weeks before deciding)
```

**What triggers a Manus brief:** Any tool with 100+ Product Hunt upvotes or 3+ Reddit threads in a single week gets a full research pass and a new tool page brief within 48 hours.

---

## Agent 7: Revenue Optimization Agent

**Schedule:** Every Monday at 10:00 AM  
**Status:** Partially active (Clay revenue trackable; others pending affiliate approval)

**What Manus does each Monday:**

1. Pull Netlify Analytics for the past 7 days (if available) or use Google Analytics
2. For each `/go/[tool]` redirect, record click count
3. Calculate estimated revenue:
   - Clay: ~20% commission on first month; avg contract ~$349/mo → ~$70/conversion
   - Apollo: ~20% commission; avg ~$99/mo → ~$20/conversion
   - (Update commission rates as affiliate programs are approved)
4. Identify pages with high traffic but low CTR on affiliate links (opportunity)
5. Write output to `coordination/revenue-reports/YYYY-MM-DD.md`

**Output format:**
```markdown
# Revenue Report — Week of YYYY-MM-DD

## Estimated Revenue
| Tool | Clicks | Est. Conversions (2%) | Commission | Est. Revenue |
|---|---|---|---|---|
| Clay | X | X | $70 | $X |
| Total | | | | $X |

## CTR Opportunities
| Page | Monthly Visits | Affiliate Clicks | CTR | Target CTR | Opportunity |
|---|---|---|---|---|---|

## Affiliate Program Status
| Tool | Status | Commission | Applied | Approved |
|---|---|---|---|---|

## Recommended CTA Improvements
(Pages with 500+ visits and under 3% CTR)
```

**What triggers a Manus brief:** Any page with 500+ monthly visits and under 3% affiliate CTR gets a "CTA Optimization Brief" — specific changes to CTA placement, copy, and design.

---

## Agent 8: Growth Strategy Agent

**Schedule:** First Monday of every month  
**Status:** Ready to activate

**What Manus does on the first Monday of each month:**

1. Review total site traffic trend (month-over-month)
2. Identify the 3 highest-ROI content opportunities not yet built:
   - Search volume × affiliate commission potential × competition difficulty
3. Review the current content backlog — reprioritize based on what's performing
4. Identify one strategic recommendation (new page type, new category, partnership)
5. Project 3-month traffic trajectory based on current growth rate
6. Write output to `coordination/growth-strategy/YYYY-MM.md`

**Output format:**
```markdown
# Growth Strategy Brief — YYYY-MM

## Traffic Trend
- This month: X sessions
- Last month: X sessions
- Month-over-month growth: X%
- 3-month projection: X sessions/mo

## Top 3 Content Investments
1. [Page title] — [Keyword] — [Est. volume] — [Affiliate potential] — [Difficulty]
2. ...
3. ...

## Backlog Reprioritization
(Changes to the current Claude Code queue based on performance data)

## Strategic Recommendation
[One specific recommendation with rationale]

## Revenue Projection
- Current estimated monthly revenue: $X
- 3-month projection: $X
- Key assumption: [conversion rate, traffic growth rate]
```

**What triggers a plan update:** Any month with less than 10% month-over-month traffic growth triggers a "Growth Intervention" — Manus does a deeper analysis and produces a specific action plan.

---

## The Monday Morning Brief

Every Monday, Manus compiles Agent 1, 2, 3, 7 outputs (and 4, 5, 6 on relevant weeks) into a single brief. Format:

```
SALESAIGUIDE MONDAY BRIEF — [Date]

REVENUE THIS WEEK
Estimated affiliate clicks: [X]
Estimated revenue: $[X]
Top revenue page: [page name]

URGENT (requires action today)
- [Any broken affiliate links]
- [Any pages with critical failures]

DATA UPDATES NEEDED
- [Tool] pricing expired — update brief ready
- [Tool] G2 count changed significantly

SEO HIGHLIGHTS
- [Page] moved from position 14 → 8 for "[keyword]"
- [Page] dropped from position 6 → 11 — investigate

NEW OPPORTUNITIES
- [Tool] getting 50+ Reddit mentions this week — build page?
- [Keyword] competitor page is weak — we can outrank it

THIS WEEK'S CLAUDE CODE QUEUE
1. [Brief ID] — [Title] — [Estimated time]
2. [Brief ID] — [Title] — [Estimated time]
3. [Brief ID] — [Title] — [Estimated time]
```

Matt reads the brief, approves the Claude Code queue, and the week's work begins.

---

## Activation Checklist

| Agent | Can Activate Now? | Blocker |
|---|---|---|
| Agent 1: Site Validator | Yes | None |
| Agent 2: Evidence Refresher | Yes | None |
| Agent 3: Affiliate Health Monitor | Yes (partial) | Full activation after affiliate approvals |
| Agent 4: SEO Performance Monitor | No | Matt must connect Search Console |
| Agent 5: Competitor Intelligence | Yes | None |
| Agent 6: New Tool Scout | Yes | None |
| Agent 7: Revenue Optimization | Yes (partial) | Full activation after affiliate approvals |
| Agent 8: Growth Strategy | Yes | None |

**Recommended activation order:**
1. Activate Agents 1, 2, 3 immediately — these protect what's already built
2. Activate Agents 5, 6 immediately — these feed the content pipeline
3. Activate Agents 7, 8 immediately — these drive revenue and strategy
4. Activate Agent 4 once Matt connects Search Console

---

## First Run Protocol

Before scheduling any agent, run it once manually to establish a baseline:

1. **Agent 1:** Run site validation manually. Record which pages pass/fail. This is the baseline — any new failure after this is a regression.
2. **Agent 2:** Run evidence refresh manually. Record current G2 counts and pricing for all 10 tools. This is the baseline for detecting changes.
3. **Agent 3:** Test all `/go/` redirects manually. Confirm Clay redirect works. Mark others as Pending.
4. **Agent 5:** Run competitor check manually. Record current rankings for all 9 priority URLs.

After first runs, schedule recurring tasks using Manus's scheduling capability.

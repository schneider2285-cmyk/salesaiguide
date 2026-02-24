# SalesAIGuide — Master Architecture Document
## Real-Data Engineering + Multi-Agent Orchestration + Permanent Agent System
**Authored by:** Manus AI — February 24, 2026  
**For:** Matthew Schneider  
**Status:** Approved design — ready for implementation

---

## Part 1 — The Real-Data Engineering Layer

### The Core Problem

Every tool page on SalesAIGuide must make claims that are verifiably true at the time a visitor reads them. A score of 76/100 for Clay is meaningless unless a visitor can trace it to a specific number of G2 reviews, a specific Reddit thread count, and a specific pricing page verification date. The site's entire competitive advantage — "not a directory, a decision engine" — collapses the moment a visitor finds a stale price or a score that doesn't match what they see on G2.

The current architecture has no mechanism to keep data fresh. Prices are hardcoded in HTML. Scores are manually entered. Evidence citations have no expiry. This is the single biggest risk to the site's credibility and SEO performance.

### The Solution: A Three-Layer Data Architecture

The engineering solution is a three-layer system: a **static data layer** (JSON files that Claude Code populates), a **verification layer** (scripts that check data freshness and flag stale fields), and a **display layer** (HTML that reads from the JSON and renders with freshness indicators).

---

### Layer 1: Static Data Layer (JSON Files)

Every tool has a single source-of-truth JSON file at `data/tools/[slug].json`. This file contains every data point displayed on the tool's page. No data is hardcoded in HTML — the HTML is a template that reads from the JSON.

**Key principle:** If a field in the JSON is empty or marked `"verified": false`, the HTML displays a "Data pending verification" placeholder rather than showing stale or invented data. Claude Code's session rule #7 ("Do not add placeholder content — if a data field is missing, leave it empty and note it") enforces this at the implementation level.

**Data fields with expiry:**

| Field | Expiry | Source | Verification Method |
|---|---|---|---|
| Pricing (all tiers) | 30 days | Vendor pricing page | Manual check by Evidence Refresher Agent |
| G2 rating + count | 30 days | G2.com/products/[slug] | Automated scrape |
| Reddit thread count | 7 days | Reddit search | Automated count |
| Feature list | 90 days | Vendor docs | Manual check |
| Enterprise readiness | 90 days | Vendor security docs | Manual check |
| Org Fit / Rep Value scores | 90 days | Composite of all sources | Manual recalculation |

**The `last_verified` and `expires` fields** are mandatory on every data point that can go stale:

```json
"pricing": {
  "starter": {
    "price": "$149/mo",
    "credits": "2,000/mo",
    "last_verified": "2026-02-24",
    "expires": "2026-03-24",
    "source_url": "https://clay.com/pricing"
  }
}
```

When `expires` is in the past, the Evidence Refresher Agent flags it and the display layer shows a "⚠ Verify pricing" badge next to the price.

---

### Layer 2: Verification Layer (Automated Scripts)

Three scripts live in `scripts/` and are run by the automated agents:

**`scripts/check-freshness.js`** — runs daily, checks every JSON file for expired fields, outputs a report:
```
STALE DATA REPORT — 2026-02-24
Clay: pricing.starter.price expires 2026-02-10 (14 days overdue)
Apollo: g2_count expires 2026-02-20 (4 days overdue)
Instantly: pricing.mid.price expires 2026-03-01 (5 days until expiry)
```

**`scripts/validate-schema.js`** — runs after every Claude Code session, checks that all JSON files conform to the schema, catches missing required fields before they reach production:
```
VALIDATION REPORT
✓ clay.json — all required fields present
✗ apollo.json — missing: user_voice.critical[0].date
✗ gong.json — missing: enterprise_readiness.soc2
```

**`scripts/build-sitemap.js`** — runs on every deploy, regenerates `sitemap.xml` from the actual files present in the repo, ensuring the sitemap is always accurate.

---

### Layer 3: Display Layer (HTML Templates)

The HTML for tool pages is a **template** that reads from the JSON. Since the site is static HTML (no build step, no framework), this is implemented as a JavaScript data-loading pattern:

```html
<!-- In tools/clay-review.html -->
<script>
  // Load tool data from JSON
  fetch('/data/tools/clay.json')
    .then(r => r.json())
    .then(data => {
      // Populate all dynamic fields
      document.getElementById('org-fit-score').textContent = data.org_fit_score;
      document.getElementById('rep-value-score').textContent = data.rep_value_score;
      document.getElementById('g2-rating').textContent = data.evidence.g2_rating;
      // ... etc
      
      // Check freshness and show warnings
      checkFreshness(data);
    });
    
  function checkFreshness(data) {
    const today = new Date();
    // Check pricing expiry
    Object.values(data.pricing).forEach(tier => {
      if (tier.expires && new Date(tier.expires) < today) {
        document.querySelector('.pricing-freshness-warning').style.display = 'block';
      }
    });
  }
</script>
```

**Why this approach (not a build step):** The site is pure static HTML deployed to Netlify with no build process. Adding a build step (e.g., a static site generator) would require a significant reengineering effort and is out of scope for Phase 0. The JavaScript data-loading pattern achieves the same result — data is centralized in JSON, HTML is a template — without requiring a build step. The tradeoff is that data is loaded client-side rather than baked into the HTML at build time, which has a minor SEO implication (Google can execute JavaScript, but it adds latency). This is an acceptable tradeoff given the current architecture.

**Future upgrade path:** When the site reaches Phase 4 (Category Pages), evaluate migrating to a lightweight static site generator (Eleventy or Astro) that can bake JSON data into HTML at build time. This would eliminate the client-side data-loading pattern and improve SEO performance.

---

### Data Sourcing Protocol for New Tool Pages

Every new tool page that Manus writes a brief for must include a complete, pre-researched JSON data block. Manus does the research (G2, Reddit, vendor docs, YouTube) and provides the data to Claude Code. Claude Code does not research — it only implements. This separation of concerns is critical:

- **Manus researches** → populates the JSON data block in the brief
- **Claude Code implements** → creates the JSON file and HTML page from the brief
- **Evidence Refresher Agent verifies** → checks data freshness weekly
- **Matt approves** → reviews each page before it goes live

The minimum evidence standard for a published tool page (from the orchestration plan):
- 50+ G2 reviews read and synthesized
- 10+ Reddit threads reviewed
- Vendor documentation verified within 30 days
- 3+ YouTube videos reviewed for adoption signals
- Pricing verified directly from vendor pricing page

---

## Part 2 — Claude Code Multi-Agent Orchestration for the Rebuild

### The Problem with Single-Session Claude Code

Claude Code loses context between sessions. A single Claude Code session can handle approximately one brief (30–90 minutes of work) before context degrades. Running all Phase 0–6 work sequentially through a single Claude Code instance would take weeks and would accumulate context drift — where later sessions contradict or overwrite earlier work.

The solution is a **parallel subagent architecture** where multiple Claude Code instances work simultaneously on non-overlapping parts of the codebase, coordinated by a shared state file.

---

### The Coordination System

**`CLAUDE.md`** — the master rules file that every Claude Code session reads first. Contains: project structure, design system tokens, session rules, what not to change.

**`MANUS_CONTEXT.md`** — updated by Manus after every validation. Contains: current phase, completed work, in-progress work, locked files (must not be changed), active brief links.

**`coordination/session-lock.json`** — prevents two Claude Code sessions from editing the same file simultaneously:
```json
{
  "locked_files": [
    { "file": "css/main.css", "locked_by": "session-A", "since": "2026-02-24T14:00:00Z" },
    { "file": "css/review.css", "locked_by": "session-A", "since": "2026-02-24T14:00:00Z" }
  ],
  "active_sessions": ["session-A", "session-B"],
  "completed_briefs": ["0.1", "0.2"],
  "in_progress_briefs": ["0.3", "0.4"]
}
```

**`coordination/planned_work_queue.json`** — the ordered queue of all briefs, with status:
```json
[
  { "brief_id": "0.1", "title": "How We Score page", "status": "complete", "files_changed": ["how-we-score.html", "sitemap.xml"] },
  { "brief_id": "0.2", "title": "Journey Bar component", "status": "complete", "files_changed": ["css/main.css", "js/main.js", "tools/*.html"] },
  { "brief_id": "0.3", "title": "Evidence Drawer component", "status": "in_progress", "assigned_to": "session-A" },
  { "brief_id": "0.4", "title": "Score Strip component", "status": "queued" }
]
```

---

### Parallel Subagent Architecture for the Rebuild

The rebuild is structured into **parallel workstreams** that can run simultaneously without file conflicts:

**Workstream A — CSS/Design System (1 session)**
Files: `css/main.css`, `css/review.css`
Must complete before any other workstream starts. All other sessions depend on the design tokens defined here.

**Workstream B — Tool Pages (up to 5 parallel sessions)**
Files: `tools/[slug]-review.html`, `data/tools/[slug].json`
Each tool page is an independent file. 5 sessions can work simultaneously on 5 different tool pages. Session B1 works on Clay, B2 on Apollo, B3 on Instantly, B4 on Gong, B5 on HubSpot — all at the same time.

**Workstream C — Comparison Pages (up to 5 parallel sessions)**
Files: `compare/[slug]-vs-[slug].html`
Independent files. Can run in parallel with Workstream B after Workstream A is complete.

**Workstream D — Category Pages (up to 5 parallel sessions)**
Files: `categories/[slug].html`
Independent files. Can run in parallel with Workstreams B and C.

**Workstream E — New Page Types (sequential)**
Files: `for/[persona].html`, `stacks/[stack].html`, `index.html`
Must run after all other workstreams complete. Homepage is last.

**Workstream F — Shared Infrastructure (sequential, runs between phases)**
Files: `js/main.js`, `_redirects`, `sitemap.xml`, `robots.txt`
Runs between phases to update shared infrastructure based on new pages added.

---

### How to Run Parallel Sessions (Matt's Workflow)

Running parallel Claude Code sessions requires multiple terminal windows or Claude Code instances. Here is the exact workflow:

**Step 1:** Open 5 terminal windows (or 5 Claude Code tabs if the interface supports it).

**Step 2:** In each window, navigate to the repo: `cd /tmp/salesaiguide_repo`

**Step 3:** Paste a different brief into each window. Each brief specifies which files it owns — there is no overlap.

**Step 4:** Let all 5 sessions run simultaneously. Each session commits its changes when done.

**Step 5:** After all 5 sessions complete, run `git log --oneline -20` to see all commits. Run `scripts/validate-schema.js` to check for errors.

**Step 6:** Push to main: `git push origin main`. Netlify deploys automatically.

**Step 7:** Send Manus the list of completed briefs. Manus validates the live site and updates `MANUS_CONTEXT.md` with the new state.

**Conflict prevention:** Each brief specifies exactly which files it will modify in the "What to Build" section. Before starting a session, check `coordination/session-lock.json` to ensure no other session has locked those files. If there is a conflict, run that brief in the next batch.

---

### Phase-by-Phase Parallelization Plan

| Phase | Sessions | Parallel? | Estimated Wall Time |
|---|---|---|---|
| Phase 0: Foundation | 6 sessions (0.1–0.6) | Sequential (CSS first, then others) | 1 day |
| Phase 1: Tool Pages Tier 1 | 5 sessions (Clay, Apollo, Instantly, Gong, HubSpot) | Parallel | 1 day |
| Phase 2: Tool Pages Tier 2 | 10 sessions | Parallel (2 batches of 5) | 2 days |
| Phase 3: Comparison Pages Tier 1 | 10 sessions | Parallel (2 batches of 5) | 2 days |
| Phase 4: Category Pages | 14 sessions | Parallel (3 batches) | 2 days |
| Phase 5: New Page Types | 8 sessions | Sequential (persona/stack pages, then homepage) | 2 days |
| Phase 6: Comparison Pages Tier 2 | 21 sessions | Parallel (5 batches) | 3 days |

**Total estimated wall time with parallelization: 13 days.** Without parallelization (sequential): 8–10 weeks.

---

## Part 3 — The Permanent Agent System

### Overview

Eight dedicated agents run permanently after the site is built. Each agent has a specific domain, a specific schedule, specific inputs, and specific outputs. Manus coordinates all agents and produces the weekly brief that Matt reviews on Monday mornings.

---

### Agent 1: Site Validator
**Domain:** Quality assurance  
**Schedule:** Daily at 8:00 AM  
**Trigger:** Automatic  

**What it does:** Crawls every page on salesaiguide.com. For each page, checks: (1) all links resolve with 200 status, (2) all required components are present (Journey Bar, Score Strip, Evidence Drawers), (3) all JSON data files load correctly, (4) no console errors, (5) page load time under 3 seconds.

**Output:** Daily report in `coordination/validation-reports/[date].md`. Flags any page that fails a check. If a critical failure is detected (broken page, missing component), sends an immediate alert to Matt.

**What triggers a Claude Code brief:** Any page that fails 2+ checks on consecutive days gets a "Fix Brief" generated by Manus and added to the work queue.

---

### Agent 2: Evidence Refresher
**Domain:** Data accuracy  
**Schedule:** Every Monday at 9:00 AM  
**Trigger:** Automatic  

**What it does:** For every tool page, checks: (1) G2 rating and review count against live G2 page, (2) pricing against vendor pricing page, (3) `last_verified` date against the 30-day expiry rule, (4) Reddit thread count for any major new discussions.

**Output:** Weekly "Evidence Update Report" listing: fields that have changed, fields that are expiring within 7 days, fields that are already expired. For each changed or expired field, generates the exact JSON update needed.

**What triggers a Claude Code brief:** Any tool where 3+ fields have changed or expired gets a "Data Update Brief" — a pre-filled JSON diff that Claude Code applies in under 15 minutes.

**Critical rule:** No score on the site is ever updated automatically. Score changes require Manus to review the new evidence and recalculate manually. The agent flags the change; Manus decides whether the score needs to change.

---

### Agent 3: Affiliate Health Monitor
**Domain:** Revenue infrastructure  
**Schedule:** Daily at 10:00 AM  
**Trigger:** Automatic  

**What it does:** Tests every `/go/[tool]` redirect link. Verifies: (1) redirect resolves with 200 or 301 status, (2) destination URL is the correct affiliate URL (not the homepage), (3) `?ref=salesaiguide` parameter is present in the destination URL, (4) no redirect chains longer than 2 hops.

**Output:** Daily affiliate health report. Any broken redirect is flagged as critical — a broken affiliate link means lost revenue.

**What triggers a Claude Code brief:** Any broken redirect gets an immediate fix brief. Any redirect missing the affiliate parameter gets a fix brief within 24 hours.

**Revenue tracking:** Logs click counts per `/go/[tool]` redirect using Netlify Analytics. Weekly summary shows which tools are getting the most affiliate clicks, which informs content prioritization.

---

### Agent 4: SEO Performance Monitor
**Domain:** Search visibility  
**Schedule:** Every Friday at 9:00 AM  
**Trigger:** Automatic  

**What it does:** Pulls data from Google Search Console API (once Matt connects it). Tracks: (1) impressions, clicks, and average position for every page, (2) which keywords each page ranks for, (3) pages that have dropped in ranking week-over-week, (4) new keyword opportunities (queries where the site appears but doesn't rank in top 10).

**Output:** Weekly SEO report with: top 10 pages by clicks, top 10 pages by impressions, 5 pages with biggest ranking drops, 5 new keyword opportunities.

**What triggers a Manus brief:** Any page that drops 5+ positions in a week gets a "Content Refresh Brief" — Manus researches why (competitor published better content, data went stale, etc.) and generates an update brief for Claude Code.

**Keyword opportunity pipeline:** New keyword opportunities with 500+ monthly searches and low competition get added to the content backlog as new page briefs.

---

### Agent 5: Competitor Intelligence Monitor
**Domain:** Competitive positioning  
**Schedule:** Every Friday at 10:00 AM  
**Trigger:** Automatic  

**What it does:** Monitors the top 5 competitors (ColdIQ, Lemlist Blog, Apollo Blog, G2 category pages, and the top-ranking page for each of SalesAIGuide's target keywords). Checks: (1) new pages published in the past 7 days, (2) changes to existing pages that compete with SalesAIGuide pages, (3) new tools they've reviewed that SalesAIGuide hasn't covered, (4) ranking changes on shared keywords.

**Output:** Weekly competitor report with: new competitor pages, ranking changes, coverage gaps (tools they review that SalesAIGuide doesn't), and 3 recommended responses.

**What triggers a Manus brief:** Any competitor page that outranks a SalesAIGuide page on a high-value keyword gets a "Competitive Response Brief" — a plan to improve the SalesAIGuide page to recapture the ranking.

---

### Agent 6: New Tool Scout
**Domain:** Content pipeline  
**Schedule:** Every Wednesday at 9:00 AM  
**Trigger:** Automatic  

**What it does:** Monitors Product Hunt (new launches in Sales/AI categories), LinkedIn (posts from sales leaders mentioning new tools), and relevant subreddits (r/sales, r/saleshacking, r/outbound) for newly launched or newly trending AI sales tools.

**Output:** Weekly "New Tool Report" with: 3–5 tools that look relevant, each with: tool name, category, pricing, G2 status (listed or not), estimated search volume for "[tool name] review", and a recommendation on whether to build a page.

**What triggers a Manus brief:** Any tool with 100+ Product Hunt upvotes, or any tool that appears in 3+ Reddit threads in a week, gets a full research pass from Manus and a new tool page brief within 48 hours.

---

### Agent 7: Revenue Optimization Agent
**Domain:** Affiliate revenue  
**Schedule:** Every Monday at 10:00 AM  
**Trigger:** Automatic  

**What it does:** This is the revenue-focused agent. It tracks: (1) affiliate click-through rates per tool page (clicks on `/go/[tool]` ÷ page visits), (2) which pages have high traffic but low CTR (opportunity to improve CTA placement), (3) which affiliate programs have the highest commission rates (prioritize those tools in content), (4) affiliate program status (applied, pending, approved, rejected), (5) estimated monthly revenue based on click counts and known commission rates.

**Output:** Weekly revenue report with: estimated monthly affiliate revenue, top 5 revenue-generating pages, top 5 pages with CTR improvement opportunity, affiliate program status dashboard.

**What triggers a Manus brief:** Any page with 500+ monthly visits but under 3% CTR gets a "CTA Optimization Brief" — specific changes to CTA placement, copy, and design to improve click-through rate.

**Affiliate program management:** Maintains a master list of all affiliate programs with status, commission rates, cookie duration, and payment terms. Alerts Matt when a new program needs to be applied for based on which tools are getting traffic.

---

### Agent 8: Growth Strategy Agent
**Domain:** Long-term growth  
**Schedule:** First Monday of every month  
**Trigger:** Automatic  

**What it does:** This is the strategic agent. Monthly, it: (1) reviews the site's overall traffic trend and projects 3-month forward trajectory, (2) identifies the highest-ROI content opportunities based on search volume, competition, and affiliate commission potential, (3) reviews the content roadmap and recommends reprioritization based on what's working, (4) identifies new content formats or page types that could unlock new traffic (e.g., "Best AI Sales Tools for [Industry]" pages), (5) monitors the broader AI sales tools market for category shifts that require new content strategies.

**Output:** Monthly "Growth Strategy Brief" with: traffic trend analysis, top 3 content investments for the next month, 1 strategic recommendation (new page type, new category, new partnership opportunity), updated revenue projection.

**What triggers a plan update:** Any month where traffic growth is below 10% month-over-month triggers a "Growth Intervention" — Manus does a deeper analysis and produces a specific action plan.

---

### The Monday Morning Brief

Every Monday morning, Manus compiles outputs from all 8 agents into a single **Monday Brief** that Matt reviews in 15 minutes. Format:

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

## Part 4 — Implementation Sequence

### What Gets Built First

The architecture must be built in this exact order. Each layer depends on the previous one.

**Week 1 (Phase 0): Foundation**
1. Brief 0.5 (JSON schema) — must be first, everything else reads from it
2. Brief 0.1 (How We Score page) — establishes credibility anchor
3. Briefs 0.2, 0.3, 0.4 (Journey Bar, Evidence Drawer, Score Strip) — in parallel
4. Brief 0.6 (Navigation update) — last, after all components exist
5. `scripts/check-freshness.js` and `scripts/validate-schema.js` — built by Claude Code in a dedicated session

**Week 2 (Phase 1): First Tool Pages with Full Data Layer**
- Clay and Instantly get their JSON files fully populated (already done in phase0-briefs.md)
- Apollo, Gong, HubSpot get full research passes from Manus → JSON data blocks → Claude Code implements in parallel

**Week 3 onward: Agents Come Online**
- After Phase 1 is complete and the data layer is proven, agents 1–3 (Site Validator, Evidence Refresher, Affiliate Health Monitor) come online
- Agents 4–8 come online after Phase 2 (when there's enough content to monitor)

---

### What Matt Needs to Set Up (One-Time)

| Task | Time | When |
|---|---|---|
| Connect Google Search Console to the site | 15 min | Before Phase 1 |
| Apply to Clay affiliate program (clay.com/affiliates) | 10 min | This week |
| Apply to Apollo affiliate program | 10 min | This week |
| Apply to Instantly affiliate program | 10 min | This week |
| Apply to HubSpot affiliate program | 10 min | This week |
| Connect Netlify Analytics (free, already on Netlify) | 5 min | This week |

---

### What Manus Does Each Week

| Task | Frequency | Output |
|---|---|---|
| Research new tool pages (G2 + Reddit + vendor docs) | Per brief | Complete JSON data block |
| Write implementation briefs for Claude Code | Per phase | Ready-to-paste briefs |
| Validate completed pages against quality checklist | After each Claude Code session | Validation report |
| Update MANUS_CONTEXT.md | After each validation | Updated state file |
| Compile Monday Brief from all agent outputs | Weekly | Monday Brief document |
| Recalculate scores when evidence changes | When flagged by Agent 2 | Updated JSON + brief |
| Write competitive response briefs | When flagged by Agent 5 | Content update brief |

---

## Summary

This architecture gives SalesAIGuide three things that no competitor has:

**1. Verified data at every claim.** Every score, price, and quote is sourced, dated, and automatically flagged when it goes stale. Visitors can trust the data because the system enforces freshness.

**2. Speed through parallelization.** What would take 8–10 weeks of sequential Claude Code sessions takes 13 days with parallel subagents. The rebuild is complete before competitors can respond.

**3. Compounding intelligence.** The 8 permanent agents don't just maintain the site — they continuously identify new opportunities, flag revenue leaks, and surface the next highest-ROI action. The site gets smarter and more valuable every week without requiring Matt to manually monitor anything.

---

*This document is the master architecture reference for SalesAIGuide. All briefs, agent prompts, and implementation decisions should be consistent with the principles defined here. Last updated: February 24, 2026 by Manus AI.*

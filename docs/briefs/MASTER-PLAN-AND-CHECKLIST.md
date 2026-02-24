# SalesAIGuide — Full Revised Plan & Master Checklist
**Last updated:** February 24, 2026  
**Maintained by:** Manus AI + Matt Schneider

---

## What We Actually Have Right Now

Before the plan, here is the honest current state of the site based on a direct audit of the repo:

| Section | Pages Built | Content Quality |
|---|---|---|
| Tool reviews | 10 pages | **Good** — Clay and Instantly are fully built with Decision Module. The other 8 have the structure and real data but need the v4 visual upgrade (sticky sidebar, tab nav, score strip above fold) |
| Comparison pages | 26 pages | **Good** — Real scores, dimension tables, user voice themes, FAQ schema. Need v4 visual upgrade and evidence drawers |
| Category pages | 14 pages | **Adequate** — Real tool cards with pricing and ratings. Thinner than tool pages. Need "Best For" decision guidance and links to full reviews |
| Homepage | 1 page | **Needs work** — Tool cards link to categories instead of reviews. Missing internal links to comparisons. No trust signals |
| Supporting pages | 6 pages | **Fine** — About, disclosure, editorial, 404, how-we-score all exist |
| **Total** | **~57 pages** | Site is far more complete than originally thought |

**The GA4 tracking ID is already live** (G-VRBZ6Z6885) across all pages — confirmed in the audit.  
**Netlify Forms email capture is already live** — confirmed in the last commit message.

---

## The Plan — In Plain English

The site is structurally complete. What it needs now is three things, in this order:

**1. A solid foundation** — Switch from hand-written HTML to Eleventy so all 57 pages are generated from templates. This fixes the SEO data accuracy risk and makes every future change 5x faster.

**2. A visual upgrade** — Apply the v4 design (sticky sidebar, tab navigation, score strip above fold) to all tool and comparison pages. This is what makes the site look like a serious publication, not a side project.

**3. More content** — Add the pages that are missing: more tool reviews, "Best X Tools" listicles, persona hub pages, and eventually the homepage redesign.

Everything runs in parallel where possible. Matt handles the 4 things only he can do. Claude Code handles the building. Manus handles the strategy, briefs, and quality checks.

---

## The Four Things Only Matt Can Do

These are not optional. Nothing moves forward on revenue until these are done.

| # | What | Why | How Long |
|---|---|---|---|
| 1 | **Apply to 4 affiliate programs** | Without affiliate links, the site earns $0 regardless of traffic | 30 min |
| 2 | **Give Manus GitHub write access** | Without this, every Claude Code change requires manual copy-paste | 5 min |
| 3 | **Connect Google Search Console** | Without this, we can't see what's ranking or request indexing | 15 min |
| 4 | **Request indexing for 9 priority URLs** | Google won't rank pages it hasn't found yet | 10 min |

---

## The Full Plan — Phase by Phase

---

### PHASE 0 — Foundation (Week 1)
**Goal:** Fix the architecture so everything built on top of it is solid and fast to maintain.  
**Who does the work:** Claude Code (builds), Manus (writes briefs), Matt (reviews)

#### What happens in Phase 0:

**Step 0 — Eleventy Migration (1 day, 4 Claude Code sessions)**

This is the most important thing. Right now all 57 pages are hand-written HTML. Eleventy converts them to templates + data files, so:
- Adding a new tool page = create one JSON file (instead of writing 400 lines of HTML)
- Updating the nav across all pages = edit one line (instead of editing 57 files)
- Google sees complete data immediately (no SEO risk from JavaScript loading)

*Session 1:* Install Eleventy, migrate Clay page as proof of concept → Matt reviews  
*Session 2:* Migrate all 10 tool pages  
*Session 3:* Migrate all 26 comparison pages + 14 category pages + homepage  
*Session 4:* Update Netlify deploy, set up branch-per-brief workflow, verify live site

**Step 0.5 — JSON Data Schema (60 min)**

Create the standard data format that every tool page reads from. Clay and Instantly get fully populated JSON files first. This is the "single source of truth" for every score, price, and quote on the site.

**Steps 0.1–0.6 — Foundation Components (half a day)**

Six small components that every page will use:
- The "How We Score" credibility page (already exists as a folder — needs content)
- Journey Bar (the 5-tab navigation on tool pages)
- Evidence Drawer (the expandable source citations)
- Score Strip (dual Org/Rep scores visible above the fold)
- Navigation update (add "How We Score" link, remove placeholder "Guides")

---

### PHASE 1 — Tool Page Upgrade (Week 2)
**Goal:** Apply the v4 design to all 10 existing tool pages.  
**Who does the work:** Claude Code (5 pages in parallel), Manus (writes data briefs for each tool)

The v4 design means:
- Sticky right sidebar (price box + "Visit [Tool]" CTA + At a Glance stats + Compare links)
- 5-tab navigation (Pricing Reality / Who Should Use / Decision Snapshot / Where It Breaks / Stack Fit)
- Score Strip visible above the fold without scrolling
- Evidence drawers on every score dimension

Manus writes the data brief for each tool (with all JSON data populated) before Claude Code builds the page. Claude Code runs 5 sessions in parallel — one per tool.

**Tools in Phase 1:** Clay, Apollo, Instantly, Gong, HubSpot, Salesloft, Outreach, Lavender, Smartlead, ZoomInfo

---

### PHASE 2 — Comparison Page Upgrade (Week 3)
**Goal:** Upgrade the 10 highest-traffic comparison pages to v4 standard.  
**Who does the work:** Claude Code (parallel batches), Manus (prioritizes by search volume)

The 26 comparison pages already have real content — they need the v4 visual treatment: evidence confidence bars, org/rep reader selector, and the sticky sidebar. The 16 lower-priority comparisons get upgraded in Phase 4.

**Priority comparisons (Phase 2):** Clay vs Apollo, Clay vs Clearbit, Apollo vs ZoomInfo, Outreach vs Salesloft, Instantly vs Smartlead, Instantly vs Lemlist, Gong vs Chorus, HubSpot vs Pipedrive, Lavender vs Autobound, Cognism vs ZoomInfo

---

### PHASE 3 — New Content Pages (Week 4)
**Goal:** Add the high-value pages that are missing from the site entirely.  
**Who does the work:** Claude Code, Manus (writes all content briefs)

These pages target high-volume searches that the site currently has no answer for:

- **5 "Best X Tools" listicles** — "Best AI Sales Tools 2026", "Best Cold Email Tools", "Best Data Enrichment Tools", "Best Sales Intelligence Platforms", "Best AI SDR Tools" (combined ~15,000 searches/month)
- **Clay Alternatives page** — 2,400 searches/month, high affiliate intent
- **10 new tool review pages** — Cognism, LeadIQ, Lusha, Lemlist, 6sense, Bombora, Clari, Seismic, Highspot, Vidyard

---

### PHASE 4 — Category Pages + Remaining Comparisons (Week 5–6)
**Goal:** Upgrade all 14 category pages to full decision-guide standard, and upgrade the remaining 16 comparison pages.  
**Who does the work:** Claude Code (parallel), Manus (content briefs)

Category pages currently have tool cards but lack the "Best For" decision guidance that makes them useful. Each category page gets: a buyer guide intro, a "Who should use this category" section, a ranked tool list with evidence, and links to the relevant comparison pages.

---

### PHASE 5 — Persona Hubs + Homepage Redesign (Week 7–8)
**Goal:** Add persona-specific entry points and redesign the homepage.  
**Who does the work:** Claude Code, Manus (designs)

This is the last phase because the homepage redesign should reflect the full site, not a half-built one. Persona hub pages (/for/solo-rep, /for/sales-team, /for/revops, /for/sales-leader, /for/enterprise) let visitors self-select into the right content.

The homepage redesign applies the v4 design language to the entry point: asymmetric layout, live stats bar, featured tool cards linking to actual reviews, and a methodology trust section.

---

### ONGOING — The 8 Permanent Agents
**Goal:** The site runs itself after Phase 2 is complete.  
**Who manages:** Manus (sets up and monitors), Matt (reviews Monday Brief)

| Agent | What It Does | When It Runs |
|---|---|---|
| Site Validator | Checks all 57+ pages for broken links, missing data, rendering errors | Daily |
| Evidence Refresher | Flags stale prices, G2 counts, and expiry dates | Every Monday |
| Affiliate Health Monitor | Verifies all /go/ redirects are live and earning | Daily |
| SEO Performance Monitor | Tracks rankings, flags drops, surfaces new opportunities | Every Friday |
| Competitor Intelligence | Monitors competing sites for new pages and ranking changes | Every Friday |
| New Tool Scout | Finds new AI sales tools worth reviewing | Every Wednesday |
| Revenue Optimization | Tracks affiliate CTR, commission rates, program status | Every Monday |
| Growth Strategy | Monthly trajectory, content ROI, what to build next | 1st Monday/month |

Every Monday morning these agents compile into a **Monday Brief** — a 15-minute read that tells Matt exactly what's working, what's broken, and what to do next.

---

## The Master Checklist

Track this together. Matt's items are marked **[MATT]**. Claude Code items are marked **[CC]**. Manus items are marked **[MANUS]**.

---

### This Week — No Blockers, Start Now

- [ ] **[MATT]** Apply to Clay affiliate program — clay.com/affiliates
- [ ] **[MATT]** Apply to Apollo affiliate program — apollo.io/partners
- [ ] **[MATT]** Apply to Instantly affiliate program — instantly.ai/affiliates
- [ ] **[MATT]** Apply to HubSpot affiliate program — hubspot.com/partners/affiliates
- [ ] **[MATT]** Give Manus GitHub write access — GitHub → repo → Settings → Collaborators
- [ ] **[MATT]** Connect Google Search Console to salesaiguide.com
- [ ] **[MATT]** Request manual indexing for these 9 URLs in Search Console:
  - salesaiguide.com/tools/clay-review.html
  - salesaiguide.com/tools/apollo-review.html
  - salesaiguide.com/tools/instantly-review.html
  - salesaiguide.com/tools/gong-review.html
  - salesaiguide.com/tools/hubspot-review.html
  - salesaiguide.com/compare/clay-vs-apollo.html
  - salesaiguide.com/compare/outreach-vs-salesloft.html
  - salesaiguide.com/categories/data-enrichment.html
  - salesaiguide.com/categories/cold-outreach.html
- [ ] **[MANUS]** Write the Eleventy migration brief (Step 0) — **DONE**
- [ ] **[MANUS]** Write the JSON schema brief (Step 0.5) — **DONE**
- [ ] **[MANUS]** Write the Phase 0 component briefs (0.1–0.6) — **DONE**
- [ ] **[CC]** Execute Step 0 Session 1 — Install Eleventy, migrate Clay page
- [ ] **[MATT]** Review Eleventy proof of concept — approve before Session 2
- [ ] **[CC]** Execute Step 0 Sessions 2–4 — Full migration
- [ ] **[CC]** Execute Step 0.5 — JSON schema + clay.json + instantly.json
- [ ] **[CC]** Execute Steps 0.1–0.6 — Foundation components

---

### Week 2 — Phase 1 (Tool Page Upgrade)

- [ ] **[MANUS]** Write data briefs for all 10 tool pages (JSON data populated)
- [ ] **[CC]** Upgrade Clay review to v4 (sticky sidebar, tab nav, score strip)
- [ ] **[CC]** Upgrade Apollo review to v4
- [ ] **[CC]** Upgrade Instantly review to v4
- [ ] **[CC]** Upgrade Gong review to v4
- [ ] **[CC]** Upgrade HubSpot review to v4
- [ ] **[CC]** Upgrade Salesloft review to v4
- [ ] **[CC]** Upgrade Outreach review to v4
- [ ] **[CC]** Upgrade Lavender review to v4
- [ ] **[CC]** Upgrade Smartlead review to v4
- [ ] **[CC]** Upgrade ZoomInfo review to v4
- [ ] **[MATT]** Review all 10 upgraded pages — approve before Phase 2
- [ ] **[MANUS]** Validate all 10 pages against v4 spec
- [ ] **[MATT]** Update _redirects with real affiliate URLs (once programs approve)

---

### Week 3 — Phase 2 (Comparison Page Upgrade)

- [ ] **[MANUS]** Write data briefs for 10 priority comparison pages
- [ ] **[CC]** Upgrade Clay vs Apollo to v4
- [ ] **[CC]** Upgrade Clay vs Clearbit to v4
- [ ] **[CC]** Upgrade Apollo vs ZoomInfo to v4
- [ ] **[CC]** Upgrade Outreach vs Salesloft to v4
- [ ] **[CC]** Upgrade Instantly vs Smartlead to v4
- [ ] **[CC]** Upgrade Instantly vs Lemlist to v4
- [ ] **[CC]** Upgrade Gong vs Chorus to v4
- [ ] **[CC]** Upgrade HubSpot vs Pipedrive to v4
- [ ] **[CC]** Upgrade Lavender vs Autobound to v4
- [ ] **[CC]** Upgrade Cognism vs ZoomInfo to v4
- [ ] **[MANUS]** Site Validator agent goes live
- [ ] **[MANUS]** Affiliate Health Monitor agent goes live
- [ ] **[MANUS]** Evidence Refresher agent goes live

---

### Week 4 — Phase 3 (New Content Pages)

- [ ] **[MANUS]** Write content briefs for 5 "Best X Tools" listicles
- [ ] **[MANUS]** Write content brief for Clay Alternatives page
- [ ] **[MANUS]** Write data briefs for 10 new tool review pages
- [ ] **[CC]** Build "Best AI Sales Tools 2026" mega-guide
- [ ] **[CC]** Build "Best Cold Email Tools" listicle
- [ ] **[CC]** Build "Best Data Enrichment Tools" listicle
- [ ] **[CC]** Build "Best Sales Intelligence Platforms" listicle
- [ ] **[CC]** Build "Best AI SDR Tools" listicle
- [ ] **[CC]** Build Clay Alternatives page
- [ ] **[CC]** Build 10 new tool review pages (Cognism, LeadIQ, Lusha, Lemlist, 6sense, Bombora, Clari, Seismic, Highspot, Vidyard)
- [ ] **[MANUS]** SEO Performance Monitor agent goes live (requires Search Console API)
- [ ] **[MANUS]** Competitor Intelligence agent goes live

---

### Weeks 5–6 — Phase 4 (Category Pages + Remaining Comparisons)

- [ ] **[MANUS]** Write upgrade briefs for all 14 category pages
- [ ] **[CC]** Upgrade all 14 category pages to full decision-guide standard
- [ ] **[CC]** Upgrade remaining 16 comparison pages to v4
- [ ] **[MANUS]** New Tool Scout agent goes live
- [ ] **[MANUS]** Revenue Optimization agent goes live

---

### Weeks 7–8 — Phase 5 (Persona Hubs + Homepage)

- [ ] **[MANUS]** Write persona hub page briefs
- [ ] **[CC]** Build /for/solo-rep persona hub
- [ ] **[CC]** Build /for/sales-team persona hub
- [ ] **[CC]** Build /for/revops persona hub
- [ ] **[CC]** Build /for/sales-leader persona hub
- [ ] **[CC]** Build /for/enterprise persona hub
- [ ] **[MANUS]** Design homepage redesign brief
- [ ] **[CC]** Execute homepage redesign
- [ ] **[MATT]** Review and approve homepage redesign
- [ ] **[MANUS]** Growth Strategy agent goes live
- [ ] **[MANUS]** Full Monday Brief system operational

---

### Ongoing — Revenue Milestones to Track

- [ ] First affiliate program approval received
- [ ] First affiliate link live on site
- [ ] First affiliate click tracked in GA4
- [ ] First affiliate conversion (first dollar earned)
- [ ] $100/month affiliate revenue
- [ ] $500/month affiliate revenue
- [ ] $1,000/month affiliate revenue
- [ ] 100 email subscribers
- [ ] 500 email subscribers
- [ ] 5,000 monthly organic visitors (Google Analytics)
- [ ] 10,000 monthly organic visitors

---

## How to Use This Document

**Matt:** Work through the [MATT] items in order. The affiliate applications are the most urgent — approval takes 1–3 days and nothing earns until they're done.

**Starting Claude Code each session:** Tell it to read `CLAUDE.md` and `MANUS_CONTEXT.md` first, then give it the specific brief for that session. Never give it more than one brief per session.

**Starting Manus each session:** Say "read MANUS_CONTEXT.md from the repo and tell me where we are." Manus will reconstruct full context and tell you exactly what's next.

**Updating this checklist:** At the end of every Claude Code session, tell Manus what was completed. Manus updates `MANUS_CONTEXT.md` and this checklist. Matt pastes both into the repo.

---

*This document replaces all previous plan documents. It is the single source of truth for the SalesAIGuide build.*  
*Generated by Manus AI — February 24, 2026*

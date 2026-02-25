# MANUS_CONTEXT.md — SalesAIGuide Strategic Context
**Last updated:** February 24, 2026  
**Maintained by:** Manus AI  
**Read this file at the start of every Manus session.**

---

## Current State (as of Feb 24, 2026)

**Phase 4 is complete and merged to main.** The site now has full v4 design coverage across all page types.

| Section | Count | Quality |
|---|---|---|
| Tool review pages | 10 | v4 complete (sticky sidebar, dual scores, 5-tab nav) |
| Comparison pages | 32 | v4 complete (dual scores, reader selector, sidebar CTAs) |
| Category pages | 14 | v4 complete (category.njk layout, decision guidance) |
| Guide/listicle pages | 6 | v4 complete (guide.njk layout, targeting 12,300/mo searches) |
| Root pages | 6 | Fine (index, about, disclosure, editorial, 404, how-we-score) |
| Blog | Placeholder only | Not started |

**Build:** 65 files, 0 errors. Netlify auto-deploys from `main`.

**Infrastructure confirmed working:**
- GA4 tracking: `G-VRBZ6Z6885` — live across all pages
- Netlify Forms email capture — live
- Netlify deploy: pushes to `main` auto-deploy via `.github/workflows/deploy.yml`
- GitHub write access: Manus has direct commit/push access
- Clay affiliate link: `https://clay.earth/?via=matthew-schneider` — live in `_redirects`

**Infrastructure NOT in use (ignore):**
- The Make.com + Airtable pipeline described in CLAUDE.md was designed but never activated. Do not set it up.
- `scripts/publish.js` and `.github/workflows/publish.yml` are unused. Do not run them.

---

## Phases Completed

| Phase | What Was Done | Status |
|---|---|---|
| Phase 0 | Eleventy migration (57 pages), GA4, Netlify Forms, branch strategy | Done |
| Phase 1 | All 10 tool review pages upgraded to v4 (dual scores, journey bar, sticky sidebar) | Done |
| Phase 2 | 10 priority comparison pages upgraded to v4 (dual scores, reader selector, sidebar CTAs) | Done |
| Phase 3 | 6 new guide pages created targeting 12,300 monthly searches | Done |
| Phase 4 | 14 category pages + 21 remaining comparison pages migrated to v4 layouts | Done |
| Phase 5 | Persona hubs + homepage redesign | Next |

---

## What's Next Right Now

**Phase 5 — Persona Hubs + Homepage Redesign**

Two parts:

**Part A: Persona Hubs (3 pages)**
- `/for-sales-reps/` — curated tool picks for individual contributors
- `/for-sales-managers/` — curated tool picks for team leads
- `/for-revenue-ops/` — curated tool picks for RevOps/operations

**Part B: Homepage Redesign**
The current homepage is a basic list of tool links. It needs a full v4 redesign:
- Asymmetric hero layout with live stats bar (X tools reviewed, X comparisons, updated monthly)
- Featured tools section with "Read Review" CTAs
- Methodology trust bar (how we score, ORG vs REP explained)
- Curated comparisons section (top 5 most-searched comparisons)
- Email capture section

**Before starting Phase 5:** Write `docs/briefs/brief-PHASE5-homepage-redesign.md`

**Start Claude Code with:**
```
Read CLAUDE.md and MANUS_CONTEXT.md first.
Today's task is Phase 5 from docs/briefs/brief-PHASE5-homepage-redesign.md.
Goal: Build 3 persona hub pages and redesign the homepage to v4 standard.
```

---

## 8 Permanent Monitoring Agents

These agents are defined in `docs/briefs/MASTER-ARCHITECTURE.md`. They launch after Phase 5 is complete.

| Agent | Domain | Schedule | Status |
|---|---|---|---|
| Agent 1: Site Validator | Quality Assurance | Daily @ 8:00 AM | Pending |
| Agent 2: Evidence Refresher | Data Accuracy | Every Monday @ 9:00 AM | Pending |
| Agent 3: Affiliate Health Monitor | Revenue Infrastructure | Daily @ 10:00 AM | Pending |
| Agent 4: SEO Performance Monitor | Search Visibility | Every Friday @ 9:00 AM | Pending |
| Agent 5: Competitor Intelligence | Competitive Positioning | Every Friday @ 10:00 AM | Pending |
| Agent 6: New Tool Scout | Content Pipeline | Every Wednesday @ 9:00 AM | Pending |
| Agent 7: Revenue Optimization | Affiliate Revenue | Every Monday @ 10:00 AM | Pending |
| Agent 8: Growth Strategy | Long-Term Growth | 1st Monday of Every Month | Pending |

Agents 1-3 launch after Phase 1 content is live and indexed. Agents 4-8 launch after Phase 2 content is live.

---

## Design Standard — v4

**v4 tool page layout:**
- Sticky right sidebar: price box + Visit CTA button + At a Glance stats + Compare links
- 5-tab in-page navigation: Pricing Reality / Who Should Use / Decision Snapshot / Where It Breaks / Stack Fit
- Score Strip above the fold: Org score + Rep score visible without scrolling, with evidence pill count
- Evidence Drawers: expandable source citations on every scored dimension
- Journey Bar: breadcrumb-style progress indicator at top of page

**v4 comparison page layout:**
- Side-by-side score display (Org + Rep for each tool)
- Evidence confidence bar
- Org/Rep reader selector (filters content by buyer type)
- Dimension-by-dimension table with Edge column

**v4 category page layout:**
- Category hero with top picks sidebar
- Decision guidance section (who should use this category)
- Tool cards with scores and CTAs

---

## Affiliate Programs

| Tool | Status | Commission | Redirect | Notes |
|---|---|---|---|---|
| Clay | Active | 20% recurring | /go/clay | clay.earth/?via=matthew-schneider — live in _redirects |
| Instantly | Pending | ~25% recurring | /go/instantly | Applied — awaiting approval |
| Apollo | Pending | 20% recurring | /go/apollo | Requires LinkedIn verification |
| HubSpot | Pending | 30% recurring (up to 1yr) | /go/hubspot | Requires LinkedIn verification |
| Gong | Not applied | TBD | /go/gong | Apply when page has traffic |
| Salesloft | Not applied | TBD | /go/salesloft | Apply when page has traffic |
| ZoomInfo | Not applied | TBD | /go/zoominfo | Apply when page has traffic |

**Matt action required:** Complete LinkedIn verification to unlock Apollo + HubSpot affiliate applications.

---

## Revenue Timeline

| Month | Projected Revenue |
|---|---|
| Month 1 | $50-150 |
| Month 3 | $1,000-3,000 |
| Month 6 | $4,000-10,000 |
| Month 12 | $12,000-30,000 |

---

## What Must Not Change

- The `_redirects` file — do not modify affiliate redirect rules without explicit instruction
- The `css/main.css` and `css/review.css` files — do not rewrite, only extend
- The GA4 tracking snippet — already live, do not remove or change the ID (G-VRBZ6Z6885)
- The Netlify Forms email capture — already live, do not remove
- The `sitemap.xml` — update when adding new pages, never remove existing entries
- The `CLAUDE.md` file — do not modify (it is Claude Code's system context)

---

## Branch Strategy

Every brief gets its own branch. Never commit directly to `main`.

Completed branches (merged to main):
- `phase4-categories-comparisons` — Phase 4 Sessions 1-3 (complete)

Next branch to create: `phase5-homepage-redesign`

---

## Key Files Reference

| File | Purpose |
|---|---|
| `CLAUDE.md` | Claude Code's system context — do not modify |
| `MANUS_CONTEXT.md` | This file — Manus reads at start of every session |
| `docs/briefs/MASTER-ARCHITECTURE.md` | Full architecture: data layer, agent system, parallelization plan |
| `docs/briefs/brief-PHASE4-categories-and-comparisons.md` | Phase 4 brief (complete) |
| `_layouts/compare.njk` | v4 comparison page template |
| `_layouts/category.njk` | v4 category page template |
| `_layouts/guide.njk` | v4 guide/listicle template |
| `_layouts/tool.njk` | v4 tool review template |
| `data/*.json` | Tool data files — single source of truth for all scores and evidence |
| `_private/progress.html` | Live progress dashboard (open in browser, not served publicly) |
| `_redirects` | Netlify redirects for all /go/[tool] affiliate links |
| `css/main.css` | Global styles |
| `css/review.css` | Tool/comparison page styles |

---

## Session Handoff Protocol

At the end of every Manus session, update this file with:
1. What was completed
2. What is in progress
3. What is next
4. Any blockers

At the end of every Claude Code session, Claude Code should:
1. List every file changed
2. Confirm the site still builds/renders correctly
3. Commit and push to the active feature branch

---

*This file is the permanent memory for the SalesAIGuide project. Keep it current.*

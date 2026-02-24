# MANUS_CONTEXT.md — SalesAIGuide Strategic Context
**Last updated:** February 24, 2026  
**Maintained by:** Manus AI  
**Read this file at the start of every Manus session.**

---

## Current State (as of Feb 24, 2026)

The site is structurally complete. 57 pages exist and are live at salesaiguide.com.

| Section | Count | Quality |
|---|---|---|
| Tool review pages | 10 | Good structure, need v4 visual upgrade |
| Comparison pages | 26 | Good content, need v4 visual upgrade |
| Category pages | 14 | Adequate — tool cards exist, need decision guidance |
| Root pages | 6 | Fine (index, about, disclosure, editorial, 404, how-we-score) |
| Blog | Placeholder only | Not started |

**Infrastructure confirmed working:**
- GA4 tracking: `G-VRBZ6Z6885` — live across all pages
- Netlify Forms email capture — live (deployed Feb 24)
- Netlify deploy: pushes to `main` auto-deploy via `.github/workflows/deploy.yml`
- GitHub write access: Manus has direct commit/push access

**Infrastructure NOT in use (ignore):**
- The Make.com + Airtable pipeline described in CLAUDE.md was designed but never activated. AIRTABLE_TOKEN secret was never set. Do not set it up — we are using Eleventy + JSON files instead.
- `scripts/publish.js` and `.github/workflows/publish.yml` are unused. Do not run them.

---

## The Plan — 5 Phases

Full details in `docs/briefs/MASTER-PLAN-AND-CHECKLIST.md`.

| Phase | What | Status |
|---|---|---|
| **Phase 0** | Eleventy migration + foundation components | **NEXT — start here** |
| Phase 1 | Upgrade all 10 tool pages to v4 design | Not started |
| Phase 2 | Upgrade 10 priority comparison pages to v4 | Not started |
| Phase 3 | New content pages (listicles, Clay Alternatives, 10 new tool reviews) | Not started |
| Phase 4 | Category page upgrades + remaining comparisons | Not started |
| Phase 5 | Persona hubs + homepage redesign | Not started |

---

## What's Next Right Now

**Phase 0, Step 0 — Eleventy Migration**

Brief is at: `docs/briefs/brief-STEP0-eleventy-migration.md`

The site is currently pure static HTML. Every page is hand-written. We are migrating to Eleventy so:
1. Pages are generated from templates + JSON data files (no more hand-writing HTML)
2. Google sees complete data baked into HTML at build time (no SEO risk)
3. Updating shared components (nav, footer) requires editing one file, not 57

**Session 1 goal:** Install Eleventy, create directory structure, migrate `tools/clay-review.html` as proof of concept. Do not migrate any other pages. Matt reviews before Session 2.

**Start Claude Code with:**
```
Read CLAUDE.md and MANUS_CONTEXT.md first.

Today's task is Phase 0, Step 0, Session 1 from docs/briefs/brief-STEP0-eleventy-migration.md.

Goal: Install Eleventy, create the _layouts/_templates/_includes/_data directory structure, 
and migrate tools/clay-review.html to use a template + JSON data file.
The output HTML must be visually identical to the current page.

Do not migrate any other pages yet.
When done: list every file created/changed, confirm eleventy --serve starts without errors.
```

---

## Design Standard — v4

All tool and comparison pages must match the v4 design. Reference: `docs/briefs/phase0-briefs.md` and the mockup described below.

**v4 tool page layout:**
- **Sticky right sidebar** (not a bottom bar): price box + "Visit [Tool] ↗" CTA button + At a Glance stats (G2 rating, review count, starting price, free trial Y/N, category) + Compare links (3–4 "[Tool] vs X" links)
- **5-tab in-page navigation**: Pricing Reality / Who Should Use / Decision Snapshot / Where It Breaks / Stack Fit
- **Score Strip above the fold**: Org score + Rep score visible without scrolling, with evidence pill count
- **Evidence Drawers**: expandable source citations on every scored dimension
- **Journey Bar**: breadcrumb-style progress indicator at top of page

**v4 comparison page layout:**
- Side-by-side score display (Org + Rep for each tool)
- Evidence confidence bar
- Org/Rep reader selector (filters content by buyer type)
- Dimension-by-dimension table with Edge column

---

## What Must Not Change

- The `_redirects` file — do not modify affiliate redirect rules
- The `css/main.css` and `css/review.css` files — do not rewrite, only extend
- The GA4 tracking snippet — already live, do not remove or change the ID
- The Netlify Forms email capture — already live, do not remove
- The `sitemap.xml` — update when adding new pages, never remove existing entries
- The `CLAUDE.md` file — do not modify (it is Claude Code's system context)

---

## Branch Strategy (Mandatory from Phase 0 onward)

Every brief gets its own branch. Never commit directly to `main`.

```
main          ← protected, always deployable
staging       ← integration branch, Manus validates here
brief/[id]    ← one branch per brief (e.g. brief/step0-session1)
```

Set this up in Session 4 of Step 0.

---

## Affiliate Programs

| Tool | Program Status | Affiliate URL |
|---|---|---|
| Clay | Application pending | `/go/clay` → placeholder |
| Apollo | Application pending | `/go/apollo` → placeholder |
| Instantly | Application pending | `/go/instantly` → placeholder |
| HubSpot | Application pending | `/go/hubspot` → placeholder |
| Gong | Not yet applied | `/go/gong` → placeholder |
| Salesloft | Not yet applied | `/go/salesloft` → placeholder |

Update `_redirects` when real affiliate URLs are received.

---

## Key Files Reference

| File | Purpose |
|---|---|
| `CLAUDE.md` | Claude Code's system context — do not modify |
| `MANUS_CONTEXT.md` | This file — Manus reads at start of every session |
| `docs/briefs/MASTER-PLAN-AND-CHECKLIST.md` | Full plan + checklist |
| `docs/briefs/MASTER-ARCHITECTURE.md` | Technical architecture decisions |
| `docs/briefs/brief-STEP0-eleventy-migration.md` | Current active brief |
| `docs/briefs/phase0-briefs.md` | Phase 0 component briefs (0.1–0.6) |
| `coordination/active_work.json` | Current Claude Code tasks |
| `coordination/planned_work_queue.json` | Backlog |
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
3. Update `coordination/active_work.json` and `coordination/completed_work.json`

---

*This file is the permanent memory for the SalesAIGuide project. Keep it current.*

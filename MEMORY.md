# Sales AI Guide — Project Memory

## Current State (Sprint 22 Complete, Mar 2026)

**132 pages, 132 A-tier, 0 B-tier, 0 C-tier**

| Type | Count | A-Tier |
|------|-------|--------|
| Reviews | 33 | 33 |
| Comparisons | 59 | 59 |
| Category Hubs | 10 | 10 |
| Alternatives | 11 | 11 |
| Best For | 7 | 7 |
| Editorial Pages | 9 | 9 |
| Directory Pages | 3 | 3 |
| **Total** | **132** | **132** |

## Site URL
https://salesaiguide.com (Netlify)

## Key Files
- Gate script: `scripts/indexation_gate.py` (READ-ONLY, never modify)
- Slop lint: `scripts/test_slop_signals.py`
- Sprint backlog: `docs/tasks/todo.md`
- Lessons: `docs/tasks/lessons.md`
- Gate report: `gate-report.json` (auto-generated)
- Sitemaps: `sitemap-core.xml`, `sitemap-hold.xml` (auto-generated)
- Feed scripts: `scripts/generate_feed.py`, `scripts/add_schemas.py`
- Safe swaps: `scripts/apply_safe_swaps.py`
- Cross-category links: `scripts/add_cross_category_links.py`

## Categories (10 Hubs)
1. Cold Outreach — 7 tools, 13 comparisons
2. Lead Prospecting — 7 tools, 9 comparisons
3. Data Enrichment — 5 tools, 8 comparisons
4. Conversation Intelligence — 5 tools, 5 comparisons
5. Sales Engagement — 5 tools, 6 comparisons
6. CRM & Pipeline — 5 tools, 1 comparison
7. Sales Content — 4 tools, 3 comparisons
8. Dialers & Calling — 6 tools, 10 comparisons (100% coverage)
9. Meeting Schedulers — 4 tools, 1 comparison
10. Sales Analytics — 4 tools, 3 comparisons

All 10 hubs have cross-category links + relevant alternatives guide links.

## Best For Pages (6 Pages + 1 Index)
1. Best CRM for Small Business — Close, Pipedrive, HubSpot, Freshsales
2. Best Free CRM Software — HubSpot (free), Freshsales (free), Close (trial), Pipedrive (trial)
3. Best Cold Email Software for Startups — Instantly, Lemlist, Smartlead, Woodpecker
4. Best AI Sales Tools — Gong, Apollo, Clay, Instantly, Lavender
5. Best Sales Automation Software — HubSpot, Outreach, Apollo, Instantly, Reply.io
6. Best Sales Tools for Solopreneurs — Pipedrive, Instantly, Apollo, Hunter

## Alternatives (10 Tool Pages + 1 Index)
1. Salesforce Alternatives — 4 CRMs (Close, HubSpot, Pipedrive, Freshsales)
2. ZoomInfo Alternatives — 5 prospecting tools (Apollo, Seamless.AI, Lusha, Clearbit, Hunter)
3. Outreach Alternatives — 5 engagement platforms (Salesloft, Reply.io, Instantly, Lemlist, Woodpecker)
4. HubSpot CRM Alternatives — 3 CRMs (Close, Pipedrive, Freshsales)
5. Gong Alternatives — 3 CI platforms (Chorus, Clari, Fireflies)
6. Salesloft Alternatives — 5 engagement platforms (Outreach, Reply.io, Instantly, Lemlist, Woodpecker)
7. Apollo Alternatives — 5 prospecting tools (ZoomInfo, Lusha, Seamless.AI, Hunter, Clay)
8. Calendly Alternatives — 2 schedulers (SavvyCal, Chili Piper)
9. Instantly Alternatives — 5 cold email tools (Lemlist, Smartlead, Reply.io, Woodpecker, Mailshake)
10. Clay Alternatives — 5 enrichment tools (Apollo, ZoomInfo, Clearbit, Lusha, Seamless.AI)

## Deploy Command
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd /Users/matthewschneider/Downloads/salesaiguide && netlify deploy --dir . --prod
```

## Gate Command
```bash
cd /Users/matthewschneider/Downloads/salesaiguide
python3 scripts/indexation_gate.py --site-dir . --out-dir . --base-url https://salesaiguide.com
```

## Sprint History
- Sprint 19: Created 12 new comparison pages (75→87 pages).
- Sprint 20: Added 6 reviews + 12 comparisons (87→105 pages), then Sprint 20b added 3 more comparisons (105→108). Sprint 20c: schema enrichment (BreadcrumbList + FAQPage), sitemaps/RSS, alt text, selective similarity fixes. 108/108 A-tier.
- Sprint 21: Created 8 alternatives pages + index (108→117 pages). Added cross-category links to all 10 category hubs. Updated compare/index.html with alternatives section. 117/117 A-tier.
- Sprint 22: Created 7 "Best For" pages (new keyword class) + 6 comparison gap fills + 2 alternatives expansion (117→132 pages). Best For pages capture "best X for Y" keyword structure. Comparisons fill lead prospecting gaps (hunter-vs-zoominfo, clearbit-vs-zoominfo, apollo-vs-clearbit), cross-category engagement pairs (outreach-vs-instantly, salesloft-vs-reply-io), and complete dialers coverage (dialpad-vs-kixie = 100%). Added Instantly + Clay alternatives. 132/132 A-tier.

## Key Lessons
- Gate counts CSS as content words — never extract inline CSS to external files without retesting
- SEO keyword swaps must be evaluated individually — "sales teams→revenue teams" kills rankings
- Safe stylistic swaps: side-by-side→head-to-head, ease of use→usability, all-in-one→unified
- Editorial gate threshold is 200 content words (much lower than reviews at 1500w)
- Every H2 section needs 50+ content words (not just links/tables)
- Alternatives pages capture entirely new keyword cluster without cannibalizing comparisons
- "Best For" pages capture "best X for Y" keyword class — different intent from category hubs
- FAQ intro prose needs 55+ words between <h2> and first <h3> to pass gate reliably
- Dollar amounts EVERYWHERE in article body (FAQ answers, verdict, bullet lists, intro) need adjacent citation <a href> links
- Bottom CTA divs with /go/ affiliate links must be OUTSIDE the <article> tag
- H3 headings in standalone CTA sections can trigger thin_sections — use <p><strong> instead

# Sales AI Guide — Project Memory

## Current State (Sprint 21 Complete, Mar 2026)

**117 pages, 117 A-tier, 0 B-tier, 0 C-tier**

| Type | Count | A-Tier |
|------|-------|--------|
| Reviews | 33 | 33 |
| Comparisons | 53 | 53 |
| Category Hubs | 10 | 10 |
| Alternatives | 9 | 9 |
| Editorial Pages | 9 | 9 |
| Directory Pages | 3 | 3 |
| **Total** | **117** | **117** |

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
2. Lead Prospecting — 7 tools, 6 comparisons
3. Data Enrichment — 5 tools, 8 comparisons
4. Conversation Intelligence — 5 tools, 5 comparisons
5. Sales Engagement — 5 tools, 4 comparisons
6. CRM & Pipeline — 5 tools, 1 comparison
7. Sales Content — 4 tools, 3 comparisons
8. Dialers & Calling — 6 tools, 7 comparisons
9. Meeting Schedulers — 4 tools, 1 comparison
10. Sales Analytics — 4 tools, 3 comparisons

All 10 hubs have cross-category links + relevant alternatives guide links.

## Alternatives (8 Tool Pages + 1 Index)
1. Salesforce Alternatives — 4 CRMs (Close, HubSpot, Pipedrive, Freshsales)
2. ZoomInfo Alternatives — 5 prospecting tools (Apollo, Seamless.AI, Lusha, Clearbit, Hunter)
3. Outreach Alternatives — 5 engagement platforms (Salesloft, Reply.io, Instantly, Lemlist, Woodpecker)
4. HubSpot CRM Alternatives — 3 CRMs (Close, Pipedrive, Freshsales)
5. Gong Alternatives — 3 CI platforms (Chorus, Clari, Fireflies)
6. Salesloft Alternatives — 5 engagement platforms (Outreach, Reply.io, Instantly, Lemlist, Woodpecker)
7. Apollo Alternatives — 5 prospecting tools (ZoomInfo, Lusha, Seamless.AI, Hunter, Clay)
8. Calendly Alternatives — 2 schedulers (SavvyCal, Chili Piper)

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

## Key Lessons
- Gate counts CSS as content words — never extract inline CSS to external files without retesting
- SEO keyword swaps must be evaluated individually — "sales teams→revenue teams" kills rankings
- Safe stylistic swaps: side-by-side→head-to-head, ease of use→usability, all-in-one→unified
- Editorial gate threshold is 200 content words (much lower than reviews at 1500w)
- Every H2 section needs 50+ content words (not just links/tables)
- Alternatives pages capture entirely new keyword cluster without cannibalizing comparisons

# Sales AI Guide — Project Memory

## Current State (Sprint 19 Complete, Mar 2026)

**87 pages, 87 A-tier, 0 B-tier, 0 C-tier**

| Type | Count | A-Tier |
|------|-------|--------|
| Reviews | 27 | 27 |
| Comparisons | 41 | 41 |
| Category Hubs | 10 | 10 |
| Editorial Pages | 6 | 6 |
| Directory Pages | 3 | 3 |
| **Total** | **87** | **87** |

## Site URL
https://salesaiguide.com (Netlify)

## Key Files
- Gate script: `scripts/indexation_gate.py` (READ-ONLY, never modify)
- Slop lint: `scripts/test_slop_signals.py`
- Sprint backlog: `docs/tasks/todo.md`
- Lessons: `docs/tasks/lessons.md`
- Gate report: `gate-report.json` (auto-generated)
- Sitemaps: `sitemap-core.xml`, `sitemap-hold.xml` (auto-generated)

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

## Last Sprint Summary
Sprint 19: Created 12 new A-tier comparison pages in 3 batches of 4 parallel subagents (75→87 pages). Fixed 4 badge mismatches. Expanded data-enrichment from 4→8 comparisons, dialers-calling from 3→7. Key lesson: bare comparison filenames fail gate — must use ../compare/ prefix.

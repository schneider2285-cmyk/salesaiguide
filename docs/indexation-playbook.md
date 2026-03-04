# Indexation Playbook — Sales AI Guide

Internal reference for GSC workflow and sitemap management. Not deployed to Netlify.

## Current Sitemap-Core URLs (26 expected after Sprint 7)

### Hubs & Editorial (6A expected)
1. `https://salesaiguide.com/`
2. `https://salesaiguide.com/about.html`
3. `https://salesaiguide.com/disclosure.html`
4. `https://salesaiguide.com/resources/cold-outreach-evaluation-checklist.html` ← NEW
5. `https://salesaiguide.com/resources/sales-dialer-evaluation-checklist.html` ← NEW
6. `https://salesaiguide.com/resources/index.html` ← NEW

### Category Hubs (B tier)
7. `https://salesaiguide.com/categories/cold-outreach.html`
8. `https://salesaiguide.com/categories/conversation-intelligence.html`
9. `https://salesaiguide.com/categories/dialers-calling.html`

### Tool Reviews (B tier)
10. `https://salesaiguide.com/tools/clay-review.html`
11. `https://salesaiguide.com/tools/fireflies-review.html`
12. `https://salesaiguide.com/tools/instantly-review.html`
13. `https://salesaiguide.com/tools/justcall-review.html`
14. `https://salesaiguide.com/tools/woodpecker-review.html`

### Comparisons (B tier)
15. `https://salesaiguide.com/compare/fireflies-vs-chorus.html`
16. `https://salesaiguide.com/compare/fireflies-vs-gong.html`
17. `https://salesaiguide.com/compare/instantly-vs-lemlist.html`
18. `https://salesaiguide.com/compare/instantly-vs-smartlead.html`
19. `https://salesaiguide.com/compare/justcall-vs-aircall.html`
20. `https://salesaiguide.com/compare/justcall-vs-dialpad.html`
21. `https://salesaiguide.com/compare/lavender-vs-instantly.html`
22. `https://salesaiguide.com/compare/lemlist-vs-smartlead.html`
23. `https://salesaiguide.com/compare/woodpecker-vs-instantly.html`
24. `https://salesaiguide.com/compare/woodpecker-vs-lemlist.html`
25. `https://salesaiguide.com/compare/woodpecker-vs-mailshake.html`
26. `https://salesaiguide.com/compare/woodpecker-vs-smartlead.html`

## Weekly GSC Process

1. **Check Coverage report** — Open GSC > Pages > look for "Not indexed" or "Crawled - currently not indexed" entries. Focus on sitemap-core URLs first.
2. **Prioritize hubs and reviews** — Category hubs and tool reviews carry the most ranking weight. If any are excluded, request indexing manually.
3. **Request indexing after meaningful updates** — Only use "Request Indexing" in URL Inspection after content changes that affect word count, structure, or internal links. Do not request indexing for cosmetic-only edits.
4. **Monitor crawl errors** — Check for 404s, redirect chains, or server errors. Fix source links before re-requesting indexing.
5. **Review excluded pages** — Some pages (thin C-tier) may be legitimately excluded by Google. Only escalate if a sitemap-core URL is excluded.

## Definition of Success

- All 26 sitemap-core URLs discovered and indexed in GSC
- No sitemap-core URLs in "Excluded" or "Error" status
- Hubs and reviews indexed within 7 days of submission
- Comparisons indexed within 14 days

## Tier Promotion Path

Pages graded C by the gate are excluded from sitemap-core. To promote a C page to B:

| Requirement | Review | Comparison | Editorial |
|-------------|--------|------------|-----------|
| Content words | ≥ 600 | ≥ 600 | ≥ 100 |
| Editorial words | — | ≥ 300 | — |
| Sources | — | ≥ 4 | — |
| Source domains | — | ≥ 2 | — |
| Internal links | — | ≥ 2 patterns | — |
| Canonical | Correct | Correct | Correct |

To promote B to A: Meet all B requirements plus the stricter A thresholds documented in `scripts/indexation_gate.py` for each page type.

## Current C-Tier Pages (17)

These pages are excluded from sitemap-core. Review periodically and promote when content is added:

- Category index pages (categories/index.html, compare/index.html, tools/index.html)
- Hub pages without sufficient content
- Comparison pages below word-count thresholds
- Any pages with canonical mismatches or empty H2 sections

Run `python3 scripts/indexation_gate.py --site-dir . --out-dir . --base-url https://salesaiguide.com` to get the current full breakdown of C-tier pages and their specific failures.

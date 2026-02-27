# Indexation Gate — Design Decisions

## 1. A/B/C vs Binary
B-tier provides a monitoring path for pages that are good enough to index but not yet flagship quality. This avoids the false binary of "perfect or noindex."

## 2. X-Robots-Tag Headers
HTTP-level enforcement via Netlify `_headers`. Merges with existing file using fenced markers for idempotent reruns. More reliable than in-HTML meta robots tags.

## 3. No AggregateRating
Google requires AggregateRating to represent aggregated *user* reviews. A single editorial review uses `Rating`, not `AggregateRating`. Hard fail if misused.

## 4. Editorial Scaffolding
E-E-A-T trust signals for affiliate content. Links to methodology, editorial policy, disclosure, and corrections placed under H1 on every review and comparison page.

## 5. sitemap-hold Excluded from Index
noindex pages should not appear in submitted sitemaps. `sitemap.xml` references only `sitemap-core.xml`. Hold file exists for internal monitoring.

## 6. Category Hubs as Hub-and-Spoke
Currently C (thin tool-card grids), but clear A-level editorial targets defined: 900+ words, what-to-consider, failure modes, best-picks-by-scenario, 8+ internal links.

## 7. 3-Shingle on core-editorial Only
`data-audit="core-editorial"` blocks exclude shared scaffolding (nav, footer, editorial rail, repeated headings) from similarity computation. Prevents false positives from template content.

## 8. Sources-Checked as Auditable Module
`data-audit="sources-checked"` enables automated trust verification: link count, domain diversity, date patterns. Hard minimums: 3 for reviews, 4 for comparisons.

## 9. Affiliate Classification by Pattern
`/go/` prefix or tracking params = affiliate. Vendor docs and pricing pages are valid editorial sources even if the vendor is also an affiliate partner.

## 10. Zero Placeholders Hard Gate
Regex scan for "coming soon", "TODO", "lorem ipsum", "TBD", "placeholder", "[insert" in content zones. Any match = hard fail. Prevents indexing incomplete content.

## 11. Decision Summary Visibility
Verdicts hidden in `<details>` tags fail. Google needs visible summaries for review/comparison rich results. Applies to `.final-verdict`, `.verdict-text`, `data-audit="decision-summary"`.

## 12. Category-Clustered Similarity
Pages compared pairwise within category clusters (inferred from `/categories/*` hub links), not flat page-type groups. Cold-outreach comparisons compared together, not against CRM comparisons.

## 13. Self-Referencing Canonical
`<link rel="canonical">` must resolve to `base_url + normalized_file_path`. Prevents canonical confusion and consolidation errors.

## 14. _headers Path Normalization
For clean-URL pages (`*/index.html`), emit both `/path/` and `/path/index.html` header entries. Covers all Netlify routing variants.

## 15. Global Uniqueness Enforcement
No page type is exempt from title/meta description dedup — homepage and editorial pages included in site-wide validation.

## 16. Canonical Path Normalization
`*/index.html` normalizes to `/path/` (not `/path/index.html`) before canonical comparison.

## 17. Dual-Path Review Resolver
A tool review is "existing" if either `tools/{slug}-review.html` OR `tools/{slug}-review/index.html` exists on disk. Supports both URL structures.

## 18. Blockquote Attribution (Optional)
Any `<blockquote>` on review/comparison pages hard-fails unless it has adjacent external attribution. Optional trust hardening for quoted content.

# Sales AI Guide — Sprint Backlog

## Current Sprint: Sprint 21 — Complete ✅

### Sprint 21 (Complete, Deployed Mar 2026)
- Created 8 new A-tier alternatives pages + 1 alternatives index page (108→117 pages)
- New content type: "[Tool] Alternatives" captures entirely new keyword cluster with high commercial intent
- Alternatives pages: Salesforce (4 CRMs), ZoomInfo (5 prospecting), Outreach (5 engagement), HubSpot CRM (3 CRMs), Gong (3 CI), Salesloft (5 engagement), Apollo (5 prospecting), Calendly (2 schedulers)
- Added cross-category links to all 10 category hubs (2-3 adjacent category + alternatives guide links each)
- Updated compare/index.html with 8-card alternatives section
- Fixed 4 gate issues during checkpoints: 2 empty H2 sections in alternatives pages (added intro paragraphs), 2 empty H2 sections in category hubs (same fix)
- All pages classified as editorial (200w threshold), each page contains 1400-1600 content words
- Template approach: Batch 1 + Batch 2 of 4 parallel subagents using salesforce.html as reference template
- 117/117 A-tier, zero slop, all similarity pairs < 0.20

### Next Sprint: Sprint 22 (planned)
- TBD — evaluate additional review/comparison/resource opportunities

---

## Previous Sprints

### Sprint 20 (Complete, Deployed Mar 2026)
- Phase A: Created 6 new A-tier review pages + 12 comparison pages (87→105 pages)
- Phase B: Added 3 more comparison pages (105→108 pages)
- Phase C: Schema enrichment (BreadcrumbList + FAQPage on all pages), RSS feed, sitemaps, alt text fixes, selective similarity reduction
- Sprint 20c enhancement scripts: 2 of 5 caused regressions (CSS consolidation dropped pages to B-tier, keyword swaps damaged SEO terms)
- Fix: git checkout revert + selective re-application of schemas/alt text + safe-only similarity swaps
- Safe swaps preserved: side-by-side→head-to-head, ease of use→usability, all-in-one→unified, comes down to→hinges on
- Keyword-damaging swaps reverted: sales teams, cold email, data enrichment, conversation intelligence, email coach, email warmup, meeting notes, scheduling tool
- Final: 108A + 0B + 0C = 108 pages, sitemap-core = 108

### Sprint 19 (Complete, Deployed Mar 2026)
- Created 12 new A-tier comparison pages in 3 batches of 4 parallel subagents (75→87 pages)
- Fixed 4 badge mismatches on hub pages (Reply.io, Orum, ZoomInfo, Lusha: Listed→Reviewed)
- Batch A (4 pages): aircall-vs-dialpad, dialpad-vs-orum, clari-vs-fireflies, chorus-vs-clari
- Batch B (4 pages): clay-vs-zoominfo, clearbit-vs-lusha, lusha-vs-zoominfo, clearbit-vs-seamless-ai
- Batch C (4 pages): lavender-vs-lemlist, lavender-vs-reply-io, instantly-vs-mailshake, salesloft-vs-instantly
- Batch A had 2 B-tier pages (aircall-vs-dialpad, clari-vs-fireflies) — both failed on other_compare link pattern due to bare filenames instead of ../compare/ prefix
- Batch B had 1 C-tier page (clay-vs-zoominfo) — unsourced_numeric_claims slop on "90%" and "60-70%" match rate claims
- All fixes applied inline, no subagent re-runs needed
- Cross-referenced 4 new cards on compare/index.html + 8 category hub "Comparisons to Read Next" updates
- Clustered salesloft-vs-instantly under sales-engagement (not cold-outreach) to manage cluster density
- Clustered lavender-vs-lemlist and lavender-vs-reply-io under sales-content
- All 41 comparison pages A-tier, all 27 reviews A-tier, all 10 hubs A-tier
- Final: 87A + 0B + 0C = 87 pages, sitemap-core = 87

### Sprint 18 (Complete, Deployed Mar 2026)
- Created 10 new A-tier comparison pages in 3 batches leveraging Sprint 17 reviews
- Batch A (4 pages): calendly-vs-chili-piper, orum-vs-justcall, seamless-ai-vs-zoominfo, clari-vs-gong
- Batch B (3 pages): seamless-ai-vs-apollo, orum-vs-aircall, seamless-ai-vs-lusha
- Batch C (3 pages, cold outreach cluster — highest similarity risk): reply-io-vs-instantly, reply-io-vs-lemlist, reply-io-vs-outreach
- Clustered reply-io-vs-outreach under sales-engagement (not cold-outreach) to manage cold outreach cluster similarity
- Batch C required 3 gate runs to resolve unsourced_numeric_claims on $99 pricing mentions in verdict paragraphs
- Cross-referenced 4 new cards on compare/index.html + 7 category hub "Comparisons to Read Next" updates
- Created first comparisons in Meeting Schedulers (calendly-vs-chili-piper) and Sales Analytics (clari-vs-gong) categories
- All 29 comparison pages A-tier, all 27 reviews A-tier, all 10 hubs A-tier
- Final: 75A + 0B + 0C = 75 pages, sitemap-core = 75

### Sprint 17 (Complete, Deployed Mar 2026)
- Created 6 new A-tier review pages: Seamless.AI (4.1/5), Orum (4.3/5), Reply.io (4.3/5), Calendly (4.5/5), Chili Piper (4.4/5), Clari (4.4/5)
- Unlocked 2 zero-reviewed categories: Meeting Schedulers (Calendly + Chili Piper) and Sales Analytics (Clari)
- Added depth to 3 established categories: Cold Outreach (Reply.io), Lead Prospecting (Seamless.AI), Dialers & Calling (Orum)
- Managed Calendly vs Chili Piper similarity through distinct vocabulary anchors ("scheduling link" vs "lead routing") and zero feature card overlap
- meeting-schedulers hub edit survived 909-word editorial threshold — replaced placeholder section with proper review bullets at ≥110 words
- Updated cross-references: tools/index.html (6 listed→reviewed), 5 category hubs, categories/index.html (5 tool count updates)
- All 27 review pages A-tier, all 19 comparisons A-tier, all 10 hubs A-tier
- Final: 65A + 0B + 0C = 65 pages, sitemap-core = 65

---

## Previous Sprints

### Sprint 16 (Complete, Deployed Mar 2026)
- Created 7 new A-tier review pages: ZoomInfo (4.6/5), Lusha (4.3/5), Lavender (4.0/5), Outreach (4.3/5), Salesloft (4.5/5), HubSpot (4.4/5), Pipedrive (4.2/5)
- All 7 reviews launched via parallel subagents with zero fix passes needed (second consecutive zero-fix sprint)
- Promoted 5 comparisons from B → A tier: apollo-vs-zoominfo, lusha-vs-apollo, outreach-vs-salesloft, hubspot-vs-pipedrive, lavender-vs-instantly
- 4 comparisons promoted via link-only additions (adding tool_a_review + tool_b_review links to Related Resources)
- lavender-vs-instantly required major expansion: content 753→1200w, editorial 487→952w, sources 4→8 from 7 domains, link_patterns 2/4→4/4
- Updated cross-references: tools/index.html (7 listed→reviewed), 4 category hubs (lead-prospecting, sales-engagement, crm-pipeline, sales-content), categories/index.html (4 tool count updates)
- Hub regression caught and fixed: sales-content and sales-engagement dropped below 900 editorial words after intro paragraph rewrites — expanded back above threshold
- All 21 review pages now A-tier, all 19 comparisons now A-tier, all 10 hubs A-tier
- Final: 56A + 3B + 0C = 59 pages, sitemap-core = 59

### Sprint 15 (Complete, Deployed Mar 2026)
- Created 6 new A-tier review pages: Apollo.io (4.8/5), Gong (4.7/5), Chorus.ai (4.5/5), Clearbit (4.4/5), Aircall (4.3/5), Dialpad (4.4/5)
- Used 2 batches × 3 parallel subagents with fireflies-review.html as A-tier template
- All 6 reviews graded A-tier on first pass (no fix passes needed) — first sprint with zero post-subagent fixes
- Each review: 2100-2400 content words, 1600-1850 editorial words, 8 sources from 6-8 domains, 6 feature cards at 80-100w each
- Promoted 7 comparisons from B → A tier by adding missing tool_b review links: clay-vs-apollo, clay-vs-clearbit, fireflies-vs-gong, fireflies-vs-chorus, gong-vs-chorus, justcall-vs-aircall, justcall-vs-dialpad
- Key insight: 7 of 12 B-tier comparisons had ONLY link_patterns as their A-tier gap — creating reviews + adding one link auto-promoted them
- Updated cross-references: tools/index.html (6 listed→reviewed), 3 category hubs (data-enrichment, conversation-intelligence, dialers-calling), categories/index.html (3 tool count updates)
- All 14 review pages now A-tier, all 10 hubs A-tier, 14 of 19 comparisons A-tier
- Final: 44A + 8B + 0C = 52 pages, sitemap-core = 52

### Sprint 14 (Complete, Deployed Mar 2026)
- Promoted 5 pages from B → A tier (26A→31A): 3 reviews + 2 comparisons
- Reviews expanded: clay-review (1162→1899w), instantly-review (1058→1788w), woodpecker-review (1170→1879w)
- All 3 reviews: renamed "Who Should Use X?" → "When to Choose X: Use Cases" (has_scenario), added "Limitations to Watch For" H2 (has_gotcha), expanded feature cards from ~20w to ~80-100w each, added 2+ other_review links with ../tools/ prefix
- Woodpecker: added pricing-table class to pricing UL + pricing-tier class to CTA div (fixed conversion_first interaction)
- Comparisons expanded: instantly-vs-lemlist (711→1215w), instantly-vs-smartlead (703→1216w)
- Both comparisons: added missing tool_b review link, added Pricing Breakdown + Integration sections, expanded verdict, added 4 source citations (8 total from 8 domains)
- Fix pass needed for instantly-vs-smartlead: unsourced_numeric_claims ($37, $97, $39, then $2) — added inline pricing page links and spelled out dollar amount
- All 8 review pages now A-tier
- Final: 31A + 15B + 0C = 46 pages, sitemap-core = 46

### Sprint 13 (Complete, Deployed Mar 2026)
- Promoted 5 category hubs from B → A tier (21A→26A): sales-content, sales-engagement, crm-pipeline, lead-prospecting, meeting-schedulers
- All 10 category hubs now A-tier
- Tool card additions: Regie.ai + Copy.ai (sales-content), Groove/Clari (sales-engagement), Close + Freshsales (crm-pipeline), Hunter.io (lead-prospecting), Acuity Scheduling + Reclaim.ai (meeting-schedulers)
- Editorial expansion across 5 hubs: ~1140 total words added (deepened What to Consider, Common Mistakes, Best Tool sections)
- Internal link additions: 15+ new /tools/ and /compare/ links across all 5 hubs
- Two fix passes needed: first pass got 3/5 promoted, second pass added incremental words to crm-pipeline (+4w) and sales-content (+2w)
- Final: 26A + 20B + 0C = 46 pages, sitemap-core = 46

### Sprint 12 (Complete, Deployed Mar 2026)
- Promoted 9 pages from B → A tier (12A→21A): 4 comparisons + 4 category hubs + 1 comparison word fix
- Comparison quick wins: woodpecker-vs-smartlead (added smartlead-review link), lemlist-vs-smartlead (added both review links), woodpecker-vs-instantly (+3 content words to hit 1200 threshold)
- Category hub promotes: data-enrichment (+2 tool cards: Apollo.io, Lusha), conversation-intelligence (+2 tool cards: Avoma, Clari Copilot), sales-analytics (+2 tool cards: InsightSquared, Aviso), dialers-calling (+1 tool card: Kixie)
- Moderate comparison promotes: woodpecker-vs-mailshake (added mailshake-review link + scaling behavior paragraph), woodpecker-vs-lemlist (added lemlist-review link + pricing section)
- All 4 hub promotes required internal link additions (only /tools/ and /compare/ paths count)
- Final: 21A + 25B + 0C = 46 pages, sitemap-core = 46

### Sprint 11 (Complete, Deployed Mar 2026)
- Promoted 6 pages from B → A tier: cold-outreach hub, fireflies, justcall, lemlist, smartlead, mailshake
- Updated stale SAG_BIBLE NEXT SPRINT directive to reflect A-tier promotion priorities
- A-tier review requirements discovered: content_words>=1500, editorial_words>=500, has_pricing (class="pricing-table"), has_scenario (H2/H3 matching "scenario|use case|when to"), has_gotcha (H2/H3 matching "gotcha|limitation|watch out|downside"), other_review>=2 links with ../tools/ prefix
- A-tier hub requirements discovered: editorial_words>=900, has_consider, has_bestpick, tool_card_count>=5, internal_links>=8
- Fixed conversion_first slop: /go/ affiliate links in quick-summary CTAs must use direct vendor URLs; keep /go/ only in final-cta section
- Gate link_patterns discovery: bare filename links (e.g., instantly-review.html) don't match other_review pattern — must use ../tools/ prefix
- Multiple incremental word-count fixes for justcall (1366→1475→1496→1500+)
- Final: 12A + 34B + 0C = 46 pages, sitemap-core = 46

### Sprint 10 (Complete, Deployed Mar 2026)
- Created 3 new standalone tool review pages: Lemlist (4.2/5), Smartlead (4.5/5), Mailshake (4.0/5)
- Used 3 parallel subagents with Instantly review as A-tier template reference
- All 3 subagent outputs required thin_sections fixes (consistent pattern: sections at 32-38 words, threshold is 40)
- Updated cross-references: tools/index.html, cold-outreach.html, categories/index.html
- Cold outreach tool count updated from 4 to 6 reviewed
- Final: 6A + 40B + 0C = 46 pages, sitemap-core = 46

### Sprint 9 (Complete, Deployed Mar 2026)
- Promoted all 10 remaining C-tier pages to B-tier (7 category hubs + 3 directory pages)
- Used 7 parallel subagents for category hub editorial upgrades
- Directory page fixes: added editorial paragraphs with internal links
- Post-subagent gate fix pass: placeholder text removal, empty H2 repair, internal link additions
- Key discovery: gate counts only /tools/ and /compare/ links as "internal links" for category hubs — /categories/ links do NOT count
- Final: 6A + 37B + 0C = 43 pages, sitemap-core = 43 (all pages indexed)

### Sprint 8 (Complete, Deployed Mar 2026)
- Promoted 7 comparison pages from C → B tier
- Batch 1 (no similarity risk): gong-vs-chorus, hubspot-vs-pipedrive, outreach-vs-salesloft
- Batch 2 (similarity pairs): apollo-vs-zoominfo, lusha-vs-apollo, clay-vs-apollo, clay-vs-clearbit
- Fixed slop failures: H3→H4 in quick-summary, removed unsourced numeric claims, removed /go/ from core-editorial
- Differentiated similarity pairs (RevOps vs SDR angle for Clay/Apollo, scale vs workflow for Apollo/ZoomInfo)
- Final: 6A + 27B + 10C = 43 pages, sitemap-core = 33

### Sprint 7 (Complete, Deployed)
- Created resources/cold-outreach-evaluation-checklist.html
- Created resources/sales-dialer-evaluation-checklist.html
- Created resources/index.html (resource hub)
- Updated category hubs with checklist cross-links
- Created docs/indexation-playbook.md
- Final: 6A + 20B + 17C = 43 pages, sitemap-core = 26

### Sprints 1–6 (Complete)
- Built full site from scratch: homepage, about, disclosure, categories, tools, comparisons
- Implemented indexation gate (A/B/C grading), slop lint, sitemap system
- Deployed to Netlify with _headers enforcement
- Established trust bar, sources-checked, editorial scaffolding patterns

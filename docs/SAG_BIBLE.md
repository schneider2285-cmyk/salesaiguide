SALES AI GUIDE (SAG) — SYSTEM BIBLE v1.0
Owner: Claude Code
Goal: Build a trusted, indexable, non-slop decision platform for AI + sales tools.
Primary 90-day KPI: Organic traffic growth + indexation of high-quality pages.
Secondary KPIs: Trust signals, conversion to "Visit official site" clicks, affiliate revenue.
Hard constraint: No "AI slop." No thin templated pages in index. Static HTML is fine.
----------------------------------------
NEXT SPRINT (DO THIS NEXT, NO DETOURS)
----------------------------------------
Continue A-tier promotion across all clusters
- Promote remaining B-tier reviews and hubs to A where gaps are small
- Prioritize pages closest to thresholds (header renames, content expansion, pricing-table class)
- Keep the gate frozen
- Rerun QA and report results
----------------------------------------
1) NORTH STAR POSITIONING
----------------------------------------
SAG is a dual-persona decision platform:
- Persona A: Org/Team buyers (Sales leaders, RevOps)
- Persona B: Individual reps (SDRs/AEs buying personal tools)
SAG is NOT:
- A tool directory
- A review aggregator
- A G2 wrapper
- A blog content farm
- A coupon site
SAG IS:
- Evidence-based decision engine
- Clear tradeoffs, stack fit, implementation reality
- Honest, structured, citation-backed synthesis
----------------------------------------
2) TRUST PRINCIPLES (NON-NEGOTIABLE)
----------------------------------------
A) Commission-blind scoring
Affiliate status must never change:
- score
- ranking
- "winner" language
Affiliate affects only link routing (/go/*).
B) Proof or silence
If we say we checked a source type, we show clickable source links.
No evidence theater.
C) No fake quotes
No synthesized quotes styled as testimonials.
Blockquotes allowed only with explicit source citation, otherwise banned.
D) No unsourced numbers
Any performance, pricing, volume, or "X+ threads" claim needs a citation link adjacent.
Otherwise remove or restate qualitatively.
E) Reviewed vs Listed clarity
Reviewed tools = scored and evidenced.
Listed tools = not reviewed, no internal scores, clearly labeled.
----------------------------------------
3) INDEXATION STRATEGY
----------------------------------------
We will not index everything.
We index only A/B pages.
Indexation system:
- A/B/C grading via scripts/indexation_gate.py
- Tier C enforced noindex,follow via Netlify _headers (X-Robots-Tag).
- sitemap.xml references sitemap-core.xml only.
- sitemap-hold.xml is internal monitoring only, never submitted.
Eligible for indexation (once they pass gates):
- Homepage
- Trust pages: About, Methodology, Editorial Policy, How We Make Money, Corrections
- Category hubs (only once upgraded)
- Tool reviews (reviewed and scored)
- High-intent comparisons
Default non-indexable:
- Listed-only tool pages
- Thin hubs and thin directories
- Any page failing gates
----------------------------------------
4) PAGE CONTRACTS
----------------------------------------
4.1 Tool review page (Reviewed and Scored)
Must have, visible by default:
- H1 "Tool Review"
- Decision summary 2–4 sentences (not in <details>)
- Best for (3 bullets max)
- Avoid if (3 bullets max)
- Evidence confidence + 1 line rationale
- Last verified date element data-audit="last-verified"
- Editorial rail links: Methodology, Editorial Policy, How we make money, Corrections
- Sources checked module (visible): min 6 sources, 4+ unique domains, each with date checked
Everything else may be collapsible, but primary decision content stays visible.
Must include in body:
- Decision Snapshot
- Strengths and limitations (balanced)
- Breaks at scale
- Implementation reality
- Stack fit
- Alternatives
- FAQ (3 Qs max)
Uniqueness requirements:
- 500+ tool-specific editorial words for Tier A
- 350+ tool-specific editorial words for Tier B
- Must include one tool-specific scenario and one gotcha
4.2 Comparison page
Must have, visible by default:
- H1 "X vs Y"
- Winner by persona (Org winner, Individual winner) or "tie by scenario"
- 3 workflow-level decision triggers
- Evidence confidence + 1 line rationale
- Sources checked module: min 8 sources total, 4+ unique domains, each with date checked
- Links to both review pages + category hub
Unique content requirements:
- >=600 unique editorial words for Tier A
- >=400 for Tier B
- No templated intros
4.3 Category hub page
Category hubs are the growth engine. They must become indexable (Tier B) to build topical authority.
Must include:
- Category definition (2–3 sentences)
- What to consider (5 bullets max)
- Failure modes (3 bullets max)
- Best picks by scenario (3 scenarios max)
- Reviewed tools section (with short unique blurbs)
- Listed tools section (clearly labeled)
- Comparisons to read next (6 links max)
Minimum editorial words:
- Tier B: 400+
- Tier A: 900+
4.4 Directory pages (/tools, /compare, /categories)
Must clearly separate Reviewed vs Listed.
Listed tools cannot show internal scores.
Must have 100–200 words intro explaining how to use the directory.
----------------------------------------
5) AI SLOP LINTER (POST-GRADE FILTER)
----------------------------------------
The slop linter runs after grading and can downgrade A/B to C.
Slop signals that trigger downgrade:
- Placeholder language (coming soon, TBD, TODO, lorem ipsum, placeholder, [insert])
- Thin H2/H3 sections (<40 words) unless rich content present
- Unsourced blockquotes
- Unsourced numeric claims in core editorial without nearby external citation
- Over-templated intros (>0.25 similarity within cluster after tool-name normalization)
- Hype density >2%
- Conversion-first affiliate placement (/go/ in core editorial, /go/ before decision summary outside allowed zones, CTA spam)
- Missing or stale last verified (A<=90d, B<=365d, C if missing or >365d)
- Reviewed vs listed confusion
- Schema overreach (AggregateRating etc)
Synthetic tests must exist and pass: scripts/test_slop_signals.py.
----------------------------------------
6) QA LOOP (EFFICIENCY ENGINE)
----------------------------------------
One command must validate everything:
- gate
- slop tests
- trust-claim scan
- outputs docs/qa-report.md
qa_run.py should:
- run gate and tests
- auto-fix common issues (thin sections via bullets/table, remove unsourced numeric phrases, insert last-verified, etc)
- rerun once
- escalate only if human decision needed (source selection, cluster prioritization)
----------------------------------------
7) MONETIZATION (TRUST-FIRST)
----------------------------------------
Approved affiliates right now:
- Clay
- Reply.io
- Fireflies
- Woodpecker
- JustCall
Pending:
- Mailshake
- Saleshandy
Monetization rules:
- Uniform CTAs for all tools. No affiliate favoritism.
- Only "Visit official site" routes through /go/* when affiliate exists.
- Never change scores due to affiliate status.
- Disclosure is consistent, minimal, non-dramatic.
Implementation:
- Netlify redirects for /go/*
- Directory filter "Affiliate available" allowed, but must not bias ranking.
----------------------------------------
8) CLUSTER BUILD STRATEGY (90 DAYS)
----------------------------------------
We build deep clusters, not broad coverage.
Cluster order:
1) Cold Email / Outbound Automation (first)
2) Calling / Dialers
3) Meeting Notes / Conversation Intelligence
4) Enrichment / Prospecting automation
For each cluster:
- 1 category hub to Tier B
- 2 reviews to Tier B/A
- 4 comparisons to Tier B
- internal linking mesh between them
Then add next cluster.
----------------------------------------
9) STOP CONDITIONS (NO MORE REVISIONS)
----------------------------------------
We stop changing gate rules unless a bug is found.
We stop changing page contracts unless a major strategic shift happens.
The system is "stable" when:
- QA loop passes
- sitemap-core is live in production
- Tier C noindex headers verified in production
- at least one cluster has a Tier B hub + multiple Tier B comparisons + Tier B/A reviews
From there, work is content promotion, not gate engineering.

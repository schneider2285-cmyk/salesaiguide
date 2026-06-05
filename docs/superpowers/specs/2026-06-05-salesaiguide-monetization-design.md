# Sales AI Guide — Monetization-First Rebuild (Design Spec)

**Date:** 2026-06-05
**Status:** Approved design, pending spec review
**Author:** Claude (Opus 4.8) with Matt

## Problem

The site has run live since March 2026 and earned $0. Root cause confirmed: **the affiliate links were never real.** Every `/go/{tool}` redirect resolved to `https://{tool}.com?ref=salesaiguide` — a self-invented query parameter that no affiliate network tracks. The owner believed the links were live; they were placeholders. The content (132 pages) is solid; the monetization plumbing never existed.

A second problem compounds it: a prior (March) session left the working tree uncommitted and half-migrated. Of the money links, 519 still route through `/go/`, but 465 were switched to **direct vendor URLs** that bypass the redirect layer entirely — so there is no single place to control monetization, and the (already fake) tracking was stripped on those.

## Goals

1. Make real affiliate revenue *possible* — give the owner an actionable signup playbook and a link system where dropping in a real link is a one-line change.
2. Standardize every money link through a single controllable layer, with a guard so placeholder/bypassed links can never silently ride live again.
3. Then (gated on a traffic check) refresh content where it's justified.

## Non-Goals

- Signing up for affiliate programs (requires owner's identity/tax info — owner action only).
- A visual redesign. The NerdWallet-style design stays.
- Rewriting content that already passes the gate, except for the specific schema/module fixes 103 pages now fail.

---

## Phase 1 — Monetization core

### 1.1 Single source of truth: `affiliate-links.json`

A file at repo root mapping tool slug → link metadata:

```json
{
  "apollo": {
    "url": "https://apollo.io",
    "network": "direct",
    "status": "placeholder",
    "signup_url": "",
    "commission": "",
    "cookie_days": null,
    "notes": ""
  }
}
```

- `status`: `placeholder` (no real link yet) or `live` (real affiliate link in `url`).
- When a program is approved, the owner pastes the real tracking URL into `url` and flips `status` to `live`. Nothing else changes.

### 1.2 Generator script: `scripts/build_redirects.py`

- Reads `affiliate-links.json`, emits the `/go/{slug}` block of `_redirects`.
- Placeholder entries emit a clean redirect to the plain vendor URL (NO `?ref=salesaiguide`).
- Idempotent; preserves the non-`/go/` redirect rules already in `_redirects` (slug→pretty-URL, etc.).
- Run as part of `deploy.sh` before the gate step.

### 1.3 Link standardization across pages

- Re-route the 465 direct CTA links back to `/go/{slug}`. A CTA = a button/link whose intent is "go try this tool" (classes like `btn-review-primary`, `inline-cta`, `/go/` historically).
- **Exception — citation links stay direct:** links that source a fact (e.g. `apollo.io/pricing` next to a price, docs links) remain direct vendor URLs with `rel="nofollow"`. These are evidence, not monetization. The migration script must distinguish CTA links from citation links (heuristic: CTA links live inside `.inline-cta` / `.btn-review-*` / verdict CTA blocks; citation links are inline in prose/tables next to dollar amounts).
- Remove the fake `?ref=salesaiguide` everywhere it remains.

### 1.4 Guard: `scripts/check_affiliate_links.py`

Fails (non-zero exit) if:
- Any page contains a money-CTA link that does NOT route through `/go/`.
- Any `/go/{slug}` referenced by a page is missing from `affiliate-links.json`.
- Any link still contains `?ref=salesaiguide`.
- (Warn, not fail) any `status: live` entry whose `url` still looks like a bare vendor homepage (likely not a real tracking link).

Wired into `deploy.sh` alongside the existing identity guards.

### 1.5 Affiliate-program research playbook: `docs/monetization/affiliate-programs.md`

Ranked table for **all 34 tools** the site covers:

| Tool | Has program? | Network | Commission | Cookie | Signup URL | Priority |
|------|-------------|---------|-----------|--------|-----------|----------|

- Priority = expected payout × likelihood-of-approval × (content already exists). Owner works top-down.
- Networks to check: PartnerStack, Impact, Tolt, FirstPromoter, Reditus, Rewardful, GetRewardful, direct/in-house.
- Where a tool has no public program, note it (and whether an alternative tool in the same category does — informs where to point content).

### 1.6 FTC disclosure check

With real affiliate links coming, confirm `disclosure.html` is accurate and that review/comparison pages carry a visible disclosure near the first money link. (Likely already present; verify, don't rebuild.)

### 1.7 Clean-baseline commit

Keep the good uncommitted changes (footer `h3`→`p` heading hierarchy, accessibility tweaks). Apply the link standardization. Commit as one clean baseline before Phase 2 so the working tree stops being a liability.

---

## 🚦 Milestone gate — traffic reality check

Before Phase 2, look at GA4 (`G-VRBZ6Z68`) and Google Search Console:
- Any organic impressions/clicks? Any page ranking in the top 50 for anything?
- If essentially zero after 3 months: content *freshness* is not the lever — domain authority / link building / niche selection is. We reassess Phase 2 scope (or whether content investment is worth it at all) with real data instead of guessing.

---

## Phase 2 — Content refresh (scope confirmed at the gate)

- **Gate fixes:** 103 pages fail new checks — `verdict_in_details`, `has_aggregate_rating`, `claimed_sources_no_module`. Add the verdict module, AggregateRating schema, and sources module to restore A-tier (back into `sitemap-core.xml`). Scriptable.
- **Pricing freshness:** pricing pages may be stale since March; spot-check against current vendor pricing, update + re-cite.
- **Untracked pages decision:** 8 half-built untracked pages (`saleshandy-review`, `fireflies-vs-otter`, `justcall-vs-ringcentral`, `mailshake-vs-lemlist`, `saleshandy-vs-{instantly,mailshake,woodpecker}`, `clay-vs-seamless-ai`). Run them through the gate — finish to A-tier or remove.
- **Freshness signals:** "last updated" dates where genuinely re-reviewed.

---

## Sequencing

1. Clean-baseline commit (keep-good + standardize links + remove fake ref).
2. `affiliate-links.json` + `build_redirects.py` + `check_affiliate_links.py`, wired into `deploy.sh`.
3. Affiliate-program research playbook (parallel research across 34 tools).
4. Deploy Phase 1. Owner begins signups.
5. Traffic gate review.
6. Phase 2 per gate findings.

## Success criteria

- Every money CTA on the site routes through `/go/{slug}`; zero `?ref=salesaiguide` remain; guard passes in `deploy.sh`.
- Owner has a ranked playbook and can swap any approved program live with a one-line JSON edit.
- (Phase 2) gate back to all-A-tier; 103 C-tier pages restored to `sitemap-core.xml`.

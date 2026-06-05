# Affiliate Program Playbook — Sales AI Guide

**Researched:** 2026-06-05. Verify exact terms on each signup page before relying on rates — affiliate terms change.

## How this works now

Every money link on the site routes through `/go/<slug>`, controlled by one file: [`affiliate-links.json`](../../affiliate-links.json). **To make a program live:**

1. Sign up for the program (links below). Get your tracking URL.
2. In `affiliate-links.json`, find the tool, paste your real URL into `url`, set `"status": "live"`.
3. Run `python3 scripts/build_redirects.py` then `python3 scripts/check_affiliate_links.py`.
4. Deploy with `bash deploy.sh`.

That's it — no page edits. The guard in `deploy.sh` blocks any deploy where a money link leaks or a placeholder is mislabeled.

---

## ✅ Already live (you signed up — these earn now)

| Tool | Network | Commission | Cookie | Your link |
|------|---------|-----------|--------|-----------|
| Woodpecker | In-house | 20% lifetime recurring | 30d | `red=salesa145703` |
| Fireflies | FirstPromoter | up to 30% recurring (12mo) | 90d | `fpr=matthew16` |
| JustCall | FirstPromoter | up to 20% lifetime recurring | 90d | `fp_ref=matthew95` |
| Saleshandy | Rewardful | 25% lifetime recurring | 90d | `via=matthew` |

---

## 🎯 TIER 1 — Sign up first (self-serve, recurring, affiliate-friendly)

Ranked by attractiveness for a content/review site. These are the priority — recurring commission, easy approval, and the site already has content for each.

| # | Tool | Network | Commission | Cookie | Signup URL |
|---|------|---------|-----------|--------|-----------|
| 1 | **HubSpot** | Impact | 30% recurring up to 1yr | **180d** | https://www.hubspot.com/partners/affiliates |
| 2 | **Smartlead** | Rewardful | 15→35% recurring (tiered) | 90d | https://smartproducts.getrewardful.com/signup?campaign=smartlead |
| 3 | **Reply.io** | PartnerStack | **30% lifetime** recurring | PS default | https://reply.io/affiliates/ |
| 4 | **Instantly** | PartnerStack | 20→40% recurring (tiered) | PS default | https://dash.partnerstack.com/application?company=instantly&group=affiliatesprogram |
| 5 | **Pipedrive** | PartnerStack | 20→33% (first 12mo) | 90d | https://www.pipedrive.com/en/affiliate-partnership |
| 6 | **Apollo.io** | PartnerStack | 15% (monthly) / 20% (annual), 12mo | n/s | https://www.apollo.io/partners/affiliates |
| 7 | **Hunter.io** | In-house | 30% recurring (12 invoices) | 30d | https://hunter.io/affiliate-program |
| 8 | **Close** | PartnerStack | 30% first-year revenue | 90d | https://dash.partnerstack.com/application?company=close&group=affiliatepartier |
| 9 | **Mailshake** | FirstPromoter | 40% recurring *(verify — aggregators say 60%)* | n/s | https://mailshake.firstpromoter.com/signup/29680 |
| 10 | **Seamless.AI** | PartnerStack | up to 40% (volume-tiered) | 90d | https://dash.partnerstack.com/application?company=seamlessai |
| 11 | **Lemlist** | PartnerStack | ~22–25% (12mo) | PS default | https://lemlist.partnerstack.com |
| 12 | **SavvyCal** | Rewardful | 25% recurring | ~60d | https://savvycal.getrewardful.com/signup |
| 13 | **Freshsales** | PartnerStack | 15% (12mo) + $5/lead | 90d | https://dash.partnerstack.com/application?company=freshworks4391 |
| 14 | **Aircall** | PartnerStack | $75 per qualified lead | 90d | https://aircall.io/partners/affiliate-partners/ |
| 15 | **Lusha** | PartnerStack | up to 20% (first year) | n/s | https://dash.partnerstack.com/application?company=lusha |
| 16 | **Kixie** | PartnerStack | 20% lifetime + $300 bounty | 30d | https://www.kixie.com/partners/apply/ |

> Most of Tier 1 is on **PartnerStack** — make one PartnerStack account and applying to each is a few clicks. Smartlead/SavvyCal are **Rewardful**, HubSpot is **Impact**, Mailshake is **FirstPromoter** (same network as your Fireflies/JustCall logins).

---

## 🟡 TIER 2 — Worth it, but caveats (one-time or slow payout)

| Tool | Network | Commission | Note |
|------|---------|-----------|------|
| Clay | Rewardful | **$50 one-time** (Pro signups) | Flat, no recurring. Hot product, easy approval. |
| Chili Piper | Euler (in-house) | 10% of first-year ARR (one-time) | https://www.chilipiper.com/chili-champion |
| ZoomInfo (+Chorus) | PartnerStack | 10% of ACV (one-time) | Big deals, slow enterprise sales cycle. https://zoominfo.partnerstack.com/ |
| Vidyard | PartnerStack | rate undisclosed | Apply to discover terms. |

---

## 🔴 No public program — cannot monetize directly

These tools have review/comparison pages on the site but **no affiliate program** (gift-card referral or enterprise contact-only). **Strategic implication: point readers from these pages toward a monetizable alternative in the same category** (e.g. Gong review → recommend Fireflies, which you already earn on).

| Tool | Status | Monetizable alternative on-site |
|------|--------|-------------------------------|
| Calendly | "Future reseller program" only | SavvyCal (Tier 1), Chili Piper (Tier 2) |
| Gong | Gift-card referral only ($600 max) | Fireflies (live), Chorus/ZoomInfo (Tier 2) |
| Dialpad | Gift-card referral, high bar | Aircall (Tier 1), JustCall (live), Kixie (Tier 1) |
| Outreach | Enterprise contact-only | Reply.io, Instantly, Lemlist (all Tier 1) |
| Salesloft (+Drift) | Contact-only partner program | Reply.io, Instantly (Tier 1) |
| Clari | No affiliate (partner only) | Gong→Fireflies path |
| Lavender | No program found | Instantly, Lemlist (Tier 1) |

---

## Recommended sequence

1. **Today:** make a PartnerStack account, apply to all PartnerStack Tier 1 programs (8 of the 16). Apply to HubSpot (Impact), Smartlead + SavvyCal (Rewardful), Mailshake (FirstPromoter).
2. **As approvals land** (usually 1–5 days): paste each tracking URL into `affiliate-links.json`, flip to `live`, deploy. The site starts earning on that tool immediately.
3. **Phase 2 content:** prioritize fresh content + internal links toward Tier 1 tools (highest recurring payout). Add "recommended alternative" callouts on the 🔴 no-program pages so that traffic isn't wasted.

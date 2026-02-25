# Phase 3 Tier 2 Brief — 10 New Tool Review Pages + Nav Fix + 2 Guide Pages

**For Claude Code | Branch: `phase3-tier2-tools`**

---

## Context

Read `CLAUDE.md` and `MANUS_CONTEXT.md` before starting.

Phases 0–5 are complete and live on `main`. The site has 10 tool reviews, 32 comparison pages, 14 category pages, 3 persona hubs, and a redesigned homepage.

This brief adds **10 new tool review pages**, fixes the global navbar, and adds 2 remaining guide pages. All tool pages must use the existing `review.njk` layout and the established JSON schema in `_data/tools/`. Do NOT create a new layout — use what exists.

---

## Session Breakdown

### Session 1 — Nav fix + 2 guide pages (30 min)

**Branch:** `git checkout -b phase3-tier2-tools`

#### Task 1: Add "How We Score" to navbar

Edit `_includes/navbar.njk`. Add one item after "Guides":

```html
<li><a href="/how-we-score/">How We Score</a></li>
```

The page already exists at `_site/how-we-score/index.html`. This is a one-line change.

#### Task 2: Best Revenue Intelligence Platforms 2026

**File:** `guides/best-revenue-intelligence-platforms.njk`
**URL:** `/guides/best-revenue-intelligence-platforms.html`
**Target keyword:** "best revenue intelligence platforms" (720/mo)
**Layout:** `guide.njk` (same as all other guide pages)

Frontmatter:
```yaml
---
layout: guide.njk
title: "6 Best Revenue Intelligence Platforms in 2026 (Tested)"
description: "Revenue intelligence tools that turn pipeline data into forecasting accuracy. We tested Clari, Gong, Salesloft, Outreach, Boostup, and Aviso — here's what actually works."
lastUpdated: "February 2026"
toolCount: 6
canonicalUrl: "https://salesaiguide.com/guides/best-revenue-intelligence-platforms.html"
sidebarTools:
  - name: "Clari"
    bestFor: "Pipeline forecasting accuracy"
    ctaUrl: "/go/clari"
  - name: "Gong"
    bestFor: "Call intelligence + revenue signals"
    ctaUrl: "/go/gong"
  - name: "Salesloft"
    bestFor: "Engagement + revenue workflow"
    ctaUrl: "/go/salesloft"
---
```

Content structure (write full content for each section):

1. **Intro paragraph** — What revenue intelligence is, why it matters in 2026 (AI forecasting vs. gut feel), who this guide is for.
2. **Quick Comparison Table** — 6 tools × columns: Tool, Best For, Org Score, Starting Price, Free Trial
3. **Tool 1: Clari** — What it does, who it's for, pricing, pros/cons, verdict
4. **Tool 2: Gong** — What it does, who it's for, pricing, pros/cons, verdict
5. **Tool 3: Salesloft** — What it does, who it's for, pricing, pros/cons, verdict
6. **Tool 4: Outreach** — What it does, who it's for, pricing, pros/cons, verdict
7. **Tool 5: Boostup** — What it does, who it's for, pricing, pros/cons, verdict
8. **Tool 6: Aviso** — What it does, who it's for, pricing, pros/cons, verdict
9. **How to Choose** — Decision framework by team size and use case
10. **FAQ** — 3 questions

Use the same writing style as `guides/best-ai-sdr-tools.njk` for reference.

#### Task 3: 6 Best Instantly Alternatives 2026

**File:** `guides/best-instantly-alternatives.njk`
**URL:** `/guides/best-instantly-alternatives.html`
**Target keyword:** "instantly alternatives" (1,100/mo)
**Layout:** `guide.njk`

Frontmatter:
```yaml
---
layout: guide.njk
title: "6 Best Instantly Alternatives in 2026 (Honest Comparison)"
description: "Looking for Instantly alternatives? We compared Smartlead, Lemlist, Mailshake, Woodpecker, QuickMail, and Apollo to find the best fit for cold email at scale."
lastUpdated: "February 2026"
toolCount: 6
canonicalUrl: "https://salesaiguide.com/guides/best-instantly-alternatives.html"
sidebarTools:
  - name: "Smartlead"
    bestFor: "Unlimited mailboxes, budget teams"
    ctaUrl: "/go/smartlead"
  - name: "Lemlist"
    bestFor: "Personalization + video"
    ctaUrl: "/go/lemlist"
  - name: "Apollo"
    bestFor: "All-in-one prospecting + sending"
    ctaUrl: "/go/apollo"
---
```

Content structure:

1. **Intro** — Why someone would leave Instantly (pricing, deliverability, features), what to look for in an alternative.
2. **Quick Comparison Table** — 6 tools × columns: Tool, Best For, Rep Score, Starting Price, Unlimited Mailboxes?
3. **Alternative 1: Smartlead** — Full writeup
4. **Alternative 2: Lemlist** — Full writeup
5. **Alternative 3: Apollo** — Full writeup
6. **Alternative 4: Mailshake** — Full writeup
7. **Alternative 5: Woodpecker** — Full writeup
8. **Alternative 6: QuickMail** — Full writeup
9. **How to Choose** — Decision tree: budget vs. features vs. deliverability
10. **FAQ** — 3 questions

---

### Session 2 — Tool pages: Cognism, Lusha, LeadIQ, Warmly (90 min)

Create 4 JSON files in `_data/tools/` and 4 `.njk` source files in `tools/`.

#### JSON Schema Reference

Every JSON file must follow the exact same schema as `_data/tools/clay.json`. All top-level keys are required:

```
meta, jsonLd, hero, scores, quickSummary, whatIs, features, pricing,
g2Reviews, competitorTable, whoIsFor, decisionModule, content,
stackPairings, alternatives, faqs, sidebar, finalCta
```

The `decisionModule` must include:
- `verdict` (bestFor, avoidIf, bottomLine, ctaUrl, ctaText)
- `dualScore` (org.score, org.explain, individual.score, individual.explain)
- `subScores` (6 items: Enterprise Fit, Ease of Adoption, AI Depth, Integration Depth, Pricing Transparency, Scalability)
- `decisionSnapshot.rows` (6 rows, each with dimension, score, notes, evidence array)
- `evidenceSignals` (confidence, confidenceNote, sourcePills, freshness, reviewSentiment, communityWorkflows, demoVerified, docsVerified, strengthThemes, limitationThemes, disagreements)

The `whatIs` object must include `paragraphs` and `noteHtml` (the "not firsthand testing" disclosure).

#### Tool 1: Cognism

**JSON:** `_data/tools/cognism.json`
**Source:** `tools/cognism-review.njk`
**URL:** `/tools/cognism-review.html`
**Category:** Data Enrichment / B2B Data
**G2:** ~4.6/5, ~700+ reviews
**Pricing:** Custom (enterprise-only, no public pricing)
**Org Score:** 68 | **Rep Score:** 62
**Persona tag:** REQUIRES ADMIN (same class as ZoomInfo)

Key facts to encode:
- EMEA-focused B2B data provider; strongest for UK/EU prospecting
- GDPR-compliant by design — "do not call" registry checks built in
- Phone-verified mobile numbers are its differentiator vs. ZoomInfo
- Waterfall enrichment available but less flexible than Clay
- No self-serve pricing — requires sales call
- Integrates with Salesforce, HubSpot, Outreach, Salesloft
- Comparison pages that exist: `cognism-vs-zoominfo.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 7 | SOC 2 compliant; GDPR-ready; SSO available |
| Ease of Adoption | 6 | Chrome extension easy; platform setup requires onboarding |
| AI Depth | 5 | Limited AI features; data quality over AI enrichment |
| Integration Depth | 8 | Native Salesforce, HubSpot, Outreach, Salesloft connectors |
| Pricing Transparency | 3 | No public pricing; requires sales call |
| Scalability | 7 | Enterprise-grade; handles large team deployments |

**`evidenceSignals`:** confidence: medium (limited public reviews vs. US tools)

**Source file frontmatter:**
```yaml
---
layout: review.njk
toolKey: cognism
permalink: tools/cognism-review.html
---
```

#### Tool 2: Lusha

**JSON:** `_data/tools/lusha.json`
**Source:** `tools/lusha-review.njk`
**URL:** `/tools/lusha-review.html`
**Category:** Data Enrichment / Contact Intelligence
**G2:** ~4.3/5, ~1,400+ reviews
**Pricing:** Free tier; Pro from $29/mo; Scale from $51/mo; custom Enterprise
**Org Score:** 58 | **Rep Score:** 65
**Persona tag:** FOR REPS (self-serve, low friction)

Key facts:
- Chrome extension for LinkedIn contact lookup — primary use case
- Smaller database than ZoomInfo/Apollo but faster for individual reps
- Free tier (5 credits/mo) makes it accessible for solo prospectors
- Data accuracy complaints in EU markets
- No sequences or email sending — data only
- Comparison pages that exist: `leadiq-vs-lusha.html`, `lusha-vs-apollo.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 4 | Limited team management; better for SMB/individual use |
| Ease of Adoption | 9 | Chrome extension installs in 2 minutes; no training needed |
| AI Depth | 3 | No AI features; straightforward contact lookup |
| Integration Depth | 6 | Salesforce, HubSpot, Pipedrive; limited vs. enterprise tools |
| Pricing Transparency | 9 | Clear public pricing; free tier available |
| Scalability | 5 | Credit model limits scale; expensive at volume |

**`evidenceSignals`:** confidence: high

#### Tool 3: LeadIQ

**JSON:** `_data/tools/leadiq.json`
**Source:** `tools/leadiq-review.njk`
**URL:** `/tools/leadiq-review.html`
**Category:** Data Enrichment / Prospecting
**G2:** ~4.2/5, ~900+ reviews
**Pricing:** Free tier; Essential from $39/mo; Pro from $79/mo; Enterprise custom
**Org Score:** 60 | **Rep Score:** 68
**Persona tag:** FOR REPS

Key facts:
- LinkedIn prospecting tool with real-time email/phone capture
- Scribe AI feature writes personalized first lines from LinkedIn data
- Smaller database than Apollo/ZoomInfo but strong for LinkedIn workflows
- CRM sync (Salesforce, HubSpot, Outreach) is a key differentiator
- Better data freshness than static databases for active LinkedIn users
- Comparison pages that exist: `leadiq-vs-lusha.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 5 | Team features exist; better suited for mid-market |
| Ease of Adoption | 8 | Chrome extension; quick LinkedIn workflow integration |
| AI Depth | 7 | Scribe AI for personalized first lines is genuinely useful |
| Integration Depth | 7 | Salesforce, HubSpot, Outreach, Salesloft native |
| Pricing Transparency | 8 | Public pricing; free tier available |
| Scalability | 6 | Credit limits can constrain high-volume teams |

**`evidenceSignals`:** confidence: high

#### Tool 4: Warmly

**JSON:** `_data/tools/warmly.json`
**Source:** `tools/warmly-review.njk`
**URL:** `/tools/warmly-review.html`
**Category:** Intent Data / Website Visitor Intelligence
**G2:** ~4.8/5, ~300+ reviews
**Pricing:** Free tier (up to 500 visitors/mo); Business from $700/mo; Enterprise custom
**Org Score:** 65 | **Rep Score:** 45
**Persona tag:** REQUIRES ADMIN

Key facts:
- Identifies anonymous website visitors using IP + intent data
- Integrates with Clearbit, 6sense, Bombora for enrichment
- Slack/CRM alerts when target accounts visit key pages
- AI agent feature (Warmly AI) can auto-engage visitors via chat
- Primarily a RevOps/marketing tool — reps rarely configure it
- Comparison pages that exist: `warmly-vs-leadfeeder.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 7 | SOC 2; enterprise integrations; team alerting workflows |
| Ease of Adoption | 5 | JavaScript snippet easy; alert routing requires RevOps setup |
| AI Depth | 8 | AI agent for real-time visitor engagement is differentiated |
| Integration Depth | 9 | Clearbit, 6sense, Bombora, Salesforce, HubSpot, Slack |
| Pricing Transparency | 6 | Free tier clear; Business pricing requires demo |
| Scalability | 7 | Scales with traffic volume; pricing jumps at enterprise |

**`evidenceSignals`:** confidence: medium (newer tool, fewer reviews)

---

### Session 3 — Tool pages: Vidyard, Chili Piper, Clari, Seismic (90 min)

Same approach as Session 2. Four more JSON + source file pairs.

#### Tool 5: Vidyard

**JSON:** `_data/tools/vidyard.json`
**Source:** `tools/vidyard-review.njk`
**URL:** `/tools/vidyard-review.html`
**Category:** Sales Enablement / Video
**G2:** ~4.5/5, ~800+ reviews
**Pricing:** Free tier; Pro from $19/mo; Plus from $59/mo; Enterprise custom
**Org Score:** 62 | **Rep Score:** 70
**Persona tag:** FOR REPS

Key facts:
- Async video messaging for sales outreach — screen + webcam recording
- Chrome extension for recording and sharing from Gmail/LinkedIn
- Video analytics show who watched, how long, and what they rewatched
- AI script generator for video outreach
- Integrates with Salesforce, HubSpot, Outreach, Salesloft
- Comparison pages that exist: `vidyard-vs-heygen.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 6 | SSO available; team analytics; enterprise compliance options |
| Ease of Adoption | 9 | Chrome extension; reps recording in under 5 minutes |
| AI Depth | 7 | AI script generator; engagement analytics |
| Integration Depth | 8 | Native CRM + SEP integrations; Gmail/LinkedIn extensions |
| Pricing Transparency | 9 | Clear public pricing; generous free tier |
| Scalability | 7 | Scales well; enterprise pricing for advanced analytics |

**`evidenceSignals`:** confidence: high

#### Tool 6: Chili Piper

**JSON:** `_data/tools/chili-piper.json`
**Source:** `tools/chili-piper-review.njk`
**URL:** `/tools/chili-piper-review.html`
**Category:** Scheduling / Meeting Intelligence
**G2:** ~4.4/5, ~1,000+ reviews
**Pricing:** Instant Booker from $22.50/seat/mo; Concierge from $30/seat/mo; Enterprise custom
**Org Score:** 70 | **Rep Score:** 65
**Persona tag:** FOR REPS

Key facts:
- Inbound lead routing and scheduling — primary use case is "book a meeting from a form fill"
- Concierge product routes inbound leads to the right rep in real time
- Distro product handles round-robin and territory-based routing
- Integrates with Salesforce, HubSpot, Marketo, Pardot
- Pricing is per seat AND per product — can get expensive
- Comparison pages that exist: `calendly-vs-chili-piper.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 8 | Salesforce-native; complex routing rules; enterprise compliance |
| Ease of Adoption | 6 | Form embed easy; routing logic requires RevOps configuration |
| AI Depth | 5 | Limited AI; routing is rule-based not ML-driven |
| Integration Depth | 9 | Deep Salesforce/HubSpot/Marketo integration; best-in-class |
| Pricing Transparency | 6 | Public pricing but multiple products add up quickly |
| Scalability | 8 | Handles enterprise inbound volume; proven at scale |

**`evidenceSignals`:** confidence: high

#### Tool 7: Clari

**JSON:** `_data/tools/clari.json`
**Source:** `tools/clari-review.njk`
**URL:** `/tools/clari-review.html`
**Category:** Revenue Intelligence / Forecasting
**G2:** ~4.6/5, ~500+ reviews
**Pricing:** Enterprise only; custom pricing; typically $50–100/seat/mo
**Org Score:** 72 | **Rep Score:** 55
**Persona tag:** REQUIRES ADMIN

Key facts:
- AI-powered pipeline forecasting — predicts deal outcomes from CRM + activity data
- Copilot feature captures call recordings and auto-updates CRM
- Revenue cadence workflow for weekly forecast reviews
- Primarily a sales manager and RevOps tool — reps use it passively
- Competes directly with Gong Revenue Intelligence and Salesforce Einstein
- Comparison pages that exist: `boostup-vs-clari.html`, `clari-vs-aviso.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 9 | SOC 2 Type II; SSO; enterprise security; Fortune 500 clients |
| Ease of Adoption | 5 | Requires CRM integration setup; 2–4 week implementation |
| AI Depth | 9 | AI forecasting is core product; call intelligence via Copilot |
| Integration Depth | 9 | Salesforce-native; HubSpot; Outreach; Salesloft; Gong |
| Pricing Transparency | 2 | No public pricing; requires enterprise sales process |
| Scalability | 9 | Built for enterprise; handles complex org structures |

**`evidenceSignals`:** confidence: medium (limited public pricing data)

#### Tool 8: Seismic

**JSON:** `_data/tools/seismic.json`
**Source:** `tools/seismic-review.njk`
**URL:** `/tools/seismic-review.html`
**Category:** Sales Enablement / Content Management
**G2:** ~4.7/5, ~1,700+ reviews
**Pricing:** Enterprise only; custom; typically $384–480/seat/year
**Org Score:** 74 | **Rep Score:** 58
**Persona tag:** REQUIRES ADMIN

Key facts:
- Sales content management platform — reps find, personalize, and share content
- LiveSend tracks what prospects engage with after content is shared
- AI content recommendations based on deal stage and buyer persona
- Competes with Highspot as the two dominant enterprise enablement platforms
- Implementation is heavy — typically 3–6 months for full deployment
- Comparison pages that exist: `seismic-vs-highspot.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 10 | SOC 2; GDPR; SSO; enterprise-grade governance and compliance |
| Ease of Adoption | 4 | Heavy implementation; requires dedicated enablement team |
| AI Depth | 8 | AI content recommendations; predictive content scoring |
| Integration Depth | 9 | Salesforce, HubSpot, Outreach, Salesloft, Teams, Slack |
| Pricing Transparency | 2 | No public pricing; enterprise-only sales process |
| Scalability | 9 | Built for global enterprise; multi-language, multi-region |

**`evidenceSignals`:** confidence: high (large G2 review base)

---

### Session 4 — Tool pages: Highspot, MindTickle (60 min)

#### Tool 9: Highspot

**JSON:** `_data/tools/highspot.json`
**Source:** `tools/highspot-review.njk`
**URL:** `/tools/highspot-review.html`
**Category:** Sales Enablement / Readiness
**G2:** ~4.7/5, ~1,100+ reviews
**Pricing:** Enterprise only; custom; comparable to Seismic
**Org Score:** 72 | **Rep Score:** 60
**Persona tag:** REQUIRES ADMIN

Key facts:
- Sales enablement platform combining content management + training + coaching
- Scorecards feature tracks rep readiness and content usage
- Copilot AI for content recommendations and pitch guidance
- Stronger on training/readiness than Seismic; Seismic stronger on content governance
- Comparison pages that exist: `seismic-vs-highspot.html`, `highspot-vs-showpad.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 9 | SOC 2 Type II; SSO; enterprise security; global deployments |
| Ease of Adoption | 5 | Lighter implementation than Seismic; still requires 4–8 weeks |
| AI Depth | 8 | Copilot AI for content recommendations; readiness scoring |
| Integration Depth | 9 | Salesforce, HubSpot, Outreach, Salesloft, Teams, Zoom |
| Pricing Transparency | 2 | No public pricing; enterprise-only |
| Scalability | 9 | Global enterprise deployments; multi-language support |

**`evidenceSignals`:** confidence: high

#### Tool 10: MindTickle

**JSON:** `_data/tools/mindtickle.json`
**Source:** `tools/mindtickle-review.njk`
**URL:** `/tools/mindtickle-review.html`
**Category:** Sales Coaching / Readiness
**G2:** ~4.7/5, ~2,000+ reviews
**Pricing:** Enterprise only; custom; typically $20–40/seat/mo
**Org Score:** 68 | **Rep Score:** 55
**Persona tag:** REQUIRES ADMIN

Key facts:
- Sales readiness platform — onboarding, training, coaching, and certification
- Call AI analyzes recorded calls and scores against custom rubrics
- Mission feature for practice pitches with AI feedback
- Competes with Highspot on readiness; more training-focused than enablement-focused
- Strong in financial services, tech, and healthcare verticals
- Comparison pages that exist: `mindtickle-vs-allego.html`

**`decisionSnapshot` rows:**
| Dimension | Score | Notes |
|---|---|---|
| Enterprise Fit | 8 | SOC 2; SSO; enterprise compliance; vertical-specific deployments |
| Ease of Adoption | 5 | Manager setup required; reps use passively for training |
| AI Depth | 8 | Call AI scoring; AI-powered practice feedback |
| Integration Depth | 7 | Salesforce, HubSpot, Zoom, Teams; fewer SEP integrations |
| Pricing Transparency | 2 | No public pricing; enterprise-only |
| Scalability | 8 | Global enterprise; handles large sales org onboarding |

**`evidenceSignals`:** confidence: high (large G2 review base)

---

### Session 5 — PR + Validation (15 min)

1. Run `npx @11ty/eleventy --quiet` — must be 0 errors, ~78 files
2. Verify all 10 new tool pages exist in `_site/tools/`
3. Verify the 2 new guide pages exist in `_site/guides/`
4. Verify "How We Score" appears in the navbar on at least 3 pages
5. Spot-check 2 tool pages: confirm `dm-score-number`, `dm-evidence-drawer`, `dm-evidence-confidence` all present in built HTML
6. Open PR titled: `feat(content): Phase 3 Tier 2 — 10 tool pages + nav fix + 2 guide pages`
7. **Do NOT merge** — Manus reviews and merges

---

## Important Notes for Claude Code

**JSON file naming:** Use lowercase with hyphens matching the URL slug. `chili-piper.json` not `chilipiper.json`.

**Source file permalink:** Must match the URL exactly. Example:
```yaml
permalink: tools/cognism-review.html
```

**Logo images:** Use `/img/logos/{toolname}.png` as the `logoSrc`. If the file doesn't exist, use `/img/logos/placeholder.png` — do not create image files.

**Affiliate CTAs:** Use `/go/{toolname}` for all `ctaUrl` fields. These are Netlify redirects. For tools without affiliate programs yet, use the vendor's homepage as a fallback in `_redirects` if not already present.

**Review URLs in comparison pages:** Several comparison pages (e.g., `cognism-vs-zoominfo.njk`) currently point `reviewUrl` to `/tools/index.html` for Cognism because the review page didn't exist. After building the Cognism review page, update `cognism-vs-zoominfo.njk` to point `toolA.reviewUrl` to `/tools/cognism-review.html`. Do the same for any other comparison pages that reference the new tools.

**Comparison pages to update after building new tool pages:**

| Comparison file | Field to update | New value |
|---|---|---|
| `cognism-vs-zoominfo.njk` | `toolA.reviewUrl` | `/tools/cognism-review.html` |
| `leadiq-vs-lusha.njk` | both `toolA.reviewUrl` and `toolB.reviewUrl` | `/tools/leadiq-review.html` and `/tools/lusha-review.html` |
| `lusha-vs-apollo.njk` | `toolA.reviewUrl` | `/tools/lusha-review.html` |
| `warmly-vs-leadfeeder.njk` | `toolA.reviewUrl` | `/tools/warmly-review.html` |
| `vidyard-vs-heygen.njk` | `toolA.reviewUrl` | `/tools/vidyard-review.html` |
| `calendly-vs-chili-piper.njk` | `toolB.reviewUrl` | `/tools/chili-piper-review.html` |
| `boostup-vs-clari.njk` | `toolB.reviewUrl` | `/tools/clari-review.html` |
| `clari-vs-aviso.njk` | `toolA.reviewUrl` | `/tools/clari-review.html` |
| `seismic-vs-highspot.njk` | both | `/tools/seismic-review.html` and `/tools/highspot-review.html` |
| `highspot-vs-showpad.njk` | `toolA.reviewUrl` | `/tools/highspot-review.html` |
| `mindtickle-vs-allego.njk` | `toolA.reviewUrl` | `/tools/mindtickle-review.html` |

**Writing tone:** Match the existing tool pages exactly. Specific, direct, no marketing language. Use "Based on G2 reviews" not "According to users". Use "Requires admin setup" not "Easy to use for teams".

# Phase 6 Brief — 21 Tier 2 Comparison Pages

**For Claude Code | Branch: `phase6-tier2-comparisons`**

---

## Context

Read `CLAUDE.md` and `MANUS_CONTEXT.md` before starting.

All 20 tool review pages now exist. This brief adds 21 new comparison pages using the existing `compare.njk` layout. Every comparison page must follow the exact same frontmatter schema as the existing pages in `compare/`. Do NOT create a new layout or modify `compare.njk`.

**Existing comparisons (do not recreate):** apollo-vs-zoominfo, boostup-vs-clari, calendly-vs-chili-piper, clari-vs-aviso, clay-vs-apollo, clay-vs-clearbit, cognism-vs-zoominfo, gong-vs-avoma, gong-vs-chorus, highspot-vs-showpad, hubspot-vs-monday-crm, hubspot-vs-pipedrive, instantly-vs-lemlist, instantly-vs-mailshake, instantly-vs-smartlead, lavender-vs-autobound, lavender-vs-instantly, leadiq-vs-lusha, lusha-vs-apollo, mindtickle-vs-allego, outreach-vs-salesloft, salesloft-vs-klenty, seismic-vs-highspot, smartlead-vs-saleshandy, vidyard-vs-heygen, warmly-vs-leadfeeder

---

## Frontmatter Schema (Required for Every Page)

```yaml
---
layout: compare.njk
title: "[ToolA] vs [ToolB]: Which Is Better in 2026? | Sales AI Guide"
description: "Decision-grade comparison of [ToolA] vs [ToolB]. Side-by-side scores, user reviews, pricing deep-dive, enterprise readiness, and migration notes for 2026."
ogTitle: "[ToolA] vs [ToolB]: Which Is Better in 2026? | Sales AI Guide"
ogDescription: "Decision-grade comparison of [ToolA] vs [ToolB]. Side-by-side scores, user reviews, pricing deep-dive, enterprise readiness, and migration notes for 2026."
ogUrl: "https://salesaiguide.com/compare/[slug].html"
twitterTitle: "[ToolA] vs [ToolB]: Which Is Better in 2026? | Sales AI Guide"
twitterDescription: "Decision-grade comparison of [ToolA] vs [ToolB]. Side-by-side scores, user reviews, pricing deep-dive, enterprise readiness, and migration notes for 2026."
canonicalUrl: "https://salesaiguide.com/compare/[slug].html"
permalink: compare/[slug].html
toolA:
  name: "[ToolA display name]"
  orgScore: [number]
  repScore: [number]
  verdict: "[one-line best-for statement]"
  startingPrice: "[price string]"
  ctaUrl: "/go/[toolA-slug]"
  reviewUrl: "/tools/[toolA-slug]-review.html"
toolB:
  name: "[ToolB display name]"
  orgScore: [number]
  repScore: [number]
  verdict: "[one-line best-for statement]"
  startingPrice: "[price string]"
  ctaUrl: "/go/[toolB-slug]"
  reviewUrl: "/tools/[toolB-slug]-review.html"
relatedComparisons:
  - url: "[related-slug].html"
    label: "[ToolX] vs [ToolY]"
  - url: "[related-slug].html"
    label: "[ToolX] vs [ToolY]"
  - url: "[related-slug].html"
    label: "[ToolX] vs [ToolY]"
footerDisclosureText: "Learn more"
extraHead: |
    <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Article",
          "headline": "[ToolA] vs [ToolB]: Comparison Guide",
          "author": {"@type": "Organization", "name": "Sales AI Guide"},
          "datePublished": "2026-02-24",
          "dateModified": "2026-02-24",
          "publisher": {"@type": "Organization", "name": "Sales AI Guide"}
        }
        </script>
    <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
            {"@type": "Question", "name": "[FAQ 1 question]", "acceptedAnswer": {"@type": "Answer", "text": "[FAQ 1 answer — 2-3 sentences, specific and direct]"}},
            {"@type": "Question", "name": "[FAQ 2 question]", "acceptedAnswer": {"@type": "Answer", "text": "[FAQ 2 answer]"}},
            {"@type": "Question", "name": "[FAQ 3 question]", "acceptedAnswer": {"@type": "Answer", "text": "[FAQ 3 answer]"}}
          ]
        }
        </script>
---
```

After the frontmatter, the file body must be **empty** — `compare.njk` generates all content from the frontmatter data. Do not add any HTML or Markdown after the closing `---`.

---

## Score Reference (All 20 Tools)

| Tool | Org Score | Rep Score | Starting Price |
|---|---|---|---|
| Apollo | 68 | 72 | $49/mo |
| Chili Piper | 70 | 65 | $22.50/seat/mo |
| Clari | 72 | 55 | Custom |
| Clay | 73 | 68 | $149/mo |
| Cognism | 68 | 62 | Custom |
| Gong | 78 | 63 | Custom |
| Highspot | 72 | 60 | Custom |
| HubSpot | 74 | 72 | $20/seat/mo |
| Instantly | 63 | 70 | $37/mo |
| Lavender | 63 | 79 | $29/mo |
| LeadIQ | 60 | 68 | $39/mo |
| Lusha | 58 | 65 | $29/mo |
| MindTickle | 68 | 55 | Custom |
| Outreach | 73 | 53 | Custom |
| Salesloft | 70 | 56 | Custom |
| Seismic | 74 | 58 | Custom |
| Smartlead | 54 | 64 | $39/mo |
| Vidyard | 62 | 70 | $19/mo |
| Warmly | 65 | 45 | $700/mo |
| ZoomInfo | 77 | 51 | Custom |

---

## Session 1 — Data Enrichment & Prospecting Comparisons (7 pages)

### 1. `apollo-vs-hubspot.njk`
**Slug:** `apollo-vs-hubspot`
**Search intent:** "apollo vs hubspot" — teams evaluating all-in-one CRM vs dedicated prospecting

```yaml
toolA:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for outbound-first teams that don't need a full CRM"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want CRM + outreach in one platform"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "apollo-vs-zoominfo.html"
    label: "Apollo.io vs ZoomInfo"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
  - url: "lusha-vs-apollo.html"
    label: "Lusha vs Apollo.io"
```

FAQs:
1. "Is Apollo better than HubSpot for cold outreach?" — Apollo wins on outbound: built-in sequences, 275M contact database, email warmup. HubSpot's sequences are limited on lower tiers and lack Apollo's prospecting depth. If cold outreach is your primary motion, Apollo is the stronger choice.
2. "Can I use Apollo and HubSpot together?" — Yes, this is a very common stack. Apollo handles prospecting and initial outreach; HubSpot manages the CRM, deal tracking, and inbound leads. Apollo's native HubSpot integration syncs contacts, activities, and sequences bidirectionally.
3. "Which is better for a small sales team?" — HubSpot's free CRM tier makes it the default starting point for small teams. Apollo's free tier (10K leads/mo) is strong for prospecting. Most small teams start with HubSpot CRM free + Apollo free, then upgrade Apollo as outbound volume grows.

---

### 2. `cognism-vs-apollo.njk`
**Slug:** `cognism-vs-apollo`
**Search intent:** "cognism vs apollo" — EMEA teams evaluating data providers

```yaml
toolA:
  name: "Cognism"
  orgScore: 68
  repScore: 62
  verdict: "Best for EMEA prospecting with GDPR compliance requirements"
  startingPrice: "Custom"
  ctaUrl: "/go/cognism"
  reviewUrl: "/tools/cognism-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for North American outbound with built-in sequences"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "cognism-vs-zoominfo.html"
    label: "Cognism vs ZoomInfo"
  - url: "apollo-vs-zoominfo.html"
    label: "Apollo.io vs ZoomInfo"
  - url: "lusha-vs-apollo.html"
    label: "Lusha vs Apollo.io"
```

FAQs:
1. "Is Cognism or Apollo better for UK/EU prospecting?" — Cognism is the stronger choice for UK/EU. It maintains GDPR-compliant data with built-in TPS/CTPS checks and phone-verified mobile numbers for European contacts. Apollo's EU data coverage is thinner and lacks the same compliance infrastructure.
2. "Does Apollo have GDPR compliance?" — Apollo has a GDPR compliance framework and EU data processing agreements, but it is not purpose-built for GDPR the way Cognism is. Cognism's data team actively removes contacts from suppression lists; Apollo relies more on user-side compliance controls.
3. "Which has better data accuracy?" — For North America, Apollo's 275M contact database is generally more comprehensive. For EMEA, Cognism's phone-verified mobile numbers have a reputation for higher accuracy, particularly for UK and DACH markets.

---

### 3. `lusha-vs-zoominfo.njk`
**Slug:** `lusha-vs-zoominfo`
**Search intent:** "lusha vs zoominfo" — SMB teams evaluating enterprise data vs self-serve

```yaml
toolA:
  name: "Lusha"
  orgScore: 58
  repScore: 65
  verdict: "Best for individual reps who need fast LinkedIn contact lookup"
  startingPrice: "$29/mo"
  ctaUrl: "/go/lusha"
  reviewUrl: "/tools/lusha-review.html"
toolB:
  name: "ZoomInfo"
  orgScore: 77
  repScore: 51
  verdict: "Best for enterprise teams that need deep company intelligence"
  startingPrice: "Custom"
  ctaUrl: "/go/zoominfo"
  reviewUrl: "/tools/zoominfo-review.html"
relatedComparisons:
  - url: "cognism-vs-zoominfo.html"
    label: "Cognism vs ZoomInfo"
  - url: "leadiq-vs-lusha.html"
    label: "LeadIQ vs Lusha"
  - url: "lusha-vs-apollo.html"
    label: "Lusha vs Apollo.io"
```

FAQs:
1. "Is Lusha cheaper than ZoomInfo?" — Significantly. Lusha starts at $29/mo with a free tier; ZoomInfo requires a custom enterprise contract typically starting at $15,000+/year. For individual reps or small teams, Lusha's self-serve pricing is far more accessible.
2. "Does ZoomInfo have better data than Lusha?" — ZoomInfo's database is larger and includes deeper company intelligence (org charts, technographics, intent data). Lusha's strength is speed and ease of use for individual contact lookup, not breadth of company data.
3. "Can a small team use ZoomInfo?" — ZoomInfo's minimum contract size and enterprise-only sales process make it impractical for teams under 10 seats. Lusha, Apollo, or LeadIQ are better fits for small teams that need self-serve access.

---

### 4. `leadiq-vs-apollo.njk`
**Slug:** `leadiq-vs-apollo`
**Search intent:** "leadiq vs apollo" — reps choosing between LinkedIn-focused vs all-in-one

```yaml
toolA:
  name: "LeadIQ"
  orgScore: 60
  repScore: 68
  verdict: "Best for LinkedIn-first prospecting with AI-personalized first lines"
  startingPrice: "$39/mo"
  ctaUrl: "/go/leadiq"
  reviewUrl: "/tools/leadiq-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for all-in-one prospecting, sequences, and CRM sync"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "leadiq-vs-lusha.html"
    label: "LeadIQ vs Lusha"
  - url: "lusha-vs-apollo.html"
    label: "Lusha vs Apollo.io"
  - url: "apollo-vs-zoominfo.html"
    label: "Apollo.io vs ZoomInfo"
```

FAQs:
1. "Does LeadIQ have email sequences like Apollo?" — No. LeadIQ is a data capture and enrichment tool — it does not include email sequencing. You capture contacts via LeadIQ and sync them to Outreach, Salesloft, or Apollo for sequencing. Apollo is the all-in-one option if you want prospecting and sequences in one platform.
2. "What is LeadIQ's Scribe feature?" — Scribe uses AI to write personalized first lines for cold emails based on a prospect's LinkedIn activity, recent posts, and job changes. It's one of LeadIQ's key differentiators over Apollo and Lusha, which don't offer AI-generated personalization at the point of capture.
3. "Which has better CRM integration?" — Both integrate with Salesforce and HubSpot. Apollo's CRM sync is deeper for sales engagement workflows; LeadIQ's sync is cleaner for simple contact creation. Teams using Outreach or Salesloft often prefer LeadIQ's native integrations with those platforms.

---

### 5. `clay-vs-zoominfo.njk`
**Slug:** `clay-vs-zoominfo`
**Search intent:** "clay vs zoominfo" — RevOps teams evaluating enrichment approaches

```yaml
toolA:
  name: "Clay"
  orgScore: 73
  repScore: 68
  verdict: "Best for RevOps teams building custom enrichment workflows"
  startingPrice: "$149/mo"
  ctaUrl: "/go/clay"
  reviewUrl: "/tools/clay-review.html"
toolB:
  name: "ZoomInfo"
  orgScore: 77
  repScore: 51
  verdict: "Best for enterprise teams that need a single authoritative data source"
  startingPrice: "Custom"
  ctaUrl: "/go/zoominfo"
  reviewUrl: "/tools/zoominfo-review.html"
relatedComparisons:
  - url: "clay-vs-apollo.html"
    label: "Clay vs Apollo.io"
  - url: "cognism-vs-zoominfo.html"
    label: "Cognism vs ZoomInfo"
  - url: "apollo-vs-zoominfo.html"
    label: "Apollo.io vs ZoomInfo"
```

FAQs:
1. "Is Clay a ZoomInfo replacement?" — Not directly. ZoomInfo is a data provider; Clay is a workflow automation platform that can pull from ZoomInfo (and 50+ other providers) as one of its sources. Teams often use Clay to waterfall across ZoomInfo, Apollo, Clearbit, and others — getting the best data from each.
2. "Which is better for large enterprise teams?" — ZoomInfo is better suited for large enterprise teams that need a single managed data contract, org chart data, and intent signals. Clay requires more technical setup and is better for RevOps-led teams that want to build custom enrichment logic.
3. "Can Clay access ZoomInfo data?" — Yes, Clay has a native ZoomInfo integration. If your company has a ZoomInfo contract, you can use it as a data source within Clay workflows alongside other providers.

---

### 6. `cognism-vs-lusha.njk`
**Slug:** `cognism-vs-lusha`
**Search intent:** "cognism vs lusha" — EMEA reps choosing between providers

```yaml
toolA:
  name: "Cognism"
  orgScore: 68
  repScore: 62
  verdict: "Best for EMEA teams that need phone-verified mobile numbers"
  startingPrice: "Custom"
  ctaUrl: "/go/cognism"
  reviewUrl: "/tools/cognism-review.html"
toolB:
  name: "Lusha"
  orgScore: 58
  repScore: 65
  verdict: "Best for individual reps who want fast, self-serve contact lookup"
  startingPrice: "$29/mo"
  ctaUrl: "/go/lusha"
  reviewUrl: "/tools/lusha-review.html"
relatedComparisons:
  - url: "cognism-vs-zoominfo.html"
    label: "Cognism vs ZoomInfo"
  - url: "leadiq-vs-lusha.html"
    label: "LeadIQ vs Lusha"
  - url: "lusha-vs-apollo.html"
    label: "Lusha vs Apollo.io"
```

FAQs:
1. "Is Cognism or Lusha better for UK prospecting?" — Cognism is significantly stronger for UK prospecting. Its phone-verified mobile numbers and TPS/CTPS compliance checks are purpose-built for the UK market. Lusha's UK data coverage is thinner and lacks the same compliance infrastructure.
2. "Does Lusha have a free tier?" — Yes, Lusha offers 5 free credits per month with no credit card required. Cognism has no free tier and requires a sales call to get pricing. For individual reps testing a data tool, Lusha is far more accessible.
3. "Which is better for a team of 5 SDRs?" — Lusha's Pro plan ($29/mo) is more practical for a small team. Cognism's minimum contract is enterprise-sized and requires negotiation. Unless the team is primarily prospecting in EMEA, Lusha or Apollo is a better fit at this scale.

---

### 7. `warmly-vs-apollo.njk`
**Slug:** `warmly-vs-apollo`
**Search intent:** "warmly vs apollo" — teams evaluating intent data vs outbound prospecting

```yaml
toolA:
  name: "Warmly"
  orgScore: 65
  repScore: 45
  verdict: "Best for RevOps teams that want to identify and act on website visitor intent"
  startingPrice: "$700/mo"
  ctaUrl: "/go/warmly"
  reviewUrl: "/tools/warmly-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for outbound prospecting with built-in sequences and a large contact database"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "warmly-vs-leadfeeder.html"
    label: "Warmly vs Leadfeeder"
  - url: "apollo-vs-zoominfo.html"
    label: "Apollo.io vs ZoomInfo"
  - url: "clay-vs-apollo.html"
    label: "Clay vs Apollo.io"
```

FAQs:
1. "Are Warmly and Apollo solving the same problem?" — No. Apollo is an outbound prospecting tool — you build lists and send cold emails. Warmly is an inbound intent tool — it identifies companies already visiting your website and alerts your team. They complement each other rather than compete directly.
2. "Is Warmly worth $700/mo?" — For teams with meaningful website traffic (500+ target account visits/month), Warmly can surface high-intent leads that would otherwise go unnoticed. For teams with low website traffic or no inbound motion, the ROI is harder to justify at this price point.
3. "Can I use Warmly with Apollo?" — Yes. A common workflow is using Warmly to identify high-intent website visitors, then using Apollo to find contact details and enrich the account before reaching out. Warmly's Salesforce and HubSpot integrations make this handoff straightforward.

---

## Session 2 — Sales Engagement & Email Comparisons (7 pages)

### 8. `outreach-vs-hubspot.njk`
**Slug:** `outreach-vs-hubspot`
**Search intent:** "outreach vs hubspot sales" — teams choosing between dedicated SEP and CRM-native sequences

```yaml
toolA:
  name: "Outreach"
  orgScore: 73
  repScore: 53
  verdict: "Best for enterprise sales teams that need advanced sequence automation"
  startingPrice: "Custom"
  ctaUrl: "/go/outreach"
  reviewUrl: "/tools/outreach-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want CRM and sequences in one platform"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "outreach-vs-salesloft.html"
    label: "Outreach vs Salesloft"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
  - url: "salesloft-vs-klenty.html"
    label: "Salesloft vs Klenty"
```

FAQs:
1. "Is Outreach better than HubSpot for sales sequences?" — For complex, high-volume outbound sequences, Outreach is more powerful — it offers A/B testing, advanced branching logic, and deeper analytics than HubSpot's sequences. HubSpot's sequences are sufficient for most inbound-led teams but lack Outreach's sophistication.
2. "Does HubSpot replace the need for Outreach?" — For teams with a primarily inbound motion, HubSpot's Sales Hub can replace Outreach. For enterprise teams running high-volume outbound with complex multi-channel sequences, Outreach's dedicated SEP capabilities are hard to replicate in HubSpot.
3. "Which is easier to set up?" — HubSpot is significantly easier to set up and administer. Outreach requires dedicated RevOps resources for configuration, sequence governance, and ongoing maintenance. HubSpot's sequences can be live within hours; Outreach typically takes weeks to configure properly.

---

### 9. `salesloft-vs-hubspot.njk`
**Slug:** `salesloft-vs-hubspot`
**Search intent:** "salesloft vs hubspot" — teams evaluating SEP vs CRM-native

```yaml
toolA:
  name: "Salesloft"
  orgScore: 70
  repScore: 56
  verdict: "Best for enterprise teams that need revenue workflow automation"
  startingPrice: "Custom"
  ctaUrl: "/go/salesloft"
  reviewUrl: "/tools/salesloft-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want CRM and sequences in one platform"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "outreach-vs-salesloft.html"
    label: "Outreach vs Salesloft"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
  - url: "salesloft-vs-klenty.html"
    label: "Salesloft vs Klenty"
```

FAQs:
1. "Does Salesloft work with HubSpot?" — Yes, Salesloft has a native HubSpot integration. Many teams use HubSpot as their CRM and Salesloft as their sales engagement platform, syncing activities, contacts, and deal stages bidirectionally.
2. "Is Salesloft or HubSpot better for a 20-person sales team?" — It depends on the motion. If the team is primarily inbound, HubSpot Sales Hub Professional handles sequences and pipeline management well. If the team runs significant outbound, Salesloft's cadence management and coaching features justify the additional cost.
3. "Which has better call recording?" — Salesloft's Conversations product includes call recording, AI transcription, and coaching features. HubSpot's call recording is more basic and lacks the coaching layer. For teams that prioritize call intelligence, Salesloft is the stronger choice.

---

### 10. `instantly-vs-apollo.njk`
**Slug:** `instantly-vs-apollo`
**Search intent:** "instantly vs apollo" — cold email teams evaluating tools

```yaml
toolA:
  name: "Instantly"
  orgScore: 63
  repScore: 70
  verdict: "Best for high-volume cold email with unlimited mailbox warmup"
  startingPrice: "$37/mo"
  ctaUrl: "/go/instantly"
  reviewUrl: "/tools/instantly-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for all-in-one prospecting, data, and email sequences"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "instantly-vs-smartlead.html"
    label: "Instantly vs Smartlead"
  - url: "instantly-vs-lemlist.html"
    label: "Instantly vs Lemlist"
  - url: "clay-vs-apollo.html"
    label: "Clay vs Apollo.io"
```

FAQs:
1. "Is Instantly or Apollo better for cold email?" — Instantly is purpose-built for cold email at scale — unlimited mailboxes, built-in warmup, and deliverability-first design. Apollo's sequences are solid but secondary to its prospecting database. For teams whose primary workflow is cold email volume, Instantly is the stronger choice.
2. "Does Apollo have unlimited mailboxes like Instantly?" — No. Apollo limits the number of sending accounts per plan. Instantly's Growth plan allows unlimited email accounts, which is a significant advantage for teams running high-volume cold email campaigns across multiple domains.
3. "Can I use Instantly and Apollo together?" — Yes, this is a popular stack. Use Apollo to build and enrich prospect lists, then export to Instantly for sending. Apollo's CSV export makes this workflow straightforward, though it requires manual transfer rather than a native integration.

---

### 11. `smartlead-vs-instantly.njk`

**Note:** `instantly-vs-smartlead.njk` already exists. This is the reverse pairing — Smartlead as toolA. Skip this one and replace with `vidyard-vs-loom.njk` below.

### 11. `vidyard-vs-loom.njk`
**Slug:** `vidyard-vs-loom`
**Search intent:** "vidyard vs loom" — reps choosing async video tools

```yaml
toolA:
  name: "Vidyard"
  orgScore: 62
  repScore: 70
  verdict: "Best for sales reps who want video analytics and CRM integration"
  startingPrice: "$19/mo"
  ctaUrl: "/go/vidyard"
  reviewUrl: "/tools/vidyard-review.html"
toolB:
  name: "Loom"
  orgScore: 55
  repScore: 72
  verdict: "Best for quick async video sharing across any team function"
  startingPrice: "$12.50/mo"
  ctaUrl: "/go/loom"
  reviewUrl: "/tools/index.html"
relatedComparisons:
  - url: "vidyard-vs-heygen.html"
    label: "Vidyard vs HeyGen"
  - url: "lavender-vs-instantly.html"
    label: "Lavender vs Instantly"
  - url: "instantly-vs-lemlist.html"
    label: "Instantly vs Lemlist"
```

FAQs:
1. "Is Vidyard or Loom better for sales outreach?" — Vidyard is purpose-built for sales — it includes CRM integrations (Salesforce, HubSpot, Outreach), viewer analytics showing who watched and for how long, and a sales-specific Chrome extension. Loom is a general-purpose async video tool that lacks the sales-specific analytics and CRM integrations.
2. "Does Loom integrate with Salesforce?" — Loom has limited Salesforce integration compared to Vidyard. Vidyard's Salesforce integration logs video views as activities, tracks engagement per contact, and surfaces this data in the CRM. Loom's Salesforce integration is primarily for sharing links, not tracking engagement.
3. "Which is cheaper?" — Loom's Starter plan is $12.50/mo vs Vidyard's $19/mo. Both have free tiers. For teams that only need basic async video without sales-specific analytics, Loom's lower price point is attractive. For sales teams that need CRM-integrated view tracking, Vidyard's premium is justified.

---

### 12. `lavender-vs-apollo.njk`
**Slug:** `lavender-vs-apollo`
**Search intent:** "lavender vs apollo email" — reps choosing email writing tools

```yaml
toolA:
  name: "Lavender"
  orgScore: 63
  repScore: 79
  verdict: "Best for reps who want real-time AI coaching on email quality"
  startingPrice: "$29/mo"
  ctaUrl: "/go/lavender"
  reviewUrl: "/tools/lavender-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for all-in-one prospecting, sequences, and AI email generation"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "lavender-vs-instantly.html"
    label: "Lavender vs Instantly"
  - url: "lavender-vs-autobound.html"
    label: "Lavender vs Autobound"
  - url: "instantly-vs-apollo.html"
    label: "Instantly vs Apollo.io"
```

FAQs:
1. "Does Apollo have an AI email writer like Lavender?" — Apollo has AI email generation that writes first drafts. Lavender's approach is different — it coaches you on emails you've already written, scoring them in real time and suggesting specific improvements. Lavender is a writing coach; Apollo is a writing generator.
2. "Can I use Lavender with Apollo sequences?" — Yes. Lavender works as a Chrome extension inside Gmail and most SEPs. You can write emails in Apollo's sequence editor and use Lavender's sidebar to score and improve them before sending.
3. "Which is better for improving reply rates?" — Lavender's real-time coaching approach is specifically designed to improve reply rates — it scores emails against patterns from millions of sent emails. Apollo's AI generation is faster but doesn't provide the same feedback loop. Teams focused on email quality often use both.

---

### 13. `gong-vs-salesloft.njk`
**Slug:** `gong-vs-salesloft`
**Search intent:** "gong vs salesloft" — managers choosing between conversation intelligence and SEP

```yaml
toolA:
  name: "Gong"
  orgScore: 78
  repScore: 63
  verdict: "Best for sales managers who need deep call intelligence and deal risk signals"
  startingPrice: "Custom"
  ctaUrl: "/go/gong"
  reviewUrl: "/tools/gong-review.html"
toolB:
  name: "Salesloft"
  orgScore: 70
  repScore: 56
  verdict: "Best for enterprise teams that need revenue workflow automation and cadences"
  startingPrice: "Custom"
  ctaUrl: "/go/salesloft"
  reviewUrl: "/tools/salesloft-review.html"
relatedComparisons:
  - url: "outreach-vs-salesloft.html"
    label: "Outreach vs Salesloft"
  - url: "gong-vs-chorus.html"
    label: "Gong vs Chorus"
  - url: "gong-vs-avoma.html"
    label: "Gong vs Avoma"
```

FAQs:
1. "Is Gong or Salesloft better for sales coaching?" — Gong is the stronger coaching tool. Its AI analyzes call recordings for talk ratios, filler words, competitor mentions, and deal risk signals, then surfaces coaching recommendations. Salesloft's Conversations product includes call recording but lacks Gong's depth of AI analysis.
2. "Do Gong and Salesloft compete or complement each other?" — They overlap on call recording but compete on positioning. Many enterprise teams use both: Salesloft for cadence management and rep workflow, Gong for call intelligence and manager coaching. The combination is expensive but covers the full revenue workflow.
3. "Which is better for forecasting?" — Gong's Revenue Intelligence product includes AI-powered forecasting. Salesloft's forecasting is less developed. For teams that prioritize forecast accuracy, Gong or Clari are stronger choices than Salesloft.

---

### 14. `gong-vs-clari.njk`
**Slug:** `gong-vs-clari`
**Search intent:** "gong vs clari" — revenue leaders choosing between call intelligence and forecasting

```yaml
toolA:
  name: "Gong"
  orgScore: 78
  repScore: 63
  verdict: "Best for call intelligence, deal risk signals, and rep coaching"
  startingPrice: "Custom"
  ctaUrl: "/go/gong"
  reviewUrl: "/tools/gong-review.html"
toolB:
  name: "Clari"
  orgScore: 72
  repScore: 55
  verdict: "Best for AI-powered pipeline forecasting and revenue cadence management"
  startingPrice: "Custom"
  ctaUrl: "/go/clari"
  reviewUrl: "/tools/clari-review.html"
relatedComparisons:
  - url: "boostup-vs-clari.html"
    label: "Boostup vs Clari"
  - url: "clari-vs-aviso.html"
    label: "Clari vs Aviso"
  - url: "gong-vs-chorus.html"
    label: "Gong vs Chorus"
```

FAQs:
1. "Is Gong or Clari better for sales forecasting?" — Clari is purpose-built for forecasting — its AI models are specifically trained on pipeline data to predict deal outcomes. Gong's forecasting is a secondary feature added to its call intelligence core. For teams where forecast accuracy is the primary need, Clari is the stronger choice.
2. "Do Gong and Clari integrate with each other?" — Yes, Gong and Clari have a native integration. Many enterprise revenue teams use both: Gong for call intelligence and coaching, Clari for pipeline management and forecasting. The integration passes deal activity signals from Gong into Clari's forecasting models.
3. "Which is more expensive?" — Both are enterprise-only with custom pricing. Gong is typically priced per seat for call recording plus a platform fee; Clari is typically priced per seat for the full platform. Most enterprises report similar total cost, though Gong's pricing scales more predictably with seat count.

---

## Session 3 — Enablement & Coaching Comparisons (7 pages)

### 15. `seismic-vs-showpad.njk`
**Slug:** `seismic-vs-showpad`
**Search intent:** "seismic vs showpad" — enterprise enablement platform evaluation

```yaml
toolA:
  name: "Seismic"
  orgScore: 74
  repScore: 58
  verdict: "Best for large enterprises that need content governance and compliance"
  startingPrice: "Custom"
  ctaUrl: "/go/seismic"
  reviewUrl: "/tools/seismic-review.html"
toolB:
  name: "Showpad"
  orgScore: 68
  repScore: 60
  verdict: "Best for mid-market teams that want easier implementation than Seismic"
  startingPrice: "Custom"
  ctaUrl: "/go/showpad"
  reviewUrl: "/tools/index.html"
relatedComparisons:
  - url: "seismic-vs-highspot.html"
    label: "Seismic vs Highspot"
  - url: "highspot-vs-showpad.html"
    label: "Highspot vs Showpad"
  - url: "mindtickle-vs-allego.html"
    label: "MindTickle vs Allego"
```

FAQs:
1. "Is Seismic or Showpad easier to implement?" — Showpad is generally faster to implement. Seismic's full deployment typically takes 3–6 months with dedicated implementation resources. Showpad can be operational in 4–8 weeks for mid-market teams. The tradeoff is that Seismic's governance and compliance features are more robust at scale.
2. "Which is better for regulated industries?" — Seismic is the stronger choice for regulated industries (financial services, healthcare, pharma). Its content compliance controls, audit trails, and approval workflows are purpose-built for environments where content accuracy is a legal requirement.
3. "Do Seismic and Showpad compete on price?" — Both are enterprise-only with custom pricing. Showpad is generally positioned as more accessible for mid-market ($500–1,000/seat/year range), while Seismic targets large enterprise with higher price points. Neither publishes pricing publicly.

---

### 16. `highspot-vs-mindtickle.njk`
**Slug:** `highspot-vs-mindtickle`
**Search intent:** "highspot vs mindtickle" — enablement vs readiness platform comparison

```yaml
toolA:
  name: "Highspot"
  orgScore: 72
  repScore: 60
  verdict: "Best for teams that need content management and rep readiness in one platform"
  startingPrice: "Custom"
  ctaUrl: "/go/highspot"
  reviewUrl: "/tools/highspot-review.html"
toolB:
  name: "MindTickle"
  orgScore: 68
  repScore: 55
  verdict: "Best for enterprise teams that prioritize structured onboarding and coaching"
  startingPrice: "Custom"
  ctaUrl: "/go/mindtickle"
  reviewUrl: "/tools/mindtickle-review.html"
relatedComparisons:
  - url: "seismic-vs-highspot.html"
    label: "Seismic vs Highspot"
  - url: "highspot-vs-showpad.html"
    label: "Highspot vs Showpad"
  - url: "mindtickle-vs-allego.html"
    label: "MindTickle vs Allego"
```

FAQs:
1. "Is Highspot or MindTickle better for sales onboarding?" — MindTickle is more focused on structured onboarding and certification. Its Mission feature for practice pitches and AI-scored role plays is specifically designed for onboarding new reps. Highspot covers onboarding but is more balanced between content management and readiness.
2. "Which has better AI features?" — Both have AI features, but they serve different purposes. MindTickle's Call AI scores recorded calls against custom rubrics. Highspot's Copilot AI recommends relevant content based on deal stage and buyer persona. The better choice depends on whether your priority is coaching or content recommendations.
3. "Can a team use both Highspot and MindTickle?" — Some large enterprises use both — Highspot for content management and Seismic-style governance, MindTickle for structured coaching and certification. This is expensive and typically only justified at 200+ rep scale where the two use cases are clearly separated.

---

### 17. `clari-vs-gong-revenue.njk`

**Note:** This would duplicate `gong-vs-clari.njk` from Session 2. Replace with `chili-piper-vs-hubspot.njk`.

### 17. `chili-piper-vs-hubspot.njk`
**Slug:** `chili-piper-vs-hubspot`
**Search intent:** "chili piper vs hubspot meetings" — teams evaluating scheduling tools

```yaml
toolA:
  name: "Chili Piper"
  orgScore: 70
  repScore: 65
  verdict: "Best for inbound lead routing and instant meeting booking from web forms"
  startingPrice: "$22.50/seat/mo"
  ctaUrl: "/go/chili-piper"
  reviewUrl: "/tools/chili-piper-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want scheduling built into their CRM"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "calendly-vs-chili-piper.html"
    label: "Calendly vs Chili Piper"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
  - url: "outreach-vs-hubspot.html"
    label: "Outreach vs HubSpot"
```

FAQs:
1. "Does HubSpot have meeting scheduling like Chili Piper?" — HubSpot includes a meetings tool that allows prospects to book time directly from a link. Chili Piper's Concierge product goes further — it routes inbound form submissions to the right rep in real time and books the meeting instantly, reducing time-to-meeting from hours to seconds.
2. "Is Chili Piper worth the cost if I already have HubSpot?" — For teams with significant inbound volume (100+ form fills/month), Chili Piper's instant routing typically improves lead-to-meeting conversion rates enough to justify the additional cost. For teams with low inbound volume, HubSpot's built-in scheduling is sufficient.
3. "Does Chili Piper integrate with HubSpot?" — Yes, Chili Piper has a deep HubSpot integration. It reads HubSpot form submissions, applies routing logic, and writes meeting data back to HubSpot contacts and deals. This is one of Chili Piper's most common deployment patterns.

---

### 18. `gong-vs-outreach.njk`
**Slug:** `gong-vs-outreach`
**Search intent:** "gong vs outreach" — enterprise teams evaluating call intelligence vs SEP

```yaml
toolA:
  name: "Gong"
  orgScore: 78
  repScore: 63
  verdict: "Best for call intelligence, deal risk signals, and revenue forecasting"
  startingPrice: "Custom"
  ctaUrl: "/go/gong"
  reviewUrl: "/tools/gong-review.html"
toolB:
  name: "Outreach"
  orgScore: 73
  repScore: 53
  verdict: "Best for enterprise sales teams that need advanced sequence automation"
  startingPrice: "Custom"
  ctaUrl: "/go/outreach"
  reviewUrl: "/tools/outreach-review.html"
relatedComparisons:
  - url: "outreach-vs-salesloft.html"
    label: "Outreach vs Salesloft"
  - url: "gong-vs-salesloft.html"
    label: "Gong vs Salesloft"
  - url: "gong-vs-chorus.html"
    label: "Gong vs Chorus"
```

FAQs:
1. "Do Gong and Outreach compete or complement each other?" — They complement each other. Outreach manages rep workflows and sequences; Gong analyzes what happens on calls and surfaces deal risk. Most enterprise teams use both: Outreach for execution, Gong for intelligence and coaching.
2. "Does Outreach have call recording like Gong?" — Outreach has a call recording feature (Outreach Kaia), but it is less sophisticated than Gong's AI analysis. Gong's call intelligence — talk ratios, sentiment analysis, competitor mentions, deal risk signals — is significantly deeper than Outreach's native recording.
3. "Which should I buy first?" — For most teams, Outreach (or Salesloft) comes first as the foundation for rep workflow. Gong is typically added once the team is running sequences consistently and managers want visibility into call quality and deal health.

---

### 19. `zoominfo-vs-apollo.njk`

**Note:** `apollo-vs-zoominfo.njk` already exists. Replace with `seismic-vs-mindtickle.njk`.

### 19. `seismic-vs-mindtickle.njk`
**Slug:** `seismic-vs-mindtickle`
**Search intent:** "seismic vs mindtickle" — enterprise enablement platform evaluation

```yaml
toolA:
  name: "Seismic"
  orgScore: 74
  repScore: 58
  verdict: "Best for large enterprises that need content governance and compliance"
  startingPrice: "Custom"
  ctaUrl: "/go/seismic"
  reviewUrl: "/tools/seismic-review.html"
toolB:
  name: "MindTickle"
  orgScore: 68
  repScore: 55
  verdict: "Best for enterprise teams that prioritize structured sales coaching and readiness"
  startingPrice: "Custom"
  ctaUrl: "/go/mindtickle"
  reviewUrl: "/tools/mindtickle-review.html"
relatedComparisons:
  - url: "seismic-vs-highspot.html"
    label: "Seismic vs Highspot"
  - url: "highspot-vs-mindtickle.html"
    label: "Highspot vs MindTickle"
  - url: "mindtickle-vs-allego.html"
    label: "MindTickle vs Allego"
```

FAQs:
1. "Is Seismic or MindTickle better for a new sales enablement program?" — They solve different problems. Seismic is a content management platform — it helps reps find and share the right content at the right time. MindTickle is a readiness platform — it trains reps and certifies their knowledge. Most mature enablement programs need both.
2. "Which integrates better with Salesforce?" — Both have strong Salesforce integrations. Seismic's integration focuses on surfacing content recommendations within Salesforce opportunities. MindTickle's integration focuses on triggering training based on deal stage or rep performance data in Salesforce.
3. "Can a mid-market company afford Seismic?" — Seismic is primarily positioned for large enterprise (500+ employees). Mid-market teams often find Highspot or Showpad more accessible in terms of implementation complexity and pricing. MindTickle has more mid-market deployments than Seismic.

---

### 20. `clari-vs-hubspot.njk`
**Slug:** `clari-vs-hubspot`
**Search intent:** "clari vs hubspot forecasting" — teams evaluating forecasting tools

```yaml
toolA:
  name: "Clari"
  orgScore: 72
  repScore: 55
  verdict: "Best for enterprise teams that need AI-powered pipeline forecasting"
  startingPrice: "Custom"
  ctaUrl: "/go/clari"
  reviewUrl: "/tools/clari-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want CRM and forecasting in one platform"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "clari-vs-aviso.html"
    label: "Clari vs Aviso"
  - url: "boostup-vs-clari.html"
    label: "Boostup vs Clari"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
```

FAQs:
1. "Does HubSpot have forecasting like Clari?" — HubSpot has a forecasting tool built into Sales Hub that shows pipeline by deal stage and weighted probability. Clari's AI forecasting is significantly more sophisticated — it analyzes CRM activity, email engagement, and historical patterns to predict deal outcomes with higher accuracy.
2. "Is Clari worth the cost if I already have HubSpot?" — For teams with 20+ reps and $5M+ in pipeline, Clari's forecast accuracy improvements typically justify the cost. For smaller teams, HubSpot's built-in forecasting is sufficient and Clari's enterprise pricing is hard to justify.
3. "Does Clari integrate with HubSpot?" — Yes, Clari has a HubSpot integration. It pulls deal and activity data from HubSpot into its forecasting models. This is less common than Clari's Salesforce integration but is supported for HubSpot-native teams.

---

### 21. `gong-vs-hubspot.njk`
**Slug:** `gong-vs-hubspot`
**Search intent:** "gong vs hubspot" — teams evaluating call intelligence vs CRM-native recording

```yaml
toolA:
  name: "Gong"
  orgScore: 78
  repScore: 63
  verdict: "Best for sales managers who need deep call intelligence and deal risk signals"
  startingPrice: "Custom"
  ctaUrl: "/go/gong"
  reviewUrl: "/tools/gong-review.html"
toolB:
  name: "HubSpot"
  orgScore: 74
  repScore: 72
  verdict: "Best for inbound-led teams that want CRM, sequences, and call recording in one platform"
  startingPrice: "$20/seat/mo"
  ctaUrl: "/go/hubspot"
  reviewUrl: "/tools/hubspot-review.html"
relatedComparisons:
  - url: "gong-vs-chorus.html"
    label: "Gong vs Chorus"
  - url: "gong-vs-salesloft.html"
    label: "Gong vs Salesloft"
  - url: "hubspot-vs-pipedrive.html"
    label: "HubSpot vs Pipedrive"
```

FAQs:
1. "Does HubSpot have call recording like Gong?" — HubSpot Sales Hub includes call recording and basic transcription. Gong's AI analysis is far more sophisticated — it surfaces talk ratios, competitor mentions, deal risk signals, and coaching recommendations that HubSpot's recording does not provide.
2. "Is Gong worth the cost if I already have HubSpot?" — For teams with 10+ reps where call quality and deal health visibility are priorities, Gong's intelligence layer typically justifies the cost. For smaller teams or teams with primarily inbound motion, HubSpot's built-in recording is sufficient.
3. "Which is better for a VP of Sales?" — A VP of Sales benefits more from Gong — it provides deal risk alerts, forecast signals, and rep coaching data that HubSpot's CRM view doesn't surface. HubSpot is better for the CRM and pipeline management layer that a VP also needs, which is why many teams use both.

---

## Session 4 — PR + Validation (15 min)

1. Run `npx @11ty/eleventy --quiet` — must be 0 errors, ~101 files (80 existing + 21 new)
2. Verify all 21 new comparison pages exist in `_site/compare/`
3. Spot-check 3 pages: confirm `compare-hero`, dual score cards, and `related-comparisons` section all render
4. Verify no `reviewUrl` points to `/tools/index.html` for any tool that now has a dedicated review page
5. Open PR titled: `feat(content): Phase 6 — 21 Tier 2 comparison pages`
6. **Do NOT merge** — Manus reviews and merges

---

## Important Notes for Claude Code

**File naming:** Use lowercase with hyphens. `apollo-vs-hubspot.njk`, not `ApolloVsHubspot.njk`.

**Permalink:** Must match the filename exactly. `permalink: compare/apollo-vs-hubspot.html`

**Body content:** Leave the file body empty after the closing `---`. The `compare.njk` template generates all content from frontmatter. Do not add HTML or Markdown after the frontmatter.

**Loom and Showpad scores:** These tools do not have dedicated review pages on SalesAIGuide yet. Use `reviewUrl: "/tools/index.html"` for them and the scores provided in the frontmatter specs above.

**`/go/` redirects for new tools:** Add these to `_redirects` if they don't exist:
- `/go/loom` → `https://loom.com`
- `/go/showpad` → `https://showpad.com`
- `/go/chili-piper` → `https://chilipiper.com`

These are placeholder URLs until affiliate programs are established.

**Total pages to build:** 21 (pages 11 and 17 in the brief had duplicates replaced — the final list is: apollo-vs-hubspot, cognism-vs-apollo, lusha-vs-zoominfo, leadiq-vs-apollo, clay-vs-zoominfo, cognism-vs-lusha, warmly-vs-apollo, outreach-vs-hubspot, salesloft-vs-hubspot, instantly-vs-apollo, vidyard-vs-loom, lavender-vs-apollo, gong-vs-salesloft, gong-vs-clari, seismic-vs-showpad, highspot-vs-mindtickle, chili-piper-vs-hubspot, gong-vs-outreach, seismic-vs-mindtickle, clari-vs-hubspot, gong-vs-hubspot)

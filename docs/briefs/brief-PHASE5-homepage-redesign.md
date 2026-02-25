# Phase 5 Brief — Persona Hubs + Homepage Redesign

## Context

Read `CLAUDE.md` and `MANUS_CONTEXT.md` before starting.

**What exists now:**
- Homepage (`index.njk`) uses `base.njk` layout — functional but generic, no persona targeting, no methodology trust bar, no stats bar
- No persona hub pages exist (`/for-sales-reps/`, `/for-sales-managers/`, `/for-revenue-ops/`)
- All 10 tool pages have `personaTags` in their JSON: `personal-friendly`, `requires-admin`, `enterprise-grade`, `low-cost`, `chrome-extension`
- Tool scores exist in `_data/tools/*.json` as `scores.org.value` and `scores.rep.value`

**What Phase 5 delivers:**
1. A `persona.njk` layout for the 3 persona hub pages
2. Three persona hub pages: `for-sales-reps.njk`, `for-sales-managers.njk`, `for-revenue-ops.njk`
3. A redesigned homepage (`index.njk`) with v4 visual quality: asymmetric hero, stats bar, methodology trust bar, persona entry points
4. CSS additions to `css/main.css` for new components

**Branch strategy:** All work on `phase5-homepage-redesign` branch. Open PR when done. Do NOT merge — Manus reviews and merges.

---

## Session 1 — Persona Layout + 3 Persona Hub Pages (60 min)

### Branch setup

```bash
git checkout main && git pull origin main
git checkout -b phase5-homepage-redesign
```

### Create `_layouts/persona.njk`

```njk
---
layout: base.njk
---
<main class="persona-page">
  <section class="persona-hero">
    <div class="container">
      <div class="persona-hero-inner">
        <div class="persona-badge">{{ badge }}</div>
        <h1>{{ title | replace(" | Sales AI Guide", "") }}</h1>
        <p class="persona-lead">{{ lead }}</p>
        <div class="persona-meta">
          <span>{{ toolCount }} tools curated for this role</span>
          <span>Updated {{ updated | default("Feb 2026") }}</span>
        </div>
      </div>
    </div>
  </section>
  <div class="container">
    <div class="persona-layout">
      <main class="persona-main">
        {{ content | safe }}
      </main>
      <aside class="persona-sidebar">
        <div class="sidebar-box">
          <h3>Quick Stack</h3>
          {% for pick in quickStack %}
          <div class="sidebar-pick">
            <div class="sidebar-pick-rank">#{{ loop.index }}</div>
            <div class="sidebar-pick-info">
              <strong>{{ pick.name }}</strong>
              <span>{{ pick.tagline }}</span>
            </div>
            <a href="{{ pick.ctaUrl }}" class="btn btn-sm btn-primary" target="_blank" rel="noopener sponsored">Visit &#8599;</a>
          </div>
          {% endfor %}
        </div>
        <div class="sidebar-box">
          <h3>Other Roles</h3>
          <a href="/for-sales-reps/" class="persona-nav-link">For Sales Reps &#8250;</a>
          <a href="/for-sales-managers/" class="persona-nav-link">For Sales Managers &#8250;</a>
          <a href="/for-revenue-ops/" class="persona-nav-link">For Revenue Ops &#8250;</a>
        </div>
        <div class="sidebar-box sidebar-newsletter">
          <h3>Get the Weekly Brief</h3>
          <p>New tool reviews and comparisons, every Tuesday.</p>
          <form name="newsletter" method="POST" data-netlify="true" netlify-honeypot="bot-field">
            <input type="hidden" name="form-name" value="newsletter" />
            <input type="hidden" name="bot-field" />
            <input type="email" name="email" placeholder="your@email.com" required />
            <button type="submit" class="btn btn-primary btn-block">Subscribe</button>
          </form>
        </div>
      </aside>
    </div>
  </div>
</main>
```

---

### Create `for-sales-reps.njk`

```njk
---
layout: persona.njk
title: "Best AI Sales Tools for Sales Reps 2026 | Sales AI Guide"
description: "Curated AI sales tools for individual contributors: cold email, prospecting, email writing, and pipeline tools that reps can set up and use independently."
canonicalUrl: "https://salesaiguide.com/for-sales-reps/"
permalink: for-sales-reps/index.html
badge: "For Sales Reps"
lead: "Tools individual contributors can buy, set up, and use without waiting for IT or RevOps approval."
toolCount: 5
updated: "Feb 2026"
quickStack:
  - name: "Apollo.io"
    tagline: "Find leads + send sequences"
    ctaUrl: "/go/apollo"
  - name: "Lavender"
    tagline: "Write better cold emails"
    ctaUrl: "/go/lavender"
  - name: "Instantly"
    tagline: "Scale cold outreach"
    ctaUrl: "/go/instantly"
---

## The Rep's Toolkit

Sales reps need tools they can start using in a day — no IT ticket, no admin approval, no six-month rollout. The tools below are rated by **Rep Score** (individual value), not Org Score (enterprise fit). They are low-cost, self-serve, and built for individual contributors.

### What to Look For

The key filter for rep-friendly tools is the `Rep Score` — our measure of how much value an individual contributor gets from a tool, independent of whether their company has bought it. High Rep Score tools tend to share three traits: they have a free tier or low starting price (under $50/month), they work as Chrome extensions or standalone apps without CRM integration, and they show value within the first week of use.

### Top 5 Tools for Sales Reps

**1. Lavender — AI Email Coach (Rep Score: 79)**

Lavender is the highest Rep Score tool in our dataset. It works as a Chrome extension inside Gmail and Outlook, scores your cold emails in real time, and suggests improvements. No admin approval needed. The free plan covers 5 emails per month; the Individual plan is $29/month. Best for reps who write their own cold outreach and want immediate feedback on open rate and reply rate predictors.

[Read the full Lavender review →](/tools/lavender-review.html)

**2. Apollo.io — All-in-One Prospecting (Rep Score: 72)**

Apollo gives individual reps access to a 275M+ contact database, built-in email sequences, and a Chrome extension for LinkedIn prospecting — all starting at $49/month. The free plan includes 50 email credits per month. Unlike ZoomInfo or Clay, Apollo is genuinely self-serve: a rep can sign up, find leads, and send a sequence in the same afternoon. Best for reps who need to build their own pipeline without a dedicated SDR.

[Read the full Apollo review →](/tools/apollo-review.html)

**3. Instantly.ai — Cold Email at Scale (Rep Score: 70)**

Instantly is built for cold email volume. Unlimited sending accounts, built-in email warmup, and a unified inbox for managing replies. At $37/month, it is the lowest-cost option for reps running their own outbound. The tradeoff: it is email-only (no LinkedIn, no calling), and setup requires connecting your own email domain. Best for reps who have a domain and want to send 500+ cold emails per week.

[Read the full Instantly review →](/tools/instantly-review.html)

**4. HubSpot CRM — Free Pipeline Tracking (Rep Score: 72)**

HubSpot's free CRM is the most rep-friendly pipeline tool available. Reps can track deals, log calls, set follow-up reminders, and use email templates without paying anything. The free tier is genuinely useful — not a crippled trial. Best for reps at companies without a CRM, or reps who want to track their own pipeline independently of the company's Salesforce instance.

[Read the full HubSpot review →](/tools/hubspot-review.html)

**5. Smartlead — Cold Email Alternative (Rep Score: 64)**

Smartlead is a strong Instantly alternative with slightly better deliverability features and a more flexible pricing structure. Starting at $39/month. Best for reps who have tried Instantly and want to compare deliverability, or who need more advanced inbox rotation.

[Read the full Smartlead review →](/tools/smartlead-review.html)

---

### What to Avoid as a Rep

Tools with `Requires Admin` or `Enterprise Grade` tags are not built for individual use. Clay ($149/month, requires RevOps setup), Gong (custom pricing, requires admin), Outreach (custom pricing, requires IT), and ZoomInfo (custom pricing, requires procurement) are all tools that your company buys for you — not tools you buy for yourself.

---

### Recommended Starting Stack

For a rep with a $100/month personal budget:

| Tool | Purpose | Cost |
|---|---|---|
| Apollo.io | Lead database + sequences | $49/month |
| Lavender | Email writing coach | $29/month |
| HubSpot CRM | Pipeline tracking | Free |

Total: $78/month. This stack covers prospecting, outreach, and pipeline tracking — the full individual contributor workflow.

---

### Related Pages

- [Best Cold Email Software 2026](/guides/best-cold-email-tools.html)
- [Best AI SDR Tools 2026](/guides/best-ai-sdr-tools.html)
- [Instantly vs Smartlead comparison](/compare/instantly-vs-smartlead.html)
- [Apollo vs ZoomInfo comparison](/compare/apollo-vs-zoominfo.html)
```

---

### Create `for-sales-managers.njk`

```njk
---
layout: persona.njk
title: "Best AI Sales Tools for Sales Managers 2026 | Sales AI Guide"
description: "AI sales tools for sales managers: coaching, pipeline visibility, forecasting, and engagement platforms that give managers insight into team performance."
canonicalUrl: "https://salesaiguide.com/for-sales-managers/"
permalink: for-sales-managers/index.html
badge: "For Sales Managers"
lead: "Tools that give managers visibility into rep activity, call quality, pipeline health, and forecast accuracy."
toolCount: 5
updated: "Feb 2026"
quickStack:
  - name: "Gong"
    tagline: "Call intelligence + coaching"
    ctaUrl: "/go/gong"
  - name: "Salesloft"
    tagline: "Team engagement + pipeline"
    ctaUrl: "/go/salesloft"
  - name: "HubSpot"
    tagline: "Pipeline + forecasting"
    ctaUrl: "/go/hubspot"
---

## The Manager's Toolkit

Sales managers need different tools than reps. Where reps need self-serve tools they can use independently, managers need visibility: into rep activity, call quality, pipeline health, and forecast accuracy. The tools below are rated by **Org Score** (organizational value) — our measure of how much value a tool delivers at the team or company level.

### What to Look For

Manager-oriented tools tend to be higher cost (custom pricing or $100+/user/month), require admin setup, and deliver value through analytics dashboards, coaching workflows, and CRM integrations rather than individual productivity. The key question for managers is: does this tool give me signal I cannot get from my CRM alone?

### Top 5 Tools for Sales Managers

**1. Gong — Conversation Intelligence (Org Score: 78)**

Gong is the category leader for conversation intelligence. It records, transcribes, and analyzes every sales call, then surfaces coaching insights, deal risks, and forecast signals. Managers use Gong to review calls without listening to them in full, identify which reps need coaching on specific objection types, and track deal health based on conversation patterns. Custom pricing (typically $1,200–$1,600/user/year). Requires admin setup and CRM integration.

[Read the full Gong review →](/tools/gong-review.html)

**2. Outreach — Sales Engagement Platform (Org Score: 73)**

Outreach is the most widely deployed sales engagement platform for mid-market and enterprise teams. Managers use it to build standardized sequences for the team, track sequence performance across reps, and enforce consistent outreach cadences. The analytics layer shows which sequences convert, which reps follow the playbook, and where deals stall. Custom pricing. Requires IT and CRM integration.

[Read the full Outreach review →](/tools/outreach-review.html)

**3. Salesloft — Sales Engagement Alternative (Org Score: 70)**

Salesloft competes directly with Outreach and is often preferred by teams that prioritize coaching workflows over sequence analytics. The Coaching feature set is stronger than Outreach's equivalent. Custom pricing. Requires admin setup.

[Read the full Salesloft review →](/tools/salesloft-review.html)

**4. HubSpot — CRM + Pipeline (Org Score: 74)**

For managers at companies without Salesforce, HubSpot's Sales Hub provides pipeline management, forecasting, and basic sequence tools in one platform. The Professional tier ($100/user/month) includes deal forecasting, pipeline automation, and team performance dashboards. Best for managers at SMBs who want a single platform rather than a CRM plus a separate engagement tool.

[Read the full HubSpot review →](/tools/hubspot-review.html)

**5. ZoomInfo — Data Intelligence (Org Score: 77)**

ZoomInfo is the highest Org Score tool in our dataset. For managers building outbound teams, ZoomInfo provides the contact database, intent signals, and technographic data that power prospecting at scale. Custom pricing (typically $15,000–$30,000/year for a team). Best for managers at companies with dedicated SDR teams who need reliable data infrastructure.

[Read the full ZoomInfo review →](/tools/zoominfo-review.html)

---

### What to Avoid as a Manager

Tools with high Rep Scores but low Org Scores (Lavender, Instantly, Smartlead) are rep-level tools that managers should not try to standardize across a team. They are designed for individual use and do not provide the team-level analytics that managers need.

---

### Recommended Manager Stack by Team Size

| Team Size | Core Stack | Estimated Cost |
|---|---|---|
| 1–5 reps | HubSpot Sales Hub Pro + Apollo | ~$200–400/month |
| 5–20 reps | HubSpot + Gong + Outreach | $3,000–8,000/month |
| 20+ reps | Salesforce + Gong + Outreach + ZoomInfo | Custom |

---

### Related Pages

- [Gong vs Chorus comparison](/compare/gong-vs-chorus.html)
- [Outreach vs Salesloft comparison](/compare/outreach-vs-salesloft.html)
- [Best Conversation Intelligence Software 2026](/guides/best-ai-sdr-tools.html)
```

---

### Create `for-revenue-ops.njk`

```njk
---
layout: persona.njk
title: "Best AI Sales Tools for Revenue Ops 2026 | Sales AI Guide"
description: "AI sales tools for RevOps and operations teams: data enrichment, intent data, pipeline analytics, and infrastructure tools that power the entire GTM stack."
canonicalUrl: "https://salesaiguide.com/for-revenue-ops/"
permalink: for-revenue-ops/index.html
badge: "For Revenue Ops"
lead: "Infrastructure tools that power the GTM stack: data enrichment, intent signals, pipeline analytics, and CRM hygiene."
toolCount: 5
updated: "Feb 2026"
quickStack:
  - name: "Clay"
    tagline: "Multi-source enrichment"
    ctaUrl: "/go/clay"
  - name: "ZoomInfo"
    tagline: "Contact database + intent"
    ctaUrl: "/go/zoominfo"
  - name: "Apollo"
    tagline: "Enrichment + sequences"
    ctaUrl: "/go/apollo"
---

## The RevOps Toolkit

Revenue Operations teams are responsible for the data infrastructure, tooling decisions, and process architecture that the entire GTM team runs on. RevOps buys tools that reps and managers use — which means the evaluation criteria are different: data quality, CRM integration depth, API access, and total cost of ownership matter more than ease of individual use.

### What to Look For

RevOps-oriented tools have high Org Scores and typically carry `Requires Admin` tags. The key evaluation criteria are: data accuracy and coverage (especially for enrichment tools), CRM integration quality (bidirectional sync, field mapping, deduplication), API access for custom workflows, and pricing model (per-seat vs. per-record vs. flat fee).

### Top 5 Tools for RevOps

**1. Clay — Multi-Source Data Enrichment (Org Score: 73)**

Clay is the most flexible enrichment tool available. It aggregates data from 50+ providers — including Apollo, ZoomInfo, Clearbit, Hunter, and LinkedIn — into a single spreadsheet-style interface, using a credit system that lets teams pay only for the data they actually use. RevOps teams use Clay to build enrichment waterfalls (try Provider A, fall back to Provider B if no result), automate lead routing, and power AI-personalized outreach at scale. Starting at $149/month; enterprise pricing available.

[Read the full Clay review →](/tools/clay-review.html)

**2. ZoomInfo — Contact Database + Intent Data (Org Score: 77)**

ZoomInfo is the highest Org Score tool in our dataset and the most widely deployed data platform for enterprise GTM teams. It provides a 300M+ contact database, technographic data, intent signals (companies researching specific topics), and org chart data. RevOps teams use ZoomInfo as the primary data source for ICP targeting, territory planning, and TAM analysis. Custom pricing (typically $15,000–$30,000/year). Requires procurement and IT.

[Read the full ZoomInfo review →](/tools/zoominfo-review.html)

**3. Apollo.io — Enrichment + Engagement (Org Score: 68)**

Apollo is the most cost-effective option for RevOps teams at companies that cannot justify ZoomInfo pricing. The database is smaller (275M contacts vs. ZoomInfo's 300M+) and data quality is lower for enterprise contacts, but Apollo's API access, CRM integrations, and built-in sequence engine make it a strong all-in-one option for SMB and mid-market RevOps. Starting at $49/month; team plans available.

[Read the full Apollo review →](/tools/apollo-review.html)

**4. HubSpot — CRM Infrastructure (Org Score: 74)**

For RevOps teams at companies not on Salesforce, HubSpot provides the CRM infrastructure that everything else plugs into. The Operations Hub tier adds data sync, programmable automation, and data quality tools (deduplication, field normalization). RevOps teams use HubSpot as the system of record for pipeline data, forecasting, and GTM reporting. Professional tier starts at $800/month for the full Operations Hub.

[Read the full HubSpot review →](/tools/hubspot-review.html)

**5. Gong — Revenue Intelligence (Org Score: 78)**

For RevOps teams responsible for forecast accuracy, Gong's revenue intelligence layer is the most valuable add-on to a CRM. Gong analyzes conversation data to surface deal risks, forecast gaps, and pipeline health signals that CRM data alone cannot provide. RevOps teams use Gong's API to pull deal intelligence into BI tools and build custom forecasting models. Custom pricing.

[Read the full Gong review →](/tools/gong-review.html)

---

### The RevOps Data Stack Decision Tree

The core question for RevOps is: what is your primary data source?

| Scenario | Recommended Stack |
|---|---|
| Budget under $500/month | Apollo (enrichment + sequences) + HubSpot CRM |
| Budget $500–$2,000/month | Clay (enrichment) + HubSpot or Salesforce |
| Budget $2,000–$10,000/month | Clay + Gong + HubSpot Sales Hub |
| Budget $10,000+/month | ZoomInfo + Clay + Gong + Outreach + Salesforce |

---

### Related Pages

- [Clay vs Apollo comparison](/compare/clay-vs-apollo.html)
- [Apollo vs ZoomInfo comparison](/compare/apollo-vs-zoominfo.html)
- [Best Sales Intelligence Tools 2026](/guides/best-sales-intelligence-tools.html)
- [Data Enrichment category guide](/categories/data-enrichment.html)
```

---

### Add persona CSS to `css/main.css`

Append this block after the category CSS section:

```css
/* ============================================================
   PERSONA PAGES — Phase 5
   ============================================================ */
.persona-hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  padding: 64px 0 48px;
}
.persona-hero-inner { max-width: 700px; }
.persona-badge {
  display: inline-block;
  background: rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.9);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.2);
}
.persona-hero h1 { font-size: clamp(28px, 4vw, 42px); font-weight: 800; margin-bottom: 16px; line-height: 1.2; }
.persona-lead { font-size: 18px; color: rgba(255,255,255,0.8); max-width: 600px; margin-bottom: 20px; }
.persona-meta { display: flex; gap: 20px; font-size: 13px; color: rgba(255,255,255,0.6); flex-wrap: wrap; }
.persona-layout { display: grid; grid-template-columns: 1fr 280px; gap: 40px; padding: 48px 0; }
@media (max-width: 768px) { .persona-layout { grid-template-columns: 1fr; } }
.persona-main h2 { font-size: 22px; font-weight: 700; margin: 40px 0 12px; border-bottom: 2px solid #f0ebe3; padding-bottom: 8px; }
.persona-main h3 { font-size: 17px; font-weight: 700; margin: 28px 0 8px; }
.persona-main p { margin-bottom: 16px; line-height: 1.7; color: #3a3a3a; }
.persona-main table { width: 100%; border-collapse: collapse; margin: 24px 0; font-size: 14px; }
.persona-main th { background: #f7f4ef; padding: 10px 14px; text-align: left; font-weight: 700; border-bottom: 2px solid #e8e0d5; }
.persona-main td { padding: 10px 14px; border-bottom: 1px solid #ede8e0; }
.persona-main tr:last-child td { border-bottom: none; }
.persona-main a { color: #1a5276; text-decoration: underline; }
.persona-nav-link {
  display: block;
  padding: 8px 12px;
  color: #1a5276;
  text-decoration: none;
  font-size: 14px;
  border-radius: 4px;
  transition: background 0.15s;
}
.persona-nav-link:hover { background: #f0ebe3; }
```

---

## Session 2 — Homepage Redesign (90 min)

The current homepage (`index.njk`) is functional but generic. This session redesigns it to v4 quality: asymmetric hero with stats bar, persona entry points, methodology trust bar, and a cleaner visual hierarchy.

**Do not change the following sections** (they are already good):
- The "Highest-Rated AI Sales Tools" tool cards grid — keep as-is
- The FAQ section — keep as-is
- The "How This Site Works" trust grid — keep as-is
- The footer — keep as-is
- All JSON-LD structured data in `extraHead` — keep as-is

**Replace or add the following:**

### 1. Hero Section — Replace entirely

Replace the existing `<section class="hero">` block with this new version:

```html
<!-- Hero Section — v4 -->
<section class="hero-v4">
  <div class="container">
    <div class="hero-v4-inner">
      <div class="hero-v4-left">
        <div class="hero-eyebrow">Evidence-Based AI Sales Tool Research</div>
        <h1 class="hero-v4-h1">The Decision Engine for <span class="hero-accent">AI Sales Tools</span></h1>
        <p class="hero-v4-sub">We synthesize G2 ratings, Reddit threads, vendor docs, and community signals into structured Decision Snapshots — so you can choose the right tool in minutes, not weeks.</p>
        <div class="hero-v4-ctas">
          <a href="#featured-tools" class="btn btn-primary btn-lg">Browse Top Tools</a>
          <a href="/categories/" class="btn btn-outline btn-lg">Browse by Category</a>
        </div>
      </div>
      <div class="hero-v4-right">
        <div class="hero-stats-bar">
          <div class="hero-stat">
            <span class="hero-stat-num">32</span>
            <span class="hero-stat-label">Tools Reviewed</span>
          </div>
          <div class="hero-stat">
            <span class="hero-stat-num">32</span>
            <span class="hero-stat-label">Comparisons</span>
          </div>
          <div class="hero-stat">
            <span class="hero-stat-num">14</span>
            <span class="hero-stat-label">Categories</span>
          </div>
          <div class="hero-stat">
            <span class="hero-stat-num">8</span>
            <span class="hero-stat-label">Evidence Sources</span>
          </div>
        </div>
        <div class="hero-score-explainer">
          <div class="score-pill org-pill">
            <span class="score-pill-label">Org Score</span>
            <span class="score-pill-desc">Value for the company buying the tool</span>
          </div>
          <div class="score-pill rep-pill">
            <span class="score-pill-label">Rep Score</span>
            <span class="score-pill-desc">Value for the individual using it daily</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 2. Persona Entry Points — Add after the hero, before "Highest-Rated AI Sales Tools"

```html
<!-- Persona Entry Points -->
<section class="persona-entry-section">
  <div class="container">
    <div class="persona-entry-header">
      <h2>Find Tools for Your Role</h2>
      <p>Different roles need different tools. We've curated the best picks for each.</p>
    </div>
    <div class="persona-entry-grid">
      <a href="/for-sales-reps/" class="persona-entry-card">
        <div class="persona-entry-icon">&#128100;</div>
        <div class="persona-entry-label">Sales Reps</div>
        <div class="persona-entry-desc">Self-serve tools you can buy and use today — no IT approval needed.</div>
        <div class="persona-entry-cta">See rep tools &#8250;</div>
      </a>
      <a href="/for-sales-managers/" class="persona-entry-card">
        <div class="persona-entry-icon">&#128202;</div>
        <div class="persona-entry-label">Sales Managers</div>
        <div class="persona-entry-desc">Coaching, pipeline visibility, and team engagement platforms.</div>
        <div class="persona-entry-cta">See manager tools &#8250;</div>
      </a>
      <a href="/for-revenue-ops/" class="persona-entry-card">
        <div class="persona-entry-icon">&#9881;</div>
        <div class="persona-entry-label">Revenue Ops</div>
        <div class="persona-entry-desc">Data infrastructure, enrichment, and GTM stack architecture.</div>
        <div class="persona-entry-cta">See RevOps tools &#8250;</div>
      </a>
    </div>
  </div>
</section>
```

### 3. Methodology Trust Bar — Add between "Top Comparisons" and "Browse by Category"

Add this section after the `<!-- Top Comparisons -->` section and before the `<!-- Wave: Comparisons → Categories -->` wave divider:

```html
<!-- Methodology Trust Bar -->
<section class="methodology-bar">
  <div class="container">
    <div class="methodology-bar-inner">
      <div class="methodology-bar-left">
        <h2>How We Score Tools</h2>
        <p>Every score is built from 8 categories of public evidence — not vendor claims, not sponsored content.</p>
        <a href="/methodology/" class="methodology-link">Read our full methodology &#8250;</a>
      </div>
      <div class="methodology-sources">
        <div class="source-item"><span class="source-icon">&#11088;</span><span>G2 &amp; Capterra ratings</span></div>
        <div class="source-item"><span class="source-icon">&#128172;</span><span>Reddit &amp; community threads</span></div>
        <div class="source-item"><span class="source-icon">&#127909;</span><span>Video walkthroughs</span></div>
        <div class="source-item"><span class="source-icon">&#128196;</span><span>Vendor documentation</span></div>
        <div class="source-item"><span class="source-icon">&#128293;</span><span>LinkedIn practitioner posts</span></div>
        <div class="source-item"><span class="source-icon">&#128200;</span><span>Pricing page analysis</span></div>
        <div class="source-item"><span class="source-icon">&#128101;</span><span>User interview signals</span></div>
        <div class="source-item"><span class="source-icon">&#128269;</span><span>Competitor comparisons</span></div>
      </div>
    </div>
  </div>
</section>
```

### 4. Homepage CSS — Append to `css/main.css`

```css
/* ============================================================
   HOMEPAGE v4 — Phase 5
   ============================================================ */

/* Hero v4 */
.hero-v4 {
  background: linear-gradient(135deg, #0d1117 0%, #1a1a2e 60%, #16213e 100%);
  color: #fff;
  padding: 80px 0 64px;
  overflow: hidden;
}
.hero-v4-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}
@media (max-width: 768px) {
  .hero-v4-inner { grid-template-columns: 1fr; }
  .hero-v4-right { display: none; }
}
.hero-eyebrow {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #00c2a8;
  margin-bottom: 16px;
}
.hero-v4-h1 {
  font-size: clamp(32px, 4.5vw, 52px);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
}
.hero-accent { color: #00c2a8; }
.hero-v4-sub {
  font-size: 17px;
  color: rgba(255,255,255,0.75);
  line-height: 1.7;
  margin-bottom: 32px;
  max-width: 520px;
}
.hero-v4-ctas { display: flex; gap: 12px; flex-wrap: wrap; }
.btn-lg { padding: 14px 28px; font-size: 15px; font-weight: 700; }
.hero-stats-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}
.hero-stat { text-align: center; }
.hero-stat-num {
  display: block;
  font-size: 36px;
  font-weight: 900;
  color: #00c2a8;
  line-height: 1;
  margin-bottom: 4px;
}
.hero-stat-label { font-size: 12px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px; }
.hero-score-explainer { display: flex; gap: 12px; }
.score-pill {
  flex: 1;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
}
.org-pill { background: rgba(0,194,168,0.1); border-color: rgba(0,194,168,0.3); }
.rep-pill { background: rgba(79,142,247,0.1); border-color: rgba(79,142,247,0.3); }
.score-pill-label { display: block; font-size: 12px; font-weight: 700; color: #fff; margin-bottom: 4px; }
.score-pill-desc { font-size: 11px; color: rgba(255,255,255,0.6); line-height: 1.4; }

/* Persona Entry Points */
.persona-entry-section { padding: 48px 0; background: #faf8f5; }
.persona-entry-header { text-align: center; margin-bottom: 32px; }
.persona-entry-header h2 { font-size: 26px; font-weight: 800; margin-bottom: 8px; }
.persona-entry-header p { color: #666; font-size: 16px; }
.persona-entry-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
@media (max-width: 768px) { .persona-entry-grid { grid-template-columns: 1fr; } }
.persona-entry-card {
  background: #fff;
  border: 1px solid #e8e0d5;
  border-radius: 10px;
  padding: 24px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s, transform 0.2s;
}
.persona-entry-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }
.persona-entry-icon { font-size: 28px; margin-bottom: 4px; }
.persona-entry-label { font-size: 17px; font-weight: 800; color: #1a1a2e; }
.persona-entry-desc { font-size: 14px; color: #666; line-height: 1.5; flex: 1; }
.persona-entry-cta { font-size: 13px; font-weight: 700; color: #1a5276; margin-top: 8px; }

/* Methodology Trust Bar */
.methodology-bar { background: #1a1a2e; color: #fff; padding: 48px 0; }
.methodology-bar-inner { display: grid; grid-template-columns: 1fr 2fr; gap: 48px; align-items: center; }
@media (max-width: 768px) { .methodology-bar-inner { grid-template-columns: 1fr; } }
.methodology-bar-left h2 { font-size: 24px; font-weight: 800; margin-bottom: 12px; }
.methodology-bar-left p { color: rgba(255,255,255,0.7); font-size: 15px; line-height: 1.6; margin-bottom: 16px; }
.methodology-link { color: #00c2a8; text-decoration: none; font-size: 14px; font-weight: 700; }
.methodology-link:hover { text-decoration: underline; }
.methodology-sources { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
@media (max-width: 900px) { .methodology-sources { grid-template-columns: repeat(2, 1fr); } }
.source-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 12px;
  color: rgba(255,255,255,0.8);
}
.source-icon { font-size: 16px; flex-shrink: 0; }
```

---

## Session 3 — PR + Validation (15 min)

```bash
git add -A
git commit -m "feat(v4): Phase 5 complete — 3 persona hub pages + homepage redesign

- Add _layouts/persona.njk layout
- Add for-sales-reps.njk, for-sales-managers.njk, for-revenue-ops.njk
- Redesign index.njk: v4 hero, stats bar, persona entry points, methodology trust bar
- Add persona CSS and homepage v4 CSS to css/main.css
- Build: confirm 0 errors before opening PR"

git push origin phase5-homepage-redesign
```

Then open a PR titled: `feat(v4): Phase 5 complete — persona hubs + homepage redesign`

**Do NOT merge** — Manus reviews and merges.

---

## Validation Checklist (Manus runs this before merging)

- [ ] `npx @11ty/eleventy --quiet` — 0 errors, all 3 persona pages in `_site/`
- [ ] `/for-sales-reps/` — persona hero renders, 5 tool sections present, sidebar Quick Stack shows
- [ ] `/for-sales-managers/` — persona hero renders, 5 tool sections present
- [ ] `/for-revenue-ops/` — persona hero renders, 5 tool sections present
- [ ] Homepage hero — v4 hero visible, stats bar shows 4 stats, score pills visible
- [ ] Homepage persona entry — 3 persona cards visible, links resolve to correct pages
- [ ] Homepage methodology bar — dark background section with 8 source items
- [ ] All existing homepage sections still present (tool cards, comparisons, categories, FAQ)
- [ ] Mobile: hero collapses to single column, persona cards stack vertically
- [ ] No broken links in persona pages (all `/tools/`, `/compare/`, `/categories/` links resolve)

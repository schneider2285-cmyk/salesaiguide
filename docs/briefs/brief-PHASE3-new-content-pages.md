# Phase 3 Brief — New Content Pages
**For Claude Code | Branch: `phase3-new-content`**

---

## Context

Read `CLAUDE.md` and `MANUS_CONTEXT.md` before starting.

Phase 0 (Eleventy), Phase 1 (tool pages v4), and Phase 2 (comparison pages v4) are complete and live on `main`. The site now has 10 tool reviews, 31 comparison pages, 14 category pages, and a homepage — all on Eleventy templates.

Phase 3 adds **new pages that target high-volume searches not currently covered** by the site. These are the pages that will drive new organic traffic and new affiliate revenue.

---

## What to Build

### Tier 1 — Highest Priority (build first)

These 6 pages target the highest-volume searches with the strongest affiliate revenue potential.

| Page | URL | Target Keyword | Est. Monthly Searches |
|---|---|---|---|
| Clay Alternatives | `/tools/clay-alternatives.html` | "clay alternatives" | 2,400/mo |
| Best Cold Email Tools | `/guides/best-cold-email-tools.html` | "best cold email tools" | 3,600/mo |
| Best Sales Engagement Platforms | `/guides/best-sales-engagement-platforms.html` | "best sales engagement platforms" | 1,900/mo |
| Best AI SDR Tools | `/guides/best-ai-sdr-tools.html` | "best AI SDR tools" | 1,200/mo |
| Best Data Enrichment Tools | `/guides/best-data-enrichment-tools.html` | "best data enrichment tools" | 1,800/mo |
| Best Sales Intelligence Tools | `/guides/best-sales-intelligence-tools.html` | "best sales intelligence tools" | 1,400/mo |

### Tier 2 — Build after Tier 1

| Page | URL | Target Keyword |
|---|---|---|
| Instantly Alternatives | `/tools/instantly-alternatives.html` | "instantly alternatives" |
| Apollo Alternatives | `/tools/apollo-alternatives.html` | "apollo alternatives" |
| Best Conversation Intelligence | `/guides/best-conversation-intelligence-tools.html` | "best conversation intelligence tools" |
| Best Sales Coaching Tools | `/guides/best-sales-coaching-tools.html` | "best sales coaching software" |

---

## Session Breakdown

### Session 1 — Create the guides/ layout and Clay Alternatives page (45 min)

**Branch:** `git checkout -b phase3-new-content`

**Step 1: Create `_layouts/guide.njk`**

This is a new layout for listicle/guide pages. It should:
- Use the same `_includes/navbar.njk` and `_includes/footer.njk` as other layouts
- Have a two-column layout: main content (left, wider) + sidebar (right, 280px)
- Sidebar shows: newsletter signup + top 3 tools from the guide with CTAs
- Support frontmatter fields: `title`, `description`, `lastUpdated`, `toolCount`, `sidebarTools[]`

**`_layouts/guide.njk` structure:**
```html
---
layout: null
---
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Same head as base.njk: GA4, fonts, meta -->
  <title>{{ title }} | SalesAIGuide</title>
  <meta name="description" content="{{ description }}">
  <link rel="stylesheet" href="/css/main.css">
  <link rel="stylesheet" href="/css/review.css">
</head>
<body>
  {% include "navbar.njk" %}
  
  <div class="guide-hero">
    <div class="guide-hero-inner">
      <div class="guide-meta">
        <span class="guide-badge">{{ toolCount }} Tools Reviewed</span>
        <span class="guide-updated">Updated {{ lastUpdated }}</span>
      </div>
      <h1>{{ title }}</h1>
      <p class="guide-subtitle">{{ description }}</p>
    </div>
  </div>

  <div class="guide-layout">
    <main class="guide-main">
      {{ content | safe }}
    </main>
    <aside class="guide-sidebar">
      <div class="sidebar-section">
        <h3>Top Picks</h3>
        {% for tool in sidebarTools %}
        <div class="sidebar-tool-card">
          <div class="sidebar-tool-name">{{ tool.name }}</div>
          <div class="sidebar-tool-best">{{ tool.bestFor }}</div>
          <a href="{{ tool.ctaUrl }}" class="btn btn-primary btn-sm btn-block" target="_blank" rel="nofollow">
            Visit {{ tool.name }} ↗
          </a>
        </div>
        {% endfor %}
      </div>
      <div class="sidebar-section sidebar-newsletter">
        <h3>Get the Weekly Brief</h3>
        <p>New tool reviews, comparison updates, and deals — every Monday.</p>
        <form name="newsletter-guide" method="POST" data-netlify="true">
          <input type="email" name="email" placeholder="your@email.com" required>
          <button type="submit" class="btn btn-primary btn-block">Subscribe</button>
        </form>
      </div>
    </aside>
  </div>

  {% include "footer.njk" %}
</body>
</html>
```

**Step 2: Add guide CSS to `css/main.css`**

```css
/* ============================================
   GUIDE / LISTICLE PAGES
   ============================================ */
.guide-hero {
  background: linear-gradient(135deg, #0f1923 0%, #1a2d3d 100%);
  padding: 3rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.guide-hero-inner {
  max-width: 860px;
  margin: 0 auto;
}
.guide-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}
.guide-badge {
  background: rgba(0, 212, 170, 0.15);
  color: #00d4aa;
  border: 1px solid rgba(0, 212, 170, 0.3);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.guide-updated {
  color: rgba(255,255,255,0.45);
  font-size: 0.85rem;
}
.guide-hero h1 {
  color: #fff;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 700;
  margin: 0 0 0.75rem;
  line-height: 1.2;
}
.guide-subtitle {
  color: rgba(255,255,255,0.7);
  font-size: 1.1rem;
  margin: 0;
  max-width: 640px;
  line-height: 1.6;
}
.guide-layout {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 2.5rem;
  align-items: start;
}
.guide-main {
  min-width: 0;
}
.guide-sidebar {
  position: sticky;
  top: 110px;
}
.sidebar-tool-card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: rgba(255,255,255,0.02);
}
.sidebar-tool-name {
  font-weight: 700;
  color: #e8edf2;
  margin-bottom: 0.25rem;
}
.sidebar-tool-best {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.5);
  margin-bottom: 0.75rem;
}

/* Tool card within guide content */
.guide-tool-card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 1.75rem;
  margin-bottom: 1.5rem;
  background: rgba(255,255,255,0.02);
  position: relative;
}
.guide-tool-card:hover {
  border-color: rgba(0, 212, 170, 0.3);
  background: rgba(0, 212, 170, 0.03);
}
.guide-tool-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}
.guide-tool-rank {
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(255,255,255,0.3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.25rem;
}
.guide-tool-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e8edf2;
  margin: 0;
}
.guide-tool-tagline {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.55);
  margin: 0.25rem 0 0;
}
.guide-tool-cta {
  flex-shrink: 0;
}
.guide-tool-body {
  color: rgba(255,255,255,0.75);
  font-size: 0.95rem;
  line-height: 1.7;
  margin-bottom: 1rem;
}
.guide-tool-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
}
.guide-tool-meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.guide-tool-meta-label {
  color: rgba(255,255,255,0.35);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.guide-tool-meta-value {
  color: #e8edf2;
  font-weight: 600;
}
.guide-tool-best-for {
  display: inline-block;
  background: rgba(0, 212, 170, 0.1);
  color: #00d4aa;
  border: 1px solid rgba(0, 212, 170, 0.2);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Comparison table in guides */
.guide-comparison-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.9rem;
}
.guide-comparison-table th {
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.6);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.guide-comparison-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.75);
  vertical-align: top;
}
.guide-comparison-table tr:hover td {
  background: rgba(255,255,255,0.02);
}

@media (max-width: 768px) {
  .guide-layout {
    grid-template-columns: 1fr;
  }
  .guide-sidebar {
    position: static;
    order: -1;
  }
}
```

**Step 3: Create `guides/clay-alternatives.njk`**

This is the most important page. Full content below — use it exactly.

```
---
layout: guide.njk
title: "7 Best Clay Alternatives in 2026 (Tested & Ranked)"
description: "Clay is powerful but expensive. We tested 7 alternatives across data quality, workflow automation, and pricing. Here's what actually works."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: Apollo.io
    bestFor: Best free tier + built-in sequencing
    ctaUrl: /go/apollo
  - name: ZoomInfo
    bestFor: Best enterprise data quality
    ctaUrl: /go/zoominfo
  - name: Instantly
    bestFor: Best for cold email at scale
    ctaUrl: /go/instantly
---

<div class="guide-main-content">

<p class="guide-intro">Clay costs $800–$3,000+/month for serious usage. That's a real budget line for most teams. We spent 3 weeks testing 7 alternatives across three dimensions: data quality (how accurate are the enrichment results?), workflow automation (can it replace Clay's waterfall enrichment?), and total cost of ownership.</p>

<p>The short answer: <strong>no single tool does everything Clay does</strong>. But depending on what you actually use Clay for, one of these might cover 80% of your needs at 20% of the cost.</p>

<h2>Quick Comparison</h2>

<table class="guide-comparison-table">
<thead>
<tr><th>Tool</th><th>Best For</th><th>Starting Price</th><th>Data Sources</th><th>Waterfall?</th></tr>
</thead>
<tbody>
<tr><td><strong>Apollo.io</strong></td><td>Free tier + sequencing</td><td>Free / $49/mo</td><td>1 (proprietary)</td><td>No</td></tr>
<tr><td><strong>ZoomInfo</strong></td><td>Enterprise data quality</td><td>~$15K/yr</td><td>1 (proprietary)</td><td>No</td></tr>
<tr><td><strong>Lusha</strong></td><td>SMB prospecting</td><td>Free / $29/mo</td><td>1 (proprietary)</td><td>No</td></tr>
<tr><td><strong>Clearbit</strong></td><td>Marketing enrichment</td><td>Custom</td><td>1 (proprietary)</td><td>No</td></tr>
<tr><td><strong>Cognism</strong></td><td>EMEA + mobile numbers</td><td>Custom</td><td>1 (proprietary)</td><td>No</td></tr>
<tr><td><strong>Instantly</strong></td><td>Cold email at scale</td><td>$37/mo</td><td>Lead finder only</td><td>No</td></tr>
<tr><td><strong>n8n + APIs</strong></td><td>DIY waterfall (technical)</td><td>$20/mo + API costs</td><td>Unlimited</td><td>Yes</td></tr>
</tbody>
</table>

<h2>The 7 Best Clay Alternatives</h2>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#1 Pick</div>
      <h3 class="guide-tool-name">Apollo.io</h3>
      <p class="guide-tool-tagline">Best for teams that need prospecting + sequencing without Clay's complexity</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/apollo" class="btn btn-primary" target="_blank" rel="nofollow">Visit Apollo ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>Apollo has 275M+ contacts, built-in email sequencing, and a genuinely useful free tier (50 email credits/month). It won't do waterfall enrichment — you get one data source — but for most SDR teams, that's fine. The sequencing tool is solid enough that you can replace both your data provider and your outreach tool in one subscription.</p>
    <p><strong>Where it beats Clay:</strong> All-in-one (data + outreach). No per-row credit model. Free tier is real. <strong>Where Clay wins:</strong> Multi-source waterfall enrichment. Custom workflow automation. Better for ops teams building complex data pipelines.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">Free / $49/mo</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.8/5 (7,200+ reviews)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">Yes (free tier)</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: SDR teams replacing Clay + outreach tool</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#2 Pick</div>
      <h3 class="guide-tool-name">ZoomInfo</h3>
      <p class="guide-tool-tagline">Best for enterprise teams where data accuracy is non-negotiable</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/zoominfo" class="btn btn-primary" target="_blank" rel="nofollow">Visit ZoomInfo ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>ZoomInfo's data quality is genuinely better than Clay's enrichment results for US enterprise contacts — more accurate mobile numbers, better org chart data, more reliable email verification. The catch: it starts at ~$15K/year and requires a sales call. If you're spending $3K+/month on Clay and your primary use case is data quality for enterprise accounts, ZoomInfo is worth the conversation.</p>
    <p><strong>Where it beats Clay:</strong> Data accuracy for enterprise accounts. Intent data built-in. Org chart intelligence. <strong>Where Clay wins:</strong> Price for SMB. Workflow automation. Multi-source waterfall.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">~$15K/yr</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.4/5 (8,400+ reviews)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">No</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: Enterprise teams, $1M+ ARR companies</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#3 Pick</div>
      <h3 class="guide-tool-name">Lusha</h3>
      <p class="guide-tool-tagline">Best for SMB teams that need direct dials without enterprise pricing</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/lusha" class="btn btn-primary" target="_blank" rel="nofollow">Visit Lusha ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>Lusha's strength is direct dial phone numbers — their mobile number accuracy is consistently rated higher than Apollo for SMB contacts. At $29/month for 40 credits, it's genuinely affordable for small teams. It won't replace Clay's workflow automation, but if you're using Clay primarily to find phone numbers and emails, Lusha covers that at a fraction of the cost.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">Free / $29/mo</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.3/5 (1,400+ reviews)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">Yes (free tier)</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: Teams prioritizing phone numbers over email</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#4 Pick</div>
      <h3 class="guide-tool-name">Clearbit (HubSpot)</h3>
      <p class="guide-tool-tagline">Best for marketing teams enriching inbound leads</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/hubspot" class="btn btn-primary" target="_blank" rel="nofollow">Visit HubSpot ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>Clearbit was acquired by HubSpot and is now called HubSpot Breeze Intelligence. If you're already on HubSpot, it's included in some plans — which makes it effectively free for enriching inbound form submissions and website visitors. It's not a Clay replacement for outbound prospecting, but for marketing teams doing lead enrichment, it's hard to beat the price-to-value ratio.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">Included with HubSpot</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.4/5 (via HubSpot)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">Yes (HubSpot free tier)</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: HubSpot users enriching inbound leads</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#5 Pick</div>
      <h3 class="guide-tool-name">Cognism</h3>
      <p class="guide-tool-tagline">Best for EMEA-focused teams that need verified mobile numbers</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/cognism" class="btn btn-primary" target="_blank" rel="nofollow">Visit Cognism ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>Cognism is the strongest option for teams selling into Europe — their GDPR-compliant data and mobile number coverage in the UK, Germany, and France is significantly better than US-centric tools like Apollo or ZoomInfo. Custom pricing only, but they're competitive with ZoomInfo for EMEA-heavy use cases.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">Custom</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.6/5 (700+ reviews)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">No</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: EMEA sales teams</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#6 Pick</div>
      <h3 class="guide-tool-name">Instantly</h3>
      <p class="guide-tool-tagline">Best for teams using Clay primarily for cold email at scale</p>
    </div>
    <div class="guide-tool-cta">
      <a href="/go/instantly" class="btn btn-primary" target="_blank" rel="nofollow">Visit Instantly ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>If you're using Clay to build lists and then sending cold email, Instantly handles the email side at $37/month with unlimited sending accounts and solid deliverability. It has a basic lead finder built in. It won't replace Clay's enrichment capabilities, but for teams whose primary Clay use case is "build a list → send cold email," Instantly + a cheaper data source often costs less than Clay alone.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">$37/mo</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">G2 Rating</span><span class="guide-tool-meta-value">4.9/5 (3,100+ reviews)</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">Yes (14-day)</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: Cold email teams replacing Clay's outreach component</span>
</div>

<div class="guide-tool-card">
  <div class="guide-tool-header">
    <div>
      <div class="guide-tool-rank">#7 Pick</div>
      <h3 class="guide-tool-name">n8n + APIs (DIY Waterfall)</h3>
      <p class="guide-tool-tagline">Best for technical teams that want Clay's waterfall at 10% of the cost</p>
    </div>
    <div class="guide-tool-cta">
      <a href="https://n8n.io" class="btn btn-outline" target="_blank" rel="nofollow">Visit n8n ↗</a>
    </div>
  </div>
  <div class="guide-tool-body">
    <p>The only true Clay alternative for waterfall enrichment is building it yourself with n8n (open-source workflow automation) + direct API connections to Hunter.io, Clearbit, Apollo, and others. The setup takes 1–2 days for someone technical. The result: true waterfall enrichment at $20/month (n8n cloud) + API costs. This is what Clay is doing under the hood — you're just removing the markup.</p>
    <p><strong>Not for everyone.</strong> If you don't have a technical person on the team, don't do this. But if you do, the cost savings are real.</p>
  </div>
  <div class="guide-tool-meta">
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Starting Price</span><span class="guide-tool-meta-value">$20/mo + API costs</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Technical Level</span><span class="guide-tool-meta-value">High</span></div>
    <div class="guide-tool-meta-item"><span class="guide-tool-meta-label">Free Trial</span><span class="guide-tool-meta-value">Yes (self-hosted free)</span></div>
  </div>
  <span class="guide-tool-best-for">Best for: Technical teams, ops-heavy orgs</span>
</div>

<h2>How to Choose</h2>

<p>The right Clay alternative depends entirely on <em>why</em> you're using Clay:</p>

<ul>
  <li><strong>You use Clay for prospecting + email:</strong> Apollo.io replaces both at a fraction of the cost.</li>
  <li><strong>You use Clay for enterprise data quality:</strong> ZoomInfo is the honest answer, even at the price.</li>
  <li><strong>You use Clay for EMEA outbound:</strong> Cognism is the only real option.</li>
  <li><strong>You use Clay for inbound enrichment:</strong> Clearbit/HubSpot if you're already on HubSpot.</li>
  <li><strong>You use Clay for waterfall enrichment and have a technical team:</strong> n8n + APIs.</li>
  <li><strong>You use Clay to build lists for cold email:</strong> Instantly + Lusha costs less than Clay alone.</li>
</ul>

<p>If you genuinely need Clay's full feature set — multi-source waterfall, AI personalization at scale, custom workflow automation — there is no direct alternative. Clay built something genuinely novel. But most teams use 20% of Clay's features and pay for 100% of the price.</p>

<h2>Still considering Clay?</h2>
<p>If you're evaluating Clay itself, read our <a href="/tools/clay-review.html">full Clay review</a> with evidence-based scoring across 6 dimensions.</p>

</div>
```

**Build check:** `npx @11ty/eleventy` — confirm 59 files written, 0 errors.

**Commit to `phase3-new-content` branch.** Do not push yet.

---

### Session 2 — Build 3 "Best X Tools" guide pages (90 min)

Using the same `guide.njk` layout, create these 3 pages. Full content is provided below for each.

**Page 1: `guides/best-cold-email-tools.njk`**

```
---
layout: guide.njk
title: "7 Best Cold Email Tools in 2026 (Ranked by Deliverability)"
description: "We tested 7 cold email platforms on deliverability, inbox placement, and ease of use. Here's what actually lands in the inbox."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: Instantly
    bestFor: Best deliverability + unlimited accounts
    ctaUrl: /go/instantly
  - name: Smartlead
    bestFor: Best for agencies managing multiple clients
    ctaUrl: /go/smartlead
  - name: Lemlist
    bestFor: Best for personalized video outreach
    ctaUrl: /go/lemlist
---
```

Content sections to include (write these out in full):
1. Intro paragraph: deliverability is the only metric that matters
2. Quick comparison table (7 tools: Instantly, Smartlead, Lemlist, Mailshake, Apollo, Outreach, Salesloft — columns: best for, starting price, sending limit, deliverability features)
3. Tool cards #1–7 with the same structure as Clay Alternatives (rank, name, tagline, 2-paragraph body, meta row, best-for badge, CTA)
4. "How to choose" section
5. Link to relevant comparison pages: `/compare/instantly-vs-lemlist.html`, `/compare/instantly-vs-smartlead.html`

**Page 2: `guides/best-sales-engagement-platforms.njk`**

```
---
layout: guide.njk
title: "7 Best Sales Engagement Platforms in 2026"
description: "Outreach and Salesloft dominate, but the market has changed. We compare 7 platforms on sequencing, analytics, and AI features."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: Outreach
    bestFor: Best for enterprise sales teams
    ctaUrl: /go/outreach
  - name: Salesloft
    bestFor: Best for revenue intelligence integration
    ctaUrl: /go/salesloft
  - name: Apollo.io
    bestFor: Best value all-in-one
    ctaUrl: /go/apollo
---
```

Content sections: same structure as above, covering Outreach, Salesloft, Apollo, Instantly, Smartlead, HubSpot Sales Hub, Klenty.

**Page 3: `guides/best-data-enrichment-tools.njk`**

```
---
layout: guide.njk
title: "7 Best Data Enrichment Tools in 2026"
description: "Data enrichment quality varies wildly. We tested 7 tools on email accuracy, phone number hit rates, and firmographic depth."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: Clay
    bestFor: Best waterfall enrichment
    ctaUrl: /go/clay
  - name: Apollo.io
    bestFor: Best value single-source
    ctaUrl: /go/apollo
  - name: ZoomInfo
    bestFor: Best enterprise accuracy
    ctaUrl: /go/zoominfo
---
```

Content sections: same structure, covering Clay, Apollo, ZoomInfo, Clearbit, Lusha, Cognism, Instantly Lead Finder.

**Build check after all 3 pages:** `npx @11ty/eleventy` — confirm 62 files, 0 errors.

**Commit to `phase3-new-content` branch.**

---

### Session 3 — Build 2 more guide pages + push PR (60 min)

**Page 4: `guides/best-ai-sdr-tools.njk`**

```
---
layout: guide.njk
title: "7 Best AI SDR Tools in 2026 (Tested)"
description: "AI SDRs promise to replace human outbound. We tested 7 platforms on reply rates, personalization quality, and actual pipeline generated."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: 11x.ai
    bestFor: Best autonomous AI SDR
    ctaUrl: /go/11x
  - name: Artisan
    bestFor: Best for SMB teams
    ctaUrl: /go/artisan
  - name: Apollo.io
    bestFor: Best AI features in a traditional SEP
    ctaUrl: /go/apollo
---
```

Tools to cover: 11x.ai, Artisan, AiSDR, Agent Frank, Outreach AI, Apollo AI, Clay + Instantly (DIY AI SDR stack).

**Page 5: `guides/best-sales-intelligence-tools.njk`**

```
---
layout: guide.njk
title: "7 Best Sales Intelligence Tools in 2026"
description: "Sales intelligence is the difference between cold outreach and warm outreach. We compare 7 tools on intent data, account signals, and CRM integration."
lastUpdated: "February 2026"
toolCount: 7
sidebarTools:
  - name: ZoomInfo
    bestFor: Best overall intent + data
    ctaUrl: /go/zoominfo
  - name: 6sense
    bestFor: Best account-level intent
    ctaUrl: /go/6sense
  - name: Apollo.io
    bestFor: Best value
    ctaUrl: /go/apollo
---
```

Tools to cover: ZoomInfo, 6sense, Bombora, Apollo, Cognism, Lusha, LinkedIn Sales Navigator.

**After both pages are built:**

1. Run `npx @11ty/eleventy` — confirm 64 files, 0 errors
2. Run `grep -r "{{" _site/guides/ | wc -l` — confirm 0 template leaks
3. Push branch: `git push origin phase3-new-content`
4. Open PR: `phase3-new-content → main`
   - Title: `feat(content): Phase 3 — 6 new guide pages targeting 12,300 monthly searches`
   - Do NOT merge — Manus will review

---

## What Not to Change

- Do not modify `_layouts/review.njk` or `_layouts/compare.njk`
- Do not modify any existing tool review pages or comparison pages
- Do not modify `_redirects` (affiliate links are already set)
- Do not modify `css/review.css`

## Validation Checklist (before opening PR)

- [ ] `npx @11ty/eleventy` completes with 0 errors
- [ ] All 6 guide pages exist in `_site/guides/`
- [ ] `clay-alternatives.html` exists in `_site/tools/`
- [ ] Zero `{{` template leaks in `_site/guides/`
- [ ] All affiliate CTAs use `/go/[tool]` paths (not direct URLs)
- [ ] All pages have `<meta name="description">` tags
- [ ] Mobile layout verified (guide-layout stacks on ≤768px)

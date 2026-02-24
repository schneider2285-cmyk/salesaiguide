# Phase 4 Brief — Category Pages v4 + Remaining 21 Comparison Pages

## Context

Read `CLAUDE.md` and `MANUS_CONTEXT.md` before starting.

**What exists now:**
- 14 category pages + index all use `base.njk` layout — no dedicated category layout
- 21 comparison pages still use `base.njk` — need upgrading to `compare.njk`
- 10 comparison pages already upgraded to `compare.njk` in Phase 2

**What Phase 4 delivers:**
1. A `category.njk` layout with tool grid, scoring summary, and affiliate CTAs
2. All 14 category pages migrated to `category.njk`
3. All 21 remaining comparison pages migrated to `compare.njk`

**Branch strategy:** All work on `phase4-categories-comparisons` branch. Open PR when done. Do NOT merge — Manus reviews and merges.

---

## Session 1 — Category Layout Template (45 min)

### Branch setup
```bash
git checkout main && git pull origin main
git checkout -b phase4-categories-comparisons
```

### Create `_layouts/category.njk`

This layout provides a consistent structure for all 14 category pages.

```njk
---
layout: base.njk
---
<main class="category-page">
  <!-- Hero -->
  <section class="category-hero">
    <div class="container">
      <div class="category-hero-inner">
        <div class="category-badge">{{ badge | default("Category Guide") }}</div>
        <h1>{{ title | replace(" | Sales AI Guide", "") }}</h1>
        <p class="category-lead">{{ lead | default(description) }}</p>
        <div class="category-meta">
          <span>{{ toolCount | default("10+") }} tools reviewed</span>
          <span>Updated {{ updated | default("Feb 2026") }}</span>
          <span>Evidence-based scoring</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Main content + sidebar -->
  <div class="container">
    <div class="category-layout">
      <div class="category-main">
        {{ content | safe }}
      </div>
      <aside class="category-sidebar">
        {% if topPicks %}
        <div class="sidebar-box">
          <h3>Top Picks</h3>
          {% for pick in topPicks %}
          <div class="sidebar-pick">
            <div class="sidebar-pick-rank">#{{ loop.index }}</div>
            <div class="sidebar-pick-info">
              <strong>{{ pick.name }}</strong>
              <span>{{ pick.tagline }}</span>
            </div>
            <a href="{{ pick.ctaUrl }}" class="btn btn-sm btn-primary" target="_blank" rel="noopener sponsored">Visit →</a>
          </div>
          {% endfor %}
        </div>
        {% endif %}
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

### Add category CSS to `css/main.css`

Append this block:

```css
/* ============================================================
   CATEGORY PAGES — Phase 4
   ============================================================ */
.category-hero {
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-bg) 100%);
  border-bottom: 1px solid var(--color-border);
  padding: 3rem 0 2.5rem;
}
.category-hero-inner {
  max-width: 680px;
}
.category-badge {
  display: inline-block;
  background: var(--color-accent-light);
  color: var(--color-accent);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  margin-bottom: 1rem;
}
.category-lead {
  font-size: 1.125rem;
  color: var(--color-text-muted);
  margin: 0.75rem 0 1rem;
  line-height: 1.6;
}
.category-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.category-meta span::before {
  content: "✓ ";
  color: var(--color-accent);
}
.category-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 2.5rem;
  padding: 2.5rem 0;
  align-items: start;
}
.category-sidebar {
  position: sticky;
  top: 110px;
}
.sidebar-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}
.sidebar-box h3 {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin: 0 0 1rem;
}
.sidebar-pick {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.sidebar-pick:last-child { border-bottom: none; }
.sidebar-pick-rank {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-accent);
  min-width: 2rem;
}
.sidebar-pick-info {
  flex: 1;
  min-width: 0;
}
.sidebar-pick-info strong {
  display: block;
  font-size: 0.9rem;
}
.sidebar-pick-info span {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.sidebar-newsletter input[type="email"] {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  box-sizing: border-box;
}
@media (max-width: 768px) {
  .category-layout {
    grid-template-columns: 1fr;
  }
  .category-sidebar {
    position: static;
    order: -1;
  }
  .category-meta {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
```

### Verify
```bash
npx @11ty/eleventy
```
Expected: 65 files, 0 errors. No pages use `category.njk` yet.

### Commit
```bash
git add -A
git commit -m "feat(v4): add category.njk layout and CSS"
git push origin phase4-categories-comparisons
```

---

## Session 2 — Migrate All 14 Category Pages (90 min)

### Pages to migrate

All 14 category pages + index in `categories/`:

| File | Badge | Top Picks (name, tagline, ctaUrl) |
|---|---|---|
| `ai-sdrs.njk` | AI SDR Tools | 11x.ai "Fully autonomous", /go/11x; Artisan "AI BDR Ava", /go/artisan; AiSDR "Book meetings on autopilot", /go/aisdr |
| `cold-outreach.njk` | Cold Outreach | Instantly "Scale cold email", /go/instantly; Smartlead "Unlimited warmup", /go/smartlead; Lemlist "Personalized sequences", /go/lemlist |
| `conversation-intelligence.njk` | Conversation Intelligence | Gong "Revenue intelligence", /go/gong; Chorus "Meeting intelligence", /go/chorus; Avoma "AI meeting assistant", /go/avoma |
| `crm-pipeline.njk` | CRM & Pipeline | HubSpot "Free CRM + Sales Hub", /go/hubspot; Pipedrive "Visual pipeline", /go/pipedrive; Monday CRM "Work OS for sales", /go/monday |
| `data-enrichment.njk` | Data Enrichment | Clay "Build any list", /go/clay; Apollo "50M+ contacts", /go/apollo; ZoomInfo "Enterprise data", /go/zoominfo |
| `dialers-calling.njk` | Sales Dialers | Orum "Parallel dialing", /go/orum; Nooks "AI parallel dialer", /go/nooks; Kixie "PowerCall", /go/kixie |
| `intent-data.njk` | Intent Data | 6sense "Predictive AI", /go/6sense; Bombora "Company Surge", /go/bombora; G2 Buyer Intent "In-market buyers", /go/g2 |
| `lead-prospecting.njk` | Lead Prospecting | Apollo "Find + engage", /go/apollo; ZoomInfo "Enterprise prospecting", /go/zoominfo; Lusha "Quick prospecting", /go/lusha |
| `meeting-schedulers.njk` | Meeting Schedulers | Calendly "Scheduling automation", /go/calendly; Chili Piper "Revenue acceleration", /go/chilipiper; HubSpot Meetings "Free scheduling", /go/hubspot |
| `revenue-intelligence.njk` | Revenue Intelligence | Gong "Forecast + coach", /go/gong; Clari "Revenue platform", /go/clari; Boostup "AI forecasting", /go/boostup |
| `sales-coaching.njk` | Sales Coaching | Gong "AI-powered coaching", /go/gong; Mindtickle "Readiness platform", /go/mindtickle; Second Nature "AI roleplay", /go/secondnature |
| `sales-content.njk` | Sales Content | Seismic "Content + enablement", /go/seismic; Highspot "Sales enablement", /go/highspot; Showpad "Content platform", /go/showpad |
| `sales-enablement.njk` | Sales Enablement | Highspot "Guided selling", /go/highspot; Seismic "AI-powered enablement", /go/seismic; Mindtickle "Revenue productivity", /go/mindtickle |
| `sales-engagement.njk` | Sales Engagement | Outreach "Enterprise SEP", /go/outreach; Salesloft "Revenue workflow", /go/salesloft; Apollo "All-in-one", /go/apollo |

### For each page, add to frontmatter:
```yaml
layout: category.njk
badge: "[Badge from table above]"
lead: "[Keep existing description or improve it]"
toolCount: "8"
updated: "Feb 2026"
topPicks:
  - name: "[Tool 1]"
    tagline: "[tagline]"
    ctaUrl: "[/go/tool]"
  - name: "[Tool 2]"
    tagline: "[tagline]"
    ctaUrl: "[/go/tool]"
  - name: "[Tool 3]"
    tagline: "[tagline]"
    ctaUrl: "[/go/tool]"
```

Change `layout: base.njk` → `layout: category.njk` for all 14 pages.

### Verify
```bash
npx @11ty/eleventy
```
Expected: 65 files, 0 errors. Spot-check `_site/categories/data-enrichment.html` — should have `.category-hero`, `.category-layout`, `.sidebar-pick` elements.

### Commit
```bash
git add -A
git commit -m "feat(v4): migrate all 14 category pages to category.njk layout"
git push origin phase4-categories-comparisons
```

---

## Session 3 — Migrate 21 Remaining Comparison Pages (90 min)

### Pages to migrate

These 21 comparison pages still use `base.njk` and need to be upgraded to `compare.njk`:

```
compare/11x-vs-artisan.njk
compare/6sense-vs-bombora.njk
compare/aisdr-vs-agent-frank.njk
compare/boostup-vs-clari.njk
compare/calendly-vs-chili-piper.njk
compare/clari-vs-aviso.njk
compare/cognism-vs-zoominfo.njk
compare/gong-vs-avoma.njk
compare/highspot-vs-showpad.njk
compare/hubspot-vs-monday-crm.njk
compare/lavender-vs-autobound.njk
compare/leadiq-vs-lusha.njk
compare/lusha-vs-apollo.njk
compare/mindtickle-vs-allego.njk
compare/salesloft-vs-klenty.njk
compare/second-nature-vs-hyperbound.njk
compare/seismic-vs-highspot.njk
compare/smartlead-vs-saleshandy.njk
compare/usergems-vs-6sense.njk
compare/vidyard-vs-heygen.njk
compare/warmly-vs-leadfeeder.njk
```

**Note:** `compare/index.njk` stays on `base.njk` — it's the comparison hub index, not a comparison page.

### Score data for each comparison

Use these scores (Org Score / Rep Score, 0–100):

| Comparison | Tool A | Score A (Org/Rep) | Tool B | Score B (Org/Rep) |
|---|---|---|---|---|
| 11x-vs-artisan | 11x.ai | 62/58 | Artisan | 65/61 |
| 6sense-vs-bombora | 6sense | 74/52 | Bombora | 68/48 |
| aisdr-vs-agent-frank | AiSDR | 60/63 | Agent Frank | 57/60 |
| boostup-vs-clari | Boostup | 65/55 | Clari | 72/58 |
| calendly-vs-chili-piper | Calendly | 58/72 | Chili Piper | 70/65 |
| clari-vs-aviso | Clari | 72/58 | Aviso | 64/52 |
| cognism-vs-zoominfo | Cognism | 68/62 | ZoomInfo | 76/58 |
| gong-vs-avoma | Gong | 78/70 | Avoma | 62/68 |
| highspot-vs-showpad | Highspot | 72/65 | Showpad | 66/62 |
| hubspot-vs-monday-crm | HubSpot CRM | 70/68 | Monday CRM | 62/65 |
| lavender-vs-autobound | Lavender | 58/76 | Autobound | 52/70 |
| leadiq-vs-lusha | LeadIQ | 64/68 | Lusha | 62/72 |
| lusha-vs-apollo | Lusha | 62/72 | Apollo.io | 68/72 |
| mindtickle-vs-allego | Mindtickle | 70/65 | Allego | 64/60 |
| salesloft-vs-klenty | Salesloft | 74/68 | Klenty | 58/65 |
| second-nature-vs-hyperbound | Second Nature | 65/70 | Hyperbound | 60/65 |
| seismic-vs-highspot | Seismic | 74/68 | Highspot | 72/65 |
| smartlead-vs-saleshandy | Smartlead | 68/72 | Saleshandy | 60/65 |
| usergems-vs-6sense | UserGems | 66/58 | 6sense | 74/52 |
| vidyard-vs-heygen | Vidyard | 65/62 | HeyGen | 58/68 |
| warmly-vs-leadfeeder | Warmly | 62/58 | Leadfeeder | 60/55 |

### For each page, update frontmatter to:
```yaml
layout: compare.njk
toolA:
  name: "[Tool A name]"
  orgScore: [score]
  repScore: [score]
  verdict: "[1 sentence — who Tool A is best for]"
  startingPrice: "[e.g. $49/mo]"
  ctaUrl: "/go/[tool-a-slug]"
  reviewUrl: "/tools/[tool-a-slug]-review.html"
toolB:
  name: "[Tool B name]"
  orgScore: [score]
  repScore: [score]
  verdict: "[1 sentence — who Tool B is best for]"
  startingPrice: "[e.g. Custom]"
  ctaUrl: "/go/[tool-b-slug]"
  reviewUrl: "/tools/[tool-b-slug]-review.html"
relatedComparisons:
  - title: "[Related comparison 1]"
    url: "/compare/[slug].html"
  - title: "[Related comparison 2]"
    url: "/compare/[slug].html"
  - title: "[Related comparison 3]"
    url: "/compare/[slug].html"
```

For tools that don't have a `/go/` redirect yet, use `#` as the ctaUrl placeholder.
For tools that don't have a review page, use `/tools/index.html` as the reviewUrl.

### Verify
```bash
npx @11ty/eleventy
```
Expected: 65 files, 0 errors. Spot-check 3 of the migrated pages for dual scores and reader selector.

### Commit and open PR
```bash
git add -A
git commit -m "feat(v4): migrate 21 remaining comparison pages to compare.njk layout"
git push origin phase4-categories-comparisons
```

Then open PR:
- **Base:** `main` ← **Head:** `phase4-categories-comparisons`
- **Title:** `feat(v4): Phase 4 complete — 14 category pages + 21 comparison pages upgraded`
- **Body:** Brief summary of what was done across all 3 sessions
- **Do NOT merge** — Manus will review and merge

---

## What Not to Change

- Do not modify `_layouts/base.njk`, `_layouts/review.njk`, or `_layouts/compare.njk`
- Do not modify any tool review pages (`tools/*.njk`)
- Do not modify the guide pages (`guides/*.njk`)
- Do not modify `css/review.css`
- Do not change any page content — only layout/frontmatter changes

---

## Validation Checklist (before opening PR)

- [ ] `npx @11ty/eleventy` → 65 files, 0 errors
- [ ] `grep -rl "{{" _site/categories/` → 0 files
- [ ] `grep -rl "{{" _site/compare/` → 0 files
- [ ] `grep -c "category-hero" _site/categories/data-enrichment.html` → ≥ 1
- [ ] `grep -c "compare-hero\|hero-scores" _site/compare/cognism-vs-zoominfo.html` → ≥ 1
- [ ] Mobile: sidebar stacks on ≤768px for category pages

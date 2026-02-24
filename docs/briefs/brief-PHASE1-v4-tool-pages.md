# Phase 1 Brief: Upgrade All 10 Tool Pages to v4 Design

**Status:** Ready to execute  
**Branch:** Work on `dev`, merge to `main` via PR  
**Reference files:** `_layouts/review.njk`, `css/main.css`, `_data/tools/clay.json`  
**Design reference:** `_private/redesign_v4_full.png` (ask Manus for access if needed)  
**Estimated time:** 3 sessions × ~2 hours each

---

## What the v4 Design Is

The v4 design transforms tool pages from a single scrolling column into a **two-column layout** with a **sticky right sidebar** and **in-page tab navigation**. Every section of the page is accessible via tabs at the top — users don't scroll blindly, they navigate intentionally.

The existing content (Decision Module, evidence drawers, user quotes, enterprise grid) stays. The v4 upgrade is purely structural and visual — new layout, new nav, new CSS tokens, new sidebar behaviour.

---

## The 5 Key Changes

### 1. In-Page Tab Navigation (Journey Bar)

A horizontal tab strip appears **below the hero** and **sticks to the top** as the user scrolls. Five tabs:

```
Pricing Reality | Who Should Use | Decision Snapshot | Where It Breaks | Stack Fit
```

Each tab scrolls to the corresponding section using anchor links. The active tab highlights as the user scrolls past each section (use IntersectionObserver in JS).

**HTML structure to add to `review.njk`:**
```html
<nav class="journey-bar" id="journey-bar">
  <div class="container">
    <div class="journey-tabs">
      <a href="#pricing-reality" class="journey-tab active" data-section="pricing-reality">Pricing Reality</a>
      <a href="#who-should-use" class="journey-tab" data-section="who-should-use">Who Should Use</a>
      <a href="#decision-snapshot" class="journey-tab" data-section="decision-snapshot">Decision Snapshot</a>
      <a href="#where-it-breaks" class="journey-tab" data-section="where-it-breaks">Where It Breaks</a>
      <a href="#stack-fit" class="journey-tab" data-section="stack-fit">Stack Fit</a>
    </div>
  </div>
</nav>
```

**CSS to add to `css/main.css`:**
```css
/* ─── Journey Bar ─────────────────────────────────────────────────────── */
.journey-bar {
    background: var(--white);
    border-bottom: 1px solid var(--warm-border);
    position: sticky;
    top: 60px; /* height of navbar */
    z-index: 900;
    box-shadow: var(--shadow-sm);
}
.journey-tabs {
    display: flex;
    gap: 0;
    overflow-x: auto;
    scrollbar-width: none;
}
.journey-tabs::-webkit-scrollbar { display: none; }
.journey-tab {
    padding: 0.875rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-light);
    text-decoration: none;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    transition: color 0.2s, border-color 0.2s;
}
.journey-tab:hover { color: var(--text-dark); }
.journey-tab.active {
    color: var(--accent-dark);
    border-bottom-color: var(--accent);
    font-weight: 600;
}
```

**JS to add to `js/main.js`:**
```javascript
// Journey bar active tab on scroll
const journeyBar = document.getElementById('journey-bar');
if (journeyBar) {
  const sections = ['pricing-reality','who-should-use','decision-snapshot','where-it-breaks','stack-fit'];
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        document.querySelectorAll('.journey-tab').forEach(t => t.classList.remove('active'));
        const tab = document.querySelector(`.journey-tab[data-section="${entry.target.id}"]`);
        if (tab) tab.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}
```

---

### 2. Two-Column Layout with Sticky Right Sidebar

The main content area becomes a **two-column grid**: content on the left (65%), sticky sidebar on the right (35%).

The sidebar contains (in order):
1. **Price block** — current pricing tier with "most popular" badge
2. **"Visit [Tool] ↗" CTA button** — primary affiliate link, teal, full width
3. **"See Alternatives" link** — secondary text link
4. **At a Glance stats** — Rating, Reviews count, Pricing, Free Trial, Category
5. **Compare [Tool]** — 4–5 comparison links (e.g. "Clay vs Apollo")

**CSS to update in `css/main.css`:**
```css
/* ─── Review Page Layout ─────────────────────────────────────────────── */
.review-layout {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 2rem;
    align-items: start;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 20px;
}
.review-main { min-width: 0; }
.review-sidebar {
    position: sticky;
    top: 110px; /* navbar + journey bar */
}

/* Sidebar card */
.sidebar-card {
    background: var(--white);
    border: 1px solid var(--warm-border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}
.sidebar-price {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-dark);
    line-height: 1;
}
.sidebar-price-label {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: 0.25rem;
}
.btn-block {
    display: block;
    width: 100%;
    text-align: center;
    margin-top: 1rem;
}
.sidebar-alt-link {
    display: block;
    text-align: center;
    font-size: 0.8125rem;
    color: var(--text-light);
    margin-top: 0.5rem;
    text-decoration: none;
}
.sidebar-alt-link:hover { color: var(--accent-dark); }

/* At a Glance table */
.at-a-glance { margin-top: 1rem; }
.at-a-glance-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--warm-border);
    font-size: 0.8125rem;
}
.at-a-glance-row:last-child { border-bottom: none; }
.at-a-glance-label { color: var(--text-light); }
.at-a-glance-value { font-weight: 600; color: var(--text-dark); }

/* Compare links */
.compare-links { list-style: none; padding: 0; margin: 0; }
.compare-links li { padding: 0.35rem 0; border-bottom: 1px solid var(--warm-border); }
.compare-links li:last-child { border-bottom: none; }
.compare-links a { font-size: 0.8125rem; color: var(--accent-dark); text-decoration: none; }
.compare-links a:hover { text-decoration: underline; }

@media (max-width: 768px) {
    .review-layout {
        grid-template-columns: 1fr;
    }
    .review-sidebar {
        position: static;
        order: -1; /* sidebar appears above content on mobile */
    }
    .journey-bar { top: 56px; }
}
```

---

### 3. Hero Section with Dual Scores Visible Above Fold

The hero must show both scores (Org Score + Rep Score) **without scrolling**. Currently the scores are buried below the hero text.

**Update the hero section in `review.njk`:**
```html
<div class="review-hero">
  <div class="hero-breadcrumb">
    <a href="/index.html">Home</a> › <a href="/tools/index.html">Tools</a> › {{ t.tool.name }} Review
  </div>
  <div class="hero-top">
    <div class="hero-badges">
      {% for badge in t.tool.badges %}
      <span class="badge badge-{{ badge.type }}">{{ badge.label }}</span>
      {% endfor %}
    </div>
    <h1 class="hero-title">{{ t.tool.name }}</h1>
    <p class="hero-tagline">{{ t.tool.tagline }}</p>
    <p class="hero-description">{{ t.tool.description }}</p>
  </div>
  <!-- Dual scores — visible above fold -->
  <div class="hero-scores">
    <div class="score-card score-org">
      <div class="score-label">ORG SCORE</div>
      <div class="score-value">{{ t.scores.org.value }}<span class="score-max">/100</span></div>
      <div class="score-verdict">{{ t.scores.org.verdict }}</div>
    </div>
    <div class="score-card score-rep">
      <div class="score-label">REP SCORE</div>
      <div class="score-value">{{ t.scores.rep.value }}<span class="score-max">/100</span></div>
      <div class="score-verdict">{{ t.scores.rep.verdict }}</div>
    </div>
  </div>
  <!-- Design note callout -->
  {% if t.tool.designNote %}
  <div class="design-note">
    <span class="design-note-icon">📐</span>
    <p>{{ t.tool.designNote }}</p>
  </div>
  {% endif %}
</div>
```

**CSS for hero scores:**
```css
/* ─── Hero Scores ─────────────────────────────────────────────────────── */
.hero-scores {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1.5rem;
}
.score-card {
    background: var(--white);
    border: 1px solid var(--warm-border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
}
.score-label {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--text-light);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.score-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--navy-dark);
    line-height: 1;
}
.score-max { font-size: 1rem; font-weight: 400; color: var(--text-muted); }
.score-verdict {
    font-size: 0.8125rem;
    color: var(--text-body);
    margin-top: 0.5rem;
    line-height: 1.4;
}
.score-org { border-top: 3px solid var(--accent); }
.score-rep { border-top: 3px solid var(--navy-light); }
```

---

### 4. Section IDs for Tab Navigation

Each major section in `review.njk` needs an `id` attribute so the journey bar tabs can scroll to them. Add these IDs to the existing section wrappers:

| Section | ID to add |
|---|---|
| Pricing section | `id="pricing-reality"` |
| Who Should Use section | `id="who-should-use"` |
| Decision Snapshot section | `id="decision-snapshot"` |
| Where It Breaks section | `id="where-it-breaks"` |
| Stack Fit / Implementation section | `id="stack-fit"` |

---

### 5. Design Token Updates in `css/main.css`

Add these tokens to the `:root` block — they are referenced in the new components above but may not exist yet:

```css
/* Add to :root in css/main.css */
--navy-light: #2a4a6b;   /* may already exist — check first */
--accent-dark: #25a99d;  /* may already exist — check first */
```

Also update the font import to add the display font used in the v4 design:
```html
<!-- In _layouts/base.njk, update the Google Fonts link to: -->
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Serif+Display&display=swap" rel="stylesheet">
```

---

## Session Breakdown

### Session 1 — CSS + Journey Bar (work on `dev` branch)

**Goal:** Add all new CSS tokens and the journey bar component. No layout changes yet.

1. Add journey bar CSS to `css/main.css`
2. Add score card CSS to `css/main.css`  
3. Add sidebar CSS to `css/main.css`
4. Add journey bar HTML to `_layouts/review.njk` (below hero, above content)
5. Add section IDs to the 5 major sections in `review.njk`
6. Add IntersectionObserver JS to `js/main.js`
7. Update Google Fonts link in `_layouts/base.njk`

**Validation:** Build with Eleventy, open Clay page locally, confirm journey bar appears and tabs highlight on scroll. No layout change expected yet.

### Session 2 — Two-Column Layout + Sticky Sidebar (work on `dev` branch)

**Goal:** Implement the two-column grid and update the sidebar to match v4.

1. Wrap main content and sidebar in `.review-layout` grid in `review.njk`
2. Update sidebar HTML to match v4 spec: price block → CTA → At a Glance → Compare links
3. Ensure `_data/tools/clay.json` has all required sidebar fields (price, atAGlance rows, compare links)
4. Test sticky sidebar behaviour on scroll

**Validation:** Build and open Clay page. Confirm two-column layout, sticky sidebar, price visible, CTA button prominent.

### Session 3 — Hero Scores + Final Polish + PR to main (work on `dev` branch)

**Goal:** Move dual scores into hero, final visual polish, open PR.

1. Update hero section in `review.njk` to show dual scores above fold
2. Verify all 10 tool JSON files have `scores.org` and `scores.rep` fields — add if missing
3. Check mobile layout (sidebar stacks above content, journey bar scrolls horizontally)
4. Open a pull request from `dev` → `main` with a summary of all changes

**Validation:** Build all 10 pages, check 3 on mobile viewport. Open PR for Manus review before merging.

---

## What NOT to Change

- Do not change any content in the JSON data files — only add missing fields if needed
- Do not change the comparison pages or category pages — Phase 1 is tool pages only
- Do not change the homepage
- Do not remove or rename any existing CSS classes — only add new ones
- Do not change the Netlify Forms newsletter integration

---

## JSON Fields Required for v4 (check each tool's JSON)

Each `_data/tools/[tool].json` must have these fields for the new sidebar and hero:

```json
{
  "scores": {
    "org": { "value": 76, "verdict": "Strong for data-driven teams" },
    "rep": { "value": 42, "verdict": "High learning curve, rep-unfriendly" }
  },
  "sidebar": {
    "startingPrice": "$149",
    "pricingLabel": "/month (5,000 credits)",
    "ctaUrl": "/go/clay",
    "ctaText": "Visit Clay",
    "altText": "See Alternatives",
    "altUrl": "/compare/index.html",
    "atAGlance": [
      { "label": "G2 Rating", "value": "4.9/5" },
      { "label": "G2 Reviews", "value": "556" },
      { "label": "Pricing", "value": "Starts $149/mo" },
      { "label": "Free Trial", "value": "Yes" },
      { "label": "Category", "value": "Data Enrichment" }
    ],
    "comparisons": [
      { "text": "Clay vs Apollo", "url": "/compare/clay-vs-apollo.html" },
      { "text": "Clay vs Clearbit", "url": "/compare/clay-vs-clearbit.html" }
    ]
  }
}
```

Verify clay.json already has this structure (it should from Session 1). For the other 9 tools, add any missing fields using the same pattern.

---

## Validation Checklist (before opening PR)

- [ ] Journey bar appears on all 10 tool pages
- [ ] Active tab updates as user scrolls through sections
- [ ] Two-column layout on desktop (≥769px)
- [ ] Sidebar stacks above content on mobile (≤768px)
- [ ] Dual scores visible in hero without scrolling
- [ ] Sticky sidebar stays visible while scrolling content
- [ ] "Visit [Tool] ↗" CTA button is teal and prominent
- [ ] At a Glance stats populated for all 10 tools
- [ ] Zero template syntax leaks (`{{` or `{%`) in built HTML
- [ ] All 10 pages return 200 on live site after PR merge

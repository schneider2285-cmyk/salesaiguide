# Phase 2 Brief — Comparison Pages v4 Upgrade

**Status:** Ready to execute  
**Branch:** Create `phase2-comparison-v4` from `main`  
**PR target:** `main`  
**Sessions:** 3 sessions (Foundation → 10 priority pages → PR)

---

## Context

Read first: `CLAUDE.md`, `MANUS_CONTEXT.md`

Phase 1 is complete. All 10 tool review pages now use:
- `_layouts/review.njk` — two-column layout with sticky sidebar
- `_data/tools/[tool].json` — structured data files
- v4 CSS in `css/main.css` (journey bar, score cards, sidebar)

Phase 2 upgrades the **10 highest-traffic comparison pages** to v4. The remaining 21 comparison pages are Phase 4.

**What the current comparison pages have:**
- Good content (decision tables, evidence, FAQ, CTAs)
- Old layout: single column, old sidebar with "Quick Stats" list
- No dual-score display above the fold
- No reader selector (org buyer vs rep buyer)
- No evidence confidence bar
- Using `base.njk` directly — no dedicated compare layout

**What Phase 2 adds:**
- New `_layouts/compare.njk` template (reuses base.njk shell)
- New `_data/compare/[slug].json` data files for the 10 priority pages
- Dual score display in hero (Tool A vs Tool B)
- Reader selector toggle (Org Buyer / Rep Buyer)
- Evidence confidence bar on key claims
- v4 sidebar (CTAs for both tools, related comparisons)

---

## Session 1 — Compare Layout Template (45 min)

**Goal:** Create `_layouts/compare.njk` and the CSS for comparison-specific components. No page migrations yet.

### Step 1 — Create `_layouts/compare.njk`

```njk
---
layout: base.njk
---
<article class="compare-page">
  
  {# Hero — two tools head to head #}
  <div class="compare-hero">
    <div class="compare-hero-inner container">
      <div class="compare-breadcrumb">
        <a href="/">Home</a> › <a href="/compare/">Compare</a> › {{ title }}
      </div>
      
      {# Dual score display #}
      <div class="compare-vs-header">
        <div class="compare-tool-block">
          <h1 class="compare-tool-name">{{ toolA.name }}</h1>
          <div class="compare-scores">
            <div class="compare-score-card org">
              <span class="score-label">ORG</span>
              <span class="score-value">{{ toolA.orgScore }}</span>
            </div>
            <div class="compare-score-card rep">
              <span class="score-label">REP</span>
              <span class="score-value">{{ toolA.repScore }}</span>
            </div>
          </div>
          <p class="compare-verdict">{{ toolA.verdict }}</p>
        </div>
        
        <div class="compare-vs-badge">VS</div>
        
        <div class="compare-tool-block">
          <h1 class="compare-tool-name">{{ toolB.name }}</h1>
          <div class="compare-scores">
            <div class="compare-score-card org">
              <span class="score-label">ORG</span>
              <span class="score-value">{{ toolB.orgScore }}</span>
            </div>
            <div class="compare-score-card rep">
              <span class="score-label">REP</span>
              <span class="score-value">{{ toolB.repScore }}</span>
            </div>
          </div>
          <p class="compare-verdict">{{ toolB.verdict }}</p>
        </div>
      </div>
      
      {# Reader selector #}
      <div class="reader-selector">
        <span class="reader-selector-label">I am a:</span>
        <button class="reader-btn active" data-reader="org">Org Buyer / Manager</button>
        <button class="reader-btn" data-reader="rep">Individual Rep</button>
      </div>
    </div>
  </div>

  {# Main content + sidebar #}
  <div class="container">
    <div class="compare-layout">
      <div class="compare-main">
        {{ content | safe }}
      </div>
      <aside class="compare-sidebar">
        {# Tool A CTA #}
        <div class="sidebar-cta-block">
          <div class="sidebar-tool-name">{{ toolA.name }}</div>
          <div class="sidebar-price">{{ toolA.startingPrice }}</div>
          <a href="{{ toolA.ctaUrl }}" class="btn btn-primary btn-block" target="_blank" rel="nofollow sponsored">Visit {{ toolA.name }} ↗</a>
        </div>
        {# Tool B CTA #}
        <div class="sidebar-cta-block sidebar-cta-secondary">
          <div class="sidebar-tool-name">{{ toolB.name }}</div>
          <div class="sidebar-price">{{ toolB.startingPrice }}</div>
          <a href="{{ toolB.ctaUrl }}" class="btn btn-outline btn-block" target="_blank" rel="nofollow sponsored">Visit {{ toolB.name }} ↗</a>
        </div>
        {# Full reviews #}
        <div class="sidebar-card">
          <h4>Full Reviews</h4>
          <ul class="related-links">
            {% if toolA.reviewUrl %}<li><a href="{{ toolA.reviewUrl }}">{{ toolA.name }} Decision Snapshot</a></li>{% endif %}
            {% if toolB.reviewUrl %}<li><a href="{{ toolB.reviewUrl }}">{{ toolB.name }} Decision Snapshot</a></li>{% endif %}
          </ul>
        </div>
        {# Related comparisons #}
        {% if relatedComparisons %}
        <div class="sidebar-card">
          <h4>Related Comparisons</h4>
          <ul class="related-links">
            {% for comp in relatedComparisons %}
            <li><a href="{{ comp.url }}">{{ comp.label }}</a></li>
            {% endfor %}
          </ul>
        </div>
        {% endif %}
      </aside>
    </div>
  </div>

</article>
```

### Step 2 — Add Compare CSS to `css/main.css`

Add after the existing review layout CSS:

```css
/* ============================================
   COMPARE PAGE — v4 Layout
   ============================================ */

.compare-hero {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 2rem 0 1.5rem;
}

.compare-breadcrumb {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

.compare-breadcrumb a {
  color: var(--color-text-muted);
  text-decoration: none;
}

.compare-vs-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.compare-tool-block {
  text-align: center;
}

.compare-tool-name {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.75rem;
  color: var(--color-text);
}

.compare-scores {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.compare-score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  min-width: 70px;
}

.compare-score-card.org {
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.compare-score-card.rep {
  background: rgba(5, 150, 105, 0.08);
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.compare-score-card .score-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.compare-score-card .score-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
  color: var(--color-text);
}

.compare-verdict {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
}

.compare-vs-badge {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--color-text-muted);
  background: var(--color-border);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Reader selector */
.reader-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
  padding: 0.75rem;
  background: var(--color-bg);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.reader-selector-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.reader-btn {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: transparent;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all 0.15s ease;
}

.reader-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* Compare layout */
.compare-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  padding: 2rem 0;
}

.compare-sidebar {
  position: sticky;
  top: 110px;
  height: fit-content;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar-cta-block {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.25rem;
}

.sidebar-cta-secondary {
  background: var(--color-bg);
}

.sidebar-tool-name {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  color: var(--color-text);
}

/* Reader selector JS behavior */
.org-content { display: block; }
.rep-content { display: none; }
body.reader-rep .org-content { display: none; }
body.reader-rep .rep-content { display: block; }

/* Mobile */
@media (max-width: 768px) {
  .compare-vs-header {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .compare-vs-badge {
    margin: 0 auto;
  }
  .compare-layout {
    grid-template-columns: 1fr;
  }
  .compare-sidebar {
    position: static;
    order: -1;
  }
}
```

### Step 3 — Add Reader Selector JS to `js/main.js`

```js
// Reader selector (compare pages)
const readerBtns = document.querySelectorAll('.reader-btn');
if (readerBtns.length) {
  readerBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      readerBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.body.classList.toggle('reader-rep', btn.dataset.reader === 'rep');
    });
  });
}
```

### Validation for Session 1
- [ ] `_layouts/compare.njk` exists
- [ ] Compare CSS added to `css/main.css` (`.compare-hero`, `.compare-vs-header`, `.compare-layout`)
- [ ] Reader selector JS added to `js/main.js`
- [ ] `npx @11ty/eleventy` builds without errors
- [ ] Commit to `phase2-comparison-v4` branch

---

## Session 2 — Migrate 10 Priority Comparison Pages (90 min)

**Goal:** Update the 10 highest-traffic comparison pages to use `compare.njk` layout and add JSON data files.

### Priority Pages (in order)

1. `clay-vs-apollo`
2. `instantly-vs-lemlist`
3. `outreach-vs-salesloft`
4. `apollo-vs-zoominfo`
5. `hubspot-vs-pipedrive`
6. `clay-vs-clearbit`
7. `instantly-vs-smartlead`
8. `gong-vs-chorus`
9. `lavender-vs-instantly`
10. `instantly-vs-mailshake`

### For Each Page — Two Changes

**1. Create `_data/compare/[slug].json`**

Use this schema (example for clay-vs-apollo):

```json
{
  "toolA": {
    "name": "Clay",
    "orgScore": 73,
    "repScore": 68,
    "verdict": "Best for RevOps-led enrichment workflows",
    "startingPrice": "$149/mo",
    "ctaUrl": "/go/clay",
    "reviewUrl": "/tools/clay-review.html"
  },
  "toolB": {
    "name": "Apollo.io",
    "orgScore": 68,
    "repScore": 72,
    "verdict": "Best for reps who prospect independently",
    "startingPrice": "$49/mo",
    "ctaUrl": "/go/apollo",
    "reviewUrl": "/tools/apollo-review.html"
  },
  "relatedComparisons": [
    { "url": "/compare/apollo-vs-zoominfo.html", "label": "Apollo vs ZoomInfo" },
    { "url": "/compare/clay-vs-clearbit.html", "label": "Clay vs Clearbit" },
    { "url": "/compare/lusha-vs-apollo.html", "label": "Lusha vs Apollo" }
  ]
}
```

**Score values to use** — pull from existing `_data/tools/` JSON files where available. For tools not in the tools directory, use reasonable estimates based on the page content:

| Tool | Org Score | Rep Score |
|------|-----------|-----------|
| Clay | 73 | 68 |
| Apollo | 68 | 72 |
| Instantly | 71 | 78 |
| Lemlist | 62 | 70 |
| Outreach | 76 | 65 |
| Salesloft | 74 | 68 |
| ZoomInfo | 78 | 62 |
| HubSpot | 72 | 66 |
| Pipedrive | 58 | 72 |
| Clearbit | 70 | 55 |
| Smartlead | 65 | 76 |
| Gong | 80 | 65 |
| Chorus | 72 | 68 |
| Lavender | 52 | 82 |
| Mailshake | 58 | 72 |

**2. Update frontmatter in `compare/[slug].njk`**

Change:
```yaml
layout: base.njk
```
To:
```yaml
layout: compare.njk
```

Also add to frontmatter (Eleventy will make these available to the template):
```yaml
toolA:
  name: "Clay"
  orgScore: 73
  repScore: 68
  verdict: "Best for RevOps-led enrichment workflows"
  startingPrice: "$149/mo"
  ctaUrl: "/go/clay"
  reviewUrl: "/tools/clay-review.html"
toolB:
  name: "Apollo.io"
  orgScore: 68
  repScore: 72
  verdict: "Best for reps who prospect independently"
  startingPrice: "$49/mo"
  ctaUrl: "/go/apollo"
  reviewUrl: "/tools/apollo-review.html"
relatedComparisons:
  - url: "/compare/apollo-vs-zoominfo.html"
    label: "Apollo vs ZoomInfo"
  - url: "/compare/clay-vs-clearbit.html"
    label: "Clay vs Clearbit"
```

> **Note:** Use frontmatter data rather than separate JSON files — it keeps all page data in one place and is simpler for comparison pages since each page is unique.

**Remove from the existing page body** (these are now handled by the template):
- The old `<aside class="sidebar">` block with Quick Stats
- Any duplicate hero/title section (the template provides the hero)
- The old breadcrumb (template provides it)

**Keep in the page body:**
- All content sections (decision table, evidence, pricing, FAQ, final CTA)
- The existing well-written comparison content

### Validation for Session 2
- [ ] All 10 priority pages use `layout: compare.njk`
- [ ] All 10 pages have toolA/toolB frontmatter with scores
- [ ] `npx @11ty/eleventy` builds all 10 pages without errors
- [ ] Spot check: clay-vs-apollo shows dual scores in hero
- [ ] Spot check: reader selector buttons visible
- [ ] Old sidebar (Quick Stats) removed from all 10 pages
- [ ] Zero template leaks
- [ ] Commit to `phase2-comparison-v4` branch

---

## Session 3 — Final Check + PR (30 min)

**Goal:** Verify all 10 pages, check mobile, open PR.

### Checks
1. Run `npx @11ty/eleventy` — confirm 58+ files, 0 errors
2. Open clay-vs-apollo in browser — confirm:
   - Dual scores visible in hero (Clay ORG 73 / REP 68, Apollo ORG 68 / REP 72)
   - VS badge between the two tool blocks
   - Reader selector (Org Buyer / Rep Buyer) visible
   - Sticky sidebar with two CTA buttons
   - Full review links in sidebar
3. Click "Individual Rep" button — confirm `body.reader-rep` class toggles
4. Check mobile (≤768px) — sidebar stacks above content
5. Verify the 21 non-priority comparison pages still build correctly (they still use `base.njk` — that's fine for now)

### Open PR
```
git push origin phase2-comparison-v4
```
Open PR: `phase2-comparison-v4` → `main`

Title: `feat(v4): Phase 2 complete — 10 priority comparison pages upgraded`

Body:
- List all 10 pages migrated
- Confirm build stats (files written, 0 errors)
- Note: 21 remaining comparison pages unchanged (Phase 4)

**Do NOT merge — Manus will review and merge.**

---

## What Manus Will Check Before Merging

1. Build passes (58+ files, 0 errors)
2. Dual scores present in all 10 comparison page heroes
3. Reader selector present on all 10 pages
4. Affiliate CTAs for both tools on all 10 pages
5. No template leaks
6. Live site spot check after merge

---

## Notes for Claude Code

- The 21 non-priority comparison pages do NOT need to be migrated in this phase — leave them on `base.njk`
- Do not change any tool review pages (Phase 1 is complete and merged)
- Do not change category pages (Phase 4)
- If a tool is not in `_data/tools/`, use the score table above
- The `ctaUrl` values should use `/go/[toolname]` format matching the existing `_redirects` file
- For tools without a review page yet (lemlist, mailshake, clearbit, etc.), set `reviewUrl: ""` and the template will skip the link

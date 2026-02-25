# Brief: Design Fixes & Polish Pass
**Assigned to:** Claude Code  
**Priority:** High  
**Estimated sessions:** 2  
**Branch:** `design-fixes-polish`

---

## Context

Manus conducted a full page-by-page design audit on Feb 25 2026. The following issues were identified across all major page types. This brief covers all of them in one pass. Do NOT merge — Manus reviews the PR.

---

## CRITICAL BUG — Fix First

### 1. Persona hub pages: Markdown not rendering

**Pages affected:** `for-sales-reps.njk`, `for-sales-managers.njk`, `for-revenue-ops.njk`

**Problem:** The main body content on all 3 persona hub pages is rendering as raw Markdown text — `##`, `**bold**`, `###` symbols are visible on the page instead of being parsed as HTML.

**Root cause:** The `persona.njk` layout is outputting the page content with `{{ content }}` instead of `{{ content | safe }}`, OR the content is being written as Markdown in the `.njk` file without a Markdown filter applied.

**Fix:** In `_layouts/persona.njk`, find where `{{ content }}` is used in the main body area and change it to use the Eleventy Markdown filter. If the content is inline Nunjucks (not a separate `.md` file), wrap the content block in a `{% markdown %}` tag or convert the body content to proper HTML.

**Verify:** After fix, `/for-sales-reps/` should show formatted headings, bold text, tables, and links — not raw Markdown symbols.

---

## Session 1 — Logo Redesign

### 2. Logo: Replace text placeholder with proper wordmark

**File:** `_includes/navbar.html` (or wherever the logo HTML lives)

**Current state:** The logo is plain text "SalesAIGuide" with a CSS highlight on "AI". It looks like a placeholder.

**Fix:** Create an inline SVG wordmark directly in the navbar HTML. Design spec:
- Font: Use a bold geometric sans-serif feel (can be achieved with SVG text + letter-spacing)
- Layout: Icon mark (a small chart/graph or "S" monogram) + "Sales**AI**Guide" wordmark beside it
- Colors: White text for "Sales" and "Guide", bright teal (`#00D4AA`) for "AI"
- Size: ~140px wide, 32px tall — fits the existing navbar height
- No external font dependency — use SVG paths or system fonts

If SVG is complex, an acceptable alternative is: keep the text logo but add a small SVG icon mark to the left (a simple bar chart or signal icon in teal), and improve the typography with `font-weight: 800`, `letter-spacing: -0.5px`, and remove the dashed underline effect.

**Do not** use an `<img>` tag — keep it inline SVG or styled HTML so it renders instantly without a network request.

---

## Session 1 — Homepage Fixes

### 3. Persona entry cards: Replace dashed borders and emoji icons

**File:** `index.njk` and `css/main.css`

**Current state:** The 3 persona cards (Sales Reps, Sales Managers, Revenue Ops) have dashed green borders and emoji icons (👤 📊 ⚙).

**Fix:**
- Replace dashed borders with solid 1px borders using `border: 1px solid rgba(0, 212, 170, 0.3)` and a subtle `box-shadow: 0 2px 12px rgba(0,0,0,0.08)`
- Replace emoji icons with inline SVG icons. Use these simple SVGs:
  - Sales Reps: person/user icon (single figure)
  - Sales Managers: team icon (two figures)
  - Revenue Ops: chart/graph icon (bar chart)
- Icon size: 32px × 32px, color: `#00D4AA`

### 4. Tool cards: Fix "Category" button label

**File:** `index.njk`

**Current state:** The "Category" button on each tool card shows the literal text "Category" instead of the actual category name.

**Fix:** The tool card template should use the tool's `category` field from the JSON data. Find the button that says "Category" and replace with `{{ tool.category }}` (or whatever the correct data field is). Check `_data/tools/clay.json` to confirm the field name.

### 5. Homepage: Fix "View All 75+ Tools" count

**File:** `index.njk`

**Current state:** The link says "View All 75+ Tools →" but the site only has 20 reviewed tools.

**Fix:** Change to "View All 20 Reviewed Tools →" or simply "Browse All Tools →". The `/tools/index.html` page should be the destination.

---

## Session 2 — Cross-Site Polish

### 6. Journey bar tabs on tool review pages: Remove dashed borders

**File:** `css/main.css` (the `.journey-bar` or `.journey-tab` styles)

**Current state:** The sticky journey bar tabs (Pricing Reality, Who Should Use, etc.) have dashed green borders — same rough look as the persona cards.

**Fix:** Replace dashed borders with clean solid borders or no border at all. Use a bottom-border indicator for the active tab instead:
```css
.journey-tab.active {
  border-bottom: 2px solid #00D4AA;
  background: transparent;
}
.journey-tab {
  border: none;
  border-bottom: 2px solid transparent;
}
```

### 7. Comparison page hero: Add subtle background treatment

**File:** `css/main.css` (the `.compare-hero` styles)

**Current state:** The comparison page hero is plain white/light — it feels flat compared to the dark tool review page hero.

**Fix:** Add a subtle dark gradient background to the compare hero section:
```css
.compare-hero {
  background: linear-gradient(135deg, #0f1a2e 0%, #1a2d4a 100%);
  color: white;
}
```
Ensure the tool names, scores, and VS divider all remain readable on the dark background. Update text colors if needed.

### 8. Category page: Add dark hero section

**File:** `_layouts/category.njk` and `css/main.css`

**Current state:** Category pages have a plain light header with just the category tag, h1, subtitle, and metadata. It looks unfinished compared to the tool review and comparison pages.

**Fix:** Wrap the category page header in a dark hero section matching the site's dark navy style:
```css
.category-hero {
  background: linear-gradient(135deg, #0f1a2e 0%, #1a2d4a 100%);
  color: white;
  padding: 3rem 0 2.5rem;
}
```
The category tag pill, h1, subtitle, and metadata (tools reviewed, updated date) should all render on the dark background. Adjust text colors to white/light.

### 9. 404 page: Fix navbar — "How We Score" and "About" links missing

**Current state:** The 404 page navbar is missing "How We Score" and "About" links that appear on all other pages. It also shows a different footer.

**Fix:** Ensure the 404 page uses the same `base.njk` layout as all other pages, or manually add the missing nav links to match the standard navbar.

---

## Build & Validation

After all fixes:
1. Run `npm run build` — confirm 0 errors
2. Check `/for-sales-reps/` — body content renders as formatted HTML, not raw Markdown
3. Check homepage — persona cards have solid borders, tool cards show real category names, count is corrected
4. Check `/tools/clay-review.html` — journey bar tabs have clean borders
5. Check `/compare/clay-vs-apollo` — hero has dark background
6. Check `/categories/cold-outreach.html` — hero has dark background
7. Check 404 page — navbar matches the rest of the site

Open a PR. Do NOT merge — Manus reviews.

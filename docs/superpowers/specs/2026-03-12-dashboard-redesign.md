# Ops Dashboard Redesign: Mission Control with Narrative

## Overview
Redesign the ops dashboard at `/ops/` to solve three problems: at-a-glance health visibility, narrative explanation of what agents do/did/plan, and progress tracking over time. Power-user audience (dense data OK). A+C hybrid: structured zones with narrative text.

## File Contract
All 4 workstreams reference these shared contracts.

### HTML IDs (JS binds to these)
```
#alert-banner          - Zone 1 container (hidden when no alerts)
#alert-list            - UL inside alert banner
#score-ring            - SVG score ring
#score-value           - Score number text
#score-delta           - Delta badge (+39)
#narrative-summary     - Paragraph element for narrative text
#stat-issues-found     - Mini stat value
#stat-issues-fixed     - Mini stat value
#stat-autofix-coverage - Mini stat value
#stat-pages-monitored  - Mini stat value
#activity-feed         - Activity feed container
#agent-{key}           - Agent cards (sitehealth, revenuefunnel, etc.)
#agent-{key}__score    - Score display in card
#agent-{key}__desc     - Description text
#agent-{key}__metric   - Primary metric
#agent-{key}__action   - Last action text
#agent-{key}__plan     - Plan/strategy text
#agent-{key}__spark    - Sparkline container
#checklist-body        - Action checklist container
#agent-plans-body      - Strategic plans container
#autofix-grid          - Auto-fix capabilities grid
#deep-revenue          - Collapsible: revenue leaks
#deep-affiliate        - Collapsible: affiliate inventory
#deep-content          - Collapsible: content pipeline
#deep-history          - Collapsible: run history
```

### CSS Class Naming (BEM)
```
.mc-alert         .mc-alert--p0  .mc-alert--p1  .mc-alert--clear
.mc-header        .mc-header__ring  .mc-header__narrative  .mc-header__stats
.mc-stat          .mc-stat__label  .mc-stat__value
.mc-feed          .mc-feed__item  .mc-feed__icon  .mc-feed__text  .mc-feed__time
.mc-grid          .mc-grid__card
.mc-card          .mc-card__header  .mc-card__score  .mc-card__desc
                  .mc-card__metric  .mc-card__action  .mc-card__plan  .mc-card__spark
.mc-card--healthy .mc-card--warning .mc-card--critical
.mc-checklist     .mc-checklist__item  .mc-checklist__check  .mc-checklist__priority
.mc-plans         .mc-plans__item  .mc-plans__agent  .mc-plans__text
.mc-autofix       .mc-autofix__item  .mc-autofix--yes  .mc-autofix--no
.mc-deep          .mc-deep__section  .mc-deep__toggle
.mc-table         (reuse existing table styles with mc- prefix)
.mc-ring          .mc-ring__circle  .mc-ring__text
.score-green .score-yellow .score-red (color utility classes)
```

### Data Structures

**agent-state.json additions per agent:**
```json
{
  "description": "Monitors page titles, meta descriptions, OG tags, and site-wide HTML quality",
  "lastAction": "Fixed 159 title, meta, and OG tag issues across 157 pages",
  "plan": {
    "reactive": "Auto-fixes title length, meta descriptions, OG tags, and freshness dates on next scan",
    "strategic": "Targeting 100% compliance on all HTML quality checks"
  }
}
```

**ops/data/activity-log.json:**
```json
{
  "lastUpdated": "2026-03-12T15:00:00Z",
  "entries": [
    {
      "timestamp": "2026-03-12T15:00:00Z",
      "agent": "sitehealth",
      "icon": "🏥",
      "action": "Fixed 159 title, meta description, and OG tag issues across 157 pages",
      "type": "fix",
      "impact": "Score improved from 0 to 95"
    }
  ]
}
```

## Zone Specs

### Zone 1: Alert Banner
- Red gradient bar for P0, amber for P1. Hidden when no active alerts.
- Icon + count + scrolling one-liner summaries
- Pulls from `revenueops.actionQueue` where status != "completed"
- Pulsing dot animation for P0

### Zone 2: Narrative Score Header
- Left: 120px SVG donut ring, stroke-dasharray animated. Score number centered. Color: green ≥80, yellow ≥50, red <50.
- Delta badge: "+39" in green pill if positive, red if negative.
- Right: `<p>` narrative auto-generated from data: "Your site scored {score}/100 on {date} — up from {prevScore}. {fixedCount} issues fixed this cycle. Auto-repair monitors {autoFixCount} issue types."
- Below: 4 stat cards in a row.

### Zone 3: Activity Feed
- Max 10 entries visible, scrollable.
- Each entry: colored left border (matches agent status color) + icon + agent name bold + action text + relative time ("2h ago").
- Newest first.

### Zone 4: Agent Grid (3x3)
- Cards have colored top border (4px, green/yellow/red based on score).
- Layout per card:
  - Row 1: Icon + Name + Score badge (large, right-aligned)
  - Row 2: Description (muted text, 1 line)
  - Row 3: Primary metric (bold number + label)
  - Row 4: Last action (small, muted, italic)
  - Row 5: Plan/Next (small, blue text, what it WILL do)
  - Row 6: Sparkline
- Null-score agents (contentengine, revenueops) show "Analysis" badge instead of score.

### Zone 5a: "What's Next" Checklist
- Each item: checkbox + priority badge + description + source agent pill
- Items with status "completed" get strikethrough + green check
- Pull from revenueops.actionQueue

### Zone 5b: "Agent Strategy" Panel
- For each agent, show its `plan.strategic` in a compact grid:
  - 3 columns, each card: agent icon + name + strategic plan text
  - Only show agents that have strategic plans (skip never_run)

### Zone 6: "How Auto-Repair Works"
- 2-column grid of capability pills
- Left column "Auto-Repairs" (green checks): prices, titles, metas, OG tags, freshness, banned phrases, demo CTAs, name leaks
- Right column "Manual Review" (red X): orphan links, schemas, new content
- Brief intro: "The agent system runs weekly. On each cycle it auto-repairs {N} issue types and flags {M} for your review."

### Zone 7: Deep Dive (Collapsible)
- Each section wrapped in `<details><summary>` with styled toggle
- Revenue Leaks, Affiliate Inventory, Content Pipeline, Run History
- Tables reuse existing column structure but new mc- styles

## Visual Design
- Dark theme (keep existing color tokens)
- More contrast between zones (subtle section dividers, not just whitespace)
- Cards get subtle gradient backgrounds instead of flat
- Score colors: green #10b981, yellow #f59e0b, red #ef4444
- Accent blue #3b82f6 for interactive/plan elements
- Purple #8b5cf6 for strategic/future elements
- Font sizes: body 14px, headings 16-18px, scores 28-32px, labels 11px
- Animations: score ring fills on load, activity feed items fade in, alert bar pulses

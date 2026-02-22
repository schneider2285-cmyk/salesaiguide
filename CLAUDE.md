# SalesAIGuide - Project Context

## What This Is
AI-automated affiliate directory for sales AI tools. Generates revenue through affiliate commissions when visitors click through to tools like Clay, Instantly, Apollo, and Gong.

**Owner:** Matt (Enterprise Sales Executive) — 30-60 min/week maintenance budget
**Goal:** $1,000-3,000/month passive revenue within 12 months
**Live site:** https://salesaiguide.com
**Repo:** schneider2285-cmyk/salesaiguide

## Architecture

```
Data Sources (G2/Capterra) → Data Agent → Airtable → Content Agent (Claude API)
→ Matt Approves → Publish Agent → GitHub → Netlify (auto-deploy)
```

### Agent Status
| Agent | Platform | Status | Trigger |
|-------|----------|--------|---------|
| Content Agent | Make.com | Working | Every 1 hour |
| Publish Agent | GitHub Actions | Working | Every 2 hours + manual |
| Data Agent | Claude Code + `scripts/data-check.js` | Working | Weekly (manual) |

### Key Infrastructure
| Service | Details |
|---------|---------|
| Airtable | Base ID: `appzCII2ZxjERaF60` — Tools, Categories, Comparisons tables |
| Netlify | Site ID: `c79f346d-e91d-42cf-80e2-295f8d7095e9` |
| GitHub Actions | `deploy.yml` (Netlify deploy on push), `publish.yml` (Airtable → HTML) |

## Agent System

Seven specialized agents in `.claude/agents/`, orchestrated via `coordination/`:

| Agent | File | Role | Trigger |
|-------|------|------|---------|
| **Publish Agent** | `publish-agent.md` | Airtable → HTML generation → deploy | Every 2h (automated) or manual |
| **Site Builder** | `site-builder.md` | Create/maintain HTML pages and CSS | When new pages needed |
| **SEO Auditor** | `seo-auditor.md` | Verify 13-point SEO checklist on all pages | Before every push |
| **Content Reviewer** | `content-reviewer.md` | Quality, accuracy, conversion optimization | After new pages published |
| **Deployment Agent** | `deployment-agent.md` | Git operations, push, verify deploy | After any file changes |
| **Data Agent** | `data-agent.md` | Monitor data freshness, spot-check G2/vendor sites | Weekly (manual trigger) |
| **Analytics Tracker** | `analytics-tracker.md` | Status reports, content coverage metrics | Weekly review |

### Coordination Files
```
coordination/
├── active_work.json          # Currently active tasks
├── completed_work.json       # Done log (append-only)
├── planned_work_queue.json   # Prioritized backlog
├── standards.md              # Output formats, quality rules, naming conventions
└── workflows/
    └── daily_pipeline.md     # Agent sequence and handoff format
```

### Daily Pipeline Sequence
```
Data Agent (weekly) → Content Agent (Make.com, hourly) → Matt Approves (Airtable) →
Publish Agent (GitHub Actions, 2h) → SEO Auditor (verify) →
Deployment Agent (git push) → Netlify (auto-deploy)
```

### Data Pipeline (Weekly)
```
Data Agent (scripts/data-check.js) → Freshness Report →
Matt Reviews → Updates Airtable → Content Agent picks up changes
```

See `coordination/workflows/daily_pipeline.md` for full details.

## File Structure

```
salesaiguide/
├── index.html              # Homepage
├── 404.html                # Custom error page
├── about.html / disclosure.html
├── favicon.svg             # SVG favicon (navy + electric blue)
├── _redirects              # Netlify affiliate /go/[tool] redirects
├── sitemap.xml / robots.txt
├── css/main.css            # Global styles
├── css/review.css          # Review/comparison page styles
├── js/main.js              # Analytics + interactions
├── compare/                # 10 comparison pages + index
├── categories/             # 10 category pages + index
├── tools/                  # Tool reviews + directory index
├── blog/                   # Resources stub
├── scripts/
│   └── publish.js          # Publish Agent (Node.js)
├── docs/
│   └── project-brief.md    # Full project context
├── context/
│   └── session-summary.md  # Ephemeral session handoff (overwritten each session)
├── coordination/           # Agent orchestration
│   ├── active_work.json
│   ├── completed_work.json
│   ├── planned_work_queue.json
│   ├── standards.md
│   └── workflows/daily_pipeline.md
├── .claude/agents/         # Agent definitions
│   ├── publish-agent.md
│   ├── site-builder.md
│   ├── seo-auditor.md
│   ├── content-reviewer.md
│   ├── deployment-agent.md
│   └── analytics-tracker.md
└── .github/workflows/
    ├── deploy.yml           # Netlify auto-deploy on push
    └── publish.yml          # Publish Agent cron (every 2h)
```

## Design System

| Token | Value | Usage |
|-------|-------|-------|
| Navy dark | `#0a192f` | Backgrounds, nav, footer |
| Navy medium | `#112240` | Cards, hero gradients |
| Electric blue | `#00d9ff` | Accents, CTAs, highlights |
| Success green | `#10b981` | Ratings, positive indicators |
| Star yellow | `#fbbf24` | Star ratings |
| Font | System stack | `-apple-system, BlinkMacSystemFont, 'Segoe UI'...` |

## Affiliate Link Pattern

All affiliate links use `/go/[tool-slug]` (managed via `_redirects`). When affiliate URLs change, update `_redirects` only — no page edits needed.

## Airtable Schema (3 linked tables)

**Tools** (30 records): Name, Slug, Website, Tagline, Category (linked), Pricing Model, Starting Price, G2 Rating, G2 Reviews, Best For, Status, Description, Affiliate Link

**Categories** (10): Name, Slug, Icon, Description, Display Order, Tools (linked)

**Comparisons** (10+): Tool A (linked), Tool B (linked), Title (formula), Slug (formula), Verdict, Status (Draft→Review→Approved→Published), Published (checkbox)

## Content Pipeline

1. **Content Agent** (Make.com) finds Draft items in Airtable → calls Claude API → generates descriptions/verdicts → sets Status = "Review"
2. **Matt** reviews in Airtable → approves (Status = "Approved")
3. **Publish Agent** (GitHub Actions) finds Approved items → generates HTML → commits to repo → Netlify auto-deploys → updates Airtable (Status = "Published")

## Secrets Required (GitHub)

| Secret | Purpose |
|--------|---------|
| `AIRTABLE_TOKEN` | Publish Agent reads/writes Airtable |
| `NETLIFY_AUTH_TOKEN` | Deploy workflow |
| `NETLIFY_SITE_ID` | Deploy workflow |
| `PAT_TOKEN` | Publish workflow push (triggers deploy) |

## Development Rules

- **Static HTML only** — no build tools, no frameworks
- **Dark navy theme** — all pages match the design system above
- **SEO on every page** — canonical URL, OG tags, JSON-LD, sitemap entry
- **Mobile responsive** — hamburger nav at 768px breakpoint
- **Favicon** — `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`
- **Affiliate links** — always use `/go/[slug]`, never hardcode partner URLs in pages

## Project Context

This project uses a **two-tool workflow**:

| Tool | Purpose |
|------|---------|
| **Claude.ai** (chat) | Strategic planning, decisions, content review |
| **Claude Code** (CLI) | Engineering, file changes, deployments |

### Rules for Claude Code Sessions

1. **Canonical project brief** lives at `docs/project-brief.md` — this is the source of truth
2. When Matt pastes updated context from Claude.ai, **update `docs/project-brief.md`** with the new information
3. When Matt says **"wrap up"**, write a session summary to `context/session-summary.md` that he can carry back to Claude.ai. Include: what was done, what changed, current state, next steps
4. **Session summaries** in `context/` are ephemeral — overwritten each session. The brief is permanent
5. Always read `CLAUDE.md` and `docs/project-brief.md` at session start for full context

### Session Summary Format

```markdown
# Session Summary — [Date]

## What Was Done
- [Bullet list of completed work]

## Files Changed
- [List of added/modified/deleted files]

## Current State
- [What's working, what's not]

## Next Steps
- [What Matt should do next]
- [What the next Claude Code session should tackle]
```

## Full Project Brief

See [docs/project-brief.md](docs/project-brief.md) for complete context including credentials, revenue projections, agent specifications, and roadmap.

# Agent Pipeline — SalesAIGuide

## Dependency Graph

```
                            ┌──────────────────────────────────────────────────────┐
                            │              WEEKLY CYCLE (Friday)                    │
                            │                                                      │
                            │   ┌─────────────┐      ┌────────────────┐            │
                            │   │ Data Agent  │      │Analytics Tracker│            │
                            │   │(data-check) │      │ (site metrics) │            │
                            │   └──────┬──────┘      └───────┬────────┘            │
                            │          │  PARALLEL            │                     │
                            │          └──────────┬───────────┘                     │
                            │                     ▼                                 │
                            │          ┌────────────────────┐                       │
                            │          │  Matt Reviews Both │                       │
                            │          │  Reports (Airtable)│                       │
                            │          └─────────┬──────────┘                       │
                            │                    │ updates stale records            │
                            └────────────────────┼──────────────────────────────────┘
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                        CONTINUOUS CYCLE (hourly/2h)                                   │
│                                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                            │
│  │Content Agent │───▶│ Matt Approves│───▶│Publish Agent │                            │
│  │ (Make.com)   │    │ (Airtable)   │    │(publish.js)  │                            │
│  │   hourly     │    │   manual     │    │  every 2h    │                            │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                            │
│                                                 │ new HTML files                     │
│                                                 ▼                                    │
│                                   ┌──────────────────────────┐                       │
│                                   │      PARALLEL GATE       │                       │
│                                   │                          │                       │
│                                   │  ┌──────────┐ ┌────────────────┐                 │
│                                   │  │SEO Auditor│ │Content Reviewer│                │
│                                   │  │(13-point) │ │ (quality/CTA)  │                │
│                                   │  └─────┬────┘ └───────┬────────┘                 │
│                                   │        └──────┬───────┘                          │
│                                   └───────────────┼──────────────────┘               │
│                                                   ▼                                  │
│                                        ┌──────────────────┐                          │
│                                        │Deployment Agent  │                          │
│                                        │(git push → live) │                          │
│                                        └──────────────────┘                          │
└──────────────────────────────────────────────────────────────────────────────────────┘

ON-DEMAND (any time):
  Site Builder ───▶ [SEO Auditor ‖ Content Reviewer] ───▶ Deployment Agent
```

---

## Agent Execution Order

### Tier 0 — No Dependencies (can always run)

| Agent | Trigger | Why independent |
|-------|---------|-----------------|
| **Data Agent** | Weekly / manual | Reads Airtable + public web. No repo file inputs needed. |
| **Analytics Tracker** | Weekly / manual | Reads repo files only. No external state needed. |
| **Content Agent** (Make.com) | Hourly (external) | Reads Airtable Drafts. Fully external to this repo. |

> **Tier 0 agents can run in parallel with each other and with any other tier.**

### Tier 1 — Depends on Airtable State

| Agent | Waits for | Input signal |
|-------|-----------|-------------|
| **Publish Agent** | Content Agent + Matt approval | Airtable: `Status = "Approved"` AND `Published = false` |

### Tier 2 — Depends on File Changes (parallelizable with each other)

| Agent | Waits for | Input signal |
|-------|-----------|-------------|
| **SEO Auditor** | Publish Agent OR Site Builder | New/modified `.html` files in repo |
| **Content Reviewer** | Publish Agent OR Site Builder | New/modified `.html` files in repo |

> **SEO Auditor and Content Reviewer ALWAYS run in parallel.** They check different things on the same files and never conflict.

### Tier 3 — Depends on All Verification Complete

| Agent | Waits for | Input signal |
|-------|-----------|-------------|
| **Deployment Agent** | SEO Auditor AND Content Reviewer | Both agents report clean or fixes applied |

### On-Demand (No Fixed Tier)

| Agent | Trigger | Feeds into |
|-------|---------|------------|
| **Site Builder** | Matt requests new pages | Tier 2 (SEO Auditor + Content Reviewer) |

---

## Four Workflows

### Workflow 1: Continuous Content Pipeline

The primary revenue-generating loop. Runs automatically.

```
Content Agent → Matt → Publish Agent → [SEO Auditor ‖ Content Reviewer] → Deployment Agent
```

| Step | Agent | Platform | Trigger | Input | Output | Handoff Signal |
|------|-------|----------|---------|-------|--------|----------------|
| 1 | Content Agent | Make.com | Every 1h (cron) | Airtable records: `Status="Draft"`, empty Description/Verdict | Updated records with content, `Status="Review"` | Airtable Status field = `"Review"` |
| 2 | Matt (human) | Airtable UI | Manual (Friday review) | Airtable records: `Status="Review"` | Records set to `Status="Approved"` | Airtable Status field = `"Approved"` |
| 3 | Publish Agent | GitHub Actions | Every 2h (cron) + manual dispatch | Airtable records: `Status="Approved"`, `Published=false` | HTML files in `compare/`, updated `sitemap.xml`, updated `compare/index.html`, Airtable marked Published | New `.html` files exist in working tree |
| 4a | SEO Auditor | Claude Code | After Step 3 | All `.html` files (focus on new ones) | Fixed HTML (missing SEO tags added), audit report | Report printed; files modified in-place |
| 4b | Content Reviewer | Claude Code | After Step 3 (parallel with 4a) | All `.html` files (focus on new ones) | Fixed HTML (placeholder text, broken CTAs), review report | Report printed; files modified in-place |
| 5 | Deployment Agent | Claude Code | After 4a AND 4b complete | Modified files in repo | Git commit + push → Netlify auto-deploys in 30-60s | `git log` shows new commit; Netlify deploy succeeds |

#### Step 1 Detail: Content Agent

**What it produces (Airtable record changes):**

For Tools:
```
Field: Description → 150-200 word AI-generated description
Field: Status → "Review"
```

For Comparisons:
```
Field: Verdict → 200-300 word comparison verdict
Field: Status → "Review"
```

**Failure mode:** If Make.com scenario fails, records stay at `Status="Draft"`. No downstream impact — Publish Agent simply finds nothing to publish.

#### Step 3 Detail: Publish Agent

**What it produces (files):**

```
compare/{tool-a}-vs-{tool-b}.html    ← New comparison page
compare/index.html                    ← Updated with new card
sitemap.xml                           ← New URL entry appended
```

**What it changes (Airtable):**

```
Field: Status → "Published"
Field: Published → true
Field: Date Published → today's date (YYYY-MM-DD)
```

**Failure mode:** If Airtable API times out, nothing publishes. Retries automatically on next 2h cycle.

#### Steps 4a + 4b Detail: Parallel Verification Gate

Both agents read the same HTML files but check **non-overlapping concerns**:

| Check | SEO Auditor | Content Reviewer |
|-------|:-----------:|:----------------:|
| `<title>` present and <60 chars | ✅ | |
| `<meta name="description">` 150-160 chars | ✅ | |
| `<link rel="canonical">` with full URL | ✅ | |
| Open Graph tags (5 required) | ✅ | |
| Twitter Card tags (3 required) | ✅ | |
| Favicon link | ✅ | |
| JSON-LD structured data | ✅ | |
| Entry in `sitemap.xml` | ✅ | |
| No placeholder text | | ✅ |
| CTAs use `/go/[slug]` pattern | | ✅ |
| `target="_blank" rel="nofollow noopener"` on CTAs | | ✅ |
| Pricing/ratings displayed correctly | | ✅ |
| Verdict balanced and actionable | | ✅ |
| "Updated [Month] [Year]" date badge | | ✅ |
| Star ratings render correctly | | ✅ |
| Category names match Airtable | | ✅ |
| Internal links resolve (no 404s) | | ✅ |

**Merge rule:** If either agent modifies files, Deployment Agent commits ALL changes in a single commit. They never edit the same lines — SEO Auditor touches `<head>` elements, Content Reviewer touches `<body>` content.

#### Step 5 Detail: Deployment Agent

**Pre-push checklist** (must ALL pass):

```
[ ] No unclosed HTML tags in modified files
[ ] All referenced CSS/JS assets exist
[ ] sitemap.xml is valid XML
[ ] _redirects has no duplicate slugs
[ ] No API tokens or secrets in any committed file
[ ] All /go/ slugs in HTML files have matching _redirects entry
```

**Commit format:**

```
<type>(<scope>): <description>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`
Scopes: `compare`, `tools`, `categories`, `blog`, `seo`, `auto`, `deploy`

**Post-push verification:**
1. `git log -1` shows expected commit
2. Wait 60 seconds for Netlify
3. `WebFetch` the new page URL to confirm 200 response

---

### Workflow 2: Weekly Data Refresh

Keeps Airtable accurate. Runs once a week during Friday review.

```
[Data Agent ‖ Analytics Tracker] → Matt Reviews → Updates Airtable → Content Agent picks up changes
```

| Step | Agent | Trigger | Input | Output | Handoff |
|------|-------|---------|-------|--------|---------|
| 1a | Data Agent | Manual: `node scripts/data-check.js` | Airtable API (all 30 tools), local repo files | Data Freshness Report (console markdown) | Matt reads report |
| 1b | Analytics Tracker | Manual: Claude Code session | All repo files via Glob/Grep | Site Status Report (console markdown) | Matt reads report |
| 2 | Matt (human) | After reading both reports | Freshness report + status report | Updated Airtable records; decisions on next priorities | Airtable fields updated |
| 3 | Content Agent | Next hourly cycle | Any records Matt set back to Draft | Regenerated content | Status = "Review" |

> **Steps 1a and 1b run in parallel** — they have zero dependencies on each other.

#### Data Agent Report Format

```markdown
# Data Freshness Report — YYYY-MM-DD

## Summary
- Tools checked: X/30
- Fresh (<30 days): Y
- Stale (>30 days): Z
- Critical (>90 days): W

## Changes Detected
| Tool | Field | Airtable Value | Current Value | Source |
|------|-------|---------------|---------------|--------|

## Stale Records
| Tool | Last Updated | Days | Priority |
|------|-------------|------|----------|

## Recommendations
1. [action items]
```

#### Analytics Tracker Report Format

```markdown
# SalesAIGuide Status Report — YYYY-MM-DD

## Content Coverage
| Type | Count | Target |
|------|-------|--------|

## SEO Health
- Pages with complete SEO: X/Y (Z%)

## Affiliate Readiness
- Active /go/ redirects: X
- Placeholder URLs remaining: Y

## Revenue Readiness Score: X/10
```

---

### Workflow 3: New Page Creation (On-Demand)

When Matt requests new page types (tool reviews, listicles, category pages).

```
Site Builder → [SEO Auditor ‖ Content Reviewer] → Deployment Agent
```

| Step | Agent | Input | Output | Handoff |
|------|-------|-------|--------|---------|
| 1 | Site Builder | Matt's requirements + Airtable data | New HTML files matching design system | Files written to repo |
| 2a | SEO Auditor | New HTML files | SEO-verified/fixed HTML | Files modified in-place |
| 2b | Content Reviewer | New HTML files (parallel with 2a) | Quality-verified/fixed HTML | Files modified in-place |
| 3 | Deployment Agent | All modified files | Git commit + push + Netlify deploy | Pages live |

**Site Builder output spec:**

Every page MUST include:
- Nav with hamburger menu (5 links: Home, Tools, Compare, Categories, About)
- `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`
- `css/main.css` (all pages) + `css/review.css` (comparison/review pages)
- Footer with Quick Links + Company columns
- Mobile responsive at 768px breakpoint
- Colors from design system only: `#0a192f`, `#112240`, `#00d9ff`, `#10b981`, `#fbbf24`

---

### Workflow 4: Hotfix (Emergency)

When a live page has a broken link, wrong data, or rendering issue.

```
[SEO Auditor OR Content Reviewer] → Deployment Agent
```

Skip Publish Agent and Site Builder entirely. Directly audit, fix, and deploy.

| Step | Agent | Input | Output |
|------|-------|-------|--------|
| 1 | SEO Auditor or Content Reviewer | Specific broken page | Fixed HTML |
| 2 | Deployment Agent | Fixed file | `fix(<scope>): <description>` commit + push |

---

## Parallel Execution Rules

| Scenario | Can Run Together? | Why |
|----------|:-----------------:|-----|
| Data Agent + Analytics Tracker | ✅ Yes | Different data sources (Airtable API vs local files) |
| Data Agent + Content Agent | ✅ Yes | Data Agent reads, Content Agent reads+writes, different records |
| SEO Auditor + Content Reviewer | ✅ Yes | Check non-overlapping concerns (`<head>` vs `<body>`) |
| Publish Agent + Site Builder | ❌ No | Both write HTML files — would conflict on index pages |
| Publish Agent + Deployment Agent | ❌ No | Deploy must wait for publish to finish writing |
| SEO Auditor + Deployment Agent | ❌ No | Deploy must wait for audit fixes |
| Content Reviewer + Deployment Agent | ❌ No | Deploy must wait for review fixes |
| Any Tier 2 + Publish Agent | ❌ No | Tier 2 must wait for new files from Tier 1 |

---

## Input/Output Contract Per Agent

### Data Agent
```
IN:  AIRTABLE_TOKEN env var
     Airtable Tools table (API)
     _redirects (local file)
     tools/*-review.html (existence check)
OUT: Data Freshness Report (stdout markdown)
     Exit code 0 = all fresh
     Exit code 1 = critical staleness detected
```

### Content Agent (External)
```
IN:  Airtable records where Status="Draft" AND (Description=empty OR Verdict=empty)
OUT: Airtable records updated:
       Tools.Description = 150-200 word text
       Comparisons.Verdict = 200-300 word text
       Status = "Review"
```

### Publish Agent
```
IN:  AIRTABLE_TOKEN env var
     Airtable Comparisons where Status="Approved" AND Published=false
     Airtable Tools (linked records for Tool A, Tool B)
     Airtable Categories (linked records for category names)
OUT: compare/{slug}.html (new file per comparison)
     compare/index.html (updated — new card added)
     sitemap.xml (updated — new URL added)
     Airtable records updated: Status="Published", Published=true, Date Published=today
```

### Site Builder
```
IN:  Matt's requirements (natural language)
     Airtable data (if data-driven pages)
     css/main.css, css/review.css (must use existing styles)
OUT: New .html files in appropriate directory
     Updated sitemap.xml (new URL entry)
     Updated _redirects (if new /go/ slugs needed)
```

### SEO Auditor
```
IN:  All .html files in repo (Glob **/*.html)
     sitemap.xml
OUT: Modified .html files (missing SEO elements added in-place)
     Audit report (stdout):
       X/Y pages pass all 13 checks
       List of fixes applied
       List of remaining issues
```

### Content Reviewer
```
IN:  All .html files in repo (Glob **/*.html)
     _redirects (to verify /go/ slugs exist)
OUT: Modified .html files (content issues fixed in-place)
     Review report (stdout):
       Issues found per page
       Fixes applied
       Manual review items (can't auto-fix)
```

### Deployment Agent
```
IN:  Modified files in git working tree
     Pre-push checklist (validated internally)
OUT: Git commit (conventional format + co-author)
     Git push to origin/main
     Netlify deploy (triggered by push, verified via WebFetch)
     Post-deploy status (stdout)
```

### Analytics Tracker
```
IN:  All .html files (Glob)
     sitemap.xml
     _redirects
     scripts/publish.js (existence check)
     .github/workflows/*.yml (existence check)
OUT: Status report (stdout markdown):
       Content coverage counts
       SEO health percentage
       Affiliate readiness metrics
       Automation health checks
       Revenue readiness score (1-10)
```

---

## Friday Review Runsheet

Matt's 30-60 minute weekly workflow, in order:

```
1. Run Data Agent + Analytics Tracker in parallel       [5 min automated]
   $ node scripts/data-check.js
   $ (Claude Code: "run analytics tracker")

2. Read both reports                                     [5 min]
   - Any critical staleness? Fix in Airtable first.
   - SEO health dropping? Note for audit.

3. Open Airtable → filter Comparisons by Status="Review" [10-15 min]
   - Read AI-generated verdicts
   - Approve, edit, or reject each one
   - Check Tools table for new Draft records

4. Wait for Publish Agent (next 2h cycle)                [0 min — async]
   - Or trigger manually: GitHub → Actions → Publish Agent → Run workflow

5. After publish: run SEO Auditor + Content Reviewer     [5 min automated]
   $ (Claude Code: "audit new pages")

6. Deploy fixes if any                                   [2 min automated]
   $ (Claude Code: "push changes")

7. Check Google Search Console (when available)          [5 min]
   - New pages indexed?
   - Any crawl errors?

8. Check affiliate program status                        [5 min]
   - Any approvals from Instantly, Reply.io, Smartlead?
   - Update _redirects with real affiliate URLs
```

---

## Error Handling Matrix

| Error | Agent | Detection | Recovery | Downstream Impact |
|-------|-------|-----------|----------|-------------------|
| Airtable API timeout | Publish Agent | HTTP 408/504 | Retry next 2h cycle | No pages published this cycle |
| Airtable API timeout | Data Agent | HTTP 408/504 | Retry once, then exit with error | No freshness report |
| Missing Tool A/B link | Publish Agent | Null linked record | Skip comparison, log to console | One fewer page published |
| HTML write failure | Publish Agent | fs.writeFile error | Skip file, continue with others | Page not published |
| Git push rejected | Deployment Agent | Non-zero exit code | Check PAT scope; split commit if workflow file | Changes stuck locally |
| Netlify deploy fails | Deployment Agent | WebFetch returns non-200 | Check deploy.yml, verify NETLIFY secrets | Site shows old content |
| Make.com scenario fails | Content Agent | No records move to "Review" | Check Make.com scenario logs | Pipeline stalls at Step 1 |
| G2 page blocked (403) | Data Agent | HTTP 403 response | Skip tool, note "unable to verify" | Partial report |
| AIRTABLE_TOKEN missing | Data/Publish Agent | Env var check | Exit with setup instructions | Agent can't run |
| Critical staleness (>90 days) | Data Agent | Timestamp comparison | Exit code 1, prominent warning | Matt must act |
| SEO element missing | SEO Auditor | DOM check | Auto-fix in-place | Fixed before deploy |
| Placeholder CTA found | Content Reviewer | `/go/` pattern check | Flag in report (can't auto-fix URL) | Matt must add real affiliate URL |
| Sitemap entry missing | SEO Auditor | XML check | Auto-add entry | Fixed before deploy |
| PAT_TOKEN expires | Deployment Agent | Push fails after May 22, 2026 | Regenerate Classic PAT with repo+workflow scope | All automated deploys stop |

---

## Metrics to Track

Measured weekly by Analytics Tracker:

| Metric | Target (Month 3) | Target (Month 6) | Target (Month 12) |
|--------|:-----------------:|:-----------------:|:------------------:|
| Total pages indexed | 50+ | 100+ | 200+ |
| Comparisons published | 20+ | 50+ | 100+ |
| Tool review pages | 10+ | 30 | 30 |
| Monthly organic sessions | — | 1,000+ | 5,000+ |
| Affiliate click-through rate | — | 2%+ | 5%+ |
| Monthly revenue | $0 | $50-200 | $500-1,000 |
| Pipeline velocity (Draft → Published) | <48h | <24h | <12h |
| SEO health (pages passing 13/13) | 90%+ | 95%+ | 100% |
| Data freshness (tools <30 days stale) | 80%+ | 90%+ | 95%+ |

---

## Adding New Content Types

### New Comparison
```
1. Add records to Airtable Comparisons table (Tool A, Tool B, Status = "Draft")
2. → Content Agent generates verdict (automatic, hourly)
3. → Matt approves in Airtable (Status = "Approved")
4. → Publish Agent generates HTML (automatic, every 2h)
5. → SEO Auditor + Content Reviewer verify (Claude Code session)
6. → Deployment Agent pushes (Claude Code session)
```

### New Tool
```
1. Add record to Airtable Tools table (all fields, Status = "Draft")
2. Add /go/[slug] entry to _redirects (placeholder or real)
3. → Content Agent generates description (automatic, hourly)
4. → Matt approves (Status = "Approved")
5. → Currently: tool appears in directory only
6. → Future: Publish Agent generates tools/[slug]-review.html
```

### New Category
```
1. Add record to Airtable Categories table
2. → Site Builder creates categories/[slug].html (Claude Code session)
3. → Update categories/index.html with new card
4. → Update sitemap.xml and _redirects
5. → SEO Auditor + Content Reviewer verify
6. → Deployment Agent pushes
```

### New Listicle ("Best X Tools")
```
1. → Site Builder creates best/[category-slug].html (Claude Code session)
2. → Content pulled from Airtable Tools filtered by category
3. → Each tool gets /go/ CTA + rating + pricing
4. → SEO Auditor + Content Reviewer verify
5. → Deployment Agent pushes
```

# ATLAS Lead Agent: Autonomous Weekly Operations Pipeline

## Overview
ATLAS (Automated Testing, Linking, Auditing & Strategy) is a lead agent that orchestrates 9 specialized audit agents across an 8-phase pipeline. It runs via GitHub Actions every Sunday at 6AM UTC, auto-fixes issues, commits changes, deploys to Netlify, and updates the ops dashboard — all without human intervention. The existing `scripts/weekly-run.sh` is superseded by ATLAS.

## Architecture

### Execution Model
Single Node.js script (`scripts/atlas.js`) that runs 8 sequential phases. Each phase completes fully before the next begins. No parallel agent execution (simplicity over speed for a weekly batch job).

### 8-Phase Cycle

```
Phase 1: AUTO-FIX (pre-audit)
  Run scripts/agent-autofix.js on all HTML files
  Handles: name leaks, banned phrases, demo CTAs, title length, meta desc, OG tags, freshness, prices
  Output: ops/data/autofix-log.json updated

Phase 2: AUDIT (9 agents)
  Run each scripts/agents/*.js sequentially:
    01-sitehealth.js → HTML quality, GA4, canonicals, schemas, newsletter forms
    02-revenuefunnel.js → /go/ link coverage, direct vendor leak detection
    03-linkhealth.js → Internal link graph, orphan detection, cross-link gaps
    04-priceverify.js → Price consistency (review pages = source of truth)
    05-contentguard.js → Name leaks, banned phrases, demo CTAs, ratings, schemas, thin content
    06-seopower.js → Title optimization, meta desc, freshness, keyword placement
    07-trafficintel.js → Commercial intent, competition proxy, content quality scoring
    08-contentengine.js → Content gap analysis (comparisons, best-picks, alternatives)
    09-revenueops.js → Aggregate scores, affiliate inventory, action queue prioritization
  Each agent: reads HTML files → evaluates rules → returns JSON result object
  No agent writes files directly — all results collected by ATLAS

Phase 3: DECIDE
  Compare audit results against previous run (ops/data/agent-state.json)
  Identify new issues, resolved issues, score changes
  Build fix plan: list of {file, fix_type, details} ordered by priority
  Apply diff limit: if total estimated changes > 500 lines, truncate to P0+P1 only

Phase 4: FIX (post-audit)
  Execute fix plan from Phase 3
  Write fix plan to ops/data/fix-plan.json, then run:
    node scripts/agent-autofix.js --fix-plan ops/data/fix-plan.json
  Fix plan format: [{ "file": "path", "fix_type": "banned_phrase|demo_cta|...", "details": "..." }]
  agent-autofix.js will be refactored to accept --fix-plan flag (targeted mode)
  Without the flag, it runs in full-scan mode (existing behavior)
  Only fix issues that agents flagged — never speculative changes

Phase 5: VALIDATE
  Re-run critical checks (name leaks, /go/ link integrity, price consistency)
  If ANY name leak detected: rollback all changes, abort cycle, log error
  If /go/ links broken: rollback, abort
  If validation passes: proceed

Phase 6: UPDATE
  Write updated ops/data/agent-state.json (all 9 agents)
  Append to ops/data/history.json (new run entry)
  Write ops/data/activity-log.json (new entries for this cycle)
  Update ops/data/autofix-log.json with final fix summary
  Recalculate overall score using weights:
    REVENUEFUNNEL(0.30) + SEOPOWER(0.20) + SITEHEALTH(0.15) +
    CONTENTGUARD(0.15) + LINKHEALTH(0.10) + PRICEVERIFY(0.10)

Phase 7: COMMIT + DEPLOY
  Stage only allowed paths: git add tools/ best/ alternatives/ categories/ compare/ pricing/ index.html ops/data/
  Verify no protected paths staged: check git diff --cached --name-only against protected list
  If protected file staged: unstage it, log warning
  git diff --stat: log what changed
  git commit -m "atlas: weekly cycle #{N} — score {X}/100, {Y} issues fixed"
  npx netlify-cli deploy --dir . --prod
  If deploy fails: log error, do NOT retry

Phase 8: REPORT (always runs, even after rollback/abort)
  Write run summary to ops/data/last-run-report.json:
    {
      "runNumber": 2,
      "timestamp": "2026-03-19T06:05:00Z",
      "durationMs": 180000,
      "status": "success",           // "success" | "failed" | "rolled_back"
      "overallScore": { "before": 88, "after": 91 },
      "issuesByAgent": {
        "sitehealth": { "found": 3, "fixed": 3 },
        "revenuefunnel": { "found": 0, "fixed": 0 }
      },
      "filesChanged": 12,
      "deployStatus": "success",     // "success" | "failed" | "skipped"
      "failureReason": null          // string if status != "success"
    }
  Dashboard auto-reads this on next load (60s refresh)
```

## File Structure

```
scripts/
  atlas.js              — Lead agent orchestrator (entry point)
  agent-autofix.js      — Auto-fix engine (already exists)
  agents/
    01-sitehealth.js
    02-revenuefunnel.js
    03-linkhealth.js
    04-priceverify.js
    05-contentguard.js
    06-seopower.js
    07-trafficintel.js
    08-contentengine.js
    09-revenueops.js
.github/
  workflows/
    atlas-weekly.yml    — GitHub Actions workflow
ops/data/
  agent-state.json      — Current agent state (exists)
  history.json          — Run history (exists)
  activity-log.json     — Activity feed (exists)
  autofix-log.json      — Auto-fix log (exists)
  last-run-report.json  — NEW: per-run summary report
```

## Agent Script Contract

Every agent script in `scripts/agents/` exports a single function and follows the same interface:

```js
// Input: path to site root
// Output: JSON result object
module.exports = async function audit(siteRoot) {
  // Read HTML files from siteRoot
  // Evaluate rules
  // Return result object:
  return {
    agent: "sitehealth",       // agent key
    status: "healthy",          // healthy | warning | critical
    score: 95,                  // 0-100 or null (see score rules below)
    metrics: { ... },           // agent-specific, opaque to ATLAS (stored as-is)
    issues: [                   // array of detected issues
      {
        check: "title_length",        // machine-readable check name
        severity: "critical",         // "critical" | "high" | "med" | "low"
        detail: "human-readable explanation"
      }
    ],
    lastAction: "...",          // human-readable summary of findings
  };
};
```

**Score rules by agent:**
- Returns 0-100: SITEHEALTH, REVENUEFUNNEL, LINKHEALTH, PRICEVERIFY, CONTENTGUARD, SEOPOWER
- Returns 0-100 (display only, excluded from weighted average): TRAFFICINTEL
- Returns null: CONTENTENGINE, REVENUEOPS

**Severity → fix priority mapping:**
- `critical` or `high` → P0 (always fixed, even under 500-line limit)
- `med` → P1 (fixed if within diff budget)
- `low` → P2 (fixed only if budget allows)

**Metrics are opaque to ATLAS** — each agent returns its own metrics shape, and ATLAS stores them as-is in `agent-state.json`. ATLAS does not inspect metric keys to build fix plans; it uses the `issues` array for that.

No agent reads or writes JSON data files. No agent modifies HTML. They only read HTML and return results. ATLAS handles all state management.

## Safety Rails

### Hard Rules (abort on violation)
1. **Name leak check**: If ANY file contains "Matt", "Matthew", "Schneider", or "Toptal" after fixes, rollback everything and abort
2. **Review page protection**: Never modify body content, prices, or ratings on `tools/*-review.html` pages (review pages are canonical source of truth)
3. **GA4 protection**: Never modify `G-VRBZ6Z6885` snippet
4. **Affiliate link protection**: Never modify `/go/` redirect URLs

### Soft Limits
1. **500-line diff limit**: If changes exceed 500 lines, only apply P0+P1 fixes
2. **Protected file list**: `.github/`, `scripts/`, `ops/js/`, `ops/css/` — never auto-modified
3. **Dry-run mode**: `ATLAS_DRY_RUN=true` skips Phase 7 (commit+deploy), logs what would change

### Rollback
If validation fails in Phase 5:
- `git checkout -- .` to discard all changes (reverts HTML + data files)
- Skip Phases 6 and 7
- Jump to Phase 8: write failure report to ops/data/last-run-report.json
- Exit with code 1 (GitHub Actions marks run as failed)

Phase 6 writes are NOT atomic — if ATLAS crashes mid-Phase-6, data files may be inconsistent. This is an accepted risk since the next successful run will overwrite all data files. The dashboard tolerates partial data gracefully (missing fields render as "—").

## GitHub Actions Workflow

```yaml
name: ATLAS Weekly Cycle
on:
  schedule:
    - cron: '0 6 * * 0'    # Sunday 6AM UTC
  workflow_dispatch:          # Manual trigger
    inputs:
      dry_run:
        description: 'Dry run (no commit/deploy)'
        type: boolean
        default: false

jobs:
  atlas:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Configure git identity
        run: |
          git config user.name "atlas-bot"
          git config user.email "atlas-bot@users.noreply.github.com"

      - name: Install netlify-cli
        run: npm install -g netlify-cli

      - name: Run ATLAS
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          ATLAS_DRY_RUN: ${{ inputs.dry_run || 'false' }}
        run: node scripts/atlas.js

      - name: Push changes
        if: success() && inputs.dry_run != 'true'
        run: git push
```

### Required Secrets
- `NETLIFY_AUTH_TOKEN`: Netlify personal access token for deploy
- `NETLIFY_SITE_ID`: Netlify site ID for salesaiguide

### Resource Usage
- Estimated run time: 2-5 minutes (file I/O only, no network calls except deploy)
- GitHub Actions free tier: 2,000 minutes/month (private repo) — ~8 minutes/month usage

## Scoring

### Per-Agent Scoring
Each agent calculates its own 0-100 score based on agent-specific rules (defined in each agent script). Agents that produce analysis only (CONTENTENGINE, REVENUEOPS) return `score: null`.

### Overall Score
Weighted average of scored agents:
```
overall = REVENUEFUNNEL * 0.30
        + SEOPOWER * 0.20
        + SITEHEALTH * 0.15
        + CONTENTGUARD * 0.15
        + LINKHEALTH * 0.10
        + PRICEVERIFY * 0.10
```
TRAFFICINTEL excluded (analysis metric, not health). CONTENTENGINE and REVENUEOPS excluded (null scores).

## Dashboard Integration
No changes needed to the dashboard. ATLAS writes the same JSON files the dashboard already reads:
- `ops/data/agent-state.json` — agent cards, scores, plans
- `ops/data/history.json` — sparkline data, score trends
- `ops/data/activity-log.json` — activity feed entries
- `ops/data/autofix-log.json` — auto-fix capability display

The dashboard's 60-second auto-refresh picks up new data after each ATLAS cycle.

## Demo CTA Rules
These tools are demo-only and must always show "Request Demo", never "Start Free Trial":
```json
["gong", "chorus", "outreach", "salesloft", "zoominfo", "clearbit", "clari", "orum"]
```
This list is the canonical source — agent-autofix.js and 05-contentguard.js both reference it.

## Dependencies
- Node.js 20+ (stdlib only for agent scripts — no npm packages required)
- Git (for commit/push)
- netlify-cli (installed globally in CI via `npm install -g netlify-cli`)
- GitHub Actions runner (ubuntu-latest)

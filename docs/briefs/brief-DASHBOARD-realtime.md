# Brief: Real-Time Agent Monitoring Dashboard
**Owner:** Claude Code  
**Reviewer:** Manus  
**Branch:** `dashboard-realtime`  
**Do NOT merge — Manus reviews and merges.**

---

## Overview

Build a standalone, password-protected, real-time dashboard at `salesaiguide.com/dashboard/` that serves as the operational control center for the SalesAIGuide agent system. This replaces the static `progress/index.html` page entirely.

The dashboard must:
- Show live data updated by agents via a REST API (no page refresh required)
- Display all 8 agent statuses, last run times, and findings
- Track build progress across all phases (migrated from the static progress.html)
- Show affiliate health, G2 data freshness, SEO metrics, and competitor flags in real time
- Be accessible only via password (same as current: `P@$$w0rd22`)
- Work without any external SaaS services — self-hosted backend only

---

## Architecture

### Stack
- **Backend:** Node.js + Express (already available in the repo's `server/` directory)
- **Database:** SQLite via `better-sqlite3` — lightweight, no setup, file-based, persists across deploys
- **Frontend:** Single HTML page with vanilla JS — no framework needed, fast to load
- **Hosting:** Netlify Functions OR a separate lightweight server — see Deployment section
- **Auth:** Client-side SHA-256 password check (same pattern as current progress page)

### Why SQLite
The dashboard data is written by agents (Manus) and read by the browser. SQLite is sufficient for this workload — it handles hundreds of writes/day with zero configuration. The database file lives at `dashboard/db/salesaiguide.db`.

---

## Database Schema

Create these 4 tables:

### `agent_runs`
Stores every agent execution result.
```sql
CREATE TABLE agent_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id TEXT NOT NULL,           -- e.g. "site-validator", "evidence-refresher"
  agent_name TEXT NOT NULL,         -- e.g. "Site Validator"
  run_date TEXT NOT NULL,           -- ISO date: "2026-02-24"
  status TEXT NOT NULL,             -- "ok" | "warning" | "action_required" | "error"
  summary TEXT NOT NULL,            -- One-line summary for dashboard card
  findings TEXT,                    -- JSON array of finding objects
  actions_required TEXT,            -- JSON array of action strings
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `tasks`
Migrated from the static progress.html — all build phase tasks.
```sql
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,              -- e.g. "p0-s1", "p3-t1"
  phase TEXT NOT NULL,              -- e.g. "Phase 0", "Phase 3"
  phase_label TEXT NOT NULL,        -- e.g. "Foundation Components"
  label TEXT NOT NULL,              -- Task description
  done INTEGER DEFAULT 0,           -- 0 = pending, 1 = done
  owner TEXT DEFAULT 'claude',      -- "claude" | "manus" | "matt"
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `metrics`
Key/value store for site-wide metrics that agents update.
```sql
CREATE TABLE metrics (
  key TEXT PRIMARY KEY,             -- e.g. "total_pages", "active_affiliates"
  value TEXT NOT NULL,              -- JSON-serialized value
  label TEXT NOT NULL,              -- Human-readable label
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `affiliate_status`
Tracks each affiliate redirect's health.
```sql
CREATE TABLE affiliate_status (
  tool TEXT PRIMARY KEY,            -- e.g. "clay", "apollo"
  redirect_url TEXT NOT NULL,
  has_affiliate_param INTEGER DEFAULT 0,
  status TEXT NOT NULL,             -- "active" | "pending" | "no_program" | "broken"
  commission TEXT,                  -- e.g. "20% of $149/mo"
  last_checked TEXT,                -- ISO date
  notes TEXT
);
```

---

## REST API Endpoints

All endpoints live under `/api/dashboard/`. No authentication on write endpoints — the API key is passed in the request body (see Agent POST Protocol below).

### GET `/api/dashboard/status`
Returns full dashboard state in one call.
```json
{
  "agents": [...],
  "tasks": { "total": 152, "done": 137, "by_phase": [...] },
  "metrics": { "total_pages": 101, "active_affiliates": 1, ... },
  "affiliates": [...],
  "last_updated": "2026-02-24T10:00:00Z"
}
```

### POST `/api/dashboard/agent-run`
Called by Manus after each agent run. Body:
```json
{
  "api_key": "SAG-DASH-2026",
  "agent_id": "site-validator",
  "agent_name": "Site Validator",
  "run_date": "2026-03-02",
  "status": "ok",
  "summary": "77/77 pages passing. No regressions.",
  "findings": [
    { "type": "info", "message": "All 20 tool pages have journey bar, dual scores, evidence drawers" }
  ],
  "actions_required": []
}
```

### POST `/api/dashboard/task-update`
Called by Manus to mark tasks done. Body:
```json
{
  "api_key": "SAG-DASH-2026",
  "task_id": "p3-t1",
  "done": true
}
```

### POST `/api/dashboard/metric-update`
Called by Manus to update site metrics. Body:
```json
{
  "api_key": "SAG-DASH-2026",
  "key": "total_pages",
  "value": 101,
  "label": "Total Pages Built"
}
```

### POST `/api/dashboard/affiliate-update`
Called by Manus when affiliate status changes. Body:
```json
{
  "api_key": "SAG-DASH-2026",
  "tool": "apollo",
  "redirect_url": "https://apollo.io?via=matt123",
  "has_affiliate_param": true,
  "status": "active",
  "commission": "20% of $99/mo",
  "notes": "Approved March 2026"
}
```

---

## Dashboard UI — Page Layout

Single HTML page at `dashboard/index.html`. Password gate identical to current `progress/index.html` pattern (SHA-256 check in JS, sessionStorage for session persistence).

### Header
- Logo + "SalesAIGuide — Operations Dashboard"
- Last updated timestamp (auto-refreshes every 60 seconds)
- "Refresh Now" button

### Section 1 — Site Health (top stats bar)
Four metric cards in a row:
- Total Pages Built (from `metrics.total_pages`)
- Tasks Complete (from `tasks` table: done/total)
- Active Affiliates (from `affiliate_status` count where status = 'active')
- Agent Runs This Week (from `agent_runs` count in last 7 days)

### Section 2 — Agent Status Grid
Eight cards, one per agent. Each card shows:
- Agent name + domain tag (e.g. "Quality Assurance", "Revenue Infrastructure")
- Schedule (e.g. "Daily @ 8:00 AM")
- Status badge: green "OK" / yellow "Warning" / red "Action Required" / grey "Not Run Yet"
- Last run date
- Summary text from most recent run
- Expandable "Findings" section (click to expand)
- "Actions Required" list (if any)

**The 8 agents and their IDs:**
| agent_id | agent_name | schedule |
|---|---|---|
| `site-validator` | Site Validator | Daily @ 8:00 AM |
| `evidence-refresher` | Evidence Refresher | Monday @ 9:00 AM |
| `affiliate-health` | Affiliate Health Monitor | Daily @ 10:00 AM |
| `seo-monitor` | SEO Performance Monitor | Friday @ 9:00 AM |
| `competitor-intel` | Competitor Intelligence | Friday @ 10:00 AM |
| `new-tool-scout` | New Tool Scout | Wednesday @ 9:00 AM |
| `revenue-optimization` | Revenue Optimization | Monday @ 10:00 AM |
| `growth-strategy` | Growth Strategy | 1st Monday/month |

### Section 3 — Affiliate Health Table
Table with columns: Tool | Redirect | Status | Commission | Last Checked | Notes
- Status badges: green "Active" / yellow "Pending" / grey "No Program" / red "Broken"
- Populated from `affiliate_status` table

### Section 4 — Build Progress
Collapsible phase sections, same structure as the old progress.html but reading from the `tasks` database table. Each phase shows:
- Phase name + completion percentage bar
- Task list with green checkmarks (done) or grey circles (pending)
- Owner tag on each task (Claude / Manus / Matt)

### Section 5 — Recent Agent Activity Feed
Chronological list of last 20 agent runs, newest first. Each entry:
- Date + agent name + status badge + summary
- Clicking expands to show full findings

---

## Seed Data

On first run, seed the database with:

### Tasks (from current progress.html — all 152 tasks)
Migrate all tasks from `_private/progress.html` into the `tasks` table. The `done` field should match the current `done: true/false` values in the JS data array. See the full task list at the end of this brief.

### Metrics (initial values)
```
total_pages: 101
tool_reviews: 20
comparison_pages: 52
category_pages: 14
persona_pages: 3
guide_pages: 2
active_affiliates: 1
agents_baselined: 8
```

### Affiliate Status (initial values)
```
clay: active, https://clay.earth/?via=matthew-schneider, commission: ~$30/conversion
apollo: pending, https://apollo.io, commission: ~$20/conversion
instantly: pending, https://instantly.ai, commission: ~$11/conversion
hubspot: pending (LinkedIn verification required), https://hubspot.com, commission: ~$30+/conversion
gong: no_program, https://gong.io
outreach: no_program, https://outreach.io
salesloft: no_program, https://salesloft.com
zoominfo: no_program, https://zoominfo.com
lavender: pending (check program), https://lavender.ai
smartlead: pending (check program), https://smartlead.ai
loom: no_program, https://loom.com
```

### Agent Runs (baseline — Feb 24, 2026)
Seed one run per agent from the Feb 24 baseline:
- `site-validator`: status "ok", summary "77/77 pages passing. No regressions."
- `evidence-refresher`: status "action_required", summary "Gong rating dropped 4.8→4.7. 4 tools have review count drift."
- `affiliate-health`: status "warning", summary "1/11 redirects have affiliate tracking. 3 programs pending application."
- `seo-monitor`: status "ok", summary "Search Console connected. 9 URLs indexed. Awaiting first impression data."
- `competitor-intel`: status "warning", summary "marketbetter.ai published 4 tool reviews targeting our keywords."
- `new-tool-scout`: status "ok", summary "Saleshandy and Lemlist flagged for Phase 7 page build."
- `revenue-optimization`: status "ok", summary "No traffic data yet. Clay is only active affiliate."
- `growth-strategy`: status "ok", summary "90-day forecast written. First organic traffic expected March–April."

---

## Deployment

The dashboard backend needs to run as a persistent server (not a Netlify static deploy). Two options — implement whichever is simpler given the existing repo structure:

**Option A: Netlify Functions**
- Create `netlify/functions/dashboard-api.js` as a serverless function
- Use `better-sqlite3` in the function (note: SQLite in serverless has persistence limitations — use a file in `/tmp` or switch to a Netlify-compatible KV store)
- If SQLite persistence is unreliable in serverless, use **Option B** instead

**Option B: Separate Express server on Railway/Render (recommended)**
- Create `dashboard-server/` directory with `server.js`, `package.json`, `db/` 
- Deploy to Railway (free tier) as a separate service
- The frontend `dashboard/index.html` fetches from the Railway URL
- Store the Railway URL in `_data/dashboard.json` so Eleventy can inject it at build time
- This is the most reliable option for SQLite persistence

**Regardless of option:** The `dashboard/index.html` frontend is always served by Netlify as a static file. Only the API calls go to the backend.

---

## Agent POST Protocol (for Manus)

After each agent run, Manus will call the API like this:

```bash
curl -X POST https://YOUR-RAILWAY-URL/api/dashboard/agent-run \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "SAG-DASH-2026",
    "agent_id": "site-validator",
    "agent_name": "Site Validator",
    "run_date": "2026-03-02",
    "status": "ok",
    "summary": "77/77 pages passing.",
    "findings": [],
    "actions_required": []
  }'
```

The API key `SAG-DASH-2026` is hardcoded in the server — no environment variable needed for this internal tool.

---

## Validation Checklist (Session 4 — PR)

Before opening the PR, verify:
- [ ] `GET /api/dashboard/status` returns valid JSON with all 4 sections
- [ ] `POST /api/dashboard/agent-run` inserts a row and is reflected in the next GET
- [ ] `POST /api/dashboard/task-update` flips a task done and is reflected in the next GET
- [ ] Dashboard page loads and shows password gate
- [ ] Correct password unlocks the dashboard
- [ ] All 8 agent cards render with baseline data
- [ ] Affiliate table shows 11 rows with correct statuses
- [ ] Build progress shows correct done/total counts
- [ ] Auto-refresh fires every 60 seconds (check browser console)
- [ ] Build: 0 errors

---

## Task Seed Data

Below is the complete task list to seed into the `tasks` table. Extract from `_private/progress.html` — the JS `phases` array contains all task objects with `id`, `label`, and `done` fields. The `phase` and `phase_label` fields map to the parent phase object's `id` and `label` fields.

Claude Code: read `_private/progress.html` and write a seed script `dashboard-server/seed.js` that parses the JS data array and inserts all tasks into SQLite. This is more reliable than manually copying 152 tasks.

The seed script should:
1. Parse the `phases` array from the HTML file using regex or string extraction
2. For each phase, iterate its `tasks` array
3. Insert each task with `phase`, `phase_label`, `label`, `done`, `owner` (default 'claude' unless the task label mentions "Matt" → owner 'matt' or "Manus" → owner 'manus')
4. Run once: `node dashboard-server/seed.js`

---

## Session Plan

**Session 1 (45 min) — Backend**
- Create `dashboard-server/` with `server.js`, `package.json`, `db/schema.sql`
- Implement all 5 API endpoints
- Write `seed.js` and run it to populate initial data
- Test all endpoints with curl

**Session 2 (60 min) — Frontend**
- Create `dashboard/index.html` with all 5 sections
- Password gate (SHA-256, sessionStorage)
- Auto-refresh every 60 seconds via `setInterval`
- Responsive layout (works on mobile)

**Session 3 (30 min) — Integration + Deployment**
- Deploy backend to Railway (or implement as Netlify Functions)
- Update `dashboard/index.html` to point to the deployed API URL
- Run `npm run build` to confirm Eleventy builds correctly with the new `dashboard/` directory

**Session 4 (15 min) — Validation + PR**
- Run full validation checklist above
- Open PR on branch `dashboard-realtime`
- Do NOT merge — Manus reviews

---

## Notes for Claude Code

- The `dashboard/` directory should be added to `.eleventy.js` as a passthrough copy (same as `progress/`)
- The `dashboard-server/` directory should NOT be in the Eleventy build — add it to `.eleventyignore`
- The SQLite database file (`dashboard-server/db/salesaiguide.db`) should be in `.gitignore` — it's runtime data, not source code. The schema and seed script ARE committed.
- If Railway deployment is complex, implement a simple in-memory store first so the frontend works, then add SQLite persistence in a follow-up
- The dashboard does NOT need to be pretty — it needs to be functional, fast, and reliable. Clean monospace/terminal aesthetic is fine.

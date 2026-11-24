# Project Dashboard (Vercel) — Design Spec

Status: DRAFT for review (2026-06-10). No code until approved.

## Context

The AROS agentic team is monitorable today only via the CLI (`npm run aros`, `npm run affiliates`, etc.) and the weekly Actions log. The owner wants a private, password-protected web page on Vercel to monitor the project and to trigger the two control actions (activate an affiliate program, deploy to production) from a browser/phone.

The hard constraint, agreed during brainstorming: control actions must NOT put powerful credentials or guard-bypasses behind a single web password. So the page triggers guarded GitHub Actions rather than acting directly, holds only a minimal token, and is built inert until the owner enables it.

## Goals
- A private dashboard showing: the AROS team report, the revenue funnel, the affiliate portfolio + activation queue, and the distribution-probe status. Live-ish (reflects the repo's committed state).
- Two control actions, each routed through a guarded GitHub Action: activate a program, deploy production.
- Strong-enough auth (password) plus defense-in-depth so a leaked password cannot cause catastrophic damage.
- Inert by default: no real power until the owner sets a token in Vercel.

## Non-goals
- The page never edits `affiliate-links.json` directly, never holds a Netlify token, never runs `deploy.sh` itself. It only dispatches workflows that do.
- No fabricated data. Reads reflect the real committed repo state.
- Not a public site. Private, password-gated.

## Architecture

Two parts:

### 1. The dashboard app (new, Next.js App Router on Vercel)
Lives in a new repo `salesaiguide-dashboard` (recommended for clean separation from the Netlify site; confirm on review). Deployed as its own Vercel project.

- **Auth:** `middleware.ts` gates every route. A `/login` page posts to `/api/login`, which constant-time-compares against `DASHBOARD_PASSWORD` (Vercel env) and sets a signed, httpOnly session cookie. Vercel serves it over HTTPS. The owner may additionally enable Vercel's built-in deployment protection as a second layer.
- **Reads (monitor):** server components / route handlers call the GitHub REST API (contents) for `ops/data/revenue-funnel.json`, `affiliate-links.json`, `ops/data/affiliate-pipeline.json`, and `ops/distribution/probe-config.json`, then render the views and reconstruct the AROS team summary from the same source data. (`aros-report.json` is gitignored and not in the repo, so the page recomputes the equivalent summary instead of fetching it.)
- **Actions:** `/api/activate` and `/api/deploy` route handlers (session-gated) call the GitHub API `workflow_dispatch` for the two workflows below. They never do the work themselves.
- **Secret on Vercel:** ONE fine-grained GitHub PAT scoped to the single repo `schneider2285-cmyk/salesaiguide`, permissions `contents:read` + `actions:write`. No `contents:write` (writes happen inside the workflow via its own `GITHUB_TOKEN`), and no Netlify token.
- **Two-stage enablement:** with no `DASHBOARD_GITHUB_TOKEN`, reads show a "configure token" state and actions are disabled (fully inert). With the token set, the monitor goes live read-only. The two control actions additionally require `DASHBOARD_ACTIONS_ENABLED=true`; until then their buttons render disabled and the dispatch routes refuse. So the owner runs monitor-only first, then flips on actions deliberately.

### 2. Guarded workflows (added to the salesaiguide repo)
- `.github/workflows/activate-program.yml` (`workflow_dispatch`, inputs: `slug`, `url`): runs `python3 scripts/affiliate_manager.py activate <slug> --url <url>`, which validates the tracking param, rejects fakes, regenerates redirects, runs `check_affiliate_links.py`, and commits. Aborts (no commit) if the guard fails.
- `.github/workflows/deploy-prod.yml` (`workflow_dispatch`): runs the `deploy.sh` guard chain (identity guards, `build_redirects.py`, `check_affiliate_links.py`, `scrub_pii.py --check`, the indexation gate) then `netlify deploy --prod`, using `NETLIFY_AUTH_TOKEN` from GitHub Actions secrets. The Netlify token never leaves Actions.

## Data + control flow

```
Browser (password)  ->  Vercel app
   reads:   Vercel app --(GitHub API, contents:read)-->  salesaiguide repo JSON  -> rendered dashboard
   activate: Vercel app --(workflow_dispatch, actions:write)--> activate-program.yml -> affiliate_manager activate (guards) -> commit
   deploy:   Vercel app --(workflow_dispatch, actions:write)--> deploy-prod.yml -> deploy.sh guards -> netlify --prod
```

## Security model (the crux)
- One password gates the UI; sessions are signed httpOnly cookies; HTTPS by default; optional Vercel deployment protection on top.
- The Vercel-held secret is minimal: a single-repo, fine-grained `contents:read + actions:write` token. It cannot write content directly and cannot deploy directly.
- Every action runs the full existing guard chain inside CI. A leaked password's worst case is triggering workflows that still reject fake links and still run the PII/identity/gate checks. No high-value secret (Netlify) is exposed to the web tier.
- Activation requires a real pasted tracking URL; the page cannot invent one, and the guard rejects fakes.

## Components (dashboard app)
- `middleware.ts`, `app/login/page.tsx`, `app/api/login/route.ts` (auth)
- `app/page.tsx` + view components: `FunnelCard`, `AffiliateTable` (status + queue), `ProbeCard`, `TeamReport`
- `lib/github.ts` (read helpers + `dispatchWorkflow`), `lib/auth.ts` (session), `lib/validate.ts` (mirror of `is_real_tracking_param` for client-side pre-check)
- `app/api/activate/route.ts`, `app/api/deploy/route.ts` (session-gated dispatch)
- `.env.example` (`DASHBOARD_PASSWORD`, `SESSION_SECRET`, `GITHUB_REPO=schneider2285-cmyk/salesaiguide`, `DASHBOARD_GITHUB_TOKEN` [enables reads/monitor], `DASHBOARD_ACTIONS_ENABLED` [default false; gates the control actions])

## Testing
- `lib/validate.ts`: unit tests mirroring `test_affiliate_manager.py` param cases (reject fake/empty, accept real).
- `lib/github.ts`: tested with a mocked fetch (read shape, dispatch payload), no live calls.
- Auth: a test that an unauthenticated request is redirected and a wrong password is rejected.
- Workflows: validated by a manual `workflow_dispatch` dry-run before wiring the buttons.

## Deployment
- New repo `salesaiguide-dashboard`, new Vercel project. Owner sets env vars in Vercel (`DASHBOARD_PASSWORD`, `SESSION_SECRET` now; `DASHBOARD_GITHUB_TOKEN` when ready to enable actions).
- The two workflows are added to the salesaiguide repo via a normal PR to `redesign/nerdwallet-v1`.
- Inert until enabled: monitor works read-only once the token is present; the control actions stay disabled until `DASHBOARD_ACTIONS_ENABLED=true`.

## Open decisions (confirm on review)
1. New repo `salesaiguide-dashboard` (recommended) vs a subdirectory of salesaiguide that Vercel builds from a root path.
2. Next.js App Router (recommended, gives the server routes for auth + dispatch) vs a lighter static page + serverless functions.
3. Password only (recommended for v1) vs also enabling Vercel's built-in protection from the start.

## Build order (for the later plan)
1. Scaffold the Next.js app + auth (password gate), deploy to Vercel (monitor shell, no data).
2. GitHub read layer + the four monitor views (live read-only dashboard).
3. The two guarded workflows in salesaiguide (dispatch-tested).
4. The action routes + buttons, inert by default behind the token flag.

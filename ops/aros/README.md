# Agentic Revenue Operating System (AROS)

Scaffold v0.1.0. No fix code is implemented here. This directory defines the agent roster, their state contract, and an inert orchestration entry point that extends the existing ATLAS weekly runner. The actual fixes (GA4 PII, conversion tracking, cruft cleanup, program activation) are the WORK these agents will perform later, gated behind explicit approval.

- Design spec: `docs/superpowers/specs/2026-06-09-agentic-revenue-operating-system.md`
- Current-state audit: `docs/ARCHITECTURE.md`

## Why this lives under ops/

The Netlify publish dir is the repo root, so anything under `.claude/agents/` or a root `skills/` would be served on the live site (`.claude/` is partly tracked already). `ops/*` is `noindex, nofollow` + `no-store` (see `_headers`) and `Disallow: /ops/` (see `robots.txt`), so internal AROS files are neither indexable nor cached. The agent and skill definitions use Claude Code compatible frontmatter, so they can be mirrored into a local, gitignored `.claude/agents/` for interactive subagent use if desired.

## Core contract: agents propose, guards dispose

No agent deploys or mutates production directly. Every change still flows through `deploy.sh`, which runs the identity guards, `build_redirects.py`, `check_affiliate_links.py`, `scrub_pii.py --check`, and the indexation gate. Agents write PROPOSALS to `ops/data/fix-plan.json` and, for auto-safe changes, stage diffs. A human or the `ATLAS_DRY_RUN=false` path runs the guarded pipeline.

## Roster

| Agent | Definition | Owns (state) | Priority (from audit) |
|-------|-----------|--------------|------------------------|
| Orchestrator | agents/aros-orchestrator.md | agent-state, activity-log, history, last-run-report, fix-plan | sequence + guard enforcement |
| Revenue Analyst | agents/revenue-analyst.md | revenue-funnel.json | GA4 PII fix, then conversion tracking |
| Growth Engineer | agents/growth-engineer.md | autofix-log.json | repo cruft cleanup, toolchain |
| Monetization Manager | agents/monetization-manager.md | affiliate-links.json | activate 45 placeholders |
| Distribution Lead | agents/distribution-lead.md | (marketing docs) | run demand probe (traffic) |
| Content Steward | agents/content-steward.md | content-scores.json | hold A-tier, pricing freshness |

## Run the scaffold (inert)

```bash
npm run aros                                 # dry-run: prints what each agent WOULD do
node scripts/aros.js --list                  # list agents and their tasks
node scripts/aros.js --agent revenue-analyst # single agent, dry-run
```

The orchestrator stub is intentionally side-effect-free. It reads the config and state, prints planned actions, and exits. It does not implement any fix, write any file, call the network, or deploy.

## Integration with ATLAS

`scripts/atlas.js` is the live weekly runner (cron Sundays 06:00 UTC). AROS does not modify it yet. The integration point: ATLAS would call `scripts/aros.js` per agent in sequence, honoring `ATLAS_DRY_RUN`. See the spec for the wiring plan.

## Secrets

No real credentials are stored in the repo. Required secrets and where to set them: `ops/aros/SECRETS.md`.

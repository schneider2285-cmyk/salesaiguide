# Agentic Revenue Operating System (AROS) — Scaffolding Plan

Status: DESIGN ONLY. No fix code implemented. Date: 2026-06-09.
Companion: `docs/ARCHITECTURE.md` (current-state audit this plan builds on).

## Context

SalesAIGuide is technically healthy (160 A / 5 B / 1 C, 165 indexed) but earns ~$0. The audit found the blockers are not content or indexing. They are: (1) only 4 of 49 affiliate programs are live, (2) near-zero organic traffic, and (3) no revenue measurement (direct CTAs and ButtonDown signups are untracked, and a PII value is being sent to GA4). The Agentic Revenue Operating System is a thin coordination layer over the EXISTING ATLAS weekly runner that assigns these problems to named agents, gives each a read/write contract against the existing `ops/data/*.json` state, and routes all changes through the existing guards (`deploy.sh`, the indexation gate, the affiliate and PII checks). Agents PROPOSE, the pipeline guards DISPOSE.

## Note on "items 2 through 8"

I do not have the original enumerated list in context. The 8 components below are my reconstruction from your direction (Revenue Analyst, Growth Engineer, monetization activation workflow, ranked fixes) plus the audit. If your list differs, point me at it and I will realign. Mapping used here:

- Item 1: Architecture map. DONE (`docs/ARCHITECTURE.md`).
- Item 2: AROS orchestration layer (this section + "Orchestration").
- Item 3: Revenue Analyst agent.
- Item 4: Growth Engineer agent.
- Item 5: Monetization Manager agent + Affiliate Activation skill.
- Item 6: Distribution Lead agent.
- Item 7: Content and Indexation Steward agent.
- Item 8: Ranked fix backlog + decision rules.

## Design Principles (non-negotiable, from audit history)

1. No fake affiliate infrastructure, ever. A link is only `status:live` after a real program approval with a real tracking param. `check_affiliate_links.py` stays the hard guard.
2. The indexation gate is the read-only referee. No agent edits `indexation_gate.py` to pass itself. The `/go/`-banned-in-core-editorial rule stands; tracking solutions must work within it.
3. Agents propose, guards dispose. Every change still flows through `deploy.sh` (identity guards, affiliate check, PII check, gate). No agent deploys by any other path.
4. Measure before optimize. Activating 45 programs while blind to conversions repeats the original mistake in a new form.
5. Traffic is the ceiling. Monetization x ~0 traffic = ~0. The OS must keep distribution visible as the dominant lever, not bury it under tooling.

## Orchestration Layer (Item 2)

- Runtime: extends the existing `scripts/atlas.js` weekly cron (`atlas-weekly.yml`, Sundays 06:00 UTC) rather than introducing a new scheduler. Each agent is a role the orchestrator invokes in sequence; interactive runs use the Claude Code agent definitions (see File Layout).
- State contract: existing `ops/data/*.json` files map onto agents as their durable memory.

  | State file | Owner agent | Role |
  |------------|-------------|------|
  | `revenue-funnel.json` | Revenue Analyst | funnel + leak ledger (currently an empty stub) |
  | `content-scores.json` | Content Steward | per-page quality/grade history |
  | `fix-plan.json` | Orchestrator | the ranked backlog (Item 8) all agents append to |
  | `autofix-log.json` | Growth Engineer | what auto-fixes ran |
  | `agent-state.json` / `activity-log.json` / `history.json` | Orchestrator | run cursor, audit trail, snapshots |
  | `last-run-report.json` | Orchestrator | latest cycle summary |

- Guardrail contract: agents write proposals to `fix-plan.json` and (for auto-safe fixes) stage diffs; a human or the `ATLAS_DRY_RUN=false` path runs `deploy.sh`, which is the only thing that can reach production. The gate exit code (0/1/2) gates the commit.

## Agent Roster (Items 3 to 7)

Each agent below is a scaffold: mission, reads, writes/proposes, tools/skills, guardrails, and the priority task drawn from the audit. None are implemented yet.

### Item 3 — Revenue Analyst
- Mission: make revenue measurable and clean. Own attribution, funnel, and analytics integrity.
- Reads: `js/main.js`, page HTML (CTA and form markup), GA4 config, `affiliate-links.json`, `ops/data/revenue-funnel.json`.
- Writes/proposes: GA4 event spec, `revenue-funnel.json` population, a weekly revenue report into `last-run-report.json`.
- Tools/skills: `conversion-tracking-setup` skill (new), GA4 Measurement Protocol knowledge, read-only access to the gate report.
- Guardrails: any client-side tracking on direct vendor links must NOT add `/go/` in core-editorial (would trip the gate). Use outbound-click event listeners that leave `href` unchanged.
- PRIORITY TASKS (audit-driven):
  1. P0 fix the GA4 PII leak: stop sending the raw email in the `newsletter_signup` event (drop it or send a hashed id). Compliance liability, trivial fix.
  2. Add `outbound_click` tracking for the ~7-8 DIRECT vendor CTAs per review (event keyed by destination domain + page + CTA zone), so the gate-mandated direct links are no longer invisible.
  3. Add a `newsletter_signup` event for the ButtonDown forms (fire client-side at submit), unifying the two email systems in GA4.
  4. Populate `revenue-funnel.json` (impressions -> outbound clicks -> live-program clicks -> known conversions) and surface the live-vs-placeholder coverage gap.

### Item 4 — Growth Engineer
- Mission: keep the repo and build pipeline lean, correct, and fast. Reduce the error surface that caused past wrong-file/stale-script mistakes.
- Reads: full repo tree, `scripts/`, `netlify.toml`, `.github/workflows/`, `.gitignore`.
- Writes/proposes: cleanup diffs, toolchain consolidation, CI/build hygiene, `autofix-log.json`.
- Tools/skills: `repo-hygiene` skill (new), the existing test (`test_slop_signals.py`) and gate.
- Guardrails: never touch the generated artifacts as source; never delete git history (archive, do not destroy); pipeline scripts stay first-class.
- PRIORITY TASKS (audit-driven):
  1. Remove the empty literal directory `{css,js,tools,comparisons,categories,blog,images}/` (brace-expansion accident).
  2. Triage `scripts/`: move the ~40 one-off `fix_*_vN.py` migrations into `scripts/archive/`, leaving the 4 pipeline scripts + recurring maintenance scripts at top level. Document each archived script in a short `scripts/archive/README.md`.
  3. Re-enable `feed.xml` freshness (wire `generate_feed.py` into the build or ATLAS; switch its links to clean URLs).
  4. Add a lightweight `scripts/README.md` index so future runs do not edit the wrong script.

### Item 5 — Monetization Manager (+ Affiliate Activation skill)
- Mission: move programs from placeholder to live without ever shipping a fake link, and keep `affiliate-links.json` the single source of truth.
- Reads: `affiliate-links.json`, `docs/monetization/affiliate-programs.md` (ranked signup playbook), `docs/monetization/tool-pricing-2026-06.md`, `_redirects`.
- Writes/proposes: program pipeline status, real tracked URLs into `affiliate-links.json` on approval, then runs `build_redirects.py` + `check_affiliate_links.py`.
- Tools/skills: `affiliate-program-activator` skill (new, detailed below).
- Guardrails: `check_affiliate_links.py` must pass; `status:live` only with a real tracking param; no `?ref=salesaiguide`-style invented params.
- PRIORITY TASK: drive the 45 placeholders to live, sequenced by the activation rule below.

#### Affiliate Activation skill (network-agnostic)
- Pipeline states per slug: `placeholder -> applied -> approved -> live` (tracked in `affiliate-links.json` metadata + `revenue-funnel.json`).
- Per slug it: looks up network + signup URL + commission from the playbook, prepares the application, records status, and on approval does the mechanical wiring (paste real URL, set `status:live`, regenerate redirects, run the guard, deploy via `deploy.sh`).
- Network adapters (pluggable, optional): PartnerStack, Rewardful, FirstPromoter, Impact. These are the real networks the playbook already targets.
- Honest constraint: no API can auto-enroll you into third-party vendor programs. Approval is a human/business step (and some networks will reject a near-zero-traffic site). Automation helps with detection, link sync, status tracking, and tracking aggregation (Strackr-style), not magic enrollment.
- Adgentic: I could NOT verify Adgentic is a real automated-affiliate API (web search 2026-06-09 surfaced PartnerStack, Rewardful, Everflow, Strackr, AffiliateWP, Post Affiliate Pro, but no Adgentic). It is modeled here as ONE optional adapter behind the same interface. If you can share its docs/API, it slots in; the design does not depend on it.

### Item 6 — Distribution Lead
- Mission: the dominant revenue lever. Generate qualified traffic, since monetization is traffic-gated.
- Reads: `docs/marketing/distribution-plan.md`, GSC/GA4 (when connected), content inventory.
- Writes/proposes: campaign briefs, the 2-week cold-email demand probe execution log, backlink/syndication targets, kill/commit decision.
- Tools/skills: existing distribution plan (with its pre-committed kill/commit rule), outreach drafting.
- Guardrails: respect the pre-committed kill/commit rule; do not declare traffic "solved" without GSC/GA4 evidence.
- PRIORITY TASK: run the 2-week probe, report against the decision rule. This outranks program activation on realized revenue because it lifts the ceiling.

### Item 7 — Content and Indexation Steward
- Mission: keep the supply side (indexable, accurate, A-tier pages) healthy. Formalizes what ATLAS already does.
- Reads: `gate-report.json`, `content-scores.json`, `tool-pricing-2026-06.md`, page HTML.
- Writes/proposes: freshness bumps after genuine re-verification (`bump_last_verified.py`), slop fixes, pricing corrections.
- Tools/skills: the indexation gate (read-only referee), existing fix scripts (curated set only).
- Guardrails: never bump `last_verified` without a real re-check (the date asserts verification); never edit the gate to self-pass.
- PRIORITY TASK: hold 160+ A-tier; keep pricing current; feed conversion signals from the Revenue Analyst back into which pages deserve refresh.

## Skills and Workflows (new, to scaffold)

| Skill | Used by | Purpose |
|-------|---------|---------|
| `affiliate-program-activator` | Monetization Manager | program pipeline + safe link wiring, network adapters |
| `conversion-tracking-setup` | Revenue Analyst | GA4 event spec, outbound-click + ButtonDown events, PII-safe |
| `repo-hygiene` | Growth Engineer | cruft removal, script archival, build/CI hygiene |

## Proposed File Layout (create on approval, NOT created now)

```
docs/superpowers/specs/2026-06-09-agentic-revenue-operating-system.md   # this plan (created)
.claude/agents/                      # Claude Code subagent role definitions (proposed)
  revenue-analyst.md
  growth-engineer.md
  monetization-manager.md
  distribution-lead.md
  content-steward.md
  aros-orchestrator.md
skills/                              # new skill packages (proposed)
  affiliate-program-activator/SKILL.md
  conversion-tracking-setup/SKILL.md
  repo-hygiene/SKILL.md
scripts/archive/                     # destination for one-off fix_*_vN.py (proposed)
```
The ATLAS node runner (`scripts/atlas.js`) can call the same role contracts for the automated weekly cycle; the `.claude/agents/*.md` definitions serve interactive runs. Recommend the `.md` agent + `skills/` approach since it matches your broader skills work and keeps roles human-readable.

## Item 8 — Ranked Fix Backlog (impact x risk)

Ranking is by EXPECTED (probability-weighted, near-term) revenue impact, with the current-state risk it addresses. The honest headline: activation has the highest ceiling but is traffic-gated, so measurement and traffic come first.

| # | Fix | Agent | Revenue impact (near-term) | Risk it addresses | Effort | Sequence |
|---|-----|-------|---------------------------|-------------------|--------|----------|
| 1 | Fix GA4 PII leak (email in event) | Revenue Analyst | None directly | HIGH (privacy/GA4 ToS liability) | XS | Do first |
| 2 | Conversion tracking: direct CTAs + ButtonDown | Revenue Analyst | Medium (indirect: enables every later decision) | Medium (currently flying blind) | M | Second |
| 3 | Distribution: run 2-week demand probe | Distribution Lead | HIGH ceiling (the actual revenue lever) | HIGH (no traffic = no revenue) | M-L | In parallel from now |
| 4 | Activate placeholder programs (45) | Monetization Manager | HIGH ceiling, LOW until traffic exists | Medium (fake-link repeat; low-traffic rejections) | L | After 1-2, paced with 3 |
| 5 | Repo cruft cleanup (empty dir + scripts) | Growth Engineer | ~None | Low (error-surface hygiene) | S | Fold into routine |

Sequencing rationale:
- 1 before everything: it is a standing liability and costs minutes.
- 2 before 4: do not activate 45 programs blind. Tracking tells you which pages/programs convert so activation is targeted, not scattershot.
- 3 is the true #1 by ceiling and should start now in parallel; without traffic, 4 realizes almost nothing.
- 4 paced to traffic: activate first the programs that (a) approve low-traffic sites and (b) back your highest-intent existing pages (the 4 already-live tools and their comparison/pricing pages).
- 5 is hygiene, not a revenue lever; it rides along with Growth Engineer's normal cycle.

Decision rules:
- Activation gate: only set `status:live` after real approval; `check_affiliate_links.py` must pass; never invent params.
- Traffic kill/commit: follow the pre-committed rule in `docs/marketing/distribution-plan.md`; if the probe fails it, do not pour effort into activation.
- Freshness honesty: no `last_verified` bump without a real re-check.

## Explicitly NOT in scope yet
- No fix code (no PII patch, no tracking JS, no cleanup, no activation wiring).
- No agent/skill files created (only this plan).
- No deploy.

## Open Questions for the User
1. Is the item 2-8 reconstruction above correct, or do you have a different original list?
2. Agent home: `.claude/agents/*.md` + `skills/` (recommended) vs wiring roles into the existing `scripts/atlas.js` node runner?
3. Adgentic: can you share a product URL or API docs so I can validate it, or proceed network-agnostic with PartnerStack/Rewardful/FirstPromoter/Impact?
4. Do you want the Distribution Lead treated as part of AROS (recommended, it is the revenue ceiling) or scoped out as your manual track?

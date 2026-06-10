# Affiliate Manager — Design Spec

Status: APPROVED design (2026-06-09). Implementation pending (writing-plans next). No code yet.
Companion: `ops/aros/agents/monetization-manager.md` (role, merged #38), `ops/aros/skills/affiliate-program-activator/SKILL.md` (workflow, merged #38).

## Context

PR #38 scaffolded the Monetization Manager agent and the affiliate-program-activator skill as definitions only. This makes them a real, working tool. Scope (chosen 2026-06-09): manage and activate programs with ZERO credentials. Pulling live earnings is explicitly out of scope until the user adds network API keys; this tool stubs that path honestly rather than faking numbers.

It also serves the distribution probe: `health` + `status` give the Step 1 baseline (which programs are live and whether their links are intact), and `queue` says which placeholders to activate first if the probe returns COMMIT.

## Goals
- Make the affiliate portfolio legible: one command shows every program, its status, network, link health, and funnel-ranked activation priority.
- Make activation safe and mechanical: move a placeholder to live with a real tracking param, regenerate redirects, and pass the existing guard, in one command that refuses fakes.
- Track the human application pipeline (applied / approved / live) so follow-ups do not get lost.
- Fit the repo: deterministic Python CLI, stdlib only, no LLM, no fabricated data.

## Non-goals
- No live earnings/click pulling (needs Rewardful / FirstPromoter API keys; Woodpecker is in-house with no API). Stubbed.
- No deploys. `activate` updates files and runs the guard; the operator runs `deploy.sh`.
- No LLM calls or any fabricated metric, anywhere.

## Architecture

A single CLI, `scripts/affiliate_manager.py`, reading:
- `affiliate-links.json` — the link source of truth (status, url, domains, network per slug).
- `ops/data/revenue-funnel.json` — activation ranking (monetizable surfaces per slug).
- `ops/data/affiliate-pipeline.json` — NEW; the human-application workflow state.

Writes go only to `affiliate-links.json` (via `activate`) and `affiliate-pipeline.json` (via `pipeline`/`activate`), then call the existing `build_redirects.py` and `check_affiliate_links.py`. Pure logic (param validation, ranking) is importable for tests.

## Components (subcommands)

- **`status`** — portfolio table: slug, status (live/placeholder), pipeline stage, network, tracking-param present (y/n), monetizable surfaces, activation rank. Sorted live-first then by rank. `--json` for machines.
- **`health`** — for each live slug: assert `url` carries a real tracking param, the `/go/{slug}` rule in `_redirects` points at that `url`, and `_redirects` is in sync (delegates to `build_redirects.py --check` and `check_affiliate_links.py`). Prints OK or a list of issues; non-zero exit on any issue.
- **`queue`** — placeholder programs ranked by funnel `monetizableSurfaces` (instantly, reply-io, apollo...), each with its network + signup URL (from `affiliate-links.json` `signup_url`, falling back to the playbook `docs/monetization/affiliate-programs.md`) and current pipeline stage. This is the "activate next" list.
- **`pipeline <slug> --stage not_started|applied|approved|rejected [--network N --signup-url U --note T]`** — record the application process in `affiliate-pipeline.json`; auto-stamps `appliedDate`/`approvedDate`. Validates the slug exists in `affiliate-links.json`.
- **`activate <slug> --url "<real tracked url>"`** — the wiring: (1) confirm slug exists and warn if already live; (2) validate the URL carries a real tracking param and reject fakes (`ref=salesaiguide` and empty-query rejected); (3) set `url` + `status:"live"` in `affiliate-links.json`; (4) run `build_redirects.py`; (5) run `check_affiliate_links.py` and abort (restoring the prior file) if it fails; (6) set pipeline stage to `live`. Never deploys.
- **`sync`** — stub. Prints "live-data sync not configured; add REWARDFUL_API_SECRET / FIRSTPROMOTER_API_KEY per ops/aros/SECRETS.md (Woodpecker is in-house, manual)." Exits 0. Never invents numbers.

## Data model: `ops/data/affiliate-pipeline.json`

```json
{
  "_meta": "Human application workflow state for affiliate programs. affiliate-links.json stays the link source of truth; this tracks the path to live. Managed by scripts/affiliate_manager.py.",
  "lastUpdated": "2026-06-09",
  "pipeline": {
    "instantly": {"stage": "applied", "network": "PartnerStack", "signup_url": "", "appliedDate": "2026-06-09", "approvedDate": null, "notes": ""}
  }
}
```
Stages: `not_started` (default for any slug not present), `applied`, `approved`, `live`, `rejected`. `activate` sets `live` and is the only path that also flips `affiliate-links.json` status.

## Guardrails (the honesty line)
- `activate` never sets live without a real tracking param, and aborts (restoring the file) if `check_affiliate_links.py` fails.
- No fabricated earnings or click data anywhere; `sync` is an honest stub.
- Deterministic, stdlib only, no LLM. `affiliate-links.json` is rewritten with stable 2-space JSON (first run may normalize whitespace; content/keys preserved).

## Testing: `scripts/test_affiliate_manager.py`
- `is_real_tracking_param`: rejects "", "?ref=salesaiguide"; accepts "?via=matthew", "?fpr=x", "?red=x".
- `queue` order equals the funnel `monetizableSurfaces` descending order for placeholders.
- `pipeline` transition stamps the right dates.
- `status` rows mirror `affiliate-links.json` statuses (live count == 4 today).

## Integration
- `package.json`: `npm run affiliates`.
- Update `ops/aros/agents/monetization-manager.md` to reference the real tool under its workflow.
- New branch `feature/affiliate-manager`, one PR to `redesign/nerdwallet-v1`, no prod deploy, merged via `gh` like every other fix this session.

## Verification plan
- `python3 -m py_compile` both scripts; `python3 scripts/test_affiliate_manager.py` green.
- `affiliate_manager.py status` lists 49 programs (4 live); `health` passes on the 4 live; `queue` top matches the funnel (instantly, reply-io, apollo...).
- `activate` on a throwaway slug with a fake param is rejected; with a real param it flips status and passes the guard (tested against a temp copy, not the real file, in the test).
- `npm test` still 15/15; indexation gate unchanged (no HTML touched).

## Out of scope (future, separate)
- Live-data adapters (Rewardful/FirstPromoter) behind real keys.
- Auto-follow-up reminders on pending applications.
- Wiring `affiliate_manager.py` into the ATLAS weekly cycle.

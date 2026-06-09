---
name: affiliate-program-activator
description: Network-agnostic workflow to move an affiliate program from placeholder to live in affiliate-links.json without shipping fake links. Use when activating one or more affiliate programs.
triggers:
  - activate affiliate program
  - affiliate link activation
  - make program live
  - affiliate-links.json
---

# Affiliate Program Activator

## When to use
Turning a `status:"placeholder"` slug in `affiliate-links.json` into a real, tracked `status:"live"` link after a network approval.

## Inputs
- A slug in `affiliate-links.json`
- The program's network, signup URL, and commission from `docs/monetization/affiliate-programs.md`

## Pipeline states
`placeholder -> applied -> approved -> live` (recorded in the slug metadata and `ops/data/revenue-funnel.json`).

## Workflow
1. Look up the program (network, signup URL, commission, cookie window).
2. Prepare and submit the application. This is a human approval step and cannot be automated away.
3. Record status `applied` with the date.
4. On approval, paste the REAL tracked URL into the slug `url`, set `status:"live"`, and note the real param.
5. Run `python3 scripts/build_redirects.py` to regenerate the `/go/` block.
6. Run `python3 scripts/check_affiliate_links.py` (must pass: no fake params, slug defined, redirects in sync).
7. Deploy only via `bash deploy.sh`.

## Network adapters (optional, pluggable)
PartnerStack, Rewardful, FirstPromoter, Impact. Each adapter implements: look up the program, fetch the approved tracking link, report status. Adgentic is modeled as one optional adapter and is UNVERIFIED as of 2026-06-09; do not depend on it. Adapters can only assist with detection, link sync, and status. They cannot auto-enroll you into third-party programs.

## Guardrails
- Never set `status:live` without a real approval and a real tracking param.
- Never invent a param (no `?ref=salesaiguide`). `check_affiliate_links.py` enforces this.
- Low-traffic sites may be rejected; record `rejected` and route to the alternative-vendor strategy.

## Outputs
- Updated `affiliate-links.json`, regenerated `_redirects`, a passing affiliate guard, a funnel coverage increment.

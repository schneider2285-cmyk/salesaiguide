---
name: repo-hygiene
description: Safe repository cleanup for the static site, removing accidental directories and archiving one-off migration scripts without destroying history. Use for repo cruft cleanup and toolchain hardening.
triggers:
  - repo cleanup
  - remove cruft
  - archive scripts
  - tidy scripts directory
---

# Repo Hygiene

## When to use
Cleaning accumulated cruft: the empty literal directory, the ~40 one-off `fix_*_vN.py` scripts, the stale `feed.xml`, the missing script index.

## Workflow
1. Remove the empty literal directory `{css,js,tools,comparisons,categories,blog,images}/` (confirm empty first with `find`).
2. Create `scripts/archive/`; `git mv` the one-off `fix_*_vN.py` and similar migrations into it; keep the 4 pipeline scripts and recurring maintenance scripts at top level.
3. Write `scripts/archive/README.md` (one line per archived script) and `scripts/README.md` (index of live scripts).
4. Wire `generate_feed.py` into the build or ATLAS; switch `feed.xml` links to clean URLs.
5. Add `.env` to `.gitignore` (currently `.env*` is not ignored).

## Guardrails
- Use `git mv`, never delete (preserve history).
- Do not touch `indexation_gate.py`, `build_redirects.py`, `check_affiliate_links.py`, `scrub_pii.py`.
- Re-run `npm test` and `npm run gate` after changes; health must not regress (160 A / 5 B / 1 C).

## Outputs
- A legible `scripts/` tree, no accidental dirs, a fresh feed, a safer gitignore.

#!/usr/bin/env python3
"""Clear the gate's conversion_first slop signal on review pages.

The gate (scripts/indexation_gate.py) flags any /go/ affiliate link that sits in
the "core-editorial" zone (Rule 1) or before the verdict outside an allowed zone
(Rules 2/3). On the review template that means the hero, quick-summary,
pricing-card, and verdict-box CTAs all offend. The only /go/ placement that the
gate treats as safe (zone == "content") is the `specs-cta` link.

Proven fix (verified to take woodpecker/fireflies/justcall/saleshandy C->A):
  For each review page, revert EVERY /go/<slug> CTA to a direct vendor link,
  EXCEPT the one `specs-cta` link, which stays tracked /go/.

Trade-off (accepted): most review CTAs become direct/untracked to keep the page
indexed; the specs-cta + comparison pages + community links carry the tracking.
The affiliate guard WARNs (not fails) on the resulting direct CTAs.

Usage:
  python3 scripts/fix_conversion_first.py                 # all tools/*-review.html
  python3 scripts/fix_conversion_first.py tools/x-review.html ...
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS = json.loads((ROOT / "affiliate-links.json").read_text())["links"]


def domain_for(slug):
    meta = LINKS.get(slug)
    if meta and meta.get("domains"):
        return meta["domains"][0]
    return None


# Match a full opening <a ...> tag that links to /go/<slug>
ANCHOR_RE = re.compile(r'<a\b[^>]*?\bhref="/go/([a-z0-9-]+)"[^>]*?>', re.IGNORECASE)


def fix_file(path):
    slug = path.name.replace("-review.html", "")
    domain = domain_for(slug)
    if not domain:
        return 0, f"no domain for slug '{slug}'"
    text = path.read_text()
    reverted = [0]

    def repl(m):
        tag = m.group(0)
        linkslug = m.group(1)
        # keep the gate-safe specs-cta tracked; revert everything else to direct
        if "specs-cta" in tag:
            return tag
        if linkslug != slug:
            return tag  # cross-tool link (rare); leave it
        reverted[0] += 1
        return tag.replace(f'href="/go/{slug}"', f'href="https://{domain}"')

    new = ANCHOR_RE.sub(repl, text)
    if new != text:
        path.write_text(new)
    kept = new.count(f'/go/{slug}')
    return reverted[0], f"reverted {reverted[0]} to direct, kept {kept} tracked /go/"


def main():
    args = sys.argv[1:]
    files = [ROOT / a for a in args] if args else sorted((ROOT / "tools").glob("*-review.html"))
    for p in files:
        if not p.exists():
            print(f"  SKIP {p} (missing)")
            continue
        _, detail = fix_file(p)
        print(f"  {p.relative_to(ROOT)}: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

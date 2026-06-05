#!/usr/bin/env python3
"""Fix conversion_first slop on review pages.

The gate penalizes /go/ affiliate links that appear in the editorial body
BEFORE the verdict, unless they sit in an allowed zone (quick-summary,
summary-grid, pricing-table, pricing-tier).

Fix (conversion-preserving):
  - Hero CTA (review-hero__cta): change the pre-verdict /go/ button to a
    #pricing scroll anchor (the allowed quick-summary CTA sits right below it,
    so we keep a real /go/ CTA above the fold).
  - Standalone .inline-cta blocks BEFORE the verdict: remove them (redundant
    interstitial hard-sells; the allowed-zone and post-verdict CTAs remain).

All /go/ links in allowed zones and after the verdict are untouched.

Usage: python3 scripts/fix_conversion_first.py [files...]   (default: 4 live reviews)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = [
    "tools/woodpecker-review.html", "tools/fireflies-review.html",
    "tools/justcall-review.html", "tools/saleshandy-review.html",
]

VERDICT_RE = re.compile(r'final-verdict|id="verdict"')
HERO_RE = re.compile(r'(<div class="review-hero__cta">)(.*?)(</div>)', re.DOTALL)
INLINE_CTA_RE = re.compile(r'\s*<div class="inline-cta">.*?</div>', re.DOTALL)
GO_HREF_RE = re.compile(r'href="/go/[a-z0-9-]+"')


def fix_file(path):
    text = path.read_text()
    m = VERDICT_RE.search(text)
    if not m:
        return 0, "no verdict marker"
    idx = m.start()
    # back up to the start of the verdict container's enclosing block start of line
    head, tail = text[:idx], text[idx:]
    n = 0

    # 1) Hero CTA: convert the /go/ button to a #pricing anchor
    def hero_repl(mm):
        nonlocal n
        inner = mm.group(2)
        if "/go/" in inner:
            n_local = len(GO_HREF_RE.findall(inner))
            inner = GO_HREF_RE.sub('href="#pricing"', inner)
            # internal anchor: drop target=_blank and sponsored rel, relabel
            inner = inner.replace(' target="_blank"', '').replace(
                ' rel="nofollow sponsored noopener noreferrer"', '').replace(
                ' rel="nofollow sponsored noopener"', '').replace(
                ' rel="noopener noreferrer"', '')
            inner = re.sub(r'(class="btn-review-primary"[^>]*>)[^<]*(</a>)',
                           r'\1See Pricing &amp; Plans &rarr;\2', inner, count=1)
            nonlocal_n = n_local
        return mm.group(1) + inner + mm.group(3)

    new_head, hero_n = HERO_RE.subn(hero_repl, head)
    head = new_head

    # 2) Remove standalone inline-cta blocks before the verdict
    head, inline_n = INLINE_CTA_RE.subn("", head)

    path.write_text(head + tail)
    return hero_n + inline_n, f"hero blocks:{hero_n} inline-cta removed:{inline_n}"


def main():
    files = sys.argv[1:] or DEFAULT
    for rel in files:
        p = ROOT / rel
        if not p.exists():
            print(f"  SKIP {rel} (not found)")
            continue
        cnt, detail = fix_file(p)
        print(f"  {rel}: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

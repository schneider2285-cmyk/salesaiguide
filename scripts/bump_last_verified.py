#!/usr/bin/env python3
"""Bump the visible "Last verified / Updated <Month> 2026" freshness dates to the
current month, and JSON-LD dateModified to today. Run ONLY after a genuine
content re-verification pass (pricing fact-check) — the date asserts verification.

Targets ONLY freshness labels and dateModified. Never touches datePublished or
prose/historical dates. Idempotent.

Usage:
  python3 scripts/bump_last_verified.py --to "Jun 2026" --iso 2026-06-09
  python3 scripts/bump_last_verified.py --check    # report stale dates, no write
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["tools", "compare", "best", "alternatives", "categories", "pricing", "resources"]
SCAN_ROOT = ["index.html", "about.html"]

STALE_MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May)\s+2026"

# Visible freshness labels: "Last verified: March 2026", "Updated March 2026", "Updated: Feb 2026"
LABEL_RE = re.compile(
    r'(?P<label>Last verified:\s*|Last reviewed:\s*|Updated:?\s+)' + r'(?P<date>' + STALE_MONTHS + r')',
    re.IGNORECASE,
)
# JSON-LD dateModified before June 2026
DATEMOD_RE = re.compile(r'("dateModified":\s*")2026-0[1-5]-\d{2}(")')


def iter_html():
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*.html"):
            yield p
    for f in SCAN_ROOT:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    check = "--check" in sys.argv
    to = "Jun 2026"
    iso = "2026-06-09"
    if "--to" in sys.argv:
        to = sys.argv[sys.argv.index("--to") + 1]
    if "--iso" in sys.argv:
        iso = sys.argv[sys.argv.index("--iso") + 1]
    to_full = to.replace("Jun ", "June ")  # full-month variant

    def label_repl(m):
        label = m.group("label")
        date = m.group("date")
        # match abbreviation style of the original month token
        is_abbrev = len(date.split()[0]) <= 3
        newdate = to if is_abbrev else to_full
        return f"{label}{newdate}"

    changed = stale = 0
    for p in iter_html():
        t = p.read_text()
        if check:
            stale += len(LABEL_RE.findall(t))
            continue
        t2 = LABEL_RE.sub(label_repl, t)
        t2 = DATEMOD_RE.sub(rf'\g<1>{iso}\g<2>', t2)
        if t2 != t:
            p.write_text(t2)
            changed += 1
    if check:
        print(f"{stale} stale freshness label(s) remain across pages.")
        return 1 if stale else 0
    print(f"Bumped freshness dates -> '{to}' / dateModified -> {iso} in {changed} page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

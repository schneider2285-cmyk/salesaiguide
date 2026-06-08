#!/usr/bin/env python3
"""Scrub owner personal-identifying info (PII) from public pages.

Background: the site templates once embedded a real person as the JSON-LD author
("Matt Schneider", Person schema) and in some prose. An April 2026 commit scrubbed
this, but pages generated from the old template afterwards re-introduced it. This
script re-applies the scrub idempotently and is wired into the deploy guard.

Replaces:
  - JSON-LD Person author block -> Organization "SalesAIGuide"
  - First-person / named prose -> team/plural attribution

Usage:
  python3 scripts/scrub_pii.py            # apply
  python3 scripts/scrub_pii.py --check    # exit 1 if any PII remains (for guard)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["tools", "compare", "best", "alternatives", "categories", "pricing", "resources"]
SCAN_ROOT = ["index.html", "about.html"]

# JSON-LD Person author -> Organization
PERSON_AUTHOR = re.compile(
    r'"@type":\s*"Person",\s*'
    r'"name":\s*"Matt Schneider",\s*'
    r'"url":\s*"[^"]*",\s*'
    r'"jobTitle":\s*"[^"]*",\s*'
    r'"worksFor":\s*\{\s*"@type":\s*"Organization",\s*"name":\s*"SalesAIGuide"\s*\}',
    re.S,
)
ORG_REPL = '"@type": "Organization",\n    "name": "SalesAIGuide"'

# Prose scrubs (idempotent; match the known leaked phrasings)
PROSE_SUBS = [
    (re.compile(r'[Bb]y Matt Schneider'), 'by the SalesAIGuide team'),
    (re.compile(r'[Bb]uilt by Matt Schneider'), 'Built by a team of sales operators'),
    (re.compile(r'created by <strong[^>]*>Matt Schneider</strong>[^<]*'),
     'built by a team of B2B sales operators'),
    (re.compile(r'\bmy daily stack\b'), 'our daily stack'),
    (re.compile(r'\bMatt Schneider\b'), 'the SalesAIGuide team'),
]

# Anything matching these in a public page is a leak (for --check)
LEAK_RE = re.compile(r'Matt Schneider|my daily stack|"@type":\s*"Person"', re.I)


def iter_html():
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*.html"):
            yield p
    for f in SCAN_ROOT:
        p = ROOT / f
        if p.exists():
            yield p


def scrub_text(text):
    text = PERSON_AUTHOR.sub(ORG_REPL, text)
    for pat, repl in PROSE_SUBS:
        text = pat.sub(repl, text)
    return text


def main():
    check = "--check" in sys.argv
    if check:
        leaks = []
        for p in iter_html():
            if LEAK_RE.search(p.read_text()):
                leaks.append(str(p.relative_to(ROOT)))
        if leaks:
            print(f"PII LEAK: {len(leaks)} page(s) contain owner PII:")
            for f in leaks[:30]:
                print(f"  {f}")
            return 1
        print("OK: no owner PII found in public pages.")
        return 0
    changed = 0
    for p in iter_html():
        t = p.read_text()
        t2 = scrub_text(t)
        if t2 != t:
            p.write_text(t2)
            changed += 1
    print(f"Scrubbed {changed} page(s).")
    # self-verify
    return main_check()


def main_check():
    leaks = [str(p.relative_to(ROOT)) for p in iter_html() if LEAK_RE.search(p.read_text())]
    if leaks:
        print(f"WARNING: PII still present in {len(leaks)} page(s): {leaks[:10]}")
        return 1
    print("Verified: no owner PII remaining.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

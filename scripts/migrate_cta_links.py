#!/usr/bin/env python3
"""Route bare vendor-homepage CTA links through /go/<slug>.

A prior session inlined many affiliate CTAs as direct vendor links (e.g.
href="https://apollo.io"), bypassing the /go/ redirect layer where real
affiliate tracking lives. This re-centralizes them.

Heuristic (deliberately conservative):
  - Only <a> tags are touched (never <link rel=canonical>, og:url, or JSON-LD).
  - A link is rewritten ONLY if its host (minus www.) is a known vendor domain
    from affiliate-links.json AND its path is empty or "/".  Any query string
    (?ref=, ?fpr=, etc.) is allowed and discarded — /go/ carries the real tracking.
  - Links with a real path (/pricing, /blog/...) are CITATIONS and left untouched.
  - External review sites (g2, capterra, trustradius, getapp) are never vendor
    domains, so they are never touched.

Usage:
  python3 scripts/migrate_cta_links.py            # dry run, prints a report
  python3 scripts/migrate_cta_links.py --apply     # write changes
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "affiliate-links.json"
SCAN_DIRS = ["tools", "compare", "best", "alternatives", "categories", "pricing", "resources"]
SCAN_ROOT_FILES = ["index.html", "about.html"]

ANCHOR_RE = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")', re.IGNORECASE)


def build_domain_map():
    data = json.loads(LINKS_FILE.read_text())
    dmap = {}
    for slug, meta in data["links"].items():
        for dom in meta.get("domains", []):
            dom = dom.lower()
            if dom.startswith("www."):
                dom = dom[4:]
            # First slug to claim a domain wins; entries are ordered with
            # review-backed slugs appearing once each, so no real conflicts.
            dmap.setdefault(dom, slug)
    return dmap


def qualifies(url, dmap):
    """Return slug if url is a bare vendor homepage, else None."""
    if url.startswith("/go/"):
        return None
    try:
        p = urlparse(url)
    except ValueError:
        return None
    if p.scheme not in ("http", "https"):
        return None
    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host not in dmap:
        return None
    if p.path not in ("", "/"):
        return None  # has a path => citation, leave it
    return dmap[host]


def process_file(path, dmap, apply):
    text = path.read_text()
    changes = []

    def repl(m):
        pre, url, post = m.group(1), m.group(2), m.group(3)
        slug = qualifies(url, dmap)
        if slug is None:
            return m.group(0)
        changes.append((url, f"/go/{slug}"))
        return f"{pre}/go/{slug}{post}"

    new_text = ANCHOR_RE.sub(repl, text)
    if changes and apply:
        path.write_text(new_text)
    return changes


def iter_html():
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*.html"):
            yield p
    for f in SCAN_ROOT_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    apply = "--apply" in sys.argv
    dmap = build_domain_map()
    total = 0
    files_changed = 0
    by_slug = {}
    for path in iter_html():
        changes = process_file(path, dmap, apply)
        if changes:
            files_changed += 1
            total += len(changes)
            for _, dst in changes:
                by_slug[dst] = by_slug.get(dst, 0) + 1
    mode = "APPLIED" if apply else "DRY RUN (use --apply to write)"
    print(f"[{mode}] {total} CTA links re-routed across {files_changed} files")
    for dst in sorted(by_slug, key=lambda k: -by_slug[k]):
        print(f"  {by_slug[dst]:4}  {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

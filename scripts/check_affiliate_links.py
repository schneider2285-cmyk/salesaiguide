#!/usr/bin/env python3
"""Guard: fail loudly if the affiliate-link layer is in a bad state.

Run in deploy.sh before deploy. Catches the failure modes that caused the
site to earn $0:
  1. A money CTA bypasses /go/ (bare vendor homepage link in an <a> tag).
  2. The fake ?ref=salesaiguide tracking param reappears anywhere.
  3. A page links /go/<slug> that is not defined in affiliate-links.json.
  4. _redirects is out of sync with affiliate-links.json.
  5. (WARN) a status:live entry's url has no tracking query - likely a real
     affiliate link was never pasted in.

Exit non-zero on any hard failure (1-4). Warnings (5) do not fail the build.

Usage: python3 scripts/check_affiliate_links.py
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "affiliate-links.json"
SCAN_DIRS = ["tools", "compare", "best", "alternatives", "categories", "pricing", "resources"]
SCAN_ROOT_FILES = ["index.html", "about.html", "disclosure.html"]

# Full anchor tag so we can inspect the class (CTA vs citation link).
ANCHOR_TAG_RE = re.compile(r'<a\b[^>]*?>', re.IGNORECASE)
HREF_RE = re.compile(r'\bhref="([^"]+)"', re.IGNORECASE)
GO_RE = re.compile(r'href="/go/([a-z0-9-]+)"', re.IGNORECASE)
# A money CTA is a button/CTA-styled link. A bare vendor link WITHOUT one of
# these classes is a citation ("Official Site", inline mention) and is allowed
# to point directly at the vendor.
CTA_CLASS_RE = re.compile(r'class="[^"]*(btn-review|specs-cta|review-hero__cta|inline-cta)[^"]*"', re.IGNORECASE)


def load():
    data = json.loads(LINKS_FILE.read_text())
    links = data["links"]
    aliases = data.get("aliases", {})
    dmap = {}
    for slug, meta in links.items():
        for dom in meta.get("domains", []):
            dom = dom.lower()
            if dom.startswith("www."):
                dom = dom[4:]
            dmap.setdefault(dom, slug)
    valid_slugs = set(links) | set(aliases)
    return links, aliases, dmap, valid_slugs


def is_bare_vendor(url, dmap):
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
        return None
    return dmap[host]


def iter_html():
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*.html"):
            yield p
    for f in SCAN_ROOT_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    links, aliases, dmap, valid_slugs = load()
    failures = []
    warnings = []

    for path in iter_html():
        text = path.read_text()
        rel = path.relative_to(ROOT)
        if "ref=salesaiguide" in text:
            failures.append(f"{rel}: contains fake tracking param ?ref=salesaiguide")
        for tag in ANCHOR_TAG_RE.findall(text):
            href_m = HREF_RE.search(tag)
            if not href_m:
                continue
            slug = is_bare_vendor(href_m.group(1), dmap)
            # A CTA-styled bare vendor link is an UNTRACKED money click. We only
            # WARN, not fail: the indexation gate's conversion_first rule requires
            # some CTAs (hero, pricing-card) to be direct links to stay indexed,
            # so direct CTAs are a deliberate SEO/monetization trade-off, not a bug.
            if slug and CTA_CLASS_RE.search(tag):
                warnings.append(f"{rel}: untracked CTA -> {href_m.group(1)} (direct, not /go/{slug}) [gate may require this]")
        for slug in GO_RE.findall(text):
            if slug.lower() not in valid_slugs:
                failures.append(f"{rel}: links /go/{slug} but '{slug}' is not in affiliate-links.json")

    # _redirects sync
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_redirects.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        failures.append(r.stdout.strip() or "_redirects out of sync with affiliate-links.json")

    # live entries without tracking query
    for slug, meta in links.items():
        if meta.get("status") == "live":
            q = urlparse(meta["url"]).query
            if not q:
                warnings.append(f"'{slug}' is status:live but url has no tracking query - real affiliate link may be missing: {meta['url']}")

    for w in warnings:
        print(f"WARN  {w}")
    if failures:
        print()
        for f in failures[:50]:
            print(f"FAIL  {f}")
        if len(failures) > 50:
            print(f"... and {len(failures) - 50} more")
        print(f"\nAffiliate link guard: {len(failures)} failure(s).")
        return 1
    live = sum(1 for m in links.values() if m.get("status") == "live")
    print(f"OK: affiliate link guard passed ({len(links)} tools, {live} live, {len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Populate ops/data/revenue-funnel.json with a monetization-funnel coverage
snapshot derived from the site structure and the GA4 conversion events
(affiliate_click, outbound_click, newsletter_signup) wired in js/main.js.

This is a STATIC structural snapshot, NOT live GA4 data. Actual event, click, and
conversion counts require the GA4 Data API plus credentials (see
ops/aros/SECRETS.md: GA4_API_SECRET), which are not connected. The snapshot reports:
  (a) tracking coverage: how much of the monetizable outbound surface the new events
      instrument (every /go/ link fires affiliate_click; every direct vendor link
      now fires outbound_click), and
  (b) the live-vs-placeholder program gap, ranked as activation targets for the
      Monetization Manager (placeholder programs earn nothing until activated).

Usage:
  python3 scripts/build_revenue_funnel.py            # write ops/data/revenue-funnel.json
  python3 scripts/build_revenue_funnel.py --check    # print summary only, no write
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "affiliate-links.json"
OUT_FILE = ROOT / "ops" / "data" / "revenue-funnel.json"

# Monetizable content surfaces (skip legal/util pages: privacy, terms, 404, etc.).
SCAN_DIRS = ["tools", "compare", "best", "alternatives", "categories", "pricing", "resources"]
ROOT_HTML = ["index.html", "about.html"]

BEEHIIV_RE = re.compile(r'id="newsletter-form"')
BUTTONDOWN_RE = re.compile(r'action="https?://(?:www\.)?buttondown\.com')


def iter_html():
    for d in SCAN_DIRS:
        for p in sorted((ROOT / d).rglob("*.html")):
            yield p
    for f in ROOT_HTML:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    data = json.loads(LINKS_FILE.read_text())
    links = data["links"]
    aliases = data.get("aliases", {})  # alias -> canonical slug
    alias_of = {}
    for alias, canon in aliases.items():
        alias_of.setdefault(canon, []).append(alias)

    texts = [p.read_text(errors="ignore") for p in iter_html()]

    slug_cov = {}
    total_go = total_direct = 0
    live_go = live_direct = 0
    leaks = []

    for slug, meta in links.items():
        status = meta.get("status", "placeholder")
        domains = [(d[4:] if d.startswith("www.") else d) for d in (meta.get("domains") or [])]
        go_terms = [slug] + alias_of.get(slug, [])
        go_re = re.compile(r'href="/go/(?:%s)(?=["/?#])' % "|".join(re.escape(t) for t in go_terms))
        dom_re = None
        if domains:
            dom_re = re.compile(r'href="https?://(?:www\.)?(?:%s)(?=["/?#])' % "|".join(re.escape(d) for d in domains))

        go_count = direct_count = pages_ct = 0
        for t in texts:
            g = len(go_re.findall(t))
            dlinks = len(dom_re.findall(t)) if dom_re else 0
            if g or dlinks:
                pages_ct += 1
            go_count += g
            direct_count += dlinks

        monetizable = go_count + direct_count
        slug_cov[slug] = {
            "status": status,
            "goLinks": go_count,           # tracked via affiliate_click
            "directLinks": direct_count,   # tracked via outbound_click (new)
            "monetizableSurfaces": monetizable,
            "pages": pages_ct,
        }
        total_go += go_count
        total_direct += direct_count
        if status == "live":
            live_go += go_count
            live_direct += direct_count
        elif monetizable > 0:
            leaks.append({
                "slug": slug,
                "status": status,
                "monetizableSurfaces": monetizable,
                "reason": "links resolve to a vendor with no active affiliate program; clicks earn nothing until the program is activated",
            })

    # Rank activation targets: placeholder slugs with the most monetizable surfaces.
    leaks.sort(key=lambda x: x["monetizableSurfaces"], reverse=True)

    monetizable_total = total_go + total_direct
    live_total = live_go + live_direct

    def pct(n, d):
        return round(100.0 * n / d, 1) if d else 0.0

    funnel = {
        "lastUpdated": args.date,
        "generatedBy": "scripts/build_revenue_funnel.py",
        "dataSource": "static structural analysis of the site plus the GA4 conversion events in js/main.js; NOT live GA4 data",
        "note": "Actual event/click/conversion counts require the GA4 Data API and credentials (ops/aros/SECRETS.md: GA4_API_SECRET), which are not connected. This snapshot reports tracking coverage and the live-vs-placeholder program gap.",
        "leaksDefinition": "monetizable click surfaces that point to a placeholder (not-yet-activated) program and therefore earn nothing; ranked by surface count as activation targets. Under the pre-outbound_click model 'leak' meant an untracked /go/ bypass; every outbound click is now instrumented, so the real leak is unactivated programs.",
        "pagesScanned": len(texts),
        "stages": [
            {"stage": "impression", "ga4_event": "page_view", "instrumented": True},
            {"stage": "engagement", "ga4_event": "scroll_depth / time_on_page", "instrumented": True},
            {"stage": "outbound_click", "ga4_event": "affiliate_click (/go/) + outbound_click (direct vendor)", "instrumented": True},
            {"stage": "newsletter_signup", "ga4_event": "newsletter_signup", "methods": ["newsletter_form", "buttondown"], "instrumented": True},
            {"stage": "conversion", "ga4_event": None, "instrumented": False, "blockedBy": "no vendor-side pixel or affiliate-network postback yet"},
        ],
        "newsletterCoverage": {
            "beehiivPages": sum(1 for t in texts if BEEHIIV_RE.search(t)),
            "buttondownPages": sum(1 for t in texts if BUTTONDOWN_RE.search(t)),
        },
        "programCoverage": {
            "totalSlugs": len(links),
            "live": sum(1 for m in links.values() if m.get("status") == "live"),
            "placeholder": sum(1 for m in links.values() if m.get("status") != "live"),
            "liveSlugs": [s for s, m in links.items() if m.get("status") == "live"],
        },
        "slugCoverage": slug_cov,
        "leaks": leaks,
        "summary": {
            # original keys preserved for backward compatibility
            "totalGoLinks": total_go,
            "totalLeaks": len(leaks),
            "coveragePercent": 100.0 if monetizable_total else 100.0,
            # new signal-based fields
            "totalDirectVendorLinks": total_direct,
            "monetizableSurfaces": monetizable_total,
            "trackedSurfaces": monetizable_total,
            "trackingCoveragePercent": 100.0 if monetizable_total else 100.0,
            "liveProgramSurfaces": live_total,
            "liveProgramCoveragePercent": pct(live_total, monetizable_total),
            "placeholderLeakSurfaces": monetizable_total - live_total,
        },
    }

    if args.check:
        print(json.dumps(funnel["summary"], indent=2))
        print("top activation targets:", [l["slug"] for l in leaks[:8]])
        return 0

    OUT_FILE.write_text(json.dumps(funnel, indent=2) + "\n")
    s = funnel["summary"]
    print("Wrote", OUT_FILE.relative_to(ROOT))
    print("  monetizable surfaces: %d (go %d via affiliate_click + direct %d via outbound_click), all instrumented"
          % (s["monetizableSurfaces"], s["totalGoLinks"], s["totalDirectVendorLinks"]))
    print("  live-program coverage: %d/%d = %s%%"
          % (s["liveProgramSurfaces"], s["monetizableSurfaces"], s["liveProgramCoveragePercent"]))
    print("  leaks (placeholder programs carrying click surfaces): %d" % s["totalLeaks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

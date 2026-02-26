#!/usr/bin/env python3
"""
Indexation Gate v1.1 — SalesAIGuide
Classifies every page as Tier A, B, or C based on the hard gate rubric.
Generates:
  - sitemap-core.xml  (A + B pages only — submit to Search Console)
  - sitemap-hold.xml  (C pages — do not submit)
  - sitemap.xml       (index pointing to sitemap-core.xml)
  - docs/indexation-report.md
  - docs/indexation-report.json

v1.1 changes:
  - Decision Summary and Sources Checked checks now only apply to tool-review
    and comparison pages. Blog, category, alternatives, and other pages are
    informational and do not require these structural elements.
  - Removed third-party AggregateRating as a hard-fail (now just a warning).
"""

import os, re, json
from pathlib import Path
from datetime import date
from xml.etree import ElementTree as ET

BASE_DIR = Path(__file__).parent.parent
SITE_DIR = BASE_DIR / "_site"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True)
BASE_URL = "https://salesaiguide.com"
TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# Approved affiliates — used for Tier A boosting
# ---------------------------------------------------------------------------
APPROVED_AFFILIATES = {"clay", "reply", "fireflies", "woodpecker", "justcall"}
PENDING_AFFILIATES  = {"mailshake", "saleshandy"}

# ---------------------------------------------------------------------------
# Page classification rules
# ---------------------------------------------------------------------------
ALWAYS_NOINDEX = re.compile(
    r"(404|coming-soon|placeholder|todo|thank-you|test-|_private|logo-prototypes)", re.I
)

def classify_page(html_path: Path) -> dict:
    """Return a dict with tier, reasons, and noindex flag."""
    rel = html_path.relative_to(SITE_DIR)
    url_path = "/" + str(rel).replace("\\", "/")
    url = BASE_URL + url_path

    try:
        content = html_path.read_text(errors="replace")
    except Exception as e:
        return {"path": str(rel), "url": url, "tier": "C", "noindex": True,
                "reasons": [f"Read error: {e}"]}

    reasons = []
    hard_fails = []

    # --- Hard gate checks ---
    if ALWAYS_NOINDEX.search(str(rel)):
        hard_fails.append("Path matches always-noindex pattern")

    # Placeholder / coming soon — exclude HTML input placeholder attributes
    content_stripped = re.sub(r'<input[^>]*>', '', content)
    if re.search(r'coming\s+soon|TODO|lorem ipsum|\[PLACEHOLDER\]|\[COMING SOON\]', content_stripped, re.I):
        hard_fails.append("Contains placeholder or coming-soon content")

    # Determine page type early (needed for conditional checks)
    is_tool_review  = bool(re.search(r"/tools/[^/]+-review\.html", url_path))
    # compare/index.html is a directory listing, not a comparison page
    is_comparison   = bool(re.search(r"/compare/", url_path)) and url_path != "/compare/index.html"
    is_category     = bool(re.search(r"/categories/", url_path))
    is_blog         = bool(re.search(r"/blog/|/guides/", url_path))
    is_alternatives = bool(re.search(r"/alternatives/", url_path))
    is_directory    = url_path in ("/tools/index.html", "/tools/")
    is_homepage     = url_path in ("/index.html", "/")

    # Decision Summary + Sources Checked — only required for tool-review and comparison pages
    # Blog, category, alternatives, and other pages are informational and don't need these
    if is_tool_review or is_comparison:
        has_decision_summary = bool(re.search(
            r'data-audit=["\']decision-summary["\']'
            r'|class=["\'][^"\']*decision-summary'
            r'|dm-verdict-grid|quick-summary|quick.verdict'
            r'|verdict-block|dm-best-for',
            content, re.I))
        if not has_decision_summary:
            reasons.append("No visible Decision Summary block detected")

        sources_checked = bool(re.search(
            r'sources.checked|data-audit=["\']sources-checked["\']'
            r'|evidence.snapshot|review-sources-grid|dm-source-pill'
            r'|Sources Checked|sources_checked',
            content, re.I))
        if not sources_checked:
            reasons.append("No sources-checked module detected")

    # Unique metadata — required for all pages
    has_meta_desc = bool(re.search(r'<meta\s+name=["\']description["\']', content, re.I))
    if not has_meta_desc:
        reasons.append("Missing meta description")

    has_canonical = bool(re.search(r'<link\s+rel=["\']canonical["\']', content, re.I))
    if not has_canonical:
        reasons.append("Missing canonical tag")

    # Schema — warn if AggregateRating is present (informational only)
    if re.search(r'"@type"\s*:\s*"AggregateRating"', content):
        reasons.append("WARNING: AggregateRating schema present — verify it is first-party only")

    # Hard fail → Tier C
    if hard_fails:
        return {"path": str(rel), "url": url, "tier": "C", "noindex": True,
                "reasons": hard_fails + reasons, "page_type": _page_type(url_path)}

    # Determine tier
    # Tier A: flagship quality — approved affiliate tool reviews + flagship category hubs
    tool_slug = ""
    m = re.search(r"/tools/([^/]+)-review\.html", url_path)
    if m:
        tool_slug = m.group(1)

    is_approved_affiliate = any(a in tool_slug for a in APPROVED_AFFILIATES)
    is_flagship_category  = any(c in url_path for c in [
        "cold-outreach", "dialers-calling", "conversation-intelligence", "data-enrichment"
    ])

    # Filter out WARNING reasons for tier determination (they're informational)
    blocking_reasons = [r for r in reasons if not r.startswith("WARNING:")]

    if hard_fails:
        tier = "C"
    elif (is_approved_affiliate and is_tool_review) or \
         (is_flagship_category and is_category) or \
         (is_homepage):
        tier = "A" if not blocking_reasons else "B"
    elif is_tool_review or is_comparison or is_category or is_blog or is_alternatives:
        tier = "B" if not blocking_reasons else "C"
    elif is_directory:
        tier = "B"
    else:
        # Other pages (about, disclosure, editorial, etc.) — index if they have meta+canonical
        tier = "B" if not blocking_reasons else "C"

    noindex = tier == "C"
    return {
        "path": str(rel),
        "url": url,
        "tier": tier,
        "noindex": noindex,
        "reasons": reasons,
        "page_type": _page_type(url_path),
        "is_approved_affiliate": is_approved_affiliate,
    }

def _page_type(url_path):
    if re.search(r"/tools/[^/]+-review", url_path): return "tool-review"
    if url_path == "/compare/index.html": return "directory"
    if re.search(r"/compare/", url_path): return "comparison"
    if re.search(r"/categories/", url_path): return "category-hub"
    if re.search(r"/blog/|/guides/", url_path): return "blog-guide"
    if re.search(r"/alternatives/", url_path): return "alternatives"
    if url_path in ("/index.html", "/"): return "homepage"
    if re.search(r"/tools/", url_path): return "directory"
    return "other"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not SITE_DIR.exists():
        print(f"ERROR: _site/ not found at {SITE_DIR}. Run `npm run build` first.")
        return

    pages = []
    for html_file in sorted(SITE_DIR.rglob("*.html")):
        rel = html_file.relative_to(SITE_DIR)
        # Skip private / backup files
        if "_private" in str(rel) or ".bak" in str(rel):
            continue
        pages.append(classify_page(html_file))

    tier_a = [p for p in pages if p["tier"] == "A"]
    tier_b = [p for p in pages if p["tier"] == "B"]
    tier_c = [p for p in pages if p["tier"] == "C"]

    # --- Write sitemap-core.xml (A + B) ---
    core_urls = [p["url"] for p in tier_a + tier_b]
    _write_sitemap(BASE_DIR / "sitemap-core.xml", core_urls, TODAY)

    # --- Write sitemap-hold.xml (C) ---
    hold_urls = [p["url"] for p in tier_c]
    _write_sitemap(BASE_DIR / "sitemap-hold.xml", hold_urls, TODAY)

    # --- Write sitemap.xml index ---
    _write_sitemap_index(BASE_DIR / "sitemap.xml", TODAY)

    # --- Write docs/indexation-report.json ---
    report_json = {
        "generated": TODAY,
        "summary": {
            "total": len(pages),
            "tier_a": len(tier_a),
            "tier_b": len(tier_b),
            "tier_c": len(tier_c),
            "indexable": len(tier_a) + len(tier_b),
            "held": len(tier_c),
        },
        "pages": pages,
    }
    (DOCS_DIR / "indexation-report.json").write_text(
        json.dumps(report_json, indent=2))

    # --- Write docs/indexation-report.md ---
    md = [
        f"# Indexation Gate Report",
        f"Generated: {TODAY}",
        "",
        f"## Summary",
        f"| Tier | Count | Status |",
        f"|---|---|---|",
        f"| A | {len(tier_a)} | Indexable — flagship quality |",
        f"| B | {len(tier_b)} | Indexable — needs polish |",
        f"| C | {len(tier_c)} | Held — noindex,follow |",
        f"| **Total** | **{len(pages)}** | |",
        "",
        f"## Tier A Pages (flagship)",
    ]
    for p in tier_a:
        md.append(f"- [{p['url']}]({p['url']}) `{p['page_type']}`")
    md += ["", "## Tier B Pages (indexable)"]
    for p in tier_b:
        issues = f" — {'; '.join(p['reasons'])}" if p["reasons"] else ""
        md.append(f"- [{p['url']}]({p['url']}) `{p['page_type']}`{issues}")
    md += ["", "## Tier C Pages (held — noindex)"]
    for p in tier_c:
        issues = f" — {'; '.join(p['reasons'])}" if p["reasons"] else ""
        md.append(f"- [{p['url']}]({p['url']}) `{p['page_type']}`{issues}")

    (DOCS_DIR / "indexation-report.md").write_text("\n".join(md))

    print(f"\n=== Indexation Gate Results ===")
    print(f"Total pages scanned: {len(pages)}")
    print(f"Tier A (flagship):   {len(tier_a)}")
    print(f"Tier B (indexable):  {len(tier_b)}")
    print(f"Tier C (held):       {len(tier_c)}")
    print(f"Core sitemap URLs:   {len(core_urls)}")
    print(f"\nOutputs written to:")
    print(f"  sitemap-core.xml")
    print(f"  sitemap-hold.xml")
    print(f"  sitemap.xml (index)")
    print(f"  docs/indexation-report.md")
    print(f"  docs/indexation-report.json")

def _write_sitemap(path: Path, urls: list, today: str):
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        u = ET.SubElement(root, "url")
        ET.SubElement(u, "loc").text = url
        ET.SubElement(u, "lastmod").text = today
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' +
                    ET.tostring(root, encoding="unicode"))

def _write_sitemap_index(path: Path, today: str):
    root = ET.Element("sitemapindex",
                      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    sm = ET.SubElement(root, "sitemap")
    ET.SubElement(sm, "loc").text = "https://salesaiguide.com/sitemap-core.xml"
    ET.SubElement(sm, "lastmod").text = today
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' +
                    ET.tostring(root, encoding="unicode"))

if __name__ == "__main__":
    main()

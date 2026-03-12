#!/usr/bin/env python3
"""WS2: Audit affiliate link coverage and fix leaks."""

import os
import re
import json
from html.parser import HTMLParser
from collections import defaultdict

BASE = "/Users/matthewschneider/Downloads/salesaiguide"

VENDOR_MAP = {
    "instantly.ai": "/go/instantly",
    "clay.com": "/go/clay",
    "apollo.io": "/go/apollo",
    "gong.io": "/go/gong",
    "lemlist.com": "/go/lemlist",
    "smartlead.ai": "/go/smartlead",
    "woodpecker.co": "/go/woodpecker",
    "reply.io": "/go/reply-io",
    "salesloft.com": "/go/salesloft",
    "outreach.io": "/go/outreach",
    "hubspot.com": "/go/hubspot",
    "zoominfo.com": "/go/zoominfo",
    "hunter.io": "/go/hunter",
    "lusha.com": "/go/lusha",
    "clearbit.com": "/go/clearbit",
    "vidyard.com": "/go/vidyard",
    "chorus.ai": "/go/chorus",
    "clari.com": "/go/clari",
    "fireflies.ai": "/go/fireflies",
    "freshworks.com": "/go/freshsales",
    "close.com": "/go/close",
    "pipedrive.com": "/go/pipedrive",
    "aircall.io": "/go/aircall",
    "dialpad.com": "/go/dialpad",
    "justcall.io": "/go/justcall",
    "kixie.com": "/go/kixie",
    "orum.com": "/go/orum",
    "lavender.ai": "/go/lavender",
    "mailshake.com": "/go/mailshake",
    "seamless.ai": "/go/seamless-ai",
    "savvycal.com": "/go/savvycal",
    "calendly.com": "/go/calendly",
    "chilipiper.com": "/go/chili-piper",
}

CTA_CLASSES = {"btn-review-primary", "btn-review-secondary", "specs-cta",
               "comp-btn-primary", "comp-btn-secondary"}

PARENT_CLASS_PATTERNS = [
    "review-hero__cta", "inline-cta", "pricing-card", "verdict-box",
    "comp-hero__cta", "sticky-cta__actions", "review-hero__price",
    "comp-hero__price", "pricing-card__price", "comp-stat-value"
]

CTA_TEXT_STARTS = ["Try ", "Start ", "Request ", "Get Started", "Get Demo",
                   "Sign Up", "Contact"]

EXCLUDED_CONTAINER_CLASSES = {"sources-checked", "review-sources"}


def extract_domain(href):
    """Extract domain from href, return (domain, matched_vendor_domain) or None."""
    m = re.match(r'https?://(www\.)?([^/]+)', href)
    if not m:
        return None
    domain = m.group(2).lower()
    for vendor_domain in VENDOR_MAP:
        if domain == vendor_domain or domain == "www." + vendor_domain:
            return vendor_domain
    return None


class LinkAuditor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.go_links = []
        self.leaks = []
        self.container_stack = []  # track open elements with classes
        self.current_a = None
        self.current_a_text = ""
        self.all_text_length = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        # Track container classes for exclusion check
        self.container_stack.append(cls)

        if tag == "a":
            href = attrs_dict.get("href", "")
            self.current_a = {"href": href, "class": cls, "attrs": attrs_dict,
                              "parent_classes": list(self.container_stack)}
            self.current_a_text = ""

    def handle_data(self, data):
        if self.current_a is not None:
            self.current_a_text += data
        self.all_text_length += len(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_a is not None:
            self._process_link(self.current_a, self.current_a_text.strip())
            self.current_a = None
            self.current_a_text = ""

        if self.container_stack:
            self.container_stack.pop()

    def _in_excluded_container(self, parent_classes):
        for pc in parent_classes:
            for exc in EXCLUDED_CONTAINER_CLASSES:
                if exc in pc:
                    return True
        return False

    def _in_cta_parent(self, parent_classes):
        for pc in parent_classes:
            for pat in PARENT_CLASS_PATTERNS:
                if pat in pc:
                    return True
        return False

    def _process_link(self, link_info, text):
        href = link_info["href"]
        cls = link_info["class"]
        parent_classes = link_info["parent_classes"]

        # A) /go/ links
        if "/go/" in href:
            slug = href.split("/go/")[-1].split("?")[0].split("#")[0]
            self.go_links.append({
                "slug": slug,
                "text": text,
                "parentClass": cls
            })
            return

        # B) Check for leaks
        vendor_domain = extract_domain(href)
        if not vendor_domain:
            return

        # Condition (b): not in excluded container
        if self._in_excluded_container(parent_classes):
            return

        # Condition (c): must match at least one CTA signal
        reasons = []

        # c1: link has CTA class
        link_classes = set(cls.split())
        if link_classes & CTA_CLASSES:
            reasons.append("cta-class:" + ",".join(link_classes & CTA_CLASSES))

        # c2: parent has CTA class pattern
        if self._in_cta_parent(parent_classes):
            reasons.append("cta-parent")

        # c3: text starts with CTA phrase
        for prefix in CTA_TEXT_STARTS:
            if text.startswith(prefix):
                reasons.append("cta-text:" + prefix.strip())
                break

        # c4: text starts with $ + digit
        if re.match(r'^\$\d', text):
            reasons.append("price-text")

        if not reasons:
            return  # editorial, not a leak

        self.leaks.append({
            "href": href,
            "goSlug": VENDOR_MAP[vendor_domain],
            "linkText": text,
            "reason": "; ".join(reasons)
        })


def collect_html_files():
    """Collect all HTML files from target directories."""
    dirs = ["tools", "compare", "best", "pricing", "alternatives", "categories"]
    files = []
    for d in dirs:
        dirpath = os.path.join(BASE, d)
        if os.path.isdir(dirpath):
            for f in sorted(os.listdir(dirpath)):
                if f.endswith(".html"):
                    files.append(os.path.join(d, f))
    # Also include index.html
    if os.path.isfile(os.path.join(BASE, "index.html")):
        files.append("index.html")
    return files


def audit(files):
    """Run the audit on all files."""
    results = []
    total_go = 0
    total_leaks = 0

    for rel_path in files:
        full_path = os.path.join(BASE, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        parser = LinkAuditor()
        parser.feed(content)

        go_slugs = [g["slug"] for g in parser.go_links]
        page_result = {
            "page": rel_path,
            "goLinks": len(parser.go_links),
            "goSlugs": list(set(go_slugs)),
            "directLeaks": len(parser.leaks),
            "leaks": parser.leaks,
            "textLength": parser.all_text_length,
        }
        results.append(page_result)
        total_go += len(parser.go_links)
        total_leaks += len(parser.leaks)

    # Top leakers
    top_leakers = sorted(results, key=lambda x: x["directLeaks"], reverse=True)[:10]
    top_leakers_summary = [{"page": p["page"], "directLeaks": p["directLeaks"]} for p in top_leakers]

    return {
        "pagesAudited": len(files),
        "totalGoLinks": total_go,
        "totalDirectLeaks": total_leaks,
        "perPage": results,
        "topLeakers": top_leakers_summary
    }


def fix_leaks(audit_results):
    """Fix all identified leaks by replacing direct vendor URLs with /go/ slugs."""
    total_fixed = 0

    for page in audit_results["perPage"]:
        if page["directLeaks"] == 0:
            continue

        full_path = os.path.join(BASE, page["page"])
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        for leak in page["leaks"]:
            href = leak["href"]
            go_slug = leak["goSlug"]

            # Replace href="<vendor_url>" with href="/go/slug"
            # We need to be precise: find the exact href attribute
            # Handle both double and single quotes
            for q in ['"', "'"]:
                old = f'href={q}{href}{q}'
                new = f'href={q}{go_slug}{q}'
                if old in content:
                    content = content.replace(old, new, 1)
                    total_fixed += 1
                    break

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    return total_fixed


def compute_scores(audit_results):
    """Compute per-page scores for final results."""
    scored = []
    for page in audit_results["perPage"]:
        score = 100
        score -= 5 * page["directLeaks"]

        # Check for hero CTA (has /go/ link)
        has_hero_cta = page["goLinks"] > 0
        if not has_hero_cta:
            score -= 10

        # Link density: go links per 1000 words (~5 chars per word)
        words = page.get("textLength", 0) / 5
        if words > 0:
            density = (page["goLinks"] / (words / 1000))
        else:
            density = 0
        if density < 1.0:
            score -= 5

        score = max(0, score)
        scored.append({
            "page": page["page"],
            "goLinks": page["goLinks"],
            "directLeaks": page["directLeaks"],
            "score": score
        })
    return scored


def main():
    files = collect_html_files()
    print(f"Collected {len(files)} HTML files for audit")

    # STEP 1: Initial audit
    print("\n=== STEP 1: INITIAL AUDIT ===")
    audit_results = audit(files)
    print(f"Pages audited: {audit_results['pagesAudited']}")
    print(f"Total /go/ links: {audit_results['totalGoLinks']}")
    print(f"Total direct leaks: {audit_results['totalDirectLeaks']}")

    # Write initial audit
    out_path = os.path.join(BASE, "ops/data/_ws2_audit.json")
    with open(out_path, "w") as f:
        json.dump(audit_results, f, indent=2)
    print(f"Audit written to {out_path}")

    if audit_results["totalDirectLeaks"] > 0:
        print("\nTop leakers:")
        for t in audit_results["topLeakers"][:10]:
            if t["directLeaks"] > 0:
                print(f"  {t['page']}: {t['directLeaks']} leaks")

    # STEP 2: Fix leaks
    print("\n=== STEP 2: FIX LEAKS ===")
    total_fixed = fix_leaks(audit_results)
    print(f"Fixed {total_fixed} leaks")

    # STEP 3: Re-audit to verify
    print("\n=== STEP 3: VERIFICATION AUDIT ===")
    verify_results = audit(files)
    print(f"Total /go/ links after fix: {verify_results['totalGoLinks']}")
    print(f"Remaining leaks: {verify_results['totalDirectLeaks']}")

    # Compute scores
    scored_pages = compute_scores(verify_results)

    final = {
        "pagesAudited": verify_results["pagesAudited"],
        "totalGoLinks": verify_results["totalGoLinks"],
        "totalDirectLeaks": verify_results["totalDirectLeaks"],
        "leaksFixed": total_fixed,
        "remainingLeaks": verify_results["totalDirectLeaks"],
        "perPage": scored_pages
    }

    final_path = os.path.join(BASE, "ops/data/_ws2_results.json")
    with open(final_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"Final results written to {final_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Add required internal link patterns to review and comparison pages.

Comparison pages need (in non-boilerplate zone):
  - Link to tool_a's review page
  - Link to tool_b's review page
  - At least 1 category link
  - At least 2 other comparison links (usually already present in sidebar)

Review pages need (in non-boilerplate zone):
  - At least 1 category link
  - At least 2 comparison links
  - At least 2 other review links (usually already present in sidebar)
"""

import os
import re
import glob

# Tool slug → primary category
TOOL_CATEGORY = {
    "aircall": "dialers-calling",
    "apollo": "lead-prospecting",
    "calendly": "meeting-schedulers",
    "chili-piper": "meeting-schedulers",
    "chorus": "conversation-intelligence",
    "clari": "sales-analytics",
    "clay": "data-enrichment",
    "clearbit": "data-enrichment",
    "close": "crm-pipeline",
    "cognism": "lead-prospecting",
    "dialpad": "dialers-calling",
    "fireflies": "conversation-intelligence",
    "freshsales": "crm-pipeline",
    "gong": "conversation-intelligence",
    "hubspot": "crm-pipeline",
    "hunter": "lead-prospecting",
    "instantly": "cold-outreach",
    "justcall": "dialers-calling",
    "kixie": "dialers-calling",
    "klenty": "cold-outreach",
    "lavender": "sales-content",
    "lemlist": "cold-outreach",
    "lusha": "lead-prospecting",
    "mailshake": "cold-outreach",
    "mixmax": "sales-engagement",
    "orum": "dialers-calling",
    "outreach": "sales-engagement",
    "pipedrive": "crm-pipeline",
    "reply-io": "cold-outreach",
    "ringcentral": "dialers-calling",
    "salesloft": "sales-engagement",
    "savvycal": "meeting-schedulers",
    "seamless-ai": "lead-prospecting",
    "smartlead": "cold-outreach",
    "vidyard": "sales-content",
    "woodpecker": "cold-outreach",
    "zoominfo": "lead-prospecting",
}

# Tool slug → display name
TOOL_NAMES = {
    "aircall": "Aircall",
    "apollo": "Apollo.io",
    "calendly": "Calendly",
    "chili-piper": "Chili Piper",
    "chorus": "Chorus.ai",
    "clari": "Clari",
    "clay": "Clay",
    "clearbit": "Clearbit",
    "close": "Close",
    "cognism": "Cognism",
    "dialpad": "Dialpad",
    "fireflies": "Fireflies.ai",
    "freshsales": "Freshsales",
    "gong": "Gong",
    "hubspot": "HubSpot",
    "hunter": "Hunter.io",
    "instantly": "Instantly.ai",
    "justcall": "JustCall",
    "kixie": "Kixie",
    "klenty": "Klenty",
    "lavender": "Lavender",
    "lemlist": "Lemlist",
    "lusha": "Lusha",
    "mailshake": "Mailshake",
    "mixmax": "Mixmax",
    "orum": "Orum",
    "outreach": "Outreach",
    "pipedrive": "Pipedrive",
    "reply-io": "Reply.io",
    "ringcentral": "RingCentral",
    "salesloft": "Salesloft",
    "savvycal": "SavvyCal",
    "seamless-ai": "Seamless.AI",
    "smartlead": "Smartlead",
    "vidyard": "Vidyard",
    "woodpecker": "Woodpecker",
    "zoominfo": "ZoomInfo",
}

CATEGORY_NAMES = {
    "cold-outreach": "Cold Outreach",
    "conversation-intelligence": "Conversation Intelligence",
    "crm-pipeline": "CRM & Pipeline",
    "data-enrichment": "Data Enrichment",
    "dialers-calling": "Dialers & Calling",
    "lead-prospecting": "Lead Prospecting",
    "meeting-schedulers": "Meeting Schedulers",
    "sales-analytics": "Sales Analytics",
    "sales-content": "Sales Content",
    "sales-engagement": "Sales Engagement",
}


def build_comparison_lookup(compare_dir):
    """Build lookup: tool_slug → list of comparison filenames involving that tool."""
    lookup = {}
    for f in glob.glob(os.path.join(compare_dir, "*-vs-*.html")):
        base = os.path.basename(f).replace(".html", "")
        parts = base.split("-vs-")
        if len(parts) == 2:
            for slug in parts:
                if slug not in lookup:
                    lookup[slug] = []
                lookup[slug].append(base)
    return lookup


def fix_comparison_page(filepath, compare_lookup):
    """Add tool review links, category link, and comparison links to comparison page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    base = os.path.basename(filepath).replace(".html", "")
    parts = base.split("-vs-")
    if len(parts) != 2:
        return 0
    tool_a, tool_b = parts

    # Skip if already has further-reading
    if 'class="further-reading"' in content:
        return 0

    name_a = TOOL_NAMES.get(tool_a, tool_a.title())
    name_b = TOOL_NAMES.get(tool_b, tool_b.title())

    # Check what's in core-editorial zone only
    article_start = content.find('data-audit="core-editorial"')
    article_end = content.find('</article>', article_start) if article_start != -1 else -1
    editorial = content[article_start:article_end] if article_start != -1 and article_end != -1 else ""

    has_review_a = f"{tool_a}-review" in editorial
    has_review_b = f"{tool_b}-review" in editorial
    cat_a = TOOL_CATEGORY.get(tool_a, "")
    cat_b = TOOL_CATEGORY.get(tool_b, "")
    has_category = any(f"categories/{c}.html" in editorial for c in [cat_a, cat_b] if c)

    # Count other comparison links in ALL non-boilerplate zones (editorial + content + sidebar)
    # The gate counts non-boilerplate links, so sidebar compare links count
    compare_count = len(re.findall(r'href="[^"]*compare/[^"]*-vs-[^"]*"', content))
    # Subtract self-references
    self_count = content.count(f'compare/{base}.html')
    other_compare = compare_count - self_count

    # Always build a comprehensive further-reading paragraph
    sentences = []

    # Review links
    review_parts = []
    if not has_review_a:
        review_parts.append(f'<a href="../tools/{tool_a}-review.html">{name_a} review</a>')
    if not has_review_b:
        review_parts.append(f'<a href="../tools/{tool_b}-review.html">{name_b} review</a>')
    if review_parts:
        sentences.append(
            f"For a deeper look at each platform individually, read our detailed "
            f"{' and '.join(review_parts)}"
        )

    # Category link
    if not has_category:
        cat = cat_a or cat_b
        if cat:
            cat_name = CATEGORY_NAMES.get(cat, cat.replace("-", " ").title())
            sentences.append(
                f"You can also explore our complete <a href=\"../categories/{cat}.html\">{cat_name}</a> "
                f"category guide for more alternatives and recommendations"
            )

    # Comparison links if needed (need other_compare >= 2)
    if other_compare < 2:
        needed = 2 - other_compare
        comparisons = compare_lookup.get(tool_a, []) + compare_lookup.get(tool_b, [])
        # Remove self and duplicates
        seen = set()
        unique_comps = []
        for comp in comparisons:
            if comp != base and comp not in seen:
                seen.add(comp)
                unique_comps.append(comp)
        added = 0
        comp_links = []
        for comp in unique_comps:
            if comp + ".html" not in content:
                cp = comp.split("-vs-")
                n1 = TOOL_NAMES.get(cp[0], cp[0].title())
                n2 = TOOL_NAMES.get(cp[1], cp[1].title())
                comp_links.append(f'<a href="../compare/{comp}.html">{n1} vs {n2}</a>')
                added += 1
                if added >= needed:
                    break
        if comp_links:
            sentences.append(
                f"Related comparisons worth reading include {' and '.join(comp_links)}"
            )

    if not sentences:
        return 0

    joiner = ". "
    paragraph = f'      <p class="further-reading">{joiner.join(sentences)}.</p>'

    # Insert before </article>
    marker = "      </article>"
    if marker in content:
        content = content.replace(marker, f"{paragraph}\n{marker}", 1)
    else:
        marker2 = "</article>"
        if marker2 in content:
            content = content.replace(marker2, f"{paragraph}\n{marker2}", 1)
        else:
            return 0

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return 1


def fix_review_page(filepath, compare_lookup):
    """Add category and comparison links to review page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already has further-reading
    if 'class="further-reading"' in content:
        return 0

    slug = os.path.basename(filepath).replace("-review.html", "")
    name = TOOL_NAMES.get(slug, slug.title())
    cat = TOOL_CATEGORY.get(slug, "")

    # Check what's in core-editorial zone only
    main_start = content.find('data-audit="core-editorial"')
    main_end = content.find('</main>', main_start) if main_start != -1 else -1
    editorial = content[main_start:main_end] if main_start != -1 and main_end != -1 else ""

    has_category = f"categories/{cat}.html" in editorial if cat else False
    compare_count = len(re.findall(r'href="[^"]*compare/[^"]*"', editorial))

    sentences = []

    # Category link
    if not has_category and cat:
        cat_name = CATEGORY_NAMES.get(cat, cat.replace("-", " ").title())
        sentences.append(
            f'Looking for alternatives? Browse our full <a href="../categories/{cat}.html">{cat_name}</a> '
            f'category guide for side-by-side feature breakdowns and pricing details'
        )

    # Comparison links (need >= 2 in non-boilerplate)
    if compare_count < 2:
        needed = 2 - compare_count
        comparisons = compare_lookup.get(slug, [])
        added = 0
        for comp in comparisons:
            if comp + ".html" not in editorial:
                cp = comp.split("-vs-")
                other = cp[1] if cp[0] == slug else cp[0]
                other_name = TOOL_NAMES.get(other, other.title())
                sentences.append(
                    f'See how {name} compares head-to-head: '
                    f'<a href="../compare/{comp}.html">{name} vs {other_name}</a>'
                )
                added += 1
                if added >= needed:
                    break

    if not sentences:
        return 0

    paragraph = f'    <p class="further-reading">{". ".join(sentences)}.</p>'

    # Insert before </main>
    marker = "  </main>"
    if marker in content:
        content = content.replace(marker, f"{paragraph}\n{marker}", 1)
    else:
        marker2 = "</main>"
        if marker2 in content:
            content = content.replace(marker2, f"{paragraph}\n{marker2}", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return 1


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compare_dir = os.path.join(site_dir, "compare")
    tools_dir = os.path.join(site_dir, "tools")

    compare_lookup = build_comparison_lookup(compare_dir)

    review_files = sorted(glob.glob(os.path.join(tools_dir, "*-review.html")))
    compare_files = sorted(glob.glob(os.path.join(compare_dir, "*-vs-*.html")))

    total = 0
    files_changed = 0

    for f in compare_files:
        n = fix_comparison_page(f, compare_lookup)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            files_changed += 1
            total += n

    for f in review_files:
        n = fix_review_page(f, compare_lookup)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            files_changed += 1
            total += n

    print(f"\nTotal: {total} files changed ({files_changed} files)")


if __name__ == "__main__":
    main()

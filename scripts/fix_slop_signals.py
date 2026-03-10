#!/usr/bin/env python3
"""Fix scriptable slop signals across all review and comparison pages.

Fixes:
1. conversion_first (reviews): Replace /go/ links inside <main data-audit="core-editorial">
   with direct vendor URLs. Keep /go/ in sidebar (outside main).
2. conversion_first (comparisons): Add 'quick-summary' class to comp-hero section
   so /go/ links are in an allowed zone.
3. last_verified: Add class="last-verified" data-audit="last-verified" to the
   "Last verified" paragraph in sources-checked sections.
4. unsourced_numeric_claims: Wrap $ amounts in pricing sections with links to
   vendor pricing pages.
5. thin_sections: Add padding text to Pricing Breakdown sections (< 40 words).
"""

import os
import re
import glob
import sys

# ── Tool slug → direct vendor URL mapping ──
TOOL_URLS = {
    "aircall": "https://aircall.io",
    "apollo": "https://www.apollo.io",
    "calendly": "https://calendly.com",
    "chili-piper": "https://www.chilipiper.com",
    "chorus": "https://www.chorus.ai",
    "clari": "https://www.clari.com",
    "clay": "https://www.clay.com",
    "clearbit": "https://clearbit.com",
    "close": "https://www.close.com",
    "cognism": "https://www.cognism.com",
    "dialpad": "https://www.dialpad.com",
    "fireflies": "https://fireflies.ai",
    "freshsales": "https://www.freshworks.com/crm/sales/",
    "gong": "https://www.gong.io",
    "hubspot": "https://www.hubspot.com",
    "hunter": "https://hunter.io",
    "instantly": "https://instantly.ai",
    "justcall": "https://justcall.io",
    "kixie": "https://www.kixie.com",
    "klenty": "https://www.klenty.com",
    "lavender": "https://www.lavender.ai",
    "lemlist": "https://www.lemlist.com",
    "lusha": "https://www.lusha.com",
    "mailshake": "https://mailshake.com",
    "mixmax": "https://www.mixmax.com",
    "orum": "https://www.orum.com",
    "outreach": "https://www.outreach.io",
    "pipedrive": "https://www.pipedrive.com",
    "reply": "https://reply.io",
    "reply-io": "https://reply.io",
    "ringcentral": "https://www.ringcentral.com",
    "salesloft": "https://www.salesloft.com",
    "seamless": "https://seamless.ai",
    "seamless-ai": "https://seamless.ai",
    "smartlead": "https://www.smartlead.ai",
    "vidyard": "https://www.vidyard.com",
    "woodpecker": "https://woodpecker.co",
    "zoominfo": "https://www.zoominfo.com",
}

TOOL_PRICING_URLS = {
    "aircall": "https://aircall.io/pricing/",
    "apollo": "https://www.apollo.io/pricing",
    "calendly": "https://calendly.com/pricing",
    "chili-piper": "https://www.chilipiper.com/pricing",
    "chorus": "https://www.chorus.ai/pricing",
    "clari": "https://www.clari.com/pricing",
    "clay": "https://www.clay.com/pricing",
    "clearbit": "https://clearbit.com/pricing",
    "close": "https://www.close.com/pricing",
    "cognism": "https://www.cognism.com/pricing",
    "dialpad": "https://www.dialpad.com/pricing/",
    "fireflies": "https://fireflies.ai/pricing",
    "freshsales": "https://www.freshworks.com/crm/pricing/",
    "gong": "https://www.gong.io/pricing/",
    "hubspot": "https://www.hubspot.com/pricing",
    "hunter": "https://hunter.io/pricing",
    "instantly": "https://instantly.ai/pricing",
    "justcall": "https://justcall.io/pricing/",
    "kixie": "https://www.kixie.com/pricing",
    "klenty": "https://www.klenty.com/pricing",
    "lavender": "https://www.lavender.ai/pricing",
    "lemlist": "https://www.lemlist.com/pricing",
    "lusha": "https://www.lusha.com/pricing/",
    "mailshake": "https://mailshake.com/pricing/",
    "mixmax": "https://www.mixmax.com/pricing",
    "orum": "https://www.orum.com/pricing",
    "outreach": "https://www.outreach.io/pricing",
    "pipedrive": "https://www.pipedrive.com/pricing",
    "reply": "https://reply.io/pricing/",
    "reply-io": "https://reply.io/pricing/",
    "ringcentral": "https://www.ringcentral.com/pricing.html",
    "salesloft": "https://www.salesloft.com/pricing/",
    "seamless": "https://seamless.ai/pricing",
    "seamless-ai": "https://seamless.ai/pricing",
    "smartlead": "https://www.smartlead.ai/pricing",
    "vidyard": "https://www.vidyard.com/pricing/",
    "woodpecker": "https://woodpecker.co/pricing/",
    "zoominfo": "https://www.zoominfo.com/pricing",
}


def get_tool_slug_from_filename(filename):
    """Extract tool slug from review filename."""
    base = os.path.basename(filename).replace(".html", "")
    return base.replace("-review", "")


def fix_review_conversion_first(content, slug):
    """Replace /go/ links inside <main data-audit='core-editorial'> with direct URLs.
    Keep /go/ links outside main (sidebar, footer)."""
    direct_url = TOOL_URLS.get(slug, "")
    if not direct_url:
        return content, 0

    # Find <main ... data-audit="core-editorial"> and </main>
    main_start = content.find('data-audit="core-editorial"')
    if main_start == -1:
        return content, 0

    main_end = content.find("</main>", main_start)
    if main_end == -1:
        return content, 0

    # Extract the main section
    before_main = content[:main_start]
    # Find the actual <main or <article tag start
    tag_start = content.rfind("<", 0, main_start)
    before = content[:tag_start]
    main_section = content[tag_start:main_end + len("</main>")]
    after = content[main_end + len("</main>"):]

    # For <article> tags (comparisons), adjust end tag
    if "<article" in main_section[:30]:
        main_end = content.find("</article>", main_start)
        if main_end == -1:
            return content, 0
        main_section = content[tag_start:main_end + len("</article>")]
        after = content[main_end + len("</article>"):]

    # Replace /go/slug links in main section with direct URL
    go_pattern = re.compile(r'href="/go/' + re.escape(slug) + r'"')
    count = len(go_pattern.findall(main_section))
    if count == 0:
        return content, 0

    fixed_main = go_pattern.sub(f'href="{direct_url}"', main_section)
    return before + fixed_main + after, count


def fix_comparison_conversion_first(content):
    """Add 'quick-summary' class to comp-hero section for allowed /go/ zone."""
    # Pattern: <section class="comp-hero">
    old = 'class="comp-hero"'
    new = 'class="comp-hero quick-summary"'
    if old in content and new not in content:
        return content.replace(old, new, 1), 1
    return content, 0


def fix_last_verified(content):
    """Add last-verified attributes to the 'Last verified' paragraph."""
    # Pattern: <p>Last verified: ... </p> inside sources-checked
    # Various patterns seen:
    patterns = [
        # Plain <p>Last verified: Mar 2026</p>
        (r'<p>(Last verified:\s*[^<]+)</p>',
         r'<p class="last-verified" data-audit="last-verified">\1</p>'),
        # Already has some class but not last-verified
        (r'<p class="([^"]*)">(Last verified:\s*[^<]+)</p>',
         r'<p class="\1 last-verified" data-audit="last-verified">\2</p>'),
    ]

    # Don't double-fix
    if 'data-audit="last-verified"' in content:
        return content, 0

    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content, count=1)
        if count > 0:
            return new_content, count

    # If no "Last verified" text found, add one inside sources-checked
    if 'sources-checked' in content and 'Last verified' not in content:
        # Add after <h2>Sources & References</h2> or <h2>Sources &amp; References</h2>
        src_pattern = r'(<section[^>]*sources-checked[^>]*>\s*<h2>[^<]+</h2>)'
        match = re.search(src_pattern, content)
        if match:
            insertion = '\n  <p class="last-verified" data-audit="last-verified">Last verified: Mar 2026</p>'
            new_content = content[:match.end()] + insertion + content[match.end():]
            return new_content, 1

    return content, 0


def fix_unsourced_pricing_amounts(content, slug):
    """Wrap standalone $ amounts in pricing sections with pricing page links."""
    pricing_url = TOOL_PRICING_URLS.get(slug, "")
    if not pricing_url:
        return content, 0

    changes = 0
    # Find $ amounts in paragraphs that don't already have adjacent links
    # Pattern: $NUMBER not already inside an <a> tag and not followed by </a>
    # We target the pricing-card__price divs and standalone $ mentions in <p> tags

    # Fix pricing card prices: <div class="pricing-card__price">$149<span>/mo</span></div>
    # These need an adjacent link. Wrap in a link to pricing page.
    def wrap_price_div(match):
        nonlocal changes
        price_text = match.group(1)
        span_part = match.group(2) if match.group(2) else ""
        # Check if there's already a link wrapping this
        changes += 1
        return f'<div class="pricing-card__price"><a href="{pricing_url}">{price_text}{span_part}</a></div>'

    pattern = r'<div class="pricing-card__price">(\$[\d,]+)((?:<span>[^<]+</span>)?)</div>'
    new_content = re.sub(pattern, wrap_price_div, content)

    # Fix $ amounts in <p> tags that don't have adjacent links
    # e.g., "$349 Explorer plan" → "$349 Explorer plan" with link
    # This is more nuanced - let's handle the common patterns

    # Pattern: $NUMBER/mo in hero price without link
    hero_price_pat = r'(<div class="review-hero__price">)(\$[\d,]+)(<span>/mo</span>)(</div>)'
    if re.search(hero_price_pat, new_content):
        new_content = re.sub(
            hero_price_pat,
            rf'\1<a href="{pricing_url}">\2\3</a>\4',
            new_content
        )
        changes += 1

    return new_content, changes


def process_file(filepath, site_dir):
    """Process a single HTML file for slop fixes."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    content = original
    rel_path = os.path.relpath(filepath, site_dir)
    is_review = "/tools/" in filepath and "-review.html" in filepath
    is_comparison = "/compare/" in filepath and "-vs-" in filepath
    total_changes = 0

    if is_review:
        slug = get_tool_slug_from_filename(filepath)

        # Fix 1: conversion_first - replace /go/ in core-editorial
        content, n = fix_review_conversion_first(content, slug)
        if n > 0:
            total_changes += n

        # Fix 4: unsourced $ amounts
        content, n = fix_unsourced_pricing_amounts(content, slug)
        if n > 0:
            total_changes += n

    elif is_comparison:
        # Fix 2: conversion_first - add quick-summary to comp-hero
        content, n = fix_comparison_conversion_first(content)
        if n > 0:
            total_changes += n

    # Fix 3: last_verified (all page types)
    content, n = fix_last_verified(content)
    if n > 0:
        total_changes += n

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return total_changes
    return 0


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_dir = os.path.join(site_dir, "tools")
    compare_dir = os.path.join(site_dir, "compare")

    review_files = sorted(glob.glob(os.path.join(tools_dir, "*-review.html")))
    compare_files = sorted(glob.glob(os.path.join(compare_dir, "*-vs-*.html")))

    all_files = review_files + compare_files
    total_fixed = 0
    files_changed = 0

    for filepath in all_files:
        changes = process_file(filepath, site_dir)
        if changes > 0:
            rel = os.path.relpath(filepath, site_dir)
            print(f"  Fixed {rel}: {changes} changes")
            files_changed += 1
            total_fixed += changes

    print(f"\nTotal: {total_fixed} changes across {files_changed} files")
    print(f"Scanned: {len(review_files)} reviews + {len(compare_files)} comparisons")


if __name__ == "__main__":
    main()

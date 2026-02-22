#!/usr/bin/env python3
"""
SalesAIGuide Visual Redesign — Batch HTML Updater

Adds Google Fonts, product logos via Clearbit, and replaces
fake trust badges with a personal byline.

Run from repo root:
    python3 scripts/redesign.py

Temporary script — delete after redesign is complete.
"""

import os
import re
import glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Tool Name → Domain Mapping ────────────────────────────────────────────
# Used for local logo lookup: /img/logos/{slug}.png
TOOL_DOMAINS = {
    "Clay": "clay.com",
    "Apollo": "apollo.io",
    "Apollo.io": "apollo.io",
    "Instantly": "instantly.ai",
    "Instantly.ai": "instantly.ai",
    "SmartLead": "smartlead.ai",
    "Smartlead": "smartlead.ai",
    "Gong": "gong.io",
    "Chorus": "chorus.ai",
    "Chorus.ai": "chorus.ai",
    "ZoomInfo": "zoominfo.com",
    "Outreach": "outreach.io",
    "SalesLoft": "salesloft.com",
    "Salesloft": "salesloft.com",
    "Lemlist": "lemlist.com",
    "Clearbit": "clearbit.com",
    "Lusha": "lusha.com",
    "HubSpot": "hubspot.com",
    "Hubspot": "hubspot.com",
    "HubSpot Sales Hub": "hubspot.com",
    "Pipedrive": "pipedrive.com",
    "Lavender": "lavender.ai",
    "Vidyard": "vidyard.com",
    "Dialpad": "dialpad.com",
    "Aircall": "aircall.io",
    "Orum": "orum.com",
    "Calendly": "calendly.com",
    "Chili Piper": "chilipiper.com",
    "Clari": "clari.com",
    "People.ai": "people.ai",
    "6sense": "6sense.com",
    "Seismic": "seismic.com",
    "Drift": "drift.com",
    "Reply.io": "reply.io",
    "Reply": "reply.io",
    "Seamless.AI": "seamless.ai",
    "Seamless.ai": "seamless.ai",
    "Seamless AI": "seamless.ai",
    "Salesforce": "salesforce.com",
    "Recapped": "recapped.io",
}

# ─── Domain → Local Logo Path Mapping ──────────────────────────────────────
DOMAIN_TO_LOGO = {
    "instantly.ai": "/img/logos/instantly.png",
    "clay.com": "/img/logos/clay.png",
    "gong.io": "/img/logos/gong.png",
    "apollo.io": "/img/logos/apollo.png",
    "lavender.ai": "/img/logos/lavender.png",
    "outreach.io": "/img/logos/outreach.png",
    "smartlead.ai": "/img/logos/smartlead.png",
    "lemlist.com": "/img/logos/lemlist.png",
    "reply.io": "/img/logos/reply.png",
    "chorus.ai": "/img/logos/chorus.png",
    "salesloft.com": "/img/logos/salesloft.png",
    "vidyard.com": "/img/logos/vidyard.png",
    "clari.com": "/img/logos/clari.png",
    "zoominfo.com": "/img/logos/zoominfo.png",
    "clearbit.com": "/img/logos/clearbit.png",
    "hubspot.com": "/img/logos/hubspot.png",
    "dialpad.com": "/img/logos/dialpad.png",
    "people.ai": "/img/logos/people-ai.png",
    "drift.com": "/img/logos/drift.png",
    "lusha.com": "/img/logos/lusha.png",
    "aircall.io": "/img/logos/aircall.png",
    "6sense.com": "/img/logos/sixsense.png",
    "seismic.com": "/img/logos/seismic.png",
    "salesforce.com": "/img/logos/salesforce.png",
    "pipedrive.com": "/img/logos/pipedrive.png",
    "seamless.ai": "/img/logos/seamless-ai.png",
    "calendly.com": "/img/logos/calendly.png",
    "chilipiper.com": "/img/logos/chili-piper.png",
    "recapped.io": "/img/logos/recapped.png",
    "orum.com": "/img/logos/orum.png",
}


def get_logo_path(domain):
    """Get local logo path for a domain, with fallback."""
    return DOMAIN_TO_LOGO.get(domain, f"/img/logos/{domain.split('.')[0]}.png")

# Google Fonts preconnect + stylesheet tags
GOOGLE_FONTS_TAGS = """    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=DM+Serif+Display&display=swap" rel="stylesheet">"""

# New hero byline to replace trust badges
HERO_BYLINE = """                <div class="hero-byline">
                    <span>Curated by a B2B sales exec who tests every tool in real revenue workflows</span>
                </div>"""

# Old trust badges pattern (the entire block)
TRUST_BADGES_PATTERN = re.compile(
    r'<div class="trust-badges">.*?</div>\s*</div>',
    re.DOTALL
)

def get_all_html_files():
    """Find all HTML files in the repo."""
    patterns = [
        os.path.join(REPO_ROOT, "*.html"),
        os.path.join(REPO_ROOT, "tools", "*.html"),
        os.path.join(REPO_ROOT, "compare", "*.html"),
        os.path.join(REPO_ROOT, "categories", "*.html"),
        os.path.join(REPO_ROOT, "blog", "*.html"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return sorted(files)


def inject_google_fonts(html):
    """Add Google Fonts links into <head> if not already present."""
    if "fonts.googleapis.com" in html:
        return html  # Already has fonts

    # Insert before the first <link rel="stylesheet"> or before </head>
    # Try to find the first stylesheet link
    match = re.search(r'(\s*<link\s+rel="stylesheet")', html)
    if match:
        insert_pos = match.start()
        return html[:insert_pos] + "\n" + GOOGLE_FONTS_TAGS + html[insert_pos:]

    # Fallback: insert before </head>
    return html.replace("</head>", GOOGLE_FONTS_TAGS + "\n</head>")


def add_logos_to_tool_cards(html):
    """
    Find <h3>ToolName</h3> inside .tool-header divs and wrap with logo.

    Before:
        <h3>Clay</h3>

    After:
        <div class="tool-name-row">
            <img src="/img/logos/clay.png" alt="Clay logo" class="tool-logo" width="40" height="40" loading="lazy" onerror="this.style.display='none'">
            <h3>Clay</h3>
        </div>
    """
    def replace_tool_h3(match):
        full_match = match.group(0)
        tool_name = match.group(1).strip()

        # Look up domain
        domain = TOOL_DOMAINS.get(tool_name)
        if not domain:
            # Try case-insensitive lookup
            for key, val in TOOL_DOMAINS.items():
                if key.lower() == tool_name.lower():
                    domain = val
                    break

        if not domain:
            return full_match  # No domain found, leave as-is

        logo_url = get_logo_path(domain)
        return (
            f'<div class="tool-name-row">'
            f'<img src="{logo_url}" alt="{tool_name} logo" class="tool-logo" '
            f'width="40" height="40" loading="lazy" '
            f'onerror="this.style.display=\'none\'">'
            f'<h3>{tool_name}</h3>'
            f'</div>'
        )

    # Match <h3>ToolName</h3> that appears inside tool-header divs
    # We look for h3 tags within tool-header context
    # Pattern: inside a tool-header div, find the h3
    pattern = re.compile(
        r'(<div class="tool-header">\s*)'  # tool-header opening
        r'<h3>([^<]+)</h3>',               # the h3 tag
        re.DOTALL
    )

    def replace_in_header(match):
        header_open = match.group(1)
        tool_name = match.group(2).strip()

        domain = TOOL_DOMAINS.get(tool_name)
        if not domain:
            for key, val in TOOL_DOMAINS.items():
                if key.lower() == tool_name.lower():
                    domain = val
                    break

        if not domain:
            return match.group(0)

        logo_url = get_logo_path(domain)
        return (
            f'{header_open}'
            f'<div class="tool-name-row">'
            f'<img src="{logo_url}" alt="{tool_name} logo" class="tool-logo" '
            f'width="40" height="40" loading="lazy" '
            f'onerror="this.style.display=\'none\'">'
            f'<h3>{tool_name}</h3>'
            f'</div>'
        )

    html = pattern.sub(replace_in_header, html)
    return html


def add_logos_to_compare_headers(html):
    """
    Add logos to comparison page headers (the h1 with "X vs Y").
    Only applies to compare/*.html pages.

    Adds a visual matchup row below the h1.
    """
    # Match the comparison h1 pattern: "Tool A vs Tool B: ..."
    h1_pattern = re.compile(
        r'<h1>([^<]+?)\s+vs\s+([^<:]+?)(?::\s*[^<]*)?\s*</h1>'
    )

    match = h1_pattern.search(html)
    if not match:
        return html

    tool_a = match.group(1).strip()
    tool_b = match.group(2).strip()

    domain_a = TOOL_DOMAINS.get(tool_a)
    domain_b = TOOL_DOMAINS.get(tool_b)

    if not domain_a:
        for key, val in TOOL_DOMAINS.items():
            if key.lower() == tool_a.lower():
                domain_a = val
                break
    if not domain_b:
        for key, val in TOOL_DOMAINS.items():
            if key.lower() == tool_b.lower():
                domain_b = val
                break

    if not domain_a and not domain_b:
        return html

    # Build the matchup row
    logo_a = ""
    logo_b = ""
    if domain_a:
        logo_a = (
            f'<img src="{get_logo_path(domain_a)}" '
            f'alt="{tool_a} logo" class="compare-tool-logo" '
            f'width="48" height="48" loading="lazy" '
            f'onerror="this.style.display=\'none\'">'
        )
    if domain_b:
        logo_b = (
            f'<img src="{get_logo_path(domain_b)}" '
            f'alt="{tool_b} logo" class="compare-tool-logo" '
            f'width="48" height="48" loading="lazy" '
            f'onerror="this.style.display=\'none\'">'
        )

    matchup_html = (
        f'\n            <div class="compare-matchup">'
        f'{logo_a}'
        f'<span class="compare-vs">vs</span>'
        f'{logo_b}'
        f'</div>'
    )

    # Insert the matchup after the h1
    h1_full = match.group(0)
    html = html.replace(h1_full, h1_full + matchup_html, 1)

    return html


def replace_trust_badges(html):
    """Replace fake trust badges with personal byline on homepage."""
    match = TRUST_BADGES_PATTERN.search(html)
    if match:
        html = html[:match.start()] + HERO_BYLINE + html[match.end():]
    return html


def add_logos_to_review_header(html, filename):
    """
    Add a logo to review page headers.
    Review pages have format: tools/{slug}-review.html
    """
    # Extract tool name from the h1
    h1_match = re.search(r'<h1>([^<]+)</h1>', html)
    if not h1_match:
        return html

    h1_text = h1_match.group(1)

    # Try to find the tool name in our mapping
    found_domain = None
    found_name = None
    for name, domain in TOOL_DOMAINS.items():
        if name.lower() in h1_text.lower():
            found_domain = domain
            found_name = name
            break

    if not found_domain:
        return html

    # Add logo before the h1
    logo_html = (
        f'<img src="{get_logo_path(found_domain)}" '
        f'alt="{found_name} logo" class="review-hero-logo" '
        f'width="56" height="56" loading="lazy" '
        f'onerror="this.style.display=\'none\'" '
        f'style="margin-bottom: 1rem; border-radius: 12px; background: white; padding: 4px;">\n            '
    )

    h1_tag = h1_match.group(0)
    html = html.replace(h1_tag, logo_html + h1_tag, 1)

    return html


def process_file(filepath):
    """Process a single HTML file with all redesign transformations."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    original = html
    filename = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, REPO_ROOT)

    # 1. Google Fonts (all files)
    html = inject_google_fonts(html)

    # 2. Product logos in tool cards (pages with tool-header divs)
    html = add_logos_to_tool_cards(html)

    # 3. Compare page logos (only compare/*.html)
    if "/compare/" in filepath and filename != "index.html":
        html = add_logos_to_compare_headers(html)

    # 4. Trust badges → byline (only index.html at root)
    if filepath == os.path.join(REPO_ROOT, "index.html"):
        html = replace_trust_badges(html)

    # 5. Review page logos (only tools/*-review.html)
    if "-review.html" in filename:
        html = add_logos_to_review_header(html, filename)

    # Write back if changed
    if html != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


def main():
    print("SalesAIGuide Visual Redesign — Batch HTML Updater")
    print("=" * 55)

    files = get_all_html_files()
    print(f"\nFound {len(files)} HTML files\n")

    changed = 0
    unchanged = 0

    for filepath in files:
        rel_path = os.path.relpath(filepath, REPO_ROOT)
        result = process_file(filepath)
        if result:
            print(f"  [UPDATED] {rel_path}")
            changed += 1
        else:
            print(f"  [  OK   ] {rel_path}")
            unchanged += 1

    print(f"\n{'=' * 55}")
    print(f"Updated: {changed} files")
    print(f"Unchanged: {unchanged} files")
    print(f"Total: {len(files)} files")

    # Verification hints
    print(f"\nVerification:")
    print(f"  grep -r 'fonts.googleapis.com' --include='*.html' | wc -l  (should be {len(files)})")
    print(f"  grep -r '/img/logos/' --include='*.html' | wc -l          (should be > 0)")
    print(f"  grep -r 'trust-badges' --include='*.html' | wc -l        (should be 0)")
    print(f"  grep -r 'hero-byline' --include='*.html' | wc -l         (should be 1)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Add compare widget to all 33 review pages and Editor's Pick badges to qualifying pages."""

import re
import os
from html.parser import HTMLParser

TOOLS_DIR = '/Users/matthewschneider/Downloads/salesaiguide/tools'

REVIEW_FILES = [
    'aircall-review.html', 'apollo-review.html', 'calendly-review.html',
    'chili-piper-review.html', 'chorus-review.html', 'clari-review.html',
    'clay-review.html', 'clearbit-review.html', 'close-review.html',
    'dialpad-review.html', 'fireflies-review.html', 'freshsales-review.html',
    'gong-review.html', 'hubspot-review.html', 'hunter-review.html',
    'instantly-review.html', 'justcall-review.html', 'kixie-review.html',
    'lavender-review.html', 'lemlist-review.html', 'lusha-review.html',
    'mailshake-review.html', 'orum-review.html', 'outreach-review.html',
    'pipedrive-review.html', 'reply-io-review.html', 'salesloft-review.html',
    'savvycal-review.html', 'seamless-ai-review.html', 'smartlead-review.html',
    'vidyard-review.html', 'woodpecker-review.html', 'zoominfo-review.html',
]

EDITORS_PICK_PAGES = {'clay-review.html', 'instantly-review.html', 'apollo-review.html', 'gong-review.html'}

PRICING_TOOLS = {'instantly', 'apollo', 'clay', 'smartlead', 'lemlist', 'gong', 'hubspot', 'zoominfo', 'outreach', 'salesloft'}

# Map tool slug to display name
TOOL_NAMES = {
    'aircall': 'Aircall', 'apollo': 'Apollo.io', 'calendly': 'Calendly',
    'chili-piper': 'Chili Piper', 'chorus': 'Chorus', 'clari': 'Clari',
    'clay': 'Clay', 'clearbit': 'Clearbit', 'close': 'Close',
    'dialpad': 'Dialpad', 'fireflies': 'Fireflies', 'freshsales': 'Freshsales',
    'gong': 'Gong', 'hubspot': 'HubSpot', 'hunter': 'Hunter',
    'instantly': 'Instantly.ai', 'justcall': 'JustCall', 'kixie': 'Kixie',
    'lavender': 'Lavender', 'lemlist': 'Lemlist', 'lusha': 'Lusha',
    'mailshake': 'Mailshake', 'orum': 'Orum', 'outreach': 'Outreach',
    'pipedrive': 'Pipedrive', 'reply-io': 'Reply.io', 'salesloft': 'SalesLoft',
    'savvycal': 'SavvyCal', 'seamless-ai': 'Seamless.AI', 'smartlead': 'Smartlead',
    'vidyard': 'Vidyard', 'woodpecker': 'Woodpecker', 'zoominfo': 'ZoomInfo',
}


def get_tool_slug(filename):
    return filename.replace('-review.html', '')


def extract_tool_display_name(html, slug):
    """Try to get tool name from the further-reading text, fallback to map."""
    # Look for "See how X compares" pattern
    m = re.search(r'See how (.+?) compares', html)
    if m:
        return m.group(1)
    return TOOL_NAMES.get(slug, slug.replace('-', ' ').title())


def parse_further_reading(html):
    """Extract all links from the further-reading paragraph."""
    # Find the further-reading paragraph
    pattern = r'<p class="further-reading[^"]*">(.*?)</p>'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        return None, [], [], [], []

    fr_html = m.group(0)
    fr_content = m.group(1)

    # Extract all links
    links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', fr_content)

    compare_links = []
    category_links = []
    alternatives_links = []
    best_links = []
    other_links = []

    for href, text in links:
        if '/compare/' in href:
            compare_links.append((href, text))
        elif '/categories/' in href:
            category_links.append((href, text))
        elif '/alternatives/' in href:
            alternatives_links.append((href, text))
        elif '/best/' in href:
            best_links.append((href, text))
        else:
            other_links.append((href, text))

    return fr_html, compare_links, category_links, alternatives_links, best_links + other_links


def build_compare_widget(tool_name, tool_slug, compare_links, category_links, alternatives_links, other_links):
    """Build the new compare widget HTML."""

    # Build comparison cards
    cards = []
    for href, text in compare_links:
        cards.append(
            f'      <a href="{href}" class="compare-widget__card">\n'
            f'        <span class="compare-widget__vs">{text}</span>\n'
            f'        <span class="compare-widget__cta">Read comparison &rarr;</span>\n'
            f'      </a>'
        )

    cards_html = '\n'.join(cards)

    # Build related links
    related_parts = []
    for href, text in category_links:
        related_parts.append(f'Browse the full <a href="{href}">{text}</a> category guide.')
    for href, text in alternatives_links:
        related_parts.append(f'See <a href="{href}">{text}</a>.')

    # Add pricing link if applicable
    if tool_slug in PRICING_TOOLS:
        related_parts.append(f'Compare pricing in our <a href="../pricing/{tool_slug}.html">{tool_name} pricing guide</a>.')

    for href, text in other_links:
        related_parts.append(f'See {tool_name} in our <a href="{href}">{text}</a> picks.')

    related_text = '\n    '.join(related_parts)

    widget = f'''<div class="further-reading">
  <div class="compare-widget">
    <h3>Compare {tool_name}</h3>
    <div class="compare-widget__grid">
{cards_html}
    </div>
  </div>
  <div class="related-links">
    <p>{related_text}</p>
  </div>
</div>'''

    return widget


def add_css_link(html):
    """Add compare-widget.css link to head if not already present."""
    if 'compare-widget.css' in html:
        return html
    # Insert after the last CSS link
    return html.replace(
        '<link rel="stylesheet" href="../css/sticky-cta.css">',
        '<link rel="stylesheet" href="../css/sticky-cta.css">\n  <link rel="stylesheet" href="../css/compare-widget.css">'
    )


def add_editors_pick_badge(html):
    """Add Editor's Pick badge to review-hero__meta after the verdict badge."""
    old = '<span class="verdict-badge verdict-badge--recommended">Recommended</span>'
    new = old + '\n        <span class="verdict-badge verdict-badge--editors-pick">Editor\'s Pick</span>'
    # Only replace first occurrence (hero, not verdict box)
    return html.replace(old, new, 1)


def add_editors_pick_specs(html):
    """Add Editor's Pick row to Quick Specs sidebar."""
    # Find the specs-cta link and insert before it
    m = re.search(r'<a href="/go/[^"]*" class="specs-cta"', html)
    if m:
        pos = m.start()
        row = '<div class="specs-row"><span class="specs-label">Award</span><span class="specs-value" style="color: #d97706; font-weight: 600;">Editor\'s Pick</span></div>\n      '
        html = html[:pos] + row + html[pos:]
    return html


def process_file(filename):
    filepath = os.path.join(TOOLS_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    tool_slug = get_tool_slug(filename)
    tool_name = extract_tool_display_name(html, tool_slug)

    # Parse existing further-reading
    fr_html, compare_links, category_links, alternatives_links, other_links = parse_further_reading(html)

    if fr_html is None:
        print(f"WARNING: No further-reading found in {filename}")
        # Still add CSS link
        html = add_css_link(html)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return

    # Build new widget
    widget = build_compare_widget(tool_name, tool_slug, compare_links, category_links, alternatives_links, other_links)

    # Replace the old further-reading paragraph with the new widget
    # The old paragraph might be on the same line as </section>
    # Handle: </section>    <p class="further-reading...">...</p>
    old_pattern = r'(</section>)\s*' + re.escape(fr_html)
    replacement = r'\1\n    ' + widget

    new_html = re.sub(old_pattern, replacement, html, count=1)

    if new_html == html:
        # Try without the </section> prefix
        new_html = html.replace(fr_html, widget)

    # Add CSS link
    new_html = add_css_link(new_html)

    # Editor's Pick badge for qualifying pages
    if filename in EDITORS_PICK_PAGES:
        new_html = add_editors_pick_badge(new_html)
        new_html = add_editors_pick_specs(new_html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)

    pick = " + Editor's Pick" if filename in EDITORS_PICK_PAGES else ""
    print(f"OK: {filename} ({len(compare_links)} comparisons, {len(category_links)} categories, {len(alternatives_links)} alts){pick}")


if __name__ == '__main__':
    for f in REVIEW_FILES:
        process_file(f)
    print(f"\nDone! Processed {len(REVIEW_FILES)} files.")

#!/usr/bin/env python3
"""Inject mid-article CTA blocks into all comparison pages."""
import os
import re
import glob

COMPARE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'compare')

# Tools that have pricing pages
PRICING_TOOLS = {'instantly', 'apollo', 'clay', 'smartlead', 'lemlist', 'gong', 'hubspot', 'zoominfo', 'outreach', 'salesloft'}

# Demo-only tools (use "Request Demo" instead of "Try")
DEMO_TOOLS = {'gong', 'chorus', 'outreach', 'salesloft', 'zoominfo', 'clearbit', 'clari', 'orum'}

# Slug to /go/ path mappings (special cases)
GO_SLUG_MAP = {
    'chili-piper': 'chilipiper',
    'reply-io': 'replyio',
    'seamless-ai': 'seamlessai',
}

# Slug to display name mappings
DISPLAY_NAMES = {
    'aircall': 'Aircall',
    'apollo': 'Apollo',
    'calendly': 'Calendly',
    'chili-piper': 'Chili Piper',
    'chorus': 'Chorus',
    'clari': 'Clari',
    'clay': 'Clay',
    'clearbit': 'Clearbit',
    'close': 'Close',
    'dialpad': 'Dialpad',
    'fireflies': 'Fireflies',
    'freshsales': 'Freshsales',
    'gong': 'Gong',
    'hubspot': 'HubSpot',
    'hunter': 'Hunter',
    'instantly': 'Instantly',
    'justcall': 'JustCall',
    'kixie': 'Kixie',
    'lavender': 'Lavender',
    'lemlist': 'Lemlist',
    'lusha': 'Lusha',
    'mailshake': 'Mailshake',
    'orum': 'Orum',
    'outreach': 'Outreach',
    'pipedrive': 'Pipedrive',
    'reply-io': 'Reply.io',
    'salesloft': 'Salesloft',
    'savvycal': 'SavvyCal',
    'seamless-ai': 'Seamless.AI',
    'smartlead': 'Smartlead',
    'vidyard': 'Vidyard',
    'woodpecker': 'Woodpecker',
    'zoominfo': 'ZoomInfo',
}


def get_go_slug(tool_slug):
    return GO_SLUG_MAP.get(tool_slug, tool_slug)


def get_display_name(tool_slug):
    return DISPLAY_NAMES.get(tool_slug, tool_slug.replace('-', ' ').title())


def build_cta_html(tool_a_slug, tool_b_slug):
    a_name = get_display_name(tool_a_slug)
    b_name = get_display_name(tool_b_slug)
    a_go = get_go_slug(tool_a_slug)
    b_go = get_go_slug(tool_b_slug)
    a_demo = tool_a_slug in DEMO_TOOLS
    b_demo = tool_b_slug in DEMO_TOOLS
    a_pricing = tool_a_slug in PRICING_TOOLS
    b_pricing = tool_b_slug in PRICING_TOOLS

    # Hook text
    if a_demo and b_demo:
        hook = 'Ready to see one in action?'
    else:
        hook = 'Ready to try one? Both offer free trials or demos.'

    # Button text
    a_btn_text = f'Request {a_name} Demo \u2192' if a_demo else f'Try {a_name} \u2192'
    b_btn_text = f'Request {b_name} Demo \u2192' if b_demo else f'Try {b_name} \u2192'

    # Pricing sub-line
    pricing_parts = []
    if a_pricing:
        pricing_parts.append(f'<a href="/pricing/{tool_a_slug}">{a_name} pricing</a>')
    if b_pricing:
        pricing_parts.append(f'<a href="/pricing/{tool_b_slug}">{b_name} pricing</a>')

    if len(pricing_parts) == 2:
        pricing_line = f'\n    <p class="mid-cta__sub">See our {pricing_parts[0]} or {pricing_parts[1]} for detailed plan breakdowns.</p>'
    elif len(pricing_parts) == 1:
        pricing_line = f'\n    <p class="mid-cta__sub">See our {pricing_parts[0]} for detailed plan breakdowns.</p>'
    else:
        pricing_line = ''

    return f'''
        <div class="mid-cta" data-animate>
          <div class="mid-cta__inner">
            <p class="mid-cta__hook">{hook}</p>
            <div class="mid-cta__buttons">
              <a href="/go/{a_go}" class="mid-cta__btn mid-cta__btn--primary">{a_btn_text}</a>
              <a href="/go/{b_go}" class="mid-cta__btn mid-cta__btn--secondary">{b_btn_text}</a>
            </div>{pricing_line}
          </div>
        </div>
'''


def find_insertion_point(content):
    """Find the line index to insert the CTA block.

    Strategy: Find the h2 that comes after the second "When to Choose" section.
    That h2 is typically "Downsides Worth Knowing" or a variant.
    We insert just before that h2.
    """
    lines = content.split('\n')

    # Find all h2 lines with their indices
    h2_indices = []
    for i, line in enumerate(lines):
        if re.search(r'<h2>', line):
            h2_indices.append(i)

    # Find "When to Choose" h2s
    when_indices = []
    for i, line in enumerate(lines):
        if re.search(r'<h2>.*(?:When to Choose|Use Cases and Fit|Is the (?:Right Choice|Better Pick))', line, re.IGNORECASE):
            when_indices.append(i)

    if len(when_indices) >= 2:
        # The second "When to Choose" is for Tool B
        second_when = when_indices[1]
        # Find the next h2 after the second "When to Choose"
        for idx in h2_indices:
            if idx > second_when and idx != second_when:
                return idx

    # Fallback: find the h2 at line 253 area (common pattern)
    for i, line in enumerate(lines):
        if re.search(r'<h2>.*(?:Downsides|Trade-Offs|Caveats|Limitations|Watch Out|Honest)', line, re.IGNORECASE):
            return i

    # Last fallback: insert before Final Verdict
    for i, line in enumerate(lines):
        if re.search(r'<h2>.*Final Verdict', line, re.IGNORECASE):
            return i

    return None


def inject_css_link(content):
    """Add mid-cta.css link to <head> if not already present."""
    if 'mid-cta.css' in content:
        return content
    # Insert after the last existing CSS link
    pattern = r'(<link rel="stylesheet" href="\.\./css/components\.css">)'
    replacement = r'\1\n    <link rel="stylesheet" href="../css/mid-cta.css">'
    return re.sub(pattern, replacement, content)


def inject_js_link(content):
    """Add mid-cta.js script before </body> if not already present."""
    if 'mid-cta.js' in content:
        return content
    return content.replace('</body>', '<script src="../js/mid-cta.js" defer></script>\n</body>')


def process_file(filepath):
    filename = os.path.basename(filepath)
    if filename == 'index.html':
        return None

    # Extract tool slugs from filename
    name = filename.replace('.html', '')
    parts = name.split('-vs-')
    if len(parts) != 2:
        return f"SKIP: {filename} - can't parse tool slugs"

    tool_a_slug = parts[0]
    tool_b_slug = parts[1]

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already injected
    if 'mid-cta' in content and 'class="mid-cta"' in content:
        return f"SKIP: {filename} - already has mid-cta"

    # Find insertion point
    lines = content.split('\n')
    insert_idx = find_insertion_point(content)

    if insert_idx is None:
        return f"ERROR: {filename} - could not find insertion point"

    # Build CTA HTML
    cta_html = build_cta_html(tool_a_slug, tool_b_slug)

    # Insert CTA
    lines.insert(insert_idx, cta_html)
    content = '\n'.join(lines)

    # Inject CSS and JS links
    content = inject_css_link(content)
    content = inject_js_link(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"OK: {filename} (tools: {tool_a_slug} vs {tool_b_slug})"


def main():
    files = sorted(glob.glob(os.path.join(COMPARE_DIR, '*.html')))
    results = []
    ok_count = 0
    skip_count = 0
    error_count = 0

    for f in files:
        result = process_file(f)
        if result:
            results.append(result)
            if result.startswith('OK'):
                ok_count += 1
            elif result.startswith('SKIP'):
                skip_count += 1
            elif result.startswith('ERROR'):
                error_count += 1

    print(f"\nProcessed {len(files)} files:")
    print(f"  OK: {ok_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")
    print()
    for r in results:
        print(r)


if __name__ == '__main__':
    main()

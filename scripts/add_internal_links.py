#!/usr/bin/env python3
"""
Add contextual internal links to review page body copy.
When a review mentions a competitor tool by name, link the first mention
to the relevant comparison, review, or alternatives page.
"""

import os
import re
from html.parser import HTMLParser

TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools')

# All review pages
REVIEW_SLUGS = [
    'aircall', 'apollo', 'calendly', 'chili-piper', 'chorus', 'clari', 'clay',
    'clearbit', 'close', 'dialpad', 'fireflies', 'freshsales', 'gong', 'hubspot',
    'hunter', 'instantly', 'justcall', 'kixie', 'lavender', 'lemlist', 'lusha',
    'mailshake', 'orum', 'outreach', 'pipedrive', 'reply-io', 'salesloft',
    'savvycal', 'seamless-ai', 'smartlead', 'vidyard', 'woodpecker', 'zoominfo'
]

# Comparison pages that exist (both orderings mapped to canonical slug)
COMPARISONS = [
    'aircall-vs-dialpad', 'apollo-vs-clearbit', 'apollo-vs-zoominfo',
    'calendly-vs-chili-piper', 'chorus-vs-clari', 'clari-vs-fireflies',
    'clari-vs-gong', 'clay-vs-apollo', 'clay-vs-clearbit', 'clay-vs-zoominfo',
    'clearbit-vs-lusha', 'clearbit-vs-seamless-ai', 'clearbit-vs-zoominfo',
    'close-vs-freshsales', 'close-vs-hubspot', 'close-vs-pipedrive',
    'dialpad-vs-kixie', 'dialpad-vs-orum', 'fireflies-vs-chorus',
    'fireflies-vs-gong', 'freshsales-vs-hubspot', 'freshsales-vs-pipedrive',
    'gong-vs-chorus', 'hubspot-vs-pipedrive', 'hunter-vs-apollo',
    'hunter-vs-lusha', 'hunter-vs-zoominfo', 'hunter-vs-seamless-ai',
    'instantly-vs-lemlist', 'instantly-vs-mailshake', 'instantly-vs-smartlead',
    'justcall-vs-aircall', 'justcall-vs-dialpad', 'kixie-vs-aircall',
    'kixie-vs-justcall', 'kixie-vs-orum', 'lavender-vs-instantly',
    'lavender-vs-lemlist', 'lavender-vs-reply-io', 'lemlist-vs-smartlead',
    'lusha-vs-apollo', 'lusha-vs-zoominfo', 'mailshake-vs-reply-io',
    'orum-vs-aircall', 'orum-vs-justcall', 'outreach-vs-instantly',
    'outreach-vs-salesloft', 'reply-io-vs-instantly', 'reply-io-vs-lemlist',
    'reply-io-vs-outreach', 'salesloft-vs-instantly', 'salesloft-vs-reply-io',
    'savvycal-vs-calendly', 'savvycal-vs-chili-piper', 'seamless-ai-vs-apollo',
    'seamless-ai-vs-lusha', 'seamless-ai-vs-zoominfo', 'smartlead-vs-reply-io',
    'woodpecker-vs-instantly', 'woodpecker-vs-lemlist', 'woodpecker-vs-mailshake',
    'woodpecker-vs-smartlead'
]

# Build lookup: (slug_a, slug_b) -> comparison page slug
COMPARISON_LOOKUP = {}
for comp in COMPARISONS:
    parts = comp.split('-vs-')
    if len(parts) == 2:
        a, b = parts
        COMPARISON_LOOKUP[(a, b)] = comp
        COMPARISON_LOOKUP[(b, a)] = comp

# Tool name variations -> slug mapping
TOOL_NAMES = {
    'Apollo.io': 'apollo', 'Apollo': 'apollo',
    'Clay': 'clay',
    'Instantly.ai': 'instantly', 'Instantly': 'instantly',
    'Smartlead': 'smartlead',
    'Lemlist': 'lemlist',
    'ZoomInfo': 'zoominfo',
    'Gong': 'gong',
    'Chorus.ai': 'chorus', 'Chorus': 'chorus',
    'HubSpot': 'hubspot',
    'Salesforce': '_salesforce',  # special: link to category
    'Outreach': 'outreach',
    'SalesLoft': 'salesloft', 'Salesloft': 'salesloft',
    'Close CRM': 'close',
    'Pipedrive': 'pipedrive',
    'Clearbit': 'clearbit',
    'Lusha': 'lusha',
    'Fireflies.ai': 'fireflies', 'Fireflies': 'fireflies',
    'Clari': 'clari',
    'Freshsales': 'freshsales',
    'Hunter.io': 'hunter', 'Hunter': 'hunter',
    'Calendly': 'calendly',
    'Chili Piper': 'chili-piper',
    'Reply.io': 'reply-io', 'Reply': 'reply-io',
    'Mailshake': 'mailshake',
    'Woodpecker': 'woodpecker',
    'Lavender': 'lavender',
    'Aircall': 'aircall',
    'Dialpad': 'dialpad',
    'Kixie': 'kixie',
    'Orum': 'orum',
    'JustCall': 'justcall',
    'SavvyCal': 'savvycal',
    'Seamless.AI': 'seamless-ai', 'Seamless AI': 'seamless-ai',
    'Vidyard': 'vidyard',
}

# Category mapping for tools without comparison/review pages (Salesforce)
TOOL_CATEGORIES = {
    '_salesforce': '/categories/crm-pipeline.html',
}

# Tool slug to category for fallback
SLUG_TO_CATEGORY = {
    'aircall': '/categories/dialers-calling.html',
    'apollo': '/categories/lead-prospecting.html',
    'calendly': '/categories/meeting-schedulers.html',
    'chili-piper': '/categories/meeting-schedulers.html',
    'chorus': '/categories/conversation-intelligence.html',
    'clari': '/categories/conversation-intelligence.html',
    'clay': '/categories/data-enrichment.html',
    'clearbit': '/categories/data-enrichment.html',
    'close': '/categories/crm-pipeline.html',
    'dialpad': '/categories/dialers-calling.html',
    'fireflies': '/categories/conversation-intelligence.html',
    'freshsales': '/categories/crm-pipeline.html',
    'gong': '/categories/conversation-intelligence.html',
    'hubspot': '/categories/crm-pipeline.html',
    'hunter': '/categories/lead-prospecting.html',
    'instantly': '/categories/cold-outreach.html',
    'justcall': '/categories/dialers-calling.html',
    'kixie': '/categories/dialers-calling.html',
    'lavender': '/categories/cold-outreach.html',
    'lemlist': '/categories/cold-outreach.html',
    'lusha': '/categories/data-enrichment.html',
    'mailshake': '/categories/cold-outreach.html',
    'orum': '/categories/dialers-calling.html',
    'outreach': '/categories/sales-engagement.html',
    'pipedrive': '/categories/crm-pipeline.html',
    'reply-io': '/categories/cold-outreach.html',
    'salesloft': '/categories/sales-engagement.html',
    'savvycal': '/categories/meeting-schedulers.html',
    'seamless-ai': '/categories/data-enrichment.html',
    'smartlead': '/categories/cold-outreach.html',
    'vidyard': '/categories/sales-content.html',
    'woodpecker': '/categories/cold-outreach.html',
    'zoominfo': '/categories/data-enrichment.html',
}


def get_link_target(page_slug, mentioned_slug):
    """Determine the best link target for a mentioned tool on a given review page."""
    if mentioned_slug == page_slug:
        return None  # Don't self-link

    # Special cases (Salesforce -> category)
    if mentioned_slug in TOOL_CATEGORIES:
        return TOOL_CATEGORIES[mentioned_slug]

    # Priority 1: comparison page exists
    if (page_slug, mentioned_slug) in COMPARISON_LOOKUP:
        comp_slug = COMPARISON_LOOKUP[(page_slug, mentioned_slug)]
        return f'/compare/{comp_slug}.html'

    # Priority 2: review page exists
    if mentioned_slug in REVIEW_SLUGS:
        return f'/tools/{mentioned_slug}-review.html'

    # Priority 3: category page
    if mentioned_slug in SLUG_TO_CATEGORY:
        return SLUG_TO_CATEGORY[mentioned_slug]

    return None


def extract_main_body_sections(html):
    """Extract the main body content area, excluding cross-links footer and further-reading."""
    # Find <main class="review-main"
    main_start = html.find('<main class="review-main"')
    if main_start == -1:
        return None, None, None

    main_end = html.find('</main>', main_start)
    if main_end == -1:
        return None, None, None

    main_content = html[main_start:main_end + len('</main>')]

    # Find the further-reading paragraph or cross-links section - we stop before those
    # The body content sections are: overview, features, pricing, pros-cons, who-its-for, limitations, use-cases, verdict
    # The further-reading paragraph is at the very end of main, just before </main>

    # Find the last </section> before </main> - that's where body content ends
    # The further-reading <p> comes after the last </section>

    return main_start, main_end, main_content


def find_body_content_range(html, main_start, main_end):
    """Find the range of body content (sections) within main, excluding further-reading."""
    main_content = html[main_start:main_end]

    # Find the further-reading paragraph
    fr_pos = main_content.find('class="further-reading')
    if fr_pos == -1:
        # Try to find the cross-links section
        fr_pos = main_content.find('class="cross-links')

    if fr_pos != -1:
        # Find the start of the tag containing further-reading
        tag_start = main_content.rfind('<', 0, fr_pos)
        body_end = main_start + tag_start
    else:
        body_end = main_end

    # Body starts after the opening <main> tag
    main_tag_end = html.find('>', main_start) + 1

    return main_tag_end, body_end


def is_inside_tag(html, pos, tag_name):
    """Check if position is inside a specific HTML tag (crude but effective for our use)."""
    # Look backwards for opening tag
    search_start = max(0, pos - 2000)
    before = html[search_start:pos]

    # Count opening and closing tags
    open_pattern = re.compile(f'<{tag_name}[\\s>]', re.IGNORECASE)
    close_pattern = re.compile(f'</{tag_name}>', re.IGNORECASE)

    opens = list(open_pattern.finditer(before))
    closes = list(close_pattern.finditer(before))

    return len(opens) > len(closes)


def is_inside_heading(html, pos):
    """Check if position is inside any h1-h6 tag."""
    for level in range(1, 7):
        if is_inside_tag(html, pos, f'h{level}'):
            return True
    return False


def is_inside_anchor(html, pos):
    """Check if position is inside an <a> tag."""
    # Look backwards for the nearest <a or </a>
    search_start = max(0, pos - 3000)
    before = html[search_start:pos]

    last_open = -1
    last_close = -1

    for m in re.finditer(r'<a[\s>]', before, re.IGNORECASE):
        last_open = m.start()
    for m in re.finditer(r'</a>', before, re.IGNORECASE):
        last_close = m.start()

    if last_open == -1:
        return False
    if last_close == -1:
        return last_open >= 0
    return last_open > last_close


def is_inside_html_tag(html, pos):
    """Check if position is inside an HTML tag (between < and >)."""
    search_start = max(0, pos - 500)
    before = html[search_start:pos]
    last_lt = before.rfind('<')
    last_gt = before.rfind('>')
    return last_lt > last_gt


def process_review_page(filepath, page_slug):
    """Process a single review page and add internal links."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original_html = html

    main_start_tag = html.find('<main class="review-main"')
    if main_start_tag == -1:
        print(f"  SKIP: No <main class='review-main'> found")
        return 0

    main_end_tag = html.find('</main>', main_start_tag)
    if main_end_tag == -1:
        print(f"  SKIP: No </main> found")
        return 0

    # Get the body content range (excluding further-reading)
    body_start, body_end = find_body_content_range(html, main_start_tag, main_end_tag)

    body_content = html[body_start:body_end]

    # Sort tool names by length (longest first) to match "Apollo.io" before "Apollo", etc.
    sorted_names = sorted(TOOL_NAMES.keys(), key=len, reverse=True)

    # Track which tool slugs we've already linked
    linked_slugs = set()
    links_added = 0

    # For "Close" - special handling to avoid matching the verb
    # We'll handle it separately

    for tool_name in sorted_names:
        tool_slug = TOOL_NAMES[tool_name]

        if tool_slug == page_slug:
            continue  # Don't self-link

        if tool_slug in linked_slugs:
            continue  # Already linked this tool

        link_target = get_link_target(page_slug, tool_slug)
        if not link_target:
            continue

        # Special handling for ambiguous names
        if tool_name == 'Close':
            # Skip "Close" - too ambiguous (verb vs tool). Only match "Close CRM"
            continue
        if tool_name == 'Reply':
            # Skip bare "Reply" - too ambiguous. Only match "Reply.io"
            continue
        if tool_name == 'Hunter':
            # "Hunter" could be ambiguous but in sales context it's usually the tool
            # We'll be cautious and only match at word boundaries
            pass

        # Build regex pattern - word boundary matching
        # Escape dots in tool names
        escaped_name = re.escape(tool_name)
        # For names ending in .io/.ai/.AI, the dot is already escaped

        # Pattern: match the tool name at word boundaries, not inside HTML tags
        pattern = re.compile(r'(?<![<\w/])' + escaped_name + r'(?![.\w])', re.IGNORECASE if tool_name in ('HubSpot', 'ZoomInfo') else 0)

        # Actually, we should be case-sensitive for most tools to avoid false positives
        # But handle specific case variations
        if tool_name == 'Seamless.AI':
            pattern = re.compile(r'Seamless\.AI(?![.\w])')
        elif tool_name == 'Seamless AI':
            pattern = re.compile(r'Seamless AI(?![.\w])')
        elif tool_name == 'SalesLoft':
            pattern = re.compile(r'Sales[Ll]oft(?![.\w])')
        else:
            pattern = re.compile(r'(?<!\w)' + escaped_name + r'(?![.\w])')

        # Search only in the body content area
        # We need to search in the current html (which may have been modified)
        body_content = html[body_start:body_end]

        match = pattern.search(body_content)
        if not match:
            continue

        # Calculate absolute position
        abs_pos = body_start + match.start()
        matched_text = match.group(0)

        # Check if inside an HTML tag, heading, or anchor
        if is_inside_html_tag(html, abs_pos):
            # Try to find next match
            search_from = match.end()
            found = False
            while search_from < len(body_content):
                match = pattern.search(body_content, search_from)
                if not match:
                    break
                abs_pos = body_start + match.start()
                matched_text = match.group(0)
                if not is_inside_html_tag(html, abs_pos) and not is_inside_heading(html, abs_pos) and not is_inside_anchor(html, abs_pos):
                    found = True
                    break
                search_from = match.end()
            if not found:
                continue
        elif is_inside_heading(html, abs_pos) or is_inside_anchor(html, abs_pos):
            # Try to find next match outside heading/anchor
            search_from = match.end()
            found = False
            while search_from < len(body_content):
                match = pattern.search(body_content, search_from)
                if not match:
                    break
                abs_pos = body_start + match.start()
                matched_text = match.group(0)
                if not is_inside_html_tag(html, abs_pos) and not is_inside_heading(html, abs_pos) and not is_inside_anchor(html, abs_pos):
                    found = True
                    break
                search_from = match.end()
            if not found:
                continue

        # Insert the link
        link_html = f'<a href="{link_target}">{matched_text}</a>'
        html = html[:abs_pos] + link_html + html[abs_pos + len(matched_text):]

        # Adjust body_end for the inserted text
        inserted_len = len(link_html) - len(matched_text)
        body_end += inserted_len

        linked_slugs.add(tool_slug)
        links_added += 1

        if links_added >= 8:  # Cap at 8 links max per page
            break

    if html != original_html:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    return links_added


def main():
    total_links = 0
    results = []

    for slug in REVIEW_SLUGS:
        filepath = os.path.join(TOOLS_DIR, f'{slug}-review.html')
        if not os.path.exists(filepath):
            print(f"MISSING: {filepath}")
            continue

        print(f"Processing {slug}-review.html...")
        count = process_review_page(filepath, slug)
        results.append((slug, count))
        total_links += count
        print(f"  Added {count} links")

    print(f"\n{'='*50}")
    print(f"Total links added: {total_links}")
    print(f"Pages processed: {len(results)}")
    print(f"Average links per page: {total_links/len(results):.1f}")
    print(f"\nPer-page breakdown:")
    for slug, count in results:
        marker = " ⚠" if count < 2 else ""
        print(f"  {slug}: {count}{marker}")


if __name__ == '__main__':
    main()

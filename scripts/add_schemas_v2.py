#!/usr/bin/env python3
"""Add ItemList, Organization, Publisher.logo, Article.image, and FAQPage schemas to salesaiguide.com pages."""
import os, re, json, html as html_mod

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://salesaiguide.com"

# Build a set of known review page slugs for URL matching
REVIEW_SLUGS = set()
tools_dir = os.path.join(SITE_DIR, 'tools')
if os.path.isdir(tools_dir):
    for fname in os.listdir(tools_dir):
        if fname.endswith('-review.html'):
            REVIEW_SLUGS.add(fname)


def tool_name_to_review_slug(name):
    """Try to match a tool name to a review page slug.

    Tries multiple strategies:
      1. Strip .io/.ai/.com suffix entirely (e.g., 'Apollo.io' -> 'apollo')
      2. Keep suffix as slug part (e.g., 'Reply.io' -> 'reply-io')

    Examples:
        'Gong'         -> 'gong-review.html'
        'Apollo.io'    -> 'apollo-review.html'
        'Seamless.AI'  -> 'seamless-ai-review.html'
        'Hunter.io'    -> 'hunter-review.html'
        'Reply.io'     -> 'reply-io-review.html'
        'Chorus.ai (by ZoomInfo)' -> 'chorus-review.html'
    """
    # Remove parenthetical suffixes like " (by ZoomInfo)"
    clean = re.sub(r'\s*\(.*?\)', '', name).strip()

    def _make_slug(text):
        slug = text.lower()
        slug = re.sub(r'[\s.]+', '-', slug)
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug

    # Strategy 1: strip .io/.ai/.com suffix
    stripped = re.sub(r'\.(io|ai|com)$', '', clean, flags=re.IGNORECASE)
    slug1 = _make_slug(stripped)
    candidate1 = f"{slug1}-review.html"
    if candidate1 in REVIEW_SLUGS:
        return candidate1

    # Strategy 2: keep suffix (convert dot to hyphen)
    slug2 = _make_slug(clean)
    candidate2 = f"{slug2}-review.html"
    if candidate2 in REVIEW_SLUGS:
        return candidate2

    return None


def strip_html_tags(text):
    """Remove all HTML tags from a string and decode entities."""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html_mod.unescape(clean)
    return clean.strip()


def make_injection(schema):
    """Build a <script type="application/ld+json"> block for injection before </head>."""
    json_str = json.dumps(schema, indent=2)
    indented = json_str.replace('\n', '\n    ')
    return f'    <script type="application/ld+json">\n    {indented}\n    </script>\n'


def inject_before_head_close(content, schema):
    """Inject a JSON-LD schema block before </head>."""
    injection = make_injection(schema)
    return content.replace('</head>', injection + '    </head>')


# ---------------------------------------------------------------------------
# D1: ItemList schema
# ---------------------------------------------------------------------------

def extract_best_for_items(content):
    """Extract tool items from best-for pages (h3 with &mdash; or em-dash separator)."""
    # Match <h3 ...>ToolName &mdash; Description</h3> or <h3 ...>ToolName — Description</h3>
    pattern = r'<h3[^>]*>(.*?)(?:&mdash;|\u2014)(.*?)</h3>'
    matches = re.findall(pattern, content)
    items = []
    for i, (raw_name, raw_desc) in enumerate(matches, 1):
        name = strip_html_tags(raw_name).strip()
        desc = strip_html_tags(raw_desc).strip()
        if not name:
            continue
        item = {
            "@type": "ListItem",
            "position": i,
            "name": name,
            "description": desc
        }
        slug = tool_name_to_review_slug(name)
        if slug:
            item["url"] = f"{BASE_URL}/tools/{slug}"
        items.append(item)
    return items


def extract_alternatives_items(content):
    """Extract tool items from alternatives pages.

    These use either <h2> or <h3> tags with numbered prefixes like:
        '1. ZoomInfo &mdash; Best for Enterprise Data Coverage'
        '1. Close: Best for Inside Sales Teams'
    """
    # Match numbered h2/h3 headings with &mdash; or em-dash separator
    pattern_mdash = r'<h[23][^>]*>\s*\d+\.\s*(.*?)(?:&mdash;|\u2014)(.*?)</h[23]>'
    matches = re.findall(pattern_mdash, content)

    # If no matches with mdash, try colon separator pattern (e.g., hubspot-crm.html)
    if not matches:
        pattern_colon = r'<h[23][^>]*>\s*\d+\.\s*(.*?):\s*(Best\s.*?)</h[23]>'
        matches = re.findall(pattern_colon, content)

    items = []
    for i, (raw_name, raw_desc) in enumerate(matches, 1):
        name = strip_html_tags(raw_name).strip()
        desc = strip_html_tags(raw_desc).strip()
        if not name:
            continue
        item = {
            "@type": "ListItem",
            "position": i,
            "name": name,
            "description": desc
        }
        slug = tool_name_to_review_slug(name)
        if slug:
            item["url"] = f"{BASE_URL}/tools/{slug}"
        items.append(item)
    return items


def extract_category_items(content):
    """Extract tool items from category hub pages using tool-card structure."""
    # Category pages use <h2 class="tool-card__name">ToolName</h2>
    # and <div class="tool-card__best-for">Best for X</div>
    card_pattern = r'<div\s+class="tool-card__best-for">(.*?)</div>\s*<h2\s+class="tool-card__name">(.*?)</h2>'
    matches = re.findall(card_pattern, content, re.DOTALL)

    items = []
    for i, (raw_bestfor, raw_name) in enumerate(matches, 1):
        name = strip_html_tags(raw_name).strip()
        desc = strip_html_tags(raw_bestfor).strip()
        if not name:
            continue
        item = {
            "@type": "ListItem",
            "position": i,
            "name": name,
            "description": desc
        }
        slug = tool_name_to_review_slug(name)
        if slug:
            item["url"] = f"{BASE_URL}/tools/{slug}"
        items.append(item)
    return items


def build_itemlist(items):
    """Build an ItemList schema from a list of ListItem dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": items
    }


# ---------------------------------------------------------------------------
# D5: FAQPage schema (only clay.html and instantly.html)
# ---------------------------------------------------------------------------

def extract_faq_items(content):
    """Extract FAQ Q&A pairs from pages with a 'Frequently Asked Questions' h2.

    After the FAQ h2, each <h3> is a question and the next <p> is its answer.
    """
    # Find the FAQ section start
    faq_match = re.search(r'<h2[^>]*>[^<]*Frequently Asked Questions[^<]*</h2>', content)
    if not faq_match:
        return []

    faq_section = content[faq_match.end():]

    # Extract all h3+p pairs until we hit another h2 or end of article
    # Stop at next <h2 or </article
    stop_match = re.search(r'<h2[^>]*>|</article', faq_section)
    if stop_match:
        faq_section = faq_section[:stop_match.start()]

    # Find h3 questions and their following p answers
    # Pattern: <h3 ...>Question</h3> ... <p ...>Answer</p>
    qa_pattern = r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>'
    matches = re.findall(qa_pattern, faq_section, re.DOTALL)

    faq_items = []
    for raw_q, raw_a in matches:
        question = strip_html_tags(raw_q).strip()
        answer = strip_html_tags(raw_a).strip()
        if question and answer:
            faq_items.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })
    return faq_items


def build_faqpage(faq_items):
    """Build a FAQPage schema."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_items
    }


# ---------------------------------------------------------------------------
# D3: Publisher.logo enrichment
# ---------------------------------------------------------------------------

def add_publisher_logo(content):
    """Add logo to publisher objects that are missing it.

    Matches minified, single-line spaced, and multi-line publisher formats.
    Returns (modified_content, was_changed).
    """
    changed = False

    # Pattern 1: minified - no spaces
    old_min = '"publisher":{"@type":"Organization","name":"SalesAIGuide"}'
    new_min = '"publisher":{"@type":"Organization","name":"SalesAIGuide","logo":{"@type":"ImageObject","url":"https://salesaiguide.com/favicon.svg"}}'

    if old_min in content:
        content = content.replace(old_min, new_min)
        changed = True

    # Pattern 2: single-line spaced (without url field)
    old_spaced = '"publisher": {"@type": "Organization", "name": "SalesAIGuide"}'
    new_spaced = '"publisher": {"@type": "Organization", "name": "SalesAIGuide", "logo": {"@type": "ImageObject", "url": "https://salesaiguide.com/favicon.svg"}}'

    if old_spaced in content:
        content = content.replace(old_spaced, new_spaced)
        changed = True

    # Pattern 3: multi-line publisher blocks with "url" field
    # These look like (with varying indentation):
    #   "publisher": {
    #     "@type": "Organization",
    #     "name": "SalesAIGuide",
    #     "url": "https://salesaiguide.com"
    #   }
    # Strategy: find the "url" line inside publisher and add comma + logo property after it.
    # We use a simple string search: find '"url": "https://salesaiguide.com"' followed by
    # newline + whitespace + '}' (closing the publisher object).
    # Replace by adding a comma and logo line before that closing brace.

    # This exact string appears in every multi-line publisher block
    old_url_ending = '"url": "https://salesaiguide.com"\n'

    if old_url_ending in content and '"logo"' not in content:
        # Find each occurrence and check it's inside a publisher block
        # by looking for the closing } after the url line
        pos = 0
        while True:
            idx = content.find(old_url_ending, pos)
            if idx == -1:
                break
            # Find the closing } after this url line
            after_url = idx + len(old_url_ending)
            # Skip whitespace to find the closing brace
            rest = content[after_url:]
            brace_match = re.match(r'(\s*)\}', rest)
            if brace_match:
                indent = brace_match.group(1)
                # Check this is inside a publisher block (look back for "publisher")
                lookback = content[max(0, idx - 200):idx]
                if '"publisher"' in lookback and '"logo"' not in lookback:
                    # Replace: add comma after url value, then logo line, then closing brace
                    old_fragment = old_url_ending + indent + '}'
                    # Determine the property indent (one level deeper than closing brace indent)
                    prop_indent = indent + '  '
                    new_fragment = (
                        '"url": "https://salesaiguide.com",\n'
                        + prop_indent + '"logo": {"@type": "ImageObject", "url": "https://salesaiguide.com/favicon.svg"}\n'
                        + indent + '}'
                    )
                    content = content[:idx] + new_fragment + content[idx + len(old_fragment):]
                    changed = True
                    # Adjust pos for next search
                    pos = idx + len(new_fragment)
                else:
                    pos = after_url
            else:
                pos = after_url

    return content, changed


# ---------------------------------------------------------------------------
# D4: Article.image enrichment
# ---------------------------------------------------------------------------

def add_article_image(content):
    """Add image property to Article/Review schemas that lack it.

    Inserts after the @type line. Uses string replacement to avoid JSON parsing issues.
    Returns (modified_content, was_changed).
    """
    changed = False

    # Find JSON-LD blocks
    ld_blocks = list(re.finditer(
        r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
        content, re.DOTALL
    ))

    for block in reversed(ld_blocks):  # reverse to preserve offsets
        block_text = block.group(1)

        # Check if this block is Article or Review type
        is_article = re.search(r'"@type"\s*:\s*"(?:Article|Review)"', block_text)
        if not is_article:
            continue

        # Check if image already exists in this block
        if '"image"' in block_text:
            continue

        # Insert "image" after the @type line
        # Match the @type line and add image after it
        new_block = re.sub(
            r'("@type"\s*:\s*"(?:Article|Review)")',
            r'\1,\n    "image": "https://salesaiguide.com/images/og-default.svg"',
            block_text
        )

        if new_block != block_text:
            content = content[:block.start(1)] + new_block + content[block.end(1):]
            changed = True

    return content, changed


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

FAQ_PAGES = {'clay.html', 'instantly.html'}


def process_page(filepath):
    """Process a single HTML page for all v2 schema enrichments.

    Returns (was_changed, list_of_descriptions).
    """
    rel = os.path.relpath(filepath, SITE_DIR)
    basename = os.path.basename(filepath)

    with open(filepath, 'r') as f:
        content = f.read()

    changes = []
    original = content

    # --- D1: ItemList schema ---
    if '"ItemList"' not in content:
        items = []

        if rel.startswith('best/') and basename != 'index.html':
            items = extract_best_for_items(content)

        elif rel.startswith('alternatives/') and basename != 'index.html':
            items = extract_alternatives_items(content)

        elif rel.startswith('categories/') and basename != 'index.html':
            items = extract_category_items(content)

        if items:
            schema = build_itemlist(items)
            content = inject_before_head_close(content, schema)
            changes.append(f"ItemList ({len(items)} items)")

    # --- D2: Organization schema (homepage only) ---
    if rel == 'index.html' and '"Organization"' not in content:
        org_schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "SalesAIGuide",
            "url": "https://salesaiguide.com",
            "logo": "https://salesaiguide.com/favicon.svg"
        }
        content = inject_before_head_close(content, org_schema)
        changes.append("Organization")

    # --- D3: Publisher.logo ---
    if '"publisher"' in content and '"SalesAIGuide"' in content:
        # Only process if publisher exists without logo
        content, logo_changed = add_publisher_logo(content)
        if logo_changed:
            changes.append("Publisher.logo")

    # --- D4: Article.image ---
    content, image_changed = add_article_image(content)
    if image_changed:
        changes.append("Article.image")

    # --- D5: FAQPage schema (only clay.html and instantly.html in alternatives/) ---
    if rel.startswith('alternatives/') and basename in FAQ_PAGES:
        if '"FAQPage"' not in content:
            faq_items = extract_faq_items(content)
            if faq_items:
                faq_schema = build_faqpage(faq_items)
                content = inject_before_head_close(content, faq_schema)
                changes.append(f"FAQPage ({len(faq_items)} Q&As)")

    # Write if changed
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True, changes

    return False, changes


def main():
    print("Schema Enrichment v2")
    print("====================")

    count = 0
    for root, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs')]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(root, f)
            rel = os.path.relpath(filepath, SITE_DIR)
            changed, descriptions = process_page(filepath)
            if changed:
                count += 1
                desc_str = ", ".join(descriptions)
                print(f"  \u2713 {rel} \u2014 added {desc_str}")

    print(f"\nDone: {count} pages updated with schema enrichment")


if __name__ == '__main__':
    main()

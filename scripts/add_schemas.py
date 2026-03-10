#!/usr/bin/env python3
"""Add BreadcrumbList and FAQPage schema.org markup to all pages."""
import os, re, json, sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://salesaiguide.com"


def classify_page(filepath):
    """Classify a page by type and extract metadata."""
    rel = os.path.relpath(filepath, SITE_DIR)
    basename = os.path.basename(filepath).replace('.html', '')

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract title
    m = re.search(r'<title>([^<]+)</title>', content)
    title = m.group(1).strip() if m else basename

    # Extract canonical
    m = re.search(r'rel="canonical"\s+href="([^"]+)"', content)
    canonical = m.group(1) if m else f"{BASE_URL}/{rel}"

    if rel.startswith('tools/') and rel.endswith('-review.html'):
        tool_name = re.search(r'^(.*?)\s+Review', title)
        return 'review', {
            'title': title,
            'canonical': canonical,
            'tool_name': tool_name.group(1) if tool_name else basename.replace('-review', '').title(),
        }
    elif rel.startswith('compare/') and '-vs-' in rel:
        parts = basename.split('-vs-')
        return 'comparison', {
            'title': title,
            'canonical': canonical,
            'tool_a': parts[0].replace('-', ' ').title().replace(' Io', '.io').replace(' Ai', '.AI'),
            'tool_b': parts[1].replace('-', ' ').title().replace(' Io', '.io').replace(' Ai', '.AI'),
        }
    elif rel.startswith('categories/') and rel != 'categories/index.html':
        cat_name = re.search(r'Best\s+(.*?)\s+Tools', title)
        return 'category', {
            'title': title,
            'canonical': canonical,
            'category_name': cat_name.group(1) if cat_name else basename.replace('-', ' ').title(),
        }
    elif rel == 'index.html':
        return 'homepage', {'title': title, 'canonical': canonical}
    elif rel.startswith('tools/index') or rel.startswith('compare/index') or rel.startswith('categories/index'):
        return 'directory', {'title': title, 'canonical': canonical}
    else:
        return 'editorial', {'title': title, 'canonical': canonical}


def make_breadcrumb(page_type, meta):
    """Generate BreadcrumbList schema."""
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"}]

    if page_type == 'review':
        items.append({"@type": "ListItem", "position": 2, "name": "Reviews", "item": BASE_URL + "/tools/"})
        items.append({"@type": "ListItem", "position": 3, "name": meta['tool_name']})
    elif page_type == 'comparison':
        items.append({"@type": "ListItem", "position": 2, "name": "Comparisons", "item": BASE_URL + "/compare/"})
        items.append({"@type": "ListItem", "position": 3, "name": f"{meta['tool_a']} vs {meta['tool_b']}"})
    elif page_type == 'category':
        items.append({"@type": "ListItem", "position": 2, "name": "Categories", "item": BASE_URL + "/categories/"})
        items.append({"@type": "ListItem", "position": 3, "name": meta['category_name']})
    elif page_type == 'directory':
        short = meta['title'].split('|')[0].strip() if '|' in meta['title'] else meta['title']
        items.append({"@type": "ListItem", "position": 2, "name": short})
    elif page_type == 'editorial':
        short = meta['title'].split('|')[0].strip() if '|' in meta['title'] else meta['title']
        items.append({"@type": "ListItem", "position": 2, "name": short})
    # homepage: just Home

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }


def make_faq(meta):
    """Generate FAQPage schema for comparison pages."""
    a, b = meta['tool_a'], meta['tool_b']
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"What is the main difference between {a} and {b}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"{a} and {b} serve similar markets but differ in their core approach, feature depth, and pricing model. Read our detailed comparison to see how they stack up across key evaluation criteria."
                }
            },
            {
                "@type": "Question",
                "name": f"Which is better for small sales teams, {a} or {b}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"The best choice between {a} and {b} for small teams depends on budget, team size, and which features matter most. Our comparison breaks down pricing tiers and ease of use for teams under 20 reps."
                }
            },
            {
                "@type": "Question",
                "name": f"How do {a} and {b} compare on pricing?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Both {a} and {b} offer tiered pricing plans. We compare their starter, professional, and enterprise tiers side by side with transparent cost breakdowns in our full analysis above."
                }
            }
        ]
    }


def inject_schemas(filepath):
    """Add schema blocks to a page."""
    with open(filepath, 'r') as f:
        content = f.read()

    if '"BreadcrumbList"' in content:
        return False, "already has BreadcrumbList"

    page_type, meta = classify_page(filepath)

    schemas = []
    breadcrumb = make_breadcrumb(page_type, meta)
    schemas.append(breadcrumb)

    if page_type == 'comparison':
        faq = make_faq(meta)
        schemas.append(faq)

    # Build injection HTML
    injection = ""
    for schema in schemas:
        injection += "    <script type=\"application/ld+json\">\n"
        injection += "    " + json.dumps(schema, indent=2).replace('\n', '\n    ')
        injection += "\n    </script>\n"

    # Insert before </head>
    content = content.replace('</head>', injection + '    </head>')

    with open(filepath, 'w') as f:
        f.write(content)

    schema_types = [s['@type'] for s in schemas]
    return True, f"added {', '.join(schema_types)}"


def main():
    count = 0
    for root, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs')]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(root, f)
            rel = os.path.relpath(filepath, SITE_DIR)
            changed, reason = inject_schemas(filepath)
            if changed:
                count += 1
                print(f"  ✓ {rel} — {reason}")
            else:
                print(f"  ⊘ {rel} — {reason}")

    print(f"\nDone: {count} pages updated with schema enrichment")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Add og:image and twitter:image meta tags to all HTML pages."""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OG_IMAGE_URL = "https://salesaiguide.com/images/og-default.svg"

# Meta tags to inject (after og:site_name line)
OG_IMAGE_TAGS = f"""    <meta property="og:image" content="{OG_IMAGE_URL}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:image" content="{OG_IMAGE_URL}">"""


def find_html_files(site_dir):
    """Find all HTML files in the site."""
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden dirs, scripts, docs, node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    return sorted(html_files)


def add_og_image(filepath):
    """Add og:image meta tags to a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has og:image
    if 'og:image' in content:
        return False, "already has og:image"

    # Strategy 1: Insert after og:site_name
    pattern = r'(<meta\s+property="og:site_name"\s+content="[^"]*"\s*/?>)'
    match = re.search(pattern, content)
    if match:
        insert_point = match.end()
        new_content = content[:insert_point] + '\n' + OG_IMAGE_TAGS + content[insert_point:]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "inserted after og:site_name"

    # Strategy 2: Insert after twitter:card
    pattern2 = r'(<meta\s+name="twitter:card"\s+content="[^"]*"\s*/?>)'
    match2 = re.search(pattern2, content)
    if match2:
        insert_point = match2.start()
        # Insert og:image tags before twitter:card
        og_only = f'    <meta property="og:image" content="{OG_IMAGE_URL}">\n    <meta property="og:image:width" content="1200">\n    <meta property="og:image:height" content="630">\n'
        new_content = content[:insert_point] + og_only + content[insert_point:]
        # Now add twitter:image after twitter:description
        tw_pattern = r'(<meta\s+name="twitter:description"\s+content="[^"]*"\s*/?>)'
        tw_match = re.search(tw_pattern, new_content)
        if tw_match:
            tw_insert = tw_match.end()
            new_content = new_content[:tw_insert] + f'\n    <meta name="twitter:image" content="{OG_IMAGE_URL}">' + new_content[tw_insert:]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "inserted before twitter:card"

    # Strategy 3: Insert before </head>
    head_match = re.search(r'</head>', content)
    if head_match:
        insert_point = head_match.start()
        new_content = content[:insert_point] + OG_IMAGE_TAGS + '\n    ' + content[insert_point:]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "inserted before </head>"

    return False, "no suitable insertion point"


def main():
    html_files = find_html_files(SITE_DIR)
    print(f"Found {len(html_files)} HTML files")

    updated = 0
    skipped = 0
    failed = 0

    for filepath in html_files:
        rel = os.path.relpath(filepath, SITE_DIR)
        success, reason = add_og_image(filepath)
        if success:
            updated += 1
            print(f"  ✓ {rel} — {reason}")
        elif "already" in reason:
            skipped += 1
            print(f"  ⊘ {rel} — {reason}")
        else:
            failed += 1
            print(f"  ✗ {rel} — {reason}")

    print(f"\nDone: {updated} updated, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

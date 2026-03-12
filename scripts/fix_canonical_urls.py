#!/usr/bin/env python3
"""Remove .html from canonical URLs in all HTML files."""
import re
import os
import glob

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_files = glob.glob(os.path.join(base_dir, '**/*.html'), recursive=True)

canonical_pattern = re.compile(
    r'(<link\s+rel="canonical"\s+href="https://salesaiguide\.com/)([^"]+)(">)'
)

changed = 0
skipped = 0

for filepath in sorted(html_files):
    rel_path = os.path.relpath(filepath, base_dir)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = canonical_pattern.search(content)
    if not match:
        print(f"  NO CANONICAL: {rel_path}")
        continue

    old_url_path = match.group(2)

    # Determine the correct clean URL path
    if rel_path == 'index.html':
        # Root index -> https://salesaiguide.com/
        new_url_path = ''
    elif rel_path.endswith('/index.html'):
        # Subdirectory index -> directory URL (e.g., tools/ )
        new_url_path = os.path.dirname(rel_path) + '/'
    elif old_url_path.endswith('.html'):
        # Regular page -> remove .html
        new_url_path = old_url_path[:-5]  # strip .html
    else:
        # Already clean
        skipped += 1
        continue

    new_tag = f'{match.group(1)}{new_url_path}{match.group(3)}'
    old_tag = match.group(0)

    if old_tag == new_tag:
        skipped += 1
        continue

    new_content = content.replace(old_tag, new_tag, 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    changed += 1
    print(f"  FIXED: {rel_path}: {old_url_path} -> {new_url_path or '/'}")

print(f"\nDone. Changed: {changed}, Already clean: {skipped}")

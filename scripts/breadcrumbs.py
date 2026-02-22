#!/usr/bin/env python3
"""Update breadcrumb separators from / to › across all HTML files."""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def update_breadcrumbs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Only replace / separators inside breadcrumbs divs
    # Pattern: </a> / <a  or  </a> / text
    content = content.replace('</a> / <a', '</a> <span style="color:var(--accent);margin:0 0.25rem">›</span> <a')
    content = content.replace('</a> / ', '</a> <span style="color:var(--accent);margin:0 0.25rem">›</span> ')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip scripts and node_modules
        dirs[:] = [d for d in dirs if d not in ('scripts', 'node_modules', '.git')]
        for fname in files:
            if fname.endswith('.html'):
                filepath = os.path.join(root, fname)
                if update_breadcrumbs(filepath):
                    count += 1
                    print(f'  Updated: {os.path.relpath(filepath, REPO_ROOT)}')
    print(f'\nDone. Updated {count} files.')

if __name__ == '__main__':
    main()

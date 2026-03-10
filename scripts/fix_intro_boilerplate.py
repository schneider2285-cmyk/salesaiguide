#!/usr/bin/env python3
"""Fix intro_similarity by removing boilerplate text from content word counting.

Changes:
1. Externalize inline theme <script> to external file (removes ~14 content words)
2. Add 'nav-menu' class to mobile-nav element (marks as boilerplate, removes ~4 words)
3. Add 'editorial-trust' class to editorial/trust bar elements (marks as boilerplate)
"""

import os
import re
import glob


def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = 0

    # 1. Externalize inline theme script
    # Handles both compact: <script>(function(){var t=localStorage...})();</script>
    # and spaced: <script>\n(function(){\n  var t = localStorage...})();\n</script>
    theme_script_pattern = re.compile(
        r"<script>\s*\(function\(\)\s*\{\s*var\s+t\s*=\s*localStorage.*?\)\(\)\s*;?\s*</script>",
        re.DOTALL
    )
    match = theme_script_pattern.search(content)
    if match:
        # Determine relative path to js/theme-init.js
        if "/tools/" in filepath or "/compare/" in filepath or "/categories/" in filepath:
            js_path = "../js/theme-init.js"
        else:
            js_path = "js/theme-init.js"

        # Only replace if not already externalized
        if "theme-init.js" not in content:
            content = content[:match.start()] + f'<script src="{js_path}"></script>' + content[match.end():]
            changes += 1

    # 2. Add 'nav-menu' to mobile-nav (if not already there)
    if 'class="mobile-nav"' in content and 'class="mobile-nav nav-menu"' not in content:
        content = content.replace('class="mobile-nav"', 'class="mobile-nav nav-menu"', 1)
        changes += 1

    # 3. Add 'editorial-trust' to trust bar elements
    # Comparison pages: <div class="comp-header__trust">
    if 'class="comp-header__trust"' in content and 'editorial-trust' not in content.split('comp-header__trust')[0]:
        content = content.replace(
            'class="comp-header__trust"',
            'class="comp-header__trust editorial-trust"',
            1
        )
        changes += 1

    # Review pages: editorial-bar trust section
    if 'class="editorial-bar"' in content and 'editorial-trust' not in content.split('editorial-bar')[0]:
        content = content.replace(
            'class="editorial-bar"',
            'class="editorial-bar editorial-trust"',
            1
        )
        changes += 1

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Find all HTML files
    patterns = [
        os.path.join(site_dir, "tools", "*.html"),
        os.path.join(site_dir, "compare", "*.html"),
        os.path.join(site_dir, "categories", "*.html"),
        os.path.join(site_dir, "*.html"),
    ]

    all_files = []
    for p in patterns:
        all_files.extend(sorted(glob.glob(p)))

    total = 0
    files_changed = 0

    for f in all_files:
        n = fix_file(f)
        if n > 0:
            rel = os.path.relpath(f, site_dir)
            print(f"  Fixed {rel}: {n} changes")
            files_changed += 1
            total += n

    print(f"\nTotal: {total} changes across {files_changed} files")


if __name__ == "__main__":
    main()

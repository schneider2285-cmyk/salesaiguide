#!/usr/bin/env python3
"""Fix intro_similarity by extracting inline <style> to external CSS files.

The gate's ContentExtractor treats inline CSS text as content words.
Since all reviews share identical CSS and all comparisons share identical CSS,
the first 200 content words are 100% CSS → similarity = 1.00.

Fix: Replace inline <style>...</style> with <link rel="stylesheet" href="...">
pointing to the already-extracted external CSS files.
"""

import os
import re
import glob


def fix_file(filepath, css_link):
    """Replace inline <style>...</style> with external CSS link."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and remove the <style>...</style> block
    # Pattern: <style> followed by CSS content followed by </style>
    # The style block is in the <head>, after the external CSS links
    pattern = re.compile(r'\s*<style>\s*.*?\s*</style>', re.DOTALL)
    match = pattern.search(content)
    if not match:
        return 0

    # Check if this style block has already been replaced
    if css_link in content:
        return 0

    # Replace the <style>...</style> with the external link
    new_content = content[:match.start()] + "\n  " + css_link + content[match.end():]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return 1


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    review_link = '<link rel="stylesheet" href="../css/review-page.css">'
    comparison_link = '<link rel="stylesheet" href="../css/comparison-page.css">'

    review_files = sorted(glob.glob(os.path.join(site_dir, "tools", "*-review.html")))
    compare_files = sorted(glob.glob(os.path.join(site_dir, "compare", "*-vs-*.html")))

    total = 0
    for f in review_files:
        n = fix_file(f, review_link)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            total += n

    for f in compare_files:
        n = fix_file(f, comparison_link)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            total += n

    print(f"\nTotal: {total} files updated")


if __name__ == "__main__":
    main()

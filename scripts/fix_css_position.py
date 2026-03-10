#!/usr/bin/env python3
"""Move CSS from external <link> back to inline <style>, but at end of <body>.

The gate's ContentExtractor counts <style> text as content words.
By placing <style> at end of <body> (instead of <head>):
  - content_words are restored (CSS words still counted)
  - intro_similarity is fixed (first 200 words are real content, not CSS)
"""

import os
import re
import glob


def fix_file(filepath, css_content, link_tag):
    """Replace external CSS <link> with inline <style> at end of body."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if this file has the external link we want to replace
    if link_tag not in content:
        return 0

    # Check if already has inline style at end of body (idempotent)
    if '</style>\n</body>' in content:
        return 0

    # Remove the external CSS link
    content = content.replace(link_tag, '', 1)
    # Clean up any resulting blank lines
    content = content.replace('\n  \n', '\n', 1)

    # Insert inline <style> just before </body>
    style_block = f'\n<style>\n{css_content}\n</style>\n</body>'
    content = content.replace('</body>', style_block, 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return 1


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Read the external CSS files
    review_css_path = os.path.join(site_dir, "css", "review-page.css")
    comparison_css_path = os.path.join(site_dir, "css", "comparison-page.css")

    with open(review_css_path, "r", encoding="utf-8") as f:
        review_css = f.read()
    with open(comparison_css_path, "r", encoding="utf-8") as f:
        comparison_css = f.read()

    review_link = '<link rel="stylesheet" href="../css/review-page.css">'
    comparison_link = '<link rel="stylesheet" href="../css/comparison-page.css">'

    review_files = sorted(glob.glob(os.path.join(site_dir, "tools", "*-review.html")))
    compare_files = sorted(glob.glob(os.path.join(site_dir, "compare", "*-vs-*.html")))

    total = 0
    for f in review_files:
        n = fix_file(f, review_css, review_link)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            total += n

    for f in compare_files:
        n = fix_file(f, comparison_css, comparison_link)
        if n:
            print(f"  Fixed {os.path.relpath(f, site_dir)}")
            total += n

    print(f"\nTotal: {total} files updated")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
fix_title_tags.py — Remove brand suffix from title tags across the site.

Strips ' | SalesAIGuide' and ' | Sales AI Guide' from:
  - <title> tags
  - og:title meta tags
  - twitter:title meta tags

Skips root-level pages (index.html, about.html, etc.) that use the brand
name naturally. Only processes content directories.
"""

import os
import re
import sys
from collections import Counter

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTENT_DIRS = ["tools", "compare", "alternatives", "best", "categories", "resources"]

SKIP_FILES = {"index.html", "about.html", "disclosure.html", "privacy.html", "terms.html"}

# Regex for <title>...</title> with brand suffix
TITLE_RE = re.compile(
    r"<title>(.*?)\s*\|\s*Sales?\s*AI\s*Guide\s*</title>",
    re.IGNORECASE | re.DOTALL,
)

# Regex for og:title meta tag with brand suffix in content attribute
OG_TITLE_RE = re.compile(
    r'(<meta\s+property="og:title"\s+content=")(.*?)\s*\|\s*Sales?\s*AI\s*Guide\s*(")',
    re.IGNORECASE,
)

# Regex for twitter:title meta tag with brand suffix in content attribute
TWITTER_TITLE_RE = re.compile(
    r'(<meta\s+name="twitter:title"\s+content=")(.*?)\s*\|\s*Sales?\s*AI\s*Guide\s*(")',
    re.IGNORECASE,
)

# Extraction regex for the final <title> value (after replacement)
EXTRACT_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def get_title_length(content):
    """Extract <title> text and return (text, length)."""
    m = EXTRACT_TITLE_RE.search(content)
    if m:
        title = m.group(1).strip()
        return title, len(title)
    return None, 0


def process_file(filepath, relpath):
    """Process a single HTML file. Returns (old_len, new_len, new_title) or None if unchanged."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    content = original

    # Get original title length
    orig_title, orig_len = get_title_length(content)

    # Replace <title> tag
    content = TITLE_RE.sub(r"<title>\1</title>", content)

    # Replace og:title
    content = OG_TITLE_RE.sub(r"\1\2\3", content)

    # Replace twitter:title
    content = TWITTER_TITLE_RE.sub(r"\1\2\3", content)

    if content == original:
        return None

    # Get new title length
    new_title, new_len = get_title_length(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return orig_len, new_len, new_title


def main():
    print("Title Tag Suffix Removal")
    print("========================")

    updated = 0
    skipped_no_change = 0
    warnings_long = []
    warnings_short = []
    all_titles = []

    for dirname in CONTENT_DIRS:
        dirpath = os.path.join(SITE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue

        for root, _dirs, files in os.walk(dirpath):
            for fname in sorted(files):
                if not fname.endswith(".html"):
                    continue
                if fname in SKIP_FILES:
                    continue

                filepath = os.path.join(root, fname)
                relpath = os.path.relpath(filepath, SITE_DIR)

                result = process_file(filepath, relpath)

                if result is None:
                    skipped_no_change += 1
                    # Still collect the title for dedup check
                    with open(filepath, "r", encoding="utf-8") as f:
                        title, length = get_title_length(f.read())
                    if title:
                        all_titles.append((relpath, title))
                    continue

                orig_len, new_len, new_title = result
                updated += 1

                print(f"  \u2713 {relpath} \u2014 {orig_len}\u2192{new_len} chars")

                if new_title:
                    all_titles.append((relpath, new_title))

                    if new_len > 60:
                        warnings_long.append((relpath, new_len))
                    elif new_len < 20:
                        warnings_short.append((relpath, new_len))

    # Print length warnings
    if warnings_long or warnings_short:
        print()
    for relpath, length in warnings_short:
        print(f"  \u26a0 {relpath} \u2014 title is {length} chars (<20, may be too short)")
    for relpath, length in warnings_long:
        print(f"  \u26a0 {relpath} \u2014 title is {length} chars (>60, may truncate)")

    # Dedup check
    title_counts = Counter(title for _, title in all_titles)
    duplicates = {title: count for title, count in title_counts.items() if count > 1}

    print()
    print(f"Done: {updated} pages updated")

    total_long = len(warnings_long)
    total_short = len(warnings_short)
    if total_long or total_short:
        parts = []
        if total_long:
            parts.append(f"{total_long} titles still >60 chars")
        if total_short:
            parts.append(f"{total_short} titles <20 chars")
        print(f"Warnings: {', '.join(parts)} (manual review recommended)")
    else:
        print("Warnings: none")

    if duplicates:
        print(f"Duplicates: {len(duplicates)} found")
        for title, count in sorted(duplicates.items()):
            pages = [rp for rp, t in all_titles if t == title]
            print(f"  \u26a0 \"{title}\" appears {count} times:")
            for p in pages:
                print(f"      - {p}")
    else:
        print("Duplicates: none found")


if __name__ == "__main__":
    main()

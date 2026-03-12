#!/usr/bin/env python3
"""
fix_footer_categories.py

Adds 4 missing category links to the footer of ALL HTML pages in the
salesaiguide static site.

Missing categories added:
  - Sales Content
  - Dialers & Calling
  - Meeting Schedulers
  - Sales Analytics

Usage:
    python scripts/fix_footer_categories.py
    python scripts/fix_footer_categories.py --dry-run
"""

import os
import sys
import argparse

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {"scripts", "docs", "node_modules", ".git", ".claude"}

# Exact block present in all 142 pages (6 category links)
OLD_BLOCK = """\
        <h4 class="footer__heading">Categories</h4>
        <div class="footer__links">
          <a href="/categories/cold-outreach.html" class="footer__link">Cold Outreach</a>
          <a href="/categories/lead-prospecting.html" class="footer__link">Lead Prospecting</a>
          <a href="/categories/data-enrichment.html" class="footer__link">Data Enrichment</a>
          <a href="/categories/conversation-intelligence.html" class="footer__link">Conversation Intel</a>
          <a href="/categories/sales-engagement.html" class="footer__link">Sales Engagement</a>
          <a href="/categories/crm-pipeline.html" class="footer__link">CRM &amp; Pipeline</a>
        </div>"""

# Replacement block with all 10 category links
NEW_BLOCK = """\
        <h4 class="footer__heading">Categories</h4>
        <div class="footer__links">
          <a href="/categories/cold-outreach.html" class="footer__link">Cold Outreach</a>
          <a href="/categories/lead-prospecting.html" class="footer__link">Lead Prospecting</a>
          <a href="/categories/data-enrichment.html" class="footer__link">Data Enrichment</a>
          <a href="/categories/conversation-intelligence.html" class="footer__link">Conversation Intel</a>
          <a href="/categories/sales-engagement.html" class="footer__link">Sales Engagement</a>
          <a href="/categories/crm-pipeline.html" class="footer__link">CRM &amp; Pipeline</a>
          <a href="/categories/sales-content.html" class="footer__link">Sales Content</a>
          <a href="/categories/dialers-calling.html" class="footer__link">Dialers &amp; Calling</a>
          <a href="/categories/meeting-schedulers.html" class="footer__link">Meeting Schedulers</a>
          <a href="/categories/sales-analytics.html" class="footer__link">Sales Analytics</a>
        </div>"""

# Detect pages that already have the new links (idempotency check)
ALREADY_UPDATED_MARKER = '/categories/sales-content.html'


def collect_html_files(site_dir):
    """Walk site_dir and return all .html file paths, excluding certain dirs."""
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        # Prune excluded directories in-place so os.walk skips them
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            if fname.endswith(".html"):
                html_files.append(os.path.join(root, fname))
    return sorted(html_files)


def process_file(filepath, dry_run=False):
    """
    Process a single HTML file.

    Returns:
        "updated"  - old block found and replaced
        "skipped"  - already contains the new links
        "no_match" - old block not found (possible template variation)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Already updated — skip
    if ALREADY_UPDATED_MARKER in content and OLD_BLOCK not in content:
        return "skipped"

    # Old block not found at all
    if OLD_BLOCK not in content:
        return "no_match"

    # Replace
    new_content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return "updated"


def main():
    parser = argparse.ArgumentParser(
        description="Add 4 missing category links to footer on all HTML pages."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN] No files will be modified.\n")

    html_files = collect_html_files(SITE_DIR)
    print(f"Found {len(html_files)} HTML files in {SITE_DIR}\n")

    updated = 0
    skipped = 0
    no_match = 0

    for filepath in html_files:
        rel = os.path.relpath(filepath, SITE_DIR)
        result = process_file(filepath, dry_run=args.dry_run)

        if result == "updated":
            prefix = "[DRY RUN] " if args.dry_run else ""
            print(f"  \u2713 {prefix}{rel}")
            updated += 1
        elif result == "skipped":
            skipped += 1
        elif result == "no_match":
            no_match += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Updated:  {updated}")
    print(f"Skipped (already had new links): {skipped}")
    if no_match > 0:
        print(f"No match (footer block not found): {no_match}")
    print(f"Total HTML files scanned: {len(html_files)}")

    if updated > 0 and updated < 130 and skipped == 0:
        print(
            f"\n** WARNING: Only {updated} pages updated (expected 130+). "
            "Some pages may use a different footer template. **"
        )

    if no_match > 0:
        print(
            f"\n** WARNING: {no_match} file(s) did not contain the expected "
            "footer block. Inspect manually. **"
        )

    if args.dry_run:
        print("\n[DRY RUN] Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()

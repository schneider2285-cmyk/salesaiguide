#!/usr/bin/env python3
"""
Update footer Categories section in all HTML files.
- Root-level files use paths without "../" prefix
- Subdirectory files use paths with "../" prefix
Adds AI SDRs and Revenue Intelligence links between Lead Prospecting and Conversation Intelligence.
"""

import os
import glob

REPO_ROOT = "/tmp/salesaiguide_repo"

# Old footer block for subdirectory pages (categories/, compare/, tools/, guides/, blog/)
OLD_SUBDIR_FOOTER = """                <div class="footer-col">
                    <h4>Categories</h4>
                    <ul>
                        <li><a href="../categories/cold-outreach.html">Cold Outreach</a></li>
                        <li><a href="../categories/lead-prospecting.html">Lead Prospecting</a></li>
                        <li><a href="../categories/conversation-intelligence.html">Conversation Intelligence</a></li>
                        <li><a href="../categories/sales-engagement.html">Sales Engagement</a></li>
                    </ul>
                </div>"""

NEW_SUBDIR_FOOTER = """                <div class="footer-col">
                    <h4>Categories</h4>
                    <ul>
                        <li><a href="../categories/cold-outreach.html">Cold Outreach</a></li>
                        <li><a href="../categories/lead-prospecting.html">Lead Prospecting</a></li>
                        <li><a href="../categories/ai-sdrs.html">AI SDRs</a></li>
                        <li><a href="../categories/revenue-intelligence.html">Revenue Intelligence</a></li>
                        <li><a href="../categories/conversation-intelligence.html">Conversation Intelligence</a></li>
                        <li><a href="../categories/sales-engagement.html">Sales Engagement</a></li>
                    </ul>
                </div>"""

# Old footer block for root-level pages
OLD_ROOT_FOOTER = """                <div class="footer-col">
                    <h4>Categories</h4>
                    <ul>
                        <li><a href="categories/cold-outreach.html">Cold Outreach</a></li>
                        <li><a href="categories/lead-prospecting.html">Lead Prospecting</a></li>
                        <li><a href="categories/conversation-intelligence.html">Conversation Intelligence</a></li>
                        <li><a href="categories/sales-engagement.html">Sales Engagement</a></li>
                    </ul>
                </div>"""

NEW_ROOT_FOOTER = """                <div class="footer-col">
                    <h4>Categories</h4>
                    <ul>
                        <li><a href="categories/cold-outreach.html">Cold Outreach</a></li>
                        <li><a href="categories/lead-prospecting.html">Lead Prospecting</a></li>
                        <li><a href="categories/ai-sdrs.html">AI SDRs</a></li>
                        <li><a href="categories/revenue-intelligence.html">Revenue Intelligence</a></li>
                        <li><a href="categories/conversation-intelligence.html">Conversation Intelligence</a></li>
                        <li><a href="categories/sales-engagement.html">Sales Engagement</a></li>
                    </ul>
                </div>"""


def is_root_level(filepath):
    """Check if the file is at the root level of the repo (not in a subdirectory)."""
    rel_path = os.path.relpath(filepath, REPO_ROOT)
    return os.sep not in rel_path


def main():
    html_files = glob.glob(os.path.join(REPO_ROOT, "**", "*.html"), recursive=True)
    html_files += glob.glob(os.path.join(REPO_ROOT, "*.html"))
    # Deduplicate
    html_files = sorted(set(html_files))

    updated_count = 0
    skipped = []

    for filepath in html_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        root = is_root_level(filepath)

        if root:
            if OLD_ROOT_FOOTER in content:
                content = content.replace(OLD_ROOT_FOOTER, NEW_ROOT_FOOTER)
            elif NEW_ROOT_FOOTER in content:
                pass  # Already updated
            else:
                skipped.append(filepath)
                continue
        else:
            if OLD_SUBDIR_FOOTER in content:
                content = content.replace(OLD_SUBDIR_FOOTER, NEW_SUBDIR_FOOTER)
            elif NEW_SUBDIR_FOOTER in content:
                pass  # Already updated
            else:
                skipped.append(filepath)
                continue

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            updated_count += 1
            rel = os.path.relpath(filepath, REPO_ROOT)
            level = "ROOT" if root else "SUBDIR"
            print(f"  UPDATED [{level}]: {rel}")

    print(f"\n=== SUMMARY ===")
    print(f"Total HTML files found: {len(html_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Files skipped (no matching footer or already updated): {len(skipped)}")
    if skipped:
        print(f"Skipped files:")
        for s in skipped:
            print(f"  - {os.path.relpath(s, REPO_ROOT)}")


if __name__ == "__main__":
    main()

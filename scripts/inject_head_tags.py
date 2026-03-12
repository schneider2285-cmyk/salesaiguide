#!/usr/bin/env python3
"""
inject_head_tags.py — Add GA4 gtag, robots meta, and sitemap link to all HTML files.

Insertions:
  1. GA4 gtag.js snippet → immediately after <meta name="viewport"> line
  2. <meta name="robots" content="index, follow"> → after <meta name="description"> (skip 404.html)
  3. <link rel="sitemap"> → before first <link rel="preconnect"> or <link rel="stylesheet">

Safety:
  - Idempotent: skips insertion if marker already present
  - Does NOT touch 404.html robots meta (it correctly has noindex)
  - Does NOT modify any content, styles, or functionality
"""

import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GA4_ID = "G-VRBZ6Z6885"

GA4_SNIPPET = f"""    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA4_ID}');
    </script>"""

# Indentation-aware versions for files using 2-space indent (tools/, compare/, etc.)
GA4_SNIPPET_2SP = f"""  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_ID}');
  </script>"""


def detect_indent(lines):
    """Detect whether file uses 2-space or 4-space indentation."""
    for line in lines[:10]:
        if line.startswith("    <meta"):
            return 4
        if line.startswith("  <meta"):
            return 2
    return 4  # default


def find_html_files(site_dir):
    """Find all .html files, excluding .git and scripts directories."""
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden dirs, scripts, node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('scripts', 'node_modules', 'css', 'js', 'images')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    return sorted(html_files)


def inject_tags(filepath):
    """Inject GA4, robots meta, and sitemap link into a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()

    lines = content.split('\n')
    indent = detect_indent(lines)
    is_404 = os.path.basename(filepath) == '404.html'

    changes = []

    # --- 1. GA4 gtag snippet (after <meta name="viewport">) ---
    if 'googletagmanager.com/gtag/js' not in content:
        snippet = GA4_SNIPPET if indent == 4 else GA4_SNIPPET_2SP
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if not inserted and re.search(r'<meta\s+name="viewport"', line, re.IGNORECASE):
                new_lines.append(snippet)
                inserted = True
        if inserted:
            lines = new_lines
            changes.append('ga4')
        else:
            changes.append('ga4:SKIP(no viewport meta)')
    else:
        changes.append('ga4:SKIP(already present)')

    # --- 2. robots meta (after <meta name="description">) ---
    if is_404:
        changes.append('robots:SKIP(404)')
    elif '<meta name="robots"' not in '\n'.join(lines):
        pad = '    ' if indent == 4 else '  '
        robots_tag = f'{pad}<meta name="robots" content="index, follow">'
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if not inserted and re.search(r'<meta\s+name="description"', line, re.IGNORECASE):
                new_lines.append(robots_tag)
                inserted = True
        if inserted:
            lines = new_lines
            changes.append('robots')
        else:
            changes.append('robots:SKIP(no description meta)')
    else:
        changes.append('robots:SKIP(already present)')

    # --- 3. sitemap link (before first <link rel="preconnect"> or <link rel="stylesheet">) ---
    if 'rel="sitemap"' not in '\n'.join(lines):
        pad = '    ' if indent == 4 else '  '
        sitemap_link = f'{pad}<link rel="sitemap" type="application/xml" href="/sitemap.xml">'
        new_lines = []
        inserted = False
        for line in lines:
            if not inserted and re.search(r'<link\s+rel="preconnect"', line, re.IGNORECASE):
                new_lines.append(sitemap_link)
                inserted = True
            new_lines.append(line)
        if inserted:
            lines = new_lines
            changes.append('sitemap-link')
        else:
            # Fallback: insert before first stylesheet
            new_lines2 = []
            for line in lines:
                if not inserted and re.search(r'<link\s+rel="stylesheet"', line, re.IGNORECASE):
                    new_lines2.append(sitemap_link)
                    inserted = True
                new_lines2.append(line)
            if inserted:
                lines = new_lines2
                changes.append('sitemap-link(before-stylesheet)')
            else:
                changes.append('sitemap-link:SKIP(no insertion point)')
    else:
        changes.append('sitemap-link:SKIP(already present)')

    # Write back
    new_content = '\n'.join(lines)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(new_content)

    return changes


def main():
    html_files = find_html_files(SITE_DIR)
    print(f"Found {len(html_files)} HTML files\n")

    ga4_count = 0
    robots_count = 0
    sitemap_count = 0
    issues = []

    for filepath in html_files:
        rel = os.path.relpath(filepath, SITE_DIR)
        changes = inject_tags(filepath)

        status_parts = []
        for c in changes:
            if c == 'ga4':
                ga4_count += 1
                status_parts.append('✅ GA4')
            elif c == 'robots':
                robots_count += 1
                status_parts.append('✅ robots')
            elif c.startswith('sitemap-link'):
                sitemap_count += 1
                status_parts.append('✅ sitemap')
            elif 'SKIP' in c:
                status_parts.append(f'⏭ {c}')
            else:
                issues.append(f'{rel}: {c}')
                status_parts.append(f'⚠ {c}')

        print(f"  {rel}: {' | '.join(status_parts)}")

    print(f"\n{'='*60}")
    print(f"  GA4 snippets inserted:    {ga4_count}")
    print(f"  robots meta inserted:     {robots_count}")
    print(f"  sitemap links inserted:   {sitemap_count}")
    print(f"  Total files processed:    {len(html_files)}")
    if issues:
        print(f"\n  ⚠ Issues:")
        for i in issues:
            print(f"    {i}")
    else:
        print(f"\n  No issues detected.")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

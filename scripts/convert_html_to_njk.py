#!/usr/bin/env python3
"""
One-time migration script: Convert HTML pages to Eleventy .njk templates.
Session 3 of the Eleventy migration.

Converts compare/*.html, categories/*.html, and index.html to .njk files
with YAML frontmatter + body content, using base.njk layout.
"""

import os
import re
import glob
import html

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_meta(content, attr_name, attr_value, target_attr="content"):
    """Extract a meta tag's content attribute value."""
    # Match meta tags with the given attribute
    pattern = rf'<meta\s+[^>]*{attr_name}="{re.escape(attr_value)}"[^>]*{target_attr}="([^"]*)"'
    m = re.search(pattern, content)
    if m:
        return m.group(1)
    # Try reversed attribute order
    pattern = rf'<meta\s+[^>]*{target_attr}="([^"]*)"[^>]*{attr_name}="{re.escape(attr_value)}"'
    m = re.search(pattern, content)
    if m:
        return m.group(1)
    return ""


def extract_title(content):
    """Extract <title> tag content."""
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_canonical(content):
    """Extract canonical URL."""
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
    return m.group(1) if m else ""


def extract_json_ld_blocks(content):
    """Extract all JSON-LD script blocks from <head>."""
    # Get head content first
    head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL)
    if not head_match:
        return ""
    head_content = head_match.group(1)

    blocks = re.findall(
        r'(<script\s+type="application/ld\+json">.*?</script>)',
        head_content,
        re.DOTALL
    )
    return "\n".join(blocks)


def has_review_css(content):
    """Check if page includes review.css."""
    return 'review.css' in content


def extract_body_content(content):
    """Extract body content between </nav> closing and newsletter section."""
    # Find end of nav
    nav_end = content.find('</nav>')
    if nav_end == -1:
        return ""
    # Move past </nav> and any immediate whitespace/newline
    start = nav_end + len('</nav>')

    # Find newsletter section start
    # Try <!-- Newsletter first
    newsletter_idx = content.find('<!-- Newsletter', start)
    if newsletter_idx == -1:
        # Try <section class="newsletter">
        newsletter_idx = content.find('<section class="newsletter">', start)
    if newsletter_idx == -1:
        # Fallback: try footer
        newsletter_idx = content.find('<footer class="footer">', start)
    if newsletter_idx == -1:
        return ""

    body = content[start:newsletter_idx]
    # Strip leading/trailing whitespace but keep internal structure
    return body.strip()


def convert_relative_paths(body, is_root=False):
    """Convert relative paths to absolute paths in body content."""
    if is_root:
        # Root pages use paths like: href="compare/index.html" → href="/compare/index.html"
        # But NOT https:// URLs or # anchors or mailto: or javascript:
        # Also convert src="css/..." → src="/css/..."
        # Pattern: any href or src that doesn't start with /, http, #, mailto, javascript, data:
        def replace_root_path(match):
            attr = match.group(1)  # href or src
            quote = match.group(2)  # quote char
            path = match.group(3)
            # Skip absolute URLs, anchors, special protocols
            if path.startswith(('/', 'http', '#', 'mailto:', 'javascript:', 'data:')):
                return match.group(0)
            return f'{attr}={quote}/{path}'

        body = re.sub(
            r'((?:href|src))=(["\'])([^"\']*)',
            replace_root_path,
            body
        )
    else:
        # Subdirectory pages use paths like: href="../compare/" → href="/compare/"
        # Replace ../ with /
        body = re.sub(r'((?:href|src))=(["\'])\.\.\/', r'\1=\2/', body)
        # Replace ./ with current directory (shouldn't be common)
        body = re.sub(r'((?:href|src))=(["\'])\.\/', r'\1=\2', body)

    return body


def escape_yaml_string(s):
    """Escape a string for YAML double-quoted format."""
    if not s:
        return '""'
    # If string contains problematic characters, use double quotes with escaping
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    return f'"{s}"'


def build_frontmatter(meta, extra_css, json_ld, permalink, is_homepage=False, footer_disclosure_text=None):
    """Build YAML frontmatter string."""
    lines = ["---"]
    lines.append("layout: base.njk")
    lines.append(f"title: {escape_yaml_string(meta['title'])}")
    lines.append(f"description: {escape_yaml_string(meta['description'])}")
    lines.append(f"ogTitle: {escape_yaml_string(meta['ogTitle'])}")
    lines.append(f"ogDescription: {escape_yaml_string(meta['ogDescription'])}")
    lines.append(f"ogUrl: {escape_yaml_string(meta['ogUrl'])}")
    lines.append(f"twitterTitle: {escape_yaml_string(meta['twitterTitle'])}")
    lines.append(f"twitterDescription: {escape_yaml_string(meta['twitterDescription'])}")
    lines.append(f"canonicalUrl: {escape_yaml_string(meta['canonicalUrl'])}")

    if extra_css:
        lines.append("extraCss:")
        for css in extra_css:
            lines.append(f'  - "{css}"')

    lines.append(f"permalink: {permalink}")

    if is_homepage:
        lines.append('footerFourthTitle: "Top Comparisons"')
        lines.append("footerFourthLinks:")
        lines.append('  - url: "/compare/clay-vs-apollo.html"')
        lines.append('    text: "Clay vs Apollo"')
        lines.append('  - url: "/compare/instantly-vs-smartlead.html"')
        lines.append('    text: "Instantly vs Smartlead"')
        lines.append('  - url: "/compare/gong-vs-chorus.html"')
        lines.append('    text: "Gong vs Chorus"')

    if footer_disclosure_text:
        lines.append(f'footerDisclosureText: "{footer_disclosure_text}"')

    if json_ld:
        lines.append("extraHead: |")
        for line in json_ld.split('\n'):
            lines.append(f"    {line}")

    lines.append("---")
    return "\n".join(lines)


def convert_file(html_path, is_root=False):
    """Convert a single HTML file to .njk."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    meta = {
        'title': extract_title(content),
        'description': extract_meta(content, 'name', 'description'),
        'ogTitle': extract_meta(content, 'property', 'og:title'),
        'ogDescription': extract_meta(content, 'property', 'og:description'),
        'ogUrl': extract_meta(content, 'property', 'og:url'),
        'twitterTitle': extract_meta(content, 'name', 'twitter:title'),
        'twitterDescription': extract_meta(content, 'name', 'twitter:description'),
        'canonicalUrl': extract_canonical(content),
    }

    # Determine extra CSS
    extra_css = []
    if has_review_css(content):
        extra_css.append("/css/review.css")

    # Extract JSON-LD
    json_ld = extract_json_ld_blocks(content)

    # Extract body content
    body = extract_body_content(content)
    body = convert_relative_paths(body, is_root=is_root)

    # Determine permalink and output path
    rel_path = os.path.relpath(html_path, REPO_ROOT)
    if is_root and rel_path == "index.html":
        permalink = "index.html"
        njk_path = os.path.join(REPO_ROOT, "index.njk")
        is_homepage = True
    else:
        permalink = rel_path
        njk_path = os.path.join(REPO_ROOT, rel_path.replace('.html', '.njk'))
        is_homepage = False

    # Determine footer disclosure text
    # Compare and category pages use "Learn more", homepage and tool reviews use "Full disclosure"
    footer_disclosure_text = None
    if not is_homepage:
        dir_name = os.path.dirname(rel_path)
        if dir_name in ('compare', 'categories'):
            footer_disclosure_text = "Learn more"

    # Build frontmatter
    frontmatter = build_frontmatter(
        meta, extra_css, json_ld, permalink,
        is_homepage=is_homepage,
        footer_disclosure_text=footer_disclosure_text
    )

    # Write .njk file
    njk_content = frontmatter + "\n" + body + "\n"
    with open(njk_path, 'w', encoding='utf-8') as f:
        f.write(njk_content)

    return njk_path


def main():
    # Collect all files to convert
    files_to_convert = []

    # Compare pages
    compare_dir = os.path.join(REPO_ROOT, 'compare')
    for html_file in sorted(glob.glob(os.path.join(compare_dir, '*.html'))):
        files_to_convert.append((html_file, False))

    # Category pages
    categories_dir = os.path.join(REPO_ROOT, 'categories')
    for html_file in sorted(glob.glob(os.path.join(categories_dir, '*.html'))):
        files_to_convert.append((html_file, False))

    # Homepage
    homepage = os.path.join(REPO_ROOT, 'index.html')
    if os.path.exists(homepage):
        files_to_convert.append((homepage, True))

    print(f"Converting {len(files_to_convert)} HTML files to .njk templates...\n")

    for html_path, is_root in files_to_convert:
        rel_path = os.path.relpath(html_path, REPO_ROOT)
        njk_path = convert_file(html_path, is_root=is_root)
        njk_rel = os.path.relpath(njk_path, REPO_ROOT)
        print(f"  {rel_path} → {njk_rel}")

    print(f"\nDone! Converted {len(files_to_convert)} files.")
    print("\nNext steps:")
    print("  1. Delete original HTML files: rm compare/*.html categories/*.html index.html")
    print("  2. Update .eleventy.js (remove compare/categories passthrough)")
    print("  3. Build: npx @11ty/eleventy")


if __name__ == "__main__":
    main()

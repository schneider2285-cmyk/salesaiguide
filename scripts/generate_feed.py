#!/usr/bin/env python3
"""Generate RSS feed and sitemap index for salesaiguide.com."""
import os, re, json, sys
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
import xml.dom.minidom

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://salesaiguide.com"
NOW = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
NOW_RFC822 = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")


def extract_page_meta(filepath):
    """Extract title, description, canonical, datePublished from HTML page."""
    with open(filepath) as f:
        content = f.read()
    meta = {}
    m = re.search(r'<title>([^<]+)</title>', content)
    meta['title'] = m.group(1).strip() if m else ''
    m = re.search(r'name="description"\s+content="([^"]+)"', content)
    meta['description'] = m.group(1).strip() if m else ''
    m = re.search(r'rel="canonical"\s+href="([^"]+)"', content)
    meta['canonical'] = m.group(1).strip() if m else ''
    m = re.search(r'"datePublished":\s*"([^"]+)"', content)
    meta['date'] = m.group(1).strip() if m else '2026-03-01'
    m = re.search(r'"dateModified":\s*"([^"]+)"', content)
    meta['modified'] = m.group(1).strip() if m else meta['date']
    return meta


def categorize_pages():
    """Scan all HTML files and categorize them."""
    categories = {'reviews': [], 'comparisons': [], 'categories': [], 'editorial': []}
    for root, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs')]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(root, f)
            rel = os.path.relpath(filepath, SITE_DIR)
            meta = extract_page_meta(filepath)
            meta['rel'] = rel
            if rel.startswith('tools/') and '-review.html' in rel:
                categories['reviews'].append(meta)
            elif rel.startswith('compare/') and '-vs-' in rel:
                categories['comparisons'].append(meta)
            elif rel.startswith('categories/'):
                categories['categories'].append(meta)
            else:
                categories['editorial'].append(meta)
    return categories


def generate_rss(reviews):
    """Generate RSS 2.0 feed from review pages."""
    # Sort by date descending, take 20 most recent
    reviews.sort(key=lambda x: x['date'], reverse=True)
    recent = reviews[:20]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    lines.append('  <channel>')
    lines.append('    <title>SalesAIGuide - AI Sales Tool Reviews</title>')
    lines.append(f'    <link>{BASE_URL}</link>')
    lines.append('    <description>Honest reviews and comparisons of the best AI sales tools for modern sales teams.</description>')
    lines.append('    <language>en-us</language>')
    lines.append(f'    <lastBuildDate>{NOW_RFC822}</lastBuildDate>')
    lines.append(f'    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>')

    for r in recent:
        lines.append('    <item>')
        lines.append(f'      <title>{r["title"]}</title>')
        lines.append(f'      <link>{r["canonical"]}</link>')
        lines.append(f'      <guid>{r["canonical"]}</guid>')
        lines.append(f'      <description>{r["description"]}</description>')
        # Convert date to RFC822
        try:
            dt = datetime.strptime(r['date'], '%Y-%m-%d')
            rfc = dt.strftime("%a, %d %b %Y 00:00:00 +0000")
        except:
            rfc = NOW_RFC822
        lines.append(f'      <pubDate>{rfc}</pubDate>')
        lines.append('    </item>')

    lines.append('  </channel>')
    lines.append('</rss>')

    output = os.path.join(SITE_DIR, 'feed.xml')
    with open(output, 'w') as f:
        f.write('\n'.join(lines))
    print(f"✓ feed.xml — {len(recent)} items")


def generate_sitemap(name, pages, priority='0.7'):
    """Generate a single sitemap XML file."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        lines.append('  <url>')
        lines.append(f'    <loc>{p["canonical"]}</loc>')
        lines.append(f'    <lastmod>{p["modified"]}</lastmod>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')

    output = os.path.join(SITE_DIR, name)
    with open(output, 'w') as f:
        f.write('\n'.join(lines))
    print(f"✓ {name} — {len(pages)} URLs")


def generate_sitemap_index(sitemap_files):
    """Generate sitemap index."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for name in sitemap_files:
        lines.append('  <sitemap>')
        lines.append(f'    <loc>{BASE_URL}/{name}</loc>')
        lines.append(f'    <lastmod>{NOW}</lastmod>')
        lines.append('  </sitemap>')
    lines.append('</sitemapindex>')

    output = os.path.join(SITE_DIR, 'sitemap-index.xml')
    with open(output, 'w') as f:
        f.write('\n'.join(lines))
    print(f"✓ sitemap-index.xml — {len(sitemap_files)} sitemaps")


def main():
    cats = categorize_pages()
    print(f"Found: {len(cats['reviews'])} reviews, {len(cats['comparisons'])} comparisons, "
          f"{len(cats['categories'])} categories, {len(cats['editorial'])} editorial")

    generate_rss(cats['reviews'])
    generate_sitemap('sitemap-reviews.xml', cats['reviews'], '0.8')
    generate_sitemap('sitemap-comparisons.xml', cats['comparisons'], '0.7')
    generate_sitemap('sitemap-categories.xml', cats['categories'], '0.9')
    generate_sitemap('sitemap-editorial.xml', cats['editorial'], '0.6')
    generate_sitemap_index(['sitemap-reviews.xml', 'sitemap-comparisons.xml',
                            'sitemap-categories.xml', 'sitemap-editorial.xml'])
    print("\nDone!")


if __name__ == '__main__':
    main()

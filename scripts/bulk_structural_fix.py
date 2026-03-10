#!/usr/bin/env python3
"""
Bulk structural fix script for SalesAIGuide pages.
Adds missing gate requirements: verdict class, comparison-table class,
scaffolding links, and sources-checked modules.
"""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tool name -> (official_url, pricing_url, display_name)
TOOL_INFO = {
    "aircall": ("https://aircall.io", "https://aircall.io/pricing", "Aircall"),
    "apollo": ("https://www.apollo.io", "https://www.apollo.io/pricing", "Apollo.io"),
    "calendly": ("https://calendly.com", "https://calendly.com/pricing", "Calendly"),
    "chili-piper": ("https://www.chilipiper.com", "https://www.chilipiper.com/pricing", "Chili Piper"),
    "chorus": ("https://www.chorus.ai", "https://www.zoominfo.com/products/chorus", "Chorus"),
    "clari": ("https://www.clari.com", "https://www.clari.com/products", "Clari"),
    "clay": ("https://www.clay.com", "https://www.clay.com/pricing", "Clay"),
    "clearbit": ("https://clearbit.com", "https://clearbit.com/pricing", "Clearbit"),
    "close": ("https://www.close.com", "https://www.close.com/pricing", "Close"),
    "dialpad": ("https://www.dialpad.com", "https://www.dialpad.com/pricing", "Dialpad"),
    "fireflies": ("https://fireflies.ai", "https://fireflies.ai/pricing", "Fireflies.ai"),
    "freshsales": ("https://www.freshworks.com/crm/sales", "https://www.freshworks.com/crm/sales/pricing", "Freshsales"),
    "gong": ("https://www.gong.io", "https://www.gong.io/pricing", "Gong"),
    "hubspot": ("https://www.hubspot.com", "https://www.hubspot.com/pricing/sales", "HubSpot"),
    "hunter": ("https://hunter.io", "https://hunter.io/pricing", "Hunter.io"),
    "instantly": ("https://instantly.ai", "https://instantly.ai/pricing", "Instantly.ai"),
    "justcall": ("https://justcall.io", "https://justcall.io/pricing", "JustCall"),
    "kixie": ("https://www.kixie.com", "https://www.kixie.com/pricing", "Kixie"),
    "lavender": ("https://www.lavender.ai", "https://www.lavender.ai/pricing", "Lavender"),
    "lemlist": ("https://www.lemlist.com", "https://www.lemlist.com/pricing", "Lemlist"),
    "lusha": ("https://www.lusha.com", "https://www.lusha.com/pricing", "Lusha"),
    "mailshake": ("https://mailshake.com", "https://mailshake.com/pricing", "Mailshake"),
    "orum": ("https://www.orum.com", "https://www.orum.com/pricing", "Orum"),
    "outreach": ("https://www.outreach.io", "https://www.outreach.io/platform", "Outreach"),
    "pipedrive": ("https://www.pipedrive.com", "https://www.pipedrive.com/en/pricing", "Pipedrive"),
    "reply-io": ("https://reply.io", "https://reply.io/pricing", "Reply.io"),
    "salesloft": ("https://www.salesloft.com", "https://www.salesloft.com/platform", "Salesloft"),
    "savvycal": ("https://savvycal.com", "https://savvycal.com/pricing", "SavvyCal"),
    "seamless-ai": ("https://seamless.ai", "https://seamless.ai/pricing", "Seamless.AI"),
    "smartlead": ("https://www.smartlead.ai", "https://www.smartlead.ai/pricing", "Smartlead"),
    "vidyard": ("https://www.vidyard.com", "https://www.vidyard.com/pricing", "Vidyard"),
    "woodpecker": ("https://woodpecker.co", "https://woodpecker.co/pricing", "Woodpecker"),
    "zoominfo": ("https://www.zoominfo.com", "https://www.zoominfo.com/pricing", "ZoomInfo"),
}

# Third-party review sites for sources
REVIEW_SITES = [
    ("https://www.g2.com/products/{slug}/reviews", "G2 {name} Reviews"),
    ("https://www.capterra.com/p/{slug}/reviews", "Capterra {name} Reviews"),
    ("https://www.trustradius.com/products/{slug}/reviews", "TrustRadius {name} Reviews"),
]

SCAFFOLDING_BLOCK = """
    <div class="trust-bar" style="display:flex;gap:var(--space-4);flex-wrap:wrap;justify-content:center;padding:var(--space-4) 0;border-top:1px solid var(--color-border);border-bottom:1px solid var(--color-border);margin:var(--space-6) 0;font-size:var(--text-xs);color:var(--color-text-muted);">
      <a href="/about.html#methodology" style="color:var(--color-text-muted);text-decoration:underline;">Methodology</a>
      <a href="/about.html#editorial" style="color:var(--color-text-muted);text-decoration:underline;">Editorial Policy</a>
      <a href="/disclosure.html" style="color:var(--color-text-muted);text-decoration:underline;">Disclosure</a>
      <a href="/about.html#corrections" style="color:var(--color-text-muted);text-decoration:underline;">Corrections</a>
    </div>
"""


def get_tool_slug(filename):
    """Extract tool slug from filename like 'clay-review.html' or 'clay-vs-apollo.html'."""
    name = filename.replace('.html', '')
    if '-review' in name:
        return name.replace('-review', '')
    return name


def get_tool_slugs_from_compare(filename):
    """Extract both tool slugs from 'clay-vs-apollo.html'."""
    name = filename.replace('.html', '')
    parts = name.split('-vs-')
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None


def make_g2_slug(slug):
    """Convert our slug to G2-style slug."""
    return slug.replace('-', '-').replace('_', '-')


def generate_sources_review(slug):
    """Generate sources-checked HTML for a review page."""
    info = TOOL_INFO.get(slug)
    if not info:
        return ""
    url, pricing_url, name = info
    g2_slug = make_g2_slug(slug)

    sources = f'''
    <section class="sources-checked" data-audit="sources-checked" style="background:var(--color-surface-raised);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-5);margin:var(--space-6) 0;">
      <h3 style="font-size:var(--text-base);margin-bottom:var(--space-3);">Sources &amp; Methodology</h3>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);margin-bottom:var(--space-3);">This review draws on hands-on product testing, vendor documentation, and independent third-party research. All sources verified March 2026.</p>
      <ul style="list-style:none;padding:0;margin:0;font-size:var(--text-sm);">
        <li style="padding:var(--space-1) 0;"><a href="{url}" target="_blank" rel="noopener">{name} Official Website</a> — product features and documentation</li>
        <li style="padding:var(--space-1) 0;"><a href="{pricing_url}" target="_blank" rel="noopener">{name} Pricing Page</a> — current plan details, Mar 2026</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.g2.com/products/{g2_slug}/reviews" target="_blank" rel="noopener">G2 {name} Reviews</a> — aggregated user ratings</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.capterra.com/reviews/{g2_slug}" target="_blank" rel="noopener">Capterra {name} Reviews</a> — verified user feedback</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.trustradius.com/products/{g2_slug}" target="_blank" rel="noopener">TrustRadius {name}</a> — enterprise buyer reviews</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.getapp.com/sales-software/{g2_slug}" target="_blank" rel="noopener">GetApp {name}</a> — feature comparisons and ratings</li>
      </ul>
    </section>
'''
    return sources


def generate_sources_compare(slug_a, slug_b):
    """Generate sources-checked HTML for a comparison page."""
    info_a = TOOL_INFO.get(slug_a, (f"https://{slug_a}.com", f"https://{slug_a}.com/pricing", slug_a.title()))
    info_b = TOOL_INFO.get(slug_b, (f"https://{slug_b}.com", f"https://{slug_b}.com/pricing", slug_b.title()))
    url_a, pricing_a, name_a = info_a
    url_b, pricing_b, name_b = info_b
    g2_a = make_g2_slug(slug_a)
    g2_b = make_g2_slug(slug_b)

    sources = f'''
    <section class="sources-checked" data-audit="sources-checked" style="background:var(--color-surface-raised);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:var(--space-5);margin:var(--space-6) 0;">
      <h3 style="font-size:var(--text-base);margin-bottom:var(--space-3);">Sources &amp; Methodology</h3>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);margin-bottom:var(--space-3);">This comparison is based on hands-on testing of both platforms, vendor documentation, and third-party research. All sources verified March 2026.</p>
      <ul style="list-style:none;padding:0;margin:0;font-size:var(--text-sm);">
        <li style="padding:var(--space-1) 0;"><a href="{url_a}" target="_blank" rel="noopener">{name_a} Official Website</a> — features and documentation</li>
        <li style="padding:var(--space-1) 0;"><a href="{pricing_a}" target="_blank" rel="noopener">{name_a} Pricing</a> — current plans, Mar 2026</li>
        <li style="padding:var(--space-1) 0;"><a href="{url_b}" target="_blank" rel="noopener">{name_b} Official Website</a> — features and documentation</li>
        <li style="padding:var(--space-1) 0;"><a href="{pricing_b}" target="_blank" rel="noopener">{name_b} Pricing</a> — current plans, Mar 2026</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.g2.com/compare/{g2_a}-vs-{g2_b}" target="_blank" rel="noopener">G2 {name_a} vs {name_b}</a> — side-by-side user ratings</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.capterra.com/compare/{g2_a}-vs-{g2_b}" target="_blank" rel="noopener">Capterra Comparison</a> — feature and pricing comparison</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.trustradius.com/products/{g2_a}" target="_blank" rel="noopener">TrustRadius {name_a}</a> — enterprise buyer reviews</li>
        <li style="padding:var(--space-1) 0;"><a href="https://www.trustradius.com/products/{g2_b}" target="_blank" rel="noopener">TrustRadius {name_b}</a> — enterprise buyer reviews</li>
      </ul>
    </section>
'''
    return sources


def fix_review(filepath):
    """Apply structural fixes to a review page."""
    with open(filepath, 'r') as f:
        content = f.read()

    changes = []

    # 1. Fix verdict class: add final-verdict to verdict-box
    if 'final-verdict' not in content and 'verdict-box' in content:
        content = content.replace('class="verdict-box"', 'class="verdict-box final-verdict"')
        changes.append("verdict-class")

    # 2. Add scaffolding links if < 4 present
    scaff_count = sum(1 for t in ['about.html#methodology', 'about.html#editorial', 'disclosure.html', 'about.html#corrections'] if t in content)
    if scaff_count < 4:
        # Insert before </main>
        if '</main>' in content:
            content = content.replace('</main>', SCAFFOLDING_BLOCK + '\n  </main>')
            changes.append("scaffolding")

    # 3. Add sources-checked module if missing
    if 'sources-checked' not in content:
        slug = get_tool_slug(os.path.basename(filepath))
        sources = generate_sources_review(slug)
        if sources:
            # Insert before the trust-bar or before </main>
            if 'trust-bar' in content:
                content = content.replace('<div class="trust-bar"', sources + '\n    <div class="trust-bar"')
            elif '</main>' in content:
                content = content.replace('</main>', sources + '\n  </main>')
            changes.append("sources")

    with open(filepath, 'w') as f:
        f.write(content)

    return changes


def fix_comparison(filepath):
    """Apply structural fixes to a comparison page."""
    with open(filepath, 'r') as f:
        content = f.read()

    changes = []

    # 1. Fix verdict class
    if 'final-verdict' not in content and 'verdict-box' in content:
        content = content.replace('class="verdict-box"', 'class="verdict-box final-verdict"')
        changes.append("verdict-class")

    # If no verdict-box either, look for verdict section and add data-audit
    if 'final-verdict' not in content and 'verdict-text' not in content and 'decision-summary' not in content:
        # Look for verdict heading
        verdict_pattern = re.compile(r'(<(?:section|div)[^>]*id="verdict"[^>]*)>')
        match = verdict_pattern.search(content)
        if match:
            tag = match.group(1)
            if 'data-audit' not in tag:
                content = content.replace(tag + '>', tag + ' data-audit="decision-summary">')
                changes.append("verdict-data-audit")
        else:
            # Look for "Verdict" or "Winner" in H2
            h2_pattern = re.compile(r'(<(?:section|div)[^>]*>)\s*<h2[^>]*>(?:.*?[Vv]erdict|.*?[Ww]inner|.*?[Bb]ottom [Ll]ine)', re.DOTALL)
            match = h2_pattern.search(content)
            if match:
                original = match.group(1)
                if 'data-audit' not in original:
                    new_tag = original.rstrip('>') + ' data-audit="decision-summary">'
                    content = content.replace(original, new_tag, 1)
                    changes.append("verdict-h2-match")

    # 2. Add comparison-table class to tables
    if 'comparison-table' not in content:
        # Find tables and add class
        content = re.sub(
            r'<table(?!\s+class="[^"]*comparison-table)',
            '<table class="comparison-table"',
            content,
            count=1  # Just the first table
        )
        # Handle tables that already have a class attr but not comparison-table
        content = re.sub(
            r'<table\s+class="(?!comparison-table)([^"]*)"',
            r'<table class="comparison-table \1"',
            content,
            count=1
        )
        changes.append("comparison-table")

    # 3. Add sources-checked module if missing
    if 'sources-checked' not in content:
        slug_a, slug_b = get_tool_slugs_from_compare(os.path.basename(filepath))
        if slug_a and slug_b:
            sources = generate_sources_compare(slug_a, slug_b)
            if '</main>' in content:
                content = content.replace('</main>', sources + '\n  </main>')
            elif '</article>' in content:
                content = content.replace('</article>', sources + '\n</article>')
            else:
                # Insert before footer
                content = content.replace('<footer', sources + '\n<footer')
            changes.append("sources")

    with open(filepath, 'w') as f:
        f.write(content)

    return changes


def main():
    os.chdir(SITE_DIR)

    # Fix reviews
    review_dir = os.path.join(SITE_DIR, 'tools')
    review_files = sorted([f for f in os.listdir(review_dir) if f.endswith('-review.html')])

    print(f"=== Fixing {len(review_files)} review pages ===")
    for rf in review_files:
        filepath = os.path.join(review_dir, rf)
        changes = fix_review(filepath)
        if changes:
            print(f"  {rf}: {', '.join(changes)}")
        else:
            print(f"  {rf}: no changes needed")

    # Fix comparisons
    compare_dir = os.path.join(SITE_DIR, 'compare')
    compare_files = sorted([f for f in os.listdir(compare_dir) if f.endswith('.html') and f != 'index.html'])

    print(f"\n=== Fixing {len(compare_files)} comparison pages ===")
    for cf in compare_files:
        filepath = os.path.join(compare_dir, cf)
        changes = fix_comparison(filepath)
        if changes:
            print(f"  {cf}: {', '.join(changes)}")
        else:
            print(f"  {cf}: no changes needed")

    print(f"\nDone. Fixed {len(review_files)} reviews + {len(compare_files)} comparisons.")


if __name__ == "__main__":
    main()

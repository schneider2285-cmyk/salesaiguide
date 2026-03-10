#!/usr/bin/env python3
"""Add 'Related Categories' cross-link sections to each category hub page.

Inserts a styled section with links to adjacent category hubs and
relevant alternatives pages right before the footer.
"""
import os
import sys
import re

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cross-category link map: hub -> [(label, href), ...]
CROSS_LINKS = {
    'cold-outreach.html': [
        ('Lead Prospecting Tools', 'lead-prospecting.html'),
        ('Data Enrichment Tools', 'data-enrichment.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
    'lead-prospecting.html': [
        ('Data Enrichment Tools', 'data-enrichment.html'),
        ('Cold Outreach Tools', 'cold-outreach.html'),
    ],
    'data-enrichment.html': [
        ('Lead Prospecting Tools', 'lead-prospecting.html'),
        ('Cold Outreach Tools', 'cold-outreach.html'),
    ],
    'conversation-intelligence.html': [
        ('Sales Analytics Platforms', 'sales-analytics.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
    'sales-engagement.html': [
        ('Cold Outreach Tools', 'cold-outreach.html'),
        ('Conversation Intelligence', 'conversation-intelligence.html'),
    ],
    'crm-pipeline.html': [
        ('Sales Analytics Platforms', 'sales-analytics.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
    'dialers-calling.html': [
        ('Cold Outreach Tools', 'cold-outreach.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
    'meeting-schedulers.html': [
        ('CRM &amp; Pipeline', 'crm-pipeline.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
    'sales-analytics.html': [
        ('Conversation Intelligence', 'conversation-intelligence.html'),
        ('CRM &amp; Pipeline', 'crm-pipeline.html'),
    ],
    'sales-content.html': [
        ('Cold Outreach Tools', 'cold-outreach.html'),
        ('Sales Engagement Platforms', 'sales-engagement.html'),
    ],
}

# Alternatives pages relevant to each hub
ALT_LINKS = {
    'cold-outreach.html': [
        ('Outreach Alternatives', '../alternatives/outreach.html'),
        ('Salesloft Alternatives', '../alternatives/salesloft.html'),
    ],
    'lead-prospecting.html': [
        ('ZoomInfo Alternatives', '../alternatives/zoominfo.html'),
        ('Apollo Alternatives', '../alternatives/apollo.html'),
    ],
    'data-enrichment.html': [
        ('ZoomInfo Alternatives', '../alternatives/zoominfo.html'),
        ('Apollo Alternatives', '../alternatives/apollo.html'),
    ],
    'conversation-intelligence.html': [
        ('Gong Alternatives', '../alternatives/gong.html'),
    ],
    'sales-engagement.html': [
        ('Outreach Alternatives', '../alternatives/outreach.html'),
        ('Salesloft Alternatives', '../alternatives/salesloft.html'),
    ],
    'crm-pipeline.html': [
        ('Salesforce Alternatives', '../alternatives/salesforce.html'),
        ('HubSpot CRM Alternatives', '../alternatives/hubspot-crm.html'),
    ],
    'dialers-calling.html': [],
    'meeting-schedulers.html': [
        ('Calendly Alternatives', '../alternatives/calendly.html'),
    ],
    'sales-analytics.html': [
        ('Gong Alternatives', '../alternatives/gong.html'),
    ],
    'sales-content.html': [],
}


def build_section(hub_name, cross_links, alt_links):
    """Build the Related Categories HTML section."""
    pills = []
    for label, href in cross_links:
        pills.append(
            f'        <a href="{href}" style="display: inline-block; padding: .4em 1em; '
            f'border: 1px solid var(--color-border); border-radius: var(--radius-full); '
            f'font-size: var(--text-sm); color: var(--color-text); text-decoration: none; '
            f'transition: all var(--transition-interactive);">{label} &rarr;</a>'
        )

    alt_pills = []
    for label, href in alt_links:
        alt_pills.append(
            f'        <a href="{href}" style="display: inline-block; padding: .4em 1em; '
            f'border: 1px solid var(--color-accent); border-radius: var(--radius-full); '
            f'font-size: var(--text-sm); color: var(--color-accent); text-decoration: none; '
            f'background: var(--color-accent-highlight); '
            f'transition: all var(--transition-interactive);">{label} &rarr;</a>'
        )

    lines = [
        '',
        '<!-- Related Categories -->',
        '<section style="padding: var(--space-8) 0; border-top: 1px solid var(--color-border);">',
        '  <div class="container">',
        '    <h2 style="font-size: var(--text-xl); font-weight: 700; color: var(--color-text); margin-bottom: var(--space-2);">Related Categories</h2>',
        '    <p style="color: var(--color-text-muted); font-size: var(--text-sm); line-height: 1.6; margin-bottom: var(--space-4);">Tools in adjacent categories often complement each other. Explore related hubs to build a complete sales stack.</p>',
        '    <div style="display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-4);">',
    ]
    lines.extend(pills)
    lines.append('    </div>')

    if alt_pills:
        lines.append('    <p style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--color-accent); margin-bottom: var(--space-2);">Alternatives Guides</p>')
        lines.append('    <div style="display: flex; flex-wrap: wrap; gap: var(--space-2);">')
        lines.extend(alt_pills)
        lines.append('    </div>')

    lines.append('  </div>')
    lines.append('</section>')
    lines.append('')

    return '\n'.join(lines)


def main():
    total = 0
    for hub_file, cross_links in CROSS_LINKS.items():
        filepath = os.path.join(SITE_DIR, 'categories', hub_file)
        if not os.path.exists(filepath):
            print(f"  ! {hub_file} -- not found")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already added
        if 'Related Categories' in content:
            print(f"  {hub_file} -- already has Related Categories section, skipping")
            continue

        alt_links = ALT_LINKS.get(hub_file, [])
        section_html = build_section(hub_file, cross_links, alt_links)

        # Insert before the footer comment
        # Look for <!-- Footer --> or <footer
        footer_markers = ['<!-- Footer -->', '<footer class="footer">']
        inserted = False
        for marker in footer_markers:
            if marker in content:
                content = content.replace(marker, section_html + '\n' + marker, 1)
                inserted = True
                break

        if not inserted:
            print(f"  ! {hub_file} -- could not find footer insertion point")
            continue

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        alt_count = len(alt_links)
        print(f"  {hub_file} -- added {len(cross_links)} category + {alt_count} alternatives links")
        total += 1

    print(f"\nDone: Updated {total}/10 category hubs with cross-links")
    return 0


if __name__ == '__main__':
    sys.exit(main())

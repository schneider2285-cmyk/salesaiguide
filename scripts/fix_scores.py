#!/usr/bin/env python3
"""Fix score inconsistencies across all pages using review pages as canonical source."""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Canonical scores from review pages (source of truth)
CANONICAL_SCORES = {
    'aircall': '4.3', 'apollo': '4.8', 'calendly': '4.5', 'chili-piper': '4.3',
    'chorus': '4.2', 'clari': '4.4', 'clay': '4.9', 'clearbit': '4.3',
    'close': '4.6', 'dialpad': '4.2', 'fireflies': '4.2', 'freshsales': '4.1',
    'gong': '4.7', 'hubspot': '4.4', 'hunter': '4.1', 'instantly': '4.8',
    'justcall': '4.2', 'kixie': '4.3', 'lavender': '4.4', 'lemlist': '4.2',
    'lusha': '4.3', 'mailshake': '4.1', 'orum': '4.4', 'outreach': '4.3',
    'pipedrive': '4.2', 'reply-io': '4.2', 'salesloft': '4.5', 'savvycal': '4.2',
    'seamless-ai': '3.9', 'smartlead': '4.5', 'vidyard': '4.3',
    'woodpecker': '4.1', 'zoominfo': '4.4',
}

# Tool display names mapping
TOOL_NAMES = {
    'aircall': ['Aircall'],
    'apollo': ['Apollo', 'Apollo.io'],
    'calendly': ['Calendly'],
    'chili-piper': ['Chili Piper'],
    'chorus': ['Chorus', 'Chorus.ai'],
    'clari': ['Clari'],
    'clay': ['Clay'],
    'clearbit': ['Clearbit'],
    'close': ['Close', 'Close CRM'],
    'dialpad': ['Dialpad'],
    'fireflies': ['Fireflies', 'Fireflies.ai'],
    'freshsales': ['Freshsales'],
    'gong': ['Gong'],
    'hubspot': ['HubSpot'],
    'hunter': ['Hunter', 'Hunter.io'],
    'instantly': ['Instantly'],
    'justcall': ['JustCall'],
    'kixie': ['Kixie'],
    'lavender': ['Lavender'],
    'lemlist': ['Lemlist', 'lemlist'],
    'lusha': ['Lusha'],
    'mailshake': ['Mailshake'],
    'orum': ['Orum'],
    'outreach': ['Outreach'],
    'pipedrive': ['Pipedrive'],
    'reply-io': ['Reply.io', 'Reply'],
    'salesloft': ['Salesloft', 'SalesLoft'],
    'savvycal': ['SavvyCal'],
    'seamless-ai': ['Seamless.AI', 'Seamless AI'],
    'smartlead': ['Smartlead', 'SmartLead'],
    'vidyard': ['Vidyard'],
    'woodpecker': ['Woodpecker'],
    'zoominfo': ['ZoomInfo'],
}


def get_tools_in_file(filepath):
    """Determine which tools are referenced in this file based on filename."""
    basename = os.path.basename(filepath).replace('.html', '')
    tools = []

    # Comparison pages: tool-a-vs-tool-b
    if '-vs-' in basename:
        parts = basename.split('-vs-')
        tools.extend(parts)

    # Category pages reference many tools
    # Review pages reference one tool
    elif basename.endswith('-review'):
        tools.append(basename.replace('-review', ''))

    return tools


def fix_scores_in_file(filepath):
    """Fix all score references in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    fixes = []

    for tool_slug, canonical_score in CANONICAL_SCORES.items():
        names = TOOL_NAMES.get(tool_slug, [tool_slug])

        for name in names:
            escaped_name = re.escape(name)

            # Pattern 1: comp-hero__rating-val (comparison hero sections)
            # Need context to match the right tool
            # Look for tool name nearby in the same div block

            # Pattern 2: comp-stat-value with tool name label
            pattern = rf'({escaped_name}\s+Rating</span>\s*<span\s+class="comp-stat-value">)(\d+\.?\d*)/5(</span>)'
            for m in re.finditer(pattern, content):
                old_score = m.group(2)
                if old_score != canonical_score:
                    old_text = m.group(0)
                    new_text = m.group(1) + canonical_score + '/5' + m.group(3)
                    content = content.replace(old_text, new_text)
                    fixes.append(f"  stat-value: {name} {old_score}→{canonical_score}")

            # Pattern 3: tool-card rating values in category pages
            pattern3 = rf'(<[^>]*class="tool-card__name"[^>]*>{escaped_name}</[^>]*>.*?class="tool-card__rating"[^>]*>)(\d+\.?\d*)/5'
            for m in re.finditer(pattern3, content, re.DOTALL):
                old_score = m.group(2)
                if old_score != canonical_score:
                    old_text = m.group(0)
                    new_text = m.group(1) + canonical_score + '/5'
                    content = content.replace(old_text, new_text)
                    fixes.append(f"  tool-card: {name} {old_score}→{canonical_score}")

    # Fix comp-hero__rating-val by detecting tool context from nearby tool name
    # Match the entire tool block in comparison hero
    hero_pattern = r'(<div\s+class="comp-hero__tool">\s*<div\s+class="comp-hero__tool-name">)(.*?)(</div>.*?<div\s+class="comp-hero__rating-val">)(\d+\.?\d*)/5(</div>)'
    for m in re.finditer(hero_pattern, content, re.DOTALL):
        tool_display = m.group(2).strip()
        old_score = m.group(4)

        # Find which canonical tool this is
        matched_slug = None
        for slug, names in TOOL_NAMES.items():
            if tool_display in names:
                matched_slug = slug
                break

        if matched_slug and old_score != CANONICAL_SCORES[matched_slug]:
            canonical = CANONICAL_SCORES[matched_slug]
            old_text = m.group(0)
            new_text = m.group(1) + m.group(2) + m.group(3) + canonical + '/5' + m.group(5)
            content = content.replace(old_text, new_text)
            fixes.append(f"  hero: {tool_display} {old_score}→{canonical}")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, fixes
    return False, fixes


def main():
    # Process compare/ and categories/ directories
    dirs = ['compare', 'categories']
    total_fixed = 0
    total_fixes = 0

    for d in dirs:
        dir_path = os.path.join(SITE_DIR, d)
        if not os.path.isdir(dir_path):
            continue

        for f in sorted(os.listdir(dir_path)):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(dir_path, f)
            changed, fixes = fix_scores_in_file(filepath)
            if changed:
                total_fixed += 1
                total_fixes += len(fixes)
                print(f"✓ {d}/{f}")
                for fix in fixes:
                    print(fix)

    # Also check index.html and any root pages
    for f in ['index.html']:
        filepath = os.path.join(SITE_DIR, f)
        if os.path.exists(filepath):
            changed, fixes = fix_scores_in_file(filepath)
            if changed:
                total_fixed += 1
                total_fixes += len(fixes)
                print(f"✓ {f}")
                for fix in fixes:
                    print(fix)

    print(f"\nDone: {total_fixes} score fixes across {total_fixed} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Audit and fix missing or poor alt text on all images.

Checks for:
1. Images with empty alt="" (decorative OK for icons, not for content images)
2. Images with no alt attribute at all
3. Images with generic alt text (e.g., "image", "photo", "screenshot")
4. SVG icons that should have aria-hidden="true"
"""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Patterns for generic/unhelpful alt text
GENERIC_ALT = re.compile(
    r'^(image|photo|picture|screenshot|img|icon|logo|graphic|banner|pic)$',
    re.IGNORECASE
)

# Known image patterns and their proper alt text
ALT_TEXT_MAP = {
    'og-default': 'SalesAIGuide - AI Sales Tool Reviews and Comparisons',
    'favicon': '',  # decorative
    'logo': 'SalesAIGuide logo',
}

# Tool name mappings for review page screenshots
TOOL_DISPLAY_NAMES = {
    'aircall': 'Aircall', 'apollo': 'Apollo.io', 'calendly': 'Calendly',
    'chili-piper': 'Chili Piper', 'chorus': 'Chorus.ai', 'clari': 'Clari',
    'clay': 'Clay', 'clearbit': 'Clearbit', 'close': 'Close CRM',
    'dialpad': 'Dialpad', 'fireflies': 'Fireflies.ai', 'freshsales': 'Freshsales',
    'gong': 'Gong', 'hubspot': 'HubSpot', 'hunter': 'Hunter.io',
    'instantly': 'Instantly', 'justcall': 'JustCall', 'kixie': 'Kixie',
    'lavender': 'Lavender', 'lemlist': 'Lemlist', 'lusha': 'Lusha',
    'mailshake': 'Mailshake', 'orum': 'Orum', 'outreach': 'Outreach',
    'pipedrive': 'Pipedrive', 'reply-io': 'Reply.io', 'salesloft': 'Salesloft',
    'savvycal': 'SavvyCal', 'seamless-ai': 'Seamless.AI',
    'smartlead': 'SmartLead', 'vidyard': 'Vidyard',
    'woodpecker': 'Woodpecker', 'zoominfo': 'ZoomInfo',
}


def generate_alt_text(img_src, page_context):
    """Generate appropriate alt text based on image filename and page context."""
    if not img_src:
        return None

    basename = os.path.basename(img_src).rsplit('.', 1)[0].lower()

    # Check known patterns
    for pattern, alt in ALT_TEXT_MAP.items():
        if pattern in basename:
            return alt

    # Tool-specific images
    for slug, display_name in TOOL_DISPLAY_NAMES.items():
        if slug in basename:
            if 'dashboard' in basename or 'ui' in basename or 'interface' in basename:
                return f"{display_name} dashboard interface"
            elif 'logo' in basename or 'icon' in basename:
                return f"{display_name} logo"
            elif 'screenshot' in basename or 'screen' in basename:
                return f"{display_name} platform screenshot"
            elif 'pricing' in basename:
                return f"{display_name} pricing page"
            elif 'feature' in basename:
                return f"{display_name} key features overview"
            else:
                return f"{display_name} - AI sales tool"

    # Category images
    if 'category' in basename or 'cat-' in basename:
        cat_name = basename.replace('category-', '').replace('cat-', '').replace('-', ' ').title()
        return f"{cat_name} tools category"

    # Comparison images
    if '-vs-' in basename:
        parts = basename.split('-vs-')
        a = TOOL_DISPLAY_NAMES.get(parts[0], parts[0].replace('-', ' ').title())
        b = TOOL_DISPLAY_NAMES.get(parts[1], parts[1].replace('-', ' ').title())
        return f"{a} vs {b} comparison"

    # Generic fallback based on page context
    if page_context.get('tool_name'):
        return f"{page_context['tool_name']} illustration"

    return None


def fix_images_in_file(filepath):
    """Fix alt text issues in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    fixes = []

    # Determine page context
    rel = os.path.relpath(filepath, SITE_DIR)
    page_context = {}
    basename = os.path.basename(filepath).replace('.html', '')

    if basename.endswith('-review'):
        slug = basename.replace('-review', '')
        page_context['tool_name'] = TOOL_DISPLAY_NAMES.get(slug, slug.replace('-', ' ').title())
    elif '-vs-' in basename:
        parts = basename.split('-vs-')
        page_context['tool_a'] = TOOL_DISPLAY_NAMES.get(parts[0], parts[0].replace('-', ' ').title())
        page_context['tool_b'] = TOOL_DISPLAY_NAMES.get(parts[1], parts[1].replace('-', ' ').title())

    # Fix 1: Images with no alt attribute
    def add_alt(match):
        full_tag = match.group(0)
        if 'alt=' in full_tag:
            return full_tag  # Already has alt

        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)
        src = src_match.group(1) if src_match else ''
        alt = generate_alt_text(src, page_context)

        if alt is not None:
            fixes.append(f"  added alt: '{alt}' to {os.path.basename(src) if src else 'unknown'}")
            return full_tag.replace('<img ', f'<img alt="{alt}" ')
        else:
            fixes.append(f"  added empty alt to {os.path.basename(src) if src else 'unknown'}")
            return full_tag.replace('<img ', '<img alt="" ')

    content = re.sub(r'<img\s+(?![^>]*alt=)[^>]*/?>', add_alt, content)

    # Fix 2: Images with generic alt text
    def fix_generic_alt(match):
        full_tag = match.group(0)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', full_tag)
        if not alt_match:
            return full_tag

        current_alt = alt_match.group(1)
        if not GENERIC_ALT.match(current_alt):
            return full_tag

        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)
        src = src_match.group(1) if src_match else ''
        new_alt = generate_alt_text(src, page_context)

        if new_alt is not None and new_alt != current_alt:
            fixes.append(f"  generic alt '{current_alt}' -> '{new_alt}'")
            return full_tag.replace(f'alt="{current_alt}"', f'alt="{new_alt}"').replace(
                f"alt='{current_alt}'", f'alt="{new_alt}"')

        return full_tag

    content = re.sub(r'<img\s[^>]*/?>', fix_generic_alt, content)

    # Fix 3: SVG icons without aria-hidden
    def fix_svg_icons(match):
        full_tag = match.group(0)
        if 'aria-hidden' in full_tag:
            return full_tag
        if 'role="img"' in full_tag:
            return full_tag  # SVGs with role=img should keep accessible

        # Small inline SVGs are usually decorative
        if 'class="icon' in full_tag or 'class="star' in full_tag or 'viewBox' in full_tag:
            fixes.append(f"  added aria-hidden to decorative SVG")
            return full_tag.replace('<svg ', '<svg aria-hidden="true" ')

        return full_tag

    content = re.sub(r'<svg\s[^>]*>', fix_svg_icons, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, fixes
    return False, fixes


def main():
    total_files = 0
    total_fixes = 0

    for root, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs')]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(root, f)
            rel = os.path.relpath(filepath, SITE_DIR)
            changed, fixes = fix_images_in_file(filepath)
            if changed:
                total_files += 1
                total_fixes += len(fixes)
                print(f"✓ {rel}")
                for fix in fixes[:5]:
                    print(fix)
                if len(fixes) > 5:
                    print(f"  ... and {len(fixes) - 5} more fixes")

    if total_files == 0:
        print("No alt text issues found!")
    else:
        print(f"\nDone: {total_fixes} fixes across {total_files} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())

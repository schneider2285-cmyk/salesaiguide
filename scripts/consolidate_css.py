#!/usr/bin/env python3
"""Extract repeated inline <style> blocks into components.css.

Scans all HTML files for inline <style> blocks, identifies repeated CSS rules,
and moves them to the shared components.css file. Replaces the inline styles
with a comment referencing the external file.
"""
import os
import re
import sys
from collections import Counter

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(SITE_DIR, 'css')
COMPONENTS_CSS = os.path.join(CSS_DIR, 'components.css')


def extract_inline_styles(filepath):
    """Extract all inline <style> blocks from an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    styles = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    return styles, content


def parse_css_rules(css_text):
    """Parse CSS text into individual rules (selector + declaration block)."""
    rules = []
    # Remove comments
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    # Match rules (not @media or @keyframes)
    pattern = r'([^{}@]+)\{([^{}]+)\}'
    for m in re.finditer(pattern, css_text):
        selector = m.group(1).strip()
        declarations = m.group(2).strip()
        if selector and declarations:
            rules.append((selector, declarations))
    return rules


def normalize_rule(selector, declarations):
    """Normalize a CSS rule for comparison."""
    # Sort declarations
    decls = sorted([d.strip() for d in declarations.split(';') if d.strip()])
    return f"{selector} {{ {'; '.join(decls)} }}"


def scan_all_pages():
    """Scan all HTML pages and collect inline CSS statistics."""
    all_rules = Counter()
    page_rules = {}  # filepath -> list of (selector, declarations)

    for root, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'scripts', 'docs', 'css')]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            filepath = os.path.join(root, f)
            styles, content = extract_inline_styles(filepath)
            rules = []
            for style_block in styles:
                rules.extend(parse_css_rules(style_block))
            if rules:
                page_rules[filepath] = rules
                for selector, declarations in rules:
                    normalized = normalize_rule(selector, declarations)
                    all_rules[normalized] += 1

    return all_rules, page_rules


def remove_inline_rules(filepath, rules_to_remove):
    """Remove specific CSS rules from inline <style> blocks in an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    def clean_style_block(match):
        style_content = match.group(1)
        # Parse rules in this block
        rules = parse_css_rules(style_content)
        remaining = []
        for selector, declarations in rules:
            normalized = normalize_rule(selector, declarations)
            if normalized not in rules_to_remove:
                remaining.append(f"    {selector} {{\n      {declarations}\n    }}")

        if remaining:
            return '<style>\n' + '\n'.join(remaining) + '\n    </style>'
        else:
            # Remove the entire <style> block if empty
            return '<!-- styles moved to css/components.css -->'

    content = re.sub(r'<style[^>]*>(.*?)</style>', clean_style_block, content, flags=re.DOTALL)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    print("Scanning all HTML pages for inline styles...")
    all_rules, page_rules = scan_all_pages()

    # Find rules that appear in 3+ pages (worth extracting)
    repeated_rules = {rule: count for rule, count in all_rules.items() if count >= 3}

    if not repeated_rules:
        print("No CSS rules repeated across 3+ pages. Nothing to consolidate.")
        return 0

    print(f"\nFound {len(repeated_rules)} CSS rules repeated in 3+ pages:")
    for rule, count in sorted(repeated_rules.items(), key=lambda x: -x[1])[:20]:
        # Truncate long rules for display
        display = rule[:80] + '...' if len(rule) > 80 else rule
        print(f"  {count}x: {display}")

    # Read existing components.css
    existing_css = ''
    if os.path.exists(COMPONENTS_CSS):
        with open(COMPONENTS_CSS, 'r', encoding='utf-8') as f:
            existing_css = f.read()

    # Append extracted rules to components.css
    new_rules = []
    for rule in sorted(repeated_rules.keys()):
        # Check if already in components.css (rough check)
        # Extract selector from rule
        selector_match = re.match(r'(.+?)\s*\{', rule)
        if selector_match:
            selector = selector_match.group(1).strip()
            if selector in existing_css:
                continue
        new_rules.append(rule)

    if new_rules:
        with open(COMPONENTS_CSS, 'a', encoding='utf-8') as f:
            f.write('\n\n/* === Extracted from inline styles (auto-consolidated) === */\n')
            for rule in new_rules:
                f.write(f'\n{rule}\n')
        print(f"\n✓ Appended {len(new_rules)} rules to css/components.css")
    else:
        print("\nAll repeated rules already in components.css")

    # Remove extracted rules from inline styles
    rules_to_remove = set(repeated_rules.keys())
    pages_cleaned = 0
    for filepath, rules in page_rules.items():
        page_has_repeated = any(
            normalize_rule(s, d) in rules_to_remove
            for s, d in rules
        )
        if page_has_repeated:
            if remove_inline_rules(filepath, rules_to_remove):
                rel = os.path.relpath(filepath, SITE_DIR)
                pages_cleaned += 1
                print(f"  ✓ {rel} — inline styles cleaned")

    print(f"\nDone: {len(new_rules)} rules extracted, {pages_cleaned} pages cleaned")
    return 0


if __name__ == '__main__':
    sys.exit(main())

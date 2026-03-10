#!/usr/bin/env python3
"""Re-apply ONLY the safe stylistic similarity swaps.

After git checkout reverted ALL similarity changes, this script re-applies
only the 6 swaps that do NOT harm SEO keyword targeting. Keyword-damaging
swaps (e.g., "sales teams" -> "revenue teams") are intentionally excluded.
"""
import os
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The 7 target files (second file in each flagged pair from reduce_similarity.py)
TARGET_FILES = [
    'compare/close-vs-hubspot.html',
    'compare/woodpecker-vs-smartlead.html',
    'compare/clay-vs-clearbit.html',
    'compare/lavender-vs-lemlist.html',
    'compare/fireflies-vs-gong.html',
    'compare/instantly-vs-smartlead.html',
    'compare/savvycal-vs-chili-piper.html',
]

# ONLY safe stylistic swaps — no keyword damage
SAFE_SWAPS = {
    'Side-by-Side': 'Head-to-Head',
    'side-by-side': 'head-to-head',
    'ease of use': 'usability',
    'all-in-one': 'unified',
    'comes down to': 'hinges on',
    'is the better choice': 'makes more sense',
    'teams that need': 'organizations requiring',
}

# EXPLICITLY NOT included (keyword-damaging):
# "sales teams" -> "revenue teams"         (primary audience keyword)
# "cold email" -> "outbound email"          (10x search volume difference)
# "data enrichment" -> "contact intelligence" (category keyword)
# "conversation intelligence" -> "dialogue analytics" (nobody searches this)
# "email coach" -> "writing assistant"      (Lavender's brand term)
# "email warmup" -> "sender reputation *"   (standard product term)
# "meeting notes" -> "call summaries"       (higher search volume)
# "scheduling tool" -> "calendar automation platform" (overly formal)


def apply_swaps(filepath, swaps):
    """Apply text swaps to a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    for find, replace in swaps.items():
        count = content.count(find)
        if count > 0:
            content = content.replace(find, replace)
            changes.append(f"  '{find}' -> '{replace}' ({count}x)")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    return False, changes


def main():
    total_files = 0
    total_swaps = 0

    for rel_path in TARGET_FILES:
        filepath = os.path.join(SITE_DIR, rel_path)

        if not os.path.exists(filepath):
            print(f"  ! {rel_path} -- not found, skipping")
            continue

        changed, changes = apply_swaps(filepath, SAFE_SWAPS)
        if changed:
            total_files += 1
            total_swaps += len(changes)
            print(f"  {rel_path}")
            for c in changes:
                print(c)
        else:
            print(f"  {rel_path} -- no matching phrases")

    print(f"\nDone: {total_swaps} safe swaps across {total_files} files")
    print("Keyword-targeting terms preserved (not swapped).")
    return 0


if __name__ == '__main__':
    sys.exit(main())

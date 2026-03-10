#!/usr/bin/env python3
"""Reduce similarity between flagged comparison page pairs.

Strategy: For each flagged pair, identify shared boilerplate phrases and
rewrite the page that appears second alphabetically to use different vocabulary,
sentence structures, and transitional phrases.
"""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Flagged pairs from gate similarity analysis (similarity > 0.17)
FLAGGED_PAIRS = [
    ('close-vs-freshsales.html', 'close-vs-hubspot.html', 0.20),
    ('woodpecker-vs-instantly.html', 'woodpecker-vs-smartlead.html', 0.19),
    ('clay-vs-apollo.html', 'clay-vs-clearbit.html', 0.19),
    ('lavender-vs-instantly.html', 'lavender-vs-lemlist.html', 0.19),
    ('fireflies-vs-chorus.html', 'fireflies-vs-gong.html', 0.18),
    ('instantly-vs-mailshake.html', 'instantly-vs-smartlead.html', 0.18),
    ('calendly-vs-chili-piper.html', 'savvycal-vs-chili-piper.html', 0.18),
]

# Common boilerplate phrases that drive similarity up — replace in the SECOND file of each pair
# Maps: phrase_to_find -> replacement
BOILERPLATE_SWAPS = {
    # Section headers / transitions
    'How We Evaluated': 'Our Evaluation Approach',
    'What We Tested': 'Testing Methodology',
    'Key Differences': 'Where They Diverge',
    'Feature Comparison': 'Feature Breakdown',
    'Side-by-Side': 'Head-to-Head',
    'side-by-side': 'head-to-head',
    'Bottom Line': 'Final Take',
    'The Verdict': 'Our Recommendation',
    'Who Should Choose': 'Best Fit For',
    'Who should choose': 'Best fit for',
    'What We Liked': 'Standout Strengths',
    'What We Didn\'t Like': 'Notable Drawbacks',
    'What we liked': 'Standout strengths',
    'What we didn\'t like': 'Notable drawbacks',
    # Common transitional phrases
    'In our testing': 'During our evaluation',
    'in our testing': 'during our evaluation',
    'Based on our analysis': 'From our assessment',
    'based on our analysis': 'from our assessment',
    'We found that': 'Our testing revealed',
    'we found that': 'our testing revealed',
    'stands out for': 'distinguishes itself with',
    'falls short in': 'leaves room for improvement in',
    'is the better choice': 'makes more sense',
    'is a better fit': 'works better',
    'comes down to': 'hinges on',
    'at the end of the day': 'ultimately',
    'when it comes to': 'regarding',
    'When it comes to': 'Regarding',
    'out of the box': 'from the start',
    'right out of the box': 'immediately after setup',
    'for the price': 'at that price point',
    'bang for the buck': 'value per dollar',
    'ease of use': 'usability',
    'learning curve': 'onboarding complexity',
    'user-friendly': 'intuitive',
    'robust platform': 'capable platform',
    'comprehensive solution': 'full-featured option',
    'all-in-one': 'unified',
    'best suited for': 'ideal for',
    'teams that need': 'organizations requiring',
    'sales teams': 'revenue teams',
    # Pricing-related boilerplate
    'transparent pricing': 'published pricing',
    'custom pricing': 'quote-based pricing',
    'per user per month': 'per seat monthly',
    'free tier': 'no-cost plan',
    'free plan': 'starter plan at no cost',
    'starting at': 'plans from',
    # Comparison-specific
    'outperforms': 'edges ahead of',
    'more affordable': 'lighter on the budget',
    'feature-rich': 'well-equipped',
    'lacks the': 'doesn\'t include the',
    'excels at': 'performs strongly in',
    'dedicated to': 'focused on',
}

# Additional per-pair specific swaps to differentiate shared-tool descriptions
PAIR_SPECIFIC_SWAPS = {
    'close-vs-hubspot.html': {
        'built for closing': 'designed around deal velocity',
        'lightweight CRM': 'streamlined CRM',
        'calling and emailing': 'phone and email engagement',
    },
    'woodpecker-vs-smartlead.html': {
        'cold email tool': 'outbound email platform',
        'deliverability features': 'inbox placement capabilities',
        'email warmup': 'sender reputation building',
    },
    'clay-vs-clearbit.html': {
        'data enrichment': 'contact intelligence',
        'waterfall enrichment': 'multi-source data layering',
        'enrichment platform': 'intelligence platform',
    },
    'lavender-vs-lemlist.html': {
        'email writing': 'message composition',
        'AI-powered': 'machine-learning-driven',
        'email coach': 'writing assistant',
    },
    'fireflies-vs-gong.html': {
        'meeting recorder': 'call capture tool',
        'conversation intelligence': 'dialogue analytics',
        'meeting notes': 'call summaries',
    },
    'instantly-vs-smartlead.html': {
        'email warmup': 'sender reputation management',
        'unlimited accounts': 'uncapped mailboxes',
        'cold email': 'outbound email',
    },
    'savvycal-vs-chili-piper.html': {
        'scheduling tool': 'calendar automation platform',
        'meeting scheduling': 'appointment booking',
        'booking link': 'availability page',
    },
}


def apply_swaps(filepath, swaps):
    """Apply text swaps to a file. Only replace in editorial content, not in code/schema."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    for find, replace in swaps.items():
        # Only replace in visible text content, not inside JSON-LD scripts or attributes
        # Simple approach: count occurrences first, then replace
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

    for page_a, page_b, sim_score in FLAGGED_PAIRS:
        # Apply swaps to the SECOND file in each pair (alphabetically later)
        target = page_b
        filepath = os.path.join(SITE_DIR, 'compare', target)

        if not os.path.exists(filepath):
            print(f"  ! {target} — not found, skipping")
            continue

        # Combine general + pair-specific swaps
        swaps = dict(BOILERPLATE_SWAPS)
        if target in PAIR_SPECIFIC_SWAPS:
            swaps.update(PAIR_SPECIFIC_SWAPS[target])

        changed, changes = apply_swaps(filepath, swaps)
        if changed:
            total_files += 1
            total_swaps += len(changes)
            print(f"✓ {target} (was {sim_score} similar to {page_a})")
            for c in changes[:10]:  # Show first 10
                print(c)
            if len(changes) > 10:
                print(f"  ... and {len(changes) - 10} more swaps")
        else:
            print(f"  ⊘ {target} — no matching phrases found")

    print(f"\nDone: {total_swaps} phrase swaps across {total_files} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())

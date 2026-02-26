#!/usr/bin/env python3
"""
Remove AggregateRating from SoftwareApplication schema in tool review njk files.
Google's guidelines: AggregateRating should only be used for ratings collected
on your own site, not for third-party platform ratings.
"""

import re
import os

TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tools')

# The 15 held tool reviews with third-party AggregateRating schema
TARGET_FILES = [
    '11x-review.njk',
    'artisan-review.njk',
    'chili-piper-review.njk',
    'clari-review.njk',
    'cognism-review.njk',
    'highspot-review.njk',
    'leadiq-review.njk',
    'lusha-review.njk',
    'mindtickle-review.njk',
    'nooks-review.njk',
    'orum-review.njk',
    'regie-review.njk',
    'seismic-review.njk',
    'vidyard-review.njk',
    'warmly-review.njk',
]

# Pattern to match aggregateRating block inside JSON-LD
# Handles both multi-line and single-line formats
AGGREGATE_RATING_PATTERN = re.compile(
    r',?\s*"aggregateRating"\s*:\s*\{[^}]*\}',
    re.DOTALL | re.IGNORECASE
)

fixed = 0
skipped = 0
errors = 0

for filename in TARGET_FILES:
    filepath = os.path.join(TOOLS_DIR, filename)
    if not os.path.exists(filepath):
        print(f'  SKIP (not found): {filename}')
        skipped += 1
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '"aggregateRating"' not in content:
        print(f'  SKIP (no AggregateRating): {filename}')
        skipped += 1
        continue

    # Remove the aggregateRating block
    new_content = AGGREGATE_RATING_PATTERN.sub('', content)

    if new_content == content:
        print(f'  WARN (pattern did not match): {filename}')
        errors += 1
        continue

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  FIXED: {filename}')
    fixed += 1

print(f'\nDone: {fixed} fixed, {skipped} skipped, {errors} errors')

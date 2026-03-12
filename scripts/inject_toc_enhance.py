#!/usr/bin/env python3
"""Inject mobile TOC HTML, CSS link, and JS script into all review pages."""

import os
import re

TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')

REVIEW_FILES = [
    'aircall-review.html', 'apollo-review.html', 'calendly-review.html',
    'chili-piper-review.html', 'chorus-review.html', 'clari-review.html',
    'clay-review.html', 'clearbit-review.html', 'close-review.html',
    'dialpad-review.html', 'fireflies-review.html', 'freshsales-review.html',
    'gong-review.html', 'hubspot-review.html', 'hunter-review.html',
    'instantly-review.html', 'justcall-review.html', 'kixie-review.html',
    'lavender-review.html', 'lemlist-review.html', 'lusha-review.html',
    'mailshake-review.html', 'orum-review.html', 'outreach-review.html',
    'pipedrive-review.html', 'reply-io-review.html', 'salesloft-review.html',
    'savvycal-review.html', 'seamless-ai-review.html', 'smartlead-review.html',
    'vidyard-review.html', 'woodpecker-review.html', 'zoominfo-review.html',
]

MOBILE_TOC_HTML = '''
    <div class="mobile-toc">
      <button class="mobile-toc__toggle" aria-expanded="false" aria-controls="mobile-toc-list">
        <span>On This Page</span>
        <svg class="mobile-toc__chevron" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6l4 4 4-4"/></svg>
      </button>
      <nav class="mobile-toc__list" id="mobile-toc-list">
        <a href="#overview">Overview</a>
        <a href="#features">Key Features</a>
        <a href="#pricing">Pricing</a>
        <a href="#pros-cons">Pros &amp; Cons</a>
        <a href="#who-its-for">Who It&#39;s For</a>
        <a href="#verdict">Final Verdict</a>
      </nav>
    </div>
'''

CSS_LINK = '  <link rel="stylesheet" href="../css/toc-enhance.css">'
JS_SCRIPT = '  <script src="../js/toc-enhance.js" defer></script>'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 1. Add CSS link in <head> (before </head>)
    if 'toc-enhance.css' not in content:
        content = content.replace('</head>', CSS_LINK + '\n</head>')
        modified = True

    # 2. Add JS before </body>
    if 'toc-enhance.js' not in content:
        content = content.replace('</body>', JS_SCRIPT + '\n</body>')
        modified = True

    # 3. Insert mobile TOC after the review-hero closing div, before the next section
    if 'mobile-toc' not in content:
        # Find the closing </div> of review-hero followed by content before next section
        # The review-hero div ends with </div> then whitespace then <section
        # We need to insert after the review-hero closing tag
        # Match the closing </div> of review-hero followed by the first <section
        # Some files have a blank line between, some don't
        pattern = r'(    </div>\n)(\s*<section class="review-section")'
        match = re.search(pattern, content)
        if match:
            content = content[:match.end(1)] + MOBILE_TOC_HTML + '\n' + content[match.start(2):]
            modified = True
        else:
            print(f'  WARNING: Could not find insertion point in {os.path.basename(filepath)}')

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  Updated: {os.path.basename(filepath)}')
    else:
        print(f'  Skipped (already has TOC enhance): {os.path.basename(filepath)}')

def main():
    count = 0
    for fname in REVIEW_FILES:
        filepath = os.path.join(TOOLS_DIR, fname)
        if not os.path.exists(filepath):
            print(f'  MISSING: {fname}')
            continue
        process_file(filepath)
        count += 1
    print(f'\nProcessed {count} files.')

if __name__ == '__main__':
    main()

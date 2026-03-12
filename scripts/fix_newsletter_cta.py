#!/usr/bin/env python3
"""Fix newsletter CTA sections on alternatives and category pages."""
import re
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pages = [
    "alternatives/salesforce.html", "alternatives/hubspot-crm.html",
    "alternatives/zoominfo.html", "alternatives/apollo.html",
    "alternatives/clay.html", "alternatives/outreach.html",
    "alternatives/salesloft.html", "alternatives/instantly.html",
    "alternatives/gong.html", "alternatives/calendly.html",
    "categories/cold-outreach.html", "categories/lead-prospecting.html",
    "categories/data-enrichment.html", "categories/conversation-intelligence.html",
    "categories/sales-engagement.html", "categories/crm-pipeline.html",
    "categories/sales-content.html", "categories/sales-analytics.html",
    "categories/dialers-calling.html", "categories/meeting-schedulers.html",
]

REPLACEMENT = '''<div class="newsletter-cta">
<div class="newsletter-cta__inner">
  <h3 class="newsletter-cta__title">Get the inside take on AI sales tools</h3>
  <p class="newsletter-cta__desc">Weekly pricing changes, new feature drops, and honest tool assessments from someone who actually uses them. No spam, unsubscribe anytime.</p>
  <form class="newsletter-cta__form" action="#" method="post" data-newsletter>
    <input type="email" class="newsletter-cta__input" placeholder="you@company.com" required aria-label="Email address">
    <button type="submit" class="newsletter-cta__btn">Subscribe \u2192</button>
  </form>
  <p class="newsletter-cta__fine">Join 2,000+ sales professionals. Read our <a href="/privacy">privacy policy</a>.</p>
</div>
</div>'''

# Match the entire <section class="newsletter-cta">...</section> block
pattern = re.compile(
    r'<section\s+class="newsletter-cta">\s*.*?</section>',
    re.DOTALL
)

changed = 0
for page in pages:
    filepath = os.path.join(base_dir, page)
    if not os.path.exists(filepath):
        print(f"  MISSING: {page}")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = pattern.search(content)
    if not match:
        print(f"  NO MATCH: {page}")
        continue

    new_content = content[:match.start()] + REPLACEMENT + content[match.end():]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    changed += 1
    print(f"  FIXED: {page}")

print(f"\nDone. Fixed: {changed}/{len(pages)}")

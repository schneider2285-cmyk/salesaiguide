#!/usr/bin/env python3
"""Inject newsletter CTA into review pages, pricing pages, and homepage."""

import os
import re
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEWSLETTER_HTML = '''<div class="newsletter-cta">
  <div class="newsletter-cta__inner">
    <h3 class="newsletter-cta__title">Get the inside take on AI sales tools</h3>
    <p class="newsletter-cta__desc">Weekly pricing changes, new feature drops, and honest tool assessments from someone who actually uses them. No spam, unsubscribe anytime.</p>
    <form class="newsletter-cta__form" action="#" method="post" data-newsletter>
      <input type="email" class="newsletter-cta__input" placeholder="you@company.com" required aria-label="Email address">
      <button type="submit" class="newsletter-cta__btn">Subscribe &rarr;</button>
    </form>
    <p class="newsletter-cta__fine">Join 2,000+ sales professionals. Read our <a href="/privacy">privacy policy</a>.</p>
  </div>
</div>'''

CSS_LINK_REVIEW = '<link rel="stylesheet" href="../css/newsletter.css">'
CSS_LINK_HOME = '<link rel="stylesheet" href="css/newsletter.css">'

def already_has_newsletter(content):
    return 'newsletter-cta' in content

def inject_css_link(content, css_link):
    """Inject newsletter.css link after the last existing CSS link in head."""
    if 'newsletter.css' in content:
        return content
    # Find last <link rel="stylesheet"> in the <head>
    head_end = content.find('</head>')
    if head_end == -1:
        return content
    head_section = content[:head_end]
    # Find last stylesheet link
    matches = list(re.finditer(r'<link\s+rel="stylesheet"[^>]*>', head_section))
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        content = content[:insert_pos] + '\n' + css_link + content[insert_pos:]
    return content

def process_review_pages():
    """Inject newsletter CTA into all 33 review pages after #verdict section."""
    review_files = sorted(glob.glob(os.path.join(BASE, 'tools', '*-review.html')))
    count = 0
    for filepath in review_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if already_has_newsletter(content):
            print(f"  SKIP (already has newsletter): {os.path.basename(filepath)}")
            continue

        # Strategy: Insert newsletter CTA after the verdict section's closing content
        # Look for the "Further reading" paragraph or cross-links that come after verdict
        # Pattern: find the verdict section content end, insert before further-reading/cross-links

        # Try to find "Further reading" or similar cross-link section after verdict
        # In review pages, the pattern is: verdict section content, then a <p> with "Further reading" or cross-links

        # Look for patterns like:
        # 1. <p class="further-reading"> or <p><strong>Further reading
        # 2. <div class="cross-links"> or similar
        # 3. After the verdict-box closing div

        modified = False

        # Pattern 1: Insert before "Further reading" paragraph
        further_reading_match = re.search(r'(\n\s*<p[^>]*>(?:<strong>)?(?:Further reading|Related|Read more|See also))', content, re.IGNORECASE)
        if further_reading_match:
            insert_pos = further_reading_match.start()
            content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + content[insert_pos:]
            modified = True

        if not modified:
            # Pattern 2: Insert after the verdict-box div
            verdict_match = re.search(r'(class="verdict-box"[^>]*>.*?</div>\s*</div>)', content, re.DOTALL)
            if verdict_match:
                insert_pos = verdict_match.end()
                content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + content[insert_pos:]
                modified = True

        if not modified:
            # Pattern 3: Insert before closing </section> of verdict section
            verdict_section = re.search(r'id="verdict"', content)
            if verdict_section:
                # Find the next </section> after verdict
                section_close = content.find('</section>', verdict_section.end())
                if section_close != -1:
                    content = content[:section_close] + '\n\n' + NEWSLETTER_HTML + '\n' + content[section_close:]
                    modified = True

        if not modified:
            # Fallback: Insert before the footer
            footer_match = re.search(r'(\n\s*<footer)', content)
            if footer_match:
                insert_pos = footer_match.start()
                content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + '\n' + content[insert_pos:]
                modified = True

        if modified:
            content = inject_css_link(content, CSS_LINK_REVIEW)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            print(f"  OK: {os.path.basename(filepath)}")
        else:
            print(f"  WARN: Could not find insertion point in {os.path.basename(filepath)}")

    return count

def process_pricing_pages():
    """Inject newsletter CTA into all 10 pricing pages at end of article before sources."""
    pricing_dir = os.path.join(BASE, 'pricing')
    if not os.path.isdir(pricing_dir):
        print("  No pricing directory found")
        return 0

    pricing_files = sorted(glob.glob(os.path.join(pricing_dir, '*.html')))
    # Exclude index.html
    pricing_files = [f for f in pricing_files if not f.endswith('index.html')]
    count = 0

    for filepath in pricing_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if already_has_newsletter(content):
            print(f"  SKIP (already has newsletter): {os.path.basename(filepath)}")
            continue

        modified = False

        # Pattern 1: Insert before sources/references section
        sources_match = re.search(r'(\n\s*<(?:section|div|h[23])[^>]*(?:id="sources"|class="sources"|>Sources|>References))', content, re.IGNORECASE)
        if sources_match:
            insert_pos = sources_match.start()
            content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + content[insert_pos:]
            modified = True

        if not modified:
            # Pattern 2: Insert before closing </article> tag
            article_close = content.rfind('</article>')
            if article_close != -1:
                content = content[:article_close] + '\n\n' + NEWSLETTER_HTML + '\n' + content[article_close:]
                modified = True

        if not modified:
            # Pattern 3: Insert before footer
            footer_match = re.search(r'(\n\s*<footer)', content)
            if footer_match:
                insert_pos = footer_match.start()
                content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + '\n' + content[insert_pos:]
                modified = True

        if modified:
            content = inject_css_link(content, CSS_LINK_REVIEW)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            print(f"  OK: {os.path.basename(filepath)}")
        else:
            print(f"  WARN: Could not find insertion point in {os.path.basename(filepath)}")

    return count

def process_homepage():
    """Inject newsletter CTA into homepage after main tool listings."""
    filepath = os.path.join(BASE, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if already_has_newsletter(content):
        print("  SKIP (already has newsletter): index.html")
        return 0

    # Find the end of the featured-tools section
    # Look for closing </section> of id="featured-tools"
    featured_match = re.search(r'id="featured-tools"', content)
    if featured_match:
        # Find the closing </section> for this section
        # Count nested sections
        pos = featured_match.end()
        depth = 1
        while depth > 0 and pos < len(content):
            next_open = content.find('<section', pos)
            next_close = content.find('</section>', pos)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 8
            else:
                depth -= 1
                if depth == 0:
                    insert_pos = next_close + len('</section>')
                    content = content[:insert_pos] + '\n\n' + NEWSLETTER_HTML + '\n' + content[insert_pos:]
                    content = inject_css_link(content, CSS_LINK_HOME)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("  OK: index.html")
                    return 1
                pos = next_close + 10

    print("  WARN: Could not find insertion point in index.html")
    return 0

if __name__ == '__main__':
    print("=== Injecting Newsletter CTAs ===")
    print("\n--- Review Pages ---")
    review_count = process_review_pages()
    print(f"\n--- Pricing Pages ---")
    pricing_count = process_pricing_pages()
    print(f"\n--- Homepage ---")
    home_count = process_homepage()
    total = review_count + pricing_count + home_count
    print(f"\n=== Done: {total} pages updated ===")
    print(f"  Reviews: {review_count}, Pricing: {pricing_count}, Homepage: {home_count}")

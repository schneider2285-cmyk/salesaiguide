#!/usr/bin/env python3
"""Add missing cross-links between content types (v2).

HIGHEST IMPACT SEO optimization: connects reviews, comparisons, category hubs,
and best-for pages with reciprocal internal links.

Sub-tasks:
  B1. Review pages  → alternatives + best-for links
  B2. Comparison pages → alternatives links
  B3. Category hubs → best-for pill links
  B4. Broken link fix (apollo-vs-hunter → hunter-vs-apollo)

Also updates dateModified in JSON-LD for every page that receives new links.
"""

import os
import re
import glob

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-03-10"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

TOOL_CATEGORY = {
    "aircall": "dialers-calling", "apollo": "lead-prospecting", "calendly": "meeting-schedulers",
    "chili-piper": "meeting-schedulers", "chorus": "conversation-intelligence", "clari": "sales-analytics",
    "clay": "data-enrichment", "clearbit": "data-enrichment", "close": "crm-pipeline",
    "cognism": "lead-prospecting", "dialpad": "dialers-calling", "fireflies": "conversation-intelligence",
    "freshsales": "crm-pipeline", "gong": "conversation-intelligence", "hubspot": "crm-pipeline",
    "hunter": "lead-prospecting", "instantly": "cold-outreach", "justcall": "dialers-calling",
    "kixie": "dialers-calling", "klenty": "cold-outreach", "lavender": "sales-content",
    "lemlist": "cold-outreach", "lusha": "lead-prospecting", "mailshake": "cold-outreach",
    "mixmax": "sales-engagement", "orum": "dialers-calling", "outreach": "sales-engagement",
    "pipedrive": "crm-pipeline", "reply-io": "cold-outreach", "ringcentral": "dialers-calling",
    "salesloft": "sales-engagement", "savvycal": "meeting-schedulers", "seamless-ai": "lead-prospecting",
    "smartlead": "cold-outreach", "vidyard": "sales-content", "woodpecker": "cold-outreach",
    "zoominfo": "lead-prospecting",
}

TOOL_NAMES = {
    "aircall": "Aircall", "apollo": "Apollo.io", "calendly": "Calendly",
    "chili-piper": "Chili Piper", "chorus": "Chorus.ai", "clari": "Clari",
    "clay": "Clay", "clearbit": "Clearbit", "close": "Close",
    "cognism": "Cognism", "dialpad": "Dialpad", "fireflies": "Fireflies.ai",
    "freshsales": "Freshsales", "gong": "Gong", "hubspot": "HubSpot",
    "hunter": "Hunter.io", "instantly": "Instantly.ai", "justcall": "JustCall",
    "kixie": "Kixie", "klenty": "Klenty", "lavender": "Lavender",
    "lemlist": "Lemlist", "lusha": "Lusha", "mailshake": "Mailshake",
    "mixmax": "Mixmax", "orum": "Orum", "outreach": "Outreach",
    "pipedrive": "Pipedrive", "reply-io": "Reply.io", "ringcentral": "RingCentral",
    "salesloft": "Salesloft", "savvycal": "SavvyCal", "seamless-ai": "Seamless.AI",
    "smartlead": "Smartlead", "vidyard": "Vidyard", "woodpecker": "Woodpecker",
    "zoominfo": "ZoomInfo",
}

TOOL_ALTERNATIVES = {
    "apollo": "apollo.html", "calendly": "calendly.html",
    "clay": "clay.html", "close": "close.html",
    "gong": "gong.html", "hubspot": "hubspot-crm.html",
    "instantly": "instantly.html", "lemlist": "lemlist.html",
    "outreach": "outreach.html", "pipedrive": "pipedrive.html",
    "reply-io": "reply-io.html", "salesforce": "salesforce.html",
    "salesloft": "salesloft.html", "zoominfo": "zoominfo.html",
}

TOOL_BEST_FOR = {
    "aircall": ["dialer-software.html"],
    "apollo": ["lead-generation-tools.html", "ai-sales-tools.html",
               "sales-automation-software.html", "sales-tools-for-solopreneurs.html"],
    "chorus": ["conversation-intelligence-software.html"],
    "clay": ["lead-generation-tools.html", "ai-sales-tools.html"],
    "close": ["crm-for-small-business.html"],
    "dialpad": ["dialer-software.html"],
    "fireflies": ["conversation-intelligence-software.html"],
    "freshsales": ["crm-for-small-business.html", "free-crm-software.html"],
    "gong": ["conversation-intelligence-software.html", "ai-sales-tools.html"],
    "hubspot": ["crm-for-small-business.html", "free-crm-software.html",
                "sales-automation-software.html"],
    "hunter": ["sales-tools-for-solopreneurs.html", "lead-generation-tools.html"],
    "instantly": ["cold-email-software-for-startups.html", "ai-sales-tools.html",
                  "sales-automation-software.html", "sales-tools-for-solopreneurs.html"],
    "justcall": ["dialer-software.html"],
    "kixie": ["dialer-software.html"],
    "lavender": ["ai-sales-tools.html"],
    "lemlist": ["cold-email-software-for-startups.html"],
    "lusha": ["lead-generation-tools.html"],
    "orum": ["dialer-software.html"],
    "outreach": ["sales-automation-software.html"],
    "pipedrive": ["crm-for-small-business.html", "sales-tools-for-solopreneurs.html"],
    "reply-io": ["sales-automation-software.html"],
    "smartlead": ["cold-email-software-for-startups.html"],
    "woodpecker": ["cold-email-software-for-startups.html"],
    "zoominfo": ["lead-generation-tools.html"],
}

BEST_FOR_LABELS = {
    "ai-sales-tools.html": "AI sales tools",
    "cold-email-software-for-startups.html": "cold email software",
    "conversation-intelligence-software.html": "conversation intelligence",
    "crm-for-small-business.html": "CRM for small business",
    "dialer-software.html": "dialer software",
    "free-crm-software.html": "free CRM",
    "lead-generation-tools.html": "lead generation tools",
    "sales-automation-software.html": "sales automation",
    "sales-tools-for-solopreneurs.html": "tools for solopreneurs",
}

CATEGORY_BEST_FOR = {
    "cold-outreach": ["cold-email-software-for-startups.html"],
    "lead-prospecting": ["lead-generation-tools.html"],
    "crm-pipeline": ["crm-for-small-business.html", "free-crm-software.html"],
    "conversation-intelligence": ["conversation-intelligence-software.html"],
    "dialers-calling": ["dialer-software.html"],
    "sales-engagement": ["sales-automation-software.html"],
}

CATEGORY_NAMES = {
    "cold-outreach": "Cold Outreach", "conversation-intelligence": "Conversation Intelligence",
    "crm-pipeline": "CRM & Pipeline", "data-enrichment": "Data Enrichment",
    "dialers-calling": "Dialers & Calling", "lead-prospecting": "Lead Prospecting",
    "meeting-schedulers": "Meeting Schedulers", "sales-analytics": "Sales Analytics",
    "sales-content": "Sales Content", "sales-engagement": "Sales Engagement",
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def update_date_modified(content):
    """Update dateModified in JSON-LD script blocks to TODAY."""
    return re.sub(
        r'("dateModified"\s*:\s*")(\d{4}-\d{2}-\d{2})(")',
        rf'\g<1>{TODAY}\3',
        content,
    )


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# B1  Review pages → alternatives + best-for links
# ---------------------------------------------------------------------------

def fix_review_page(filepath):
    """Add alternatives and best-for cross-links to a review page."""
    content = read_file(filepath)

    # Idempotency: skip if v2 marker already present
    if 'further-reading-v2' in content:
        return None

    slug = os.path.basename(filepath).replace("-review.html", "")
    name = TOOL_NAMES.get(slug, slug.replace("-", " ").title())

    new_sentences = []

    # Alternatives link
    if slug in TOOL_ALTERNATIVES:
        alt_file = TOOL_ALTERNATIVES[slug]
        alt_href = f"../alternatives/{alt_file}"
        if alt_href not in content:
            new_sentences.append(
                f'Explore the top <a href="{alt_href}">{name} alternatives</a>.'
            )

    # Best-for links (limit to first 2 from the list, skip any already linked)
    if slug in TOOL_BEST_FOR:
        added = 0
        for bf_file in TOOL_BEST_FOR[slug][:2]:
            bf_href = f"../best/{bf_file}"
            if bf_href not in content:
                label = BEST_FOR_LABELS.get(bf_file, bf_file.replace(".html", "").replace("-", " "))
                new_sentences.append(
                    f'See {name} in our <a href="{bf_href}">best {label}</a> picks.'
                )
                added += 1

    if not new_sentences:
        return None

    added_text = " ".join(new_sentences)

    # Check for existing further-reading paragraph
    fr_pattern = re.compile(r'(<p\s+class="further-reading"[^>]*>)(.*?)(</p>)', re.DOTALL)
    match = fr_pattern.search(content)

    if match:
        # Append new sentences to existing paragraph, add v2 class marker
        existing_open = match.group(1)
        existing_body = match.group(2).rstrip()
        # Ensure separator
        if existing_body and not existing_body.endswith("."):
            existing_body += "."
        separator = " " if existing_body else ""
        new_open = existing_open.replace('class="further-reading"', 'class="further-reading further-reading-v2"')
        replacement = f'{new_open}{existing_body}{separator}{added_text}</p>'
        content = content[:match.start()] + replacement + content[match.end():]
    else:
        # Create new paragraph before </main> or </article>
        paragraph = f'    <p class="further-reading further-reading-v2">{added_text}</p>'
        for marker in ["  </main>", "</main>", "      </article>", "</article>"]:
            if marker in content:
                content = content.replace(marker, f"{paragraph}\n{marker}", 1)
                break

    content = update_date_modified(content)
    write_file(filepath, content)

    return added_text


# ---------------------------------------------------------------------------
# B2  Comparison pages → alternatives links
# ---------------------------------------------------------------------------

def fix_comparison_page(filepath):
    """Add alternatives cross-links to a comparison page."""
    content = read_file(filepath)

    # Skip if already has an editorial alternatives link (not the footer nav link)
    # Footer has href="/alternatives/" — we look for relative ../alternatives/ links
    if "../alternatives/" in content:
        return None

    base = os.path.basename(filepath).replace(".html", "")
    parts = base.split("-vs-")
    if len(parts) != 2:
        return None
    tool_a, tool_b = parts

    new_sentences = []

    for slug in [tool_a, tool_b]:
        if slug in TOOL_ALTERNATIVES:
            alt_file = TOOL_ALTERNATIVES[slug]
            name = TOOL_NAMES.get(slug, slug.replace("-", " ").title())
            new_sentences.append(
                f'See all <a href="../alternatives/{alt_file}">{name} alternatives</a>.'
            )

    if not new_sentences:
        return None

    added_text = " ".join(new_sentences)

    # Check for existing further-reading paragraph
    fr_pattern = re.compile(r'(<p\s+class="further-reading"[^>]*>)(.*?)(</p>)', re.DOTALL)
    match = fr_pattern.search(content)

    if match:
        existing_open = match.group(1)
        existing_body = match.group(2).rstrip()
        if existing_body and not existing_body.endswith("."):
            existing_body += "."
        separator = " " if existing_body else ""
        replacement = f'{existing_open}{existing_body}{separator}{added_text}</p>'
        content = content[:match.start()] + replacement + content[match.end():]
    else:
        # Create new paragraph before </article>
        paragraph = f'      <p class="further-reading">{added_text}</p>'
        for marker in ["      </article>", "</article>"]:
            if marker in content:
                content = content.replace(marker, f"{paragraph}\n{marker}", 1)
                break

    content = update_date_modified(content)
    write_file(filepath, content)

    return added_text


# ---------------------------------------------------------------------------
# B3  Category hubs → best-for pill links
# ---------------------------------------------------------------------------

def fix_category_hub(filepath):
    """Add best-for pill links to a category hub page."""
    content = read_file(filepath)

    slug = os.path.basename(filepath).replace(".html", "")

    # Only process categories that have best-for mappings
    if slug not in CATEGORY_BEST_FOR:
        return None

    # Idempotency: skip if already has best picks guides section
    # (Note: footer has "Best Picks" text — we check for the specific heading)
    if "Best Picks Guides" in content:
        return None

    best_for_pages = CATEGORY_BEST_FOR[slug]

    # Build pill links
    pills = []
    for bf_file in best_for_pages:
        label = BEST_FOR_LABELS.get(bf_file, bf_file.replace(".html", "").replace("-", " "))
        # Capitalize first letter of label for pill display
        display_label = label[0].upper() + label[1:] if label else label
        pills.append(
            f'        <a href="../best/{bf_file}" style="display: inline-block; padding: .4em 1em; '
            f'border: 1px solid var(--color-accent); border-radius: var(--radius-full); '
            f'font-size: var(--text-sm); color: var(--color-accent); text-decoration: none; '
            f'background: var(--color-accent-highlight); transition: all var(--transition-interactive);">'
            f'{display_label} &rarr;</a>'
        )

    heading = (
        '    <p style="font-size: var(--text-xs); font-weight: 700; text-transform: uppercase; '
        'letter-spacing: .08em; color: var(--color-accent); margin-bottom: var(--space-2); '
        'margin-top: var(--space-4);">Best Picks Guides</p>'
    )
    pills_div = '    <div style="display: flex; flex-wrap: wrap; gap: var(--space-2);">\n'
    pills_div += "\n".join(pills)
    pills_div += "\n    </div>"

    best_picks_block = f"{heading}\n{pills_div}"

    # Strategy: insert after the last </div> inside the Related Categories section,
    # right before the closing </div>\n</section> of that section.
    # Look for "Alternatives Guides" section end first; if present, insert after its closing div.
    # If no Alternatives Guides, insert after the category pills div.

    # Find the Related Categories section
    rc_idx = content.find("Related Categories")
    if rc_idx == -1:
        return None

    # Find the </section> that closes the Related Categories block
    section_close_idx = content.find("</section>", rc_idx)
    if section_close_idx == -1:
        return None

    # Find the </div> for the container, which is just before </section>
    # We need to insert before "  </div>\n</section>" at the Related Categories section end
    container_close = content.rfind("  </div>", rc_idx, section_close_idx)
    if container_close == -1:
        return None

    # Insert the best picks block before the container's closing </div>
    content = content[:container_close] + best_picks_block + "\n" + content[container_close:]

    content = update_date_modified(content)
    write_file(filepath, content)

    labels = [BEST_FOR_LABELS.get(p, p) for p in best_for_pages]
    return f"best-for pills: {', '.join(labels)}"


# ---------------------------------------------------------------------------
# B4  Broken link fix
# ---------------------------------------------------------------------------

def fix_broken_links():
    """Fix apollo-vs-hunter.html → hunter-vs-apollo.html in best/lead-generation-tools.html."""
    filepath = os.path.join(SITE_DIR, "best", "lead-generation-tools.html")
    if not os.path.exists(filepath):
        return 0

    content = read_file(filepath)
    if "apollo-vs-hunter.html" not in content:
        return 0

    new_content = content.replace("apollo-vs-hunter.html", "hunter-vs-apollo.html")
    if new_content != content:
        write_file(filepath, new_content)
        count = content.count("apollo-vs-hunter.html")
        return count
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    tools_dir = os.path.join(SITE_DIR, "tools")
    compare_dir = os.path.join(SITE_DIR, "compare")
    categories_dir = os.path.join(SITE_DIR, "categories")

    total_files = 0
    total_links = 0

    # --- B1: Review pages → alternatives + best-for ---
    print("=== B1: Review pages → alternatives + best-for ===")
    review_files = sorted(glob.glob(os.path.join(tools_dir, "*-review.html")))
    b1_count = 0
    for fp in review_files:
        result = fix_review_page(fp)
        if result:
            rel = os.path.relpath(fp, SITE_DIR)
            # Count new links added
            link_count = result.count("<a ")
            total_links += link_count
            print(f"  \u2713 {rel}  (+{link_count} links: {_summarize(result)})")
            b1_count += 1
            total_files += 1
    print(f"  {b1_count} review pages updated\n")

    # --- B2: Comparison pages → alternatives ---
    print("=== B2: Comparison pages → alternatives ===")
    compare_files = sorted(glob.glob(os.path.join(compare_dir, "*-vs-*.html")))
    b2_count = 0
    for fp in compare_files:
        result = fix_comparison_page(fp)
        if result:
            rel = os.path.relpath(fp, SITE_DIR)
            link_count = result.count("<a ")
            total_links += link_count
            print(f"  \u2713 {rel}  (+{link_count} links: {_summarize(result)})")
            b2_count += 1
            total_files += 1
    print(f"  {b2_count} comparison pages updated\n")

    # --- B3: Category hubs → best-for ---
    print("=== B3: Category hubs → best-for pills ===")
    cat_files = sorted(glob.glob(os.path.join(categories_dir, "*.html")))
    b3_count = 0
    for fp in cat_files:
        if os.path.basename(fp) == "index.html":
            continue
        result = fix_category_hub(fp)
        if result:
            rel = os.path.relpath(fp, SITE_DIR)
            link_count = result.count(",") + 1  # count of pills
            total_links += link_count
            print(f"  \u2713 {rel}  ({result})")
            b3_count += 1
            total_files += 1
    print(f"  {b3_count} category hubs updated\n")

    # --- B4: Broken link fix ---
    print("=== B4: Broken link fix ===")
    fixed = fix_broken_links()
    if fixed:
        print(f"  \u2713 best/lead-generation-tools.html  (fixed {fixed} broken links: apollo-vs-hunter → hunter-vs-apollo)")
        total_files += 1
    else:
        print("  (no broken links found or already fixed)")
    print()

    # --- Summary ---
    print(f"Total: {total_files} files updated, ~{total_links} new internal links added")


def _summarize(html_text):
    """Extract a short summary of what links were added from the HTML sentence(s)."""
    links = re.findall(r'href="[^"]*?/([^/"]+)"', html_text)
    if len(links) <= 3:
        return ", ".join(links)
    return f"{', '.join(links[:3])}... +{len(links)-3} more"


if __name__ == "__main__":
    main()

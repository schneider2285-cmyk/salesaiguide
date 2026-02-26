#!/usr/bin/env python3
"""
Fix internal linking gaps in tool review JSON data files.
Adds missing compare page links to competitorTable.seeFullLinks
and missing alternatives page links to the dm-alternatives section.

Run after: npm run build (to verify links are rendered)
"""

import json, os, re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
COMPARE_DIR = BASE_DIR / "compare"
ALTERNATIVES_DIR = BASE_DIR / "alternatives"
TOOL_DATA_DIR = BASE_DIR / "_data" / "tools"

def get_tool_label(slug):
    """Convert slug to display name."""
    label_map = {
        "11x": "11x",
        "apollo": "Apollo",
        "artisan": "Artisan",
        "chili-piper": "Chili Piper",
        "clari": "Clari",
        "clay": "Clay",
        "cognism": "Cognism",
        "gong": "Gong",
        "highspot": "Highspot",
        "hubspot": "HubSpot",
        "instantly": "Instantly",
        "lavender": "Lavender",
        "leadiq": "LeadIQ",
        "lemlist": "Lemlist",
        "lusha": "Lusha",
        "mindtickle": "Mindtickle",
        "nooks": "Nooks",
        "orum": "Orum",
        "outreach": "Outreach",
        "regie": "Regie.ai",
        "reply": "Reply.io",
        "saleshandy": "Saleshandy",
        "salesloft": "Salesloft",
        "seismic": "Seismic",
        "smartlead": "Smartlead",
        "vidyard": "Vidyard",
        "warmly": "Warmly",
        "zoominfo": "ZoomInfo",
        "fireflies": "Fireflies.ai",
        "justcall": "JustCall",
        "woodpecker": "Woodpecker",
        "avoma": "Avoma",
        "chorus": "Chorus",
        "aviso": "Aviso",
        "clearbit": "Clearbit",
        "autobound": "Autobound",
        "mailshake": "Mailshake",
        "klenty": "Klenty",
        "showpad": "Showpad",
        "allego": "Allego",
        "loom": "Loom",
        "heygen": "HeyGen",
        "leadfeeder": "Leadfeeder",
        "monday-crm": "Monday CRM",
        "salesforce": "Salesforce",
        "pipedrive": "Pipedrive",
        "agent-frank": "Agent Frank",
        "aisdr": "AiSDR",
        "6sense": "6sense",
        "bombora": "Bombora",
        "usergems": "UserGems",
        "second-nature": "Second Nature",
        "hyperbound": "Hyperbound",
        "boostup": "BoostUp",
    }
    return label_map.get(slug, slug.replace("-", " ").title())

def make_compare_label(slug1, slug2):
    """Make a human-readable compare label."""
    return f"{get_tool_label(slug1)} vs {get_tool_label(slug2)}"

def main():
    # Build compare map: tool_slug -> [(url, label)]
    compare_files = [f for f in os.listdir(COMPARE_DIR) 
                     if f.endswith('.njk') and f != 'index.njk']
    tool_compare_map = {}  # tool_slug -> [(url, label)]

    for f in compare_files:
        url = '/compare/' + f.replace('.njk', '.html')
        m = re.match(r'(.+)-vs-(.+)\.njk', f)
        if m:
            t1, t2 = m.group(1), m.group(2)
            label = make_compare_label(t1, t2)
            tool_compare_map.setdefault(t1, []).append({"url": url, "text": label})
            tool_compare_map.setdefault(t2, []).append({"url": url, "text": label})

    # Build alternatives map: tool_slug -> url
    alternatives_files = [f for f in os.listdir(ALTERNATIVES_DIR) if f.endswith('.njk')]
    tool_alternatives_map = {}
    for f in alternatives_files:
        slug = f.replace('-alternatives.njk', '')
        url = '/alternatives/' + f.replace('.njk', '.html')
        tool_alternatives_map[slug] = url

    # Process each tool data file
    tool_files = [f for f in os.listdir(TOOL_DATA_DIR) if f.endswith('.json')]
    fixed_count = 0
    link_count = 0

    for tf in sorted(tool_files):
        slug = tf.replace('.json', '')
        filepath = TOOL_DATA_DIR / tf

        with open(filepath) as f:
            data = json.load(f)

        changed = False

        # Fix compare links in competitorTable.seeFullLinks
        if 'competitorTable' in data:
            existing_urls = {l['url'] for l in data['competitorTable'].get('seeFullLinks', [])}
            all_compare_links = tool_compare_map.get(slug, [])
            
            for link in all_compare_links:
                if link['url'] not in existing_urls:
                    data['competitorTable'].setdefault('seeFullLinks', []).append(link)
                    existing_urls.add(link['url'])
                    changed = True
                    link_count += 1
                    print(f"  [{slug}] Added compare link: {link['url']}")

        # Fix alternatives link in dm-alternatives section
        alt_url = tool_alternatives_map.get(slug)
        if alt_url:
            # Check if alternatives URL is already referenced anywhere in the data
            data_str = json.dumps(data)
            if alt_url not in data_str:
                # Add to decisionModule.alternatives if it exists
                if 'decisionModule' in data and 'alternatives' in data['decisionModule']:
                    alts = data['decisionModule']['alternatives']
                    if 'seeAllUrl' not in alts:
                        alts['seeAllUrl'] = alt_url
                        alts['seeAllText'] = f"See all {get_tool_label(slug)} alternatives →"
                        changed = True
                        link_count += 1
                        print(f"  [{slug}] Added alternatives link: {alt_url}")

        if changed:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
            fixed_count += 1

    print(f"\nDone: {fixed_count} files updated, {link_count} links added")

if __name__ == "__main__":
    main()

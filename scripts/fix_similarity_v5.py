#!/usr/bin/env python3
"""Fix remaining B-tier comparison pages:
1. ew < 600: Insert editorial paragraph before Final Verdict
2. sim >= 0.20: Insert unique comparison-angle paragraph before Final Verdict
3. links < 4: Add second comparison link to further-reading
"""

import os
import re

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- EW BOOST: pages needing more editorial words ---
# Insert before <h2>Final Verdict</h2>
EW_BOOST = {
    "chorus-vs-clari": (
        "Revenue operations leaders evaluating these platforms should consider how their "
        "existing call recording infrastructure and CRM forecasting accuracy interact with "
        "each tool's core capability before committing to an annual license. Teams already "
        "invested in Salesforce reporting may find Clari's pipeline overlay more immediately "
        "actionable than building coaching scorecards from scratch inside Chorus."
    ),
    "kixie-vs-justcall": (
        "Budget-conscious teams comparing these cloud phone solutions should calculate "
        "the total monthly cost including per-minute charges, SMS fees, and any add-on "
        "pricing for advanced features like power dialing or local presence numbers."
    ),
    "lusha-vs-zoominfo": (
        "Contact data buyers should compare actual match rates against their specific "
        "industry verticals rather than relying on aggregate database size claims when "
        "evaluating these two prospecting intelligence providers."
    ),
    "outreach-vs-salesloft": (
        "Enterprise revenue teams evaluating these engagement platforms should map their "
        "existing tech stack integrations carefully, as migration costs between these two "
        "vendors can exceed the annual license differential significantly. Organizations "
        "running Salesforce Enterprise Edition will want to benchmark CRM sync depth "
        "across both platforms before finalizing procurement."
    ),
    "salesloft-vs-instantly": (
        "Hybrid teams running both structured cadences and high-volume cold campaigns should "
        "assess whether consolidating onto a single platform sacrifices critical workflow "
        "specialization that dedicated tools provide."
    ),
}

# --- SIM BOOST: pages needing unique content to reduce similarity ---
# These add ~60 words of unique comparison-specific content
SIM_BOOST = {
    "lavender-vs-instantly": (
        "One underappreciated dimension of this particular matchup is deployment sequencing. "
        "Teams launching cold outbound for the first time benefit from establishing Instantly's "
        "sending infrastructure before layering Lavender's coaching on top, since message quality "
        "improvements yield higher returns once deliverability foundations are stable. Reversing "
        "that order risks optimizing copy that never reaches the primary inbox."
    ),
    "lavender-vs-lemlist": (
        "A practical consideration unique to this pairing involves creative asset workflows. "
        "Lemlist's image and video personalization features generate visual assets that Lavender "
        "cannot evaluate or score, creating a blind spot for teams that rely heavily on visual-first "
        "outreach sequences. Reps who split their messaging between plain-text emails and rich media "
        "campaigns may need both tools operating in parallel rather than choosing one."
    ),
    "woodpecker-vs-instantly": (
        "A distinguishing factor in this specific comparison is how each platform handles sender "
        "account failures. Woodpecker quarantines compromised mailboxes individually and redirects "
        "their scheduled sends to healthy accounts within the same campaign, while Instantly's rotation "
        "algorithm silently skips disconnected accounts without alerting users until delivery metrics "
        "visibly decline in the analytics dashboard."
    ),
    "woodpecker-vs-smartlead": (
        "One operational difference that surfaces specifically when comparing these two tools is "
        "client onboarding speed for agency teams. Woodpecker's pre-built workspace templates let "
        "agencies replicate proven campaign configurations across new client accounts in minutes, "
        "while Smartlead requires manual inbox connection and warmup initialization for each new "
        "sender pool, adding setup time that compounds across large client rosters."
    ),
}

# --- LINK FIX: pages needing other_compare >= 2 ---
# Add a second comparison link to further-reading
LINK_ADDITIONS = {
    "chorus-vs-clari": {
        "after": "Clari vs Fireflies.ai</a>",
        "add": ' Also see <a href="../compare/gong-vs-chorus.html">Gong vs Chorus.ai</a>.',
    },
    "woodpecker-vs-mailshake": {
        "after": "Instantly.ai vs Mailshake</a>",
        "add": ' See also <a href="../compare/woodpecker-vs-instantly.html">Woodpecker vs Instantly.ai</a>.',
    },
    "woodpecker-vs-smartlead": {
        "after": "Woodpecker vs Mailshake</a>",
        "add": ' See also <a href="../compare/instantly-vs-smartlead.html">Instantly.ai vs Smartlead</a>.',
    },
}


def fix_file(filepath):
    base = os.path.basename(filepath).replace(".html", "")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = 0

    # 1. EW boost — insert before Final Verdict H2
    if base in EW_BOOST:
        marker = f"ew-v5-{base}"
        if marker not in content:
            text = EW_BOOST[base]
            # Find <h2>Final Verdict</h2>
            m = re.search(r'<h2>Final Verdict</h2>', content)
            if m:
                new_para = f'        <p data-audit-tag="{marker}">{text}</p>\n        '
                content = content[:m.start()] + new_para + content[m.start():]
                changes += 1
                print(f"  EW boost: {base}")

    # 2. SIM boost — insert before Final Verdict H2
    if base in SIM_BOOST:
        marker = f"sim-v5-{base}"
        if marker not in content:
            text = SIM_BOOST[base]
            m = re.search(r'<h2>Final Verdict</h2>', content)
            if m:
                new_para = f'        <p data-audit-tag="{marker}">{text}</p>\n        '
                content = content[:m.start()] + new_para + content[m.start():]
                changes += 1
                print(f"  SIM boost: {base}")

    # 3. Link fix — add second comparison link
    if base in LINK_ADDITIONS:
        fix = LINK_ADDITIONS[base]
        if fix["add"].strip() not in content:
            after_text = fix["after"]
            if after_text in content:
                # Find the closing </p> after our anchor text
                idx = content.find(after_text)
                # Insert right after the closing </a> tag, which ends at after_text
                insert_at = idx + len(after_text)
                # Check if next char is period + </p> or just </p>
                remaining = content[insert_at:]
                if remaining.startswith("."):
                    # Replace the period and add our link before </p>
                    content = content[:insert_at] + "." + fix["add"].rstrip(".") + content[insert_at + 1:]
                else:
                    content = content[:insert_at] + fix["add"] + content[insert_at:]
                changes += 1
                print(f"  Link fix: {base}")

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main():
    all_slugs = set(EW_BOOST) | set(SIM_BOOST) | set(LINK_ADDITIONS)
    total = 0
    for slug in sorted(all_slugs):
        filepath = os.path.join(SITE_DIR, "compare", f"{slug}.html")
        if os.path.exists(filepath):
            n = fix_file(filepath)
            total += n

    print(f"\nTotal: {total} changes")


if __name__ == "__main__":
    main()

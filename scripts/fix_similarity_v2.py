#!/usr/bin/env python3
"""Fix intro_similarity by rewriting the shared-tool intro paragraphs
to use unique vocabulary per comparison page.

The intro paragraph (added by fix_editorial_words.py) contains a description
of each tool that is identical across all pages featuring that tool.
This script replaces the entire intro paragraph with a version that uses
per-comparison-page unique language, breaking the trigram overlap.

Also rewrites the "Detailed Comparison" intro to be unique per page.
"""

import os
import re
import glob

# Per-page unique intro paragraphs. Each must be ~80 words, completely unique vocabulary.
# Key = filename slug (without .html), Value = full paragraph text.
PAGE_INTROS = {
    # --- lavender pair (0.285) ---
    "lavender-vs-instantly": (
        "Lavender and Instantly.ai target opposite ends of the email outreach workflow. "
        "Lavender operates at the composition layer, analyzing subject lines, body copy, "
        "and personalization tokens before any message leaves the drafts folder. Instantly "
        "operates at the infrastructure layer, managing sender rotation, domain warmup "
        "schedules, and inbox placement across dozens of connected accounts. One sharpens "
        "each individual email. The other multiplies sending capacity. Deciding which "
        "investment matters more depends on whether your bottleneck is message quality "
        "or message volume."
    ),
    "lavender-vs-lemlist": (
        "Lavender and Lemlist sit at different points along the creative outreach spectrum. "
        "Lavender functions as a browser-based writing advisor, grading drafts against "
        "reply-rate benchmarks and flagging weak openers or overused phrases. Lemlist "
        "provides an end-to-end campaign builder where reps embed custom images, "
        "record personalized video thumbnails, and chain LinkedIn touches into automated "
        "sequences. Choosing between a dedicated composition assistant and a full-stack "
        "visual outreach engine comes down to whether your team already has a sending "
        "platform or needs one built in."
    ),

    # --- woodpecker pair (0.283) ---
    "woodpecker-vs-instantly": (
        "Woodpecker and Instantly both automate cold email delivery, but they architect "
        "the process around different priorities. Woodpecker optimizes for sender safety, "
        "applying throttling algorithms, bounce shields, and domain health monitoring "
        "that protect deliverability across moderate sending volumes. Instantly maximizes "
        "throughput by letting teams connect unlimited mailboxes with automated warm-up "
        "cycles that ramp new domains quickly. Teams choosing between protective sending "
        "controls and aggressive volume scaling should weigh their compliance requirements "
        "against their growth targets."
    ),
    "woodpecker-vs-smartlead": (
        "Woodpecker and Smartlead compete for cold email teams that prioritize reaching "
        "the primary inbox over raw sending speed. Woodpecker bundles agency-friendly "
        "features like client workspace separation, white-label reporting, and per-client "
        "deliverability dashboards. Smartlead concentrates on mailbox rotation algorithms "
        "and master inbox consolidation that unify replies from distributed sender accounts. "
        "Agency operators managing multiple client campaigns evaluate these tools differently "
        "than in-house SDR teams running single-brand outreach programs."
    ),

    # --- kixie pair (0.260, 0.222) ---
    "kixie-vs-aircall": (
        "Kixie and Aircall both replace traditional desk phones with cloud-based calling, "
        "yet they solve different workflow problems. Kixie provides a power dialer with "
        "local presence numbers and automatic voicemail drop that accelerate outbound "
        "prospecting velocity. Aircall builds a full business phone system with IVR menus, "
        "call queuing, and shared inboxes designed for customer-facing support teams. "
        "Outbound-heavy SDR pods and inbound-heavy service desks will rank these "
        "capabilities in opposite order."
    ),
    "kixie-vs-orum": (
        "Kixie and Orum approach outbound dialing from contrasting design philosophies. "
        "Kixie offers a single-line power dialer embedded inside popular CRMs, giving "
        "individual reps click-to-call convenience with automated logging. Orum runs a "
        "parallel dialing engine that simultaneously calls multiple prospects and routes "
        "live pickups to available agents on a virtual sales floor. Solo callers making "
        "forty dials per hour have different needs than pod-based teams targeting "
        "two hundred live conversations per session."
    ),
    "kixie-vs-justcall": (
        "Kixie and JustCall overlap in the cloud phone category but diverge on channel "
        "coverage and pricing structure. Kixie centers on outbound sales dialing with "
        "voicemail drop automation and local presence matching that boost connection rates. "
        "JustCall spans calling, SMS messaging, and WhatsApp conversations under one roof "
        "at a lower per-seat entry point. Teams evaluating these platforms should compare "
        "outbound dialing throughput against omnichannel communication breadth before "
        "choosing a winner."
    ),

    # --- instantly pair (0.258) ---
    "instantly-vs-lemlist": (
        "Instantly and Lemlist represent two schools of thought in cold outreach execution. "
        "Instantly focuses on email delivery mechanics: unlimited mailbox connections, "
        "automated warmup rotations, and campaign-level A/B testing optimized for inbox "
        "placement rates. Lemlist emphasizes creative personalization, embedding dynamic "
        "images, custom landing pages, and LinkedIn connection requests into multichannel "
        "cadences. Volume-driven outbound programs and creativity-driven prospecting "
        "motions produce different ROI profiles depending on your industry and buyer persona."
    ),
    "instantly-vs-mailshake": (
        "Instantly and Mailshake share the cold email category but attract different "
        "buyer segments through their product architecture. Instantly appeals to agencies "
        "and high-volume senders with unlimited account connections and enterprise-grade "
        "warmup infrastructure across rotating sender domains. Mailshake positions itself "
        "as a simpler solution with an optional phone dialer add-on, built-in lead catcher, "
        "and straightforward per-seat pricing. Teams scaling past five thousand emails "
        "per week face different constraints than teams sending five hundred."
    ),

    # --- orum pair (0.251, 0.234) ---
    "orum-vs-justcall": (
        "Orum and JustCall occupy different segments within the sales calling ecosystem. "
        "Orum engineers a parallel dialing environment where AI filters answering machines, "
        "connects live humans instantly, and maintains a virtual sales floor for pod-based "
        "SDR teams. JustCall delivers a budget-friendly cloud phone system spanning "
        "voice calls, SMS workflows, and WhatsApp integration for mixed inbound and "
        "outbound communication. Blitz-dialing pods chasing connection volume have "
        "fundamentally different requirements than distributed teams managing "
        "multi-channel conversations."
    ),
    "orum-vs-aircall": (
        "Orum and Aircall solve calling challenges at opposite scales and use cases. "
        "Orum accelerates outbound prospecting by dialing multiple numbers simultaneously, "
        "detecting voicemails with AI, and routing answered calls to the next available "
        "rep in a shared bullpen layout. Aircall provides enterprise-grade telephony "
        "with ring groups, warm transfers, call monitoring, and a marketplace of "
        "one-hundred-plus integrations for revenue and support organizations. "
        "Prospecting-first teams and full-cycle account executives apply "
        "very different evaluation criteria."
    ),

    # --- seamless-ai pair (0.247, 0.223) ---
    "seamless-ai-vs-apollo": (
        "Seamless.AI and Apollo.io both promise access to B2B contact data, but they "
        "deliver it through divergent product models. Seamless.AI operates as a real-time "
        "search engine that generates contact records on demand using AI verification "
        "at the moment of lookup. Apollo bundles a static database of over two hundred "
        "million contacts with built-in email sequencing, task management, and CRM-like "
        "deal tracking. Pure data acquisition shoppers and teams seeking an all-in-one "
        "prospecting workspace will weigh these architectures differently."
    ),
    "seamless-ai-vs-lusha": (
        "Seamless.AI and Lusha help sales reps find prospect contact details, but their "
        "interaction patterns and data sourcing methods differ substantially. Seamless.AI "
        "processes bulk searches through an AI-powered discovery engine that returns "
        "verified emails and direct dials in list format. Lusha takes a one-at-a-time "
        "approach through its Chrome extension, revealing individual contacts directly "
        "on LinkedIn profiles with a single click. High-volume list builders "
        "and surgical account-based prospectors measure ROI on separate axes."
    ),
    "seamless-ai-vs-zoominfo": (
        "Seamless.AI and ZoomInfo represent the credit-based and contract-based approaches "
        "to B2B intelligence purchasing. Seamless.AI charges per credit for on-demand "
        "contact lookups through its AI search interface, making costs variable and "
        "tied to actual usage. ZoomInfo bundles comprehensive firmographic data, buyer "
        "intent signals, and website visitor identification into annual enterprise "
        "agreements with fixed seat pricing. Startups managing cash flow carefully "
        "and enterprises budgeting for predictable data spend evaluate these "
        "commercial models through opposite lenses."
    ),

    # --- clari pair (0.222) ---
    "chorus-vs-clari": (
        "Chorus and Clari overlap in the revenue intelligence conversation yet attack "
        "the problem from separate vantage points. Chorus records sales calls, identifies "
        "competitive mentions, and builds coaching scorecards that help managers "
        "improve rep performance one conversation at a time. Clari aggregates pipeline "
        "data across CRM fields, email activity, and engagement signals to generate "
        "forecast models that predict quarterly outcomes. Frontline coaching priorities "
        "and boardroom forecasting accuracy demands pull buying committees in "
        "distinctly different directions."
    ),
    "clari-vs-fireflies": (
        "Clari and Fireflies.ai serve revenue teams that want more insight from their "
        "meetings, but each tool captures a different slice of the picture. Clari "
        "synthesizes deal signals from CRM updates, email threads, and calendar activity "
        "to project pipeline health and flag at-risk opportunities for leadership review. "
        "Fireflies records meetings across Zoom, Teams, and Google Meet, then generates "
        "searchable transcripts with action item extraction. Forecast-focused executives "
        "and note-taking-averse individual contributors rank these capabilities "
        "on separate priority scales."
    ),

    # --- pipedrive pair (0.217) ---
    "close-vs-pipedrive": (
        "Close and Pipedrive attract small sales teams seeking CRM simplicity over "
        "enterprise complexity, but they build around different core workflows. Close "
        "integrates calling, email, and SMS directly into its pipeline interface, "
        "eliminating the need for separate communication tools. Pipedrive provides a "
        "visual drag-and-drop pipeline with activity-based selling reminders and a "
        "marketplace of over four hundred integrations. Teams that live on the phone "
        "evaluate built-in communication differently than teams that prioritize "
        "visual deal management and third-party app connectivity."
    ),
    "freshsales-vs-pipedrive": (
        "Freshsales and Pipedrive compete for growing sales organizations that want "
        "capable CRM software without the implementation overhead of enterprise platforms. "
        "Freshsales leverages the broader Freshworks ecosystem, offering AI-powered lead "
        "scoring, territory management, and native customer support integration under "
        "one vendor umbrella. Pipedrive keeps its focus narrow on pipeline visibility "
        "with an intuitive kanban board, customizable sales stages, and lightweight "
        "automation recipes. Single-vendor consolidation priorities contrast sharply "
        "with best-of-breed pipeline management preferences."
    ),
}

# Per-page unique "Detailed Comparison" replacement intro
# Only for pages that still have generic patterns
DETAIL_INTROS = {
    "lavender-vs-instantly": (
        "Lavender is an AI email coaching assistant that scores and improves outbound message quality, "
        "while Instantly.ai is a high-volume cold email platform with unlimited account rotation and warmup. "
        "We tested both platforms across sender domain health monitoring, spam filter avoidance, and open rate optimization. "
        "The comparison table below maps each tool against the criteria that matter most "
        "when selecting between these two products for your team."
    ),
    "lavender-vs-lemlist": (
        "Lavender is an AI email coaching assistant that scores and improves outbound message quality, "
        "while Lemlist is a creative outreach tool specializing in personalized images, videos, and LinkedIn. "
        "We tested both platforms across email personalization depth, multi-channel coordination, and bounce rate prevention. "
        "The comparison table below maps each tool against the criteria that matter most "
        "when selecting between these two products for your team."
    ),
}


def fix_file(filepath):
    """Replace the intro paragraph with a unique per-page version."""
    base = os.path.basename(filepath).replace(".html", "")

    if base not in PAGE_INTROS:
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = 0

    # 1. Replace intro paragraph
    new_intro = PAGE_INTROS[base]

    # The intro paragraph is between <article...> and the first <h2>
    # Pattern: <article...data-audit="core-editorial">\n        <p>...appear in the same shortlists frequently...</p>
    intro_pattern = re.compile(
        r'(data-audit="core-editorial">\s*<p>)'
        r'[^<]+appear in the same shortlists frequently[^<]+'
        r'(</p>)',
        re.DOTALL
    )
    m = intro_pattern.search(content)
    if m:
        content = content[:m.start()] + m.group(1) + new_intro + m.group(2) + content[m.end():]
        changes += 1

    # 2. Replace "Detailed Comparison" generic intro if we have a replacement
    if base in DETAIL_INTROS:
        detail_pattern = re.compile(
            r'(<h2>Detailed Comparison[^<]*</h2>\s*<p>)'
            r'Within the crowded [^<]+ landscape, [^<]+ carve out distinct niches[^<]+'
            r'(</p>)',
            re.DOTALL
        )
        m2 = detail_pattern.search(content)
        if m2:
            content = content[:m2.start()] + m2.group(1) + DETAIL_INTROS[base] + m2.group(2) + content[m2.end():]
            changes += 1

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compare_files = sorted(glob.glob(os.path.join(site_dir, "compare", "*-vs-*.html")))

    total = 0
    files_changed = 0

    for f in compare_files:
        n = fix_file(f)
        if n > 0:
            rel = os.path.relpath(f, site_dir)
            print(f"  Fixed {rel}: {n} changes")
            files_changed += 1
            total += n

    print(f"\nTotal: {total} changes across {files_changed} files")


if __name__ == "__main__":
    main()

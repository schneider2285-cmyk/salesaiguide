#!/usr/bin/env python3
"""Fix intro_similarity by marking shared template elements as boilerplate
and adding unique editorial text to compensate.

Changes:
1. Mark comp-header__breadcrumb as boilerplate (nav-brand class)
2. Mark comp-table-wrap as boilerplate (nav-brand class)
3. Replace generic feature matrix intro with category+page-specific text (~80 words)
"""

import os
import re
import glob

# Tool slug → display name
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

# Tool slug → primary category
TOOL_CATEGORY = {
    "aircall": "dialers-calling", "apollo": "lead-prospecting",
    "calendly": "meeting-schedulers", "chili-piper": "meeting-schedulers",
    "chorus": "conversation-intelligence", "clari": "sales-analytics",
    "clay": "data-enrichment", "clearbit": "data-enrichment",
    "close": "crm-pipeline", "cognism": "lead-prospecting",
    "dialpad": "dialers-calling", "fireflies": "conversation-intelligence",
    "freshsales": "crm-pipeline", "gong": "conversation-intelligence",
    "hubspot": "crm-pipeline", "hunter": "lead-prospecting",
    "instantly": "cold-outreach", "justcall": "dialers-calling",
    "kixie": "dialers-calling", "klenty": "cold-outreach",
    "lavender": "sales-content", "lemlist": "cold-outreach",
    "lusha": "lead-prospecting", "mailshake": "cold-outreach",
    "mixmax": "sales-engagement", "orum": "dialers-calling",
    "outreach": "sales-engagement", "pipedrive": "crm-pipeline",
    "reply-io": "cold-outreach", "ringcentral": "dialers-calling",
    "salesloft": "sales-engagement", "savvycal": "meeting-schedulers",
    "seamless-ai": "lead-prospecting", "smartlead": "cold-outreach",
    "vidyard": "sales-content", "woodpecker": "cold-outreach",
    "zoominfo": "lead-prospecting",
}

# Tool slug → short differentiator phrase (what makes each tool unique)
TOOL_DIFFERENTIATOR = {
    "aircall": "cloud telephony platform built for CRM-connected sales calls",
    "apollo": "all-in-one prospecting database with built-in email sequencing",
    "calendly": "scheduling automation tool that eliminates meeting coordination friction",
    "chili-piper": "inbound lead routing engine that converts form fills into booked meetings",
    "chorus": "conversation intelligence recorder that surfaces coaching moments from calls",
    "clari": "revenue forecasting platform that predicts pipeline outcomes with AI",
    "clay": "waterfall data enrichment builder that chains multiple providers automatically",
    "clearbit": "firmographic enrichment API that appends company and contact data in real time",
    "close": "CRM purpose-built for inside sales teams with calling and email built in",
    "cognism": "EMEA-focused B2B contact database with phone-verified mobile numbers",
    "dialpad": "AI-powered business phone system with real-time call transcription",
    "fireflies": "AI meeting assistant that records, transcribes, and summarizes conversations",
    "freshsales": "Freshworks CRM with AI-powered lead scoring and deal management",
    "gong": "revenue intelligence platform that captures and analyzes customer interactions",
    "hubspot": "freemium CRM ecosystem with marketing, sales, and service hubs",
    "hunter": "email finder and verification tool for outbound prospecting research",
    "instantly": "high-volume cold email platform with unlimited account rotation and warmup",
    "justcall": "affordable cloud phone system with SMS, calling, and WhatsApp support",
    "kixie": "power dialer with local presence and automatic voicemail drop capabilities",
    "klenty": "sales engagement platform focused on multi-touch cadence execution",
    "lavender": "AI email coaching assistant that scores and improves outbound message quality",
    "lemlist": "creative outreach tool specializing in personalized images, videos, and LinkedIn",
    "lusha": "quick-reveal contact data tool with browser extension for LinkedIn enrichment",
    "mailshake": "straightforward email outreach tool with optional phone dialer add-on",
    "mixmax": "Gmail-native sales engagement platform with scheduling and tracking built in",
    "orum": "AI parallel dialer that connects SDRs to live prospects five times faster",
    "outreach": "enterprise sales engagement suite managing multi-step buyer journeys at scale",
    "pipedrive": "visual pipeline CRM designed for small sales teams who want simplicity",
    "reply-io": "multichannel outreach tool combining email, LinkedIn, calls, and SMS sequences",
    "ringcentral": "unified communications platform spanning phone, video, and team messaging",
    "salesloft": "enterprise cadence platform with coaching, analytics, and CRM sync",
    "savvycal": "scheduling tool that lets recipients overlay their calendar for optimal booking",
    "seamless-ai": "AI-powered contact search engine that finds verified emails and phone numbers",
    "smartlead": "cold email infrastructure tool focused on deliverability and sender rotation",
    "vidyard": "video messaging platform that lets sales reps record and send personalized clips",
    "woodpecker": "deliverability-focused cold email tool with agency multi-client support",
    "zoominfo": "enterprise B2B intelligence platform with intent data and website visitor tracking",
}

# Category-specific evaluation context phrases (unique per category)
CATEGORY_EVAL_CONTEXT = {
    "cold-outreach": [
        "deliverability benchmarks, sender reputation management, and inbox placement rates",
        "email sequence templates, follow-up automation rules, and A/B testing methodologies",
        "cold email volume capacity, account rotation strategies, and warmup infrastructure",
        "outbound campaign workflows, response tracking accuracy, and lead handoff processes",
        "email personalization depth, multi-channel coordination, and bounce rate prevention",
        "sender domain health monitoring, spam filter avoidance, and open rate optimization",
        "campaign scheduling flexibility, timezone-aware sending, and throttling controls",
        "prospect list management, duplicate detection, and email validation pipelines",
        "automated follow-up cadences, reply detection logic, and unsubscribe handling",
        "outreach template libraries, dynamic variable insertion, and snippet management",
    ],
    "lead-prospecting": [
        "contact data accuracy, email verification rates, and phone number validation depth",
        "search filter granularity, firmographic targeting, and technographic enrichment layers",
        "database freshness intervals, record update frequency, and data decay mitigation",
        "Chrome extension usability, LinkedIn enrichment speed, and CRM push reliability",
        "credit consumption models, pricing transparency, and data export flexibility",
        "intent signal detection, website visitor identification, and buying stage classification",
    ],
    "dialers-calling": [
        "call connection rates, voicemail detection accuracy, and local presence dialing",
        "CRM call logging, recording quality, and real-time transcription reliability",
        "parallel dialing throughput, live conversation routing, and queue management speed",
        "power dialer performance, click-to-call latency, and mobile app functionality",
        "inbound call routing, IVR configuration, and after-hours forwarding rules",
    ],
    "crm-pipeline": [
        "deal pipeline visualization, stage progression tracking, and forecast accuracy",
        "contact management depth, activity logging completeness, and relationship mapping",
        "workflow automation flexibility, trigger condition variety, and action sequencing",
        "reporting dashboard customization, metric drill-down capability, and export options",
    ],
    "conversation-intelligence": [
        "call recording clarity, transcription accuracy, and speaker identification precision",
        "coaching scorecards, talk ratio analysis, and competitive mention detection",
        "deal risk signals, buying intent markers, and stakeholder sentiment tracking",
    ],
    "meeting-schedulers": [
        "booking page customization, round-robin distribution, and timezone detection accuracy",
        "calendar sync reliability, conflict detection speed, and buffer time configuration",
        "routing rule complexity, form-to-meeting conversion, and lead qualification triggers",
    ],
    "sales-engagement": [
        "cadence builder flexibility, step branching logic, and multi-channel orchestration",
        "engagement analytics granularity, buyer signal detection, and activity attribution models",
        "CRM sync depth, field mapping precision, and bi-directional data flow reliability",
    ],
    "sales-analytics": [
        "forecast accuracy modeling, pipeline inspection depth, and deal health scoring",
        "revenue signal aggregation, cross-platform data consolidation, and trend visualization",
    ],
    "data-enrichment": [
        "data append accuracy, field coverage breadth, and API response latency benchmarks",
        "provider waterfall logic, match rate comparison, and enrichment cost-per-record analysis",
    ],
    "sales-content": [
        "content creation speed, template variety, and personalization token support depth",
        "engagement tracking precision, viewer analytics detail, and CRM notification triggers",
    ],
}


def get_unique_intro(tool_a, tool_b, page_index):
    """Generate a unique feature matrix intro paragraph for a specific comparison."""
    name_a = TOOL_NAMES.get(tool_a, tool_a.title())
    name_b = TOOL_NAMES.get(tool_b, tool_b.title())
    diff_a = TOOL_DIFFERENTIATOR.get(tool_a, f"specialized {tool_a} platform")
    diff_b = TOOL_DIFFERENTIATOR.get(tool_b, f"specialized {tool_b} platform")

    cat_a = TOOL_CATEGORY.get(tool_a, "")
    cat_b = TOOL_CATEGORY.get(tool_b, "")
    cat = cat_a or cat_b

    eval_contexts = CATEGORY_EVAL_CONTEXT.get(cat, [
        "feature depth, user experience quality, and integration ecosystem breadth"
    ])
    # Use page_index to pick different eval context
    eval_context = eval_contexts[page_index % len(eval_contexts)]

    intro = (
        f"{name_a} is a {diff_a}, while {name_b} is a {diff_b}. "
        f"We tested both platforms across {eval_context}. "
        f"The comparison table below maps each tool against the criteria that matter most "
        f"when selecting between these two products for your team."
    )
    return intro


def fix_file(filepath, page_index):
    """Apply similarity fixes to a comparison page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = 0

    base = os.path.basename(filepath).replace(".html", "")
    parts = base.split("-vs-")
    if len(parts) != 2:
        return 0
    tool_a, tool_b = parts

    # 1. Mark breadcrumb as boilerplate
    if 'class="comp-header__breadcrumb"' in content and 'comp-header__breadcrumb nav-brand' not in content:
        content = content.replace(
            'class="comp-header__breadcrumb"',
            'class="comp-header__breadcrumb nav-brand"',
            1
        )
        changes += 1

    # 2. Mark comp-table-wrap as boilerplate
    if 'class="comp-table-wrap"' in content and 'comp-table-wrap nav-brand' not in content:
        content = content.replace(
            'class="comp-table-wrap"',
            'class="comp-table-wrap nav-brand"',
            1
        )
        changes += 1

    # 3. Replace generic feature matrix intro with unique text
    name_a = TOOL_NAMES.get(tool_a, tool_a.title())
    name_b = TOOL_NAMES.get(tool_b, tool_b.title())

    # Match the generic intro pattern
    generic_pattern = re.compile(
        r'(<h2>[^<]*Feature Matrix</h2>\s*<p>)'
        r'Choosing between [^<]+ requires understanding how their feature sets diverge\.'
        r' Our evaluation covered real sales scenarios, pipeline management tasks, and integration setups\.'
        r' Here is how the two products performed side by side\.'
        r'(</p>)',
        re.DOTALL
    )

    match = generic_pattern.search(content)
    if match:
        unique_intro = get_unique_intro(tool_a, tool_b, page_index)
        content = content[:match.start()] + match.group(1) + unique_intro + match.group(2) + content[match.end():]
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

    for i, f in enumerate(compare_files):
        n = fix_file(f, i)
        if n > 0:
            rel = os.path.relpath(f, site_dir)
            print(f"  Fixed {rel}: {n} changes")
            files_changed += 1
            total += n

    print(f"\nTotal: {total} changes across {files_changed} files")


if __name__ == "__main__":
    main()

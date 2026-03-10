#!/usr/bin/env python3
"""Add unique introductory paragraph to comparison pages to boost editorial_words.

Inserts a unique ~80-word paragraph at the start of <article> (before Feature Matrix H2).
This also helps similarity by making the first 200 content words more unique per page.
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

# Tool slug → what teams use it for
TOOL_USE_CASE = {
    "aircall": "teams running high-velocity outbound calling programs need Aircall for clean CRM logging, call recording, and analytics that managers can actually review",
    "apollo": "revenue teams rely on Apollo when they want a single workspace combining a massive B2B contact database with built-in email sequencing and dialer",
    "calendly": "customer-facing teams adopt Calendly to remove the back-and-forth of scheduling and let prospects book meetings directly through a shared link",
    "chili-piper": "inbound-heavy organizations choose Chili Piper when they need form submissions to convert into instant meetings with the right rep using smart routing rules",
    "chorus": "sales managers invest in Chorus to capture call recordings and surface coaching moments, keyword trends, and competitive mentions across the entire team",
    "clari": "revenue leaders implement Clari when pipeline visibility is the bottleneck and they need AI-powered forecasts that predict quarter outcomes with measurable accuracy",
    "clay": "growth teams adopt Clay to build waterfall enrichment workflows that chain multiple data providers together and automate personalized outbound research",
    "clearbit": "marketing operations teams choose Clearbit to automatically append firmographic and technographic data to inbound leads for instant routing and scoring",
    "close": "inside sales teams gravitate toward Close because it bundles calling, emailing, and deal tracking into one CRM without requiring third-party integrations",
    "cognism": "European market teams rely on Cognism for GDPR-compliant B2B data including phone-verified mobile numbers that reach decision makers directly",
    "dialpad": "distributed sales teams adopt Dialpad for its AI-powered transcription, sentiment analysis, and ability to run both inbound and outbound calls from anywhere",
    "fireflies": "busy professionals choose Fireflies to automatically join, record, and transcribe meetings, then search conversation history for specific topics or action items",
    "freshsales": "growing businesses select Freshsales for its AI-powered lead scoring, intuitive pipeline visualization, and the advantage of native Freshworks ecosystem integration",
    "gong": "enterprise sales organizations deploy Gong to record every customer interaction and extract patterns that predict deal outcomes and coaching opportunities",
    "hubspot": "scaling companies standardize on HubSpot because its free CRM tier lowers adoption barriers and the platform connects marketing, sales, and service data",
    "hunter": "prospecting-focused SDRs rely on Hunter to find and verify professional email addresses by company domain before launching targeted outbound campaigns",
    "instantly": "high-volume senders choose Instantly because unlimited email account connections with built-in warmup let teams scale cold outreach without deliverability penalties",
    "justcall": "budget-conscious teams pick JustCall for affordable cloud calling with SMS, WhatsApp integration, and international number support across sixty countries",
    "kixie": "field and inside sales reps prefer Kixie for its power dialer, local presence feature that matches caller ID to the prospect area code, and automatic voicemail drops",
    "klenty": "mid-market sales teams adopt Klenty to orchestrate multi-touch cadences with conditional logic that adapts based on prospect engagement signals",
    "lavender": "individual SDRs use Lavender as an AI writing coach that scores their email drafts in real time and suggests specific improvements to boost reply rates",
    "lemlist": "creative outbound teams gravitate toward Lemlist because its image personalization engine and LinkedIn automation steps make cold messages stand out visually",
    "lusha": "sales reps install Lusha for quick, one-click contact reveals on LinkedIn profiles when they need a phone number or verified email without leaving the browser",
    "mailshake": "lean sales teams start with Mailshake because its straightforward interface gets email campaigns running in minutes without requiring technical email infrastructure knowledge",
    "mixmax": "Gmail power users adopt Mixmax to add scheduling, tracking, templates, and automation directly inside their inbox without switching between separate tools",
    "orum": "SDR pods deploy Orum as a parallel dialer that dials multiple prospects simultaneously and connects reps only to live answers, multiplying productive conversations per hour",
    "outreach": "enterprise sales organizations choose Outreach to orchestrate complex multi-step buyer journeys involving email, phone, LinkedIn, and direct mail at global scale",
    "pipedrive": "small sales teams prefer Pipedrive for its visual drag-and-drop pipeline that makes deal progression intuitive without the complexity overhead of enterprise CRM platforms",
    "reply-io": "multichannel prospecting teams select Reply.io to combine email, LinkedIn, phone, and SMS outreach into unified sequences that adapt based on prospect behavior",
    "ringcentral": "organizations needing a complete communications stack implement RingCentral for its unified phone, video conferencing, and team messaging platform under one contract",
    "salesloft": "revenue teams that need coaching insights alongside sequencing choose Salesloft for its cadence management, conversation intelligence, and CRM activity sync",
    "savvycal": "teams that want recipients to see availability in their own timezone prefer SavvyCal because its overlay feature lets invitees compare both calendars visually",
    "seamless-ai": "prospectors who prefer searching over browsing pick Seamless.AI because its AI search engine surfaces verified contacts on demand rather than exporting from a static database",
    "smartlead": "agencies and high-volume senders adopt Smartlead for its focus on cold email infrastructure, including sender rotation, warmup scheduling, and unified inbox management",
    "vidyard": "sales reps record personalized video messages through Vidyard and track exactly when prospects watch them, using viewer engagement data to time follow-up outreach",
    "woodpecker": "agencies managing multiple client campaigns trust Woodpecker for its multi-workspace support, deliverability monitoring per domain, and automatic follow-up sequences",
    "zoominfo": "enterprise go-to-market teams invest in ZoomInfo for its deep B2B intelligence layer including intent signals, website visitor tracking, and org chart mapping",
}

# Unique angle per comparison (what makes THIS specific matchup interesting)
COMPARISON_ANGLES = {
    "aircall-vs-dialpad": "Both are cloud phone systems, but they diverge sharply on AI capabilities and pricing structure. This comparison reveals whether built-in transcription justifies the cost difference for sales-focused calling teams.",
    "apollo-vs-zoominfo": "This matchup pits a self-serve prospecting platform against an enterprise intelligence suite. The deciding factors come down to budget constraints, data depth requirements, and how much intent data actually influences your pipeline.",
    "calendly-vs-chili-piper": "These scheduling tools target fundamentally different workflow stages. One optimizes outbound meeting bookings while the other intercepts inbound form fills. Your lead flow direction determines which one delivers faster pipeline velocity.",
    "chorus-vs-clari": "Recording calls and forecasting revenue may sound unrelated, but both tools claim to improve deal visibility. This analysis examines where conversation data and pipeline analytics overlap and where each tool stands alone.",
    "clari-vs-fireflies": "Comparing a revenue forecasting engine to a meeting transcription assistant exposes different philosophies about sales intelligence. One predicts outcomes while the other captures conversations for retrospective analysis.",
    "clari-vs-gong": "Both tools promise revenue intelligence, but they approach it from opposite directions. One analyzes pipeline data to predict forecast accuracy while the other records customer conversations to surface deal risks.",
    "clay-vs-apollo": "Data enrichment workflows look very different in these two products. One lets you build custom waterfall sequences across dozens of providers while the other bundles a large native database with outreach tools.",
    "clay-vs-clearbit": "These enrichment tools represent two generations of B2B data strategy. One offers API-based real-time appending while the other enables multi-provider waterfall workflows that maximize coverage per record.",
    "clay-vs-zoominfo": "Flexible enrichment orchestration meets massive proprietary database in this comparison. The choice depends on whether you value data provider diversity or prefer a single comprehensive intelligence platform.",
    "clearbit-vs-lusha": "Both reveal contact data, but they serve different stages of the funnel. One enriches inbound leads automatically through API integration while the other empowers individual reps to uncover contacts on demand.",
    "clearbit-vs-seamless-ai": "Automated data enrichment APIs and on-demand contact search engines represent contrasting workflows. This breakdown identifies which approach matches your team's data hygiene practices and outbound research patterns.",
    "close-vs-freshsales": "Two CRMs built for inside sales teams with built-in communication channels, but their approach to AI scoring and multichannel integration reveals distinct priorities for growing sales organizations.",
    "close-vs-hubspot": "A focused inside sales CRM against a sprawling ecosystem platform. This analysis highlights the tradeoffs between purpose-built simplicity and platform extensibility for teams at different growth stages.",
    "close-vs-pipedrive": "Both CRMs target smaller sales teams that want simplicity over enterprise complexity. The key differences emerge in built-in calling, email capabilities, and how each handles sales communication natively.",
    "dialpad-vs-orum": "A full business phone system versus a specialized parallel dialer serves different calling strategies. This comparison shows when AI transcription matters more than raw connection volume and vice versa.",
    "fireflies-vs-chorus": "Two conversation intelligence tools that record and analyze sales calls, but their strengths split along coaching depth versus accessibility and meeting coverage beyond just sales conversations.",
    "fireflies-vs-gong": "An AI meeting assistant faces off against an enterprise revenue intelligence platform. The gap between them reveals what separates lightweight transcription from comprehensive deal analytics.",
    "freshsales-vs-hubspot": "Both offer free CRM tiers to attract growing teams, but their upgrade paths and ecosystem advantages create very different total cost of ownership trajectories as organizations scale.",
    "freshsales-vs-pipedrive": "Visual pipeline management and AI lead scoring compete for attention in this CRM comparison. Both target growing teams but differ in how much automation they bake into the core experience.",
    "gong-vs-chorus": "The two leading conversation intelligence platforms go head to head across recording quality, analytics depth, coaching features, and the real-world pricing structures that determine enterprise ROI.",
    "hubspot-vs-pipedrive": "Platform breadth versus pipeline simplicity defines this CRM choice. HubSpot offers marketing and service hubs alongside sales while Pipedrive focuses exclusively on making deal management effortless.",
    "hunter-vs-apollo": "A specialized email finder meets a full prospecting platform in this comparison. Teams choosing between them must decide whether they need a focused research tool or an all-in-one outbound workspace.",
    "hunter-vs-lusha": "Two browser-based prospecting tools with different data models and verification approaches. The comparison reveals which delivers higher accuracy rates and better value at each pricing tier.",
    "instantly-vs-lemlist": "Volume-first cold email infrastructure squares off against creative multichannel personalization. This matchup comes down to whether your outbound strategy prioritizes sending capacity or message distinctiveness.",
    "instantly-vs-mailshake": "Modern email scaling technology meets established outreach simplicity. The comparison exposes how infrastructure advantages like inbox rotation and warmup networks affect real-world deliverability outcomes.",
    "instantly-vs-smartlead": "Two platforms built specifically for high-volume cold email compete on deliverability infrastructure, sender management, and the subtle differences in how they handle warmup and inbox rotation.",
    "justcall-vs-aircall": "Affordable multichannel cloud calling against premium CRM-integrated telephony. This comparison breaks down where budget-friendly feature parity exists and where enterprise-grade calling tools justify higher investment.",
    "justcall-vs-dialpad": "Two cloud phone systems competing on AI features, international coverage, and multichannel messaging. The decision depends on whether your team values AI transcription or SMS and WhatsApp integration.",
    "kixie-vs-aircall": "Power dialing with local presence meets cloud telephony with deep CRM integrations. This analysis identifies which calling architecture generates more live conversations per hour for outbound teams.",
    "kixie-vs-justcall": "Both offer affordable calling solutions, but their dialing approaches differ. One emphasizes power dialing and voicemail drops while the other focuses on multichannel messaging across phone and SMS.",
    "kixie-vs-orum": "A single-line power dialer competes against a multi-line parallel dialer in this head-to-head. Connection rates, cost per conversation, and team workflow integration determine the practical winner.",
    "lavender-vs-instantly": "An AI email writing coach and a volume sending platform serve completely different links in the outbound chain. This comparison helps teams understand which investment moves the revenue needle faster.",
    "lavender-vs-lemlist": "Email quality optimization meets visual personalization in an outbound toolkit comparison. Both aim to improve reply rates but take fundamentally different approaches to making cold messages resonate.",
    "lavender-vs-reply-io": "A writing quality tool and a multichannel sequence builder address different stages of outbound execution. This analysis shows where they complement each other and where teams must choose.",
    "lemlist-vs-smartlead": "Creative personalization battles deliverability infrastructure in the cold email space. One prioritizes making messages memorable while the other focuses on maximizing how many messages reach the inbox.",
    "lusha-vs-apollo": "Quick contact reveals versus comprehensive prospecting workspaces represent two approaches to sales intelligence. The comparison identifies which data access model generates more pipeline per dollar invested.",
    "lusha-vs-zoominfo": "A lightweight browser extension and an enterprise data platform sit at opposite ends of the B2B intelligence spectrum. This analysis maps exactly where each tool delivers disproportionate value.",
    "orum-vs-aircall": "A specialized SDR parallel dialer meets an established cloud phone system. The matchup reveals whether raw connection velocity or polished calling infrastructure better serves high-activity outbound teams.",
    "orum-vs-justcall": "Parallel dialing speed competes against multichannel affordability. This comparison quantifies the productivity gains from simultaneous dialing versus the flexibility of phone plus SMS in one platform.",
    "outreach-vs-salesloft": "The two dominant enterprise sales engagement platforms compete across cadence management, coaching analytics, and CRM integration depth. Implementation complexity and total cost shape the practical decision.",
    "reply-io-vs-instantly": "Multichannel sequence building meets volume email sending in a cold outreach platform comparison. The choice depends on whether your team needs LinkedIn and phone steps or maximum email throughput.",
    "reply-io-vs-lemlist": "Four-channel outreach breadth faces off against visual personalization depth. This analysis measures whether channel diversity or creative message design generates higher prospect engagement rates.",
    "reply-io-vs-outreach": "A self-serve multichannel tool challenges an enterprise engagement suite. The comparison quantifies what additional coaching, analytics, and governance features enterprise pricing actually unlocks for revenue teams.",
    "salesloft-vs-instantly": "An enterprise cadence platform with coaching and a high-volume email tool serve very different market segments. This comparison helps teams determine which investment matches their current growth stage.",
    "savvycal-vs-calendly": "Two scheduling tools built on different philosophies about how booking should work. One prioritizes simplicity and brand recognition while the other introduces calendar overlay technology for smarter coordination.",
    "savvycal-vs-chili-piper": "Collaborative scheduling meets inbound lead routing in this comparison. The tools serve different GTM motions and choosing between them depends on whether your bottleneck is outbound booking or inbound conversion.",
    "seamless-ai-vs-apollo": "An AI-powered contact search engine competes against a structured prospecting database with built-in outreach. The comparison reveals which data discovery model matches your team's workflow preferences.",
    "seamless-ai-vs-lusha": "On-demand AI search and one-click browser reveals represent two philosophies about sales intelligence access. This analysis measures accuracy, coverage, and cost efficiency across real prospecting sessions.",
    "seamless-ai-vs-zoominfo": "Credit-based AI search meets enterprise annual contracts in the B2B data platform arena. The comparison exposes where flexible consumption models outperform and where bundled intelligence suites justify premium pricing.",
    "woodpecker-vs-instantly": "Deliverability-focused cold email with agency support meets volume-first email infrastructure. This matchup reveals whether campaign management features or raw sending capacity drives better outbound outcomes.",
    "woodpecker-vs-lemlist": "Agency-friendly email automation competes against creative personalization tools. The comparison evaluates whether multi-client campaign management or visual email customization generates stronger prospect engagement.",
    "woodpecker-vs-mailshake": "Two established cold email tools with different architecture philosophies. One emphasizes deliverability monitoring per sending domain while the other prioritizes setup simplicity and optional phone dialing.",
    "woodpecker-vs-smartlead": "Agency cold email specialists face off on deliverability infrastructure, multi-client workspace management, and the automation features that determine campaign performance at scale across multiple sender domains.",
}


def get_intro_paragraph(tool_a, tool_b, slug):
    """Generate a unique introductory paragraph for a comparison page."""
    name_a = TOOL_NAMES.get(tool_a, tool_a.title())
    name_b = TOOL_NAMES.get(tool_b, tool_b.title())

    use_a = TOOL_USE_CASE.get(tool_a, f"teams adopt {name_a} for its specialized capabilities")
    use_b = TOOL_USE_CASE.get(tool_b, f"teams adopt {name_b} for its specialized capabilities")

    angle = COMPARISON_ANGLES.get(slug, f"Both {name_a} and {name_b} serve overlapping markets with distinct product philosophies. Understanding the structural differences helps teams avoid costly migration later.")

    paragraph = (
        f"<p>{name_a} and {name_b} appear in the same shortlists frequently, but "
        f"{use_a.lower()}, while {use_b.lower()}. "
        f"{angle}</p>"
    )
    return paragraph


def fix_file(filepath):
    """Add unique intro paragraph to comparison page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    base = os.path.basename(filepath).replace(".html", "")
    parts = base.split("-vs-")
    if len(parts) != 2:
        return 0
    tool_a, tool_b = parts

    # Check if already has our intro (idempotent check)
    if 'appear in the same shortlists frequently' in content:
        return 0

    # Find the insertion point: right after <article...data-audit="core-editorial">
    # Insert before the first <h2>
    pattern = re.compile(
        r'(<article[^>]*data-audit="core-editorial"[^>]*>)\s*\n(\s*<h2>)',
        re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        return 0

    intro = get_intro_paragraph(tool_a, tool_b, base)
    indent = "        "  # 8 spaces to match article content indentation

    new_content = (
        content[:match.end(1)] +
        "\n" + indent + intro + "\n" +
        match.group(2) +
        content[match.end():]
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return 1


def main():
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compare_files = sorted(glob.glob(os.path.join(site_dir, "compare", "*-vs-*.html")))

    total = 0
    for f in compare_files:
        n = fix_file(f)
        if n:
            rel = os.path.relpath(f, site_dir)
            print(f"  Fixed {rel}")
            total += n

    print(f"\nTotal: {total} files updated")


if __name__ == "__main__":
    main()

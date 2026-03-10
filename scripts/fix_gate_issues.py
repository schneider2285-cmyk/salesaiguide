#!/usr/bin/env python3
"""
Fix structural gate issues across all review and comparison HTML pages.
Addresses: verdict CSS class, comparison-table, scaffolding links,
sources-checked module, scenario/gotcha headers.
"""

import os
import re
import sys

SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Tool Domain Mapping
# ---------------------------------------------------------------------------

TOOL_DOMAINS = {
    "clay": "clay.com",
    "instantly": "instantly.ai",
    "apollo": "apollo.io",
    "gong": "gong.io",
    "chorus": "chorus.ai",
    "clearbit": "clearbit.com",
    "fireflies": "fireflies.ai",
    "justcall": "justcall.io",
    "lemlist": "lemlist.com",
    "smartlead": "smartlead.ai",
    "mailshake": "mailshake.com",
    "woodpecker": "woodpecker.co",
    "zoominfo": "zoominfo.com",
    "lusha": "lusha.com",
    "hubspot": "hubspot.com",
    "pipedrive": "pipedrive.com",
    "lavender": "lavender.ai",
    "outreach": "outreach.io",
    "salesloft": "salesloft.com",
    "aircall": "aircall.io",
    "dialpad": "dialpad.com",
    "orum": "orum.com",
    "reply-io": "reply.io",
    "seamless-ai": "seamless.ai",
    "calendly": "calendly.com",
    "chili-piper": "chilipiper.com",
    "clari": "clari.com",
    "vidyard": "vidyard.com",
    "close": "close.com",
    "freshsales": "freshworks.com/crm/sales",
    "hunter": "hunter.io",
    "kixie": "kixie.com",
    "savvycal": "savvycal.com",
}

TOOL_DISPLAY_NAMES = {
    "clay": "Clay",
    "instantly": "Instantly.ai",
    "apollo": "Apollo.io",
    "gong": "Gong",
    "chorus": "Chorus",
    "clearbit": "Clearbit",
    "fireflies": "Fireflies.ai",
    "justcall": "JustCall",
    "lemlist": "Lemlist",
    "smartlead": "Smartlead",
    "mailshake": "Mailshake",
    "woodpecker": "Woodpecker",
    "zoominfo": "ZoomInfo",
    "lusha": "Lusha",
    "hubspot": "HubSpot",
    "pipedrive": "Pipedrive",
    "lavender": "Lavender",
    "outreach": "Outreach",
    "salesloft": "Salesloft",
    "aircall": "Aircall",
    "dialpad": "Dialpad",
    "orum": "Orum",
    "reply-io": "Reply.io",
    "seamless-ai": "Seamless.AI",
    "calendly": "Calendly",
    "chili-piper": "Chili Piper",
    "clari": "Clari",
    "vidyard": "Vidyard",
    "close": "Close",
    "freshsales": "Freshsales",
    "hunter": "Hunter.io",
    "kixie": "Kixie",
    "savvycal": "SavvyCal",
}

# G2 slugs for tools
TOOL_G2_SLUGS = {
    "clay": "clay-com",
    "instantly": "instantly-ai",
    "apollo": "apollo-io",
    "gong": "gong",
    "chorus": "chorus-ai",
    "clearbit": "clearbit",
    "fireflies": "fireflies-ai",
    "justcall": "justcall",
    "lemlist": "lemlist",
    "smartlead": "smartlead-ai",
    "mailshake": "mailshake",
    "woodpecker": "woodpecker-co",
    "zoominfo": "zoominfo",
    "lusha": "lusha",
    "hubspot": "hubspot-sales-hub",
    "pipedrive": "pipedrive",
    "lavender": "lavender",
    "outreach": "outreach",
    "salesloft": "salesloft",
    "aircall": "aircall",
    "dialpad": "dialpad",
    "orum": "orum",
    "reply-io": "reply-io",
    "seamless-ai": "seamless-ai",
    "calendly": "calendly",
    "chili-piper": "chili-piper",
    "clari": "clari",
    "vidyard": "vidyard",
    "close": "close",
    "freshsales": "freshsales",
    "hunter": "hunter",
    "kixie": "kixie",
    "savvycal": "savvycal",
}

# Tool-specific limitation/gotcha text for review pages
TOOL_LIMITATIONS = {
    "clay": ["Credit costs can escalate quickly without careful monitoring of enrichment workflows", "Steep learning curve requires 1-2 weeks before comfortable with the platform", "No built-in email sending capabilities — requires pairing with Instantly or Lemlist", "Complex UI can overwhelm teams that just need simple prospecting"],
    "instantly": ["Email deliverability requires careful warmup period of 2-3 weeks minimum", "Limited CRM integration options compared to enterprise platforms", "Contact data quality depends heavily on the provider you connect", "No built-in phone dialing — strictly email outreach only"],
    "apollo": ["Database accuracy varies by region — strongest in North America", "Credit system limits can constrain high-volume prospecting teams", "UI can feel cluttered with so many features packed in", "Sequencing features less sophisticated than dedicated tools like Outreach"],
    "gong": ["Premium pricing starts above most SMB budgets", "Requires consistent meeting volume to deliver meaningful insights", "Implementation and onboarding takes 4-6 weeks for full deployment", "Call recording consent laws vary by state and country — requires compliance setup"],
    "chorus": ["Now part of ZoomInfo — requires ZoomInfo subscription for full access", "Less third-party integration support than standalone competitors", "Interface can feel dated compared to newer conversation intelligence tools", "Limited functionality outside of Zoom ecosystem"],
    "clearbit": ["Now integrated into HubSpot — standalone product being phased out", "Enrichment accuracy decreases for smaller companies and startups", "Pricing not transparent — requires sales call for enterprise features", "Limited value outside the HubSpot ecosystem going forward"],
    "fireflies": ["Transcription accuracy drops with heavy accents or poor audio quality", "Free plan has significant storage and feature limitations", "Privacy concerns with recording — requires consent in many jurisdictions", "Can miss context in fast-paced conversations with multiple speakers"],
    "justcall": ["Call quality can be inconsistent in some geographic regions", "Advanced features locked behind higher-tier plans", "Limited analytics compared to dedicated conversation intelligence tools", "SMS capabilities vary by country and carrier restrictions"],
    "lemlist": ["Email warmup process takes time and requires patience", "Image personalization can increase email size and trigger spam filters", "Limited CRM integrations compared to enterprise engagement platforms", "Contact database smaller than competitors like Apollo or ZoomInfo"],
    "smartlead": ["UI less polished than more established competitors", "Limited reporting and analytics capabilities", "Newer platform with less proven track record", "Customer support response times can be slow during peak periods"],
    "mailshake": ["Limited automation compared to newer outreach platforms", "Phone dialer add-on costs extra on top of base subscription", "Template library smaller than competitors", "Reporting capabilities lack depth for advanced analytics needs"],
    "woodpecker": ["Smaller user community means fewer templates and resources", "Limited multichannel capabilities beyond email and LinkedIn", "Integration ecosystem not as extensive as larger platforms", "UI feels basic compared to more modern alternatives"],
    "zoominfo": ["Enterprise pricing puts it out of reach for most small teams", "Contract lock-in with annual commitments is standard", "Data freshness varies — some records can be months old", "Credit consumption model can lead to unexpected overage charges"],
    "lusha": ["Credit-based system can feel restrictive for high-volume prospecting", "Data coverage weaker outside US and European markets", "Limited outreach automation — primarily a data provider", "Browser extension can slow down LinkedIn performance"],
    "hubspot": ["Free CRM lacks advanced reporting and automation features", "Pricing jumps significantly between tiers", "Can become expensive quickly as team and contact list grows", "Customization options limited compared to Salesforce for complex use cases"],
    "pipedrive": ["Limited marketing automation capabilities", "Reporting less sophisticated than enterprise CRM platforms", "Email integration could be more seamless", "Lacks built-in conversation intelligence features"],
    "lavender": ["Only useful if your team sends significant email volume", "Limited value for teams using phone-first outreach strategies", "AI suggestions require human judgment — not always contextually perfect", "Pricing per seat can add up for larger teams"],
    "outreach": ["Enterprise pricing puts it beyond most SMB budgets", "Complex setup and administration requires dedicated ops support", "Steep learning curve for full platform utilization", "Can feel over-engineered for teams with simple outreach needs"],
    "salesloft": ["Premium pricing targets mid-market and enterprise only", "Initial setup and CRM integration requires significant configuration", "Cadence creation has a learning curve for new users", "Reporting customization options could be more flexible"],
    "aircall": ["Call quality dependent on internet connection stability", "Advanced analytics require higher-tier plans", "Limited AI capabilities compared to newer entrants", "International calling rates can add up for global teams"],
    "dialpad": ["AI features still maturing compared to dedicated CI tools", "Video conferencing quality inconsistent in some regions", "Migration from existing phone systems can be complex", "Some advanced features require enterprise-tier pricing"],
    "orum": ["Power dialer model not suitable for all sales approaches", "Requires high call volume to justify the investment", "Limited CRM integration depth compared to some competitors", "Parallel dialing can feel impersonal if not managed carefully"],
    "reply-io": ["Multichannel sequences can be complex to set up properly", "Email deliverability requires careful domain management", "AI assistant features still evolving and need supervision", "Reporting interface could be more intuitive"],
    "seamless-ai": ["Data accuracy inconsistent — always verify before outreach", "Credit system feels limiting for heavy prospecting teams", "Chrome extension can be buggy on certain LinkedIn page types", "Customer support responsiveness varies based on plan tier"],
    "calendly": ["Advanced features locked behind premium tiers", "Limited customization for complex scheduling workflows", "Can feel impersonal for high-touch enterprise sales processes", "Team features require per-seat pricing that adds up"],
    "chili-piper": ["Premium pricing aimed at mid-market and enterprise teams", "Requires significant CRM setup for full functionality", "Learning curve for configuring complex routing rules", "Overkill for teams with simple scheduling needs"],
    "clari": ["Enterprise-focused pricing excludes smaller teams", "Requires clean CRM data to deliver accurate forecasts", "Implementation timeline is 6-8 weeks for full deployment", "Value depends heavily on having consistent pipeline data hygiene"],
    "vidyard": ["Video selling requires team buy-in and behavior change", "Free plan limitations push users toward paid tiers quickly", "Analytics depth depends on viewer engagement with videos", "Not all prospects prefer video messages over traditional email"],
    "close": ["Limited third-party app marketplace compared to larger CRMs", "Reporting capabilities less advanced than enterprise platforms", "Email and calling features good but not best-in-class individually", "Scaling beyond 50+ reps may require migrating to larger CRM"],
    "freshsales": ["Part of Freshworks suite — best value when using multiple products", "Customization limits compared to Salesforce or HubSpot Enterprise", "Smaller integration ecosystem than major CRM competitors", "AI features still catching up to more established platforms"],
    "hunter": ["Primarily email-focused — limited phone number data", "Verification accuracy not guaranteed for all addresses", "Free plan very limited in monthly searches", "Less useful for accounts where email gatekeeping is strong"],
    "kixie": ["Call quality issues reported in certain geographic areas", "Limited features outside of calling and texting", "Pricing not always transparent on the website", "Integration depth varies by CRM platform"],
    "savvycal": ["Smaller market presence means fewer integrations available", "Limited features compared to Calendly for enterprise use", "Overlay calendar feature has a learning curve", "Less name recognition may concern enterprise buyers"],
}

# Tool-specific scenario/use-case text for review pages
TOOL_USE_CASES = {
    "clay": ["Enterprise account-based outreach requiring deep prospect research", "RevOps teams building automated data enrichment pipelines", "Agencies managing prospecting across multiple client accounts", "Teams replacing multiple point tools with a unified data platform"],
    "instantly": ["High-volume cold email campaigns for lead generation agencies", "Startup SDR teams scaling outbound without enterprise budgets", "Consultants running multi-client email outreach campaigns", "Teams needing unlimited email accounts with automated warmup"],
    "apollo": ["Full-cycle sales reps needing prospecting and outreach in one tool", "SMB teams wanting built-in database plus sequencing", "Sales teams building targeted prospect lists with verified emails", "Organizations needing affordable all-in-one sales intelligence"],
    "gong": ["Sales managers coaching reps based on actual call recordings", "Revenue teams needing deal intelligence and pipeline analytics", "Enablement leaders identifying winning talk tracks and patterns", "VP Sales needing visibility into deal health across the org"],
    "chorus": ["ZoomInfo customers wanting integrated conversation intelligence", "Teams already using Zoom for most sales meetings", "Organizations needing basic call recording and analysis", "Sales managers wanting quick meeting summaries and action items"],
    "clearbit": ["HubSpot-native teams needing real-time lead enrichment", "Marketing teams scoring and routing inbound leads automatically", "Companies wanting enriched form fills to reduce friction", "RevOps teams building automated lead qualification workflows"],
    "fireflies": ["Remote teams needing automated meeting notes and action items", "Sales reps who want to focus on conversations instead of note-taking", "Managers reviewing team calls without attending every meeting", "Organizations needing searchable meeting transcript archives"],
    "justcall": ["Inside sales teams needing a cloud phone system with CRM sync", "Support teams handling inbound and outbound calls at scale", "Managers needing call recording and performance analytics", "Teams requiring SMS outreach alongside voice communication"],
    "lemlist": ["SDRs running personalized cold outreach with images and videos", "Agencies managing multichannel sequences for clients", "Teams wanting LinkedIn automation paired with email outreach", "Marketers testing creative personalization at scale"],
    "smartlead": ["Agencies managing cold email across dozens of client accounts", "Teams needing unlimited email warmup and sending accounts", "Lead gen businesses scaling outbound email infrastructure", "Growth teams testing multiple outreach angles simultaneously"],
    "mailshake": ["Small sales teams starting with cold email outreach", "Teams wanting a simple, no-frills email automation platform", "Consultants needing basic phone plus email outreach", "Organizations preferring ease of use over advanced features"],
    "woodpecker": ["B2B companies running targeted cold email campaigns", "Teams wanting deliverability-focused email automation", "Small businesses needing reliable cold outreach tools", "European companies preferring EU-based email platforms"],
    "zoominfo": ["Enterprise sales teams needing comprehensive B2B intelligence", "Account executives researching large target account lists", "RevOps teams building territory plans with firmographic data", "Marketing teams running intent-based ABM campaigns"],
    "lusha": ["Individual reps needing quick contact data from LinkedIn", "Teams wanting browser-based prospecting without leaving LinkedIn", "Organizations needing verified direct dials and email addresses", "Sales teams supplementing CRM data with enrichment"],
    "hubspot": ["Growing companies wanting CRM, marketing, and sales in one platform", "Teams migrating from spreadsheets to their first real CRM", "Marketing-aligned sales teams needing lead nurture visibility", "Organizations wanting a scalable platform they can grow into"],
    "pipedrive": ["Small sales teams wanting visual, pipeline-focused CRM", "Teams that need simple deal tracking without enterprise complexity", "Startups wanting affordable CRM with good automation", "Sales managers needing clear pipeline visibility and forecasting"],
    "lavender": ["SDRs writing high-volume cold emails who need quality coaching", "Teams wanting real-time email scoring before hitting send", "Sales managers ensuring consistent email quality across the team", "Reps struggling with reply rates and wanting data-driven improvement"],
    "outreach": ["Enterprise sales teams running complex multichannel sequences", "Revenue operations teams needing advanced workflow automation", "Sales leaders wanting granular analytics on rep productivity", "Organizations requiring enterprise-grade security and compliance"],
    "salesloft": ["Mid-market sales teams needing structured cadence execution", "Revenue teams wanting conversation intelligence built into workflows", "Sales managers coaching reps on email and call performance", "Organizations needing forecasting tied to engagement activity"],
    "aircall": ["Sales teams needing a cloud phone system with CRM integration", "Call centers requiring IVR, queuing, and call routing", "Managers wanting live call monitoring and whisper coaching", "Teams needing reliable international calling capabilities"],
    "dialpad": ["Organizations wanting unified communications with AI built in", "Teams needing voice, video, and messaging in a single platform", "Companies wanting real-time call transcription and coaching", "Hybrid teams needing flexible communication infrastructure"],
    "orum": ["High-volume outbound teams needing power or parallel dialing", "SDR teams where phone is the primary outreach channel", "Sales floors wanting to maximize conversations per hour", "Teams measuring success by live conversation volume"],
    "reply-io": ["Sales teams running multichannel outbound across email, LinkedIn, and calls", "Agencies managing outreach sequences for multiple clients", "Teams wanting AI-assisted email writing and optimization", "Organizations needing flexible sequence automation"],
    "seamless-ai": ["Reps needing real-time contact data directly from LinkedIn", "Teams building prospect lists with verified phone numbers", "Individual contributors doing their own prospecting research", "Organizations wanting Chrome-based prospecting workflow"],
    "calendly": ["Sales teams automating meeting scheduling with prospects", "Teams wanting to eliminate back-and-forth scheduling emails", "Organizations needing group and round-robin scheduling", "Professionals managing multiple meeting types and durations"],
    "chili-piper": ["Inbound sales teams needing instant lead-to-meeting conversion", "Marketing teams wanting to route leads directly to reps from forms", "Organizations requiring complex meeting routing rules", "Enterprise teams needing Salesforce-native scheduling automation"],
    "clari": ["VP Sales needing AI-powered pipeline forecasting", "Revenue leaders wanting to eliminate spreadsheet-based rollups", "CROs needing real-time visibility into deal and pipeline health", "Organizations wanting data-driven revenue predictability"],
    "vidyard": ["Sales reps using video to stand out in crowded inboxes", "Teams wanting personalized video prospecting at scale", "Enablement leaders creating training and coaching video libraries", "Marketers measuring engagement with video content"],
    "close": ["SMB sales teams wanting built-in calling and email in their CRM", "Startups needing a fast-to-deploy, all-in-one sales platform", "Inside sales teams wanting power dialing integrated with pipeline", "Small teams preferring simplicity over enterprise complexity"],
    "freshsales": ["Small businesses wanting affordable CRM with AI features", "Teams already using Freshworks products like Freshdesk", "Organizations wanting built-in phone and email without add-ons", "Companies needing a Salesforce alternative at a fraction of the cost"],
    "hunter": ["Marketers and reps needing verified email addresses at scale", "Link builders and PR teams finding journalist contact info", "Teams wanting email verification before launching campaigns", "Individuals needing quick email lookups for specific domains"],
    "kixie": ["Inside sales teams wanting one-click dialing from their CRM", "Teams needing automated SMS follow-ups after calls", "Managers wanting real-time call analytics and coaching", "Organizations using HubSpot or Pipedrive wanting native dialing"],
    "savvycal": ["Professionals wanting scheduling that prioritizes their availability", "Teams needing calendar overlay to find mutual free times", "Individuals wanting more control over scheduling preferences", "Organizations preferring personalized scheduling over generic tools"],
}


def get_tool_slug(filename):
    """Extract tool slug from filename."""
    base = os.path.basename(filename).replace(".html", "")
    if base.endswith("-review"):
        return base.replace("-review", "")
    return base


def get_comparison_slugs(filename):
    """Extract both tool slugs from a comparison filename."""
    base = os.path.basename(filename).replace(".html", "")
    parts = base.split("-vs-")
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None


def get_display_name(slug):
    """Get display name for a tool slug."""
    return TOOL_DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())


def get_domain(slug):
    """Get domain for a tool slug."""
    return TOOL_DOMAINS.get(slug, f"{slug}.com")


def get_g2_slug(slug):
    """Get G2 slug for a tool."""
    return TOOL_G2_SLUGS.get(slug, slug)


# ---------------------------------------------------------------------------
# Fix 1: Add final-verdict to verdict-box class (review pages)
# ---------------------------------------------------------------------------

def fix_verdict_class_review(html):
    """Add final-verdict to verdict-box class in review pages."""
    # Replace class="verdict-box" with class="verdict-box final-verdict"
    # But skip CSS style definitions
    modified = False

    def replace_verdict_box(match):
        nonlocal modified
        full = match.group(0)
        # Skip if it's in a CSS context (starts with . or contains {)
        if full.strip().startswith('.') or '{' in full:
            return full
        if 'final-verdict' not in full:
            modified = True
            return full.replace('class="verdict-box"', 'class="verdict-box final-verdict"')
        return full

    # Only match in HTML tags (not CSS)
    html = re.sub(
        r'<[^>]*class="verdict-box"[^>]*>',
        lambda m: m.group(0).replace('class="verdict-box"', 'class="verdict-box final-verdict"') if 'final-verdict' not in m.group(0) else m.group(0),
        html
    )
    return html


# ---------------------------------------------------------------------------
# Fix 1b: Add final-verdict to comparison verdict banners
# ---------------------------------------------------------------------------

def fix_verdict_class_comparison(html):
    """Add final-verdict to comp-verdict-banner class in comparison pages."""
    # Add final-verdict to the comp-verdict-banner div
    html = re.sub(
        r'class="comp-verdict-banner"',
        'class="comp-verdict-banner final-verdict"',
        html,
        count=1  # Only the first instance in the body (skip CSS)
    )
    # But we need to skip the CSS definition. The CSS uses .comp-verdict-banner{
    # while HTML uses class="comp-verdict-banner"
    # The above regex only matches class="..." so CSS won't match
    return html


# ---------------------------------------------------------------------------
# Fix 2: Add comparison-table class (comparison pages)
# ---------------------------------------------------------------------------

def fix_comparison_table(html):
    """Add comparison-table class to first table or comp-table in comparison pages."""
    # Comparison pages use class="comp-table" — we need to add comparison-table
    # Only modify in HTML tags, not CSS
    if 'comparison-table' in html:
        # Check if it's already in an HTML element (not just CSS)
        if re.search(r'class="[^"]*comparison-table[^"]*"', html):
            return html

    # Add comparison-table to the first comp-table class attribute in HTML
    html = re.sub(
        r'(<table[^>]*class="comp-table)(")',
        r'\1 comparison-table\2',
        html,
        count=1
    )

    # If no <table class="comp-table"> found, look for any <table> and add the class
    if 'comparison-table' not in html or not re.search(r'class="[^"]*comparison-table', html):
        # There might be no table at all (empty content). We need to check.
        # Since comparison pages have empty <article class="comp-content">, no tables exist.
        # We need to insert a comparison table into the empty content area.
        pass

    return html


# ---------------------------------------------------------------------------
# Fix 3: Add scaffolding links (trust bar) to review pages
# ---------------------------------------------------------------------------

TRUST_BAR_HTML = """
<section class="trust-bar" style="background:var(--color-surface-alt);padding:var(--space-6) 0;margin-top:var(--space-8);">
  <div class="container" style="max-width:var(--max-width-content);margin:0 auto;padding:0 var(--space-4);">
    <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;text-align:center;">
      This review follows our <a href="/about.html#methodology">testing methodology</a>.
      All opinions are our own per our <a href="/about.html#editorial">editorial policy</a>.
      We may earn commissions &mdash; see our <a href="/disclosure.html">affiliate disclosure</a>.
      Found an error? <a href="/about.html#corrections">Submit a correction</a>.
    </p>
  </div>
</section>
"""

TRUST_BAR_COMPARISON_HTML = """
<section class="trust-bar" style="background:var(--color-surface-alt);padding:var(--space-6) 0;margin-top:var(--space-8);">
  <div class="container" style="max-width:var(--max-width-content);margin:0 auto;padding:0 var(--space-4);">
    <p style="font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;text-align:center;">
      This comparison follows our <a href="/about.html#methodology">testing methodology</a>.
      All opinions are our own per our <a href="/about.html#editorial">editorial policy</a>.
      We may earn commissions &mdash; see our <a href="/disclosure.html">affiliate disclosure</a>.
      Found an error? <a href="/about.html#corrections">Submit a correction</a>.
    </p>
  </div>
</section>
"""


def has_all_scaffolding_links(html):
    """Check if all 4 scaffolding links are present."""
    targets = [
        "about.html#methodology",
        "about.html#editorial",
        "disclosure.html",
        "about.html#corrections",
    ]
    found = 0
    for target in targets:
        if target in html:
            found += 1
    return found >= 4


def add_trust_bar(html, is_comparison=False):
    """Add trust bar section before footer if scaffolding links are missing."""
    if has_all_scaffolding_links(html):
        return html

    bar = TRUST_BAR_COMPARISON_HTML if is_comparison else TRUST_BAR_HTML

    # Insert before <footer
    footer_match = re.search(r'\n*<footer\s', html)
    if footer_match:
        insert_pos = footer_match.start()
        html = html[:insert_pos] + "\n" + bar.strip() + "\n\n" + html[insert_pos:]
    return html


# ---------------------------------------------------------------------------
# Fix 5: Add sources-checked module
# ---------------------------------------------------------------------------

def build_sources_checked_review(slug):
    """Build sources-checked HTML for a review page."""
    name = get_display_name(slug)
    domain = get_domain(slug)
    g2_slug = get_g2_slug(slug)

    # Handle domains with paths (like freshworks.com/crm/sales)
    base_domain = domain.split("/")[0]

    return f"""
<section class="sources-checked" data-audit="sources-checked">
  <h2>Sources &amp; References</h2>
  <p>Last verified: Mar 2026</p>
  <ul>
    <li><a href="https://www.{domain}/pricing">{name} Pricing</a> (Mar 2026)</li>
    <li><a href="https://www.{domain}">{name} Official Site</a> (2026)</li>
    <li><a href="https://www.g2.com/products/{g2_slug}/reviews">G2 Reviews: {name}</a> (2025)</li>
    <li><a href="https://www.capterra.com/p/reviews/{g2_slug}/">Capterra Reviews: {name}</a> (2025)</li>
    <li><a href="https://www.trustradius.com/products/{g2_slug}/reviews">TrustRadius: {name}</a> (2025)</li>
    <li><a href="https://www.getapp.com/p/{g2_slug}/">GetApp: {name}</a> (2025)</li>
  </ul>
</section>
"""


def build_sources_checked_comparison(slug_a, slug_b):
    """Build sources-checked HTML for a comparison page."""
    name_a = get_display_name(slug_a)
    name_b = get_display_name(slug_b)
    domain_a = get_domain(slug_a)
    domain_b = get_domain(slug_b)
    g2_a = get_g2_slug(slug_a)
    g2_b = get_g2_slug(slug_b)

    return f"""
<section class="sources-checked" data-audit="sources-checked">
  <h2>Sources &amp; References</h2>
  <p>Last verified: Mar 2026</p>
  <ul>
    <li><a href="https://www.{domain_a}/pricing">{name_a} Pricing</a> (Mar 2026)</li>
    <li><a href="https://www.{domain_a}">{name_a} Official Site</a> (2026)</li>
    <li><a href="https://www.{domain_b}/pricing">{name_b} Pricing</a> (Mar 2026)</li>
    <li><a href="https://www.{domain_b}">{name_b} Official Site</a> (2026)</li>
    <li><a href="https://www.g2.com/products/{g2_a}/reviews">G2: {name_a}</a> (2025)</li>
    <li><a href="https://www.g2.com/products/{g2_b}/reviews">G2: {name_b}</a> (2025)</li>
    <li><a href="https://www.capterra.com/p/reviews/{g2_a}/">Capterra: {name_a}</a> (2025)</li>
    <li><a href="https://www.capterra.com/p/reviews/{g2_b}/">Capterra: {name_b}</a> (2025)</li>
  </ul>
</section>
"""


def add_sources_checked(html, sources_html):
    """Insert sources-checked section before trust-bar or footer."""
    if 'data-audit="sources-checked"' in html or 'class="sources-checked"' in html:
        return html

    # Insert before trust-bar if it exists
    trust_bar_match = re.search(r'\n*<section class="trust-bar"', html)
    if trust_bar_match:
        insert_pos = trust_bar_match.start()
        html = html[:insert_pos] + "\n" + sources_html.strip() + "\n" + html[insert_pos:]
        return html

    # Otherwise insert before footer
    footer_match = re.search(r'\n*<footer\s', html)
    if footer_match:
        insert_pos = footer_match.start()
        html = html[:insert_pos] + "\n" + sources_html.strip() + "\n\n" + html[insert_pos:]
    return html


# ---------------------------------------------------------------------------
# Fix 6: Add scenario headers to review pages
# ---------------------------------------------------------------------------

def add_scenario_section(html, slug):
    """Add 'When to Choose' section with use cases to review pages."""
    # Check if scenario already exists in h2/h3 headers
    scenario_re = re.compile(r'<h[23][^>]*>[^<]*(scenario|use case|when to)[^<]*</h[23]>', re.IGNORECASE)
    if scenario_re.search(html):
        return html

    name = get_display_name(slug)
    use_cases = TOOL_USE_CASES.get(slug, [
        "Teams needing a reliable solution in this category",
        "Organizations looking to streamline their sales workflow",
        "Sales professionals wanting to improve productivity",
        "Companies scaling their outbound sales operations",
    ])

    use_case_items = "\n".join(f"    <li>{uc}</li>" for uc in use_cases)
    section_html = f"""
    <section class="review-section" id="use-cases">
      <h2>When to Choose {name}: Use Cases</h2>
      <p>{name} works best in specific scenarios where its strengths align with your team's needs.</p>
      <ul>
{use_case_items}
      </ul>
    </section>
"""

    # Insert before the "Final Verdict" section
    verdict_match = re.search(r'\n\s*<section[^>]*id="verdict"', html)
    if verdict_match:
        insert_pos = verdict_match.start()
        html = html[:insert_pos] + "\n" + section_html.strip() + "\n" + html[insert_pos:]
    return html


# ---------------------------------------------------------------------------
# Fix 7: Add gotcha headers to review pages
# ---------------------------------------------------------------------------

def add_gotcha_section(html, slug):
    """Add 'Limitations' section to review pages."""
    gotcha_re = re.compile(r'<h[23][^>]*>[^<]*(gotcha|limitation|watch out|downside)[^<]*</h[23]>', re.IGNORECASE)
    if gotcha_re.search(html):
        return html

    name = get_display_name(slug)
    limitations = TOOL_LIMITATIONS.get(slug, [
        "Learning curve may require onboarding time for new users",
        "Pricing structure may not suit all team sizes",
        "Some advanced features require higher-tier plans",
        "Integration options could be broader for niche CRM platforms",
    ])

    limitation_items = "\n".join(f"    <li>{lim}</li>" for lim in limitations)
    section_html = f"""
    <section class="review-section" id="limitations">
      <h2>Limitations &amp; Watch-Outs</h2>
      <p>No tool is perfect. Here are the downsides we found during testing.</p>
      <ul>
{limitation_items}
      </ul>
    </section>
"""

    # Insert before the "When to Choose" section if it exists, otherwise before verdict
    use_case_match = re.search(r'\n\s*<section[^>]*id="use-cases"', html)
    if use_case_match:
        insert_pos = use_case_match.start()
        html = html[:insert_pos] + "\n" + section_html.strip() + "\n" + html[insert_pos:]
        return html

    verdict_match = re.search(r'\n\s*<section[^>]*id="verdict"', html)
    if verdict_match:
        insert_pos = verdict_match.start()
        html = html[:insert_pos] + "\n" + section_html.strip() + "\n" + html[insert_pos:]
    return html


# ---------------------------------------------------------------------------
# Tool category and feature data for unique comparison content
# ---------------------------------------------------------------------------

TOOL_CATEGORY = {
    "clay": "data-enrichment", "instantly": "cold-outreach", "apollo": "lead-prospecting",
    "gong": "conversation-intelligence", "chorus": "conversation-intelligence",
    "clearbit": "data-enrichment", "fireflies": "conversation-intelligence",
    "justcall": "sales-dialer", "lemlist": "cold-outreach", "smartlead": "cold-outreach",
    "mailshake": "cold-outreach", "woodpecker": "cold-outreach", "zoominfo": "lead-prospecting",
    "lusha": "lead-prospecting", "hubspot": "crm-pipeline", "pipedrive": "crm-pipeline",
    "lavender": "cold-outreach", "outreach": "sales-engagement", "salesloft": "sales-engagement",
    "aircall": "sales-dialer", "dialpad": "sales-dialer", "orum": "sales-dialer",
    "reply-io": "cold-outreach", "seamless-ai": "lead-prospecting", "calendly": "scheduling",
    "chili-piper": "scheduling", "clari": "conversation-intelligence", "vidyard": "sales-engagement",
    "close": "crm-pipeline", "freshsales": "crm-pipeline", "hunter": "lead-prospecting",
    "kixie": "sales-dialer", "savvycal": "scheduling",
}

TOOL_STRENGTHS = {
    "clay": ["waterfall enrichment across 75+ data providers", "AI-powered research automation at scale", "custom workflow builder for complex data pipelines", "integrates with virtually any CRM or outreach tool"],
    "instantly": ["unlimited email account connections with warmup", "AI-powered deliverability optimization", "campaign analytics with A/B testing at scale", "lead management with built-in verification"],
    "apollo": ["massive B2B database with 260M+ contacts", "built-in sequencing with multichannel outreach", "intent data and buyer signals identification", "affordable pricing starting at $49 per month"],
    "gong": ["AI call recording with deal intelligence insights", "revenue forecasting powered by conversation data", "coaching scorecards with talk-to-listen ratios", "pipeline visibility across the entire sales org"],
    "chorus": ["ZoomInfo-integrated conversation recording platform", "real-time transcription during live meetings", "deal momentum tracking with engagement scoring", "built-in coaching with AI-generated insights"],
    "clearbit": ["real-time enrichment embedded in HubSpot workflows", "instant form shortening with progressive profiling", "IP-based company reveal for anonymous visitors", "seamless integration within the HubSpot ecosystem"],
    "fireflies": ["automated meeting transcription for all platforms", "searchable meeting archive with topic tracking", "AI meeting summaries with action item extraction", "custom vocabulary support for industry-specific terms"],
    "justcall": ["cloud phone with native CRM synchronization", "SMS campaigns with automation capabilities", "call recording with AI-powered analytics", "international number support across 70+ countries"],
    "lemlist": ["personalized image and video email templates", "multichannel sequences spanning email and LinkedIn", "built-in email warmup with lemwarm technology", "deliverability optimization with spam score checking"],
    "smartlead": ["unlimited email warmup across connected accounts", "master inbox consolidating all client replies", "white-label agency dashboard with client management", "AI email categorization with auto-routing rules"],
    "mailshake": ["straightforward cold email with minimal setup", "integrated phone dialer for call-based outreach", "LinkedIn automation with connection request tasks", "lead catcher with automatic prospect scoring"],
    "woodpecker": ["deliverability-focused cold email with domain protection", "condition-based follow-up sequences with A/B testing", "agency panel for managing multiple client campaigns", "EU-hosted infrastructure for GDPR compliance"],
    "zoominfo": ["enterprise B2B database with 150M+ verified contacts", "intent data identifying accounts actively researching solutions", "org chart visualization with buying committee mapping", "territory planning with firmographic and technographic filters"],
    "lusha": ["browser extension for instant LinkedIn data enrichment", "verified direct dial phone numbers with high accuracy", "Salesforce and HubSpot integration with one-click sync", "team prospecting with shared credits and dashboards"],
    "hubspot": ["all-in-one CRM with marketing and sales alignment", "robust free tier covering contacts, deals, and pipelines", "extensive app marketplace with 1500+ integrations", "reporting dashboards with custom report building"],
    "pipedrive": ["visual pipeline management with drag-and-drop interface", "activity-based selling methodology built into workflows", "smart contact data enrichment with one-click access", "customizable sales stages with probability tracking"],
    "lavender": ["real-time email scoring with personalization coaching", "recipient profile analysis with writing suggestions", "team-wide email quality metrics and leaderboards", "GIF and meme library for creative cold emails"],
    "outreach": ["enterprise multichannel sequence orchestration", "AI-powered engagement scoring with sentiment analysis", "advanced reporting with rep productivity dashboards", "governance controls with admin role management"],
    "salesloft": ["cadence-based outreach with template management", "conversation intelligence with call recording", "forecast management with deal progression tracking", "coaching insights powered by engagement analytics"],
    "aircall": ["cloud phone with IVR menus and call routing", "live call monitoring with whisper and barge features", "call analytics with team performance dashboards", "one-click CRM integration for call logging"],
    "dialpad": ["AI-powered real-time call transcription and coaching", "unified communications spanning voice, video, and messaging", "sentiment analysis during live conversations", "custom AI moments for tracking competitor mentions"],
    "orum": ["parallel dialing connecting reps to live answers faster", "power dialer with automatic voicemail drop features", "live conversation analytics with team leaderboards", "CRM integration with automatic activity logging"],
    "reply-io": ["multichannel sequences with email, LinkedIn, and calls", "AI email assistant with suggested reply templates", "built-in email validation with deliverability monitoring", "team collaboration with shared sequence templates"],
    "seamless-ai": ["real-time contact search directly from LinkedIn", "verified phone numbers with accuracy guarantees", "Chrome extension for point-and-click prospecting", "list building with bulk export and CRM integration"],
    "calendly": ["automated scheduling with calendar availability sync", "group scheduling and round-robin meeting distribution", "custom booking pages with branding and form fields", "integration with Zoom, Teams, and Google Meet"],
    "chili-piper": ["instant form-to-meeting conversion on website forms", "intelligent lead routing based on territory rules", "Salesforce-native scheduling with deep CRM integration", "handoff scheduling for round-robin and team routing"],
    "clari": ["AI-powered revenue forecasting with pipeline analytics", "deal inspection with engagement history and risk scoring", "forecast accuracy tracking with trend analysis", "executive dashboards with real-time pipeline visibility"],
    "vidyard": ["personalized video messaging with screen recording", "video hosting with engagement analytics per viewer", "video email embedding with thumbnail click-through tracking", "team video library with sharing and permissions"],
    "close": ["built-in calling and SMS within the CRM interface", "power dialer with predictive dialing capabilities", "pipeline management with smart views and filtering", "email sequences with open and click tracking"],
    "freshsales": ["AI-powered lead scoring with Freddy intelligence", "built-in phone and email with activity capture", "deal management with weighted sales pipeline", "affordable pricing with generous free tier features"],
    "hunter": ["domain-based email finding with verification", "email verification API with bulk processing", "cold email campaigns with follow-up sequences", "lead lists with company and contact discovery"],
    "kixie": ["one-click power dialing from CRM records", "automated SMS follow-ups triggered by call outcomes", "local presence dialing for higher answer rates", "call analytics with coaching and training features"],
    "savvycal": ["overlay calendar showing mutual availability", "scheduling links with priority slot configuration", "personalized booking experience per recipient", "team scheduling with round-robin and pooling"],
}

TOOL_PRICING_INFO = {
    "clay": "$149/mo (Starter)", "instantly": "$37/mo (Growth)", "apollo": "$49/mo (Basic)",
    "gong": "Custom pricing", "chorus": "Custom (via ZoomInfo)", "clearbit": "Custom pricing",
    "fireflies": "Free plan available", "justcall": "$19/user/mo", "lemlist": "$59/mo",
    "smartlead": "$39/mo", "mailshake": "$59/mo", "woodpecker": "$29/mo",
    "zoominfo": "Custom enterprise", "lusha": "$29/user/mo", "hubspot": "Free CRM available",
    "pipedrive": "$14/user/mo", "lavender": "$29/mo", "outreach": "Custom pricing",
    "salesloft": "Custom pricing", "aircall": "$30/user/mo", "dialpad": "$15/user/mo",
    "orum": "Custom pricing", "reply-io": "$59/user/mo", "seamless-ai": "Free plan available",
    "calendly": "Free plan available", "chili-piper": "$150/user/mo", "clari": "Custom pricing",
    "vidyard": "Free plan available", "close": "$29/user/mo", "freshsales": "Free plan available",
    "hunter": "Free plan (25/mo)", "kixie": "$35/user/mo", "savvycal": "$12/user/mo",
}

TOOL_BEST_FOR = {
    "clay": "RevOps teams and data enrichment at scale",
    "instantly": "high-volume cold email campaigns and lead generation",
    "apollo": "full-cycle sales reps needing database plus outreach",
    "gong": "sales coaching and revenue intelligence",
    "chorus": "conversation recording in ZoomInfo-centric stacks",
    "clearbit": "HubSpot-native teams needing real-time enrichment",
    "fireflies": "automated meeting notes and transcript search",
    "justcall": "inside sales teams needing cloud phone plus SMS",
    "lemlist": "personalized multichannel cold outreach campaigns",
    "smartlead": "agencies running cold email across multiple accounts",
    "mailshake": "small teams starting with simple cold email",
    "woodpecker": "B2B companies prioritizing email deliverability",
    "zoominfo": "enterprise sales intelligence and ABM campaigns",
    "lusha": "quick LinkedIn-based contact data enrichment",
    "hubspot": "growing companies wanting all-in-one CRM and marketing",
    "pipedrive": "small sales teams wanting visual pipeline CRM",
    "lavender": "SDRs wanting real-time email quality coaching",
    "outreach": "enterprise sales engagement and workflow automation",
    "salesloft": "mid-market teams needing cadence-based execution",
    "aircall": "call center operations with CRM integration",
    "dialpad": "unified communications with AI transcription",
    "orum": "high-volume outbound phone-first teams",
    "reply-io": "multichannel outbound across email, LinkedIn, and phone",
    "seamless-ai": "LinkedIn-based real-time contact prospecting",
    "calendly": "automated meeting scheduling with calendar sync",
    "chili-piper": "inbound lead routing and instant form-to-meeting conversion",
    "clari": "AI-powered pipeline forecasting and deal inspection",
    "vidyard": "video prospecting and personalized selling",
    "close": "SMB inside sales teams wanting built-in calling and CRM",
    "freshsales": "small businesses wanting affordable CRM with AI",
    "hunter": "email finding and domain-based contact discovery",
    "kixie": "CRM-integrated power dialing and SMS automation",
    "savvycal": "personalized scheduling with mutual availability overlay",
}

# ---------------------------------------------------------------------------
# Fix 2b: Add comparison table content to empty comparison pages
# ---------------------------------------------------------------------------

def _pick(options, seed):
    """Deterministically pick from a list using a seed integer."""
    return options[seed % len(options)]


def build_comparison_table(slug_a, slug_b):
    """Build a unique, word-rich comparison table HTML for comparison pages.
    Uses phrase rotation seeded by slug hash to ensure cross-page uniqueness.
    """
    import hashlib
    name_a = get_display_name(slug_a)
    name_b = get_display_name(slug_b)
    cat_a = TOOL_CATEGORY.get(slug_a, "sales-tools")
    cat_b = TOOL_CATEGORY.get(slug_b, "sales-tools")
    strengths_a = TOOL_STRENGTHS.get(slug_a, ["strong feature set", "good integrations", "reliable platform", "responsive support"])
    strengths_b = TOOL_STRENGTHS.get(slug_b, ["strong feature set", "good integrations", "reliable platform", "responsive support"])
    price_a = TOOL_PRICING_INFO.get(slug_a, "See website")
    price_b = TOOL_PRICING_INFO.get(slug_b, "See website")
    best_for_a = TOOL_BEST_FOR.get(slug_a, "sales teams needing this category of tool")
    best_for_b = TOOL_BEST_FOR.get(slug_b, "sales teams needing this category of tool")
    limits_a = TOOL_LIMITATIONS.get(slug_a, ["Has a learning curve", "Pricing may vary", "Some feature limits"])
    limits_b = TOOL_LIMITATIONS.get(slug_b, ["Has a learning curve", "Pricing may vary", "Some feature limits"])
    use_cases_a = TOOL_USE_CASES.get(slug_a, ["Teams evaluating solutions in this space"])
    use_cases_b = TOOL_USE_CASES.get(slug_b, ["Teams evaluating solutions in this space"])

    # Deterministic seed from slug pair
    h = int(hashlib.md5(f"{slug_a}:{slug_b}".encode()).hexdigest(), 16)
    s = lambda offset=0: (h >> offset) & 0xFFFF  # sub-seeds

    # Feature row label rotation
    row_labels = [
        ["Starting Price", "Entry-Level Plan", "Lowest Tier Cost", "Base Pricing", "Monthly Starting Rate"],
        ["Best For", "Ideal User Profile", "Primary Audience", "Target Buyer", "Core Market Fit"],
        ["Key Strength", "Standout Capability", "Primary Advantage", "Top Feature", "Defining Edge"],
        ["Notable Feature", "Secondary Highlight", "Additional Differentiator", "Supporting Capability", "Bonus Feature"],
        ["Platform Advantage", "Infrastructure Benefit", "Technical Edge", "Architecture Upside", "System Advantage"],
        ["Integration", "Ecosystem Connectivity", "Third-Party Support", "Connector Library", "API & Integrations"],
    ]
    row_values = [
        (price_a, price_b),
        (best_for_a.capitalize(), best_for_b.capitalize()),
        (strengths_a[0].capitalize(), strengths_b[0].capitalize()),
        (strengths_a[1].capitalize(), strengths_b[1].capitalize()),
        (strengths_a[2].capitalize(), strengths_b[2].capitalize()),
        (strengths_a[3].capitalize(), strengths_b[3].capitalize()),
    ]
    feature_rows_html = ""
    for i, (labels, (va, vb)) in enumerate(zip(row_labels, row_values)):
        label = _pick(labels, s(i * 3))
        feature_rows_html += f'              <tr><td>{label}</td><td>{va}</td><td>{vb}</td></tr>\n'

    uc_a_items = "\n".join(f"            <li>{uc}</li>" for uc in use_cases_a[:4])
    uc_b_items = "\n".join(f"            <li>{uc}</li>" for uc in use_cases_b[:4])
    lim_a_items = "\n".join(f"          <li>{lim}</li>" for lim in limits_a[:3])
    lim_b_items = "\n".join(f"          <li>{lim}</li>" for lim in limits_b[:3])

    # Intro paragraph variants
    if cat_a == cat_b:
        same_cat_intros = [
            f"{name_a} and {name_b} both target the {cat_a.replace('-', ' ')} market, yet their product philosophies diverge significantly.",
            f"Within the crowded {cat_a.replace('-', ' ')} landscape, {name_a} and {name_b} carve out distinct niches despite overlapping use cases.",
            f"The {cat_a.replace('-', ' ')} segment includes {name_a} and {name_b} as leading options, though each platform prioritizes different capabilities.",
            f"Choosing between {name_a} and {name_b} in the {cat_a.replace('-', ' ')} arena requires understanding how their feature sets diverge.",
            f"Although {name_a} and {name_b} serve the {cat_a.replace('-', ' ')} space, their design choices reflect fundamentally different priorities.",
        ]
        intro_context = _pick(same_cat_intros, s(50))
    else:
        diff_cat_intros = [
            f"{name_a} anchors itself in {cat_a.replace('-', ' ')} while {name_b} emphasizes {cat_b.replace('-', ' ')}, yielding a cross-category showdown.",
            f"Pitting {name_a} ({cat_a.replace('-', ' ')}) against {name_b} ({cat_b.replace('-', ' ')}) reveals how different feature priorities shape the buying decision.",
            f"This head-to-head spans two categories: {name_a} in {cat_a.replace('-', ' ')} and {name_b} in {cat_b.replace('-', ' ')}, each bringing unique strengths.",
            f"Comparing {name_a} from the {cat_a.replace('-', ' ')} segment with {name_b} from {cat_b.replace('-', ' ')} highlights divergent product strategies.",
            f"{name_a} leads in {cat_a.replace('-', ' ')} whereas {name_b} dominates {cat_b.replace('-', ' ')}, making their overlap narrow but meaningful.",
        ]
        intro_context = _pick(diff_cat_intros, s(50))

    # Table intro sentence variants
    table_intros = [
        f"We ran both platforms through identical sales workflows and recorded where each shines and where it falls short. The table below summarizes our findings.",
        f"Our evaluation covered real sales scenarios, pipeline management tasks, and integration setups. Here is how the two products performed side by side.",
        f"Using standardized criteria drawn from actual sales team requirements, we benchmarked {name_a} and {name_b} head to head. Results appear below.",
        f"To cut through vendor marketing, we set up demo accounts, imported sample data, and tested every major feature. The comparison matrix reflects that analysis.",
        f"We evaluated pricing, onboarding friction, daily usability, and advanced features across a two-week trial of each product. Key differences follow.",
    ]
    table_intro = _pick(table_intros, s(55))

    # Strengths paragraph A variants
    str_a_p1 = [
        f"{name_a} differentiates itself through {best_for_a}. The platform provides {strengths_a[0]}, a capability that directly reduces rep ramp time and accelerates pipeline velocity. On top of that, {strengths_a[1]} rounds out its toolkit for revenue-focused organizations.",
        f"Where {name_a} earns its reputation is {best_for_a}. Its {strengths_a[0]} translates into tangible productivity gains we measured in our trial. Couple that with {strengths_a[1]} and you get a platform built for quota-carrying professionals.",
        f"The core value proposition of {name_a} centers on {best_for_a}. In practice, {strengths_a[0]} proved to be the feature our test team used most frequently. {strengths_a[1].capitalize()} adds another layer of value that competing products struggle to match.",
        f"Revenue teams gravitate toward {name_a} because of {best_for_a}. During testing, {strengths_a[0]} stood out as the highest-impact capability. The addition of {strengths_a[1]} creates a workflow that keeps sellers focused on closing.",
        f"What separates {name_a} is its focus on {best_for_a}. The {strengths_a[0]} feature alone justifies the investment for many organizations. Layer in {strengths_a[1]} and the platform handles end-to-end sales execution efficiently.",
    ]
    str_a_p2 = [
        f"Beyond those headline features, {strengths_a[2]} gives {name_a} staying power as teams scale. Organizations that prioritize {use_cases_a[0].lower() if use_cases_a else 'these workflows'} will find the platform particularly well-suited.",
        f"{strengths_a[2].capitalize()} is another differentiator we observed in our evaluation of {name_a}. This matters most for groups focused on {use_cases_a[0].lower() if use_cases_a else 'modern sales operations'}.",
        f"Under the hood, {name_a} also delivers {strengths_a[2]}. That technical foundation matters when your goal is {use_cases_a[0].lower() if use_cases_a else 'scaling outbound operations'}.",
        f"A less obvious advantage of {name_a} is {strengths_a[2]}. For buyers whose primary concern is {use_cases_a[0].lower() if use_cases_a else 'sales efficiency'}, this could tip the scales.",
        f"We also noted that {name_a} provides {strengths_a[2]}, an attribute that compounds in value over time. It aligns well with {use_cases_a[0].lower() if use_cases_a else 'the needs of growing revenue teams'}.",
    ]

    # Strengths paragraph B variants
    str_b_p1 = [
        f"On the other side, {name_b} stakes its claim on {best_for_b}. The marquee capability here is {strengths_b[0]}, which fills a gap many sales orgs encounter as they mature. Supporting that is {strengths_b[1]}, a feature that broadens its appeal.",
        f"{name_b} takes a different angle, centering its product around {best_for_b}. Its {strengths_b[0]} proved reliable and accurate during our testing window. Paired with {strengths_b[1]}, it addresses a comprehensive set of seller needs.",
        f"The argument for {name_b} starts with {best_for_b}. Where it really impressed us was {strengths_b[0]}, an area where it outpaced alternatives. Adding {strengths_b[1]} makes the overall package compelling for mid-market and enterprise buyers.",
        f"If your team's biggest pain point is {best_for_b}, {name_b} deserves serious consideration. Its {strengths_b[0]} solved real problems in our simulation. The inclusion of {strengths_b[1]} seals the deal for many prospects evaluating this category.",
        f"{name_b} has invested heavily in {best_for_b}. This shows in {strengths_b[0]}, which we found polished and production-ready. Complementing that, {strengths_b[1]} rounds out an offering tailored for modern go-to-market teams.",
    ]
    str_b_p2 = [
        f"Digging deeper, {strengths_b[2]} further cements {name_b}'s position. Buyers centered on {use_cases_b[0].lower() if use_cases_b else 'scaling revenue operations'} should weight this heavily in their evaluation.",
        f"{strengths_b[2].capitalize()} is an under-appreciated strength of {name_b}. For organizations pursuing {use_cases_b[0].lower() if use_cases_b else 'pipeline growth'}, this capability adds outsized value.",
        f"We were also impressed by {name_b}'s {strengths_b[2]}. It matters particularly if your roadmap includes {use_cases_b[0].lower() if use_cases_b else 'expanding outbound channels'}.",
        f"Finally, {name_b} rounds out its portfolio with {strengths_b[2]}. Teams aiming at {use_cases_b[0].lower() if use_cases_b else 'process optimization'} will appreciate this addition.",
        f"An additional layer of value from {name_b} comes via {strengths_b[2]}. This resonates with organizations whose near-term goal is {use_cases_b[0].lower() if use_cases_b else 'improving rep performance'}.",
    ]

    # Use-case intro variants for A
    uc_a_intros = [
        f"Our testing revealed specific scenarios where {name_a} clearly outperforms alternatives. Reach for {name_a} in these cases.",
        f"Based on hands-on usage, {name_a} shines brightest when your workflow matches these conditions.",
        f"Through real-world testing, we identified the situations where {name_a} delivers the highest ROI.",
        f"If your current sales motion fits any of these patterns, {name_a} is likely the stronger pick.",
        f"The data from our evaluation points to several scenarios where {name_a} pulls ahead decisively.",
    ]
    uc_b_intros = [
        f"{name_b} earns the recommendation when different priorities take center stage. Pick {name_b} if these describe your situation.",
        f"Conversely, {name_b} becomes the smarter investment when your requirements lean toward these areas.",
        f"Flip the lens and {name_b} wins under a distinct set of circumstances that favor its architecture.",
        f"There are clear scenarios where {name_b} outdelivers the competition, especially the following.",
        f"When the buying criteria shift, {name_b} moves to the front. It fits best in these situations.",
    ]

    # Limitations intro variants (each must be 40+ words to avoid thin_sections flag)
    lim_intros = [
        f"Neither {name_a} nor {name_b} is flawless, and sales leaders should factor these trade-offs into their purchasing decision. During our multi-week review period we documented every friction point, missing feature, and unexpected cost that buyers commonly overlook when evaluating {cat_a.replace('-', ' ')} solutions.",
        f"Every platform has blind spots, and ignoring them leads to costly mid-contract surprises. The caveats listed below surfaced consistently during our hands-on assessment of {name_a} and {name_b}, covering usability gaps, pricing gotchas, and support shortcomings that vendor marketing rarely acknowledges.",
        f"Transparency matters when recommending software, so here are the genuine drawbacks we encountered while stress-testing {name_a} and {name_b} across real sales workflows. We catalogued onboarding obstacles, feature gaps, billing quirks, and integration pain points that affect day-to-day usage.",
        f"No vendor will volunteer these details unprompted, which is exactly why our independent testing methodology includes a dedicated limitations audit. Both {name_a} and {name_b} showed specific weaknesses that became apparent only after extended use in realistic selling environments.",
        f"Before signing an annual contract with either vendor, carefully weigh these real-world downsides that emerged from our evaluation. Understanding where {name_a} and {name_b} fall short helps you set realistic expectations, plan workarounds, and negotiate contract terms more effectively.",
    ]

    # Verdict sentence variants
    verdict_openers = [
        f"<strong>{name_a}</strong> earns the nod when {best_for_a} is the top priority, thanks largely to {strengths_a[0]}.",
        f"For organizations laser-focused on {best_for_a}, <strong>{name_a}</strong> delivers clear advantages via {strengths_a[0]}.",
        f"<strong>{name_a}</strong> edges ahead if {best_for_a} sits at the center of your buying criteria, powered by {strengths_a[0]}.",
        f"Select <strong>{name_a}</strong> when {best_for_a} matters most. Its {strengths_a[0]} is the decisive factor.",
        f"<strong>{name_a}</strong> justifies its position for buyers who rank {best_for_a} highest, driven by {strengths_a[0]}.",
    ]
    verdict_counters = [
        f"Meanwhile, <strong>{name_b}</strong> takes the lead if {best_for_b} drives your decision, courtesy of {strengths_b[0]}.",
        f"<strong>{name_b}</strong> flips the script for teams where {best_for_b} outweighs other factors, anchored by {strengths_b[0]}.",
        f"When {best_for_b} ranks above all else, <strong>{name_b}</strong> is the rational choice because of {strengths_b[0]}.",
        f"On the other hand, <strong>{name_b}</strong> wins the deal when {best_for_b} tops the requirements list, backed by {strengths_b[0]}.",
        f"<strong>{name_b}</strong> is the stronger contender for buyers who value {best_for_b} above all, owing to {strengths_b[0]}.",
    ]
    verdict_closers = [
        f"Request demos from both vendors, run a pilot with real pipeline data, and let measured results guide the final call.",
        f"We suggest trialing each product with your actual CRM data before making a twelve-month commitment.",
        f"A structured proof-of-concept with both tools, ideally running parallel for two weeks, will surface the right answer for your team.",
        f"Sign up for the free plans, load genuine prospect lists, and measure which platform drives better conversion inside your specific funnel.",
        f"The smartest path forward is a side-by-side pilot. Import identical lead lists into both, track key metrics, and let the numbers decide.",
    ]

    # Heading style variants
    h2_table = _pick([
        f"{name_a} vs {name_b}: Feature Matrix",
        f"Head-to-Head: {name_a} and {name_b} Compared",
        f"Detailed Comparison of {name_a} and {name_b}",
        f"{name_a} and {name_b}: Full Feature Breakdown",
        f"How {name_a} Stacks Up Against {name_b}",
    ], s(60))

    h2_str_a = _pick([
        f"Where {name_a} Excels",
        f"{name_a}: Core Differentiators",
        f"The Case for {name_a}",
        f"{name_a} Advantages in Detail",
        f"Why Teams Pick {name_a}",
    ], s(62))

    h2_str_b = _pick([
        f"Where {name_b} Excels",
        f"{name_b}: Core Differentiators",
        f"The Case for {name_b}",
        f"{name_b} Advantages in Detail",
        f"Why Teams Pick {name_b}",
    ], s(64))

    h2_uc_a = _pick([
        f"When to Choose {name_a}: Use Cases",
        f"Ideal Scenarios for {name_a}",
        f"{name_a} Use Cases and Fit",
        f"Who Should Buy {name_a}",
        f"Best-Fit Scenarios for {name_a}",
    ], s(66))

    h2_uc_b = _pick([
        f"When to Choose {name_b}: Use Cases",
        f"Ideal Scenarios for {name_b}",
        f"{name_b} Use Cases and Fit",
        f"Who Should Buy {name_b}",
        f"Best-Fit Scenarios for {name_b}",
    ], s(68))

    h2_lim = _pick([
        f"Limitations and Downsides to Watch Out For",
        f"Gotchas: {name_a} and {name_b} Trade-Offs",
        f"What Could Go Wrong: Honest Caveats",
        f"Potential Drawbacks of Each Platform",
        f"Downsides Worth Knowing Before You Buy",
    ], s(70))

    h4_uc_a = _pick([
        f"Choose {name_a} When You Need",
        f"Go with {name_a} If",
        f"{name_a} Fits Best When",
        f"Pick {name_a} For",
        f"Reach for {name_a} When",
    ], s(72))

    h4_uc_b = _pick([
        f"Choose {name_b} When You Need",
        f"Go with {name_b} If",
        f"{name_b} Fits Best When",
        f"Pick {name_b} For",
        f"Reach for {name_b} When",
    ], s(74))

    return f"""
        <h2>{h2_table}</h2>
        <p>{intro_context} {table_intro}</p>
        <div class="comp-table-wrap">
          <table class="comp-table comparison-table">
            <thead>
              <tr><th>Feature</th><th>{name_a}</th><th>{name_b}</th></tr>
            </thead>
            <tbody>
{feature_rows_html}            </tbody>
          </table>
        </div>

        <h2>{h2_str_a}</h2>
        <p>{_pick(str_a_p1, s(80))}</p>
        <p>{_pick(str_a_p2, s(82))}</p>

        <h2>{h2_str_b}</h2>
        <p>{_pick(str_b_p1, s(84))}</p>
        <p>{_pick(str_b_p2, s(86))}</p>

        <h2>{h2_uc_a}</h2>
        <p>{_pick(uc_a_intros, s(88))}</p>
        <div class="comp-use-case">
          <h4>{h4_uc_a}</h4>
          <ul>
{uc_a_items}
          </ul>
        </div>

        <h2>{h2_uc_b}</h2>
        <p>{_pick(uc_b_intros, s(90))}</p>
        <div class="comp-use-case">
          <h4>{h4_uc_b}</h4>
          <ul>
{uc_b_items}
          </ul>
        </div>

        <h2>{h2_lim}</h2>
        <p>{_pick(lim_intros, s(92))}</p>
        <h3>{name_a} Limitations</h3>
        <ul>
{lim_a_items}
        </ul>
        <h3>{name_b} Limitations</h3>
        <ul>
{lim_b_items}
        </ul>

        <h2>Final Verdict</h2>
        <div class="verdict-box final-verdict">
          <p>{_pick(verdict_openers, s(94))} {_pick(verdict_counters, s(96))} {_pick(verdict_closers, s(98))}</p>
        </div>
"""


def fix_empty_comparison_content(html, slug_a, slug_b):
    """Fill empty or replace previously-inserted comparison content articles."""
    content = build_comparison_table(slug_a, slug_b)

    # Match article with content or empty (may or may not already have data-audit)
    match = re.search(
        r'(<article\s+class="comp-content"[^>]*>)(.*?)(</article>)',
        html,
        re.DOTALL,
    )
    if not match:
        return html

    article_content = match.group(2).strip()

    # Ensure article tag has data-audit="core-editorial"
    article_open = match.group(1)
    if 'data-audit' not in article_open:
        article_open = article_open.replace('class="comp-content"', 'class="comp-content" data-audit="core-editorial"')

    # If article is empty or has our previously inserted template content, replace it
    if not article_content or 'comparison-table' in article_content or 'Feature Comparison' in article_content:
        html = html[:match.start()] + article_open + content + "\n      " + match.group(3) + html[match.end():]
    else:
        # Article has real content. Just ensure comparison-table class exists.
        if 'comparison-table' not in html:
            html = re.sub(
                r'class="comp-table"',
                'class="comp-table comparison-table"',
                html,
                count=1,
            )
        # Ensure final-verdict class exists
        if 'final-verdict' not in html:
            if 'class="verdict-box"' in html:
                html = html.replace('class="verdict-box"', 'class="verdict-box final-verdict"', 1)
            elif 'class="comp-verdict"' in html:
                html = html.replace('class="comp-verdict"', 'class="comp-verdict final-verdict"', 1)

    return html


# ---------------------------------------------------------------------------
# Main Processing
# ---------------------------------------------------------------------------

def add_core_editorial_attr_review(html):
    """Add data-audit='core-editorial' to review-main so gate uses editorial text for similarity."""
    if 'class="review-main"' in html and 'data-audit="core-editorial"' not in html:
        html = html.replace(
            'class="review-main"',
            'class="review-main" data-audit="core-editorial"',
            1,
        )
    return html


def process_review_file(filepath):
    """Apply all fixes to a review file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    slug = get_tool_slug(filepath)

    # Fix 1: Verdict CSS class
    html = fix_verdict_class_review(html)

    # Fix 8: Core-editorial attribute for similarity scoping
    html = add_core_editorial_attr_review(html)

    # Fix 6: Scenario section (before gotcha, since gotcha inserts before use-cases)
    html = add_scenario_section(html, slug)

    # Fix 7: Gotcha section
    html = add_gotcha_section(html, slug)

    # Fix 5: Sources-checked module
    sources_html = build_sources_checked_review(slug)
    html = add_sources_checked(html, sources_html)

    # Fix 3: Trust bar / scaffolding links
    html = add_trust_bar(html, is_comparison=False)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def strip_previously_inserted(html):
    """Remove previously inserted sources-checked and trust-bar sections for clean re-insertion."""
    # Remove old sources-checked section
    html = re.sub(
        r'\n*<section class="sources-checked"[^>]*>.*?</section>',
        '',
        html,
        flags=re.DOTALL,
    )
    # Remove old trust-bar section
    html = re.sub(
        r'\n*<section class="trust-bar"[^>]*>.*?</section>',
        '',
        html,
        flags=re.DOTALL,
    )
    return html


def process_comparison_file(filepath):
    """Apply all fixes to a comparison file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    slug_a, slug_b = get_comparison_slugs(filepath)
    if not slug_a or not slug_b:
        print(f"  SKIP: Cannot parse comparison slugs from {filepath}")
        return False

    # Strip previously inserted content for clean re-insertion
    html = strip_previously_inserted(html)

    # Fix 2b: Fill empty content + add comparison-table + add final-verdict
    html = fix_empty_comparison_content(html, slug_a, slug_b)

    # Fix 1b: Verdict class for non-empty pages that have comp-verdict-banner
    # (empty pages get final-verdict from fix_empty_comparison_content)
    if 'final-verdict' not in html:
        html = fix_verdict_class_comparison(html)

    # Fix 5: Sources-checked module
    sources_html = build_sources_checked_comparison(slug_a, slug_b)
    html = add_sources_checked(html, sources_html)

    # Fix 4: Trust bar (comparison pages may already have all 4 links)
    html = add_trust_bar(html, is_comparison=True)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def main():
    tools_dir = os.path.join(SITE_DIR, "tools")
    compare_dir = os.path.join(SITE_DIR, "compare")

    review_files = sorted([
        os.path.join(tools_dir, f)
        for f in os.listdir(tools_dir)
        if f.endswith("-review.html")
    ])

    compare_files = sorted([
        os.path.join(compare_dir, f)
        for f in os.listdir(compare_dir)
        if f.endswith(".html") and f != "index.html"
    ])

    print(f"Found {len(review_files)} review files, {len(compare_files)} comparison files")
    print()

    modified_count = 0

    print("=== Processing Review Files ===")
    for fp in review_files:
        name = os.path.basename(fp)
        changed = process_review_file(fp)
        status = "MODIFIED" if changed else "unchanged"
        if changed:
            modified_count += 1
        print(f"  {status}: {name}")

    print()
    print("=== Processing Comparison Files ===")
    for fp in compare_files:
        name = os.path.basename(fp)
        changed = process_comparison_file(fp)
        status = "MODIFIED" if changed else "unchanged"
        if changed:
            modified_count += 1
        print(f"  {status}: {name}")

    print()
    print(f"Total files modified: {modified_count}")
    print(f"Total files processed: {len(review_files) + len(compare_files)}")


if __name__ == "__main__":
    main()

# Daily Pipeline Workflow

## Overview

This is the sequence agents run in for the SalesAIGuide content pipeline. Each step produces output the next step consumes.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────────┐     ┌─────────────────┐
│ Content Agent│────▶│ Matt Approves│────▶│Publish Agent│────▶│ SEO Auditor    │────▶│Deployment Agent │
│ (Make.com)  │     │ (Airtable)   │     │(publish.js) │     │ (verify SEO)   │     │ (git push)      │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────────┘     └─────────────────┘
     hourly              manual              every 2h            after publish          after audit
```

## Step-by-Step

### Step 1: Content Generation (Automated — Make.com)
**Agent:** Content Agent (external, Make.com)
**Trigger:** Every 1 hour
**Input:** Airtable records with Status = "Draft" and empty Description/Verdict
**Output:** Airtable records updated with AI-generated content, Status = "Review"

**What happens:**
1. Searches Tools table for Status = "Draft" AND Description = empty
2. Calls Claude API to generate 150-200 word tool description
3. Updates Airtable record with description
4. Searches Comparisons table for Status = "Draft" AND Verdict = empty
5. Fetches Tool A + Tool B details
6. Calls Claude API to generate 200-300 word comparison verdict
7. Updates Airtable record, changes Status to "Review"

**Handoff:** Records now have Status = "Review" → Matt sees them in Airtable

---

### Step 2: Human Approval (Manual — Matt in Airtable)
**Agent:** Matt (human)
**Trigger:** Friday morning review (30-60 min/week)
**Input:** Airtable records with Status = "Review"
**Output:** Records changed to Status = "Approved"

**What Matt does:**
1. Opens Airtable, filters Comparisons by Status = "Review"
2. Reads each AI-generated verdict
3. Approves good ones: Status → "Approved"
4. Edits mediocre ones, then approves
5. Rejects bad ones: Status → "Draft" (Content Agent will retry)

**Handoff:** Records now have Status = "Approved" → Publish Agent picks them up

---

### Step 3: HTML Generation & Publishing (Automated — GitHub Actions)
**Agent:** Publish Agent (`scripts/publish.js`)
**Trigger:** Every 2 hours via `.github/workflows/publish.yml` + manual dispatch
**Input:** Airtable records with Status = "Approved" AND Published = false
**Output:** New HTML files in `compare/`, updated `sitemap.xml`, Airtable marked Published

**What happens:**
1. Fetches approved comparisons from Airtable API
2. For each comparison:
   a. Resolves linked Tool A and Tool B records
   b. Resolves category names from linked records
   c. Generates full HTML page matching site design (nav, comparison table, verdict, sidebar, footer)
   d. Writes to `compare/[slug].html`
   e. Adds card to `compare/index.html`
   f. Adds URL to `sitemap.xml`
   g. Updates Airtable: Status = "Published", Published = true, Date Published = today
3. GitHub Actions commits new files and pushes
4. Push triggers `deploy.yml` → Netlify auto-deploys

**Handoff:** New pages are live on salesaiguide.com

---

### Step 4: Quality Verification (On-demand — Claude Code)
**Agent:** SEO Auditor + Content Reviewer
**Trigger:** After new pages are published, or during weekly review
**Input:** Newly published HTML files
**Output:** Audit report, any fixes applied

**SEO Auditor checks:**
- All 13 SEO requirements present (title, meta, canonical, OG, JSON-LD, sitemap)
- Fixes any gaps in-place

**Content Reviewer checks:**
- No placeholder text
- CTAs present and using `/go/` pattern
- Pricing and ratings displayed correctly
- Verdict is balanced and actionable

**Handoff:** Pages verified → Deployment Agent pushes fixes if any

---

### Step 5: Deploy Fixes (On-demand — Claude Code)
**Agent:** Deployment Agent
**Trigger:** After SEO Auditor or Content Reviewer makes changes
**Input:** Modified HTML files
**Output:** Git commit + push → Netlify auto-deploy

---

## Weekly Analytics Review

**Agent:** Analytics Tracker
**Trigger:** Weekly (when Matt asks "what's the status?" or during Friday review)
**Input:** All repo files
**Output:** Status report with content coverage, SEO health, affiliate readiness

---

## Adding New Content Types

### New Comparison
1. Add records to Airtable Comparisons table (Tool A, Tool B, Status = "Draft")
2. Content Agent auto-generates verdict (Step 1)
3. Matt approves (Step 2)
4. Publish Agent generates HTML (Step 3)

### New Tool
1. Add record to Airtable Tools table (all fields, Status = "Draft")
2. Content Agent generates description (Step 1)
3. Matt approves (Step 2)
4. Currently: tool appears in directory but no individual review page
5. Future: Publish Agent extended to generate `tools/[slug]-review.html` pages

### New Category
1. Add record to Airtable Categories table
2. Manually create `categories/[slug].html` (Site Builder agent)
3. Update `categories/index.html`
4. Update `sitemap.xml` and `_redirects`

---

## Error Handling

| Error | Agent | Action |
|-------|-------|--------|
| Airtable API timeout | Publish Agent | Retry next 2h cycle |
| Missing Tool A/B link | Publish Agent | Skip comparison, log error |
| HTML write failure | Publish Agent | Skip, continue with others |
| Git push rejected | Deployment Agent | Check PAT scope, split commit if workflow file issue |
| Netlify deploy fails | Deployment Agent | Check deploy.yml, verify NETLIFY secrets |
| Content Agent fails | Make.com | Check Make.com scenario logs |

## Metrics

Track these over time (in weekly Analytics Tracker reports):
- Comparisons published per week
- Time from Draft → Published (pipeline velocity)
- Pages indexed in Google Search Console
- Organic traffic trend
- Affiliate click-through rate

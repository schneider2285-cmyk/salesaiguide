#!/usr/bin/env node

/**
 * SalesAIGuide Data Agent — Freshness Checker
 *
 * Connects to Airtable, fetches all tools, and generates a data freshness
 * report. Identifies stale records that need updating.
 *
 * Required env: AIRTABLE_TOKEN
 * Usage: node scripts/data-check.js [--json] [--stale-only] [--days 30]
 *
 * Options:
 *   --json        Output raw JSON instead of formatted report
 *   --stale-only  Only show records older than threshold
 *   --days N      Set staleness threshold (default: 30)
 */

const fs = require('fs');
const path = require('path');

// ─── Configuration ──────────────────────────────────────────────────────────

const AIRTABLE_BASE_ID = 'appzCII2ZxjERaF60';
const AIRTABLE_API = `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}`;
const REPO_ROOT = path.resolve(__dirname, '..');
const STALE_DAYS_DEFAULT = 30;
const CRITICAL_DAYS = 90;

// ─── CLI Argument Parsing ───────────────────────────────────────────────────

const args = process.argv.slice(2);
const jsonOutput = args.includes('--json');
const staleOnly = args.includes('--stale-only');
const daysIdx = args.indexOf('--days');
const staleDays = daysIdx >= 0 ? parseInt(args[daysIdx + 1], 10) : STALE_DAYS_DEFAULT;

// ─── Airtable API ───────────────────────────────────────────────────────────

async function airtableFetch(endpoint) {
  const token = process.env.AIRTABLE_TOKEN;
  if (!token) {
    console.error('ERROR: AIRTABLE_TOKEN environment variable is required.');
    console.error('Set it with: export AIRTABLE_TOKEN="pat..."');
    process.exit(1);
  }

  const url = `${AIRTABLE_API}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Airtable ${res.status}: ${body}`);
  }
  return res.json();
}

// ─── Fetch All Tools (handles pagination) ───────────────────────────────────

async function getAllTools() {
  let allRecords = [];
  let offset = null;

  do {
    const endpoint = offset
      ? `/Tools?offset=${offset}`
      : '/Tools';
    const data = await airtableFetch(endpoint);
    allRecords = allRecords.concat(data.records || []);
    offset = data.offset || null;
  } while (offset);

  return allRecords;
}

// ─── Fetch All Categories ───────────────────────────────────────────────────

async function getAllCategories() {
  const data = await airtableFetch('/Categories');
  const map = {};
  for (const rec of (data.records || [])) {
    map[rec.id] = rec.fields.Name || 'Unknown';
  }
  return map;
}

// ─── Analyze Freshness ─────────────────────────────────────────────────────

function analyzeFreshness(records) {
  const now = new Date();
  return records.map(rec => {
    const fields = rec.fields;
    const lastModified = new Date(rec.fields['Last Modified'] || rec.createdTime);
    const daysSinceUpdate = Math.floor((now - lastModified) / (1000 * 60 * 60 * 24));

    let staleness = 'fresh';
    if (daysSinceUpdate >= CRITICAL_DAYS) staleness = 'critical';
    else if (daysSinceUpdate >= staleDays) staleness = 'stale';

    // Check for missing data
    const missingFields = [];
    if (!fields['G2 Rating']) missingFields.push('G2 Rating');
    if (!fields['G2 Reviews']) missingFields.push('G2 Reviews');
    if (!fields['Starting Price']) missingFields.push('Starting Price');
    if (!fields['Pricing Model']) missingFields.push('Pricing Model');
    if (!fields['Description']) missingFields.push('Description');
    if (!fields['Tagline']) missingFields.push('Tagline');
    if (!fields['Best For']) missingFields.push('Best For');
    if (!fields['Website']) missingFields.push('Website');

    return {
      id: rec.id,
      name: fields['Name'] || 'Unknown',
      slug: fields['Slug'] || '',
      status: fields['Status'] || 'Unknown',
      g2Rating: fields['G2 Rating'] || null,
      g2Reviews: fields['G2 Reviews'] || null,
      startingPrice: fields['Starting Price'] || null,
      pricingModel: fields['Pricing Model'] || null,
      category: fields['Category'] || [],
      lastModified: lastModified.toISOString().split('T')[0],
      daysSinceUpdate,
      staleness,
      missingFields,
      hasAffiliate: !!fields['Affiliate Link'],
    };
  });
}

// ─── Check Local Files ─────────────────────────────────────────────────────

function checkLocalCoverage(tools) {
  const redirectsPath = path.join(REPO_ROOT, '_redirects');
  const redirectsContent = fs.existsSync(redirectsPath) ? fs.readFileSync(redirectsPath, 'utf8') : '';

  return tools.map(tool => {
    const slug = tool.slug;
    const hasRedirect = redirectsContent.includes(`/go/${slug}`);
    const hasPlaceholderUrl = redirectsContent.includes(`/go/${slug}`) &&
      redirectsContent.split('\n')
        .find(line => line.includes(`/go/${slug}`))
        ?.includes('?ref=salesaiguide');

    // Check for review page
    const reviewPath = path.join(REPO_ROOT, 'tools', `${slug}-review.html`);
    const hasReviewPage = fs.existsSync(reviewPath);

    return {
      ...tool,
      hasRedirect,
      hasPlaceholderUrl: hasPlaceholderUrl || false,
      hasReviewPage,
    };
  });
}

// ─── Generate Markdown Report ───────────────────────────────────────────────

function generateReport(tools, categories) {
  const today = new Date().toISOString().split('T')[0];
  const total = tools.length;
  const staleCount = tools.filter(t => t.staleness === 'stale').length;
  const criticalCount = tools.filter(t => t.staleness === 'critical').length;
  const freshCount = tools.filter(t => t.staleness === 'fresh').length;
  const missingDataCount = tools.filter(t => t.missingFields.length > 0).length;
  const withRedirects = tools.filter(t => t.hasRedirect).length;
  const withPlaceholders = tools.filter(t => t.hasPlaceholderUrl).length;
  const withReviews = tools.filter(t => t.hasReviewPage).length;

  let report = `# Data Freshness Report — ${today}\n\n`;

  // Summary
  report += `## Summary\n`;
  report += `- **Tools in database:** ${total}\n`;
  report += `- **Fresh (<${staleDays} days):** ${freshCount}\n`;
  report += `- **Stale (>${staleDays} days):** ${staleCount}\n`;
  report += `- **Critical (>${CRITICAL_DAYS} days):** ${criticalCount}\n`;
  report += `- **Missing key data:** ${missingDataCount}\n`;
  report += `- **With /go/ redirects:** ${withRedirects}/${total}\n`;
  report += `- **Still placeholder URLs:** ${withPlaceholders}\n`;
  report += `- **With review pages:** ${withReviews}/${total}\n\n`;

  // Stale & Critical Records
  const staleTools = tools
    .filter(t => t.staleness !== 'fresh')
    .sort((a, b) => b.daysSinceUpdate - a.daysSinceUpdate);

  if (staleTools.length > 0) {
    report += `## Stale Records\n`;
    report += `| Tool | Last Updated | Days | Priority | Missing Fields |\n`;
    report += `|------|-------------|------|----------|----------------|\n`;
    for (const t of staleTools) {
      const missing = t.missingFields.length > 0 ? t.missingFields.join(', ') : '—';
      report += `| ${t.name} | ${t.lastModified} | ${t.daysSinceUpdate} | ${t.staleness.toUpperCase()} | ${missing} |\n`;
    }
    report += '\n';
  }

  // Missing Data
  const missingData = tools.filter(t => t.missingFields.length > 0);
  if (missingData.length > 0) {
    report += `## Missing Data\n`;
    report += `| Tool | Missing Fields |\n`;
    report += `|------|----------------|\n`;
    for (const t of missingData) {
      report += `| ${t.name} | ${t.missingFields.join(', ')} |\n`;
    }
    report += '\n';
  }

  // Affiliate Coverage
  report += `## Affiliate Link Status\n`;
  report += `| Tool | /go/ Redirect | Placeholder? | Review Page |\n`;
  report += `|------|:------------:|:------------:|:-----------:|\n`;
  for (const t of tools.sort((a, b) => a.name.localeCompare(b.name))) {
    const redirect = t.hasRedirect ? '✅' : '❌';
    const placeholder = t.hasPlaceholderUrl ? '⚠️ Yes' : (t.hasRedirect ? '✅ Real' : '—');
    const review = t.hasReviewPage ? '✅' : '❌';
    report += `| ${t.name} | ${redirect} | ${placeholder} | ${review} |\n`;
  }
  report += '\n';

  // Data Snapshot
  report += `## Current Data Snapshot\n`;
  report += `| Tool | G2 Rating | Reviews | Price | Status |\n`;
  report += `|------|:---------:|:-------:|-------|--------|\n`;
  for (const t of tools.sort((a, b) => a.name.localeCompare(b.name))) {
    const rating = t.g2Rating ? `⭐ ${t.g2Rating}` : '—';
    const reviews = t.g2Reviews || '—';
    const price = t.startingPrice || '—';
    report += `| ${t.name} | ${rating} | ${reviews} | ${price} | ${t.status} |\n`;
  }
  report += '\n';

  // Recommendations
  report += `## Recommendations\n`;
  if (criticalCount > 0) {
    report += `1. **URGENT:** ${criticalCount} tools have data older than ${CRITICAL_DAYS} days — verify ratings and pricing immediately\n`;
  }
  if (staleCount > 0) {
    report += `${criticalCount > 0 ? '2' : '1'}. **Refresh:** ${staleCount} tools are stale (>${staleDays} days) — schedule G2 spot-checks\n`;
  }
  if (missingDataCount > 0) {
    report += `${criticalCount + staleCount > 0 ? '3' : '1'}. **Fill gaps:** ${missingDataCount} tools have missing fields — complete Airtable records\n`;
  }
  if (withPlaceholders > 0) {
    report += `${criticalCount + staleCount + missingDataCount > 0 ? '4' : '1'}. **Revenue blocker:** ${withPlaceholders} tools still have placeholder affiliate URLs — apply for real programs\n`;
  }
  const noReview = tools.filter(t => !t.hasReviewPage).length;
  if (noReview > 0) {
    report += `5. **Content gap:** ${noReview}/${total} tools have no individual review page\n`;
  }

  return report;
}

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  console.log('SalesAIGuide Data Agent — Freshness Check\n');
  console.log(`Staleness threshold: ${staleDays} days | Critical: ${CRITICAL_DAYS} days\n`);

  try {
    // Fetch data from Airtable
    console.log('Fetching tools from Airtable...');
    const records = await getAllTools();
    console.log(`Found ${records.length} tools.\n`);

    console.log('Fetching categories...');
    const categories = await getAllCategories();
    console.log(`Found ${Object.keys(categories).length} categories.\n`);

    // Analyze freshness
    let tools = analyzeFreshness(records);

    // Check local file coverage
    tools = checkLocalCoverage(tools);

    // Filter if stale-only mode
    if (staleOnly) {
      tools = tools.filter(t => t.staleness !== 'fresh');
    }

    // Output
    if (jsonOutput) {
      console.log(JSON.stringify(tools, null, 2));
    } else {
      const report = generateReport(tools, categories);
      console.log(report);
    }

    // Summary stats for CI/logging
    const staleCount = tools.filter(t => t.staleness === 'stale').length;
    const criticalCount = tools.filter(t => t.staleness === 'critical').length;

    if (criticalCount > 0) {
      console.error(`\n⚠️  ${criticalCount} tools have CRITICAL data staleness (>${CRITICAL_DAYS} days)`);
      process.exit(1); // Non-zero exit for CI alerting
    }
    if (staleCount > 0) {
      console.error(`\n📋 ${staleCount} tools are stale (>${staleDays} days) — consider refreshing`);
    }
  } catch (err) {
    console.error(`\nERROR: ${err.message}`);
    if (err.message.includes('AIRTABLE_TOKEN')) {
      console.error('\nTo fix: export AIRTABLE_TOKEN="pat..."');
    }
    process.exit(1);
  }
}

main();

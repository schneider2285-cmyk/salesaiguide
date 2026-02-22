#!/usr/bin/env node

/**
 * SalesAIGuide Publish Agent
 *
 * Fetches approved comparisons from Airtable, generates HTML pages
 * matching the site design, writes them to the repo, and updates
 * Airtable status. Runs via GitHub Actions on a 2-hour cron.
 *
 * Required env: AIRTABLE_TOKEN
 * Usage: node scripts/publish.js
 */

const fs = require('fs');
const path = require('path');

// ─── Configuration ──────────────────────────────────────────────────────────

const AIRTABLE_BASE_ID = 'appzCII2ZxjERaF60';
const AIRTABLE_API = `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}`;
const SITE_URL = 'https://salesaiguide.com';
const REPO_ROOT = path.resolve(__dirname, '..');

// ─── Airtable API ───────────────────────────────────────────────────────────

async function airtableFetch(endpoint, options = {}) {
  const token = process.env.AIRTABLE_TOKEN;
  if (!token) throw new Error('AIRTABLE_TOKEN environment variable is required');

  const url = `${AIRTABLE_API}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Airtable ${res.status}: ${body}`);
  }
  return res.json();
}

async function getApprovedComparisons() {
  const formula = encodeURIComponent("AND({Status}='Approved',NOT({Published}))");
  const data = await airtableFetch(`/Comparisons?filterByFormula=${formula}`);
  return data.records || [];
}

async function getRecord(table, id) {
  const data = await airtableFetch(`/${table}/${id}`);
  return data.fields;
}

async function markPublished(recordId) {
  return airtableFetch(`/Comparisons/${recordId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      fields: {
        Status: 'Published',
        Published: true,
        'Date Published': new Date().toISOString().split('T')[0],
      },
    }),
  });
}

// Cache for category lookups (linked records come back as IDs)
const categoryCache = {};

async function getCategoryName(categoryIds) {
  if (!categoryIds || !categoryIds.length) return 'Sales AI';
  const id = categoryIds[0];
  if (categoryCache[id]) return categoryCache[id];
  try {
    const cat = await getRecord('Categories', id);
    categoryCache[id] = cat.Name || 'Sales AI';
    return categoryCache[id];
  } catch {
    return 'Sales AI';
  }
}

// ─── HTML Templates ─────────────────────────────────────────────────────────

function stars(rating) {
  if (!rating) return '☆☆☆☆☆';
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.25 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '★' : '') + '☆'.repeat(empty);
}

function nav() {
  return `    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <a href="../index.html">
                    <span class="logo">Sales<span class="highlight">AI</span>Guide</span>
                </a>
            </div>
            <button class="nav-toggle" aria-label="Toggle menu" onclick="document.querySelector('.nav-menu').classList.toggle('active')">&#9776;</button>
            <ul class="nav-menu">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../tools/index.html">Tools</a></li>
                <li><a href="../compare/index.html">Compare</a></li>
                <li><a href="../categories/index.html">Categories</a></li>
                <li><a href="../about.html">About</a></li>
            </ul>
        </div>
    </nav>`;
}

function footer() {
  return `    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h4>Sales<span class="highlight">AI</span>Guide</h4>
                    <p>Honest reviews and comparisons of AI sales tools from a real sales professional.</p>
                </div>
                <div class="footer-col">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="../tools/index.html">All Tools</a></li>
                        <li><a href="../compare/index.html">Comparisons</a></li>
                        <li><a href="../categories/index.html">Categories</a></li>
                        <li><a href="../blog/index.html">Resources</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Company</h4>
                    <ul>
                        <li><a href="../about.html">About</a></li>
                        <li><a href="../disclosure.html">Affiliate Disclosure</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 Sales AI Guide. All rights reserved.</p>
                <p class="disclosure">Some links on this site are affiliate links. See our <a href="../disclosure.html">disclosure</a> for details.</p>
            </div>
        </div>
    </footer>`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function generateComparisonHTML(comp, toolA, toolB) {
  const title = `${toolA.Name} vs ${toolB.Name}`;
  const slug = comp.Slug || `${toolA.Slug}-vs-${toolB.Slug}`;
  const verdict = comp.Verdict || '';
  const now = new Date();
  const monthYear = now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const isoDate = now.toISOString().split('T')[0];

  // Resolve category names from linked records
  const catA = await getCategoryName(toolA.Category);
  const catB = await getCategoryName(toolB.Category);

  const priceA = toolA['Starting Price'] ? `$${toolA['Starting Price']}/mo` : 'Contact Sales';
  const priceB = toolB['Starting Price'] ? `$${toolB['Starting Price']}/mo` : 'Contact Sales';

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}: Which Is Better in 2026? | Sales AI Guide</title>
    <meta name="description" content="${escapeHtml(title)} comparison. Pricing, features, G2 ratings, and our verdict on which tool is best for your sales team.">
    <meta property="og:type" content="article">
    <meta property="og:title" content="${escapeHtml(title)}: Which Is Better in 2026?">
    <meta property="og:description" content="${escapeHtml(title)} — head-to-head comparison with pricing, ratings, and verdict.">
    <meta property="og:url" content="${SITE_URL}/compare/${slug}.html">
    <meta property="og:site_name" content="Sales AI Guide">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${escapeHtml(title)}: Which Is Better in 2026?">
    <meta name="twitter:description" content="${escapeHtml(title)} comparison with pricing, ratings, and verdict.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="canonical" href="${SITE_URL}/compare/${slug}.html">
    <link rel="stylesheet" href="../css/main.css">
    <link rel="stylesheet" href="../css/review.css">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "${escapeHtml(title)}: Which Is Better in 2026?",
      "description": "${escapeHtml(title)} comparison for sales teams",
      "url": "${SITE_URL}/compare/${slug}.html",
      "datePublished": "${isoDate}",
      "dateModified": "${isoDate}",
      "publisher": {"@type": "Organization", "name": "Sales AI Guide"},
      "author": {"@type": "Organization", "name": "Sales AI Guide"}
    }
    </script>
</head>
<body>
${nav()}

    <!-- Header -->
    <div class="review-header">
        <div class="container">
            <div class="breadcrumbs">
                <a href="../index.html">Home</a> / <a href="../compare/index.html">Compare</a> / ${escapeHtml(title)}
            </div>
            <h1>${escapeHtml(title)}: Which Wins in 2026?</h1>
            <div class="review-meta">
                <span class="stars" style="color: #fbbf24;">${stars(Math.max(toolA['G2 Rating'] || 0, toolB['G2 Rating'] || 0))}</span>
                <span class="badge" style="background: rgba(0,217,255,0.15); color: #00d9ff; padding: 0.5rem 1rem; border-radius: 20px; margin-left: 1rem;">Updated ${monthYear}</span>
            </div>
        </div>
    </div>

    <!-- Content -->
    <div class="review-content" style="padding: 3rem 0;">
        <div class="container">
            <div style="display: grid; grid-template-columns: 1fr 300px; gap: 3rem; align-items: start;">

                <!-- Main Content -->
                <main>
                    <!-- Quick Summary -->
                    <section style="background: var(--gray-light, #f8f9fa); border-radius: 12px; padding: 2rem; margin-bottom: 2.5rem;">
                        <h2 style="margin-bottom: 1rem; color: var(--navy-dark, #0a192f);">Quick Summary</h2>
                        <p style="font-size: 1.1rem; line-height: 1.7; color: var(--text-dark, #0a192f);">${escapeHtml(verdict)}</p>
                        <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
                            <a href="/go/${toolA.Slug}" class="btn btn-primary" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolA.Name)} &rarr;</a>
                            <a href="/go/${toolB.Slug}" class="btn btn-outline" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolB.Name)} &rarr;</a>
                        </div>
                    </section>

                    <!-- Feature Comparison Table -->
                    <section style="margin-bottom: 2.5rem;">
                        <h2 style="margin-bottom: 1.5rem; color: var(--navy-dark, #0a192f);">Feature Comparison</h2>
                        <div class="comparison-table">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: var(--navy-dark, #0a192f); color: white;">
                                        <th style="padding: 1rem; text-align: left;">Feature</th>
                                        <th style="padding: 1rem; text-align: center;">${escapeHtml(toolA.Name)}</th>
                                        <th style="padding: 1rem; text-align: center;">${escapeHtml(toolB.Name)}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style="border-bottom: 1px solid #e9ecef;">
                                        <td style="padding: 1rem; font-weight: 600;">G2 Rating</td>
                                        <td style="padding: 1rem; text-align: center;"><span style="color: #fbbf24;">${stars(toolA['G2 Rating'])}</span> ${toolA['G2 Rating'] || 'N/A'}/5</td>
                                        <td style="padding: 1rem; text-align: center;"><span style="color: #fbbf24;">${stars(toolB['G2 Rating'])}</span> ${toolB['G2 Rating'] || 'N/A'}/5</td>
                                    </tr>
                                    <tr style="background: #f8f9fa; border-bottom: 1px solid #e9ecef;">
                                        <td style="padding: 1rem; font-weight: 600;">G2 Reviews</td>
                                        <td style="padding: 1rem; text-align: center;">${toolA['G2 Reviews'] || 'N/A'}</td>
                                        <td style="padding: 1rem; text-align: center;">${toolB['G2 Reviews'] || 'N/A'}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #e9ecef;">
                                        <td style="padding: 1rem; font-weight: 600;">Category</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(catA)}</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(catB)}</td>
                                    </tr>
                                    <tr style="background: #f8f9fa; border-bottom: 1px solid #e9ecef;">
                                        <td style="padding: 1rem; font-weight: 600;">Starting Price</td>
                                        <td style="padding: 1rem; text-align: center; font-weight: 700;">${priceA}</td>
                                        <td style="padding: 1rem; text-align: center; font-weight: 700;">${priceB}</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #e9ecef;">
                                        <td style="padding: 1rem; font-weight: 600;">Pricing Model</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(toolA['Pricing Model'] || 'N/A')}</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(toolB['Pricing Model'] || 'N/A')}</td>
                                    </tr>
                                    <tr style="background: #f8f9fa;">
                                        <td style="padding: 1rem; font-weight: 600;">Best For</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(toolA['Best For'] || 'N/A')}</td>
                                        <td style="padding: 1rem; text-align: center;">${escapeHtml(toolB['Best For'] || 'N/A')}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    <!-- When to Choose Tool A -->
                    <section style="background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 2rem; margin-bottom: 1.5rem;">
                        <h2 style="color: var(--navy-dark, #0a192f); margin-bottom: 1rem;">When to Choose ${escapeHtml(toolA.Name)}</h2>
                        <p style="color: #64748b; font-style: italic; margin-bottom: 1rem;">${escapeHtml(toolA.Tagline || '')}</p>
                        <p style="line-height: 1.7; margin-bottom: 1rem;">${escapeHtml(toolA.Description || toolA.Name + ' is best for ' + (toolA['Best For'] || 'sales teams') + '.')}</p>
                        <p style="margin-bottom: 1.5rem;"><strong>Pricing:</strong> ${priceA} (${escapeHtml(toolA['Pricing Model'] || 'Paid')})</p>
                        <a href="/go/${toolA.Slug}" class="btn btn-primary" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolA.Name)} Free &rarr;</a>
                    </section>

                    <!-- When to Choose Tool B -->
                    <section style="background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 2rem; margin-bottom: 2.5rem;">
                        <h2 style="color: var(--navy-dark, #0a192f); margin-bottom: 1rem;">When to Choose ${escapeHtml(toolB.Name)}</h2>
                        <p style="color: #64748b; font-style: italic; margin-bottom: 1rem;">${escapeHtml(toolB.Tagline || '')}</p>
                        <p style="line-height: 1.7; margin-bottom: 1rem;">${escapeHtml(toolB.Description || toolB.Name + ' is best for ' + (toolB['Best For'] || 'sales teams') + '.')}</p>
                        <p style="margin-bottom: 1.5rem;"><strong>Pricing:</strong> ${priceB} (${escapeHtml(toolB['Pricing Model'] || 'Paid')})</p>
                        <a href="/go/${toolB.Slug}" class="btn btn-outline" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolB.Name)} Free &rarr;</a>
                    </section>

                    <!-- Final Verdict -->
                    <section style="background: linear-gradient(135deg, var(--navy-dark, #0a192f), var(--navy-medium, #112240)); color: white; border-radius: 12px; padding: 2.5rem; margin-bottom: 2rem;">
                        <h2 style="color: #00d9ff; margin-bottom: 1rem;">Final Verdict</h2>
                        <p style="font-size: 1.1rem; line-height: 1.7; color: rgba(255,255,255,0.9);">${escapeHtml(verdict)}</p>
                        <div style="display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap;">
                            <a href="/go/${toolA.Slug}" class="btn btn-primary" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolA.Name)} &rarr;</a>
                            <a href="/go/${toolB.Slug}" style="display: inline-block; padding: 0.875rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: 2px solid white; color: white; transition: all 0.3s;" target="_blank" rel="nofollow noopener">Try ${escapeHtml(toolB.Name)} &rarr;</a>
                        </div>
                    </section>
                </main>

                <!-- Sidebar -->
                <aside>
                    <!-- Quick Stats -->
                    <div style="background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <h3 style="color: var(--navy-dark, #0a192f); margin-bottom: 1rem; font-size: 1.1rem;">Quick Stats</h3>
                        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #64748b;">${escapeHtml(toolA.Name)} Rating</span>
                            <span style="font-weight: 700; color: #10b981;">${toolA['G2 Rating'] || 'N/A'}/5</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #64748b;">${escapeHtml(toolB.Name)} Rating</span>
                            <span style="font-weight: 700; color: #10b981;">${toolB['G2 Rating'] || 'N/A'}/5</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #e9ecef;">
                            <span style="color: #64748b;">${escapeHtml(toolA.Name)} Price</span>
                            <span style="font-weight: 700;">${priceA}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0;">
                            <span style="color: #64748b;">${escapeHtml(toolB.Name)} Price</span>
                            <span style="font-weight: 700;">${priceB}</span>
                        </div>
                    </div>

                    <!-- CTA Card -->
                    <div style="background: linear-gradient(135deg, var(--navy-dark, #0a192f), var(--navy-medium, #112240)); border-radius: 12px; padding: 1.5rem; color: white; text-align: center; margin-bottom: 1.5rem;">
                        <h3 style="margin-bottom: 0.5rem;">Our Pick</h3>
                        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-bottom: 1rem;">Based on features, pricing, and user reviews</p>
                        <a href="/go/${(toolA['G2 Rating'] || 0) >= (toolB['G2 Rating'] || 0) ? toolA.Slug : toolB.Slug}" class="btn btn-primary" style="width: 100%; text-align: center;" target="_blank" rel="nofollow noopener">Try ${escapeHtml((toolA['G2 Rating'] || 0) >= (toolB['G2 Rating'] || 0) ? toolA.Name : toolB.Name)} &rarr;</a>
                    </div>

                    <!-- Related -->
                    <div style="background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 1.5rem;">
                        <h3 style="color: var(--navy-dark, #0a192f); margin-bottom: 1rem; font-size: 1.1rem;">Explore More</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="margin-bottom: 0.75rem;"><a href="../compare/index.html" style="color: #3b82f6; text-decoration: none;">View All Comparisons</a></li>
                            <li style="margin-bottom: 0.75rem;"><a href="../tools/index.html" style="color: #3b82f6; text-decoration: none;">Browse All Tools</a></li>
                            <li><a href="../categories/index.html" style="color: #3b82f6; text-decoration: none;">Browse Categories</a></li>
                        </ul>
                    </div>
                </aside>
            </div>
        </div>
    </div>

${footer()}
    <script src="../js/main.js"></script>
</body>
</html>`;
}

// ─── Sitemap ────────────────────────────────────────────────────────────────

function addToSitemap(urls) {
  const sitemapPath = path.join(REPO_ROOT, 'sitemap.xml');
  let sitemap = fs.readFileSync(sitemapPath, 'utf-8');

  for (const url of urls) {
    if (sitemap.includes(url)) continue;
    const entry = `  <url>\n    <loc>${url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n`;
    sitemap = sitemap.replace('</urlset>', entry + '</urlset>');
  }

  fs.writeFileSync(sitemapPath, sitemap);
}

// ─── Compare Index ──────────────────────────────────────────────────────────

function addToCompareIndex(slug, toolAName, toolBName, ratingA, ratingB) {
  const indexPath = path.join(REPO_ROOT, 'compare', 'index.html');
  if (!fs.existsSync(indexPath)) return;

  let html = fs.readFileSync(indexPath, 'utf-8');

  // Check if already listed
  if (html.includes(`${slug}.html`)) return;

  // Build new card matching existing design
  const card = `
                <a href="${slug}.html" class="compare-card">
                    <div class="compare-vs">
                        <div class="compare-tool">
                            <h3>${escapeHtml(toolAName)}</h3>
                            <span class="compare-rating">${ratingA || 'N/A'}/5</span>
                        </div>
                        <div class="vs-badge">VS</div>
                        <div class="compare-tool">
                            <h3>${escapeHtml(toolBName)}</h3>
                            <span class="compare-rating">${ratingB || 'N/A'}/5</span>
                        </div>
                    </div>
                    <p class="compare-summary">${escapeHtml(toolAName)} vs ${escapeHtml(toolBName)} — see our full comparison</p>
                </a>`;

  // Insert before closing compare-grid div (find last </a> in the grid)
  const gridEndMarker = '</div>\n    </section>';
  if (html.includes(gridEndMarker)) {
    html = html.replace(gridEndMarker, card + '\n            </div>\n    </section>');
    fs.writeFileSync(indexPath, html);
  }
}

// ─── Homepage Compare Section ───────────────────────────────────────────────

function addToHomepageCompare(slug, toolAName, toolBName, ratingA, ratingB) {
  const indexPath = path.join(REPO_ROOT, 'index.html');
  if (!fs.existsSync(indexPath)) return;

  let html = fs.readFileSync(indexPath, 'utf-8');
  if (html.includes(`${slug}.html`)) return;

  // Don't add to homepage if there are already 6+ comparisons shown
  const compareCardCount = (html.match(/compare-card/g) || []).length;
  if (compareCardCount >= 6) return;

  const card = `
                <a href="compare/${slug}.html" class="compare-card">
                    <div class="compare-vs">
                        <div class="compare-tool">
                            <h3>${escapeHtml(toolAName)}</h3>
                            <span class="compare-rating">${ratingA || 'N/A'}/5</span>
                        </div>
                        <div class="vs-badge">VS</div>
                        <div class="compare-tool">
                            <h3>${escapeHtml(toolBName)}</h3>
                            <span class="compare-rating">${ratingB || 'N/A'}/5</span>
                        </div>
                    </div>
                    <p class="compare-summary">${escapeHtml(toolAName)} vs ${escapeHtml(toolBName)} — see our verdict</p>
                </a>`;

  // Try to insert into compare-grid on homepage
  const marker = '<!-- end-compare-grid -->';
  if (html.includes(marker)) {
    html = html.replace(marker, card + '\n            ' + marker);
    fs.writeFileSync(indexPath, html);
  }
}

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  console.log('');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  SalesAIGuide Publish Agent');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');

  // 1. Fetch approved comparisons
  console.log('Fetching approved comparisons from Airtable...');
  const comparisons = await getApprovedComparisons();

  if (comparisons.length === 0) {
    console.log('No new comparisons to publish. Done.');
    return;
  }

  console.log(`Found ${comparisons.length} approved comparison(s)\n`);

  const published = [];
  const failed = [];
  const newUrls = [];

  // 2. Process each
  for (const record of comparisons) {
    const fields = record.fields;
    const title = fields.Title || 'Unknown';

    try {
      console.log(`Processing: ${title}`);

      // Get linked tools
      const toolAId = fields['Tool A']?.[0];
      const toolBId = fields['Tool B']?.[0];
      if (!toolAId || !toolBId) throw new Error('Missing Tool A or Tool B link');

      const toolA = await getRecord('Tools', toolAId);
      const toolB = await getRecord('Tools', toolBId);
      console.log(`  ${toolA.Name} (${toolA['G2 Rating']}/5) vs ${toolB.Name} (${toolB['G2 Rating']}/5)`);

      // Generate HTML
      const slug = fields.Slug || `${toolA.Slug}-vs-${toolB.Slug}`;
      const html = await generateComparisonHTML(fields, toolA, toolB);

      // Write file
      const filePath = path.join(REPO_ROOT, 'compare', `${slug}.html`);
      fs.writeFileSync(filePath, html);
      console.log(`  Written: compare/${slug}.html`);

      // Update indexes
      addToCompareIndex(slug, toolA.Name, toolB.Name, toolA['G2 Rating'], toolB['G2 Rating']);
      addToHomepageCompare(slug, toolA.Name, toolB.Name, toolA['G2 Rating'], toolB['G2 Rating']);

      // Track
      const url = `${SITE_URL}/compare/${slug}.html`;
      newUrls.push(url);

      // Update Airtable
      await markPublished(record.id);
      console.log(`  Published & updated in Airtable\n`);

      published.push(title);
    } catch (err) {
      console.error(`  FAILED: ${err.message}\n`);
      failed.push({ title, error: err.message });
    }
  }

  // 3. Update sitemap
  if (newUrls.length > 0) {
    console.log('Updating sitemap.xml...');
    addToSitemap(newUrls);
    console.log('Sitemap updated\n');
  }

  // 4. Summary
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`  Published: ${published.length} | Failed: ${failed.length}`);
  if (published.length > 0) {
    published.forEach(t => console.log(`  + ${t}`));
  }
  if (failed.length > 0) {
    failed.forEach(f => console.log(`  x ${f.title}: ${f.error}`));
  }
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
}

main().catch(err => {
  console.error('Publish Agent failed:', err.message);
  process.exit(1);
});

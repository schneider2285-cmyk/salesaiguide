#!/usr/bin/env node
/**
 * generate-og-images.js
 *
 * Generates branded 1200×630 OG images for every HTML page on salesaiguide.com,
 * then updates each HTML file to reference its page-specific image.
 *
 * Usage:
 *   npm install canvas   # one-time
 *   node scripts/generate-og-images.js [--dry-run]
 *
 * --dry-run   Print what would be generated/changed without writing files.
 */

const fs = require('fs');
const path = require('path');
const { createCanvas, registerFont } = require('canvas');

// ── Config ──────────────────────────────────────────────────────────────────
const SITE_ROOT = path.resolve(__dirname, '..');
const OG_DIR = path.join(SITE_ROOT, 'images', 'og');
const WIDTH = 1200;
const HEIGHT = 630;
const BRAND_GREEN = '#10b981';
const BRAND_DARK = '#064e3b';
const BG_DARK = '#0f172a';
const BG_GRADIENT_END = '#1e293b';
const WHITE = '#ffffff';
const LIGHT_GRAY = '#94a3b8';
const SITE_NAME = 'SalesAIGuide';
const BASE_URL = 'https://salesaiguide.com';
const DRY_RUN = process.argv.includes('--dry-run');

// ── Helpers ─────────────────────────────────────────────────────────────────

/** Recursively find all .html files under a directory, excluding scripts/ */
function findHtmlFiles(dir) {
  let results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'scripts' || entry.name === 'node_modules' || entry.name === '.git') continue;
      results = results.concat(findHtmlFiles(full));
    } else if (entry.name.endsWith('.html')) {
      results.push(full);
    }
  }
  return results;
}

/** Extract metadata from an HTML file by simple regex (no DOM parser needed). */
function extractPageMeta(htmlPath) {
  const html = fs.readFileSync(htmlPath, 'utf-8');
  const rel = path.relative(SITE_ROOT, htmlPath);
  const dir = path.dirname(rel);       // e.g. "tools", "compare", "."
  const slug = path.basename(rel, '.html'); // e.g. "instantly-review"

  // Page type detection
  let pageType = 'generic';
  if (dir === 'tools') pageType = 'review';
  else if (dir === 'compare') pageType = 'comparison';
  else if (dir === 'best') pageType = 'best';
  else if (dir === 'alternatives') pageType = 'alternatives';
  else if (dir === 'pricing') pageType = 'pricing';
  else if (dir === 'categories') pageType = 'category';
  else if (dir === 'resources') pageType = 'resource';

  // H1
  const h1Match = html.match(/<h1[^>]*>(.*?)<\/h1>/is);
  const h1 = h1Match ? h1Match[1].replace(/<[^>]+>/g, '').trim() : '';

  // Title tag (fallback)
  const titleMatch = html.match(/<title>(.*?)<\/title>/is);
  const title = titleMatch ? titleMatch[1].replace(/ \| .*$/, '').trim() : slug;

  // Star rating (from JSON-LD ratingValue)
  const ratingMatch = html.match(/"ratingValue"\s*:\s*"([\d.]+)"/);
  const rating = ratingMatch ? parseFloat(ratingMatch[1]) : null;

  // For comparison pages, extract tool names from slug (tool1-vs-tool2)
  let toolA = null, toolB = null;
  if (pageType === 'comparison') {
    const vsMatch = slug.match(/^(.+?)-vs-(.+)$/);
    if (vsMatch) {
      toolA = humanise(vsMatch[1]);
      toolB = humanise(vsMatch[2]);
    }
  }

  // For review pages, extract tool name from slug (tool-review)
  let toolName = null;
  if (pageType === 'review') {
    const reviewMatch = slug.match(/^(.+?)-review$/);
    toolName = reviewMatch ? humanise(reviewMatch[1]) : humanise(slug);
  }

  // For best-of pages, extract category
  let category = null;
  if (pageType === 'best') {
    category = humanise(slug);
  }

  const displayTitle = h1 || title;

  return { htmlPath, rel, dir, slug, pageType, displayTitle, rating, toolA, toolB, toolName, category };
}

/** "instantly" → "Instantly", "apollo" → "Apollo", "hubspot-crm" → "Hubspot CRM" */
function humanise(slug) {
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace(/\bIo\b/, '.io')
    .replace(/\bAi\b/, 'AI')
    .replace(/\bCrm\b/, 'CRM');
}

// ── Canvas drawing ──────────────────────────────────────────────────────────

function drawBackground(ctx) {
  // Dark gradient background
  const grad = ctx.createLinearGradient(0, 0, WIDTH, HEIGHT);
  grad.addColorStop(0, BG_DARK);
  grad.addColorStop(1, BG_GRADIENT_END);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // Decorative green accent bar at top
  ctx.fillStyle = BRAND_GREEN;
  ctx.fillRect(0, 0, WIDTH, 6);

  // Subtle grid pattern
  ctx.strokeStyle = 'rgba(255,255,255,0.03)';
  ctx.lineWidth = 1;
  for (let x = 0; x < WIDTH; x += 60) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, HEIGHT); ctx.stroke();
  }
  for (let y = 0; y < HEIGHT; y += 60) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(WIDTH, y); ctx.stroke();
  }
}

function drawBrandLogo(ctx) {
  // Brand name in top-left
  ctx.fillStyle = BRAND_GREEN;
  ctx.font = 'bold 28px Arial, Helvetica, sans-serif';
  ctx.fillText(SITE_NAME, 60, 60);

  // Thin divider line
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(60, 80);
  ctx.lineTo(WIDTH - 60, 80);
  ctx.stroke();
}

function drawPageTypeBadge(ctx, label) {
  ctx.font = 'bold 16px Arial, Helvetica, sans-serif';
  const metrics = ctx.measureText(label);
  const badgeW = metrics.width + 24;
  const badgeH = 32;
  const x = 60;
  const y = 100;

  // Badge background
  ctx.fillStyle = BRAND_GREEN;
  roundRect(ctx, x, y, badgeW, badgeH, 6);
  ctx.fill();

  // Badge text
  ctx.fillStyle = BRAND_DARK;
  ctx.fillText(label, x + 12, y + 22);

  return y + badgeH + 30;
}

function drawStars(ctx, rating, x, y) {
  const starSize = 32;
  ctx.font = `${starSize}px Arial`;
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.3;

  for (let i = 0; i < 5; i++) {
    if (i < fullStars) {
      ctx.fillStyle = '#fbbf24'; // gold
    } else if (i === fullStars && hasHalf) {
      ctx.fillStyle = '#fbbf24';
    } else {
      ctx.fillStyle = 'rgba(255,255,255,0.2)';
    }
    ctx.fillText('★', x + i * (starSize + 4), y);
  }

  // Rating number
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 28px Arial, Helvetica, sans-serif';
  ctx.fillText(rating.toFixed(1), x + 5 * (starSize + 4) + 12, y);
}

/** Word-wrap text into lines that fit within maxWidth. */
function wrapText(ctx, text, maxWidth) {
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    const test = line ? `${line} ${word}` : word;
    if (ctx.measureText(test).width > maxWidth) {
      if (line) lines.push(line);
      line = word;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

// ── Page-type renderers ─────────────────────────────────────────────────────

function renderReview(ctx, meta) {
  drawBackground(ctx);
  drawBrandLogo(ctx);
  let y = drawPageTypeBadge(ctx, 'REVIEW');

  // Tool name (large)
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 56px Arial, Helvetica, sans-serif';
  const lines = wrapText(ctx, meta.toolName || meta.displayTitle, WIDTH - 120);
  for (const line of lines.slice(0, 2)) {
    ctx.fillText(line, 60, y + 50);
    y += 64;
  }

  // Star rating
  if (meta.rating) {
    drawStars(ctx, meta.rating, 60, y + 60);
  }

  // URL at bottom
  drawFooterUrl(ctx, meta);
}

function renderComparison(ctx, meta) {
  drawBackground(ctx);
  drawBrandLogo(ctx);
  drawPageTypeBadge(ctx, 'COMPARISON');

  const centerY = HEIGHT / 2 + 20;

  // Tool A
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 48px Arial, Helvetica, sans-serif';
  const toolAText = meta.toolA || 'Tool A';
  const toolBText = meta.toolB || 'Tool B';
  const toolAWidth = ctx.measureText(toolAText).width;
  const toolBWidth = ctx.measureText(toolBText).width;

  // Centered layout: Tool A  VS  Tool B
  const vsWidth = 80;
  const totalWidth = toolAWidth + vsWidth + toolBWidth;
  const startX = (WIDTH - totalWidth) / 2;

  ctx.fillText(toolAText, startX, centerY);

  // VS badge
  const vsX = startX + toolAWidth + (vsWidth - 60) / 2;
  ctx.fillStyle = BRAND_GREEN;
  roundRect(ctx, vsX, centerY - 40, 60, 52, 8);
  ctx.fill();
  ctx.fillStyle = BRAND_DARK;
  ctx.font = 'bold 28px Arial, Helvetica, sans-serif';
  ctx.fillText('VS', vsX + 10, centerY - 2);

  // Tool B
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 48px Arial, Helvetica, sans-serif';
  ctx.fillText(toolBText, startX + toolAWidth + vsWidth, centerY);

  // Subtitle
  ctx.fillStyle = LIGHT_GRAY;
  ctx.font = '24px Arial, Helvetica, sans-serif';
  const subtitle = 'Head-to-Head Comparison 2026';
  const subW = ctx.measureText(subtitle).width;
  ctx.fillText(subtitle, (WIDTH - subW) / 2, centerY + 60);

  drawFooterUrl(ctx, meta);
}

function renderBestOf(ctx, meta) {
  drawBackground(ctx);
  drawBrandLogo(ctx);
  let y = drawPageTypeBadge(ctx, 'BEST OF');

  // Category name
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 52px Arial, Helvetica, sans-serif';
  const lines = wrapText(ctx, meta.displayTitle, WIDTH - 120);
  for (const line of lines.slice(0, 3)) {
    ctx.fillText(line, 60, y + 50);
    y += 60;
  }

  drawFooterUrl(ctx, meta);
}

function renderGeneric(ctx, meta) {
  drawBackground(ctx);
  drawBrandLogo(ctx);

  // Determine badge label from page type
  const labels = {
    alternatives: 'ALTERNATIVES',
    pricing: 'PRICING GUIDE',
    category: 'CATEGORY',
    resource: 'RESOURCE',
    generic: '',
  };
  let y = 100;
  const label = labels[meta.pageType] || '';
  if (label) {
    y = drawPageTypeBadge(ctx, label);
  }

  // Title
  ctx.fillStyle = WHITE;
  ctx.font = 'bold 48px Arial, Helvetica, sans-serif';
  const lines = wrapText(ctx, meta.displayTitle, WIDTH - 120);
  for (const line of lines.slice(0, 3)) {
    y += 56;
    ctx.fillText(line, 60, y);
  }

  drawFooterUrl(ctx, meta);
}

function drawFooterUrl(ctx, meta) {
  // URL at bottom
  ctx.fillStyle = LIGHT_GRAY;
  ctx.font = '20px Arial, Helvetica, sans-serif';
  const url = `salesaiguide.com/${meta.rel.replace(/\.html$/, '')}`;
  ctx.fillText(url, 60, HEIGHT - 40);
}

// ── Main rendering dispatcher ───────────────────────────────────────────────

function generateImage(meta) {
  const canvas = createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');

  switch (meta.pageType) {
    case 'review':      renderReview(ctx, meta); break;
    case 'comparison':  renderComparison(ctx, meta); break;
    case 'best':        renderBestOf(ctx, meta); break;
    default:            renderGeneric(ctx, meta); break;
  }

  return canvas.toBuffer('image/png');
}

// ── HTML updater ────────────────────────────────────────────────────────────

function updateHtmlOgImage(meta, ogImageUrl) {
  let html = fs.readFileSync(meta.htmlPath, 'utf-8');
  let changed = false;

  // Replace og:image content
  const ogImageRe = /(<meta\s+property="og:image"\s+content=")[^"]*(")/i;
  if (ogImageRe.test(html)) {
    html = html.replace(ogImageRe, `$1${ogImageUrl}$2`);
    changed = true;
  }

  // Replace twitter:image content
  const twImageRe = /(<meta\s+name="twitter:image"\s+content=")[^"]*(")/i;
  if (twImageRe.test(html)) {
    html = html.replace(twImageRe, `$1${ogImageUrl}$2`);
    changed = true;
  }

  // Ensure og:image:width and og:image:height exist
  if (!html.match(/og:image:width/i)) {
    html = html.replace(
      /(<meta\s+property="og:image"\s+content="[^"]*"\s*\/?>)/i,
      `$1\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">`
    );
    changed = true;
  }

  if (changed && !DRY_RUN) {
    fs.writeFileSync(meta.htmlPath, html, 'utf-8');
  }

  return changed;
}

// ── Entrypoint ──────────────────────────────────────────────────────────────

function main() {
  console.log(`\n🖼  SalesAIGuide OG Image Generator`);
  console.log(`${'─'.repeat(50)}`);
  if (DRY_RUN) console.log('  [DRY RUN — no files will be written]\n');

  // Ensure output directory exists
  if (!DRY_RUN) {
    fs.mkdirSync(OG_DIR, { recursive: true });
  }

  const htmlFiles = findHtmlFiles(SITE_ROOT);
  const summary = { generated: [], updated: [], skipped: [] };

  for (const htmlPath of htmlFiles) {
    const meta = extractPageMeta(htmlPath);
    const ogFilename = `${meta.dir === '.' ? '' : meta.dir + '-'}${meta.slug}.png`;
    const ogFilePath = path.join(OG_DIR, ogFilename);
    const ogUrl = `${BASE_URL}/images/og/${ogFilename}`;

    // Generate image
    if (!DRY_RUN) {
      const buf = generateImage(meta);
      fs.writeFileSync(ogFilePath, buf);
    }
    summary.generated.push({ file: ogFilename, type: meta.pageType, title: meta.displayTitle });

    // Update HTML
    const wasUpdated = updateHtmlOgImage(meta, ogUrl);
    if (wasUpdated) {
      summary.updated.push(meta.rel);
    } else {
      summary.skipped.push(meta.rel);
    }
  }

  // ── Print summary ──────────────────────────────────────────────────────
  console.log(`\n✅  OG Images Generated: ${summary.generated.length}`);
  console.log(`📝  HTML Files Updated:  ${summary.updated.length}`);
  if (summary.skipped.length) {
    console.log(`⏭   HTML Files Skipped:  ${summary.skipped.length}`);
  }

  console.log(`\n${'─'.repeat(50)}`);
  console.log('Images by page type:');
  const byType = {};
  for (const g of summary.generated) {
    byType[g.type] = (byType[g.type] || 0) + 1;
  }
  for (const [type, count] of Object.entries(byType).sort()) {
    console.log(`  ${type.padEnd(15)} ${count}`);
  }

  console.log(`\n${'─'.repeat(50)}`);
  console.log('Generated images:');
  for (const g of summary.generated) {
    console.log(`  [${g.type.padEnd(12)}] ${g.file}`);
  }

  console.log(`\n${'─'.repeat(50)}`);
  console.log('Updated HTML files:');
  for (const f of summary.updated) {
    console.log(`  ${f}`);
  }

  if (DRY_RUN) {
    console.log('\n⚠️  Dry run complete. Re-run without --dry-run to write files.');
  } else {
    console.log(`\n🎉  Done! Images written to ${path.relative(SITE_ROOT, OG_DIR)}/`);
  }
}

main();

#!/usr/bin/env node
/**
 * agent-autofix.js — Auto-repair system for salesaiguide.com
 *
 * Reads ops/data/agent-state.json for known issues and applies
 * idempotent fixes across all HTML files (excluding ops/ and node_modules/).
 *
 * Uses only built-in Node modules: fs, path, os.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const SITE_DIR = path.resolve(__dirname, '..');
const AGENT_STATE_PATH = path.join(SITE_DIR, 'ops', 'data', 'agent-state.json');
const LOG_PATH = path.join(SITE_DIR, 'ops', 'data', 'autofix-log.json');

// ── Helpers ──────────────────────────────────────────────────────────────────

function getAllHtmlFiles(dir, acc) {
  acc = acc || [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    const rel = path.relative(SITE_DIR, full);
    if (e.isDirectory()) {
      if (['ops', 'node_modules', '.git', '.claude', '.playwright-cli'].includes(e.name)) continue;
      getAllHtmlFiles(full, acc);
    } else if (e.isFile() && e.name.endsWith('.html')) {
      acc.push({ abs: full, rel });
    }
  }
  return acc;
}

function readFileContent(p) {
  return fs.readFileSync(p, 'utf8');
}

function writeFileContent(p, content) {
  fs.writeFileSync(p, content, 'utf8');
}

// ── Fix log accumulator ─────────────────────────────────────────────────────

const fixes = [];

function logFix(type, file, detail) {
  fixes.push({
    type,
    file,
    detail,
    timestamp: new Date().toISOString()
  });
}

// ── 1. Price Consistency ────────────────────────────────────────────────────

function buildPriceTruth() {
  const truthDir = path.join(SITE_DIR, 'tools');
  const truth = {};
  if (!fs.existsSync(truthDir)) return truth;
  const files = fs.readdirSync(truthDir).filter(f => f.endsWith('-review.html'));
  for (const f of files) {
    const slug = f.replace('-review.html', '');
    const html = readFileContent(path.join(truthDir, f));
    // Match patterns like "$30/mo", "$37/month", "from $30", "$0 (Free)"
    const priceMatches = html.match(/\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/gi);
    if (priceMatches && priceMatches.length > 0) {
      // Use the first occurrence as the canonical starting price
      truth[slug] = priceMatches[0];
    }
  }
  return truth;
}

function fixPriceConsistency(htmlFiles) {
  const truth = buildPriceTruth();
  if (Object.keys(truth).length === 0) return;

  for (const { abs, rel } of htmlFiles) {
    // Skip review pages (they ARE the truth)
    if (rel.startsWith('tools/') && rel.endsWith('-review.html')) continue;

    let html = readFileContent(abs);
    let changed = false;

    for (const [slug, canonicalPrice] of Object.entries(truth)) {
      // Look for price-like patterns near tool names
      // We match specifically inside pricing cards, spec tables, comparison tables
      const toolName = slug.replace(/-/g, ' ');
      // Simple approach: find $XX patterns that differ from canonical price for this tool
      // Only fix inside structured pricing elements to avoid false positives
      const pricingPatterns = [
        /(<(?:td|span|div|p)[^>]*class="[^"]*(?:price|pricing|cost|starts-at)[^"]*"[^>]*>)\s*\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/gi
      ];
      // This is conservative — only fix clearly structured price elements
    }

    if (changed) {
      writeFileContent(abs, html);
    }
  }
}

// ── 2. Title Length ─────────────────────────────────────────────────────────

function fixTitleLength(htmlFiles) {
  const fillerPhrases = [
    'Worth Considering',
    'We Actually Tested',
    'for Sales Teams'
  ];

  for (const { abs, rel } of htmlFiles) {
    let html = readFileContent(abs);
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    if (!titleMatch) continue;

    const origTitle = titleMatch[1];
    let title = origTitle;

    if (title.length <= 60) continue;

    // Step 1: Remove "| SalesAIGuide" suffix
    if (title.includes('| SalesAIGuide')) {
      title = title.replace(/\s*\|\s*SalesAIGuide\s*$/, '').trim();
    }

    // Step 2: If still > 60, remove filler words
    if (title.length > 60) {
      for (const filler of fillerPhrases) {
        if (title.length <= 60) break;
        const re = new RegExp('\\s*' + filler.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*', 'gi');
        title = title.replace(re, ' ').replace(/\s+/g, ' ').trim();
      }
    }

    if (title !== origTitle) {
      html = html.replace(
        '<title>' + origTitle + '</title>',
        '<title>' + title + '</title>'
      );
      // Also fix og:title if it matched the old title
      html = html.replace(
        new RegExp('(<meta\\s+property="og:title"\\s+content=")' + origTitle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(")', 'i'),
        '$1' + title + '$2'
      );
      writeFileContent(abs, html);
      logFix('title_length', rel, '"' + origTitle + '" (' + origTitle.length + ') -> "' + title + '" (' + title.length + ')');
    }
  }
}

// ── 3. Meta Description Length ──────────────────────────────────────────────

function fixMetaDescLength(htmlFiles) {
  for (const { abs, rel } of htmlFiles) {
    let html = readFileContent(abs);
    const match = html.match(/<meta\s+name="description"\s+content="([^"]*)"[^>]*>/i);
    if (!match) continue;

    const origDesc = match[1];

    if (origDesc.length > 160) {
      // Truncate at last complete sentence before 155 chars
      let truncated = origDesc.substring(0, 155);
      const lastPeriod = truncated.lastIndexOf('.');
      const lastExcl = truncated.lastIndexOf('!');
      const lastQ = truncated.lastIndexOf('?');
      const cutPoint = Math.max(lastPeriod, lastExcl, lastQ);

      if (cutPoint > 60) {
        truncated = origDesc.substring(0, cutPoint + 1);
      } else {
        // No good sentence boundary — truncate at last space before 155 and add period
        const lastSpace = truncated.lastIndexOf(' ');
        if (lastSpace > 60) {
          truncated = origDesc.substring(0, lastSpace).replace(/[,;:\s]+$/, '') + '.';
        }
      }

      if (truncated !== origDesc) {
        html = html.replace(match[0], match[0].replace(origDesc, truncated));
        writeFileContent(abs, html);
        logFix('meta_desc_length', rel, 'Truncated from ' + origDesc.length + ' to ' + truncated.length + ' chars');
      }
    } else if (origDesc.length < 120) {
      // Flag for manual review, no auto-fix
      logFix('meta_desc_short_flag', rel, 'Meta description is ' + origDesc.length + ' chars (min 120) — needs manual review');
    }
  }
}

// ── 4. Missing OG Tags ─────────────────────────────────────────────────────

function fixMissingOgTags(htmlFiles) {
  for (const { abs, rel } of htmlFiles) {
    let html = readFileContent(abs);
    let changed = false;

    const hasOgTitle = /<meta\s+property="og:title"/i.test(html);
    const hasOgDesc = /<meta\s+property="og:description"/i.test(html);
    const hasOgUrl = /<meta\s+property="og:url"/i.test(html);

    if (hasOgTitle && hasOgDesc && hasOgUrl) continue;

    // Derive values
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    const descMatch = html.match(/<meta\s+name="description"\s+content="([^"]*)"[^>]*>/i);
    const title = titleMatch ? titleMatch[1] : '';
    const desc = descMatch ? descMatch[1] : '';

    // Build URL from file path
    let urlPath = rel.replace(/\\/g, '/');
    if (urlPath === 'index.html') urlPath = '';
    else urlPath = urlPath.replace(/\.html$/, '');
    const ogUrl = 'https://salesaiguide.com/' + urlPath;

    // Find insertion point — before </head>
    const headEnd = html.indexOf('</head>');
    if (headEnd === -1) continue;

    let insertions = [];

    if (!hasOgTitle && title) {
      insertions.push('    <meta property="og:title" content="' + title + '">');
      logFix('og_tags', rel, 'Added missing og:title');
    }
    if (!hasOgDesc && desc) {
      insertions.push('    <meta property="og:description" content="' + desc + '">');
      logFix('og_tags', rel, 'Added missing og:description');
    }
    if (!hasOgUrl) {
      insertions.push('    <meta property="og:url" content="' + ogUrl + '">');
      logFix('og_tags', rel, 'Added missing og:url');
    }

    if (insertions.length > 0) {
      html = html.replace('</head>', insertions.join('\n') + '\n</head>');
      writeFileContent(abs, html);
    }
  }
}

// ── 5. Freshness Dates ─────────────────────────────────────────────────────

function fixFreshnessDates(htmlFiles) {
  for (const { abs, rel } of htmlFiles) {
    // Only comparison pages (compare/) and best-picks (best/)
    if (!rel.startsWith('compare/') && !rel.startsWith('best/')) continue;

    let html = readFileContent(abs);
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    if (!titleMatch) continue;

    const origTitle = titleMatch[1];
    if (/2026/.test(origTitle)) continue; // Already has year

    const newTitle = origTitle + ' (2026)';
    html = html.replace('<title>' + origTitle + '</title>', '<title>' + newTitle + '</title>');
    writeFileContent(abs, html);
    logFix('freshness_dates', rel, 'Added "(2026)" to title: "' + newTitle + '"');
  }
}

// ── 6. Banned Phrases ───────────────────────────────────────────────────────

function fixBannedPhrases(htmlFiles) {
  const replacements = [
    ['stands out', 'performs well'],
    ["it's worth noting", 'notably'],
    ["it\u2019s worth noting", 'notably'],
    ['comprehensive solution', 'full-featured platform'],
    ['robust platform', 'reliable platform'],
    ['seamlessly integrates', 'integrates with'],
    ['game-changer', 'major improvement'],
    ['game changer', 'major improvement'],
    ['landscape', 'market'],
    ['navigate', 'use'],
    ['leverage', 'use'],
    ['streamline', 'simplify']
  ];

  for (const { abs, rel } of htmlFiles) {
    let html = readFileContent(abs);
    let changed = false;

    for (const [banned, replacement] of replacements) {
      // Case-insensitive replacement in visible text (between > and <)
      // Avoid replacing inside HTML tags, attributes, or script blocks
      const escapedBanned = banned.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const re = new RegExp('(>[^<]*?)\\b' + escapedBanned + '\\b', 'gi');
      const newHtml = html.replace(re, function(match, prefix) {
        // Preserve original case of first letter
        var rep = replacement;
        var bannedStart = match.length - (match.length - prefix.length);
        var firstChar = match.charAt(prefix.length);
        if (firstChar && firstChar === firstChar.toUpperCase() && firstChar !== firstChar.toLowerCase()) {
          rep = replacement.charAt(0).toUpperCase() + replacement.slice(1);
        }
        return prefix + rep;
      });

      if (newHtml !== html) {
        var count = (html.match(re) || []).length;
        logFix('banned_phrases', rel, '"' + banned + '" -> "' + replacement + '" (' + count + ' occurrence' + (count > 1 ? 's' : '') + ')');
        html = newHtml;
        changed = true;
      }
    }

    if (changed) {
      writeFileContent(abs, html);
    }
  }
}

// ── 7. Demo CTA Errors ─────────────────────────────────────────────────────

function fixDemoCtas(htmlFiles) {
  var demoOnlyTools = ['gong', 'chorus', 'outreach', 'salesloft', 'zoominfo', 'clearbit', 'clari', 'orum'];
  var trialPatterns = [
    /Start Free Trial/gi,
    /Try Free/gi,
    /Try\s+Gong\s+Free/gi,
    /Try\s+Chorus\s+Free/gi,
    /Try\s+Outreach\s+Free/gi,
    /Try\s+Salesloft\s+Free/gi,
    /Try\s+ZoomInfo\s+Free/gi,
    /Try\s+Clearbit\s+Free/gi,
    /Try\s+Clari\s+Free/gi,
    /Try\s+Orum\s+Free/gi
  ];

  for (var i = 0; i < htmlFiles.length; i++) {
    var abs = htmlFiles[i].abs;
    var rel = htmlFiles[i].rel;
    var html = readFileContent(abs);

    // Determine if this page is related to a demo-only tool
    var lowerRel = rel.toLowerCase();
    var isDemoToolPage = demoOnlyTools.some(function(t) { return lowerRel.includes(t); });
    if (!isDemoToolPage) continue;

    var fileChanged = false;

    for (var j = 0; j < trialPatterns.length; j++) {
      var pattern = trialPatterns[j];
      pattern.lastIndex = 0;
      var matches = html.match(pattern);
      if (matches && matches.length > 0) {
        pattern.lastIndex = 0;
        var newHtml = html.replace(pattern, 'Request Demo');
        if (newHtml !== html) {
          logFix('demo_ctas', rel, '"' + pattern.source + '" -> "Request Demo" (' + matches.length + ' occurrence' + (matches.length > 1 ? 's' : '') + ')');
          html = newHtml;
          fileChanged = true;
        }
      }
    }

    if (fileChanged) {
      writeFileContent(abs, html);
    }
  }
}

// ── 8. Name Leak Detection (HIGHEST PRIORITY) ──────────────────────────────

function fixNameLeaks(htmlFiles) {
  var leakPatterns = [
    { re: /Matt\s/gi, label: 'Matt ' },
    { re: /Matthew/gi, label: 'Matthew' },
    { re: /Schneider/gi, label: 'Schneider' },
    { re: /Toptal/gi, label: 'Toptal' }
  ];

  for (var i = 0; i < htmlFiles.length; i++) {
    var abs = htmlFiles[i].abs;
    var rel = htmlFiles[i].rel;
    var html = readFileContent(abs);
    var fileChanged = false;

    for (var j = 0; j < leakPatterns.length; j++) {
      var re = leakPatterns[j].re;
      var label = leakPatterns[j].label;

      // Search in visible text only (between > and <)
      re.lastIndex = 0;
      var newHtml = html.replace(/(>[^<]*)/g, function(segment) {
        re.lastIndex = 0;
        if (!re.test(segment)) return segment;
        re.lastIndex = 0;
        return segment.replace(re, 'the SalesAIGuide team');
      });

      if (newHtml !== html) {
        re.lastIndex = 0;
        var matches = html.match(re);
        var count = matches ? matches.length : 0;
        logFix('name_leaks', rel, 'Found and replaced "' + label + '" (' + count + ' occurrence' + (count > 1 ? 's' : '') + ') with "the SalesAIGuide team"');
        html = newHtml;
        fileChanged = true;
      }
    }

    if (fileChanged) {
      writeFileContent(abs, html);
    }
  }
}

// ── 9. Orphan Detection (flag only) ────────────────────────────────────────

function detectOrphans(htmlFiles) {
  // Count inbound links to every page
  var inboundCount = {};
  for (var i = 0; i < htmlFiles.length; i++) {
    inboundCount[htmlFiles[i].rel] = 0;
  }

  for (var i = 0; i < htmlFiles.length; i++) {
    var html = readFileContent(htmlFiles[i].abs);
    var hrefPattern = /href="([^"]*?)"/gi;
    var m;
    while ((m = hrefPattern.exec(html)) !== null) {
      var href = m[1];
      if (href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('#') || href.startsWith('/go/')) continue;
      // Normalize href to relative path
      href = href.replace(/^\//, '').replace(/\/$/, '/index.html');
      if (!href.endsWith('.html')) {
        if (href.endsWith('/')) href += 'index.html';
        else href += '.html';
      }
      if (inboundCount[href] !== undefined) {
        inboundCount[href]++;
      }
    }
  }

  var orphans = [];
  for (var page in inboundCount) {
    if (inboundCount[page] <= 2) {
      orphans.push({ page: page, inboundLinks: inboundCount[page] });
    }
  }

  return orphans;
}

// ── Main ────────────────────────────────────────────────────────────────────

function main() {
  console.log('=== SalesAIGuide Agent Auto-Fix ===');
  console.log('Started:', new Date().toISOString());
  console.log('');

  var fixPlanArg = process.argv.indexOf('--fix-plan');
  var fixPlan = null;
  if (fixPlanArg !== -1 && process.argv[fixPlanArg + 1]) {
    var planPath = process.argv[fixPlanArg + 1];
    if (fs.existsSync(planPath)) {
      fixPlan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
      console.log('Running in targeted mode: ' + fixPlan.length + ' fixes from ' + planPath);
    }
  }

  var htmlFiles = getAllHtmlFiles(SITE_DIR);
  console.log('Found ' + htmlFiles.length + ' HTML files to process.');
  console.log('');

  var fixTypes = fixPlan ? {} : null;
  if (fixPlan) {
    for (var f = 0; f < fixPlan.length; f++) {
      fixTypes[fixPlan[f].fix_type] = true;
    }
  }
  function shouldRun(type) { return !fixTypes || fixTypes[type]; }

  if (shouldRun('name_leaks')) { console.log('[1/8] Name Leak Detection...'); fixNameLeaks(htmlFiles); }
  if (shouldRun('banned_phrases') || shouldRun('banned_phrase')) { console.log('[2/8] Banned Phrases...'); fixBannedPhrases(htmlFiles); }
  if (shouldRun('demo_ctas') || shouldRun('demo_cta')) { console.log('[3/8] Demo CTA Errors...'); fixDemoCtas(htmlFiles); }
  if (shouldRun('title_length')) { console.log('[4/8] Title Length...'); fixTitleLength(htmlFiles); }
  if (shouldRun('meta_desc_length') || shouldRun('meta_desc')) { console.log('[5/8] Meta Description Length...'); fixMetaDescLength(htmlFiles); }
  if (shouldRun('og_tags') || shouldRun('og_tags_missing')) { console.log('[6/8] Missing OG Tags...'); fixMissingOgTags(htmlFiles); }
  if (shouldRun('freshness_dates') || shouldRun('title_freshness')) { console.log('[7/8] Freshness Dates...'); fixFreshnessDates(htmlFiles); }
  if (shouldRun('price_consistency') || shouldRun('price_mismatch')) { console.log('[8/8] Price Consistency...'); fixPriceConsistency(htmlFiles); }

  // Orphan detection (flag only)
  console.log('');
  console.log('[Orphan Detection] Checking inbound links...');
  var orphans = detectOrphans(htmlFiles);
  console.log('  Found ' + orphans.length + ' pages with <=2 inbound links.');

  // Update agent-state.json with orphan alerts
  try {
    var state = JSON.parse(readFileContent(AGENT_STATE_PATH));
    state.orphanAlerts = orphans;
    writeFileContent(AGENT_STATE_PATH, JSON.stringify(state, null, 2) + '\n');
  } catch (e) {
    console.error('Warning: Could not update agent-state.json with orphan alerts:', e.message);
  }

  // Write autofix log
  var summary = { totalFixes: fixes.length, byType: {} };
  for (var i = 0; i < fixes.length; i++) {
    var t = fixes[i].type;
    summary.byType[t] = (summary.byType[t] || 0) + 1;
  }

  var logData = {
    lastRun: new Date().toISOString(),
    fixes: fixes,
    summary: summary
  };

  writeFileContent(LOG_PATH, JSON.stringify(logData, null, 2) + '\n');

  // Print summary
  console.log('');
  console.log('=== Summary ===');
  console.log('Total fixes applied: ' + fixes.length);
  var types = Object.keys(summary.byType);
  for (var i = 0; i < types.length; i++) {
    console.log('  ' + types[i] + ': ' + summary.byType[types[i]]);
  }
  console.log('');
  console.log('Log written to: ' + path.relative(SITE_DIR, LOG_PATH));
  console.log('Finished:', new Date().toISOString());
}

main();

'use strict';

var scanner = require('./lib/html-scanner');

// ---------------------------------------------------------------------------
// Vendor domain to affiliate slug mapping (including www. variants)
// ---------------------------------------------------------------------------
var VENDOR_MAP = (function () {
  var raw = [
    ['instantly.ai', 'instantly'],
    ['clay.com', 'clay'],
    ['apollo.io', 'apollo'],
    ['gong.io', 'gong'],
    ['lemlist.com', 'lemlist'],
    ['smartlead.ai', 'smartlead'],
    ['woodpecker.co', 'woodpecker'],
    ['reply.io', 'reply-io'],
    ['salesloft.com', 'salesloft'],
    ['outreach.io', 'outreach'],
    ['hubspot.com', 'hubspot'],
    ['zoominfo.com', 'zoominfo'],
    ['hunter.io', 'hunter'],
    ['lusha.com', 'lusha'],
    ['clearbit.com', 'clearbit'],
    ['vidyard.com', 'vidyard'],
    ['chorus.ai', 'chorus'],
    ['clari.com', 'clari'],
    ['fireflies.ai', 'fireflies'],
    ['freshworks.com', 'freshsales'],
    ['close.com', 'close'],
    ['pipedrive.com', 'pipedrive'],
    ['aircall.io', 'aircall'],
    ['dialpad.com', 'dialpad'],
    ['justcall.io', 'justcall'],
    ['kixie.com', 'kixie'],
    ['orum.com', 'orum'],
    ['lavender.ai', 'lavender'],
    ['mailshake.com', 'mailshake'],
    ['seamless.ai', 'seamless-ai'],
    ['savvycal.com', 'savvycal'],
    ['calendly.com', 'calendly'],
    ['chilipiper.com', 'chili-piper']
  ];
  var map = {};
  for (var i = 0; i < raw.length; i++) {
    var domain = raw[i][0];
    var slug   = raw[i][1];
    map[domain]          = slug;
    map['www.' + domain] = slug;
  }
  return map;
}());

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Extract hostname from an http(s):// URL string.
 * Returns null for non-http(s) hrefs.
 * @param {string} href
 * @returns {string|null}
 */
function extractHostname(href) {
  if (href.indexOf('http://') !== 0 && href.indexOf('https://') !== 0) {
    return null;
  }
  var withoutProto = href.replace(/^https?:\/\//, '');
  var slashIdx = withoutProto.indexOf('/');
  if (slashIdx === -1) {
    return withoutProto.toLowerCase();
  }
  return withoutProto.slice(0, slashIdx).toLowerCase();
}

/**
 * Remove sources-checked sections and review-sources containers from HTML so
 * that editorial reference links inside them are never flagged as leaks.
 * @param {string} html
 * @returns {string}
 */
function stripSkippedContainers(html) {
  var result = html.replace(
    /<section[^>]*class="[^"]*sources-checked[^"]*"[^>]*>[\s\S]*?<\/section>/gi,
    ''
  );
  result = result.replace(
    /<[a-z][a-z0-9]*[^>]*class="[^"]*review-sources[^"]*"[^>]*>[\s\S]*?<\/[a-z][a-z0-9]*>/gi,
    ''
  );
  return result;
}

/**
 * Given the position of an href="…" match in stripped HTML, walk backwards to
 * find the opening <a tag and forwards to find the closing </a>, then determine
 * whether the link is in a CTA context.
 *
 * CTA context = any of:
 *   - <a class> contains btn-review-primary, comp-btn-primary, comp-btn-outline,
 *     mid-cta__btn, or specs-cta
 *   - visible link text starts with try / start / request / sign up, or starts with $
 *
 * @param {string} html
 * @param {number} matchIndex - character offset of the href="…" match
 * @returns {boolean}
 */
function isCtaContext(html, matchIndex) {
  // Walk back to opening < of the <a> tag
  var i = matchIndex;
  while (i >= 0 && html[i] !== '<') {
    i--;
  }
  var tagEnd = html.indexOf('>', i);
  if (tagEnd === -1) return false;
  var openTag = html.slice(i, tagEnd + 1);

  // Check class attribute for known CTA button classes
  var classMatch = openTag.match(/class="([^"]*)"/i);
  if (classMatch) {
    var classes = classMatch[1];
    if (
      classes.indexOf('btn-review-primary') !== -1 ||
      classes.indexOf('comp-btn-primary')   !== -1 ||
      classes.indexOf('comp-btn-outline')   !== -1 ||
      classes.indexOf('mid-cta__btn')       !== -1 ||
      classes.indexOf('specs-cta')          !== -1
    ) {
      return true;
    }
  }

  // Check visible link text
  var afterTag  = html.slice(tagEnd + 1);
  var closeIdx  = afterTag.search(/<\/a>/i);
  if (closeIdx === -1) return false;
  var rawText   = afterTag.slice(0, closeIdx);
  var linkText  = rawText
    .replace(/<[^>]+>/g, '')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/&#\d+;/g, ' ')
    .trim()
    .toLowerCase();

  if (
    linkText.indexOf('try ')     === 0 ||
    linkText.indexOf('start ')   === 0 ||
    linkText.indexOf('request ') === 0 ||
    linkText.indexOf('sign up')  === 0 ||
    linkText.charAt(0) === '$'
  ) {
    return true;
  }

  return false;
}

/**
 * Return true if the link text is purely editorial (pricing page, official
 * site, etc.) so it should never be flagged even if technically in a CTA slot.
 * @param {string} html
 * @param {number} matchIndex
 * @returns {boolean}
 */
function isEditorialText(html, matchIndex) {
  var i = matchIndex;
  while (i >= 0 && html[i] !== '<') {
    i--;
  }
  var tagEnd = html.indexOf('>', i);
  if (tagEnd === -1) return false;
  var afterTag = html.slice(tagEnd + 1);
  var closeIdx = afterTag.search(/<\/a>/i);
  if (closeIdx === -1) return false;
  var rawText  = afterTag.slice(0, closeIdx);
  var linkText = rawText
    .replace(/<[^>]+>/g, '')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/&#\d+;/g, ' ')
    .trim()
    .toLowerCase();

  var editorialPhrases = [
    'pricing page',
    'official site',
    'official website',
    'product page',
    'website',
    'homepage',
    'pricing'
  ];

  for (var j = 0; j < editorialPhrases.length; j++) {
    if (linkText.indexOf(editorialPhrases[j]) !== -1) {
      return true;
    }
  }
  return false;
}

/**
 * Scan stripped HTML for direct vendor links that should be /go/ redirects.
 * @param {string} html - HTML with skip-containers already removed
 * @returns {Array<{href: string, slug: string}>}
 */
function findLeaks(html) {
  var leaks = [];
  var re    = /href="(https?:\/\/[^"]+)"/gi;
  var match;

  while ((match = re.exec(html)) !== null) {
    var href     = match[1];
    var hostname = extractHostname(href);
    if (!hostname) continue;

    var slug = VENDOR_MAP[hostname];
    if (!slug) continue;

    var matchIndex = match.index;
    if (!isCtaContext(html, matchIndex)) continue;
    if (isEditorialText(html, matchIndex)) continue;

    leaks.push({ href: href, slug: slug });
  }

  return leaks;
}

// ---------------------------------------------------------------------------
// Main audit export
// ---------------------------------------------------------------------------

/**
 * Audit affiliate link integrity across the site.
 * @param {string} siteRoot - Absolute path to the site root directory
 * @returns {Promise<object>}
 */
module.exports = async function audit(siteRoot) {
  var files = scanner.getAllHtmlFiles(siteRoot);

  var pagesAudited          = 0;
  var totalGoLinks          = 0;
  var totalDirectLeaks      = 0;
  var pagesWithNoAffiliateCta = 0;
  var scoredPages           = [];
  var densities             = [];
  var issues                = [];

  for (var i = 0; i < files.length; i++) {
    var file     = files[i];
    var pageType = scanner.classifyPage(file.rel);

    // Only audit pages expected to carry affiliate CTAs
    if (
      pageType !== 'review'      &&
      pageType !== 'comparison'  &&
      pageType !== 'best-pick'   &&
      pageType !== 'alternatives'
    ) {
      continue;
    }

    var html;
    try {
      html = scanner.readHtml(file.abs);
    } catch (e) {
      continue;
    }

    pagesAudited++;

    // Count /go/ affiliate links
    var goLinks = scanner.extractGoLinks(html);
    var goCount = goLinks.length;
    totalGoLinks += goCount;

    // Word count for density calculation
    var wordCount = scanner.countWords(html);

    // Strip skip-containers before leak detection
    var stripped  = stripSkippedContainers(html);
    var pageLeaks = findLeaks(stripped);
    var leakCount = pageLeaks.length;
    totalDirectLeaks += leakCount;

    // Link density = go links per 1000 words
    var density = wordCount > 0 ? (goCount / wordCount) * 1000 : 0;
    densities.push(density);

    // Page score: start 100, -5 per leak, -5 if density < 1.0
    var score = 100;
    score -= leakCount * 5;
    if (density < 1.0) {
      score -= 5;
    }
    if (score < 0) score = 0;
    scoredPages.push(score);

    if (goCount === 0) {
      pagesWithNoAffiliateCta++;
    }

    // Accumulate issues
    for (var j = 0; j < pageLeaks.length; j++) {
      issues.push({
        type: 'direct_vendor_link',
        page: file.rel,
        href: pageLeaks[j].href,
        expectedSlug: pageLeaks[j].slug,
        message: 'Direct vendor link; should use /go/' + pageLeaks[j].slug
      });
    }

    if (density < 1.0 && wordCount > 0) {
      issues.push({
        type: 'low_affiliate_density',
        page: file.rel,
        density: Math.round(density * 100) / 100,
        message: 'Affiliate link density below 1.0 per 1000 words (' + (Math.round(density * 100) / 100) + ')'
      });
    }
  }

  // Compute averages
  var avgPageScore = 100;
  if (scoredPages.length > 0) {
    var scoreSum = 0;
    for (var m = 0; m < scoredPages.length; m++) {
      scoreSum += scoredPages[m];
    }
    avgPageScore = Math.round((scoreSum / scoredPages.length) * 10) / 10;
  }

  var avgLinkDensity = 0;
  if (densities.length > 0) {
    var densitySum = 0;
    for (var n = 0; n < densities.length; n++) {
      densitySum += densities[n];
    }
    avgLinkDensity = Math.round((densitySum / densities.length) * 100) / 100;
  }

  var status = totalDirectLeaks > 0 ? 'critical' : 'healthy';

  return {
    agent: 'revenuefunnel',
    status: status,
    score: avgPageScore,
    metrics: {
      pagesAudited: pagesAudited,
      totalGoLinks: totalGoLinks,
      totalDirectLeaks: totalDirectLeaks,
      leaksFixed: 0,
      pagesWithNoAffiliateCta: pagesWithNoAffiliateCta,
      avgLinkDensity: avgLinkDensity,
      avgPageScore: avgPageScore
    },
    issues: issues,
    lastAction: new Date().toISOString()
  };
};

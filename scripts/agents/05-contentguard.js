'use strict';

var scanner = require('./lib/html-scanner');

var NAME_PATTERNS = [
  /Matt\s/gi,
  /Matthew/gi,
  /Schneider/gi,
  /Toptal/gi,
];

var BANNED_PHRASES = [
  "stands out",
  "it's worth noting",
  "it\u2019s worth noting",
  "comprehensive solution",
  "robust platform",
  "seamlessly integrates",
  "game-changer",
  "game changer",
  "landscape",
  "navigate",
  "leverage",
  "streamline",
];

var DEMO_TOOLS = [
  'gong',
  'chorus',
  'outreach',
  'salesloft',
  'zoominfo',
  'clearbit',
  'clari',
  'orum',
];

var SCHEMA_REQUIREMENTS = {
  'review':       ['Review', 'BreadcrumbList', 'FAQPage'],
  'comparison':   ['Article', 'BreadcrumbList', 'FAQPage'],
  'best-pick':    ['Article', 'BreadcrumbList', 'ItemList', 'FAQPage'],
  'pricing':      ['Article', 'BreadcrumbList', 'FAQPage'],
  'category':     ['ItemList', 'BreadcrumbList', 'FAQPage'],
  'alternatives': ['Article', 'BreadcrumbList', 'ItemList', 'FAQPage'],
};

function stripScriptsStylesTags(html) {
  var text = html.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  text = text.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  text = text.replace(/<[^>]+>/g, ' ');
  text = text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#\d+;/g, ' ');
  return text;
}

function checkNameLeaks(visibleText, rel) {
  var found = [];
  for (var i = 0; i < NAME_PATTERNS.length; i++) {
    var pattern = NAME_PATTERNS[i];
    pattern.lastIndex = 0;
    var match;
    while ((match = pattern.exec(visibleText)) !== null) {
      found.push({ page: rel, pattern: pattern.toString(), match: match[0].trim() });
    }
  }
  return found;
}

function checkBannedPhrases(visibleText, rel) {
  var found = [];
  var lowerText = visibleText.toLowerCase();
  for (var i = 0; i < BANNED_PHRASES.length; i++) {
    var phrase = BANNED_PHRASES[i];
    if (lowerText.indexOf(phrase.toLowerCase()) !== -1) {
      found.push({ page: rel, phrase: phrase });
    }
  }
  return found;
}

function checkDemoCta(html, rel) {
  var relNorm = rel.replace(/\\/g, '/').toLowerCase();
  var toolMatched = null;
  for (var i = 0; i < DEMO_TOOLS.length; i++) {
    if (relNorm.indexOf(DEMO_TOOLS[i]) !== -1) {
      toolMatched = DEMO_TOOLS[i];
      break;
    }
  }
  if (!toolMatched) return null;

  var ctaPatterns = [
    /Start Free Trial/i,
    /Try Free/i,
    /Try\s+\w+\s+Free/i,
  ];
  for (var j = 0; j < ctaPatterns.length; j++) {
    if (ctaPatterns[j].test(html)) {
      return null;
    }
  }
  return {
    page: rel,
    tool: toolMatched,
    issue: 'Missing demo CTA (Start Free Trial / Try Free)',
  };
}

function collectSchemaTypes(jsonLdBlocks) {
  var presentTypes = {};
  for (var i = 0; i < jsonLdBlocks.length; i++) {
    var block = jsonLdBlocks[i];
    if (block['@type']) {
      var types = Array.isArray(block['@type']) ? block['@type'] : [block['@type']];
      for (var j = 0; j < types.length; j++) {
        presentTypes[types[j]] = true;
      }
    }
    if (block['@graph'] && Array.isArray(block['@graph'])) {
      for (var k = 0; k < block['@graph'].length; k++) {
        var node = block['@graph'][k];
        if (node['@type']) {
          var nodeTypes = Array.isArray(node['@type']) ? node['@type'] : [node['@type']];
          for (var m = 0; m < nodeTypes.length; m++) {
            presentTypes[nodeTypes[m]] = true;
          }
        }
      }
    }
  }
  return presentTypes;
}

function checkSchema(html, rel, pageType) {
  var required = SCHEMA_REQUIREMENTS[pageType];
  if (!required) return [];

  var jsonLdBlocks = scanner.extractJsonLd(html);
  var presentTypes = collectSchemaTypes(jsonLdBlocks);

  var missing = [];
  for (var n = 0; n < required.length; n++) {
    if (!presentTypes[required[n]]) {
      missing.push({ page: rel, missingType: required[n], pageType: pageType });
    }
  }
  return missing;
}

module.exports = async function audit(siteRoot) {
  var issues = [];
  var metrics = {
    pagesScanned: 0,
    nameLeaks: 0,
    bannedPhrases: 0,
    bannedPhrasesFixed: 0,
    ratingMismatches: 0,
    demoCtaErrors: 0,
    demoCtaFixed: 0,
    schemaErrors: 0,
    thinContentPages: 0,
  };

  var files = scanner.getAllHtmlFiles(siteRoot);
  metrics.pagesScanned = files.length;

  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    var html = scanner.readHtml(file.abs);
    var pageType = scanner.classifyPage(file.rel);
    var visibleText = stripScriptsStylesTags(html);

    // Check 1: Name leaks (CRITICAL)
    var nameLeakResults = checkNameLeaks(visibleText, file.rel);
    for (var n = 0; n < nameLeakResults.length; n++) {
      metrics.nameLeaks++;
      issues.push({
        severity: 'CRITICAL',
        check: 'name-leak',
        page: nameLeakResults[n].page,
        detail: 'Name leak detected: "' + nameLeakResults[n].match + '" matched ' + nameLeakResults[n].pattern,
      });
    }

    // Check 2: Banned phrases
    var bannedResults = checkBannedPhrases(visibleText, file.rel);
    for (var b = 0; b < bannedResults.length; b++) {
      metrics.bannedPhrases++;
      issues.push({
        severity: 'warning',
        check: 'banned-phrase',
        page: bannedResults[b].page,
        detail: 'Banned phrase found: "' + bannedResults[b].phrase + '"',
      });
    }

    // Check 3: Demo CTA
    var ctaError = checkDemoCta(html, file.rel);
    if (ctaError) {
      metrics.demoCtaErrors++;
      issues.push({
        severity: 'warning',
        check: 'demo-cta',
        page: ctaError.page,
        detail: ctaError.issue + ' (tool: ' + ctaError.tool + ')',
      });
    }

    // Check 4: Schema by page type
    var schemaErrors = checkSchema(html, file.rel, pageType);
    for (var s = 0; s < schemaErrors.length; s++) {
      metrics.schemaErrors++;
      issues.push({
        severity: 'warning',
        check: 'schema',
        page: schemaErrors[s].page,
        detail: 'Missing schema type "' + schemaErrors[s].missingType + '" for page type "' + schemaErrors[s].pageType + '"',
      });
    }

    // Check 5: Thin content (skip homepage and other)
    if (pageType !== 'homepage' && pageType !== 'other') {
      var wordCount = scanner.countWords(html);
      if (wordCount < 800) {
        metrics.thinContentPages++;
        issues.push({
          severity: 'warning',
          check: 'thin-content',
          page: file.rel,
          detail: 'Thin content: ' + wordCount + ' words (minimum 800)',
        });
      }
    }
  }

  // Scoring: 100 - (nameLeaks*25) - min(bannedPhraseCount,10) - (demoCtaErrors*5) - (schemaErrors*2) - thinContentPages
  var score = 100;
  score -= metrics.nameLeaks * 25;
  score -= Math.min(metrics.bannedPhrases, 10);
  score -= metrics.demoCtaErrors * 5;
  score -= metrics.schemaErrors * 2;
  score -= metrics.thinContentPages;
  if (score < 0) score = 0;
  if (score > 100) score = 100;

  var status;
  if (metrics.nameLeaks > 0) {
    status = 'critical';
  } else if (score >= 80) {
    status = 'healthy';
  } else {
    status = 'warning';
  }

  return {
    agent: 'contentguard',
    status: status,
    score: score,
    metrics: metrics,
    issues: issues,
    lastAction: null,
  };
};

// Smoke test
if (require.main === module) {
  var path = require('path');
  var siteRoot = path.resolve(__dirname, '../../');
  module.exports(siteRoot).then(function(result) {
    console.log(JSON.stringify(result, null, 2));
  }).catch(function(err) {
    console.error('Error:', err.message);
    process.exit(1);
  });
}

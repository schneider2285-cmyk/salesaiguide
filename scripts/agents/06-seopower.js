'use strict';

var scanner = require('./lib/html-scanner');

var WORD_TARGETS = {
  'review': 2500,
  'comparison': 2000,
  'best-pick': 1500,
  'pricing': 1000,
  'alternatives': 1200,
  'category': 800,
  'homepage': 500
};

var TITLE_2026_TYPES = ['comparison', 'best-pick'];

function countH1(html) {
  var regex = /<h1[\s>]/gi;
  var count = 0;
  var m;
  while ((m = regex.exec(html)) !== null) {
    count++;
  }
  return count;
}

function countH2(html) {
  var regex = /<h2[\s>]/gi;
  var count = 0;
  var m;
  while ((m = regex.exec(html)) !== null) {
    count++;
  }
  return count;
}

function countImages(html) {
  var total = 0;
  var withAlt = 0;
  var regex = /<img\b([^>]*)>/gi;
  var altRegex = /\balt=["']([^"']*)["']/i;
  var m;
  while ((m = regex.exec(html)) !== null) {
    total++;
    var attrs = m[1];
    var altMatch = altRegex.exec(attrs);
    if (altMatch && altMatch[1].trim().length > 0) {
      withAlt++;
    }
  }
  return { total: total, withAlt: withAlt };
}

function hasCanonical(html) {
  return /<link\s[^>]*rel=["']canonical["'][^>]*>/i.test(html) ||
         /<link\s[^>]*rel=canonical[^>]*>/i.test(html);
}

function scorePage(html, rel, pageType) {
  var issues = [];
  var score = 0;

  // Title (15pts)
  var title = scanner.extractTitle(html);
  var titleScore = 0;
  if (title) {
    titleScore += 7;
    if (title.length >= 30 && title.length <= 60) {
      titleScore += 5;
    } else {
      issues.push('title-length:' + rel + ' (' + title.length + ' chars)');
    }
    if (TITLE_2026_TYPES.indexOf(pageType) !== -1) {
      if (title.indexOf('2026') !== -1) {
        titleScore += 3;
      } else {
        issues.push('title-missing-2026:' + rel);
      }
    } else {
      titleScore += 3;
    }
  } else {
    issues.push('missing-title:' + rel);
  }
  score += titleScore;

  // Meta description (10pts)
  var metaDesc = scanner.extractMetaDesc(html);
  var metaScore = 0;
  if (metaDesc) {
    metaScore += 5;
    if (metaDesc.length >= 120 && metaDesc.length <= 160) {
      metaScore += 5;
    } else {
      issues.push('meta-desc-length:' + rel + ' (' + metaDesc.length + ' chars)');
    }
  } else {
    issues.push('missing-meta-desc:' + rel);
  }
  score += metaScore;

  // H1 (10pts): exactly one
  var h1Count = countH1(html);
  if (h1Count === 1) {
    score += 10;
  } else if (h1Count === 0) {
    issues.push('missing-h1:' + rel);
  } else {
    issues.push('multiple-h1:' + rel + ' (' + h1Count + ')');
    score += 5;
  }

  // H2 structure (10pts)
  var h2Count = countH2(html);
  var h2Min = (pageType === 'review' || pageType === 'comparison') ? 4 : 2;
  if (h2Count >= h2Min) {
    score += 10;
  } else {
    issues.push('insufficient-h2:' + rel + ' (' + h2Count + '/' + h2Min + ')');
    score += Math.round(10 * (h2Count / h2Min));
  }

  // Content depth (15pts)
  var target = WORD_TARGETS[pageType] || 800;
  var words = scanner.countWords(html);
  var depthRatio = Math.min(1, words / target);
  var depthScore = Math.round(15 * depthRatio);
  if (depthRatio < 1) {
    issues.push('content-thin:' + rel + ' (' + words + '/' + target + ' words)');
  }
  score += depthScore;

  // Schema (10pts)
  var schemas = scanner.extractJsonLd(html);
  var validSchema = false;
  for (var i = 0; i < schemas.length; i++) {
    if (schemas[i]['@type'] && !schemas[i]._parseError) {
      validSchema = true;
      break;
    }
  }
  if (validSchema) {
    score += 10;
  } else {
    issues.push('missing-schema:' + rel);
  }

  // Freshness (10pts): "2026" appears in page
  if (html.indexOf('2026') !== -1) {
    score += 10;
  } else {
    issues.push('stale-content:' + rel);
  }

  // Internal links (10pts): >=5 = full marks
  var internalLinks = scanner.extractInternalLinks(html);
  if (internalLinks.length >= 5) {
    score += 10;
  } else {
    issues.push('few-internal-links:' + rel + ' (' + internalLinks.length + ')');
    score += Math.round(10 * (internalLinks.length / 5));
  }

  // Images (5pts): ratio with non-empty alt
  var imgData = countImages(html);
  if (imgData.total === 0) {
    score += 5;
  } else {
    var altRatio = imgData.withAlt / imgData.total;
    score += Math.round(5 * altRatio);
    if (altRatio < 1) {
      issues.push('images-missing-alt:' + rel + ' (' + imgData.withAlt + '/' + imgData.total + ')');
    }
  }

  // Canonical (5pts)
  if (hasCanonical(html)) {
    score += 5;
  } else {
    issues.push('missing-canonical:' + rel);
  }

  return {
    score: Math.min(100, score),
    issues: issues,
    missingMetaDesc: !metaDesc,
    stale: html.indexOf('2026') === -1
  };
}

module.exports = async function audit(siteRoot) {
  var files = scanner.getAllHtmlFiles(siteRoot);

  var pagesAudited = 0;
  var totalScore = 0;
  var pagesAbove80 = 0;
  var pagesBelow50 = 0;
  var missingMetaDesc = 0;
  var staleFreshness = 0;
  var allIssues = [];

  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    var pageType = scanner.classifyPage(file.rel);

    if (pageType === 'other' && file.rel.replace(/\\/g, '/') !== 'index.html') {
      continue;
    }

    var html;
    try {
      html = scanner.readHtml(file.abs);
    } catch (e) {
      allIssues.push('read-error:' + file.rel);
      continue;
    }

    var result = scorePage(html, file.rel, pageType);
    pagesAudited++;
    totalScore += result.score;

    if (result.score >= 80) {
      pagesAbove80++;
    } else if (result.score < 50) {
      pagesBelow50++;
    }

    if (result.missingMetaDesc) {
      missingMetaDesc++;
    }

    if (result.stale) {
      staleFreshness++;
    }

    for (var j = 0; j < result.issues.length; j++) {
      allIssues.push(result.issues[j]);
    }
  }

  var avgSeoScore = pagesAudited > 0 ? Math.round(totalScore / pagesAudited) : 0;

  var status;
  if (avgSeoScore >= 80) {
    status = 'healthy';
  } else if (avgSeoScore >= 50) {
    status = 'warning';
  } else {
    status = 'critical';
  }

  return {
    agent: 'seopower',
    status: status,
    score: avgSeoScore,
    metrics: {
      pagesAudited: pagesAudited,
      avgSeoScore: avgSeoScore,
      pagesAbove80: pagesAbove80,
      pagesBelow50: pagesBelow50,
      missingMetaDesc: missingMetaDesc,
      staleFreshness: staleFreshness,
      autoFixed: 0
    },
    issues: allIssues,
    lastAction: 'audited ' + pagesAudited + ' pages, avgScore=' + avgSeoScore
  };
};

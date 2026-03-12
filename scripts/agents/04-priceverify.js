'use strict';

var fs = require('fs');
var path = require('path');
var scanner = require('./lib/html-scanner');

var PRICE_RE = /\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/i;

function buildPriceTruth(siteRoot) {
  var toolsDir = path.join(siteRoot, 'tools');
  var truth = {};
  var entries;
  try {
    entries = fs.readdirSync(toolsDir);
  } catch (e) {
    return truth;
  }
  var reviewFiles = entries.filter(function(f) {
    return f.endsWith('-review.html');
  });
  for (var i = 0; i < reviewFiles.length; i++) {
    var filename = reviewFiles[i];
    var slug = filename.replace('-review.html', '');
    var filePath = path.join(toolsDir, filename);
    var html;
    try {
      html = scanner.readHtml(filePath);
    } catch (e) {
      continue;
    }
    var m = html.match(PRICE_RE);
    if (m) {
      truth[slug] = m[0];
    }
  }
  return truth;
}

function normSlug(slug) {
  return slug.replace(/-/g, '').toLowerCase();
}

module.exports = async function audit(siteRoot) {
  var issues = [];
  var priceTruth = buildPriceTruth(siteRoot);
  var slugs = Object.keys(priceTruth);
  var toolsAudited = slugs.length;

  var normSlugs = {};
  for (var s = 0; s < slugs.length; s++) {
    normSlugs[slugs[s]] = normSlug(slugs[s]);
  }

  var allFiles = scanner.getAllHtmlFiles(siteRoot);
  var inconsistentSet = {};

  for (var f = 0; f < allFiles.length; f++) {
    var fileInfo = allFiles[f];
    var rel = fileInfo.rel.replace(/\\/g, '/');

    if (/^tools\/[^/]+-review\.html$/.test(rel)) {
      continue;
    }

    var html;
    try {
      html = scanner.readHtml(fileInfo.abs);
    } catch (e) {
      continue;
    }

    var lowerRel = rel.toLowerCase();

    for (var si = 0; si < slugs.length; si++) {
      var slug = slugs[si];
      var ns = normSlugs[slug];

      if (lowerRel.indexOf(ns) === -1) {
        continue;
      }

      var canonical = priceTruth[slug];
      var pricePattern = /\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/gi;
      var pageMatch;
      var foundMismatch = false;

      while ((pageMatch = pricePattern.exec(html)) !== null) {
        var found = pageMatch[0];
        var normFound = found.replace(/\s*\/\s*/g, '/').toLowerCase();
        var normCanon = canonical.replace(/\s*\/\s*/g, '/').toLowerCase();
        if (normFound !== normCanon) {
          foundMismatch = true;
          issues.push({
            type: 'price_mismatch',
            severity: 'high',
            file: rel,
            detail: 'Expected ' + canonical + ' (from ' + slug + '-review.html) but found ' + found
          });
          break;
        }
      }

      if (foundMismatch) {
        inconsistentSet[slug] = true;
      }
    }
  }

  var inconsistentTools = Object.keys(inconsistentSet).length;
  var consistentTools = toolsAudited - inconsistentTools;
  var rawScore = 100 - (inconsistentTools * 15);
  var score = rawScore < 0 ? 0 : rawScore;
  var status = inconsistentTools > 0 ? 'warning' : 'healthy';

  return {
    agent: 'priceverify',
    status: status,
    score: score,
    metrics: {
      toolsAudited: toolsAudited,
      consistentTools: consistentTools,
      inconsistentTools: inconsistentTools,
      staleTools: 0,
      autoFixed: 0
    },
    issues: issues,
    lastAction: 'Audited ' + toolsAudited + ' tool prices across ' + allFiles.length + ' pages'
  };
};

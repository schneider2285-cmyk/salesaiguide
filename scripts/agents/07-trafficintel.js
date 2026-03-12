'use strict';

var scanner = require('./lib/html-scanner');
var extractGoLinks = scanner.extractGoLinks;
var extractInternalLinks = scanner.extractInternalLinks;
var extractJsonLd = scanner.extractJsonLd;
var countWords = scanner.countWords;
var classifyPage = scanner.classifyPage;
var extractTitle = scanner.extractTitle;
var getAllHtmlFiles = scanner.getAllHtmlFiles;
var readHtml = scanner.readHtml;

var COMMERCIAL_INTENT = {
  'pricing': 10,
  'best-pick': 9,
  'comparison': 8,
  'alternatives': 7,
  'review': 7,
  'category': 6,
  'homepage': 3,
  'other': 3
};

function competitionProxy(title) {
  if (!title) return 0.3;
  var words = title.trim().split(/\s+/).filter(function(w) { return w.length > 0; });
  if (words.length >= 5) return 0.9;
  if (words.length >= 3) return 0.6;
  return 0.3;
}

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);
  var pages = [];

  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    var pageType = classifyPage(file.rel);

    if (pageType === 'other' && file.rel !== 'index.html') {
      continue;
    }

    var html = readHtml(file.abs);
    var goLinks = extractGoLinks(html);
    var internalLinks = extractInternalLinks(html);
    var schemas = extractJsonLd(html);
    var words = countWords(html);
    var title = extractTitle(html);

    var ci = COMMERCIAL_INTENT[pageType] !== undefined ? COMMERCIAL_INTENT[pageType] : 3;
    var cp = competitionProxy(title);
    var quality = Math.min((words / 2000) * 30 + schemas.length * 10 + internalLinks.length * 2, 100);
    var rawScore = ci * cp * (goLinks.length * 2 + quality) / 20;
    var revenueScore = Math.min(Math.round(rawScore), 100);

    pages.push({
      rel: file.rel,
      pageType: pageType,
      revenueScore: revenueScore
    });
  }

  var pagesAnalyzed = pages.length;
  var highPotentialPages = 0;
  var underperformingPages = 0;
  var totalScore = 0;

  for (var j = 0; j < pages.length; j++) {
    var s = pages[j].revenueScore;
    totalScore += s;
    if (s >= 60) highPotentialPages++;
    if (s < 20) underperformingPages++;
  }

  var avgRevenueScore = pagesAnalyzed > 0 ? Math.round(totalScore / pagesAnalyzed) : 0;

  return {
    agent: 'trafficintel',
    status: 'healthy',
    score: Math.round(avgRevenueScore),
    metrics: {
      pagesAnalyzed: pagesAnalyzed,
      highPotentialPages: highPotentialPages,
      underperformingPages: underperformingPages,
      avgRevenueScore: avgRevenueScore
    },
    issues: [],
    lastAction: 'Revenue potential scored across ' + pagesAnalyzed + ' pages'
  };
};

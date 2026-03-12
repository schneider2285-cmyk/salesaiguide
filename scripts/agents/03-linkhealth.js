// scripts/agents/03-linkhealth.js
var fs = require('fs');
var path = require('path');
var scanner = require('./lib/html-scanner');

function normalizeHref(href) {
  var h = href.replace(/^\//, '').replace(/\/$/, '/index.html');
  if (!h.endsWith('.html')) {
    if (h.endsWith('/')) h += 'index.html';
    else h += '.html';
  }
  return h;
}

module.exports = async function audit(siteRoot) {
  var files = scanner.getAllHtmlFiles(siteRoot);
  var issues = [];
  var fileSet = {};
  for (var i = 0; i < files.length; i++) fileSet[files[i].rel] = true;

  var inbound = {};
  for (var i = 0; i < files.length; i++) inbound[files[i].rel] = 0;

  var totalInternalLinks = 0;

  for (var i = 0; i < files.length; i++) {
    var html = scanner.readHtml(files[i].abs);
    var links = scanner.extractInternalLinks(html);
    totalInternalLinks += links.length;

    for (var j = 0; j < links.length; j++) {
      var target = normalizeHref(links[j]);
      if (inbound[target] !== undefined) {
        inbound[target]++;
      }
    }
  }

  // Orphan detection
  var orphans = [];
  var pages = Object.keys(inbound);
  for (var i = 0; i < pages.length; i++) {
    var page = pages[i];
    var count = inbound[page];
    if (count < 3 && page !== 'index.html' && page !== '404.html') {
      orphans.push({ page: page, inboundLinks: count });
      issues.push({
        check: 'orphan_page',
        severity: count === 0 ? 'high' : 'med',
        detail: page + ': only ' + count + ' inbound links (minimum 3)'
      });
    }
  }

  // Cross-link gap detection
  var missingCrossLinks = 0;
  for (var i = 0; i < files.length; i++) {
    var rel = files[i].rel;
    var type = scanner.classifyPage(rel);
    if (type !== 'comparison') continue;

    var html = scanner.readHtml(files[i].abs);
    var basename = path.basename(rel, '.html');
    var parts = basename.split('-vs-');
    if (parts.length !== 2) continue;

    for (var p = 0; p < parts.length; p++) {
      var slug = parts[p];
      var reviewPath = 'tools/' + slug + '-review.html';
      if (fileSet[reviewPath] && html.indexOf('/' + slug + '-review') === -1) {
        missingCrossLinks++;
      }
    }
  }

  if (missingCrossLinks > 0) {
    issues.push({
      check: 'missing_cross_links',
      severity: 'med',
      detail: missingCrossLinks + ' cross-link opportunities remaining across comparison and review pages'
    });
  }

  // Sitemap consistency
  var sitemapConsistent = true;
  var sitemapPath = path.join(siteRoot, 'sitemap-core.xml');
  if (fs.existsSync(sitemapPath)) {
    var xml = fs.readFileSync(sitemapPath, 'utf8');
    var locRe = /<loc>([^<]+)<\/loc>/g;
    var match;
    while ((match = locRe.exec(xml)) !== null) {
      var url = match[1].replace('https://salesaiguide.com/', '').replace(/\/$/, '');
      var expected = url === '' ? 'index.html' : url + '.html';
      if (!fileSet[expected] && !fileSet[url + '/index.html'] && !fileSet[url]) {
        sitemapConsistent = false;
      }
    }
  }

  var avgLinksPerPage = files.length > 0 ? +(totalInternalLinks / files.length).toFixed(1) : 0;

  var score = 100;
  score -= orphans.length * 5;
  score -= Math.min(missingCrossLinks * 0.2, 50);
  score = Math.max(0, Math.min(100, Math.round(score)));

  return {
    agent: 'linkhealth',
    status: score >= 80 ? 'healthy' : score >= 50 ? 'warning' : 'critical',
    score: score,
    metrics: {
      totalInternalLinks: totalInternalLinks,
      orphanedPages: orphans.length,
      avgLinksPerPage: avgLinksPerPage,
      missingCrossLinks: missingCrossLinks,
      sitemapConsistent: sitemapConsistent
    },
    issues: issues.slice(0, 50),
    lastAction: 'Mapped ' + totalInternalLinks + ' internal links across ' + files.length + ' pages. ' + orphans.length + ' orphans, ' + missingCrossLinks + ' cross-link gaps.'
  };
};

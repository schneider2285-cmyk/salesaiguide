'use strict';

var scanner = require('./lib/html-scanner');
var extractGoLinks = scanner.extractGoLinks;
var readHtml = scanner.readHtml;
var getAllHtmlFiles = scanner.getAllHtmlFiles;

module.exports = async function audit(siteRoot, otherResults) {
  var files = getAllHtmlFiles(siteRoot);

  // Build affiliate inventory: slug -> count of /go/<slug> links across all pages
  var slugCounts = {};
  var totalGoLinksAcrossSite = 0;

  for (var i = 0; i < files.length; i++) {
    var html = readHtml(files[i].abs);
    var goLinks = extractGoLinks(html);
    for (var j = 0; j < goLinks.length; j++) {
      var href = goLinks[j];
      // href is like /go/slug or /go/slug/path — extract slug as first segment after /go/
      var parts = href.replace(/^\/go\//, '').split('/');
      var slug = parts[0];
      if (!slug) continue;
      slugCounts[slug] = (slugCounts[slug] || 0) + 1;
      totalGoLinksAcrossSite++;
    }
  }

  var totalGoSlugs = Object.keys(slugCounts).length;

  // Concentration risk: top 3 slugs' share of total links
  var slugEntries = [];
  var slugKeys = Object.keys(slugCounts);
  for (var k = 0; k < slugKeys.length; k++) {
    slugEntries.push({ slug: slugKeys[k], count: slugCounts[slugKeys[k]] });
  }
  slugEntries.sort(function(a, b) { return b.count - a.count; });

  var top3Count = 0;
  for (var t = 0; t < Math.min(3, slugEntries.length); t++) {
    top3Count += slugEntries[t].count;
  }

  var concentrationRatio = totalGoLinksAcrossSite > 0 ? top3Count / totalGoLinksAcrossSite : 0;
  var concentrationRisk;
  if (concentrationRatio > 0.5) {
    concentrationRisk = 'high';
  } else if (concentrationRatio > 0.3) {
    concentrationRisk = 'medium';
  } else {
    concentrationRisk = 'low';
  }

  // Pull totalDirectLeaks from revenuefunnel result if present
  var totalDirectLeaks = 0;
  if (otherResults && otherResults.revenuefunnel && otherResults.revenuefunnel.metrics) {
    var rfm = otherResults.revenuefunnel.metrics;
    if (typeof rfm.totalDirectLeaks === 'number') {
      totalDirectLeaks = rfm.totalDirectLeaks;
    } else if (typeof rfm.directLeaks === 'number') {
      totalDirectLeaks = rfm.directLeaks;
    }
  }

  // Build action queue from critical/high severity issues across all other agents
  var actionQueue = [];
  if (otherResults && typeof otherResults === 'object') {
    var agentKeys = Object.keys(otherResults);
    for (var ai = 0; ai < agentKeys.length; ai++) {
      var agentResult = otherResults[agentKeys[ai]];
      if (!agentResult || !Array.isArray(agentResult.issues)) continue;
      for (var ii = 0; ii < agentResult.issues.length; ii++) {
        var issue = agentResult.issues[ii];
        var sev = issue.severity ? String(issue.severity).toLowerCase() : '';
        if (sev === 'critical' || sev === 'high') {
          actionQueue.push({
            priority: 'P0',
            source: agentKeys[ai],
            issue: issue.message || issue.description || JSON.stringify(issue)
          });
        }
      }
    }
  }

  return {
    agent: 'revenueops',
    status: 'healthy',
    score: null,
    metrics: {
      totalGoSlugs: totalGoSlugs,
      totalGoLinksAcrossSite: totalGoLinksAcrossSite,
      totalDirectLeaks: totalDirectLeaks,
      concentrationRisk: concentrationRisk,
      weeklyActionItems: actionQueue
    },
    issues: [],
    lastAction: 'Affiliate inventory built: ' + totalGoSlugs + ' slugs, ' + totalGoLinksAcrossSite + ' total links'
  };
};

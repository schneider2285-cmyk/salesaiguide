'use strict';

var path = require('path');
var scanner = require('./lib/html-scanner');
var getAllHtmlFiles = scanner.getAllHtmlFiles;
var classifyPage = scanner.classifyPage;

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);

  var toolSlugs = [];
  var existingComparisons = [];
  var existingBestPicks = 0;
  var existingAlternatives = [];

  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    var rel = file.rel.replace(/\\/g, '/');
    var pageType = classifyPage(rel);

    if (pageType === 'review') {
      var basename = path.basename(rel, '.html');
      var slug = basename.replace(/-review$/, '');
      toolSlugs.push(slug);
    } else if (pageType === 'comparison') {
      existingComparisons.push(rel);
    } else if (pageType === 'best-pick') {
      existingBestPicks++;
    } else if (pageType === 'alternatives') {
      var altBasename = path.basename(rel, '.html');
      var altSlug = altBasename.replace(/-alternatives$/, '');
      existingAlternatives.push(altSlug);
    }
  }

  // Build set of existing comparison pairs (both orderings)
  var existingPairSet = {};
  for (var c = 0; c < existingComparisons.length; c++) {
    var compRel = existingComparisons[c];
    var compBase = path.basename(compRel, '.html');
    // e.g. apollo-vs-clearbit
    var parts = compBase.split('-vs-');
    if (parts.length === 2) {
      var key1 = parts[0] + '-vs-' + parts[1];
      var key2 = parts[1] + '-vs-' + parts[0];
      existingPairSet[key1] = true;
      existingPairSet[key2] = true;
    }
  }

  // Count comparison gaps: all tool pairs minus existing
  var comparisonGaps = 0;
  for (var a = 0; a < toolSlugs.length; a++) {
    for (var b = a + 1; b < toolSlugs.length; b++) {
      var pairKey = toolSlugs[a] + '-vs-' + toolSlugs[b];
      if (!existingPairSet[pairKey]) {
        comparisonGaps++;
      }
    }
  }

  // Alternatives gaps: tools without *-alternatives page
  var altSet = {};
  for (var ae = 0; ae < existingAlternatives.length; ae++) {
    altSet[existingAlternatives[ae]] = true;
  }
  var alternativesGaps = 0;
  for (var t = 0; t < toolSlugs.length; t++) {
    if (!altSet[toolSlugs[t]]) {
      alternativesGaps++;
    }
  }

  // Best picks gaps: 7 minus existing
  var bestPicksGaps = Math.max(0, 7 - existingBestPicks);

  // Top opportunity
  var topOpportunity;
  if (comparisonGaps >= alternativesGaps && comparisonGaps >= bestPicksGaps) {
    topOpportunity = 'comparison pages (' + comparisonGaps + ' gaps)';
  } else if (alternativesGaps >= bestPicksGaps) {
    topOpportunity = 'alternatives pages (' + alternativesGaps + ' gaps)';
  } else {
    topOpportunity = 'best-pick pages (' + bestPicksGaps + ' gaps)';
  }

  return {
    agent: 'contentengine',
    status: 'healthy',
    score: null,
    metrics: {
      comparisonGaps: comparisonGaps,
      bestPicksGaps: bestPicksGaps,
      alternativesGaps: alternativesGaps,
      briefsGenerated: 0,
      topOpportunity: topOpportunity
    },
    issues: [],
    lastAction: 'Content gap analysis complete: ' + comparisonGaps + ' comparison gaps, ' + alternativesGaps + ' alternatives gaps'
  };
};

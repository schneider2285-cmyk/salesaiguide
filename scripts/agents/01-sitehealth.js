'use strict';

var path = require('path');
var scanner = require('./lib/html-scanner');

var GA4_ID = 'G-VRBZ6Z6885';
var AGENT_NAME = 'sitehealth';

function clamp(n, lo, hi) {
  return n < lo ? lo : n > hi ? hi : n;
}

function addIssue(issues, check, severity, detail) {
  if (issues.length < 50) {
    issues.push({ check: check, severity: severity, detail: detail });
  }
}

function checkGa4(html, rel, issues) {
  if (html.indexOf(GA4_ID) === -1) {
    addIssue(issues, 'ga4', 'high', 'Missing GA4 snippet (' + GA4_ID + ') in ' + rel);
    return false;
  }
  return true;
}

function checkCanonical(html, rel, issues) {
  var match = html.match(/<link[^>]+rel=["']canonical["'][^>]*>/i)
    || html.match(/<link[^>]+rel=canonical[^>]*>/i);
  if (!match) {
    addIssue(issues, 'canonical', 'med', 'Missing canonical tag in ' + rel);
    return false;
  }
  var tag = match[0];
  var hrefMatch = tag.match(/href=["']([^"']+)["']/i);
  if (!hrefMatch) {
    addIssue(issues, 'canonical', 'med', 'Canonical tag has no href in ' + rel);
    return false;
  }
  var href = hrefMatch[1];
  var valid = true;
  if (!href.match(/^https:\/\//)) {
    addIssue(issues, 'canonical', 'med', 'Canonical href does not start with https:// in ' + rel + ' (got: ' + href + ')');
    valid = false;
  }
  if (href.match(/\.html($|\?|#)/)) {
    addIssue(issues, 'canonical', 'med', 'Canonical href contains .html extension in ' + rel + ' (got: ' + href + ')');
    valid = false;
  }
  return valid;
}

function checkTitle(html, rel, issues) {
  var title = scanner.extractTitle(html);
  if (!title) {
    addIssue(issues, 'title', 'high', 'Missing title tag in ' + rel);
    return { ok: false, value: null };
  }
  if (title.length > 60) {
    addIssue(issues, 'title', 'high', 'Title exceeds 60 chars (' + title.length + ') in ' + rel);
    return { ok: false, value: title };
  }
  return { ok: true, value: title };
}

function checkMetaDesc(html, rel, issues) {
  var desc = scanner.extractMetaDesc(html);
  if (!desc) {
    addIssue(issues, 'meta-description', 'high', 'Missing meta description in ' + rel);
    return { ok: false, value: null };
  }
  var len = desc.length;
  if (len < 120 || len > 160) {
    addIssue(issues, 'meta-description', 'med', 'Meta description length ' + len + ' out of 120-160 range in ' + rel);
    return { ok: false, value: desc };
  }
  return { ok: true, value: desc };
}

function checkOgTags(html, rel, issues) {
  var hasOgTitle = /property=["']og:title["']/i.test(html)
    || /property=og:title/i.test(html);
  var hasOgDesc = /property=["']og:description["']/i.test(html)
    || /property=og:description/i.test(html);
  if (!hasOgTitle || !hasOgDesc) {
    var missing = [];
    if (!hasOgTitle) missing.push('og:title');
    if (!hasOgDesc) missing.push('og:description');
    addIssue(issues, 'og-tags', 'low', 'Missing OG tags [' + missing.join(', ') + '] in ' + rel);
    return false;
  }
  return true;
}

function checkJsonLd(html, rel, issues) {
  var blocks = scanner.extractJsonLd(html);
  var validCount = 0;
  var invalidCount = 0;
  for (var i = 0; i < blocks.length; i++) {
    var block = blocks[i];
    if (block._parseError) {
      addIssue(issues, 'json-ld', 'med', 'JSON-LD parse error in ' + rel + ': ' + block._parseError);
      invalidCount++;
    } else if (!block['@type']) {
      addIssue(issues, 'json-ld', 'med', 'JSON-LD block missing @type in ' + rel);
      invalidCount++;
    } else {
      validCount++;
    }
  }
  return { total: blocks.length, valid: validCount, invalid: invalidCount };
}

function extractNewsletterForms(html) {
  var results = [];
  var re = /<form[^>]+>/gi;
  var m;
  while ((m = re.exec(html)) !== null) {
    var tag = m[0];
    var classMatch = tag.match(/class=["']([^"']*)["']/i);
    if (!classMatch) continue;
    var cls = classMatch[1];
    if (cls.indexOf('newsletter') === -1) continue;
    var actionMatch = tag.match(/action=["']([^"']*)["']/i);
    results.push({ action: actionMatch ? actionMatch[1] : null });
  }
  return results;
}

function checkNewsletterForms(html, rel, issues) {
  var forms = extractNewsletterForms(html);
  var total = forms.length;
  var validCount = 0;
  for (var i = 0; i < forms.length; i++) {
    var action = forms[i].action;
    if (action && action.indexOf('buttondown.com') !== -1) {
      validCount++;
    } else {
      addIssue(issues, 'newsletter-form', 'low', 'Newsletter form action is not buttondown.com in ' + rel + ' (got: ' + (action || '(none)') + ')');
    }
  }
  return { total: total, valid: validCount };
}

module.exports = async function audit(siteRoot) {
  var absRoot = path.resolve(siteRoot);
  var files = scanner.getAllHtmlFiles(absRoot);

  var score = 100;
  var issues = [];
  var titlesSeen = Object.create(null);
  var descsSeen = Object.create(null);
  var duplicateTitles = 0;
  var duplicateDescs = 0;

  var ga4PagesOk = 0;
  var canonicalsValid = 0;
  var descsValid = 0;
  var schemasTotal = 0;
  var schemasValid = 0;
  var newsletterFormsTotal = 0;
  var newsletterFormsValid = 0;

  var total = files.length;

  for (var i = 0; i < total; i++) {
    var file = files[i];
    var html = scanner.readHtml(file.abs);
    var rel = file.rel;

    var ga4Ok = checkGa4(html, rel, issues);
    if (ga4Ok) {
      ga4PagesOk++;
    } else {
      score -= 10;
    }

    var canonOk = checkCanonical(html, rel, issues);
    if (canonOk) {
      canonicalsValid++;
    } else {
      score -= 5;
    }

    var titleResult = checkTitle(html, rel, issues);
    if (!titleResult.ok) {
      score -= 3;
    }
    if (titleResult.value) {
      var tKey = titleResult.value.toLowerCase().trim();
      if (titlesSeen[tKey]) {
        addIssue(issues, 'duplicate-title', 'med', 'Duplicate title "' + titleResult.value + '" in ' + rel + ' (also: ' + titlesSeen[tKey] + ')');
        duplicateTitles++;
      } else {
        titlesSeen[tKey] = rel;
      }
    }

    var descResult = checkMetaDesc(html, rel, issues);
    if (!descResult.value) {
      score -= 3;
    } else if (!descResult.ok) {
      score -= 1;
    } else {
      descsValid++;
    }
    if (descResult.value) {
      var dKey = descResult.value.toLowerCase().trim();
      if (descsSeen[dKey]) {
        addIssue(issues, 'duplicate-description', 'low', 'Duplicate meta description in ' + rel + ' (also: ' + descsSeen[dKey] + ')');
        duplicateDescs++;
      } else {
        descsSeen[dKey] = rel;
      }
    }

    var ogOk = checkOgTags(html, rel, issues);
    if (!ogOk) {
      score -= 1;
    }

    var ldResult = checkJsonLd(html, rel, issues);
    schemasTotal += ldResult.total;
    schemasValid += ldResult.valid;
    score -= ldResult.invalid * 2;

    var nlResult = checkNewsletterForms(html, rel, issues);
    newsletterFormsTotal += nlResult.total;
    newsletterFormsValid += nlResult.valid;
    score -= (nlResult.total - nlResult.valid);
  }

  score -= duplicateTitles * 2;
  score -= duplicateDescs;

  score = clamp(score, 0, 100);

  var issueCount = issues.length;

  var status;
  if (score >= 80) {
    status = 'healthy';
  } else if (score >= 50) {
    status = 'warning';
  } else {
    status = 'critical';
  }

  var metrics = {
    pagesAudited: total,
    issuesFound: issueCount,
    issuesFixed: 0,
    ga4Coverage: ga4PagesOk + '/' + total,
    canonicalsValid: canonicalsValid,
    schemasValid: schemasValid,
    newsletterFormsValid: newsletterFormsValid,
    brokenLinks: 0
  };

  return {
    agent: AGENT_NAME,
    status: status,
    score: score,
    metrics: metrics,
    issues: issues,
    lastAction: new Date().toISOString()
  };
};

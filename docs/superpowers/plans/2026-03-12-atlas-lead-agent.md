# ATLAS Lead Agent Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the ATLAS orchestrator that autonomously runs 9 audit agents weekly, auto-fixes issues, commits, and deploys.

**Architecture:** Single Node.js entry point (`scripts/atlas.js`) runs 8 sequential phases. 9 agent scripts in `scripts/agents/` each export an `audit(siteRoot)` function returning a standard result object. `agent-autofix.js` is refactored to accept `--fix-plan` for targeted fixes. GitHub Actions cron triggers weekly.

**Tech Stack:** Node.js 20+ (stdlib only), Git, netlify-cli, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-03-12-atlas-lead-agent-design.md`

**Security note:** `scripts/atlas.js` uses `execSync` to call git and netlify-cli. All arguments are hardcoded strings (no user input), so command injection is not a risk. This is a CLI automation script, not a web server.

---

## Chunk 1: Shared Utilities

### Task 1: Create shared HTML scanner utility

**Files:**
- Create: `scripts/agents/lib/html-scanner.js`

- [ ] **Step 1: Create the shared scanner module**

```js
// scripts/agents/lib/html-scanner.js
const fs = require('fs');
const path = require('path');

const SKIP_DIRS = ['ops', 'node_modules', '.git', '.claude', '.playwright-cli', 'scripts', '.github'];

function getAllHtmlFiles(siteRoot) {
  const results = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(dir, e.name);
      const rel = path.relative(siteRoot, full);
      if (e.isDirectory()) {
        if (SKIP_DIRS.includes(e.name)) continue;
        walk(full);
      } else if (e.isFile() && e.name.endsWith('.html')) {
        results.push({ abs: full, rel });
      }
    }
  }
  walk(siteRoot);
  return results;
}

function readHtml(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function classifyPage(rel) {
  if (rel.startsWith('tools/') && rel.endsWith('-review.html')) return 'review';
  if (rel.startsWith('compare/')) return 'comparison';
  if (rel.startsWith('best/')) return 'best-pick';
  if (rel.startsWith('pricing/')) return 'pricing';
  if (rel.startsWith('alternatives/')) return 'alternatives';
  if (rel.startsWith('categories/')) return 'category';
  if (rel === 'index.html') return 'homepage';
  return 'other';
}

function extractTitle(html) {
  const m = html.match(/<title>([^<]+)<\/title>/i);
  return m ? m[1] : '';
}

function extractMetaDesc(html) {
  const m = html.match(/<meta\s+name="description"\s+content="([^"]*)"[^>]*>/i);
  return m ? m[1] : '';
}

function extractJsonLd(html) {
  const blocks = [];
  const re = /<script\s+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    try {
      blocks.push(JSON.parse(m[1]));
    } catch (e) {
      blocks.push({ _parseError: e.message, _raw: m[1].substring(0, 200) });
    }
  }
  return blocks;
}

function countWords(html) {
  const text = html.replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return text.split(' ').filter(w => w.length > 0).length;
}

function extractGoLinks(html) {
  const links = [];
  const re = /href="(\/go\/[^"]+)"/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    links.push(m[1]);
  }
  return links;
}

function extractInternalLinks(html) {
  const links = [];
  const re = /href="([^"]*?)"/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const href = m[1];
    if (href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('#') || href.startsWith('/go/') || href.startsWith('tel:')) continue;
    links.push(href);
  }
  return links;
}

module.exports = {
  getAllHtmlFiles,
  readHtml,
  classifyPage,
  extractTitle,
  extractMetaDesc,
  extractJsonLd,
  countWords,
  extractGoLinks,
  extractInternalLinks,
  SKIP_DIRS
};
```

- [ ] **Step 2: Verify module loads**

Run: `node -e "const s = require('./scripts/agents/lib/html-scanner.js'); console.log(Object.keys(s).join(', '))"`
Expected: `getAllHtmlFiles, readHtml, classifyPage, extractTitle, extractMetaDesc, extractJsonLd, countWords, extractGoLinks, extractInternalLinks, SKIP_DIRS`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/lib/html-scanner.js
git commit -m "feat(atlas): add shared HTML scanner utility for agent scripts"
```

---

## Chunk 2: Audit Agents 01-03

### Task 2: Create 01-sitehealth.js

**Files:**
- Create: `scripts/agents/01-sitehealth.js`

**Checks (from ops/agents/01-sitehealth.md):**
- GA4 snippet present in every file
- Canonical tags exist and match sitemap format
- Title tag exists, 30-60 chars
- Meta description exists, 120-160 chars
- OG tags present
- JSON-LD valid with @type
- Newsletter forms have correct action/inputs
- No duplicate titles/descriptions across pages

**Scoring:** Start at 100. Deduct: missing GA4 -10/page, invalid canonical -5, missing title/meta -3, invalid schema -2, broken link -2, missing newsletter attrs -1.

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/01-sitehealth.js
const path = require('path');
const fs = require('fs');
const { getAllHtmlFiles, readHtml, extractTitle, extractMetaDesc, extractJsonLd, classifyPage } = require('./lib/html-scanner');

const GA4_ID = 'G-VRBZ6Z6885';

module.exports = async function audit(siteRoot) {
  const files = getAllHtmlFiles(siteRoot);
  const issues = [];
  let score = 100;

  let pagesAudited = 0;
  let issuesFound = 0;
  let ga4Present = 0;
  let canonicalsValid = 0;
  let schemasValid = 0;
  let newsletterFormsValid = 0;
  let brokenLinks = 0;

  const titles = new Map();
  const descriptions = new Map();

  for (const { abs, rel } of files) {
    pagesAudited++;
    const html = readHtml(abs);

    // GA4 check
    if (html.includes(GA4_ID)) {
      ga4Present++;
    } else {
      issues.push({ check: 'ga4_missing', severity: 'high', detail: rel + ': missing GA4 snippet ' + GA4_ID });
      score -= 10;
      issuesFound++;
    }

    // Canonical check
    const canonicalMatch = html.match(/<link\s+rel="canonical"\s+href="([^"]*)"[^>]*>/i);
    if (canonicalMatch) {
      const url = canonicalMatch[1];
      if (!url.endsWith('.html') && url.startsWith('https://')) {
        canonicalsValid++;
      } else {
        issues.push({ check: 'canonical_invalid', severity: 'med', detail: rel + ': canonical "' + url + '" has .html extension or bad format' });
        score -= 5;
        issuesFound++;
      }
    } else {
      issues.push({ check: 'canonical_missing', severity: 'med', detail: rel + ': missing canonical tag' });
      score -= 5;
      issuesFound++;
    }

    // Title check
    const title = extractTitle(html);
    if (!title) {
      issues.push({ check: 'title_missing', severity: 'high', detail: rel + ': missing <title> tag' });
      score -= 3;
      issuesFound++;
    } else {
      if (title.length > 60) {
        issues.push({ check: 'title_length', severity: 'med', detail: rel + ': title is ' + title.length + ' chars (max 60): "' + title + '"' });
        score -= 3;
        issuesFound++;
      }
      if (titles.has(title)) {
        issues.push({ check: 'title_duplicate', severity: 'med', detail: rel + ': duplicate title with ' + titles.get(title) });
        issuesFound++;
      } else {
        titles.set(title, rel);
      }
    }

    // Meta description check
    const desc = extractMetaDesc(html);
    if (!desc) {
      issues.push({ check: 'meta_desc_missing', severity: 'med', detail: rel + ': missing meta description' });
      score -= 3;
      issuesFound++;
    } else {
      if (desc.length > 160 || desc.length < 120) {
        issues.push({ check: 'meta_desc_length', severity: 'low', detail: rel + ': meta description is ' + desc.length + ' chars (target 120-160)' });
        score -= 1;
        issuesFound++;
      }
      if (descriptions.has(desc)) {
        issues.push({ check: 'meta_desc_duplicate', severity: 'med', detail: rel + ': duplicate description with ' + descriptions.get(desc) });
        issuesFound++;
      } else {
        descriptions.set(desc, rel);
      }
    }

    // OG tags check
    const hasOgTitle = /<meta\s+property="og:title"/i.test(html);
    const hasOgDesc = /<meta\s+property="og:description"/i.test(html);
    if (!hasOgTitle || !hasOgDesc) {
      issues.push({ check: 'og_tags_missing', severity: 'low', detail: rel + ': missing og:title or og:description' });
      score -= 1;
      issuesFound++;
    }

    // JSON-LD check
    const schemas = extractJsonLd(html);
    let pageSchemaValid = true;
    for (const s of schemas) {
      if (s._parseError) {
        issues.push({ check: 'schema_invalid', severity: 'med', detail: rel + ': invalid JSON-LD: ' + s._parseError });
        score -= 2;
        issuesFound++;
        pageSchemaValid = false;
      } else if (!s['@type']) {
        issues.push({ check: 'schema_no_type', severity: 'med', detail: rel + ': JSON-LD block missing @type' });
        score -= 2;
        issuesFound++;
        pageSchemaValid = false;
      }
    }
    if (pageSchemaValid) schemasValid += schemas.length;

    // Newsletter form check
    const formMatches = html.match(/<form[^>]*class="[^"]*newsletter[^"]*"[^>]*>/gi) || [];
    for (const form of formMatches) {
      const formEnd = html.indexOf('</form>', html.indexOf(form));
      if (formEnd === -1) continue;
      const formSection = html.substring(html.indexOf(form), formEnd + 7);
      if (formSection.includes('buttondown.com/api/emails/embed-subscribe/salesaiguide')) {
        newsletterFormsValid++;
      } else {
        issues.push({ check: 'newsletter_form', severity: 'low', detail: rel + ': newsletter form has incorrect action' });
        score -= 1;
        issuesFound++;
      }
    }
  }

  score = Math.max(0, Math.min(100, score));

  return {
    agent: 'sitehealth',
    status: score >= 80 ? 'healthy' : score >= 50 ? 'warning' : 'critical',
    score,
    metrics: {
      pagesAudited,
      issuesFound,
      issuesFixed: 0,
      ga4Coverage: ga4Present + '/' + pagesAudited,
      canonicalsValid,
      schemasValid,
      newsletterFormsValid,
      brokenLinks
    },
    issues: issues.slice(0, 50),
    lastAction: 'Audited ' + pagesAudited + ' pages — found ' + issuesFound + ' issues. GA4: ' + ga4Present + '/' + pagesAudited + ', schemas: ' + schemasValid + ' valid.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/01-sitehealth.js'); a('.').then(r => console.log(r.agent, r.status, r.score, r.metrics.pagesAudited + ' pages'))"`
Expected: `sitehealth healthy|warning|critical <score> <N> pages`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/01-sitehealth.js
git commit -m "feat(atlas): add 01-sitehealth audit agent"
```

### Task 3: Create 02-revenuefunnel.js

**Files:**
- Create: `scripts/agents/02-revenuefunnel.js`

**Checks (from ops/agents/02-revenuefunnel.md):**
- Count /go/ links per page
- Detect direct vendor links that bypass /go/ (leak detection)
- CTA text accuracy (demo-only tools must say "Request Demo")
- Per-page affiliate link density

**Scoring:** Start at 100/page, -5 per leak, -10 no hero CTA, -5 low density. Average across pages.

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/02-revenuefunnel.js
const path = require('path');
const { getAllHtmlFiles, readHtml, extractGoLinks, countWords, classifyPage } = require('./lib/html-scanner');

// Domain to /go/ slug mapping
const VENDOR_DOMAINS = {
  'instantly.ai': 'instantly', 'www.instantly.ai': 'instantly',
  'clay.com': 'clay', 'www.clay.com': 'clay',
  'apollo.io': 'apollo', 'www.apollo.io': 'apollo',
  'gong.io': 'gong', 'www.gong.io': 'gong',
  'lemlist.com': 'lemlist', 'www.lemlist.com': 'lemlist',
  'smartlead.ai': 'smartlead', 'www.smartlead.ai': 'smartlead',
  'woodpecker.co': 'woodpecker', 'www.woodpecker.co': 'woodpecker',
  'reply.io': 'reply-io', 'www.reply.io': 'reply-io',
  'salesloft.com': 'salesloft', 'www.salesloft.com': 'salesloft',
  'outreach.io': 'outreach', 'www.outreach.io': 'outreach',
  'hubspot.com': 'hubspot', 'www.hubspot.com': 'hubspot',
  'zoominfo.com': 'zoominfo', 'www.zoominfo.com': 'zoominfo',
  'hunter.io': 'hunter', 'www.hunter.io': 'hunter',
  'lusha.com': 'lusha', 'www.lusha.com': 'lusha',
  'clearbit.com': 'clearbit', 'www.clearbit.com': 'clearbit',
  'vidyard.com': 'vidyard', 'www.vidyard.com': 'vidyard',
  'chorus.ai': 'chorus', 'www.chorus.ai': 'chorus',
  'clari.com': 'clari', 'www.clari.com': 'clari',
  'fireflies.ai': 'fireflies', 'www.fireflies.ai': 'fireflies',
  'freshworks.com': 'freshsales', 'www.freshworks.com': 'freshsales',
  'close.com': 'close', 'www.close.com': 'close',
  'pipedrive.com': 'pipedrive', 'www.pipedrive.com': 'pipedrive',
  'aircall.io': 'aircall', 'www.aircall.io': 'aircall',
  'dialpad.com': 'dialpad', 'www.dialpad.com': 'dialpad',
  'justcall.io': 'justcall', 'www.justcall.io': 'justcall',
  'kixie.com': 'kixie', 'www.kixie.com': 'kixie',
  'orum.com': 'orum', 'www.orum.com': 'orum',
  'lavender.ai': 'lavender', 'www.lavender.ai': 'lavender',
  'mailshake.com': 'mailshake', 'www.mailshake.com': 'mailshake',
  'seamless.ai': 'seamless-ai', 'www.seamless.ai': 'seamless-ai',
  'savvycal.com': 'savvycal', 'www.savvycal.com': 'savvycal',
  'calendly.com': 'calendly', 'www.calendly.com': 'calendly',
  'chilipiper.com': 'chili-piper', 'www.chilipiper.com': 'chili-piper'
};

const CTA_CLASSES = ['btn-review-primary', 'btn-review-secondary', 'specs-cta',
  'comp-btn-primary', 'comp-btn-secondary'];
const CTA_CONTAINERS = ['review-hero__cta', 'inline-cta', 'pricing-card',
  'pricing-card--featured', 'verdict-box', 'comp-hero__cta', 'sticky-cta__actions'];
const CTA_TEXT_STARTS = ['try', 'start', 'request', 'get started', 'sign up'];

function detectLeaks(html) {
  const leaks = [];
  const re = /href="(https?:\/\/[^"]+)"[^>]*>([^<]*)</gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const url = m[1];
    const linkText = m[2].trim().toLowerCase();
    try {
      const domain = new URL(url).hostname;
      const slug = VENDOR_DOMAINS[domain];
      if (!slug) continue;

      const surroundingStart = Math.max(0, m.index - 500);
      const surrounding = html.substring(surroundingStart, m.index + m[0].length + 200);
      if (/class="[^"]*sources-checked[^"]*"/i.test(surrounding) ||
          /class="[^"]*review-sources[^"]*"/i.test(surrounding)) continue;
      if (['pricing page', 'pricing', 'official site', 'source', 'blog'].includes(linkText)) continue;

      const isCta = CTA_CLASSES.some(function(c) { return surrounding.includes(c); }) ||
        CTA_CONTAINERS.some(function(c) { return surrounding.includes(c); }) ||
        CTA_TEXT_STARTS.some(function(t) { return linkText.startsWith(t); }) ||
        /^\$\d/.test(linkText);

      if (isCta) {
        leaks.push({ url: url, slug: slug, linkText: m[2].trim() });
      }
    } catch (e) { /* invalid URL, skip */ }
  }
  return leaks;
}

module.exports = async function audit(siteRoot) {
  const files = getAllHtmlFiles(siteRoot);
  const issues = [];
  let totalGoLinks = 0;
  let totalDirectLeaks = 0;
  let pagesAudited = 0;
  let totalScore = 0;
  let scoredPages = 0;

  for (const { abs, rel } of files) {
    const html = readHtml(abs);
    const goLinks = extractGoLinks(html);
    totalGoLinks += goLinks.length;
    if (goLinks.length === 0 && classifyPage(rel) === 'other') continue;

    pagesAudited++;
    let pageScore = 100;

    const leaks = detectLeaks(html);
    totalDirectLeaks += leaks.length;
    for (const leak of leaks) {
      pageScore -= 5;
      issues.push({
        check: 'direct_leak',
        severity: 'critical',
        detail: rel + ': direct link to ' + leak.url + ' should be /go/' + leak.slug + ' (text: "' + leak.linkText + '")'
      });
    }

    const words = countWords(html);
    const density = words > 0 ? (goLinks.length / words) * 1000 : 0;
    if (density < 1.0 && goLinks.length > 0) {
      pageScore -= 5;
    }

    pageScore = Math.max(0, pageScore);
    totalScore += pageScore;
    scoredPages++;
  }

  const avgScore = scoredPages > 0 ? Math.round(totalScore / scoredPages) : 100;

  return {
    agent: 'revenuefunnel',
    status: totalDirectLeaks > 0 ? 'critical' : 'healthy',
    score: avgScore,
    metrics: {
      pagesAudited: pagesAudited,
      totalGoLinks: totalGoLinks,
      totalDirectLeaks: totalDirectLeaks,
      leaksFixed: 0,
      pagesWithNoAffiliateCta: 0,
      avgLinkDensity: scoredPages > 0 ? +(totalGoLinks / scoredPages).toFixed(1) : 0,
      avgPageScore: avgScore
    },
    issues: issues.slice(0, 50),
    lastAction: 'Scanned ' + pagesAudited + ' pages — ' + totalGoLinks + ' /go/ links, ' + totalDirectLeaks + ' direct leaks detected.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/02-revenuefunnel.js'); a('.').then(r => console.log(r.agent, r.score, r.metrics.totalGoLinks + ' go links'))"`
Expected: `revenuefunnel <score> <N> go links`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/02-revenuefunnel.js
git commit -m "feat(atlas): add 02-revenuefunnel audit agent"
```

### Task 4: Create 03-linkhealth.js

**Files:**
- Create: `scripts/agents/03-linkhealth.js`

**Checks (from ops/agents/03-linkhealth.md):**
- Count internal links per page
- Find orphaned pages (< 3 inbound)
- Cross-link gap detection (comparison pages link to both tools' reviews)
- Sitemap consistency

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/03-linkhealth.js
const fs = require('fs');
const path = require('path');
const { getAllHtmlFiles, readHtml, extractInternalLinks, classifyPage } = require('./lib/html-scanner');

function normalizeHref(href) {
  let h = href.replace(/^\//, '').replace(/\/$/, '/index.html');
  if (!h.endsWith('.html')) {
    if (h.endsWith('/')) h += 'index.html';
    else h += '.html';
  }
  return h;
}

module.exports = async function audit(siteRoot) {
  const files = getAllHtmlFiles(siteRoot);
  const issues = [];
  const fileSet = new Set(files.map(function(f) { return f.rel; }));

  const inbound = {};
  for (const f of files) inbound[f.rel] = 0;

  let totalInternalLinks = 0;

  for (const { abs, rel } of files) {
    const html = readHtml(abs);
    const links = extractInternalLinks(html);
    totalInternalLinks += links.length;

    for (const href of links) {
      const target = normalizeHref(href);
      if (inbound[target] !== undefined) {
        inbound[target]++;
      }
    }
  }

  const orphans = [];
  for (const page of Object.keys(inbound)) {
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

  let missingCrossLinks = 0;
  for (const { abs, rel } of files) {
    var type = classifyPage(rel);
    if (type !== 'comparison') continue;

    var html = readHtml(abs);
    var basename = path.basename(rel, '.html');
    var parts = basename.split('-vs-');
    if (parts.length !== 2) continue;

    for (const slug of parts) {
      var reviewPath = 'tools/' + slug + '-review.html';
      if (fileSet.has(reviewPath) && !html.includes('/' + slug + '-review')) {
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

  let sitemapConsistent = true;
  var sitemapPath = path.join(siteRoot, 'sitemap-core.xml');
  if (fs.existsSync(sitemapPath)) {
    var sitemap = fs.readFileSync(sitemapPath, 'utf8');
    var urlRe = /<loc>([^<]+)<\/loc>/g;
    var m;
    while ((m = urlRe.exec(sitemap)) !== null) {
      var url = m[1].replace('https://salesaiguide.com/', '').replace(/\/$/, '');
      var expected = url === '' ? 'index.html' : url + '.html';
      if (!fileSet.has(expected) && !fileSet.has(url + '/index.html') && !fileSet.has(url)) {
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
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/03-linkhealth.js'); a('.').then(r => console.log(r.agent, r.score, r.metrics.orphanedPages + ' orphans'))"`
Expected: `linkhealth <score> <N> orphans`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/03-linkhealth.js
git commit -m "feat(atlas): add 03-linkhealth audit agent"
```

---

## Chunk 3: Audit Agents 04-06

### Task 5: Create 04-priceverify.js

**Files:**
- Create: `scripts/agents/04-priceverify.js`

**Logic:** Extract canonical prices from `tools/*-review.html`, then scan all other pages for price mismatches per tool. Score: 100 - (inconsistent tools * 15).

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/04-priceverify.js
const path = require('path');
const fs = require('fs');
const { getAllHtmlFiles, readHtml, classifyPage } = require('./lib/html-scanner');

function buildPriceTruth(siteRoot) {
  var truthDir = path.join(siteRoot, 'tools');
  var truth = {};
  if (!fs.existsSync(truthDir)) return truth;
  var reviewFiles = fs.readdirSync(truthDir).filter(function(f) { return f.endsWith('-review.html'); });
  for (var i = 0; i < reviewFiles.length; i++) {
    var f = reviewFiles[i];
    var slug = f.replace('-review.html', '');
    var html = readHtml(path.join(truthDir, f));
    var priceMatches = html.match(/\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/gi);
    if (priceMatches && priceMatches.length > 0) {
      truth[slug] = priceMatches[0];
    }
  }
  return truth;
}

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);
  var truth = buildPriceTruth(siteRoot);
  var issues = [];
  var toolNames = Object.keys(truth);
  var consistentTools = 0;
  var inconsistentTools = 0;

  for (var t = 0; t < toolNames.length; t++) {
    var slug = toolNames[t];
    var canonical = truth[slug];
    var mismatches = [];

    for (var i = 0; i < files.length; i++) {
      var rel = files[i].rel;
      var abs = files[i].abs;
      if (rel.startsWith('tools/') && rel.endsWith('-review.html')) continue;
      if (!rel.toLowerCase().includes(slug.replace(/-/g, ''))) continue;

      var html = readHtml(abs);
      var prices = html.match(/\$\d[\d,]*(?:\.\d{1,2})?(?:\s*\/\s*(?:mo|month|user|seat))?/gi) || [];
      for (var j = 0; j < prices.length; j++) {
        if (prices[j] !== canonical && !mismatches.some(function(m) { return m.page === rel; })) {
          mismatches.push({ page: rel, displayedPrice: prices[j] });
        }
      }
    }

    if (mismatches.length > 0) {
      inconsistentTools++;
      issues.push({
        check: 'price_mismatch',
        severity: 'high',
        detail: slug + ': review says ' + canonical + ', but ' + mismatches.length + ' pages differ'
      });
    } else {
      consistentTools++;
    }
  }

  var score = Math.max(0, Math.min(100, 100 - inconsistentTools * 15));

  return {
    agent: 'priceverify',
    status: inconsistentTools > 0 ? 'warning' : 'healthy',
    score: score,
    metrics: {
      toolsAudited: toolNames.length,
      consistentTools: consistentTools,
      inconsistentTools: inconsistentTools,
      staleTools: 0,
      autoFixed: 0
    },
    issues: issues.slice(0, 50),
    lastAction: 'Verified prices for ' + toolNames.length + ' tools. ' + consistentTools + ' consistent, ' + inconsistentTools + ' with mismatches.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/04-priceverify.js'); a('.').then(r => console.log(r.agent, r.score, r.metrics.toolsAudited + ' tools'))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/04-priceverify.js
git commit -m "feat(atlas): add 04-priceverify audit agent"
```

### Task 6: Create 05-contentguard.js

**Files:**
- Create: `scripts/agents/05-contentguard.js`

**Checks:** Name leaks (critical), banned phrases, demo CTA enforcement, schema correctness by page type, thin content.

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/05-contentguard.js
const path = require('path');
const { getAllHtmlFiles, readHtml, extractJsonLd, classifyPage, countWords } = require('./lib/html-scanner');

var DEMO_ONLY_TOOLS = ['gong', 'chorus', 'outreach', 'salesloft', 'zoominfo', 'clearbit', 'clari', 'orum'];

var NAME_LEAK_PATTERNS = [
  { re: /Matt\s/gi, label: 'Matt' },
  { re: /Matthew/gi, label: 'Matthew' },
  { re: /Schneider/gi, label: 'Schneider' },
  { re: /Toptal/gi, label: 'Toptal' }
];

var BANNED_PHRASES = [
  'stands out', "it's worth noting", "it\u2019s worth noting", 'comprehensive solution',
  'robust platform', 'seamlessly integrates', 'game-changer', 'game changer',
  'landscape', 'navigate', 'leverage', 'streamline'
];

var REQUIRED_SCHEMAS = {
  review: ['Review', 'BreadcrumbList', 'FAQPage'],
  comparison: ['Article', 'BreadcrumbList', 'FAQPage'],
  'best-pick': ['Article', 'BreadcrumbList', 'ItemList', 'FAQPage'],
  pricing: ['Article', 'BreadcrumbList', 'FAQPage'],
  category: ['ItemList', 'BreadcrumbList', 'FAQPage'],
  alternatives: ['Article', 'BreadcrumbList', 'ItemList', 'FAQPage']
};

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);
  var issues = [];
  var nameLeaks = 0;
  var bannedPhraseCount = 0;
  var demoCtaErrors = 0;
  var schemaErrors = 0;
  var thinContentPages = 0;

  for (var i = 0; i < files.length; i++) {
    var abs = files[i].abs;
    var rel = files[i].rel;
    var html = readHtml(abs);

    var visibleText = html.replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ');

    // Name leak check (CRITICAL)
    for (var j = 0; j < NAME_LEAK_PATTERNS.length; j++) {
      var p = NAME_LEAK_PATTERNS[j];
      p.re.lastIndex = 0;
      if (p.re.test(visibleText)) {
        nameLeaks++;
        issues.push({ check: 'name_leak', severity: 'critical', detail: rel + ': contains "' + p.label + '"' });
      }
    }

    // Banned phrases
    for (var k = 0; k < BANNED_PHRASES.length; k++) {
      var phrase = BANNED_PHRASES[k];
      var escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      var re = new RegExp('\\b' + escaped + '\\b', 'gi');
      var matches = visibleText.match(re);
      if (matches) {
        bannedPhraseCount += matches.length;
        issues.push({ check: 'banned_phrase', severity: 'low', detail: rel + ': contains "' + phrase + '" (' + matches.length + 'x)' });
      }
    }

    // Demo CTA check
    var lowerRel = rel.toLowerCase();
    var isDemoPage = DEMO_ONLY_TOOLS.some(function(t) { return lowerRel.includes(t); });
    if (isDemoPage) {
      var trialRe = /Start Free Trial|Try Free|Try\s+\w+\s+Free/gi;
      var trialMatches = html.match(trialRe);
      if (trialMatches) {
        demoCtaErrors += trialMatches.length;
        issues.push({ check: 'demo_cta', severity: 'high', detail: rel + ': has "' + trialMatches[0] + '" for demo-only tool' });
      }
    }

    // Schema check
    var pageType = classifyPage(rel);
    var required = REQUIRED_SCHEMAS[pageType];
    if (required) {
      var schemas = extractJsonLd(html);
      var types = schemas.map(function(s) { return s['@type']; }).filter(Boolean);
      for (var r = 0; r < required.length; r++) {
        if (types.indexOf(required[r]) === -1) {
          schemaErrors++;
          issues.push({ check: 'schema_missing', severity: 'med', detail: rel + ': missing ' + required[r] + ' schema (' + pageType + ' page)' });
        }
      }
    }

    // Thin content
    var words = countWords(html);
    if (words < 800 && pageType !== 'homepage' && pageType !== 'other') {
      thinContentPages++;
      issues.push({ check: 'thin_content', severity: 'low', detail: rel + ': ' + words + ' words (minimum 800)' });
    }
  }

  var score = 100;
  score -= nameLeaks * 25;
  score -= Math.min(bannedPhraseCount, 10);
  score -= demoCtaErrors * 5;
  score -= schemaErrors * 2;
  score -= thinContentPages;
  score = Math.max(0, Math.min(100, score));

  return {
    agent: 'contentguard',
    status: nameLeaks > 0 ? 'critical' : score >= 80 ? 'healthy' : 'warning',
    score: score,
    metrics: {
      pagesScanned: files.length,
      nameLeaks: nameLeaks,
      bannedPhrases: bannedPhraseCount,
      bannedPhrasesFixed: 0,
      ratingMismatches: 0,
      demoCtaErrors: demoCtaErrors,
      demoCtaFixed: 0,
      schemaErrors: schemaErrors,
      thinContentPages: thinContentPages
    },
    issues: issues.slice(0, 50),
    lastAction: 'Scanned ' + files.length + ' pages. ' + nameLeaks + ' name leaks, ' + bannedPhraseCount + ' banned phrases, ' + demoCtaErrors + ' demo CTA errors.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/05-contentguard.js'); a('.').then(r => console.log(r.agent, r.score, 'leaks:', r.metrics.nameLeaks))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/05-contentguard.js
git commit -m "feat(atlas): add 05-contentguard audit agent"
```

### Task 7: Create 06-seopower.js

**Files:**
- Create: `scripts/agents/06-seopower.js`

**Checks:** Title (15pts), meta desc (10), H1 (10), H2 structure (10), content depth (15), schema (10), freshness (10), internal links (10), images (5), canonical (5).

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/06-seopower.js
const { getAllHtmlFiles, readHtml, extractTitle, extractMetaDesc, extractJsonLd, extractInternalLinks, classifyPage, countWords } = require('./lib/html-scanner');

var DEPTH_TARGETS = {
  review: 2500, comparison: 2000, 'best-pick': 1500, pricing: 1000,
  alternatives: 1200, category: 800
};

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);
  var issues = [];
  var totalScore = 0;
  var pagesAbove80 = 0;
  var pagesBelow50 = 0;
  var missingMetaDesc = 0;
  var staleFreshness = 0;
  var scoredPages = 0;

  for (var i = 0; i < files.length; i++) {
    var abs = files[i].abs;
    var rel = files[i].rel;
    var html = readHtml(abs);
    var type = classifyPage(rel);
    if (type === 'other' && rel !== 'index.html') continue;

    var pageScore = 0;
    scoredPages++;

    // Title (15 pts)
    var title = extractTitle(html);
    if (title) {
      var titleScore = 15;
      if (title.length > 60 || title.length < 30) titleScore -= 5;
      if (!/2026/.test(title) && (type === 'comparison' || type === 'best-pick')) {
        titleScore -= 5;
        staleFreshness++;
      }
      pageScore += Math.max(0, titleScore);
    } else {
      issues.push({ check: 'title_missing', severity: 'high', detail: rel + ': no title tag' });
    }

    // Meta description (10 pts)
    var desc = extractMetaDesc(html);
    if (desc) {
      var descScore = 10;
      if (desc.length > 160 || desc.length < 120) descScore -= 5;
      pageScore += Math.max(0, descScore);
    } else {
      missingMetaDesc++;
      issues.push({ check: 'meta_desc_missing', severity: 'med', detail: rel + ': no meta description' });
    }

    // H1 (10 pts)
    var h1s = html.match(/<h1[^>]*>/gi) || [];
    pageScore += h1s.length === 1 ? 10 : 0;

    // H2 structure (10 pts)
    var h2s = html.match(/<h2[^>]*>/gi) || [];
    if (type === 'review' || type === 'comparison') {
      pageScore += h2s.length >= 4 ? 10 : Math.round(h2s.length * 2.5);
    } else {
      pageScore += h2s.length >= 2 ? 10 : 5;
    }

    // Content depth (15 pts)
    var words = countWords(html);
    var target = DEPTH_TARGETS[type] || 500;
    var depthRatio = Math.min(words / target, 1);
    pageScore += Math.round(depthRatio * 15);

    // Schema (10 pts)
    var schemas = extractJsonLd(html);
    var validSchemas = schemas.filter(function(s) { return s['@type'] && !s._parseError; });
    pageScore += validSchemas.length > 0 ? 10 : 0;

    // Freshness (10 pts)
    if (/2026/.test(html) || /March 2026|February 2026|January 2026/i.test(html)) {
      pageScore += 10;
    } else {
      if (type === 'review' || type === 'comparison' || type === 'best-pick') {
        staleFreshness++;
      }
    }

    // Internal links (10 pts)
    var internalLinks = extractInternalLinks(html);
    pageScore += internalLinks.length >= 5 ? 10 : Math.round(internalLinks.length * 2);

    // Images (5 pts)
    var imgs = html.match(/<img[^>]+>/gi) || [];
    var withAlt = imgs.filter(function(im) { return /alt="[^"]+"/i.test(im); });
    pageScore += imgs.length === 0 ? 5 : Math.round((withAlt.length / imgs.length) * 5);

    // Canonical (5 pts)
    var hasCanonical = /<link\s+rel="canonical"/i.test(html);
    pageScore += hasCanonical ? 5 : 0;

    totalScore += pageScore;
    if (pageScore >= 80) pagesAbove80++;
    if (pageScore < 50) pagesBelow50++;
  }

  var avgScore = scoredPages > 0 ? +(totalScore / scoredPages).toFixed(1) : 0;
  var overallScore = Math.round(avgScore);

  return {
    agent: 'seopower',
    status: overallScore >= 80 ? 'healthy' : overallScore >= 50 ? 'warning' : 'critical',
    score: overallScore,
    metrics: {
      pagesAudited: scoredPages,
      avgSeoScore: avgScore,
      pagesAbove80: pagesAbove80,
      pagesBelow50: pagesBelow50,
      missingMetaDesc: missingMetaDesc,
      staleFreshness: staleFreshness,
      autoFixed: 0
    },
    issues: issues.slice(0, 50),
    lastAction: 'Scored ' + scoredPages + ' pages. Average SEO score: ' + avgScore + '. ' + pagesAbove80 + ' above 80, ' + staleFreshness + ' with stale freshness.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/06-seopower.js'); a('.').then(r => console.log(r.agent, r.score, 'avg:', r.metrics.avgSeoScore))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/06-seopower.js
git commit -m "feat(atlas): add 06-seopower audit agent"
```

---

## Chunk 4: Audit Agents 07-09

### Task 8: Create 07-trafficintel.js

**Files:**
- Create: `scripts/agents/07-trafficintel.js`

**Logic:** Score each page by commercial intent (page type), competition proxy (title length), monetization density (/go/ links), content quality. Returns ranked list. Score is display-only (excluded from weighted average).

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/07-trafficintel.js
const { getAllHtmlFiles, readHtml, extractGoLinks, extractInternalLinks, extractJsonLd, countWords, classifyPage, extractTitle } = require('./lib/html-scanner');

function commercialIntent(type) {
  if (type === 'pricing') return 10;
  if (type === 'best-pick') return 9;
  if (type === 'comparison') return 8;
  if (type === 'alternatives') return 7;
  if (type === 'review') return 7;
  if (type === 'category') return 6;
  return 3;
}

function competitionProxy(title) {
  var words = title.split(/\s+/).length;
  if (words >= 5) return 0.9;
  if (words >= 3) return 0.6;
  return 0.3;
}

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);
  var rankings = [];

  for (var i = 0; i < files.length; i++) {
    var abs = files[i].abs;
    var rel = files[i].rel;
    var type = classifyPage(rel);
    if (type === 'other' && rel !== 'index.html') continue;

    var html = readHtml(abs);
    var title = extractTitle(html);
    var goLinks = extractGoLinks(html);
    var internalLinks = extractInternalLinks(html);
    var schemas = extractJsonLd(html).filter(function(s) { return !s._parseError; });
    var words = countWords(html);

    var ci = commercialIntent(type);
    var cp = competitionProxy(title);
    var monetization = goLinks.length * 2;
    var quality = Math.min(
      ((words / 2000) * 30) + (schemas.length * 10) + (internalLinks.length * 2),
      100
    );
    var revenueScore = +((ci * cp * (monetization + quality) / 20).toFixed(1));

    rankings.push({
      url: '/' + rel.replace('.html', '').replace('index', ''),
      revenueScore: Math.min(revenueScore, 100),
      type: type
    });
  }

  rankings.sort(function(a, b) { return b.revenueScore - a.revenueScore; });

  var avgScore = rankings.length > 0
    ? +(rankings.reduce(function(s, r) { return s + r.revenueScore; }, 0) / rankings.length).toFixed(1)
    : 0;

  var highPotential = rankings.filter(function(r) { return r.revenueScore >= 60; }).length;
  var underperforming = rankings.filter(function(r) { return r.revenueScore < 20; }).length;

  return {
    agent: 'trafficintel',
    status: 'healthy',
    score: Math.round(avgScore),
    metrics: {
      pagesAnalyzed: rankings.length,
      highPotentialPages: highPotential,
      underperformingPages: underperforming,
      avgRevenueScore: avgScore
    },
    issues: [],
    lastAction: 'Analyzed ' + rankings.length + ' pages. ' + highPotential + ' high-potential, ' + underperforming + ' underperforming. Avg revenue score: ' + avgScore + '.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/07-trafficintel.js'); a('.').then(r => console.log(r.agent, r.score, r.metrics.pagesAnalyzed + ' pages'))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/07-trafficintel.js
git commit -m "feat(atlas): add 07-trafficintel audit agent"
```

### Task 9: Create 08-contentengine.js

**Files:**
- Create: `scripts/agents/08-contentengine.js`

**Logic:** Enumerate all tools, compute comparison pairs, find gaps vs existing pages. Find missing best-picks and alternatives.

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/08-contentengine.js
const fs = require('fs');
const path = require('path');
const { getAllHtmlFiles, classifyPage } = require('./lib/html-scanner');

module.exports = async function audit(siteRoot) {
  var files = getAllHtmlFiles(siteRoot);

  var toolSlugs = [];
  var existingComparisons = {};
  var existingBestPicks = {};
  var existingAlternatives = {};

  for (var i = 0; i < files.length; i++) {
    var rel = files[i].rel;
    var type = classifyPage(rel);
    var basename = path.basename(rel, '.html');

    if (type === 'review') {
      toolSlugs.push(basename.replace('-review', ''));
    } else if (type === 'comparison') {
      existingComparisons[basename] = true;
    } else if (type === 'best-pick') {
      existingBestPicks[basename] = true;
    } else if (type === 'alternatives') {
      existingAlternatives[basename] = true;
    }
  }

  // Comparison gaps
  var comparisonGaps = [];
  for (var a = 0; a < toolSlugs.length; a++) {
    for (var b = a + 1; b < toolSlugs.length; b++) {
      var pair1 = toolSlugs[a] + '-vs-' + toolSlugs[b];
      var pair2 = toolSlugs[b] + '-vs-' + toolSlugs[a];
      if (!existingComparisons[pair1] && !existingComparisons[pair2]) {
        comparisonGaps.push({ toolA: toolSlugs[a], toolB: toolSlugs[b] });
      }
    }
  }

  // Alternatives gaps
  var alternativesGaps = [];
  for (var c = 0; c < toolSlugs.length; c++) {
    var altName = toolSlugs[c] + '-alternatives';
    if (!existingAlternatives[altName]) {
      alternativesGaps.push(toolSlugs[c]);
    }
  }

  var bestPicksGaps = 7 - Object.keys(existingBestPicks).length;

  return {
    agent: 'contentengine',
    status: 'healthy',
    score: null,
    metrics: {
      comparisonGaps: comparisonGaps.length,
      bestPicksGaps: Math.max(0, bestPicksGaps),
      alternativesGaps: alternativesGaps.length,
      briefsGenerated: 0,
      topOpportunity: comparisonGaps.length > 0
        ? comparisonGaps[0].toolA + ' vs ' + comparisonGaps[0].toolB
        : 'None'
    },
    issues: [],
    lastAction: 'Found ' + comparisonGaps.length + ' comparison gaps, ' + alternativesGaps.length + ' missing alternatives pages, ' + Math.max(0, bestPicksGaps) + ' best-picks opportunities.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/08-contentengine.js'); a('.').then(r => console.log(r.agent, r.score, r.metrics.comparisonGaps + ' gaps'))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/08-contentengine.js
git commit -m "feat(atlas): add 08-contentengine audit agent"
```

### Task 10: Create 09-revenueops.js

**Files:**
- Create: `scripts/agents/09-revenueops.js`

**Logic:** Aggregate all other agent results (passed as second argument), build affiliate inventory, calculate concentration risk, generate prioritized action queue.

- [ ] **Step 1: Create the agent script**

```js
// scripts/agents/09-revenueops.js
const { getAllHtmlFiles, readHtml, extractGoLinks } = require('./lib/html-scanner');

module.exports = async function audit(siteRoot, otherResults) {
  otherResults = otherResults || {};
  var files = getAllHtmlFiles(siteRoot);

  var slugCounts = {};
  var slugPages = {};
  var totalGoLinks = 0;

  for (var i = 0; i < files.length; i++) {
    var abs = files[i].abs;
    var rel = files[i].rel;
    var html = readHtml(abs);
    var goLinks = extractGoLinks(html);
    totalGoLinks += goLinks.length;

    for (var j = 0; j < goLinks.length; j++) {
      var slug = goLinks[j].replace('/go/', '').split('/')[0].split('?')[0];
      slugCounts[slug] = (slugCounts[slug] || 0) + 1;
      if (!slugPages[slug]) slugPages[slug] = {};
      slugPages[slug][rel] = true;
    }
  }

  var inventory = Object.keys(slugCounts)
    .map(function(slug) {
      return {
        slug: slug,
        pagesFeaturingIt: Object.keys(slugPages[slug]).length,
        totalGoLinks: slugCounts[slug],
        exposureLevel: slugCounts[slug] >= 50 ? 'high' : slugCounts[slug] >= 20 ? 'medium' : 'low'
      };
    })
    .sort(function(a, b) { return b.totalGoLinks - a.totalGoLinks; });

  // Concentration risk
  var totalLinks = 0;
  var slugKeys = Object.keys(slugCounts);
  for (var k = 0; k < slugKeys.length; k++) totalLinks += slugCounts[slugKeys[k]];
  var top3 = inventory.slice(0, 3);
  var top3Total = 0;
  for (var t = 0; t < top3.length; t++) top3Total += top3[t].totalGoLinks;
  var top3Share = totalLinks > 0 ? top3Total / totalLinks : 0;
  var riskLevel = top3Share > 0.5 ? 'high' : top3Share > 0.3 ? 'medium' : 'low';
  var concentrationDetail = riskLevel + ' \u2014 top 3 tools (' + top3.map(function(i) { return i.slug; }).join(', ') + ') account for ' + (top3Share * 100).toFixed(1) + '% of all affiliate links';

  // Build action queue from other agent results
  var actionQueue = [];
  var agentKeys = Object.keys(otherResults);
  for (var a = 0; a < agentKeys.length; a++) {
    var result = otherResults[agentKeys[a]];
    if (!result || !result.issues) continue;
    for (var q = 0; q < result.issues.length; q++) {
      var issue = result.issues[q];
      if (issue.severity === 'critical' || issue.severity === 'high') {
        actionQueue.push({
          priority: 'P0',
          description: issue.detail,
          sourceAgent: result.agent ? result.agent.toUpperCase() : agentKeys[a].toUpperCase(),
          estimatedImpact: 'high'
        });
      }
    }
  }
  actionQueue.sort(function(a, b) { return a.priority.localeCompare(b.priority); });

  return {
    agent: 'revenueops',
    status: 'healthy',
    score: null,
    metrics: {
      totalGoSlugs: slugKeys.length,
      totalGoLinksAcrossSite: totalGoLinks,
      totalDirectLeaks: otherResults.revenuefunnel ? otherResults.revenuefunnel.metrics.totalDirectLeaks : 0,
      concentrationRisk: concentrationDetail,
      weeklyActionItems: actionQueue.length
    },
    issues: [],
    lastAction: 'Aggregated ' + agentKeys.length + ' agent results. ' + slugKeys.length + ' affiliate slugs, ' + totalGoLinks + ' total /go/ links. ' + actionQueue.length + ' action items queued.'
  };
};
```

- [ ] **Step 2: Smoke test**

Run: `node -e "const a = require('./scripts/agents/09-revenueops.js'); a('.', {}).then(r => console.log(r.agent, r.metrics.totalGoSlugs + ' slugs'))"`

- [ ] **Step 3: Commit**

```bash
git add scripts/agents/09-revenueops.js
git commit -m "feat(atlas): add 09-revenueops aggregation agent"
```

---

## Chunk 5: Refactor agent-autofix.js

### Task 11: Add --fix-plan mode to agent-autofix.js

**Files:**
- Modify: `scripts/agent-autofix.js`

The existing script runs all 8 fix types on all files. Add a `--fix-plan` flag that accepts a JSON file path. When provided, only run fix types specified in the plan.

- [ ] **Step 1: Add CLI argument parsing at the top of main()**

Insert after the line `console.log('');` (line 458) and before `var htmlFiles = getAllHtmlFiles(SITE_DIR);` (line 460):

```js
  // Parse --fix-plan argument for targeted mode
  var fixPlanArg = process.argv.indexOf('--fix-plan');
  var fixPlan = null;
  if (fixPlanArg !== -1 && process.argv[fixPlanArg + 1]) {
    var planPath = process.argv[fixPlanArg + 1];
    if (fs.existsSync(planPath)) {
      fixPlan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
      console.log('Running in targeted mode: ' + fixPlan.length + ' fixes from ' + planPath);
    }
  }
```

- [ ] **Step 2: Wrap fix calls with targeted filtering**

Replace the sequential fix calls (lines 464-494) with:

```js
  var fixTypes = fixPlan ? {} : null;
  if (fixPlan) {
    for (var f = 0; f < fixPlan.length; f++) {
      fixTypes[fixPlan[f].fix_type] = true;
    }
  }
  function shouldRun(type) { return !fixTypes || fixTypes[type]; }

  if (shouldRun('name_leaks')) {
    console.log('[1/8] Name Leak Detection (HIGHEST PRIORITY)...');
    fixNameLeaks(htmlFiles);
  }
  if (shouldRun('banned_phrases') || shouldRun('banned_phrase')) {
    console.log('[2/8] Banned Phrases...');
    fixBannedPhrases(htmlFiles);
  }
  if (shouldRun('demo_ctas') || shouldRun('demo_cta')) {
    console.log('[3/8] Demo CTA Errors...');
    fixDemoCtas(htmlFiles);
  }
  if (shouldRun('title_length')) {
    console.log('[4/8] Title Length...');
    fixTitleLength(htmlFiles);
  }
  if (shouldRun('meta_desc_length') || shouldRun('meta_desc')) {
    console.log('[5/8] Meta Description Length...');
    fixMetaDescLength(htmlFiles);
  }
  if (shouldRun('og_tags') || shouldRun('og_tags_missing')) {
    console.log('[6/8] Missing OG Tags...');
    fixMissingOgTags(htmlFiles);
  }
  if (shouldRun('freshness_dates') || shouldRun('title_freshness')) {
    console.log('[7/8] Freshness Dates...');
    fixFreshnessDates(htmlFiles);
  }
  if (shouldRun('price_consistency') || shouldRun('price_mismatch')) {
    console.log('[8/8] Price Consistency...');
    fixPriceConsistency(htmlFiles);
  }
```

- [ ] **Step 3: Test both modes**

Run full scan: `node scripts/agent-autofix.js 2>&1 | head -15`
Expected: all 8 fix types run

Run targeted: `echo '[{"fix_type":"name_leaks","file":"test.html","details":"test"}]' > /tmp/test-plan.json && node scripts/agent-autofix.js --fix-plan /tmp/test-plan.json 2>&1 | head -15`
Expected: only name leak detection runs

- [ ] **Step 4: Commit**

```bash
git add scripts/agent-autofix.js
git commit -m "feat(atlas): add --fix-plan targeted mode to agent-autofix"
```

---

## Chunk 6: ATLAS Orchestrator

### Task 12: Create scripts/atlas.js

**Files:**
- Create: `scripts/atlas.js`

This is the main orchestrator with 8 phases. Uses `execSync` with hardcoded command strings (no user input) to call git and netlify-cli.

- [ ] **Step 1: Create atlas.js with all 8 phases**

```js
#!/usr/bin/env node
/**
 * ATLAS - Automated Testing, Linking, Auditing & Strategy
 * Lead agent orchestrator. Runs 8 sequential phases.
 * See: docs/superpowers/specs/2026-03-12-atlas-lead-agent-design.md
 *
 * Security: All execSync calls use hardcoded strings with no user input.
 */

var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');
var execSync = childProcess.execSync;

var SITE_ROOT = path.resolve(__dirname, '..');
var DATA_DIR = path.join(SITE_ROOT, 'ops', 'data');
var DRY_RUN = process.env.ATLAS_DRY_RUN === 'true';

var SCORE_WEIGHTS = {
  revenuefunnel: 0.30,
  seopower: 0.20,
  sitehealth: 0.15,
  contentguard: 0.15,
  linkhealth: 0.10,
  priceverify: 0.10
};

var ALLOWED_STAGE_PATHS = [
  'tools/', 'best/', 'alternatives/', 'categories/', 'compare/',
  'pricing/', 'index.html', 'ops/data/', '404.html'
];

var PROTECTED_PATHS = ['.github/', 'scripts/', 'ops/js/', 'ops/css/', 'ops/index.html'];

var NAME_LEAK_PATTERNS = [/Matt\s/gi, /Matthew/gi, /Schneider/gi, /Toptal/gi];

function log(phase, msg) {
  console.log('[ATLAS:' + phase + '] ' + msg);
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

// Phase 1: AUTO-FIX (pre-audit)
function phase1() {
  log('P1', 'Running pre-audit auto-fix...');
  try {
    execSync('node scripts/agent-autofix.js', {
      cwd: SITE_ROOT, encoding: 'utf8', timeout: 120000
    });
    log('P1', 'Auto-fix complete.');
    return true;
  } catch (e) {
    log('P1', 'Auto-fix failed: ' + e.message);
    return false;
  }
}

// Phase 2: AUDIT (9 agents)
async function phase2() {
  log('P2', 'Running 9 audit agents...');
  var agentFiles = [
    '01-sitehealth', '02-revenuefunnel', '03-linkhealth',
    '04-priceverify', '05-contentguard', '06-seopower',
    '07-trafficintel', '08-contentengine', '09-revenueops'
  ];

  var results = {};

  for (var i = 0; i < agentFiles.length; i++) {
    var name = agentFiles[i];
    var agentKey = name.replace(/^\d+-/, '');
    log('P2', 'Running ' + name + '...');
    try {
      var agentFn = require(path.join(__dirname, 'agents', name + '.js'));
      var result = agentKey === 'revenueops'
        ? await agentFn(SITE_ROOT, results)
        : await agentFn(SITE_ROOT);
      results[agentKey] = result;
      log('P2', '  ' + agentKey + ': score=' + result.score + ', status=' + result.status);
    } catch (e) {
      log('P2', '  ' + agentKey + ' FAILED: ' + e.message);
      results[agentKey] = {
        agent: agentKey, status: 'critical', score: 0,
        metrics: {}, issues: [{ check: 'agent_error', severity: 'critical', detail: e.message }],
        lastAction: 'Agent failed: ' + e.message
      };
    }
  }

  return results;
}

// Phase 3: DECIDE
function phase3(results) {
  log('P3', 'Building fix plan...');
  var fixPlan = [];

  var keys = Object.keys(results);
  for (var i = 0; i < keys.length; i++) {
    var result = results[keys[i]];
    if (!result.issues) continue;
    for (var j = 0; j < result.issues.length; j++) {
      var issue = result.issues[j];
      if (issue.severity === 'critical' || issue.severity === 'high') {
        fixPlan.push({
          file: issue.detail.split(':')[0] || '',
          fix_type: issue.check,
          details: issue.detail,
          priority: 'P0'
        });
      } else if (issue.severity === 'med') {
        fixPlan.push({
          file: issue.detail.split(':')[0] || '',
          fix_type: issue.check,
          details: issue.detail,
          priority: 'P1'
        });
      }
    }
  }

  fixPlan.sort(function(a, b) { return a.priority.localeCompare(b.priority); });

  if (fixPlan.length > 200) {
    var trimmed = fixPlan.filter(function(f) { return f.priority === 'P0' || f.priority === 'P1'; });
    log('P3', 'Fix plan trimmed from ' + fixPlan.length + ' to ' + trimmed.length + ' (P0+P1 only)');
    return trimmed;
  }

  log('P3', 'Fix plan: ' + fixPlan.length + ' items');
  return fixPlan;
}

// Phase 4: FIX (post-audit)
function phase4(fixPlan) {
  if (fixPlan.length === 0) {
    log('P4', 'No fixes to apply.');
    return;
  }

  log('P4', 'Applying ' + fixPlan.length + ' targeted fixes...');
  var planPath = path.join(DATA_DIR, 'fix-plan.json');
  writeJson(planPath, fixPlan);

  try {
    execSync('node scripts/agent-autofix.js --fix-plan ' + planPath, {
      cwd: SITE_ROOT, encoding: 'utf8', timeout: 120000
    });
    log('P4', 'Targeted fixes applied.');
  } catch (e) {
    log('P4', 'Targeted fix failed: ' + e.message);
  }
}

// Phase 5: VALIDATE
function phase5() {
  log('P5', 'Running validation checks...');

  var scanner = require('./agents/lib/html-scanner');
  var files = scanner.getAllHtmlFiles(SITE_ROOT);
  for (var i = 0; i < files.length; i++) {
    var html = scanner.readHtml(files[i].abs);
    var visibleText = html.replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ');

    for (var j = 0; j < NAME_LEAK_PATTERNS.length; j++) {
      NAME_LEAK_PATTERNS[j].lastIndex = 0;
      if (NAME_LEAK_PATTERNS[j].test(visibleText)) {
        log('P5', 'CRITICAL: Name leak found in ' + files[i].rel + '! Rolling back.');
        return { valid: false, reason: 'Name leak in ' + files[i].rel };
      }
    }
  }

  log('P5', 'Validation passed.');
  return { valid: true };
}

// Phase 6: UPDATE
function phase6(results, previousState) {
  log('P6', 'Updating data files...');

  var overall = 0;
  var weightKeys = Object.keys(SCORE_WEIGHTS);
  for (var w = 0; w < weightKeys.length; w++) {
    var agent = weightKeys[w];
    var weight = SCORE_WEIGHTS[agent];
    var result = results[agent];
    if (result && typeof result.score === 'number') {
      overall += result.score * weight;
    }
  }
  overall = Math.round(overall);

  var state = previousState || {};
  var runCount = (state.runCount || 0) + 1;
  state.lastRun = new Date().toISOString();
  state.runCount = runCount;
  state.overallScore = overall;

  if (!state.agents) state.agents = {};
  var resultKeys = Object.keys(results);
  for (var i = 0; i < resultKeys.length; i++) {
    var key = resultKeys[i];
    var r = results[key];
    var existing = state.agents[key] || {};
    state.agents[key] = {
      name: existing.name || key.toUpperCase(),
      icon: existing.icon || '',
      description: existing.description || '',
      lastAction: r.lastAction,
      plan: existing.plan || {},
      status: r.status,
      lastRun: new Date().toISOString(),
      metrics: r.metrics,
      issues: r.issues.slice(0, 20),
      score: r.score
    };
  }

  writeJson(path.join(DATA_DIR, 'agent-state.json'), state);

  // Update history
  var historyPath = path.join(DATA_DIR, 'history.json');
  var history;
  try { history = readJson(historyPath); } catch (e) { history = { runs: [] }; }
  var agentScores = {};
  var totalFound = 0;
  var totalFixed = 0;
  for (var h = 0; h < resultKeys.length; h++) {
    var rr = results[resultKeys[h]];
    agentScores[resultKeys[h]] = rr.score;
    totalFound += (rr.issues || []).length;
    if (rr.metrics && typeof rr.metrics.issuesFixed === 'number') totalFixed += rr.metrics.issuesFixed;
  }
  history.runs.push({
    date: new Date().toISOString().split('T')[0],
    runNumber: runCount,
    overallScore: overall,
    issuesFound: totalFound,
    issuesFixed: totalFixed,
    topAction: 'Weekly cycle #' + runCount + ' \u2014 score ' + overall + '/100',
    agentScores: agentScores
  });
  writeJson(historyPath, history);

  // Update activity log
  var activityPath = path.join(DATA_DIR, 'activity-log.json');
  var activity;
  try { activity = readJson(activityPath); } catch (e) { activity = { lastUpdated: '', entries: [] }; }
  var now = new Date().toISOString();
  activity.lastUpdated = now;
  for (var a = 0; a < resultKeys.length; a++) {
    var ar = results[resultKeys[a]];
    if (ar.lastAction) {
      activity.entries.unshift({
        timestamp: now,
        agent: resultKeys[a],
        icon: (state.agents[resultKeys[a]] && state.agents[resultKeys[a]].icon) || '',
        action: ar.lastAction,
        type: ar.issues.length > 0 ? 'fix' : 'audit',
        impact: 'Score: ' + (ar.score !== null ? ar.score : 'N/A')
      });
    }
  }
  activity.entries = activity.entries.slice(0, 50);
  writeJson(activityPath, activity);

  log('P6', 'Data updated. Overall score: ' + overall + '. Run #' + runCount + '.');
  return { overall: overall, runCount: runCount, totalFound: totalFound, totalFixed: totalFixed };
}

// Phase 7: COMMIT + DEPLOY
function phase7(runCount, overall, issuesFixed) {
  if (DRY_RUN) {
    log('P7', 'DRY RUN \u2014 skipping commit and deploy.');
    try {
      var diff = execSync('git diff --stat', { cwd: SITE_ROOT, encoding: 'utf8' });
      log('P7', 'Would commit:\n' + diff);
    } catch (e) { /* ignore */ }
    return 'skipped';
  }

  log('P7', 'Staging and committing changes...');

  try {
    for (var i = 0; i < ALLOWED_STAGE_PATHS.length; i++) {
      try {
        execSync('git add ' + ALLOWED_STAGE_PATHS[i], { cwd: SITE_ROOT, encoding: 'utf8' });
      } catch (e) { /* path may not exist */ }
    }

    var staged = execSync('git diff --cached --name-only', { cwd: SITE_ROOT, encoding: 'utf8' });
    var stagedFiles = staged.split('\n').filter(Boolean);
    for (var j = 0; j < stagedFiles.length; j++) {
      var file = stagedFiles[j];
      for (var k = 0; k < PROTECTED_PATHS.length; k++) {
        if (file.startsWith(PROTECTED_PATHS[k])) {
          log('P7', 'WARNING: unstaging protected file: ' + file);
          execSync('git reset HEAD -- "' + file + '"', { cwd: SITE_ROOT, encoding: 'utf8' });
          break;
        }
      }
    }

    var cachedDiff = execSync('git diff --cached --stat', { cwd: SITE_ROOT, encoding: 'utf8' });
    if (!cachedDiff.trim()) {
      log('P7', 'No changes to commit.');
      return 'no_changes';
    }

    log('P7', cachedDiff);

    var msg = 'atlas: weekly cycle #' + runCount + ' \u2014 score ' + overall + '/100, ' + issuesFixed + ' issues fixed';
    execSync('git commit -m "' + msg + '"', { cwd: SITE_ROOT, encoding: 'utf8' });
    log('P7', 'Committed.');

    log('P7', 'Deploying to Netlify...');
    try {
      execSync('npx netlify-cli deploy --dir . --prod', {
        cwd: SITE_ROOT, encoding: 'utf8', timeout: 300000
      });
      log('P7', 'Deployed successfully.');
      return 'success';
    } catch (e) {
      log('P7', 'Deploy FAILED: ' + e.message);
      return 'deploy_failed';
    }
  } catch (e) {
    log('P7', 'Commit/deploy failed: ' + e.message);
    return 'failed';
  }
}

// Phase 8: REPORT (always runs)
function phase8(status, runCount, overall, previousScore, results, filesChanged, deployStatus, failureReason, startTime) {
  var report = {
    runNumber: runCount,
    timestamp: new Date().toISOString(),
    durationMs: Date.now() - startTime,
    status: status,
    overallScore: { before: previousScore, after: overall },
    issuesByAgent: {},
    filesChanged: filesChanged,
    deployStatus: deployStatus,
    failureReason: failureReason
  };

  var keys = Object.keys(results);
  for (var i = 0; i < keys.length; i++) {
    var r = results[keys[i]];
    report.issuesByAgent[keys[i]] = {
      found: (r.issues || []).length,
      fixed: (r.metrics && r.metrics.issuesFixed) || 0
    };
  }

  writeJson(path.join(DATA_DIR, 'last-run-report.json'), report);
  log('P8', 'Report written. Status: ' + status + '. Duration: ' + report.durationMs + 'ms.');
  return report;
}

// Main
async function main() {
  var startTime = Date.now();
  log('MAIN', '=== ATLAS Weekly Cycle ===');
  log('MAIN', 'Started: ' + new Date().toISOString());
  if (DRY_RUN) log('MAIN', 'DRY RUN MODE \u2014 no commit or deploy');

  var statePath = path.join(DATA_DIR, 'agent-state.json');
  var previousState = {};
  var previousScore = 0;
  try {
    previousState = readJson(statePath);
    previousScore = previousState.overallScore || 0;
  } catch (e) { /* first run */ }

  var runCount = (previousState.runCount || 0) + 1;

  // Phase 1
  phase1();

  // Phase 2
  var results = await phase2();

  // Phase 3
  var fixPlan = phase3(results);

  // Phase 4
  phase4(fixPlan);

  // Phase 5
  var validation = phase5();
  if (!validation.valid) {
    log('MAIN', 'VALIDATION FAILED \u2014 rolling back.');
    try {
      execSync('git checkout -- .', { cwd: SITE_ROOT, encoding: 'utf8' });
    } catch (e) { /* ignore */ }
    phase8('rolled_back', runCount, 0, previousScore, results, 0, 'skipped', validation.reason, startTime);
    process.exit(1);
  }

  // Phase 6
  var p6 = phase6(results, previousState);

  // Phase 7
  var filesChanged = 0;
  try {
    var stat = execSync('git diff --stat', { cwd: SITE_ROOT, encoding: 'utf8' });
    var fMatch = stat.match(/(\d+) file/);
    filesChanged = fMatch ? parseInt(fMatch[1], 10) : 0;
  } catch (e) { /* ignore */ }

  var deployStatus = phase7(p6.runCount, p6.overall, p6.totalFixed);

  // Phase 8
  var finalStatus = deployStatus === 'failed' ? 'failed' : 'success';
  phase8(finalStatus, p6.runCount, p6.overall, previousScore, results, filesChanged,
    DRY_RUN ? 'skipped' : deployStatus, null, startTime);

  log('MAIN', '=== ATLAS Complete. Score: ' + p6.overall + '/100 ===');
}

main().catch(function(e) {
  console.error('[ATLAS:FATAL]', e);
  process.exit(1);
});
```

- [ ] **Step 2: Test in dry-run mode**

Run: `ATLAS_DRY_RUN=true node scripts/atlas.js 2>&1 | tail -30`
Expected output includes:
- `[ATLAS:P1] Running pre-audit auto-fix...`
- `[ATLAS:P2] Running 9 audit agents...`
- `[ATLAS:P5] Validation passed.`
- `[ATLAS:P7] DRY RUN`
- `[ATLAS:P8] Report written.`
- `[ATLAS:MAIN] === ATLAS Complete.`

- [ ] **Step 3: Verify report was written**

Run: `node -e "var r = JSON.parse(require('fs').readFileSync('ops/data/last-run-report.json','utf8')); console.log('status:', r.status, 'score:', r.overallScore.after, 'agents:', Object.keys(r.issuesByAgent).length)"`
Expected: `status: success score: <N> agents: 9`

- [ ] **Step 4: Commit**

```bash
git add scripts/atlas.js
git commit -m "feat(atlas): add lead agent orchestrator with 8-phase pipeline"
```

---

## Chunk 7: GitHub Actions Workflow + Final Test

### Task 13: Create .github/workflows/atlas-weekly.yml

**Files:**
- Create: `.github/workflows/atlas-weekly.yml`

- [ ] **Step 1: Create the workflow file**

```yaml
name: ATLAS Weekly Cycle
on:
  schedule:
    - cron: '0 6 * * 0'
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (no commit/deploy)'
        type: boolean
        default: false

jobs:
  atlas:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Configure git identity
        run: |
          git config user.name "atlas-bot"
          git config user.email "atlas-bot@users.noreply.github.com"

      - name: Install netlify-cli
        run: npm install -g netlify-cli

      - name: Run ATLAS
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          ATLAS_DRY_RUN: ${{ inputs.dry_run || 'false' }}
        run: node scripts/atlas.js

      - name: Push changes
        if: success() && inputs.dry_run != 'true'
        run: git push
```

- [ ] **Step 2: Validate YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atlas-weekly.yml')); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/atlas-weekly.yml
git commit -m "ci(atlas): add weekly GitHub Actions workflow with dry-run support"
```

### Task 14: End-to-end dry-run test

- [ ] **Step 1: Run full ATLAS in dry-run mode**

Run: `ATLAS_DRY_RUN=true node scripts/atlas.js 2>&1 | tail -30`
Expected: all 8 phases complete, report written, no commit/deploy

- [ ] **Step 2: Verify all data files were updated**

Run: `ls -la ops/data/last-run-report.json ops/data/agent-state.json ops/data/history.json ops/data/activity-log.json`
Expected: all 4 files exist with recent timestamps

- [ ] **Step 3: Verify report content**

Run: `node -e "var r = JSON.parse(require('fs').readFileSync('ops/data/last-run-report.json','utf8')); console.log('status:', r.status, 'score:', r.overallScore.after, 'agents:', Object.keys(r.issuesByAgent).length)"`
Expected: `status: success score: <N> agents: 9`

- [ ] **Step 4: Final commit with test data**

```bash
git add ops/data/last-run-report.json
git commit -m "test(atlas): verify dry-run produces valid report"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Shared HTML scanner | `scripts/agents/lib/html-scanner.js` |
| 2 | SITEHEALTH agent | `scripts/agents/01-sitehealth.js` |
| 3 | REVENUEFUNNEL agent | `scripts/agents/02-revenuefunnel.js` |
| 4 | LINKHEALTH agent | `scripts/agents/03-linkhealth.js` |
| 5 | PRICEVERIFY agent | `scripts/agents/04-priceverify.js` |
| 6 | CONTENTGUARD agent | `scripts/agents/05-contentguard.js` |
| 7 | SEOPOWER agent | `scripts/agents/06-seopower.js` |
| 8 | TRAFFICINTEL agent | `scripts/agents/07-trafficintel.js` |
| 9 | CONTENTENGINE agent | `scripts/agents/08-contentengine.js` |
| 10 | REVENUEOPS agent | `scripts/agents/09-revenueops.js` |
| 11 | Refactor autofix | `scripts/agent-autofix.js` (modify) |
| 12 | ATLAS orchestrator | `scripts/atlas.js` |
| 13 | GitHub Actions | `.github/workflows/atlas-weekly.yml` |
| 14 | E2E dry-run test | Verification only |

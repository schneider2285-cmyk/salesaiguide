'use strict';

const fs = require('fs');
const path = require('path');

const SKIP_DIRS = ['ops', 'node_modules', '.git', '.claude', '.playwright-cli', '.playwright-mcp', 'scripts', '.github', '_private', 'docs', 'progress'];

/**
 * Recursively walk directories and return all .html files.
 * @param {string} siteRoot - Absolute path to the site root
 * @returns {Array<{abs: string, rel: string}>}
 */
function getAllHtmlFiles(siteRoot) {
  const results = [];

  function walk(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
      return;
    }

    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (SKIP_DIRS.includes(entry.name)) continue;
        walk(path.join(dir, entry.name));
      } else if (entry.isFile() && entry.name.endsWith('.html')) {
        const abs = path.join(dir, entry.name);
        const rel = path.relative(siteRoot, abs);
        results.push({ abs, rel });
      }
    }
  }

  walk(siteRoot);
  return results;
}

/**
 * Read an HTML file as a UTF-8 string.
 * @param {string} filePath
 * @returns {string}
 */
function readHtml(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * Classify a page based on its relative path.
 * @param {string} rel - Relative path from site root
 * @returns {string} page type
 */
function classifyPage(rel) {
  const normalized = rel.replace(/\\/g, '/');

  if (/^tools\/[^/]+-review\.html$/.test(normalized)) return 'review';
  if (normalized.startsWith('compare/')) return 'comparison';
  if (normalized.startsWith('best/')) return 'best-pick';
  if (normalized.startsWith('pricing/')) return 'pricing';
  if (normalized.startsWith('alternatives/')) return 'alternatives';
  if (normalized.startsWith('categories/')) return 'category';
  if (normalized === 'index.html') return 'homepage';
  return 'other';
}

/**
 * Extract the text content of the <title> tag.
 * @param {string} html
 * @returns {string|null}
 */
function extractTitle(html) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return match ? match[1].trim() : null;
}

/**
 * Extract the content attribute of <meta name="description">.
 * @param {string} html
 * @returns {string|null}
 */
function extractMetaDesc(html) {
  const match = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i)
    || html.match(/<meta\s+content=["']([\s\S]*?)["']\s+name=["']description["']/i);
  return match ? match[1].trim() : null;
}

/**
 * Find and parse all <script type="application/ld+json"> blocks.
 * @param {string} html
 * @returns {Array<object>} Parsed JSON objects; invalid blocks include _parseError
 */
function extractJsonLd(html) {
  const results = [];
  const regex = /<script\s+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let match;

  while ((match = regex.exec(html)) !== null) {
    const raw = match[1].trim();
    try {
      results.push(JSON.parse(raw));
    } catch (e) {
      results.push({ _parseError: e.message, _raw: raw });
    }
  }

  return results;
}

/**
 * Count words in an HTML document after stripping scripts, styles, and tags.
 * @param {string} html
 * @returns {number}
 */
function countWords(html) {
  let text = html.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  text = text.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  text = text.replace(/<[^>]+>/g, ' ');
  text = text.replace(/&nbsp;/g, ' ')
             .replace(/&amp;/g, '&')
             .replace(/&lt;/g, '<')
             .replace(/&gt;/g, '>')
             .replace(/&quot;/g, '"')
             .replace(/&#\d+;/g, ' ');
  const words = text.split(/\s+/).filter(w => w.length > 0);
  return words.length;
}

/**
 * Extract all /go/... affiliate link hrefs.
 * @param {string} html
 * @returns {string[]}
 */
function extractGoLinks(html) {
  const results = [];
  const regex = /href=["'](\/go\/[^"'#?]*)["']/gi;
  let match;

  while ((match = regex.exec(html)) !== null) {
    results.push(match[1]);
  }

  return results;
}

/**
 * Extract all internal link hrefs (not http/https, mailto, #, /go/, or tel:).
 * @param {string} html
 * @returns {string[]}
 */
function extractInternalLinks(html) {
  const results = [];
  const regex = /href=["']([^"']+)["']/gi;
  let match;

  while ((match = regex.exec(html)) !== null) {
    const href = match[1];
    if (
      href.startsWith('http') ||
      href.startsWith('mailto:') ||
      href.startsWith('#') ||
      href.startsWith('/go/') ||
      href.startsWith('tel:')
    ) {
      continue;
    }
    results.push(href);
  }

  return results;
}

module.exports = {
  SKIP_DIRS,
  getAllHtmlFiles,
  readHtml,
  classifyPage,
  extractTitle,
  extractMetaDesc,
  extractJsonLd,
  countWords,
  extractGoLinks,
  extractInternalLinks,
};

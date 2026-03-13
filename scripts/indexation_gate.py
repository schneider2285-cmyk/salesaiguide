#!/usr/bin/env python3
"""
SalesAIGuide.com Indexation Gate
Grades pages A/B/C, generates sitemaps, _headers, and reports.
Python stdlib only.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VOID_ELEMENTS = frozenset([
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
])

BOILERPLATE_CLASSES = frozenset([
    "navbar", "footer", "nav-menu", "nav-brand", "editorial-trust",
])

CONTENT_CLASSES = frozenset([
    "review-content", "content-section", "quick-summary", "summary-grid",
    "review-header", "hero",
])

PLACEHOLDER_RE = re.compile(
    r"coming soon|TODO|lorem ipsum|TBD|placeholder|\[insert",
    re.IGNORECASE,
)

DATE_PATTERN_RE = re.compile(r"\(\w{3,9}\s+\d{4}\)|\(\d{4}\)")

AFFILIATE_RE = re.compile(r"^/go/|[?&](ref=|via=|utm_source=salesaiguide)")

SCENARIO_RE = re.compile(r"scenario|use case|when to", re.IGNORECASE)
GOTCHA_RE = re.compile(r"gotcha|limitation|watch out|downside", re.IGNORECASE)
CONSIDER_RE = re.compile(r"what to consider|how to choose|things to look for", re.IGNORECASE)
FAILURE_RE = re.compile(r"failure|common mistake|pitfall|avoid", re.IGNORECASE)
BESTPICK_RE = re.compile(r"best.+for|pick.+by.+scenario|recommended.+for", re.IGNORECASE)

EDITORIAL_FILES = {"about.html", "disclosure.html", "methodology.html",
                   "editorial-policy.html", "corrections.html"}

STATIC_FILES = {"privacy.html", "terms.html"}

PRIORITY_MAP = {
    "homepage": "1.0", "review": "0.9", "comparison": "0.8",
    "directory": "0.8", "best_of": "0.8", "alternatives": "0.7",
    "pricing": "0.7", "category_hub": "0.6", "resource": "0.5",
    "editorial": "0.3", "static_page": "0.3",
}

CHANGEFREQ_MAP = {
    "homepage": "weekly",
    "review": "monthly",
    "comparison": "monthly",
    "best_of": "monthly",
    "alternatives": "monthly",
    "pricing": "weekly",
    "category_hub": "monthly",
    "directory": "monthly",
    "resource": "monthly",
    "editorial": "yearly",
    "static_page": "yearly",
}

# ---------------------------------------------------------------------------
# Slop Linter Constants
# ---------------------------------------------------------------------------

SLOP_APPLICABLE_TYPES = frozenset(["review", "comparison"])

# Signal 4: Numeric claims that need citations
NUMERIC_CLAIM_RE = re.compile(
    r"\d+%|\d+x|\$\d+|\d+-\d+%|\d+\.\d+/\d+"
)

# Signal 4: Date patterns to EXCLUDE from numeric claim detection
DATE_EXCLUDE_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b"                          # ISO dates
    r"|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{4}\b"                         # Month YYYY
    r"|\bv\d+(?:\.\d+)*\b"                              # Version strings
)

# Signal 6: Hype words
HYPE_WORDS = frozenset([
    "revolutionary", "game-changing", "cutting-edge", "next-generation",
    "world-class", "best-in-class", "state-of-the-art", "groundbreaking",
    "unparalleled", "unmatched", "unrivaled", "seamless", "seamlessly",
    "effortless", "effortlessly", "supercharge", "skyrocket", "turbocharge",
    "unprecedented", "transformative", "leverage", "synergy",
])

HYPE_DENSITY_THRESHOLD = 0.02  # 2%

# Signal 7: Allowed zones for /go/ links
ALLOWED_GO_ZONES = frozenset([
    "quick-summary", "summary-grid", "pricing-table", "pricing-tier",
])

# Signal 9: Last-verified thresholds (days)
LAST_VERIFIED_A_MAX = 90
LAST_VERIFIED_B_MAX = 365

# Signal 9: Month name lookup
MONTH_NAMES = {
    "jan": 1, "january": 1, "feb": 2, "february": 2,
    "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# ---------------------------------------------------------------------------
# Content Extractor
# ---------------------------------------------------------------------------

class ContentExtractor(HTMLParser):
    """Parse HTML and extract structured data with zone tracking."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.canonical = ""
        self.json_ld = []

        # Zone tracking
        self._zone_stack = []  # list of (zone_name, tag, depth)
        self._depth = 0
        self._in_title = False
        self._in_script = False
        self._script_type = ""
        self._script_buf = ""
        self._in_details = False
        self._details_depth = 0

        # Text by zone
        self.text_by_zone = defaultdict(list)  # zone -> [words]
        self.all_content_text = []
        self.core_editorial_text = []
        self.sources_checked_text = []
        self.tool_card_text = []

        # Links: (href, zone, anchor_text)
        self.links = []
        self._current_link_href = None
        self._current_link_text = []
        self._current_link_zone = None

        # Section headers
        self.headers = []  # (level, text)
        self._in_header = False
        self._header_level = 0
        self._header_text = []

        # Empty H2 section tracking
        self._last_h2_text = None  # text of most recent H2
        self._words_since_h2 = 0   # content words since that H2
        self.empty_h2_sections = []  # list of H2 texts with < 10 content words

        # Detections
        self.has_comparison_table = False
        self.has_pros_cons = False
        self.has_pricing = False
        self.has_verdict = False
        self.verdict_in_details = False
        self.has_scenario = False
        self.has_gotcha = False
        self.has_consider = False
        self.has_failure = False
        self.has_bestpick = False
        self.tool_card_count = 0
        self.placeholders_found = []

        # Sources-checked module
        self.sources_checked_links = []  # (href, text)
        self._in_sources_checked = False
        self._sources_checked_depth = 0
        self._sources_checked_raw = []

        # Blockquotes
        self.blockquotes = []  # list of dicts
        self._in_blockquote = False
        self._blockquote_depth = 0
        self._blockquote_text = []

        # Rating markup in tool cards
        self.tool_card_ratings = []  # list of {"links": [...], "has_rating": bool} for cards with ratings
        self._in_tool_card = False
        self._tool_card_depth = 0
        self._tool_card_links = []
        self._tool_card_has_rating = False

        # --- Slop Linter Fields ---

        # Signal 2: Thin section tracking (SEPARATE from empty_h2 hard-fail)
        self.section_stats = []       # {"header", "level", "words", "has_rich_content"}
        self._section_header = None
        self._section_level = 0
        self._section_words = 0
        self._section_has_rich = False
        self._li_count = 0
        self._in_list = False

        # Signal 3: Blockquote attribution tracking
        self._blockquote_links = []   # links found inside current blockquote
        self._post_bq_check = False   # flag to capture first link after blockquote

        # Signal 4: Core-editorial paragraphs for numeric claims
        self.core_editorial_paragraphs = []  # {"text": str, "links": [(pos, href)]}
        self._ce_para_text = ""
        self._ce_para_links = []
        self._in_ce_para = False

        # Signal 7: /go/ link tracking for conversion-first
        self.go_links_in_core_editorial = []   # list of hrefs
        self.go_link_word_positions = []       # (word_offset, href, zone)
        self.verdict_word_position = None
        self._content_word_count = 0

        # Signal 7: Allowed CTA zone tracking
        self._in_allowed_go_zone = False
        self._allowed_go_zone_depth = 0

        # Signal 9: Last verified
        self.last_verified_text = ""
        self._in_last_verified = False

    def _current_zone(self):
        return self._zone_stack[-1][0] if self._zone_stack else "content"

    def _get_classes(self, attrs):
        for k, v in attrs:
            if k == "class" and v:
                return set(v.split())
        return set()

    def _get_attr(self, attrs, name):
        for k, v in attrs:
            if k == name:
                return v or ""
        return ""

    def handle_starttag(self, tag, attrs):
        if tag in VOID_ELEMENTS:
            self._handle_void(tag, attrs)
            return

        self._depth += 1
        classes = self._get_classes(attrs)
        data_audit = self._get_attr(attrs, "data-audit")

        # Zone detection
        if classes & BOILERPLATE_CLASSES:
            self._zone_stack.append(("boilerplate", tag, self._depth))
        elif data_audit == "core-editorial":
            self._zone_stack.append(("core-editorial", tag, self._depth))
        elif data_audit == "sources-checked" or "sources-checked" in classes:
            self._zone_stack.append(("sources-checked", tag, self._depth))
            self._in_sources_checked = True
            self._sources_checked_depth = self._depth
        elif "tool-card" in classes:
            self._zone_stack.append(("tool-card", tag, self._depth))
            self.tool_card_count += 1
            self._in_tool_card = True
            self._tool_card_depth = self._depth
            self._tool_card_links = []
            self._tool_card_has_rating = False
        elif classes & CONTENT_CLASSES:
            self._zone_stack.append(("content", tag, self._depth))

        # Feature detection
        if "comparison-table" in classes:
            self.has_comparison_table = True
        if "pros-cons" in classes:
            self.has_pros_cons = True
        if "pricing-table" in classes or "pricing-tier" in classes:
            self.has_pricing = True
        if "final-verdict" in classes or "verdict-text" in classes or data_audit == "decision-summary":
            self.has_verdict = True
            if self._in_details:
                self.verdict_in_details = True
            # Signal 7: Record verdict word position (prefer decision-summary)
            if data_audit == "decision-summary" or self.verdict_word_position is None:
                self.verdict_word_position = self._content_word_count

        # Signal 7: Allowed /go/ zone tracking
        if classes & ALLOWED_GO_ZONES:
            self._in_allowed_go_zone = True
            self._allowed_go_zone_depth = self._depth

        # Signal 9: Last-verified tracking
        if data_audit == "last-verified" or "last-verified" in classes:
            self._in_last_verified = True

        # Rating markup in tool cards (exclude listed-rating which is intentionally unscored)
        if self._in_tool_card and classes & {"stars", "score", "rating"} and "listed-rating" not in classes:
            self._tool_card_has_rating = True

        # Details tracking
        if tag == "details":
            self._in_details = True
            self._details_depth = self._depth

        # Signal 2: Rich content detection for current section
        if tag in ("table", "iframe"):
            self._section_has_rich = True
        if tag == "figure":
            self._section_has_rich = True
        if tag in ("ul", "ol"):
            self._in_list = True
            self._li_count = 0
        if tag == "li" and self._in_list:
            self._li_count += 1

        # Signal 4: Core-editorial paragraph tracking
        if tag == "p" and self._current_zone() == "core-editorial":
            self._in_ce_para = True
            self._ce_para_text = ""
            self._ce_para_links = []

        # Blockquote tracking
        if tag == "blockquote":
            self._in_blockquote = True
            self._blockquote_depth = self._depth
            self._blockquote_text = []
            self._blockquote_links = []  # Signal 3: reset links for this blockquote

        # Title
        if tag == "title":
            self._in_title = True

        # Script (JSON-LD)
        if tag == "script":
            stype = self._get_attr(attrs, "type")
            if stype == "application/ld+json":
                self._in_script = True
                self._script_buf = ""

        # Headers
        if tag in ("h2", "h3"):
            # Check if previous H2 section was empty (< 10 content words)
            if tag == "h2" and self._last_h2_text is not None:
                if self._words_since_h2 < 10:
                    self.empty_h2_sections.append(self._last_h2_text)
            # Signal 2: Finalize previous section stats (separate from empty_h2)
            if self._section_header is not None:
                self.section_stats.append({
                    "header": self._section_header,
                    "level": self._section_level,
                    "words": self._section_words,
                    "has_rich_content": self._section_has_rich,
                })
            self._section_header = None  # Will be set in handle_endtag
            self._section_level = int(tag[1])
            self._section_words = 0
            self._section_has_rich = False

            self._in_header = True
            self._header_level = int(tag[1])
            self._header_text = []

        # Links
        if tag == "a":
            href = self._get_attr(attrs, "href")
            self._current_link_href = href
            self._current_link_text = []
            self._current_link_zone = self._current_zone()
            if self._in_tool_card and href:
                self._tool_card_links.append(href)
            if self._in_sources_checked and href:
                self._current_link_text = []
            # Signal 3: Track links inside blockquotes
            if self._in_blockquote and href:
                self._blockquote_links.append(href)
            # Signal 4: Track links inside core-editorial paragraphs
            if self._in_ce_para and href:
                self._ce_para_links.append((len(self._ce_para_text), href))
            # Signal 7: Track /go/ links
            if href and (href.startswith("/go/") or "/go/" in href):
                zone = self._current_zone()
                zone_label = "allowed" if self._in_allowed_go_zone else zone
                self.go_link_word_positions.append(
                    (self._content_word_count, href, zone_label)
                )
                if zone == "core-editorial":
                    self.go_links_in_core_editorial.append(href)

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return

        # Title
        if tag == "title":
            self._in_title = False

        # Script
        if tag == "script" and self._in_script:
            self._in_script = False
            try:
                self.json_ld.append(json.loads(self._script_buf))
            except (json.JSONDecodeError, ValueError):
                pass

        # Signal 2: List end → check if rich content (≥3 items)
        if tag in ("ul", "ol") and self._in_list:
            if self._li_count >= 3:
                self._section_has_rich = True
            self._in_list = False

        # Signal 4: Core-editorial paragraph end
        if tag == "p" and self._in_ce_para:
            self._in_ce_para = False
            if self._ce_para_text.strip():
                self.core_editorial_paragraphs.append({
                    "text": self._ce_para_text.strip(),
                    "links": list(self._ce_para_links),
                })

        # Headers
        if tag in ("h2", "h3") and self._in_header:
            self._in_header = False
            text = " ".join(self._header_text).strip()
            self.headers.append((self._header_level, text))
            # Signal 2: Record section header text
            self._section_header = text
            # Track H2 sections for empty detection
            if self._header_level == 2:
                self._last_h2_text = text
                self._words_since_h2 = 0
            if SCENARIO_RE.search(text):
                self.has_scenario = True
            if GOTCHA_RE.search(text):
                self.has_gotcha = True
            if CONSIDER_RE.search(text):
                self.has_consider = True
            if FAILURE_RE.search(text):
                self.has_failure = True
            if BESTPICK_RE.search(text):
                self.has_bestpick = True

        # Links
        if tag == "a" and self._current_link_href is not None:
            anchor = " ".join(self._current_link_text).strip()
            href = self._current_link_href
            self.links.append((href, self._current_link_zone, anchor))
            if self._in_sources_checked:
                self.sources_checked_links.append((href, anchor))
            # Signal 3: First link after blockquote → update attribution
            if self._post_bq_check and self.blockquotes:
                self._post_bq_check = False
                if href.startswith("https://") and not href.startswith("/go/") and "/go/" not in href:
                    self.blockquotes[-1]["has_external_cite"] = True
            self._current_link_href = None

        # Details
        if tag == "details" and self._in_details and self._depth == self._details_depth:
            self._in_details = False

        # Blockquote
        if tag == "blockquote" and self._in_blockquote and self._depth == self._blockquote_depth:
            self._in_blockquote = False
            # Signal 3: Check if blockquote has external citation link
            has_ext_cite = False
            for lnk in self._blockquote_links:
                if lnk.startswith("https://") and not lnk.startswith("/go/") and "/go/" not in lnk:
                    has_ext_cite = True
                    break
            self.blockquotes.append({
                "text": " ".join(self._blockquote_text).strip(),
                "has_external_cite": has_ext_cite,
            })
            self._post_bq_check = True  # Check next link after blockquote

        # Sources-checked zone end
        if self._in_sources_checked and self._depth == self._sources_checked_depth:
            self._in_sources_checked = False

        # Signal 7: Allowed /go/ zone end
        if self._in_allowed_go_zone and self._depth == self._allowed_go_zone_depth:
            self._in_allowed_go_zone = False

        # Signal 9: Last-verified zone end
        if self._in_last_verified and tag in ("div", "span", "p"):
            self._in_last_verified = False

        # Tool card zone end
        if self._in_tool_card and self._depth == self._tool_card_depth:
            self._in_tool_card = False
            if self._tool_card_has_rating:
                self.tool_card_ratings.append({
                    "links": list(self._tool_card_links),
                    "has_rating": True,
                })

        # Pop zone stack
        while self._zone_stack and self._zone_stack[-1][2] >= self._depth:
            self._zone_stack.pop()

        self._depth -= 1

    def _handle_void(self, tag, attrs):
        if tag == "meta":
            name = self._get_attr(attrs, "name").lower()
            if name == "description":
                self.meta_desc = self._get_attr(attrs, "content")
        elif tag == "link":
            rel = self._get_attr(attrs, "rel").lower()
            if rel == "canonical":
                self.canonical = self._get_attr(attrs, "href")

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        if self._in_title:
            self.title += text
            return

        if self._in_script:
            self._script_buf += data
            return

        if self._in_header:
            self._header_text.append(text)

        if self._current_link_href is not None:
            self._current_link_text.append(text)

        if self._in_blockquote:
            self._blockquote_text.append(text)

        if self._in_sources_checked:
            self._sources_checked_raw.append(text)

        zone = self._current_zone()
        words = text.split()

        if zone != "boilerplate":
            self.all_content_text.extend(words)
            # Placeholder check
            if PLACEHOLDER_RE.search(text):
                self.placeholders_found.append(text[:80])
            # Track words since last H2 (for empty section detection)
            if self._last_h2_text is not None and not self._in_header:
                self._words_since_h2 += len(words)
            # Signal 2: Section word tracking (non-header content only)
            if self._section_header is not None and not self._in_header:
                self._section_words += len(words)
            # Signal 7: Content word counting
            self._content_word_count += len(words)

        if zone == "core-editorial":
            self.core_editorial_text.extend(words)
        elif zone == "tool-card":
            self.tool_card_text.extend(words)
        elif zone == "sources-checked":
            self.sources_checked_text.extend(words)

        self.text_by_zone[zone].extend(words)

        # Signal 4: Accumulate CE paragraph text
        if self._in_ce_para:
            self._ce_para_text += text + " "

        # Signal 9: Capture last-verified text
        if self._in_last_verified:
            self.last_verified_text += text + " "

    def finalize(self):
        """Call after feeding all HTML to check final sections."""
        if self._last_h2_text is not None and self._words_since_h2 < 10:
            self.empty_h2_sections.append(self._last_h2_text)

        # Signal 2: Finalize last section stats
        if self._section_header is not None:
            self.section_stats.append({
                "header": self._section_header,
                "level": self._section_level,
                "words": self._section_words,
                "has_rich_content": self._section_has_rich,
            })

        # Signal 2: Compute thin_sections from section_stats
        self.thin_sections = [
            s for s in self.section_stats
            if s["words"] < 40 and not s["has_rich_content"]
        ]

        # Signal 4: Finalize last CE paragraph
        if self._in_ce_para and self._ce_para_text.strip():
            self.core_editorial_paragraphs.append({
                "text": self._ce_para_text.strip(),
                "links": list(self._ce_para_links),
            })


def extract_page(html_content):
    """Parse HTML and return structured extraction."""
    ext = ContentExtractor()
    ext.feed(html_content)
    ext.finalize()
    return ext


# ---------------------------------------------------------------------------
# Page Type Detection
# ---------------------------------------------------------------------------

def detect_page_type(rel_path):
    """Determine page type from relative file path."""
    parts = rel_path.replace("\\", "/").split("/")

    # Homepage
    if rel_path == "index.html":
        return "homepage"

    # Static pages (privacy, terms)
    base = os.path.basename(rel_path)
    if base in STATIC_FILES:
        return "static_page"

    # Editorial (about, disclosure, etc.)
    if base in EDITORIAL_FILES:
        return "editorial"

    # Directory indexes
    if rel_path in ("tools/index.html", "compare/index.html",
                     "categories/index.html", "best/index.html",
                     "pricing/index.html", "alternatives/index.html",
                     "resources/index.html"):
        return "directory"

    # Reviews
    if rel_path.startswith("tools/"):
        if base.endswith("-review.html"):
            return "review"
        if len(parts) == 3 and parts[2] == "index.html":
            return "review"  # tools/slug/index.html

    # Comparisons
    if rel_path.startswith("compare/"):
        if base != "index.html":
            if len(parts) == 2:
                return "comparison"
            if len(parts) == 3 and parts[2] == "index.html":
                return "comparison"

    # Category hubs
    if rel_path.startswith("categories/"):
        if base != "index.html":
            if len(parts) == 2:
                return "category_hub"
            if len(parts) == 3 and parts[2] == "index.html":
                return "category_hub"

    # Best-of pages
    if rel_path.startswith("best/"):
        if base != "index.html":
            return "best_of"

    # Alternatives pages
    if rel_path.startswith("alternatives/"):
        if base != "index.html":
            return "alternatives"

    # Pricing pages
    if rel_path.startswith("pricing/"):
        if base != "index.html":
            return "pricing"

    # Resources
    if rel_path.startswith("resources/"):
        if base != "index.html":
            return "resource"

    return "editorial"  # fallback


# ---------------------------------------------------------------------------
# Canonical & URL helpers
# ---------------------------------------------------------------------------

def normalize_path(rel_path):
    """Normalize rel_path for canonical comparison.
    */index.html -> /path/  (not /path/index.html)
    Root index.html -> '' (just base_url/)
    *.html -> strip .html (pretty URLs)
    """
    if rel_path == "index.html":
        return ""
    if rel_path.endswith("/index.html"):
        return rel_path[:-len("index.html")]
    if rel_path.endswith(".html"):
        return rel_path[:-len(".html")]
    return rel_path


def sitemap_url_path(rel_path):
    """Normalize path for sitemap URLs (strip .html for pretty URLs)."""
    if rel_path == "index.html":
        return ""
    if rel_path.endswith("/index.html"):
        return rel_path[:-len("index.html")]
    if rel_path.endswith(".html"):
        return rel_path[:-len(".html")]
    return rel_path


def check_canonical(ext, rel_path, base_url):
    """Check self-referencing canonical. Returns (ok, expected, actual)."""
    norm = normalize_path(rel_path)
    expected = base_url.rstrip("/") + "/" + norm
    actual = ext.canonical.strip()
    if not actual:
        return False, expected, "(missing)"
    # Normalize trailing slashes for comparison
    exp_norm = expected.rstrip("/")
    act_norm = actual.rstrip("/")
    return exp_norm == act_norm, expected, actual


# ---------------------------------------------------------------------------
# Affiliate classification
# ---------------------------------------------------------------------------

def is_affiliate_link(href):
    if not href:
        return False
    if href.startswith("/go/") or "salesaiguide.com/go/" in href:
        return True
    return bool(AFFILIATE_RE.search(href))


# ---------------------------------------------------------------------------
# Sources-Checked Analysis
# ---------------------------------------------------------------------------

def analyze_sources_checked(ext):
    """Analyze the sources-checked module."""
    links = ext.sources_checked_links
    if not links:
        return {"count": 0, "domains": 0, "has_dates": False, "domain_list": []}

    domains = set()
    for href, _ in links:
        try:
            parsed = urlparse(href)
            if parsed.hostname:
                domains.add(parsed.hostname.replace("www.", ""))
        except Exception:
            pass

    raw_text = " ".join(ext._sources_checked_raw)
    has_dates = bool(DATE_PATTERN_RE.search(raw_text))

    return {
        "count": len(links),
        "domains": len(domains),
        "domain_list": sorted(domains),
        "has_dates": has_dates,
    }


SOURCES_HEADER_RE = re.compile(
    r"source|external review|reference|review.*walkthrough",
    re.IGNORECASE,
)


def check_claimed_sources(ext, sources):
    """Check if page headers claim sources but no valid module exists.
    Returns (has_claim, claim_header) — True if a header mentions sources
    but the sources-checked module has 0 links."""
    if sources["count"] > 0:
        return False, None  # Module exists and has links — no issue
    for level, text in ext.headers:
        if SOURCES_HEADER_RE.search(text):
            return True, text
    return False, None


# ---------------------------------------------------------------------------
# Internal Link Pattern Checks
# ---------------------------------------------------------------------------

def check_review_links(ext, rel_path):
    """Check internal link patterns for review pages. Returns (patterns_met, details)."""
    patterns = {"category": 0, "compare": 0, "other_review": 0}
    self_slug = os.path.basename(rel_path)  # e.g. instantly-review.html

    for href, zone, _ in ext.links:
        if zone == "boilerplate":
            continue
        # Normalize href
        h = href.replace("../", "").lstrip("/")
        full = href  # keep original for pattern matching

        if "/categories/" in href or h.startswith("categories/"):
            patterns["category"] += 1
        if "/compare/" in href or h.startswith("compare/"):
            patterns["compare"] += 1
        if ("/tools/" in href or h.startswith("tools/")) and "-review" in href:
            # Exclude self
            if self_slug not in href:
                patterns["other_review"] += 1

    met = 0
    if patterns["category"] >= 1:
        met += 1
    if patterns["compare"] >= 2:
        met += 1
    elif patterns["compare"] >= 1:
        met += 0  # need 2
    if patterns["other_review"] >= 2:
        met += 1
    # Total possible pattern groups: 3 (category, compare>=2, other_review>=2)
    # But plan says 5+ links total across patterns for A
    # Let's count matched link minimums
    details = patterns
    # Pattern count: how many of the 3 pattern types are fully met
    return met, details


def check_comparison_links(ext, rel_path):
    """Check internal link patterns for comparison pages."""
    # Try to infer tool slugs from filename
    base = os.path.basename(rel_path).replace(".html", "")
    # e.g. clay-vs-apollo -> tool_a=clay, tool_b=apollo
    parts = base.split("-vs-")
    tool_a = parts[0] if len(parts) == 2 else ""
    tool_b = parts[1] if len(parts) == 2 else ""

    patterns = {"tool_a_review": False, "tool_b_review": False,
                "category": 0, "other_compare": 0}

    for href, zone, _ in ext.links:
        if zone == "boilerplate":
            continue
        h = href.replace("../", "").lstrip("/")

        if tool_a and f"{tool_a}-review" in href:
            patterns["tool_a_review"] = True
        if tool_b and f"{tool_b}-review" in href:
            patterns["tool_b_review"] = True
        if "/categories/" in href or h.startswith("categories/"):
            patterns["category"] += 1
        if "/compare/" in href or h.startswith("compare/"):
            # Exclude self
            if base not in href:
                patterns["other_compare"] += 1

    met = 0
    if patterns["tool_a_review"]:
        met += 1
    if patterns["tool_b_review"]:
        met += 1
    if patterns["category"] >= 1:
        met += 1
    if patterns["other_compare"] >= 2:
        met += 1

    return met, patterns


# ---------------------------------------------------------------------------
# Similarity: 3-Shingle Jaccard
# ---------------------------------------------------------------------------

def build_shingles(words, n=3):
    """Build set of n-shingles from word list."""
    if len(words) < n:
        return set()
    lower = [w.lower() for w in words]
    return {tuple(lower[i:i + n]) for i in range(len(lower) - n + 1)}


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def infer_category(ext):
    """Infer category hub from first /categories/ link."""
    for href, zone, _ in ext.links:
        if zone == "boilerplate":
            continue
        if "/categories/" in href:
            # Normalize to just the category filename
            m = re.search(r"categories/([^/]+\.html)", href)
            if m:
                return m.group(1)
            m = re.search(r"categories/([^/]+)/?$", href)
            if m:
                return m.group(1)
    return None


def compute_similarity_clusters(pages_data):
    """Compute pairwise similarity within category clusters.
    pages_data: list of {file, page_type, ext, shingles, category}
    Returns: dict of file -> max_similarity, plus pairs list.
    """
    # Group into clusters
    clusters = defaultdict(list)
    for pd in pages_data:
        cat = pd.get("category")
        if cat:
            clusters[cat].append(pd)
        else:
            clusters[f"_type_{pd['page_type']}"].append(pd)

    max_sim = {}
    pairs = []
    for cluster_name, members in clusters.items():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                sim = jaccard(a["shingles"], b["shingles"])
                pairs.append({
                    "file_a": a["file"],
                    "file_b": b["file"],
                    "cluster": cluster_name,
                    "similarity": round(sim, 4),
                })
                max_sim[a["file"]] = max(max_sim.get(a["file"], 0), sim)
                max_sim[b["file"]] = max(max_sim.get(b["file"], 0), sim)

    return max_sim, pairs


# ---------------------------------------------------------------------------
# Schema checks
# ---------------------------------------------------------------------------

def has_aggregate_rating(ext):
    for schema in ext.json_ld:
        if _schema_has_type(schema, "AggregateRating"):
            return True
    return False


def _schema_has_type(obj, type_name):
    if isinstance(obj, dict):
        if obj.get("@type") == type_name:
            return True
        for v in obj.values():
            if _schema_has_type(v, type_name):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _schema_has_type(item, type_name):
                return True
    return False


# ---------------------------------------------------------------------------
# Directory reviewed-vs-listed check
# ---------------------------------------------------------------------------

def check_directory_listings(ext, site_dir):
    """Check that listed-only tools don't show ratings."""
    issues = []
    for card in ext.tool_card_ratings:
        # A card has rating markup. Check if ANY link in the card
        # points to an existing review page.
        has_review = False
        for href in card["links"]:
            h = href.replace("../", "").lstrip("/")
            # Direct review link check
            if "-review" in h:
                path = os.path.join(site_dir, h)
                if os.path.exists(path):
                    has_review = True
                    break
            # Try slug-based resolution for /go/ links, category links, etc.
            slug = h.replace("tools/", "").replace("-review.html", "").replace(".html", "")
            slug = slug.split("/")[-1]  # Get the last segment
            path2 = os.path.join(site_dir, "tools", slug + "-review.html")
            path3 = os.path.join(site_dir, "tools", slug + "-review", "index.html")
            if os.path.exists(path2) or os.path.exists(path3):
                has_review = True
                break
        if not has_review:
            # Report the first link as identifier
            first_link = card["links"][0] if card["links"] else "unknown"
            issues.append(f"Rating shown for unreviewed tool: {first_link}")
    return issues


# ---------------------------------------------------------------------------
# Editorial scaffolding check
# ---------------------------------------------------------------------------

SCAFFOLDING_TARGETS = [
    "about.html#methodology",
    "about.html#editorial",
    "disclosure.html",
    "about.html#corrections",
]


def count_scaffolding_links(ext):
    """Count how many of the 4 editorial scaffolding links are present."""
    found = 0
    for href, _, _ in ext.links:
        for target in SCAFFOLDING_TARGETS:
            if target in href:
                found += 1
                break
    return min(found, 4)


# ---------------------------------------------------------------------------
# Slop Linter Helper Functions
# ---------------------------------------------------------------------------

def check_numeric_claims(ext):
    """Signal 4: Scan core-editorial paragraphs for unsourced numeric claims.
    Returns list of {"claim": str, "paragraph_excerpt": str}.
    """
    unsourced = []
    for para in ext.core_editorial_paragraphs:
        text = para["text"]
        links = para["links"]  # list of (char_position, href)

        # Find all numeric claims
        for m in NUMERIC_CLAIM_RE.finditer(text):
            claim_text = m.group()
            claim_pos = m.start()

            # Check if this match is part of an excluded date/version pattern
            excluded = False
            for dm in DATE_EXCLUDE_RE.finditer(text):
                if dm.start() <= claim_pos < dm.end():
                    excluded = True
                    break
            if excluded:
                continue

            # Check for external citation link in same paragraph or within 200 chars
            has_cite = False
            for link_pos, href in links:
                if href.startswith("https://") and "/go/" not in href:
                    # Link is within paragraph — close enough
                    if abs(link_pos - claim_pos) <= 200 or link_pos >= 0:
                        has_cite = True
                        break
            if not has_cite:
                unsourced.append({
                    "claim": claim_text,
                    "paragraph_excerpt": text[:100],
                })
    return unsourced


def check_hype_density(ext):
    """Signal 6: Compute hype word density over content text.
    Returns (density, flagged_words).
    """
    content = ext.all_content_text
    if not content:
        return 0.0, []

    total = len(content)
    flagged = []
    count = 0
    for w in content:
        lower = w.lower().strip(".,;:!?\"'()[]")
        if lower in HYPE_WORDS:
            count += 1
            if lower not in flagged:
                flagged.append(lower)

    # Also check bigrams for hyphenated hype words
    for i in range(len(content) - 1):
        bigram = content[i].lower().strip(".,;:!?\"'()[]") + "-" + content[i + 1].lower().strip(".,;:!?\"'()[]")
        if bigram in HYPE_WORDS:
            count += 1
            if bigram not in flagged:
                flagged.append(bigram)

    density = count / total if total else 0.0
    return density, flagged


def check_conversion_first(ext):
    """Signal 7: Check /go/ link placement.
    Returns (is_fail, detail_str).
    """
    reasons = []

    # Rule 1: /go/ inside core-editorial blocks
    if ext.go_links_in_core_editorial:
        reasons.append(f"/go/ in core-editorial: {ext.go_links_in_core_editorial[0]}")

    # Rule 2: /go/ before verdict outside allowed zones
    verdict_pos = ext.verdict_word_position
    if verdict_pos is not None:
        for offset, href, zone in ext.go_link_word_positions:
            if offset < verdict_pos and zone not in ("allowed",):
                reasons.append(f"/go/ at word {offset} before verdict at {verdict_pos}: {href}")
                break

    # Rule 3: ≥2 /go/ in first 300 content words excluding allowed zones
    early_non_allowed = [
        (off, href) for off, href, zone in ext.go_link_word_positions
        if off < 300 and zone != "allowed"
    ]
    if len(early_non_allowed) >= 2:
        reasons.append(f"{len(early_non_allowed)} /go/ links in first 300 words outside allowed zones")

    if reasons:
        return True, "; ".join(reasons)
    return False, ""


def check_intro_similarity(page_data, cluster_pages):
    """Signal 5: 200-word intro similarity with tool name normalization.
    Returns {"max_sim": float, "paired_with": str} or None if no cluster peers.
    """
    page_type = page_data["page_type"]
    rel_path = page_data["file"]

    # Get first 200 content words
    ext = page_data["ext"]
    intro_words = list(ext.all_content_text[:200])
    if len(intro_words) < 20:
        return None  # Too short to compare

    # Infer tool names from filename for normalization
    base = os.path.basename(rel_path).replace(".html", "")
    if page_type == "review":
        tool_name = base.replace("-review", "").lower()
        # Normalize: replace tool name variants with TOOL
        intro_lower = [w.lower() for w in intro_words]
        normalized = []
        for w in intro_lower:
            if tool_name in w:
                normalized.append("TOOL")
            else:
                normalized.append(w)
    elif page_type == "comparison":
        parts = base.split("-vs-")
        tool_a = parts[0].lower() if len(parts) == 2 else ""
        tool_b = parts[1].lower() if len(parts) == 2 else ""
        intro_lower = [w.lower() for w in intro_words]
        normalized = []
        for w in intro_lower:
            if tool_a and tool_a in w:
                normalized.append("TOOL_A")
            elif tool_b and tool_b in w:
                normalized.append("TOOL_B")
            else:
                normalized.append(w)
    else:
        normalized = [w.lower() for w in intro_words]

    my_shingles = build_shingles(normalized)
    if not my_shingles:
        return None

    max_sim = 0.0
    paired_with = ""

    for peer in cluster_pages:
        if peer["file"] == rel_path:
            continue
        # Get peer's first 200 words, normalized
        peer_ext = peer["ext"]
        peer_intro = list(peer_ext.all_content_text[:200])
        if len(peer_intro) < 20:
            continue

        peer_base = os.path.basename(peer["file"]).replace(".html", "")
        if peer["page_type"] == "review":
            peer_tool = peer_base.replace("-review", "").lower()
            peer_norm = []
            for w in peer_intro:
                wl = w.lower()
                if peer_tool in wl:
                    peer_norm.append("TOOL")
                else:
                    peer_norm.append(wl)
        elif peer["page_type"] == "comparison":
            pp = peer_base.split("-vs-")
            pa = pp[0].lower() if len(pp) == 2 else ""
            pb = pp[1].lower() if len(pp) == 2 else ""
            peer_norm = []
            for w in peer_intro:
                wl = w.lower()
                if pa and pa in wl:
                    peer_norm.append("TOOL_A")
                elif pb and pb in wl:
                    peer_norm.append("TOOL_B")
                else:
                    peer_norm.append(wl)
        else:
            peer_norm = [w.lower() for w in peer_intro]

        peer_shingles = build_shingles(peer_norm)
        if not peer_shingles:
            continue

        sim = jaccard(my_shingles, peer_shingles)
        if sim > max_sim:
            max_sim = sim
            paired_with = peer["file"]

    if max_sim > 0:
        return {"max_sim": round(max_sim, 4), "paired_with": paired_with}
    return None


def check_last_verified(ext, today=None):
    """Signal 9: Parse last-verified date.
    Returns (days_old_or_None, date_str_or_None, tier).
    tier: 'A' = eligible for A, 'B' = cap at B, 'C' = force C.
    today param allows injectable date for time-stable tests.
    """
    text = ext.last_verified_text.strip()
    if not text:
        return None, None, "C"

    # Parse "Last verified: Mon YYYY" or "Last verified: Month YYYY"
    # Also handle just "Feb 2026" without prefix
    date_match = re.search(
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)\s+(\d{4})",
        text, re.IGNORECASE,
    )
    if not date_match:
        return None, text, "C"

    month_str = date_match.group().split()[0].lower()
    year = int(date_match.group(1))
    month = MONTH_NAMES.get(month_str, None)
    if not month:
        return None, text, "C"

    if today is None:
        today = datetime.utcnow().date()

    try:
        verified_date = datetime(year, month, 1).date()
    except (ValueError, OverflowError):
        return None, text, "C"

    days_old = (today - verified_date).days

    if days_old <= LAST_VERIFIED_A_MAX:
        tier = "A"
    elif days_old <= LAST_VERIFIED_B_MAX:
        tier = "B"
    else:
        tier = "C"

    date_str = f"{date_match.group()}"
    return days_old, date_str, tier


# ---------------------------------------------------------------------------
# Per-Type Grading
# ---------------------------------------------------------------------------

def grade_review(ext, rel_path, base_url, site_dir, max_sim):
    """Grade a review page. Returns (grade, checks)."""
    checks = {}

    content_words = len(ext.all_content_text)
    checks["content_words"] = content_words

    # Tool-specific words: core-editorial or all content minus boilerplate
    editorial_words = len(ext.core_editorial_text) if ext.core_editorial_text else content_words
    checks["editorial_words"] = editorial_words

    checks["has_pricing"] = ext.has_pricing
    checks["has_pros_cons"] = ext.has_pros_cons
    checks["has_verdict"] = ext.has_verdict
    checks["verdict_in_details"] = ext.verdict_in_details
    checks["has_aggregate_rating"] = has_aggregate_rating(ext)
    checks["placeholders"] = ext.placeholders_found
    checks["has_scenario"] = ext.has_scenario
    checks["has_gotcha"] = ext.has_gotcha
    checks["empty_h2_sections"] = ext.empty_h2_sections

    scaffolding = count_scaffolding_links(ext)
    checks["scaffolding_links"] = scaffolding

    sources = analyze_sources_checked(ext)
    checks["sources_checked"] = sources

    claimed, claimed_header = check_claimed_sources(ext, sources)
    checks["claimed_sources_no_module"] = claimed
    checks["claimed_sources_header"] = claimed_header

    link_patterns, link_details = check_review_links(ext, rel_path)
    checks["internal_link_patterns"] = link_patterns
    checks["internal_link_details"] = link_details

    canon_ok, canon_exp, canon_act = check_canonical(ext, rel_path, base_url)
    checks["canonical_ok"] = canon_ok
    checks["canonical_expected"] = canon_exp
    checks["canonical_actual"] = canon_act

    sim = max_sim.get(rel_path, 0)
    checks["max_similarity"] = round(sim, 4)

    # Grade
    hard_fail = False
    fail_reasons = []

    if ext.empty_h2_sections:
        hard_fail = True
        fail_reasons.append(f"empty H2 sections: {ext.empty_h2_sections}")
    if not ext.has_verdict:
        hard_fail = True
        fail_reasons.append("missing verdict")
    if ext.verdict_in_details:
        hard_fail = True
        fail_reasons.append("verdict hidden in <details>")
    if has_aggregate_rating(ext):
        hard_fail = True
        fail_reasons.append("AggregateRating in schema")
    if ext.placeholders_found:
        hard_fail = True
        fail_reasons.append(f"placeholders found: {ext.placeholders_found[0]}")
    if not canon_ok:
        hard_fail = True
        fail_reasons.append(f"canonical mismatch: {canon_act}")
    if editorial_words < 350:
        hard_fail = True
        fail_reasons.append(f"editorial words {editorial_words} < 350")
    if sources["count"] < 3:
        hard_fail = True
        fail_reasons.append(f"sources-checked {sources['count']} < 3")
    if claimed:
        hard_fail = True
        fail_reasons.append(f"claimed sources without valid module: '{claimed_header}'")
    if sources["domains"] < 2:
        hard_fail = True
        fail_reasons.append(f"source domain diversity {sources['domains']} < 2")
    if scaffolding < 3:
        hard_fail = True
        fail_reasons.append(f"scaffolding links {scaffolding} < 3")
    if link_patterns < 2:
        hard_fail = True
        fail_reasons.append(f"internal link patterns {link_patterns} < 2")
    if sim >= 0.25:
        hard_fail = True
        fail_reasons.append(f"similarity {sim:.2f} >= 0.25")

    if hard_fail:
        checks["fail_reasons"] = fail_reasons
        return "C", checks

    # Check for A
    is_a = (
        content_words >= 1500
        and editorial_words >= 500
        and ext.has_pricing and ext.has_pros_cons
        and scaffolding == 4
        and sources["count"] >= 6
        and sources["domains"] >= 4
        and sources["has_dates"]
        and link_patterns >= 3
        and sim < 0.15
        and ext.has_scenario
        and ext.has_gotcha
    )

    return "A" if is_a else "B", checks


def grade_comparison(ext, rel_path, base_url, site_dir, max_sim):
    """Grade a comparison page."""
    checks = {}

    content_words = len(ext.all_content_text)
    checks["content_words"] = content_words

    editorial_words = len(ext.core_editorial_text) if ext.core_editorial_text else content_words
    checks["editorial_words"] = editorial_words

    checks["has_comparison_table"] = ext.has_comparison_table
    checks["has_verdict"] = ext.has_verdict
    checks["verdict_in_details"] = ext.verdict_in_details
    checks["has_aggregate_rating"] = has_aggregate_rating(ext)
    checks["placeholders"] = ext.placeholders_found
    checks["empty_h2_sections"] = ext.empty_h2_sections

    scaffolding = count_scaffolding_links(ext)
    checks["scaffolding_links"] = scaffolding

    sources = analyze_sources_checked(ext)
    checks["sources_checked"] = sources

    claimed, claimed_header = check_claimed_sources(ext, sources)
    checks["claimed_sources_no_module"] = claimed
    checks["claimed_sources_header"] = claimed_header

    link_patterns, link_details = check_comparison_links(ext, rel_path)
    checks["internal_link_patterns"] = link_patterns
    checks["internal_link_details"] = link_details

    canon_ok, canon_exp, canon_act = check_canonical(ext, rel_path, base_url)
    checks["canonical_ok"] = canon_ok
    checks["canonical_expected"] = canon_exp
    checks["canonical_actual"] = canon_act

    sim = max_sim.get(rel_path, 0)
    checks["max_similarity"] = round(sim, 4)

    # Hard fails
    hard_fail = False
    fail_reasons = []

    if ext.empty_h2_sections:
        hard_fail = True
        fail_reasons.append(f"empty H2 sections: {ext.empty_h2_sections}")
    if not ext.has_comparison_table:
        hard_fail = True
        fail_reasons.append("missing comparison table")
    if not ext.has_verdict:
        hard_fail = True
        fail_reasons.append("missing verdict")
    if ext.verdict_in_details:
        hard_fail = True
        fail_reasons.append("verdict hidden in <details>")
    if has_aggregate_rating(ext):
        hard_fail = True
        fail_reasons.append("AggregateRating in schema")
    if ext.placeholders_found:
        hard_fail = True
        fail_reasons.append(f"placeholders: {ext.placeholders_found[0]}")
    if not canon_ok:
        hard_fail = True
        fail_reasons.append(f"canonical mismatch: {canon_act}")
    if content_words < 600:
        hard_fail = True
        fail_reasons.append(f"content words {content_words} < 600")
    if editorial_words < 300:
        hard_fail = True
        fail_reasons.append(f"editorial words {editorial_words} < 300")
    if sources["count"] < 4:
        hard_fail = True
        fail_reasons.append(f"sources-checked {sources['count']} < 4")
    if claimed:
        hard_fail = True
        fail_reasons.append(f"claimed sources without valid module: '{claimed_header}'")
    if sources["domains"] < 2:
        hard_fail = True
        fail_reasons.append(f"source domain diversity {sources['domains']} < 2")
    if scaffolding < 3:
        hard_fail = True
        fail_reasons.append(f"scaffolding links {scaffolding} < 3")
    if link_patterns < 2:
        hard_fail = True
        fail_reasons.append(f"internal link patterns {link_patterns} < 2")
    if sim >= 0.30:
        hard_fail = True
        fail_reasons.append(f"similarity {sim:.2f} >= 0.30")

    if hard_fail:
        checks["fail_reasons"] = fail_reasons
        return "C", checks

    is_a = (
        content_words >= 1200
        and editorial_words >= 600
        and scaffolding == 4
        and sources["count"] >= 8
        and sources["domains"] >= 4
        and sources["has_dates"]
        and link_patterns >= 4
        and sim < 0.20
    )

    return "A" if is_a else "B", checks


def grade_category_hub(ext, rel_path, base_url, max_sim):
    """Grade a category hub page."""
    checks = {}

    # Editorial words = content words minus tool-card text
    total_content = len(ext.all_content_text)
    tool_card_words = len(ext.tool_card_text)
    editorial_words = total_content - tool_card_words
    checks["content_words"] = total_content
    checks["editorial_words"] = editorial_words
    checks["tool_card_count"] = ext.tool_card_count
    checks["placeholders"] = ext.placeholders_found
    checks["empty_h2_sections"] = ext.empty_h2_sections
    checks["has_consider"] = ext.has_consider
    checks["has_failure"] = ext.has_failure
    checks["has_bestpick"] = ext.has_bestpick

    # Internal links (non-boilerplate)
    internal_links = 0
    for href, zone, _ in ext.links:
        if zone == "boilerplate":
            continue
        if ("/tools/" in href or "/compare/" in href or
                href.startswith("../tools/") or href.startswith("../compare/")):
            internal_links += 1
    checks["internal_links"] = internal_links

    canon_ok, canon_exp, canon_act = check_canonical(ext, rel_path, base_url)
    checks["canonical_ok"] = canon_ok
    checks["canonical_expected"] = canon_exp
    checks["canonical_actual"] = canon_act

    # Hard fails
    hard_fail = False
    fail_reasons = []

    if ext.empty_h2_sections:
        hard_fail = True
        fail_reasons.append(f"empty H2 sections: {ext.empty_h2_sections}")
    if editorial_words < 100:
        hard_fail = True
        fail_reasons.append(f"editorial words {editorial_words} < 100")
    if ext.tool_card_count < 3:
        hard_fail = True
        fail_reasons.append(f"tools listed {ext.tool_card_count} < 3")
    if ext.placeholders_found:
        hard_fail = True
        fail_reasons.append(f"placeholders: {ext.placeholders_found[0]}")
    if not canon_ok:
        hard_fail = True
        fail_reasons.append(f"canonical mismatch: {canon_act}")
    if internal_links < 2:
        hard_fail = True
        fail_reasons.append(f"internal links {internal_links} < 2")

    if hard_fail:
        checks["fail_reasons"] = fail_reasons
        return "C", checks

    is_a = (
        editorial_words >= 900
        and ext.tool_card_count >= 5
        and ext.has_consider
        and ext.has_failure
        and ext.has_bestpick
        and internal_links >= 8
        and canon_ok
    )

    if is_a:
        return "A", checks

    is_b = (
        editorial_words >= 400
        and ext.tool_card_count >= 3
        and internal_links >= 4
    )

    return "B" if is_b else "C", checks


def grade_directory(ext, rel_path, base_url, site_dir):
    """Grade a directory page."""
    checks = {}

    editorial_words = len(ext.all_content_text) - len(ext.tool_card_text)
    checks["editorial_words"] = editorial_words
    checks["placeholders"] = ext.placeholders_found
    checks["empty_h2_sections"] = ext.empty_h2_sections

    # Internal links
    internal_links = 0
    for href, zone, _ in ext.links:
        if zone == "boilerplate":
            continue
        h = href.replace("../", "").lstrip("/")
        if h.startswith("tools/") or h.startswith("compare/") or h.startswith("categories/"):
            internal_links += 1
    checks["internal_links"] = internal_links

    # Reviewed vs Listed
    listing_issues = check_directory_listings(ext, site_dir)
    checks["listing_issues"] = listing_issues

    canon_ok, canon_exp, canon_act = check_canonical(ext, rel_path, base_url)
    checks["canonical_ok"] = canon_ok
    checks["canonical_expected"] = canon_exp
    checks["canonical_actual"] = canon_act

    hard_fail = False
    fail_reasons = []

    if ext.empty_h2_sections:
        hard_fail = True
        fail_reasons.append(f"empty H2 sections: {ext.empty_h2_sections}")
    if editorial_words < 50:
        hard_fail = True
        fail_reasons.append(f"editorial words {editorial_words} < 50")
    if ext.placeholders_found:
        hard_fail = True
        fail_reasons.append(f"placeholders: {ext.placeholders_found[0]}")
    if not canon_ok:
        hard_fail = True
        fail_reasons.append(f"canonical mismatch: {canon_act}")
    if internal_links < 3:
        hard_fail = True
        fail_reasons.append(f"internal links {internal_links} < 3")
    if listing_issues:
        hard_fail = True
        fail_reasons.extend(listing_issues)

    if hard_fail:
        checks["fail_reasons"] = fail_reasons
        return "C", checks

    is_a = (
        editorial_words >= 200
        and internal_links >= 10
        and not listing_issues
    )

    if is_a:
        return "A", checks

    is_b = editorial_words >= 100 and internal_links >= 5

    return "B" if is_b else "C", checks


def grade_editorial(ext, rel_path, base_url):
    """Grade editorial / homepage."""
    checks = {}

    content_words = len(ext.all_content_text)
    checks["content_words"] = content_words
    checks["placeholders"] = ext.placeholders_found
    checks["empty_h2_sections"] = ext.empty_h2_sections

    canon_ok, canon_exp, canon_act = check_canonical(ext, rel_path, base_url)
    checks["canonical_ok"] = canon_ok
    checks["canonical_expected"] = canon_exp
    checks["canonical_actual"] = canon_act

    hard_fail = False
    fail_reasons = []

    if ext.empty_h2_sections:
        hard_fail = True
        fail_reasons.append(f"empty H2 sections: {ext.empty_h2_sections}")
    if content_words < 50:
        hard_fail = True
        fail_reasons.append(f"content words {content_words} < 50")
    if ext.placeholders_found:
        hard_fail = True
        fail_reasons.append(f"placeholders: {ext.placeholders_found[0]}")
    if not canon_ok:
        hard_fail = True
        fail_reasons.append(f"canonical mismatch: {canon_act}")

    if hard_fail:
        checks["fail_reasons"] = fail_reasons
        return "C", checks

    is_a = content_words >= 200 and canon_ok
    is_b = content_words >= 100

    if is_a:
        return "A", checks
    return "B" if is_b else "C", checks


# ---------------------------------------------------------------------------
# Slop Lint Pass
# ---------------------------------------------------------------------------

def slop_lint_pass(results, all_pages):
    """Post-grade slop filter. Only applies to review + comparison pages.
    A + slop → C (and triggers exit 2). B + slop → C. C → unchanged.
    Returns list of downgrade dicts: {"file", "from", "to", "signals"}.
    """
    downgrades = []

    # Build cluster lookup for intro similarity
    # Group by category (same logic as similarity computation)
    clusters = defaultdict(list)
    for p in all_pages:
        if p["page_type"] in SLOP_APPLICABLE_TYPES:
            cat = p.get("category")
            key = cat if cat else f"_type_{p['page_type']}"
            clusters[key].append(p)

    # Build page lookup from all_pages
    page_lookup = {p["file"]: p for p in all_pages}

    for r in results:
        if r["page_type"] not in SLOP_APPLICABLE_TYPES:
            continue
        if r["grade"] == "C":
            continue  # Already noindex, skip

        ext = r.get("_ext")
        if ext is None:
            continue

        signals = []

        # Signal 2: Thin sections
        if ext.thin_sections:
            thin_names = [s["header"] for s in ext.thin_sections[:3]]
            signals.append(f"thin_sections: {thin_names}")

        # Signal 3: Unsourced blockquotes
        unsourced_bq = [bq for bq in ext.blockquotes if not bq.get("has_external_cite", False)]
        if unsourced_bq:
            signals.append(f"unsourced_blockquotes: {len(unsourced_bq)}")

        # Signal 4: Unsourced numeric claims
        unsourced_claims = check_numeric_claims(ext)
        if unsourced_claims:
            claims_str = ", ".join(c["claim"] for c in unsourced_claims[:3])
            signals.append(f"unsourced_numeric_claims: [{claims_str}]")

        # Signal 5: Over-templated intros
        page_data = page_lookup.get(r["file"])
        if page_data:
            cat = page_data.get("category")
            cluster_key = cat if cat else f"_type_{page_data['page_type']}"
            cluster_members = clusters.get(cluster_key, [])
            if len(cluster_members) > 1:
                intro_result = check_intro_similarity(page_data, cluster_members)
                if intro_result and intro_result["max_sim"] > 0.25:
                    signals.append(
                        f"intro_similarity: {intro_result['max_sim']:.2f} with {intro_result['paired_with']}"
                    )

        # Signal 6: Hype word density
        density, flagged = check_hype_density(ext)
        if density > HYPE_DENSITY_THRESHOLD:
            signals.append(f"hype_density: {density:.3f} ({', '.join(flagged[:5])})")

        # Signal 7: Conversion-first layout
        conv_fail, conv_detail = check_conversion_first(ext)
        if conv_fail:
            signals.append(f"conversion_first: {conv_detail}")

        # Signal 9: Last verified date
        days_old, date_str, tier = check_last_verified(ext)
        if tier == "C":
            signals.append(f"last_verified: missing or stale ({date_str or 'not found'})")
        elif tier == "B" and r["grade"] == "A":
            signals.append(f"last_verified: {days_old}d old, caps at B ({date_str})")

        # Apply downgrades
        if signals:
            old_grade = r["grade"]
            r["grade"] = "C"
            r["checks"]["slop_signals"] = signals
            r["checks"].setdefault("fail_reasons", []).extend(
                [f"slop: {s}" for s in signals]
            )
            downgrades.append({
                "file": r["file"],
                "from": old_grade,
                "to": "C",
                "signals": signals,
            })
        elif tier == "B" and r["grade"] == "A":
            # Last verified caps at B but doesn't trigger slop downgrade to C
            r["grade"] = "B"
            r["checks"]["last_verified_cap"] = f"{days_old}d old, capped at B"
            downgrades.append({
                "file": r["file"],
                "from": "A",
                "to": "B",
                "signals": [f"last_verified: {days_old}d old, caps at B ({date_str})"],
            })

    return downgrades


# ---------------------------------------------------------------------------
# Global Uniqueness Checks
# ---------------------------------------------------------------------------

def check_global_uniqueness(all_pages):
    """Check title and meta description uniqueness across all pages."""
    titles = defaultdict(list)
    metas = defaultdict(list)

    for p in all_pages:
        t = p["ext"].title.strip()
        m = p["ext"].meta_desc.strip()
        if t:
            titles[t].append(p["file"])
        if m:
            metas[m].append(p["file"])

    dup_titles = {t: files for t, files in titles.items() if len(files) > 1}
    dup_metas = {m: files for m, files in metas.items() if len(files) > 1}

    return dup_titles, dup_metas


# ---------------------------------------------------------------------------
# Output Generation
# ---------------------------------------------------------------------------

def generate_sitemap_core(results, base_url, out_dir, site_dir=None):
    """Generate sitemap-core.xml with A+B pages."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for r in sorted(results, key=lambda x: x["file"]):
        if r["grade"] in ("A", "B"):
            norm = sitemap_url_path(r["file"])
            url = base_url.rstrip("/") + "/" + norm
            priority = PRIORITY_MAP.get(r["page_type"], "0.5")
            changefreq = CHANGEFREQ_MAP.get(r["page_type"], "monthly")
            # Use actual file modification date for lastmod
            lastmod = datetime.utcnow().strftime("%Y-%m-%d")
            if site_dir:
                fpath = os.path.join(site_dir, r["file"])
                if os.path.exists(fpath):
                    mtime = os.path.getmtime(fpath)
                    lastmod = datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%d")
            lines.append("  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
            lines.append(f"    <priority>{priority}</priority>")
            lines.append("  </url>")

    lines.append("</urlset>")

    path = os.path.join(out_dir, "sitemap-core.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def generate_sitemap_hold(results, base_url, out_dir, site_dir=None):
    """Generate sitemap-hold.xml with C pages (monitoring only)."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for r in sorted(results, key=lambda x: x["file"]):
        if r["grade"] == "C":
            norm = sitemap_url_path(r["file"])
            url = base_url.rstrip("/") + "/" + norm
            changefreq = CHANGEFREQ_MAP.get(r["page_type"], "monthly")
            lastmod = datetime.utcnow().strftime("%Y-%m-%d")
            if site_dir:
                fpath = os.path.join(site_dir, r["file"])
                if os.path.exists(fpath):
                    mtime = os.path.getmtime(fpath)
                    lastmod = datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%d")
            lines.append("  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
            lines.append("    <priority>0.1</priority>")
            lines.append("  </url>")

    lines.append("</urlset>")

    path = os.path.join(out_dir, "sitemap-hold.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def generate_sitemap_index(base_url, out_dir):
    """Generate sitemap.xml index referencing sitemap-core.xml ONLY."""
    now = datetime.utcnow().strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append("  <sitemap>")
    lines.append(f"    <loc>{base_url.rstrip('/')}/sitemap-core.xml</loc>")
    lines.append(f"    <lastmod>{now}</lastmod>")
    lines.append("  </sitemap>")
    lines.append("</sitemapindex>")

    path = os.path.join(out_dir, "sitemap.xml")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def generate_headers(results, out_dir):
    """Generate / merge _headers with noindex for C-tier pages."""
    headers_path = os.path.join(out_dir, "_headers")
    existing = ""
    if os.path.exists(headers_path):
        with open(headers_path) as f:
            existing = f.read()

    marker_start = "# --- BEGIN indexation_gate ---"
    marker_end = "# --- END indexation_gate ---"

    if marker_start in existing:
        before = existing[:existing.index(marker_start)]
        after_idx = existing.index(marker_end) + len(marker_end)
        existing = before + existing[after_idx:]

    lines = [marker_start]
    for r in sorted(results, key=lambda x: x["file"]):
        if r["grade"] == "C":
            path = r["file"]
            lines.append(f"/{path}")
            lines.append("  X-Robots-Tag: noindex, follow")
            if path.endswith("/index.html"):
                dir_path = path[: -len("index.html")]
                lines.append(f"/{dir_path}")
                lines.append("  X-Robots-Tag: noindex, follow")
    lines.append(marker_end)

    with open(headers_path, "w") as f:
        f.write(existing.rstrip() + "\n\n" + "\n".join(lines) + "\n")
    return headers_path


def generate_report(results, similarity_pairs, dup_titles, dup_metas, out_dir,
                    slop_downgrades=None):
    """Generate gate-report.json."""
    report = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total": len(results),
            "A": sum(1 for r in results if r["grade"] == "A"),
            "B": sum(1 for r in results if r["grade"] == "B"),
            "C": sum(1 for r in results if r["grade"] == "C"),
        },
        "pages": [],
        "similarity_pairs": similarity_pairs,
        "duplicate_titles": {t: files for t, files in dup_titles.items()},
        "duplicate_metas": {m: files for m, files in dup_metas.items()},
        "slop_downgrades": slop_downgrades or [],
    }

    for r in sorted(results, key=lambda x: x["file"]):
        page = {
            "file": r["file"],
            "page_type": r["page_type"],
            "grade": r["grade"],
            "title": r["title"],
            "checks": r["checks"],
        }
        report["pages"].append(page)

    path = os.path.join(out_dir, "gate-report.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def print_summary(results, similarity_pairs, dup_titles, dup_metas,
                  slop_downgrades=None):
    """Print human-readable summary to stdout."""
    a = sum(1 for r in results if r["grade"] == "A")
    b = sum(1 for r in results if r["grade"] == "B")
    c = sum(1 for r in results if r["grade"] == "C")

    print("=" * 60)
    print("  SalesAIGuide Indexation Gate Report")
    print("=" * 60)
    print(f"\n  Total pages: {len(results)}")
    print(f"  A (flagship):  {a}")
    print(f"  B (indexed):   {b}")
    print(f"  C (noindex):   {c}")

    print(f"\n  sitemap-core.xml: {a + b} pages")
    print(f"  sitemap-hold.xml: {c} pages (monitoring only)")

    # By type
    by_type = defaultdict(list)
    for r in results:
        by_type[r["page_type"]].append(r)

    print("\n--- By Page Type ---")
    for ptype in ["homepage", "editorial", "review", "comparison",
                  "category_hub", "directory"]:
        pages = by_type.get(ptype, [])
        if not pages:
            continue
        grades = [r["grade"] for r in pages]
        print(f"\n  {ptype} ({len(pages)} pages):")
        for r in sorted(pages, key=lambda x: x["file"]):
            grade = r["grade"]
            marker = "  " if grade != "C" else "!!"
            fail = ""
            if "fail_reasons" in r["checks"]:
                fail = " -- " + "; ".join(r["checks"]["fail_reasons"][:3])
            print(f"    {marker} [{grade}] {r['file']}{fail}")

    # Similarity
    if similarity_pairs:
        high = [p for p in similarity_pairs if p["similarity"] >= 0.15]
        if high:
            print("\n--- High Similarity Pairs ---")
            for p in sorted(high, key=lambda x: -x["similarity"]):
                print(f"    {p['similarity']:.2f}  {p['file_a']}  <->  {p['file_b']}  [{p['cluster']}]")

    # Duplicates
    if dup_titles:
        print("\n--- Duplicate Titles ---")
        for t, files in dup_titles.items():
            print(f"    \"{t[:60]}...\"")
            for f in files:
                print(f"      - {f}")

    if dup_metas:
        print("\n--- Duplicate Meta Descriptions ---")
        for m, files in dup_metas.items():
            print(f"    \"{m[:60]}...\"")
            for f in files:
                print(f"      - {f}")

    # Slop lint results
    if slop_downgrades:
        print("\n--- Slop Lint ---")
        for d in slop_downgrades:
            print(f"    {d['from']} → {d['to']}  {d['file']}")
            for s in d["signals"]:
                print(f"        • {s}")
    else:
        print("\n--- Slop Lint ---")
        print("    No slop signals detected.")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_html_files(site_dir):
    """Recursively find all .html files under site_dir."""
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden dirs and scripts/docs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("scripts", "docs", "node_modules")]
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, site_dir).replace("\\", "/")
                html_files.append(rel)
    return sorted(html_files)


def main():
    parser = argparse.ArgumentParser(description="SalesAIGuide Indexation Gate")
    parser.add_argument("--site-dir", default=".", help="Site root directory")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: site-dir)")
    parser.add_argument("--base-url", default="https://salesaiguide.com", help="Base URL")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files")
    parser.add_argument("--format", choices=["text", "json", "both"], default="both")
    args = parser.parse_args()

    site_dir = os.path.abspath(args.site_dir)
    # Auto-detect _site/ subdir
    site_subdir = os.path.join(site_dir, "_site")
    if os.path.isdir(site_subdir):
        site_dir = site_subdir

    out_dir = os.path.abspath(args.out_dir) if args.out_dir else site_dir
    base_url = args.base_url.rstrip("/")

    # 1. Find all HTML files
    html_files = find_html_files(site_dir)
    if not html_files:
        print(f"ERROR: No HTML files found in {site_dir}", file=sys.stderr)
        sys.exit(1)

    # 2. Parse all pages
    all_pages = []
    for rel in html_files:
        full_path = os.path.join(site_dir, rel)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()

        ext = extract_page(html)
        page_type = detect_page_type(rel)
        category = infer_category(ext)

        # Build shingles from core-editorial or fallback
        sim_words = ext.core_editorial_text if ext.core_editorial_text else [
            w for w in ext.all_content_text
        ]
        shingles = build_shingles(sim_words)

        all_pages.append({
            "file": rel,
            "page_type": page_type,
            "ext": ext,
            "shingles": shingles,
            "category": category,
            "title": ext.title.strip(),
        })

    # 3. Compute similarity clusters
    max_sim, similarity_pairs = compute_similarity_clusters(all_pages)

    # 4. Check global uniqueness
    dup_titles, dup_metas = check_global_uniqueness(all_pages)

    # Build duplicate lookup for per-page checks
    dup_title_files = set()
    for files in dup_titles.values():
        dup_title_files.update(files)
    dup_meta_files = set()
    for files in dup_metas.values():
        dup_meta_files.update(files)

    # 5. Grade each page
    results = []
    for p in all_pages:
        ext = p["ext"]
        rel = p["file"]
        ptype = p["page_type"]

        if ptype == "review":
            grade, checks = grade_review(ext, rel, base_url, site_dir, max_sim)
        elif ptype == "comparison":
            grade, checks = grade_comparison(ext, rel, base_url, site_dir, max_sim)
        elif ptype == "category_hub":
            grade, checks = grade_category_hub(ext, rel, base_url, max_sim)
        elif ptype == "directory":
            grade, checks = grade_directory(ext, rel, base_url, site_dir)
        else:  # editorial, homepage
            grade, checks = grade_editorial(ext, rel, base_url)

        # Apply global uniqueness hard-fails
        if rel in dup_title_files:
            checks["duplicate_title"] = True
            if grade != "C":
                grade = "C"
                checks.setdefault("fail_reasons", []).append("duplicate title")
        if rel in dup_meta_files:
            checks["duplicate_meta"] = True
            if grade != "C":
                grade = "C"
                checks.setdefault("fail_reasons", []).append("duplicate meta description")

        results.append({
            "file": rel,
            "page_type": ptype,
            "grade": grade,
            "title": p["title"],
            "checks": checks,
            "_ext": ext,  # Temporarily store for slop lint pass
        })

    # 5b. Slop lint pass (post-grade, pre-output)
    slop_downgrades = slop_lint_pass(results, all_pages)

    # Strip _ext before JSON serialization
    for r in results:
        r.pop("_ext", None)

    # 6. Generate outputs
    if not args.dry_run:
        generate_sitemap_core(results, base_url, out_dir, site_dir)
        generate_sitemap_hold(results, base_url, out_dir, site_dir)
        generate_sitemap_index(base_url, out_dir)
        generate_headers(results, out_dir)

    if args.format in ("json", "both") and not args.dry_run:
        generate_report(results, similarity_pairs, dup_titles, dup_metas,
                        out_dir, slop_downgrades)

    if args.format in ("text", "both"):
        print_summary(results, similarity_pairs, dup_titles, dup_metas,
                      slop_downgrades)

    # Exit code: 2 if any A-page slop downgrade, 1 if C among reviews/comparisons, 0 otherwise
    a_downgraded = any(d["from"] == "A" and d["to"] == "C" for d in slop_downgrades)
    if a_downgraded:
        sys.exit(2)

    critical_c = any(
        r["grade"] == "C" and r["page_type"] in ("review", "comparison")
        for r in results
    )
    sys.exit(1 if critical_c else 0)


if __name__ == "__main__":
    main()

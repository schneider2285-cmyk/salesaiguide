#!/usr/bin/env python3
"""
Synthetic test fixtures for the Slop Linter signals.
Each test creates a minimal HTML page, extracts it, and asserts the expected behavior.
Run: python3 scripts/test_slop_signals.py
"""

import os
import sys
from datetime import date

# Add parent dir so we can import indexation_gate
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import indexation_gate as gate


# ---------------------------------------------------------------------------
# HTML scaffold — minimal valid structure for review/comparison pages
# ---------------------------------------------------------------------------

def make_html(title, body, page_type="review", canonical_slug="test-review.html"):
    """Build a minimal HTML page with required metadata."""
    canonical = f"https://salesaiguide.com/tools/{canonical_slug}"
    if page_type == "comparison":
        canonical = f"https://salesaiguide.com/compare/{canonical_slug}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="Test description for {title}">
    <link rel="canonical" href="{canonical}">
</head>
<body>
    <nav class="navbar"><div class="container">Nav</div></nav>
    {body}
    <footer class="footer">Footer</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Signal 2: Thin Sections
# ---------------------------------------------------------------------------

def test_thin_section_flagged():
    """H2 with 5 words and no rich content → thin section."""
    body = """
    <article class="review-content">
        <h2>Short Section</h2>
        <p>Only five words here now.</p>
        <h2>Another Section</h2>
        <p>This section has enough words to pass the thin section check because it contains
        more than forty words of real editorial content that provides actual value to the
        reader and demonstrates substantive coverage of the topic at hand.</p>
    </article>"""
    html = make_html("Thin Section Test", body)
    ext = gate.extract_page(html)
    assert len(ext.thin_sections) >= 1, f"Expected thin section, got {ext.thin_sections}"
    assert ext.thin_sections[0]["header"] == "Short Section"
    print("  ✓ test_thin_section_flagged")


def test_thin_section_table():
    """H2 with 5 words + table → NOT thin (has rich content)."""
    body = """
    <article class="review-content">
        <h2>Short With Table</h2>
        <p>Only five words here now.</p>
        <table><tr><td>Data</td></tr></table>
        <h2>Next Section</h2>
        <p>This section has enough words to pass the thin section check because it contains
        more than forty words of real editorial content that provides actual value.</p>
    </article>"""
    html = make_html("Thin Section Table Test", body)
    ext = gate.extract_page(html)
    thin_headers = [s["header"] for s in ext.thin_sections]
    assert "Short With Table" not in thin_headers, f"Table section wrongly flagged: {ext.thin_sections}"
    print("  ✓ test_thin_section_table")


# ---------------------------------------------------------------------------
# Signal 3: Unsourced Blockquotes
# ---------------------------------------------------------------------------

def test_blockquote_unsourced():
    """Blockquote with no external citation → unsourced."""
    body = """
    <article class="review-content">
        <section data-audit="core-editorial">
            <h2>Test Section</h2>
            <blockquote>This is a great quote from someone.</blockquote>
            <p>Some text after the blockquote.</p>
        </section>
    </article>"""
    html = make_html("Blockquote Unsourced Test", body)
    ext = gate.extract_page(html)
    assert len(ext.blockquotes) == 1
    assert ext.blockquotes[0]["has_external_cite"] is False
    print("  ✓ test_blockquote_unsourced")


def test_blockquote_sourced():
    """Blockquote with external citation link → sourced."""
    body = """
    <article class="review-content">
        <section data-audit="core-editorial">
            <h2>Test Section</h2>
            <blockquote>This is a great quote.
                <a href="https://www.example.com/source">Source</a>
            </blockquote>
            <p>Some text after.</p>
        </section>
    </article>"""
    html = make_html("Blockquote Sourced Test", body)
    ext = gate.extract_page(html)
    assert len(ext.blockquotes) == 1
    assert ext.blockquotes[0]["has_external_cite"] is True
    print("  ✓ test_blockquote_sourced")


# ---------------------------------------------------------------------------
# Signal 4: Unsourced Numeric Claims
# ---------------------------------------------------------------------------

def test_numeric_unsourced():
    """47% claim with no cite link → unsourced."""
    body = """
    <article class="review-content">
        <section data-audit="core-editorial">
            <h2>Claims Section</h2>
            <p>Studies show that 47% of users prefer this tool over alternatives.</p>
        </section>
    </article>"""
    html = make_html("Numeric Unsourced Test", body)
    ext = gate.extract_page(html)
    claims = gate.check_numeric_claims(ext)
    assert len(claims) >= 1, f"Expected unsourced claim, got {claims}"
    assert any("47%" in c["claim"] for c in claims)
    print("  ✓ test_numeric_unsourced")


def test_numeric_sourced():
    """47% claim with cite link in paragraph → sourced."""
    body = """
    <article class="review-content">
        <section data-audit="core-editorial">
            <h2>Claims Section</h2>
            <p>Studies show that 47% of users prefer this tool
            <a href="https://www.example.com/study">according to research</a>.</p>
        </section>
    </article>"""
    html = make_html("Numeric Sourced Test", body)
    ext = gate.extract_page(html)
    claims = gate.check_numeric_claims(ext)
    assert len(claims) == 0, f"Expected no unsourced claims, got {claims}"
    print("  ✓ test_numeric_sourced")


def test_numeric_dates():
    """Feb 2026 and v2.0 excluded; 4.9/5 IS flagged unless cited."""
    body = """
    <article class="review-content">
        <section data-audit="core-editorial">
            <h2>Date Section</h2>
            <p>Updated February 2026 and using v2.0 of the platform.</p>
            <p>The tool has a 4.9/5 rating on G2.</p>
        </section>
    </article>"""
    html = make_html("Numeric Dates Test", body)
    ext = gate.extract_page(html)
    claims = gate.check_numeric_claims(ext)
    # Feb 2026 and v2.0 should be excluded. 4.9/5 should be flagged (no cite).
    claim_texts = [c["claim"] for c in claims]
    assert not any("2026" in c for c in claim_texts), f"Date wrongly flagged: {claim_texts}"
    assert any("4.9/5" in c for c in claim_texts), f"Rating not flagged: {claim_texts}"
    print("  ✓ test_numeric_dates")


# ---------------------------------------------------------------------------
# Signal 5: Over-Templated Intros
# ---------------------------------------------------------------------------

def test_intro_templated():
    """Two pages with identical intros after tool name normalization → flagged."""
    body_a = """
    <article class="review-content">
        <h1>Clay Review</h1>
        <p>Clay is one of the best sales AI tools on the market today. In this comprehensive
        review we will cover all the features, pricing plans, integrations, pros and cons,
        and help you decide if Clay is the right tool for your sales team workflow needs.</p>
        <div class="final-verdict"><p>Verdict here.</p></div>
    </article>"""
    body_b = """
    <article class="review-content">
        <h1>Apollo Review</h1>
        <p>Apollo is one of the best sales AI tools on the market today. In this comprehensive
        review we will cover all the features, pricing plans, integrations, pros and cons,
        and help you decide if Apollo is the right tool for your sales team workflow needs.</p>
        <div class="final-verdict"><p>Verdict here.</p></div>
    </article>"""

    html_a = make_html("Clay Review Test", body_a, canonical_slug="clay-review.html")
    html_b = make_html("Apollo Review Test", body_b, canonical_slug="apollo-review.html")

    ext_a = gate.extract_page(html_a)
    ext_b = gate.extract_page(html_b)

    page_a = {"file": "tools/clay-review.html", "page_type": "review", "ext": ext_a}
    page_b = {"file": "tools/apollo-review.html", "page_type": "review", "ext": ext_b}

    result = gate.check_intro_similarity(page_a, [page_a, page_b])
    assert result is not None, "Expected similarity result"
    assert result["max_sim"] > 0.25, f"Expected >0.25 similarity, got {result['max_sim']}"
    print("  ✓ test_intro_templated")


# ---------------------------------------------------------------------------
# Signal 6: Hype Word Density
# ---------------------------------------------------------------------------

def test_hype_heavy():
    """Content with >2% hype words → flagged."""
    # ~50 words, 2+ hype = >2% density
    body = """
    <article class="review-content">
        <h2>Review</h2>
        <p>This revolutionary tool offers seamless integration with cutting-edge
        technology. The transformative features provide unparalleled performance
        that will supercharge your sales pipeline and turbocharge your revenue.</p>
    </article>"""
    html = make_html("Hype Heavy Test", body)
    ext = gate.extract_page(html)
    density, flagged = gate.check_hype_density(ext)
    assert density > gate.HYPE_DENSITY_THRESHOLD, f"Expected >2% density, got {density:.3f}"
    assert len(flagged) > 0
    print("  ✓ test_hype_heavy")


def test_hype_light():
    """Content with <2% hype words → passes."""
    body = """
    <article class="review-content">
        <h2>Review</h2>
        <p>This tool provides solid email enrichment capabilities for sales teams.
        The pricing is reasonable and the data quality is consistently good across
        most use cases. Integration with common CRMs works well in our testing
        and the support team was responsive when we had questions about the API
        documentation. Overall a practical choice for mid-market teams that need
        reliable prospecting data without breaking the budget.</p>
    </article>"""
    html = make_html("Hype Light Test", body)
    ext = gate.extract_page(html)
    density, flagged = gate.check_hype_density(ext)
    assert density <= gate.HYPE_DENSITY_THRESHOLD, f"Expected <=2% density, got {density:.3f}"
    print("  ✓ test_hype_light")


# ---------------------------------------------------------------------------
# Signal 7: Conversion-First Layout
# ---------------------------------------------------------------------------

def test_conversion_fail():
    """/go/ link inside core-editorial → fail."""
    body = """
    <article class="review-content">
        <div class="quick-summary">
            <a href="/go/tool">Try Tool</a>
        </div>
        <section data-audit="core-editorial">
            <h2>Features</h2>
            <p>Great features. <a href="/go/tool">Sign up here</a> to get started.</p>
        </section>
        <div class="final-verdict"><p>Our verdict.</p></div>
    </article>"""
    html = make_html("Conversion Fail Test", body)
    ext = gate.extract_page(html)
    fail, detail = gate.check_conversion_first(ext)
    assert fail, f"Expected conversion-first fail, got pass. Detail: {detail}"
    assert "core-editorial" in detail
    print("  ✓ test_conversion_fail")


def test_conversion_pass():
    """/go/ only in allowed zones + after verdict → pass."""
    body = """
    <article class="review-content">
        <div class="quick-summary">
            <a href="/go/tool">Try Tool Free</a>
        </div>
        <section data-audit="core-editorial">
            <h2>Features</h2>
            <p>This tool has many features including enrichment and outreach capabilities
            that work well for most sales teams in the mid-market segment.</p>
        </section>
        <div class="final-verdict" data-audit="decision-summary">
            <p>Our verdict: great tool.</p>
        </div>
        <div class="final-cta">
            <a href="/go/tool">Try Tool</a>
        </div>
    </article>"""
    html = make_html("Conversion Pass Test", body)
    ext = gate.extract_page(html)
    fail, detail = gate.check_conversion_first(ext)
    assert not fail, f"Expected pass, got fail: {detail}"
    print("  ✓ test_conversion_pass")


# ---------------------------------------------------------------------------
# Signal 9: Last Verified Date
# ---------------------------------------------------------------------------

def test_last_verified_missing():
    """No last-verified element → C tier."""
    body = """
    <article class="review-content">
        <h2>Review</h2>
        <p>Content here.</p>
    </article>"""
    html = make_html("Last Verified Missing Test", body)
    ext = gate.extract_page(html)
    days, date_str, tier = gate.check_last_verified(ext)
    assert tier == "C", f"Expected C tier, got {tier}"
    assert days is None
    print("  ✓ test_last_verified_missing")


def test_last_verified_stale():
    """Last verified Jun 2025 with today=2026-02-27 → >365d → C tier."""
    body = """
    <article class="review-content">
        <div class="review-meta">
            <div class="last-verified" data-audit="last-verified">Last verified: Jun 2025</div>
        </div>
        <h2>Review</h2>
        <p>Content here.</p>
    </article>"""
    html = make_html("Last Verified Stale Test", body)
    ext = gate.extract_page(html)
    # Inject a fixed "today" for time-stable test
    test_today = date(2026, 6, 2)  # Jun 2025 → Jun 2026 = ~365d
    days, date_str, tier = gate.check_last_verified(ext, today=test_today)
    assert tier == "C", f"Expected C tier for stale date, got {tier} ({days}d)"
    assert days is not None and days > 365
    print("  ✓ test_last_verified_stale")


def test_last_verified_fresh():
    """Last verified: Feb 2026 with today=2026-02-27 → ≤90d → A tier."""
    body = """
    <article class="review-content">
        <div class="review-meta">
            <div class="last-verified" data-audit="last-verified">Last verified: Feb 2026</div>
        </div>
        <h2>Review</h2>
        <p>Content here.</p>
    </article>"""
    html = make_html("Last Verified Fresh Test", body)
    ext = gate.extract_page(html)
    # Inject today for time-stable test
    test_today = date(2026, 2, 27)
    days, date_str, tier = gate.check_last_verified(ext, today=test_today)
    assert tier == "A", f"Expected A tier for fresh date, got {tier} ({days}d)"
    assert days is not None and days <= 90
    print("  ✓ test_last_verified_fresh")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    tests = [
        test_thin_section_flagged,
        test_thin_section_table,
        test_blockquote_unsourced,
        test_blockquote_sourced,
        test_numeric_unsourced,
        test_numeric_sourced,
        test_numeric_dates,
        test_hype_heavy,
        test_hype_light,
        test_conversion_fail,
        test_conversion_pass,
        test_last_verified_missing,
        test_last_verified_stale,
        test_last_verified_fresh,
        test_intro_templated,
    ]

    print(f"\nRunning {len(tests)} slop signal tests...\n")
    passed = 0
    failed = 0

    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:  # noqa: E501
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: EXCEPTION: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

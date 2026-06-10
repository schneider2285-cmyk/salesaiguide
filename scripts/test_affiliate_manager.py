#!/usr/bin/env python3
"""Tests for scripts/affiliate_manager.py pure logic. Run: python3 scripts/test_affiliate_manager.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import affiliate_manager as am  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, bool(cond)))


def run():
    # is_real_tracking_param
    check("reject_empty", am.is_real_tracking_param("") is False)
    check("reject_no_query", am.is_real_tracking_param("https://woodpecker.co") is False)
    check("reject_fake_ref", am.is_real_tracking_param("https://x.com?ref=salesaiguide") is False)
    check("accept_via", am.is_real_tracking_param("https://www.saleshandy.com/?via=matthew") is True)
    check("accept_red", am.is_real_tracking_param("https://woodpecker.co/?red=salesa145703") is True)

    # validate_activation
    links = {"woodpecker": {"status": "placeholder"}}
    ok, _ = am.validate_activation("woodpecker", "https://woodpecker.co/?red=abc", links)
    check("validate_ok", ok)
    ok, _ = am.validate_activation("woodpecker", "https://woodpecker.co", links)
    check("validate_no_param", not ok)
    ok, _ = am.validate_activation("nope", "https://x?a=b", links)
    check("validate_unknown_slug", not ok)

    passed = sum(1 for _, ok in CASES if ok)
    print("Running %d affiliate-manager tests...\n" % len(CASES))
    for name, ok in CASES:
        print("  %s %s" % ("✓" if ok else "✗", name))
    print("\nResults: %d passed, %d failed out of %d" % (passed, len(CASES) - passed, len(CASES)))
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(run())

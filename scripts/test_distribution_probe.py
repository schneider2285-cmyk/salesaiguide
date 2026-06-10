#!/usr/bin/env python3
"""Tests for the distribution-probe decision rule (scripts/distribution_probe.py).

Encodes the pre-committed STOP/COMMIT/CONTINUE thresholds as executable assertions so
the go/no-go decision cannot silently drift once results arrive. Run:
  python3 scripts/test_distribution_probe.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribution_probe import decide, load_config  # noqa: E402

TH = load_config()["decisionRule"]

CASES = [
    # name, metrics, expected verdict
    ("signup_commits", {"helpful_answers": 40, "clicks": 3, "signups": 1, "qualified_visits": 5}, "COMMIT"),
    ("engagement_commits", {"helpful_answers": 40, "clicks": 12, "signups": 0, "qualified_visits": 20}, "COMMIT"),
    ("early_signup_commits_despite_low_effort", {"helpful_answers": 8, "clicks": 2, "signups": 1, "qualified_visits": 3}, "COMMIT"),
    ("low_effort_no_signal_undecided", {"helpful_answers": 10, "clicks": 1, "signups": 0, "qualified_visits": 2}, "INSUFFICIENT_EFFORT"),
    ("dead_stops", {"helpful_answers": 40, "clicks": 1, "signups": 0, "qualified_visits": 3}, "STOP"),
    ("middle_continues", {"helpful_answers": 40, "clicks": 6, "signups": 0, "qualified_visits": 8}, "CONTINUE"),
]


def main():
    print("Running %d distribution-probe decision tests...\n" % len(CASES))
    passed = 0
    for name, metrics, expected in CASES:
        verdict, _ = decide(metrics, TH)
        ok = verdict == expected
        print("  %s %s (got %s, want %s)" % ("✓" if ok else "✗", name, verdict, expected))
        passed += int(ok)
    print("\nResults: %d passed, %d failed out of %d" % (passed, len(CASES) - passed, len(CASES)))
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())

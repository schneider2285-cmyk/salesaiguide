#!/usr/bin/env python3
"""Distribution probe harness: the 2-week cold-email-wedge community demand test.

Strategy and rationale live in docs/marketing/distribution-plan.md. This tool makes the
probe runnable and the go/no-go decision MECHANICAL, so sunk-cost bias cannot move the
goalposts once results come in (the plan explicitly demands a pre-committed rule).

Subcommands:
  validate   check the config and that every target page actually exists in the repo.
  links      build UTM-tagged URLs for each target page x channel, so GA4 attributes
             probe traffic. (Affiliate /go/ clicks are tracked by the vendor dashboards
             regardless of UTM, so attribution survives even if a community strips params.)
  score      read the answer tracker (CSV) plus entered dashboard numbers and apply the
             pre-committed rule -> COMMIT / STOP / CONTINUE / INSUFFICIENT_EFFORT.

This sends nothing and connects no credentials. The operator runs the outreach by hand
(per the plan's rules of engagement) and logs it in ops/distribution/answer-tracker.csv.

Usage:
  python3 scripts/distribution_probe.py validate
  python3 scripts/distribution_probe.py links [--base-url https://salesaiguide.com]
  python3 scripts/distribution_probe.py score --results ops/distribution/answer-tracker.csv
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "ops" / "distribution" / "probe-config.json"

TRUTHY = {"y", "yes", "1", "true"}


def load_config():
    return json.loads(CONFIG.read_text())


def target_file(path):
    # clean URL "/tools/woodpecker-review" -> source file "tools/woodpecker-review.html"
    return ROOT / (path.lstrip("/") + ".html")


def cmd_validate(cfg, args):
    problems = []
    for t in cfg.get("targets", []):
        f = target_file(t["path"])
        if not f.exists():
            problems.append("missing target page: %s (expected %s)" % (t["path"], f.relative_to(ROOT)))
    th = cfg.get("decisionRule", {})
    for k in ("minHelpfulAnswers", "stopClicksMax", "commitClicksMin", "commitQualifiedVisitsMin"):
        if k not in th:
            problems.append("decisionRule missing threshold: %s" % k)
    if not cfg.get("channels"):
        problems.append("no channels defined")
    if problems:
        print("INVALID probe config:")
        for p in problems:
            print("  -", p)
        return 1
    print("probe config OK: %d targets, %d channels, decision rule pre-committed (%s)."
          % (len(cfg["targets"]), len(cfg["channels"]), th.get("_committedOn", "?")))
    return 0


def cmd_links(cfg, args):
    base = (args.base_url or cfg.get("baseUrl", "https://salesaiguide.com")).rstrip("/")
    med = cfg["utm"]["medium"]
    camp = cfg["utm"]["campaign"]
    w = csv.writer(sys.stdout)
    w.writerow(["channel", "target", "url"])
    for ch in cfg["channels"]:
        src = ch["utm_source"]
        for t in cfg["targets"]:
            url = "%s%s?utm_source=%s&utm_medium=%s&utm_campaign=%s" % (base, t["path"], src, med, camp)
            w.writerow([ch["name"], t["label"], url])
    return 0


def decide(metrics, th):
    """Pure, pre-committed decision rule. Returns (verdict, reasons).

    Order matters: a real positive signal COMMITS regardless of effort count; the
    effort floor only blocks a premature STOP (you cannot declare failure before
    honestly running the probe).
    """
    answers = metrics.get("helpful_answers", 0)
    clicks = metrics.get("clicks", 0)
    signups = metrics.get("signups", 0)
    visits = metrics.get("qualified_visits", 0)

    committed = signups >= 1 or (clicks >= th["commitClicksMin"] and visits >= th["commitQualifiedVisitsMin"])
    if committed:
        if signups >= 1:
            return "COMMIT", ["%d affiliate signup(s): real money signal" % signups]
        return "COMMIT", ["%d clicks and %d qualified visits clear the commit bar" % (clicks, visits)]

    if answers < th["minHelpfulAnswers"]:
        return "INSUFFICIENT_EFFORT", [
            "only %d helpful answers logged; need >= %d before a STOP can be declared"
            % (answers, th["minHelpfulAnswers"])]

    if clicks <= th["stopClicksMax"] and signups == 0:
        return "STOP", ["~0 clicks (%d <= %d) and 0 signups after honest effort; stop investing per the plan"
                        % (clicks, th["stopClicksMax"])]

    return "CONTINUE", ["some signal (%d clicks, %d visits, %d signups) but below the commit bar; iterate messaging/targeting once"
                        % (clicks, visits, signups)]


def cmd_score(cfg, args):
    th = cfg["decisionRule"]
    path = Path(args.results)
    if not path.exists():
        print("results file not found: %s" % path)
        print("start from ops/distribution/answer-tracker.template.csv")
        return 1
    metrics = {"helpful_answers": 0, "links_dropped": 0, "clicks": 0, "signups": 0, "qualified_visits": 0}
    with path.open() as f:
        for row in csv.DictReader(f):
            if (row.get("date", "").strip().upper() in ("", "EXAMPLE")):
                continue
            if (row.get("helpful", "").strip().lower() in TRUTHY):
                metrics["helpful_answers"] += 1
            if (row.get("link_dropped", "").strip().lower() in TRUTHY):
                metrics["links_dropped"] += 1
            metrics["clicks"] += int(row.get("clicks", "0") or 0)
            metrics["signups"] += int(row.get("signups", "0") or 0)
            metrics["qualified_visits"] += int(row.get("qualified_visits", "0") or 0)

    verdict, reasons = decide(metrics, th)
    print("Probe metrics:", json.dumps(metrics))
    print("Pre-committed rule:", json.dumps({k: v for k, v in th.items() if not k.startswith("_") and k != "logic"}))
    print("VERDICT:", verdict)
    for r in reasons:
        print("  -", r)
    if metrics["links_dropped"]:
        ratio = metrics["helpful_answers"] / metrics["links_dropped"]
        flag = "" if ratio >= 5 else "  (below the >= 5 target; ease off the links)"
        print("  link discipline: 1 link per %.1f helpful answers%s" % (ratio, flag))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Distribution probe harness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    pl = sub.add_parser("links")
    pl.add_argument("--base-url")
    ps = sub.add_parser("score")
    ps.add_argument("--results", default=str(ROOT / "ops" / "distribution" / "answer-tracker.csv"))
    args = ap.parse_args()
    cfg = load_config()
    return {"validate": cmd_validate, "links": cmd_links, "score": cmd_score}[args.cmd](cfg, args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Affiliate program manager. Spec: docs/superpowers/specs/2026-06-09-affiliate-manager-design.md.
Deterministic, stdlib only, no LLM, no fabricated data. Manages the affiliate portfolio and the
placeholder->live activation. Does not pull live earnings (stubbed) and does not deploy."""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "affiliate-links.json"
FUNNEL_FILE = ROOT / "ops" / "data" / "revenue-funnel.json"
PIPELINE_FILE = ROOT / "ops" / "data" / "affiliate-pipeline.json"

FAKE_PARAM_RE = re.compile(r"ref=salesaiguide", re.IGNORECASE)


def is_real_tracking_param(url):
    """True if the URL carries a plausible real affiliate tracking param.
    Rejects empty/no-query and the known-fake ref=salesaiguide."""
    if not url or "?" not in url:
        return False
    query = url.split("?", 1)[1]
    if not query.strip():
        return False
    if FAKE_PARAM_RE.search(query):
        return False
    return any("=" in part and part.split("=", 1)[1] for part in query.split("&"))


def validate_activation(slug, url, links):
    if slug not in links:
        return False, "unknown slug '%s' (not in affiliate-links.json)" % slug
    if not is_real_tracking_param(url):
        return False, "url has no real tracking param (empty query or fake ref=salesaiguide)"
    return True, "ok"


def activation_queue(links, funnel, pipeline):
    """Placeholder programs ranked by funnel monetizableSurfaces desc."""
    cov = funnel.get("slugCoverage", {})
    pl = pipeline.get("pipeline", {})
    rows = []
    for slug, meta in links.items():
        if meta.get("status") == "live":
            continue
        rows.append({
            "slug": slug,
            "surfaces": cov.get(slug, {}).get("monetizableSurfaces", 0),
            "network": meta.get("network", "") or pl.get(slug, {}).get("network", ""),
            "signup_url": meta.get("signup_url", "") or pl.get(slug, {}).get("signup_url", ""),
            "stage": pl.get(slug, {}).get("stage", "not_started"),
        })
    rows.sort(key=lambda r: r["surfaces"], reverse=True)
    return rows


def portfolio_rows(links, funnel, pipeline):
    cov = funnel.get("slugCoverage", {})
    pl = pipeline.get("pipeline", {})
    rank = {r["slug"]: i + 1 for i, r in enumerate(activation_queue(links, funnel, pipeline))}
    rows = []
    for slug, meta in links.items():
        status = meta.get("status", "placeholder")
        rows.append({
            "slug": slug,
            "status": status,
            "stage": "live" if status == "live" else pl.get(slug, {}).get("stage", "not_started"),
            "network": meta.get("network", ""),
            "param": is_real_tracking_param(meta.get("url", "")),
            "surfaces": cov.get(slug, {}).get("monetizableSurfaces", 0),
            "rank": rank.get(slug),
        })
    rows.sort(key=lambda r: (r["status"] != "live", r["rank"] or 9999))
    return rows


STAGES = ["not_started", "applied", "approved", "live", "rejected"]


def set_pipeline_stage(pipeline, slug, stage, network=None, signup_url=None, note=None, today=None):
    if stage not in STAGES:
        raise ValueError("invalid stage: %s" % stage)
    today = today or date.today().isoformat()
    pl = pipeline.setdefault("pipeline", {})
    entry = pl.setdefault(slug, {"stage": "not_started", "network": "", "signup_url": "",
                                 "appliedDate": None, "approvedDate": None, "notes": ""})
    entry["stage"] = stage
    if network is not None:
        entry["network"] = network
    if signup_url is not None:
        entry["signup_url"] = signup_url
    if note:
        entry["notes"] = note
    if stage == "applied" and not entry.get("appliedDate"):
        entry["appliedDate"] = today
    if stage == "approved" and not entry.get("approvedDate"):
        entry["approvedDate"] = today
    pipeline["lastUpdated"] = today
    return pipeline


def _load(p, default):
    try:
        return json.loads(p.read_text())
    except FileNotFoundError:
        return default


def load_links():
    return json.loads(LINKS_FILE.read_text())


def load_funnel():
    return _load(FUNNEL_FILE, {"slugCoverage": {}})


def load_pipeline():
    return _load(PIPELINE_FILE, {"_meta": "", "lastUpdated": None, "pipeline": {}})


def save_pipeline(pipeline):
    PIPELINE_FILE.write_text(json.dumps(pipeline, indent=2) + "\n")


def _run(script, *flags):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *flags],
                          capture_output=True, text=True)


def cmd_status(args):
    rows = portfolio_rows(load_links()["links"], load_funnel(), load_pipeline())
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    fmt = "%-16s %-11s %-11s %-13s %-6s %-9s %s"
    print(fmt % ("slug", "status", "stage", "network", "param", "surfaces", "rank"))
    for r in rows:
        print(fmt % (r["slug"], r["status"], r["stage"], (r["network"] or "-")[:13],
                     "yes" if r["param"] else "no", r["surfaces"], r["rank"] or "-"))
    live = sum(1 for r in rows if r["status"] == "live")
    print("\n%d programs, %d live, %d placeholder" % (len(rows), live, len(rows) - live))
    return 0


def cmd_queue(args):
    q = activation_queue(load_links()["links"], load_funnel(), load_pipeline())
    if args.json:
        print(json.dumps(q, indent=2))
        return 0
    fmt = "%-4s %-16s %-9s %-13s %-11s %s"
    print(fmt % ("#", "slug", "surfaces", "network", "stage", "signup_url"))
    for i, r in enumerate(q, 1):
        print(fmt % (i, r["slug"], r["surfaces"], (r["network"] or "-")[:13], r["stage"], r["signup_url"] or "-"))
    return 0


def cmd_health(args):
    links = load_links()["links"]
    live = [s for s, m in links.items() if m.get("status") == "live"]
    issues = []
    for slug in live:
        if not is_real_tracking_param(links[slug].get("url", "")):
            issues.append("%s: live but url has no real tracking param (%s)" % (slug, links[slug].get("url", "")))
    # check_affiliate_links.py is a read-only guard: catches fake refs, undefined
    # slugs, bypassed CTAs, and _redirects out of sync with affiliate-links.json.
    guard = _run("check_affiliate_links.py")
    if guard.returncode != 0:
        issues.append("check_affiliate_links.py failed: " + (guard.stdout + guard.stderr).strip()[:200])
    if issues:
        print("HEALTH: %d issue(s), live=[%s]:" % (len(issues), ", ".join(live)))
        for i in issues:
            print("  -", i)
        return 1
    print("HEALTH OK: %d live programs (%s), real params, guard clean." % (len(live), ", ".join(live)))
    return 0


def cmd_pipeline(args):
    if args.slug not in load_links()["links"]:
        print("unknown slug '%s'" % args.slug)
        return 1
    pipeline = load_pipeline()
    set_pipeline_stage(pipeline, args.slug, args.stage, network=args.network,
                       signup_url=args.signup_url, note=args.note)
    save_pipeline(pipeline)
    print("pipeline: %s -> %s" % (args.slug, args.stage))
    return 0


def cmd_activate(args):
    data = load_links()
    links = data["links"]
    ok, reason = validate_activation(args.slug, args.url, links)
    if not ok:
        print("REFUSED:", reason)
        return 1
    if links[args.slug].get("status") == "live":
        print("note: %s already live; updating url" % args.slug)
    backup = LINKS_FILE.read_text()
    links[args.slug]["url"] = args.url
    links[args.slug]["status"] = "live"
    LINKS_FILE.write_text(json.dumps(data, indent=2) + "\n")
    _run("build_redirects.py")
    guard = _run("check_affiliate_links.py")
    if guard.returncode != 0:
        LINKS_FILE.write_text(backup)
        _run("build_redirects.py")
        print("ABORTED: guard failed, reverted affiliate-links.json:\n" + (guard.stdout + guard.stderr).strip()[:300])
        return 1
    pipeline = load_pipeline()
    set_pipeline_stage(pipeline, args.slug, "live")
    save_pipeline(pipeline)
    print("ACTIVATED %s -> live. Run 'bash deploy.sh' to publish." % args.slug)
    return 0


def cmd_sync(args):
    print("live-data sync not configured. Add REWARDFUL_API_SECRET / FIRSTPROMOTER_API_KEY per ops/aros/SECRETS.md.")
    print("(Woodpecker is in-house with no API; enter its numbers manually.) No data fabricated.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Affiliate program manager")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    q = sub.add_parser("queue")
    q.add_argument("--json", action="store_true")
    sub.add_parser("health")
    p = sub.add_parser("pipeline")
    p.add_argument("slug")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--network")
    p.add_argument("--signup-url", dest="signup_url")
    p.add_argument("--note")
    a = sub.add_parser("activate")
    a.add_argument("slug")
    a.add_argument("--url", required=True)
    sub.add_parser("sync")
    args = ap.parse_args()
    return {"status": cmd_status, "queue": cmd_queue, "health": cmd_health,
            "pipeline": cmd_pipeline, "activate": cmd_activate, "sync": cmd_sync}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())

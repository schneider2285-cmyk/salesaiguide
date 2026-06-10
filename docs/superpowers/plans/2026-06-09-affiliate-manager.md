# Affiliate Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A deterministic CLI (`scripts/affiliate_manager.py`) that manages the affiliate portfolio and performs safe placeholder->live activation, operationalizing the merged Monetization Manager scaffold.

**Architecture:** One Python CLI reading `affiliate-links.json` (link source of truth) + `ops/data/revenue-funnel.json` (activation ranking) + `ops/data/affiliate-pipeline.json` (new application-workflow state). Pure functions are importable for tests; `activate`/`health` shell out to the existing `build_redirects.py` and `check_affiliate_links.py` guards. No credentials, no LLM, no fabricated data, no deploy.

**Tech Stack:** Python 3 stdlib only (argparse, json, re, subprocess, datetime). Tests are a plain assert-based script run directly (matches `scripts/test_slop_signals.py` and `scripts/test_distribution_probe.py`), not pytest.

**Spec:** `docs/superpowers/specs/2026-06-09-affiliate-manager-design.md`

---

## File Structure
- Create `scripts/affiliate_manager.py` — the CLI + importable pure logic.
- Create `scripts/test_affiliate_manager.py` — assert-based tests for the pure logic.
- Create `ops/data/affiliate-pipeline.json` — seeded with the 4 live programs at stage `live`.
- Modify `package.json` — add `"affiliates"` script.
- Modify `ops/aros/agents/monetization-manager.md` — point the role at the real tool.

---

### Task 1: Tracking-param validation (pure)

**Files:**
- Create: `scripts/affiliate_manager.py`
- Create: `scripts/test_affiliate_manager.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/test_affiliate_manager.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'affiliate_manager'` (the module does not exist yet).

- [ ] **Step 3: Write minimal implementation**

Create `scripts/affiliate_manager.py`:
```python
#!/usr/bin/env python3
"""Affiliate program manager. Spec: docs/superpowers/specs/2026-06-09-affiliate-manager-design.md.
Deterministic, stdlib only, no LLM, no fabricated data. Manages the affiliate portfolio and the
placeholder->live activation. Does not pull live earnings (stubbed) and does not deploy."""
import re

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: PASS — `Results: 8 passed, 0 failed out of 8`.

- [ ] **Step 5: Commit**

```bash
git add scripts/affiliate_manager.py scripts/test_affiliate_manager.py
git commit -m "feat(affiliate): tracking-param validation for the affiliate manager"
```

---

### Task 2: Activation queue and portfolio rows (pure)

**Files:**
- Modify: `scripts/affiliate_manager.py`
- Modify: `scripts/test_affiliate_manager.py`

- [ ] **Step 1: Write the failing test**

In `scripts/test_affiliate_manager.py`, add these lines inside `run()` immediately before the `passed = ...` line:
```python
    # activation_queue: rank placeholders by surfaces desc, exclude live
    links2 = {"a": {"status": "placeholder"}, "b": {"status": "placeholder"}, "c": {"status": "live"}}
    funnel = {"slugCoverage": {"a": {"monetizableSurfaces": 5}, "b": {"monetizableSurfaces": 20}, "c": {"monetizableSurfaces": 99}}}
    q = am.activation_queue(links2, funnel, {"pipeline": {}})
    check("queue_excludes_live", all(r["slug"] != "c" for r in q))
    check("queue_sorted_desc", [r["slug"] for r in q] == ["b", "a"])

    # portfolio_rows: live-first, count matches
    rows = am.portfolio_rows(links2, funnel, {"pipeline": {}})
    check("portfolio_live_first", rows[0]["status"] == "live")
    check("portfolio_count", len(rows) == 3)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: FAIL — `AttributeError: module 'affiliate_manager' has no attribute 'activation_queue'`.

- [ ] **Step 3: Write minimal implementation**

In `scripts/affiliate_manager.py`, append:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: PASS — `Results: 12 passed, 0 failed out of 12`.

- [ ] **Step 5: Commit**

```bash
git add scripts/affiliate_manager.py scripts/test_affiliate_manager.py
git commit -m "feat(affiliate): funnel-ranked activation queue and portfolio rows"
```

---

### Task 3: Pipeline state transitions (pure) + seed file

**Files:**
- Modify: `scripts/affiliate_manager.py`
- Modify: `scripts/test_affiliate_manager.py`
- Create: `ops/data/affiliate-pipeline.json`

- [ ] **Step 1: Write the failing test**

In `scripts/test_affiliate_manager.py`, add inside `run()` before `passed = ...`:
```python
    # set_pipeline_stage stamps dates and keeps earlier ones
    pl2 = {"pipeline": {}}
    am.set_pipeline_stage(pl2, "a", "applied", today="2026-06-09")
    check("applied_date", pl2["pipeline"]["a"]["appliedDate"] == "2026-06-09")
    am.set_pipeline_stage(pl2, "a", "approved", today="2026-06-10")
    check("approved_date", pl2["pipeline"]["a"]["approvedDate"] == "2026-06-10")
    check("applied_date_kept", pl2["pipeline"]["a"]["appliedDate"] == "2026-06-09")
    try:
        am.set_pipeline_stage(pl2, "a", "bogus")
        check("reject_bad_stage", False)
    except ValueError:
        check("reject_bad_stage", True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: FAIL — `AttributeError: module 'affiliate_manager' has no attribute 'set_pipeline_stage'`.

- [ ] **Step 3: Write minimal implementation**

In `scripts/affiliate_manager.py`, add the import line at the top (just below `import re`):
```python
from datetime import date
```
Then append:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 scripts/test_affiliate_manager.py`
Expected: PASS — `Results: 16 passed, 0 failed out of 16`.

- [ ] **Step 5: Create the seed pipeline file**

Create `ops/data/affiliate-pipeline.json`:
```json
{
  "_meta": "Human application workflow state for affiliate programs. affiliate-links.json stays the link source of truth; this tracks the path to live. Managed by scripts/affiliate_manager.py.",
  "lastUpdated": "2026-06-09",
  "pipeline": {
    "woodpecker": {"stage": "live", "network": "in-house", "signup_url": "", "appliedDate": null, "approvedDate": null, "notes": "live with red=salesa145703"},
    "fireflies": {"stage": "live", "network": "FirstPromoter", "signup_url": "", "appliedDate": null, "approvedDate": null, "notes": "live with fpr=matthew16"},
    "justcall": {"stage": "live", "network": "FirstPromoter", "signup_url": "", "appliedDate": null, "approvedDate": null, "notes": "live with fp_ref=matthew95"},
    "saleshandy": {"stage": "live", "network": "Rewardful", "signup_url": "", "appliedDate": null, "approvedDate": null, "notes": "live with via=matthew"}
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add scripts/affiliate_manager.py scripts/test_affiliate_manager.py ops/data/affiliate-pipeline.json
git commit -m "feat(affiliate): pipeline state transitions + seed live programs"
```

---

### Task 4: IO + CLI subcommands

**Files:**
- Modify: `scripts/affiliate_manager.py`

- [ ] **Step 1: Add IO helpers and subcommands**

In `scripts/affiliate_manager.py`, add to the top imports (below `from datetime import date`):
```python
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "affiliate-links.json"
FUNNEL_FILE = ROOT / "ops" / "data" / "revenue-funnel.json"
PIPELINE_FILE = ROOT / "ops" / "data" / "affiliate-pipeline.json"
```
Then append the IO + CLI layer:
```python
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
```

- [ ] **Step 2: Verify syntax and the unit tests still pass**

Run: `python3 -m py_compile scripts/affiliate_manager.py && python3 scripts/test_affiliate_manager.py`
Expected: compiles; `Results: 16 passed, 0 failed out of 16`.

- [ ] **Step 3: Smoke-test the read-only subcommands on real data**

Run: `python3 scripts/affiliate_manager.py status | tail -3`
Expected: a summary line `49 programs, 4 live, 45 placeholder`.

Run: `python3 scripts/affiliate_manager.py queue | head -3`
Expected: header + `instantly` as row #1 (matches the funnel ranking).

Run: `python3 scripts/affiliate_manager.py health`
Expected: `HEALTH OK: 4 live programs (...)` exit 0.

Run: `python3 scripts/affiliate_manager.py sync`
Expected: the not-configured stub message.

- [ ] **Step 4: Verify activate refuses a fake param (no real-file mutation)**

Run: `python3 scripts/affiliate_manager.py activate apollo --url "https://apollo.io?ref=salesaiguide"`
Expected: `REFUSED: url has no real tracking param ...`, exit 1, and `git status --short affiliate-links.json` shows no change.

- [ ] **Step 5: Commit**

```bash
git add scripts/affiliate_manager.py
git commit -m "feat(affiliate): status/queue/health/pipeline/activate/sync CLI"
```

---

### Task 5: Integration (npm script + agent role) and full verification

**Files:**
- Modify: `package.json`
- Modify: `ops/aros/agents/monetization-manager.md`

- [ ] **Step 1: Add the npm script**

In `package.json`, change the `scripts` block so the line after `"probe": ...` adds:
```json
    "probe": "python3 scripts/distribution_probe.py",
    "affiliates": "python3 scripts/affiliate_manager.py"
```
(Keep the existing comma placement valid: `probe` line gets a trailing comma, `affiliates` is the last entry.)

- [ ] **Step 2: Point the agent role at the real tool**

In `ops/aros/agents/monetization-manager.md`, under the `## Skill` section, add this line:
```markdown
- Tool: `scripts/affiliate_manager.py` (`npm run affiliates`) — status / health / queue / pipeline / activate / sync.
```

- [ ] **Step 3: Validate package.json and run the full check set**

Run: `python3 -m json.tool package.json >/dev/null && echo OK`
Expected: `OK`.

Run: `npm run affiliates -- status | tail -1`
Expected: `49 programs, 4 live, 45 placeholder`.

Run: `npm test`
Expected: `Results: 15 passed, 0 failed out of 15` (unchanged; no HTML touched).

Run: `rm -rf /tmp/am-gate && mkdir -p /tmp/am-gate && python3 scripts/indexation_gate.py --site-dir . --out-dir /tmp/am-gate --base-url https://salesaiguide.com >/tmp/am-gate/run.log 2>&1; python3 -c "import json;print(json.load(open('/tmp/am-gate/gate-report.json'))['summary'])"`
Expected: `{'total': 166, 'A': 160, 'B': 5, 'C': 1}` (unchanged).

- [ ] **Step 4: Commit**

```bash
git add package.json ops/aros/agents/monetization-manager.md
git commit -m "feat(affiliate): npm run affiliates + wire into monetization-manager role"
```

- [ ] **Step 5: Push and open the PR**

```bash
git push -u origin feature/affiliate-manager
gh pr create --base redesign/nerdwallet-v1 --head feature/affiliate-manager \
  --title "feat(affiliate): affiliate program manager CLI" \
  --body "Implements docs/superpowers/specs/2026-06-09-affiliate-manager-design.md. Deterministic CLI (status/health/queue/pipeline/activate/sync), zero credentials, no fabricated data, no deploy. Verified: affiliate-manager tests 16/16, npm test 15/15, gate unchanged 160A/5B/1C. Base redesign/nerdwallet-v1 (preview only)."
```

---

## Verification Checklist (end state)
- `python3 scripts/test_affiliate_manager.py` -> 16/16.
- `npm run affiliates -- status` shows 49 programs / 4 live; `queue` top = instantly; `health` exits 0.
- `activate` rejects a fake-param URL and does not mutate `affiliate-links.json`.
- `npm test` 15/15; indexation gate unchanged (160A/5B/1C).
- PR open to `redesign/nerdwallet-v1`, not deployed.

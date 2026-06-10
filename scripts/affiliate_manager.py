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

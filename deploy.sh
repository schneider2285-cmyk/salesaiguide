#!/usr/bin/env bash
set -euo pipefail

# SalesAIGuide — one-command deploy
# Usage: bash deploy.sh
#
# This is the ONLY sanctioned way to deploy salesaiguide.com.
# Identity guards below prevent the May 2026 incident where another
# project's files were uploaded to this Netlify site.

cd "$(dirname "$0")"

EXPECTED_SITE_ID="c79f346d-e91d-42cf-80e2-295f8d7095e9"
EXPECTED_REMOTE_SUFFIX="salesaiguide.git"
EXPECTED_TITLE_MARKER="Sales AI Guide"

# ── Identity guards (abort fast if anything looks wrong) ─────────────
echo "==> Verifying deploy identity..."

# 1. Git remote must point at the salesaiguide repo
if [ -d .git ]; then
  REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
  if [[ "$REMOTE_URL" != *"$EXPECTED_REMOTE_SUFFIX" ]]; then
    echo "  ✗ ABORT: git remote 'origin' is '$REMOTE_URL'"
    echo "    Expected suffix: $EXPECTED_REMOTE_SUFFIX"
    echo "    You are deploying from the wrong directory."
    exit 1
  fi
  echo "  ✓ git remote matches salesaiguide repo"
else
  echo "  ✗ ABORT: no .git directory — refusing to deploy un-versioned files"
  exit 1
fi

# 2. Netlify link must point at the salesaiguide site ID
if [ -f .netlify/state.json ]; then
  LINKED_SITE_ID=$(python3 -c "import json;print(json.load(open('.netlify/state.json')).get('siteId',''))" 2>/dev/null || echo "")
  if [ "$LINKED_SITE_ID" != "$EXPECTED_SITE_ID" ]; then
    echo "  ✗ ABORT: .netlify/state.json points at site '$LINKED_SITE_ID'"
    echo "    Expected: $EXPECTED_SITE_ID (resilient-salamander-b2ddc4)"
    exit 1
  fi
  echo "  ✓ Netlify link matches expected site ID"
fi

# 3. Content sentinel — index.html must look like the Sales AI Guide
if ! grep -q "$EXPECTED_TITLE_MARKER" index.html 2>/dev/null; then
  echo "  ✗ ABORT: index.html does not contain '$EXPECTED_TITLE_MARKER'"
  echo "    The file in this directory is not the Sales AI Guide homepage."
  exit 1
fi
echo "  ✓ index.html contains Sales AI Guide title marker"

echo ""

# ── Load nvm + node ──────────────────────────────────
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if ! command -v netlify &>/dev/null; then
  echo "ERROR: Netlify CLI not found. Run: npm install -g netlify-cli"
  exit 1
fi

# ── Step 1a: Affiliate links ──────────────────────────
echo "==> Regenerating affiliate redirects from affiliate-links.json..."
python3 scripts/build_redirects.py

echo "==> Checking affiliate link integrity (no $0 leaks)..."
if ! python3 scripts/check_affiliate_links.py; then
  echo "  ✗ ABORT: affiliate link guard failed. Fix the issues above before deploying."
  exit 1
fi

echo "==> Checking for owner PII leaks..."
if ! python3 scripts/scrub_pii.py --check; then
  echo "  ✗ ABORT: owner PII found on public pages. Run: python3 scripts/scrub_pii.py"
  exit 1
fi
echo ""

# ── Step 1b: Gate ─────────────────────────────────────
echo "==> Running indexation gate..."
python3 scripts/indexation_gate.py --site-dir . --out-dir . \
  --base-url https://salesaiguide.com || true

echo ""
echo "Gate outputs regenerated. Verifying..."
[ -f sitemap.xml ]      && echo "  ✓ sitemap.xml"
[ -f sitemap-core.xml ] && echo "  ✓ sitemap-core.xml"
[ -f _headers ]         && echo "  ✓ _headers"
echo ""

# ── Step 2: Auth ──────────────────────────────────────
if ! netlify status &>/dev/null; then
  echo "==> Not logged in. Opening browser for Netlify auth..."
  netlify login
fi

# ── Step 3: Link ──────────────────────────────────────
if [ ! -f .netlify/state.json ]; then
  echo "==> Linking to existing Netlify site..."
  echo "    Select 'Link this directory to an existing site'"
  echo "    Then search for: salesaiguide"
  netlify link
fi

# ── Step 4: Deploy ────────────────────────────────────
echo "==> Deploying to production..."
netlify deploy --dir . --prod

echo ""
echo "==> Deploy complete. Running production checks..."
echo ""

# ── Step 5: Verify ────────────────────────────────────
echo "--- Production Verification ---"

# Check sitemap.xml
HTTP_CODE=$(curl -sI https://salesaiguide.com/sitemap.xml | head -1 | awk '{print $2}')
echo "  /sitemap.xml → HTTP $HTTP_CODE"
SITEMAP_TYPE=$(curl -s https://salesaiguide.com/sitemap.xml | head -3 | grep -c "sitemapindex" || true)
if [ "$SITEMAP_TYPE" -ge 1 ]; then
  echo "  ✓ Is sitemapindex (correct)"
else
  echo "  ✗ NOT a sitemapindex — still old file?"
fi

# Check sitemap-core.xml
HTTP_CODE=$(curl -sI https://salesaiguide.com/sitemap-core.xml | head -1 | awk '{print $2}')
echo "  /sitemap-core.xml → HTTP $HTTP_CODE"
CORE_COUNT=$(curl -s https://salesaiguide.com/sitemap-core.xml | grep -c "<url>" || true)
echo "  Pages in sitemap-core: $CORE_COUNT"

# Check Tier C noindex header
XROBOTS=$(curl -sI https://salesaiguide.com/compare/clay-vs-apollo.html | grep -i "x-robots-tag" || echo "(none)")
echo "  Tier C X-Robots-Tag: $XROBOTS"

echo ""
echo "=== Done ==="

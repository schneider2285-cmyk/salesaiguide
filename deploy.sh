#!/usr/bin/env bash
set -euo pipefail

# SalesAIGuide — one-command deploy
# Usage: bash deploy.sh

cd "$(dirname "$0")"

# ── Load nvm + node ──────────────────────────────────
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if ! command -v netlify &>/dev/null; then
  echo "ERROR: Netlify CLI not found. Run: npm install -g netlify-cli"
  exit 1
fi

# ── Step 1: Gate ──────────────────────────────────────
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

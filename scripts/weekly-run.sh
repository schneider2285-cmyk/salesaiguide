#!/usr/bin/env bash
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SITE_DIR"

echo "=== SALESAIGUIDE WEEKLY AGENT RUN ==="
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Phase 1: Auto-fix known issues
echo ""
echo "--- Phase 1: Auto-Fix ---"
node scripts/agent-autofix.js

# Phase 2: Full agent audit cycle
echo ""
echo "--- Phase 2: Agent Audit ---"
echo "Run agent audit scripts here (manual or via claude)"
echo "Agents: SITEHEALTH, SEOPOWER, REVENUEFUNNEL, CONTENTGUARD, PRICEVERIFY, LINKHEALTH, TRAFFICINTEL, CONTENTENGINE, REVENUEOPS"

# Phase 3: Deploy
echo ""
echo "--- Phase 3: Deploy ---"
npx netlify-cli deploy --dir . --prod

echo ""
echo "=== WEEKLY RUN COMPLETE ==="
echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

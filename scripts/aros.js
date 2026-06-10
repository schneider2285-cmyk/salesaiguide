#!/usr/bin/env node
/**
 * AROS orchestrator. v0.2.0.
 *
 * Runs each role's SAFE, read-only / reporting operation, assembles a team status
 * report, and writes it to ops/data/aros-report.json. It NEVER activates a program or
 * deploys: agents propose, only deploy.sh disposes. Money-mutating ops
 * (affiliate_manager activate) and deploys are deliberately out of scope here.
 *
 * Usage:
 *   node scripts/aros.js            run: execute safe ops, write + print the report
 *   node scripts/aros.js --dry-run  print planned actions only (no exec, no write)
 *   node scripts/aros.js --list     list agents and their tasks
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(ROOT, 'ops', 'aros', 'config', 'aros.config.json');
const REPORT = path.join(ROOT, 'ops', 'data', 'aros-report.json');

function readJSON(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { return fallback; }
}

// Run a read-only python tool. Returns exit code and captured streams.
function py(args) {
  const r = spawnSync('python3', args, { cwd: ROOT, encoding: 'utf8' });
  return {
    code: r.status === null ? 1 : r.status,
    stdout: r.stdout || '',
    stderr: r.stderr || '',
  };
}

function firstLine(s) {
  return (s || '').trim().split('\n')[0];
}

function reviewRevenue() {
  const f = readJSON(path.join(ROOT, 'ops', 'data', 'revenue-funnel.json'), null);
  if (!f || !f.summary) {
    return { id: 'revenue-analyst', tool: 'build_revenue_funnel.py', status: 'no-data',
             note: 'revenue-funnel.json missing; run npm run funnel' };
  }
  return {
    id: 'revenue-analyst', tool: 'build_revenue_funnel.py', status: 'ok',
    summary: {
      monetizableSurfaces: f.summary.monetizableSurfaces,
      trackingCoveragePercent: f.summary.trackingCoveragePercent,
      liveProgramCoveragePercent: f.summary.liveProgramCoveragePercent,
      funnelLastUpdated: f.lastUpdated,
    },
  };
}

function reviewMonetization() {
  const status = py(['scripts/affiliate_manager.py', 'status', '--json']);
  let total = 0, live = 0, parsed = false;
  try {
    const rows = JSON.parse(status.stdout);
    total = rows.length;
    live = rows.filter(function (r) { return r.status === 'live'; }).length;
    parsed = true;
  } catch (e) { /* parsed stays false; flagged below */ }
  const health = py(['scripts/affiliate_manager.py', 'health']);
  const ok = parsed && health.code === 0;
  return {
    id: 'monetization-manager', tool: 'affiliate_manager.py',
    status: ok ? 'ok' : 'issue',
    summary: { total: total, live: live, placeholder: total - live, health: health.code === 0 ? 'ok' : 'issue' },
    detail: firstLine(health.stdout) || firstLine(health.stderr),
  };
}

function reviewDistribution() {
  const valid = py(['scripts/distribution_probe.py', 'validate']);
  const tracker = path.join(ROOT, 'ops', 'distribution', 'answer-tracker.csv');
  const started = fs.existsSync(tracker);
  let verdict = null;
  if (started) {
    const scored = py(['scripts/distribution_probe.py', 'score', '--results', 'ops/distribution/answer-tracker.csv']);
    const m = scored.stdout.match(/VERDICT:\s*(\S+)/);
    verdict = m ? m[1] : null;
  }
  return {
    id: 'distribution-lead', tool: 'distribution_probe.py',
    status: valid.code === 0 ? 'ok' : 'issue',
    summary: { configValid: valid.code === 0, probeStarted: started, verdict: verdict },
    detail: firstLine(valid.stdout) || firstLine(valid.stderr),
  };
}

function notWired(id, note) {
  return { id: id, tool: null, status: 'not-wired', note: note };
}

function buildReport(stamp) {
  return {
    generatedAt: stamp,
    mode: 'report (read-only ops only; never activates or deploys)',
    guardContract: 'agents propose; only deploy.sh reaches production',
    agents: [
      reviewRevenue(),
      reviewMonetization(),
      reviewDistribution(),
      notWired('growth-engineer', 'cruft cleanup deferred by owner'),
      notWired('content-steward', 'leans on the indexation gate + bump scripts; not wired here'),
    ],
  };
}

function printSummary(report) {
  console.log('AROS team report  ' + report.generatedAt);
  console.log(report.guardContract + '\n');
  report.agents.forEach(function (a) {
    console.log('  [' + a.status + '] ' + a.id + (a.tool ? '  (' + a.tool + ')' : ''));
    if (a.summary) console.log('      ' + JSON.stringify(a.summary));
    if (a.detail) console.log('      ' + a.detail);
    if (a.note) console.log('      ' + a.note);
  });
}

function main() {
  const argv = process.argv.slice(2);
  const cfg = readJSON(CONFIG, null);
  if (!cfg) {
    console.error('AROS: cannot read config at ' + CONFIG);
    process.exit(1);
  }

  if (argv.indexOf('--list') !== -1) {
    cfg.agents.forEach(function (a) {
      console.log('- ' + a.id + ': ' + (a.tasks || []).join(', '));
    });
    return;
  }

  if (argv.indexOf('--dry-run') !== -1) {
    console.log('AROS ' + cfg.version + ' dry-run. Would run each role\'s safe read-only op and write '
      + path.relative(ROOT, REPORT) + '. Nothing executed.');
    cfg.agents.forEach(function (a) {
      console.log('  ' + a.id + ': ' + (a.tasks || []).join(', '));
    });
    return;
  }

  // Real run: safe read-only ops + write the report. No activation, no deploy.
  const stamp = new Date().toISOString();
  const report = buildReport(stamp);
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n');
  printSummary(report);
  console.log('\nWrote ' + path.relative(ROOT, REPORT) + '. No program activated, nothing deployed.');
}

main();

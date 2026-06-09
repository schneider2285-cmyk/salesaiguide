#!/usr/bin/env node
/**
 * AROS orchestrator. SCAFFOLD v0.1.0.
 *
 * Side-effect-free. Reads ops/aros/config/aros.config.json and ops/data state,
 * then prints what each agent WOULD do. It does NOT implement any fix, write any
 * file, make any network call, or deploy. All real changes flow through deploy.sh.
 *
 * Usage:
 *   node scripts/aros.js                       dry-run, all agents
 *   node scripts/aros.js --list                list agents and tasks
 *   node scripts/aros.js --agent revenue-analyst
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(ROOT, 'ops', 'aros', 'config', 'aros.config.json');

function readJSON(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { return fallback; }
}

function parseArgs(argv) {
  const args = { dryRun: true, agent: null, list: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--agent') args.agent = argv[++i];
    else if (a === '--list') args.list = true;
    else if (a === '--no-dry-run' || a === '--apply') args.dryRun = false;
  }
  return args;
}

function main() {
  const args = parseArgs(process.argv);
  const cfg = readJSON(CONFIG, null);
  if (!cfg) {
    console.error('AROS: cannot read config at ' + CONFIG);
    process.exit(1);
  }

  console.log('AROS ' + cfg.version + ' (scaffold). No fixes are implemented.');
  console.log('Guard contract: agents propose; only ' + cfg.guards.deployOnlyVia + ' reaches production.\n');

  if (args.list) {
    cfg.agents.forEach(function (a) {
      console.log('- ' + a.id + ': ' + (a.tasks || []).join(', '));
    });
    return;
  }

  // SAFETY: this scaffold refuses to apply. Real execution is not wired.
  if (!args.dryRun) {
    console.log('Apply mode requested, but this scaffold has no executors wired.');
    console.log('Refusing to act. Use deploy.sh for any real change.\n');
  }

  const agents = args.agent
    ? cfg.agents.filter(function (a) { return a.id === args.agent; })
    : cfg.agents;

  if (args.agent && agents.length === 0) {
    console.error('Unknown agent: ' + args.agent);
    process.exit(1);
  }

  const stateDir = path.join(ROOT, cfg.stateDir);
  agents.forEach(function (a) {
    console.log('# ' + a.id);
    (a.owns || []).forEach(function (f) {
      const exists = fs.existsSync(path.join(stateDir, f));
      console.log('  state ' + cfg.stateDir + '/' + f + ': ' + (exists ? 'present' : 'MISSING'));
    });
    (a.sources || []).forEach(function (f) {
      const exists = fs.existsSync(path.join(ROOT, f));
      console.log('  source ' + f + ': ' + (exists ? 'present' : 'MISSING'));
    });
    (a.tasks || []).forEach(function (t) {
      console.log('  would plan: ' + t + ' (not executed)');
    });
    console.log('');
  });

  console.log('Dry-run complete. No files written, no network, no deploy.');
}

main();

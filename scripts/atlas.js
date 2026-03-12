#!/usr/bin/env node
/**
 * ATLAS - Automated Testing, Linking, Auditing & Strategy
 * Lead agent orchestrator. Runs 8 sequential phases.
 * See: docs/superpowers/specs/2026-03-12-atlas-lead-agent-design.md
 *
 * Security: All child_process calls use hardcoded strings with no user input.
 */

var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');

var SITE_ROOT = path.resolve(__dirname, '..');
var DATA_DIR = path.join(SITE_ROOT, 'ops', 'data');
var DRY_RUN = process.env.ATLAS_DRY_RUN === 'true';

var SCORE_WEIGHTS = {
  revenuefunnel: 0.30,
  seopower: 0.20,
  sitehealth: 0.15,
  contentguard: 0.15,
  linkhealth: 0.10,
  priceverify: 0.10
};

var ALLOWED_STAGE_PATHS = [
  'tools/', 'best/', 'alternatives/', 'categories/', 'compare/',
  'pricing/', 'index.html', 'ops/data/', '404.html'
];

var PROTECTED_PATHS = ['.github/', 'scripts/', 'ops/js/', 'ops/css/', 'ops/index.html'];

var NAME_LEAK_PATTERNS = [/Matt\s/gi, /Matthew/gi, /Schneider/gi, /Toptal/gi];

function log(phase, msg) {
  console.log('[ATLAS:' + phase + '] ' + msg);
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

function run(cmd, opts) {
  var defaults = { cwd: SITE_ROOT, encoding: 'utf8', timeout: 120000 };
  if (opts) {
    var keys = Object.keys(opts);
    for (var i = 0; i < keys.length; i++) defaults[keys[i]] = opts[keys[i]];
  }
  return childProcess.execSync(cmd, defaults);
}

// Phase 1: AUTO-FIX (pre-audit)
function phase1() {
  log('P1', 'Running pre-audit auto-fix...');
  try {
    run('node scripts/agent-autofix.js');
    log('P1', 'Auto-fix complete.');
    return true;
  } catch (e) {
    log('P1', 'Auto-fix failed: ' + e.message);
    return false;
  }
}

// Phase 2: AUDIT (9 agents)
async function phase2() {
  log('P2', 'Running 9 audit agents...');
  var agentFiles = [
    '01-sitehealth', '02-revenuefunnel', '03-linkhealth',
    '04-priceverify', '05-contentguard', '06-seopower',
    '07-trafficintel', '08-contentengine', '09-revenueops'
  ];

  var results = {};

  for (var i = 0; i < agentFiles.length; i++) {
    var name = agentFiles[i];
    var agentKey = name.replace(/^\d+-/, '');
    log('P2', 'Running ' + name + '...');
    try {
      var agentFn = require(path.join(__dirname, 'agents', name + '.js'));
      var result = agentKey === 'revenueops'
        ? await agentFn(SITE_ROOT, results)
        : await agentFn(SITE_ROOT);
      results[agentKey] = result;
      log('P2', '  ' + agentKey + ': score=' + result.score + ', status=' + result.status);
    } catch (e) {
      log('P2', '  ' + agentKey + ' FAILED: ' + e.message);
      results[agentKey] = {
        agent: agentKey, status: 'critical', score: 0,
        metrics: {}, issues: [{ check: 'agent_error', severity: 'critical', detail: e.message }],
        lastAction: 'Agent failed: ' + e.message
      };
    }
  }

  return results;
}

// Phase 3: DECIDE
function phase3(results) {
  log('P3', 'Building fix plan...');
  var fixPlan = [];

  var keys = Object.keys(results);
  for (var i = 0; i < keys.length; i++) {
    var result = results[keys[i]];
    if (!result.issues) continue;
    for (var j = 0; j < result.issues.length; j++) {
      var issue = result.issues[j];
      if (issue.severity === 'critical' || issue.severity === 'high') {
        fixPlan.push({
          file: issue.detail.split(':')[0] || '',
          fix_type: issue.check,
          details: issue.detail,
          priority: 'P0'
        });
      } else if (issue.severity === 'med') {
        fixPlan.push({
          file: issue.detail.split(':')[0] || '',
          fix_type: issue.check,
          details: issue.detail,
          priority: 'P1'
        });
      }
    }
  }

  fixPlan.sort(function(a, b) { return a.priority.localeCompare(b.priority); });

  if (fixPlan.length > 200) {
    var trimmed = fixPlan.filter(function(f) { return f.priority === 'P0' || f.priority === 'P1'; });
    log('P3', 'Fix plan trimmed from ' + fixPlan.length + ' to ' + trimmed.length + ' (P0+P1 only)');
    return trimmed;
  }

  log('P3', 'Fix plan: ' + fixPlan.length + ' items');
  return fixPlan;
}

// Phase 4: FIX (post-audit)
function phase4(fixPlan) {
  if (fixPlan.length === 0) {
    log('P4', 'No fixes to apply.');
    return;
  }

  log('P4', 'Applying ' + fixPlan.length + ' targeted fixes...');
  var planPath = path.join(DATA_DIR, 'fix-plan.json');
  writeJson(planPath, fixPlan);

  try {
    run('node scripts/agent-autofix.js --fix-plan ' + planPath);
    log('P4', 'Targeted fixes applied.');
  } catch (e) {
    log('P4', 'Targeted fix failed: ' + e.message);
  }
}

// Phase 5: VALIDATE
function phase5() {
  log('P5', 'Running validation checks...');

  var scanner = require('./agents/lib/html-scanner');
  var files = scanner.getAllHtmlFiles(SITE_ROOT);
  for (var i = 0; i < files.length; i++) {
    var html = scanner.readHtml(files[i].abs);
    var visibleText = html.replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ');

    for (var j = 0; j < NAME_LEAK_PATTERNS.length; j++) {
      NAME_LEAK_PATTERNS[j].lastIndex = 0;
      if (NAME_LEAK_PATTERNS[j].test(visibleText)) {
        log('P5', 'CRITICAL: Name leak found in ' + files[i].rel + '! Rolling back.');
        return { valid: false, reason: 'Name leak in ' + files[i].rel };
      }
    }
  }

  log('P5', 'Validation passed.');
  return { valid: true };
}

// Phase 6: UPDATE
function phase6(results, previousState) {
  log('P6', 'Updating data files...');

  var overall = 0;
  var weightKeys = Object.keys(SCORE_WEIGHTS);
  for (var w = 0; w < weightKeys.length; w++) {
    var agent = weightKeys[w];
    var weight = SCORE_WEIGHTS[agent];
    var result = results[agent];
    if (result && typeof result.score === 'number') {
      overall += result.score * weight;
    }
  }
  overall = Math.round(overall);

  var state = previousState || {};
  var runCount = (state.runCount || 0) + 1;
  state.lastRun = new Date().toISOString();
  state.runCount = runCount;
  state.overallScore = overall;

  if (!state.agents) state.agents = {};
  var resultKeys = Object.keys(results);
  for (var i = 0; i < resultKeys.length; i++) {
    var key = resultKeys[i];
    var r = results[key];
    var existing = state.agents[key] || {};
    state.agents[key] = {
      name: existing.name || key.toUpperCase(),
      icon: existing.icon || '',
      description: existing.description || '',
      lastAction: r.lastAction,
      plan: existing.plan || {},
      status: r.status,
      lastRun: new Date().toISOString(),
      metrics: r.metrics,
      issues: r.issues.slice(0, 20),
      score: r.score
    };
  }

  writeJson(path.join(DATA_DIR, 'agent-state.json'), state);

  // Update history
  var historyPath = path.join(DATA_DIR, 'history.json');
  var history;
  try { history = readJson(historyPath); } catch (e) { history = { runs: [] }; }
  var agentScores = {};
  var totalFound = 0;
  var totalFixed = 0;
  for (var h = 0; h < resultKeys.length; h++) {
    var rr = results[resultKeys[h]];
    agentScores[resultKeys[h]] = rr.score;
    totalFound += (rr.issues || []).length;
    if (rr.metrics && typeof rr.metrics.issuesFixed === 'number') totalFixed += rr.metrics.issuesFixed;
  }
  history.runs.push({
    date: new Date().toISOString().split('T')[0],
    runNumber: runCount,
    overallScore: overall,
    issuesFound: totalFound,
    issuesFixed: totalFixed,
    topAction: 'Weekly cycle #' + runCount + ' \u2014 score ' + overall + '/100',
    agentScores: agentScores
  });
  writeJson(historyPath, history);

  // Update activity log
  var activityPath = path.join(DATA_DIR, 'activity-log.json');
  var activity;
  try { activity = readJson(activityPath); } catch (e) { activity = { lastUpdated: '', entries: [] }; }
  var now = new Date().toISOString();
  activity.lastUpdated = now;
  for (var a = 0; a < resultKeys.length; a++) {
    var ar = results[resultKeys[a]];
    if (ar.lastAction) {
      activity.entries.unshift({
        timestamp: now,
        agent: resultKeys[a],
        icon: (state.agents[resultKeys[a]] && state.agents[resultKeys[a]].icon) || '',
        action: ar.lastAction,
        type: ar.issues.length > 0 ? 'fix' : 'audit',
        impact: 'Score: ' + (ar.score !== null ? ar.score : 'N/A')
      });
    }
  }
  activity.entries = activity.entries.slice(0, 50);
  writeJson(activityPath, activity);

  log('P6', 'Data updated. Overall score: ' + overall + '. Run #' + runCount + '.');
  return { overall: overall, runCount: runCount, totalFound: totalFound, totalFixed: totalFixed };
}

// Phase 7: COMMIT + DEPLOY
function phase7(runCount, overall, issuesFixed) {
  if (DRY_RUN) {
    log('P7', 'DRY RUN \u2014 skipping commit and deploy.');
    try {
      var diff = run('git diff --stat');
      log('P7', 'Would commit:\n' + diff);
    } catch (e) { /* ignore */ }
    return 'skipped';
  }

  log('P7', 'Staging and committing changes...');

  try {
    for (var i = 0; i < ALLOWED_STAGE_PATHS.length; i++) {
      try {
        run('git add ' + ALLOWED_STAGE_PATHS[i]);
      } catch (e) { /* path may not exist */ }
    }

    var staged = run('git diff --cached --name-only');
    var stagedFiles = staged.split('\n').filter(Boolean);
    for (var j = 0; j < stagedFiles.length; j++) {
      var file = stagedFiles[j];
      for (var k = 0; k < PROTECTED_PATHS.length; k++) {
        if (file.indexOf(PROTECTED_PATHS[k]) === 0) {
          log('P7', 'WARNING: unstaging protected file: ' + file);
          run('git reset HEAD -- "' + file + '"');
          break;
        }
      }
    }

    var cachedDiff = run('git diff --cached --stat');
    if (!cachedDiff.trim()) {
      log('P7', 'No changes to commit.');
      return 'no_changes';
    }

    log('P7', cachedDiff);

    var msg = 'atlas: weekly cycle #' + runCount + ' \u2014 score ' + overall + '/100, ' + issuesFixed + ' issues fixed';
    run('git commit -m "' + msg + '"');
    log('P7', 'Committed.');

    log('P7', 'Skipping CLI deploy — Netlify auto-deploys from git push.');
    return 'success';
  } catch (e) {
    log('P7', 'Commit/deploy failed: ' + e.message);
    return 'failed';
  }
}

// Phase 8: REPORT (always runs, even after rollback)
function phase8(status, runCount, overall, previousScore, results, filesChanged, deployStatus, failureReason, startTime) {
  var report = {
    runNumber: runCount,
    timestamp: new Date().toISOString(),
    durationMs: Date.now() - startTime,
    status: status,
    overallScore: { before: previousScore, after: overall },
    issuesByAgent: {},
    filesChanged: filesChanged,
    deployStatus: deployStatus,
    failureReason: failureReason
  };

  var keys = Object.keys(results);
  for (var i = 0; i < keys.length; i++) {
    var r = results[keys[i]];
    report.issuesByAgent[keys[i]] = {
      found: (r.issues || []).length,
      fixed: (r.metrics && r.metrics.issuesFixed) || 0
    };
  }

  writeJson(path.join(DATA_DIR, 'last-run-report.json'), report);
  log('P8', 'Report written. Status: ' + status + '. Duration: ' + report.durationMs + 'ms.');
  return report;
}

// Main
async function main() {
  var startTime = Date.now();
  log('MAIN', '=== ATLAS Weekly Cycle ===');
  log('MAIN', 'Started: ' + new Date().toISOString());
  if (DRY_RUN) log('MAIN', 'DRY RUN MODE \u2014 no commit or deploy');

  var statePath = path.join(DATA_DIR, 'agent-state.json');
  var previousState = {};
  var previousScore = 0;
  try {
    previousState = readJson(statePath);
    previousScore = previousState.overallScore || 0;
  } catch (e) { /* first run */ }

  var runCount = (previousState.runCount || 0) + 1;

  // Phase 1
  phase1();

  // Phase 2
  var results = await phase2();

  // Phase 3
  var fixPlan = phase3(results);

  // Phase 4
  phase4(fixPlan);

  // Phase 5
  var validation = phase5();
  if (!validation.valid) {
    log('MAIN', 'VALIDATION FAILED \u2014 rolling back.');
    try {
      run('git checkout -- .');
    } catch (e) { /* ignore */ }
    phase8('rolled_back', runCount, 0, previousScore, results, 0, 'skipped', validation.reason, startTime);
    process.exit(1);
  }

  // Phase 6
  var p6 = phase6(results, previousState);

  // Phase 7
  var filesChanged = 0;
  try {
    var stat = run('git diff --stat');
    var fMatch = stat.match(/(\d+) file/);
    filesChanged = fMatch ? parseInt(fMatch[1], 10) : 0;
  } catch (e) { /* ignore */ }

  var deployStatus = phase7(p6.runCount, p6.overall, p6.totalFixed);

  // Phase 8
  var finalStatus = deployStatus === 'failed' ? 'failed' : 'success';
  phase8(finalStatus, p6.runCount, p6.overall, previousScore, results, filesChanged,
    DRY_RUN ? 'skipped' : deployStatus, null, startTime);

  log('MAIN', '=== ATLAS Complete. Score: ' + p6.overall + '/100 ===');
}

main().catch(function(e) {
  console.error('[ATLAS:FATAL]', e);
  process.exit(1);
});

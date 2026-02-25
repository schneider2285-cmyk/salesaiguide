/**
 * Seed script — populates the SQLite database with initial data.
 *
 * 1. Parses tasks from _private/progress.html
 * 2. Seeds baseline metrics
 * 3. Seeds affiliate status entries
 * 4. Seeds baseline agent runs from Feb 24, 2026
 *
 * Usage: node db/seed.js
 */

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'salesaiguide.db');
const SCHEMA_PATH = path.join(__dirname, 'schema.sql');
const PROGRESS_PATH = path.join(__dirname, '..', '..', '_private', 'progress.html');

// ---------------------------------------------------------------------------
// Init database
// ---------------------------------------------------------------------------
console.log('Initializing database...');

// Remove old DB if it exists (clean seed)
if (fs.existsSync(DB_PATH)) {
  fs.unlinkSync(DB_PATH);
  console.log('  Removed existing database');
}

const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('busy_timeout = 5000');

// Run schema — strip comments, then run each statement
const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
const cleanSchema = schema.replace(/--[^\n]*/g, ''); // strip SQL comments
cleanSchema.split(';').filter(s => s.trim()).forEach(stmt => {
  const trimmed = stmt.trim();
  if (trimmed) {
    db.prepare(trimmed + ';').run();
  }
});
console.log('  Schema created');

// ---------------------------------------------------------------------------
// 1. Parse and seed tasks from progress.html
// ---------------------------------------------------------------------------
console.log('\nSeeding tasks from progress.html...');

const html = fs.readFileSync(PROGRESS_PATH, 'utf-8');

// Extract the phases array from the JS code
const phasesStart = html.indexOf('const phases = [');
if (phasesStart === -1) {
  console.error('ERROR: Could not find "const phases = [" in progress.html');
  process.exit(1);
}

// Find the end: look for "];\n\nconst agentIds" which follows the phases array
const endMarker = html.indexOf('const agentIds', phasesStart);
if (endMarker === -1) {
  console.error('ERROR: Could not find "const agentIds" after phases array');
  process.exit(1);
}

// The "];" is right before agentIds — find the last "];" before endMarker
const searchRegion = html.substring(phasesStart, endMarker);
const lastBracket = searchRegion.lastIndexOf('];');
if (lastBracket === -1) {
  console.error('ERROR: Could not find end of phases array');
  process.exit(1);
}

const arrayStart = html.indexOf('[', phasesStart);
const phasesStr = html.substring(arrayStart, phasesStart + lastBracket + 1);

const insertTask = db.prepare(`
  INSERT OR REPLACE INTO tasks (id, phase, phase_label, label, done, owner, updated_at)
  VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
`);

const insertMany = db.transaction((tasks) => {
  for (const task of tasks) {
    insertTask.run(task.id, task.phase, task.phase_label, task.label, task.done, task.owner);
  }
});

// Parse phases using regex extraction via matchAll
const tasks = [];

// First pass: collect all phase info with their positions
const phasePattern = /id:\s*'([^']+)',\s*\n?\s*label:\s*'([^']+)',\s*\n?\s*title:\s*'([^']+)'/g;
const phaseInfo = [];
for (const m of phasesStr.matchAll(phasePattern)) {
  phaseInfo.push({
    id: m[1],
    label: m[2],
    title: m[3],
    position: m.index
  });
}

// Match individual tasks within each phase section
const taskPattern = /\{\s*id:\s*'([^']+)',\s*text:\s*'([^']*(?:\\'[^']*)*)',\s*who:\s*'([^']+)',\s*done:\s*(true|false)/g;

for (let i = 0; i < phaseInfo.length; i++) {
  const phase = phaseInfo[i];
  const startPos = phase.position;
  const endPos = (i + 1 < phaseInfo.length) ? phaseInfo[i + 1].position : phasesStr.length;
  const phaseSlice = phasesStr.substring(startPos, endPos);

  for (const localMatch of phaseSlice.matchAll(taskPattern)) {
    const taskId = localMatch[1];
    const taskText = localMatch[2].replace(/\\'/g, "'");
    const who = localMatch[3];
    const done = localMatch[4] === 'true' ? 1 : 0;

    // Map owner
    let owner = 'claude';
    if (who === 'matt') owner = 'matt';
    else if (who === 'manus') owner = 'manus';

    tasks.push({
      id: taskId,
      phase: phase.id,
      phase_label: `${phase.label}: ${phase.title}`,
      label: taskText,
      done: done,
      owner: owner
    });
  }
}

insertMany(tasks);
console.log(`  Inserted ${tasks.length} tasks`);

// Count done tasks
const doneCount = tasks.filter(t => t.done === 1).length;
console.log(`  Done: ${doneCount}/${tasks.length} (${Math.round(doneCount/tasks.length*100)}%)`);

// ---------------------------------------------------------------------------
// 2. Seed metrics
// ---------------------------------------------------------------------------
console.log('\nSeeding metrics...');

const insertMetric = db.prepare(`
  INSERT OR REPLACE INTO metrics (key, value, label, updated_at)
  VALUES (?, ?, ?, CURRENT_TIMESTAMP)
`);

const metricsData = [
  { key: 'total_pages', value: 101, label: 'Total Pages Built' },
  { key: 'tool_reviews', value: 20, label: 'Tool Review Pages' },
  { key: 'comparison_pages', value: 52, label: 'Comparison Pages' },
  { key: 'category_pages', value: 14, label: 'Category Pages' },
  { key: 'persona_pages', value: 3, label: 'Persona Hub Pages' },
  { key: 'guide_pages', value: 2, label: 'Guide Pages' },
  { key: 'active_affiliates', value: 1, label: 'Active Affiliates' },
  { key: 'agents_baselined', value: 8, label: 'Agents Baselined' }
];

for (const m of metricsData) {
  insertMetric.run(m.key, JSON.stringify(m.value), m.label);
}
console.log(`  Inserted ${metricsData.length} metrics`);

// ---------------------------------------------------------------------------
// 3. Seed affiliate status
// ---------------------------------------------------------------------------
console.log('\nSeeding affiliate status...');

const insertAffiliate = db.prepare(`
  INSERT OR REPLACE INTO affiliate_status (tool, redirect_url, has_affiliate_param, status, commission, last_checked, notes)
  VALUES (?, ?, ?, ?, ?, ?, ?)
`);

const affiliateData = [
  { tool: 'clay', redirect_url: 'https://clay.earth/?via=matthew-schneider', has_affiliate_param: 1, status: 'active', commission: '~$30/conversion', last_checked: '2026-02-24', notes: 'Approved Feb 24 — redirect live at /go/clay' },
  { tool: 'apollo', redirect_url: 'https://apollo.io', has_affiliate_param: 0, status: 'pending', commission: '~$20/conversion', last_checked: '2026-02-24', notes: 'Application pending' },
  { tool: 'instantly', redirect_url: 'https://instantly.ai', has_affiliate_param: 0, status: 'pending', commission: '~$11/conversion', last_checked: '2026-02-24', notes: 'Application pending' },
  { tool: 'hubspot', redirect_url: 'https://hubspot.com', has_affiliate_param: 0, status: 'pending', commission: '~$30+/conversion', last_checked: '2026-02-24', notes: 'LinkedIn verification required' },
  { tool: 'gong', redirect_url: 'https://gong.io', has_affiliate_param: 0, status: 'no_program', commission: null, last_checked: '2026-02-24', notes: null },
  { tool: 'outreach', redirect_url: 'https://outreach.io', has_affiliate_param: 0, status: 'no_program', commission: null, last_checked: '2026-02-24', notes: null },
  { tool: 'salesloft', redirect_url: 'https://salesloft.com', has_affiliate_param: 0, status: 'no_program', commission: null, last_checked: '2026-02-24', notes: null },
  { tool: 'zoominfo', redirect_url: 'https://zoominfo.com', has_affiliate_param: 0, status: 'no_program', commission: null, last_checked: '2026-02-24', notes: null },
  { tool: 'lavender', redirect_url: 'https://lavender.ai', has_affiliate_param: 0, status: 'pending', commission: null, last_checked: '2026-02-24', notes: 'Check program availability' },
  { tool: 'smartlead', redirect_url: 'https://smartlead.ai', has_affiliate_param: 0, status: 'pending', commission: null, last_checked: '2026-02-24', notes: 'Check program availability' },
  { tool: 'loom', redirect_url: 'https://loom.com', has_affiliate_param: 0, status: 'no_program', commission: null, last_checked: '2026-02-24', notes: null }
];

for (const a of affiliateData) {
  insertAffiliate.run(a.tool, a.redirect_url, a.has_affiliate_param, a.status, a.commission, a.last_checked, a.notes);
}
console.log(`  Inserted ${affiliateData.length} affiliate entries`);

// ---------------------------------------------------------------------------
// 4. Seed baseline agent runs (Feb 24, 2026)
// ---------------------------------------------------------------------------
console.log('\nSeeding baseline agent runs...');

const insertRun = db.prepare(`
  INSERT INTO agent_runs (agent_id, agent_name, run_date, status, summary, findings, actions_required)
  VALUES (?, ?, ?, ?, ?, ?, ?)
`);

const agentRuns = [
  {
    agent_id: 'site-validator',
    agent_name: 'Site Validator',
    run_date: '2026-02-24',
    status: 'ok',
    summary: '77/77 pages passing. No regressions.',
    findings: [{ type: 'info', message: 'All 20 tool pages have journey bar, dual scores, evidence drawers' }],
    actions_required: []
  },
  {
    agent_id: 'evidence-refresher',
    agent_name: 'Evidence Refresher',
    run_date: '2026-02-24',
    status: 'action_required',
    summary: 'Gong rating dropped 4.8 to 4.7. 4 tools have review count drift.',
    findings: [
      { type: 'warning', message: 'Gong G2 rating dropped from 4.8 to 4.7' },
      { type: 'info', message: '4 tools have minor review count differences vs G2' }
    ],
    actions_required: ['Update gong.json G2 rating to 4.7', 'Add lastVerified timestamps to all 10 tool JSONs']
  },
  {
    agent_id: 'affiliate-health',
    agent_name: 'Affiliate Health Monitor',
    run_date: '2026-02-24',
    status: 'warning',
    summary: '1/11 redirects have affiliate tracking. 3 programs pending application.',
    findings: [
      { type: 'ok', message: 'Clay redirect live with affiliate param' },
      { type: 'warning', message: 'Apollo, Instantly, HubSpot applications still pending' }
    ],
    actions_required: ['Follow up on Apollo affiliate application', 'Follow up on Instantly affiliate application']
  },
  {
    agent_id: 'seo-monitor',
    agent_name: 'SEO Performance Monitor',
    run_date: '2026-02-24',
    status: 'ok',
    summary: 'Search Console connected. 9 URLs indexed. Awaiting first impression data.',
    findings: [
      { type: 'info', message: '9 URLs submitted and indexed in Google Search Console' },
      { type: 'info', message: 'First impression data expected by March 3' }
    ],
    actions_required: []
  },
  {
    agent_id: 'competitor-intel',
    agent_name: 'Competitor Intelligence',
    run_date: '2026-02-24',
    status: 'warning',
    summary: 'marketbetter.ai published 4 tool reviews targeting our keywords.',
    findings: [
      { type: 'warning', message: 'marketbetter.ai identified as primary competitor' },
      { type: 'info', message: 'Saleshandy and Lemlist coverage gaps identified for Phase 7' }
    ],
    actions_required: []
  },
  {
    agent_id: 'new-tool-scout',
    agent_name: 'New Tool Scout',
    run_date: '2026-02-24',
    status: 'ok',
    summary: 'Saleshandy and Lemlist flagged for Phase 7 page build.',
    findings: [
      { type: 'info', message: 'Saleshandy: high search volume, direct competitor to Instantly' },
      { type: 'info', message: 'Lemlist: growing market share in cold outreach category' }
    ],
    actions_required: []
  },
  {
    agent_id: 'revenue-optimization',
    agent_name: 'Revenue Optimization',
    run_date: '2026-02-24',
    status: 'ok',
    summary: 'No traffic data yet. Clay is only active affiliate.',
    findings: [
      { type: 'info', message: 'Clay affiliate is only active revenue source' },
      { type: 'info', message: 'No organic traffic data available yet — site too new' }
    ],
    actions_required: []
  },
  {
    agent_id: 'growth-strategy',
    agent_name: 'Growth Strategy',
    run_date: '2026-02-24',
    status: 'ok',
    summary: '90-day forecast written. First organic traffic expected March to April.',
    findings: [
      { type: 'info', message: '90-day growth forecast completed' },
      { type: 'info', message: 'Phase 7 roadmap defined: Saleshandy + Lemlist pages' }
    ],
    actions_required: []
  }
];

for (const run of agentRuns) {
  insertRun.run(
    run.agent_id,
    run.agent_name,
    run.run_date,
    run.status,
    run.summary,
    JSON.stringify(run.findings),
    JSON.stringify(run.actions_required)
  );
}
console.log(`  Inserted ${agentRuns.length} agent runs`);

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------
console.log('\n--- Seed Complete ---');
console.log(`Tasks:      ${tasks.length}`);
console.log(`Metrics:    ${metricsData.length}`);
console.log(`Affiliates: ${affiliateData.length}`);
console.log(`Agent runs: ${agentRuns.length}`);
console.log(`Database:   ${DB_PATH}`);

db.close();

/**
 * SalesAIGuide Operations Dashboard — API Server
 *
 * Express + SQLite backend serving 5 REST endpoints.
 * Agents POST results after each run; frontend GETs full state.
 *
 * Endpoints:
 *   GET  /health                        → health check
 *   GET  /api/dashboard/status           → full dashboard state
 *   POST /api/dashboard/agent-run        → log an agent run
 *   POST /api/dashboard/task-update      → mark task done/undone
 *   POST /api/dashboard/metric-update    → upsert a metric
 *   POST /api/dashboard/affiliate-update → upsert affiliate status
 */

const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const PORT = process.env.PORT || 3001;
const API_KEY = 'SAG-DASH-2026';
const DB_PATH = path.join(__dirname, 'db', 'salesaiguide.db');
const SCHEMA_PATH = path.join(__dirname, 'db', 'schema.sql');

// ---------------------------------------------------------------------------
// Database init
// ---------------------------------------------------------------------------
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('busy_timeout = 5000');

// Run schema if tables don't exist — strip comments, then run each statement
const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
const cleanSchema = schema.replace(/--[^\n]*/g, '');
cleanSchema.split(';').filter(s => s.trim()).forEach(stmt => {
  const trimmed = stmt.trim();
  if (trimmed) {
    db.prepare(trimmed + ';').run();
  }
});

// ---------------------------------------------------------------------------
// Express app
// ---------------------------------------------------------------------------
const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// ---------------------------------------------------------------------------
// Auth middleware for POST endpoints
// ---------------------------------------------------------------------------
function requireApiKey(req, res, next) {
  const key = req.headers['x-api-key'] || (req.body && req.body.api_key);
  if (key !== API_KEY) {
    return res.status(401).json({ error: 'Invalid or missing API key' });
  }
  next();
}

// ---------------------------------------------------------------------------
// GET /health
// ---------------------------------------------------------------------------
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// GET /api/dashboard/status
// Returns the full dashboard state in one call.
// ---------------------------------------------------------------------------
app.get('/api/dashboard/status', (_req, res) => {
  try {
    // --- Agents: latest run per agent ---
    const latestRuns = db.prepare(`
      SELECT ar.*
      FROM agent_runs ar
      INNER JOIN (
        SELECT agent_id, MAX(id) as max_id
        FROM agent_runs
        GROUP BY agent_id
      ) latest ON ar.id = latest.max_id
      ORDER BY ar.agent_id
    `).all();

    const agents = latestRuns.map(r => ({
      agent_id: r.agent_id,
      agent_name: r.agent_name,
      run_date: r.run_date,
      status: r.status,
      summary: r.summary,
      findings: safeJsonParse(r.findings, []),
      actions_required: safeJsonParse(r.actions_required, []),
      created_at: r.created_at
    }));

    // --- Tasks: summary + by phase ---
    const taskTotals = db.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as done
      FROM tasks
    `).get();

    const tasksByPhase = db.prepare(`
      SELECT
        phase,
        phase_label,
        COUNT(*) as total,
        SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as done
      FROM tasks
      GROUP BY phase
      ORDER BY phase
    `).all();

    const allTasks = db.prepare(`
      SELECT id, phase, phase_label, label, done, owner, updated_at
      FROM tasks
      ORDER BY phase, id
    `).all();

    // --- Metrics ---
    const metricsRows = db.prepare('SELECT * FROM metrics ORDER BY key').all();
    const metrics = {};
    metricsRows.forEach(m => {
      metrics[m.key] = {
        value: safeJsonParse(m.value, m.value),
        label: m.label,
        updated_at: m.updated_at
      };
    });

    // --- Affiliates ---
    const affiliates = db.prepare('SELECT * FROM affiliate_status ORDER BY tool').all();

    // --- Agent runs this week ---
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const runsThisWeek = db.prepare(`
      SELECT COUNT(*) as count FROM agent_runs
      WHERE created_at >= ?
    `).get(weekAgo.toISOString()).count;

    // --- Recent activity (last 20 runs) ---
    const recentActivity = db.prepare(`
      SELECT * FROM agent_runs ORDER BY id DESC LIMIT 20
    `).all().map(r => ({
      ...r,
      findings: safeJsonParse(r.findings, []),
      actions_required: safeJsonParse(r.actions_required, [])
    }));

    res.json({
      agents,
      tasks: {
        total: taskTotals.total,
        done: taskTotals.done,
        by_phase: tasksByPhase,
        all: allTasks
      },
      metrics,
      affiliates,
      runs_this_week: runsThisWeek,
      recent_activity: recentActivity,
      last_updated: new Date().toISOString()
    });
  } catch (err) {
    console.error('GET /api/dashboard/status error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/dashboard/agent-run
// ---------------------------------------------------------------------------
app.post('/api/dashboard/agent-run', requireApiKey, (req, res) => {
  try {
    const { agent_id, agent_name, run_date, status, summary, findings, actions_required } = req.body;

    if (!agent_id || !agent_name || !run_date || !status || !summary) {
      return res.status(400).json({ error: 'Missing required fields: agent_id, agent_name, run_date, status, summary' });
    }

    const validStatuses = ['ok', 'warning', 'action_required', 'error'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` });
    }

    const stmt = db.prepare(`
      INSERT INTO agent_runs (agent_id, agent_name, run_date, status, summary, findings, actions_required)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      agent_id,
      agent_name,
      run_date,
      status,
      summary,
      JSON.stringify(findings || []),
      JSON.stringify(actions_required || [])
    );

    res.json({ success: true, id: result.lastInsertRowid });
  } catch (err) {
    console.error('POST /api/dashboard/agent-run error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/dashboard/task-update
// ---------------------------------------------------------------------------
app.post('/api/dashboard/task-update', requireApiKey, (req, res) => {
  try {
    const { task_id, done } = req.body;

    if (!task_id || done === undefined) {
      return res.status(400).json({ error: 'Missing required fields: task_id, done' });
    }

    const stmt = db.prepare(`
      UPDATE tasks SET done = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    `);

    const result = stmt.run(done ? 1 : 0, task_id);

    if (result.changes === 0) {
      return res.status(404).json({ error: `Task not found: ${task_id}` });
    }

    res.json({ success: true, task_id, done: !!done });
  } catch (err) {
    console.error('POST /api/dashboard/task-update error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/dashboard/metric-update
// ---------------------------------------------------------------------------
app.post('/api/dashboard/metric-update', requireApiKey, (req, res) => {
  try {
    const { key, value, label } = req.body;

    if (!key || value === undefined || !label) {
      return res.status(400).json({ error: 'Missing required fields: key, value, label' });
    }

    const stmt = db.prepare(`
      INSERT INTO metrics (key, value, label, updated_at)
      VALUES (?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET
        value = excluded.value,
        label = excluded.label,
        updated_at = CURRENT_TIMESTAMP
    `);

    stmt.run(key, JSON.stringify(value), label);
    res.json({ success: true, key, value });
  } catch (err) {
    console.error('POST /api/dashboard/metric-update error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/dashboard/affiliate-update
// ---------------------------------------------------------------------------
app.post('/api/dashboard/affiliate-update', requireApiKey, (req, res) => {
  try {
    const { tool, redirect_url, has_affiliate_param, status, commission, notes } = req.body;

    if (!tool || !redirect_url || !status) {
      return res.status(400).json({ error: 'Missing required fields: tool, redirect_url, status' });
    }

    const validStatuses = ['active', 'pending', 'no_program', 'broken'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` });
    }

    const stmt = db.prepare(`
      INSERT INTO affiliate_status (tool, redirect_url, has_affiliate_param, status, commission, last_checked, notes)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(tool) DO UPDATE SET
        redirect_url = excluded.redirect_url,
        has_affiliate_param = excluded.has_affiliate_param,
        status = excluded.status,
        commission = excluded.commission,
        last_checked = excluded.last_checked,
        notes = excluded.notes
    `);

    stmt.run(
      tool,
      redirect_url,
      has_affiliate_param ? 1 : 0,
      status,
      commission || null,
      new Date().toISOString().split('T')[0],
      notes || null
    );

    res.json({ success: true, tool, status });
  } catch (err) {
    console.error('POST /api/dashboard/affiliate-update error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function safeJsonParse(str, fallback) {
  if (!str) return fallback;
  try { return JSON.parse(str); } catch { return fallback; }
}

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`Dashboard API running on port ${PORT}`);
  console.log(`Database: ${DB_PATH}`);
});

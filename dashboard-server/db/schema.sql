-- SalesAIGuide Operations Dashboard — Database Schema
-- WAL mode is set in code via db.pragma('journal_mode = WAL')

-- Agent run results — one row per agent execution
CREATE TABLE IF NOT EXISTS agent_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  run_date TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('ok', 'warning', 'action_required', 'error')),
  summary TEXT NOT NULL,
  findings TEXT,
  actions_required TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Build phase tasks — migrated from progress.html
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  phase TEXT NOT NULL,
  phase_label TEXT NOT NULL,
  label TEXT NOT NULL,
  done INTEGER DEFAULT 0,
  owner TEXT DEFAULT 'claude',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Key/value metrics store
CREATE TABLE IF NOT EXISTS metrics (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  label TEXT NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Affiliate redirect health tracking
CREATE TABLE IF NOT EXISTS affiliate_status (
  tool TEXT PRIMARY KEY,
  redirect_url TEXT NOT NULL,
  has_affiliate_param INTEGER DEFAULT 0,
  status TEXT NOT NULL CHECK(status IN ('active', 'pending', 'no_program', 'broken')),
  commission TEXT,
  last_checked TEXT,
  notes TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_id ON agent_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at ON agent_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_phase ON tasks(phase);
CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);

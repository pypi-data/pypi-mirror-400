"""Database schema setup.

This is a fresh schema with no migration history. Users upgrading from
older versions should delete their ~/.vibelab directory and start fresh.
"""

import sqlite3

SCHEMA_VERSION = 2

SCHEMA_SQL = """
-- Schema versioning
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Projects (multi-project support)
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Scenarios (evaluation tasks)
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    code_type TEXT NOT NULL CHECK (code_type IN ('github', 'local', 'empty')),
    code_ref TEXT,
    prompt TEXT NOT NULL,
    archived INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scenarios_project ON scenarios(project_id);

-- Results (execution outputs)
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    harness TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'timeout', 'infra_failure')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    finished_at TEXT,
    updated_at TEXT,
    duration_ms INTEGER,
    lines_added INTEGER,
    lines_removed INTEGER,
    files_changed INTEGER,
    tokens_used INTEGER,
    cost_usd REAL,
    harness_metrics TEXT,
    annotations TEXT,
    timeout_seconds INTEGER,
    driver TEXT,
    error_message TEXT,
    notes TEXT,
    quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4))
);

CREATE INDEX IF NOT EXISTS idx_results_scenario ON results(scenario_id);
CREATE INDEX IF NOT EXISTS idx_results_status ON results(status);

-- Datasets (scenario collections)
CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_datasets_project ON datasets(project_id);

-- Dataset-Scenario join table
CREATE TABLE IF NOT EXISTS dataset_scenarios (
    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    PRIMARY KEY (dataset_id, scenario_id)
);

CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_dataset ON dataset_scenarios(dataset_id);
CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_scenario ON dataset_scenarios(scenario_id);

-- LLM Judges (per-scenario evaluation)
CREATE TABLE IF NOT EXISTS llm_scenario_judges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    guidance TEXT NOT NULL,
    training_sample_ids TEXT NOT NULL,
    alignment_score REAL,
    judge_provider TEXT NOT NULL,
    judge_model TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_judges_scenario ON llm_scenario_judges(scenario_id);

-- Judgements (LLM judge outputs)
CREATE TABLE IF NOT EXISTS judgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    judge_id INTEGER NOT NULL REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
    notes TEXT,
    quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(result_id, judge_id)
);

CREATE INDEX IF NOT EXISTS idx_judgements_result ON judgements(result_id);
CREATE INDEX IF NOT EXISTS idx_judgements_judge ON judgements(judge_id);

-- Tasks (durable work queue)
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    task_type TEXT NOT NULL CHECK (task_type IN ('agent_run', 'judge_result', 'train_judge', 'generate_scenario_from_commit')),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    finished_at TEXT,
    error_message TEXT,
    worker_id TEXT,
    pid INTEGER,
    cancel_requested_at TEXT,

    -- agent_run fields
    result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    executor_spec TEXT,
    timeout_seconds INTEGER,
    driver TEXT,

    -- judge_result fields
    judge_id INTEGER REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
    target_result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
    judge_provider TEXT,
    judge_model TEXT,

    -- train_judge fields
    alignment_result_ids TEXT,

    -- generate_scenario_from_commit fields
    draft_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_tasks_poll ON tasks(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_tasks_result_id ON tasks(result_id);
CREATE INDEX IF NOT EXISTS idx_tasks_target_result_id ON tasks(target_result_id);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);

-- Commit scenario drafts (for generating scenarios from commits)
CREATE TABLE IF NOT EXISTS commit_scenario_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER REFERENCES tasks(id),

    -- Source commit
    owner TEXT NOT NULL,
    repo TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    parent_sha TEXT NOT NULL,
    commit_message TEXT NOT NULL,
    commit_author TEXT,
    pr_number INTEGER,
    pr_title TEXT,
    pr_body TEXT,
    diff TEXT NOT NULL,

    -- Generated content
    generated_prompt TEXT,
    generated_judge_guidance TEXT,
    generated_summary TEXT,

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'saved', 'failed')),
    error_message TEXT,

    -- Final references (after save)
    scenario_id INTEGER REFERENCES scenarios(id),
    judge_id INTEGER REFERENCES llm_scenario_judges(id),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_commit_drafts_task_id ON commit_scenario_drafts(task_id);
CREATE INDEX IF NOT EXISTS idx_commit_drafts_status ON commit_scenario_drafts(status);

-- Pairwise preferences (human comparison judgments)
CREATE TABLE IF NOT EXISTS pairwise_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    result_a_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    result_b_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    preference TEXT NOT NULL
        CHECK (preference IN ('a_better', 'b_better', 'tie', 'both_good', 'both_bad')),
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(result_a_id, result_b_id),
    CHECK (result_a_id < result_b_id)
);

CREATE INDEX IF NOT EXISTS idx_pairwise_scenario ON pairwise_preferences(scenario_id);
CREATE INDEX IF NOT EXISTS idx_pairwise_result_a ON pairwise_preferences(result_a_id);
CREATE INDEX IF NOT EXISTS idx_pairwise_result_b ON pairwise_preferences(result_b_id);
"""


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0


MIGRATION_V2_SQL = """
-- Pairwise preferences (human comparison judgments)
CREATE TABLE IF NOT EXISTS pairwise_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    result_a_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    result_b_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
    preference TEXT NOT NULL
        CHECK (preference IN ('a_better', 'b_better', 'tie', 'both_good', 'both_bad')),
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(result_a_id, result_b_id),
    CHECK (result_a_id < result_b_id)
);

CREATE INDEX IF NOT EXISTS idx_pairwise_scenario ON pairwise_preferences(scenario_id);
CREATE INDEX IF NOT EXISTS idx_pairwise_result_a ON pairwise_preferences(result_a_id);
CREATE INDEX IF NOT EXISTS idx_pairwise_result_b ON pairwise_preferences(result_b_id);
"""


def migrate(conn: sqlite3.Connection) -> None:
    """Apply schema if not already applied."""
    current = get_schema_version(conn)

    if current == 0:
        # Fresh install - apply full schema
        conn.executescript(SCHEMA_SQL)
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()
    elif current < SCHEMA_VERSION:
        # Incremental migrations
        if current < 2:
            conn.executescript(MIGRATION_V2_SQL)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (2,))
            conn.commit()

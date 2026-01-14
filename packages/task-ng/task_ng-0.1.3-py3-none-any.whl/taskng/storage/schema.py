"""Database schema for Task-NG."""

SCHEMA = """
-- Core task table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    priority TEXT,
    project TEXT,

    -- Timestamps
    entry TEXT NOT NULL,
    modified TEXT NOT NULL,
    start TEXT,
    end TEXT,
    due TEXT,
    scheduled TEXT,
    until TEXT,
    wait TEXT,

    -- Recurrence
    recur TEXT,
    parent_uuid TEXT,

    -- Calculated
    urgency REAL DEFAULT 0.0,

    -- Content
    notes TEXT
);

-- Normalized tags
CREATE TABLE IF NOT EXISTS tags (
    task_uuid TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (task_uuid, tag),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Normalized dependencies
CREATE TABLE IF NOT EXISTS dependencies (
    task_uuid TEXT NOT NULL,
    depends_on_uuid TEXT NOT NULL,
    PRIMARY KEY (task_uuid, depends_on_uuid),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Annotations
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY,
    task_uuid TEXT NOT NULL,
    entry TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- User Defined Attributes
CREATE TABLE IF NOT EXISTS uda_values (
    task_uuid TEXT NOT NULL,
    attribute TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (task_uuid, attribute),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Audit trail
CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY,
    task_uuid TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_data TEXT,
    new_data TEXT,
    synced INTEGER DEFAULT 0
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
CREATE INDEX IF NOT EXISTS idx_tasks_urgency ON tasks(urgency DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_modified ON tasks(modified);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_deps_depends ON dependencies(depends_on_uuid);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON task_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_history_synced ON task_history(synced);
"""

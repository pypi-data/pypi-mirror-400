"""Database connection and initialization."""

import os
import sqlite3
from collections.abc import Generator
from contextvars import ContextVar
from pathlib import Path

from .migrations import migrate

_DEFAULT_PROJECT = "default"

# Context variable for current project ID (set per-request in API)
_current_project_id: ContextVar[int | None] = ContextVar("current_project_id", default=None)


def get_current_project_id() -> int | None:
    """Get the current project ID from context (set per-request)."""
    return _current_project_id.get()


def set_current_project_id(project_id: int | None) -> None:
    """Set the current project ID in context."""
    _current_project_id.set(project_id)


def get_vibelab_home() -> Path:
    """
    Get VibeLab root data directory.

    This is configurable via `VIBELAB_HOME`.
    """
    home = os.environ.get("VIBELAB_HOME")
    if home:
        return Path(home).expanduser()
    return Path.home() / ".vibelab"


def get_vibelab_project() -> str:
    """Get the active project name (defaults to 'default').

    Note: This is now primarily used for initial setup. At runtime, use
    get_current_project_id() for the database-backed project context.
    """
    return os.environ.get("VIBELAB_PROJECT", _DEFAULT_PROJECT)


# =============================================================================
# Three-Tier Storage Layout
# =============================================================================
#
# db/   - Database storage (would be PostgreSQL in production)
# blob/ - Persistent application artifacts (would be S3 in production)
# tmp/  - Ephemeral cache, can be wiped without breaking app
# =============================================================================


def get_db_dir() -> Path:
    """Get (and ensure) the database directory: ~/.vibelab/db/"""
    db_dir = get_vibelab_home() / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir


def get_db_path() -> Path:
    """Get database file path: ~/.vibelab/db/data.db"""
    return get_db_dir() / "data.db"


def get_blob_dir() -> Path:
    """Get (and ensure) the blob storage directory: ~/.vibelab/blob/

    This is for persistent application artifacts (S3-equivalent in production).
    """
    blob_dir = get_vibelab_home() / "blob"
    blob_dir.mkdir(parents=True, exist_ok=True)
    return blob_dir


def get_results_dir(project_id: int) -> Path:
    """Get (and ensure) the results directory for a project.

    Path: ~/.vibelab/blob/projects/{project_id}/results/

    Results contain persistent artifacts: logs, patches, streaming files.
    """
    results_dir = get_blob_dir() / "projects" / str(project_id) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def get_tmp_dir() -> Path:
    """Get (and ensure) the temporary/ephemeral directory: ~/.vibelab/tmp/

    This directory can be safely deleted to reclaim disk space.
    Each worker would have their own tmp/ in a distributed setup.
    """
    tmp_dir = get_vibelab_home() / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def get_repos_dir() -> Path:
    """Get (and ensure) the repos directory for bare git clones.

    Path: ~/.vibelab/tmp/repos/

    Structure: tmp/repos/{host}/{owner}/{repo}.git
    This is ephemeral - each worker would have their own cache.
    """
    repos_dir = get_tmp_dir() / "repos"
    repos_dir.mkdir(parents=True, exist_ok=True)
    return repos_dir


def get_worktrees_dir() -> Path:
    """Get (and ensure) the worktrees directory.

    Path: ~/.vibelab/tmp/worktrees/

    Structure: tmp/worktrees/{result_id}/
    Working directories are ephemeral and tied to result execution.
    """
    worktrees_dir = get_tmp_dir() / "worktrees"
    worktrees_dir.mkdir(parents=True, exist_ok=True)
    return worktrees_dir


def get_containers_dir() -> Path:
    """Get (and ensure) the containers directory for Docker temp files.

    Path: ~/.vibelab/tmp/containers/

    Structure: tmp/containers/{result_id}/
    """
    containers_dir = get_tmp_dir() / "containers"
    containers_dir.mkdir(parents=True, exist_ok=True)
    return containers_dir


def get_modal_dir() -> Path:
    """Get (and ensure) the Modal temp directory.

    Path: ~/.vibelab/tmp/modal/

    Structure: tmp/modal/{result_id}/
    """
    modal_dir = get_tmp_dir() / "modal"
    modal_dir.mkdir(parents=True, exist_ok=True)
    return modal_dir


# =============================================================================
# Database Connection
# =============================================================================


def _configure_sqlite_connection(conn: sqlite3.Connection) -> None:
    """
    Apply SQLite connection pragmas.

    Notes:
    - WAL mode improves concurrency for API + worker.
    - busy_timeout helps avoid transient "database is locked" errors.
    - foreign_keys must be enabled per-connection in SQLite.
    """
    # Enforce foreign key constraints declared in schema.
    conn.execute("PRAGMA foreign_keys = ON")

    # Better concurrency for concurrent readers/writers.
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except sqlite3.OperationalError:
        # Some SQLite configurations might not allow WAL; proceed best-effort.
        pass

    busy_timeout_ms = int(os.environ.get("VIBELAB_SQLITE_BUSY_TIMEOUT_MS", "5000"))
    conn.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    _configure_sqlite_connection(conn)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with schema and migrations."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    _configure_sqlite_connection(conn)
    try:
        migrate(conn)
        conn.commit()
    finally:
        conn.close()

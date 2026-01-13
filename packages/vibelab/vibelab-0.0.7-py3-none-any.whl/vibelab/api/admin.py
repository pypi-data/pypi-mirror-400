"""Admin API endpoints for system introspection."""

import os
import sqlite3
from datetime import UTC
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..db.connection import (
    get_blob_dir,
    get_db,
    get_db_path,
    get_repos_dir,
    get_tmp_dir,
    get_vibelab_home,
    get_vibelab_project,
)

router = APIRouter()


# --- Models ---


class ProjectInfo(BaseModel):
    """Project information for admin config."""

    id: int
    name: str
    description: str | None
    scenario_count: int
    dataset_count: int


class ConfigResponse(BaseModel):
    """Configuration variables and system info."""

    vibelab_home: str
    project: str
    project_id: int | None
    db_path: str
    blob_dir: str
    tmp_dir: str
    repos_dir: str
    log_level: str
    sqlite_busy_timeout_ms: int
    # Worker info (from CLI defaults)
    default_workers: int
    # Image overrides
    claude_code_image: str | None
    openai_codex_image: str | None
    cursor_image: str | None
    gemini_image: str | None
    # Driver settings
    oci_runtime: str | None
    default_driver: str
    default_timeout: int
    # Multi-project support
    projects: list[ProjectInfo]


class RepoInfo(BaseModel):
    """Information about a cached repository."""

    host: str
    owner: str
    repo: str
    path: str
    size_mb: float


class ReposResponse(BaseModel):
    """List of cached repositories."""

    repos_dir: str
    repos: list[RepoInfo]
    total_size_mb: float


class FileEntry(BaseModel):
    """A file or directory entry."""

    name: str
    path: str
    is_dir: bool
    size_bytes: int | None
    modified_at: str | None


class FileBrowserResponse(BaseModel):
    """File browser response."""

    current_path: str
    parent_path: str | None
    entries: list[FileEntry]


class QueryRequest(BaseModel):
    """SQLite query request."""

    query: str


class QueryResponse(BaseModel):
    """SQLite query response."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    error: str | None = None


class TableInfo(BaseModel):
    """Information about a database table."""

    name: str
    row_count: int
    columns: list[str]


class SchemaResponse(BaseModel):
    """Database schema information."""

    tables: list[TableInfo]
    schema_version: int


class ScenarioCacheEntry(BaseModel):
    """A cached scenario entry."""

    scenario_id: int
    code_type: str
    code_ref: dict | None
    prompt_preview: str
    result_count: int
    has_worktree: bool


class ScenarioCacheResponse(BaseModel):
    """Cached scenarios response."""

    scenarios: list[ScenarioCacheEntry]
    total_scenarios: int
    scenarios_with_worktrees: int


# --- Endpoints ---


@router.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    """Get current configuration variables."""
    from ..db.connection import get_current_project_id
    from ..db.queries import list_projects

    # Get projects list
    projects_list: list[ProjectInfo] = []
    for conn in get_db():
        projects = list_projects(conn)
        for project in projects:
            scenario_count = conn.execute(
                "SELECT COUNT(*) FROM scenarios WHERE project_id = ?",
                (project.id,),
            ).fetchone()[0]
            dataset_count = conn.execute(
                "SELECT COUNT(*) FROM datasets WHERE project_id = ?",
                (project.id,),
            ).fetchone()[0]
            projects_list.append(
                ProjectInfo(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    scenario_count=scenario_count,
                    dataset_count=dataset_count,
                )
            )
        break

    return ConfigResponse(
        vibelab_home=str(get_vibelab_home()),
        project=get_vibelab_project(),
        project_id=get_current_project_id(),
        db_path=str(get_db_path()),
        blob_dir=str(get_blob_dir()),
        tmp_dir=str(get_tmp_dir()),
        repos_dir=str(get_repos_dir()),
        log_level=os.environ.get("VIBELAB_LOG_LEVEL", "INFO"),
        sqlite_busy_timeout_ms=int(os.environ.get("VIBELAB_SQLITE_BUSY_TIMEOUT_MS", "5000")),
        default_workers=1,  # CLI default
        claude_code_image=os.environ.get("VIBELAB_CLAUDE_CODE_IMAGE"),
        openai_codex_image=os.environ.get("VIBELAB_OPENAI_CODEX_IMAGE"),
        cursor_image=os.environ.get("VIBELAB_CURSOR_IMAGE"),
        gemini_image=os.environ.get("VIBELAB_GEMINI_IMAGE"),
        oci_runtime=os.environ.get("VIBELAB_OCI_RUNTIME"),
        default_driver=os.environ.get("VIBELAB_DRIVER", "local"),
        default_timeout=int(os.environ.get("VIBELAB_TIMEOUT", "1800")),
        projects=projects_list,
    )


@router.get("/repos", response_model=ReposResponse)
def list_repos() -> ReposResponse:
    """List cached git repositories."""
    repos_dir = get_repos_dir()
    repos: list[RepoInfo] = []
    total_size = 0.0

    if repos_dir.exists():
        # Structure: repos/{host}/{owner}/{repo}.git
        for host_dir in repos_dir.iterdir():
            if not host_dir.is_dir():
                continue
            for owner_dir in host_dir.iterdir():
                if not owner_dir.is_dir():
                    continue
                for repo_dir in owner_dir.iterdir():
                    if not repo_dir.is_dir() or not repo_dir.name.endswith(".git"):
                        continue

                    # Calculate size
                    size_bytes = sum(f.stat().st_size for f in repo_dir.rglob("*") if f.is_file())
                    size_mb = size_bytes / (1024 * 1024)
                    total_size += size_mb

                    repos.append(
                        RepoInfo(
                            host=host_dir.name,
                            owner=owner_dir.name,
                            repo=repo_dir.name.replace(".git", ""),
                            path=str(repo_dir),
                            size_mb=round(size_mb, 2),
                        )
                    )

    return ReposResponse(
        repos_dir=str(repos_dir),
        repos=sorted(repos, key=lambda r: (r.host, r.owner, r.repo)),
        total_size_mb=round(total_size, 2),
    )


@router.get("/files", response_model=FileBrowserResponse)
def browse_files(
    path: str = Query("", description="Relative path within data directory"),
) -> FileBrowserResponse:
    """Browse files in the data directory."""
    vibelab_home = get_vibelab_home()

    # Resolve and validate path
    if path:
        target_path = (vibelab_home / path).resolve()
        # Security: ensure we're still under vibelab_home
        try:
            target_path.relative_to(vibelab_home)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid path")
    else:
        target_path = vibelab_home

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    # Compute parent path
    parent_path: str | None = None
    if target_path != vibelab_home:
        parent_rel = target_path.parent.relative_to(vibelab_home)
        parent_path = str(parent_rel) if str(parent_rel) != "." else ""

    entries: list[FileEntry] = []

    if target_path.is_dir():
        for entry in sorted(target_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            try:
                stat = entry.stat()
                rel_path = entry.relative_to(vibelab_home)
                entries.append(
                    FileEntry(
                        name=entry.name,
                        path=str(rel_path),
                        is_dir=entry.is_dir(),
                        size_bytes=stat.st_size if entry.is_file() else None,
                        modified_at=_format_timestamp(stat.st_mtime),
                    )
                )
            except (OSError, PermissionError):
                # Skip files we can't access
                continue
    else:
        # Single file
        stat = target_path.stat()
        rel_path = target_path.relative_to(vibelab_home)
        entries.append(
            FileEntry(
                name=target_path.name,
                path=str(rel_path),
                is_dir=False,
                size_bytes=stat.st_size,
                modified_at=_format_timestamp(stat.st_mtime),
            )
        )

    current_rel = target_path.relative_to(vibelab_home)
    current_path = str(current_rel) if str(current_rel) != "." else ""

    return FileBrowserResponse(
        current_path=current_path,
        parent_path=parent_path,
        entries=entries,
    )


@router.get("/schema", response_model=SchemaResponse)
def get_schema() -> SchemaResponse:
    """Get database schema information."""
    for conn in get_db():
        # Get schema version
        try:
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            row = cursor.fetchone()
            schema_version = row[0] if row and row[0] is not None else 0
        except sqlite3.OperationalError:
            schema_version = 0

        # Get tables
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [row[0] for row in cursor.fetchall()]

        tables: list[TableInfo] = []
        for table_name in table_names:
            # Get row count
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa: S608
                row_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                row_count = 0

            # Get columns
            cursor = conn.execute(f"PRAGMA table_info({table_name})")  # noqa: S608
            columns = [row[1] for row in cursor.fetchall()]

            tables.append(TableInfo(name=table_name, row_count=row_count, columns=columns))

        return SchemaResponse(tables=tables, schema_version=schema_version)


@router.post("/query", response_model=QueryResponse)
def execute_query(request: QueryRequest) -> QueryResponse:
    """Execute a read-only SQLite query.

    Only SELECT queries are allowed for safety.
    """
    query = request.query.strip()

    # Safety check: only allow SELECT and EXPLAIN
    query_lower = query.lower()
    if not query_lower.startswith(("select", "explain", "pragma")):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT, EXPLAIN, and PRAGMA queries are allowed",
        )

    # Block dangerous patterns
    dangerous_patterns = ["drop", "delete", "insert", "update", "create", "alter", "attach"]
    for pattern in dangerous_patterns:
        if pattern in query_lower:
            raise HTTPException(
                status_code=400,
                detail=f"Query contains forbidden keyword: {pattern}",
            )

    for conn in get_db():
        try:
            cursor = conn.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = [list(row) for row in cursor.fetchall()]

            return QueryResponse(
                columns=columns,
                rows=rows[:1000],  # Limit results
                row_count=len(rows),
                error=None,
            )
        except sqlite3.Error as e:
            return QueryResponse(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
            )


@router.get("/scenarios", response_model=ScenarioCacheResponse)
def list_cached_scenarios() -> ScenarioCacheResponse:
    """List scenarios with their cache status."""
    import json

    from ..db.connection import get_worktrees_dir

    worktrees_dir = get_worktrees_dir()

    for conn in get_db():
        # Get all scenarios with result counts
        cursor = conn.execute(
            """
            SELECT 
                s.id,
                s.code_type,
                s.code_ref,
                s.prompt,
                COUNT(r.id) as result_count
            FROM scenarios s
            LEFT JOIN results r ON r.scenario_id = s.id
            WHERE s.archived = 0
            GROUP BY s.id
            ORDER BY s.id DESC
            """
        )

        scenarios: list[ScenarioCacheEntry] = []
        scenarios_with_worktrees = 0

        for row in cursor.fetchall():
            scenario_id = row[0]

            # Check if worktree exists for any result
            has_worktree = False
            if worktrees_dir.exists():
                # Check for any worktree directories for this scenario's results
                result_cursor = conn.execute(
                    "SELECT id FROM results WHERE scenario_id = ?", (scenario_id,)
                )
                for result_row in result_cursor:
                    worktree_path = worktrees_dir / str(result_row[0])
                    if worktree_path.exists():
                        has_worktree = True
                        break

            if has_worktree:
                scenarios_with_worktrees += 1

            # Parse code_ref if JSON
            code_ref = None
            if row[2]:
                try:
                    code_ref = json.loads(row[2])
                except (json.JSONDecodeError, TypeError):
                    code_ref = {"raw": row[2]}

            # Truncate prompt for preview
            prompt = row[3] or ""
            prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt

            scenarios.append(
                ScenarioCacheEntry(
                    scenario_id=scenario_id,
                    code_type=row[1],
                    code_ref=code_ref,
                    prompt_preview=prompt_preview,
                    result_count=row[4],
                    has_worktree=has_worktree,
                )
            )

        return ScenarioCacheResponse(
            scenarios=scenarios,
            total_scenarios=len(scenarios),
            scenarios_with_worktrees=scenarios_with_worktrees,
        )


def _format_timestamp(ts: float) -> str:
    """Format a Unix timestamp as ISO format."""
    from datetime import datetime

    return datetime.fromtimestamp(ts, tz=UTC).isoformat()

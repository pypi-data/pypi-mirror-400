"""SQLite-backed task queue.

This is the durable source of truth for pending work so that `vibelab start`
can survive API restarts: the worker simply continues processing rows in
the `tasks` table.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    AGENT_RUN = "agent_run"
    JUDGE_RESULT = "judge_result"
    TRAIN_JUDGE = "train_judge"
    GENERATE_SCENARIO_FROM_COMMIT = "generate_scenario_from_commit"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Task:
    id: int
    task_type: TaskType
    status: TaskStatus
    priority: int
    created_at: str
    started_at: str | None
    finished_at: str | None
    error_message: str | None
    worker_id: str | None
    pid: int | None
    cancel_requested_at: str | None

    # Project ownership
    project_id: int | None

    # agent_run
    result_id: int | None
    scenario_id: int | None
    executor_spec: str | None
    timeout_seconds: int | None
    driver: str | None

    # judge_result / train_judge
    judge_id: int | None
    target_result_id: int | None
    judge_provider: str | None
    judge_model: str | None
    alignment_result_ids: list[int] | None  # For train_judge: result IDs to evaluate alignment on

    # generate_scenario_from_commit fields
    draft_id: int | None  # For generate_scenario_from_commit: draft ID to generate content for


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _get_project_id() -> int:
    """Get current project ID for task creation.

    Raises:
        ValueError: If no project context is set.
    """
    from ..db.connection import get_current_project_id

    project_id = get_current_project_id()
    if project_id is None:
        raise ValueError("project_id is required (no project context set)")
    return project_id


def enqueue_agent_run(
    conn: sqlite3.Connection,
    *,
    result_id: int,
    scenario_id: int,
    executor_spec: str,
    timeout_seconds: int,
    driver: str,
    priority: int = 0,
    project_id: int | None = None,
) -> int:
    if project_id is None:
        project_id = _get_project_id()
    cursor = conn.execute(
        """
        INSERT INTO tasks (
          task_type, status, priority,
          result_id, scenario_id, executor_spec, timeout_seconds, driver, project_id
        )
        VALUES (
          'agent_run', 'queued', ?,
          ?, ?, ?, ?, ?, ?
        )
        """,
        (priority, result_id, scenario_id, executor_spec, timeout_seconds, driver, project_id),
    )
    conn.commit()
    task_id = cursor.lastrowid
    if task_id is None:
        raise RuntimeError("Failed to enqueue task (no lastrowid)")
    return int(task_id)


def enqueue_judge_result(
    conn: sqlite3.Connection,
    *,
    judge_id: int,
    target_result_id: int,
    judge_provider: str,
    judge_model: str,
    priority: int = 10,
    project_id: int | None = None,
) -> int:
    if project_id is None:
        project_id = _get_project_id()
    cursor = conn.execute(
        """
        INSERT INTO tasks (
          task_type, status, priority,
          judge_id, target_result_id, judge_provider, judge_model, project_id
        )
        VALUES (
          'judge_result', 'queued', ?,
          ?, ?, ?, ?, ?
        )
        """,
        (priority, judge_id, target_result_id, judge_provider, judge_model, project_id),
    )
    conn.commit()
    task_id = cursor.lastrowid
    if task_id is None:
        raise RuntimeError("Failed to enqueue task (no lastrowid)")
    return int(task_id)


def enqueue_train_judge(
    conn: sqlite3.Connection,
    *,
    judge_id: int,
    judge_provider: str,
    judge_model: str,
    result_ids: list[int] | None = None,
    priority: int = 5,
    project_id: int | None = None,
) -> int:
    import json

    if project_id is None:
        project_id = _get_project_id()
    alignment_result_ids_json = json.dumps(result_ids) if result_ids else None
    cursor = conn.execute(
        """
        INSERT INTO tasks (
          task_type, status, priority,
          judge_id, judge_provider, judge_model, alignment_result_ids, project_id
        )
        VALUES (
          'train_judge', 'queued', ?,
          ?, ?, ?, ?, ?
        )
        """,
        (priority, judge_id, judge_provider, judge_model, alignment_result_ids_json, project_id),
    )
    conn.commit()
    task_id = cursor.lastrowid
    if task_id is None:
        raise RuntimeError("Failed to enqueue task (no lastrowid)")
    return int(task_id)


def enqueue_generate_scenario_from_commit(
    conn: sqlite3.Connection,
    *,
    draft_id: int,
    priority: int = 5,
    project_id: int | None = None,
) -> int:
    """Enqueue a task to generate scenario content from a commit draft."""
    if project_id is None:
        project_id = _get_project_id()
    cursor = conn.execute(
        """
        INSERT INTO tasks (
          task_type, status, priority,
          draft_id, project_id
        )
        VALUES (
          'generate_scenario_from_commit', 'queued', ?,
          ?, ?
        )
        """,
        (priority, draft_id, project_id),
    )
    conn.commit()
    task_id = cursor.lastrowid
    if task_id is None:
        raise RuntimeError("Failed to enqueue task (no lastrowid)")
    return int(task_id)


def claim_next_task(conn: sqlite3.Connection, worker_id: str) -> Task | None:
    """Atomically claim the next queued task by switching it to RUNNING.

    Uses `BEGIN IMMEDIATE` to ensure a single claimant across concurrent workers.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE status = 'queued'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
            """
        ).fetchone()
        if not row:
            conn.rollback()
            return None

        task_id = int(row["id"])
        started_at = _now_iso()
        updated = conn.execute(
            """
            UPDATE tasks
            SET status = 'running', started_at = ?, worker_id = ?
            WHERE id = ? AND status = 'queued'
            """,
            (started_at, worker_id, task_id),
        )
        if updated.rowcount != 1:
            # Someone else claimed it. Retry next poll tick.
            conn.rollback()
            return None

        conn.commit()

        # Re-read the full row so we return an accurate, consistent Task.
        claimed = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not claimed:
            return None
        return _row_to_task(claimed)
    except Exception:
        conn.rollback()
        raise


def update_task_completed(conn: sqlite3.Connection, task_id: int) -> None:
    conn.execute(
        "UPDATE tasks SET status = 'completed', finished_at = ? WHERE id = ?",
        (_now_iso(), task_id),
    )
    conn.commit()


def update_task_failed(conn: sqlite3.Connection, task_id: int, *, error_message: str) -> None:
    conn.execute(
        """
        UPDATE tasks
        SET status = 'failed', finished_at = ?, error_message = ?
        WHERE id = ?
        """,
        (_now_iso(), error_message, task_id),
    )
    conn.commit()


def update_task_cancelled(
    conn: sqlite3.Connection, task_id: int, *, error_message: str | None = None
) -> None:
    conn.execute(
        """
        UPDATE tasks
        SET status = 'cancelled', finished_at = ?, error_message = COALESCE(?, error_message)
        WHERE id = ?
        """,
        (_now_iso(), error_message, task_id),
    )
    conn.commit()


def get_task(conn: sqlite3.Connection, task_id: int) -> Task | None:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        return None
    return _row_to_task(row)


def set_task_pid(conn: sqlite3.Connection, task_id: int, *, pid: int | None) -> None:
    conn.execute("UPDATE tasks SET pid = ? WHERE id = ?", (pid, task_id))
    conn.commit()


def promote_task(conn: sqlite3.Connection, task_id: int) -> Task | None:
    """Promote a queued task to the top of the queue by bumping its priority."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            conn.rollback()
            return None
        if str(row["status"]) != "queued":
            # Only queued tasks can be reprioritized.
            conn.rollback()
            return _row_to_task(row)

        max_row = conn.execute(
            "SELECT COALESCE(MAX(priority), 0) AS maxp FROM tasks WHERE status = 'queued'"
        ).fetchone()
        maxp = int(max_row["maxp"]) if max_row else 0
        new_priority = maxp + 1
        conn.execute(
            "UPDATE tasks SET priority = ? WHERE id = ? AND status = 'queued'",
            (new_priority, task_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_task(updated) if updated else None
    except Exception:
        conn.rollback()
        raise


def cancel_task(conn: sqlite3.Connection, task_id: int) -> Task | None:
    """Cancel a task.

    - queued -> cancelled immediately
    - running -> set cancel_requested_at (worker will finalize as cancelled)
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            conn.rollback()
            return None

        status = str(row["status"])
        if status == "queued":
            conn.execute(
                "UPDATE tasks SET status = 'cancelled', finished_at = ?, error_message = ? WHERE id = ? AND status = 'queued'",
                (_now_iso(), "cancelled", task_id),
            )
            conn.commit()
            updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return _row_to_task(updated) if updated else None

        if status == "running":
            conn.execute(
                "UPDATE tasks SET cancel_requested_at = COALESCE(cancel_requested_at, ?) WHERE id = ? AND status = 'running'",
                (_now_iso(), task_id),
            )
            conn.commit()
            updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return _row_to_task(updated) if updated else None

        # completed/failed/cancelled: no-op
        conn.rollback()
        return _row_to_task(row)
    except Exception:
        conn.rollback()
        raise


def cancel_queued_tasks(conn: sqlite3.Connection) -> int:
    """Cancel all queued (not-yet-started) tasks.

    Returns the number of tasks cancelled.
    """
    now = _now_iso()
    cursor = conn.execute(
        """
        UPDATE tasks
        SET status = 'cancelled', finished_at = ?, error_message = 'cancelled'
        WHERE status = 'queued'
        """,
        (now,),
    )
    conn.commit()
    return cursor.rowcount


def list_tasks(
    conn: sqlite3.Connection,
    *,
    status: TaskStatus | None = None,
    task_type: TaskType | None = None,
    limit: int = 100,
) -> list[Task]:
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list[Any] = []
    if status is not None:
        query += " AND status = ?"
        params.append(status.value)
    if task_type is not None:
        query += " AND task_type = ?"
        params.append(task_type.value)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    return [_row_to_task(r) for r in rows]


def cleanup_stale_running_tasks(conn: sqlite3.Connection) -> int:
    """Clean up tasks stuck in 'running' status whose results have completed.
    
    This handles cases where a task's result finishes but the task status
    wasn't properly updated (e.g., worker crash, exception before update).
    
    Returns the number of tasks cleaned up.
    """
    # Find running agent_run tasks with result_id set
    running_tasks = conn.execute(
        """
        SELECT id, result_id
        FROM tasks
        WHERE status = 'running'
          AND task_type = 'agent_run'
          AND result_id IS NOT NULL
        """
    ).fetchall()
    
    if not running_tasks:
        return 0
    
    cleaned_count = 0
    now = _now_iso()
    
    for task_row in running_tasks:
        task_id = task_row["id"]
        result_id = task_row["result_id"]
        
        # Check the result status
        result_row = conn.execute(
            "SELECT status FROM results WHERE id = ?",
            (result_id,),
        ).fetchone()
        
        if not result_row:
            # Result doesn't exist - skip (might be a race condition)
            continue
        
        result_status = str(result_row["status"])
        
        # If result is finished, update task to match
        if result_status == "completed":
            conn.execute(
                "UPDATE tasks SET status = 'completed', finished_at = ? WHERE id = ?",
                (now, task_id),
            )
            cleaned_count += 1
        elif result_status in ("failed", "timeout", "infra_failure"):
            # Map result failure statuses to task failed status
            error_msg = f"result finished with status: {result_status}"
            conn.execute(
                """
                UPDATE tasks 
                SET status = 'failed', finished_at = ?, error_message = ?
                WHERE id = ?
                """,
                (now, error_msg, task_id),
            )
            cleaned_count += 1
    
    if cleaned_count > 0:
        conn.commit()
        logger.info("Cleaned up %d stale running task(s)", cleaned_count)
    
    return cleaned_count


def list_active_tasks(conn: sqlite3.Connection, *, limit: int = 200) -> list[Task]:
    # Clean up stale tasks before listing
    cleanup_stale_running_tasks(conn)
    
    rows = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE status IN ('queued', 'running')
        ORDER BY
          CASE status WHEN 'running' THEN 0 ELSE 1 END,
          priority DESC,
          created_at ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [_row_to_task(r) for r in rows]


def task_stats(conn: sqlite3.Connection) -> dict[str, dict[str, int]]:
    """Return counts grouped by task_type and status.

    Includes all statuses: queued, running, completed, failed.
    """
    # Ensure we read the latest committed data
    rows = conn.execute(
        """
        SELECT task_type, status, COUNT(*) AS cnt
        FROM tasks
        GROUP BY task_type, status
        ORDER BY task_type, status
        """
    ).fetchall()
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        t = str(r["task_type"])
        s = str(r["status"])
        out.setdefault(t, {})[s] = int(r["cnt"])
    return out


def _row_to_task(row: sqlite3.Row) -> Task:
    import json

    alignment_result_ids = None
    # Check if column exists and has a value
    try:
        alignment_result_ids_val = row["alignment_result_ids"]
        if alignment_result_ids_val:
            try:
                alignment_result_ids = json.loads(str(alignment_result_ids_val))
            except (json.JSONDecodeError, TypeError):
                alignment_result_ids = None
    except (KeyError, IndexError):
        # Column doesn't exist (old database schema)
        alignment_result_ids = None

    return Task(
        id=int(row["id"]),
        task_type=TaskType(str(row["task_type"])),
        status=TaskStatus(str(row["status"])),
        priority=int(row["priority"]),
        created_at=str(row["created_at"]),
        started_at=str(row["started_at"]) if row["started_at"] is not None else None,
        finished_at=str(row["finished_at"]) if row["finished_at"] is not None else None,
        error_message=str(row["error_message"]) if row["error_message"] is not None else None,
        worker_id=str(row["worker_id"]) if row["worker_id"] is not None else None,
        pid=int(row["pid"]) if "pid" in row.keys() and row["pid"] is not None else None,
        cancel_requested_at=(
            str(row["cancel_requested_at"])
            if "cancel_requested_at" in row.keys() and row["cancel_requested_at"] is not None
            else None
        ),
        project_id=int(row["project_id"])
        if "project_id" in row.keys() and row["project_id"] is not None
        else None,
        result_id=int(row["result_id"]) if row["result_id"] is not None else None,
        scenario_id=int(row["scenario_id"]) if row["scenario_id"] is not None else None,
        executor_spec=str(row["executor_spec"]) if row["executor_spec"] is not None else None,
        timeout_seconds=int(row["timeout_seconds"]) if row["timeout_seconds"] is not None else None,
        driver=str(row["driver"]) if row["driver"] is not None else None,
        judge_id=int(row["judge_id"]) if row["judge_id"] is not None else None,
        target_result_id=int(row["target_result_id"])
        if row["target_result_id"] is not None
        else None,
        judge_provider=str(row["judge_provider"]) if row["judge_provider"] is not None else None,
        judge_model=str(row["judge_model"]) if row["judge_model"] is not None else None,
        alignment_result_ids=alignment_result_ids,
        draft_id=int(row["draft_id"])
        if "draft_id" in row.keys() and row["draft_id"] is not None
        else None,
    )

"""Task queue inspection endpoints."""

from __future__ import annotations

import os
import signal
from typing import Any

from fastapi import APIRouter, HTTPException

from ..db import get_db
from ..engine.queue import (
    TaskStatus,
    TaskType,
    cancel_queued_tasks,
    cancel_task,
    get_task,
    list_active_tasks,
    list_tasks,
    promote_task,
    task_stats,
)

router = APIRouter()


@router.get("")
def list_tasks_endpoint(
    status: str | None = None,
    task_type: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    st = TaskStatus(status) if status else None
    tt = TaskType(task_type) if task_type else None
    for db in get_db():
        tasks = list_tasks(db, status=st, task_type=tt, limit=limit)
        return [t.__dict__ for t in tasks]
    return []


@router.get("/active")
def list_active_tasks_endpoint(limit: int = 200) -> list[dict[str, Any]]:
    """List queued+running tasks for the Active Jobs view."""
    for db in get_db():
        tasks = list_active_tasks(db, limit=limit)
        return [t.__dict__ for t in tasks]
    return []


@router.post("/{task_id}/promote")
def promote_task_endpoint(task_id: int) -> dict[str, Any]:
    """Promote a queued task to the top of the queue."""
    for db in get_db():
        task = promote_task(db, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.__dict__
    raise HTTPException(status_code=500, detail="DB unavailable")


@router.post("/{task_id}/cancel")
def cancel_task_endpoint(task_id: int) -> dict[str, Any]:
    """Cancel a queued task immediately; request cancellation for a running task.

    For running tasks executed by the worker in a subprocess, this will also
    best-effort send SIGTERM to the task's process group using the recorded pid.
    """
    signal_sent = False
    for db in get_db():
        before = get_task(db, task_id)
        if before is None:
            raise HTTPException(status_code=404, detail="Task not found")

        updated = cancel_task(db, task_id)
        if updated is None:
            raise HTTPException(status_code=404, detail="Task not found")

        # Only try to signal if it was (or is) running and we have a pid recorded.
        pid = updated.pid
        if pid is not None and before.status == TaskStatus.RUNNING:
            try:
                # Worker starts tasks with start_new_session=True, so pid is a process group leader.
                os.killpg(pid, signal.SIGTERM)
                signal_sent = True
            except ProcessLookupError:
                signal_sent = False
            except PermissionError:
                signal_sent = False
            except Exception:
                # Fallback: try killing the pid itself.
                try:
                    os.kill(pid, signal.SIGTERM)
                    signal_sent = True
                except Exception:
                    signal_sent = False

        out = updated.__dict__.copy()
        out["signal_sent"] = signal_sent
        return out

    raise HTTPException(status_code=500, detail="DB unavailable")


@router.get("/stats")
def task_stats_endpoint() -> dict[str, Any]:
    """Return task stats with worker count."""
    for db in get_db():
        stats = task_stats(db)

        running_row = db.execute(
            "SELECT COUNT(*) AS running_count FROM tasks WHERE status = 'running'"
        ).fetchone()
        total_running = int(running_row["running_count"]) if running_row else 0

        # Also count unique worker_ids for reference (workers that have claimed tasks)
        worker_rows = db.execute(
            """
            SELECT COUNT(DISTINCT worker_id) AS worker_count
            FROM tasks
            WHERE status = 'running' AND worker_id IS NOT NULL
            """
        ).fetchone()
        worker_count = int(worker_rows["worker_count"]) if worker_rows else 0

        return {
            "task_stats": stats,
            "running_tasks": total_running,
            "active_workers": worker_count,  # Workers with running tasks
        }
    return {"task_stats": {}, "running_tasks": 0, "active_workers": 0}


@router.post("/cancel-queued")
def cancel_queued_tasks_endpoint() -> dict[str, Any]:
    """Cancel all queued (not-yet-started) tasks."""
    for db in get_db():
        count = cancel_queued_tasks(db)
        return {"status": "ok", "cancelled": count}
    raise HTTPException(status_code=500, detail="DB unavailable")

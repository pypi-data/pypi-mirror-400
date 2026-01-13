"""Unit tests for the durable SQLite task queue."""

from datetime import datetime, timezone

from vibelab.db import get_db
from vibelab.db.queries import create_llm_scenario_judge, create_result, create_scenario
from vibelab.engine.queue import (
    TaskStatus,
    TaskType,
    claim_next_task,
    cancel_task,
    cleanup_stale_running_tasks,
    enqueue_agent_run,
    enqueue_judge_result,
    list_active_tasks,
    list_tasks,
    promote_task,
)
from vibelab.models.judge import LLMScenarioJudge
from vibelab.models.result import Result, ResultStatus
from vibelab.models.scenario import CodeType, Scenario


def test_enqueue_and_claim_order_by_priority():
    for db in get_db():
        scenario = Scenario(
            id=0,
            code_type=CodeType.EMPTY,
            code_ref=None,
            prompt="x",
            created_at=datetime.now(timezone.utc),
        )
        scenario = create_scenario(db, scenario)

        result1 = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        result1 = create_result(db, result1)

        result2 = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        result2 = create_result(db, result2)

        judge = LLMScenarioJudge(
            id=0,
            scenario_id=scenario.id,
            guidance="x",
            training_sample_ids=[],
            alignment_score=None,
            created_at=datetime.now(timezone.utc),
        )
        judge = create_llm_scenario_judge(db, judge)

        t1 = enqueue_agent_run(
            db,
            result_id=result1.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
            priority=0,
        )
        t2 = enqueue_judge_result(
            db,
            judge_id=judge.id,
            target_result_id=result2.id,
            judge_provider="anthropic",
            judge_model="claude-sonnet-4-20250514",
            priority=10,
        )
        break

    for db in get_db():
        task = claim_next_task(db, worker_id="w1")
        assert task is not None
        assert task.id == t2
        assert task.status == TaskStatus.RUNNING
        assert task.worker_id == "w1"
        break

    for db in get_db():
        task = claim_next_task(db, worker_id="w2")
        assert task is not None
        assert task.id == t1
        assert task.status == TaskStatus.RUNNING
        break


def test_list_tasks_filters():
    for db in get_db():
        scenario = Scenario(
            id=0,
            code_type=CodeType.EMPTY,
            code_ref=None,
            prompt="x",
            created_at=datetime.now(timezone.utc),
        )
        scenario = create_scenario(db, scenario)

        result = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        result = create_result(db, result)

        enqueue_agent_run(
            db,
            result_id=result.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
        )
        break

    for db in get_db():
        tasks = list_tasks(db, status=TaskStatus.QUEUED, task_type=TaskType.AGENT_RUN)
        assert len(tasks) == 1
        assert tasks[0].task_type == TaskType.AGENT_RUN
        assert tasks[0].status == TaskStatus.QUEUED
        break


def test_cancel_queued_task_marks_cancelled():
    for db in get_db():
        scenario = Scenario(
            id=0,
            code_type=CodeType.EMPTY,
            code_ref=None,
            prompt="x",
            created_at=datetime.now(timezone.utc),
        )
        scenario = create_scenario(db, scenario)
        result = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        result = create_result(db, result)
        task_id = enqueue_agent_run(
            db,
            result_id=result.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
        )
        cancelled = cancel_task(db, task_id)
        assert cancelled is not None
        assert cancelled.status == TaskStatus.CANCELLED
        break


def test_promote_queued_task_bumps_priority_above_others():
    for db in get_db():
        scenario = Scenario(
            id=0,
            code_type=CodeType.EMPTY,
            code_ref=None,
            prompt="x",
            created_at=datetime.now(timezone.utc),
        )
        scenario = create_scenario(db, scenario)
        r1 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="claude-code",
                provider="anthropic",
                model="haiku",
                status=ResultStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                timeout_seconds=1,
                driver="local",
            ),
        )
        r2 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="claude-code",
                provider="anthropic",
                model="haiku",
                status=ResultStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                timeout_seconds=1,
                driver="local",
            ),
        )

        # Enqueue in low priority order.
        t1 = enqueue_agent_run(
            db,
            result_id=r1.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
            priority=0,
        )
        t2 = enqueue_agent_run(
            db,
            result_id=r2.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
            priority=0,
        )

        promoted = promote_task(db, t2)
        assert promoted is not None
        assert promoted.id == t2
        assert promoted.priority >= 1
        break

    for db in get_db():
        claimed = claim_next_task(db, worker_id="w1")
        assert claimed is not None
        assert claimed.id == t2
        break


def test_cleanup_stale_running_tasks():
    """Test that tasks stuck in 'running' status are cleaned up when results complete."""
    for db in get_db():
        scenario = Scenario(
            id=0,
            code_type=CodeType.EMPTY,
            code_ref=None,
            prompt="x",
            created_at=datetime.now(timezone.utc),
        )
        scenario = create_scenario(db, scenario)

        # Create a result that's already completed
        completed_result = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        completed_result = create_result(db, completed_result)

        # Create a result that's failed
        failed_result = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.FAILED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        failed_result = create_result(db, failed_result)

        # Create a result that's still running (should not be cleaned up)
        running_result = Result(
            id=0,
            scenario_id=scenario.id,
            harness="claude-code",
            provider="anthropic",
            model="haiku",
            status=ResultStatus.RUNNING,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=1,
            driver="local",
        )
        running_result = create_result(db, running_result)

        # Enqueue tasks
        completed_task_id = enqueue_agent_run(
            db,
            result_id=completed_result.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
        )
        failed_task_id = enqueue_agent_run(
            db,
            result_id=failed_result.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
        )
        running_task_id = enqueue_agent_run(
            db,
            result_id=running_result.id,
            scenario_id=scenario.id,
            executor_spec="claude-code:anthropic:haiku",
            timeout_seconds=1,
            driver="local",
        )

        # Manually mark tasks as running (simulating a worker crash scenario)
        db.execute(
            "UPDATE tasks SET status = 'running', worker_id = 'test-worker' WHERE id IN (?, ?, ?)",
            (completed_task_id, failed_task_id, running_task_id),
        )
        db.commit()
        break

    # Run cleanup
    for db in get_db():
        cleaned_count = cleanup_stale_running_tasks(db)
        assert cleaned_count == 2  # Should clean up completed and failed tasks

        # Verify completed task was cleaned up
        completed_task = db.execute(
            "SELECT * FROM tasks WHERE id = ?", (completed_task_id,)
        ).fetchone()
        assert completed_task is not None
        assert completed_task["status"] == "completed"
        assert completed_task["finished_at"] is not None

        # Verify failed task was cleaned up
        failed_task = db.execute(
            "SELECT * FROM tasks WHERE id = ?", (failed_task_id,)
        ).fetchone()
        assert failed_task is not None
        assert failed_task["status"] == "failed"
        assert failed_task["finished_at"] is not None
        assert "result finished with status: failed" in (failed_task["error_message"] or "")

        # Verify running task was NOT cleaned up (result is still running)
        running_task = db.execute(
            "SELECT * FROM tasks WHERE id = ?", (running_task_id,)
        ).fetchone()
        assert running_task is not None
        assert running_task["status"] == "running"

        # Verify list_active_tasks calls cleanup automatically
        active_tasks = list_active_tasks(db)
        # Should only include the running task (completed and failed are no longer active)
        active_task_ids = [t.id for t in active_tasks]
        assert completed_task_id not in active_task_ids
        assert failed_task_id not in active_task_ids
        assert running_task_id in active_task_ids
        break

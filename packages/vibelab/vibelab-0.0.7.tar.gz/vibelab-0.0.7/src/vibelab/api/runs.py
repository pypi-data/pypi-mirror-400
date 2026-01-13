"""Run API endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import create_result, get_db, get_scenario
from ..engine.queue import enqueue_agent_run
from ..models.executor import ExecutorSpec
from ..models.result import Result, ResultStatus

router = APIRouter()


class CreateRunRequest(BaseModel):
    """Request to create a run."""

    scenario_id: int
    executor_spec: str
    timeout_seconds: int = 1800
    driver: str = "local"


@router.post("")
def create_run(request: CreateRunRequest):
    """Queue a new run."""
    executor_spec = ExecutorSpec.parse(request.executor_spec)
    for db in get_db():
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Create result record synchronously
        result = Result(
            id=0,  # Will be set by database
            scenario_id=request.scenario_id,
            harness=executor_spec.harness,
            provider=executor_spec.provider,
            model=executor_spec.model,
            status=ResultStatus.QUEUED,
            created_at=datetime.now(UTC),
            timeout_seconds=request.timeout_seconds,
            driver=request.driver,
        )
        result = create_result(db, result)

        # Get project_id for streaming log
        from ..db.queries import get_project_id_for_result

        project_id = get_project_id_for_result(db, result.id)
        if project_id is None:
            project_id = 1

        # Initialize streaming log early so frontend can connect immediately
        from ..engine.streaming import StreamingLog

        streaming_log = StreamingLog(result_id=result.id, project_id=project_id)
        streaming_log.set_status("queued")

        task_id = enqueue_agent_run(
            db,
            result_id=result.id,
            scenario_id=request.scenario_id,
            executor_spec=request.executor_spec,
            timeout_seconds=request.timeout_seconds,
            driver=request.driver,
        )

        return {
            "status": "queued",
            "scenario_id": request.scenario_id,
            "executor_spec": request.executor_spec,
            "result_id": result.id,
            "task_id": task_id,
        }

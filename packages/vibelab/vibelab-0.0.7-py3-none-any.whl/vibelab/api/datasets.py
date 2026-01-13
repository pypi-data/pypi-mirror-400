"""Dataset API endpoints."""

from datetime import UTC, datetime
from itertools import product
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import (
    add_scenario_to_dataset,
    create_dataset,
    create_result,
    delete_dataset,
    get_dataset,
    get_dataset_scenarios,
    get_db,
    get_scenario,
    list_datasets,
    list_judgements,
    list_results,
    remove_scenario_from_dataset,
)
from ..engine.metrics import aggregate_values, compute_ranks, compute_relative_score
from ..engine.queue import enqueue_agent_run
from ..models.dataset import Dataset
from ..models.executor import ExecutorSpec
from ..models.result import Result, ResultStatus
from ..models.scenario import Scenario

router = APIRouter()


class CreateDatasetRequest(BaseModel):
    """Request to create a dataset."""

    name: str
    description: str | None = None


class AddScenarioRequest(BaseModel):
    """Request to add a scenario to a dataset."""

    scenario_id: int


class CreateDatasetRunRequest(BaseModel):
    """Request to create a dataset run."""

    executor_specs: list[str]
    trials: int = 1
    minimal: bool = False
    timeout_seconds: int = 1800
    driver: str = "local"


@router.get("")
def list_datasets_endpoint(limit: int | None = None):
    """List datasets."""
    for db in get_db():
        datasets = list_datasets(db, limit=limit)
        datasets_with_scenarios = []
        for dataset in datasets:
            scenarios = get_dataset_scenarios(db, dataset.id)
            datasets_with_scenarios.append(
                {
                    **dataset.model_dump(),
                    "scenario_count": len(scenarios),
                }
            )
        return {"datasets": datasets_with_scenarios}


@router.get("/{dataset_id}")
def get_dataset_endpoint(dataset_id: int):
    """Get dataset with scenarios."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        scenarios = get_dataset_scenarios(db, dataset_id)
        return {
            "dataset": dataset.model_dump(),
            "scenarios": [s.model_dump() for s in scenarios],
        }


@router.post("")
def create_dataset_endpoint(request: CreateDatasetRequest):
    """Create a new dataset."""
    dataset = Dataset(
        id=0,
        name=request.name,
        description=request.description,
        created_at=datetime.now(UTC),
    )
    for db in get_db():
        dataset = create_dataset(db, dataset)
        break
    return dataset.model_dump()


@router.delete("/{dataset_id}")
def delete_dataset_endpoint(dataset_id: int):
    """Delete a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        deleted = delete_dataset(db, dataset_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Dataset not found")
        break
    return {"status": "deleted", "dataset_id": dataset_id}


@router.post("/{dataset_id}/scenarios")
def add_scenario_endpoint(dataset_id: int, request: AddScenarioRequest):
    """Add a scenario to a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        add_scenario_to_dataset(db, dataset_id, request.scenario_id)
        break
    return {"status": "added", "dataset_id": dataset_id, "scenario_id": request.scenario_id}


@router.delete("/{dataset_id}/scenarios/{scenario_id}")
def remove_scenario_endpoint(dataset_id: int, scenario_id: int):
    """Remove a scenario from a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        remove_scenario_from_dataset(db, dataset_id, scenario_id)
        break
    return {"status": "removed", "dataset_id": dataset_id, "scenario_id": scenario_id}


@router.post("/{dataset_id}/runs")
def create_dataset_run_endpoint(dataset_id: int, request: CreateDatasetRunRequest):
    """Queue runs for all scenarios in a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        scenarios = get_dataset_scenarios(db, dataset_id)
        if not scenarios:
            raise HTTPException(status_code=400, detail="Dataset has no scenarios")

        executor_specs = [ExecutorSpec.parse(e) for e in request.executor_specs]

        # Determine which scenario-executor pairs to run
        pairs_to_run = []
        if request.minimal:
            # Only run pairs that don't have completed results
            for scenario in scenarios:
                for executor_spec in executor_specs:
                    executor_spec_str = str(executor_spec)
                    results = list_results(
                        db, scenario_id=scenario.id, executor_spec=executor_spec_str
                    )
                    completed_count = sum(1 for r in results if r.status.value == "completed")
                    if completed_count == 0:
                        pairs_to_run.append((scenario, executor_spec))
        else:
            # Run all combinations with specified number of trials
            for scenario, executor_spec in product(scenarios, executor_specs):
                for _ in range(request.trials):
                    pairs_to_run.append((scenario, executor_spec))

        # Create result records for all pairs
        result_ids = []
        task_ids: list[int] = []
        for scenario, executor_spec in pairs_to_run:
            result = Result(
                id=0,
                scenario_id=scenario.id,
                harness=executor_spec.harness,
                provider=executor_spec.provider,
                model=executor_spec.model,
                status=ResultStatus.QUEUED,
                created_at=datetime.now(UTC),
                timeout_seconds=request.timeout_seconds,
                driver=request.driver,
            )
            result = create_result(db, result)
            result_ids.append(result.id)

            # Get project_id for streaming log
            from ..db.queries import get_project_id_for_result

            project_id = get_project_id_for_result(db, result.id)
            if project_id is None:
                project_id = 1

            # Initialize streaming log
            from ..engine.streaming import StreamingLog

            streaming_log = StreamingLog(result_id=result.id, project_id=project_id)
            streaming_log.set_status("queued")

            task_id = enqueue_agent_run(
                db,
                result_id=result.id,
                scenario_id=scenario.id,
                executor_spec=str(executor_spec),
                timeout_seconds=request.timeout_seconds,
                driver=request.driver,
            )
            task_ids.append(task_id)

        return {
            "status": "queued",
            "dataset_id": dataset_id,
            "pairs_run": len(pairs_to_run),
            "result_ids": result_ids,
            "task_ids": task_ids,
        }


def build_analytics_matrix(
    db: Any,
    scenarios: list[Scenario],
) -> dict[str, Any]:
    """Build analytics matrix for a set of scenarios.

    This is a shared function used by both dataset and global analytics endpoints.

    Returns a dict with:
        - executors: list of executor keys
        - matrix: list of row dicts with scenario info and cells
        - aggregations: global, byScenario, and byExecutor aggregations with std and relative scores
    """
    # Get all unique executors from results
    all_results = []
    for scenario in scenarios:
        results = list_results(db, scenario_id=scenario.id)
        all_results.extend(results)

    # Build executor set
    executors_set: set[str] = set()
    for result in all_results:
        executor_key = f"{result.harness}:{result.provider}:{result.model}"
        executors_set.add(executor_key)

    executors_list = sorted(list(executors_set))

    # Build matrix and collect aggregation data
    matrix = []

    # For aggregation tracking
    all_quality_scores: list[float] = []
    all_latency_values: list[float] = []
    executor_quality: dict[str, list[float]] = {e: [] for e in executors_list}
    executor_latency: dict[str, list[float]] = {e: [] for e in executors_list}
    scenario_quality: dict[int, list[float]] = {}
    scenario_latency: dict[int, list[float]] = {}

    for scenario in scenarios:
        scenario_quality[scenario.id] = []
        scenario_latency[scenario.id] = []

        row: dict[str, Any] = {
            "scenario_id": scenario.id,
            "scenario_prompt": scenario.prompt[:100] + "..."
            if len(scenario.prompt) > 100
            else scenario.prompt,
            "cells": {},
        }
        for executor_key in executors_list:
            results = list_results(db, scenario_id=scenario.id, executor_spec=executor_key)
            completed = [r for r in results if r.status.value == "completed"]
            failed = [
                r
                for r in results
                if r.status.value == "failed" or r.status.value == "infra_failure"
            ]
            timeout = [r for r in results if r.status.value == "timeout"]
            running = [r for r in results if r.status.value == "running" and not r.is_stale()]
            queued = [r for r in results if r.status.value == "queued"]

            # Determine overall status
            if len(completed) > 0:
                status = "completed"
            elif len(running) > 0:
                status = "running"
            elif len(queued) > 0:
                status = "queued"
            elif len(failed) > 0:
                status = "failed"
            elif len(timeout) > 0:
                status = "timeout"
            else:
                status = "pending"

            # Collect result IDs (prefer completed, then any)
            result_ids = [r.id for r in completed] if completed else [r.id for r in results]

            # Calculate quality stats from completed results
            # Use human quality if available, otherwise fall back to latest judgement quality
            quality_scores: list[float] = []
            for r in completed:
                if r.quality is not None:
                    # Human quality takes precedence
                    quality_scores.append(float(r.quality))
                else:
                    # Check for judgement quality
                    judgements = list_judgements(db, result_id=r.id)
                    if judgements:
                        # Get the latest judgement with a quality score
                        for j in sorted(judgements, key=lambda x: x.created_at, reverse=True):
                            if j.quality is not None:
                                quality_scores.append(float(j.quality))
                                break

            # Calculate quality metrics with std dev
            quality_agg = aggregate_values(quality_scores)

            # Calculate duration metrics from completed results
            durations = [float(r.duration_ms) for r in completed if r.duration_ms is not None]
            duration_agg = aggregate_values(durations)

            # Calculate avg cost from completed results
            costs = [r.cost_usd for r in completed if r.cost_usd is not None]
            avg_cost_usd = sum(costs) / len(costs) if costs else None

            # Track for aggregations
            all_quality_scores.extend(quality_scores)
            all_latency_values.extend(durations)
            executor_quality[executor_key].extend(quality_scores)
            executor_latency[executor_key].extend(durations)
            scenario_quality[scenario.id].extend(quality_scores)
            scenario_latency[scenario.id].extend(durations)

            row["cells"][executor_key] = {
                "status": status,
                "total": len(results),
                "completed": len(completed),
                "failed": len(failed),
                "timeout": len(timeout),
                "running": len(running),
                "queued": len(queued),
                "result_ids": result_ids,
                # Quality metrics with std dev
                "avg_quality": quality_agg.mean,
                "quality_std": quality_agg.std,
                "quality_count": quality_agg.count,
                # Latency metrics with std dev
                "avg_duration_ms": duration_agg.mean,
                "duration_std": duration_agg.std,
                "duration_count": duration_agg.count,
                # Cost metrics
                "avg_cost_usd": avg_cost_usd,
                "cost_count": len(costs),
            }
        matrix.append(row)

    # Build aggregations
    global_quality = aggregate_values(all_quality_scores)
    global_latency = aggregate_values(all_latency_values)

    # By-executor aggregations
    by_executor: dict[str, dict[str, Any]] = {}
    executor_means: dict[str, float | None] = {}
    for exec_key in executors_list:
        q_agg = aggregate_values(executor_quality[exec_key])
        l_agg = aggregate_values(executor_latency[exec_key])
        executor_means[exec_key] = q_agg.mean
        by_executor[exec_key] = {
            "quality": {"mean": q_agg.mean, "std": q_agg.std, "count": q_agg.count},
            "latency": {"mean": l_agg.mean, "std": l_agg.std, "count": l_agg.count},
        }

    # Compute ranks and relative scores for executors
    quality_ranks = compute_ranks(executor_means, higher_is_better=True)
    for exec_key in executors_list:
        by_executor[exec_key]["rank"] = quality_ranks.get(exec_key)
        exec_mean = executor_means.get(exec_key)
        if exec_mean is not None and global_quality.mean is not None:
            by_executor[exec_key]["relative"] = compute_relative_score(
                exec_mean, global_quality.mean, global_quality.std
            )
        else:
            by_executor[exec_key]["relative"] = None

    # By-scenario aggregations
    by_scenario: dict[int, dict[str, Any]] = {}
    for scen_id in scenario_quality:
        q_agg = aggregate_values(scenario_quality[scen_id])
        l_agg = aggregate_values(scenario_latency[scen_id])
        by_scenario[scen_id] = {
            "quality": {"mean": q_agg.mean, "std": q_agg.std, "count": q_agg.count},
            "latency": {"mean": l_agg.mean, "std": l_agg.std, "count": l_agg.count},
        }

    return {
        "executors": executors_list,
        "matrix": matrix,
        "aggregations": {
            "global": {
                "quality": {
                    "mean": global_quality.mean,
                    "std": global_quality.std,
                    "count": global_quality.count,
                },
                "latency": {
                    "mean": global_latency.mean,
                    "std": global_latency.std,
                    "count": global_latency.count,
                },
            },
            "byExecutor": by_executor,
            "byScenario": by_scenario,
        },
    }


@router.get("/{dataset_id}/analytics")
def get_dataset_analytics_endpoint(dataset_id: int):
    """Get analytics for a dataset showing scenario-executor matrix."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        scenarios = get_dataset_scenarios(db, dataset_id)

        analytics = build_analytics_matrix(db, scenarios)

        return {
            "dataset": dataset.model_dump(),
            **analytics,
        }

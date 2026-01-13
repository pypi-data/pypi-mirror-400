"""Judge API endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import (
    create_llm_scenario_judge,
    delete_llm_scenario_judge,
    get_db,
    get_judgement,
    get_judgement_for_result,
    get_latest_llm_scenario_judge,
    get_llm_scenario_judge,
    get_result,
    get_scenario,
    list_judgements,
    list_llm_scenario_judges,
    list_results,
    update_result_notes_and_quality,
)
from ..engine.judge import JudgeExecutor
from ..engine.queue import enqueue_judge_result, enqueue_train_judge
from ..models.judge import LLMScenarioJudge
from ..models.result import ResultStatus

router = APIRouter()


class CreateJudgeRequest(BaseModel):
    """Request to create an LLM scenario judge."""

    scenario_id: int
    guidance: str
    judge_provider: str = "anthropic"
    judge_model: str = "claude-sonnet-4-20250514"
    training_sample_ids: list[int] = Field(default_factory=list)


@router.post("")
def create_judge(request: CreateJudgeRequest):
    """Create a new LLM scenario judge."""
    for db in get_db():
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Validate sample IDs
        for sample_id in request.training_sample_ids:
            result = get_result(db, sample_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"Result {sample_id} not found")
            if result.scenario_id != request.scenario_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Result {sample_id} does not belong to scenario {request.scenario_id}",
                )

        judge = LLMScenarioJudge(
            id=0,  # Will be set by database
            scenario_id=request.scenario_id,
            guidance=request.guidance,
            judge_provider=request.judge_provider,
            judge_model=request.judge_model,
            training_sample_ids=request.training_sample_ids,
            alignment_score=None,
            created_at=datetime.now(UTC),
        )
        judge = create_llm_scenario_judge(db, judge)
        return judge.model_dump()


@router.put("/{judge_id}")
def update_judge(judge_id: int, request: CreateJudgeRequest):
    """Update an existing LLM scenario judge (creates a new version)."""
    # For now, we'll just create a new judge since judges evolve over time
    # But we validate the judge exists first
    for db in get_db():
        existing_judge = get_llm_scenario_judge(db, judge_id)
        if not existing_judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # Create new judge with updated data
        return create_judge(request)


@router.get("")
def list_judges(scenario_id: int | None = None):
    """List LLM scenario judges."""
    for db in get_db():
        judges = list_llm_scenario_judges(db, scenario_id=scenario_id)
        return [j.model_dump() for j in judges]


@router.get("/judgements/all")
def list_all_judgements():
    """List all judgements across all judges."""
    for db in get_db():
        judgements = list_judgements(db)
        # Enrich with result and judge info
        enriched = []
        for judgement in judgements:
            result = get_result(db, judgement.result_id)
            judge = get_llm_scenario_judge(db, judgement.judge_id)
            enriched.append(
                {
                    **judgement.model_dump(),
                    "result": result.model_dump() if result else None,
                    "judge": judge.model_dump() if judge else None,
                }
            )
        return enriched


@router.get("/judgements/pending")
def list_pending_judgements():
    """List completed results that don't have judgements yet (for informational purposes only).

    Note: Judgements are now triggered manually from the UI, one at a time.
    This endpoint is kept for informational purposes but doesn't represent a queue.
    """
    for db in get_db():
        from ..db import list_results
        from ..models.result import ResultStatus

        # Get all completed results
        all_results = list_results(db)
        completed_results = [r for r in all_results if r.status == ResultStatus.COMPLETED]

        # Find results that don't have judgements but have judges available
        pending = []
        for result in completed_results:
            judge = get_latest_llm_scenario_judge(db, result.scenario_id)
            if judge:
                # Check if judgement exists
                existing_judgement = get_judgement_for_result(db, result.id, judge.id)
                if not existing_judgement:
                    pending.append(
                        {
                            "result": result.model_dump(),
                            "judge": judge.model_dump(),
                        }
                    )

        return pending


@router.get("/scenarios/{scenario_id}/judgements")
def list_scenario_judgements(scenario_id: int):
    """List all judgements for a scenario (from all judges)."""
    for db in get_db():
        from ..db import list_llm_scenario_judges, list_results

        # Get all judges for this scenario
        judges = list_llm_scenario_judges(db, scenario_id=scenario_id)
        latest_judge_id = judges[0].id if judges else None

        # Get all results for this scenario
        results = list_results(db, scenario_id=scenario_id)

        # Get all judgements for these results
        enriched_judgements = []
        for result in results:
            # Get all judgements for this result
            result_judgements = list_judgements(db, result_id=result.id)
            for judgement in result_judgements:
                # Find the judge that made this judgement
                judge = next((j for j in judges if j.id == judgement.judge_id), None)
                if judge:
                    enriched_judgements.append(
                        {
                            **judgement.model_dump(),
                            "result": result.model_dump(),
                            "judge": judge.model_dump(),
                            "is_latest_judge": judgement.judge_id == latest_judge_id,
                        }
                    )

        return enriched_judgements


@router.post("/judgements/{judgement_id}/accept")
def accept_judgement(judgement_id: int):
    """Accept a judgement by copying its notes and quality to the result's human feedback."""
    for db in get_db():
        judgement = get_judgement(db, judgement_id)
        if not judgement:
            raise HTTPException(status_code=404, detail="Judgement not found")

        # Copy judgement notes and quality to result
        update_result_notes_and_quality(db, judgement.result_id, judgement.notes, judgement.quality)

        # Return updated result
        from ..db import get_result

        result = get_result(db, judgement.result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        return result.model_dump()


@router.get("/{judge_id}")
def get_judge(judge_id: int):
    """Get judge detail."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")
        return judge.model_dump()


class EvaluateAlignmentRequest(BaseModel):
    """Request to evaluate alignment score for a judge."""

    result_ids: list[int] = Field(default_factory=list)


@router.post("/{judge_id}/train")
def train_judge_endpoint(judge_id: int, request: EvaluateAlignmentRequest):
    """Evaluate alignment score for a judge on specified results (durable queue).

    If result_ids is empty, automatically finds all completed results with human quality scores
    for the judge's scenario.
    """
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # If no result_ids provided, automatically find all scorable results
        if not request.result_ids:
            from ..db import list_results
            from ..models.result import ResultStatus

            all_results = list_results(db, scenario_id=judge.scenario_id)
            # Filter to completed results with human quality scores
            scorable_result_ids = [
                r.id
                for r in all_results
                if r.status == ResultStatus.COMPLETED and r.quality is not None
            ]

            if not scorable_result_ids:
                raise HTTPException(
                    status_code=400,
                    detail="No completed results with human quality scores found for this scenario",
                )

            request.result_ids = scorable_result_ids
        else:
            # Validate provided result IDs
            for result_id in request.result_ids:
                result = get_result(db, result_id)
                if not result:
                    raise HTTPException(status_code=404, detail=f"Result {result_id} not found")
                if result.scenario_id != judge.scenario_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Result {result_id} does not belong to scenario {judge.scenario_id}",
                    )

        task_id = enqueue_train_judge(
            db,
            judge_id=judge_id,
            judge_provider=judge.judge_provider,
            judge_model=judge.judge_model,
            result_ids=request.result_ids,
        )
        return {"status": "queued", "judge_id": judge_id, "task_id": task_id}


@router.delete("/{judge_id}")
def delete_judge_endpoint(judge_id: int):
    """Delete a judge."""
    for db in get_db():
        deleted = delete_llm_scenario_judge(db, judge_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Judge not found")
        return {"status": "deleted", "judge_id": judge_id}


@router.get("/{judge_id}/judgements")
def list_judge_judgements(judge_id: int):
    """List judgements made by a judge."""
    for db in get_db():
        judgements = list_judgements(db, judge_id=judge_id)
        return [j.model_dump() for j in judgements]


@router.post("/{judge_id}/judge-result/{result_id}")
def judge_result_endpoint(
    judge_id: int,
    result_id: int,
    async_: bool = False,
):
    """Judge a result (sync by default; async_=true enqueues durable work)."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        if result.scenario_id != judge.scenario_id:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} does not belong to scenario {judge.scenario_id}",
            )

        if result.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} is not completed (status: {result.status})",
            )

        # Check if judgement already exists - if it's from an older judge version, allow replacement
        existing_judgement = get_judgement_for_result(db, result.id, judge_id)
        if existing_judgement:
            # Allow replacing if it's from an older judge version
            from ..db import get_latest_llm_scenario_judge

            latest_judge = get_latest_llm_scenario_judge(db, judge.scenario_id)
            if latest_judge and existing_judgement.judge_id == latest_judge.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Judgement already exists for result {result_id} from the latest judge",
                )
            # If it's from an older judge, we'll replace it (delete old, create new)
            from ..db import delete_judgement

            delete_judgement(db, existing_judgement.id)

        if async_:
            task_id = enqueue_judge_result(
                db,
                judge_id=judge_id,
                target_result_id=result_id,
                judge_provider=judge.judge_provider,
                judge_model=judge.judge_model,
                priority=10,
            )
            return {
                "status": "queued",
                "judge_id": judge_id,
                "result_id": result_id,
                "task_id": task_id,
            }

        executor = JudgeExecutor()
        try:
            judgement = executor.execute_judge(judge, result)
            return judgement.model_dump()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to execute judge {judge_id} on result {result_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute judge: {str(e)}",
            )


class ApplyJudgeRequest(BaseModel):
    """Request to apply judge to results."""

    result_ids: list[int] | None = None  # If None, apply to all completed results for scenario
    force: bool = False  # If true, re-evaluate even if a judgement already exists for this judge_id


@router.post("/{judge_id}/apply")
def apply_judge_endpoint(judge_id: int, request: ApplyJudgeRequest, async_: bool = False):
    """Apply judge to results (sync by default; async_=true enqueues durable work)."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # Resolve target results.
        if request.result_ids is None:
            results = list_results(db, scenario_id=judge.scenario_id)
            completed_ids = [r.id for r in results if r.status == ResultStatus.COMPLETED]
            target_ids = completed_ids
        else:
            target_ids = request.result_ids

        if not target_ids:
            return {"status": "queued" if async_ else "done", "judge_id": judge_id, "total": 0}

        # Async: enqueue one task per result.
        if async_:
            queued = 0
            for rid in target_ids:
                result = get_result(db, rid)
                if not result:
                    continue
                if result.scenario_id != judge.scenario_id:
                    continue
                if result.status != ResultStatus.COMPLETED:
                    continue

                existing = get_judgement_for_result(db, result.id, judge_id)
                if existing and not request.force:
                    continue
                if existing and request.force:
                    from ..db import delete_judgement

                    delete_judgement(db, existing.id)

                enqueue_judge_result(
                    db,
                    judge_id=judge_id,
                    target_result_id=rid,
                    judge_provider=judge.judge_provider,
                    judge_model=judge.judge_model,
                    priority=10,
                )
                queued += 1

            return {"status": "queued", "judge_id": judge_id, "total": queued}

        # Sync: for safety/latency, only allow a single result synchronously.
        if len(target_ids) != 1:
            raise HTTPException(
                status_code=400,
                detail="Synchronous apply only supports a single result_id. Use async_=true to apply to multiple results.",
            )

        result_id = target_ids[0]
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        if result.scenario_id != judge.scenario_id:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} does not belong to scenario {judge.scenario_id}",
            )

        if result.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} is not completed (status: {result.status})",
            )

        # Check if judgement already exists
        existing_judgement = get_judgement_for_result(db, result.id, judge_id)
        if existing_judgement:
            if not request.force:
                raise HTTPException(
                    status_code=400,
                    detail=f"Judgement already exists for result {result_id} from this judge",
                )
            from ..db import delete_judgement

            delete_judgement(db, existing_judgement.id)

        # Execute judge synchronously
        executor = JudgeExecutor()
        try:
            judgement = executor.execute_judge(judge, result)
            return judgement.model_dump()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to execute judge {judge_id} on result {result_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute judge: {str(e)}",
            )


@router.get("/models")
def list_judge_models():
    """List available judge models from LiteLLM (filtered to OpenAI and Anthropic)."""
    from ..pricing import LITELLM_AVAILABLE

    if not LITELLM_AVAILABLE:
        # Fallback to hardcoded models if LiteLLM not available
        return {
            "providers": [
                {
                    "id": "anthropic",
                    "name": "Anthropic",
                    "models": [
                        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
                        {"id": "claude-opus-4-20250514", "name": "Claude Opus 4"},
                        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
                    ],
                },
                {
                    "id": "openai",
                    "name": "OpenAI",
                    "models": [
                        {"id": "gpt-4o", "name": "GPT-4o"},
                        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                        {"id": "o1", "name": "o1"},
                    ],
                },
            ]
        }

    try:
        from typing import Any

        from litellm import model_cost

        # Define which providers to include and their display names
        provider_config = {
            "openai": {"name": "OpenAI", "prefix": "openai/"},
            "anthropic": {"name": "Anthropic", "prefix": "anthropic/"},
        }

        providers_data: dict[str, dict[str, Any]] = {}

        for model_id, cost_data in model_cost.items():
            litellm_provider = cost_data.get("litellm_provider", "")

            # Determine which provider this model belongs to
            provider_key = None
            if (
                "openai" in litellm_provider.lower()
                or model_id.startswith("gpt-")
                or model_id.startswith("o1")
                or model_id.startswith("o3")
            ):
                provider_key = "openai"
            elif "anthropic" in litellm_provider.lower() or model_id.startswith("claude"):
                provider_key = "anthropic"

            if not provider_key:
                continue

            # Skip models without pricing (experimental/deprecated)
            input_cost = cost_data.get("input_cost_per_token", 0)
            output_cost = cost_data.get("output_cost_per_token", 0)
            if input_cost == 0 and output_cost == 0:
                continue

            # Skip non-chat models
            mode = cost_data.get("mode", "")
            if mode and mode not in ("chat", ""):
                continue

            # Skip prefixed duplicates (prefer non-prefixed)
            if "/" in model_id:
                base_id = model_id.split("/", 1)[1]
                if base_id in model_cost:
                    continue

            # Initialize provider if not exists
            if provider_key not in providers_data:
                providers_data[provider_key] = {
                    "id": provider_key,
                    "name": provider_config[provider_key]["name"],
                    "models": [],
                }

            # Format model name nicely
            model_name = model_id.replace("-", " ").title()
            # Fix common naming issues
            model_name = model_name.replace("Gpt ", "GPT-")
            model_name = model_name.replace("O1 ", "o1-")
            model_name = model_name.replace("O3 ", "o3-")
            model_name = model_name.replace("Claude ", "Claude ")

            # Calculate price per 1M tokens for display
            input_price_1m = input_cost * 1_000_000
            output_price_1m = output_cost * 1_000_000

            providers_data[provider_key]["models"].append(
                {
                    "id": model_id,
                    "name": model_name,
                    "input_price_per_1m": round(input_price_1m, 4),
                    "output_price_per_1m": round(output_price_1m, 4),
                }
            )

        # Sort models within each provider by name
        for provider in providers_data.values():
            provider["models"].sort(key=lambda m: m["name"])

        # Return providers in consistent order
        result = []
        for key in ["anthropic", "openai"]:
            if key in providers_data:
                result.append(providers_data[key])

        return {"providers": result}

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.exception(f"Failed to load models from LiteLLM: {e}")
        # Fallback to hardcoded models
        return {
            "providers": [
                {
                    "id": "anthropic",
                    "name": "Anthropic",
                    "models": [
                        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
                        {"id": "claude-opus-4-20250514", "name": "Claude Opus 4"},
                    ],
                },
                {
                    "id": "openai",
                    "name": "OpenAI",
                    "models": [
                        {"id": "gpt-4o", "name": "GPT-4o"},
                        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                    ],
                },
            ]
        }

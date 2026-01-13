"""Review Queue API endpoints.

The Review Queue is an annotation interface that helps humans efficiently
score results to maximize judge alignment. The prioritization algorithm:

1. Balances across scenarios (don't fill up one scenario first)
2. Prioritizes score diversity (use LLM judge predictions to get spread)
3. Targets scenarios with judges that need alignment data
"""

import logging
from collections import defaultdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import (
    get_db,
    get_judgement_for_result,
    get_result,
    get_scenario,
    list_llm_scenario_judges,
    list_results,
    update_result_notes_and_quality,
)
from ..models.result import ResultStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class ReviewQueueStats(BaseModel):
    """Statistics for the review queue."""

    queue_length: int = Field(description="Total unscored results with judges")
    scored_count: int = Field(description="Total human-scored results")
    alignment_score: float | None = Field(description="Overall alignment score (0-1)")
    alignment_samples: int = Field(description="Number of alignment samples")
    scenarios_with_judges: int = Field(description="Scenarios that have judges configured")
    target_per_scenario: int = Field(default=10, description="Target samples per scenario")


class ReviewQueueItem(BaseModel):
    """A single item in the review queue."""

    result_id: int
    scenario_id: int
    scenario_prompt: str
    executor: str
    harness: str
    provider: str
    model: str
    duration_ms: int | None
    # Judge prediction (if available)
    judge_quality: int | None = Field(description="LLM judge's predicted quality (1-4)")
    judge_notes: str | None = Field(description="LLM judge's notes")
    judge_id: int | None
    # Prioritization info
    scenario_scored_count: int = Field(
        description="How many results are human-scored for this scenario"
    )
    priority_reason: str = Field(description="Why this item was prioritized")


class SubmitScoreRequest(BaseModel):
    """Request to score a result."""

    quality: int = Field(
        ge=1, le=4, description="Quality score: 4=Perfect, 3=Good, 2=Workable, 1=Bad"
    )
    notes: str | None = None


def compute_global_alignment(db) -> tuple[float | None, int]:
    """Compute global alignment across all judges.

    Returns:
        Tuple of (alignment_score, sample_count)
    """
    judges = list_llm_scenario_judges(db)
    if not judges:
        return None, 0

    total_matches = 0
    total_pairs = 0

    for judge in judges:
        results = list_results(db, scenario_id=judge.scenario_id)
        for result in results:
            if result.status != ResultStatus.COMPLETED:
                continue
            if result.quality is None:
                continue

            judgement = get_judgement_for_result(db, result.id, judge.id)
            if not judgement or judgement.quality is None:
                continue

            total_pairs += 1
            if result.quality == judgement.quality:
                total_matches += 1

    if total_pairs == 0:
        return None, 0

    return total_matches / total_pairs, total_pairs


def build_review_queue(db, limit: int = 50) -> list[ReviewQueueItem]:
    """Build prioritized review queue.

    Prioritization algorithm:
    1. Only include scenarios that have judges configured
    2. Balance across scenarios (prioritize scenarios with fewer human scores)
    3. Within scenarios, prioritize score diversity using judge predictions
    """
    # Get all scenarios with judges
    judges = list_llm_scenario_judges(db)
    judge_by_scenario: dict[int, int] = {}  # scenario_id -> latest judge_id
    for judge in sorted(judges, key=lambda j: j.created_at, reverse=True):
        if judge.scenario_id not in judge_by_scenario:
            judge_by_scenario[judge.scenario_id] = judge.id

    if not judge_by_scenario:
        return []

    # Collect unscored results per scenario
    scenario_unscored: dict[int, list[dict]] = defaultdict(list)
    scenario_scored_count: dict[int, int] = defaultdict(int)
    scenario_score_distribution: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))

    for scenario_id, judge_id in judge_by_scenario.items():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            continue

        results = list_results(db, scenario_id=scenario_id)
        for result in results:
            if result.status != ResultStatus.COMPLETED:
                continue

            if result.quality is not None:
                # Track scored results
                scenario_scored_count[scenario_id] += 1
                scenario_score_distribution[scenario_id][result.quality] += 1
            else:
                # Get judge prediction
                judgement = get_judgement_for_result(db, result.id, judge_id)
                judge_quality = judgement.quality if judgement else None
                judge_notes = judgement.notes if judgement else None

                scenario_unscored[scenario_id].append(
                    {
                        "result": result,
                        "scenario": scenario,
                        "judge_id": judge_id,
                        "judge_quality": judge_quality,
                        "judge_notes": judge_notes,
                    }
                )

    # Prioritization: Round-robin across scenarios, sorted by least-scored first
    # Within each scenario, prioritize by judge prediction diversity
    queue: list[ReviewQueueItem] = []

    # Sort scenarios by scored count (ascending) - prioritize underrepresented
    scenario_order = sorted(scenario_unscored.keys(), key=lambda s: scenario_scored_count[s])

    # Round-robin until we have enough items
    while len(queue) < limit and any(scenario_unscored.values()):
        for scenario_id in scenario_order:
            if not scenario_unscored[scenario_id]:
                continue
            if len(queue) >= limit:
                break

            # Pick the best candidate from this scenario
            # Strategy: Pick the result whose judge prediction is least represented
            candidates = scenario_unscored[scenario_id]
            dist = scenario_score_distribution[scenario_id]

            # Score each candidate by how much diversity it would add
            def diversity_score(item: dict) -> tuple[int, int]:
                jq = item["judge_quality"]
                if jq is None:
                    # No prediction - medium priority
                    return (1, 0)
                # Prioritize scores that are underrepresented
                current_count = dist.get(jq, 0)
                return (0, current_count)  # Lower is better

            candidates.sort(key=diversity_score)
            item = candidates.pop(0)

            result = item["result"]
            scenario = item["scenario"]

            # Determine priority reason
            scored = scenario_scored_count[scenario_id]
            if scored == 0:
                reason = "No human scores yet"
            elif item["judge_quality"] is not None:
                jq = item["judge_quality"]
                count = dist.get(jq, 0)
                if count == 0:
                    reason = f"New score value ({jq})"
                else:
                    reason = f"Balance scores (has {count}x {jq}s)"
            else:
                reason = "Needs scoring"

            queue.append(
                ReviewQueueItem(
                    result_id=result.id,
                    scenario_id=scenario.id,
                    scenario_prompt=scenario.prompt[:200] + "..."
                    if len(scenario.prompt) > 200
                    else scenario.prompt,
                    executor=f"{result.harness}:{result.provider}:{result.model}",
                    harness=result.harness,
                    provider=result.provider,
                    model=result.model,
                    duration_ms=result.duration_ms,
                    judge_quality=item["judge_quality"],
                    judge_notes=item["judge_notes"],
                    judge_id=item["judge_id"],
                    scenario_scored_count=scored,
                    priority_reason=reason,
                )
            )

            # Update distribution as if this will be scored
            if item["judge_quality"] is not None:
                dist[item["judge_quality"]] += 1

    return queue


@router.get("/stats")
def get_review_queue_stats():
    """Get review queue statistics."""
    for db in get_db():
        # Get judges
        judges = list_llm_scenario_judges(db)
        judge_scenario_ids = {j.scenario_id for j in judges}

        # Count unscored and scored results in scenarios with judges
        queue_length = 0
        scored_count = 0

        for scenario_id in judge_scenario_ids:
            results = list_results(db, scenario_id=scenario_id)
            for result in results:
                if result.status != ResultStatus.COMPLETED:
                    continue
                if result.quality is not None:
                    scored_count += 1
                else:
                    queue_length += 1

        # Compute alignment
        alignment, samples = compute_global_alignment(db)

        return ReviewQueueStats(
            queue_length=queue_length,
            scored_count=scored_count,
            alignment_score=alignment,
            alignment_samples=samples,
            scenarios_with_judges=len(judge_scenario_ids),
            target_per_scenario=10,
        )


@router.get("")
def get_review_queue(limit: int = 20):
    """Get prioritized review queue items."""
    for db in get_db():
        queue = build_review_queue(db, limit=limit)
        return {"items": [item.model_dump() for item in queue]}


@router.get("/next")
def get_next_review_item():
    """Get the single next item to review."""
    for db in get_db():
        queue = build_review_queue(db, limit=1)
        if not queue:
            return {"item": None}
        return {"item": queue[0].model_dump()}


@router.post("/{result_id}/score")
def score_result(result_id: int, request: SubmitScoreRequest):
    """Submit a score for a result."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        if result.status != ResultStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Can only score completed results")

        # Update the result
        update_result_notes_and_quality(db, result_id, request.notes, request.quality)

        # Get updated result
        updated = get_result(db, result_id)

        # Re-evaluate alignment for all judges on this scenario
        from ..engine.judge import evaluate_alignment_score

        judges = list_llm_scenario_judges(db, scenario_id=result.scenario_id)
        for judge in judges:
            results = list_results(db, scenario_id=judge.scenario_id)
            result_ids = [
                r.id
                for r in results
                if r.status == ResultStatus.COMPLETED and r.quality is not None
            ]
            if result_ids:
                evaluate_alignment_score(judge, result_ids)

        return {
            "status": "scored",
            "result_id": result_id,
            "quality": request.quality,
            "result": updated.model_dump() if updated else None,
        }


@router.post("/{result_id}/skip")
def skip_result(result_id: int):
    """Skip a result (no-op, just returns next item)."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        # Get next item (excluding this one - but since we're getting limit=2,
        # we can return the second one if it exists)
        queue = build_review_queue(db, limit=5)
        next_items = [item for item in queue if item.result_id != result_id]

        return {
            "status": "skipped",
            "result_id": result_id,
            "next_item": next_items[0].model_dump() if next_items else None,
        }


"""Pairwise comparison API endpoints.

Provides endpoints for creating, viewing, and managing pairwise preferences,
as well as smart pair selection and ranking computation.
"""

import logging
from itertools import combinations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db import (
    count_pairwise_preferences,
    count_result_comparisons,
    create_pairwise_preference,
    delete_pairwise_preference,
    get_compared_result_pairs,
    get_db,
    get_judgement_for_result,
    get_pairwise_preference,
    get_pairwise_preference_for_results,
    get_result,
    get_scenario,
    list_llm_scenario_judges,
    list_pairwise_preferences,
    list_results,
    update_pairwise_preference,
)
from ..models.pairwise import (
    PairwisePreferenceCreate,
    PairwiseStats,
    PreferenceType,
    compute_pairwise_alignment,
    compute_rankings,
)
from ..models.result import ResultStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class CreatePreferenceRequest(BaseModel):
    """Request to create a pairwise preference."""

    result_a_id: int
    result_b_id: int
    preference: PreferenceType
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Confidence in the preference"
    )
    notes: str | None = None


class NextPairResponse(BaseModel):
    """Response with the next pair to compare."""

    result_a_id: int
    result_b_id: int
    scenario_id: int
    scenario_prompt: str
    result_a_executor: str
    result_b_executor: str
    result_a_duration_ms: int | None
    result_b_duration_ms: int | None
    # Judge hints
    judge_a_quality: int | None = None
    judge_b_quality: int | None = None
    # Context
    scenario_comparison_count: int
    priority_reason: str


def get_next_pair_to_compare(db, scenario_id: int | None = None) -> NextPairResponse | None:
    """Get the next best pair to compare using smart selection.

    Priority algorithm:
    1. Balance across scenarios (prioritize scenarios with fewer comparisons)
    2. Prioritize pairs that haven't been compared
    3. Within uncompared pairs, prefer pairs where judge scores differ (informative)
    4. Prefer results with fewer total comparisons (coverage)
    """
    # Get scenarios with judges (only compare within scenarios that have judges)
    judges = list_llm_scenario_judges(db)
    scenario_judge_map: dict[int, int] = {}  # scenario_id -> latest judge_id
    for judge in sorted(judges, key=lambda j: j.created_at, reverse=True):
        if judge.scenario_id not in scenario_judge_map:
            scenario_judge_map[judge.scenario_id] = judge.id

    if not scenario_judge_map:
        return None

    # Filter to requested scenario if specified
    if scenario_id is not None:
        if scenario_id not in scenario_judge_map:
            return None
        scenario_ids = [scenario_id]
    else:
        scenario_ids = list(scenario_judge_map.keys())

    # For each scenario, find the best uncompared pair
    best_pair = None
    best_score = -1

    # Sort scenarios by comparison count (prioritize underrepresented)
    scenario_comparison_counts = {
        sid: count_pairwise_preferences(db, scenario_id=sid) for sid in scenario_ids
    }
    sorted_scenarios = sorted(scenario_ids, key=lambda s: scenario_comparison_counts[s])

    for sid in sorted_scenarios:
        scenario = get_scenario(db, sid)
        if not scenario:
            continue

        # Get completed results for this scenario
        results = list_results(db, scenario_id=sid)
        completed = [r for r in results if r.status == ResultStatus.COMPLETED]

        if len(completed) < 2:
            continue

        # Get already-compared pairs
        compared = get_compared_result_pairs(db, sid)

        # Get judge scores for prioritization
        judge_id = scenario_judge_map[sid]
        judge_scores: dict[int, int | None] = {}
        for r in completed:
            judgement = get_judgement_for_result(db, r.id, judge_id)
            judge_scores[r.id] = judgement.quality if judgement else None

        # Find uncompared pairs
        for r1, r2 in combinations(completed, 2):
            # Normalize order
            a_id, b_id = (r1.id, r2.id) if r1.id < r2.id else (r2.id, r1.id)

            if (a_id, b_id) in compared:
                continue

            # Score this pair for prioritization
            # Lower comparison count = higher priority
            a_comp = count_result_comparisons(db, a_id)
            b_comp = count_result_comparisons(db, b_id)
            coverage_score = 10 - min(a_comp + b_comp, 10)

            # Judge score difference = higher priority (more informative)
            score_a = judge_scores.get(a_id)
            score_b = judge_scores.get(b_id)
            if score_a is not None and score_b is not None:
                diff_score = abs(score_a - score_b)
            else:
                diff_score = 2  # Medium priority if no judge scores

            # Scenario underrepresentation bonus
            scenario_bonus = 5 - min(scenario_comparison_counts[sid], 5)

            total_score = coverage_score + diff_score + scenario_bonus

            if total_score > best_score:
                best_score = total_score
                result_a = r1 if r1.id == a_id else r2
                result_b = r2 if r1.id == a_id else r1

                # Determine priority reason
                if scenario_comparison_counts[sid] == 0:
                    reason = "New scenario"
                elif a_comp == 0 or b_comp == 0:
                    reason = "New result"
                elif diff_score >= 2:
                    reason = f"Judge scores differ ({score_a} vs {score_b})"
                else:
                    reason = "Coverage balance"

                best_pair = NextPairResponse(
                    result_a_id=a_id,
                    result_b_id=b_id,
                    scenario_id=sid,
                    scenario_prompt=(
                        scenario.prompt[:200] + "..."
                        if len(scenario.prompt) > 200
                        else scenario.prompt
                    ),
                    result_a_executor=(
                        f"{result_a.harness}:{result_a.provider}:{result_a.model}"
                    ),
                    result_b_executor=(
                        f"{result_b.harness}:{result_b.provider}:{result_b.model}"
                    ),
                    result_a_duration_ms=result_a.duration_ms,
                    result_b_duration_ms=result_b.duration_ms,
                    judge_a_quality=score_a,
                    judge_b_quality=score_b,
                    scenario_comparison_count=scenario_comparison_counts[sid],
                    priority_reason=reason,
                )

    return best_pair


@router.get("/stats")
def get_pairwise_stats():
    """Get overall pairwise comparison statistics."""
    for db in get_db():
        total = count_pairwise_preferences(db)

        # Count scenarios with preferences
        all_prefs = list_pairwise_preferences(db)
        scenarios_with_prefs = len({p.scenario_id for p in all_prefs})

        # Count unique results
        unique_results = set()
        for p in all_prefs:
            unique_results.add(p.result_a_id)
            unique_results.add(p.result_b_id)

        avg_per_result = (
            (total * 2 / len(unique_results)) if unique_results else None
        )

        return PairwiseStats(
            total_preferences=total,
            scenarios_with_preferences=scenarios_with_prefs,
            unique_results_compared=len(unique_results),
            average_comparisons_per_result=avg_per_result,
        )


@router.get("")
def list_preferences(scenario_id: int | None = None, result_id: int | None = None):
    """List pairwise preferences with optional filters."""
    for db in get_db():
        prefs = list_pairwise_preferences(db, scenario_id=scenario_id, result_id=result_id)
        return {"preferences": [p.model_dump() for p in prefs]}


@router.get("/next")
def get_next_pair(scenario_id: int | None = None):
    """Get the next pair to compare."""
    for db in get_db():
        pair = get_next_pair_to_compare(db, scenario_id=scenario_id)
        if not pair:
            return {"pair": None, "message": "No more pairs to compare"}
        return {"pair": pair.model_dump()}


@router.get("/rankings")
def get_rankings(scenario_id: int):
    """Get rankings for a scenario based on pairwise preferences."""
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Get completed results
        results = list_results(db, scenario_id=scenario_id)
        completed = [r for r in results if r.status == ResultStatus.COMPLETED]
        result_ids = [r.id for r in completed]

        # Get preferences
        prefs = list_pairwise_preferences(db, scenario_id=scenario_id)

        # Compute rankings
        rankings = compute_rankings(prefs, result_ids)

        # Add executor info
        result_map = {r.id: r for r in completed}
        rankings_with_info = []
        for ranking in rankings:
            result = result_map.get(ranking.result_id)
            rankings_with_info.append({
                **ranking.model_dump(),
                "executor": f"{result.harness}:{result.provider}:{result.model}"
                if result
                else None,
            })

        return {"scenario_id": scenario_id, "rankings": rankings_with_info}


@router.get("/alignment")
def get_pairwise_alignment(scenario_id: int | None = None, judge_id: int | None = None):
    """Get pairwise alignment statistics.

    If judge_id is provided, uses that specific judge.
    If scenario_id is provided, uses the latest judge for that scenario.
    """
    for db in get_db():
        # Determine which judge to use
        if judge_id is not None:
            from ..db import get_llm_scenario_judge

            judge = get_llm_scenario_judge(db, judge_id)
            if not judge:
                raise HTTPException(status_code=404, detail="Judge not found")
            judges_to_check = [judge]
        elif scenario_id is not None:
            judges_to_check = list_llm_scenario_judges(db, scenario_id=scenario_id)
            if not judges_to_check:
                raise HTTPException(
                    status_code=404, detail="No judges found for scenario"
                )
        else:
            judges_to_check = list_llm_scenario_judges(db)

        # Aggregate alignment across all judges
        all_stats: list[dict] = []
        for judge in judges_to_check:
            prefs = list_pairwise_preferences(db, scenario_id=judge.scenario_id)
            if not prefs:
                continue

            # Get judge scores for all results
            judge_scores: dict[int, int | None] = {}
            result_ids = set()
            for p in prefs:
                result_ids.add(p.result_a_id)
                result_ids.add(p.result_b_id)

            for rid in result_ids:
                judgement = get_judgement_for_result(db, rid, judge.id)
                judge_scores[rid] = judgement.quality if judgement else None

            stats = compute_pairwise_alignment(prefs, judge_scores)
            all_stats.append({
                "judge_id": judge.id,
                "scenario_id": judge.scenario_id,
                **stats.model_dump(),
            })

        # Compute overall accuracy
        total_pairs = sum(s["total_pairs"] for s in all_stats)
        total_correct = sum(s["correct_predictions"] for s in all_stats)
        overall_accuracy = total_correct / total_pairs if total_pairs > 0 else None

        return {
            "overall_pairwise_accuracy": overall_accuracy,
            "total_pairs": total_pairs,
            "total_correct": total_correct,
            "by_judge": all_stats,
        }


@router.post("")
def create_preference(request: CreatePreferenceRequest):
    """Create a new pairwise preference."""
    for db in get_db():
        # Validate results exist and are from same scenario
        result_a = get_result(db, request.result_a_id)
        result_b = get_result(db, request.result_b_id)

        if not result_a:
            raise HTTPException(
                status_code=404, detail=f"Result {request.result_a_id} not found"
            )
        if not result_b:
            raise HTTPException(
                status_code=404, detail=f"Result {request.result_b_id} not found"
            )

        if result_a.scenario_id != result_b.scenario_id:
            raise HTTPException(
                status_code=400,
                detail="Results must be from the same scenario",
            )

        if result_a.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {request.result_a_id} is not completed",
            )
        if result_b.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {request.result_b_id} is not completed",
            )

        # Normalize ordering using the model
        create_model = PairwisePreferenceCreate(
            result_a_id=request.result_a_id,
            result_b_id=request.result_b_id,
            preference=request.preference,
            confidence=request.confidence,
            notes=request.notes,
        )

        # Check if preference already exists
        existing = get_pairwise_preference_for_results(
            db, create_model.result_a_id, create_model.result_b_id
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Preference already exists (id={existing.id})",
            )

        # Create preference
        pref = create_pairwise_preference(
            db,
            scenario_id=result_a.scenario_id,
            result_a_id=create_model.result_a_id,
            result_b_id=create_model.result_b_id,
            preference=create_model.preference,
            confidence=create_model.confidence,
            notes=create_model.notes,
        )

        return {"preference": pref.model_dump()}


@router.get("/{preference_id}")
def get_preference(preference_id: int):
    """Get a specific pairwise preference."""
    for db in get_db():
        pref = get_pairwise_preference(db, preference_id)
        if not pref:
            raise HTTPException(status_code=404, detail="Preference not found")
        return {"preference": pref.model_dump()}


@router.put("/{preference_id}")
def update_preference(
    preference_id: int,
    preference: PreferenceType | None = None,
    confidence: float | None = None,
    notes: str | None = None,
):
    """Update a pairwise preference."""
    for db in get_db():
        existing = get_pairwise_preference(db, preference_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Preference not found")

        updated = update_pairwise_preference(
            db,
            preference_id,
            preference=preference,
            confidence=confidence,
            notes=notes,
        )
        return {"preference": updated.model_dump() if updated else None}


@router.delete("/{preference_id}")
def delete_preference(preference_id: int):
    """Delete a pairwise preference."""
    for db in get_db():
        deleted = delete_pairwise_preference(db, preference_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Preference not found")
        return {"status": "deleted", "id": preference_id}


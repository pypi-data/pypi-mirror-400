from __future__ import annotations

from datetime import datetime, timezone

from vibelab.db import (
    create_judgement,
    create_llm_scenario_judge,
    create_result,
    create_scenario,
    get_db,
    get_llm_scenario_judge,
    update_result_quality,
)
from vibelab.engine.judge import evaluate_alignment_score
from vibelab.models.judge import LLMScenarioJudge, Judgement
from vibelab.models.result import Result, ResultStatus
from vibelab.models.scenario import CodeType, Scenario


def test_alignment_score_uses_existing_judgements_only() -> None:
    now = datetime.now(timezone.utc)

    for db in get_db():
        scenario = create_scenario(
            db,
            Scenario(id=0, code_type=CodeType.EMPTY, code_ref=None, prompt="p", created_at=now),
        )
        # Two completed results with human quality
        r1 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="cursor",
                provider="anthropic",
                model="claude",
                status=ResultStatus.COMPLETED,
                created_at=now,
            ),
        )
        update_result_quality(db, r1.id, 4)
        r2 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="cursor",
                provider="anthropic",
                model="claude",
                status=ResultStatus.COMPLETED,
                created_at=now,
            ),
        )
        update_result_quality(db, r2.id, 2)
        judge = create_llm_scenario_judge(
            db,
            LLMScenarioJudge(
                id=0,
                scenario_id=scenario.id,
                guidance="g",
                training_sample_ids=[],
                alignment_score=None,
                created_at=now,
            ),
        )

        # Only create an existing judgement for r1 (r2 missing -> should be skipped)
        create_judgement(
            db,
            Judgement(
                id=0,
                result_id=r1.id,
                judge_id=judge.id,
                notes="ok",
                quality=4,
                created_at=now,
            ),
        )
        break

    # With only one overlapping pair, score is 1.0 when they match.
    alignment = evaluate_alignment_score(judge, result_ids=[r1.id, r2.id])
    assert alignment == 1.0

    for db in get_db():
        refreshed = get_llm_scenario_judge(db, judge.id)
        assert refreshed is not None
        assert refreshed.alignment_score == 1.0
        break


def test_alignment_score_partial_match() -> None:
    """Test alignment with partial matches (previously failed with Pearson correlation)."""
    now = datetime.now(timezone.utc)

    for db in get_db():
        scenario = create_scenario(
            db,
            Scenario(id=0, code_type=CodeType.EMPTY, code_ref=None, prompt="p", created_at=now),
        )
        # Two completed results with different human quality scores
        r1 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="cursor",
                provider="anthropic",
                model="claude",
                status=ResultStatus.COMPLETED,
                created_at=now,
            ),
        )
        update_result_quality(db, r1.id, 4)  # Human says 4
        r2 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="cursor",
                provider="anthropic",
                model="claude",
                status=ResultStatus.COMPLETED,
                created_at=now,
            ),
        )
        update_result_quality(db, r2.id, 2)  # Human says 2
        judge = create_llm_scenario_judge(
            db,
            LLMScenarioJudge(
                id=0,
                scenario_id=scenario.id,
                guidance="g",
                training_sample_ids=[],
                alignment_score=None,
                created_at=now,
            ),
        )

        # Judge gives same score (4) to both results
        create_judgement(
            db,
            Judgement(
                id=0,
                result_id=r1.id,
                judge_id=judge.id,
                notes="ok",
                quality=4,  # Matches human
                created_at=now,
            ),
        )
        create_judgement(
            db,
            Judgement(
                id=0,
                result_id=r2.id,
                judge_id=judge.id,
                notes="ok",
                quality=4,  # Does NOT match human (human=2)
                created_at=now,
            ),
        )
        break

    # 1 out of 2 matches -> 50% alignment
    # Note: Previously this returned 0.0 due to Pearson correlation failing
    # when judge scores had no variance.
    alignment = evaluate_alignment_score(judge, result_ids=[r1.id, r2.id])
    assert alignment == 0.5

    for db in get_db():
        refreshed = get_llm_scenario_judge(db, judge.id)
        assert refreshed is not None
        assert refreshed.alignment_score == 0.5
        break


def test_alignment_score_returns_none_if_no_pairs() -> None:
    now = datetime.now(timezone.utc)

    for db in get_db():
        scenario = create_scenario(
            db,
            Scenario(id=0, code_type=CodeType.EMPTY, code_ref=None, prompt="p", created_at=now),
        )
        r1 = create_result(
            db,
            Result(
                id=0,
                scenario_id=scenario.id,
                harness="cursor",
                provider="anthropic",
                model="claude",
                status=ResultStatus.COMPLETED,
                created_at=now,
            ),
        )
        update_result_quality(db, r1.id, 4)
        judge = create_llm_scenario_judge(
            db,
            LLMScenarioJudge(
                id=0,
                scenario_id=scenario.id,
                guidance="g",
                training_sample_ids=[],
                alignment_score=None,
                created_at=now,
            ),
        )
        break

    # No judgement exists -> no pairs -> None and DB remains NULL.
    alignment = evaluate_alignment_score(judge, result_ids=[r1.id])
    assert alignment is None

    for db in get_db():
        refreshed = get_llm_scenario_judge(db, judge.id)
        assert refreshed is not None
        assert refreshed.alignment_score is None
        break

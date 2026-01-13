from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from vibelab.api.app import app
from vibelab.db import (
    create_llm_scenario_judge,
    create_result,
    create_scenario,
    get_db,
    list_judgements,
)
from vibelab.models.judge import LLMScenarioJudge, Judgement
from vibelab.models.result import Result, ResultStatus
from vibelab.models.scenario import CodeType, Scenario


def test_apply_judge_to_all_completed_results() -> None:
    # Create a scenario + two completed results
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

    client = TestClient(app)
    resp = client.post(
        f"/api/judges/{judge.id}/apply?async_=true", json={"result_ids": None, "force": True}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "queued"
    assert body["total"] == 2

    # Run the worker to process the queued judge_result tasks without calling an external LLM.
    from vibelab.engine.worker import Worker

    class DummyRunner:
        def run(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return None

    class DummyJudgeExecutor:
        def execute_judge(self, judge_obj, result_obj):  # type: ignore[no-untyped-def]
            j = Judgement(
                id=0,
                result_id=result_obj.id,
                judge_id=judge_obj.id,
                notes="ok",
                quality=3,
                created_at=datetime.now(timezone.utc),
            )
            for db in get_db():
                from vibelab.db import create_judgement

                create_judgement(db, j)
                break

    w = Worker(
        worker_id="w",
        runner_factory=lambda: DummyRunner(),
        judge_executor_factory=lambda: DummyJudgeExecutor(),
    )
    while w._tick():
        pass

    # We should see 2 judgements
    for db in get_db():
        judgements = list_judgements(db, judge_id=judge.id)
        assert len(judgements) == 2
        judged_ids = {j.result_id for j in judgements}
        assert judged_ids == {r1.id, r2.id}
        break

"""Unit tests for worker dispatch behavior (with dependency injection)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from vibelab.db import create_llm_scenario_judge, create_result, create_scenario, get_db
from vibelab.engine.queue import enqueue_agent_run, enqueue_judge_result
from vibelab.engine.worker import Worker
from vibelab.models.judge import LLMScenarioJudge
from vibelab.models.result import Result, ResultStatus
from vibelab.models.scenario import CodeType, Scenario


@dataclass
class DummyRunner:
    called: bool = False

    def run(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self.called = True
        return None


@dataclass
class DummyJudgeExecutor:
    called: bool = False

    def execute_judge(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self.called = True
        return None


def test_worker_dispatches_agent_run():
    # Create minimal scenario + result
    scenario = Scenario(
        id=0,
        code_type=CodeType.EMPTY,
        code_ref=None,
        prompt="x",
        created_at=datetime.now(timezone.utc),
    )
    for db in get_db():
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

    dummy_runner = DummyRunner()
    w = Worker(
        worker_id="w",
        execution_mode="inline",
        runner_factory=lambda: dummy_runner,
        judge_executor_factory=lambda: DummyJudgeExecutor(),
    )
    assert w._tick() is True
    assert dummy_runner.called is True


def test_worker_dispatches_judge_result():
    scenario = Scenario(
        id=0,
        code_type=CodeType.EMPTY,
        code_ref=None,
        prompt="x",
        created_at=datetime.now(timezone.utc),
    )
    for db in get_db():
        scenario = create_scenario(db, scenario)
        result = Result(
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
        result = create_result(db, result)
        judge = LLMScenarioJudge(
            id=0,
            scenario_id=scenario.id,
            guidance="x",
            training_sample_ids=[],
            alignment_score=None,
            created_at=datetime.now(timezone.utc),
        )
        judge = create_llm_scenario_judge(db, judge)
        enqueue_judge_result(
            db,
            judge_id=judge.id,
            target_result_id=result.id,
            judge_provider="anthropic",
            judge_model="claude-sonnet-4-20250514",
        )
        break

    dummy_exec = DummyJudgeExecutor()
    w = Worker(
        worker_id="w",
        execution_mode="inline",
        runner_factory=lambda: DummyRunner(),
        judge_executor_factory=lambda: dummy_exec,
    )
    assert w._tick() is True
    assert dummy_exec.called is True

"""Execute a single durable task by task_id.

This runs in a separate process (spawned by the worker) so tasks can be cancelled
by terminating the process group.
"""

from __future__ import annotations

import argparse
import logging
import sys

from ..db import (
    get_commit_scenario_draft,
    get_db,
    get_llm_scenario_judge,
    get_result,
    get_scenario,
    update_commit_scenario_draft,
)
from ..models.executor import ExecutorSpec
from .judge import JudgeExecutor, evaluate_alignment_score
from .queue import Task, TaskType, get_task
from .runner import Runner

logger = logging.getLogger(__name__)


def execute_task(task: Task) -> None:
    if task.task_type == TaskType.AGENT_RUN:
        _execute_agent_run(task)
        return
    if task.task_type == TaskType.JUDGE_RESULT:
        _execute_judge_result(task)
        return
    if task.task_type == TaskType.TRAIN_JUDGE:
        _execute_train_judge(task)
        return
    if task.task_type == TaskType.GENERATE_SCENARIO_FROM_COMMIT:
        _execute_generate_scenario_from_commit(task)
        return
    raise ValueError(f"Unknown task_type: {task.task_type}")


def _execute_agent_run(task: Task) -> None:
    if task.result_id is None or task.scenario_id is None or not task.executor_spec:
        raise ValueError("agent_run task missing required fields")
    timeout_seconds = int(task.timeout_seconds or 1800)
    driver_id = task.driver or "local"
    executor_spec = ExecutorSpec.parse(task.executor_spec)

    scenario = None
    for db in get_db():
        scenario = get_scenario(db, task.scenario_id)
        break
    if scenario is None:
        raise ValueError(f"Scenario {task.scenario_id} not found")

    runner = Runner()
    runner.run(
        scenario=scenario,
        executor_spec=executor_spec,
        timeout_seconds=timeout_seconds,
        driver_id=driver_id,
        result_id=task.result_id,
    )


def _execute_judge_result(task: Task) -> None:
    if task.judge_id is None or task.target_result_id is None:
        raise ValueError("judge_result task missing required fields")

    judge = None
    result = None
    for db in get_db():
        judge = get_llm_scenario_judge(db, task.judge_id)
        result = get_result(db, task.target_result_id)
        break
    if judge is None:
        raise ValueError(f"Judge {task.judge_id} not found")
    if result is None:
        raise ValueError(f"Result {task.target_result_id} not found")

    executor = JudgeExecutor()
    executor.execute_judge(judge, result)


def _execute_train_judge(task: Task) -> None:
    if task.judge_id is None:
        raise ValueError("train_judge task missing judge_id")

    judge = None
    for db in get_db():
        judge = get_llm_scenario_judge(db, task.judge_id)
        break
    if judge is None:
        raise ValueError(f"Judge {task.judge_id} not found")

    evaluate_alignment_score(judge, result_ids=task.alignment_result_ids)


def _execute_generate_scenario_from_commit(task: Task) -> None:
    """Generate scenario prompt and judge guidance from a commit draft."""
    if task.draft_id is None:
        raise ValueError("generate_scenario_from_commit task missing draft_id")

    draft = None
    for db in get_db():
        draft = get_commit_scenario_draft(db, task.draft_id)
        break
    if draft is None:
        raise ValueError(f"Draft {task.draft_id} not found")

    try:
        # Build LLM prompt
        prompt = _build_generation_prompt(draft)

        # Call LLM (use same provider/model as judge infrastructure)
        provider = "anthropic"
        model = "claude-sonnet-4-20250514"
        # Only log in verbose mode (DEBUG level)
        log_level = logging.getLogger().getEffectiveLevel()
        if log_level <= logging.DEBUG:
            logger.debug(f"Generating scenario from commit draft {task.draft_id}")
        response = _call_llm_for_generation(prompt, provider, model)

        # Parse response
        generated_prompt, generated_judge_guidance, generated_summary = _parse_generation_response(
            response, draft
        )

        # Update draft
        for db in get_db():
            update_commit_scenario_draft(
                db,
                draft.id,
                generated_prompt=generated_prompt,
                generated_judge_guidance=generated_judge_guidance,
                generated_summary=generated_summary,
                status="ready",
            )
            break
    except Exception as e:
        logger.exception(f"Failed to generate scenario from commit draft {task.draft_id}")
        # Update draft with error
        for db in get_db():
            update_commit_scenario_draft(
                db,
                draft.id,
                status="failed",
                error_message=str(e),
            )
            break
        raise


def _build_generation_prompt(draft) -> str:
    """Build the prompt for LLM to generate scenario content."""
    parts = [
        "You are helping generate a coding task prompt from a real git commit.",
        "",
        "Given:",
        "- Commit message",
        "- PR description (if available)",
        "- Code diff",
        "",
        "Generate:",
        "1. **User Prompt**: A natural prompt a developer might give to an AI coding agent",
        "   to achieve this change. Write as if the user doesn't know the solution yet.",
        "   Focus on the 'what' and 'why', not the 'how'.",
        "",
        "2. **Judge Guidance**: Evaluation criteria for checking if an AI agent's solution",
        "   is correct. Focus on:",
        "   - Required functionality changes",
        "   - Key files/functions that should be modified",
        "   - Expected behavior outcomes",
        "   NOTE: Do NOT include the diff in judge_guidance - it will be added automatically.",
        "",
        "3. **Summary**: A brief 1-2 sentence description of what this commit does.",
        "",
        "## Commit Message",
        draft.commit_message,
        "",
    ]

    if draft.pr_title or draft.pr_body:
        parts.extend(
            [
                "## PR Description",
                f"**Title:** {draft.pr_title or 'N/A'}",
                f"**Body:** {draft.pr_body or 'N/A'}",
                "",
            ]
        )
    else:
        parts.extend(
            [
                "## PR Description",
                "Not available",
                "",
            ]
        )

    # Truncate diff if too large (already done in fetch_commit_diff, but be safe)
    diff = draft.diff
    if len(diff) > 8000:
        diff = diff[:8000] + "\n... (truncated)"

    parts.extend(
        [
            "## Diff",
            "```diff",
            diff,
            "```",
            "",
            "Please provide your response in the following JSON format:",
            '{"prompt": "Add a new CLI command that...",',
            ' "judge_guidance": "The solution should:\\n1. Modify file X...\\n2. Add function Y...",',
            ' "summary": "Adds CLI command for exporting data to CSV"}',
        ]
    )

    return "\n".join(parts)


def _call_llm_for_generation(prompt: str, provider: str, model: str) -> str:
    """Call LLM API for generation."""
    import os

    if provider == "anthropic":
        try:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            if message.content:
                text = message.content[0].text
                return text if isinstance(text, str) else str(text)
            return ""
        except ImportError:
            raise ValueError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.exception(f"Error calling Anthropic API: {e}")
            raise
    elif provider == "openai":
        try:
            import openai

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return ""
        except ImportError:
            raise ValueError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            logger.exception(f"Error calling OpenAI API: {e}")
            raise
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _parse_generation_response(response: str, draft) -> tuple[str, str, str]:
    """Parse LLM response to extract prompt, judge_guidance, and summary.

    Always appends the actual diff as a reference implementation to judge_guidance.
    """
    import json
    import re

    prompt = ""
    judge_guidance = ""
    summary = ""

    # Try to extract JSON from response
    # Look for JSON block (may be fenced)
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL | re.IGNORECASE)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            prompt = parsed.get("prompt", "")
            judge_guidance = parsed.get("judge_guidance", "")
            summary = parsed.get("summary", "")
        except json.JSONDecodeError:
            pass

    # Try to find JSON without fences if not found yet
    if not prompt:
        json_match = re.search(r"(\{.*?\})", response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                prompt = parsed.get("prompt", "")
                judge_guidance = parsed.get("judge_guidance", "")
                summary = parsed.get("summary", "")
            except json.JSONDecodeError:
                pass

    # Fallback: use commit message as basis
    if not prompt:
        prompt = f"Implement the following change: {draft.commit_message}"
    if not summary:
        summary = draft.commit_message.split("\n")[0] if draft.commit_message else ""
    if not judge_guidance:
        judge_guidance = "Evaluate if the solution correctly implements the changes."

    # Truncate diff for reference (use more for judge context)
    diff_for_judge = draft.diff
    if len(diff_for_judge) > 4000:
        diff_for_judge = diff_for_judge[:4000] + "\n... (truncated)"

    # Always append the scoring system and reference implementation
    judge_guidance = f"""{judge_guidance}

## Scoring Guidelines
Rate the solution on a 1-4 scale:
- **4 (Perfect)**: Fully implements the required functionality. May differ in style/approach.
- **3 (Good)**: Implements core functionality with minor gaps or issues.
- **2 (Workable)**: Partially implements the functionality; needs significant improvements.
- **1 (Bad)**: Does not implement the required functionality or introduces bugs.

**Important**: An exact match to the reference implementation is NOT required.
Focus on whether the solution achieves the same functional outcome, not identical code.

## Reference Implementation
The original commit made the following changes:
```diff
{diff_for_judge}
```

Compare the agent's solution for **functional equivalence** to these changes."""

    return prompt, judge_guidance, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", type=int, required=True)
    args = parser.parse_args(argv)

    for db in get_db():
        task = get_task(db, args.task_id)
        break
    else:
        task = None

    if task is None:
        raise SystemExit(f"Task {args.task_id} not found")

    execute_task(task)
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        raise SystemExit(130)

"""LLM Judge execution engine."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from ..db import create_judgement, get_db, get_result, get_scenario
from ..db.connection import get_results_dir
from ..db.queries import get_project_id_for_result
from ..models.judge import Judgement, LLMScenarioJudge
from ..models.result import Result

logger = logging.getLogger(__name__)


class JudgeExecutor:
    """Executes LLM judges to make judgements on results."""

    def execute_judge(
        self,
        judge: LLMScenarioJudge,
        result: Result,
    ) -> Judgement:
        """Execute a judge on a result and return the judgement."""
        # Get scenario for context
        for db in get_db():
            scenario = get_scenario(db, judge.scenario_id)
            if not scenario:
                raise ValueError(f"Scenario {judge.scenario_id} not found")
            break

        # Build prompt with few-shot examples
        prompt = self._build_judge_prompt(judge, result, scenario)

        # Call LLM
        response = self._call_llm(prompt, judge.judge_provider, judge.judge_model)

        # Parse response
        notes, quality = self._parse_judgement_response(response)

        # Create judgement
        judgement = Judgement(
            id=0,  # Will be set by database
            result_id=result.id,
            judge_id=judge.id,
            notes=notes,
            quality=quality,
            created_at=datetime.now(UTC),
        )

        for db in get_db():
            judgement = create_judgement(db, judgement)
            break

        return judgement

    def _build_judge_prompt(self, judge: LLMScenarioJudge, result: Result, scenario: Any) -> str:
        """Build the prompt for the judge with few-shot examples."""
        # Get training samples
        training_examples = []
        for db in get_db():
            for sample_id in judge.training_sample_ids:
                sample_result = get_result(db, sample_id)
                if sample_result:
                    training_examples.append(self._format_result_example(sample_result, scenario))
            break

        # Format current result
        current_result_text = self._format_result_for_judgement(result, scenario)

        # Build prompt
        prompt_parts: list[str] = [judge.guidance, ""]
        if training_examples:
            prompt_parts.extend(["## Few-shot Examples", ""])
            for i, example in enumerate(training_examples, 1):
                prompt_parts.append(f"### Example {i}")
                prompt_parts.append(example)
                prompt_parts.append("")

        prompt_parts.extend(
            [
                "## Result to Judge",
                "",
                current_result_text,
                "",
                "## Your Judgement",
                "",
                "Please provide your judgement in the following JSON format:",
                '{"notes": "Your detailed notes about the quality of this result...", "quality": 4}',
                "",
                "Quality scores:",
                "- 4 = Perfect: The best possible outcome",
                "- 3 = Good: Valid, but could be better",
                "- 2 = Workable: At least 1 thing is incorrect or needs revision, but directionally correct",
                "- 1 = Bad: Just not good, invalid",
            ]
        )

        return "\n".join(prompt_parts)

    def _format_result_example(self, result: Result, scenario: Any) -> str:
        """Format a result as a few-shot example."""
        parts = [
            f"**Result ID:** {result.id}",
            f"**Executor:** {result.harness}:{result.provider}:{result.model}",
            f"**Status:** {result.status.value}",
        ]

        # Add patch if available
        patch = self._get_result_patch(result.id)
        if patch:
            parts.append(f"**Patch:**\n```diff\n{patch[:2000]}\n```")  # Limit patch size

        # Add human notes/quality if available
        if result.notes or result.quality is not None:
            parts.append("**Human Judgement:**")
            if result.quality is not None:
                quality_labels = {4: "Perfect", 3: "Good", 2: "Workable", 1: "Bad"}
                parts.append(
                    f"- Quality: {result.quality} ({quality_labels.get(result.quality, 'Unknown')})"
                )
            if result.notes:
                parts.append(f"- Notes: {result.notes}")

        return "\n".join(parts)

    def _format_result_for_judgement(self, result: Result, scenario: Any) -> str:
        """Format a result for judgement."""
        parts = [
            f"**Result ID:** {result.id}",
            f"**Executor:** {result.harness}:{result.provider}:{result.model}",
            f"**Status:** {result.status.value}",
            f"**Scenario Prompt:** {scenario.prompt}",
        ]

        # Add patch if available
        patch = self._get_result_patch(result.id)
        if patch:
            parts.append(f"**Patch:**\n```diff\n{patch}\n```")

        # Add logs summary
        stdout, stderr = self._get_result_logs(result.id)
        if stdout:
            parts.append(f"**Output (first 1000 chars):**\n{stdout[:1000]}")
        if stderr:
            parts.append(f"**Errors:**\n{stderr[:500]}")

        return "\n".join(parts)

    def _get_result_patch(self, result_id: int) -> str | None:
        """Get patch for a result."""
        project_id = self._get_project_id(result_id)
        patch_file = get_results_dir(project_id) / str(result_id) / "patch.diff"
        if patch_file.exists():
            return patch_file.read_text()
        return None

    def _get_result_logs(self, result_id: int) -> tuple[str, str]:
        """Get logs for a result."""
        project_id = self._get_project_id(result_id)
        stdout_file = get_results_dir(project_id) / str(result_id) / "stdout.log"
        stderr_file = get_results_dir(project_id) / str(result_id) / "stderr.log"
        stdout = stdout_file.read_text() if stdout_file.exists() else ""
        stderr = stderr_file.read_text() if stderr_file.exists() else ""
        return stdout, stderr

    def _get_project_id(self, result_id: int) -> int:
        """Get project_id for a result.

        Raises:
            ValueError: If project_id cannot be determined.
        """
        for db in get_db():
            project_id = get_project_id_for_result(db, result_id)
            if project_id is not None:
                return project_id
        raise ValueError(f"Could not determine project_id for result {result_id}")

    def _call_llm(self, prompt: str, provider: str, model: str) -> str:
        """Call LLM API via LiteLLM for unified provider support.

        LiteLLM handles API key management and provider-specific formatting.
        Set API keys via environment variables:
        - ANTHROPIC_API_KEY for Anthropic models
        - OPENAI_API_KEY for OpenAI models

        Or use LiteLLM's proxy by setting LITELLM_PROXY_URL.
        """
        try:
            import litellm

            # Format the model name for LiteLLM if needed
            # LiteLLM accepts models like "gpt-4o", "claude-3-5-sonnet-20241022", etc.
            # For explicit provider routing, prefix with provider name
            if provider == "anthropic" and not model.startswith("anthropic/"):
                # Anthropic models may need the provider prefix for routing
                litellm_model = model
            elif provider == "openai" and not model.startswith("openai/"):
                litellm_model = model
            else:
                litellm_model = model

            # Use LiteLLM's completion API
            response = litellm.completion(
                model=litellm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=4096,
            )

            # Extract text from response
            if response.choices and response.choices[0].message.content:
                return str(response.choices[0].message.content)
            return ""

        except ImportError:
            raise ValueError("litellm package not installed. Install with: pip install litellm")
        except Exception as e:
            logger.exception(
                f"Error calling LLM API via LiteLLM (provider={provider}, model={model}): {e}"
            )
            raise

    def _parse_judgement_response(self, response: str) -> tuple[str | None, int | None]:
        """Parse LLM response to extract notes and quality."""
        # The judge is prompted to emit JSON, but in practice the model may wrap it in
        # markdown fences, add extra text, or include multiple brace blocks. Be robust:
        # - Prefer fenced JSON
        # - Otherwise, try each { ... } candidate (non-greedy) until one parses
        # - Normalize quality to an int in [1,4] when possible
        import re

        def _normalize_quality(value: Any) -> int | None:
            if value is None:
                return None
            if isinstance(value, bool):
                return None
            if isinstance(value, int):
                return value if 1 <= value <= 4 else None
            if isinstance(value, float):
                if value.is_integer():
                    iv = int(value)
                    return iv if 1 <= iv <= 4 else None
                return None
            if isinstance(value, str):
                s = value.strip().lower()
                if s.isdigit():
                    iv = int(s)
                    return iv if 1 <= iv <= 4 else None
                # Common label fallbacks
                labels = {"perfect": 4, "good": 3, "workable": 2, "bad": 1}
                return labels.get(s)
            return None

        def _extract_from_json_obj(obj: Any) -> tuple[str | None, int | None] | None:
            if not isinstance(obj, dict):
                return None
            notes_val = obj.get("notes")
            # Some models may use alternative keys despite prompting.
            quality_val = obj.get("quality")
            if quality_val is None:
                quality_val = obj.get("score") or obj.get("rating")
            notes = notes_val if isinstance(notes_val, str) else None
            quality = _normalize_quality(quality_val)
            if notes is None and quality is None:
                return None
            return (notes, quality)

        # 1) Try fenced JSON blocks first.
        pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        for m in re.finditer(pattern, response, re.DOTALL | re.IGNORECASE):
            candidate = m.group(1)
            try:
                parsed = json.loads(candidate)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            extracted = _extract_from_json_obj(parsed)
            if extracted is not None:
                return extracted

        # 2) Try non-fenced candidates (non-greedy to avoid spanning multiple blocks).
        for m in re.finditer(r"(\{.*?\})", response, re.DOTALL):
            candidate = m.group(1)
            try:
                parsed = json.loads(candidate)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            extracted = _extract_from_json_obj(parsed)
            if extracted is not None:
                return extracted

        # 3) Fallback: capture a numeric quality if it appears in-text, even if JSON is mangled.
        quality_match = re.search(r'"quality"\s*:\s*([1-4])', response)
        if not quality_match:
            quality_match = re.search(r"\bquality\s*[:=]\s*([1-4])\b", response, re.IGNORECASE)
        quality = int(quality_match.group(1)) if quality_match else None
        return (response.strip() or None, quality)


def evaluate_alignment_score(
    judge: LLMScenarioJudge,
    result_ids: list[int] | None = None,
) -> float | None:
    """Calculate (and persist) alignment score for a judge using existing data.

    Important: this does **not** run the judge again. It computes alignment from:
    - existing human scores: `results.quality`
    - existing judge scores: `judgements.quality` for this `judge.id`
    - existing pairwise preferences for the scenario

    The final alignment is a weighted average of:
    - Absolute alignment: % of exact matches between human and judge scores
    - Pairwise alignment: % of pairwise preferences correctly predicted by judge

    Returns:
      - float if alignment could be computed (>= 1 matched pair or pairwise)
      - None if there was insufficient data to evaluate
    """
    from ..db import get_judgement_for_result, list_pairwise_preferences
    from ..models.pairwise import compute_pairwise_alignment

    # Track absolute alignment
    matched_pairs: list[tuple[int, int]] = []
    judge_scores: dict[int, int | None] = {}

    for db in get_db():
        # Get result_ids if not provided
        if not result_ids:
            from ..db import list_results

            results = list_results(db, scenario_id=judge.scenario_id)
            result_ids = [r.id for r in results if r.status.value == "completed"]

        # Calculate absolute alignment
        for result_id in result_ids:
            result = get_result(db, result_id)
            if not result:
                continue
            if result.status.value != "completed":
                continue

            judgement = get_judgement_for_result(db, result.id, judge.id)
            judge_quality = judgement.quality if judgement else None
            judge_scores[result_id] = judge_quality

            if result.quality is not None and judge_quality is not None:
                matched_pairs.append((result.quality, judge_quality))

        # Calculate pairwise alignment
        pairwise_prefs = list_pairwise_preferences(db, scenario_id=judge.scenario_id)
        pairwise_stats = compute_pairwise_alignment(pairwise_prefs, judge_scores)
        break

    # Calculate absolute alignment
    abs_alignment = None
    abs_samples = len(matched_pairs)
    if abs_samples > 0:
        exact_matches = sum(1 for h, j in matched_pairs if h == j)
        abs_alignment = exact_matches / abs_samples

    # Get pairwise alignment
    pair_alignment = pairwise_stats.pairwise_accuracy
    pair_samples = pairwise_stats.total_pairs

    # Combine alignments weighted by sample size
    total_samples = abs_samples + pair_samples

    if total_samples == 0:
        logger.info("No alignment data available (no absolute or pairwise scores)")
        return None

    if abs_samples > 0 and pair_samples > 0:
        # Weighted average
        alignment = (
            (abs_alignment * abs_samples + pair_alignment * pair_samples) / total_samples
        )
        logger.debug(
            f"Combined alignment: {alignment:.2%} "
            f"(absolute: {abs_alignment:.2%} on {abs_samples}, "
            f"pairwise: {pair_alignment:.2%} on {pair_samples})"
        )
    elif abs_samples > 0:
        alignment = abs_alignment
        logger.debug(f"Absolute alignment only: {alignment:.2%} on {abs_samples}")
    else:
        alignment = pair_alignment
        logger.debug(f"Pairwise alignment only: {alignment:.2%} on {pair_samples}")

    # Update judge alignment score
    for db in get_db():
        from ..db.queries import update_llm_scenario_judge_alignment

        update_llm_scenario_judge_alignment(db, judge.id, alignment)
        break

    return alignment

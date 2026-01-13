"""Pairwise preference model definitions."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class PreferenceType(str, Enum):
    """Type of pairwise preference."""

    A_BETTER = "a_better"  # Result A is clearly better
    B_BETTER = "b_better"  # Result B is clearly better
    TIE = "tie"  # Both are roughly equal quality
    BOTH_GOOD = "both_good"  # Both excellent, can't distinguish
    BOTH_BAD = "both_bad"  # Both poor, can't distinguish


class PairwisePreference(BaseModel):
    """A human comparison between two results."""

    id: int
    scenario_id: int
    result_a_id: int
    result_b_id: int
    preference: PreferenceType
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Confidence in the preference (0-1)"
    )
    notes: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_result_ordering(self) -> "PairwisePreference":
        """Ensure result_a_id < result_b_id for canonical ordering."""
        if self.result_a_id >= self.result_b_id:
            raise ValueError("result_a_id must be less than result_b_id")
        return self

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "result_a_id": self.result_a_id,
            "result_b_id": self.result_b_id,
            "preference": self.preference.value,
            "confidence": self.confidence,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "PairwisePreference":
        """Create from database dictionary."""
        return cls(
            id=data["id"],
            scenario_id=data["scenario_id"],
            result_a_id=data["result_a_id"],
            result_b_id=data["result_b_id"],
            preference=PreferenceType(data["preference"]),
            confidence=data.get("confidence"),
            notes=data.get("notes"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


class PairwisePreferenceCreate(BaseModel):
    """Input for creating a pairwise preference."""

    result_a_id: int
    result_b_id: int
    preference: PreferenceType
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Confidence in the preference (0-1)"
    )
    notes: str | None = None

    @model_validator(mode="after")
    def normalize_ordering(self) -> "PairwisePreferenceCreate":
        """Normalize ordering so result_a_id < result_b_id, swapping preference if needed."""
        if self.result_a_id > self.result_b_id:
            # Swap IDs and flip preference
            self.result_a_id, self.result_b_id = self.result_b_id, self.result_a_id
            if self.preference == PreferenceType.A_BETTER:
                self.preference = PreferenceType.B_BETTER
            elif self.preference == PreferenceType.B_BETTER:
                self.preference = PreferenceType.A_BETTER
            # tie, both_good, both_bad stay the same
        elif self.result_a_id == self.result_b_id:
            raise ValueError("Cannot compare a result with itself")
        return self


class ResultRanking(BaseModel):
    """Ranking information for a result derived from pairwise comparisons."""

    result_id: int
    wins: int = 0
    losses: int = 0
    ties: int = 0
    win_rate: float | None = None  # (wins + 0.5*ties) / total
    comparisons: int = 0
    rank: int | None = None  # 1 = best


class PairwiseStats(BaseModel):
    """Statistics about pairwise comparisons."""

    total_preferences: int
    scenarios_with_preferences: int
    unique_results_compared: int
    average_comparisons_per_result: float | None


class PairwiseAlignmentStats(BaseModel):
    """Pairwise alignment statistics for a judge."""

    total_pairs: int
    correct_predictions: int
    pairwise_accuracy: float | None  # correct / total


def compute_pairwise_alignment(
    preferences: list[PairwisePreference],
    judge_scores: dict[int, int | None],
) -> PairwiseAlignmentStats:
    """Compute how well judge scores align with human pairwise preferences.

    For each human preference where A > B, check if judge_score(A) > judge_score(B).

    Args:
        preferences: List of human pairwise preferences
        judge_scores: Dict mapping result_id -> judge quality score (1-4)

    Returns:
        PairwiseAlignmentStats with accuracy metrics
    """
    total = 0
    correct = 0

    for pref in preferences:
        score_a = judge_scores.get(pref.result_a_id)
        score_b = judge_scores.get(pref.result_b_id)

        # Skip if either score is missing
        if score_a is None or score_b is None:
            continue

        if pref.preference == PreferenceType.A_BETTER:
            total += 1
            if score_a > score_b:
                correct += 1
        elif pref.preference == PreferenceType.B_BETTER:
            total += 1
            if score_b > score_a:
                correct += 1
        elif pref.preference in (
            PreferenceType.TIE, PreferenceType.BOTH_GOOD, PreferenceType.BOTH_BAD
        ):
            total += 1
            if score_a == score_b:
                correct += 1

    return PairwiseAlignmentStats(
        total_pairs=total,
        correct_predictions=correct,
        pairwise_accuracy=correct / total if total > 0 else None,
    )


def compute_rankings(
    preferences: list[PairwisePreference],
    result_ids: list[int],
) -> list[ResultRanking]:
    """Compute rankings from pairwise preferences using simple win rate.

    Args:
        preferences: List of pairwise preferences
        result_ids: List of result IDs to rank

    Returns:
        List of ResultRanking objects sorted by win_rate descending
    """
    # Initialize rankings
    rankings: dict[int, ResultRanking] = {
        rid: ResultRanking(result_id=rid) for rid in result_ids
    }

    # Count wins/losses/ties
    for pref in preferences:
        if pref.result_a_id not in rankings or pref.result_b_id not in rankings:
            continue

        ra = rankings[pref.result_a_id]
        rb = rankings[pref.result_b_id]

        ra.comparisons += 1
        rb.comparisons += 1

        if pref.preference == PreferenceType.A_BETTER:
            ra.wins += 1
            rb.losses += 1
        elif pref.preference == PreferenceType.B_BETTER:
            rb.wins += 1
            ra.losses += 1
        else:  # tie, both_good, both_bad
            ra.ties += 1
            rb.ties += 1

    # Compute win rates
    for r in rankings.values():
        if r.comparisons > 0:
            r.win_rate = (r.wins + 0.5 * r.ties) / r.comparisons

    # Sort by win rate and assign ranks
    sorted_rankings = sorted(
        rankings.values(),
        key=lambda r: (r.win_rate if r.win_rate is not None else -1, r.wins),
        reverse=True,
    )

    current_rank = 1
    for i, r in enumerate(sorted_rankings):
        if r.comparisons > 0:
            r.rank = current_rank
            # Handle ties in ranking
            if i + 1 < len(sorted_rankings):
                next_r = sorted_rankings[i + 1]
                if next_r.win_rate != r.win_rate:
                    current_rank = i + 2

    return sorted_rankings


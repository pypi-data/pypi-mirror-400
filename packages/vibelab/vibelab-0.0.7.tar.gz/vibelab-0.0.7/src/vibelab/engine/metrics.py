"""Statistical metrics for matrix aggregation.

This module provides statistical functions for computing mean, standard deviation,
weighted averages, and relative scores used in the comparison matrix.

Mathematical Notation Reference:
- μ (mu): population/sample mean
- σ (sigma): standard deviation
- n: sample size
- w: weight
"""

import math
from dataclasses import dataclass


@dataclass
class AggregatedMetric:
    """Result of aggregating a set of values.

    Attributes:
        mean: The arithmetic mean (μ = Σx_i / n)
        std: Sample standard deviation (σ = √(Σ(x_i - μ)² / (n-1)))
        count: Number of values (n)
    """

    mean: float | None
    std: float | None
    count: int


def compute_mean(values: list[float]) -> float | None:
    """Compute arithmetic mean.

    Formula: μ = Σx_i / n

    Args:
        values: List of numeric values

    Returns:
        Mean value, or None if empty
    """
    if not values:
        return None
    return sum(values) / len(values)


def compute_std(values: list[float], mean: float | None = None) -> float | None:
    """Compute sample standard deviation.

    Formula: σ = √(Σ(x_i - μ)² / (n-1))

    Uses Bessel's correction (n-1 denominator) for unbiased estimation
    of population standard deviation from a sample.

    Args:
        values: List of numeric values
        mean: Pre-computed mean (computed if not provided)

    Returns:
        Sample standard deviation, or None if fewer than 2 values
    """
    n = len(values)
    if n < 2:
        return None

    if mean is None:
        mean = compute_mean(values)
    if mean is None:
        return None

    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return math.sqrt(variance)


def aggregate_values(values: list[float]) -> AggregatedMetric:
    """Compute mean and standard deviation for a list of values.

    Args:
        values: List of numeric values

    Returns:
        AggregatedMetric with mean, std, and count
    """
    if not values:
        return AggregatedMetric(mean=None, std=None, count=0)

    mean = compute_mean(values)
    std = compute_std(values, mean)
    return AggregatedMetric(mean=mean, std=std, count=len(values))


def weighted_mean(
    values: list[float],
    weights: list[float],
) -> float | None:
    """Compute weighted arithmetic mean.

    Formula: μ_w = Σ(w_i × x_i) / Σw_i

    Args:
        values: List of values
        weights: Corresponding weights (must be same length)

    Returns:
        Weighted mean, or None if empty or all weights are zero
    """
    if not values or not weights or len(values) != len(weights):
        return None

    total_weight = sum(weights)
    if total_weight == 0:
        return None

    return sum(v * w for v, w in zip(values, weights)) / total_weight


def weighted_std(
    values: list[float],
    weights: list[float],
    mean: float | None = None,
) -> float | None:
    """Compute weighted sample standard deviation.

    Formula: σ_w = √(Σw_i × (x_i - μ_w)² / Σw_i)

    Note: This uses frequency weights (not reliability weights).

    Args:
        values: List of values
        weights: Corresponding weights
        mean: Pre-computed weighted mean

    Returns:
        Weighted standard deviation, or None if insufficient data
    """
    if not values or not weights or len(values) != len(weights):
        return None
    if len(values) < 2:
        return None

    total_weight = sum(weights)
    if total_weight == 0:
        return None

    if mean is None:
        mean = weighted_mean(values, weights)
    if mean is None:
        return None

    variance = sum(w * (v - mean) ** 2 for v, w in zip(values, weights)) / total_weight
    return math.sqrt(variance)


def aggregate_weighted(
    values: list[float],
    weights: list[float],
) -> AggregatedMetric:
    """Compute weighted mean and standard deviation.

    Args:
        values: List of values
        weights: Corresponding weights

    Returns:
        AggregatedMetric with weighted mean, std, and count
    """
    if not values or not weights:
        return AggregatedMetric(mean=None, std=None, count=0)

    mean = weighted_mean(values, weights)
    std = weighted_std(values, weights, mean)
    return AggregatedMetric(mean=mean, std=std, count=len(values))


def compute_judge_weight(
    alignment_score: float | None,
    sample_count: int,
) -> float:
    """Compute weight for a judge based on alignment and sample size.

    Formula: w_j = alignment_j × √(sample_count_j)

    This balances:
    - Alignment: How well the judge agrees with human scores (0-1)
    - Sample Count: More training samples = more confidence (sqrt dampens effect)

    Args:
        alignment_score: Judge's alignment with human scores (0-1), or None
        sample_count: Number of training samples for this judge

    Returns:
        Computed weight (defaults to 1.0 if no alignment data)
    """
    if alignment_score is None:
        # No alignment data - use equal weight
        return 1.0

    if sample_count <= 0:
        return alignment_score

    return alignment_score * math.sqrt(sample_count)


def compute_relative_score(
    value: float,
    reference_mean: float,
    reference_std: float | None,
) -> float | None:
    """Compute Z-score relative to a reference distribution.

    Formula: z = (x - μ) / σ

    Interpretation:
    - z = 0: At the mean
    - z = +1: One standard deviation above mean
    - z = -1: One standard deviation below mean

    Args:
        value: The value to normalize
        reference_mean: Mean of the reference distribution
        reference_std: Standard deviation of the reference distribution

    Returns:
        Z-score, or None if std is zero/None
    """
    if reference_std is None or reference_std == 0:
        return None

    return (value - reference_mean) / reference_std


def compute_ranks(
    values: dict[str, float | None],
    higher_is_better: bool = True,
) -> dict[str, int | None]:
    """Compute ranks for a set of named values.

    Args:
        values: Dictionary mapping keys to values (None values are unranked)
        higher_is_better: If True, highest value gets rank 1

    Returns:
        Dictionary mapping keys to ranks (1 = best)
    """
    # Filter out None values
    valid = [(k, v) for k, v in values.items() if v is not None]

    if not valid:
        return {k: None for k in values}

    # Sort by value
    sorted_items = sorted(valid, key=lambda x: x[1], reverse=higher_is_better)

    # Assign ranks
    ranks: dict[str, int | None] = {k: None for k in values}
    for rank, (key, _) in enumerate(sorted_items, start=1):
        ranks[key] = rank

    return ranks


@dataclass
class CellMetrics:
    """Computed metrics for a single matrix cell.

    Represents aggregated data for a (scenario, executor) combination.
    """

    # Run counts
    total_runs: int
    completed: int
    failed: int
    timeout: int
    running: int
    queued: int

    # Quality metrics
    quality_mean: float | None
    quality_std: float | None
    quality_count: int

    # Latency metrics (milliseconds)
    latency_mean: float | None
    latency_std: float | None
    latency_count: int

    # Cost metrics
    cost_mean: float | None
    cost_count: int

    @property
    def state(self) -> str:
        """Cell state classification.

        Returns:
            'empty': No runs
            'no_success': Has runs but none completed successfully
            'success': At least one completed run
        """
        if self.total_runs == 0:
            return "empty"
        if self.completed == 0:
            return "no_success"
        return "success"


@dataclass
class AggregationResult:
    """Result of aggregating metrics across rows or columns.

    Includes both the aggregated values and relative scoring information.
    """

    quality: AggregatedMetric
    latency: AggregatedMetric
    rank: int | None = None
    relative: float | None = None


def aggregate_cells(
    cells: list[CellMetrics],
) -> AggregationResult:
    """Aggregate metrics across multiple cells using weighted mean.

    Each cell contributes proportionally to its sample count.

    Formula:
        aggregate_mean = Σ(cell_mean × cell_count) / Σ(cell_count)
        aggregate_std = √(Σ(cell_count × (cell_mean - aggregate_mean)²) / Σ(cell_count))

    Args:
        cells: List of CellMetrics to aggregate

    Returns:
        AggregationResult with quality and latency aggregations
    """
    # Quality aggregation
    q_values = []
    q_weights = []
    for c in cells:
        if c.quality_mean is not None and c.quality_count > 0:
            q_values.append(c.quality_mean)
            q_weights.append(float(c.quality_count))

    quality = aggregate_weighted(q_values, q_weights)

    # Latency aggregation
    l_values = []
    l_weights = []
    for c in cells:
        if c.latency_mean is not None and c.latency_count > 0:
            l_values.append(c.latency_mean)
            l_weights.append(float(c.latency_count))

    latency = aggregate_weighted(l_values, l_weights)

    return AggregationResult(quality=quality, latency=latency)

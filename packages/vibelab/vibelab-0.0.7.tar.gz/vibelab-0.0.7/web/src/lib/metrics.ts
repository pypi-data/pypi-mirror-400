/**
 * Statistical metrics for matrix aggregation.
 *
 * This module provides statistical functions for computing mean, standard deviation,
 * weighted averages, and relative scores used in the comparison matrix.
 *
 * Mathematical Notation Reference:
 * - μ (mu): population/sample mean
 * - σ (sigma): standard deviation
 * - n: sample size
 * - w: weight
 */

/**
 * Result of aggregating a set of values.
 */
export interface AggregatedMetric {
  /** The arithmetic mean (μ = Σx_i / n) */
  mean: number | null
  /** Sample standard deviation (σ = √(Σ(x_i - μ)² / (n-1))) */
  std: number | null
  /** Number of values (n) */
  count: number
  /** Optional rank (1 = best) */
  rank?: number | null
  /** Optional Z-score relative to reference distribution */
  relative?: number | null
}

/**
 * Compute arithmetic mean.
 *
 * Formula: μ = Σx_i / n
 *
 * @param values - List of numeric values
 * @returns Mean value, or null if empty
 */
export function computeMean(values: number[]): number | null {
  if (values.length === 0) return null
  return values.reduce((sum, v) => sum + v, 0) / values.length
}

/**
 * Compute sample standard deviation.
 *
 * Formula: σ = √(Σ(x_i - μ)² / (n-1))
 *
 * Uses Bessel's correction (n-1 denominator) for unbiased estimation
 * of population standard deviation from a sample.
 *
 * @param values - List of numeric values
 * @param mean - Pre-computed mean (computed if not provided)
 * @returns Sample standard deviation, or null if fewer than 2 values
 */
export function computeStd(values: number[], mean?: number | null): number | null {
  const n = values.length
  if (n < 2) return null

  const mu = mean ?? computeMean(values)
  if (mu === null) return null

  const variance = values.reduce((sum, v) => sum + Math.pow(v - mu, 2), 0) / (n - 1)
  return Math.sqrt(variance)
}

/**
 * Compute mean and standard deviation for a list of values.
 *
 * @param values - List of numeric values
 * @returns AggregatedMetric with mean, std, and count
 */
export function aggregateValues(values: number[]): AggregatedMetric {
  if (values.length === 0) {
    return { mean: null, std: null, count: 0 }
  }

  const mean = computeMean(values)
  const std = computeStd(values, mean)
  return { mean, std, count: values.length }
}

/**
 * Compute weighted arithmetic mean.
 *
 * Formula: μ_w = Σ(w_i × x_i) / Σw_i
 *
 * @param values - List of values
 * @param weights - Corresponding weights (must be same length)
 * @returns Weighted mean, or null if empty or all weights are zero
 */
export function weightedMean(values: number[], weights: number[]): number | null {
  if (values.length === 0 || weights.length === 0 || values.length !== weights.length) {
    return null
  }

  const totalWeight = weights.reduce((sum, w) => sum + w, 0)
  if (totalWeight === 0) return null

  const weightedSum = values.reduce((sum, v, i) => sum + v * weights[i], 0)
  return weightedSum / totalWeight
}

/**
 * Compute weighted sample standard deviation.
 *
 * Formula: σ_w = √(Σw_i × (x_i - μ_w)² / Σw_i)
 *
 * Note: This uses frequency weights (not reliability weights).
 *
 * @param values - List of values
 * @param weights - Corresponding weights
 * @param mean - Pre-computed weighted mean
 * @returns Weighted standard deviation, or null if insufficient data
 */
export function weightedStd(
  values: number[],
  weights: number[],
  mean?: number | null
): number | null {
  if (values.length < 2 || weights.length !== values.length) {
    return null
  }

  const totalWeight = weights.reduce((sum, w) => sum + w, 0)
  if (totalWeight === 0) return null

  const mu = mean ?? weightedMean(values, weights)
  if (mu === null) return null

  const variance = values.reduce((sum, v, i) => sum + weights[i] * Math.pow(v - mu, 2), 0) / totalWeight
  return Math.sqrt(variance)
}

/**
 * Compute weighted mean and standard deviation.
 *
 * @param values - List of values
 * @param weights - Corresponding weights
 * @returns AggregatedMetric with weighted mean, std, and count
 */
export function aggregateWeighted(values: number[], weights: number[]): AggregatedMetric {
  if (values.length === 0 || weights.length === 0) {
    return { mean: null, std: null, count: 0 }
  }

  const mean = weightedMean(values, weights)
  const std = weightedStd(values, weights, mean)
  return { mean, std, count: values.length }
}

/**
 * Compute weight for a judge based on alignment and sample size.
 *
 * Formula: w_j = alignment_j × √(sample_count_j)
 *
 * This balances:
 * - Alignment: How well the judge agrees with human scores (0-1)
 * - Sample Count: More training samples = more confidence (sqrt dampens effect)
 *
 * @param alignmentScore - Judge's alignment with human scores (0-1), or null
 * @param sampleCount - Number of training samples for this judge
 * @returns Computed weight (defaults to 1.0 if no alignment data)
 */
export function computeJudgeWeight(
  alignmentScore: number | null | undefined,
  sampleCount: number
): number {
  if (alignmentScore === null || alignmentScore === undefined) {
    // No alignment data - use equal weight
    return 1.0
  }

  if (sampleCount <= 0) {
    return alignmentScore
  }

  return alignmentScore * Math.sqrt(sampleCount)
}

/**
 * Compute Z-score relative to a reference distribution.
 *
 * Formula: z = (x - μ) / σ
 *
 * Interpretation:
 * - z = 0: At the mean
 * - z = +1: One standard deviation above mean
 * - z = -1: One standard deviation below mean
 *
 * @param value - The value to normalize
 * @param referenceMean - Mean of the reference distribution
 * @param referenceStd - Standard deviation of the reference distribution
 * @returns Z-score, or null if std is zero/null
 */
export function computeRelativeScore(
  value: number,
  referenceMean: number,
  referenceStd: number | null | undefined
): number | null {
  if (referenceStd === null || referenceStd === undefined || referenceStd === 0) {
    return null
  }

  return (value - referenceMean) / referenceStd
}

/**
 * Compute ranks for a set of named values.
 *
 * @param values - Record mapping keys to values (null values are unranked)
 * @param higherIsBetter - If true, highest value gets rank 1
 * @returns Record mapping keys to ranks (1 = best)
 */
export function computeRanks(
  values: Record<string, number | null | undefined>,
  higherIsBetter: boolean = true
): Record<string, number | null> {
  const entries = Object.entries(values)
  const valid = entries.filter(([, v]) => v !== null && v !== undefined) as [string, number][]

  if (valid.length === 0) {
    return Object.fromEntries(entries.map(([k]) => [k, null]))
  }

  // Sort by value
  const sorted = [...valid].sort((a, b) => (higherIsBetter ? b[1] - a[1] : a[1] - b[1]))

  // Assign ranks
  const ranks: Record<string, number | null> = {}
  for (const [key] of entries) {
    ranks[key] = null
  }
  sorted.forEach(([key], index) => {
    ranks[key] = index + 1
  })

  return ranks
}

/**
 * Cell state classification.
 */
export type CellState = 'empty' | 'no_success' | 'success'

/**
 * Determine cell state based on run counts.
 *
 * @param totalRuns - Total number of runs
 * @param completed - Number of completed runs
 * @returns Cell state classification
 */
export function getCellState(totalRuns: number, completed: number): CellState {
  if (totalRuns === 0) return 'empty'
  if (completed === 0) return 'no_success'
  return 'success'
}

/**
 * Format a value with ± standard deviation.
 *
 * @param value - The mean value
 * @param std - The standard deviation (optional)
 * @param decimals - Number of decimal places
 * @returns Formatted string like "3.25 ± 0.50" or "3.25" if no std
 */
export function formatWithStd(
  value: number | null | undefined,
  std: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined) return '—'

  const formattedValue = value.toFixed(decimals)
  if (std === null || std === undefined) return formattedValue

  return `${formattedValue} ± ${std.toFixed(decimals)}`
}

/**
 * Format duration in milliseconds with optional standard deviation.
 *
 * @param ms - Duration in milliseconds
 * @param stdMs - Standard deviation in milliseconds (optional)
 * @returns Formatted string like "2.3s ± 0.4s" or "2.3s"
 */
export function formatDurationWithStd(
  ms: number | null | undefined,
  stdMs?: number | null
): string {
  if (ms === null || ms === undefined) return '—'

  const formatMs = (val: number): string => {
    if (val < 1000) return `${Math.round(val)}ms`
    if (val < 60000) return `${(val / 1000).toFixed(1)}s`
    const mins = Math.floor(val / 60000)
    const secs = Math.round((val % 60000) / 1000)
    return `${mins}m${secs}s`
  }

  const formattedValue = formatMs(ms)
  if (stdMs === null || stdMs === undefined) return formattedValue

  return `${formattedValue} ± ${formatMs(stdMs)}`
}

/**
 * Format a relative score (Z-score) for display.
 *
 * @param relative - The Z-score value
 * @returns Formatted string like "+0.8σ" or "-0.3σ"
 */
export function formatRelativeScore(relative: number | null | undefined): string {
  if (relative === null || relative === undefined) return '—'
  const sign = relative >= 0 ? '+' : ''
  return `${sign}${relative.toFixed(1)}σ`
}

/**
 * Get color class for relative performance.
 *
 * @param relative - Z-score relative to average
 * @returns CSS class string for coloring
 */
export function getRelativeColorClass(relative: number | null | undefined): string {
  if (relative === null || relative === undefined) return ''

  if (relative >= 1.0) return 'text-emerald-400'
  if (relative >= 0.5) return 'text-emerald-300'
  if (relative >= 0) return 'text-text-secondary'
  if (relative >= -0.5) return 'text-amber-300'
  if (relative >= -1.0) return 'text-amber-400'
  return 'text-rose-400'
}

/**
 * Get background color class for relative performance (for cells).
 *
 * @param relative - Z-score relative to average
 * @returns CSS class string for background coloring
 */
export function getRelativeBgClass(relative: number | null | undefined): string {
  if (relative === null || relative === undefined) return ''

  if (relative >= 1.0) return 'bg-emerald-500/10'
  if (relative >= 0.5) return 'bg-emerald-500/5'
  if (relative >= 0) return ''
  if (relative >= -0.5) return 'bg-amber-500/5'
  if (relative >= -1.0) return 'bg-amber-500/10'
  return 'bg-rose-500/10'
}


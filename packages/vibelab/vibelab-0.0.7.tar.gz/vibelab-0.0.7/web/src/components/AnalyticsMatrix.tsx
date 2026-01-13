import { Link } from 'react-router-dom'
import { ArrowLeftRight } from 'lucide-react'
import {
  type AggregatedMetric,
  type CellState,
  getCellState,
  formatDurationWithStd,
  formatRelativeScore,
  getRelativeColorClass,
  getRelativeBgClass,
  computeRanks,
  computeRelativeScore,
  aggregateValues,
} from '../lib/metrics'

// Shared types for analytics matrix
export interface CellData {
  status: string
  total: number
  completed: number
  failed: number
  timeout: number
  running: number
  queued: number
  result_ids?: number[]
  // Quality metrics with std dev
  avg_quality?: number | null
  quality_std?: number | null
  quality_count?: number
  // Latency metrics with std dev
  avg_duration_ms?: number | null
  duration_std?: number | null
  duration_count?: number
  // Cost metrics
  avg_cost_usd?: number | null
  cost_count?: number
}

export interface MatrixRow {
  scenario_id: number
  scenario_prompt: string
  cells: Record<string, CellData>
}

/** Aggregated metric with mean, std, count, rank, and relative score */
export interface AggMetric {
  mean: number | null
  std: number | null
  count: number
  rank?: number | null
  relative?: number | null
}

export interface Aggregations {
  global: {
    quality: AggMetric
    latency: AggMetric
  }
  byScenario: Record<number, {
    quality: AggMetric
    latency: AggMetric
  }>
  byExecutor: Record<string, {
    quality: AggMetric
    latency: AggMetric
    /** Quality rank (1 = best quality) */
    qualityRank?: number | null
    /** Latency rank (1 = fastest) */
    latencyRank?: number | null
    /** Quality relative score (positive = above average) */
    qualityRelative?: number | null
    /** Latency relative score (negative = faster than average) */
    latencyRelative?: number | null
    /** Legacy: same as qualityRank for backwards compat */
    rank?: number | null
    /** Legacy: same as qualityRelative for backwards compat */
    relative?: number | null
  }>
}

// Re-export types from metrics lib
export type { AggregatedMetric, CellState }

// Quality score badge with optional std dev
export function MatrixQualityBadge({ 
  value, 
  std,
  count,
  size = 'md',
  showStd = false,
}: { 
  value: number | null | undefined
  std?: number | null
  count?: number
  size?: 'sm' | 'md' | 'lg'
  showStd?: boolean
}) {
  if (value === null || value === undefined) {
    return <span className="text-text-disabled text-xs">—</span>
  }
  
  let color = 'text-text-secondary bg-surface-2'
  let label = ''
  
  if (value >= 3.5) { color = 'text-emerald-400 bg-emerald-500/15'; label = 'Perfect' }
  else if (value >= 2.5) { color = 'text-sky-400 bg-sky-500/15'; label = 'Good' }
  else if (value >= 1.5) { color = 'text-amber-400 bg-amber-500/15'; label = 'Workable' }
  else { color = 'text-rose-400 bg-rose-500/15'; label = 'Bad' }
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 min-w-[52px]',
    md: 'text-sm px-2.5 py-1 min-w-[60px]',
    lg: 'text-xl px-4 py-2 min-w-[80px]',
  }
  
  // Format value with optional std
  const formattedValue = showStd && std != null
    ? `${value.toFixed(2)} ± ${std.toFixed(2)}`
    : value.toFixed(2)
  
  return (
    <div className={`inline-flex flex-col items-center rounded-md ${color} ${sizeClasses[size]}`}>
      <span className="font-semibold">{formattedValue}</span>
      {size !== 'sm' && (
        <span className="text-[9px] opacity-70">
          {label}{count !== undefined && count > 0 ? ` (${count})` : ''}
        </span>
      )}
    </div>
  )
}

// Format duration nicely
export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '—'
  if (ms < 1000) return `${Math.round(ms)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.round((ms % 60000) / 1000)
  return `${mins}m${secs}s`
}

// Compact status line with latency showing std dev
export function StatusLine({ cell, showStd = false }: { cell: CellData; showStd?: boolean }) {
  if (cell.total === 0) return null
  
  return (
    <div className="flex flex-col items-center gap-0.5 mt-1">
      <div className="flex items-center justify-center gap-1 text-[10px] font-medium">
        {cell.running > 0 && (
          <span className="text-status-info flex items-center gap-0.5">
            <span className="w-1 h-1 rounded-full bg-current animate-pulse" />
            {cell.running}
          </span>
        )}
        {cell.completed > 0 && <span className="text-status-success">✓{cell.completed}</span>}
        {cell.failed > 0 && <span className="text-status-error">✗{cell.failed}</span>}
        {cell.timeout > 0 && <span className="text-status-warning">⏱{cell.timeout}</span>}
      </div>
      {cell.avg_duration_ms != null && (
        <div className="text-[9px] text-text-tertiary">
          {showStd 
            ? formatDurationWithStd(cell.avg_duration_ms, cell.duration_std)
            : formatDuration(cell.avg_duration_ms)
          }
        </div>
      )}
    </div>
  )
}

// Check if a cell needs a run (no successful completed results)
export function cellNeedsRun(cell: CellData): boolean {
  return cell.completed === 0
}

/**
 * Cell content component with three states:
 * - empty: Shows "▶ Run" button
 * - no_success: Shows failure counts + "▶ Retry" button
 * - success: Shows quality badge with std, latency, and counts
 */
export function MatrixCellContent({
  cell,
  onCellClick,
  onRunClick,
  isStartingRun,
  showStd = false,
  relative,
}: {
  cell: CellData
  onCellClick?: (e: React.MouseEvent) => void
  onRunClick?: (e: React.MouseEvent) => void
  isStartingRun?: boolean
  showStd?: boolean
  /** Relative score for background coloring */
  relative?: number | null
}) {
  const state = getCellState(cell.total, cell.completed)
  const bgClass = getRelativeBgClass(relative)
  
  // State: empty - no runs at all
  if (state === 'empty') {
    return (
      <button
        onClick={onRunClick}
        disabled={isStartingRun}
        className="text-xs text-text-tertiary hover:text-accent transition-colors disabled:opacity-50"
        title="Start a run"
      >
        {isStartingRun ? '...' : '▶ Run'}
      </button>
    )
  }

  // State: no_success - has runs but none completed
  if (state === 'no_success') {
    return (
      <div className="flex flex-col items-center">
        <StatusLine cell={cell} showStd={showStd} />
        {cell.running === 0 && cell.queued === 0 && (
          <button
            onClick={onRunClick}
            disabled={isStartingRun}
            className="mt-1 text-[10px] text-text-tertiary hover:text-accent transition-colors disabled:opacity-50"
            title="Retry run"
          >
            {isStartingRun ? '...' : '▶ Retry'}
          </button>
        )}
      </div>
    )
  }

  // State: success - at least one completed run
  const hasResults = cell.result_ids && cell.result_ids.length > 0

  return (
    <div className={`flex flex-col items-center rounded p-1 ${bgClass}`}>
      <div
        className={`flex flex-col items-center ${hasResults ? 'cursor-pointer hover:opacity-70 transition-opacity' : ''}`}
        onClick={hasResults ? onCellClick : undefined}
      >
        <MatrixQualityBadge 
          value={cell.avg_quality} 
          std={cell.quality_std}
          count={cell.quality_count} 
          size="sm" 
          showStd={showStd}
        />
        <StatusLine cell={cell} showStd={showStd} />
      </div>
      {/* Show retry button if there are also failures alongside successes */}
      {cell.failed > 0 && cell.running === 0 && cell.queued === 0 && (
        <button
          onClick={onRunClick}
          disabled={isStartingRun}
          className="mt-1 text-[10px] text-text-tertiary hover:text-accent transition-colors disabled:opacity-50"
          title="Retry failed"
        >
          {isStartingRun ? '...' : '▶ Retry'}
        </button>
      )}
    </div>
  )
}

// Run missing button component
export function RunMissingButton({
  count,
  onClick,
  isRunning,
  size = 'sm',
  label,
}: {
  count: number
  onClick: () => void
  isRunning: boolean
  size?: 'sm' | 'md'
  label?: string
}) {
  if (count === 0) return null

  const sizeClasses = size === 'sm' 
    ? 'text-[10px] px-1.5 py-0.5' 
    : 'text-xs px-2 py-1'

  return (
    <button
      onClick={onClick}
      disabled={isRunning}
      className={`${sizeClasses} rounded bg-accent/10 text-accent hover:bg-accent/20 transition-colors disabled:opacity-50 whitespace-nowrap`}
      title={`Run ${count} missing`}
    >
      {isRunning ? '...' : label || `▶ ${count}`}
    </button>
  )
}

// Scenario row title with compare button
export function ScenarioRowTitle({
  scenarioId,
  prompt,
  hasResults,
  onCompare,
}: {
  scenarioId: number
  prompt: string
  hasResults: boolean
  onCompare?: () => void
}) {
  return (
    <div className="flex items-start gap-1.5">
      <div className="min-w-0 flex-1">
        <Link to={`/scenario/${scenarioId}`} className="font-medium text-text-primary hover:text-accent">
          #{scenarioId}
        </Link>
        <div className="text-xs text-text-tertiary line-clamp-1 mt-0.5" title={prompt}>
          {prompt}
        </div>
      </div>
      {hasResults && onCompare && (
        <button 
          onClick={onCompare} 
          className="p-1 rounded text-text-tertiary hover:text-accent hover:bg-surface-2 transition-colors shrink-0"
          title="Compare all results"
        >
          <ArrowLeftRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  )
}

/**
 * Compute aggregations from matrix data including mean, std dev, ranks, and relative scores.
 * 
 * This function aggregates quality and latency metrics across:
 * - Global: All cells combined
 * - By Scenario: Per row aggregation
 * - By Executor: Per column aggregation with rank and relative score
 */
export function computeAggregations(matrix: MatrixRow[], executors: string[]): Aggregations {
  // Collect all raw values for proper std dev calculation
  const allQualityValues: number[] = []
  const allLatencyValues: number[] = []
  
  // Per-executor and per-scenario raw values
  const execQuality: Record<string, number[]> = {}
  const execLatency: Record<string, number[]> = {}
  const scenQuality: Record<number, number[]> = {}
  const scenLatency: Record<number, number[]> = {}
  
  executors.forEach((e) => {
    execQuality[e] = []
    execLatency[e] = []
  })

  matrix.forEach((row) => {
    scenQuality[row.scenario_id] = []
    scenLatency[row.scenario_id] = []
    
    executors.forEach((exec) => {
      const c = row.cells[exec]
      
      // Quality: use cell avg as a single data point (weighted by count happens implicitly)
      if (c?.avg_quality != null && c.quality_count && c.quality_count > 0) {
        // Add the avg_quality value once per quality_count to weight properly
        for (let i = 0; i < c.quality_count; i++) {
          allQualityValues.push(c.avg_quality)
          execQuality[exec].push(c.avg_quality)
          scenQuality[row.scenario_id].push(c.avg_quality)
        }
      }
      
      // Latency: similar treatment
      if (c?.avg_duration_ms != null && c.duration_count && c.duration_count > 0) {
        for (let i = 0; i < c.duration_count; i++) {
          allLatencyValues.push(c.avg_duration_ms)
          execLatency[exec].push(c.avg_duration_ms)
          scenLatency[row.scenario_id].push(c.avg_duration_ms)
        }
      }
    })
  })

  // Global aggregations
  const globalQuality = aggregateValues(allQualityValues)
  const globalLatency = aggregateValues(allLatencyValues)

  // By-executor aggregations
  const byExecutor: Aggregations['byExecutor'] = {}
  const execQualityMeans: Record<string, number | null> = {}
  const execLatencyMeans: Record<string, number | null> = {}
  
  executors.forEach((exec) => {
    const qAgg = aggregateValues(execQuality[exec])
    const lAgg = aggregateValues(execLatency[exec])
    execQualityMeans[exec] = qAgg.mean
    execLatencyMeans[exec] = lAgg.mean
    byExecutor[exec] = {
      quality: { mean: qAgg.mean, std: qAgg.std, count: qAgg.count },
      latency: { mean: lAgg.mean, std: lAgg.std, count: lAgg.count },
    }
  })

  // Compute ranks and relative scores for executors
  const qualityRanks = computeRanks(execQualityMeans, true) // higher is better
  const latencyRanks = computeRanks(execLatencyMeans, false) // lower is better (faster)
  
  executors.forEach((exec) => {
    // Quality ranking
    byExecutor[exec].qualityRank = qualityRanks[exec]
    byExecutor[exec].rank = qualityRanks[exec] // Legacy compat
    
    const qMean = execQualityMeans[exec]
    if (qMean !== null && globalQuality.mean !== null) {
      const qRel = computeRelativeScore(qMean, globalQuality.mean, globalQuality.std)
      byExecutor[exec].qualityRelative = qRel
      byExecutor[exec].relative = qRel // Legacy compat
    } else {
      byExecutor[exec].qualityRelative = null
      byExecutor[exec].relative = null
    }
    
    // Latency ranking
    byExecutor[exec].latencyRank = latencyRanks[exec]
    
    const lMean = execLatencyMeans[exec]
    if (lMean !== null && globalLatency.mean !== null) {
      // Note: for latency, negative relative = faster = better
      byExecutor[exec].latencyRelative = computeRelativeScore(lMean, globalLatency.mean, globalLatency.std)
    } else {
      byExecutor[exec].latencyRelative = null
    }
  })

  // By-scenario aggregations
  const byScenario: Aggregations['byScenario'] = {}
  matrix.forEach((row) => {
    const qAgg = aggregateValues(scenQuality[row.scenario_id] || [])
    const lAgg = aggregateValues(scenLatency[row.scenario_id] || [])
    byScenario[row.scenario_id] = {
      quality: { mean: qAgg.mean, std: qAgg.std, count: qAgg.count },
      latency: { mean: lAgg.mean, std: lAgg.std, count: lAgg.count },
    }
  })

  return { 
    global: { 
      quality: { mean: globalQuality.mean, std: globalQuality.std, count: globalQuality.count },
      latency: { mean: globalLatency.mean, std: globalLatency.std, count: globalLatency.count },
    }, 
    byScenario, 
    byExecutor 
  }
}

// Compute stats from matrix data
export function computeStats(matrix: MatrixRow[]): { completed: number; failed: number; running: number } {
  let completed = 0, failed = 0, running = 0
  matrix.forEach((row) => {
    Object.values(row.cells).forEach((c) => {
      completed += c.completed
      failed += c.failed + c.timeout
      running += c.running + c.queued
    })
  })
  return { completed, failed, running }
}

/**
 * Rank badge for showing executor rankings with medal icons.
 * 
 * @param type - 'quality' (higher is better) or 'latency' (lower is better)
 */
export function RankBadge({ 
  rank, 
  relative,
  type = 'quality',
  size = 'sm',
  showRelative = true,
}: { 
  rank: number | null | undefined
  relative?: number | null
  /** 'quality' = higher is better (default), 'latency' = lower is better */
  type?: 'quality' | 'latency'
  size?: 'sm' | 'md'
  showRelative?: boolean
}) {
  if (rank === null || rank === undefined) return null
  
  const sizeClasses = size === 'sm' ? 'text-[9px]' : 'text-xs'
  
  // For latency, invert relative for coloring (negative = faster = good = green)
  const colorRelative = type === 'latency' && relative !== null && relative !== undefined
    ? -relative 
    : relative
  const colorClass = getRelativeColorClass(colorRelative)
  
  // Medal emoji for top 3
  const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : ''
  
  // Latency icon for speed rankings
  const icon = type === 'latency' ? '⚡' : ''
  
  return (
    <div className={`${sizeClasses} ${colorClass} flex items-center gap-0.5 whitespace-nowrap`}>
      {medal && <span>{medal}</span>}
      {!medal && icon && <span>{icon}</span>}
      <span>#{rank}</span>
      {showRelative && relative !== null && relative !== undefined && (
        <span className="opacity-70">({formatRelativeScore(relative)})</span>
      )}
    </div>
  )
}

/**
 * Combined quality and latency ranks display for column headers.
 */
export function ExecutorRanks({
  qualityRank,
  latencyRank,
  qualityRelative,
  latencyRelative,
  size = 'sm',
}: {
  qualityRank?: number | null
  latencyRank?: number | null
  qualityRelative?: number | null
  latencyRelative?: number | null
  size?: 'sm' | 'md'
}) {
  const hasQuality = qualityRank !== null && qualityRank !== undefined
  const hasLatency = latencyRank !== null && latencyRank !== undefined
  
  if (!hasQuality && !hasLatency) return null
  
  return (
    <div className="flex flex-col items-center gap-0.5">
      {hasQuality && (
        <RankBadge 
          rank={qualityRank} 
          relative={qualityRelative} 
          type="quality" 
          size={size}
          showRelative={true}
        />
      )}
      {hasLatency && (
        <RankBadge 
          rank={latencyRank} 
          relative={latencyRelative} 
          type="latency" 
          size={size}
          showRelative={false}
        />
      )}
    </div>
  )
}

// Latency badge with optional std and relative coloring
export function LatencyBadge({
  value,
  std,
  relative,
  showStd = false,
  size = 'sm',
}: {
  value: number | null | undefined
  std?: number | null
  relative?: number | null
  showStd?: boolean
  size?: 'sm' | 'md'
}) {
  if (value === null || value === undefined) {
    return <span className="text-text-disabled text-xs">—</span>
  }
  
  const sizeClasses = size === 'sm' ? 'text-[9px]' : 'text-xs'
  // For latency, lower is better, so invert the relative score for coloring
  const colorClass = relative !== null && relative !== undefined 
    ? getRelativeColorClass(-relative) // Invert: negative relative (fast) = green
    : 'text-text-tertiary'
  
  return (
    <span className={`${sizeClasses} ${colorClass}`}>
      {showStd ? formatDurationWithStd(value, std) : formatDuration(value)}
    </span>
  )
}

// Matrix legend
export function MatrixLegend() {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-text-tertiary">
      <span className="text-emerald-400">≥3.5 Perfect</span>
      <span className="text-sky-400">≥2.5 Good</span>
      <span className="text-amber-400">≥1.5 Workable</span>
      <span className="text-rose-400">&lt;1.5 Bad</span>
      <span className="border-l border-border pl-4 text-status-success">✓ Done</span>
      <span className="text-status-error">✗ Failed</span>
      <span className="text-status-warning">⏱ Timeout</span>
      <span className="border-l border-border pl-4">🥇🥈🥉 Quality rank</span>
      <span>⚡ Speed rank</span>
      <span className="border-l border-border pl-4">σ = std dev</span>
    </div>
  )
}


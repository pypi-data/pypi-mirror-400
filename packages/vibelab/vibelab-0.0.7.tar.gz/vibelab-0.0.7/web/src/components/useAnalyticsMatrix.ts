import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState, useCallback, useEffect, useRef } from 'react'
import {
  getGlobalAnalytics,
  getDatasetAnalytics,
  listPendingJudgements,
  getActiveJudgementResultIds,
  enqueueJudgeResult,
  createRun,
  listJudges,
} from '../api'
import {
  MatrixRow,
  computeAggregations,
  computeStats,
  cellNeedsRun,
  Aggregations,
} from './AnalyticsMatrix'
import { getExecutorDisplayName } from '../lib/modelNames'

export type AnalyticsMode = 'global' | 'dataset'

export interface UseAnalyticsMatrixOptions {
  mode: AnalyticsMode
  datasetId?: number
}

export type ModelSummaryPoint = {
  executor: string
  harness: string
  provider: string
  model: string
  avgQuality: number
  qualityCount: number
  avgDurationMs: number | null
  durationCount: number
  avgCostUsd: number | null
  costCount: number
}

// Common analytics data shape
interface AnalyticsData {
  executors: string[]
  matrix: MatrixRow[]
  dataset?: { id: number; name: string; description?: string }
  scenario_count?: number
}

export function useAnalyticsMatrix({ mode, datasetId }: UseAnalyticsMatrixOptions) {
  const queryClient = useQueryClient()
  const [judgingResultIds, setJudgingResultIds] = useState<Set<number>>(new Set())
  const [batchRunning, setBatchRunning] = useState<Set<string>>(new Set())
  const [autoJudgeScenarios, setAutoJudgeScenarios] = useState<Set<number>>(new Set())
  const prevPendingRef = useRef<Set<number>>(new Set())

  const queryKey = mode === 'global' ? ['global-analytics'] : ['dataset-analytics', datasetId]

  const { data: rawData, isLoading } = useQuery({
    queryKey,
    queryFn: async (): Promise<AnalyticsData | null> => {
      if (mode === 'global') {
        const result = await getGlobalAnalytics()
        return result as AnalyticsData
      } else if (datasetId != null) {
        const result = await getDatasetAnalytics(datasetId)
        return result as AnalyticsData
      }
      return null
    },
    enabled: mode === 'global' || datasetId != null,
    refetchInterval: (query) => {
      const d = query.state.data
      if (d?.matrix?.some((row: MatrixRow) =>
        Object.values(row.cells).some((cell) => cell.status === 'running' || cell.status === 'queued')
      )) {
        return 3000
      }
      return judgingResultIds.size > 0 || batchRunning.size > 0 || autoJudgeScenarios.size > 0 ? 2000 : false
    },
  })

  // Normalize to AnalyticsData
  const data = rawData ?? null

  const { data: pendingJudgements } = useQuery({
    queryKey: ['judgements', 'pending'],
    queryFn: listPendingJudgements,
    refetchInterval: judgingResultIds.size > 0 || autoJudgeScenarios.size > 0 ? 2000 : 10000,
  })

  const { data: activeJudgementResultIds } = useQuery({
    queryKey: ['tasks', 'judge_result', 'active_result_ids'],
    queryFn: getActiveJudgementResultIds,
    refetchInterval: 2000,
  })

  const { data: allJudges } = useQuery({
    queryKey: ['judges'],
    queryFn: () => listJudges(),
  })

  const judgeByScenario = useMemo(() => {
    const map = new Map<number, number>()
    if (allJudges) {
      const sorted = [...allJudges].sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      for (const judge of sorted) {
        if (!map.has(judge.scenario_id)) {
          map.set(judge.scenario_id, judge.id)
        }
      }
    }
    return map
  }, [allJudges])

  // Filter pending judgements to only those relevant to current data
  const relevantPendingJudgements = useMemo(() => {
    const pending = pendingJudgements ?? []
    const active = activeJudgementResultIds ?? new Set<number>()
    const filtered = pending.filter((item: any) => !active.has(item.result.id))
    
    if (mode === 'dataset' && data) {
      const scenarioIds = new Set(data.matrix.map((row: MatrixRow) => row.scenario_id))
      return filtered.filter((item: any) => scenarioIds.has(item.result?.scenario_id))
    }
    return filtered
  }, [pendingJudgements, activeJudgementResultIds, mode, data])

  const runMutation = useMutation({
    mutationFn: (params: { scenario_id: number; executor_spec: string }) => createRun(params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  })

  const runJudge = useCallback(async (judgeId: number, resultId: number) => {
    setJudgingResultIds(prev => new Set(prev).add(resultId))
    try {
      await enqueueJudgeResult(judgeId, resultId)
      queryClient.invalidateQueries({ queryKey: ['judgements'] })
      queryClient.invalidateQueries({ queryKey })
    } catch (e) {
      console.error(`Failed to judge result ${resultId}:`, e)
    } finally {
      setJudgingResultIds(prev => { const n = new Set(prev); n.delete(resultId); return n })
    }
  }, [queryClient, queryKey])

  const runAllJudges = useCallback(() => {
    relevantPendingJudgements.forEach((item: any) => {
      if (!judgingResultIds.has(item.result.id)) runJudge(item.judge.id, item.result.id)
    })
  }, [relevantPendingJudgements, judgingResultIds, runJudge])

  // Auto-judge newly completed results
  useEffect(() => {
    if (!pendingJudgements || autoJudgeScenarios.size === 0) return

    const currentPendingIds = new Set(pendingJudgements.map((p: any) => p.result.id))
    const prevPendingIds = prevPendingRef.current

    for (const item of pendingJudgements) {
      const resultId = item.result.id
      const scenarioId = item.result.scenario_id

      if (!prevPendingIds.has(resultId) && autoJudgeScenarios.has(scenarioId)) {
        if (!judgingResultIds.has(resultId)) {
          runJudge(item.judge.id, resultId)
        }
      }
    }

    prevPendingRef.current = currentPendingIds
  }, [pendingJudgements, autoJudgeScenarios, judgingResultIds, runJudge])

  // Filter executors to only show those with at least 1 completed run
  // Sort by average quality (best first)
  const visibleExecutors = useMemo(() => {
    if (!data) return []
    
    // Filter to executors with at least 1 completed run
    const filtered = data.executors.filter((exec: string) => {
      return data.matrix.some((row: MatrixRow) => {
        const cell = row.cells[exec]
        return cell && cell.completed > 0
      })
    })
    
    // Compute average quality per executor for sorting
    const qualityByExec: Record<string, { sum: number; count: number }> = {}
    filtered.forEach((exec: string) => {
      qualityByExec[exec] = { sum: 0, count: 0 }
    })
    
    data.matrix.forEach((row: MatrixRow) => {
      filtered.forEach((exec: string) => {
        const cell = row.cells[exec]
        if (cell?.avg_quality != null && cell.quality_count && cell.quality_count > 0) {
          qualityByExec[exec].sum += cell.avg_quality * cell.quality_count
          qualityByExec[exec].count += cell.quality_count
        }
      })
    })
    
    // Sort by average quality (highest first), then by name for stability
    return filtered.sort((a, b) => {
      const aAvg = qualityByExec[a].count > 0 ? qualityByExec[a].sum / qualityByExec[a].count : -Infinity
      const bAvg = qualityByExec[b].count > 0 ? qualityByExec[b].sum / qualityByExec[b].count : -Infinity
      if (bAvg !== aAvg) return bAvg - aAvg // Higher quality first
      return a.localeCompare(b) // Alphabetical for ties
    })
  }, [data])

  // Compute missing runs (only for visible executors)
  const missingRuns = useMemo(() => {
    if (!data) return { byRow: {} as Record<number, Array<{ scenarioId: number; executor: string }>>, byColumn: {} as Record<string, Array<{ scenarioId: number; executor: string }>>, all: [] as Array<{ scenarioId: number; executor: string }> }

    const byRow: Record<number, Array<{ scenarioId: number; executor: string }>> = {}
    const byColumn: Record<string, Array<{ scenarioId: number; executor: string }>> = {}
    const all: Array<{ scenarioId: number; executor: string }> = []

    for (const row of data.matrix) {
      byRow[row.scenario_id] = []
      for (const executor of visibleExecutors) {
        if (!byColumn[executor]) byColumn[executor] = []

        const cell = row.cells[executor] || { completed: 0, running: 0, queued: 0 }
        if (cellNeedsRun(cell) && cell.running === 0 && cell.queued === 0) {
          const item = { scenarioId: row.scenario_id, executor }
          byRow[row.scenario_id].push(item)
          byColumn[executor].push(item)
          all.push(item)
        }
      }
    }

    return { byRow, byColumn, all }
  }, [data, visibleExecutors])

  // Batch run handler
  const runBatch = useCallback(async (
    items: Array<{ scenarioId: number; executor: string }>,
    trackAutoJudge = true
  ) => {
    const keys = items.map(i => `${i.scenarioId}:${i.executor}`)
    setBatchRunning(prev => new Set([...prev, ...keys]))

    if (trackAutoJudge) {
      const scenariosWithJudges = new Set(
        items
          .filter(i => judgeByScenario.has(i.scenarioId))
          .map(i => i.scenarioId)
      )
      if (scenariosWithJudges.size > 0) {
        setAutoJudgeScenarios(prev => new Set([...prev, ...scenariosWithJudges]))
      }
    }

    try {
      await Promise.all(
        items.map(({ scenarioId, executor }) =>
          createRun({ scenario_id: scenarioId, executor_spec: executor })
        )
      )
      queryClient.invalidateQueries({ queryKey })
    } catch (e) {
      console.error('Batch run failed:', e)
    } finally {
      setBatchRunning(prev => {
        const n = new Set(prev)
        keys.forEach(k => n.delete(k))
        return n
      })
    }
  }, [judgeByScenario, queryClient, queryKey])

  const handleRunRowMissing = useCallback((scenarioId: number) => {
    const items = missingRuns.byRow[scenarioId] || []
    if (items.length > 0) runBatch(items)
  }, [missingRuns.byRow, runBatch])

  const handleRunColumnMissing = useCallback((executor: string) => {
    const items = missingRuns.byColumn[executor] || []
    if (items.length > 0) runBatch(items)
  }, [missingRuns.byColumn, runBatch])

  const handleRunAllMissing = useCallback(() => {
    if (missingRuns.all.length > 0) runBatch(missingRuns.all)
  }, [missingRuns.all, runBatch])

  // Aggregations using new format with mean/std/count
  const agg = useMemo((): Aggregations => {
    if (!data) return {
      global: { 
        quality: { mean: null, std: null, count: 0 }, 
        latency: { mean: null, std: null, count: 0 } 
      },
      byScenario: {},
      byExecutor: {},
    }
    return computeAggregations(data.matrix, data.executors)
  }, [data])

  const stats = useMemo(() => {
    if (!data) return { completed: 0, failed: 0, running: 0, pendingJudges: 0 }
    const base = computeStats(data.matrix)
    return { ...base, pendingJudges: relevantPendingJudgements.length }
  }, [data, relevantPendingJudgements])

  // Model summary for tradeoff plot
  const modelSummaryPoints: ModelSummaryPoint[] = useMemo(() => {
    if (!data) return []
    const { executors, matrix } = data

    const byExec = new Map<
      string,
      { qSum: number; qCount: number; dSum: number; dCount: number; cSum: number; cCount: number }
    >()
    executors.forEach((e: string) => byExec.set(e, { qSum: 0, qCount: 0, dSum: 0, dCount: 0, cSum: 0, cCount: 0 }))

    matrix.forEach((row: MatrixRow) => {
      executors.forEach((exec: string) => {
        const cell = row.cells[exec]
        if (!cell) return
        if (cell.avg_quality != null && cell.quality_count) {
          const s = byExec.get(exec)
          if (s) {
            s.qSum += cell.avg_quality * cell.quality_count
            s.qCount += cell.quality_count
          }
        }
        if (cell.avg_duration_ms != null && cell.duration_count) {
          const s = byExec.get(exec)
          if (s) {
            s.dSum += cell.avg_duration_ms * cell.duration_count
            s.dCount += cell.duration_count
          }
        }
        if (cell.avg_cost_usd != null && cell.cost_count) {
          const s = byExec.get(exec)
          if (s) {
            s.cSum += cell.avg_cost_usd * cell.cost_count
            s.cCount += cell.cost_count
          }
        }
      })
    })

    const out: ModelSummaryPoint[] = []
    byExec.forEach((v, exec) => {
      if (v.qCount <= 0) return
      const [harness, provider, model] = exec.split(':')
      out.push({
        executor: exec,
        harness: harness ?? '',
        provider: provider ?? 'unknown',
        model: model ?? exec,
        avgQuality: v.qSum / v.qCount,
        qualityCount: v.qCount,
        avgDurationMs: v.dCount > 0 ? v.dSum / v.dCount : null,
        durationCount: v.dCount,
        avgCostUsd: v.cCount > 0 ? v.cSum / v.cCount : null,
        costCount: v.cCount,
      })
    })

    return out.sort((a, b) => a.provider.localeCompare(b.provider) || a.model.localeCompare(b.model))
  }, [data])

  const tradeoffPoints = useMemo(() => {
    return modelSummaryPoints
      .filter((p) => p.avgQuality != null)
      .map((p) => ({
        key: p.executor,
        provider: p.provider,
        label: getExecutorDisplayName(p.executor),
        quality: p.avgQuality,
        hasQuality: true,
        durationMs: p.avgDurationMs,
        costUsd: p.avgCostUsd,
        count: p.qualityCount,
      }))
  }, [modelSummaryPoints])

  const handleStartRun = useCallback((scenarioId: number, executor: string) => {
    runMutation.mutate({ scenario_id: scenarioId, executor_spec: executor })
  }, [runMutation])

  const isStartingRun = useCallback((scenarioId: number, executor: string) => {
    return runMutation.isPending &&
      runMutation.variables?.scenario_id === scenarioId &&
      runMutation.variables?.executor_spec === executor
  }, [runMutation])

  // Sort matrix rows by average quality (ascending - hardest scenarios first)
  const sortedMatrix = useMemo(() => {
    if (!data?.matrix) return []
    
    // Compute average quality per scenario
    const qualityByScenario: Record<number, { sum: number; count: number }> = {}
    
    data.matrix.forEach((row: MatrixRow) => {
      qualityByScenario[row.scenario_id] = { sum: 0, count: 0 }
      
      Object.values(row.cells).forEach((cell) => {
        if (cell?.avg_quality != null && cell.quality_count && cell.quality_count > 0) {
          qualityByScenario[row.scenario_id].sum += cell.avg_quality * cell.quality_count
          qualityByScenario[row.scenario_id].count += cell.quality_count
        }
      })
    })
    
    // Sort by average quality (ascending - lowest/hardest first)
    return [...data.matrix].sort((a, b) => {
      const aAvg = qualityByScenario[a.scenario_id].count > 0 
        ? qualityByScenario[a.scenario_id].sum / qualityByScenario[a.scenario_id].count 
        : Infinity
      const bAvg = qualityByScenario[b.scenario_id].count > 0 
        ? qualityByScenario[b.scenario_id].sum / qualityByScenario[b.scenario_id].count 
        : Infinity
      if (aAvg !== bAvg) return aAvg - bAvg // Lower quality (harder) first
      return a.scenario_id - b.scenario_id // By ID for stability
    })
  }, [data?.matrix])

  return {
    // Data
    data,
    isLoading,
    matrix: sortedMatrix,
    visibleExecutors,
    agg,
    stats,
    tradeoffPoints,
    
    // State
    judgingResultIds,
    batchRunning,
    judgeByScenario,
    missingRuns,
    
    // Actions
    runJudge,
    runAllJudges,
    handleStartRun,
    isStartingRun,
    handleRunRowMissing,
    handleRunColumnMissing,
    handleRunAllMissing,
  }
}

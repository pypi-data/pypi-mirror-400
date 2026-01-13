import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState, useMemo } from 'react'
import { getScenario, deleteScenario, rerunResult, listJudges, listScenarioJudgements, judgeResult, applyJudgeToAllCompleted, applyJudgeToResultsAsync, trainJudge, listTasks, getActiveJudgementResultIds, createJudge, updateJudge, listJudgeModels, getPairwiseRankings, Result, Task, ResultRanking } from '../api'
import { FullPageTableLayout, Table, StatusBadge, Button, Checkbox, ConfirmDialog, EmptyState, DropdownMenu, DropdownItem, OverflowMenuTrigger, QualityBadge, Textarea, Select } from './ui'
import { QualityTradeoffPlot, type QualityTradeoffPoint } from './QualityTradeoffPlot'
import { DEFAULT_JUDGE_GUIDANCE } from '../lib/judgeDefaults'

// Scatter Plot component for time vs score tradeoff
interface ScatterPlotProps {
  results: Result[]
  judgementsByResultId: Map<number, any>
  onPointClick?: (resultId: number) => void
  xMetric?: 'time' | 'cost'
}

function TimeVsScoreChart({ results, judgementsByResultId, onPointClick, xMetric = 'time' }: ScatterPlotProps) {
  const DEFAULT_QUALITY = 2.5
  
  const points: QualityTradeoffPoint[] = useMemo(() => {
    return results
      .filter((r) => r.status === 'completed')
      .map((r) => {
        let quality = r.quality
        let hasQuality = true
        if (quality === null || quality === undefined) {
          const judgement = judgementsByResultId.get(r.id)
          quality = judgement?.quality ?? null
          if (quality === null || quality === undefined) {
            quality = DEFAULT_QUALITY
            hasQuality = false
          }
        }

        return {
          key: String(r.id),
          provider: r.provider,
          label: r.model,
          quality: quality!,
          hasQuality,
          durationMs: r.duration_ms ?? null,
          costUsd: r.cost_usd ?? null,
          count: 1,
        }
      })
  }, [results, judgementsByResultId])

  return (
    <QualityTradeoffPlot
      points={points}
      xMetric={xMetric}
      emptyText="No completed results yet"
      onPointClick={(p) => onPointClick?.(Number(p.key))}
    />
  )
}

// Judge Drawer Panel with integrated form
interface JudgeDrawerProps {
  open: boolean
  onClose: () => void
  scenarioId: number
  latestJudge: any
  judges: any[]
  results: Result[]
  latestJudgeJudgements: any[]
  outdatedJudgements: number[]
  judgementCountByJudgeId: Map<number, number>
  alignmentTask: Task | undefined
  alignmentTaskFinal: Task | null
  alignmentTaskId: number | null
  onTrainAlignment: () => void
  isTrainingAlignment: boolean
  onRejudgeAllOutdated: () => void
  isRejudging: boolean
  rejudgeProgress: { current: number; total: number } | null
  onApplyAll: () => void
  isApplyingAll: boolean
}

function JudgeDrawer({
  open,
  onClose,
  scenarioId,
  latestJudge,
  judges,
  results,
  latestJudgeJudgements,
  outdatedJudgements,
  judgementCountByJudgeId,
  alignmentTask,
  alignmentTaskFinal,
  alignmentTaskId,
  onTrainAlignment,
  isTrainingAlignment,
  onRejudgeAllOutdated,
  isRejudging,
  rejudgeProgress,
  onApplyAll,
  isApplyingAll,
}: JudgeDrawerProps) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'view' | 'edit'>('view')
  
  // Form state
  const [guidance, setGuidance] = useState('')
  const [judgeProvider, setJudgeProvider] = useState('anthropic')
  const [judgeModel, setJudgeModel] = useState('claude-sonnet-4-20250514')
  const [trainingSampleIds, setTrainingSampleIds] = useState<Set<number>>(new Set())
  const [formError, setFormError] = useState<string | null>(null)

  // Get available judge models
  const { data: judgeModelsData } = useQuery({
    queryKey: ['judge-models'],
    queryFn: listJudgeModels,
    enabled: open,
    staleTime: 5 * 60 * 1000,
  })

  const currentProviderModels = judgeModelsData?.providers.find(p => p.id === judgeProvider)?.models || []

  // Reset to view mode when drawer closes
  useEffect(() => {
    if (!open) {
      setMode('view')
      setFormError(null)
    }
  }, [open])

  // Load existing judge data when entering edit mode
  useEffect(() => {
    if (mode === 'edit') {
      if (latestJudge) {
        setGuidance(latestJudge.guidance)
        setJudgeProvider(latestJudge.judge_provider)
        setJudgeModel(latestJudge.judge_model)
        setTrainingSampleIds(new Set(latestJudge.training_sample_ids))
      } else {
        setGuidance(DEFAULT_JUDGE_GUIDANCE)
        setJudgeProvider('anthropic')
        setJudgeModel('claude-sonnet-4-20250514')
        setTrainingSampleIds(new Set())
      }
      setFormError(null)
    }
  }, [mode, latestJudge])

  // Auto-enter edit mode if no judge exists
  useEffect(() => {
    if (open && !latestJudge) {
      setMode('edit')
    }
  }, [open, latestJudge])

  const saveMutation = useMutation({
    mutationFn: (data: { guidance: string, judge_provider: string, judge_model: string, training_sample_ids: number[] }) => {
      if (latestJudge) {
        return updateJudge(latestJudge.id, { scenario_id: scenarioId, ...data })
      }
      return createJudge({ scenario_id: scenarioId, ...data })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['judges', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      setMode('view')
    },
  })

  const handleSave = () => {
    setFormError(null)
    if (!guidance.trim()) {
      setFormError('Please provide guidance for the judge')
      return
    }
    saveMutation.mutate({
      guidance,
      judge_provider: judgeProvider,
      judge_model: judgeModel,
      training_sample_ids: Array.from(trainingSampleIds),
    })
  }

  const toggleTrainingSample = (resultId: number) => {
    const newSet = new Set(trainingSampleIds)
    if (newSet.has(resultId)) {
      newSet.delete(resultId)
    } else {
      newSet.add(resultId)
    }
    setTrainingSampleIds(newSet)
  }

  const scorableResults = results.filter(r => 
    r.status === 'completed' && (r.quality !== null && r.quality !== undefined)
  )

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/40 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-[520px] max-w-[90vw] bg-surface border-l border-border shadow-xl z-50 flex flex-col animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="shrink-0 px-6 py-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">
            {mode === 'edit' ? (latestJudge ? 'Edit Judge' : 'Create Judge') : 'Judge Configuration'}
          </h2>
          <div className="flex items-center gap-2">
            {mode === 'view' && latestJudge && (
              <Button size="sm" variant="secondary" onClick={() => setMode('edit')}>
                Edit
              </Button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded hover:bg-surface-2 text-text-tertiary hover:text-text-primary transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        {/* Drawer Content */}
        <div className="flex-1 overflow-auto p-6">
          {mode === 'edit' ? (
            // Edit Mode - Form
            <div className="space-y-5">
              <div>
                <label className="block text-xs text-text-tertiary uppercase tracking-wide mb-2">
                  Guidance
                </label>
                <Textarea
                  value={guidance}
                  onChange={(e) => setGuidance(e.target.value)}
                  placeholder="Provide guidance for the judge on how to evaluate results..."
                  rows={8}
                  className="text-sm"
                />
              </div>

              <div>
                <label className="block text-xs text-text-tertiary uppercase tracking-wide mb-2">
                  Judge Model
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <Select
                    value={judgeProvider}
                    onChange={(e) => {
                      const newProvider = e.target.value
                      setJudgeProvider(newProvider)
                      const newProviderModels = judgeModelsData?.providers.find(p => p.id === newProvider)?.models || []
                      if (newProviderModels.length > 0) {
                        setJudgeModel(newProviderModels[0].id)
                      }
                    }}
                    options={
                      judgeModelsData?.providers.map(p => ({ value: p.id, label: p.name })) || [
                        { value: 'anthropic', label: 'Anthropic' },
                        { value: 'openai', label: 'OpenAI' },
                      ]
                    }
                  />
                  <Select
                    value={judgeModel}
                    onChange={(e) => setJudgeModel(e.target.value)}
                    options={
                      currentProviderModels.length > 0
                        ? currentProviderModels.map(m => ({
                            value: m.id,
                            label: m.input_price_per_1m !== undefined
                              ? `${m.name} ($${m.input_price_per_1m})`
                              : m.name
                          }))
                        : [{ value: judgeModel, label: judgeModel }]
                    }
                  />
                </div>
              </div>

              {scorableResults.length > 0 && (
                <div>
                  <label className="block text-xs text-text-tertiary uppercase tracking-wide mb-2">
                    Few-shot Examples
                    <span className="ml-2 text-text-secondary font-normal normal-case">
                      {trainingSampleIds.size} selected
                    </span>
                  </label>
                  <div className="text-xs text-text-tertiary mb-2">
                    Select human-scored results to include as examples.
                  </div>
                  <div className="max-h-48 overflow-y-auto border border-border rounded-lg bg-surface-2 divide-y divide-border-muted">
                    {scorableResults.map((result) => (
                      <div
                        key={result.id}
                        onClick={() => toggleTrainingSample(result.id)}
                        className="flex items-center gap-3 px-3 py-2 hover:bg-surface-3 cursor-pointer transition-colors"
                      >
                        <Checkbox
                          checked={trainingSampleIds.has(result.id)}
                          onChange={() => toggleTrainingSample(result.id)}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-text-tertiary font-mono truncate">
                            {result.harness}:{result.provider}:{result.model}
                          </div>
                        </div>
                        <QualityBadge quality={result.quality as 1|2|3|4|null} size="sm" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {scorableResults.length === 0 && (
                <div className="bg-surface-2 border border-border rounded-lg p-4">
                  <p className="text-sm text-text-secondary">
                    Add human scores to results to enable few-shot examples for better alignment.
                  </p>
                </div>
              )}

              {formError && (
                <div className="px-3 py-2 rounded-lg bg-status-error-muted border border-status-error/30 text-sm text-status-error">
                  {formError}
                </div>
              )}
            </div>
          ) : (
            // View Mode
            <div className="space-y-5">
              {/* Stats row */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-surface-2 rounded-lg p-3">
                  <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Alignment</div>
                  <div className="text-lg font-semibold text-text-primary">
                    {latestJudge?.alignment_score != null
                      ? latestJudge.alignment_score.toFixed(3)
                      : '—'}
                  </div>
                </div>
                <div className="bg-surface-2 rounded-lg p-3">
                  <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Examples</div>
                  <div className="text-lg font-semibold text-text-primary">
                    {latestJudge?.training_sample_ids.length ?? 0}
                  </div>
                </div>
                <div className="bg-surface-2 rounded-lg p-3">
                  <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Judged</div>
                  <div className="text-lg font-semibold text-text-primary">
                    {latestJudgeJudgements.length}
                    <span className="text-xs font-normal text-text-tertiary">
                      /{results.filter(r => r.status === 'completed').length}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={onTrainAlignment}
                  disabled={isTrainingAlignment || alignmentTaskId !== null || scorableResults.length === 0}
                  className="flex-1"
                  title={scorableResults.length === 0 ? 'Add human scores to results first' : undefined}
                >
                  {alignmentTaskId !== null
                    ? 'Evaluating...'
                    : latestJudge?.alignment_score != null
                      ? 'Recalculate Alignment'
                      : 'Evaluate Alignment'}
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={onApplyAll}
                  disabled={isApplyingAll || results.filter(r => r.status === 'completed').length === 0}
                  className="flex-1"
                >
                  {isApplyingAll ? 'Applying...' : 'Apply to All'}
                </Button>
              </div>

              {alignmentTask && (
                <div className="text-xs text-text-tertiary">Status: {alignmentTask.status}</div>
              )}
              {alignmentTaskFinal?.status === 'failed' && alignmentTaskFinal.error_message && (
                <div className="text-xs text-status-error bg-status-error-muted px-3 py-2 rounded">
                  Failed: {alignmentTaskFinal.error_message}
                </div>
              )}

              {/* Re-judge outdated */}
              {outdatedJudgements.length > 0 && (
                <div className="bg-status-warning-muted border border-status-warning/30 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="text-status-warning text-xs font-medium flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-status-warning" />
                        {outdatedJudgements.length} outdated
                      </div>
                      <div className="text-text-secondary text-xs mt-0.5">
                        Judgements from older versions
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={onRejudgeAllOutdated}
                      disabled={isRejudging}
                    >
                      {isRejudging && rejudgeProgress
                        ? `${rejudgeProgress.current}/${rejudgeProgress.total}`
                        : 'Re-judge'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Guidance */}
              {latestJudge?.guidance && (
                <div>
                  <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-2">Guidance</div>
                  <div className="bg-surface-2 rounded-lg p-3 text-text-secondary text-sm whitespace-pre-wrap max-h-[200px] overflow-auto">
                    {latestJudge.guidance}
                  </div>
                </div>
              )}

              {/* Model info */}
              {latestJudge && (
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-tertiary">Model</span>
                  <span className="font-mono text-text-secondary">
                    {latestJudge.judge_provider}:{latestJudge.judge_model}
                  </span>
                </div>
              )}

              {/* Judge versions */}
              {judges && judges.length > 1 && (
                <div>
                  <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-2">
                    Version History ({judges.length})
                  </div>
                  <div className="space-y-1.5">
                    {judges.map((j: any, idx: number) => (
                      <div 
                        key={j.id} 
                        className={`flex items-center justify-between px-3 py-2 rounded text-xs ${
                          idx === 0 ? 'bg-accent/10 border border-accent/20' : 'bg-surface-2'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-text-primary">v{judges.length - idx}</span>
                          {idx === 0 && (
                            <span className="text-[9px] px-1 py-0.5 rounded bg-accent/20 text-accent font-medium">
                              Current
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-text-tertiary">
                          <span>{j.training_sample_ids.length} ex</span>
                          <span>{judgementCountByJudgeId.get(j.id) ?? 0} judged</span>
                          <span>{j.alignment_score?.toFixed(2) ?? '—'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer for edit mode */}
        {mode === 'edit' && (
          <div className="shrink-0 px-6 py-4 border-t border-border flex items-center justify-end gap-2">
            <Button 
              variant="ghost" 
              onClick={() => latestJudge ? setMode('view') : onClose()}
              disabled={saveMutation.isPending}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving...' : (latestJudge ? 'Update Judge' : 'Create Judge')}
            </Button>
          </div>
        )}
      </div>
    </>
  )
}

export default function ScenarioDetail() {
  const { id } = useParams<{ id: string }>()
  const scenarioId = id ? Number(id) : Number.NaN
  const hasScenarioId = Number.isFinite(scenarioId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set())
  const [timeVsQualityX, setTimeVsQualityX] = useState<'time' | 'cost'>('time')
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showJudgeDrawer, setShowJudgeDrawer] = useState(false)
  const [alignmentTaskId, setAlignmentTaskId] = useState<number | null>(null)
  const [alignmentTaskFinal, setAlignmentTaskFinal] = useState<Task | null>(null)
  
  const { data, isLoading } = useQuery({
    queryKey: ['scenario', scenarioId],
    queryFn: () => getScenario(scenarioId),
    enabled: hasScenarioId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data && data.results.some((r: any) => r.status === 'running' || r.status === 'queued')) {
        return 3000
      }
      return false
    },
  })

  const { data: judges } = useQuery({
    queryKey: ['judges', scenarioId],
    queryFn: () => listJudges(scenarioId),
    enabled: hasScenarioId,
  })
  const latestJudge = judges?.[0]

  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => listTasks({ limit: 200 }),
    enabled: alignmentTaskId !== null,
    refetchInterval: alignmentTaskId !== null ? 1000 : false,
  })

  const { data: activeJudgementResultIds = new Set<number>() } = useQuery({
    queryKey: ['active-judgement-results'],
    queryFn: getActiveJudgementResultIds,
    refetchInterval: 2000,
    select: (data) => data,
  })

  const alignmentTask: Task | undefined = useMemo(() => {
    if (!alignmentTaskId || !tasks) return undefined
    return tasks.find(t => t.id === alignmentTaskId)
  }, [alignmentTaskId, tasks])

  const { data: allJudgements } = useQuery({
    queryKey: ['scenario-judgements', scenarioId],
    queryFn: () => listScenarioJudgements(scenarioId),
    enabled: hasScenarioId,
  })

  const { data: pairwiseRankingsData } = useQuery({
    queryKey: ['pairwise-rankings', scenarioId],
    queryFn: () => getPairwiseRankings(scenarioId),
    enabled: hasScenarioId,
  })

  const judgementsByResultId = useMemo(() => {
    if (!allJudgements) return new Map()
    const map = new Map()
    const sorted = [...allJudgements].sort((a, b) => {
      if (a.is_latest_judge && !b.is_latest_judge) return -1
      if (!a.is_latest_judge && b.is_latest_judge) return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
    sorted.forEach((j: any) => {
      if (!map.has(j.result_id)) {
        map.set(j.result_id, j)
      }
    })
    return map
  }, [allJudgements])

  const latestJudgeJudgements = useMemo(() => {
    if (!allJudgements || !latestJudge) return []
    return allJudgements.filter((j: any) => j.judge_id === latestJudge.id)
  }, [allJudgements, latestJudge])

  const judgementCountByJudgeId = useMemo(() => {
    const counts = new Map<number, number>()
    if (!allJudgements) return counts
    allJudgements.forEach((j: any) => {
      counts.set(j.judge_id, (counts.get(j.judge_id) ?? 0) + 1)
    })
    return counts
  }, [allJudgements])

  const outdatedJudgements = useMemo(() => {
    if (!allJudgements || !latestJudge || !data?.results) return []
    const completedResultIds = new Set(
      data.results.filter(r => r.status === 'completed').map(r => r.id)
    )
    const resultsWithLatestJudge = new Set(
      allJudgements.filter((j: any) => j.judge_id === latestJudge.id).map((j: any) => j.result_id)
    )
    const outdatedResultIds: number[] = []
    allJudgements.forEach((j: any) => {
      if (
        completedResultIds.has(j.result_id) &&
        !resultsWithLatestJudge.has(j.result_id) &&
        !outdatedResultIds.includes(j.result_id)
      ) {
        outdatedResultIds.push(j.result_id)
      }
    })
    return outdatedResultIds
  }, [allJudgements, latestJudge, data?.results])

  const rankingsByResultId = useMemo(() => {
    const map = new Map<number, ResultRanking>()
    if (!pairwiseRankingsData?.rankings) return map
    pairwiseRankingsData.rankings.forEach((r) => {
      map.set(r.result_id, r)
    })
    return map
  }, [pairwiseRankingsData])

  const hasPairwiseData = rankingsByResultId.size > 0 && 
    Array.from(rankingsByResultId.values()).some(r => r.comparisons > 0)

  useEffect(() => {
    if (!alignmentTaskId) return
    if (!alignmentTask) return
    if (alignmentTask.status !== 'completed' && alignmentTask.status !== 'failed') return

    setAlignmentTaskFinal(alignmentTask)
    setAlignmentTaskId(null)
    if (alignmentTask.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['judges', scenarioId] })
    }
  }, [alignmentTaskId, alignmentTask, queryClient, scenarioId])

  const trainAlignmentMutation = useMutation({
    mutationFn: async () => {
      if (!latestJudge) throw new Error('No judge configured')
      return trainJudge(latestJudge.id, [])
    },
    onSuccess: (res) => {
      setAlignmentTaskFinal(null)
      setAlignmentTaskId(res.task_id)
    },
  })

  const [isRejudging, setIsRejudging] = useState(false)
  const [rejudgeProgress, setRejudgeProgress] = useState<{ current: number; total: number } | null>(null)

  const deleteMutation = useMutation({
    mutationFn: () => deleteScenario(scenarioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      navigate('/scenarios')
    },
  })

  const rerunMutation = useMutation({
    mutationFn: (resultId: number) => rerunResult(resultId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    },
  })

  const judgeResultMutation = useMutation({
    mutationFn: ({ resultId }: { resultId: number }) => {
      if (!latestJudge) throw new Error('No judge available')
      return judgeResult(latestJudge.id, resultId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
    },
  })

  const applyAllCompletedMutation = useMutation({
    mutationFn: () => {
      if (!latestJudge) throw new Error('No judge available')
      return applyJudgeToAllCompleted(latestJudge.id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
    },
  })

  const handleRejudgeAllOutdated = async () => {
    if (!latestJudge || outdatedJudgements.length === 0) return

    setIsRejudging(true)
    setRejudgeProgress({ current: 0, total: outdatedJudgements.length })

    try {
      await applyJudgeToResultsAsync(latestJudge.id, outdatedJudgements, true)
      setRejudgeProgress({ current: outdatedJudgements.length, total: outdatedJudgements.length })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
    } catch (error) {
      console.error('Failed to re-judge:', error)
      alert(`Failed to re-judge: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsRejudging(false)
      setRejudgeProgress(null)
    }
  }

  const scenario = data?.scenario
  const results = data?.results || []

  const runningCount = useMemo(() => {
    return results.filter(r => r.status === 'running' || r.status === 'queued').length
  }, [results])

  const toggleResult = (resultId: number) => {
    const newSelected = new Set(selectedResults)
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId)
    } else {
      newSelected.add(resultId)
    }
    setSelectedResults(newSelected)
  }

  const toggleAll = () => {
    if (selectedResults.size === results.length) {
      setSelectedResults(new Set())
    } else {
      setSelectedResults(new Set(results.map(r => r.id)))
    }
  }

  const handleCompare = () => {
    if (selectedResults.size >= 2) {
      const ids = Array.from(selectedResults).join(',')
      navigate(`/compare?ids=${ids}&scenario=${scenario?.id}`)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Header content
  const header = (
    <div className="space-y-3">
      {/* Title row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-text-primary">Scenario #{scenario?.id}</h1>
          {runningCount > 0 && (
            <div className="flex items-center gap-1.5 px-2 py-0.5 bg-accent-muted rounded-full">
              <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-xs text-accent font-medium">{runningCount} running</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button 
            size="sm"
            variant="secondary"
            onClick={handleCompare}
            disabled={selectedResults.size < 2}
          >
            Compare{selectedResults.size > 0 ? ` (${selectedResults.size})` : ''}
          </Button>
          <Link to={`/run/create?scenario=${scenario?.id}`}>
            <Button size="sm">New Run</Button>
          </Link>
          <DropdownMenu trigger={<OverflowMenuTrigger />}>
            <DropdownItem danger onClick={() => setShowDeleteDialog(true)}>
              Delete scenario
            </DropdownItem>
          </DropdownMenu>
        </div>
      </div>

      {/* Info + Plot row */}
      <div className="flex items-stretch bg-surface border border-border rounded-lg overflow-hidden h-[200px]">
        {/* Scenario info */}
        <div className="flex-1 py-3 px-4 min-w-0 flex flex-col">
          <div className="text-[10px] text-text-tertiary uppercase tracking-wide mb-1 shrink-0">Prompt</div>
          <div className="flex-1 overflow-auto">
            <p className="text-sm text-text-primary whitespace-pre-wrap">{scenario?.prompt}</p>
          </div>
        </div>

        {/* Code ref */}
        <div className="py-3 px-4 border-l border-border w-[160px] shrink-0">
          <div className="text-[10px] text-text-tertiary uppercase tracking-wide mb-1">Code</div>
          <div className="text-xs text-text-secondary">
            {scenario?.code_type === 'github' && scenario?.code_ref?.owner && (
              <a
                href={`https://github.com/${scenario.code_ref.owner}/${scenario.code_ref.repo}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:text-accent-hover font-mono"
              >
                {scenario.code_ref.owner}/{scenario.code_ref.repo}
              </a>
            )}
            {scenario?.code_type === 'local' && scenario?.code_ref?.path && (
              <span className="font-mono truncate block">{scenario.code_ref.path}</span>
            )}
            {!scenario?.code_ref && <span className="text-text-disabled">Empty</span>}
          </div>
        </div>

        {/* Judge metrics - clickable to open drawer */}
        <button
          onClick={() => setShowJudgeDrawer(true)}
          className="py-3 px-4 border-l border-border w-[200px] shrink-0 text-left hover:bg-surface-2 transition-colors group flex flex-col"
        >
          <div className="text-[10px] text-text-tertiary uppercase tracking-wide mb-2 flex items-center gap-1 shrink-0">
            Judge
            <svg className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
          {latestJudge ? (
            <div className="flex-1 flex flex-col justify-center gap-2">
              {/* Alignment */}
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-text-tertiary">Alignment</span>
                <span className="text-sm font-medium text-text-primary">
                  {latestJudge.alignment_score != null ? latestJudge.alignment_score.toFixed(3) : '—'}
                </span>
              </div>
              {/* Judged count */}
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-text-tertiary">Judged</span>
                <span className="text-sm text-text-primary">
                  {latestJudgeJudgements.length}
                  <span className="text-text-tertiary">/{results.filter(r => r.status === 'completed').length}</span>
                </span>
              </div>
              {/* Average quality */}
              {latestJudgeJudgements.length > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-text-tertiary">Avg Quality</span>
                  <span className="text-sm font-medium text-text-primary">
                    {(latestJudgeJudgements.reduce((sum: number, j: any) => sum + (j.quality || 0), 0) / latestJudgeJudgements.length).toFixed(2)}
                  </span>
                </div>
              )}
              {/* Outdated warning */}
              {outdatedJudgements.length > 0 && (
                <div className="flex items-center gap-1.5 text-status-warning">
                  <span className="w-1.5 h-1.5 rounded-full bg-status-warning" />
                  <span className="text-[10px]">{outdatedJudgements.length} outdated</span>
                </div>
              )}
              {/* Few-shot examples */}
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-text-tertiary">Examples</span>
                <span className="text-xs text-text-secondary">{latestJudge.training_sample_ids.length}</span>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <span className="text-xs text-accent">+ Create Judge</span>
            </div>
          )}
        </button>

        {/* Plot */}
        <div className="py-2 px-3 border-l border-border w-[320px] shrink-0 flex flex-col">
          <div className="flex items-center justify-between mb-1 shrink-0">
            <span className="text-[10px] text-text-tertiary uppercase tracking-wide">
              {timeVsQualityX === 'time' ? 'Time' : 'Cost'} vs Quality
            </span>
            <select
              className="h-5 rounded border border-border bg-surface px-1.5 text-[10px] text-text-secondary"
              value={timeVsQualityX}
              onChange={(e) => setTimeVsQualityX(e.target.value as 'time' | 'cost')}
            >
              <option value="time">Time</option>
              <option value="cost">Cost</option>
            </select>
          </div>
          <div className="flex-1 min-h-0">
            <TimeVsScoreChart
              results={results}
              judgementsByResultId={judgementsByResultId}
              xMetric={timeVsQualityX}
              onPointClick={(resultId) => navigate(`/result/${resultId}`)}
            />
          </div>
        </div>
      </div>
    </div>
  )

  if (isLoading) {
    return (
      <FullPageTableLayout header={header} isEmpty>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </FullPageTableLayout>
    )
  }

  if (!data) {
    return (
      <FullPageTableLayout
        header={header}
        isEmpty
        emptyState={<EmptyState title="Scenario not found" description="The scenario you're looking for doesn't exist." />}
      />
    )
  }

  return (
    <>
      <FullPageTableLayout
        header={header}
        isEmpty={results.length === 0}
        emptyState={
          <EmptyState
            title="No results yet"
            description="Run this scenario with different executors to see results."
            action={
              <Link to={`/run/create?scenario=${scenario?.id}`}>
                <Button>Run Scenario</Button>
              </Link>
            }
          />
        }
      >
        <Table fullPage maxHeight="full">
          <Table.Header>
            <tr>
              <Table.Head className="w-10 pl-6">
                <Checkbox
                  checked={selectedResults.size === results.length && results.length > 0}
                  onChange={toggleAll}
                />
              </Table.Head>
              <Table.Head>Executor</Table.Head>
              <Table.Head>Driver</Table.Head>
              <Table.Head>Status</Table.Head>
              <Table.Head>Human</Table.Head>
              {latestJudge && <Table.Head>Judge</Table.Head>}
              {hasPairwiseData && <Table.Head>Pairwise</Table.Head>}
              <Table.Head>Duration</Table.Head>
              <Table.Head>Changes</Table.Head>
              <Table.Head>Files</Table.Head>
              <Table.Head>Cost</Table.Head>
              <Table.Head>Finished</Table.Head>
              <Table.Head className="pr-6"></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {results.map((result) => (
              <Table.Row 
                key={result.id} 
                selected={selectedResults.has(result.id)}
                className="cursor-pointer"
                onClick={() => navigate(`/result/${result.id}`)}
              >
                <Table.Cell className="pl-6">
                  <div onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedResults.has(result.id)}
                      onChange={() => toggleResult(result.id)}
                    />
                  </div>
                </Table.Cell>
                <Table.Cell mono className="text-text-secondary text-xs">
                  {result.harness}:{result.provider}:{result.model}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {result.driver || 'local'}
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    {(result.status === 'running' || result.status === 'queued') && (
                      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                    )}
                    <StatusBadge status={result.status} isStale={result.is_stale} />
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <QualityBadge quality={result.quality as 1|2|3|4|null} />
                </Table.Cell>
                {latestJudge && (
                  <Table.Cell>
                    {judgementsByResultId.has(result.id) ? (
                      (() => {
                        const judgement = judgementsByResultId.get(result.id)
                        const isOutdated = !judgement.is_latest_judge
                        return (
                          <div className="flex items-center gap-2">
                            <QualityBadge quality={judgement.quality as 1|2|3|4|null} />
                            {isOutdated && (
                              <button
                                className={`text-xs hover:text-status-warning/80 ${
                                  activeJudgementResultIds.has(result.id)
                                    ? 'text-status-warning animate-pulse'
                                    : 'text-status-warning'
                                }`}
                                title={activeJudgementResultIds.has(result.id) ? 'Judging...' : 'Re-run with latest judge'}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  judgeResultMutation.mutate({ resultId: result.id })
                                }}
                                disabled={activeJudgementResultIds.has(result.id) || judgeResultMutation.isPending}
                              >
                                {activeJudgementResultIds.has(result.id) ? '⟳' : '↻'}
                              </button>
                            )}
                          </div>
                        )
                      })()
                    ) : activeJudgementResultIds.has(result.id) ? (
                      <div className="flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                        <span className="text-text-tertiary text-xs">Judging...</span>
                      </div>
                    ) : (
                      <span className="text-text-disabled text-sm">—</span>
                    )}
                  </Table.Cell>
                )}
                {hasPairwiseData && (
                  <Table.Cell>
                    {(() => {
                      const ranking = rankingsByResultId.get(result.id)
                      if (!ranking || ranking.comparisons === 0) {
                        return <span className="text-text-disabled text-sm">—</span>
                      }
                      const winRate = ranking.win_rate !== null 
                        ? Math.round(ranking.win_rate * 100) 
                        : null
                      return (
                        <div className="flex items-center gap-2">
                          {ranking.rank !== null && (
                            <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                              ranking.rank === 1 
                                ? 'bg-status-success-muted text-status-success' 
                                : ranking.rank === 2
                                  ? 'bg-accent-muted text-accent'
                                  : 'bg-surface-2 text-text-secondary'
                            }`}>
                              #{ranking.rank}
                            </span>
                          )}
                          <span className="text-xs text-text-tertiary" title={`${ranking.wins}W-${ranking.losses}L-${ranking.ties}T`}>
                            {winRate !== null ? `${winRate}%` : '—'}
                          </span>
                        </div>
                      )
                    })()}
                  </Table.Cell>
                )}
                <Table.Cell className="text-text-tertiary text-sm">
                  {result.duration_ms ? `${(result.duration_ms / 1000).toFixed(1)}s` : '—'}
                </Table.Cell>
                <Table.Cell className="text-sm">
                  {result.lines_added !== null && result.lines_removed !== null ? (
                    <span>
                      <span className="text-status-success">+{result.lines_added}</span>
                      <span className="text-text-tertiary">/</span>
                      <span className="text-status-error">-{result.lines_removed}</span>
                    </span>
                  ) : (
                    <span className="text-text-disabled">—</span>
                  )}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {typeof result.files_changed === 'number' ? result.files_changed : '—'}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '—'}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {result.finished_at ? formatDate(result.finished_at) : '—'}
                </Table.Cell>
                <Table.Cell className="pr-6">
                  <div 
                    className="flex items-center justify-end"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <DropdownMenu trigger={<OverflowMenuTrigger />}>
                      <DropdownItem
                        onClick={() => rerunMutation.mutate(result.id)}
                        disabled={rerunMutation.isPending}
                      >
                        Rerun
                      </DropdownItem>
                    </DropdownMenu>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FullPageTableLayout>

      {/* Judge Drawer */}
      <JudgeDrawer
        open={showJudgeDrawer}
        onClose={() => setShowJudgeDrawer(false)}
        scenarioId={scenarioId}
        latestJudge={latestJudge}
        judges={judges || []}
        results={results}
        latestJudgeJudgements={latestJudgeJudgements}
        outdatedJudgements={outdatedJudgements}
        judgementCountByJudgeId={judgementCountByJudgeId}
        alignmentTask={alignmentTask}
        alignmentTaskFinal={alignmentTaskFinal}
        alignmentTaskId={alignmentTaskId}
        onTrainAlignment={() => trainAlignmentMutation.mutate()}
        isTrainingAlignment={trainAlignmentMutation.isPending}
        onRejudgeAllOutdated={handleRejudgeAllOutdated}
        isRejudging={isRejudging}
        rejudgeProgress={rejudgeProgress}
        onApplyAll={() => applyAllCompletedMutation.mutate()}
        isApplyingAll={applyAllCompletedMutation.isPending}
      />

      <ConfirmDialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={() => {
          deleteMutation.mutate()
          setShowDeleteDialog(false)
        }}
        title="Delete Scenario"
        description={`Are you sure you want to delete scenario ${scenario?.id}? This will permanently delete the scenario and all ${results.length} associated results.`}
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </>
  )
}

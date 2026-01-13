import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getResult, getResultPatch, getResultLogs, deleteResult, rerunResult, updateResultNotesAndQuality, listJudges, listJudgeJudgements, acceptJudgement, judgeResult, getActiveJudgementResultIds, getPairwiseRankings, listPairwisePreferences, ResultRanking, PairwisePreference } from '../api'
import GitHubDiffViewer from './GitHubDiffViewer'
import LogsViewer from './LogsViewer'
import StreamingLogs from './StreamingLogs'
import { PageLayout, PageHeader, Card, StatusBadge, Button, ConfirmDialog, EmptyState, DropdownMenu, DropdownItem, OverflowMenuTrigger, Textarea, Select } from './ui'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { AlertCircle } from 'lucide-react'

export default function ResultDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  
  const { data: result, isLoading: resultLoading } = useQuery({
    queryKey: ['result', id],
    queryFn: () => getResult(Number(id!)),
    // Poll every 2 seconds while result is running/queued
    refetchInterval: (query) => {
      const data = query.state.data
      const isActive = data?.status === 'running' || data?.status === 'queued'
      return isActive ? 2000 : false
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteResult(Number(id!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      navigate('/runs')
    },
  })

  const rerunMutation = useMutation({
    mutationFn: () => rerunResult(Number(id!)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      navigate(`/result/${data.result_id}`)
    },
  })

  const [notes, setNotes] = useState<string>('')
  const [quality, setQuality] = useState<number | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  // Initialize notes and quality from result when it loads
  useEffect(() => {
    if (result && !isEditing) {
      setNotes(result.notes || '')
      setQuality(result.quality || null)
    }
  }, [result?.id, isEditing])

  const updateNotesAndQualityMutation = useMutation({
    mutationFn: ({ notes, quality }: { notes: string | null, quality: number | null }) =>
      updateResultNotesAndQuality(Number(id!), notes || null, quality),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['result', id] })
      queryClient.invalidateQueries({ queryKey: ['result-judgements', id] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', result?.scenario_id] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
      setIsEditing(false)
    },
  })

  const handleSave = () => {
    updateNotesAndQualityMutation.mutate({
      notes: notes.trim() || null,
      quality: quality,
    })
  }

  const handleCancel = () => {
    setNotes(result?.notes || '')
    setQuality(result?.quality || null)
    setIsEditing(false)
  }

  const acceptJudgementMutation = useMutation({
    mutationFn: (judgementId: number) => acceptJudgement(judgementId),
    onSuccess: (updatedResult) => {
      queryClient.invalidateQueries({ queryKey: ['result', id] })
      queryClient.invalidateQueries({ queryKey: ['result-judgements', id] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', result?.scenario_id] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
      // Update local state
      setNotes(updatedResult.notes || '')
      setQuality(updatedResult.quality || null)
    },
  })

  const handleAcceptJudgement = () => {
    if (!judgement) return
    if (confirm('Accept this judgement? This will copy the judge\'s notes and quality score to your feedback.')) {
      acceptJudgementMutation.mutate(judgement.id)
    }
  }

  const isRunning = result?.status === 'running' || result?.status === 'queued'
  
  // Track streaming patch for live updates
  const [streamingPatch, setStreamingPatch] = useState<string>('')
  
  // Reset streaming patch when result changes or completes
  useEffect(() => {
    if (!isRunning) {
      setStreamingPatch('')
    }
  }, [isRunning, id])
  
  const handlePatchUpdate = useCallback((patch: string) => {
    setStreamingPatch(patch)
  }, [])

  const { data: patchData } = useQuery({
    queryKey: ['result-patch', id],
    queryFn: () => getResultPatch(Number(id!)),
    enabled: !!result && !isRunning,
  })
  
  // Use streaming patch when running, otherwise use fetched patch
  const currentPatch = isRunning ? streamingPatch : patchData?.patch

  const { data: logsData } = useQuery({
    queryKey: ['result-logs', id],
    queryFn: () => getResultLogs(Number(id!)),
    enabled: !!result && !isRunning,
  })

  // Get judge for this scenario
  const { data: judges } = useQuery({
    queryKey: ['judges', result?.scenario_id],
    queryFn: () => result ? listJudges(result.scenario_id) : [],
    enabled: !!result,
  })
  const latestJudge = judges?.[0]

  // Get all judgements for this result (from any judge)
  const { data: allJudgements } = useQuery({
    queryKey: ['result-judgements', id],
    queryFn: async () => {
      if (!result) return []
      // Get all judgements for this result
      const judgementsList: any[] = []
      if (judges) {
        for (const judge of judges) {
          const judgeJudgements = await listJudgeJudgements(judge.id)
          const judgement = judgeJudgements.find((j: any) => j.result_id === result.id)
          if (judgement) {
            judgementsList.push({
              ...judgement,
              judge,
              is_latest_judge: judge.id === latestJudge?.id,
            })
          }
        }
      }
      // Sort: latest judge first, then by created_at desc
      return judgementsList.sort((a, b) => {
        if (a.is_latest_judge && !b.is_latest_judge) return -1
        if (!a.is_latest_judge && b.is_latest_judge) return 1
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      })
    },
    enabled: !!result && !!judges,
  })
  
  // Use the most recent judgement (preferring latest judge)
  const judgement = allJudgements?.[0] || null

  // Track active judgement tasks
  const { data: activeJudgementResultIds = new Set<number>() } = useQuery({
    queryKey: ['active-judgement-results'],
    queryFn: getActiveJudgementResultIds,
    refetchInterval: 2000, // Poll every 2 seconds when there are active tasks
    select: (data) => data, // Keep as Set
  })

  // Get pairwise rankings for this scenario
  const { data: pairwiseRankingsData } = useQuery({
    queryKey: ['pairwise-rankings', result?.scenario_id],
    queryFn: () => result ? getPairwiseRankings(result.scenario_id) : null,
    enabled: !!result,
  })

  // Get pairwise preferences involving this result
  const { data: pairwisePreferencesData } = useQuery({
    queryKey: ['pairwise-preferences', 'result', id],
    queryFn: () => listPairwisePreferences(undefined, Number(id)),
    enabled: !!id,
  })

  // Get ranking for this specific result
  const resultRanking = useMemo((): ResultRanking | null => {
    if (!pairwiseRankingsData?.rankings || !result) return null
    return pairwiseRankingsData.rankings.find(r => r.result_id === result.id) || null
  }, [pairwiseRankingsData, result])

  // Get preferences involving this result
  const resultPreferences = useMemo((): PairwisePreference[] => {
    return pairwisePreferencesData?.preferences || []
  }, [pairwisePreferencesData])

  const hasPairwiseData = resultRanking !== null && resultRanking.comparisons > 0

  const judgeResultMutation = useMutation({
    mutationFn: () => {
      if (!latestJudge || !result) throw new Error('No judge or result available')
      return judgeResult(latestJudge.id, result.id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['result-judgements', id] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', result?.scenario_id] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['result', id] })
      queryClient.invalidateQueries({ queryKey: ['active-judgement-results'] })
    },
  })

  const isJudging = activeJudgementResultIds.has(Number(id!)) || judgeResultMutation.isPending

  const handleJudgeResult = () => {
    if (!latestJudge || !result) return
    const message = judgement && !judgement.is_latest_judge
      ? `Re-run the latest judge (${latestJudge.id}) on this result? This will replace the outdated judgement.`
      : `Run judge ${latestJudge.id} on this result?`
    if (confirm(message)) {
      judgeResultMutation.mutate()
    }
  }

  if (resultLoading) {
    return (
      <div>
        <PageHeader title={`Result ${id}`} />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  if (!result) {
    return (
      <div>
        <PageHeader title="Result Not Found" />
        <EmptyState title="Result not found" description="The result you're looking for doesn't exist." />
      </div>
    )
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  return (
    <PageLayout>
      <PageHeader
        title={`Result ${result.id}`}
        description={`${result.harness}:${result.provider}:${result.model}`}
        actions={
          <>
            <Button
              onClick={() => rerunMutation.mutate()}
              disabled={rerunMutation.isPending}
            >
              {rerunMutation.isPending ? 'Rerunning...' : 'Rerun'}
            </Button>
            <DropdownMenu trigger={<OverflowMenuTrigger />}>
              <DropdownItem danger onClick={() => setShowDeleteDialog(true)}>
                Delete result
              </DropdownItem>
            </DropdownMenu>
          </>
        }
      />

      <div className="mb-4">
        <Link to={`/scenario/${result.scenario_id}`} className="text-sm text-accent hover:text-accent-hover">
          ← Back to Scenario {result.scenario_id}
        </Link>
      </div>

      {/* Error Message Banner */}
      {result.error_message && (
        <div className="mb-6">
          <Card className="border-status-error/30 bg-status-error-muted">
            <Card.Content className="pt-4">
              <div className="flex items-start gap-3">
                <div className="text-status-error mt-0.5">
                  <AlertCircle className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-status-error mb-1">
                    {result.status === 'infra_failure' ? 'Infrastructure Failure' : 'Error'}
                  </h3>
                  <p className="text-sm text-text-secondary whitespace-pre-wrap font-mono">
                    {result.error_message}
                  </p>
                </div>
              </div>
            </Card.Content>
          </Card>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <Card.Header>
            <Card.Title>Status & Timing</Card.Title>
          </Card.Header>
          <Card.Content>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Status</dt>
                <dd><StatusBadge status={result.status} isStale={result.is_stale} /></dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Driver</dt>
                <dd className="text-text-secondary font-mono text-xs">{result.driver || 'local'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Queued</dt>
                <dd className="text-text-secondary">{formatDate(result.created_at)}</dd>
              </div>
              {result.started_at && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Started</dt>
                  <dd className="text-text-secondary">{formatDate(result.started_at)}</dd>
                </div>
              )}
              {result.finished_at && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Finished</dt>
                  <dd className="text-text-secondary">{formatDate(result.finished_at)}</dd>
                </div>
              )}
              {result.timeout_seconds && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Timeout</dt>
                  <dd className="text-text-secondary">{Math.floor(result.timeout_seconds / 60)}m {result.timeout_seconds % 60}s</dd>
                </div>
              )}
              {result.duration_ms !== null && result.duration_ms !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Duration</dt>
                  <dd className="text-text-primary font-medium">{(result.duration_ms / 1000).toFixed(1)}s</dd>
                </div>
              )}
            </dl>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Code Changes</Card.Title>
          </Card.Header>
          <Card.Content>
            <dl className="space-y-2 text-sm">
              {result.lines_added !== null && result.lines_added !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Lines Added</dt>
                  <dd className="text-status-success font-medium">+{result.lines_added}</dd>
                </div>
              )}
              {result.lines_removed !== null && result.lines_removed !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Lines Removed</dt>
                  <dd className="text-status-error font-medium">-{result.lines_removed}</dd>
                </div>
              )}
              {result.files_changed !== null && result.files_changed !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Files Changed</dt>
                  <dd className="text-text-primary font-medium">{result.files_changed}</dd>
                </div>
              )}
              {(!result.lines_added && !result.lines_removed && result.files_changed === null) && (
                <p className="text-text-disabled italic">No changes detected</p>
              )}
            </dl>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Usage & Cost</Card.Title>
          </Card.Header>
          <Card.Content>
            <dl className="space-y-2 text-sm">
              {result.tokens_used ? (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Tokens</dt>
                  <dd className="text-text-secondary">{result.tokens_used.toLocaleString()}</dd>
                </div>
              ) : (
                <p className="text-text-disabled italic">No token usage recorded</p>
              )}
              {result.cost_usd ? (
                <div className="flex justify-between">
                  <dt className="text-text-tertiary">Cost</dt>
                  <dd className="text-text-primary font-medium">${result.cost_usd.toFixed(4)}</dd>
                </div>
              ) : (
                <p className="text-text-disabled italic">No cost recorded</p>
              )}
            </dl>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Executor</Card.Title>
          </Card.Header>
          <Card.Content>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Harness</dt>
                <dd className="text-text-secondary font-mono">{result.harness}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Provider</dt>
                <dd className="text-text-secondary font-mono">{result.provider}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-tertiary">Model</dt>
                <dd className="text-text-secondary font-mono">{result.model}</dd>
              </div>
            </dl>
          </Card.Content>
        </Card>
      </div>

      {/* Judge Judgement Section */}
      {latestJudge && result && result.status === 'completed' && !judgement && (
        <div className="mb-6">
          <Card>
            <Card.Header>
              <Card.Title>LLM Judge</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <p className="text-sm text-text-secondary">
                  No judgement yet. Click the button below to run the judge on this result.
                </p>
                <Button
                  onClick={handleJudgeResult}
                  disabled={isJudging}
                >
                  {isJudging ? 'Judging...' : 'Run Judge'}
                </Button>
                {judgeResultMutation.isError && (
                  <div className="text-sm text-status-error">
                    Failed to judge: {judgeResultMutation.error?.message || 'Unknown error'}
                  </div>
                )}
              </div>
            </Card.Content>
          </Card>
        </div>
      )}

      {judgement && (
        <div className="mb-6">
          <Card className={`border-accent/30 ${judgement.is_latest_judge ? '' : 'border-status-warning/30'}`}>
            <Card.Header>
              <div className="flex items-center justify-between">
                <Card.Title>LLM Judge Judgement</Card.Title>
                <div className="flex items-center gap-2">
                  {!judgement.is_latest_judge && (
                    <>
                      <span className="text-xs px-2 py-1 rounded bg-status-warning-muted text-status-warning">
                        Outdated
                      </span>
                      {latestJudge && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleJudgeResult}
                          disabled={judgeResultMutation.isPending}
                        >
                          {judgeResultMutation.isPending ? 'Re-running...' : 'Re-run Judge'}
                        </Button>
                      )}
                    </>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleAcceptJudgement}
                    disabled={acceptJudgementMutation.isPending}
                  >
                    {acceptJudgementMutation.isPending ? 'Accepting...' : 'Accept'}
                  </Button>
                </div>
              </div>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-text-tertiary mb-1">Judge Alignment</div>
                    <div className="text-base font-medium">
                      {judgement.judge?.alignment_score !== null && judgement.judge?.alignment_score !== undefined
                        ? judgement.judge.alignment_score.toFixed(3)
                        : 'Not evaluated'}
                    </div>
                    {!judgement.is_latest_judge && (
                      <div className="text-xs text-text-tertiary mt-1">
                        Judge {judgement.judge_id} (latest: {latestJudge?.id})
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="text-sm text-text-tertiary mb-1">Judge Quality</div>
                    <div className="text-base font-medium">
                      {judgement.quality !== null && judgement.quality !== undefined ? (
                        <>
                          {judgement.quality === 4 && 'Perfect (4)'}
                          {judgement.quality === 3 && 'Good (3)'}
                          {judgement.quality === 2 && 'Workable (2)'}
                          {judgement.quality === 1 && 'Bad (1)'}
                        </>
                      ) : (
                        <span className="text-text-disabled">No score</span>
                      )}
                    </div>
                  </div>
                </div>
                {judgement.notes && (
                  <div>
                    <div className="text-sm text-text-tertiary mb-1">Judge Notes</div>
                    <div className="text-sm text-text-primary whitespace-pre-wrap">{judgement.notes}</div>
                  </div>
                )}
                {!judgement.is_latest_judge && latestJudge && (
                  <div className="pt-2 border-t border-border">
                    <div className="text-xs text-text-tertiary">
                      This judgement was made by an older judge version. Consider re-running the judge to get an updated assessment.
                    </div>
                  </div>
                )}
              </div>
            </Card.Content>
          </Card>
        </div>
      )}

      {/* Notes & Quality Section */}
      <div className="mb-6">
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <Card.Title>Human Notes & Quality</Card.Title>
              {!isEditing && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </Button>
              )}
            </div>
          </Card.Header>
          <Card.Content>
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-2">
                    Quality Score
                  </label>
                  <Select
                    value={quality?.toString() || ''}
                    onChange={(e) => setQuality(e.target.value ? parseInt(e.target.value) : null)}
                    options={[
                      { value: '', label: 'No score' },
                      { value: '4', label: 'Perfect (4)' },
                      { value: '3', label: 'Good (3)' },
                      { value: '2', label: 'Workable (2)' },
                      { value: '1', label: 'Bad (1)' },
                    ]}
                  />
                </div>
                <div>
                  <Textarea
                    label="Notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add notes about this run..."
                    rows={6}
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCancel}
                    disabled={updateNotesAndQualityMutation.isPending}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={updateNotesAndQualityMutation.isPending}
                  >
                    {updateNotesAndQualityMutation.isPending ? 'Saving...' : 'Save'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {result?.quality !== null && result?.quality !== undefined && (
                  <div>
                    <div className="text-sm text-text-tertiary mb-1">Quality Score</div>
                    <div className="text-base font-medium">
                      {result.quality === 4 && 'Perfect (4)'}
                      {result.quality === 3 && 'Good (3)'}
                      {result.quality === 2 && 'Workable (2)'}
                      {result.quality === 1 && 'Bad (1)'}
                    </div>
                  </div>
                )}
                {result?.notes ? (
                  <div>
                    <div className="text-sm text-text-tertiary mb-1">Notes</div>
                    <div className="text-sm text-text-primary whitespace-pre-wrap">{result.notes}</div>
                  </div>
                ) : (
                  <div className="text-sm text-text-disabled italic">No notes added yet</div>
                )}
              </div>
            )}
          </Card.Content>
        </Card>
      </div>

      {/* Pairwise Comparison Section */}
      {hasPairwiseData && resultRanking && (
        <div className="mb-6">
          <Card>
            <Card.Header>
              <Card.Title>Pairwise Comparisons</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                {/* Ranking summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-surface-2 rounded-lg p-3">
                    <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Rank</div>
                    <div className={`text-2xl font-bold ${
                      resultRanking.rank === 1 
                        ? 'text-status-success' 
                        : resultRanking.rank === 2
                          ? 'text-accent'
                          : 'text-text-primary'
                    }`}>
                      {resultRanking.rank !== null ? `#${resultRanking.rank}` : '—'}
                    </div>
                  </div>
                  <div className="bg-surface-2 rounded-lg p-3">
                    <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Win Rate</div>
                    <div className="text-2xl font-bold text-text-primary">
                      {resultRanking.win_rate !== null 
                        ? `${Math.round(resultRanking.win_rate * 100)}%` 
                        : '—'}
                    </div>
                  </div>
                  <div className="bg-surface-2 rounded-lg p-3">
                    <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Record</div>
                    <div className="text-lg font-medium">
                      <span className="text-status-success">{resultRanking.wins}W</span>
                      <span className="text-text-tertiary mx-1">-</span>
                      <span className="text-status-error">{resultRanking.losses}L</span>
                      <span className="text-text-tertiary mx-1">-</span>
                      <span className="text-text-secondary">{resultRanking.ties}T</span>
                    </div>
                  </div>
                  <div className="bg-surface-2 rounded-lg p-3">
                    <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-1">Comparisons</div>
                    <div className="text-2xl font-bold text-text-primary">
                      {resultRanking.comparisons}
                    </div>
                  </div>
                </div>

                {/* Recent comparisons */}
                {resultPreferences.length > 0 && (
                  <div>
                    <div className="text-text-tertiary text-[10px] uppercase tracking-wide mb-2">Recent Comparisons</div>
                    <div className="space-y-2">
                      {resultPreferences.slice(0, 5).map((pref) => {
                        const isResultA = pref.result_a_id === result?.id
                        const opponentId = isResultA ? pref.result_b_id : pref.result_a_id
                        let outcome: 'win' | 'loss' | 'tie'
                        if (pref.preference === 'tie' || pref.preference === 'both_good' || pref.preference === 'both_bad') {
                          outcome = 'tie'
                        } else if (
                          (isResultA && pref.preference === 'a_better') ||
                          (!isResultA && pref.preference === 'b_better')
                        ) {
                          outcome = 'win'
                        } else {
                          outcome = 'loss'
                        }
                        return (
                          <div 
                            key={pref.id} 
                            className="flex items-center justify-between px-3 py-2 bg-surface-2 rounded-lg text-sm"
                          >
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                                outcome === 'win' 
                                  ? 'bg-status-success-muted text-status-success'
                                  : outcome === 'loss'
                                    ? 'bg-status-error-muted text-status-error'
                                    : 'bg-surface-3 text-text-secondary'
                              }`}>
                                {outcome === 'win' ? 'WIN' : outcome === 'loss' ? 'LOSS' : 'TIE'}
                              </span>
                              <span className="text-text-secondary">
                                vs{' '}
                                <Link 
                                  to={`/result/${opponentId}`}
                                  className="text-accent hover:text-accent-hover"
                                >
                                  Result #{opponentId}
                                </Link>
                              </span>
                            </div>
                            <span className="text-text-tertiary text-xs">
                              {new Date(pref.created_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                              })}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                    {resultPreferences.length > 5 && (
                      <div className="mt-2 text-xs text-text-tertiary">
                        +{resultPreferences.length - 5} more comparisons
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card.Content>
          </Card>
        </div>
      )}

      {/* Patch Section */}
      {(currentPatch || isRunning) && (
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-3">
            <h2 className="text-lg font-semibold text-text-primary">Patch</h2>
            {isRunning && (
              <span className="flex items-center gap-1.5 px-2 py-1 bg-surface-2 rounded text-xs text-accent">
                <span className="w-1.5 h-1.5 bg-accent rounded-full animate-pulse" />
                Live
              </span>
            )}
          </div>
          {currentPatch ? (
            <GitHubDiffViewer patch={currentPatch} maxHeight="600px" />
          ) : (
            <div className="border border-border rounded-lg p-8 text-text-tertiary text-sm text-center">
              Waiting for file changes...
            </div>
          )}
        </div>
      )}

      {/* Logs Section */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-text-primary mb-3">Output</h2>
        {isRunning ? (
          <StreamingLogs
            resultId={result.id}
            onStatusChange={(status) => {
              // Invalidate queries when status changes to refresh UI
              if (status === 'completed' || status === 'failed' || status === 'infra_failure') {
                queryClient.invalidateQueries({ queryKey: ['result', id] })
                queryClient.invalidateQueries({ queryKey: ['result-logs', id] })
                queryClient.invalidateQueries({ queryKey: ['result-patch', id] })
              }
            }}
            onPatchUpdate={handlePatchUpdate}
            onComplete={() => {
              queryClient.invalidateQueries({ queryKey: ['result', id] })
              queryClient.invalidateQueries({ queryKey: ['result-logs', id] })
              queryClient.invalidateQueries({ queryKey: ['result-patch', id] })
            }}
          />
        ) : logsData ? (
          <>
            {logsData.stdout && (
              <div className="mb-4">
                <LogsViewer 
                  logs={logsData.stdout} 
                  title="stdout" 
                  defaultMode="chat"
                  maxHeight="500px"
                />
              </div>
            )}
            {logsData.stderr && logsData.stderr.trim() && (
              <div>
                <LogsViewer 
                  logs={logsData.stderr} 
                  title="stderr" 
                  defaultMode="raw"
                  maxHeight="300px"
                />
              </div>
            )}
            {!logsData.stdout && !logsData.stderr?.trim() && (
              <EmptyState title="No output recorded" description="This run did not produce any output." />
            )}
          </>
        ) : (
          <div className="text-center py-8 text-text-tertiary">Loading logs...</div>
        )}
      </div>

      <ConfirmDialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={() => {
          deleteMutation.mutate()
          setShowDeleteDialog(false)
        }}
        title="Delete Result"
        description={`Are you sure you want to delete result ${result.id}? This action cannot be undone.`}
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </PageLayout>
  )
}

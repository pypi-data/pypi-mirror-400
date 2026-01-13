import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { listScenarios, deleteScenario, archiveScenario } from '../api'
import { FullPageTableLayout, Table, EmptyState, Button, ConfirmDialog, DropdownMenu, DropdownItem, OverflowMenuTrigger } from './ui'
import { useState } from 'react'
import { Github, Folder, Archive, ArchiveRestore, Eye, EyeOff } from 'lucide-react'

export default function Scenarios() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; resultCount: number } | null>(null)
  const [showArchived, setShowArchived] = useState(false)
  
  const { data, isLoading } = useQuery({
    queryKey: ['scenarios', { includeArchived: showArchived }],
    queryFn: () => listScenarios({ includeArchived: showArchived }),
    refetchInterval: (query) => {
      const data = query.state.data
      const hasRunning = Object.values(data?.results_by_scenario || {}).flat().some(
        (r: any) => r.status === 'running' || r.status === 'queued'
      )
      return hasRunning ? 3000 : false
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteScenario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      setDeleteTarget(null)
    },
  })

  const archiveMutation = useMutation({
    mutationFn: ({ id, archived }: { id: number; archived: boolean }) => archiveScenario(id, archived),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      queryClient.invalidateQueries({ queryKey: ['global-analytics'] })
    },
  })

  const formatRelativeTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const getCodeRefDisplay = (scenario: any) => {
    if (!scenario.code_ref) return null
    if (scenario.code_type === 'github') {
      const ref = scenario.code_ref
      return {
        type: 'github',
        display: `${ref.owner}/${ref.repo}`,
        full: `${ref.owner}/${ref.repo}@${ref.commit_sha || ref.branch || 'main'}`,
      }
    } else if (scenario.code_type === 'local') {
      const path = scenario.code_ref.path
      const parts = path.split('/')
      return {
        type: 'local',
        display: parts.length > 2 ? `.../${parts.slice(-2).join('/')}` : path,
        full: path,
      }
    }
    return null
  }

  const getResultStats = (results: any[]) => {
    const completed = results.filter(r => r.status === 'completed').length
    const failed = results.filter(r => r.status === 'failed' || r.status === 'infra_failure').length
    const timeout = results.filter(r => r.status === 'timeout').length
    const running = results.filter(r => (r.status === 'running' || r.status === 'queued') && !r.is_stale).length
    
    // Calculate average quality from completed results that have quality scores
    const qualityScores = results
      .filter(r => r.status === 'completed' && r.quality !== null && r.quality !== undefined)
      .map(r => r.quality)
    const avgQuality = qualityScores.length > 0 
      ? qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length 
      : null
    
    return { total: results.length, completed, failed, timeout, running, avgQuality, qualityCount: qualityScores.length }
  }

  const scenarios = data?.scenarios || []
  const resultsByScenario = data?.results_by_scenario || {}
  const judgesByScenario = data?.judges_by_scenario || {}

  const header = (
    <FullPageTableLayout.Header
      title="Scenarios"
      count={scenarios.length}
      countLabel={scenarios.length === 1 ? 'scenario' : 'scenarios'}
      actions={
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowArchived(!showArchived)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
              showArchived 
                ? 'bg-accent/10 text-accent hover:bg-accent/20' 
                : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-2'
            }`}
            title={showArchived ? 'Hide archived scenarios' : 'Show archived scenarios'}
          >
            {showArchived ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            {showArchived ? 'Showing archived' : 'Show archived'}
          </button>
          <Link to="/run/create">
            <Button>New Scenario</Button>
          </Link>
        </div>
      }
    />
  )

  if (isLoading) {
    return (
      <FullPageTableLayout header={header} isEmpty>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </FullPageTableLayout>
    )
  }

  return (
    <>
      <FullPageTableLayout
        header={header}
        isEmpty={scenarios.length === 0}
        emptyState={
          <EmptyState
            title="No scenarios yet"
            description="Create your first scenario to get started comparing AI agents."
            action={
              <Link to="/run/create">
                <Button>Create Scenario</Button>
              </Link>
            }
          />
        }
      >
        <Table fullPage maxHeight="full">
          <Table.Header>
            <tr>
              <Table.Head className="w-[45%] pl-6">Scenario</Table.Head>
              <Table.Head>Code</Table.Head>
              <Table.Head>Results</Table.Head>
              <Table.Head>Quality</Table.Head>
              <Table.Head className="w-[80px] pr-6"></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {scenarios.map((scenario) => {
              const results = resultsByScenario[scenario.id] || []
              const stats = getResultStats(results)
              const codeRef = getCodeRefDisplay(scenario)
              const judge = judgesByScenario[scenario.id]

              return (
                <Table.Row 
                  key={scenario.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/scenario/${scenario.id}`)}
                >
                  {/* Scenario info */}
                  <Table.Cell className="pl-6">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${scenario.archived ? 'text-text-tertiary' : 'text-text-primary'}`}>
                          Scenario #{scenario.id}
                        </span>
                        {scenario.archived && (
                          <span 
                            className="text-[10px] px-1.5 py-0.5 rounded bg-surface-3 text-text-tertiary font-medium flex items-center gap-1"
                            title="This scenario is archived"
                          >
                            <Archive className="w-3 h-3" /> Archived
                          </span>
                        )}
                        {judge && (
                          <span 
                            className="text-[10px] px-1.5 py-0.5 rounded bg-accent/10 text-accent font-medium"
                            title={`Judge configured${judge.alignment_score ? ` (alignment: ${judge.alignment_score.toFixed(2)})` : ''}`}
                          >
                            ⚖ Judge
                          </span>
                        )}
                        <span className="text-xs text-text-disabled">
                          {formatRelativeTime(scenario.created_at)}
                        </span>
                      </div>
                      <div className={`text-sm line-clamp-2 ${scenario.archived ? 'text-text-tertiary' : 'text-text-secondary'}`}>
                        {scenario.prompt}
                      </div>
                    </div>
                  </Table.Cell>

                  {/* Code reference */}
                  <Table.Cell>
                    {codeRef ? (
                      <div className="flex items-center gap-1.5">
                        {codeRef.type === 'github' && (
                          <Github className="w-3.5 h-3.5 text-text-tertiary shrink-0" />
                        )}
                        {codeRef.type === 'local' && (
                          <Folder className="w-3.5 h-3.5 text-text-tertiary shrink-0" />
                        )}
                        <span
                          className="text-xs font-mono text-text-tertiary truncate max-w-[150px]"
                          title={codeRef.full}
                        >
                          {codeRef.display}
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-text-disabled">Empty</span>
                    )}
                  </Table.Cell>

                  {/* Results summary */}
                  <Table.Cell>
                    {stats.total === 0 ? (
                      <span className="text-xs text-text-disabled">No runs</span>
                    ) : (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-text-secondary font-medium">{stats.total}</span>
                        {stats.completed > 0 && (
                          <span className="text-status-success">✓ {stats.completed}</span>
                        )}
                        {stats.failed > 0 && (
                          <span className="text-status-error">✗ {stats.failed}</span>
                        )}
                        {stats.timeout > 0 && (
                          <span className="text-status-warning">⏱ {stats.timeout}</span>
                        )}
                        {stats.running > 0 && (
                          <span className="text-status-info flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-status-info animate-pulse" />
                            {stats.running}
                          </span>
                        )}
                      </div>
                    )}
                  </Table.Cell>

                  {/* Quality */}
                  <Table.Cell>
                    {stats.avgQuality !== null ? (
                      <div className="flex items-center gap-1.5">
                        <span className={`text-xs font-medium ${
                          stats.avgQuality >= 3.5 ? 'text-emerald-500' :
                          stats.avgQuality >= 2.5 ? 'text-sky-500' :
                          stats.avgQuality >= 1.5 ? 'text-amber-500' : 'text-rose-500'
                        }`}>
                          {stats.avgQuality >= 3.5 ? '★' :
                           stats.avgQuality >= 2.5 ? '●' :
                           stats.avgQuality >= 1.5 ? '◐' : '✗'} {stats.avgQuality.toFixed(1)}
                        </span>
                        <span className="text-[10px] text-text-disabled">
                          ({stats.qualityCount})
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-text-disabled">—</span>
                    )}
                  </Table.Cell>

                  {/* Actions */}
                  <Table.Cell className="pr-6">
                    <div 
                      className="flex items-center justify-end"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <DropdownMenu trigger={<OverflowMenuTrigger />}>
                        <DropdownItem
                          onClick={() => archiveMutation.mutate({ id: scenario.id, archived: !scenario.archived })}
                        >
                          <span className="flex items-center gap-2">
                            {scenario.archived ? (
                              <>
                                <ArchiveRestore className="w-3.5 h-3.5" />
                                Unarchive scenario
                              </>
                            ) : (
                              <>
                                <Archive className="w-3.5 h-3.5" />
                                Archive scenario
                              </>
                            )}
                          </span>
                        </DropdownItem>
                        <DropdownItem
                          danger
                          onClick={() => setDeleteTarget({ id: scenario.id, resultCount: stats.total })}
                        >
                          Delete scenario
                        </DropdownItem>
                      </DropdownMenu>
                    </div>
                  </Table.Cell>
                </Table.Row>
              )
            })}
          </Table.Body>
        </Table>
      </FullPageTableLayout>

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget.id)
          }
        }}
        title="Delete Scenario"
        description={
          deleteTarget
            ? `Are you sure you want to delete scenario ${deleteTarget.id}? This will permanently delete the scenario and all ${deleteTarget.resultCount} associated results.`
            : ''
        }
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </>
  )
}

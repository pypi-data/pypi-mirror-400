import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { getResult, getResultPatch, getResultLogs, Result, listScenarioJudgements, Judgement, getActiveJudgementResultIds } from '../api'
import GitHubDiffViewer from './GitHubDiffViewer'
import LogsViewer from './LogsViewer'
import StreamingLogs from './StreamingLogs'
import { PageLayout, PageHeader, Card, Table, StatusBadge, Button, EmptyState, Select, QualityBadge } from './ui'
import { useMemo, useState } from 'react'
import { QualityTradeoffPlot, type QualityTradeoffPoint } from './QualityTradeoffPlot'
import { splitPatchByFile } from '../lib/diffUtils'
import { FileText, File, Columns } from 'lucide-react'

// Scatter Plot component for time vs score tradeoff
interface ScatterPlotProps {
  results: Result[]
  judgementsByResult: Record<number, Judgement | null>
  onPointClick?: (resultId: number) => void
  xMetric?: 'time' | 'cost'
}

function TimeVsScoreChart({ results, judgementsByResult, onPointClick, xMetric = 'time' }: ScatterPlotProps) {
  const safeJudgements = judgementsByResult || {}

  // Default quality value for null scores (2.5 = middle of 1-4 scale)
  const DEFAULT_QUALITY = 2.5

  const points: QualityTradeoffPoint[] = useMemo(() => {
    return results
      .filter((r) => r.status === 'completed')
      .map((r) => {
        // Get quality score - prefer human, fall back to judge
        let quality: number | undefined = r.quality ?? undefined
        let hasQuality = true
        if (quality === undefined) {
          const judgement = safeJudgements[r.id]
          quality = judgement?.quality ?? undefined
          if (quality === undefined) {
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
  }, [results, safeJudgements])

  return (
    <QualityTradeoffPlot
      points={points}
      xMetric={xMetric}
      emptyText="No completed results yet"
      onPointClick={(p) => onPointClick?.(Number(p.key))}
    />
  )
}

// Extract file contents from a patch (for baseline comparison)
function extractFileContents(patch: string): Record<string, string> {
  const files = splitPatchByFile(patch)
  const contents: Record<string, string> = {}
  for (const file of files) {
    contents[file.path] = file.content
  }
  return contents
}

// Compute a simple diff between two patches (for baseline comparison)
function computePatchDiff(baselinePatch: string, resultPatch: string): string {
  const baselineFiles = extractFileContents(baselinePatch)
  const resultFiles = extractFileContents(resultPatch)
  
  // Collect all file paths
  const allFiles = new Set([...Object.keys(baselineFiles), ...Object.keys(resultFiles)])
  
  const diffLines: string[] = []
  
  for (const filePath of Array.from(allFiles).sort()) {
    const baselineContent = baselineFiles[filePath] || ''
    const resultContent = resultFiles[filePath] || ''
    
    if (baselineContent === resultContent) {
      continue // No changes
    }
    
    // File header
    diffLines.push(`diff --git a/${filePath} b/${filePath}`)
    diffLines.push(`--- a/${filePath}`)
    diffLines.push(`+++ b/${filePath}`)
    
    // Simple line-by-line diff
    const baselineLines = baselineContent.split('\n')
    const resultLines = resultContent.split('\n')
    
    // Find differences
    const maxLen = Math.max(baselineLines.length, resultLines.length)
    for (let i = 0; i < maxLen; i++) {
      const baselineLine = baselineLines[i]
      const resultLine = resultLines[i]
      
      if (baselineLine === undefined) {
        diffLines.push(`+${resultLine}`)
      } else if (resultLine === undefined) {
        diffLines.push(`-${baselineLine}`)
      } else if (baselineLine !== resultLine) {
        diffLines.push(`-${baselineLine}`)
        diffLines.push(`+${resultLine}`)
      } else {
        diffLines.push(` ${baselineLine}`)
      }
    }
  }
  
  return diffLines.join('\n')
}

function FileDiffViewer({ patch }: { patch: string }) {
  const files = splitPatchByFile(patch)
  const [selectedFile, setSelectedFile] = useState<string | null>(
    files.length > 0 ? files[0].path : null
  )

  if (files.length === 0) {
    return <GitHubDiffViewer patch={patch} />
  }

  if (files.length === 1) {
    return <GitHubDiffViewer patch={files[0].content} />
  }

  const selectedFileContent =
    files.find((f) => f.path === selectedFile)?.content || files[0].content

  return (
    <div className="space-y-2">
      {/* File tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {files.map((file) => (
          <button
            key={file.path}
            onClick={() => setSelectedFile(file.path)}
            className={`px-3 py-1.5 text-sm rounded whitespace-nowrap transition-colors ${
              selectedFile === file.path
                ? 'bg-accent text-on-accent font-medium'
                : 'bg-surface-2 text-text-secondary hover:bg-surface-3 hover:text-text-primary'
            }`}
          >
            {file.path.split('/').pop()}
          </button>
        ))}
      </div>
      {/* Diff content */}
      <GitHubDiffViewer patch={selectedFileContent} />
    </div>
  )
}

function ComparisonTable({ results, judgementsByResult }: { results: Result[]; judgementsByResult: Record<number, Judgement | null> }) {
  // Ensure judgementsByResult is never undefined
  const safeJudgements = judgementsByResult || {}
  
  return (
    <div>
      {/* <h2 className="text-lg font-semibold text-text-primary mb-3">Comparison</h2> */}
      <Table>
        <Table.Header>
          <tr>
            <Table.Head>Executor</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head className="text-center">Human</Table.Head>
            <Table.Head className="text-center">Judge</Table.Head>
            <Table.Head className="text-right">Duration</Table.Head>
            <Table.Head className="text-right">+/-</Table.Head>
            <Table.Head className="text-right">Files</Table.Head>
            <Table.Head className="text-right">Cost</Table.Head>
          </tr>
        </Table.Header>
        <Table.Body>
          {results.map((result) => {
            const judgement = safeJudgements[result.id]
            return (
              <Table.Row key={result.id}>
                <Table.Cell mono className="text-xs">
                  <Link to={`/result/${result.id}`} className="text-accent hover:text-accent-hover">
                    {result.harness}:{result.provider}:{result.model}
                  </Link>
                </Table.Cell>
                <Table.Cell>
                  <StatusBadge status={result.status} isStale={result.is_stale} />
                </Table.Cell>
                <Table.Cell className="text-center">
                  <QualityBadge quality={result.quality as 1 | 2 | 3 | 4 | null | undefined} />
                </Table.Cell>
                <Table.Cell className="text-center">
                  {judgement ? (
                    <QualityBadge quality={judgement.quality as 1 | 2 | 3 | 4 | null | undefined} />
                  ) : (
                    <span className="text-text-disabled text-xs">—</span>
                  )}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.duration_ms ? `${(result.duration_ms / 1000).toFixed(1)}s` : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-xs">
                  {result.lines_added !== null && result.lines_added !== undefined ? (
                    <span>
                      <span className="text-status-success">+{result.lines_added}</span>
                      <span className="text-text-tertiary">/</span>
                      <span className="text-status-error">-{result.lines_removed || 0}</span>
                    </span>
                  ) : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.files_changed !== null && result.files_changed !== undefined ? result.files_changed : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '—'}
                </Table.Cell>
              </Table.Row>
            )
          })}
        </Table.Body>
      </Table>
    </div>
  )
}

type ViewMode = 'logs' | 'split' | 'files'

function ViewModeSwitcher({ value, onChange }: { value: ViewMode; onChange: (mode: ViewMode) => void }) {
  const options: { value: ViewMode; label: string; icon: React.ReactNode }[] = [
    {
      value: 'logs',
      label: 'Logs',
      icon: <FileText className="w-3.5 h-3.5" />,
    },
    {
      value: 'split',
      label: 'Split',
      icon: <Columns className="w-3.5 h-3.5" />,
    },
    {
      value: 'files',
      label: 'Files',
      icon: <File className="w-3.5 h-3.5" />,
    },
  ]

  return (
    <div className="inline-flex items-center bg-surface border border-border rounded-lg p-1 gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150
            ${value === option.value
              ? 'bg-accent text-on-accent shadow-sm'
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-2'
            }
          `}
        >
          {option.icon}
          <span>{option.label}</span>
        </button>
      ))}
    </div>
  )
}

export default function CompareResults() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const ids = useMemo(() => searchParams.get('ids')?.split(',').map(Number).filter(Boolean) || [], [searchParams])
  const scenarioId = searchParams.get('scenario')
  
  const [baselineId, setBaselineId] = useState<number | null>(ids.length > 0 ? ids[0] : null)
  const [groupBy, setGroupBy] = useState<'executor' | 'file'>('executor')
  const [compareTo, setCompareTo] = useState<'parent' | 'baseline'>('parent')
  const [viewMode, setViewMode] = useState<ViewMode>('split')
  const [timeVsQualityX, setTimeVsQualityX] = useState<'time' | 'cost'>('time')

  // Fetch all results and patches
  const resultsQueries = useQueries({
    queries: ids.map((id) => ({
      queryKey: ['result', id],
      queryFn: () => getResult(id),
      // Poll every 2 seconds while result is running/queued
      refetchInterval: (query: any) => {
        const data = query.state.data
        const isActive = data?.status === 'running' || data?.status === 'queued'
        return isActive ? 2000 : false
      },
    })),
  })

  const patchQueries = useQueries({
    queries: ids.map((id, idx) => {
      const result = resultsQueries[idx]?.data
      const isRunning = result?.status === 'running' || result?.status === 'queued'
      return {
        queryKey: ['result-patch', id],
        queryFn: () => getResultPatch(id),
        enabled: !!result && !isRunning,
      }
    }),
  })

  const results = resultsQueries.map((q) => q.data).filter((r): r is Result => !!r)
  const patches = patchQueries.map((q) => q.data?.patch || '')
  
  const isLoading = ids.length >= 2 && results.length !== ids.length
  const hasEnoughIds = ids.length >= 2

  // Get scenario ID from URL or from results
  const effectiveScenarioId = scenarioId ? Number(scenarioId) : results[0]?.scenario_id

  // Track active judgement tasks
  const { data: activeJudgementResultIdsSet = new Set<number>() } = useQuery({
    queryKey: ['active-judgement-results'],
    queryFn: getActiveJudgementResultIds,
    refetchInterval: 2000, // Poll every 2 seconds when there are active tasks
    select: (data) => data, // Keep as Set
  })
  const activeJudgementResultIds = activeJudgementResultIdsSet as Set<number>

  // Fetch judgements for the scenario
  const { data: scenarioJudgements } = useQuery({
    queryKey: ['scenario-judgements', effectiveScenarioId],
    queryFn: () => listScenarioJudgements(effectiveScenarioId!),
    enabled: !!effectiveScenarioId && results.length > 0,
    refetchInterval: () => {
      // Poll if there are active judgement tasks for any of the results
      const hasActiveJudgements = ids.some(id => activeJudgementResultIds.has(id))
      return hasActiveJudgements ? 2000 : false
    },
  })

  // Map judgements to results (latest judgement per result)
  const judgementsByResult = useMemo(() => {
    const map: Record<number, Judgement | null> = {}
    for (const id of ids) {
      map[id] = null
    }
    if (scenarioJudgements) {
      // Group by result_id, take the latest one
      const byResultId = new Map<number, Judgement[]>()
      for (const j of scenarioJudgements) {
        if (!byResultId.has(j.result_id)) {
          byResultId.set(j.result_id, [])
        }
        byResultId.get(j.result_id)!.push(j)
      }
      // For each result, take the latest judgement
      for (const [resultId, judgements] of byResultId) {
        if (judgements.length > 0) {
          const sorted = judgements.sort((a, b) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )
          map[resultId] = sorted[0]
        }
      }
    }
    return map
  }, [scenarioJudgements, ids])

  const baselinePatch = baselineId ? patches[results.findIndex((r) => r.id === baselineId)] || '' : ''

  // Compute display patches based on compareTo mode
  // Must be called unconditionally (before any early returns)
  const displayPatches = useMemo(() => {
    if (!hasEnoughIds || isLoading) return []
    return patches.map((patch, idx) => {
      const result = results[idx]
      if (!result) return patch
      
      const isBaseline = baselineId === result.id
      
      if (compareTo === 'baseline' && baselineId && !isBaseline && baselinePatch) {
        // Compare against baseline - compute diff
        return computePatchDiff(baselinePatch, patch)
      }
      
      // Default: show parent patch (original patch from result)
      return patch
    })
  }, [patches, results, baselineId, baselinePatch, compareTo, hasEnoughIds, isLoading])

  // Group files across all results for "Group by File" mode
  // Must be called unconditionally (before any early returns)
  const filesByPath = useMemo(() => {
    const fileMap = new Map<string, Array<{ result: Result; patch: string; fileContent: string }>>()
    
    if (!hasEnoughIds || isLoading) return fileMap
    
    results.forEach((result, idx) => {
      // Skip baseline when comparing to baseline
      if (compareTo === 'baseline' && baselineId === result.id) {
        return
      }
      
      const patch = displayPatches[idx] || ''
      const files = splitPatchByFile(patch)
      
      files.forEach((file) => {
        // Skip "changes" files that are empty or have minimal content
        if (file.path === 'changes') {
          const trimmedContent = file.content.trim()
          // Skip if empty or only contains whitespace/newlines
          if (!trimmedContent || trimmedContent.split('\n').filter(l => l.trim()).length === 0) {
            return
          }
        }
        
        if (!fileMap.has(file.path)) {
          fileMap.set(file.path, [])
        }
        fileMap.get(file.path)!.push({
          result,
          patch,
          fileContent: file.content,
        })
      })
    })
    
    return fileMap
  }, [results, displayPatches, compareTo, baselineId, hasEnoughIds, isLoading])

  // Early returns AFTER all hooks
  if (!hasEnoughIds) {
    return (
      <div>
        <PageHeader title="Compare Results" />
        <EmptyState
          title="Select at least 2 results to compare"
          description="Go back and select multiple results from a scenario to compare them side by side."
          action={
            scenarioId ? (
              <Link to={`/scenario/${scenarioId}`}>
                <Button>Back to Scenario</Button>
              </Link>
            ) : (
              <Link to="/runs">
                <Button>View Runs</Button>
              </Link>
            )
          }
        />
      </div>
    )
  }

  if (isLoading) {
    return (
      <PageLayout>
        <PageHeader title="Compare Results" />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </PageLayout>
    )
  }

  // Files panel content
  function FilesPanel({ patch, isStreaming }: { patch: string; isStreaming?: boolean }) {
    if (patch) {
      return (
        <div className="relative">
          {isStreaming && (
            <div className="absolute top-2 right-2 z-10 flex items-center gap-1.5 px-2 py-1 bg-surface-2/90 backdrop-blur rounded text-xs text-accent">
              <span className="w-1.5 h-1.5 bg-accent rounded-full animate-pulse" />
              Live
            </div>
          )}
          <FileDiffViewer patch={patch} />
        </div>
      )
    }
    return (
      <div className="py-8 text-center text-text-tertiary">
        {isStreaming ? 'Waiting for file changes...' : 'No patch available'}
      </div>
    )
  }

  // Result card component with viewMode support and streaming patch handling
  function ResultCard({ 
    result, 
    patch: initialPatch, 
    isBaseline 
  }: { 
    result: Result
    patch: string
    isBaseline: boolean
  }) {
    const queryClient = useQueryClient()
    const isRunning = result.status === 'running' || result.status === 'queued'
    
    // Track streaming patch updates
    const [streamingPatch, setStreamingPatch] = useState<string>('')
    
    // Use streaming patch when running, otherwise use the fetched patch
    const currentPatch = isRunning && streamingPatch ? streamingPatch : initialPatch
    
    // Fetch logs for completed results
    const { data: logsData } = useQuery({
      queryKey: ['result-logs', result.id],
      queryFn: () => getResultLogs(result.id),
      enabled: !isRunning && !!result.id,
    })

    // Logs panel content - inline for access to state
    const renderLogsPanel = (maxHeight: string) => {
      if (isRunning) {
        return (
          <StreamingLogs
            resultId={result.id}
            onStatusChange={(status) => {
              // Invalidate queries when status changes to refresh UI
              if (status === 'completed' || status === 'failed' || status === 'infra_failure') {
                queryClient.invalidateQueries({ queryKey: ['result', result.id] })
                queryClient.invalidateQueries({ queryKey: ['result-logs', result.id] })
                queryClient.invalidateQueries({ queryKey: ['result-patch', result.id] })
              }
            }}
            onPatchUpdate={(patch) => setStreamingPatch(patch)}
            onComplete={() => {
              queryClient.invalidateQueries({ queryKey: ['result', result.id] })
              queryClient.invalidateQueries({ queryKey: ['result-logs', result.id] })
              queryClient.invalidateQueries({ queryKey: ['result-patch', result.id] })
            }}
          />
        )
      }
      
      if (logsData) {
        return (
          <div className="space-y-4">
            {logsData.stdout && (
              <LogsViewer 
                logs={logsData.stdout} 
                title="stdout" 
                defaultMode="chat"
                maxHeight={maxHeight}
              />
            )}
            {logsData.stderr && logsData.stderr.trim() && (
              <LogsViewer 
                logs={logsData.stderr} 
                title="stderr" 
                defaultMode="raw"
                maxHeight="200px"
              />
            )}
            {!logsData.stdout && !logsData.stderr?.trim() && (
              <div className="py-8 text-center text-text-tertiary text-sm">No output recorded</div>
            )}
          </div>
        )
      }
      
      return <div className="py-8 text-center text-text-tertiary">Loading logs...</div>
    }

    return (
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title className="font-mono text-sm">
              {result.harness}:{result.provider}:{result.model}
              {isBaseline && compareTo === 'baseline' && (
                <span className="ml-2 text-xs text-text-tertiary">(Baseline)</span>
              )}
            </Card.Title>
            <StatusBadge status={result.status} isStale={result.is_stale} />
          </div>
        </Card.Header>
        <Card.Content>
          {viewMode === 'split' ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <FileText className="w-3 h-3" />
                  Logs
                </div>
                {renderLogsPanel('400px')}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <File className="w-3 h-3" />
                  Files
                </div>
                <FilesPanel patch={currentPatch} isStreaming={isRunning} />
              </div>
            </div>
          ) : viewMode === 'logs' ? (
            renderLogsPanel('600px')
          ) : (
            <FilesPanel patch={currentPatch} isStreaming={isRunning} />
          )}
        </Card.Content>
      </Card>
    )
  }

  // Render executor-grouped view (default)
  const renderExecutorGrouped = () => {
    // Filter out baseline when comparing to baseline
    const displayResults = compareTo === 'baseline' && baselineId
      ? results.filter((result) => result.id !== baselineId)
      : results
    
    return (
      <div className="space-y-6">
        {displayResults.map((result) => {
          const idx = results.findIndex((r) => r.id === result.id)
          const patch = displayPatches[idx] || ''
          const isBaseline = baselineId === result.id

          return (
            <ResultCard
              key={result.id}
              result={result}
              patch={patch}
              isBaseline={isBaseline}
            />
          )
        })}
      </div>
    )
  }

  // Simple logs display for file-grouped view (typically completed results)
  function SimpleLogsPanel({ result, maxHeight = '400px' }: { result: Result; maxHeight?: string }) {
    const { data: logsData } = useQuery({
      queryKey: ['result-logs', result.id],
      queryFn: () => getResultLogs(result.id),
      enabled: !!result.id,
    })
    
    if (logsData) {
      return (
        <div className="space-y-4">
          {logsData.stdout && (
            <LogsViewer 
              logs={logsData.stdout} 
              title="stdout" 
              defaultMode="chat"
              maxHeight={maxHeight}
            />
          )}
          {logsData.stderr && logsData.stderr.trim() && (
            <LogsViewer 
              logs={logsData.stderr} 
              title="stderr" 
              defaultMode="raw"
              maxHeight="200px"
            />
          )}
          {!logsData.stdout && !logsData.stderr?.trim() && (
            <div className="py-8 text-center text-text-tertiary text-sm">No output recorded</div>
          )}
        </div>
      )
    }
    
    return <div className="py-8 text-center text-text-tertiary">Loading logs...</div>
  }

  // File card component for file-grouped view
  function FileGroupedCard({ 
    filePath, 
    fileResults 
  }: { 
    filePath: string
    fileResults: Array<{ result: Result; patch: string; fileContent: string }>
  }) {
    const [selectedExecutor, setSelectedExecutor] = useState<string | null>(
      fileResults.length > 0 ? `${fileResults[0].result.harness}:${fileResults[0].result.provider}:${fileResults[0].result.model}` : null
    )

    const selectedResult = fileResults.find(
      (fr) => `${fr.result.harness}:${fr.result.provider}:${fr.result.model}` === selectedExecutor
    ) || fileResults[0]

    return (
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title className="font-mono text-sm">{filePath}</Card.Title>
            {fileResults.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {fileResults.map((fr) => {
                  const executorKey = `${fr.result.harness}:${fr.result.provider}:${fr.result.model}`
                  const isSelected = executorKey === selectedExecutor
                  return (
                    <button
                      key={executorKey}
                      onClick={() => setSelectedExecutor(executorKey)}
                      className={`px-3 py-1.5 text-xs rounded whitespace-nowrap transition-colors ${
                        isSelected
                          ? 'bg-accent text-on-accent font-medium'
                          : 'bg-surface-2 text-text-secondary hover:bg-surface-3 hover:text-text-primary'
                      }`}
                    >
                      {fr.result.harness}:{fr.result.provider}:{fr.result.model}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </Card.Header>
        <Card.Content>
          {viewMode === 'split' ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <FileText className="w-3 h-3" />
                  Logs
                </div>
                {selectedResult && <SimpleLogsPanel result={selectedResult.result} maxHeight="400px" />}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <File className="w-3 h-3" />
                  Files
                </div>
                {selectedResult ? (
                  <GitHubDiffViewer patch={selectedResult.fileContent} />
                ) : (
                  <div className="py-8 text-center text-text-tertiary">No content available</div>
                )}
              </div>
            </div>
          ) : viewMode === 'logs' ? (
            selectedResult && <SimpleLogsPanel result={selectedResult.result} maxHeight="600px" />
          ) : (
            selectedResult ? (
              <GitHubDiffViewer patch={selectedResult.fileContent} />
            ) : (
              <div className="py-8 text-center text-text-tertiary">No content available</div>
            )
          )}
        </Card.Content>
      </Card>
    )
  }

  // Render file-grouped view
  const renderFileGrouped = () => {
    const files = Array.from(filesByPath.keys()).sort()
    
    if (files.length === 0) {
      return (
        <div className="py-8 text-center text-text-tertiary">No files changed</div>
      )
    }

    return (
      <div className="space-y-6">
        {files.map((filePath) => (
          <FileGroupedCard
            key={filePath}
            filePath={filePath}
            fileResults={filesByPath.get(filePath) || []}
          />
        ))}
      </div>
    )
  }

  return (
    <PageLayout>
      <PageHeader
        title="Compare Results"
        description={`Comparing ${ids.length} results side by side`}
      />

      {/* Comparison Table + Time vs Score Chart */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <div className="min-w-0">
          <ComparisonTable 
            results={
              compareTo === 'baseline' && baselineId
                ? results.filter((result) => result.id !== baselineId)
                : results
            }
            judgementsByResult={judgementsByResult} 
          />
        </div>
        
        {/* Time/Cost vs Score Scatter Plot */}
        <Card className="min-w-0">
          <Card.Header>
            <div className="flex items-center justify-between gap-3">
              <Card.Title className="text-sm">Time vs Quality</Card.Title>
              <div className="flex items-center gap-2">
                <span className="text-xs text-text-tertiary">X</span>
                <select
                  className="h-8 rounded-md border border-border bg-surface px-2 text-xs text-text-secondary"
                  value={timeVsQualityX}
                  onChange={(e) => setTimeVsQualityX(e.target.value as 'time' | 'cost')}
                >
                  <option value="time">Time</option>
                  <option value="cost">Cost</option>
                </select>
              </div>
            </div>
          </Card.Header>
          <Card.Content className="py-2 w-full">
            <TimeVsScoreChart
              results={
                compareTo === 'baseline' && baselineId
                  ? results.filter((result) => result.id !== baselineId)
                  : results
              }
              judgementsByResult={judgementsByResult}
              xMetric={timeVsQualityX}
              onPointClick={(resultId) => navigate(`/result/${resultId}`)}
            />
          </Card.Content>
        </Card>
      </div>

      {/* View Controls */}
      <Card className="mb-6">
        <Card.Content>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-6 flex-wrap">
              <div className="flex items-center gap-3">
                <Select
                  label="Group by"
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value as 'executor' | 'file')}
                  className="w-40"
                  options={[
                    { value: 'executor', label: 'Executor' },
                    { value: 'file', label: 'File' },
                  ]}
                />
              </div>
              <div className="flex items-center gap-3">
                <Select
                  label="Compare to"
                  value={compareTo}
                  onChange={(e) => setCompareTo(e.target.value as 'parent' | 'baseline')}
                  className="w-40"
                  options={[
                    { value: 'parent', label: 'Parent' },
                    { value: 'baseline', label: 'Baseline' },
                  ]}
                />
              </div>
              {compareTo === 'baseline' && (
                <div className="flex items-center gap-3">
                  <Select
                    label="Baseline"
                    value={baselineId?.toString() || (ids.length > 0 ? ids[0].toString() : '')}
                    onChange={(e) => setBaselineId(e.target.value ? Number(e.target.value) : null)}
                    className="w-64"
                    options={results.map((result) => ({
                      value: result.id.toString(),
                      label: `${result.harness}:${result.provider}:${result.model} (Result ${result.id})`,
                    }))}
                  />
                </div>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-tertiary">View</label>
              <ViewModeSwitcher value={viewMode} onChange={setViewMode} />
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Diffs */}
      {groupBy === 'file' ? renderFileGrouped() : renderExecutorGrouped()}
    </PageLayout>
  )
}

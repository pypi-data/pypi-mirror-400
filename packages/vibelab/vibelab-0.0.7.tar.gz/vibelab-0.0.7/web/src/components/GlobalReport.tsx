import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { FullPageMatrixLayout, Button, EmptyState } from './ui'
import { QualityTradeoffPlot, type TradeoffXMetric } from './QualityTradeoffPlot'
import { MatrixQualityBadge } from './AnalyticsMatrix'
import { QualityMatrixView } from './QualityMatrixView'
import { useAnalyticsMatrix } from './useAnalyticsMatrix'
import { formatDurationWithStd } from '../lib/metrics'

export default function GlobalReport() {
  const navigate = useNavigate()
  const [tradeoffX, setTradeoffX] = useState<TradeoffXMetric>('time')

  const analytics = useAnalyticsMatrix({ mode: 'global' })

  // Compact header with title, metrics, plot, and actions all in one row
  const header = (
    <div className="space-y-3">
      {/* Title row */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">Global Report</h1>
          <p className="text-sm text-text-secondary">
            {analytics.matrix.length} scenarios × {analytics.visibleExecutors.length} executors
          </p>
        </div>
        <div className="flex items-center gap-2">
          {analytics.stats.pendingJudges > 0 && (
            <Button
              size="sm"
              variant="secondary"
              onClick={analytics.runAllJudges}
              disabled={analytics.judgingResultIds.size === analytics.stats.pendingJudges}
            >
              {analytics.judgingResultIds.size > 0
                ? `⚖️ ${analytics.judgingResultIds.size}/${analytics.stats.pendingJudges} judging...`
                : `⚖️ Judge All (${analytics.stats.pendingJudges})`}
            </Button>
          )}
          {analytics.missingRuns.all.length > 0 && (
            <Button
              size="sm"
              variant="secondary"
              onClick={analytics.handleRunAllMissing}
              disabled={analytics.batchRunning.size > 0}
            >
              {analytics.batchRunning.size > 0
                ? `Running ${analytics.batchRunning.size}...`
                : `▶ Run Missing (${analytics.missingRuns.all.length})`}
            </Button>
          )}
        </div>
      </div>

      {/* Metrics + Plot row */}
      <div className="flex items-stretch gap-4 bg-surface border border-border rounded-lg overflow-hidden">
        {/* Summary metrics - left side */}
        <div className="flex items-center gap-6 px-5 py-3 border-r border-border">
          {/* Global Quality - Hero metric */}
          <div className="flex items-center gap-3">
            <MatrixQualityBadge
              value={analytics.agg.global.quality.mean}
              std={analytics.agg.global.quality.std}
              count={analytics.agg.global.quality.count}
              size="lg"
              showStd
            />
            <div>
              <div className="text-[10px] text-text-tertiary uppercase tracking-wide">Quality</div>
              <div className="text-xs text-text-secondary">
                {analytics.agg.global.quality.count} rated
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="w-px h-10 bg-border" />

          {/* Stats */}
          <div className="flex gap-5">
            <div>
              <div className="text-[10px] text-text-tertiary uppercase tracking-wide">Time</div>
              <div className="text-sm font-semibold text-text-primary">
                {analytics.agg.global.latency.mean != null
                  ? formatDurationWithStd(analytics.agg.global.latency.mean, analytics.agg.global.latency.std)
                  : '—'}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-text-tertiary uppercase tracking-wide">Done</div>
              <div className="text-sm font-semibold text-status-success">
                {analytics.stats.completed}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-text-tertiary uppercase tracking-wide">Failed</div>
              <div className={`text-sm font-semibold ${analytics.stats.failed > 0 ? 'text-status-error' : 'text-text-disabled'}`}>
                {analytics.stats.failed}
              </div>
            </div>
            {analytics.stats.running > 0 && (
              <div>
                <div className="text-[10px] text-text-tertiary uppercase tracking-wide">Running</div>
                <div className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-status-info animate-pulse" />
                  <span className="text-sm font-semibold text-status-info">{analytics.stats.running}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Plot - right side (fills remaining space) */}
        <div className="flex-1 px-3 py-2 min-w-[320px]">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-text-tertiary uppercase tracking-wide">
              {tradeoffX === 'time' ? 'Time' : 'Cost'} vs Quality
            </span>
            <select
              className="h-5 rounded border border-border bg-surface px-1.5 text-[10px] text-text-secondary"
              value={tradeoffX}
              onChange={(e) => setTradeoffX(e.target.value as TradeoffXMetric)}
            >
              <option value="time">Time</option>
              <option value="cost">Cost</option>
            </select>
          </div>
          <div className="h-[160px]">
            <QualityTradeoffPlot
              points={analytics.tradeoffPoints}
              xMetric={tradeoffX}
              emptyText="No data"
            />
          </div>
        </div>
      </div>
    </div>
  )

  if (analytics.isLoading) {
    return (
      <FullPageMatrixLayout header={header} isEmpty>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </FullPageMatrixLayout>
    )
  }

  if (!analytics.data) {
    return (
      <FullPageMatrixLayout
        header={header}
        isEmpty
        emptyState={<EmptyState title="No data" description="Could not load global analytics." />}
      />
    )
  }

  if (analytics.matrix.length === 0) {
    return (
      <FullPageMatrixLayout
        header={header}
        isEmpty
        emptyState={
          <EmptyState
            title="No scenarios yet"
            description="Create scenarios and run them to see the global report."
            action={<Button onClick={() => navigate('/run/create')}>Create Run</Button>}
          />
        }
      />
    )
  }

  return (
    <FullPageMatrixLayout header={header}>
      <QualityMatrixView
        matrix={analytics.matrix}
        visibleExecutors={analytics.visibleExecutors}
        agg={analytics.agg}
        stats={analytics.stats}
        missingRuns={analytics.missingRuns}
        judgeByScenario={analytics.judgeByScenario}
        judgingResultIds={analytics.judgingResultIds}
        batchRunning={analytics.batchRunning}
        runAllJudges={analytics.runAllJudges}
        handleStartRun={analytics.handleStartRun}
        isStartingRun={analytics.isStartingRun}
        handleRunRowMissing={analytics.handleRunRowMissing}
        handleRunColumnMissing={analytics.handleRunColumnMissing}
        handleRunAllMissing={analytics.handleRunAllMissing}
        fullPage
        hideHeader
      />
    </FullPageMatrixLayout>
  )
}

import { useQuery } from '@tanstack/react-query'
import { getTaskStats, getHealth } from '../api'
import { cn } from '../lib/cn'
import { Tooltip } from './ui/Tooltip'

// Animated pulse dot for running state
function PulseDot({ className }: { className?: string }) {
  return (
    <span className={cn('relative flex h-2 w-2', className)}>
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-info opacity-75" />
      <span className="relative inline-flex h-2 w-2 rounded-full bg-status-info" />
    </span>
  )
}

// Static dot for status indicators
function StatusDot({ variant }: { variant: 'queued' | 'idle' }) {
  const colors = {
    queued: 'bg-status-warning',
    idle: 'bg-text-disabled',
  }
  return (
    <span
      className={cn('inline-flex h-2 w-2 rounded-full', colors[variant])}
    />
  )
}

interface TaskGroupStats {
  queued: number
  running: number
}

function TaskGroupDisplay({ 
  label, 
  stats, 
  showLabel = true,
  groupDescription
}: { 
  label: string
  stats: TaskGroupStats
  showLabel?: boolean
  groupDescription?: string
}) {
  const hasAny = stats.queued > 0 || stats.running > 0
  
  if (!hasAny && !showLabel) {
    return null
  }

  return (
    <div className="flex items-center gap-3">
      {showLabel && (
        <Tooltip content={groupDescription || `${label} tasks`}>
          <span className="text-xs font-medium text-text-secondary min-w-[50px] cursor-help">
            {label}:
          </span>
        </Tooltip>
      )}
      <div className="flex items-center gap-3">
        {stats.queued > 0 && (
          <Tooltip content={`${stats.queued} queued - Waiting in queue to be processed`}>
            <div className="flex items-center gap-1.5 cursor-help">
              <StatusDot variant="queued" />
              <span className="text-xs text-text-tertiary">{stats.queued}</span>
            </div>
          </Tooltip>
        )}
        {stats.running > 0 && (
          <Tooltip content={`${stats.running} running - Currently being executed by a worker`}>
            <div className="flex items-center gap-1.5 cursor-help">
              <PulseDot />
              <span className="text-xs font-medium text-text-secondary">{stats.running}</span>
            </div>
          </Tooltip>
        )}
        {!hasAny && (
          <span className="text-xs text-text-disabled">—</span>
        )}
      </div>
    </div>
  )
}

export default function WorkerStatusFooter() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['taskStats'],
    queryFn: getTaskStats,
    refetchInterval: 2000,
    retry: 3,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    staleTime: 60000, // Cache for 1 minute
    retry: 1,
  })

  // Don't render anything during initial load to avoid layout shift
  if (isLoading && !stats) {
    return (
      <footer className="shrink-0 h-9 bg-surface border-t border-border-muted">
        <div className="h-full px-6 flex items-center">
          <div className="flex items-center gap-2 text-xs text-text-disabled">
            <span className="inline-block w-2 h-2 rounded-full bg-text-disabled animate-pulse" />
            <span>Connecting...</span>
          </div>
        </div>
      </footer>
    )
  }

  if (error || !stats) {
    return (
      <footer className="shrink-0 h-9 bg-surface border-t border-border-muted">
        <div className="h-full px-6 flex items-center">
          <div className="flex items-center gap-2 text-xs text-text-disabled">
            <span className="inline-block w-2 h-2 rounded-full bg-status-error" />
            <span>Queue unavailable</span>
          </div>
        </div>
      </footer>
    )
  }

  const taskStats = stats.task_stats || {}

  // Aggregate stats by category: runs vs judges
  const runsStats: TaskGroupStats = {
    queued: taskStats.agent_run?.queued || 0,
    running: taskStats.agent_run?.running || 0,
  }

  const judgesStats: TaskGroupStats = {
    queued: (taskStats.judge_result?.queued || 0) + (taskStats.train_judge?.queued || 0),
    running: (taskStats.judge_result?.running || 0) + (taskStats.train_judge?.running || 0),
  }

  // Calculate totals
  const totalQueued = runsStats.queued + judgesStats.queued
  const totalRunning = runsStats.running + judgesStats.running
  const queueLength = totalQueued
  const hasActivity = totalQueued > 0 || totalRunning > 0

  return (
    <footer className="shrink-0 min-h-[36px] bg-surface border-t border-border-muted">
      <div className="h-full px-6 py-1.5 flex items-center justify-between">
        <div className="flex items-center gap-6 flex-wrap">
          {/* Queue length */}
          {queueLength > 0 && (
            <Tooltip content={`Total tasks waiting in queue: ${queueLength} tasks (${runsStats.queued} runs + ${judgesStats.queued} judges) waiting to be processed`}>
              <div className="flex items-center gap-2 cursor-help">
                <span className="text-xs text-text-disabled">Queue:</span>
                <span className="text-xs font-medium text-text-secondary">{queueLength}</span>
              </div>
            </Tooltip>
          )}

          {/* Runs stats */}
          <TaskGroupDisplay 
            label="Runs" 
            stats={runsStats}
            groupDescription="Agent execution tasks: running code generation agents on scenarios"
          />

          {/* Judges stats */}
          <TaskGroupDisplay 
            label="Judges" 
            stats={judgesStats}
            groupDescription="Evaluation tasks: judging results and training judges"
          />

          {/* Idle state */}
          {!hasActivity && (
            <Tooltip content="No tasks in queue or running - worker is idle">
              <div className="flex items-center gap-2 cursor-help">
                <StatusDot variant="idle" />
                <span className="text-xs text-text-disabled">Idle</span>
              </div>
            </Tooltip>
          )}
        </div>

        {/* Right side: version */}
        <div className="text-[10px] tracking-wide uppercase text-text-disabled select-none shrink-0">
          VibeLab {health?.version ? `v${health.version}` : ''}
        </div>
      </div>
    </footer>
  )
}

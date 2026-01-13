import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  getReviewQueueStats,
  getReviewQueue,
  scoreReviewItem,
  skipReviewItem,
  getResultPatch,
  ReviewQueueItem,
} from '../api'
import GitHubDiffViewer from './GitHubDiffViewer'
import {
  PageLayout,
  PageHeader,
  Card,
  Button,
  EmptyState,
  Textarea,
} from './ui'
import {
  Target,
  TrendingUp,
  ListChecks,
  Award,
  Zap,
  SkipForward,
  ExternalLink,
  Clock,
  Check,
} from 'lucide-react'
import { cn } from '../lib/cn'

// Quality score definitions
const QUALITY_SCORES = [
  { value: 1, label: 'Bad', shortLabel: '1', color: 'bg-red-500', description: 'Completely wrong or broken' },
  { value: 2, label: 'Workable', shortLabel: '2', color: 'bg-amber-500', description: 'Has issues but partly works' },
  { value: 3, label: 'Good', shortLabel: '3', color: 'bg-blue-500', description: 'Correct with minor issues' },
  { value: 4, label: 'Perfect', shortLabel: '4', color: 'bg-emerald-500', description: 'Exactly right' },
]

// Alignment level badges
function getAlignmentLevel(score: number | null): { label: string; color: string; emoji: string } {
  if (score === null) return { label: 'Not Started', color: 'text-text-tertiary', emoji: '🔮' }
  if (score >= 0.9) return { label: 'Excellent', color: 'text-emerald-400', emoji: '🏆' }
  if (score >= 0.75) return { label: 'Good', color: 'text-blue-400', emoji: '⭐' }
  if (score >= 0.5) return { label: 'Fair', color: 'text-amber-400', emoji: '📈' }
  return { label: 'Needs Work', color: 'text-red-400', emoji: '🎯' }
}

// Stat card component
function StatCard({
  icon: Icon,
  label,
  value,
  subValue,
  color = 'text-accent',
}: {
  icon: React.ElementType
  label: string
  value: string | number
  subValue?: string
  color?: string
}) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4 flex items-center gap-4">
      <div className={cn('p-3 rounded-lg bg-surface-2', color)}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <div className="text-sm text-text-secondary">{label}</div>
        <div className="text-2xl font-bold text-text-primary">{value}</div>
        {subValue && <div className="text-xs text-text-tertiary">{subValue}</div>}
      </div>
    </div>
  )
}

// Progress bar
function ProgressBar({
  current,
  target,
  color = 'bg-accent',
}: {
  current: number
  target: number
  color?: string
}) {
  const percentage = Math.min((current / target) * 100, 100)
  return (
    <div className="w-full h-2 bg-surface-3 rounded-full overflow-hidden">
      <div
        className={cn('h-full transition-all duration-500', color)}
        style={{ width: `${percentage}%` }}
      />
    </div>
  )
}

// Queue item preview card
function QueueItemCard({
  item,
  isActive,
  onClick,
}: {
  item: ReviewQueueItem
  isActive: boolean
  onClick: () => void
}) {
  const judgeScore = QUALITY_SCORES.find(q => q.value === item.judge_quality)

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left p-3 rounded-lg border transition-colors',
        isActive
          ? 'bg-accent/10 border-accent'
          : 'bg-surface border-border hover:bg-surface-2 hover:border-border-hover'
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-text-secondary">
          Scenario #{item.scenario_id}
        </span>
        {judgeScore && (
          <span className={cn('px-2 py-0.5 rounded text-xs font-medium text-white', judgeScore.color)}>
            Judge: {judgeScore.shortLabel}
          </span>
        )}
      </div>
      <div className="text-sm text-text-primary line-clamp-2 mb-2">
        {item.scenario_prompt}
      </div>
      <div className="flex items-center justify-between text-xs text-text-tertiary">
        <span>{item.model}</span>
        <span className="text-text-quaternary">{item.priority_reason}</span>
      </div>
    </button>
  )
}

// Main score buttons
function ScoreButtons({
  onScore,
  isLoading,
}: {
  onScore: (quality: number) => void
  isLoading: boolean
}) {
  return (
    <div className="flex gap-3">
      {QUALITY_SCORES.map((score) => (
        <button
          key={score.value}
          onClick={() => onScore(score.value)}
          disabled={isLoading}
          className={cn(
            'flex-1 py-4 px-4 rounded-lg border-2 transition-all',
            'hover:scale-105 active:scale-95',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
            'flex flex-col items-center gap-1',
            score.color.replace('bg-', 'border-').replace('500', '500/30'),
            score.color.replace('bg-', 'hover:border-'),
            'bg-surface hover:bg-surface-2'
          )}
        >
          <div className={cn('w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg', score.color)}>
            {score.shortLabel}
          </div>
          <span className="font-medium text-text-primary">{score.label}</span>
          <span className="text-xs text-text-tertiary text-center hidden sm:block">{score.description}</span>
        </button>
      ))}
    </div>
  )
}

export default function ReviewQueue() {
  const queryClient = useQueryClient()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [notes, setNotes] = useState('')
  const [recentScore, setRecentScore] = useState<{ quality: number; resultId: number } | null>(null)
  const [streak, setStreak] = useState(0)

  // Fetch stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['review-queue-stats'],
    queryFn: getReviewQueueStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch queue items
  const { data: queueData, isLoading: queueLoading } = useQuery({
    queryKey: ['review-queue'],
    queryFn: () => getReviewQueue(50),
    refetchInterval: 60000, // Refresh every minute
  })

  const items = queueData?.items ?? []
  const currentItem = items[currentIndex]

  // Fetch diff for current item
  const { data: patchData, isLoading: patchLoading } = useQuery({
    queryKey: ['result-patch', currentItem?.result_id],
    queryFn: () => getResultPatch(currentItem!.result_id),
    enabled: !!currentItem,
  })

  // Score mutation
  const scoreMutation = useMutation({
    mutationFn: ({ resultId, quality, notes }: { resultId: number; quality: number; notes?: string }) =>
      scoreReviewItem(resultId, quality, notes),
    onSuccess: (_data, variables) => {
      // Show success feedback
      setRecentScore({ quality: variables.quality, resultId: variables.resultId })
      setStreak(s => s + 1)
      setTimeout(() => setRecentScore(null), 1500)

      // Clear notes
      setNotes('')

      // Move to next item
      if (currentIndex < items.length - 1) {
        setCurrentIndex(i => i + 1)
      }

      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['review-queue-stats'] })
      queryClient.invalidateQueries({ queryKey: ['review-queue'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    },
  })

  // Skip mutation
  const skipMutation = useMutation({
    mutationFn: (resultId: number) => skipReviewItem(resultId),
    onSuccess: () => {
      setStreak(0) // Reset streak on skip
      if (currentIndex < items.length - 1) {
        setCurrentIndex(i => i + 1)
      }
    },
  })

  // Reset index when queue changes
  useEffect(() => {
    if (currentIndex >= items.length && items.length > 0) {
      setCurrentIndex(0)
    }
  }, [items.length, currentIndex])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture if user is typing in textarea
      if (document.activeElement?.tagName === 'TEXTAREA') return
      
      if (e.key >= '1' && e.key <= '4') {
        const quality = parseInt(e.key)
        if (currentItem) {
          scoreMutation.mutate({ resultId: currentItem.result_id, quality, notes: notes || undefined })
        }
      } else if (e.key === 's' || e.key === 'S') {
        if (currentItem) {
          skipMutation.mutate(currentItem.result_id)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentItem, notes, scoreMutation, skipMutation])

  const isLoading = statsLoading || queueLoading
  const alignmentLevel = getAlignmentLevel(stats?.alignment_score ?? null)

  // Calculate target progress
  const targetTotal = (stats?.scenarios_with_judges ?? 0) * (stats?.target_per_scenario ?? 10)
  const progressToTarget = stats?.scored_count ?? 0

  return (
    <PageLayout>
      <PageHeader
        title="Review Queue"
        description="Score results to improve judge alignment"
        actions={
          streak > 2 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/20 text-amber-400 rounded-full text-sm font-medium">
              <Zap className="w-4 h-4" />
              {streak} streak!
            </div>
          )
        }
      />

      {/* Success animation overlay */}
      {recentScore && (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
          <div className="animate-ping">
            <div className={cn(
              'w-20 h-20 rounded-full flex items-center justify-center text-white text-3xl font-bold',
              QUALITY_SCORES.find(q => q.value === recentScore.quality)?.color
            )}>
              <Check className="w-10 h-10" />
            </div>
          </div>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={TrendingUp}
          label="Alignment Score"
          value={stats?.alignment_score !== null && stats?.alignment_score !== undefined
            ? `${(stats.alignment_score * 100).toFixed(0)}%`
            : '—'
          }
          subValue={`${alignmentLevel.emoji} ${alignmentLevel.label}`}
          color={alignmentLevel.color}
        />
        <StatCard
          icon={ListChecks}
          label="Queue Length"
          value={stats?.queue_length ?? '—'}
          subValue="results to score"
          color="text-blue-400"
        />
        <StatCard
          icon={Award}
          label="Scored"
          value={stats?.scored_count ?? '—'}
          subValue={`of ${targetTotal} target`}
          color="text-emerald-400"
        />
        <StatCard
          icon={Target}
          label="Scenarios"
          value={stats?.scenarios_with_judges ?? '—'}
          subValue="with judges"
          color="text-purple-400"
        />
      </div>

      {/* Progress bar */}
      {targetTotal > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-text-secondary">Progress to target</span>
            <span className="text-text-primary font-medium">
              {progressToTarget} / {targetTotal} ({Math.round((progressToTarget / targetTotal) * 100)}%)
            </span>
          </div>
          <ProgressBar
            current={progressToTarget}
            target={targetTotal}
            color="bg-gradient-to-r from-accent to-emerald-500"
          />
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12 text-text-tertiary">Loading queue...</div>
      ) : items.length === 0 ? (
        <EmptyState
          title="🎉 Queue is empty!"
          description="All results have been scored. Great work! New results will appear here when available."
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Queue sidebar */}
          <div className="lg:col-span-1 space-y-3">
            <h3 className="font-medium text-text-primary mb-3 flex items-center gap-2">
              <ListChecks className="w-4 h-4 text-text-tertiary" />
              Up Next
            </h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {items.slice(0, 15).map((item, idx) => (
                <QueueItemCard
                  key={item.result_id}
                  item={item}
                  isActive={idx === currentIndex}
                  onClick={() => setCurrentIndex(idx)}
                />
              ))}
              {items.length > 15 && (
                <div className="text-center text-xs text-text-tertiary py-2">
                  +{items.length - 15} more items
                </div>
              )}
            </div>
          </div>

          {/* Main review area */}
          <div className="lg:col-span-3">
            {currentItem ? (
              <Card className="p-0 overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-border bg-surface-2">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-semibold text-text-primary">
                        Result #{currentItem.result_id}
                      </span>
                      <Link
                        to={`/result/${currentItem.result_id}`}
                        className="text-text-tertiary hover:text-accent"
                        target="_blank"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Link>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      {currentItem.duration_ms && (
                        <span className="flex items-center gap-1 text-text-secondary">
                          <Clock className="w-4 h-4" />
                          {(currentItem.duration_ms / 1000).toFixed(1)}s
                        </span>
                      )}
                      <span className="text-text-tertiary">
                        {currentIndex + 1} of {items.length}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 text-sm">
                    <span className="px-2 py-1 bg-surface rounded text-text-secondary">
                      {currentItem.harness}
                    </span>
                    <span className="px-2 py-1 bg-surface rounded text-text-secondary">
                      {currentItem.provider}
                    </span>
                    <span className="px-2 py-1 bg-accent/20 text-accent rounded font-medium">
                      {currentItem.model}
                    </span>
                  </div>
                </div>

                {/* Scenario prompt */}
                <div className="p-4 border-b border-border">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Scenario</h4>
                  <p className="text-text-primary">{currentItem.scenario_prompt}</p>
                </div>

                {/* Judge hint */}
                {currentItem.judge_quality !== null && (
                  <div className="p-4 border-b border-border bg-blue-500/5">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-text-secondary">LLM Judge suggests:</span>
                      <span className={cn(
                        'px-2 py-1 rounded text-sm font-medium text-white',
                        QUALITY_SCORES.find(q => q.value === currentItem.judge_quality)?.color
                      )}>
                        {QUALITY_SCORES.find(q => q.value === currentItem.judge_quality)?.label}
                      </span>
                    </div>
                    {currentItem.judge_notes && (
                      <p className="mt-2 text-sm text-text-tertiary italic">
                        "{currentItem.judge_notes.substring(0, 200)}..."
                      </p>
                    )}
                  </div>
                )}

                {/* Diff viewer */}
                <div className="p-4 border-b border-border">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Output Diff</h4>
                  {patchLoading ? (
                    <div className="text-center py-8 text-text-tertiary">Loading diff...</div>
                  ) : patchData?.patch ? (
                    <div className="max-h-96 overflow-y-auto rounded border border-border">
                      <GitHubDiffViewer patch={patchData.patch} />
                    </div>
                  ) : (
                    <div className="text-center py-8 text-text-tertiary">No diff available</div>
                  )}
                </div>

                {/* Notes */}
                <div className="p-4 border-b border-border">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Notes (optional)</h4>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add any notes about this result..."
                    rows={2}
                    className="w-full"
                  />
                </div>

                {/* Score buttons */}
                <div className="p-4 bg-surface-2">
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-sm text-text-secondary">
                      <span className="text-text-tertiary">Keyboard:</span>{' '}
                      Press <kbd className="px-1.5 py-0.5 bg-surface rounded border border-border text-xs">1</kbd>-
                      <kbd className="px-1.5 py-0.5 bg-surface rounded border border-border text-xs">4</kbd> to score,{' '}
                      <kbd className="px-1.5 py-0.5 bg-surface rounded border border-border text-xs">S</kbd> to skip
                    </div>
                    <Button
                      variant="ghost"
                      onClick={() => skipMutation.mutate(currentItem.result_id)}
                      disabled={skipMutation.isPending}
                    >
                      <SkipForward className="w-4 h-4 mr-2" />
                      Skip
                    </Button>
                  </div>
                  <ScoreButtons
                    onScore={(quality) => {
                      scoreMutation.mutate({
                        resultId: currentItem.result_id,
                        quality,
                        notes: notes || undefined,
                      })
                    }}
                    isLoading={scoreMutation.isPending}
                  />
                </div>
              </Card>
            ) : (
              <EmptyState
                title="No item selected"
                description="Select an item from the queue to review"
              />
            )}
          </div>
        </div>
      )}

      {/* Link to Pairwise Compare */}
      <div className="mt-6 text-center">
        <Link
          to="/pairwise"
          className="text-sm text-text-secondary hover:text-accent"
        >
          Try pairwise comparison mode →
        </Link>
      </div>
    </PageLayout>
  )
}


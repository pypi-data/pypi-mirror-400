import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  getPairwiseStats,
  getNextPair,
  createPairwisePreference,
  getResultPatch,
  PreferenceType,
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
  ArrowLeft,
  ArrowRight,
  Equal,
  ThumbsUp,
  ThumbsDown,
  SkipForward,
  ExternalLink,
  Clock,
  Check,
  Zap,
  Trophy,
  Target,
  BarChart3,
} from 'lucide-react'
import { cn } from '../lib/cn'

// Preference options with keyboard shortcuts
const PREFERENCE_OPTIONS: {
  value: PreferenceType
  label: string
  shortLabel: string
  icon: React.ElementType
  key: string
  color: string
  bgColor: string
  description: string
}[] = [
  {
    value: 'a_better',
    label: 'A Better',
    shortLabel: 'A',
    icon: ArrowLeft,
    key: '1',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500',
    description: 'Left result is clearly better',
  },
  {
    value: 'both_good',
    label: 'Both Good',
    shortLabel: '★★',
    icon: ThumbsUp,
    key: '2',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500',
    description: 'Both excellent, hard to choose',
  },
  {
    value: 'tie',
    label: 'Tie',
    shortLabel: '=',
    icon: Equal,
    key: '3',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500',
    description: 'Roughly equal quality',
  },
  {
    value: 'both_bad',
    label: 'Both Bad',
    shortLabel: '✗✗',
    icon: ThumbsDown,
    key: '4',
    color: 'text-red-400',
    bgColor: 'bg-red-500',
    description: 'Both poor, hard to choose',
  },
  {
    value: 'b_better',
    label: 'B Better',
    shortLabel: 'B',
    icon: ArrowRight,
    key: '5',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500',
    description: 'Right result is clearly better',
  },
]

// Quality score badge
function QualityBadge({ score, label }: { score: number | null; label: string }) {
  if (score === null) return null
  
  const colors: Record<number, string> = {
    1: 'bg-red-500',
    2: 'bg-amber-500',
    3: 'bg-blue-500',
    4: 'bg-emerald-500',
  }
  
  return (
    <span className={cn(
      'px-2 py-0.5 rounded text-xs font-medium text-white',
      colors[score] || 'bg-gray-500'
    )}>
      {label}: {score}
    </span>
  )
}

// Stat card
function StatCard({
  icon: Icon,
  label,
  value,
  color = 'text-accent',
}: {
  icon: React.ElementType
  label: string
  value: string | number
  color?: string
}) {
  return (
    <div className="bg-surface rounded-lg border border-border p-3 flex items-center gap-3">
      <div className={cn('p-2 rounded-lg bg-surface-2', color)}>
        <Icon className="w-4 h-4" />
      </div>
      <div>
        <div className="text-xs text-text-secondary">{label}</div>
        <div className="text-lg font-bold text-text-primary">{value}</div>
      </div>
    </div>
  )
}

// Result panel for side-by-side comparison
function ResultPanel({
  side,
  executor,
  durationMs,
  judgeQuality,
  patch,
  patchLoading,
  resultId,
}: {
  side: 'A' | 'B'
  executor: string
  durationMs: number | null
  judgeQuality: number | null
  patch: string | undefined
  patchLoading: boolean
  resultId: number
}) {
  const [model, provider] = executor.split(':').reverse()
  
  return (
    <div className="flex-1 flex flex-col min-w-0">
      {/* Header */}
      <div className={cn(
        'p-3 border-b border-border flex items-center justify-between',
        side === 'A' ? 'bg-blue-500/10' : 'bg-purple-500/10'
      )}>
        <div className="flex items-center gap-2">
          <span className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold',
            side === 'A' ? 'bg-blue-500' : 'bg-purple-500'
          )}>
            {side}
          </span>
          <div>
            <div className="font-medium text-text-primary">{model}</div>
            <div className="text-xs text-text-secondary">{provider}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {durationMs && (
            <span className="flex items-center gap-1 text-xs text-text-secondary">
              <Clock className="w-3 h-3" />
              {(durationMs / 1000).toFixed(1)}s
            </span>
          )}
          <Link
            to={`/result/${resultId}`}
            className="text-text-tertiary hover:text-accent"
            target="_blank"
          >
            <ExternalLink className="w-4 h-4" />
          </Link>
        </div>
      </div>
      
      {/* Judge hint */}
      {judgeQuality !== null && (
        <div className="px-3 py-2 bg-surface-2 border-b border-border">
          <QualityBadge score={judgeQuality} label="Judge" />
        </div>
      )}
      
      {/* Diff viewer */}
      <div className="flex-1 overflow-y-auto">
        {patchLoading ? (
          <div className="text-center py-8 text-text-tertiary">Loading diff...</div>
        ) : patch ? (
          <GitHubDiffViewer patch={patch} />
        ) : (
          <div className="text-center py-8 text-text-tertiary">No diff available</div>
        )}
      </div>
    </div>
  )
}

export default function PairwiseCompare() {
  const queryClient = useQueryClient()
  const [notes, setNotes] = useState('')
  const [recentChoice, setRecentChoice] = useState<PreferenceType | null>(null)
  const [streak, setStreak] = useState(0)
  const [totalCompared, setTotalCompared] = useState(0)

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['pairwise-stats'],
    queryFn: getPairwiseStats,
    refetchInterval: 30000,
  })

  // Fetch next pair
  const { data: pairData, isLoading: pairLoading, refetch: refetchPair } = useQuery({
    queryKey: ['pairwise-next'],
    queryFn: () => getNextPair(),
  })

  const pair = pairData?.pair

  // Fetch patches for both results
  const { data: patchA, isLoading: patchALoading } = useQuery({
    queryKey: ['result-patch', pair?.result_a_id],
    queryFn: () => getResultPatch(pair!.result_a_id),
    enabled: !!pair,
  })

  const { data: patchB, isLoading: patchBLoading } = useQuery({
    queryKey: ['result-patch', pair?.result_b_id],
    queryFn: () => getResultPatch(pair!.result_b_id),
    enabled: !!pair,
  })

  // Create preference mutation
  const createMutation = useMutation({
    mutationFn: ({
      resultAId,
      resultBId,
      preference,
      notes,
    }: {
      resultAId: number
      resultBId: number
      preference: PreferenceType
      notes?: string
    }) => createPairwisePreference(resultAId, resultBId, preference, undefined, notes),
    onSuccess: (_data, variables) => {
      // Show feedback
      setRecentChoice(variables.preference)
      setStreak(s => s + 1)
      setTotalCompared(t => t + 1)
      setTimeout(() => setRecentChoice(null), 1000)

      // Clear notes
      setNotes('')

      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['pairwise-stats'] })
      queryClient.invalidateQueries({ queryKey: ['pairwise-next'] })
      queryClient.invalidateQueries({ queryKey: ['review-queue-stats'] })
    },
  })

  // Handle skip (just refetch next pair)
  const handleSkip = () => {
    setStreak(0)
    refetchPair()
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'TEXTAREA') return
      if (!pair) return

      const option = PREFERENCE_OPTIONS.find(o => o.key === e.key)
      if (option) {
        createMutation.mutate({
          resultAId: pair.result_a_id,
          resultBId: pair.result_b_id,
          preference: option.value,
          notes: notes || undefined,
        })
      } else if (e.key === 's' || e.key === 'S') {
        handleSkip()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [pair, notes, createMutation])

  return (
    <PageLayout>
      <PageHeader
        title="Pairwise Compare"
        description="Compare results side-by-side to improve judge alignment"
        actions={
          streak > 2 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/20 text-amber-400 rounded-full text-sm font-medium">
              <Zap className="w-4 h-4" />
              {streak} streak!
            </div>
          )
        }
      />

      {/* Success animation */}
      {recentChoice && (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
          <div className="animate-ping">
            <div className={cn(
              'w-20 h-20 rounded-full flex items-center justify-center text-white',
              PREFERENCE_OPTIONS.find(o => o.value === recentChoice)?.bgColor
            )}>
              <Check className="w-10 h-10" />
            </div>
          </div>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <StatCard
          icon={Trophy}
          label="Compared"
          value={stats?.total_preferences ?? 0}
          color="text-amber-400"
        />
        <StatCard
          icon={Target}
          label="Results"
          value={stats?.unique_results_compared ?? 0}
          color="text-blue-400"
        />
        <StatCard
          icon={BarChart3}
          label="Scenarios"
          value={stats?.scenarios_with_preferences ?? 0}
          color="text-purple-400"
        />
        <StatCard
          icon={Zap}
          label="This Session"
          value={totalCompared}
          color="text-emerald-400"
        />
      </div>

      {pairLoading ? (
        <div className="text-center py-12 text-text-tertiary">Loading next pair...</div>
      ) : !pair ? (
        <EmptyState
          title="🎉 No more pairs!"
          description="All available pairs have been compared. Great work!"
        />
      ) : (
        <Card className="p-0 overflow-hidden">
          {/* Scenario context */}
          <div className="p-4 border-b border-border bg-surface-2">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-text-secondary">
                Scenario #{pair.scenario_id}
              </span>
              <span className="text-xs text-text-tertiary">
                {pair.scenario_comparison_count} comparisons • {pair.priority_reason}
              </span>
            </div>
            <p className="text-text-primary">{pair.scenario_prompt}</p>
          </div>

          {/* Side-by-side comparison */}
          <div className="flex divide-x divide-border h-[400px]">
            <ResultPanel
              side="A"
              executor={pair.result_a_executor}
              durationMs={pair.result_a_duration_ms}
              judgeQuality={pair.judge_a_quality}
              patch={patchA?.patch}
              patchLoading={patchALoading}
              resultId={pair.result_a_id}
            />
            <ResultPanel
              side="B"
              executor={pair.result_b_executor}
              durationMs={pair.result_b_duration_ms}
              judgeQuality={pair.judge_b_quality}
              patch={patchB?.patch}
              patchLoading={patchBLoading}
              resultId={pair.result_b_id}
            />
          </div>

          {/* Notes */}
          <div className="p-4 border-t border-border">
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes about your choice..."
              rows={2}
              className="w-full"
            />
          </div>

          {/* Choice buttons */}
          <div className="p-4 bg-surface-2 border-t border-border">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm text-text-secondary">
                <span className="text-text-tertiary">Keyboard:</span>{' '}
                {PREFERENCE_OPTIONS.map(o => (
                  <span key={o.key}>
                    <kbd className="px-1.5 py-0.5 bg-surface rounded border border-border text-xs mx-0.5">
                      {o.key}
                    </kbd>
                    {o.shortLabel}{' '}
                  </span>
                ))}
                <kbd className="px-1.5 py-0.5 bg-surface rounded border border-border text-xs mx-0.5">S</kbd> skip
              </div>
              <Button
                variant="ghost"
                onClick={handleSkip}
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip
              </Button>
            </div>

            <div className="flex gap-2 justify-center">
              {PREFERENCE_OPTIONS.map((option) => {
                const Icon = option.icon
                return (
                  <button
                    key={option.value}
                    onClick={() => {
                      createMutation.mutate({
                        resultAId: pair.result_a_id,
                        resultBId: pair.result_b_id,
                        preference: option.value,
                        notes: notes || undefined,
                      })
                    }}
                    disabled={createMutation.isPending}
                    className={cn(
                      'flex-1 max-w-32 py-3 px-3 rounded-lg border-2 transition-all',
                      'hover:scale-105 active:scale-95',
                      'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
                      'flex flex-col items-center gap-1',
                      option.color,
                      'border-current/30 hover:border-current',
                      'bg-surface hover:bg-surface-2'
                    )}
                  >
                    <Icon className="w-6 h-6" />
                    <span className="font-medium text-sm">{option.label}</span>
                    <span className="text-xs text-text-tertiary hidden sm:block">
                      {option.description}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>
        </Card>
      )}

      {/* Link to Review Queue */}
      <div className="mt-6 text-center">
        <Link
          to="/review"
          className="text-sm text-text-secondary hover:text-accent"
        >
          ← Switch to absolute scoring (Review Queue)
        </Link>
      </div>
    </PageLayout>
  )
}


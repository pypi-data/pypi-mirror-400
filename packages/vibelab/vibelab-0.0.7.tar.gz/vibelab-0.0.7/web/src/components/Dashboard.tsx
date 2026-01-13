import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listScenarios, listDatasets, listExecutors, Result } from '../api'
import { PageLayout, Card, StatusBadge, Button } from './ui'
import { useMemo } from 'react'
import {
  Play,
  Folder,
  Layers,
  Cpu,
  DollarSign,
  CheckCircle,
  Clock,
  Star,
  Scale,
  BarChart3,
} from 'lucide-react'

// Stat card component
function StatCard({
  label,
  value,
  subValue,
  color = 'text-text-primary',
  icon,
}: {
  label: string
  value: string | number
  subValue?: string
  color?: string
  icon: React.ReactNode
}) {
  return (
    <div className="bg-surface border border-border rounded-lg p-3 sm:p-4 flex items-start gap-2.5 sm:gap-3">
      <div className="p-1.5 sm:p-2 rounded-lg bg-surface-2 text-text-tertiary shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-xl sm:text-2xl font-semibold leading-tight ${color}`}>{value}</div>
        <div className="text-xs text-text-tertiary">{label}</div>
        {subValue && <div className="text-xs text-text-disabled mt-0.5 hidden sm:block">{subValue}</div>}
      </div>
    </div>
  )
}

// Quick action button
function QuickAction({
  to,
  icon,
  label,
  description,
}: {
  to: string
  icon: React.ReactNode
  label: string
  description: string
}) {
  return (
    <Link
      to={to}
      className="flex items-start gap-3 p-4 bg-surface border border-border rounded-lg hover:border-accent hover:bg-surface-2 transition-all group"
    >
      <div className="p-2 rounded-lg bg-accent/10 text-accent group-hover:bg-accent group-hover:text-on-accent transition-colors">
        {icon}
      </div>
      <div>
        <div className="font-medium text-text-primary group-hover:text-accent transition-colors">
          {label}
        </div>
        <div className="text-xs text-text-tertiary">{description}</div>
      </div>
    </Link>
  )
}

// Recent result row
function RecentResultRow({ result }: { result: Result }) {
  const executorParts = [result.harness, result.provider, result.model].filter(Boolean)
  const executor = executorParts.join(':')

  const formatTime = (dateStr: string) => {
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

  return (
    <Link
      to={`/result/${result.id}`}
      className={[
        // Mobile: stack to avoid cramped horizontal layouts and accidental overlaps
        'flex flex-col gap-2 py-3 px-4',
        'sm:flex-row sm:items-center sm:gap-3',
        // Full-width row styling
        'hover:bg-surface-2 transition-colors',
        // Separators (avoid parent divide-y + negative margins, which can visually overlap)
        'border-b border-border-muted last:border-b-0',
      ].join(' ')}
    >
      <div className="flex items-center gap-3 min-w-0 w-full sm:flex-1">
        <StatusBadge status={result.status} isStale={result.is_stale} />
        <div className="flex-1 min-w-0">
          <div className="text-sm text-text-primary truncate">
            Scenario #{result.scenario_id}
          </div>
          <div className="text-xs text-text-tertiary font-mono truncate">{executor}</div>
        </div>
        <div className="text-xs text-text-disabled shrink-0 sm:hidden">
          {formatTime(result.updated_at || result.created_at)}
        </div>
      </div>
      <div className="text-xs text-text-disabled shrink-0 hidden sm:block">
        {formatTime(result.updated_at || result.created_at)}
      </div>
    </Link>
  )
}

// Active run indicator
function ActiveRunCard({ result }: { result: Result }) {
  const executorParts = [result.harness, result.provider, result.model].filter(Boolean)
  const executor = executorParts.join(':')

  return (
    <Link
      to={`/result/${result.id}`}
      className="flex items-center gap-3 p-3 bg-status-info-muted border border-status-info/30 rounded-lg hover:border-status-info transition-colors"
    >
      <div className="w-2 h-2 rounded-full bg-status-info animate-pulse" />
      <div className="flex-1 min-w-0">
        <div className="text-sm text-text-primary">Scenario #{result.scenario_id}</div>
        <div className="text-xs text-text-tertiary font-mono truncate">{executor}</div>
      </div>
      <StatusBadge status={result.status} />
    </Link>
  )
}

// Icons (using Lucide components)
const PlayIcon = () => <Play className="w-4 h-4" />
const FolderIcon = () => <Folder className="w-4 h-4" />
const LayersIcon = () => <Layers className="w-4 h-4" />
const CpuIcon = () => <Cpu className="w-4 h-4" />
const DollarIcon = () => <DollarSign className="w-4 h-4" />
const CheckIcon = () => <CheckCircle className="w-4 h-4" />
const ClockIcon = () => <Clock className="w-4 h-4" />
const StarIcon = () => <Star className="w-4 h-4" />
const ScaleIcon = () => <Scale className="w-4 h-4" />
const ChartIcon = () => <BarChart3 className="w-4 h-4" />

export default function Dashboard() {
  const { data: scenariosData, isLoading: scenariosLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: () => listScenarios(),
    refetchInterval: (query) => {
      const data = query.state.data
      const hasRunning = Object.values(data?.results_by_scenario || {})
        .flat()
        .some((r: any) => r.status === 'running' || r.status === 'queued')
      return hasRunning ? 3000 : false
    },
  })

  const { data: datasetsData, isLoading: datasetsLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: listDatasets,
  })

  const { data: executorsData } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  // Compute stats
  const stats = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    const completed = allResults.filter((r) => r.status === 'completed').length
    const failed = allResults.filter(
      (r) => r.status === 'failed' || r.status === 'infra_failure'
    ).length
    const timeout = allResults.filter((r) => r.status === 'timeout').length
    const running = allResults.filter(
      (r) => (r.status === 'running' || r.status === 'queued') && !r.is_stale
    ).length
    const totalCost = allResults.reduce((sum, r) => sum + (r.cost_usd || 0), 0)
    const successRate = allResults.length > 0 ? Math.round((completed / allResults.length) * 100) : 0

    // Calculate quality stats
    const qualityScores = allResults
      .filter((r) => r.status === 'completed' && r.quality !== null && r.quality !== undefined)
      .map((r) => r.quality as number)
    const avgQuality = qualityScores.length > 0
      ? qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length
      : null
    const ratedCount = qualityScores.length

    // Count scenarios with judges
    const scenariosWithJudges = Object.keys(scenariosData?.judges_by_scenario || {}).length

    return {
      scenarios: scenariosData?.scenarios.length || 0,
      results: allResults.length,
      completed,
      failed,
      timeout,
      running,
      totalCost,
      successRate,
      datasets: datasetsData?.datasets.length || 0,
      executors: executorsData?.harnesses.length || 0,
      avgQuality,
      ratedCount,
      scenariosWithJudges,
    }
  }, [scenariosData, datasetsData, executorsData])

  // Get recent results
  const recentResults = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    return allResults
      .sort(
        (a, b) =>
          new Date(b.updated_at || b.created_at).getTime() -
          new Date(a.updated_at || a.created_at).getTime()
      )
      .slice(0, 8)
  }, [scenariosData])

  // Get active runs
  const activeRuns = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    return allResults.filter(
      (r) => (r.status === 'running' || r.status === 'queued') && !r.is_stale
    )
  }, [scenariosData])

  const isLoading = scenariosLoading || datasetsLoading

  if (isLoading) {
    return (
      <PageLayout>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </PageLayout>
    )
  }

  const isEmpty = stats.scenarios === 0 && stats.datasets === 0

  return (
    <PageLayout>
      {isEmpty ? (
        // Empty state for new users
        <div className="mt-8">
          <Card>
            <Card.Content className="py-12">
              <div className="text-center max-w-md mx-auto">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                  <PlayIcon />
                </div>
                <h2 className="text-xl font-semibold text-text-primary mb-2">
                  Welcome to VibeLab
                </h2>
                <p className="text-text-secondary mb-6">
                  Compare AI coding agents side-by-side. Create your first run to get started.
                </p>
                <div className="flex gap-3 justify-center">
                  <Link to="/run/create">
                    <Button>Create First Run</Button>
                  </Link>
                  <Link to="/datasets/create">
                    <Button variant="secondary">Create Dataset</Button>
                  </Link>
                </div>
              </div>
            </Card.Content>
          </Card>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active Runs Alert */}
          {activeRuns.length > 0 && (
            <Card>
              <Card.Header>
                <Card.Title className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-status-info animate-pulse" />
                  Active Runs ({activeRuns.length})
                </Card.Title>
              </Card.Header>
              <Card.Content>
                <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                  {activeRuns.slice(0, 6).map((result) => (
                    <ActiveRunCard key={result.id} result={result} />
                  ))}
                </div>
                {activeRuns.length > 6 && (
                  <div className="mt-3 text-center">
                    <Link to="/runs" className="text-sm text-accent hover:text-accent-hover">
                      View all {activeRuns.length} active runs →
                    </Link>
                  </div>
                )}
              </Card.Content>
            </Card>
          )}

          {/* Stats Overview */}
          <div className="grid gap-3 sm:gap-4 [grid-template-columns:repeat(auto-fit,minmax(160px,1fr))]">
            <StatCard
              icon={<LayersIcon />}
              label="Scenarios"
              value={stats.scenarios}
              subValue={stats.scenariosWithJudges > 0 ? `${stats.scenariosWithJudges} with judges` : undefined}
              color="text-text-primary"
            />
            <StatCard
              icon={<CpuIcon />}
              label="Total Runs"
              value={stats.results}
              color="text-text-primary"
            />
            <StatCard
              icon={<CheckIcon />}
              label="Success Rate"
              value={`${stats.successRate}%`}
              subValue={`${stats.completed} completed`}
              color="text-status-success"
            />
            <StatCard
              icon={<ClockIcon />}
              label="Failed / Timeout"
              value={stats.failed + stats.timeout}
              color={stats.failed + stats.timeout > 0 ? 'text-status-error' : 'text-text-tertiary'}
            />
            <StatCard
              icon={<StarIcon />}
              label="Avg Quality"
              value={stats.avgQuality !== null ? stats.avgQuality.toFixed(1) : '—'}
              subValue={stats.ratedCount > 0 ? `${stats.ratedCount} rated` : 'No ratings yet'}
              color={
                stats.avgQuality === null ? 'text-text-tertiary' :
                stats.avgQuality >= 3.5 ? 'text-emerald-500' :
                stats.avgQuality >= 2.5 ? 'text-sky-500' :
                stats.avgQuality >= 1.5 ? 'text-amber-500' : 'text-rose-500'
              }
            />
            <StatCard
              icon={<FolderIcon />}
              label="Datasets"
              value={stats.datasets}
              color="text-text-primary"
            />
            <StatCard
              icon={<DollarIcon />}
              label="Total Cost"
              value={`$${stats.totalCost.toFixed(2)}`}
              color="text-text-primary"
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <Card className="lg:col-span-1">
              <Card.Header>
                <Card.Title>Quick Actions</Card.Title>
              </Card.Header>
              <Card.Content className="space-y-3">
                <QuickAction
                  to="/run/create"
                  icon={<PlayIcon />}
                  label="New Run"
                  description="Create a new evaluation run"
                />
                <QuickAction
                  to="/datasets/create"
                  icon={<FolderIcon />}
                  label="Create Dataset"
                  description="Group scenarios for batch evaluation"
                />
                <QuickAction
                  to="/scenarios"
                  icon={<LayersIcon />}
                  label="Browse Scenarios"
                  description="View and manage all scenarios"
                />
                <QuickAction
                  to="/executors"
                  icon={<CpuIcon />}
                  label="View Executors"
                  description="See available AI agents"
                />
                <QuickAction
                  to="/judgements"
                  icon={<ScaleIcon />}
                  label="View Judgements"
                  description="LLM judge assessments"
                />
                <QuickAction
                  to="/report"
                  icon={<ChartIcon />}
                  label="Global Report"
                  description="Quality matrix across all scenarios"
                />
              </Card.Content>
            </Card>

            {/* Recent Activity */}
            <Card className="lg:col-span-2">
              <Card.Header>
                <div className="flex items-center justify-between">
                  <Card.Title>Recent Activity</Card.Title>
                  <Link to="/runs" className="text-sm text-accent hover:text-accent-hover">
                    View all →
                  </Link>
                </div>
              </Card.Header>
              <Card.Content>
                {recentResults.length === 0 ? (
                  <div className="text-center py-8 text-text-tertiary">
                    No results yet. Create a run to get started.
                  </div>
                ) : (
                  <div className="-mx-4">
                    {recentResults.map((result) => (
                      <RecentResultRow key={result.id} result={result} />
                    ))}
                  </div>
                )}
              </Card.Content>
            </Card>
          </div>

          {/* Datasets Section */}
          {datasetsData && datasetsData.datasets.length > 0 && (
            <Card>
              <Card.Header>
                <div className="flex items-center justify-between">
                  <Card.Title>Datasets</Card.Title>
                  <Link to="/datasets" className="text-sm text-accent hover:text-accent-hover">
                    View all →
                  </Link>
                </div>
              </Card.Header>
              <Card.Content>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {datasetsData.datasets.slice(0, 6).map((dataset) => (
                    <Link
                      key={dataset.id}
                      to={`/dataset/${dataset.id}`}
                      className="p-4 bg-surface-2 rounded-lg hover:bg-surface-3 transition-colors"
                    >
                      <div className="font-medium text-text-primary">{dataset.name}</div>
                      <div className="text-xs text-text-tertiary mt-1">
                        {dataset.scenario_count} scenarios
                      </div>
                      {dataset.description && (
                        <div className="text-xs text-text-disabled mt-2 line-clamp-2">
                          {dataset.description}
                        </div>
                      )}
                    </Link>
                  ))}
                </div>
              </Card.Content>
            </Card>
          )}
        </div>
      )}
    </PageLayout>
  )
}

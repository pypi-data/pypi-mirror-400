import { useQuery } from '@tanstack/react-query'
import { Button } from '../ui'
import { RefreshCw, CheckCircle2 } from 'lucide-react'
import { getAdminScenarios, type ScenarioCacheEntry } from '../../api'

export function ScenariosSection() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['admin', 'scenarios'],
    queryFn: getAdminScenarios,
  })

  if (isLoading) return <div className="text-text-tertiary text-sm">Loading scenarios...</div>
  if (error) return <div className="text-status-error text-sm">Failed to load scenarios</div>

  const scenarios = data?.scenarios ?? []
  const totalScenarios = data?.total_scenarios ?? 0
  const withWorktrees = data?.scenarios_with_worktrees ?? 0

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs text-text-tertiary">
          {totalScenarios} scenarios • {withWorktrees} with active worktrees
        </div>
        <Button variant="ghost" size="sm" onClick={() => refetch()}>
          <RefreshCw className="w-3.5 h-3.5" />
        </Button>
      </div>

      {scenarios.length === 0 ? (
        <div className="text-center py-6 text-text-tertiary text-sm">No scenarios yet</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="py-1.5 pr-3 font-medium text-text-secondary">ID</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary">Type</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary">Prompt</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary text-right">Results</th>
                <th className="py-1.5 font-medium text-text-secondary text-center">Worktree</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((scenario: ScenarioCacheEntry) => (
                <tr key={scenario.scenario_id} className="border-b border-border-muted">
                  <td className="py-1.5 pr-3 font-mono text-xs text-accent">#{scenario.scenario_id}</td>
                  <td className="py-1.5 pr-3 text-xs text-text-tertiary">{scenario.code_type}</td>
                  <td className="py-1.5 pr-3 text-xs text-text-secondary max-w-xs truncate">{scenario.prompt_preview}</td>
                  <td className="py-1.5 pr-3 text-xs text-text-tertiary text-right">{scenario.result_count}</td>
                  <td className="py-1.5 text-center">
                    {scenario.has_worktree ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-status-success inline" />
                    ) : (
                      <span className="text-text-disabled">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


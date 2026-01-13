import { useQuery } from '@tanstack/react-query'
import { Button } from '../ui'
import { FolderGit2, RefreshCw } from 'lucide-react'
import { getAdminRepos, type RepoInfo } from '../../api'

export function ReposSection() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['admin', 'repos'],
    queryFn: getAdminRepos,
  })

  if (isLoading) return <div className="text-text-tertiary text-sm">Loading repositories...</div>
  if (error) return <div className="text-status-error text-sm">Failed to load repositories</div>

  const repos = data?.repos ?? []
  const totalSize = data?.total_size_mb ?? 0

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs text-text-tertiary">
          {repos.length} cached {repos.length === 1 ? 'repository' : 'repositories'} • {totalSize.toFixed(1)} MB
        </div>
        <Button variant="ghost" size="sm" onClick={() => refetch()}>
          <RefreshCw className="w-3.5 h-3.5" />
        </Button>
      </div>

      {repos.length === 0 ? (
        <div className="text-center py-6 text-text-tertiary text-sm">No cached repositories yet</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="py-1.5 pr-3 font-medium text-text-secondary">Repository</th>
                <th className="py-1.5 font-medium text-text-secondary text-right">Size</th>
              </tr>
            </thead>
            <tbody>
              {repos.map((repo: RepoInfo) => (
                <tr key={repo.path} className="border-b border-border-muted">
                  <td className="py-1.5 pr-3">
                    <div className="flex items-center gap-2">
                      <FolderGit2 className="w-3.5 h-3.5 text-text-tertiary shrink-0" />
                      <span className="font-mono text-xs text-text-primary">
                        {repo.host}/{repo.owner}/{repo.repo}
                      </span>
                    </div>
                  </td>
                  <td className="py-1.5 text-right text-xs text-text-tertiary">{repo.size_mb.toFixed(1)} MB</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="text-[10px] text-text-disabled font-mono">{data?.repos_dir}</div>
    </div>
  )
}


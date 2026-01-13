import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '../ui'
import { ChevronRight, ChevronUp, Folder, File, RefreshCw } from 'lucide-react'
import { cn } from '../../lib/cn'
import { browseAdminFiles, type FileEntry } from '../../api'

export function FileBrowserSection() {
  const [currentPath, setCurrentPath] = useState('')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['admin', 'files', currentPath],
    queryFn: () => browseAdminFiles(currentPath),
  })

  const navigateTo = (path: string) => setCurrentPath(path)

  const goUp = () => {
    if (data?.parent_path !== null && data?.parent_path !== undefined) {
      setCurrentPath(data.parent_path)
    }
  }

  if (isLoading) return <div className="text-text-tertiary text-sm">Loading files...</div>
  if (error) return <div className="text-status-error text-sm">Failed to load files</div>

  const entries = data?.entries ?? []
  const canGoUp = data?.parent_path !== null && data?.parent_path !== undefined

  const formatSize = (bytes: number | null): string => {
    if (bytes === null) return '—'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={goUp} disabled={!canGoUp} className="shrink-0">
          <ChevronUp className="w-4 h-4" />
        </Button>
        <div className="flex-1 font-mono text-xs text-text-tertiary bg-surface-2 px-2 py-1 rounded overflow-x-auto">
          ~/{data?.current_path || ''}
        </div>
        <Button variant="ghost" size="sm" onClick={() => refetch()} className="shrink-0">
          <RefreshCw className="w-3.5 h-3.5" />
        </Button>
      </div>

      {entries.length === 0 ? (
        <div className="text-center py-6 text-text-tertiary text-sm">Empty directory</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="py-1.5 pr-3 font-medium text-text-secondary">Name</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary text-right">Size</th>
                <th className="py-1.5 font-medium text-text-secondary hidden sm:table-cell">Modified</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry: FileEntry) => (
                <tr
                  key={entry.path}
                  className={cn('border-b border-border-muted', entry.is_dir && 'cursor-pointer hover:bg-surface-2')}
                  onClick={() => entry.is_dir && navigateTo(entry.path)}
                >
                  <td className="py-1.5 pr-3">
                    <div className="flex items-center gap-2">
                      {entry.is_dir ? (
                        <Folder className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                      ) : (
                        <File className="w-3.5 h-3.5 text-text-tertiary shrink-0" />
                      )}
                      <span className={cn('text-xs', entry.is_dir ? 'text-text-primary font-medium' : 'text-text-secondary')}>
                        {entry.name}
                      </span>
                      {entry.is_dir && <ChevronRight className="w-3 h-3 text-text-disabled ml-auto" />}
                    </div>
                  </td>
                  <td className="py-1.5 pr-3 text-xs text-text-tertiary text-right whitespace-nowrap">
                    {formatSize(entry.size_bytes)}
                  </td>
                  <td className="py-1.5 text-xs text-text-disabled hidden sm:table-cell whitespace-nowrap">
                    {entry.modified_at ? new Date(entry.modified_at).toLocaleString() : '—'}
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


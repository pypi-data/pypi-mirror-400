import { useState, Fragment, useMemo } from 'react'
import { cn } from '../lib/cn'
import { parseUnifiedDiff, type ParsedFile, type DiffLine } from '../lib/diffUtils'
import { File } from 'lucide-react'

interface GitHubDiffViewerProps {
  patch: string
  maxHeight?: string
}

const FileIcon = () => <File className="w-4 h-4 text-text-tertiary flex-shrink-0" />

function SingleFileDiff({ file, defaultExpanded = true }: { file: ParsedFile; defaultExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [expandedHunks, setExpandedHunks] = useState<Set<number>>(new Set([0]))

  // Group lines into hunks
  const hunks = useMemo(() => {
    const result: Array<{ startIdx: number; endIdx: number }> = []
    let currentHunk: { startIdx: number; endIdx: number } | null = null

    file.lines.forEach((line, idx) => {
      if (line.type === 'hunk') {
        if (currentHunk) {
          currentHunk.endIdx = idx - 1
          result.push(currentHunk)
        }
        currentHunk = { startIdx: idx, endIdx: file.lines.length - 1 }
      }
    })
    if (currentHunk) {
      result.push(currentHunk)
    }
    // If no hunks found, treat entire diff as one hunk
    if (result.length === 0 && file.lines.length > 0) {
      result.push({ startIdx: 0, endIdx: file.lines.length - 1 })
    }
    return result
  }, [file.lines])

  const toggleHunk = (hunkIdx: number) => {
    setExpandedHunks((prev) => {
      const next = new Set(prev)
      if (next.has(hunkIdx)) {
        next.delete(hunkIdx)
      } else {
        next.add(hunkIdx)
      }
      return next
    })
  }

  const renderLine = (line: DiffLine, idx: number) => {
    const bgClass = {
      added: 'bg-status-success-muted',
      removed: 'bg-status-error-muted',
      context: 'bg-transparent',
      hunk: 'bg-status-info-muted',
    }[line.type]

    const textClass = {
      added: 'text-status-success',
      removed: 'text-status-error',
      context: 'text-text-secondary',
      hunk: 'text-status-info',
    }[line.type]

    return (
      <tr key={idx} className={cn('hover:brightness-95 dark:hover:brightness-110 transition-all', bgClass)}>
        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-xs text-text-disabled select-none border-r border-border-muted tabular-nums">
          {line.oldLineNumber !== null ? line.oldLineNumber : ''}
        </td>
        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-xs text-text-disabled select-none border-r border-border-muted tabular-nums">
          {line.newLineNumber !== null ? line.newLineNumber : ''}
        </td>
        <td className={cn('px-3 py-0.5 text-sm font-mono whitespace-pre', textClass)}>
          {line.type === 'hunk' ? (
            <span className="font-semibold">{line.content}</span>
          ) : (
            <span>{line.content || ' '}</span>
          )}
        </td>
      </tr>
    )
  }

  const displayPath = file.newPath || file.oldPath || 'changes'
  const isNewFile = !file.oldPath && file.newPath
  const isDeletedFile = file.oldPath && !file.newPath

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface">
      {/* File header */}
      <div 
        className="bg-surface-2 border-b border-border px-3 py-2 flex items-center gap-2 cursor-pointer hover:bg-surface-3 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <button className="text-text-tertiary hover:text-text-secondary flex-shrink-0">
          <span className="text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
        <FileIcon />
        <span className="font-mono text-sm text-text-primary truncate flex-1">
          {displayPath}
        </span>
        {isNewFile && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-status-success-muted text-status-success">new</span>
        )}
        {isDeletedFile && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-status-error-muted text-status-error">deleted</span>
        )}
        <div className="flex items-center gap-2 text-xs flex-shrink-0">
          {file.additions > 0 && (
            <span className="text-status-success font-medium">+{file.additions}</span>
          )}
          {file.deletions > 0 && (
            <span className="text-status-error font-medium">−{file.deletions}</span>
          )}
        </div>
      </div>

      {/* Diff content */}
      {expanded && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <tbody>
              {hunks.map((hunk, hunkIdx) => {
                const isHunkExpanded = expandedHunks.has(hunkIdx)
                const hunkLine = file.lines[hunk.startIdx]
                const startContentIdx = hunkLine?.type === 'hunk' ? hunk.startIdx + 1 : hunk.startIdx
                const hunkLines = file.lines.slice(startContentIdx, hunk.endIdx + 1)

                return (
                  <Fragment key={hunkIdx}>
                    {hunkLine?.type === 'hunk' && (
                      <tr className="bg-surface-2 hover:bg-surface-3 transition-colors">
                        <td colSpan={3} className="px-3 py-2">
                          <button
                            onClick={(e) => { e.stopPropagation(); toggleHunk(hunkIdx) }}
                            className="flex items-center gap-2 w-full text-left text-xs text-text-tertiary hover:text-text-secondary transition-colors"
                          >
                            <span className="text-text-disabled">{isHunkExpanded ? '▼' : '▶'}</span>
                            <span className="font-mono text-status-info">{hunkLine.content}</span>
                            <span className="text-text-disabled">
                              ({hunkLines.length} line{hunkLines.length !== 1 ? 's' : ''})
                            </span>
                          </button>
                        </td>
                      </tr>
                    )}
                    {isHunkExpanded &&
                      hunkLines.map((line, lineIdx) => renderLine(line, startContentIdx + lineIdx))}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function GitHubDiffViewer({ patch, maxHeight = '600px' }: GitHubDiffViewerProps) {
  const parsed = useMemo(() => parseUnifiedDiff(patch), [patch])

  if (parsed.files.length === 0) {
    return (
      <div className="border border-border rounded-lg p-8 text-text-tertiary text-sm text-center">
        No changes to display
      </div>
    )
  }

  const totalAdditions = parsed.files.reduce((sum, f) => sum + f.additions, 0)
  const totalDeletions = parsed.files.reduce((sum, f) => sum + f.deletions, 0)

  return (
    <div className="space-y-3" style={{ maxHeight, overflowY: 'auto' }}>
      {/* Summary header */}
      <div className="flex items-center gap-4 text-sm text-text-secondary">
        <span>
          Showing <strong className="text-text-primary">{parsed.files.length}</strong> changed {parsed.files.length === 1 ? 'file' : 'files'}
        </span>
        {totalAdditions > 0 && <span className="text-status-success font-medium">+{totalAdditions}</span>}
        {totalDeletions > 0 && <span className="text-status-error font-medium">−{totalDeletions}</span>}
      </div>

      {/* File diffs */}
      {parsed.files.map((file, idx) => (
        <SingleFileDiff key={idx} file={file} defaultExpanded={parsed.files.length <= 3} />
      ))}
    </div>
  )
}

// Re-export SingleFileDiff for use in other components
export { SingleFileDiff }

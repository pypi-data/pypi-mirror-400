import { useState, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import CodeMirror from '@uiw/react-codemirror'
import { sql, SQLite } from '@codemirror/lang-sql'
import { oneDark } from '@codemirror/theme-one-dark'
import { Button } from '../ui'
import { Play, AlertCircle, Download, Copy, X } from 'lucide-react'
import { cn } from '../../lib/cn'
import { getAdminSchema, executeAdminQuery, type TableInfo, type QueryResponse } from '../../api'
import { useTheme } from './useTheme'

export function SQLiteSection() {
  const [query, setQuery] = useState('SELECT * FROM scenarios LIMIT 10')
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [copyStatus, setCopyStatus] = useState<string | null>(null)
  const [selectedRow, setSelectedRow] = useState<number | null>(null)
  const theme = useTheme()

  const { data: schema, isLoading: schemaLoading } = useQuery({
    queryKey: ['admin', 'schema'],
    queryFn: getAdminSchema,
  })

  const mutation = useMutation({
    mutationFn: executeAdminQuery,
    onSuccess: (data) => {
      setResult(data)
      setSelectedRow(null)
    },
    onError: () => setResult({ columns: [], rows: [], row_count: 0, error: 'Request failed' }),
  })

  const executeQuery = useCallback(() => {
    mutation.mutate(query)
  }, [query, mutation])

  const insertTableQuery = (tableName: string) => {
    setQuery(`SELECT * FROM ${tableName} LIMIT 100`)
  }

  const copyResultsAsCSV = () => {
    if (!result || result.error || result.columns.length === 0) return
    const csv = [
      result.columns.join(','),
      ...result.rows.map(row => 
        row.map(cell => {
          if (cell === null) return ''
          const str = typeof cell === 'object' ? JSON.stringify(cell) : String(cell)
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str
        }).join(',')
      )
    ].join('\n')
    navigator.clipboard.writeText(csv)
    setCopyStatus('CSV')
    setTimeout(() => setCopyStatus(null), 1500)
  }

  const copyResultsAsJSON = () => {
    if (!result || result.error || result.columns.length === 0) return
    const json = result.rows.map(row => {
      const obj: Record<string, unknown> = {}
      result.columns.forEach((col, i) => { obj[col] = row[i] })
      return obj
    })
    navigator.clipboard.writeText(JSON.stringify(json, null, 2))
    setCopyStatus('JSON')
    setTimeout(() => setCopyStatus(null), 1500)
  }

  const downloadCSV = () => {
    if (!result || result.error || result.columns.length === 0) return
    const csv = [
      result.columns.join(','),
      ...result.rows.map(row => 
        row.map(cell => {
          if (cell === null) return ''
          const str = typeof cell === 'object' ? JSON.stringify(cell) : String(cell)
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str
        }).join(',')
      )
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'query_results.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleEditorKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      executeQuery()
    }
  }, [executeQuery])

  const selectedRowData = selectedRow !== null && result && result.rows[selectedRow]
    ? result.columns.reduce((obj, col, i) => {
        obj[col] = result.rows[selectedRow][i]
        return obj
      }, {} as Record<string, unknown>)
    : null

  return (
    <div className="space-y-4">
      {/* Editor area */}
      <div className="flex gap-4">
        {/* Tables sidebar */}
        <div className="w-40 shrink-0">
          <div className="text-[11px] font-medium text-text-secondary mb-2">
            Tables <span className="text-text-disabled">(v{schema?.schema_version ?? 0})</span>
          </div>
          {schemaLoading ? (
            <div className="text-text-tertiary text-xs">Loading...</div>
          ) : (
            <div className="border border-border rounded bg-surface-2 overflow-hidden">
              <div className="max-h-28 overflow-y-auto">
                {schema?.tables.map((table: TableInfo) => (
                  <button
                    key={table.name}
                    onClick={() => insertTableQuery(table.name)}
                    className="w-full text-left px-2 py-1 text-[11px] font-mono text-text-secondary hover:bg-surface hover:text-text-primary flex items-center justify-between transition-colors"
                  >
                    <span className="truncate">{table.name}</span>
                    <span className="text-text-disabled text-[10px] ml-1">{table.row_count}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Editor */}
        <div className="flex-1">
          <div className="relative" onKeyDown={handleEditorKeyDown}>
            <CodeMirror
              value={query}
              onChange={setQuery}
              height="112px"
              theme={theme === 'dark' ? oneDark : undefined}
              extensions={[sql({ dialect: SQLite })]}
              placeholder="SELECT * FROM ..."
              basicSetup={{
                lineNumbers: true,
                highlightActiveLineGutter: true,
                highlightActiveLine: true,
                foldGutter: false,
                dropCursor: true,
                allowMultipleSelections: true,
                indentOnInput: true,
                bracketMatching: true,
                closeBrackets: true,
                autocompletion: true,
                highlightSelectionMatches: true,
              }}
              className={cn(
                "rounded overflow-hidden border text-[13px]",
                theme === 'dark' ? "border-border" : "border-gray-300"
              )}
            />
            <div className={cn(
              "absolute bottom-1 right-2 text-[10px] px-1 py-0.5 rounded opacity-60",
              theme === 'dark' ? "text-gray-500 bg-[#282c34]" : "text-gray-400 bg-gray-100"
            )}>
              ⌘↵
            </div>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Button onClick={executeQuery} disabled={mutation.isPending || !query.trim()} size="sm">
              <Play className="w-3 h-3 mr-1" />
              {mutation.isPending ? 'Running...' : 'Run'}
            </Button>
            <span className="text-[10px] text-text-disabled">Read-only queries only</span>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-2">
          {result.error ? (
            <div className="flex items-center gap-2 text-status-error text-sm bg-status-error/10 px-3 py-2 rounded">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <code className="text-xs">{result.error}</code>
            </div>
          ) : (
            <>
              {/* Results header */}
              <div className="flex items-center justify-between">
                <div className="text-[11px] text-text-tertiary">
                  {result.row_count} row{result.row_count !== 1 ? 's' : ''}
                  {selectedRow !== null && (
                    <span className="ml-1.5 text-accent">• Row {selectedRow + 1}</span>
                  )}
                </div>
                {result.columns.length > 0 && (
                  <div className="flex items-center gap-1">
                    {copyStatus && (
                      <span className="text-[10px] text-status-success mr-1">Copied {copyStatus}!</span>
                    )}
                    <button onClick={copyResultsAsCSV} className="p-1 text-text-tertiary hover:text-text-primary" title="Copy CSV">
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={copyResultsAsJSON} className="p-1 text-text-tertiary hover:text-text-primary" title="Copy JSON">
                      <span className="text-[10px] font-mono">{'{}'}</span>
                    </button>
                    <button onClick={downloadCSV} className="p-1 text-text-tertiary hover:text-text-primary" title="Download">
                      <Download className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>

              {/* Table + Detail panel */}
              <div className="flex gap-3">
                {result.columns.length > 0 && (
                  <div className={cn(
                    "flex-1 overflow-auto border border-border rounded",
                    selectedRow !== null ? "max-h-64" : "max-h-80"
                  )}>
                    <table className="w-full text-[11px]">
                      <thead className="sticky top-0 bg-surface-2">
                        <tr className="border-b border-border">
                          <th className="px-1.5 py-1 text-center font-mono text-text-disabled w-7">#</th>
                          {result.columns.map((col, i) => (
                            <th key={i} className="px-2 py-1 text-left font-mono font-medium text-text-secondary whitespace-nowrap">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.rows.map((row, i) => (
                          <tr 
                            key={i} 
                            className={cn(
                              "border-b border-border-muted cursor-pointer transition-colors",
                              selectedRow === i ? "bg-accent/15" : "hover:bg-surface-2"
                            )}
                            onClick={() => setSelectedRow(selectedRow === i ? null : i)}
                          >
                            <td className="px-1.5 py-0.5 text-center font-mono text-text-disabled text-[10px]">{i + 1}</td>
                            {row.map((cell, j) => (
                              <td key={j} className="px-2 py-0.5 font-mono text-text-primary max-w-[180px] truncate">
                                {cell === null ? (
                                  <span className="text-text-disabled italic">NULL</span>
                                ) : typeof cell === 'object' ? (
                                  <span className="text-amber-500">{JSON.stringify(cell).slice(0, 40)}…</span>
                                ) : typeof cell === 'number' ? (
                                  <span className="text-cyan-500">{cell}</span>
                                ) : (
                                  String(cell).length > 60 ? String(cell).slice(0, 60) + '…' : String(cell)
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Detail panel */}
                {selectedRowData && (
                  <div className="w-72 shrink-0 border border-border rounded bg-surface-2 overflow-hidden">
                    <div className="px-2 py-1.5 border-b border-border bg-surface-3 flex items-center justify-between">
                      <span className="text-[11px] font-medium text-text-secondary">Row {selectedRow! + 1}</span>
                      <button onClick={() => setSelectedRow(null)} className="text-text-tertiary hover:text-text-primary">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="p-2 overflow-y-auto max-h-56 space-y-2">
                      {Object.entries(selectedRowData).map(([key, value]) => (
                        <div key={key}>
                          <div className="font-mono text-[10px] text-text-tertiary mb-0.5">{key}</div>
                          <div className={cn(
                            "font-mono text-[11px] p-1.5 rounded bg-surface break-all whitespace-pre-wrap",
                            value === null ? "text-text-disabled italic" 
                              : typeof value === 'number' ? "text-cyan-500"
                              : typeof value === 'object' ? "text-amber-500"
                              : "text-text-primary"
                          )}>
                            {value === null ? 'NULL' 
                              : typeof value === 'object' ? JSON.stringify(value, null, 2)
                              : String(value)
                            }
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}


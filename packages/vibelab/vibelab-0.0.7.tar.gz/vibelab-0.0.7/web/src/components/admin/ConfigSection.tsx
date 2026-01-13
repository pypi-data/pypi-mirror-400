import { useQuery } from '@tanstack/react-query'
import { getAdminConfig } from '../../api'

export function ConfigSection() {
  const { data: config, isLoading, error } = useQuery({
    queryKey: ['admin', 'config'],
    queryFn: getAdminConfig,
  })

  if (isLoading) return <div className="text-text-tertiary text-sm">Loading configuration...</div>
  if (error) return <div className="text-status-error text-sm">Failed to load configuration</div>

  const configItems: Array<{ label: string; value: string | number | null; description?: string }> = [
    { label: 'VIBELAB_HOME', value: config?.vibelab_home ?? null, description: 'Root data directory' },
    { label: 'Project', value: config?.project ?? null, description: 'Current project name' },
    { label: 'Project Home', value: config?.project_home ?? null, description: 'Project-specific directory' },
    { label: 'Database Path', value: config?.db_path ?? null, description: 'SQLite database file' },
    { label: 'Repos Directory', value: config?.repos_dir ?? null, description: 'Shared bare clones' },
    { label: 'Log Level', value: config?.log_level ?? null, description: 'VIBELAB_LOG_LEVEL' },
    { label: 'SQLite Busy Timeout', value: config?.sqlite_busy_timeout_ms ? `${config.sqlite_busy_timeout_ms}ms` : null, description: 'VIBELAB_SQLITE_BUSY_TIMEOUT_MS' },
    { label: 'Default Driver', value: config?.default_driver ?? null, description: 'VIBELAB_DRIVER' },
    { label: 'Default Timeout', value: config?.default_timeout ? `${config.default_timeout}s` : null, description: 'VIBELAB_TIMEOUT' },
    { label: 'OCI Runtime', value: config?.oci_runtime ?? '(auto-detect)', description: 'VIBELAB_OCI_RUNTIME' },
  ]

  const imageOverrides: Array<{ label: string; value: string | null }> = [
    { label: 'Claude Code Image', value: config?.claude_code_image ?? null },
    { label: 'OpenAI Codex Image', value: config?.openai_codex_image ?? null },
    { label: 'Cursor Image', value: config?.cursor_image ?? null },
    { label: 'Gemini Image', value: config?.gemini_image ?? null },
  ]

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="py-1.5 pr-3 font-medium text-text-secondary">Setting</th>
              <th className="py-1.5 pr-3 font-medium text-text-secondary">Value</th>
              <th className="py-1.5 font-medium text-text-secondary hidden md:table-cell">Description</th>
            </tr>
          </thead>
          <tbody>
            {configItems.map((item) => (
              <tr key={item.label} className="border-b border-border-muted">
                <td className="py-1.5 pr-3 font-mono text-xs text-text-primary">{item.label}</td>
                <td className="py-1.5 pr-3 font-mono text-xs text-accent break-all max-w-md">
                  {item.value ?? <span className="text-text-disabled">—</span>}
                </td>
                <td className="py-1.5 text-xs text-text-tertiary hidden md:table-cell">{item.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {imageOverrides.some((i) => i.value) && (
        <div>
          <h4 className="text-xs font-medium text-text-secondary mb-1.5">Container Image Overrides</h4>
          <div className="space-y-0.5">
            {imageOverrides.filter((i) => i.value).map((item) => (
              <div key={item.label} className="flex gap-2 text-xs">
                <span className="text-text-tertiary">{item.label}:</span>
                <span className="font-mono text-accent">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


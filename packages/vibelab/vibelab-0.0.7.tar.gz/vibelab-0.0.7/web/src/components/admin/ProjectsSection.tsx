import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '../ui'
import { RefreshCw, AlertCircle, FolderKanban, Plus, Check } from 'lucide-react'
import { cn } from '../../lib/cn'
import {
  listProjects,
  createProject,
  getCurrentProject,
  setCurrentProject,
  type ProjectWithStats,
} from '../../api'

export function ProjectsSection() {
  const queryClient = useQueryClient()
  const [currentProjectName, setCurrentProjectName] = useState(getCurrentProject())
  const [newProjectName, setNewProjectName] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const { data: projects, isLoading, error, refetch } = useQuery({
    queryKey: ['projects'],
    queryFn: listProjects,
  })

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      setNewProjectName('')
      setIsCreating(false)
      refetch()
    },
  })

  // Listen for project changes from other components
  useEffect(() => {
    const handler = (e: CustomEvent<string>) => {
      setCurrentProjectName(e.detail)
    }
    window.addEventListener('vibelab-project-changed', handler as EventListener)
    return () => window.removeEventListener('vibelab-project-changed', handler as EventListener)
  }, [])

  const handleSwitchProject = (projectName: string) => {
    setCurrentProject(projectName)
    setCurrentProjectName(projectName)
    queryClient.invalidateQueries()
  }

  const handleCreateProject = () => {
    if (newProjectName.trim()) {
      createMutation.mutate({ name: newProjectName.trim() })
    }
  }

  if (isLoading) return <div className="text-text-tertiary text-sm">Loading projects...</div>
  if (error) return <div className="text-status-error text-sm">Failed to load projects</div>

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs text-text-tertiary">
          {projects?.length ?? 0} {(projects?.length ?? 0) === 1 ? 'project' : 'projects'}
        </div>
        <div className="flex items-center gap-1">
          {!isCreating && (
            <Button variant="ghost" size="sm" onClick={() => setIsCreating(true)}>
              <Plus className="w-3.5 h-3.5 mr-1" />
              New
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => refetch()}>
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {isCreating && (
        <div className="flex items-center gap-2 p-2 bg-surface-2 rounded">
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="Project name"
            className="flex-1 px-2 py-1 bg-surface border border-border rounded text-sm text-text-primary placeholder:text-text-disabled focus:outline-none focus:border-accent"
            onKeyDown={(e) => e.key === 'Enter' && handleCreateProject()}
            autoFocus
          />
          <Button size="sm" onClick={handleCreateProject} disabled={!newProjectName.trim() || createMutation.isPending}>
            Create
          </Button>
          <Button variant="ghost" size="sm" onClick={() => { setIsCreating(false); setNewProjectName('') }}>
            Cancel
          </Button>
        </div>
      )}

      {createMutation.isError && (
        <div className="flex items-center gap-2 text-status-error text-xs">
          <AlertCircle className="w-3.5 h-3.5" />
          {(createMutation.error as Error)?.message || 'Failed to create project'}
        </div>
      )}

      {(!projects || projects.length === 0) ? (
        <div className="text-center py-6 text-text-tertiary text-sm">
          No projects yet. Create one to get started.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="py-1.5 pr-3 font-medium text-text-secondary w-6"></th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary">Name</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary text-right">Scenarios</th>
                <th className="py-1.5 pr-3 font-medium text-text-secondary text-right">Datasets</th>
                <th className="py-1.5 font-medium text-text-secondary text-right">Tasks</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project: ProjectWithStats) => {
                const isActive = project.name === currentProjectName
                return (
                  <tr
                    key={project.id}
                    className={cn(
                      'border-b border-border-muted cursor-pointer hover:bg-surface-2 transition-colors',
                      isActive && 'bg-accent/10'
                    )}
                    onClick={() => handleSwitchProject(project.name)}
                  >
                    <td className="py-1.5 pr-3">
                      {isActive && <Check className="w-3.5 h-3.5 text-accent" />}
                    </td>
                    <td className="py-1.5 pr-3">
                      <div className="flex items-center gap-2">
                        <FolderKanban className="w-3.5 h-3.5 text-text-tertiary shrink-0" />
                        <span className={cn("font-mono text-xs", isActive ? "text-accent font-semibold" : "text-text-primary")}>
                          {project.name}
                        </span>
                      </div>
                    </td>
                    <td className="py-1.5 pr-3 text-right text-xs text-text-tertiary">{project.scenario_count}</td>
                    <td className="py-1.5 pr-3 text-right text-xs text-text-tertiary">{project.dataset_count}</td>
                    <td className="py-1.5 text-right text-xs text-text-tertiary">{project.task_count}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="text-[10px] text-text-disabled">
        Current: <span className="font-mono text-accent">{currentProjectName}</span>
      </div>
    </div>
  )
}


import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { cancelQueuedTasks, cancelTask, listActiveTasks, promoteTask, Task } from '../api'
import { Button, ConfirmDialog, EmptyState, FullPageTableLayout, StatusBadge, Table } from './ui'
import { useMemo, useState } from 'react'

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function jobTitle(t: Task): string {
  if (t.task_type === 'agent_run') {
    return `Run result ${t.result_id ?? '—'}`
  }
  if (t.task_type === 'judge_result') {
    return `Judge result ${t.target_result_id ?? '—'}`
  }
  if (t.task_type === 'train_judge') {
    return `Train judge ${t.judge_id ?? '—'}`
  }
  return t.task_type
}

function primaryLink(t: Task): { label: string; to: string } | null {
  if (t.task_type === 'agent_run' && t.result_id != null) {
    return { label: `Result ${t.result_id}`, to: `/result/${t.result_id}` }
  }
  if (t.task_type === 'judge_result' && t.target_result_id != null) {
    return { label: `Result ${t.target_result_id}`, to: `/result/${t.target_result_id}` }
  }
  return null
}

export default function ActiveJobs() {
  const queryClient = useQueryClient()
  const [cancelTarget, setCancelTarget] = useState<Task | null>(null)
  const [showCancelQueueDialog, setShowCancelQueueDialog] = useState(false)

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', 'active'],
    queryFn: () => listActiveTasks(200),
    refetchInterval: 1000,
  })

  const promoteMutation = useMutation({
    mutationFn: (taskId: number) => promoteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', 'active'] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: (taskId: number) => cancelTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', 'active'] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setCancelTarget(null)
    },
  })

  const cancelQueueMutation = useMutation({
    mutationFn: () => cancelQueuedTasks(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', 'active'] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setShowCancelQueueDialog(false)
    },
  })

  const rows = useMemo(() => (tasks ?? []).slice(), [tasks])
  const queuedCount = useMemo(() => rows.filter((t) => t.status === 'queued').length, [rows])
  const runningCount = useMemo(() => rows.filter((t) => t.status === 'running').length, [rows])

  const header = (
    <FullPageTableLayout.Header
      title="Active Jobs"
      count={rows.length}
      countLabel={`${runningCount} running, ${queuedCount} queued`}
      description="Queued and running jobs (runs + judgements)"
      actions={
        <div className="flex items-center gap-2">
          {queuedCount > 0 && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowCancelQueueDialog(true)}
            >
              Cancel Queue ({queuedCount})
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['tasks', 'active'] })
            }}
          >
            Refresh
          </Button>
        </div>
      }
    />
  )

  if (isLoading) {
    return (
      <FullPageTableLayout header={header} isEmpty>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </FullPageTableLayout>
    )
  }

  return (
    <>
      <FullPageTableLayout
        header={header}
        isEmpty={rows.length === 0}
        emptyState={
          <EmptyState
            title="No active jobs"
            description="Nothing is currently queued or running."
          />
        }
      >
        <Table fullPage maxHeight="full">
          <Table.Header>
            <tr>
              <Table.Head className="pl-6">ID</Table.Head>
              <Table.Head>Type</Table.Head>
              <Table.Head>Status</Table.Head>
              <Table.Head>Priority</Table.Head>
              <Table.Head>Created</Table.Head>
              <Table.Head>Started</Table.Head>
              <Table.Head>Worker</Table.Head>
              <Table.Head>Link</Table.Head>
              <Table.Head className="pr-6"></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {rows.map((t) => {
              const link = primaryLink(t)
              const canPromote = t.status === 'queued'
              const canCancel = t.status === 'queued' || t.status === 'running'
              return (
                <Table.Row key={t.id}>
                  <Table.Cell mono className="text-text-tertiary text-xs pl-6">
                    {t.id}
                  </Table.Cell>
                  <Table.Cell className="text-sm">
                    {jobTitle(t)}
                  </Table.Cell>
                  <Table.Cell>
                    <StatusBadge status={t.status} />
                  </Table.Cell>
                  <Table.Cell mono className="text-text-secondary text-xs">
                    {t.priority}
                  </Table.Cell>
                  <Table.Cell className="text-text-tertiary text-xs">
                    {formatDate(t.created_at)}
                  </Table.Cell>
                  <Table.Cell className="text-text-tertiary text-xs">
                    {t.started_at ? formatDate(t.started_at) : '—'}
                  </Table.Cell>
                  <Table.Cell mono className="text-text-tertiary text-xs">
                    {t.worker_id || '—'}
                  </Table.Cell>
                  <Table.Cell className="text-sm">
                    {link ? (
                      <Link to={link.to} className="text-accent hover:text-accent-hover">
                        {link.label}
                      </Link>
                    ) : (
                      <span className="text-text-disabled">—</span>
                    )}
                  </Table.Cell>
                  <Table.Cell className="pr-6">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => promoteMutation.mutate(t.id)}
                        disabled={!canPromote || promoteMutation.isPending}
                      >
                        Promote
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => setCancelTarget(t)}
                        disabled={!canCancel || cancelMutation.isPending}
                      >
                        Cancel
                      </Button>
                    </div>
                  </Table.Cell>
                </Table.Row>
              )
            })}
          </Table.Body>
        </Table>
      </FullPageTableLayout>

      <ConfirmDialog
        open={cancelTarget !== null}
        onClose={() => setCancelTarget(null)}
        onConfirm={() => {
          if (cancelTarget) cancelMutation.mutate(cancelTarget.id)
        }}
        title="Cancel Job"
        description={
          cancelTarget
            ? `Cancel task ${cancelTarget.id}? If it is running, we will send SIGTERM to its process group.`
            : ''
        }
        confirmLabel="Cancel"
        danger
        loading={cancelMutation.isPending}
      />

      <ConfirmDialog
        open={showCancelQueueDialog}
        onClose={() => setShowCancelQueueDialog(false)}
        onConfirm={() => cancelQueueMutation.mutate()}
        title="Cancel Entire Queue"
        description={`Cancel all ${queuedCount} queued job${queuedCount === 1 ? '' : 's'}? This will not affect currently running jobs.`}
        confirmLabel="Cancel Queue"
        danger
        loading={cancelQueueMutation.isPending}
      />
    </>
  )
}

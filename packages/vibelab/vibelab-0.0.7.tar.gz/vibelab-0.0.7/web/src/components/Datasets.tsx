import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { listDatasets, deleteDataset } from '../api'
import { FullPageTableLayout, Table, EmptyState, Button, ConfirmDialog, DropdownMenu, DropdownItem, OverflowMenuTrigger } from './ui'
import { useState } from 'react'

export default function Datasets() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null)
  
  const { data, isLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: listDatasets,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteDataset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
      setDeleteTarget(null)
    },
  })

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const datasets = data?.datasets || []

  const header = (
    <FullPageTableLayout.Header
      title="Datasets"
      count={datasets.length}
      countLabel={datasets.length === 1 ? 'dataset' : 'datasets'}
      description="Collections of scenarios for evaluation"
      actions={
        <Link to="/dataset/create">
          <Button>New Dataset</Button>
        </Link>
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
        isEmpty={datasets.length === 0}
        emptyState={
          <EmptyState
            title="No datasets yet"
            description="Create your first dataset to organize scenarios."
            action={
              <Link to="/dataset/create">
                <Button>Create Dataset</Button>
              </Link>
            }
          />
        }
      >
        <Table fullPage maxHeight="full">
          <Table.Header>
            <tr>
              <Table.Head className="pl-6 w-16">ID</Table.Head>
              <Table.Head>Name</Table.Head>
              <Table.Head className="w-[40%]">Description</Table.Head>
              <Table.Head>Scenarios</Table.Head>
              <Table.Head>Created</Table.Head>
              <Table.Head className="pr-6 w-[180px]"></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {datasets.map((dataset) => (
              <Table.Row 
                key={dataset.id}
                className="cursor-pointer"
                onClick={() => navigate(`/dataset/${dataset.id}`)}
              >
                <Table.Cell mono className="text-text-tertiary text-xs pl-6">
                  {dataset.id}
                </Table.Cell>
                <Table.Cell>
                  <span className="text-text-primary font-medium">
                    {dataset.name}
                  </span>
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {dataset.description || '—'}
                </Table.Cell>
                <Table.Cell>
                  <span className="text-text-secondary">{dataset.scenario_count}</span>
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {formatDate(dataset.created_at)}
                </Table.Cell>
                <Table.Cell className="pr-6">
                  <div 
                    className="flex items-center justify-end gap-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Link to={`/dataset/${dataset.id}`}>
                      <Button variant="ghost" size="sm">View</Button>
                    </Link>
                    <Link to={`/dataset/${dataset.id}/analytics`}>
                      <Button variant="ghost" size="sm">Analytics</Button>
                    </Link>
                    <DropdownMenu trigger={<OverflowMenuTrigger />}>
                      <DropdownItem
                        danger
                        onClick={() => setDeleteTarget(dataset.id)}
                      >
                        Delete dataset
                      </DropdownItem>
                    </DropdownMenu>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FullPageTableLayout>

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget)
          }
        }}
        title="Delete Dataset"
        description={
          deleteTarget
            ? `Are you sure you want to delete dataset ${deleteTarget}? This will not delete the scenarios, only the dataset grouping.`
            : ''
        }
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </>
  )
}

import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { listExecutors, getHarnessDetail } from '../api'
import { FullPageTableLayout, Table, Button, EmptyState, Checkbox } from './ui'

interface ExecutorTuple {
  harness: string
  harnessName: string
  provider: string
  modelId: string
  modelName: string
  executorSpec: string
}

export default function Executors() {
  const navigate = useNavigate()
  const [selectedExecutors, setSelectedExecutors] = useState<Set<string>>(new Set())

  const { data: executorsData, isLoading } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  const harnessIds = executorsData?.harnesses.map((h: any) => h.id) || []
  const harnessDetailsQueries = useQuery({
    queryKey: ['harness-details', harnessIds],
    queryFn: async () => {
      if (!executorsData) return []
      const details = await Promise.all(
        executorsData.harnesses.map((h: any) => getHarnessDetail(h.id))
      )
      return details
    },
    enabled: !!executorsData && harnessIds.length > 0,
  })

  const executorTuples = useMemo<ExecutorTuple[]>(() => {
    if (!executorsData || !harnessDetailsQueries.data) return []

    const tuples: ExecutorTuple[] = []
    for (let i = 0; i < executorsData.harnesses.length; i++) {
      const harness = executorsData.harnesses[i]
      const detail = harnessDetailsQueries.data[i]
      if (!detail) continue

      for (const providerDetail of detail.providers) {
        for (const model of providerDetail.models) {
          tuples.push({
            harness: harness.id,
            harnessName: harness.name,
            provider: providerDetail.id,
            modelId: model.id,
            modelName: model.name,
            executorSpec: `${harness.id}:${providerDetail.id}:${model.id}`,
          })
        }
      }
    }
    return tuples
  }, [executorsData, harnessDetailsQueries.data])

  const toggleExecutor = (executorSpec: string) => {
    const newSelected = new Set(selectedExecutors)
    if (newSelected.has(executorSpec)) {
      newSelected.delete(executorSpec)
    } else {
      newSelected.add(executorSpec)
    }
    setSelectedExecutors(newSelected)
  }

  const toggleAll = () => {
    if (selectedExecutors.size === executorTuples.length) {
      setSelectedExecutors(new Set())
    } else {
      setSelectedExecutors(new Set(executorTuples.map(t => t.executorSpec)))
    }
  }

  const handleStartRun = () => {
    if (selectedExecutors.size === 0) return
    const executorSpecs = Array.from(selectedExecutors).join(',')
    navigate(`/run/create?executors=${executorSpecs}`)
  }

  const header = (
    <FullPageTableLayout.Header
      title="Executors"
      count={executorTuples.length}
      countLabel={executorTuples.length === 1 ? 'executor' : 'executors'}
      description="Available harness, provider, and model combinations"
      actions={
        <Button 
          onClick={handleStartRun}
          disabled={selectedExecutors.size === 0}
        >
          Start Run{selectedExecutors.size > 0 ? ` (${selectedExecutors.size})` : ''}
        </Button>
      }
    />
  )

  if (isLoading || harnessDetailsQueries.isLoading) {
    return (
      <FullPageTableLayout header={header} isEmpty>
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </FullPageTableLayout>
    )
  }

  return (
    <FullPageTableLayout
      header={header}
      isEmpty={executorTuples.length === 0}
      emptyState={
        <EmptyState
          title="No executors available"
          description="No harness/provider/model combinations found."
        />
      }
    >
      <Table fullPage maxHeight="full">
        <Table.Header>
          <tr>
            <Table.Head className="w-10 pl-6">
              <Checkbox
                checked={selectedExecutors.size === executorTuples.length && executorTuples.length > 0}
                onChange={toggleAll}
              />
            </Table.Head>
            <Table.Head>Harness</Table.Head>
            <Table.Head>Provider</Table.Head>
            <Table.Head>Model ID</Table.Head>
            <Table.Head>Model Name</Table.Head>
            <Table.Head className="pr-6"></Table.Head>
          </tr>
        </Table.Header>
        <Table.Body>
          {executorTuples.map((tuple) => (
            <Table.Row
              key={tuple.executorSpec}
              selected={selectedExecutors.has(tuple.executorSpec)}
            >
              <Table.Cell className="pl-6">
                <Checkbox
                  checked={selectedExecutors.has(tuple.executorSpec)}
                  onChange={() => toggleExecutor(tuple.executorSpec)}
                />
              </Table.Cell>
              <Table.Cell>
                <span className="text-text-primary font-medium">{tuple.harnessName}</span>
                <span className="text-text-disabled font-mono text-xs ml-2">({tuple.harness})</span>
              </Table.Cell>
              <Table.Cell mono className="text-text-secondary text-sm">
                {tuple.provider}
              </Table.Cell>
              <Table.Cell mono className="text-text-secondary text-sm">
                {tuple.modelId}
              </Table.Cell>
              <Table.Cell className="text-text-tertiary text-sm">
                {tuple.modelName}
              </Table.Cell>
              <Table.Cell className="pr-6">
                <Link to={`/runs?executor=${encodeURIComponent(tuple.executorSpec)}`}>
                  <Button variant="ghost" size="sm">View Runs</Button>
                </Link>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </FullPageTableLayout>
  )
}

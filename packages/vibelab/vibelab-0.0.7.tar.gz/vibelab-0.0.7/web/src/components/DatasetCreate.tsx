import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { createDataset } from '../api'
import { PageLayout, PageHeader, Card, Input, Textarea, Button } from './ui'

export default function DatasetCreate() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const createMutation = useMutation({
    mutationFn: createDataset,
    onSuccess: (dataset) => {
      navigate(`/dataset/${dataset.id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    
    createMutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
    })
  }

  return (
    <PageLayout width="narrow">
      <PageHeader
        title="Create Dataset"
        description="Create a new dataset to organize scenarios"
      />

      <form onSubmit={handleSubmit}>
        <Card>
          <Card.Header>
            <Card.Title>Dataset Details</Card.Title>
          </Card.Header>
          <Card.Content className="space-y-4">
            <Input
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Dataset name"
              required
            />

            <Textarea
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              placeholder="Optional description for this dataset"
            />
          </Card.Content>
        </Card>

        <div className="mt-6 flex gap-2">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate('/datasets')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={createMutation.isPending || !name.trim()}
          >
            {createMutation.isPending ? 'Creating...' : 'Create Dataset'}
          </Button>
        </div>
      </form>
    </PageLayout>
  )
}





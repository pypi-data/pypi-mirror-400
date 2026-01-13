import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getScenario, listScenarios, listJudges, analyzeCommit, getDraft, listJudgeModels, type CommitScenarioDraft } from '../api'
import { Card, Select, Textarea, Checkbox, Button } from './ui'
import { DEFAULT_JUDGE_GUIDANCE } from '../lib/judgeDefaults'

interface ScenarioFormProps {
  selectedScenarioId: string
  onScenarioIdChange: (id: string) => void
  codeType: string
  onCodeTypeChange: (type: string) => void
  codeRef: string
  onCodeRefChange: (ref: string) => void
  prompt: string
  onPromptChange: (prompt: string) => void
  showLoadFromExisting?: boolean
  excludeScenarioIds?: number[]
  // Judge settings (optional)
  showJudgeSettings?: boolean
  enableJudge?: boolean
  onEnableJudgeChange?: (enabled: boolean) => void
  judgeGuidance?: string
  onJudgeGuidanceChange?: (guidance: string) => void
  judgeProvider?: string
  onJudgeProviderChange?: (provider: string) => void
  judgeModel?: string
  onJudgeModelChange?: (model: string) => void
  autoJudge?: boolean
  onAutoJudgeChange?: (auto: boolean) => void
}

export function ScenarioForm({
  selectedScenarioId,
  onScenarioIdChange,
  codeType,
  onCodeTypeChange,
  codeRef,
  onCodeRefChange,
  prompt,
  onPromptChange,
  showLoadFromExisting = true,
  excludeScenarioIds = [],
  // Judge settings
  showJudgeSettings = false,
  enableJudge = false,
  onEnableJudgeChange,
  judgeGuidance = '',
  onJudgeGuidanceChange,
  judgeProvider = 'anthropic',
  onJudgeProviderChange,
  judgeModel = 'claude-sonnet-4-20250514',
  onJudgeModelChange,
  autoJudge = true,
  onAutoJudgeChange,
}: ScenarioFormProps) {
  const { data: scenariosData } = useQuery({
    queryKey: ['scenarios'],
    queryFn: () => listScenarios(),
  })

  const { data: scenarioData } = useQuery({
    queryKey: ['scenario', selectedScenarioId],
    queryFn: () => getScenario(Number(selectedScenarioId!)),
    enabled: !!selectedScenarioId,
  })

  // Get existing judge for selected scenario
  const { data: existingJudges } = useQuery({
    queryKey: ['judges', selectedScenarioId],
    queryFn: () => listJudges(Number(selectedScenarioId!)),
    enabled: !!selectedScenarioId && showJudgeSettings,
  })

  // Get available judge models from LiteLLM
  const { data: judgeModelsData } = useQuery({
    queryKey: ['judge-models'],
    queryFn: listJudgeModels,
    enabled: showJudgeSettings,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  // Get current provider's models
  const currentProviderModels = judgeModelsData?.providers.find(p => p.id === judgeProvider)?.models || []

  // Load scenario data when selected
  useEffect(() => {
    if (scenarioData?.scenario) {
      const s = scenarioData.scenario
      onPromptChange(s.prompt)
      onCodeTypeChange(s.code_type)
      if (s.code_ref) {
        if (s.code_type === 'github') {
          const ref = s.code_ref
          onCodeRefChange(`${ref.owner}/${ref.repo}@${ref.commit_sha || ref.branch || 'main'}`)
        } else if (s.code_type === 'local') {
          onCodeRefChange(s.code_ref.path)
        }
      }
    }
  }, [scenarioData, onPromptChange, onCodeTypeChange, onCodeRefChange])

  // Load existing judge data when scenario has a judge
  useEffect(() => {
    if (existingJudges && existingJudges.length > 0 && onJudgeGuidanceChange && onEnableJudgeChange) {
      const latestJudge = existingJudges[0]
      onEnableJudgeChange(true)
      onJudgeGuidanceChange(latestJudge.guidance || '')
      if (onJudgeProviderChange && latestJudge.judge_provider) {
        onJudgeProviderChange(latestJudge.judge_provider)
      }
      if (onJudgeModelChange && latestJudge.judge_model) {
        onJudgeModelChange(latestJudge.judge_model)
      }
    }
  }, [existingJudges, onJudgeGuidanceChange, onEnableJudgeChange, onJudgeProviderChange, onJudgeModelChange])

  const getCodeRefDisplay = (scenario: any) => {
    if (!scenario.code_ref) return 'Empty'
    if (scenario.code_type === 'github') {
      return `${scenario.code_ref.owner}/${scenario.code_ref.repo}`
    } else if (scenario.code_type === 'local') {
      return scenario.code_ref.path
    }
    return '—'
  }

  const availableScenarios = scenariosData?.scenarios.filter(
    s => !excludeScenarioIds.includes(s.id)
  ) || []

  // Import from commit state
  const [importMode, setImportMode] = useState<'manual' | 'from-commit'>('manual')
  const [commitUrl, setCommitUrl] = useState('')
  const [draft, setDraft] = useState<CommitScenarioDraft | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analyzeError, setAnalyzeError] = useState<string | null>(null)

  // Poll for draft status when analyzing
  const { data: draftData } = useQuery({
    queryKey: ['draft', draft?.id],
    queryFn: () => draft ? getDraft(draft.id) : null,
    enabled: !!draft && draft.status === 'pending',
    refetchInterval: (query) => {
      const data = query.state.data
      // Stop polling when draft is ready/failed or task failed
      if (data?.status === 'ready' || data?.status === 'failed') {
        return false
      }
      if (data?.task?.status === 'failed') {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
  })

  // Update draft when polling data changes
  useEffect(() => {
    if (draftData?.draft) {
      setDraft(draftData.draft)
      if (draftData.status === 'ready' && draftData.draft.generated_prompt && draftData.draft.generated_judge_guidance) {
        // Auto-populate form when ready
        onPromptChange(draftData.draft.generated_prompt)
        if (onJudgeGuidanceChange) {
          onJudgeGuidanceChange(draftData.draft.generated_judge_guidance)
        }
        if (onEnableJudgeChange) {
          onEnableJudgeChange(true)
        }
        onCodeTypeChange('github')
        if (draftData.draft.parent_sha) {
          onCodeRefChange(`${draftData.draft.owner}/${draftData.draft.repo}@${draftData.draft.parent_sha}`)
        }
      }
      // Check if task failed (draft may still show pending)
      if (draftData.task?.status === 'failed' && draftData.draft.status === 'pending') {
        // Task failed but draft wasn't updated - update draft status locally
        setDraft({ ...draftData.draft, status: 'failed', error_message: draftData.task.error_message || 'Task failed' })
      }
    }
  }, [draftData, onPromptChange, onJudgeGuidanceChange, onEnableJudgeChange, onCodeTypeChange, onCodeRefChange])

  const handleAnalyzeCommit = async () => {
    if (!commitUrl.trim()) {
      setAnalyzeError('Please enter a commit URL')
      return
    }
    setIsAnalyzing(true)
    setAnalyzeError(null)
    try {
      const result = await analyzeCommit(commitUrl.trim())
      const draftResult = await getDraft(result.draft_id)
      setDraft(draftResult.draft)
    } catch (err: any) {
      setAnalyzeError(err.message || 'Failed to analyze commit')
    } finally {
      setIsAnalyzing(false)
    }
  }

  // If in import mode and draft is ready, show the form with generated content
  if (importMode === 'from-commit' && draft) {
    return (
      <>
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <Card.Title>Import from Commit</Card.Title>
              <button
                onClick={() => {
                  setImportMode('manual')
                  setDraft(null)
                  setCommitUrl('')
                  setAnalyzeError(null)
                }}
                className="text-sm text-text-secondary hover:text-text-primary"
              >
                Switch to Manual Entry
              </button>
            </div>
          </Card.Header>
          <Card.Content className="space-y-4">
            {draft.status === 'pending' && (
              <div className="p-4 bg-accent-muted rounded-lg">
                <p className="text-sm text-text-secondary">
                  Analyzing commit and generating scenario content... This may take a moment.
                </p>
              </div>
            )}
            {draft.status === 'failed' && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-sm text-red-500">
                  <strong>Error:</strong> {draft.error_message || 'Failed to generate scenario'}
                </p>
              </div>
            )}
            {draft.status === 'ready' && (
              <>
                <div className="p-3 bg-surface-2 rounded-lg text-sm space-y-1">
                  <div><strong>Commit:</strong> {draft.commit_message.split('\n')[0]}</div>
                  <div><strong>Author:</strong> {draft.commit_author || 'Unknown'}</div>
                  {draft.pr_title && (
                    <div><strong>PR:</strong> #{draft.pr_number} - {draft.pr_title}</div>
                  )}
                  {!draft.pr_title && (
                    <div className="text-text-tertiary text-xs">PR description not available</div>
                  )}
                </div>
                <Textarea
                  label="Generated Prompt (editable)"
                  value={prompt}
                  onChange={(e) => onPromptChange(e.target.value)}
                  rows={6}
                  mono
                  placeholder="Generated prompt will appear here..."
                />
                {showJudgeSettings && (
                  <Textarea
                    label="Generated Judge Guidance (editable)"
                    value={judgeGuidance}
                    onChange={(e) => onJudgeGuidanceChange?.(e.target.value)}
                    rows={8}
                    mono
                    placeholder="Generated judge guidance will appear here..."
                  />
                )}
              </>
            )}
          </Card.Content>
        </Card>
        {showJudgeSettings && draft.status === 'ready' && (
          <Card className="mt-4">
            <Card.Header>
              <div className="flex items-center justify-between">
                <Card.Title>LLM Judge</Card.Title>
                <Checkbox
                  checked={enableJudge}
                  onChange={(e) => {
                    const enabled = e.target.checked
                    onEnableJudgeChange?.(enabled)
                    if (enabled && onJudgeGuidanceChange && !judgeGuidance.trim()) {
                      onJudgeGuidanceChange(draft.generated_judge_guidance || DEFAULT_JUDGE_GUIDANCE)
                    }
                  }}
                  label="Enable"
                />
              </div>
            </Card.Header>
            {enableJudge && (
              <Card.Content className="space-y-4">
                {/* Provider & Model Selection */}
                <div>
                  <label className="block text-sm text-text-secondary mb-2">
                    Judge Provider & Model
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <Select
                      value={judgeProvider}
                      onChange={(e) => {
                        const newProvider = e.target.value
                        onJudgeProviderChange?.(newProvider)
                        // Reset model to first available when provider changes
                        const newProviderModels = judgeModelsData?.providers.find(p => p.id === newProvider)?.models || []
                        if (newProviderModels.length > 0) {
                          onJudgeModelChange?.(newProviderModels[0].id)
                        }
                      }}
                      options={
                        judgeModelsData?.providers.map(p => ({ value: p.id, label: p.name })) || [
                          { value: 'anthropic', label: 'Anthropic' },
                          { value: 'openai', label: 'OpenAI' },
                        ]
                      }
                    />
                    <Select
                      value={judgeModel}
                      onChange={(e) => onJudgeModelChange?.(e.target.value)}
                      options={
                        currentProviderModels.length > 0
                          ? currentProviderModels.map(m => ({
                              value: m.id,
                              label: m.input_price_per_1m !== undefined
                                ? `${m.name} ($${m.input_price_per_1m}/$${m.output_price_per_1m})`
                                : m.name
                            }))
                          : [{ value: judgeModel, label: judgeModel }]
                      }
                    />
                  </div>
                </div>

                <div>
                  <Textarea
                    label="Judge Guidance"
                    value={judgeGuidance}
                    onChange={(e) => onJudgeGuidanceChange?.(e.target.value)}
                    rows={6}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={autoJudge}
                    onChange={(e) => onAutoJudgeChange?.(e.target.checked)}
                    label="Auto-judge when run completes"
                  />
                </div>
              </Card.Content>
            )}
          </Card>
        )}
      </>
    )
  }

  return (
    <>
    <Card>
      <Card.Header>
        <Card.Title>Scenario Details</Card.Title>
      </Card.Header>
      <Card.Content className="space-y-4">
        {/* Mode toggle */}
        <div className="flex gap-2 border-b border-border pb-4">
          <button
            onClick={() => {
              setImportMode('manual')
              setDraft(null)
              setCommitUrl('')
              setAnalyzeError(null)
            }}
            className={`px-4 py-2 text-sm rounded ${
              importMode === 'manual'
                ? 'bg-accent text-text-primary font-medium'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            Manual Entry
          </button>
          <button
            onClick={() => setImportMode('from-commit')}
            className={`px-4 py-2 text-sm rounded ${
              importMode === 'from-commit'
                ? 'bg-accent text-text-primary font-medium'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            Import from Commit
          </button>
        </div>

        {importMode === 'from-commit' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1.5">
                Commit URL or Reference
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={commitUrl}
                  onChange={(e) => setCommitUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !isAnalyzing) {
                      handleAnalyzeCommit()
                    }
                  }}
                  className="flex-1 px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
                  placeholder="https://github.com/owner/repo/commit/abc123 or owner/repo@abc123"
                  disabled={isAnalyzing}
                />
                <Button
                  onClick={handleAnalyzeCommit}
                  disabled={isAnalyzing || !commitUrl.trim()}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                </Button>
              </div>
              {analyzeError && (
                <p className="mt-1 text-sm text-red-500">{analyzeError}</p>
              )}
              <p className="mt-1 text-xs text-text-tertiary">
                Paste a GitHub commit URL or reference (owner/repo@sha) to generate a scenario from real code changes.
              </p>
            </div>
          </div>
        ) : (
          <>
        {showLoadFromExisting && (
          <Select
            label="Load from existing scenario (optional)"
            value={selectedScenarioId}
            onChange={(e) => {
              onScenarioIdChange(e.target.value)
              if (!e.target.value) {
                onPromptChange('')
                onCodeRefChange('')
                onCodeTypeChange('github')
              }
            }}
          >
            <option value="">Create new scenario</option>
            {availableScenarios.slice(0, 20).map((scenario: any) => (
              <option key={scenario.id} value={scenario.id}>
                #{scenario.id}: {scenario.prompt.substring(0, 50)}
                {scenario.prompt.length > 50 ? '...' : ''} ({getCodeRefDisplay(scenario)})
              </option>
            ))}
          </Select>
        )}

        <Select
          label="Code Type"
          value={codeType}
          onChange={(e) => onCodeTypeChange(e.target.value)}
          options={[
            { value: 'github', label: 'GitHub' },
            { value: 'local', label: 'Local' },
            { value: 'empty', label: 'Empty' },
          ]}
        />

        {codeType !== 'empty' && (
          <div className="space-y-1.5">
            <label className="block text-sm text-text-secondary">
              Code Reference {codeType === 'github' && '(owner/repo@sha)'}
            </label>
            <input
              type="text"
              value={codeRef}
              onChange={(e) => onCodeRefChange(e.target.value)}
              className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
              placeholder={codeType === 'github' ? 'owner/repo@sha' : '/path/to/repo'}
            />
          </div>
        )}

            <Textarea
              label="Prompt"
              value={prompt}
              onChange={(e) => onPromptChange(e.target.value)}
              rows={6}
              mono
              placeholder="Task instructions for the agent..."
              required
            />
          </>
        )}
      </Card.Content>
    </Card>

    {/* Judge Settings Card (optional) */}
    {showJudgeSettings && (
      <Card className="mt-4">
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title>LLM Judge</Card.Title>
            <Checkbox
              checked={enableJudge}
              onChange={(e) => {
                const enabled = e.target.checked
                onEnableJudgeChange?.(enabled)
                if (enabled && onJudgeGuidanceChange && !judgeGuidance.trim()) {
                  onJudgeGuidanceChange(DEFAULT_JUDGE_GUIDANCE)
                }
              }}
              label="Enable"
            />
          </div>
        </Card.Header>
        {enableJudge && (
          <Card.Content className="space-y-4">
            {/* Provider & Model Selection */}
            <div>
              <label className="block text-sm text-text-secondary mb-2">
                Judge Provider & Model
              </label>
              <div className="grid grid-cols-2 gap-2">
                <Select
                  value={judgeProvider}
                  onChange={(e) => {
                    const newProvider = e.target.value
                    onJudgeProviderChange?.(newProvider)
                    // Reset model to first available when provider changes
                    const newProviderModels = judgeModelsData?.providers.find(p => p.id === newProvider)?.models || []
                    if (newProviderModels.length > 0) {
                      onJudgeModelChange?.(newProviderModels[0].id)
                    }
                  }}
                  options={
                    judgeModelsData?.providers.map(p => ({ value: p.id, label: p.name })) || [
                      { value: 'anthropic', label: 'Anthropic' },
                      { value: 'openai', label: 'OpenAI' },
                    ]
                  }
                />
                <Select
                  value={judgeModel}
                  onChange={(e) => onJudgeModelChange?.(e.target.value)}
                  options={
                    currentProviderModels.length > 0
                      ? currentProviderModels.map(m => ({
                          value: m.id,
                          label: m.input_price_per_1m !== undefined
                            ? `${m.name} ($${m.input_price_per_1m}/$${m.output_price_per_1m})`
                            : m.name
                        }))
                      : [{ value: judgeModel, label: judgeModel }]
                  }
                />
              </div>
            </div>

            <div>
              <Textarea
                label="Judge Guidance"
                value={judgeGuidance}
                onChange={(e) => onJudgeGuidanceChange?.(e.target.value)}
                placeholder="Describe what makes a successful result. E.g., 'The code should compile without errors, all tests should pass, and the feature should work as described in the prompt.'"
                rows={4}
              />
              <p className="mt-1 text-xs text-text-tertiary">
                Provide criteria for the LLM judge to evaluate results. Clear, specific criteria work best.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={autoJudge}
                onChange={(e) => onAutoJudgeChange?.(e.target.checked)}
                label="Auto-judge when run completes"
              />
            </div>
            {existingJudges && existingJudges.length > 0 && (
              <div className="p-3 bg-accent-muted rounded-lg text-xs text-text-secondary">
                <strong className="text-text-primary">Note:</strong> This scenario already has a judge configured. 
                Updating the guidance will update the existing judge.
              </div>
            )}
            {(!existingJudges || existingJudges.length === 0) && (
              <div className="p-3 bg-surface-2 rounded-lg text-xs text-text-secondary">
                <strong className="text-text-primary">Note:</strong> Few-shot examples and alignment evaluation are optional.
                If you want an alignment score, rate a few results manually and select them in the judge form.
              </div>
            )}
          </Card.Content>
        )}
      </Card>
    )}
    </>
  )
}


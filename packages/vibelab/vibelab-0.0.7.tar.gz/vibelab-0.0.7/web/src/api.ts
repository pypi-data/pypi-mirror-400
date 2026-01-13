const API_BASE = '/api'

// Project context - stored in localStorage and sent with all requests
const PROJECT_STORAGE_KEY = 'vibelab-project'

export function getCurrentProject(): string {
  return localStorage.getItem(PROJECT_STORAGE_KEY) || 'default'
}

export function setCurrentProject(projectName: string): void {
  localStorage.setItem(PROJECT_STORAGE_KEY, projectName)
  // Dispatch event so components can react to project change
  window.dispatchEvent(new CustomEvent('vibelab-project-changed', { detail: projectName }))
}

// Wrapper for fetch that adds project header
async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const projectName = getCurrentProject()
  const headers = new Headers(options.headers)
  headers.set('X-VibeLab-Project', projectName)
  
  return fetch(url, {
    ...options,
    headers,
  })
}

export interface Scenario {
  id: number
  code_type: string
  code_ref: any
  prompt: string
  created_at: string
  archived: boolean
}

export interface Result {
  id: number
  scenario_id: number
  harness: string
  provider: string
  model: string
  status: string
  created_at: string
  updated_at?: string
  started_at?: string
  finished_at?: string
  duration_ms?: number
  lines_added?: number
  lines_removed?: number
  files_changed?: number
  tokens_used?: number
  cost_usd?: number
  harness_metrics?: any
  annotations?: any
  timeout_seconds?: number
  driver?: string
  is_stale?: boolean
  error_message?: string
  notes?: string
  quality?: number  // 1=Bad, 2=Workable, 3=Good, 4=Perfect
}

export interface ExecutorInfo {
  id: string
  name: string
  providers: string[]
}

export interface DriverInfo {
  id: string
  name: string
}

export interface ProviderDetail {
  id: string
  models: Array<{ id: string; name: string }>
}

export interface HarnessDetail {
  harness: string
  providers: ProviderDetail[]
}

export async function listScenarios(options?: { includeArchived?: boolean }): Promise<{ 
  scenarios: Scenario[], 
  results_by_scenario: Record<string, Result[]>,
  judges_by_scenario: Record<string, { id: number, alignment_score: number | null }> 
}> {
  const params = new URLSearchParams()
  if (options?.includeArchived) params.append('include_archived', 'true')
  const url = params.toString() ? `${API_BASE}/scenarios?${params}` : `${API_BASE}/scenarios`
  const response = await apiFetch(url)
  if (!response.ok) throw new Error('Failed to fetch scenarios')
  return response.json()
}

export async function getScenario(id: number): Promise<{ scenario: Scenario, results: Result[] }> {
  const response = await apiFetch(`${API_BASE}/scenarios/${id}`)
  if (!response.ok) throw new Error('Failed to fetch scenario')
  return response.json()
}

export async function createScenario(data: { code_type: string, code_ref?: any, prompt: string }): Promise<Scenario> {
  const response = await apiFetch(`${API_BASE}/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create scenario')
  return response.json()
}

export async function listResults(filters?: { scenario_id?: number, executor?: string, status?: string }): Promise<Result[]> {
  const params = new URLSearchParams()
  if (filters?.scenario_id) params.append('scenario_id', String(filters.scenario_id))
  if (filters?.executor) params.append('executor', filters.executor)
  if (filters?.status) params.append('status', filters.status)
  const response = await apiFetch(`${API_BASE}/results?${params}`)
  if (!response.ok) throw new Error('Failed to fetch results')
  return response.json()
}

export async function getResult(id: number): Promise<Result> {
  const response = await apiFetch(`${API_BASE}/results/${id}`)
  if (!response.ok) throw new Error('Failed to fetch result')
  return response.json()
}

export async function getResultPatch(id: number): Promise<{ patch: string }> {
  const response = await apiFetch(`${API_BASE}/results/${id}/patch`)
  if (!response.ok) throw new Error('Failed to fetch patch')
  return response.json()
}

export async function getResultLogs(id: number): Promise<{ stdout: string, stderr: string }> {
  const response = await apiFetch(`${API_BASE}/results/${id}/logs`)
  if (!response.ok) throw new Error('Failed to fetch logs')
  return response.json()
}

export async function createRun(data: { scenario_id: number, executor_spec: string, timeout_seconds?: number, driver?: string }): Promise<{ status: string, scenario_id: number, executor_spec: string, result_id: number }> {
  const response = await apiFetch(`${API_BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create run')
  return response.json()
}

export async function listExecutors(): Promise<{ harnesses: ExecutorInfo[] }> {
  const response = await apiFetch(`${API_BASE}/executors`)
  if (!response.ok) throw new Error('Failed to fetch executors')
  return response.json()
}

export async function getExecutorModels(harness: string, provider: string): Promise<{ models: Array<{ id: string, name: string }> }> {
  const response = await apiFetch(`${API_BASE}/executors/${harness}/${provider}`)
  if (!response.ok) throw new Error('Failed to fetch models')
  return response.json()
}

export async function getHarnessDetail(harness: string): Promise<HarnessDetail> {
  const response = await apiFetch(`${API_BASE}/executors/${harness}`)
  if (!response.ok) throw new Error('Failed to fetch harness detail')
  return response.json()
}

export async function listDrivers(): Promise<{ drivers: DriverInfo[] }> {
  const response = await apiFetch(`${API_BASE}/executors/drivers/list`)
  if (!response.ok) throw new Error('Failed to fetch drivers')
  return response.json()
}

export async function deleteScenario(id: number): Promise<{ status: string, scenario_id: number }> {
  const response = await apiFetch(`${API_BASE}/scenarios/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete scenario')
  return response.json()
}

export async function archiveScenario(id: number, archived: boolean): Promise<Scenario> {
  const response = await apiFetch(`${API_BASE}/scenarios/${id}/archive`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ archived }),
  })
  if (!response.ok) throw new Error('Failed to archive scenario')
  return response.json()
}

export async function deleteResult(id: number): Promise<{ status: string, result_id: number }> {
  const response = await apiFetch(`${API_BASE}/results/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete result')
  return response.json()
}

export async function rerunResult(id: number): Promise<{ result_id: number, status: string, scenario_id: number, executor_spec: string, original_result_id: number }> {
  const response = await apiFetch(`${API_BASE}/results/${id}/rerun`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to rerun result')
  return response.json()
}

export async function updateResultNotes(id: number, notes: string | null): Promise<Result> {
  const response = await apiFetch(`${API_BASE}/results/${id}/notes`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  })
  if (!response.ok) throw new Error('Failed to update result notes')
  return response.json()
}

export async function updateResultQuality(id: number, quality: number | null): Promise<Result> {
  const response = await apiFetch(`${API_BASE}/results/${id}/quality`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quality }),
  })
  if (!response.ok) throw new Error('Failed to update result quality')
  return response.json()
}

export async function updateResultNotesAndQuality(id: number, notes: string | null, quality: number | null): Promise<Result> {
  const response = await apiFetch(`${API_BASE}/results/${id}/notes-quality`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes, quality }),
  })
  if (!response.ok) throw new Error('Failed to update result notes and quality')
  return response.json()
}

// Streaming types
export interface StreamEvent {
  type: 'connected' | 'status' | 'output' | 'patch' | 'done' | 'error'
  data: any
}

export interface StreamCallbacks {
  onConnect?: (resultId: number) => void
  onStatus?: (status: string) => void
  onOutput?: (data: string, offset?: number) => void
  onPatch?: (patch: string) => void
  onDone?: (status: string) => void
  onError?: (error: string) => void
}

/**
 * Subscribe to streaming logs for a result.
 * Returns a function to close the connection.
 */
export function subscribeToResultStream(
  resultId: number,
  callbacks: StreamCallbacks
): () => void {
  const url = `${API_BASE}/results/${resultId}/stream`
  console.log('[Streaming] Connecting to:', url)
  const eventSource = new EventSource(url)

  eventSource.addEventListener('connected', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Connected:', data)
      callbacks.onConnect?.(data.result_id)
    } catch (e) {
      console.error('[Streaming] Error parsing connected event:', e)
    }
  })

  eventSource.addEventListener('status', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Status update:', data.status)
      callbacks.onStatus?.(data.status)
    } catch (e) {
      console.error('[Streaming] Error parsing status event:', e)
    }
  })

  eventSource.addEventListener('output', (event) => {
    try {
      const data = JSON.parse(event.data)
      callbacks.onOutput?.(data.data, data.offset)
    } catch (e) {
      console.error('[Streaming] Error parsing output event:', e)
    }
  })

  eventSource.addEventListener('patch', (event) => {
    try {
      const data = JSON.parse(event.data)
      callbacks.onPatch?.(data.patch)
    } catch (e) {
      console.error('[Streaming] Error parsing patch event:', e)
    }
  })

  eventSource.addEventListener('done', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Done:', data.status)
      callbacks.onDone?.(data.status)
      eventSource.close()
    } catch (e) {
      console.error('[Streaming] Error parsing done event:', e)
      eventSource.close()
    }
  })

  eventSource.addEventListener('error', (event) => {
    // Check if it's a real error or just a connection close
    if (eventSource.readyState === EventSource.CLOSED) {
      return
    }
    try {
      const data = JSON.parse((event as MessageEvent).data)
      console.error('[Streaming] Error event:', data.error)
      callbacks.onError?.(data.error)
    } catch {
      console.error('[Streaming] Connection error')
      callbacks.onError?.('Connection error')
    }
  })

  eventSource.onerror = (error) => {
    console.error('[Streaming] EventSource error:', error, 'readyState:', eventSource.readyState)
    if (eventSource.readyState === EventSource.CLOSED) {
      return
    }
    // Don't call onError here if we're just waiting for connection
    // Only call if it's a real error after connection
    if (eventSource.readyState === EventSource.CONNECTING) {
      // Still connecting, might be normal
      return
    }
    callbacks.onError?.('Connection lost')
  }

  return () => {
    console.log('[Streaming] Closing connection')
    eventSource.close()
  }
}

export async function getStreamStatus(id: number): Promise<{ status: string, streaming: boolean }> {
  const response = await apiFetch(`${API_BASE}/results/${id}/stream/status`)
  if (!response.ok) throw new Error('Failed to fetch stream status')
  return response.json()
}

// Dataset types and functions
export interface Dataset {
  id: number
  name: string
  description?: string
  created_at: string
}

export async function listDatasets(): Promise<{ datasets: Array<Dataset & { scenario_count: number }> }> {
  const response = await apiFetch(`${API_BASE}/datasets`)
  if (!response.ok) throw new Error('Failed to fetch datasets')
  return response.json()
}

export async function getDataset(id: number): Promise<{ dataset: Dataset, scenarios: Scenario[] }> {
  const response = await apiFetch(`${API_BASE}/datasets/${id}`)
  if (!response.ok) throw new Error('Failed to fetch dataset')
  return response.json()
}

export async function createDataset(data: { name: string, description?: string }): Promise<Dataset> {
  const response = await apiFetch(`${API_BASE}/datasets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create dataset')
  return response.json()
}

export async function deleteDataset(id: number): Promise<{ status: string, dataset_id: number }> {
  const response = await apiFetch(`${API_BASE}/datasets/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete dataset')
  return response.json()
}

export async function addScenarioToDataset(datasetId: number, scenarioId: number): Promise<{ status: string, dataset_id: number, scenario_id: number }> {
  const response = await apiFetch(`${API_BASE}/datasets/${datasetId}/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId }),
  })
  if (!response.ok) throw new Error('Failed to add scenario to dataset')
  return response.json()
}

export async function removeScenarioFromDataset(datasetId: number, scenarioId: number): Promise<{ status: string, dataset_id: number, scenario_id: number }> {
  const response = await apiFetch(`${API_BASE}/datasets/${datasetId}/scenarios/${scenarioId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to remove scenario from dataset')
  return response.json()
}

export async function createDatasetRun(data: {
  dataset_id: number,
  executor_specs: string[],
  trials?: number,
  minimal?: boolean,
  timeout_seconds?: number,
  driver?: string
}): Promise<{ status: string, dataset_id: number, pairs_run: number, result_ids: number[] }> {
  const response = await apiFetch(`${API_BASE}/datasets/${data.dataset_id}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      executor_specs: data.executor_specs,
      trials: data.trials ?? 1,
      minimal: data.minimal ?? false,
      timeout_seconds: data.timeout_seconds ?? 1800,
      driver: data.driver ?? 'local',
    }),
  })
  if (!response.ok) throw new Error('Failed to create dataset run')
  return response.json()
}

export async function getDatasetAnalytics(id: number): Promise<{
  dataset: Dataset,
  executors: string[],
  matrix: Array<{
    scenario_id: number,
    scenario_prompt: string,
    cells: Record<string, {
      status: string,
      total: number,
      completed: number,
      failed: number,
      timeout: number,
      running: number,
      queued: number,
      result_ids?: number[],
      avg_quality?: number | null,
      quality_count?: number,
      avg_duration_ms?: number | null,
      duration_count?: number,
      avg_cost_usd?: number | null,
      cost_count?: number
    }>
  }>
}> {
  const response = await apiFetch(`${API_BASE}/datasets/${id}/analytics`)
  if (!response.ok) throw new Error('Failed to fetch dataset analytics')
  return response.json()
}

export interface GlobalAnalytics {
  title: string
  description: string
  scenario_count: number
  executors: string[]
  matrix: Array<{
    scenario_id: number
    scenario_prompt: string
    cells: Record<string, {
      status: string
      total: number
      completed: number
      failed: number
      timeout: number
      running: number
      queued: number
      result_ids?: number[]
      avg_quality?: number | null
      quality_count?: number
      avg_duration_ms?: number | null
      duration_count?: number
      avg_cost_usd?: number | null
      cost_count?: number
    }>
  }>
}

export async function getGlobalAnalytics(): Promise<GlobalAnalytics> {
  const response = await apiFetch(`${API_BASE}/scenarios/analytics/global`)
  if (!response.ok) throw new Error('Failed to fetch global analytics')
  return response.json()
}

// Judge types and functions
export interface LLMScenarioJudge {
  id: number
  scenario_id: number
  guidance: string
  judge_provider: string
  judge_model: string
  training_sample_ids: number[]
  alignment_score?: number | null
  created_at: string
}

export interface Judgement {
  id: number
  result_id: number
  judge_id: number
  notes?: string | null
  quality?: number | null
  created_at: string
}

export interface JudgeModel {
  id: string
  name: string
  input_price_per_1m?: number
  output_price_per_1m?: number
}

export interface JudgeProvider {
  id: string
  name: string
  models: JudgeModel[]
}

export interface JudgeModelsResponse {
  providers: JudgeProvider[]
}

export async function listJudgeModels(): Promise<JudgeModelsResponse> {
  const response = await apiFetch(`${API_BASE}/judges/models`)
  if (!response.ok) throw new Error('Failed to fetch judge models')
  return response.json()
}

export async function listJudges(scenarioId?: number): Promise<LLMScenarioJudge[]> {
  const params = scenarioId ? `?scenario_id=${scenarioId}` : ''
  const response = await apiFetch(`${API_BASE}/judges${params}`)
  if (!response.ok) throw new Error('Failed to fetch judges')
  return response.json()
}

export async function getJudge(id: number): Promise<LLMScenarioJudge> {
  const response = await apiFetch(`${API_BASE}/judges/${id}`)
  if (!response.ok) throw new Error('Failed to fetch judge')
  return response.json()
}

export async function createJudge(data: {
  scenario_id: number,
  guidance: string,
  judge_provider: string,
  judge_model: string,
  training_sample_ids: number[]
}): Promise<LLMScenarioJudge> {
  const response = await apiFetch(`${API_BASE}/judges`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create judge')
  return response.json()
}

export async function updateJudge(judgeId: number, data: {
  scenario_id: number,
  guidance: string,
  judge_provider: string,
  judge_model: string,
  training_sample_ids: number[]
}): Promise<LLMScenarioJudge> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to update judge')
  return response.json()
}

export async function deleteJudge(id: number): Promise<{ status: string, judge_id: number }> {
  const response = await apiFetch(`${API_BASE}/judges/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete judge')
  return response.json()
}

export async function listJudgeJudgements(judgeId: number): Promise<Judgement[]> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/judgements`)
  if (!response.ok) throw new Error('Failed to fetch judgements')
  return response.json()
}

export interface EnrichedJudgement extends Judgement {
  result?: Result
  judge?: LLMScenarioJudge
}

export async function listAllJudgements(): Promise<EnrichedJudgement[]> {
  const response = await apiFetch(`${API_BASE}/judges/judgements/all`)
  if (!response.ok) throw new Error('Failed to fetch judgements')
  return response.json()
}

export async function listPendingJudgements(): Promise<Array<{ result: Result, judge: LLMScenarioJudge }>> {
  const response = await apiFetch(`${API_BASE}/judges/judgements/pending`)
  if (!response.ok) throw new Error('Failed to fetch pending judgements')
  return response.json()
}

export interface ScenarioJudgement extends Judgement {
  result?: Result
  judge?: LLMScenarioJudge
  is_latest_judge?: boolean
}

export async function listScenarioJudgements(scenarioId: number): Promise<ScenarioJudgement[]> {
  const response = await apiFetch(`${API_BASE}/judges/scenarios/${scenarioId}/judgements`)
  if (!response.ok) throw new Error('Failed to fetch scenario judgements')
  return response.json()
}

export async function acceptJudgement(judgementId: number): Promise<Result> {
  const response = await apiFetch(`${API_BASE}/judges/judgements/${judgementId}/accept`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to accept judgement')
  return response.json()
}

export async function applyJudge(judgeId: number, resultId: number): Promise<Judgement> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result_ids: [resultId], // Single result only
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to apply judge' }))
    throw new Error(error.detail || 'Failed to apply judge')
  }
  return response.json()
}

export async function applyJudgeToAllCompleted(
  judgeId: number,
): Promise<{ status: string, judge_id: number, total: number }> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/apply?async_=true`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result_ids: null, // All completed for scenario
      force: true, // Re-evaluate
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to apply judge to all completed results' }))
    throw new Error(error.detail || 'Failed to apply judge to all completed results')
  }
  return response.json()
}

export interface QueuedJudgeResult {
  status: 'queued'
  judge_id: number
  result_id: number
  task_id: number
}

export async function enqueueJudgeResult(judgeId: number, resultId: number): Promise<QueuedJudgeResult> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/judge-result/${resultId}?async_=true`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to queue judge' }))
    throw new Error(error.detail || 'Failed to queue judge')
  }
  return response.json()
}

export async function applyJudgeToResultsAsync(
  judgeId: number,
  resultIds: number[],
  force: boolean = true,
): Promise<{ status: string, judge_id: number, total: number }> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/apply?async_=true`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result_ids: resultIds,
      force,
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to apply judge to results' }))
    throw new Error(error.detail || 'Failed to apply judge to results')
  }
  return response.json()
}

export async function judgeResult(judgeId: number, resultId: number): Promise<Judgement> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/judge-result/${resultId}`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to judge result' }))
    throw new Error(error.detail || 'Failed to judge result')
  }
  return response.json()
}

export async function trainJudge(judgeId: number, resultIds: number[] = []): Promise<{ status: string; judge_id: number; task_id: number }> {
  const response = await apiFetch(`${API_BASE}/judges/${judgeId}/train`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ result_ids: resultIds }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to queue alignment evaluation' }))
    throw new Error(error.detail || 'Failed to queue alignment evaluation')
  }
  return response.json()
}

// Task queue types and functions
export interface Task {
  id: number
  task_type: string
  status: string
  priority: number
  created_at: string
  started_at?: string | null
  finished_at?: string | null
  error_message?: string | null
  worker_id?: string | null
  pid?: number | null
  cancel_requested_at?: string | null

  // agent_run fields
  result_id?: number | null
  scenario_id?: number | null
  executor_spec?: string | null
  timeout_seconds?: number | null
  driver?: string | null

  // judge_result/train_judge fields
  judge_id?: number | null
  target_result_id?: number | null
  judge_provider?: string | null
  judge_model?: string | null
}

export interface TaskStats {
  task_stats: Record<string, Record<string, number>>
  running_tasks: number
  active_workers: number
}

export async function listTasks(filters?: { status?: string; task_type?: string; limit?: number }): Promise<Task[]> {
  const params = new URLSearchParams()
  if (filters?.status) params.append('status', filters.status)
  if (filters?.task_type) params.append('task_type', filters.task_type)
  if (filters?.limit != null) params.append('limit', String(filters.limit))
  const response = await apiFetch(`${API_BASE}/tasks?${params}`)
  if (!response.ok) throw new Error('Failed to fetch tasks')
  return response.json()
}

export async function getTaskStats(): Promise<TaskStats> {
  const response = await apiFetch(`${API_BASE}/tasks/stats`)
  if (!response.ok) throw new Error('Failed to fetch task stats')
  return response.json()
}

export async function listActiveTasks(limit: number = 200): Promise<Task[]> {
  const params = new URLSearchParams()
  params.append('limit', String(limit))
  const response = await apiFetch(`${API_BASE}/tasks/active?${params}`)
  if (!response.ok) throw new Error('Failed to fetch active tasks')
  return response.json()
}

export async function cancelTask(taskId: number): Promise<Task & { signal_sent?: boolean }> {
  const response = await apiFetch(`${API_BASE}/tasks/${taskId}/cancel`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to cancel task' }))
    throw new Error(error.detail || 'Failed to cancel task')
  }
  return response.json()
}

export async function promoteTask(taskId: number): Promise<Task> {
  const response = await apiFetch(`${API_BASE}/tasks/${taskId}/promote`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to promote task' }))
    throw new Error(error.detail || 'Failed to promote task')
  }
  return response.json()
}

export async function cancelQueuedTasks(): Promise<{ status: string; cancelled: number }> {
  const response = await apiFetch(`${API_BASE}/tasks/cancel-queued`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to cancel queued tasks' }))
    throw new Error(error.detail || 'Failed to cancel queued tasks')
  }
  return response.json()
}

/**
 * Get result IDs that are currently being judged (have queued or running judge_result tasks)
 */
export async function getActiveJudgementResultIds(): Promise<Set<number>> {
  const tasks = await listTasks({ 
    task_type: 'judge_result',
    limit: 1000 
  })
  const activeTasks = tasks.filter(
    t => t.status === 'queued' || t.status === 'running'
  )
  return new Set(
    activeTasks
      .map(t => t.target_result_id)
      .filter((id): id is number => id !== null && id !== undefined)
  )
}

// Commit-to-Scenario types and functions
export interface CommitInfo {
  owner: string
  repo: string
  commit_sha: string
  parent_sha: string
  commit_message: string
  commit_author?: string
  pr_number?: number
  pr_title?: string
}

export interface CommitScenarioDraft {
  id: number
  task_id?: number  // May be null initially, set after task creation
  status: 'pending' | 'ready' | 'saved' | 'failed'
  owner: string
  repo: string
  commit_sha: string
  parent_sha: string
  commit_message: string
  commit_author?: string
  pr_number?: number
  pr_title?: string
  pr_body?: string
  generated_prompt?: string
  generated_judge_guidance?: string
  generated_summary?: string
  error_message?: string
  created_at: string
}

export async function analyzeCommit(commitUrl: string): Promise<{
  draft_id: number
  task_id: number
  commit_info: CommitInfo
}> {
  const response = await apiFetch(`${API_BASE}/scenarios/from-commit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ commit_url: commitUrl }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to analyze commit' }))
    throw new Error(error.detail || 'Failed to analyze commit')
  }
  return response.json()
}

export interface DraftTask {
  id: number
  status: string
  error_message?: string | null
  started_at?: string | null
  finished_at?: string | null
}

export async function getDraft(draftId: number): Promise<{
  draft: CommitScenarioDraft
  status: string
  task?: DraftTask | null
}> {
  const response = await apiFetch(`${API_BASE}/scenarios/drafts/${draftId}`)
  if (!response.ok) throw new Error('Failed to fetch draft')
  return response.json()
}

export async function saveDraft(draftId: number, data: {
  prompt: string
  judge_guidance: string
  enable_judge: boolean
}): Promise<{ scenario_id: number, judge_id?: number, status: string }> {
  const response = await apiFetch(`${API_BASE}/scenarios/drafts/${draftId}/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to save draft' }))
    throw new Error(error.detail || 'Failed to save draft')
  }
  return response.json()
}

// Health check
export interface HealthResponse {
  status: string
  version: string
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiFetch(`${API_BASE}/health`)
  if (!response.ok) throw new Error('Failed to fetch health')
  return response.json()
}

// Project types and functions
export interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
}

export interface ProjectWithStats extends Project {
  scenario_count: number
  dataset_count: number
  task_count: number
}

export async function listProjects(): Promise<ProjectWithStats[]> {
  const response = await apiFetch(`${API_BASE}/projects`)
  if (!response.ok) throw new Error('Failed to fetch projects')
  return response.json()
}

export async function createProject(data: { name: string, description?: string }): Promise<Project> {
  const response = await apiFetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create project' }))
    throw new Error(error.detail || 'Failed to create project')
  }
  return response.json()
}

export async function getProject(id: number): Promise<ProjectWithStats> {
  const response = await apiFetch(`${API_BASE}/projects/${id}`)
  if (!response.ok) throw new Error('Failed to fetch project')
  return response.json()
}

export async function deleteProject(id: number): Promise<{ status: string, project_id: number }> {
  const response = await apiFetch(`${API_BASE}/projects/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete project' }))
    throw new Error(error.detail || 'Failed to delete project')
  }
  return response.json()
}

// Admin types and functions
export interface ProjectInfo {
  id: number
  name: string
  description: string | null
  scenario_count: number
  dataset_count: number
}

export interface AdminConfig {
  vibelab_home: string
  project: string
  project_id: number | null
  project_home: string
  db_path: string
  repos_dir: string
  log_level: string
  sqlite_busy_timeout_ms: number
  default_workers: number
  claude_code_image: string | null
  openai_codex_image: string | null
  cursor_image: string | null
  gemini_image: string | null
  oci_runtime: string | null
  default_driver: string
  default_timeout: number
  projects: ProjectInfo[]
}

export interface RepoInfo {
  host: string
  owner: string
  repo: string
  path: string
  size_mb: number
}

export interface ReposResponse {
  repos_dir: string
  repos: RepoInfo[]
  total_size_mb: number
}

export interface FileEntry {
  name: string
  path: string
  is_dir: boolean
  size_bytes: number | null
  modified_at: string | null
}

export interface FileBrowserResponse {
  current_path: string
  parent_path: string | null
  entries: FileEntry[]
}

export interface TableInfo {
  name: string
  row_count: number
  columns: string[]
}

export interface SchemaResponse {
  tables: TableInfo[]
  schema_version: number
}

export interface QueryResponse {
  columns: string[]
  rows: any[][]
  row_count: number
  error: string | null
}

export interface ScenarioCacheEntry {
  scenario_id: number
  code_type: string
  code_ref: Record<string, any> | null
  prompt_preview: string
  result_count: number
  has_worktree: boolean
}

export interface ScenarioCacheResponse {
  scenarios: ScenarioCacheEntry[]
  total_scenarios: number
  scenarios_with_worktrees: number
}

export async function getAdminConfig(): Promise<AdminConfig> {
  const response = await apiFetch(`${API_BASE}/admin/config`)
  if (!response.ok) throw new Error('Failed to fetch admin config')
  return response.json()
}

export async function getAdminRepos(): Promise<ReposResponse> {
  const response = await apiFetch(`${API_BASE}/admin/repos`)
  if (!response.ok) throw new Error('Failed to fetch repos')
  return response.json()
}

export async function getAdminScenarios(): Promise<ScenarioCacheResponse> {
  const response = await apiFetch(`${API_BASE}/admin/scenarios`)
  if (!response.ok) throw new Error('Failed to fetch scenarios cache')
  return response.json()
}

export async function browseAdminFiles(path: string = ''): Promise<FileBrowserResponse> {
  const params = new URLSearchParams()
  if (path) params.append('path', path)
  const response = await apiFetch(`${API_BASE}/admin/files?${params}`)
  if (!response.ok) throw new Error('Failed to browse files')
  return response.json()
}

export async function getAdminSchema(): Promise<SchemaResponse> {
  const response = await apiFetch(`${API_BASE}/admin/schema`)
  if (!response.ok) throw new Error('Failed to fetch schema')
  return response.json()
}

export async function executeAdminQuery(query: string): Promise<QueryResponse> {
  const response = await apiFetch(`${API_BASE}/admin/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) throw new Error('Failed to execute query')
  return response.json()
}

// =====================
// Review Queue API
// =====================

export interface ReviewQueueStats {
  queue_length: number
  scored_count: number
  alignment_score: number | null
  alignment_samples: number
  scenarios_with_judges: number
  target_per_scenario: number
}

export interface ReviewQueueItem {
  result_id: number
  scenario_id: number
  scenario_prompt: string
  executor: string
  harness: string
  provider: string
  model: string
  duration_ms: number | null
  judge_quality: number | null
  judge_notes: string | null
  judge_id: number | null
  scenario_scored_count: number
  priority_reason: string
}

export async function getReviewQueueStats(): Promise<ReviewQueueStats> {
  const response = await apiFetch(`${API_BASE}/review-queue/stats`)
  if (!response.ok) throw new Error('Failed to fetch review queue stats')
  return response.json()
}

export async function getReviewQueue(limit: number = 20): Promise<{ items: ReviewQueueItem[] }> {
  const response = await apiFetch(`${API_BASE}/review-queue?limit=${limit}`)
  if (!response.ok) throw new Error('Failed to fetch review queue')
  return response.json()
}

export async function getNextReviewItem(): Promise<{ item: ReviewQueueItem | null }> {
  const response = await apiFetch(`${API_BASE}/review-queue/next`)
  if (!response.ok) throw new Error('Failed to fetch next review item')
  return response.json()
}

export async function scoreReviewItem(
  resultId: number,
  quality: number,
  notes?: string
): Promise<{ status: string; result_id: number; quality: number; result: Result | null }> {
  const response = await apiFetch(`${API_BASE}/review-queue/${resultId}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quality, notes }),
  })
  if (!response.ok) throw new Error('Failed to score result')
  return response.json()
}

export async function skipReviewItem(
  resultId: number
): Promise<{ status: string; result_id: number; next_item: ReviewQueueItem | null }> {
  const response = await apiFetch(`${API_BASE}/review-queue/${resultId}/skip`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to skip result')
  return response.json()
}

// =====================
// Pairwise Comparison API
// =====================

export type PreferenceType = 'a_better' | 'b_better' | 'tie' | 'both_good' | 'both_bad'

export interface PairwisePreference {
  id: number
  scenario_id: number
  result_a_id: number
  result_b_id: number
  preference: PreferenceType
  confidence: number | null
  notes: string | null
  created_at: string
}

export interface NextPair {
  result_a_id: number
  result_b_id: number
  scenario_id: number
  scenario_prompt: string
  result_a_executor: string
  result_b_executor: string
  result_a_duration_ms: number | null
  result_b_duration_ms: number | null
  judge_a_quality: number | null
  judge_b_quality: number | null
  scenario_comparison_count: number
  priority_reason: string
}

export interface PairwiseStats {
  total_preferences: number
  scenarios_with_preferences: number
  unique_results_compared: number
  average_comparisons_per_result: number | null
}

export interface ResultRanking {
  result_id: number
  wins: number
  losses: number
  ties: number
  win_rate: number | null
  comparisons: number
  rank: number | null
  executor: string | null
}

export async function getPairwiseStats(): Promise<PairwiseStats> {
  const response = await apiFetch(`${API_BASE}/pairwise/stats`)
  if (!response.ok) throw new Error('Failed to fetch pairwise stats')
  return response.json()
}

export async function listPairwisePreferences(
  scenarioId?: number,
  resultId?: number
): Promise<{ preferences: PairwisePreference[] }> {
  const params = new URLSearchParams()
  if (scenarioId !== undefined) params.append('scenario_id', String(scenarioId))
  if (resultId !== undefined) params.append('result_id', String(resultId))
  const url = params.toString()
    ? `${API_BASE}/pairwise?${params}`
    : `${API_BASE}/pairwise`
  const response = await apiFetch(url)
  if (!response.ok) throw new Error('Failed to fetch pairwise preferences')
  return response.json()
}

export async function getNextPair(
  scenarioId?: number
): Promise<{ pair: NextPair | null; message?: string }> {
  const params = new URLSearchParams()
  if (scenarioId !== undefined) params.append('scenario_id', String(scenarioId))
  const url = params.toString()
    ? `${API_BASE}/pairwise/next?${params}`
    : `${API_BASE}/pairwise/next`
  const response = await apiFetch(url)
  if (!response.ok) throw new Error('Failed to fetch next pair')
  return response.json()
}

export async function getPairwiseRankings(
  scenarioId: number
): Promise<{ scenario_id: number; rankings: ResultRanking[] }> {
  const response = await apiFetch(`${API_BASE}/pairwise/rankings?scenario_id=${scenarioId}`)
  if (!response.ok) throw new Error('Failed to fetch rankings')
  return response.json()
}

export async function createPairwisePreference(
  resultAId: number,
  resultBId: number,
  preference: PreferenceType,
  confidence?: number,
  notes?: string
): Promise<{ preference: PairwisePreference }> {
  const response = await apiFetch(`${API_BASE}/pairwise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result_a_id: resultAId,
      result_b_id: resultBId,
      preference,
      confidence,
      notes,
    }),
  })
  if (!response.ok) throw new Error('Failed to create preference')
  return response.json()
}

export async function deletePairwisePreference(
  preferenceId: number
): Promise<{ status: string; id: number }> {
  const response = await apiFetch(`${API_BASE}/pairwise/${preferenceId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete preference')
  return response.json()
}

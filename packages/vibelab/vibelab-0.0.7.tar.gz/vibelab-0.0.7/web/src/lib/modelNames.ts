/**
 * Model name utilities for displaying friendly names in the UI.
 * Dynamically parses model IDs to generate human-readable display names.
 */

/**
 * Get a friendly display name for a model ID.
 * Dynamically parses the model ID to create a readable name.
 */
export function getModelDisplayName(modelId: string): string {
  // Remove date suffixes (YYYY-MM-DD or YYYYMMDD)
  let name = modelId
    .replace(/-20\d{2}-\d{2}-\d{2}$/, '')
    .replace(/-20\d{6}$/, '')
    .replace(/-\d{2}-\d{2}$/, '')  // For patterns like -06-05
    .replace(/-00\d$/, '')  // For patterns like -001, -002
  
  // Handle GPT models
  if (name.startsWith('gpt-')) {
    name = name.replace('gpt-', 'GPT-')
    name = name.replace(/-mini$/, ' Mini')
    name = name.replace(/-nano$/, ' Nano')
    name = name.replace(/-pro$/, ' Pro')
    name = name.replace(/-turbo$/, ' Turbo')
    name = name.replace(/-preview$/, ' Preview')
    return name
  }
  
  // Handle o-series models (o1, o3, o4)
  if (/^o[134]/.test(name)) {
    name = name.replace(/-mini$/, ' Mini')
    name = name.replace(/-pro$/, ' Pro')
    name = name.replace(/-preview$/, ' Preview')
    return name
  }
  
  // Handle Claude models
  if (name.startsWith('claude-')) {
    name = name.replace('claude-', 'Claude ')
    // Convert "3-5" to "3.5"
    name = name.replace(/(\d)-(\d)/g, '$1.$2')
    name = name.replace(/-/g, ' ')
    // Title case tier names
    name = name.replace(/\b(opus|sonnet|haiku)\b/gi, (m) => m.charAt(0).toUpperCase() + m.slice(1).toLowerCase())
    return name.trim()
  }
  
  // Handle Gemini models
  if (name.startsWith('gemini-')) {
    name = name.replace('gemini-', 'Gemini ')
    name = name.replace(/-/g, ' ')
    // Title case common suffixes
    name = name.replace(/\b(flash|pro|lite|ultra|thinking|exp|preview)\b/gi, (m) => m.charAt(0).toUpperCase() + m.slice(1).toLowerCase())
    return name.trim()
  }
  
  // Handle Cursor models
  if (name === 'composer-1' || name === 'composer') {
    return 'Composer'
  }
  
  // Fallback: just clean up the name
  return name
}

// Mapping of harness IDs to friendly short names
const HARNESS_DISPLAY_NAMES: Record<string, string> = {
  'claude-code': 'CC',
  'openai-codex': 'Codex',
  'cursor': 'Cursor',
  'gemini': 'Gemini',
}

/**
 * Get a friendly display name for a harness ID.
 */
export function getHarnessDisplayName(harnessId: string): string {
  return HARNESS_DISPLAY_NAMES[harnessId] || harnessId
}

/**
 * Get a friendly display name for an executor string (harness:provider:model).
 * Returns harness + friendly model name for column headers.
 */
export function getExecutorDisplayName(executor: string): string {
  const parts = executor.split(':')
  const harness = parts[0] || ''
  const modelId = parts[2] || executor
  const harnessName = getHarnessDisplayName(harness)
  const modelName = getModelDisplayName(modelId)
  
  return `${harnessName}: ${modelName}`
}

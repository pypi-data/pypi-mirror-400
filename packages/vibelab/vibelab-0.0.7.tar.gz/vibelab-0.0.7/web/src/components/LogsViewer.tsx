import { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import { cn } from '../lib/cn'
import { Button } from './ui/Button'
import { User, Bot, Wrench, Check, X, HelpCircle } from 'lucide-react'

type ViewMode = 'chat' | 'raw'

// Unified message types after parsing
interface UnifiedMessage {
  type: 'system' | 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'thinking' | 'result' | 'text'
  raw: string
  data: any
}

// Parse a single log line into a unified message
function parseLogLine(line: string): UnifiedMessage | null {
  const trimmed = line.trim()
  if (!trimmed) return null
  
  if (!trimmed.startsWith('{')) {
    return { type: 'text', raw: line, data: { text: line } }
  }
  
  try {
    const parsed = JSON.parse(trimmed)
    return normalizeMessage(parsed, line)
  } catch {
    return { type: 'text', raw: line, data: { text: line } }
  }
}

// Normalize different log formats into unified structure
// Supports: Claude Code, Cursor/Composer, and OpenAI Codex formats
function normalizeMessage(parsed: any, raw: string): UnifiedMessage | null {
  const type = parsed.type
  
  switch (type) {
    // === Claude Code / Cursor formats ===
    case 'system':
      return { type: 'system', raw, data: parsed }
    
    case 'user': {
      // Check if this is a tool result (Claude Code style)
      const content = parsed.message?.content
      if (Array.isArray(content)) {
        const toolResult = content.find((c: any) => c.type === 'tool_result')
        if (toolResult) {
          return {
            type: 'tool_result',
            raw,
            data: {
              tool_use_id: toolResult.tool_use_id,
              content: toolResult.content,
              is_error: toolResult.is_error,
              // Also include parsed result if available
              parsed_result: parsed.tool_use_result
            }
          }
        }
      }
      // Regular user message
      return { type: 'user', raw, data: parsed }
    }
    
    case 'assistant': {
      // Check for tool_use in content (Claude Code style)
      const content = parsed.message?.content
      if (Array.isArray(content)) {
        const toolUse = content.find((c: any) => c.type === 'tool_use')
        if (toolUse) {
          return {
            type: 'tool_call',
            raw,
            data: {
              id: toolUse.id,
              name: toolUse.name,
              input: toolUse.input,
              status: 'started', // Claude Code doesn't have separate started/completed
              // Keep the text content too if any
              text: content.find((c: any) => c.type === 'text')?.text
            }
          }
        }
        // Check for just text content
        const textContent = content.find((c: any) => c.type === 'text')
        if (textContent) {
          return {
            type: 'assistant',
            raw,
            data: { text: textContent.text, message: parsed.message }
          }
        }
      }
      return { type: 'assistant', raw, data: parsed }
    }
    
    case 'thinking':
      return { type: 'thinking', raw, data: parsed }
    
    case 'tool_call': {
      // Composer style tool calls
      const toolCall = parsed.tool_call
      let name = 'unknown'
      let input = {}
      let result = null
      
      // Extract from nested structure (readToolCall, editToolCall, etc.)
      if (toolCall) {
        const keys = Object.keys(toolCall).filter(k => k.endsWith('ToolCall'))
        if (keys.length > 0) {
          const key = keys[0]
          name = key.replace('ToolCall', '')
          input = toolCall[key]?.args || {}
          if (toolCall[key]?.result) {
            result = toolCall[key].result.success || toolCall[key].result.error
          }
        }
      }
      
      return {
        type: 'tool_call',
        raw,
        data: {
          id: parsed.call_id,
          name,
          input,
          result,
          status: parsed.subtype, // 'started' or 'completed'
          is_error: !!toolCall?.[Object.keys(toolCall).find(k => k.endsWith('ToolCall')) || '']?.result?.error
        }
      }
    }
    
    case 'result':
      return {
        type: 'result',
        raw,
        data: {
          success: !parsed.is_error,
          duration_ms: parsed.duration_ms,
          result: parsed.result,
          cost_usd: parsed.total_cost_usd,
          usage: parsed.usage,
          modelUsage: parsed.modelUsage
        }
      }
    
    // === OpenAI Codex format ===
    // Codex uses: thread.started, turn.started, item.started, item.completed, turn.completed
    case 'thread.started':
      return {
        type: 'system',
        raw,
        data: {
          subtype: 'init',
          thread_id: parsed.thread_id,
          model: 'OpenAI Codex',
        }
      }
    
    case 'turn.started':
      // Turn started - can be ignored or shown as system message
      return null
    
    case 'item.started': {
      // Tool/command execution started
      const item = parsed.item
      if (item?.type === 'command_execution') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'shell',
            input: { command: item.command },
            status: 'started',
            is_error: false
          }
        }
      }
      if (item?.type === 'file_edit') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'edit',
            input: { file_path: item.file_path, content: item.content },
            status: 'started',
            is_error: false
          }
        }
      }
      if (item?.type === 'file_read') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'read',
            input: { file_path: item.file_path },
            status: 'started',
            is_error: false
          }
        }
      }
      return { type: 'text', raw, data: parsed }
    }
    
    case 'item.completed': {
      // Tool/command completed OR agent message
      const item = parsed.item
      if (item?.type === 'agent_message') {
        return {
          type: 'assistant',
          raw,
          data: { text: item.text }
        }
      }
      if (item?.type === 'command_execution') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'shell',
            input: { command: item.command },
            result: item.aggregated_output || `Exit code: ${item.exit_code}`,
            status: 'completed',
            is_error: item.exit_code !== 0
          }
        }
      }
      if (item?.type === 'file_edit') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'edit',
            input: { file_path: item.file_path },
            result: item.status === 'completed' ? 'File edited successfully' : item.error,
            status: 'completed',
            is_error: item.status !== 'completed'
          }
        }
      }
      if (item?.type === 'file_read') {
        return {
          type: 'tool_call',
          raw,
          data: {
            id: item.id,
            name: 'read',
            input: { file_path: item.file_path },
            result: item.content || 'File read successfully',
            status: 'completed',
            is_error: false
          }
        }
      }
      return { type: 'text', raw, data: parsed }
    }
    
    case 'turn.completed':
      // End of turn with usage stats
      return {
        type: 'result',
        raw,
        data: {
          success: true,
          usage: parsed.usage,
          input_tokens: parsed.usage?.input_tokens,
          output_tokens: parsed.usage?.output_tokens,
          cached_input_tokens: parsed.usage?.cached_input_tokens
        }
      }
    
    default:
      return { type: 'text', raw, data: parsed }
  }
}

// Group messages for better display
function groupMessages(messages: UnifiedMessage[]): UnifiedMessage[][] {
  const groups: UnifiedMessage[][] = []
  let currentToolGroup: UnifiedMessage[] = []
  
  for (const msg of messages) {
    // Skip empty thinking deltas
    if (msg.type === 'thinking' && msg.data?.subtype === 'delta' && !msg.data?.text) {
      continue
    }
    
    // Group tool calls with their results
    if (msg.type === 'tool_call') {
      if (msg.data.status === 'started' || !msg.data.status) {
        // Start new tool group
        if (currentToolGroup.length > 0) {
          groups.push(currentToolGroup)
        }
        currentToolGroup = [msg]
      } else if (msg.data.status === 'completed') {
        currentToolGroup.push(msg)
        groups.push(currentToolGroup)
        currentToolGroup = []
      }
      continue
    }
    
    // Tool results (Claude Code style) - attach to previous tool call
    if (msg.type === 'tool_result') {
      if (currentToolGroup.length > 0) {
        currentToolGroup.push(msg)
        groups.push(currentToolGroup)
        currentToolGroup = []
      } else {
        groups.push([msg])
      }
      continue
    }
    
    // Flush any pending tool group
    if (currentToolGroup.length > 0) {
      groups.push(currentToolGroup)
      currentToolGroup = []
    }
    
    groups.push([msg])
  }
  
  // Flush remaining
  if (currentToolGroup.length > 0) {
    groups.push(currentToolGroup)
  }
  
  return groups
}

// Icons (using Lucide components)
const UserIcon = () => <User className="w-3.5 h-3.5" />
const BotIcon = () => <Bot className="w-3.5 h-3.5" />
const ToolIcon = () => <Wrench className="w-3 h-3" />
const CheckIcon = () => <Check className="w-3 h-3" />
const ErrorIcon = () => <X className="w-3 h-3" />
const ThinkingIcon = () => <HelpCircle className="w-3 h-3 animate-pulse" />

// Format path for display
function formatPath(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  if (parts.length <= 3) return path
  return '.../' + parts.slice(-3).join('/')
}

// Format tool name for display
function formatToolName(name: string): string {
  // Handle camelCase and snake_case
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .replace(/^\s+/, '')
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ')
}

// System init message
function SystemInitCard({ data }: { data: any }) {
  return (
    <div className="flex items-center gap-2 py-2 px-3 bg-surface-2 rounded-lg text-xs">
      <span className="text-status-info">●</span>
      <span className="text-text-secondary">Session started</span>
      <span className="text-text-tertiary">•</span>
      <span className="font-mono text-text-tertiary">{data.model || 'unknown'}</span>
      {data.cwd && (
        <>
          <span className="text-text-tertiary">•</span>
          <span className="font-mono text-text-disabled truncate max-w-[200px]" title={data.cwd}>
            {formatPath(data.cwd)}
          </span>
        </>
      )}
      {data.claude_code_version && (
        <>
          <span className="text-text-tertiary">•</span>
          <span className="text-text-disabled">v{data.claude_code_version}</span>
        </>
      )}
      {data.thread_id && (
        <>
          <span className="text-text-tertiary">•</span>
          <span className="font-mono text-text-disabled truncate max-w-[150px]" title={data.thread_id}>
            {data.thread_id.substring(0, 8)}...
          </span>
        </>
      )}
    </div>
  )
}

// User message
function UserMessageCard({ data }: { data: any }) {
  const content = data.message?.content
  let text = ''
  
  if (typeof content === 'string') {
    text = content
  } else if (Array.isArray(content)) {
    const textBlock = content.find((c: any) => c.type === 'text')
    text = textBlock?.text || ''
  }
  
  if (!text) return null
  
  return (
    <div className="flex gap-3 py-3">
      <div className="shrink-0 w-6 h-6 rounded-full bg-surface-3 flex items-center justify-center text-text-secondary">
        <UserIcon />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="text-xs font-medium text-text-tertiary mb-1">You</div>
        <div className="text-sm text-text-primary whitespace-pre-wrap">{text}</div>
      </div>
    </div>
  )
}

// Assistant message
function AssistantMessageCard({ data }: { data: any }) {
  const text = data.text || ''
  if (!text.trim()) return null
  
  return (
    <div className="flex gap-3 py-3">
      <div className="shrink-0 w-6 h-6 rounded-full bg-accent flex items-center justify-center text-on-accent">
        <BotIcon />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="text-xs font-medium text-text-tertiary mb-1">Assistant</div>
        <div className="text-sm text-text-primary whitespace-pre-wrap">{text.trim()}</div>
      </div>
    </div>
  )
}

// Thinking indicator
function ThinkingCard({ messages }: { messages: UnifiedMessage[] }) {
  const [expanded, setExpanded] = useState(false)
  const thinkingText = messages
    .filter(m => m.data?.text)
    .map(m => m.data.text)
    .join('')
  
  if (!thinkingText) {
    return (
      <div className="flex items-center gap-2 py-2 text-xs text-text-tertiary">
        <ThinkingIcon />
        <span>Thinking...</span>
      </div>
    )
  }
  
  return (
    <div className="py-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-text-tertiary hover:text-text-secondary transition-colors"
      >
        <ThinkingIcon />
        <span>Thinking</span>
        <span className="text-text-disabled">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="mt-2 pl-5 text-xs text-text-tertiary italic whitespace-pre-wrap border-l-2 border-border-muted">
          {thinkingText}
        </div>
      )}
    </div>
  )
}

// Tool call card (unified for both formats)
function ToolCallCard({ messages }: { messages: UnifiedMessage[] }) {
  const [expanded, setExpanded] = useState(false)
  
  const toolCall = messages.find(m => m.type === 'tool_call')
  const toolResult = messages.find(m => m.type === 'tool_result' || (m.type === 'tool_call' && m.data.status === 'completed'))
  
  if (!toolCall) return null
  
  const name = toolCall.data.name || 'unknown'
  const input = toolCall.data.input || {}
  const displayName = formatToolName(name)
  
  // Determine result
  let result: any = null
  let isError = false
  let isCompleted = false
  
  if (toolResult) {
    isCompleted = true
    if (toolResult.type === 'tool_result') {
      // Claude Code style
      result = toolResult.data.content || toolResult.data.parsed_result
      isError = toolResult.data.is_error
    } else {
      // Composer style
      result = toolResult.data.result
      isError = toolResult.data.is_error
    }
  }
  
  // Get inline info
  let inlineInfo = ''
  if (input.file_path || input.path) {
    inlineInfo = formatPath(input.file_path || input.path)
  } else if (input.query) {
    inlineInfo = input.query.substring(0, 40) + (input.query.length > 40 ? '...' : '')
  } else if (input.command) {
    inlineInfo = input.command.substring(0, 40) + (input.command.length > 40 ? '...' : '')
  }
  
  return (
    <div className="my-2 ml-9">
      <div className={cn(
        'border rounded-lg overflow-hidden',
        isCompleted 
          ? isError ? 'border-status-error/30 bg-status-error-muted' : 'border-status-success/30 bg-status-success-muted'
          : 'border-status-warning/30 bg-status-warning-muted'
      )}>
        {/* Header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-black/5 transition-colors"
        >
          <span className={cn(
            'shrink-0',
            isCompleted 
              ? isError ? 'text-status-error' : 'text-status-success'
              : 'text-status-warning'
          )}>
            {isCompleted ? (isError ? <ErrorIcon /> : <CheckIcon />) : <ToolIcon />}
          </span>
          <span className="text-sm font-medium text-text-primary">{displayName}</span>
          {inlineInfo && (
            <span className="text-xs text-text-tertiary font-mono truncate max-w-[300px]">{inlineInfo}</span>
          )}
          <span className="ml-auto text-text-disabled text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
        
        {/* Expanded content */}
        {expanded && (
          <div className="border-t border-inherit">
            {/* Input */}
            <div className="px-3 py-2 bg-surface/50">
              <div className="text-xs text-text-tertiary mb-1">Input</div>
              <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-40">
                {JSON.stringify(input, null, 2)}
              </pre>
            </div>
            
            {/* Result */}
            {result && (
              <div className="px-3 py-2 border-t border-inherit">
                <div className="text-xs text-text-tertiary mb-1">
                  {isError ? 'Error' : 'Result'}
                </div>
                <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-48 whitespace-pre-wrap">
                  {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Tool result card (standalone, for when we don't have the matching call)
function ToolResultCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false)
  const isError = data.is_error
  const content = data.content || data.parsed_result
  
  return (
    <div className="my-2 ml-9">
      <div className={cn(
        'border rounded-lg overflow-hidden',
        isError ? 'border-status-error/30 bg-status-error-muted' : 'border-status-success/30 bg-status-success-muted'
      )}>
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-black/5 transition-colors"
        >
          <span className={isError ? 'text-status-error' : 'text-status-success'}>
            {isError ? <ErrorIcon /> : <CheckIcon />}
          </span>
          <span className="text-sm text-text-secondary">Tool Result</span>
          <span className="ml-auto text-text-disabled text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
        {expanded && (
          <div className="px-3 py-2 border-t border-inherit">
            <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-48 whitespace-pre-wrap">
              {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

// Result message (final)
function ResultCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false)
  const isError = !data.success
  const duration = data.duration_ms ? `${(data.duration_ms / 1000).toFixed(1)}s` : null
  const cost = data.cost_usd ? `$${data.cost_usd.toFixed(4)}` : null
  
  // Token counts (for Codex format)
  const inputTokens = data.input_tokens || data.usage?.input_tokens
  const outputTokens = data.output_tokens || data.usage?.output_tokens
  const cachedTokens = data.cached_input_tokens || data.usage?.cached_input_tokens
  const hasTokenInfo = inputTokens || outputTokens
  
  return (
    <div className="my-4">
      <div className="flex items-center justify-center gap-3">
        <div className="h-px flex-1 bg-border" />
        <button
          onClick={() => setExpanded(!expanded)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs transition-colors',
            isError ? 'bg-status-error-muted text-status-error' : 'bg-status-success-muted text-status-success',
            'hover:brightness-95'
          )}
        >
          {isError ? <ErrorIcon /> : <CheckIcon />}
          <span className="font-medium">{isError ? 'Failed' : 'Completed'}</span>
          {duration && <span className="text-text-tertiary">• {duration}</span>}
          {cost && <span className="text-text-tertiary">• {cost}</span>}
          {hasTokenInfo && (
            <span className="text-text-tertiary">
              • {inputTokens?.toLocaleString() || 0} in / {outputTokens?.toLocaleString() || 0} out
            </span>
          )}
          <span className="text-text-disabled ml-1">{expanded ? '▼' : '▶'}</span>
        </button>
        <div className="h-px flex-1 bg-border" />
      </div>
      
      {expanded && (data.modelUsage || hasTokenInfo) && (
        <div className="mt-3 p-3 bg-surface-2 rounded-lg text-xs">
          <div className="text-text-tertiary mb-2">Usage</div>
          <div className="space-y-1 font-mono">
            {data.modelUsage ? (
              Object.entries(data.modelUsage).map(([model, usage]: [string, any]) => (
                <div key={model} className="flex items-center justify-between">
                  <span className="text-text-secondary">{model}</span>
                  <span className="text-text-tertiary">
                    {usage.inputTokens?.toLocaleString() || 0} in / {usage.outputTokens?.toLocaleString() || 0} out
                    {usage.costUSD && <span className="ml-2 text-status-success">${usage.costUSD.toFixed(4)}</span>}
                  </span>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Tokens</span>
                <span className="text-text-tertiary">
                  {inputTokens?.toLocaleString() || 0} in / {outputTokens?.toLocaleString() || 0} out
                  {cachedTokens ? <span className="ml-2 text-text-disabled">({cachedTokens.toLocaleString()} cached)</span> : null}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Chat view
function ChatView({ messages }: { messages: UnifiedMessage[] }) {
  const groups = useMemo(() => groupMessages(messages), [messages])
  
  return (
    <div className="space-y-1">
      {groups.map((group, idx) => {
        const firstMsg = group[0]
        
        switch (firstMsg.type) {
          case 'system':
            if (firstMsg.data?.subtype === 'init') {
              return <SystemInitCard key={idx} data={firstMsg.data} />
            }
            return null
          
          case 'user':
            return <UserMessageCard key={idx} data={firstMsg.data} />
          
          case 'thinking':
            return <ThinkingCard key={idx} messages={group} />
          
          case 'assistant':
            return <AssistantMessageCard key={idx} data={firstMsg.data} />
          
          case 'tool_call':
            return <ToolCallCard key={idx} messages={group} />
          
          case 'tool_result':
            // Standalone tool result (no matching call found)
            return <ToolResultCard key={idx} data={firstMsg.data} />
          
          case 'result':
            return <ResultCard key={idx} data={firstMsg.data} />
          
          case 'text':
            if (!firstMsg.data?.text?.trim()) return null
            return (
              <div key={idx} className="py-1 text-xs text-text-tertiary font-mono">
                {firstMsg.data.text}
              </div>
            )
          
          default:
            return null
        }
      })}
    </div>
  )
}

// Raw log view
function RawView({ text }: { text: string }) {
  const lines = text.split('\n')
  
  return (
    <div className="font-mono text-xs leading-relaxed">
      {lines.map((line, idx) => {
        let color = 'text-text-secondary'
        
        if (line.trim().startsWith('{')) {
          try {
            const parsed = JSON.parse(line.trim())
            // Support both Claude Code and Codex event types
            const typeColors: Record<string, string> = {
              // Claude Code / Cursor types
              'system': 'text-text-tertiary',
              'user': 'text-status-info',
              'thinking': 'text-text-disabled',
              'assistant': 'text-accent',
              'tool_call': 'text-status-warning',
              'result': 'text-status-success',
              // OpenAI Codex types
              'thread.started': 'text-text-tertiary',
              'turn.started': 'text-text-disabled',
              'item.started': 'text-status-warning',
              'item.completed': 'text-accent',
              'turn.completed': 'text-status-success',
            }
            color = typeColors[parsed.type] || 'text-text-tertiary'
          } catch {
            // Invalid JSON
          }
        }
        
        return (
          <div key={idx} className={cn('py-0.5 hover:bg-surface-2 px-1 -mx-1 rounded', color)}>
            <span className="text-text-disabled select-none mr-3 inline-block w-8 text-right">{idx + 1}</span>
            {line || '\u00A0'}
          </div>
        )
      })}
    </div>
  )
}

interface LogsViewerProps {
  logs: string
  title?: string
  defaultMode?: ViewMode
  maxHeight?: string
}

export default function LogsViewer({ 
  logs, 
  title = 'Output',
  defaultMode = 'chat',
  maxHeight = '600px'
}: LogsViewerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(defaultMode)
  const [autoScroll, setAutoScroll] = useState(true)
  const containerRef = useRef<HTMLDivElement>(null)

  const messages = useMemo(() => {
    return logs.split('\n').map(parseLogLine).filter(Boolean) as UnifiedMessage[]
  }, [logs])

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
    setAutoScroll(isAtBottom)
  }, [])

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  if (!logs) {
    return (
      <div className="bg-surface border border-border rounded-lg p-8 text-center">
        <div className="text-text-tertiary">No output yet</div>
      </div>
    )
  }

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface">
      {/* Header */}
      <div className="flex items-center justify-between bg-surface-2 px-4 py-2.5 border-b border-border">
        <span className="text-sm font-medium text-text-primary">{title}</span>
        
        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="flex rounded-lg overflow-hidden border border-border bg-surface">
            <button
              onClick={() => setViewMode('chat')}
              className={cn(
                'px-3 py-1.5 text-xs font-medium transition-all',
                viewMode === 'chat'
                  ? 'bg-accent text-on-accent'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-2'
              )}
            >
              Chat
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={cn(
                'px-3 py-1.5 text-xs font-medium transition-all border-l border-border',
                viewMode === 'raw'
                  ? 'bg-accent text-on-accent'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-2'
              )}
            >
              Raw
            </button>
          </div>
          
          {/* Scroll to bottom */}
          <Button
            variant={autoScroll ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => {
              setAutoScroll(true)
              if (containerRef.current) {
                containerRef.current.scrollTop = containerRef.current.scrollHeight
              }
            }}
            title={autoScroll ? 'Auto-scroll enabled' : 'Click to scroll to bottom'}
          >
            ↓
          </Button>
        </div>
      </div>

      {/* Content */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="p-4 overflow-auto bg-canvas"
        style={{ maxHeight }}
      >
        {viewMode === 'chat' ? (
          <ChatView messages={messages} />
        ) : (
          <RawView text={logs} />
        )}
      </div>
    </div>
  )
}

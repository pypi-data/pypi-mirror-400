import { useMemo, useState } from 'react'
import { useElementSize } from '../lib/useElementSize'

export type TradeoffXMetric = 'time' | 'cost'

export type QualityTradeoffPoint = {
  key: string
  provider: string
  label: string
  quality: number
  hasQuality: boolean
  durationMs?: number | null
  costUsd?: number | null
  count?: number
}

const PROVIDER_COLORS = [
  '#60a5fa', // blue
  '#34d399', // emerald
  '#f472b6', // pink
  '#f59e0b', // amber
  '#a78bfa', // violet
  '#22d3ee', // cyan
  '#fb7185', // rose
  '#84cc16', // lime
]

function formatDuration(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(0)}s`
  return `${Math.round(ms / 60000)}m`
}

function formatUsd(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`
  if (cost < 1) return `$${cost.toFixed(3)}`
  if (cost < 10) return `$${cost.toFixed(2)}`
  return `$${cost.toFixed(1)}`
}

export function QualityTradeoffPlot({
  points,
  xMetric,
  onPointClick,
  emptyText = 'No completed results yet',
}: {
  points: QualityTradeoffPoint[]
  xMetric: TradeoffXMetric
  onPointClick?: (point: QualityTradeoffPoint) => void
  emptyText?: string
}) {
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const [hoveredKey, setHoveredKey] = useState<string | null>(null)

  const providerColorByName = useMemo(() => {
    const providers = Array.from(new Set(points.map((p) => p.provider ?? 'unknown'))).sort()
    const map = new Map<string, string>()
    providers.forEach((p, idx) => map.set(p, PROVIDER_COLORS[idx % PROVIDER_COLORS.length]!))
    return map
  }, [points])

  const getProviderColor = (provider: string | null | undefined) => {
    const key = provider ?? 'unknown'
    return providerColorByName.get(key) ?? '#6b7280'
  }

  const filtered = useMemo(() => {
    return points.filter((p) => (xMetric === 'time' ? p.durationMs != null : p.costUsd != null))
  }, [points, xMetric])

  if (filtered.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-text-tertiary text-sm">
        {emptyText}
      </div>
    )
  }

  const fallbackWidth = 720
  const width = size.width > 0 ? size.width : fallbackWidth
  const height = size.height > 0 ? size.height : Math.round(Math.min(300, Math.max(120, width * 0.3)))
  const padding = { top: 18, right: 18, bottom: 44, left: 56 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  const xValues =
    xMetric === 'time'
      ? filtered.map((p) => p.durationMs!).filter((v): v is number => v != null)
      : filtered.map((p) => p.costUsd!).filter((v): v is number => v != null)

  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)
  const xRange = maxX - minX || 1
  const xScale = (x: number) => padding.left + ((x - minX) / xRange) * chartWidth

  // Y scale: quality (1-4)
  const yScale = (q: number) => padding.top + chartHeight - ((q - 1) / 3) * chartHeight

  const xTicks = [minX, (minX + maxX) / 2, maxX]
  const yTicks = [1, 2, 3, 4]
  const yLabels = ['Bad', 'Workable', 'Good', 'Perfect']

  const maxCount = Math.max(...filtered.map((p) => p.count ?? 1))
  const rScale = (n: number) => {
    const t = maxCount > 0 ? Math.sqrt(n) / Math.sqrt(maxCount) : 0
    return 5 + t * 5
  }

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-0 overflow-hidden">
      <svg width={width} height={height} className="overflow-visible" style={{ maxHeight: '100%' }}>
        {/* Grid lines */}
        <g className="text-border">
          {yTicks.map((tick) => (
            <line
              key={`y-grid-${tick}`}
              x1={padding.left}
              y1={yScale(tick)}
              x2={width - padding.right}
              y2={yScale(tick)}
              stroke="currentColor"
              strokeOpacity={0.3}
              strokeDasharray="4,4"
            />
          ))}
        </g>

        {/* X axis */}
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="currentColor"
          className="text-border"
        />
        {xTicks.map((tick) => (
          <g key={`x-tick-${tick}`}>
            <text
              x={xScale(tick)}
              y={height - padding.bottom + 16}
              textAnchor="middle"
              className="text-[10px] fill-text-tertiary"
            >
              {xMetric === 'time' ? formatDuration(tick) : formatUsd(tick)}
            </text>
          </g>
        ))}
        <text
          x={padding.left + chartWidth / 2}
          y={height - 4}
          textAnchor="middle"
          className="text-[10px] fill-text-tertiary"
        >
          {xMetric === 'time' ? 'Execution Time' : 'Cost (USD)'}
        </text>

        {/* Y axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="currentColor"
          className="text-border"
        />
        {yTicks.map((tick, i) => (
          <g key={`y-tick-${tick}`}>
            <text
              x={padding.left - 8}
              y={yScale(tick) + 3}
              textAnchor="end"
              className="text-[10px] fill-text-tertiary"
            >
              {yLabels[i]}
            </text>
          </g>
        ))}

        {/* Points */}
        {filtered.map((p) => {
          const isHovered = hoveredKey === p.key
          const xValue = (xMetric === 'time' ? p.durationMs : p.costUsd) ?? 0
          const r = rScale(p.count ?? 1)
          return (
            <g key={p.key}>
              <circle
                cx={xScale(xValue)}
                cy={yScale(p.quality)}
                r={isHovered ? r + 2 : r}
                fill={getProviderColor(p.provider)}
                fillOpacity={p.hasQuality ? (isHovered ? 1 : 0.85) : (isHovered ? 0.6 : 0.4)}
                stroke={isHovered ? '#fff' : (p.hasQuality ? 'transparent' : '#6b7280')}
                strokeWidth={p.hasQuality ? 2 : 1}
                strokeDasharray={p.hasQuality ? undefined : '2,2'}
                className={onPointClick ? 'cursor-pointer transition-all duration-150' : 'cursor-default transition-all duration-150'}
                onMouseEnter={() => setHoveredKey(p.key)}
                onMouseLeave={() => setHoveredKey(null)}
                onClick={() => onPointClick?.(p)}
              />
            </g>
          )
        })}
      </svg>

      {/* Tooltip */}
      {hoveredKey && (() => {
        const p = filtered.find((x) => x.key === hoveredKey)
        if (!p) return null
        const xValue = (xMetric === 'time' ? p.durationMs : p.costUsd) ?? 0
        const x = xScale(xValue)
        const y = yScale(p.quality)
        return (
          <div
            className="absolute pointer-events-none bg-surface-3 border border-border rounded-md shadow-lg px-2 py-1 text-xs z-10"
            style={{
              left: x + 12,
              top: y - 20,
              transform: x > width - 140 ? 'translateX(-100%)' : undefined,
            }}
          >
            <div className="font-medium text-text-primary truncate max-w-[260px]">{p.label}</div>
            <div className="text-text-tertiary">
              {(xMetric === 'time' && p.durationMs != null)
                ? formatDuration(p.durationMs)
                : (p.costUsd != null ? formatUsd(p.costUsd) : '—')}
              {' • '}
              {p.provider}
              {' • '}
              Quality: {p.hasQuality ? p.quality : 'N/A'}
              {p.count != null ? ` • n=${p.count}` : ''}
            </div>
          </div>
        )
      })()}
    </div>
  )
}



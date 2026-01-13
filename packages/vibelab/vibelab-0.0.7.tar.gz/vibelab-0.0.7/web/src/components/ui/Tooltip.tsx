import { useState, type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface TooltipProps {
  children: ReactNode
  content: string
  side?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

export function Tooltip({ children, content, side = 'top', className }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  const sideClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  return (
    <div
      className={cn('relative inline-block', className)}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          className={cn(
            'absolute z-50 px-2 py-1.5',
            'text-xs text-text-primary',
            'bg-surface-2 border border-border rounded-md',
            'shadow-lg shadow-black/20',
            'whitespace-nowrap max-w-xs',
            sideClasses[side],
            'pointer-events-none'
          )}
        >
          {content}
          {/* Arrow */}
          {side === 'top' && (
            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
              <div className="w-2 h-2 bg-surface-2 border-r border-b border-border rotate-45" />
            </div>
          )}
          {side === 'bottom' && (
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 -mb-1">
              <div className="w-2 h-2 bg-surface-2 border-l border-t border-border rotate-45" />
            </div>
          )}
          {side === 'left' && (
            <div className="absolute left-full top-1/2 -translate-y-1/2 -ml-1">
              <div className="w-2 h-2 bg-surface-2 border-r border-t border-border rotate-45" />
            </div>
          )}
          {side === 'right' && (
            <div className="absolute right-full top-1/2 -translate-y-1/2 -mr-1">
              <div className="w-2 h-2 bg-surface-2 border-l border-b border-border rotate-45" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}


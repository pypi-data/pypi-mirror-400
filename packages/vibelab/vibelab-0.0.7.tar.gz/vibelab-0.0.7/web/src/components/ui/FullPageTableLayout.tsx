import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface FullPageTableLayoutProps {
  /** Header content (title, actions, filters) - receives internal padding */
  header: ReactNode
  /** Table content - renders edge-to-edge with full height. Optional when isEmpty is true. */
  children?: ReactNode
  /** Empty state to show when there's no data */
  emptyState?: ReactNode
  /** Whether to show the empty state */
  isEmpty?: boolean
  /** Additional className for the container */
  className?: string
}

/**
 * FullPageTableLayout provides a full-page table experience:
 * - Header area with proper padding for title/actions
 * - Table extends edge-to-edge (no side padding)
 * - Table fills remaining vertical space with internal scrolling
 * - No parent scrolling - everything fits in viewport
 * 
 * Use this for list pages like Scenarios, Datasets, Runs, Active Jobs.
 */
export function FullPageTableLayout({ 
  header, 
  children, 
  emptyState,
  isEmpty = false,
  className 
}: FullPageTableLayoutProps) {
  return (
    <div className={cn(
      // Cancel out parent padding and fill available space
      '-mx-6 -my-6 -mb-16 flex flex-col h-[calc(100vh-var(--navbar-height,56px)-var(--footer-height,40px))]',
      className
    )}>
      {/* Header area with padding */}
      <div className="shrink-0 px-6 pt-6 pb-4">
        {header}
      </div>
      
      {/* Table area - fills remaining space */}
      {isEmpty && emptyState ? (
        <div className="flex-1 flex items-center justify-center px-6">
          {emptyState}
        </div>
      ) : (
        <div className="flex-1 min-h-0 border-t border-border">
          {children}
        </div>
      )}
    </div>
  )
}

interface TableHeaderProps {
  title: string
  description?: string
  actions?: ReactNode
  /** Item count to display (e.g., "24 scenarios") */
  count?: number
  countLabel?: string
  className?: string
}

/**
 * Standard header for FullPageTableLayout.
 * Includes title, optional description, count badge, and actions.
 */
FullPageTableLayout.Header = function TableHeader({ 
  title, 
  description, 
  actions, 
  count,
  countLabel,
  className 
}: TableHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between gap-6', className)}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
          {count !== undefined && (
            <span className="text-sm text-text-tertiary bg-surface-2 px-2 py-0.5 rounded-full">
              {count} {countLabel || 'items'}
            </span>
          )}
        </div>
        {description && (
          <p className="text-sm text-text-secondary leading-relaxed mt-1">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  )
}


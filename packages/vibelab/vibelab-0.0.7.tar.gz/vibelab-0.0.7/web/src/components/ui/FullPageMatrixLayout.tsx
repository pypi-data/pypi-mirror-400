import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface FullPageMatrixLayoutProps {
  /** Header area with title, summary metrics, and plot */
  header: ReactNode
  /** Matrix content - renders edge-to-edge with full height */
  children?: ReactNode
  /** Empty state to show when there's no data */
  emptyState?: ReactNode
  /** Whether to show the empty state */
  isEmpty?: boolean
  /** Additional className for the container */
  className?: string
}

/**
 * FullPageMatrixLayout provides a full-page experience for analytics/matrix views:
 * - Compact header area with title, metrics, and plot
 * - Matrix extends edge-to-edge with internal scrolling
 * - Matrix fills all remaining vertical space
 * 
 * Use this for analytics pages like GlobalReport and DatasetAnalytics.
 */
export function FullPageMatrixLayout({ 
  header, 
  children, 
  emptyState,
  isEmpty = false,
  className 
}: FullPageMatrixLayoutProps) {
  return (
    <div className={cn(
      // Cancel out parent padding and fill available space
      '-mx-6 -my-6 -mb-16 flex flex-col h-[calc(100vh-var(--navbar-height,56px)-var(--footer-height,40px))]',
      className
    )}>
      {/* Header area with padding - contains title, metrics, plot */}
      <div className="shrink-0 px-6 pt-5 pb-4">
        {header}
      </div>
      
      {/* Matrix area - fills remaining space */}
      {isEmpty && emptyState ? (
        <div className="flex-1 flex items-center justify-center px-6">
          {emptyState}
        </div>
      ) : (
        <div className="flex-1 min-h-0 overflow-hidden">
          {children}
        </div>
      )}
    </div>
  )
}




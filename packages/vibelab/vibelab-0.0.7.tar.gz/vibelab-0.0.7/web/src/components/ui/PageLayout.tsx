import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

type PageWidth = 'narrow' | 'medium' | 'wide' | 'full'

interface PageLayoutProps {
  /** Width variant for the page content */
  width?: PageWidth
  /** Page content */
  children: ReactNode
  /** Additional className for the container */
  className?: string
}

const widthClasses: Record<PageWidth, string> = {
  narrow: 'max-w-2xl',   // Forms, simple creation pages
  medium: 'max-w-4xl',   // Medium content, detail pages with moderate width
  wide: 'max-w-6xl',     // Wider content
  full: 'max-w-7xl',     // Full width tables, matrices, dashboards
}

/**
 * PageLayout provides consistent width and spacing for all pages.
 * 
 * Width variants:
 * - `narrow` (max-w-2xl): Forms, creation pages
 * - `medium` (max-w-4xl): Detail pages, moderate content
 * - `wide` (max-w-6xl): Wider content  
 * - `full` (max-w-7xl): Tables, matrices, dashboards (default)
 */
export function PageLayout({ width = 'full', children, className }: PageLayoutProps) {
  return (
    <div className={cn(widthClasses[width], 'mx-auto w-full', className)}>
      {children}
    </div>
  )
}




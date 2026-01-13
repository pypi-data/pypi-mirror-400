import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface PageHeaderProps {
  title: string
  description?: string
  actions?: ReactNode
  className?: string
}

export function PageHeader({ title, description, actions, className }: PageHeaderProps) {
  return (
    <div className={cn('mb-6', className)}>
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-semibold text-text-primary mb-1">{title}</h1>
          {description && (
            <p className="text-sm text-text-secondary leading-relaxed">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
      </div>
    </div>
  )
}

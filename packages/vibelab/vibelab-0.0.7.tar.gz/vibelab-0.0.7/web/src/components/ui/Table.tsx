import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface TableProps {
  children: ReactNode
  className?: string
  /** Max height for the table. Use 'none' or 'full' for flex-based layouts. */
  maxHeight?: string | 'none' | 'full'
  /** Whether table is used in full-page mode (fills parent, no border radius) */
  fullPage?: boolean
}

export function Table({ children, className, maxHeight = '600px', fullPage = false }: TableProps) {
  const isFlexHeight = maxHeight === 'none' || maxHeight === 'full'
  
  return (
    <div 
      className={cn(
        'overflow-hidden',
        !fullPage && 'border border-border rounded-lg',
        fullPage && 'h-full flex flex-col',
        className
      )}
    >
      <div 
        className={cn(
          'overflow-auto',
          fullPage && 'flex-1'
        )}
        style={isFlexHeight ? undefined : { maxHeight }}
      >
        <table className="w-full border-collapse">
          {children}
        </table>
      </div>
    </div>
  )
}

interface TableHeaderProps {
  children: ReactNode
  className?: string
}

Table.Header = function TableHeader({ children, className }: TableHeaderProps) {
  return (
    <thead className={cn('bg-surface-2 sticky top-0 z-10', className)}>
      {children}
    </thead>
  )
}

interface TableBodyProps {
  children: ReactNode
  className?: string
}

Table.Body = function TableBody({ children, className }: TableBodyProps) {
  return <tbody className={cn('bg-surface', className)}>{children}</tbody>
}

interface TableRowProps {
  children: ReactNode
  className?: string
  onClick?: () => void
  selected?: boolean
}

Table.Row = function TableRow({ children, className, onClick, selected }: TableRowProps) {
  return (
    <tr
      className={cn(
        'border-b border-border-muted',
        'transition-colors duration-100',
        onClick && 'cursor-pointer',
        selected 
          ? 'bg-accent-muted' 
          : 'hover:bg-surface-2 active:bg-surface-3',
        className
      )}
      onClick={onClick}
    >
      {children}
    </tr>
  )
}

interface TableHeadProps {
  children?: ReactNode
  className?: string
}

Table.Head = function TableHead({ children, className }: TableHeadProps) {
  return (
    <th
      className={cn(
        'text-left p-3 text-xs font-semibold text-text-secondary uppercase tracking-wide',
        'bg-surface-2 border-b border-border',
        className
      )}
    >
      {children}
    </th>
  )
}

interface TableCellProps {
  children?: ReactNode
  className?: string
  mono?: boolean
}

Table.Cell = function TableCell({ children, className, mono }: TableCellProps) {
  return (
    <td className={cn('p-3 text-sm', mono && 'font-mono', className)}>
      {children}
    </td>
  )
}

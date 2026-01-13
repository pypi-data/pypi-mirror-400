import { Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { cn } from '../lib/cn'
import { listActiveTasks, getReviewQueueStats } from '../api'
import {
  LayoutGrid,
  FileText,
  Folder,
  Play,
  // Star, // Temporarily disabled - judgements tab
  Server,
  BarChart3,
  Cpu,
  Settings,
  ClipboardCheck,
  GitCompare,
} from 'lucide-react'

// Wrap Lucide icons with correct sizing (18px to match original)
const DashboardIcon = ({ className }: { className?: string }) => <LayoutGrid className={cn('w-[18px] h-[18px]', className)} />
const ScenariosIcon = ({ className }: { className?: string }) => <FileText className={cn('w-[18px] h-[18px]', className)} />
const DatasetsIcon = ({ className }: { className?: string }) => <Folder className={cn('w-[18px] h-[18px]', className)} />
const RunsIcon = ({ className }: { className?: string }) => <Play className={cn('w-[18px] h-[18px]', className)} />
// Temporarily disabled - judgements data available elsewhere
// const JudgementsIcon = ({ className }: { className?: string }) => <Star className={cn('w-[18px] h-[18px]', className)} />
const JobsIcon = ({ className }: { className?: string }) => <Server className={cn('w-[18px] h-[18px]', className)} />
const ReportIcon = ({ className }: { className?: string }) => <BarChart3 className={cn('w-[18px] h-[18px]', className)} />
const ExecutorsIcon = ({ className }: { className?: string }) => <Cpu className={cn('w-[18px] h-[18px]', className)} />
const AdminIcon = ({ className }: { className?: string }) => <Settings className={cn('w-[18px] h-[18px]', className)} />
const ReviewQueueIcon = ({ className }: { className?: string }) => <ClipboardCheck className={cn('w-[18px] h-[18px]', className)} />
const CompareIcon = ({ className }: { className?: string }) => <GitCompare className={cn('w-[18px] h-[18px]', className)} />

interface NavItem {
  path: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  matchPaths?: string[] // Additional paths that should mark this nav item as active
  badge?: number // Optional badge count to show
}

interface NavSection {
  title: string
  items: Omit<NavItem, 'badge'>[]
}

const navSections: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { path: '/', label: 'Dashboard', icon: DashboardIcon },
      { path: '/report', label: 'Report', icon: ReportIcon },
    ],
  },
  {
    title: 'Human Review',
    items: [
      { path: '/review', label: 'Review Queue', icon: ReviewQueueIcon },
      { path: '/pairwise', label: 'Pairwise', icon: CompareIcon },
    ],
  },
  {
    title: 'Data',
    items: [
      { path: '/scenarios', label: 'Scenarios', icon: ScenariosIcon, matchPaths: ['/scenario/'] },
      { path: '/datasets', label: 'Datasets', icon: DatasetsIcon, matchPaths: ['/dataset/'] },
    ],
  },
  {
    title: 'Execution',
    items: [
      { path: '/jobs', label: 'Active Jobs', icon: JobsIcon },
      { path: '/runs', label: 'Runs', icon: RunsIcon, matchPaths: ['/result/'] },
      // Temporarily disabled - judgements data available elsewhere
      // { path: '/judgements', label: 'Judgements', icon: JudgementsIcon },
      { path: '/executors', label: 'Executors', icon: ExecutorsIcon },
    ],
  },
  {
    title: 'System',
    items: [
      { path: '/admin', label: 'Admin', icon: AdminIcon },
    ],
  },
]

export default function Sidebar() {
  const location = useLocation()

  // Fetch active tasks count for badge
  const { data: activeTasks } = useQuery({
    queryKey: ['tasks', 'active', 'sidebar'],
    queryFn: () => listActiveTasks(200),
    refetchInterval: 3000, // Poll every 3 seconds
  })

  // Fetch review queue stats for badge
  const { data: reviewStats } = useQuery({
    queryKey: ['review-queue-stats', 'sidebar'],
    queryFn: getReviewQueueStats,
    refetchInterval: 30000, // Poll every 30 seconds
  })

  const activeJobCount = activeTasks?.length ?? 0
  const reviewQueueLength = reviewStats?.queue_length ?? 0

  const getBadge = (path: string): number | undefined => {
    if (path === '/jobs' && activeJobCount > 0) {
      return activeJobCount
    }
    if (path === '/review' && reviewQueueLength > 0) {
      return reviewQueueLength
    }
    return undefined
  }

  const isActive = (item: Omit<NavItem, 'badge'>) => {
    if (item.path === '/') {
      return location.pathname === '/'
    }
    if (location.pathname.startsWith(item.path)) {
      return true
    }
    // Check additional match paths
    if (item.matchPaths) {
      return item.matchPaths.some(p => location.pathname.startsWith(p))
    }
    return false
  }

  return (
    <aside className="w-56 shrink-0 bg-surface border-r border-border flex flex-col">
      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-4">
        {navSections.map((section) => (
          <div key={section.title}>
            {/* Section header */}
            <div className="px-3 py-1.5 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
              {section.title}
            </div>
            {/* Section items */}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item)
                const badge = getBadge(item.path)
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      active
                        ? 'bg-accent/10 text-accent'
                        : 'text-text-secondary hover:bg-surface-2 hover:text-text-primary'
                    )}
                  >
                    <Icon className={cn('shrink-0', active ? 'text-accent' : 'text-text-tertiary')} />
                    <span className="flex-1">{item.label}</span>
                    {badge !== undefined && (
                      <span className={cn(
                        'ml-auto min-w-5 h-5 px-1.5 rounded-full text-xs font-medium flex items-center justify-center',
                        active
                          ? 'bg-accent text-white'
                          : 'bg-amber-500/20 text-amber-500'
                      )}>
                        {badge > 99 ? '99+' : badge}
                      </span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

    </aside>
  )
}


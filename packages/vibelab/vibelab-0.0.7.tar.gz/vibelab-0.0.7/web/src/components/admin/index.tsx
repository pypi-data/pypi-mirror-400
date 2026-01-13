import { useState } from 'react'
import { PageLayout, PageHeader, Card } from '../ui'
import { Settings, Database, FolderGit2, FolderTree, Layers, FolderKanban } from 'lucide-react'
import { cn } from '../../lib/cn'

import { ProjectsSection } from './ProjectsSection'
import { ConfigSection } from './ConfigSection'
import { ReposSection } from './ReposSection'
import { ScenariosSection } from './ScenariosSection'
import { FileBrowserSection } from './FileBrowserSection'
import { SQLiteSection } from './SQLiteSection'

interface TabDef {
  id: string
  title: string
  icon: React.ReactNode
  description: string
}

const TABS: TabDef[] = [
  { id: 'projects', title: 'Projects', icon: <FolderKanban className="w-4 h-4" />, description: 'Switch between projects or create new ones' },
  { id: 'config', title: 'Configuration', icon: <Settings className="w-4 h-4" />, description: 'Environment variables and system settings' },
  { id: 'repos', title: 'Repositories', icon: <FolderGit2 className="w-4 h-4" />, description: 'Bare git clones for scenario repositories' },
  { id: 'scenarios', title: 'Scenarios', icon: <Layers className="w-4 h-4" />, description: 'Scenarios and their active worktrees' },
  { id: 'files', title: 'Files', icon: <FolderTree className="w-4 h-4" />, description: 'Browse the data directory' },
  { id: 'sqlite', title: 'SQLite', icon: <Database className="w-4 h-4" />, description: 'Execute read-only queries against the database' },
]

export default function Admin() {
  const [activeTab, setActiveTab] = useState('projects')
  const activeTabDef = TABS.find(t => t.id === activeTab)

  const renderTabContent = () => {
    switch (activeTab) {
      case 'projects': return <ProjectsSection />
      case 'config': return <ConfigSection />
      case 'repos': return <ReposSection />
      case 'scenarios': return <ScenariosSection />
      case 'files': return <FileBrowserSection />
      case 'sqlite': return <SQLiteSection />
      default: return null
    }
  }

  return (
    <PageLayout>
      <PageHeader title="Admin" description="System configuration and low-level tools" />
      
      {/* Tab bar */}
      <div className="border-b border-border mb-4">
        <nav className="flex gap-0.5 -mb-px overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-accent text-accent'
                  : 'border-transparent text-text-tertiary hover:text-text-secondary hover:border-border'
              )}
            >
              {tab.icon}
              {tab.title}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab description */}
      {activeTabDef && (
        <p className="text-xs text-text-tertiary mb-3">{activeTabDef.description}</p>
      )}

      {/* Tab content */}
      <Card className="p-3">
        {renderTabContent()}
      </Card>
    </PageLayout>
  )
}


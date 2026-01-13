import { Link } from 'react-router-dom'
import { Button, ThemeToggle } from './ui'
import Logo from './Logo'

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 h-14 border-b border-border bg-surface/95 backdrop-blur-sm shrink-0">
      <div className="h-full px-4 sm:px-6 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-lg font-semibold text-text-primary hover:text-accent transition-colors">
          <Logo size={28} className="text-accent" />
          <span>VibeLab</span>
        </Link>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link to="/run/create">
            <Button size="sm">New Run</Button>
          </Link>
        </div>
      </div>
    </nav>
  )
}

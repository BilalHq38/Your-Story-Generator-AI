import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BookOpen, PlusCircle, Library, Sparkles } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: BookOpen },
  { path: '/create', label: 'New Story', icon: PlusCircle },
  { path: '/library', label: 'Library', icon: Library },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 bg-story-darker/80 backdrop-blur-lg border-b border-story-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <motion.div
              className="p-2 rounded-lg bg-story-accent/20 text-story-accent"
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Sparkles className="w-6 h-6" />
            </motion.div>
            <span className="text-xl font-bold text-gradient">Story Teller</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path
              
              return (
                <Link
                  key={path}
                  to={path}
                  className={`
                    relative px-4 py-2 rounded-lg flex items-center gap-2 transition-colors
                    ${isActive 
                      ? 'text-white' 
                      : 'text-gray-400 hover:text-gray-200'
                    }
                  `}
                >
                  {isActive && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute inset-0 bg-story-accent/20 rounded-lg"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <Icon className="w-4 h-4 relative z-10" />
                  <span className="relative z-10 hidden sm:inline">{label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

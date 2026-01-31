import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Story, NARRATOR_PERSONAS } from '@/types'
import { Clock, ChevronRight, Trash2 } from 'lucide-react'
import { Card } from '@/components/ui'

interface StoryCardProps {
  story: Story
  onDelete?: (id: string) => void
}

export default function StoryCard({ story, onDelete }: StoryCardProps) {
  const narrator = NARRATOR_PERSONAS[story.narrator_persona]
  const createdAt = new Date(story.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })

  return (
    <Link to={`/story/${story.id}`}>
      <Card hoverable className="h-full">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${narrator.color}`}>
              <span>{narrator.icon}</span>
              {story.genre}
            </span>
            {story.is_completed && (
              <span className="text-xs text-amber-400">✨ Complete</span>
            )}
          </div>

          {/* Title & Description */}
          <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
            {story.title}
          </h3>
          {story.description && (
            <p className="text-gray-400 text-sm mb-4 line-clamp-2 flex-1">
              {story.description}
            </p>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-auto pt-4 border-t border-story-border">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <Clock className="w-3.5 h-3.5" />
                {createdAt}
              </div>
              {onDelete && (
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    onDelete(story.id)
                  }}
                  className="p-1 rounded hover:bg-red-500/20 text-gray-500 hover:text-red-400 transition-colors"
                  title="Delete story"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            <motion.div 
              className="flex items-center gap-1 text-story-accent text-sm font-medium"
              whileHover={{ x: 4 }}
            >
              {story.is_completed ? 'Read' : 'Continue'}
              <ChevronRight className="w-4 h-4" />
            </motion.div>
          </div>
        </div>
      </Card>
    </Link>
  )
}

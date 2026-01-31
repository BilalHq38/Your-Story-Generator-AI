import { motion } from 'framer-motion'
import { STORY_GENRES } from '@/types'

interface GenreSelectorProps {
  value: string
  onChange: (genre: string) => void
}

export default function GenreSelector({ value, onChange }: GenreSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-300">
        Select Genre
      </label>
      <div className="flex flex-wrap gap-2">
        {STORY_GENRES.map((genre) => {
          const isSelected = value === genre
          
          return (
            <motion.button
              key={genre}
              type="button"
              onClick={() => onChange(genre)}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                border
                ${isSelected 
                  ? 'border-story-accent bg-story-accent/20 text-white' 
                  : 'border-story-border bg-story-muted/30 text-gray-400 hover:text-gray-200 hover:border-story-border/70'
                }
              `}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {genre}
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}

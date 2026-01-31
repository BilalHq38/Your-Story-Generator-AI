import { motion } from 'framer-motion'
import { StoryAtmosphere, STORY_ATMOSPHERES } from '@/types'
import { Cloud, Moon, Sparkles, Zap, Smile } from 'lucide-react'

interface AtmosphereSelectorProps {
  value: StoryAtmosphere
  onChange: (atmosphere: StoryAtmosphere) => void
}

const atmosphereIcons: Record<StoryAtmosphere, React.ReactNode> = {
  dark: <Moon className="w-5 h-5" />,
  magical: <Sparkles className="w-5 h-5" />,
  peaceful: <Cloud className="w-5 h-5" />,
  tense: <Zap className="w-5 h-5" />,
  whimsical: <Smile className="w-5 h-5" />,
}

export default function AtmosphereSelector({ value, onChange }: AtmosphereSelectorProps) {
  const atmospheres = Object.entries(STORY_ATMOSPHERES) as [StoryAtmosphere, typeof STORY_ATMOSPHERES[StoryAtmosphere]][]

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-300">
        Set the Atmosphere
      </label>
      <div className="flex flex-wrap gap-2">
        {atmospheres.map(([key, atmosphere]) => {
          const isSelected = value === key
          
          return (
            <motion.button
              key={key}
              type="button"
              onClick={() => onChange(key)}
              className={`
                relative px-4 py-2 rounded-lg flex items-center gap-2 transition-all
                border
                ${isSelected 
                  ? 'border-story-accent bg-story-accent/20 text-white' 
                  : 'border-story-border bg-story-muted/30 text-gray-400 hover:text-gray-200 hover:border-story-border/70'
                }
              `}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {atmosphereIcons[key]}
              <span className="text-sm font-medium">{atmosphere.name}</span>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}

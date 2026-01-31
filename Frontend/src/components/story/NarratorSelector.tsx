import { motion } from 'framer-motion'
import { NarratorPersona, NARRATOR_PERSONAS } from '@/types'

interface NarratorSelectorProps {
  value: NarratorPersona
  onChange: (persona: NarratorPersona) => void
}

export default function NarratorSelector({ value, onChange }: NarratorSelectorProps) {
  const personas = Object.entries(NARRATOR_PERSONAS) as [NarratorPersona, typeof NARRATOR_PERSONAS[NarratorPersona]][]

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-300">
        Choose Your Narrator
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {personas.map(([key, persona]) => {
          const isSelected = value === key
          
          return (
            <motion.button
              key={key}
              type="button"
              onClick={() => onChange(key)}
              className={`
                relative p-4 rounded-xl text-left transition-all
                border-2 
                ${isSelected 
                  ? `border-${persona.color.replace('narrator-', 'narrator-')}/70 bg-${persona.color.replace('narrator-', 'narrator-')}/10` 
                  : 'border-story-border bg-story-muted/30 hover:border-story-border/70'
                }
              `}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Selection indicator */}
              {isSelected && (
                <motion.div
                  layoutId="narrator-selection"
                  className="absolute inset-0 rounded-xl bg-gradient-to-br from-story-accent/10 to-transparent"
                  initial={false}
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              
              <div className="relative z-10 flex items-start gap-3">
                <span className="text-2xl">{persona.icon}</span>
                <div>
                  <h4 className={`font-medium ${isSelected ? 'text-white' : 'text-gray-200'}`}>
                    {persona.name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {persona.description}
                  </p>
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}

import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { StoryChoice } from '@/types'

interface ChoiceButtonsProps {
  choices: StoryChoice[]
  onChoose: (choice: StoryChoice) => void
  disabled?: boolean
}

export default function ChoiceButtons({ choices, onChoose, disabled }: ChoiceButtonsProps) {
  if (!choices || choices.length === 0) return null

  return (
    <motion.div
      className="space-y-3"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
    >
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
        What will you do?
      </h3>
      <AnimatePresence>
        <div className="space-y-3">
          {choices.map((choice, index) => (
            <motion.button
              key={choice.id}
              onClick={() => onChoose(choice)}
              disabled={disabled}
              className={`
                choice-btn w-full text-left group
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              whileHover={disabled ? {} : { x: 8 }}
            >
              <div className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-story-accent/20 text-story-accent flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </span>
                <div className="flex-1">
                  <p className="text-gray-200 font-medium group-hover:text-white transition-colors">
                    {choice.text}
                  </p>
                  {choice.consequence_hint && (
                    <p className="text-sm text-gray-500 mt-1 italic">
                      {choice.consequence_hint}
                    </p>
                  )}
                </div>
                <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-story-accent transition-colors flex-shrink-0 mt-1" />
              </div>
            </motion.button>
          ))}
        </div>
      </AnimatePresence>
    </motion.div>
  )
}

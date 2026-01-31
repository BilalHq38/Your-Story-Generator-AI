import { motion } from 'framer-motion'
import { Sparkles, Wand2 } from 'lucide-react'

interface GeneratingOverlayProps {
  message: string
}

export default function GeneratingOverlay({ message }: GeneratingOverlayProps) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-story-darker/90 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="text-center space-y-8">
        {/* Animated icons */}
        <div className="relative w-32 h-32 mx-auto">
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          >
            <Sparkles className="w-6 h-6 text-story-accent absolute top-0" />
            <Sparkles className="w-4 h-4 text-story-accent-light absolute bottom-0 right-0" />
            <Sparkles className="w-5 h-5 text-purple-400 absolute bottom-0 left-0" />
          </motion.div>
          
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="p-6 rounded-full bg-story-accent/20 border border-story-accent/30">
              <Wand2 className="w-12 h-12 text-story-accent" />
            </div>
          </motion.div>
        </div>

        {/* Message */}
        <div className="space-y-2">
          <motion.h3 
            className="text-xl font-medium text-white"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {message}
          </motion.h3>
          <p className="text-gray-400 text-sm">
            The AI is crafting your unique story...
          </p>
        </div>

        {/* Loading dots */}
        <div className="flex items-center justify-center gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 rounded-full bg-story-accent"
              animate={{ y: [0, -8, 0] }}
              transition={{ 
                duration: 0.6, 
                repeat: Infinity, 
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

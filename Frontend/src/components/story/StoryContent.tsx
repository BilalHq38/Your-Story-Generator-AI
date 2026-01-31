import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { NARRATOR_PERSONAS, NarratorPersona, STORY_ATMOSPHERES, StoryAtmosphere, StoryLanguage } from '@/types'
import AudioPlayer from './AudioPlayer.tsx'

interface StoryContentProps {
  content: string
  narratorPersona: NarratorPersona
  atmosphere: StoryAtmosphere
  language?: StoryLanguage
  isEnding?: boolean
  animate?: boolean
  showAudioPlayer?: boolean
  audioUrl?: string  // Pre-generated audio URL from backend
}

export default function StoryContent({ 
  content, 
  narratorPersona, 
  atmosphere,
  language = 'english',
  isEnding = false,
  animate = true,
  showAudioPlayer = true,
  audioUrl
}: StoryContentProps) {
  const [displayedContent, setDisplayedContent] = useState('')
  const [isComplete, setIsComplete] = useState(!animate)
  
  const narrator = NARRATOR_PERSONAS[narratorPersona]
  const atmosphereStyle = STORY_ATMOSPHERES[atmosphere]

  // Typewriter effect
  useEffect(() => {
    if (!animate) {
      setDisplayedContent(content)
      setIsComplete(true)
      return
    }

    setDisplayedContent('')
    setIsComplete(false)
    
    let index = 0
    const speed = 15 // ms per character
    
    const timer = setInterval(() => {
      if (index < content.length) {
        setDisplayedContent(content.slice(0, index + 1))
        index++
      } else {
        setIsComplete(true)
        clearInterval(timer)
      }
    }, speed)

    return () => clearInterval(timer)
  }, [content, animate])

  // Parse content for special formatting
  const formatContent = (text: string) => {
    // Split into paragraphs
    return text.split('\n\n').map((paragraph, i) => (
      <p key={i} className="mb-4 last:mb-0">
        {paragraph}
      </p>
    ))
  }

  return (
    <motion.div
      className={`relative rounded-2xl p-6 md:p-8 ${atmosphereStyle.className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Narrator badge */}
      <div className="flex items-center gap-2 mb-6">
        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${narrator.color}`}>
          <span>{narrator.icon}</span>
          {narrator.name}
        </span>
        {isEnding && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-400 border border-amber-500/30">
            ✨ The End
          </span>
        )}
      </div>

      {/* Story text */}
      <div className="story-text">
        {formatContent(displayedContent)}
        {!isComplete && (
          <span className="inline-block w-0.5 h-5 bg-story-accent animate-pulse ml-1" />
        )}
      </div>

      {/* Audio Player - Show immediately if audio is preloaded, otherwise show when content is typed */}
      {showAudioPlayer && (isComplete || audioUrl) && content && (
        <div className="mt-6 pt-4 border-t border-story-border/30">
          <AudioPlayer 
            text={content} 
            narratorPersona={narratorPersona} 
            language={language}
            preloadedAudioUrl={audioUrl}
          />
        </div>
      )}

      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-radial from-story-accent/5 to-transparent rounded-full blur-2xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-radial from-story-accent/5 to-transparent rounded-full blur-2xl pointer-events-none" />
    </motion.div>
  )
}

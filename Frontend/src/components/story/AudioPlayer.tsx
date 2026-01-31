import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  User, 
  Loader2,
  Settings,
  X,
  RefreshCw,
  Sparkles
} from 'lucide-react'
import { VoiceGender, NarratorPersona, NARRATOR_PERSONAS, StoryLanguage } from '@/types'
import { api } from '@/api/client'

interface AudioPlayerProps {
  text: string
  narratorPersona?: NarratorPersona
  language?: StoryLanguage
  autoPlay?: boolean
  onPlayStateChange?: (isPlaying: boolean) => void
  className?: string
  preloadedAudioUrl?: string  // Pre-generated audio URL from backend
}

// Narrator voice descriptions for UI
const NARRATOR_VOICE_STYLES: Record<NarratorPersona, { description: string; icon: string }> = {
  mysterious: { 
    description: 'Slow, deliberate, with dark mystery', 
    icon: '🌙' 
  },
  epic: { 
    description: 'Grand, dramatic narration', 
    icon: '⚔️' 
  },
  horror: { 
    description: 'Slow, creeping whispers', 
    icon: '👁️' 
  },
  comedic: { 
    description: 'Upbeat, lively delivery', 
    icon: '🎭' 
  },
  romantic: { 
    description: 'Soft, emotional tones', 
    icon: '🌹' 
  },
}

export default function AudioPlayer({ 
  text, 
  narratorPersona,
  language = 'english',
  autoPlay = false,
  onPlayStateChange,
  className = '',
  preloadedAudioUrl
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(preloadedAudioUrl || null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [audioReady, setAudioReady] = useState(!!preloadedAudioUrl)
  
  // Voice settings
  const [gender, setGender] = useState<VoiceGender>('female')
  const [useNarratorVoice, setUseNarratorVoice] = useState(true)

  // Get current narrator info
  const narratorInfo = narratorPersona ? NARRATOR_PERSONAS[narratorPersona] : null
  const narratorVoiceStyle = narratorPersona ? NARRATOR_VOICE_STYLES[narratorPersona] : null

  // Use preloaded audio URL if available
  useEffect(() => {
    if (preloadedAudioUrl && preloadedAudioUrl !== audioUrl) {
      setAudioUrl(preloadedAudioUrl)
      setAudioReady(true)
      if (audioRef.current) {
        audioRef.current.src = preloadedAudioUrl
        audioRef.current.load()
      }
    }
  }, [preloadedAudioUrl])

  // Cleanup audio URL on unmount (only for blob URLs, not data URLs)
  useEffect(() => {
    return () => {
      if (audioUrl && audioUrl.startsWith('blob:')) {
        URL.revokeObjectURL(audioUrl)
      }
    }
  }, [audioUrl])

  // Reset audio when text changes
  useEffect(() => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl(null)
      setProgress(0)
      setIsPlaying(false)
    }
  }, [text])

  // Handle audio events
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => {
      setProgress((audio.currentTime / audio.duration) * 100 || 0)
    }

    const handleLoadedMetadata = () => {
      setDuration(audio.duration)
    }

    const handleEnded = () => {
      setIsPlaying(false)
      setProgress(0)
      onPlayStateChange?.(false)
    }

    const handleError = () => {
      setError('Failed to play audio')
      setIsPlaying(false)
      setIsLoading(false)
    }

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
    }
  }, [onPlayStateChange])

  const generateAudio = async () => {
    if (!text.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      // Build request with narrator persona if using narrator voice
      const requestData: Record<string, unknown> = {
        text,
        gender,
        language, // Include language for proper voice selection
      }

      // If using narrator voice, include the narrator persona
      if (useNarratorVoice && narratorPersona) {
        requestData.narrator = narratorPersona
      }

      const response = await api.post('/tts/synthesize', requestData, {
        responseType: 'blob',
      })

      // Revoke old URL if exists
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }

      // Create new blob URL
      const blob = new Blob([response.data], { type: 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      setAudioUrl(url)

      // Play automatically if requested
      if (audioRef.current) {
        audioRef.current.src = url
        audioRef.current.load()
        if (autoPlay) {
          await audioRef.current.play()
          setIsPlaying(true)
          onPlayStateChange?.(true)
        }
      }
    } catch (err) {
      console.error('TTS error:', err)
      setError('Failed to generate audio')
    } finally {
      setIsLoading(false)
    }
  }

  const togglePlay = async () => {
    const audio = audioRef.current
    if (!audio) return

    if (!audioUrl) {
      // Generate audio first
      await generateAudio()
      // After generation, auto-play
      if (audioRef.current && audioRef.current.src) {
        await audioRef.current.play()
        setIsPlaying(true)
        onPlayStateChange?.(true)
      }
      return
    }

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
      onPlayStateChange?.(false)
    } else {
      await audio.play()
      setIsPlaying(true)
      onPlayStateChange?.(true)
    }
  }

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    if (!audio || !duration) return

    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    audio.currentTime = percent * duration
  }

  const regenerateAudio = async () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl(null)
    }
    setProgress(0)
    setIsPlaying(false)
    await generateAudio()
    // Auto-play after regeneration
    if (audioRef.current && audioRef.current.src) {
      await audioRef.current.play()
      setIsPlaying(true)
      onPlayStateChange?.(true)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className={`relative ${className}`}>
      <audio ref={audioRef} preload="none" />
      
      {/* Narrator voice indicator */}
      {narratorInfo && useNarratorVoice && (
        <div className="flex items-center gap-2 mb-2 text-xs text-story-muted">
          <Sparkles className="w-3 h-3" />
          <span>
            Voice: <span className="text-story-accent">{narratorInfo.name}</span>
            {narratorVoiceStyle && (
              <span className="ml-1 opacity-70">• {narratorVoiceStyle.description}</span>
            )}
          </span>
        </div>
      )}
      
      {/* Main player controls */}
      <div className="flex items-center gap-3 p-3 bg-story-card/50 rounded-xl border border-story-border/50 backdrop-blur-sm">
        {/* Play/Pause button */}
        <button
          onClick={togglePlay}
          disabled={isLoading || !text}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-story-accent hover:bg-story-accent/80 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5 ml-0.5" />
          )}
        </button>

        {/* Progress bar */}
        <div 
          className="flex-1 h-2 bg-story-border/50 rounded-full cursor-pointer overflow-hidden"
          onClick={handleSeek}
        >
          <motion.div
            className="h-full bg-story-accent rounded-full"
            style={{ width: `${progress}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>

        {/* Time display */}
        {duration > 0 && (
          <span className="text-xs text-story-muted min-w-[45px]">
            {formatTime((progress / 100) * duration)}
          </span>
        )}

        {/* Mute button */}
        <button
          onClick={toggleMute}
          className="p-2 text-story-muted hover:text-story-text transition-colors"
        >
          {isMuted ? (
            <VolumeX className="w-4 h-4" />
          ) : (
            <Volume2 className="w-4 h-4" />
          )}
        </button>

        {/* Settings button */}
        <button
          onClick={() => setShowSettings(!showSettings)}
          className={`p-2 transition-colors ${showSettings ? 'text-story-accent' : 'text-story-muted hover:text-story-text'}`}
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* Regenerate button */}
        {audioUrl && (
          <button
            onClick={regenerateAudio}
            disabled={isLoading}
            className="p-2 text-story-muted hover:text-story-text transition-colors disabled:opacity-50"
            title="Regenerate with new settings"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="mt-2 text-sm text-red-400">{error}</p>
      )}

      {/* Settings panel */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-full left-0 right-0 mb-2 p-4 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl z-50"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-white">Voice Settings</h4>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Narrator voice toggle */}
            {narratorPersona && (
              <div className="mb-4 p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useNarratorVoice}
                    onChange={(e) => setUseNarratorVoice(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-600 text-purple-500 focus:ring-purple-500 bg-gray-800"
                  />
                  <div>
                    <div className="text-sm font-medium text-white flex items-center gap-2">
                      <span>{narratorVoiceStyle?.icon}</span>
                      Use {narratorInfo?.name} Voice
                    </div>
                    <div className="text-xs text-gray-400">
                      {narratorVoiceStyle?.description}
                    </div>
                  </div>
                </label>
              </div>
            )}

            {/* Gender selection */}
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-2">Voice Gender</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setGender('male')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg border transition-colors ${
                    gender === 'male'
                      ? 'bg-purple-500/20 border-purple-500 text-purple-400'
                      : 'border-gray-600 text-gray-300 hover:border-purple-500/50 hover:text-white'
                  }`}
                >
                  <User className="w-4 h-4" />
                  Male
                </button>
                <button
                  onClick={() => setGender('female')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg border transition-colors ${
                    gender === 'female'
                      ? 'bg-purple-500/20 border-purple-500 text-purple-400'
                      : 'border-gray-600 text-gray-300 hover:border-purple-500/50 hover:text-white'
                  }`}
                >
                  <User className="w-4 h-4" />
                  Female
                </button>
              </div>
            </div>

            {/* Narrator voice info */}
            {useNarratorVoice && narratorPersona && (
              <div className="p-3 rounded-lg bg-gray-800 border border-gray-700">
                <p className="text-xs text-gray-300">
                  Voice settings are automatically optimized for the <strong className="text-white">{narratorInfo?.name}</strong> narrator style.
                  The voice will have appropriate pacing and tone to match the storytelling mood.
                </p>
              </div>
            )}

            {/* Apply note */}
            {audioUrl && (
              <p className="mt-3 text-xs text-gray-400 text-center">
                Click regenerate to apply new voice settings
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

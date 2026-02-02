// Story Types
export interface Story {
  id: string
  title: string
  description: string | null
  genre: string
  narrator_persona: NarratorPersona
  atmosphere: StoryAtmosphere
  language: StoryLanguage
  root_node_id: string | null
  current_node_id: string | null  // Track where user left off
  is_completed: boolean
  created_at: string
  updated_at: string
}

export interface StoryNode {
  id: string
  story_id: string
  parent_id: string | null
  content: string
  choice_text?: string // The choice text that led to this node
  choices: StoryChoice[]
  is_ending: boolean
  metadata: NodeMetadata
  node_metadata?: {
    audio_url?: string  // Pre-generated audio URL
    [key: string]: unknown
  }
  created_at: string
}

export interface StoryChoice {
  id: string
  text: string
  consequence_hint?: string
}

export interface NodeMetadata {
  mood?: string
  tension_level?: number
  word_count?: number
  generation_time?: number
}

// Narrator personas for unique storytelling styles
export type NarratorPersona = 
  | 'mysterious'   // Dark, enigmatic narrator
  | 'epic'         // Grand, heroic narrator
  | 'horror'       // Creepy, unsettling narrator
  | 'comedic'      // Witty, humorous narrator
  | 'romantic'     // Passionate, emotional narrator

export const NARRATOR_PERSONAS: Record<NarratorPersona, {
  name: string
  description: string
  icon: string
  color: string
}> = {
  mysterious: {
    name: 'The Enigma',
    description: 'Speaks in riddles and shadows, revealing secrets slowly',
    icon: '🌙',
    color: 'narrator-mysterious',
  },
  epic: {
    name: 'The Chronicler',
    description: 'Grand tales of heroes and legends, with dramatic flair',
    icon: '⚔️',
    color: 'narrator-epic',
  },
  horror: {
    name: 'The Whisperer',
    description: 'Unsettling tales that creep under your skin',
    icon: '👁️',
    color: 'narrator-horror',
  },
  comedic: {
    name: 'The Jester',
    description: 'Witty observations and unexpected humor',
    icon: '🎭',
    color: 'narrator-comedic',
  },
  romantic: {
    name: 'The Poet',
    description: 'Passionate prose that stirs the heart',
    icon: '🌹',
    color: 'narrator-romantic',
  },
}

// Story atmosphere/mood settings
export type StoryAtmosphere = 
  | 'dark'
  | 'magical'
  | 'peaceful'
  | 'tense'
  | 'whimsical'

export const STORY_ATMOSPHERES: Record<StoryAtmosphere, {
  name: string
  description: string
  className: string
}> = {
  dark: {
    name: 'Dark & Foreboding',
    description: 'Shadows lurk in every corner',
    className: 'atmosphere-dark',
  },
  magical: {
    name: 'Mystical & Enchanting',
    description: 'Wonder and magic fill the air',
    className: 'atmosphere-magical',
  },
  peaceful: {
    name: 'Calm & Serene',
    description: 'A gentle journey awaits',
    className: 'atmosphere-peaceful',
  },
  tense: {
    name: 'Suspenseful',
    description: 'Every moment matters',
    className: 'atmosphere-dark',
  },
  whimsical: {
    name: 'Light & Playful',
    description: 'Adventure with a smile',
    className: 'atmosphere-magical',
  },
}

// Language options
export type StoryLanguage = 'english' | 'urdu'

export const STORY_LANGUAGES: Record<StoryLanguage, {
  name: string
  nativeName: string
  icon: string
  direction: 'ltr' | 'rtl'
  description: string
}> = {
  english: {
    name: 'English',
    nativeName: 'English',
    icon: '🇬🇧',
    direction: 'ltr',
    description: 'Stories in English',
  },
  urdu: {
    name: 'Urdu',
    nativeName: 'اردو',
    icon: '🇵🇰',
    direction: 'rtl',
    description: 'اردو میں کہانیاں',
  },
}

// Genre options
export const STORY_GENRES = [
  'Fantasy',
  'Science Fiction',
  'Horror',
  'Mystery',
  'Romance',
  'Adventure',
  'Thriller',
  'Historical',
  'Comedy',
  'Drama',
] as const

export type StoryGenre = typeof STORY_GENRES[number]

// Job/Task Types
export interface Job {
  id: string
  story_id: string
  node_id: string | null
  job_type: JobType
  status: JobStatus
  result: JobResult | null
  error_message: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export type JobType = 'generate_opening' | 'generate_continuation' | 'generate_ending'
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface JobResult {
  content: string
  choices?: StoryChoice[]
  is_ending?: boolean
}

// API Request/Response Types
export interface CreateStoryRequest {
  title: string
  description?: string
  genre: string
  narrator_persona: NarratorPersona
  atmosphere: StoryAtmosphere
  language?: StoryLanguage
  initial_prompt?: string
}

export interface ContinueStoryRequest {
  choice_id: string
  choice_text: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Store Types
export interface StoryState {
  currentStory: Story | null
  currentNode: StoryNode | null
  storyPath: StoryNode[]
  isLoading: boolean
  isGenerating: boolean
  error: string | null
}

// TTS (Text-to-Speech) Types
export type VoiceGender = 'male' | 'female'

export interface VoiceInfo {
  id: string
  name: string
  locale: string
  style: string
  gender: VoiceGender
}

export interface TTSVoicesResponse {
  male_voices: VoiceInfo[]
  female_voices: VoiceInfo[]
  default_male: string
  default_female: string
}

export interface TTSRequest {
  text: string
  voice?: string
  gender: VoiceGender
  rate?: string
  pitch?: string
}

export interface TTSSettings {
  enabled: boolean
  gender: VoiceGender
  voice: string | null
  rate: string
  pitch: string
  autoPlay: boolean
}

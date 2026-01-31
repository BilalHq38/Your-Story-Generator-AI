import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Wand2, ArrowLeft, Sparkles } from 'lucide-react'
import { Button, Input, TextArea, Card } from '@/components/ui'
import { 
  NarratorSelector, 
  AtmosphereSelector, 
  GenreSelector,
  LanguageSelector,
  GeneratingOverlay 
} from '@/components/story'
import { storyApi, jobApi } from '@/api'
import type { NarratorPersona, StoryAtmosphere, StoryLanguage, CreateStoryRequest } from '@/types'

export default function CreateStoryPage() {
  const navigate = useNavigate()
  
  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [language, setLanguage] = useState<StoryLanguage>('english')
  const [genre, setGenre] = useState('Fantasy')
  const [narratorPersona, setNarratorPersona] = useState<NarratorPersona>('mysterious')
  const [atmosphere, setAtmosphere] = useState<StoryAtmosphere>('magical')
  const [initialPrompt, setInitialPrompt] = useState('')
  
  // Creation state
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationMessage, setGenerationMessage] = useState('')

  // Create story mutation
  const createStoryMutation = useMutation({
    mutationFn: async (data: CreateStoryRequest) => {
      // Step 1: Create the story
      setGenerationMessage('Creating your story...')
      const story = await storyApi.createStory(data)
      
      // Step 2: Generate the opening
      setGenerationMessage('AI is crafting the opening...')
      const { job_id } = await storyApi.generateOpening(story.id)
      
      // Step 3: Poll for completion
      setGenerationMessage('Weaving the narrative...')
      await jobApi.pollJob(job_id, (job) => {
        if (job.status === 'processing') {
          setGenerationMessage('The story takes shape...')
        }
      })
      
      return story
    },
    onSuccess: (story) => {
      toast.success('Your adventure awaits!')
      navigate(`/story/${story.id}`)
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create story')
      setIsGenerating(false)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!title.trim()) {
      toast.error('Please enter a title for your story')
      return
    }
    
    setIsGenerating(true)
    createStoryMutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      genre,
      narrator_persona: narratorPersona,
      atmosphere,
      language,
      initial_prompt: initialPrompt.trim() || undefined,
    })
  }

  return (
    <>
      {isGenerating && <GeneratingOverlay message={generationMessage} />}
      
      <div className="min-h-screen py-8 md:py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
            
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-story-accent/20 text-story-accent">
                <Sparkles className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Create Your Story</h1>
                <p className="text-gray-400 mt-1">Configure your unique adventure</p>
              </div>
            </div>
          </motion.div>

          {/* Form */}
          <motion.form
            onSubmit={handleSubmit}
            className="space-y-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {/* Language Selection - First Step */}
            <Card>
              <LanguageSelector value={language} onChange={setLanguage} />
            </Card>

            {/* Basic Info */}
            <Card>
              <h2 className="text-lg font-semibold text-white mb-6">Story Details</h2>
              <div className="space-y-4">
                <Input
                  label="Title"
                  placeholder="Enter a captivating title..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
                <TextArea
                  label="Description (Optional)"
                  placeholder="A brief description of your story..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </div>
            </Card>

            {/* Genre Selection */}
            <Card>
              <GenreSelector value={genre} onChange={setGenre} />
            </Card>

            {/* Narrator Selection */}
            <Card>
              <NarratorSelector value={narratorPersona} onChange={setNarratorPersona} />
            </Card>

            {/* Atmosphere Selection */}
            <Card>
              <AtmosphereSelector value={atmosphere} onChange={setAtmosphere} />
            </Card>

            {/* Custom Prompt */}
            <Card>
              <h2 className="text-lg font-semibold text-white mb-4">Starting Point (Optional)</h2>
              <TextArea
                placeholder="Give the AI a specific starting scenario, character, or setting... Leave empty for a surprise!"
                value={initialPrompt}
                onChange={(e) => setInitialPrompt(e.target.value)}
                rows={4}
                helperText="Example: 'A young mage discovers a forbidden spell book in an ancient library...'"
              />
            </Card>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate(-1)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                leftIcon={<Wand2 className="w-5 h-5" />}
                disabled={!title.trim() || isGenerating}
                isLoading={isGenerating}
              >
                Begin Adventure
              </Button>
            </div>
          </motion.form>
        </div>
      </div>
    </>
  )
}

import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, GitBranch, RotateCcw, Flag, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import { Button, LoadingSpinner, Card } from '@/components/ui'
import { 
  StoryContent, 
  ChoiceButtons, 
  GeneratingOverlay 
} from '@/components/story'
import { useStoryStore } from '@/stores'
import type { StoryChoice } from '@/types'

export default function StoryPage() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  const [showFullStory, setShowFullStory] = useState(false)
  
  const {
    currentStory,
    currentNode,
    storyPath,
    isLoading,
    isGenerating,
    generationProgress,
    loadStory,
    continueStory,
    generateEnding,
    reset,
  } = useStoryStore()

  // Load story on mount
  useEffect(() => {
    if (storyId) {
      loadStory(storyId)
    }
    
    return () => {
      reset()
    }
  }, [storyId, loadStory, reset])

  const handleChoose = async (choice: StoryChoice) => {
    if (!storyId || !currentNode) return
    await continueStory(storyId, currentNode.id, choice.id, choice.text)
  }

  const handleEndStory = async () => {
    if (!storyId || !currentNode) return
    await generateEnding(storyId, currentNode.id)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading your story..." />
      </div>
    )
  }

  if (!currentStory) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="text-center py-12 px-8">
          <h2 className="text-xl font-semibold text-white mb-4">Story Not Found</h2>
          <p className="text-gray-400 mb-6">This story doesn't exist or has been deleted.</p>
          <Button onClick={() => navigate('/')}>Go Home</Button>
        </Card>
      </div>
    )
  }

  return (
    <>
      <AnimatePresence>
        {isGenerating && <GeneratingOverlay message={generationProgress} />}
      </AnimatePresence>

      <div className="min-h-screen py-8 md:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => navigate('/library')}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Library
              </button>
              
              <div className="flex items-center gap-2">
                <Link to={`/story/${storyId}/tree`}>
                  <Button variant="ghost" size="sm" leftIcon={<GitBranch className="w-4 h-4" />}>
                    View Tree
                  </Button>
                </Link>
              </div>
            </div>
            
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              {currentStory.title}
            </h1>
            
            {/* Story path breadcrumb */}
            {storyPath.length > 1 && (
              <div className="flex items-center gap-2 mt-3 text-sm text-gray-500 overflow-x-auto">
                <span>Chapter</span>
                {storyPath.map((node, i) => (
                  <span key={node.id} className="flex items-center gap-2">
                    {i > 0 && <span>→</span>}
                    <span className={i === storyPath.length - 1 ? 'text-story-accent' : ''}>
                      {i + 1}
                    </span>
                  </span>
                ))}
              </div>
            )}
          </motion.div>

          {/* Story Content */}
          {currentNode ? (
            <motion.div
              className="space-y-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <StoryContent
                content={currentNode.content}
                narratorPersona={currentStory.narrator_persona}
                atmosphere={currentStory.atmosphere}
                language={currentStory.language || 'english'}
                isEnding={currentNode.is_ending}
                animate={true}
                audioUrl={currentNode.node_metadata?.audio_url}
              />

              {/* Choices or Ending Actions */}
              {!currentNode.is_ending && currentNode.choices && currentNode.choices.length > 0 && (
                <ChoiceButtons
                  choices={currentNode.choices}
                  onChoose={handleChoose}
                  disabled={isGenerating}
                />
              )}

              {/* Additional Actions */}
              {!currentNode.is_ending && (
                <div className="flex items-center justify-center gap-4 pt-4 border-t border-story-border">
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Flag className="w-4 h-4" />}
                    onClick={handleEndStory}
                    disabled={isGenerating}
                  >
                    End Story Here
                  </Button>
                </div>
              )}

              {/* Ending Actions */}
              {currentNode.is_ending && (
                <motion.div
                  className="flex flex-col gap-6 pt-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  {/* Complete Story Toggle */}
                  <div className="border border-story-border rounded-xl overflow-hidden">
                    <button
                      onClick={() => setShowFullStory(!showFullStory)}
                      className="w-full flex items-center justify-between p-4 bg-story-muted/30 hover:bg-story-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <BookOpen className="w-5 h-5 text-story-accent" />
                        <span className="font-medium text-white">
                          View Complete Story ({storyPath.length} chapters)
                        </span>
                      </div>
                      {showFullStory ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                    
                    <AnimatePresence>
                      {showFullStory && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.3 }}
                          className="overflow-hidden"
                        >
                          <div className="p-4 space-y-6 bg-story-darker/50">
                            {storyPath.map((node, index) => (
                              <motion.div
                                key={node.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                              >
                                <div className="flex items-center gap-2 mb-3">
                                  <span className="px-2 py-1 bg-story-accent/20 text-story-accent text-xs font-medium rounded">
                                    Chapter {index + 1}
                                  </span>
                                  {node.is_ending && (
                                    <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs font-medium rounded">
                                      ✨ The End
                                    </span>
                                  )}
                                </div>
                                <div 
                                  className={`prose prose-invert max-w-none ${
                                    currentStory?.language === 'urdu' 
                                      ? 'font-urdu text-right' 
                                      : 'font-story'
                                  }`}
                                  style={{ 
                                    fontFamily: currentStory?.language === 'urdu' 
                                      ? '"Noto Nastaliq Urdu", serif' 
                                      : undefined,
                                    direction: currentStory?.language === 'urdu' ? 'rtl' : 'ltr'
                                  }}
                                >
                                  {node.content.split('\n\n').map((paragraph, i) => (
                                    <p key={i} className="text-gray-300 mb-3 last:mb-0">
                                      {paragraph}
                                    </p>
                                  ))}
                                </div>
                                {index < storyPath.length - 1 && (
                                  <div className="mt-4 pt-4 border-t border-story-border/30">
                                    <p className="text-sm text-gray-500 italic">
                                      ➤ You chose: {storyPath[index + 1].choice_text || 'Continue'}
                                    </p>
                                  </div>
                                )}
                              </motion.div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* End actions */}
                  <div className="text-center">
                    <p className="text-gray-400 mb-4">
                      Your adventure has come to an end. What would you like to do?
                    </p>
                    <div className="flex items-center justify-center gap-4">
                      <Link to={`/story/${storyId}/tree`}>
                        <Button
                          variant="secondary"
                          leftIcon={<GitBranch className="w-4 h-4" />}
                        >
                          View Story Tree
                        </Button>
                      </Link>
                      <Button
                        variant="secondary"
                        leftIcon={<RotateCcw className="w-4 h-4" />}
                        onClick={() => storyId && loadStory(storyId)}
                      >
                        Start Over
                      </Button>
                      <Link to="/create">
                        <Button>New Story</Button>
                      </Link>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <Card className="text-center py-12">
              <p className="text-gray-400 mb-6">
                This story hasn't been started yet.
              </p>
              <Button onClick={() => navigate('/create')}>
                Create New Story
              </Button>
            </Card>
          )}
        </div>
      </div>
    </>
  )
}

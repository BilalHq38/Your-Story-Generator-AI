import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, GitBranch, BookOpen } from 'lucide-react'
import { Button, LoadingSpinner, Card } from '@/components/ui'
import { AudioPlayer } from '@/components/story'
import { useStoryStore } from '@/stores'
import { storyApi } from '@/api'

export default function StoryReadPage() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  const [viewMode, setViewMode] = useState<'paragraphs' | 'chapters'>('paragraphs')
  
  const {
    currentStory,
    allNodes,
    isLoading,
    loadStory,
    reset,
  } = useStoryStore()

  // Fetch branches from API
  const { data: branchesData, isLoading: isBranchesLoading } = useQuery({
    queryKey: ['story-branches', storyId],
    queryFn: () => storyApi.getStoryBranches(storyId!),
    enabled: !!storyId,
  })

  useEffect(() => {
    if (storyId) {
      loadStory(storyId)
    }
    return () => reset()
  }, [storyId, loadStory, reset])

  // Build the story path from root to an ending (fallback if branches not loaded)
  const getStoryPath = () => {
    if (!allNodes.length) return []
    
    // Find root node
    const rootNode = allNodes.find(n => !n.parent_id)
    if (!rootNode) return []
    
    // Build path following first/main branch to an ending
    const path: typeof allNodes = [rootNode]
    let current = rootNode
    
    while (!current.is_ending) {
      const children = allNodes.filter(n => n.parent_id === current.id)
      if (children.length === 0) break
      // Follow the first child (main path)
      current = children[0]
      path.push(current)
    }
    
    return path
  }

  // Get all branches for the branches view
  const getAllBranches = () => {
    if (!allNodes.length) return []
    
    interface Branch {
      id: string
      path: typeof allNodes
      isEnding: boolean
    }
    
    const branches: Branch[] = []
    
    const collectBranches = (node: typeof allNodes[0], currentPath: typeof allNodes) => {
      const newPath = [...currentPath, node]
      
      if (node.is_ending) {
        branches.push({ id: node.id, path: newPath, isEnding: true })
        return
      }
      
      const children = allNodes.filter(n => n.parent_id === node.id)
      
      if (children.length === 0) {
        branches.push({ id: node.id, path: newPath, isEnding: false })
        return
      }
      
      children.forEach(child => collectBranches(child, newPath))
    }
    
    const rootNode = allNodes.find(n => !n.parent_id)
    if (rootNode) {
      collectBranches(rootNode, [])
    }
    
    return branches
  }

  const storyPath = getStoryPath()
  const allBranches = getAllBranches()

  // Use API complete text if available, otherwise build from storyPath
  const completeStoryText = branchesData?.complete_story_text || 
    storyPath.map(n => n.content).join('\n\n')

  if (isLoading || isBranchesLoading) {
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
          <Button onClick={() => navigate('/app')}>Go Home</Button>
        </Card>
      </div>
    )
  }

  const isRtl = currentStory.language === 'urdu'

  return (
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
              onClick={() => navigate('/app/library')}
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
              <Link to={`/story/${storyId}`}>
                <Button variant="ghost" size="sm" leftIcon={<BookOpen className="w-4 h-4" />}>
                  Interactive Mode
                </Button>
              </Link>
            </div>
          </div>
          
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
            {currentStory.title}
          </h1>
          <p className="text-gray-400">
            {currentStory.genre} • {currentStory.narrator_persona} narrator • {allNodes.length} chapters
          </p>
        </motion.div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 mb-8 p-1 bg-story-muted/30 rounded-lg inline-flex">
          <button
            onClick={() => setViewMode('paragraphs')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'paragraphs'
                ? 'bg-story-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-4 h-4 inline-block mr-2" />
            Full Story
          </button>
          <button
            onClick={() => setViewMode('chapters')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'chapters'
                ? 'bg-story-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <GitBranch className="w-4 h-4 inline-block mr-2" />
            All Branches ({allBranches.length})
          </button>
        </div>

        {/* Story Content */}
        {viewMode === 'paragraphs' ? (
          /* Full Story as Paragraphs */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-story-card/50 border border-story-border rounded-2xl p-8 md:p-12"
          >
            {/* Audio Player for Full Story */}
            <div className="mb-8">
              <AudioPlayer 
                text={completeStoryText}
                language={currentStory.language || 'english'}
                narratorPersona={currentStory.narrator_persona || 'mysterious'}
              />
            </div>

            <div 
              className={`prose prose-invert prose-lg max-w-none ${
                isRtl ? 'font-urdu text-right' : 'font-story'
              }`}
              style={{ 
                fontFamily: isRtl ? '"Noto Nastaliq Urdu", serif' : undefined,
                direction: isRtl ? 'rtl' : 'ltr'
              }}
            >
              {storyPath.map((node, index) => (
                <motion.div
                  key={node.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="mb-8"
                >
                  {node.content.split('\n\n').map((paragraph, i) => (
                    <p key={i} className="text-gray-200 leading-relaxed mb-4">
                      {paragraph}
                    </p>
                  ))}
                  
                  {node.is_ending && (
                    <div className="text-center mt-12 pt-8 border-t border-story-border/50">
                      <span className="text-amber-400 text-xl">✨ The End ✨</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        ) : (
          /* All Branches View */
          <div className="space-y-8">
            {allBranches.map((branch, branchIndex) => (
              <motion.div
                key={branch.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: branchIndex * 0.1 }}
                className="bg-story-card/50 border border-story-border rounded-2xl overflow-hidden"
              >
                <div className="p-4 bg-story-muted/30 border-b border-story-border flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-story-accent/20 text-story-accent text-sm font-medium rounded-full">
                      Branch {branchIndex + 1}
                    </span>
                    <span className="text-gray-400 text-sm">
                      {branch.path.length} chapters
                    </span>
                  </div>
                  {branch.isEnding && (
                    <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs font-medium rounded">
                      ✨ Complete Ending
                    </span>
                  )}
                </div>
                
                <div 
                  className={`p-6 md:p-8 ${isRtl ? 'font-urdu text-right' : 'font-story'}`}
                  style={{ 
                    fontFamily: isRtl ? '"Noto Nastaliq Urdu", serif' : undefined,
                    direction: isRtl ? 'rtl' : 'ltr'
                  }}
                >
                  {branch.path.map((node, nodeIndex) => (
                    <div key={node.id} className="mb-6 last:mb-0">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xs text-gray-500 font-medium">
                          Chapter {nodeIndex + 1}
                        </span>
                        {node.choice_text && (
                          <span className="text-xs text-story-accent/70 italic">
                            → "{node.choice_text}"
                          </span>
                        )}
                      </div>
                      
                      {node.content.split('\n\n').map((paragraph, i) => (
                        <p key={i} className="text-gray-300 mb-3 last:mb-0 leading-relaxed">
                          {paragraph}
                        </p>
                      ))}
                      
                      {nodeIndex < branch.path.length - 1 && (
                        <div className="mt-4 pt-4 border-t border-story-border/20" />
                      )}
                    </div>
                  ))}
                  
                  {branch.isEnding && (
                    <div className="text-center mt-8 pt-6 border-t border-story-border/50">
                      <span className="text-amber-400">✨ The End ✨</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Actions */}
        <motion.div 
          className="mt-12 flex items-center justify-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <Link to={`/app/story/${storyId}`}>
            <Button variant="secondary">
              Read Interactively
            </Button>
          </Link>
          <Link to="/app/create">
            <Button>
              Create New Story
            </Button>
          </Link>
        </motion.div>
      </div>
    </div>
  )
}

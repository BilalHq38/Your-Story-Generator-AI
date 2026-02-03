import { useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, BookOpen, Circle, CheckCircle2 } from 'lucide-react'
import { Button, LoadingSpinner, Card } from '@/components/ui'
import { useStoryStore } from '@/stores'

export default function StoryTreePage() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  
  const {
    currentStory,
    allNodes,
    currentNode,
    isLoading,
    loadStory,
    reset,
  } = useStoryStore()

  useEffect(() => {
    if (storyId) {
      loadStory(storyId)
    }
    return () => reset()
  }, [storyId, loadStory, reset])

  // Build tree structure
  const treeData = useMemo(() => {
    if (!allNodes.length) return null

    const rootNode = allNodes.find(n => !n.parent_id)
    
    if (!rootNode) return null

    interface TreeNode {
      node: typeof rootNode
      children: TreeNode[]
      depth: number
    }

    const buildTree = (node: typeof rootNode, depth: number = 0): TreeNode => {
      const children = allNodes
        .filter(n => n.parent_id === node.id)
        .map(child => buildTree(child, depth + 1))
      
      return { node, children, depth }
    }

    return buildTree(rootNode)
  }, [allNodes])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading story tree..." />
      </div>
    )
  }

  if (!currentStory) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="text-center py-12 px-8">
          <h2 className="text-xl font-semibold text-white mb-4">Story Not Found</h2>
          <Button onClick={() => navigate('/app')}>Go Home</Button>
        </Card>
      </div>
    )
  }

  // Recursive tree node renderer
  interface TreeNodeComponentProps {
    treeNode: {
      node: {
        id: string
        content: string
        is_ending: boolean
        choices?: Array<{ text: string }>
      }
      children: TreeNodeComponentProps['treeNode'][]
      depth: number
    }
  }

  const TreeNodeComponent = ({ treeNode }: TreeNodeComponentProps) => {
    const { node, children, depth } = treeNode
    const isCurrentNode = currentNode?.id === node.id
    const preview = node.content.slice(0, 100) + (node.content.length > 100 ? '...' : '')

    return (
      <div className="flex flex-col">
        <motion.div
          className={`
            relative p-4 rounded-xl border-2 transition-all cursor-pointer
            ${isCurrentNode 
              ? 'border-story-accent bg-story-accent/10' 
              : 'border-story-border bg-story-muted/30 hover:border-story-border/70'
            }
            ${node.is_ending ? 'border-amber-500/50' : ''}
          `}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: depth * 0.1 }}
          onClick={() => navigate(`/story/${storyId}`)}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-start gap-3">
            {node.is_ending ? (
              <CheckCircle2 className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            ) : (
              <Circle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${isCurrentNode ? 'text-story-accent' : 'text-gray-500'}`} />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-300 line-clamp-3">
                {preview}
              </p>
              {node.choices && node.choices.length > 0 && (
                <p className="text-xs text-gray-500 mt-2">
                  {node.choices.length} choice{node.choices.length > 1 ? 's' : ''} available
                </p>
              )}
            </div>
          </div>
          
          {node.is_ending && (
            <span className="absolute -top-2 -right-2 px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full border border-amber-500/30">
              Ending
            </span>
          )}
        </motion.div>

        {/* Children */}
        {children.length > 0 && (
          <div className="ml-8 mt-4 space-y-4 relative">
            {/* Connection line */}
            <div className="absolute left-0 top-0 bottom-0 w-px bg-story-border -translate-x-4" />
            
            {children.map((child) => (
              <div key={child.node.id} className="relative">
                {/* Horizontal connector */}
                <div className="absolute left-0 top-6 w-4 h-px bg-story-border -translate-x-4" />
                <TreeNodeComponent treeNode={child} />
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 md:py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate(`/app/story/${storyId}`)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Story
            </button>
          </div>
          
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
            Story Tree: {currentStory.title}
          </h1>
          <p className="text-gray-400">
            Visualize all paths and branches in your story
          </p>
        </motion.div>

        {/* Tree Visualization */}
        {treeData ? (
          <motion.div
            className="p-6 rounded-2xl bg-story-muted/20 border border-story-border"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <TreeNodeComponent treeNode={treeData} />
          </motion.div>
        ) : (
          <Card className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">No story content yet</p>
          </Card>
        )}

        {/* Legend */}
        <div className="mt-6 flex items-center gap-6 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Circle className="w-4 h-4 text-gray-500" />
            <span>Story Node</span>
          </div>
          <div className="flex items-center gap-2">
            <Circle className="w-4 h-4 text-story-accent" />
            <span>Current Position</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-amber-500" />
            <span>Ending</span>
          </div>
        </div>
      </div>
    </div>
  )
}

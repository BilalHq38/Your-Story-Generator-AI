import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { Story, StoryNode } from '@/types'
import { storyApi } from '@/api'
import toast from 'react-hot-toast'

interface StoryStore {
  // State
  currentStory: Story | null
  currentNode: StoryNode | null
  storyPath: StoryNode[]
  allNodes: StoryNode[]
  isLoading: boolean
  isGenerating: boolean
  generationProgress: string
  streamingContent: string  // NEW: content being streamed
  error: string | null

  // Actions
  setCurrentStory: (story: Story | null) => void
  setCurrentNode: (node: StoryNode | null) => void
  loadStory: (storyId: string) => Promise<void>
  loadNode: (storyId: string, nodeId: string) => Promise<void>
  generateOpening: (storyId: string) => Promise<void>
  continueStory: (storyId: string, nodeId: string, choiceId: string, choiceText: string) => Promise<void>
  generateEnding: (storyId: string, nodeId: string) => Promise<void>
  reset: () => void
}

const initialState = {
  currentStory: null,
  currentNode: null,
  storyPath: [],
  allNodes: [],
  isLoading: false,
  isGenerating: false,
  generationProgress: '',
  streamingContent: '',
  error: null,
}

export const useStoryStore = create<StoryStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setCurrentStory: (story) => set({ currentStory: story }),
      
      setCurrentNode: (node) => set({ currentNode: node }),

      loadStory: async (storyId) => {
        set({ isLoading: true, error: null })
        try {
          const [story, nodes] = await Promise.all([
            storyApi.getStory(storyId),
            storyApi.getStoryNodes(storyId),
          ])
          
          set({ 
            currentStory: story, 
            allNodes: nodes,
            isLoading: false,
          })

          // Resume from current_node_id if available, otherwise use root_node
          const resumeNodeId = story.current_node_id || story.root_node_id
          if (resumeNodeId) {
            const currentNode = nodes.find(n => n.id === resumeNodeId)
            if (currentNode) {
              // Get the path from root to current node
              try {
                const path = await storyApi.getStoryPath(storyId, String(resumeNodeId))
                set({ currentNode, storyPath: path })
              } catch {
                // If path fails, just set the current node
                set({ currentNode, storyPath: [currentNode] })
              }
            }
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load story',
            isLoading: false,
          })
        }
      },

      loadNode: async (storyId, nodeId) => {
        set({ isLoading: true, error: null })
        try {
          const [node, path] = await Promise.all([
            storyApi.getNode(storyId, nodeId),
            storyApi.getStoryPath(storyId, nodeId),
          ])
          
          set({ 
            currentNode: node, 
            storyPath: path,
            isLoading: false,
          })
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load node',
            isLoading: false,
          })
        }
      },

      generateOpening: async (storyId) => {
        set({ isGenerating: true, generationProgress: 'Starting story generation...', streamingContent: '', error: null })
        
        try {
          await storyApi.streamOpening(storyId, {
            onToken: (token) => {
              set((state) => ({ 
                streamingContent: state.streamingContent + token,
                generationProgress: 'Generating your story...',
              }))
            },
            onDone: async () => {
              // Reload the story to get the new node with proper structure
              await get().loadStory(storyId)
              set({ streamingContent: '', isGenerating: false, generationProgress: '' })
              toast.success('Your adventure begins!')
            },
            onError: (error) => {
              set({ error, isGenerating: false, generationProgress: '', streamingContent: '' })
              toast.error(error)
            },
          })
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to generate opening'
          set({ error: message, isGenerating: false, generationProgress: '', streamingContent: '' })
          toast.error(message)
        }
      },

      continueStory: async (storyId, nodeId, choiceId, choiceText) => {
        set({ isGenerating: true, generationProgress: 'Processing your choice...', streamingContent: '', error: null })
        
        try {
          await storyApi.streamContinuation(storyId, nodeId, {
            choice_id: choiceId,
            choice_text: choiceText,
          }, {
            onToken: (token) => {
              set((state) => ({ 
                streamingContent: state.streamingContent + token,
                generationProgress: 'The story unfolds...',
              }))
            },
            onDone: async (result) => {
              // Reload nodes and navigate to the new node
              const nodes = await storyApi.getStoryNodes(storyId)
              const newNode = nodes.find(n => n.id === String(result.node_id))
              
              if (newNode) {
                const path = await storyApi.getStoryPath(storyId, String(result.node_id))
                set({ 
                  allNodes: nodes,
                  currentNode: newNode, 
                  storyPath: path,
                  streamingContent: '',
                  isGenerating: false,
                  generationProgress: '',
                })
              } else {
                set({ streamingContent: '', isGenerating: false, generationProgress: '' })
              }
            },
            onError: (error) => {
              set({ error, isGenerating: false, generationProgress: '', streamingContent: '' })
              toast.error(error)
            },
          })
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to continue story'
          set({ error: message, isGenerating: false, generationProgress: '', streamingContent: '' })
          toast.error(message)
        }
      },

      generateEnding: async (storyId, nodeId) => {
        set({ isGenerating: true, generationProgress: 'Preparing the finale...', streamingContent: '', error: null })
        
        try {
          await storyApi.streamEnding(storyId, nodeId, {
            onToken: (token) => {
              set((state) => ({ 
                streamingContent: state.streamingContent + token,
                generationProgress: 'Writing the conclusion...',
              }))
            },
            onDone: async (result) => {
              // Reload nodes to get the new ending node
              const nodes = await storyApi.getStoryNodes(storyId)
              const endingNode = nodes.find(n => n.id === String(result.node_id))
              
              if (endingNode) {
                const path = await storyApi.getStoryPath(storyId, String(result.node_id))
                const story = await storyApi.getStory(storyId)
                set({ 
                  currentStory: story,
                  allNodes: nodes,
                  currentNode: endingNode, 
                  storyPath: path,
                  streamingContent: '',
                  isGenerating: false,
                  generationProgress: '',
                })
              } else {
                // Fallback to loadStory if ending node not found
                await get().loadStory(storyId)
                set({ streamingContent: '', isGenerating: false, generationProgress: '' })
              }
              toast.success('The story reaches its conclusion!')
            },
            onError: (error) => {
              set({ error, isGenerating: false, generationProgress: '', streamingContent: '' })
              toast.error(error)
            },
          })
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to generate ending'
          set({ error: message, isGenerating: false, generationProgress: '', streamingContent: '' })
          toast.error(message)
        }
      },

      reset: () => set(initialState),
    }),
    { name: 'story-store' }
  )
)

// Selector hooks for performance
export const useCurrentStory = () => useStoryStore((s) => s.currentStory)
export const useCurrentNode = () => useStoryStore((s) => s.currentNode)
export const useStoryPath = () => useStoryStore((s) => s.storyPath)
export const useIsGenerating = () => useStoryStore((s) => s.isGenerating)
export const useGenerationProgress = () => useStoryStore((s) => s.generationProgress)
export const useStreamingContent = () => useStoryStore((s) => s.streamingContent)

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { Story, StoryNode } from '@/types'
import { storyApi, jobApi } from '@/api'
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

          // If there's a root node, load it
          if (story.root_node_id) {
            const rootNode = nodes.find(n => n.id === story.root_node_id)
            if (rootNode) {
              set({ currentNode: rootNode, storyPath: [rootNode] })
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
        set({ isGenerating: true, generationProgress: 'Starting story generation...', error: null })
        try {
          const { job_id } = await storyApi.generateOpening(storyId)
          
          set({ generationProgress: 'AI is crafting your story...' })
          
          const job = await jobApi.pollJob(job_id, (j) => {
            if (j.status === 'processing') {
              set({ generationProgress: 'Weaving the narrative...' })
            }
          })
          
          if (job.result) {
            // Reload the story to get the new node
            await get().loadStory(storyId)
            toast.success('Your adventure begins!')
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to generate opening'
          set({ error: message })
          toast.error(message)
        } finally {
          set({ isGenerating: false, generationProgress: '' })
        }
      },

      continueStory: async (storyId, nodeId, choiceId, choiceText) => {
        set({ isGenerating: true, generationProgress: 'Processing your choice...', error: null })
        try {
          const { job_id } = await storyApi.continueStory(storyId, nodeId, {
            choice_id: choiceId,
            choice_text: choiceText,
          })
          
          set({ generationProgress: 'The story unfolds...' })
          
          const job = await jobApi.pollJob(job_id, (j) => {
            if (j.status === 'processing') {
              set({ generationProgress: 'Crafting the next chapter...' })
            }
          })
          
          if (job.result) {
            // Reload nodes and navigate to the new node
            const nodes = await storyApi.getStoryNodes(storyId)
            const newNode = nodes.find(n => n.parent_id === nodeId)
            
            if (newNode) {
              const path = await storyApi.getStoryPath(storyId, newNode.id)
              set({ 
                allNodes: nodes,
                currentNode: newNode, 
                storyPath: path,
              })
            }
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to continue story'
          set({ error: message })
          toast.error(message)
        } finally {
          set({ isGenerating: false, generationProgress: '' })
        }
      },

      generateEnding: async (storyId, nodeId) => {
        set({ isGenerating: true, generationProgress: 'Preparing the finale...', error: null })
        try {
          const { job_id } = await storyApi.generateEnding(storyId, nodeId)
          
          set({ generationProgress: 'Writing the conclusion...' })
          
          const job = await jobApi.pollJob(job_id, (j) => {
            if (j.status === 'processing') {
              set({ generationProgress: 'The end draws near...' })
            }
          })
          
          if (job.result) {
            // Reload nodes to get the new ending node
            const nodes = await storyApi.getStoryNodes(storyId)
            // Find the new ending node (child of current node with is_ending=true)
            const endingNode = nodes.find(n => n.parent_id === nodeId && n.is_ending)
            
            if (endingNode) {
              const path = await storyApi.getStoryPath(storyId, endingNode.id)
              const story = await storyApi.getStory(storyId)
              set({ 
                currentStory: story,
                allNodes: nodes,
                currentNode: endingNode, 
                storyPath: path,
              })
            } else {
              // Fallback to loadStory if ending node not found
              await get().loadStory(storyId)
            }
            toast.success('The story reaches its conclusion!')
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to generate ending'
          set({ error: message })
          toast.error(message)
        } finally {
          set({ isGenerating: false, generationProgress: '' })
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

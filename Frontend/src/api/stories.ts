import { api } from './client'
import type { 
  Story, 
  StoryNode, 
  CreateStoryRequest, 
  ContinueStoryRequest,
  PaginatedResponse 
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Helper to get auth token
function getAuthToken(): string | null {
  try {
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      const { state } = JSON.parse(authStorage)
      return state?.token || null
    }
  } catch {
    // Ignore parse errors
  }
  return null
}

// Streaming callback types
export interface StreamCallbacks {
  onToken: (token: string) => void
  onDone: (result: { node_id: number; content: string; choices: Array<{ id: string; text: string }>; is_ending: boolean }) => void
  onError: (error: string) => void
}

// Stream story generation using SSE
async function streamGeneration(
  url: string,
  callbacks: StreamCallbacks,
  body?: object
): Promise<void> {
  const token = getAuthToken()
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Stream failed' }))
    callbacks.onError(error.detail || 'Failed to start generation')
    return
  }
  
  const reader = response.body?.getReader()
  if (!reader) {
    callbacks.onError('Streaming not supported')
    return
  }
  
  const decoder = new TextDecoder()
  let buffer = ''
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      
      // Parse SSE messages
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'token') {
              callbacks.onToken(data.content)
            } else if (data.type === 'done') {
              callbacks.onDone(data)
            } else if (data.type === 'error') {
              callbacks.onError(data.message)
            }
          } catch {
            // Ignore parse errors for incomplete JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

// Story API endpoints
export const storyApi = {
  // Get all stories with pagination
  async getStories(page = 1, size = 10): Promise<PaginatedResponse<Story>> {
    const response = await api.get('/stories', { params: { page, size } })
    return response.data
  },

  // Get a single story by ID
  async getStory(storyId: string): Promise<Story> {
    const response = await api.get(`/stories/${storyId}`)
    return response.data
  },

  // Create a new story
  async createStory(data: CreateStoryRequest): Promise<Story> {
    const response = await api.post('/stories', data)
    return response.data
  },

  // Delete a story
  async deleteStory(storyId: string): Promise<void> {
    await api.delete(`/stories/${storyId}`)
  },

  // Get story nodes (the story tree)
  async getStoryNodes(storyId: string): Promise<StoryNode[]> {
    const response = await api.get(`/stories/${storyId}/nodes`)
    return response.data
  },

  // Get a specific node
  async getNode(storyId: string, nodeId: string): Promise<StoryNode> {
    const response = await api.get(`/stories/${storyId}/nodes/${nodeId}`)
    return response.data
  },

  // Get the story path from root to a specific node
  async getStoryPath(storyId: string, nodeId: string): Promise<StoryNode[]> {
    const response = await api.get(`/stories/${storyId}/nodes/${nodeId}/path`)
    return response.data
  },

  // Generate story opening (starts the story)
  async generateOpening(storyId: string): Promise<{ job_id: string }> {
    const response = await api.post(`/stories/${storyId}/generate/opening`)
    return response.data
  },

  // Continue the story with a choice
  async continueStory(
    storyId: string, 
    nodeId: string, 
    data: ContinueStoryRequest
  ): Promise<{ job_id: string }> {
    const response = await api.post(
      `/stories/${storyId}/nodes/${nodeId}/continue`,
      data
    )
    return response.data
  },

  // Generate an ending for the story
  async generateEnding(storyId: string, nodeId: string): Promise<{ job_id: string }> {
    const response = await api.post(`/stories/${storyId}/nodes/${nodeId}/ending`)
    return response.data
  },

  // Get story tree structure for visualization
  async getStoryTree(storyId: string): Promise<{
    nodes: StoryNode[]
    edges: Array<{ from: string; to: string }>
  }> {
    const response = await api.get(`/stories/${storyId}/tree`)
    return response.data
  },

  // Get story branches for reading
  async getStoryBranches(storyId: string): Promise<{
    story_id: number
    title: string
    complete_story_text: string | null
    branches: Array<{
      id: string
      nodes: Array<{
        id: number
        content: string
        choice_text: string | null
        is_ending: boolean
      }>
      is_complete: boolean
    }>
    total_branches: number
    has_complete_ending: boolean
  }> {
    const response = await api.get(`/stories/${storyId}/branches`)
    return response.data
  },

  // Save story branches
  async saveStoryBranches(
    storyId: string,
    data: {
      complete_story_text?: string
      branches: Array<{
        id: string
        nodes: Array<{
          id: number
          content: string
          choice_text?: string | null
          is_ending: boolean
        }>
        is_complete: boolean
      }>
    }
  ): Promise<void> {
    await api.post(`/stories/${storyId}/branches`, data)
  },

  // Get current node (resume from where left off)
  async getCurrentNode(storyId: string): Promise<StoryNode> {
    const response = await api.get(`/stories/${storyId}/current`)
    return response.data
  },

  // === Streaming endpoints for real-time generation ===
  
  // Stream story opening generation
  async streamOpening(storyId: string, callbacks: StreamCallbacks): Promise<void> {
    return streamGeneration(`/stories/${storyId}/stream/opening`, callbacks)
  },

  // Stream story continuation
  async streamContinuation(
    storyId: string,
    nodeId: string,
    data: ContinueStoryRequest,
    callbacks: StreamCallbacks
  ): Promise<void> {
    return streamGeneration(
      `/stories/${storyId}/nodes/${nodeId}/stream/continue`,
      callbacks,
      data
    )
  },

  // Stream story ending
  async streamEnding(
    storyId: string,
    nodeId: string,
    callbacks: StreamCallbacks
  ): Promise<void> {
    return streamGeneration(`/stories/${storyId}/nodes/${nodeId}/stream/ending`, callbacks)
  },
}

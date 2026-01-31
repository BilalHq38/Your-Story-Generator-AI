import { api } from './client'
import type { 
  Story, 
  StoryNode, 
  CreateStoryRequest, 
  ContinueStoryRequest,
  PaginatedResponse 
} from '@/types'

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
}

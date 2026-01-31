import { api } from './client'
import type { Job } from '@/types'

// Job API endpoints for async story generation
export const jobApi = {
  // Get job status
  async getJob(jobId: string): Promise<Job> {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },

  // Poll job until completion
  async pollJob(
    jobId: string, 
    onProgress?: (job: Job) => void,
    interval = 1000,
    maxAttempts = 120 // 2 minutes max
  ): Promise<Job> {
    let attempts = 0
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++
          const job = await this.getJob(jobId)
          
          if (onProgress) {
            onProgress(job)
          }
          
          if (job.status === 'completed') {
            resolve(job)
            return
          }
          
          if (job.status === 'failed') {
            reject(new Error(job.error_message || 'Job failed'))
            return
          }
          
          if (attempts >= maxAttempts) {
            reject(new Error('Job timed out'))
            return
          }
          
          // Continue polling
          setTimeout(poll, interval)
        } catch (error) {
          reject(error)
        }
      }
      
      poll()
    })
  },

  // Cancel a job (if supported)
  async cancelJob(jobId: string): Promise<void> {
    await api.post(`/jobs/${jobId}/cancel`)
  },

  // Get all jobs for a story
  async getStoryJobs(storyId: string): Promise<Job[]> {
    const response = await api.get(`/jobs`, { params: { story_id: storyId } })
    return response.data.items
  },
}

import axios, { AxiosError } from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Create axios instance with defaults
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for AI generation
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail: string }>) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    
    // Don't show toast for specific errors we handle manually
    if (!error.config?.headers?.['X-Silent-Error']) {
      toast.error(message)
    }
    
    return Promise.reject(error)
  }
)

// API Response types
interface ApiResponse<T> {
  data: T
}

// Export type for use elsewhere if needed
export type { ApiResponse }

// Generic request helper
export async function apiRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  url: string,
  data?: unknown,
  silent = false
): Promise<T> {
  const config = silent ? { headers: { 'X-Silent-Error': 'true' } } : {}
  
  const response = await api.request<T>({
    method,
    url,
    data,
    ...config,
  })
  
  return response.data
}

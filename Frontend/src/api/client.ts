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

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage (persisted by zustand)
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      try {
        const { state } = JSON.parse(authStorage)
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail: string }>) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    
    // Handle 401 Unauthorized - clear auth and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      // Only redirect if not already on auth pages
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/signup')) {
        window.location.href = '/login'
      }
    }
    
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

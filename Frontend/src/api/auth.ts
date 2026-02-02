import { api } from './client'
import { useAuthStore, User } from '@/stores/authStore'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials)
    return response.data
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', userData)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async updateProfile(data: { name?: string }): Promise<User> {
    const response = await api.patch<User>('/auth/me', data)
    return response.data
  },

  async changePassword(data: { current_password: string; new_password: string }): Promise<void> {
    await api.post('/auth/change-password', data)
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } finally {
      useAuthStore.getState().logout()
    }
  },
}

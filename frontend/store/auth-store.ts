import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  company_name?: string
  role: string
  subscription_tier: string
  email_verified: boolean
  created_at: string
  last_login?: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (tokens: { access_token: string; refresh_token: string }, user: User) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  setTokens: (tokens: { access_token: string; refresh_token: string }) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: (tokens, user) => {
        // Store tokens in localStorage for API client
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', tokens.access_token)
          localStorage.setItem('refresh_token', tokens.refresh_token)
        }
        
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          isAuthenticated: true,
          isLoading: false
        })
      },

      logout: () => {
        // Clear tokens from localStorage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        }
        
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false
        })
      },

      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData }
          })
        }
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      },

      setTokens: (tokens) => {
        // Update tokens in localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', tokens.access_token)
          localStorage.setItem('refresh_token', tokens.refresh_token)
        }
        
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token
        })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// Helper hooks
export const useUser = () => {
  const user = useAuthStore(state => state.user)
  return user
}

export const useIsAuthenticated = () => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated)
  return isAuthenticated
}

export const useAuthActions = () => {
  const { login, logout, updateUser, setLoading, setTokens } = useAuthStore()
  return { login, logout, updateUser, setLoading, setTokens }
}

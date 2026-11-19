import { reactive } from 'vue'
import { authService } from '../services/auth.service'
import {
  clearSessionTokens,
  getAccessToken,
  getRefreshToken,
  setSessionTokens,
} from '../services/session'

const state = reactive({ user: null })
let sessionRestored = false
let restorationPromise = null

export const authStore = {
  get user() {
    return state.user
  },
  get isAuthenticated() {
    return Boolean(getAccessToken() && state.user)
  },
  get isStaff() {
    return state.user?.rol === 'admin' || state.user?.rol === 'bibliotecario'
  },
  get isAdmin() {
    return state.user?.rol === 'admin'
  },

  async login(email, password) {
    const tokens = await authService.login(email, password)
    setSessionTokens(tokens)
    sessionRestored = true
    try {
      state.user = await authService.me()
      return state.user
    } catch (error) {
      clearSessionTokens()
      state.user = null
      throw error
    }
  },

  async loadUser() {
    if (!getAccessToken()) return null
    if (state.user) return state.user
    state.user = await authService.me()
    return state.user
  },

  async restoreSession() {
    if (state.user && getAccessToken()) return state.user
    if (sessionRestored) return null
    if (restorationPromise) return restorationPromise

    sessionRestored = true
    const refreshToken = getRefreshToken()
    if (!refreshToken) return null

    restorationPromise = (async () => {
      try {
        const tokens = await authService.refresh(refreshToken)
        setSessionTokens(tokens)
        state.user = await authService.me()
        return state.user
      } catch {
        clearSessionTokens()
        state.user = null
        return null
      } finally {
        restorationPromise = null
      }
    })()
    return restorationPromise
  },

  async logout() {
    const refreshToken = getRefreshToken()
    try {
      if (refreshToken) await authService.logout(refreshToken)
    } finally {
      clearSessionTokens()
      state.user = null
    }
  },

  clearUser() {
    clearSessionTokens()
    state.user = null
    sessionRestored = true
  },
}

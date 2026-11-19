import axios from 'axios'
import {
  clearSessionTokens,
  getAccessToken,
  getRefreshToken,
  setSessionTokens,
} from './session'

const configuredUrl = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, '')
const apiBaseUrl = configuredUrl
  ? configuredUrl.endsWith('/api/v1')
    ? configuredUrl
    : `${configuredUrl}/api/v1`
  : undefined

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 20000,
})

let refreshRequest

function notifySessionExpired(status) {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('biblioteca:session-expired', { detail: { status } }))
  }
}

api.interceptors.request.use((config) => {
  if (!apiBaseUrl) {
    return Promise.reject(new Error('Configura VITE_API_URL para conectar con la API.'))
  }

  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config
    if (
      error.response?.status !== 401
      || !request
      || request.skipAuthRefresh
      || request._authRetried
      || request.url?.includes('/auth/login')
    ) {
      return Promise.reject(error)
    }

    const currentRefreshToken = getRefreshToken()
    if (!currentRefreshToken) {
      clearSessionTokens()
      notifySessionExpired()
      return Promise.reject(error)
    }

    request._authRetried = true
    if (!refreshRequest) {
      refreshRequest = axios.post(
        `${apiBaseUrl}/auth/refresh`,
        { refresh_token: currentRefreshToken },
        { timeout: 20000 },
      )
        .then(({ data }) => {
          setSessionTokens(data)
          return data.access_token
        })
        .catch((refreshError) => {
          clearSessionTokens()
          notifySessionExpired(refreshError.response?.status)
          throw refreshError
        })
        .finally(() => {
          refreshRequest = undefined
        })
    }

    try {
      const token = await refreshRequest
      request.headers.Authorization = `Bearer ${token}`
      return api(request)
    } catch (refreshError) {
      return Promise.reject(refreshError)
    }
  },
)

export function getApiErrorMessage(error, fallback = 'No se pudo completar la solicitud.') {
  if (error instanceof Error && !error.isAxiosError) return error.message

  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item.msg).filter(Boolean)
    if (messages.length) return messages.join('. ')
  }

  if (error.response?.status === 401) return 'Tu sesión venció. Inicia sesión nuevamente.'
  if (error.response?.status === 403) return 'No tienes permisos para realizar esta acción.'
  if (error.response?.status >= 500) return 'El servidor no pudo completar la solicitud.'
  if (!error.response) return 'No se pudo conectar con la API. Comprueba la conexión e inténtalo de nuevo.'
  return fallback
}

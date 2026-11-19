let accessToken = null
let refreshToken = null
const refreshTokenStorageKey = 'biblioteca.refresh_token'

function readStoredRefreshToken() {
  if (typeof window === 'undefined') return null
  return window.sessionStorage.getItem(refreshTokenStorageKey)
}

export function setSessionTokens(tokens) {
  if (
    typeof tokens?.access_token !== 'string'
    || typeof tokens?.refresh_token !== 'string'
  ) {
    throw new Error('La API devolvió tokens de sesión inválidos.')
  }

  accessToken = tokens.access_token
  refreshToken = tokens.refresh_token
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(refreshTokenStorageKey, refreshToken)
  }
}

export function getAccessToken() {
  return accessToken
}

export function getRefreshToken() {
  refreshToken = readStoredRefreshToken()
  return refreshToken
}

export function clearSessionTokens() {
  accessToken = null
  refreshToken = null
  if (typeof window !== 'undefined') {
    window.sessionStorage.clear()
  }
}

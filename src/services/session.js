let accessToken = null
let refreshToken = null

export function setSessionTokens(tokens) {
  if (
    typeof tokens?.access_token !== 'string'
    || typeof tokens?.refresh_token !== 'string'
  ) {
    throw new Error('La API devolvió tokens de sesión inválidos.')
  }

  accessToken = tokens.access_token
  refreshToken = tokens.refresh_token
}

export function getAccessToken() {
  return accessToken
}

export function getRefreshToken() {
  return refreshToken
}

export function clearSessionTokens() {
  accessToken = null
  refreshToken = null
}

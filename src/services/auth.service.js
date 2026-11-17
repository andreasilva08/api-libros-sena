import { api } from './api'

export const authService = {
  async login(email, password) {
    const form = new URLSearchParams({ username: email, password })
    const { data } = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      skipAuthRefresh: true,
    })
    return data
  },

  async me() {
    const { data } = await api.get('/auth/me')
    return data
  },

  async logout(refreshToken) {
    await api.post('/auth/logout', { refresh_token: refreshToken }, {
      skipAuthRefresh: true,
    })
  },

  async changePassword(payload) {
    await api.patch('/auth/me/password', payload)
  },
}

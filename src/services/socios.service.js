import { api } from './api'

export const sociosService = {
  async list(params) {
    const { data } = await api.get('/socios/', { params })
    return data
  },
  async get(id) {
    const { data } = await api.get(`/socios/${id}`)
    return data
  },
  async me() {
    const { data } = await api.get('/socios/me')
    return data
  },
  async create(payload) {
    const { data } = await api.post('/socios/', payload)
    return data
  },
  async update(id, payload) {
    const { data } = await api.patch(`/socios/${id}`, payload)
    return data
  },
  async updateMe(payload) {
    const { data } = await api.patch('/socios/me', payload)
    return data
  },
  async remove(id) {
    const { data } = await api.delete(`/socios/${id}`)
    return data
  },
  async loansForMe(params) {
    const { data } = await api.get('/socios/me/prestamos', { params })
    return data
  },
  async finesForMe(params) {
    const { data } = await api.get('/socios/me/multas', { params })
    return data
  },
}

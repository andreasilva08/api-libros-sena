import { api } from './api'
import { normalizeAuthor, normalizePage } from './catalog-normalizers'

export const autoresService = {
  async list(params = {}) {
    const requestParams = { skip: 0, limit: 100, ...params }
    const { data } = await api.get('/autores/', { params: requestParams })
    return normalizePage(data, requestParams, normalizeAuthor, 'autores')
  },
  async get(id) {
    const { data } = await api.get(`/autores/${id}`)
    return data
  },
  async create(payload) {
    const { data } = await api.post('/autores/', payload)
    return data
  },
  async update(id, payload) {
    const { data } = await api.patch(`/autores/${id}`, payload)
    return data
  },
  async remove(id) {
    await api.delete(`/autores/${id}`)
  },
}

import { api } from './api'

export const autoresService = {
  async list(params) {
    const { data } = await api.get('/autores/', { params })
    return data
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

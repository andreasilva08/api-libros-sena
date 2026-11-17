import { api } from './api'

export const librosService = {
  async list(params) {
    const { data } = await api.get('/libros/', { params })
    return data
  },
  async get(id) {
    const { data } = await api.get(`/libros/${id}`)
    return data
  },
  async create(payload) {
    const { data } = await api.post('/libros/', payload)
    return data
  },
  async update(id, payload) {
    const { data } = await api.patch(`/libros/${id}`, payload)
    return data
  },
  async uploadCover(id, file) {
    const form = new FormData()
    form.append('archivo', file)
    const { data } = await api.put(`/libros/${id}/portada`, form)
    return data
  },
  async remove(id) {
    await api.delete(`/libros/${id}`)
  },
}

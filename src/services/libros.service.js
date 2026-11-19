import { api } from './api'
import { normalizeBook, normalizePage } from './catalog-normalizers'

export const librosService = {
  async list(params = {}) {
    const requestParams = { skip: 0, limit: 8, ...params }
    const { data } = await api.get('/libros/', {
      params: requestParams,
    })
    return normalizePage(
      data,
      requestParams,
      normalizeBook,
      'el catálogo de libros',
    )
  },
  async get(id) {
    const { data } = await api.get(`/libros/${id}`)
    return normalizeBook(data)
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

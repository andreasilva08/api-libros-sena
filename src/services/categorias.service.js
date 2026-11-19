import { api } from './api'
import { normalizeCategory, normalizePage } from './catalog-normalizers'

export const categoriasService = {
  async list(params = {}) {
    const requestParams = { skip: 0, limit: 100, ...params }
    const { data } = await api.get('/categorias/', { params: requestParams })
    return normalizePage(data, requestParams, normalizeCategory, 'categorías')
  },
  async create(payload) {
    const { data } = await api.post('/categorias/', payload)
    return data
  },
  async update(id, payload) {
    const { data } = await api.patch(`/categorias/${id}`, payload)
    return data
  },
  async remove(id) {
    await api.delete(`/categorias/${id}`)
  },
}

import { api } from './api'

export const categoriasService = {
  async list(params) {
    const { data } = await api.get('/categorias/', { params })
    return data
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

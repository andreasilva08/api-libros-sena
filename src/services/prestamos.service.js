import { api } from './api'

export const prestamosService = {
  async list(params) {
    const { data } = await api.get('/prestamos/', { params })
    return data
  },
  async get(id) {
    const { data } = await api.get(`/prestamos/${id}`)
    return data
  },
  async create(payload) {
    const { data } = await api.post('/prestamos/', payload)
    return data
  },
  async request(payload) {
    const { data } = await api.post('/prestamos/solicitar', payload)
    return data
  },
  async returnLoan(id, payload) {
    const { data } = await api.post(`/prestamos/${id}/devolucion`, payload)
    return data
  },
}

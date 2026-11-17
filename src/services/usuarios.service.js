import { api } from './api'

export const usuariosService = {
  async list(params) {
    const { data } = await api.get('/usuarios/', { params })
    return data
  },
  async create(payload) {
    const { data } = await api.post('/usuarios/', payload)
    return data
  },
  async updateRole(id, rol) {
    const { data } = await api.patch(`/usuarios/${id}/rol`, { rol })
    return data
  },
  async updateActive(id, activo) {
    const { data } = await api.patch(`/usuarios/${id}/activo`, { activo })
    return data
  },
}

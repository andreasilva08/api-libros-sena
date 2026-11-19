import { api } from './api'

export const solicitudesService = {
  async list(params) {
    const { data } = await api.get('/solicitudes', { params })
    return data
  },
  async approve(id) {
    const { data } = await api.post(`/solicitudes/${id}/aprobar`)
    return data
  },
  async reject(id, motivo_rechazo) {
    const { data } = await api.post(`/solicitudes/${id}/rechazar`, {
      motivo_rechazo: motivo_rechazo || null,
    })
    return data
  },
}

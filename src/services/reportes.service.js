import { api } from './api'

export const reportesService = {
  async summary() {
    const { data } = await api.get('/reportes/resumen')
    return data
  },
  async mostBorrowedBooks(params) {
    const { data } = await api.get('/reportes/libros-mas-prestados', { params })
    return data
  },
  async categories() {
    const { data } = await api.get('/reportes/categorias')
    return data
  },
  async overdueLoans() {
    const { data } = await api.get('/reportes/prestamos-vencidos')
    return data
  },
  async membersWithFines() {
    const { data } = await api.get('/reportes/socios-con-multas')
    return data
  },
  async authors() {
    const { data } = await api.get('/reportes/autores')
    return data
  },
}

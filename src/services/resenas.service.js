import { api } from './api'

export const resenasService = {
  async list(bookId) {
    const { data } = await api.get(`/libros/${bookId}/opiniones`)
    return data
  },
  async save(bookId, payload, hasExistingReview) {
    const url = `/libros/${bookId}/opiniones`
    const { data } = hasExistingReview
      ? await api.put(url, payload)
      : await api.post(url, payload)
    return data
  },
  async remove(bookId, reviewId) {
    await api.delete(`/libros/${bookId}/opiniones/${reviewId}`)
  },
}

function asRecord(value) {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value
    : null
}

function asNumber(value, fallback = 0) {
  if (value === null || value === undefined || value === '') return fallback
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function asName(value, fallback) {
  if (typeof value === 'string') return value
  const record = asRecord(value)
  const name = record?.nombre ?? record?.name
  return typeof name === 'string' ? name : fallback
}

export function normalizePage(payload, params = {}, normalizeItem = (item) => item, resource = 'registros') {
  const outer = asRecord(payload)
  const nested = asRecord(outer?.data)
  const source = Array.isArray(payload)
    ? payload
    : Array.isArray(outer?.items)
      ? outer.items
      : Array.isArray(outer?.results)
        ? outer.results
        : Array.isArray(outer?.data)
          ? outer.data
          : Array.isArray(nested?.items)
            ? nested.items
            : Array.isArray(nested?.results)
              ? nested.results
              : null

  if (!source) {
    throw new Error(`La API devolvió un formato inválido para ${resource}.`)
  }

  const metadata = [outer, nested].filter(Boolean)
  const readInteger = (keys, fallback) => {
    for (const record of metadata) {
      for (const key of keys) {
        const raw = record[key]
        if (raw === null || raw === undefined || raw === '') continue
        const value = Number(raw)
        if (Number.isInteger(value) && value >= 0) return value
      }
    }
    return fallback
  }

  return {
    items: source.map((item) => {
      if (!asRecord(item)) {
        throw new Error(`La API devolvió un elemento inválido en ${resource}.`)
      }
      return normalizeItem(item)
    }),
    total: readInteger(['total', 'count'], source.length),
    skip: readInteger(['skip', 'offset'], asNumber(params.skip)),
    limit: readInteger(['limit'], asNumber(params.limit, source.length)),
  }
}

export function normalizeBook(value) {
  const book = asRecord(value)
  if (!book) {
    throw new Error('La API devolvió un libro inválido.')
  }

  const categories = Array.isArray(book.categorias)
    ? book.categorias
    : Array.isArray(book.categories)
      ? book.categories
      : []

  return {
    ...book,
    titulo: typeof book.titulo === 'string' ? book.titulo : '',
    isbn: typeof book.isbn === 'string' ? book.isbn : '',
    anio_publicacion: asNumber(book.anio_publicacion, null),
    ejemplares: asNumber(book.ejemplares),
    disponibles: asNumber(book.disponibles),
    autor: asRecord(book.autor) || (typeof book.autor === 'string' ? { nombre: book.autor } : null),
    categorias: categories
      .filter((category) => asRecord(category) || typeof category === 'string')
      .map((category) => (
        typeof category === 'string'
          ? { nombre: category }
          : { ...category, nombre: asName(category, 'Categoría sin nombre') }
      )),
    calificacion_promedio: asNumber(book.calificacion_promedio),
    resenas_total: Math.max(0, Math.trunc(asNumber(book.resenas_total))),
    portada_url: typeof book.portada_url === 'string' ? book.portada_url : null,
    portada_thumbnail_url: typeof book.portada_thumbnail_url === 'string'
      ? book.portada_thumbnail_url
      : null,
  }
}

export function normalizeAuthor(value) {
  const author = asRecord(value)
  if (!author) {
    throw new Error('La API devolvió un autor inválido.')
  }
  return { ...author, nombre: asName(author, 'Autor sin nombre') }
}

export function normalizeCategory(value) {
  const category = asRecord(value)
  if (!category) {
    throw new Error('La API devolvió una categoría inválida.')
  }
  return { ...category, nombre: asName(category, 'Categoría sin nombre') }
}

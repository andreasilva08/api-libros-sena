<template>
  <AppShell>
    <ModuleHeading
      eyebrow="CATÁLOGO · COLECCIÓN"
      title="Libros"
      description="Explora el catálogo, sus portadas y la disponibilidad de cada título."
    >
      <template #actions>
        <button v-if="authStore.isStaff" class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar libro
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar por título o ISBN">
      <label class="sr-only" for="book-author-filter">Filtrar por autor</label>
      <input id="book-author-filter" v-model="authorFilter" class="module-filter" type="search" placeholder="Autor" />
      <label class="sr-only" for="book-category-filter">Filtrar por categoría</label>
      <select id="book-category-filter" v-model="categoryFilter" class="module-filter">
        <option value="">Todas las categorías</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.nombre }}</option>
      </select>
      <label class="sr-only" for="book-order-filter">Ordenar libros</label>
      <select id="book-order-filter" v-model="order" class="module-filter">
        <option value="">Orden original</option>
        <option value="titulo">Título</option>
        <option value="anio">Año ascendente</option>
        <option value="-anio">Año descendente</option>
      </select>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <p v-if="optionsError" class="form-notice module-feedback" role="alert">{{ optionsError }}</p>
    <section class="catalog-section" aria-label="Catálogo de libros">
      <div class="catalog-section-heading">
        <div><h2>Catálogo visual</h2><p>Portadas, autoría y ejemplares disponibles.</p></div>
        <span class="catalog-view-label"><LayoutGrid :size="15" /> {{ page.total }} títulos</span>
      </div>
      <div v-if="loading" class="table-loading" role="status" aria-live="polite">
        <LoaderCircle class="loading-icon" :size="20" /><span>Cargando catálogo…</span>
      </div>
      <div v-else-if="loadError" class="table-empty" role="alert">
        <span class="empty-illustration"><BookOpen :size="23" /></span>
        <strong>No se pudo cargar el catálogo</strong>
        <p>{{ loadError }}</p>
        <button class="button button-secondary table-retry" type="button" @click="load">Reintentar</button>
      </div>
      <div v-else-if="!page.items.length" class="table-empty">
        <span class="empty-illustration"><BookOpen :size="23" /></span>
        <strong>No hay libros para mostrar</strong>
        <p>No se encontraron títulos con estos filtros.</p>
      </div>
      <div v-else class="book-grid">
        <article v-for="book in page.items" :key="book.id" class="book-card-template book-card-live">
          <div class="book-cover-template book-cover-live">
            <img
              v-if="coverUrl(book) && !failedCovers.has(book.id)"
              :src="coverUrl(book)"
              :alt="`Portada de ${book.titulo}`"
              loading="lazy"
              @error="markCoverFailed(book.id)"
            />
            <template v-else><BookOpen :size="32" :stroke-width="1.4" /><span>Sin portada</span></template>
          </div>
          <div class="book-template-content">
            <span class="card-overline">FICHA DE CATÁLOGO · {{ book.id }}</span>
            <h3>{{ book.titulo }}</h3>
            <p class="book-template-author"><Feather :size="14" /> {{ book.autor?.nombre || 'Autor no disponible' }}</p>
            <div class="book-template-meta">
              <span><small>ISBN</small><strong>{{ book.isbn }}</strong></span>
              <span><small>AÑO</small><strong>{{ book.anio_publicacion }}</strong></span>
              <span><small>CATEGORÍAS</small><strong>{{ book.categorias?.map((category) => category.nombre).join(', ') || '—' }}</strong></span>
            </div>
            <div class="book-availability">
              <span><span class="availability-dot"></span>Disponibilidad</span>
              <strong>{{ book.disponibles }} disponibles / {{ book.ejemplares }} ejemplares</strong>
            </div>
            <div class="book-template-footer">
              <span>{{ book.disponibles > 0 ? 'Disponible para préstamo' : 'Sin ejemplares disponibles' }}</span>
              <div v-if="authStore.isStaff" class="row-actions">
                <button class="row-action" type="button" :aria-label="`Editar ${book.titulo}`" title="Editar libro" @click="openEdit(book)"><PencilLine :size="15" /></button>
                <button class="row-action" type="button" :aria-label="`Actualizar portada de ${book.titulo}`" title="Actualizar portada" @click="openCoverEdit(book)"><ImagePlus :size="15" /></button>
                <button class="row-action" type="button" :aria-label="`Eliminar ${book.titulo}`" title="Eliminar libro" @click="pendingDelete = book"><Trash2 :size="15" /></button>
              </div>
            </div>
          </div>
        </article>
      </div>
      <footer v-if="page.total > limit" class="module-pagination">
        <span>{{ skip + 1 }}–{{ Math.min(skip + limit, page.total) }} de {{ page.total }}</span>
        <div>
          <button class="button button-secondary" type="button" :disabled="skip <= 0 || loading" @click="changePage(Math.max(0, skip - limit))">Anterior</button>
          <button class="button button-secondary" type="button" :disabled="skip + limit >= page.total || loading" @click="changePage(skip + limit)">Siguiente</button>
        </div>
      </footer>
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="book-form"
      module-name="libros"
      :modes="formModes"
      :initial-mode="dialogMode"
      :initial-values="initialValues"
      :loading="saving"
      :error="formError"
      @close="dialogOpen = false"
      @submit="save"
    />
    <ConfirmActionDialog
      :open="Boolean(pendingDelete)"
      dialog-id="delete-book"
      title="Eliminar libro"
      :description="`¿Deseas eliminar “${pendingDelete?.titulo || 'este libro'}”? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @cancel="pendingDelete = null"
      @confirm="removeBook"
    />
  </AppShell>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  BookOpen,
  Feather,
  ImagePlus,
  LayoutGrid,
  LoaderCircle,
  PencilLine,
  Plus,
  Trash2,
} from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ConfirmActionDialog from '../components/common/ConfirmActionDialog.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { autoresService } from '../services/autores.service'
import { categoriasService } from '../services/categorias.service'
import { librosService } from '../services/libros.service'
import { authStore } from '../stores/auth'

const limit = 8
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const authors = ref([])
const categories = ref([])
const loading = ref(false)
const loadError = ref('')
const optionsError = ref('')
const search = ref('')
const authorFilter = ref('')
const categoryFilter = ref('')
const order = ref('')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const selectedBook = ref(null)
const initialValues = ref({})
const formError = ref('')
const saving = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const failedCovers = ref(new Set())
let searchTimer

const bookFields = computed(() => [
  { name: 'titulo', label: 'Título', required: true, minlength: 1, maxlength: 150, placeholder: 'Título del libro' },
  { name: 'isbn', label: 'ISBN', required: true, maxlength: 13, pattern: '[0-9]{13}', placeholder: '13 dígitos', hint: 'Debe contener exactamente 13 dígitos.' },
  { name: 'anio_publicacion', label: 'Año de publicación', type: 'number', required: true, min: 1450, max: new Date().getFullYear() },
  { name: 'ejemplares', label: 'Ejemplares', type: 'number', required: true, min: 1, max: 50 },
  {
    name: 'autor_id', label: 'Autor', type: 'select', required: true,
    placeholder: 'Selecciona un autor',
    options: authors.value.map((author) => ({ value: author.id, label: author.nombre })),
  },
  {
    name: 'categoria_ids', label: 'Categorías', type: 'select', multiple: true, required: true,
    hint: 'Selecciona entre 1 y 5 categorías.',
    options: categories.value.map((category) => ({ value: category.id, label: category.nombre })),
  },
  { name: 'portada', label: 'Portada', type: 'file', accept: 'image/jpeg,image/png,image/webp', hint: 'JPEG, PNG o WebP; máximo 5 MB.' },
])
const formModes = computed(() => [
  { key: 'create', label: 'Nuevo libro', title: 'Registrar libro', submitLabel: 'Registrar libro', fields: bookFields.value },
  { key: 'edit', label: 'Editar libro', title: 'Editar libro', submitLabel: 'Guardar cambios', fields: bookFields.value },
  { key: 'cover', label: 'Portada', title: 'Actualizar portada', submitLabel: 'Subir portada', fields: [bookFields.value[6]] },
])

onMounted(async () => {
  await Promise.all([load(), loadOptions()])
})
onBeforeUnmount(() => clearTimeout(searchTimer))
watch([search, authorFilter, categoryFilter, order], () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    skip.value = 0
    load()
  }, 250)
})

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const params = {
      skip: skip.value,
      limit,
      ...(search.value.trim() ? { buscar: search.value.trim() } : {}),
      ...(authorFilter.value.trim() ? { autor: authorFilter.value.trim() } : {}),
      ...(categoryFilter.value ? { categoria_id: Number(categoryFilter.value) } : {}),
      ...(order.value ? { orden: order.value } : {}),
    }
    page.value = await librosService.list(params)
    failedCovers.value = new Set()
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudo cargar el catálogo.')
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  optionsError.value = ''
  try {
    const [authorPage, categoryPage] = await Promise.all([
      autoresService.list({ skip: 0, limit: 100 }),
      categoriasService.list({ skip: 0, limit: 100 }),
    ])
    authors.value = authorPage.items
    categories.value = categoryPage.items
  } catch (error) {
    optionsError.value = getApiErrorMessage(error, 'No se pudieron cargar autores y categorías para los filtros.')
  }
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function coverUrl(book) {
  return book.portada_thumbnail_url || book.portada_url
}

function markCoverFailed(id) {
  failedCovers.value = new Set([...failedCovers.value, id])
}

function openCreate() {
  selectedBook.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = optionsError.value
  dialogOpen.value = true
}

function openEdit(book) {
  selectedBook.value = book
  initialValues.value = {
    titulo: book.titulo,
    isbn: book.isbn,
    anio_publicacion: book.anio_publicacion,
    ejemplares: book.ejemplares,
    autor_id: book.autor_id,
    categoria_ids: book.categorias?.map((category) => category.id) || [],
    portada: null,
  }
  dialogMode.value = 'edit'
  formError.value = ''
  dialogOpen.value = true
}

function openCoverEdit(book) {
  selectedBook.value = book
  initialValues.value = { portada: null }
  dialogMode.value = 'cover'
  formError.value = ''
  dialogOpen.value = true
}

function buildBookPayload(values, mode) {
  const payload = {
    titulo: values.titulo?.trim(),
    isbn: values.isbn?.trim(),
    anio_publicacion: Number(values.anio_publicacion),
    ejemplares: Number(values.ejemplares),
    autor_id: Number(values.autor_id),
  }
  const categoryIds = (values.categoria_ids || []).map(Number).filter(Number.isInteger)
  if (mode === 'create' || categoryIds.length) payload.categoria_ids = categoryIds
  return payload
}

async function save({ mode, values }) {
  if (saving.value) return
  const categoryCount = values.categoria_ids?.length || 0
  if (mode === 'create' && categoryCount === 0) {
    formError.value = 'Selecciona al menos una categoría para el libro.'
    return
  }
  if (mode !== 'cover' && categoryCount > 5) {
    formError.value = 'Selecciona como máximo cinco categorías.'
    return
  }
  saving.value = true
  formError.value = ''
  const cover = values.portada
  try {
    if (cover instanceof File && !['image/jpeg', 'image/png', 'image/webp'].includes(cover.type)) {
      throw new Error('La portada debe ser JPEG, PNG o WebP.')
    }
    if (cover instanceof File && cover.size > 5 * 1024 * 1024) {
      throw new Error('La portada no puede superar 5 MB.')
    }
    if (mode === 'cover') {
      if (!selectedBook.value || !(cover instanceof File)) {
        throw new Error('Selecciona una imagen de portada.')
      }
      await librosService.uploadCover(selectedBook.value.id, cover)
      notice.value = 'Portada actualizada correctamente.'
    } else {
      const payload = buildBookPayload(values, mode)
      const saved = mode === 'edit' && selectedBook.value
        ? await librosService.update(selectedBook.value.id, payload)
        : await librosService.create(payload)
      notice.value = mode === 'edit' ? 'Libro actualizado correctamente.' : 'Libro registrado correctamente.'
      if (cover instanceof File) {
        try {
          await librosService.uploadCover(saved.id, cover)
          notice.value += ' Portada cargada.'
        } catch (error) {
          notice.value += ` No se pudo cargar la portada: ${getApiErrorMessage(error)}`
        }
      }
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar el libro.')
  } finally {
    saving.value = false
  }
}

async function removeBook() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  notice.value = ''
  try {
    await librosService.remove(pendingDelete.value.id)
    pendingDelete.value = null
    notice.value = 'Libro eliminado correctamente.'
    if (skip.value > 0 && page.value.items.length === 1) skip.value = Math.max(0, skip.value - limit)
    await load()
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudo eliminar el libro.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <AppShell>
    <ModuleHeading
      eyebrow="COLECCIÓN · ORGANIZACIÓN"
      title="Categorías"
      description="Organiza los libros de la biblioteca por temas y colecciones."
    >
      <template #actions>
        <button v-if="authStore.isStaff" class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar categoría
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar categorías cargadas">
      <span class="filter-hint"><Tags :size="15" /> Organización de la colección</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section" aria-label="Listado de categorías">
      <div class="table-section-heading">
        <div><h2>Directorio de categorías</h2><p>Temas disponibles para clasificar los libros.</p></div>
        <span class="record-count"><Tags :size="15" /> {{ page.total }} registros</span>
      </div>
      <ModuleTable
        aria-label="Categorías"
        :columns="columns"
        :rows="filteredCategories"
        :actions="actions"
        :icon="Tags"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="Aún no hay categorías para mostrar"
        empty-description="No se encontraron categorías con este texto."
        @row-action="handleRowAction"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="category-form"
      module-name="categorías"
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
      dialog-id="delete-category"
      title="Eliminar categoría"
      :description="`¿Deseas eliminar ${pendingDelete?.nombre || 'esta categoría'}? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @cancel="pendingDelete = null"
      @confirm="removeCategory"
    />
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { PencilLine, Plus, Tags, Trash2 } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ConfirmActionDialog from '../components/common/ConfirmActionDialog.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { categoriasService } from '../services/categorias.service'
import { authStore } from '../stores/auth'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const loading = ref(false)
const loadError = ref('')
const search = ref('')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const initialValues = ref({})
const selectedCategory = ref(null)
const formError = ref('')
const saving = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción' },
  { key: 'acciones', label: 'Acciones' },
]
const actions = computed(() => authStore.isStaff
  ? [
      { key: 'edit', label: 'Editar categoría', icon: PencilLine },
      { key: 'delete', label: 'Eliminar categoría', icon: Trash2 },
    ]
  : [])
const filteredCategories = computed(() => page.value.items.filter((category) => (
  `${category.nombre} ${category.descripcion || ''}`.toLowerCase().includes(search.value.trim().toLowerCase())
)))
const categoryFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 3, maxlength: 50, placeholder: 'Nombre de la categoría' },
  { name: 'descripcion', label: 'Descripción', type: 'textarea', maxlength: 200, placeholder: 'Descripción (opcional)', rows: 3 },
]
const formModes = [
  { key: 'create', label: 'Nueva categoría', title: 'Registrar categoría', submitLabel: 'Registrar categoría', fields: categoryFields },
  { key: 'edit', label: 'Editar categoría', title: 'Editar categoría', submitLabel: 'Guardar cambios', fields: categoryFields },
]

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    page.value = await categoriasService.list({ skip: skip.value, limit })
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar las categorías.')
  } finally {
    loading.value = false
  }
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function openCreate() {
  selectedCategory.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = ''
  dialogOpen.value = true
}

function handleRowAction({ action, row }) {
  if (action === 'edit') {
    selectedCategory.value = row
    initialValues.value = { nombre: row.nombre, descripcion: row.descripcion ?? '' }
    dialogMode.value = 'edit'
    formError.value = ''
    dialogOpen.value = true
  } else if (action === 'delete') {
    pendingDelete.value = row
  }
}

async function save({ mode, values }) {
  if (saving.value) return
  saving.value = true
  formError.value = ''
  const payload = {
    nombre: values.nombre.trim(),
    descripcion: values.descripcion?.trim() || (mode === 'edit' ? null : undefined),
  }
  if (payload.descripcion === undefined) delete payload.descripcion
  try {
    if (mode === 'edit' && selectedCategory.value) {
      await categoriasService.update(selectedCategory.value.id, payload)
      notice.value = 'Categoría actualizada correctamente.'
    } else {
      await categoriasService.create(payload)
      notice.value = 'Categoría registrada correctamente.'
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar la categoría.')
  } finally {
    saving.value = false
  }
}

async function removeCategory() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  notice.value = ''
  try {
    await categoriasService.remove(pendingDelete.value.id)
    pendingDelete.value = null
    notice.value = 'Categoría eliminada correctamente.'
    if (skip.value > 0 && page.value.items.length === 1) skip.value = Math.max(0, skip.value - limit)
    await load()
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudo eliminar la categoría.')
  } finally {
    deleting.value = false
  }
}
</script>

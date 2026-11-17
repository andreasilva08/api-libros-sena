<template>
  <AppShell>
    <ModuleHeading
      eyebrow="PERSONAS · AUTORÍA"
      title="Autores"
      description="Consulta y organiza la información de quienes dan vida a cada historia."
    >
      <template #actions>
        <button v-if="authStore.isStaff" class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar autor
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar en autores cargados">
      <label class="sr-only" for="author-nationality-filter">Filtrar por nacionalidad</label>
      <input
        id="author-nationality-filter"
        v-model="nationalityInput"
        class="module-filter"
        type="search"
        placeholder="Nacionalidad"
        @change="applyNationality"
      />
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Filtro de API</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section" aria-label="Listado de autores">
      <div class="table-section-heading">
        <div><h2>Directorio de autores</h2><p>Nombre, nacionalidad y año de nacimiento.</p></div>
        <span class="record-count"><Feather :size="15" /> {{ page.total }} registros</span>
      </div>
      <ModuleTable
        aria-label="Autores"
        :columns="columns"
        :rows="filteredAuthors"
        :actions="actions"
        :icon="Feather"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="Aún no hay autores para mostrar"
        empty-description="No se encontraron autores con estos filtros."
        @row-action="handleRowAction"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="author-form"
      module-name="autores"
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
      dialog-id="delete-author"
      title="Eliminar autor"
      :description="`¿Deseas eliminar a ${pendingDelete?.nombre || 'este autor'}? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @cancel="pendingDelete = null"
      @confirm="removeAuthor"
    />
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Feather, PencilLine, Plus, SlidersHorizontal, Trash2 } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ConfirmActionDialog from '../components/common/ConfirmActionDialog.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { autoresService } from '../services/autores.service'
import { authStore } from '../stores/auth'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const loading = ref(false)
const loadError = ref('')
const search = ref('')
const nationalityInput = ref('')
const nationality = ref('')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const initialValues = ref({})
const selectedAuthor = ref(null)
const formError = ref('')
const saving = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'nacionalidad', label: 'Nacionalidad' },
  { key: 'anio_naci', label: 'Año de nacimiento' },
  { key: 'acciones', label: 'Acciones' },
]
const actions = computed(() => authStore.isStaff
  ? [
      { key: 'edit', label: 'Editar autor', icon: PencilLine },
      { key: 'delete', label: 'Eliminar autor', icon: Trash2 },
    ]
  : [])
const filteredAuthors = computed(() => page.value.items.filter((author) => (
  `${author.nombre} ${author.nacionalidad || ''}`.toLowerCase().includes(search.value.trim().toLowerCase())
)))
const authorFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 100, placeholder: 'Nombre del autor' },
  { name: 'nacionalidad', label: 'Nacionalidad', maxlength: 60, placeholder: 'Nacionalidad (opcional)' },
  { name: 'anio_naci', label: 'Año de nacimiento', type: 'number', min: 1000, max: new Date().getFullYear(), placeholder: 'Año (opcional)' },
]
const formModes = [
  { key: 'create', label: 'Nuevo autor', title: 'Registrar autor', submitLabel: 'Registrar autor', fields: authorFields },
  { key: 'edit', label: 'Editar autor', title: 'Editar autor', submitLabel: 'Guardar cambios', fields: authorFields },
]

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    page.value = await autoresService.list({
      skip: skip.value,
      limit,
      ...(nationality.value ? { nacionalidad: nationality.value } : {}),
    })
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar los autores.')
  } finally {
    loading.value = false
  }
}

function applyNationality() {
  nationality.value = nationalityInput.value.trim()
  skip.value = 0
  load()
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function openCreate() {
  selectedAuthor.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = ''
  dialogOpen.value = true
}

function handleRowAction({ action, row }) {
  if (action === 'edit') {
    selectedAuthor.value = row
    initialValues.value = {
      nombre: row.nombre,
      nacionalidad: row.nacionalidad ?? '',
      anio_naci: row.anio_naci ?? '',
    }
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
    nacionalidad: values.nacionalidad?.trim() || (mode === 'edit' ? null : undefined),
    anio_naci: values.anio_naci === '' ? (mode === 'edit' ? null : undefined) : Number(values.anio_naci),
  }
  Object.keys(payload).forEach((key) => payload[key] === undefined && delete payload[key])
  try {
    if (mode === 'edit' && selectedAuthor.value) {
      await autoresService.update(selectedAuthor.value.id, payload)
      notice.value = 'Autor actualizado correctamente.'
    } else {
      await autoresService.create(payload)
      notice.value = 'Autor registrado correctamente.'
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar el autor.')
  } finally {
    saving.value = false
  }
}

async function removeAuthor() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  notice.value = ''
  try {
    await autoresService.remove(pendingDelete.value.id)
    pendingDelete.value = null
    notice.value = 'Autor eliminado correctamente.'
    if (skip.value > 0 && page.value.items.length === 1) skip.value = Math.max(0, skip.value - limit)
    await load()
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudo eliminar el autor.')
  } finally {
    deleting.value = false
  }
}
</script>

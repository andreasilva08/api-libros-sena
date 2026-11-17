<template>
  <AppShell>
    <ModuleHeading
      eyebrow="COMUNIDAD · AFILIACIÓN"
      :title="authStore.user?.rol === 'socio' ? 'Mi perfil' : 'Socios'"
      description="Acompaña a tu comunidad lectora y mantén sus datos al día."
    >
      <template #actions>
        <button v-if="authStore.isStaff" class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar socio
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar en socios cargados">
      <label v-if="authStore.isStaff" class="sr-only" for="member-status-filter">Filtrar por estado</label>
      <select
        v-if="authStore.isStaff"
        id="member-status-filter"
        v-model="activeFilter"
        class="module-filter"
        @change="applyFilters"
      >
        <option value="">Todos los estados</option>
        <option value="true">Activo</option>
        <option value="false">Inactivo</option>
      </select>
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Estado de afiliación</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section" aria-label="Listado de socios">
      <div class="table-section-heading">
        <div><h2>{{ authStore.user?.rol === 'socio' ? 'Información de afiliación' : 'Comunidad lectora' }}</h2><p>Contacto, estado de afiliación y fecha de alta.</p></div>
        <span class="record-count"><UsersRound :size="15" /> {{ page.total }} registros</span>
      </div>
      <ModuleTable
        aria-label="Socios"
        :columns="columns"
        :rows="filteredMembers"
        :actions="actions"
        :icon="UsersRound"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="La comunidad aparecerá aquí"
        empty-description="No se encontraron socios con estos filtros."
        @row-action="handleRowAction"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="member-form"
      module-name="socios"
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
      dialog-id="delete-member"
      title="Eliminar socio"
      :description="`¿Deseas eliminar a ${pendingDelete?.nombre || 'este socio'}? Esta acción no se puede deshacer.`"
      :loading="deleting"
      @cancel="pendingDelete = null"
      @confirm="removeMember"
    />
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { PencilLine, Plus, SlidersHorizontal, Trash2, UsersRound } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ConfirmActionDialog from '../components/common/ConfirmActionDialog.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { sociosService } from '../services/socios.service'
import { authStore } from '../stores/auth'
import { formatDate } from '../utils/format'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const loading = ref(false)
const loadError = ref('')
const search = ref('')
const activeFilter = ref('')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const initialValues = ref({})
const selectedMember = ref(null)
const formError = ref('')
const saving = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const isMemberAccount = computed(() => authStore.user?.rol === 'socio')

const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Correo electrónico' },
  { key: 'telefono', label: 'Teléfono' },
  { key: 'activo', label: 'Estado', type: 'status' },
  { key: 'fecha_alta', label: 'Fecha de afiliación', format: (row) => formatDate(row.fecha_alta) },
  { key: 'acciones', label: 'Acciones' },
]
const actions = computed(() => {
  if (isMemberAccount.value) return [{ key: 'edit', label: 'Editar mi perfil', icon: PencilLine }]
  const memberActions = [{ key: 'edit', label: 'Editar socio', icon: PencilLine }]
  if (authStore.isAdmin) memberActions.push({ key: 'delete', label: 'Eliminar socio', icon: Trash2 })
  return memberActions
})
const filteredMembers = computed(() => page.value.items.filter((member) => (
  `${member.nombre} ${member.email}`.toLowerCase().includes(search.value.trim().toLowerCase())
)))
const staffFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 100, placeholder: 'Nombre del socio' },
  { name: 'email', label: 'Correo electrónico', type: 'email', required: true, maxlength: 100, placeholder: 'persona@correo.com' },
  { name: 'telefono', label: 'Teléfono', maxlength: 15, pattern: '[0-9\\s+]{7,15}', placeholder: 'Teléfono (opcional)' },
  {
    name: 'activo', label: 'Estado de afiliación', type: 'select', default: true,
    options: [{ value: true, label: 'Activo' }, { value: false, label: 'Inactivo' }],
  },
]
const ownFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 3, maxlength: 100 },
  { name: 'telefono', label: 'Teléfono', maxlength: 15, pattern: '[0-9\\s+]{7,15}', placeholder: 'Teléfono (opcional)' },
]
const formModes = computed(() => {
  if (isMemberAccount.value) {
    return [{ key: 'edit', label: 'Mi perfil', title: 'Actualizar mi perfil', submitLabel: 'Guardar cambios', fields: ownFields }]
  }
  return [
    { key: 'create', label: 'Nuevo socio', title: 'Registrar socio', submitLabel: 'Registrar socio', fields: staffFields },
    { key: 'edit', label: 'Editar socio', title: 'Editar socio', submitLabel: 'Guardar cambios', fields: staffFields },
  ]
})

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    if (isMemberAccount.value) {
      const member = await sociosService.me()
      page.value = { items: [member], total: 1, skip: 0, limit: 1 }
    } else {
      const params = { skip: skip.value, limit }
      if (activeFilter.value !== '') params.activo = activeFilter.value === 'true'
      page.value = await sociosService.list(params)
    }
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar los socios.')
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  skip.value = 0
  load()
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function openCreate() {
  selectedMember.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = ''
  dialogOpen.value = true
}

function handleRowAction({ action, row }) {
  if (action === 'edit') {
    selectedMember.value = row
    initialValues.value = {
      nombre: row.nombre,
      email: row.email,
      telefono: row.telefono ?? '',
      activo: row.activo ?? true,
    }
    dialogMode.value = 'edit'
    formError.value = ''
    dialogOpen.value = true
  } else if (action === 'delete' && authStore.isAdmin) {
    pendingDelete.value = row
  }
}

async function save({ mode, values }) {
  if (saving.value) return
  saving.value = true
  formError.value = ''
  try {
    if (isMemberAccount.value) {
      await sociosService.updateMe({
        nombre: values.nombre.trim(),
        telefono: values.telefono?.trim() || null,
      })
      notice.value = 'Tu perfil se actualizó correctamente.'
    } else if (mode === 'edit' && selectedMember.value) {
      await sociosService.update(selectedMember.value.id, {
        nombre: values.nombre.trim(),
        email: values.email.trim(),
        telefono: values.telefono?.trim() || null,
        activo: values.activo,
      })
      notice.value = 'Socio actualizado correctamente.'
    } else {
      const payload = {
        nombre: values.nombre.trim(),
        email: values.email.trim(),
        ...(values.telefono?.trim() ? { telefono: values.telefono.trim() } : {}),
        activo: values.activo === '' ? true : values.activo,
      }
      await sociosService.create(payload)
      notice.value = 'Socio registrado correctamente.'
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar el socio.')
  } finally {
    saving.value = false
  }
}

async function removeMember() {
  if (!pendingDelete.value || deleting.value) return
  deleting.value = true
  notice.value = ''
  try {
    await sociosService.remove(pendingDelete.value.id)
    pendingDelete.value = null
    notice.value = 'Socio eliminado correctamente.'
    if (skip.value > 0 && page.value.items.length === 1) skip.value = Math.max(0, skip.value - limit)
    await load()
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudo eliminar el socio.')
  } finally {
    deleting.value = false
  }
}
</script>

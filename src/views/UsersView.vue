<template>
  <AppShell>
    <ModuleHeading
      eyebrow="ACCESO · EQUIPO"
      title="Usuarios"
      description="Administra las cuentas, los roles y el estado de acceso del sistema."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar usuario
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar en usuarios cargados">
      <label class="sr-only" for="user-role-filter">Filtrar por rol</label>
      <select id="user-role-filter" v-model="roleFilter" class="module-filter">
        <option value="">Todos los roles</option>
        <option value="admin">Administrador</option>
        <option value="bibliotecario">Bibliotecario</option>
        <option value="socio">Socio</option>
      </select>
      <span class="filter-hint"><ShieldCheck :size="15" /> Filtro en la página</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section" aria-label="Listado de usuarios">
      <div class="table-section-heading">
        <div><h2>Cuentas de usuario</h2><p>Correo, rol, estado y socio asociado cuando corresponda.</p></div>
        <span class="record-count"><UserRoundCog :size="15" /> {{ page.total }} cuentas</span>
      </div>
      <ModuleTable
        aria-label="Usuarios"
        :columns="columns"
        :rows="filteredUsers"
        :actions="actions"
        :icon="UsersRound"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="Las cuentas aparecerán aquí"
        empty-description="No se encontraron cuentas con estos filtros."
        @row-action="handleRowAction"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <div class="loan-note"><Info :size="17" /><p>La API permite crear cuentas, cambiar su rol y estado por separado. Para asignar el rol Socio debe vincularse un socio existente con el mismo correo.</p></div>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="user-form"
      module-name="usuarios"
      :modes="formModes"
      :initial-mode="dialogMode"
      :initial-values="initialValues"
      :loading="saving"
      :error="formError"
      @close="dialogOpen = false"
      @submit="save"
    />
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Info, PencilLine, Plus, ShieldCheck, UserRoundCog, UsersRound } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { sociosService } from '../services/socios.service'
import { usuariosService } from '../services/usuarios.service'
import { authStore } from '../stores/auth'
import { formatDate } from '../utils/format'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const members = ref([])
const loading = ref(false)
const loadError = ref('')
const optionsError = ref('')
const search = ref('')
const roleFilter = ref('')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const selectedUser = ref(null)
const initialValues = ref({})
const formError = ref('')
const saving = ref(false)

const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Correo electrónico' },
  { key: 'rol', label: 'Rol', format: (row) => ({ admin: 'Administrador', bibliotecario: 'Bibliotecario', socio: 'Socio' }[row.rol] || row.rol) },
  { key: 'activo', label: 'Estado', type: 'status' },
  { key: 'socio_id', label: 'Socio asociado' },
  { key: 'creado_en', label: 'Creado', format: (row) => formatDate(row.creado_en) },
  { key: 'acciones', label: 'Acciones' },
]
const actions = computed(() => [
  { key: 'role', label: 'Cambiar rol', icon: ShieldCheck, visible: (row) => row.id !== authStore.user?.id },
  { key: 'status', label: 'Cambiar estado', icon: PencilLine, visible: (row) => row.id !== authStore.user?.id },
])
const filteredUsers = computed(() => page.value.items.filter((user) => {
  const matchesSearch = `${user.nombre} ${user.email}`.toLowerCase().includes(search.value.trim().toLowerCase())
  return matchesSearch && (!roleFilter.value || user.rol === roleFilter.value)
}))
const availableMembers = computed(() => {
  const linked = new Set(page.value.items.map((user) => user.socio_id).filter(Boolean))
  return members.value.filter((member) => !linked.has(member.id))
})
const formModes = computed(() => [
  {
    key: 'create',
    label: 'Crear usuario',
    title: 'Registrar usuario',
    submitLabel: 'Registrar usuario',
    fields: [
      { name: 'nombre', label: 'Nombre', required: true, minlength: 3, maxlength: 100, placeholder: 'Nombre de usuario' },
      { name: 'email', label: 'Correo electrónico', type: 'email', required: true, maxlength: 100, placeholder: 'persona@correo.com' },
      {
        name: 'password',
        label: 'Contraseña',
        type: 'password',
        required: true,
        minlength: 8,
        maxlength: 64,
        pattern: '(?=.*[A-Z])(?=.*[a-z])(?=.*\\d).{8,64}',
        placeholder: 'Contraseña (8 a 64 caracteres)',
        hint: 'Incluye al menos una mayúscula, una minúscula y un número.',
      },
      { name: 'rol', label: 'Rol', type: 'select', required: true, options: [
        { value: 'admin', label: 'Administrador' },
        { value: 'bibliotecario', label: 'Bibliotecario' },
        { value: 'socio', label: 'Socio' },
      ] },
      {
        name: 'socio_id', label: 'Socio vinculado', type: 'select',
        placeholder: 'No aplica / seleccionar socio',
        hint: 'Obligatorio para el rol Socio; el correo debe coincidir con el del socio.',
        options: availableMembers.value.map((member) => ({
          value: member.id,
          label: `${member.nombre} — ${member.email}`,
        })),
      },
    ],
  },
  {
    key: 'role',
    label: 'Cambiar rol',
    title: 'Actualizar rol',
    submitLabel: 'Actualizar rol',
    fields: [{
      name: 'rol', label: 'Nuevo rol', type: 'select', required: true,
      options: [
        { value: 'admin', label: 'Administrador' },
        { value: 'bibliotecario', label: 'Bibliotecario' },
        { value: 'socio', label: 'Socio' },
      ],
    }],
  },
  {
    key: 'status',
    label: 'Cambiar estado',
    title: 'Actualizar estado',
    submitLabel: 'Actualizar estado',
    fields: [{
      name: 'activo', label: 'Estado de la cuenta', type: 'select', required: true,
      options: [{ value: true, label: 'Activo' }, { value: false, label: 'Inactivo' }],
    }],
  },
])

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const [usersResult, membersResult] = await Promise.allSettled([
      usuariosService.list({ skip: skip.value, limit }),
      sociosService.list({ skip: 0, limit: 100 }),
    ])
    if (usersResult.status === 'rejected') throw usersResult.reason
    page.value = usersResult.value
    if (membersResult.status === 'fulfilled') {
      members.value = membersResult.value.items
      optionsError.value = ''
    } else {
      optionsError.value = getApiErrorMessage(membersResult.reason, 'No se pudieron cargar los socios para vincular.')
    }
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar los usuarios.')
  } finally {
    loading.value = false
  }
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function openCreate() {
  selectedUser.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = optionsError.value
  dialogOpen.value = true
}

function handleRowAction({ action, row }) {
  selectedUser.value = row
  formError.value = ''
  if (action === 'role') {
    initialValues.value = { rol: row.rol }
    dialogMode.value = 'role'
    dialogOpen.value = true
  } else if (action === 'status') {
    initialValues.value = { activo: row.activo }
    dialogMode.value = 'status'
    dialogOpen.value = true
  }
}

async function save({ mode, values }) {
  if (saving.value || !selectedUser.value && mode !== 'create') return
  saving.value = true
  formError.value = ''
  try {
    if (mode === 'role') {
      if (values.rol === 'socio' && !selectedUser.value.socio_id) {
        throw new Error('Para asignar el rol Socio, primero debe existir un socio vinculado a esta cuenta.')
      }
      await usuariosService.updateRole(selectedUser.value.id, values.rol)
      notice.value = 'Rol actualizado correctamente.'
    } else if (mode === 'status') {
      await usuariosService.updateActive(selectedUser.value.id, values.activo)
      notice.value = 'Estado actualizado correctamente.'
    } else {
      const socioId = values.socio_id ? Number(values.socio_id) : null
      const selectedMember = members.value.find((member) => member.id === socioId)
      if (values.rol === 'socio' && !selectedMember) {
        throw new Error('Selecciona un socio existente para crear una cuenta con ese rol.')
      }
      if (selectedMember && selectedMember.email.toLowerCase() !== values.email.trim().toLowerCase()) {
        throw new Error('El correo de la cuenta debe coincidir con el correo del socio vinculado.')
      }
      await usuariosService.create({
        nombre: values.nombre.trim(),
        email: values.email.trim(),
        password: values.password,
        rol: values.rol,
        ...(socioId ? { socio_id: socioId } : {}),
      })
      notice.value = 'Usuario registrado correctamente.'
    }
    dialogOpen.value = false
    await load()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar el usuario.')
  } finally {
    saving.value = false
  }
}
</script>

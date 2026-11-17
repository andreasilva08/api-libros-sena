<template>
  <AppShell>
    <ModuleHeading
      eyebrow="CIRCULACIÓN · LECTURAS"
      :title="isMemberAccount ? 'Mis préstamos' : 'Préstamos'"
      description="Revisa los préstamos, sus fechas límite y las devoluciones pendientes."
    >
      <template #actions>
        <button v-if="authStore.isStaff" class="button button-primary module-action" type="button" @click="openCreate">
          <Plus :size="17" /> Registrar préstamo
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar v-model="search" search-placeholder="Buscar en préstamos cargados">
      <div class="loan-state-tabs" role="group" aria-label="Estado del préstamo">
        <button
          v-for="state in states"
          :key="state.value"
          type="button"
          :aria-pressed="selectedState === state.value"
          :class="{ 'loan-state-active': selectedState === state.value }"
          @click="selectState(state.value)"
        >{{ state.label }}</button>
      </div>
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Estado admitido por la API</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section" aria-label="Listado de préstamos">
      <div class="table-section-heading">
        <div><h2>{{ selectedTitle }}</h2><p>Fechas de préstamo, vencimiento, devolución y multa.</p></div>
        <span class="record-count"><ArrowLeftRight :size="15" /> {{ page.total }} registros</span>
      </div>
      <ModuleTable
        aria-label="Préstamos"
        :columns="columns"
        :rows="filteredLoans"
        :actions="actions"
        :icon="BookOpenCheck"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="No hay préstamos para mostrar"
        empty-description="No se encontraron préstamos con este estado."
        @row-action="handleRowAction"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <div class="loan-note"><CalendarDays :size="17" /><p>La API calcula y devuelve la fecha límite y la multa. El modelo actual no expone el personal responsable.</p></div>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="loan-form"
      module-name="préstamos"
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
import { ArrowLeftRight, BookOpenCheck, CalendarDays, CornerDownLeft, Plus, SlidersHorizontal } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'
import { getApiErrorMessage } from '../services/api'
import { librosService } from '../services/libros.service'
import { prestamosService } from '../services/prestamos.service'
import { sociosService } from '../services/socios.service'
import { authStore } from '../stores/auth'
import { formatCurrency, formatDate } from '../utils/format'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const books = ref([])
const members = ref([])
const loading = ref(false)
const loadError = ref('')
const optionsError = ref('')
const search = ref('')
const selectedState = ref('activo')
const notice = ref('')
const dialogOpen = ref(false)
const dialogMode = ref('create')
const selectedLoan = ref(null)
const initialValues = ref({})
const formError = ref('')
const saving = ref(false)
const isMemberAccount = computed(() => authStore.user?.rol === 'socio')
const states = [
  { value: 'activo', label: 'Activos' },
  { value: 'vencido', label: 'Vencidos' },
  { value: 'devuelto', label: 'Devueltos' },
]
const selectedTitle = computed(() => isMemberAccount.value
  ? states.find((state) => state.value === selectedState.value)?.label || 'Mis préstamos'
  : states.find((state) => state.value === selectedState.value)?.label || 'Préstamos')
const columns = [
  { key: 'id', label: 'Préstamo' },
  { key: 'libro', label: 'Libro', format: (row) => row.libro?.titulo || '—' },
  { key: 'socio', label: 'Socio', format: (row) => row.socio?.nombre || '—' },
  { key: 'fecha_prestamo', label: 'Fecha de préstamo', format: (row) => formatDate(row.fecha_prestamo) },
  { key: 'fecha_limite', label: 'Fecha límite', format: (row) => formatDate(row.fecha_limite) },
  { key: 'fecha_devolucion', label: 'Devolución', format: (row) => formatDate(row.fecha_devolucion) },
  { key: 'multa', label: 'Multa', format: (row) => formatCurrency(row.multa) },
  { key: 'acciones', label: 'Acciones' },
]
const actions = computed(() => authStore.isStaff
  ? [{ key: 'return', label: 'Registrar devolución', icon: CornerDownLeft, visible: (row) => !row.fecha_devolucion }]
  : [])
const filteredLoans = computed(() => page.value.items.filter((loan) => {
  const searchValue = `${loan.id} ${loan.libro?.titulo || ''} ${loan.socio?.nombre || ''}`.toLowerCase()
  return searchValue.includes(search.value.trim().toLowerCase())
}))
const formModes = computed(() => authStore.isStaff
  ? [
      {
        key: 'create',
        label: 'Nuevo préstamo',
        title: 'Registrar préstamo',
        submitLabel: 'Registrar préstamo',
        fields: [
          {
            name: 'libro_id', label: 'Libro disponible', type: 'select', required: true,
            placeholder: 'Selecciona un libro',
            options: books.value.filter((book) => book.disponibles > 0).map((book) => ({
              value: book.id,
              label: `${book.titulo} (${book.disponibles} disponibles)`,
            })),
          },
          {
            name: 'socio_id', label: 'Socio activo', type: 'select', required: true,
            placeholder: 'Selecciona un socio',
            options: members.value.filter((member) => member.activo).map((member) => ({
              value: member.id,
              label: `${member.nombre} — ${member.email}`,
            })),
          },
          { name: 'fecha_prestamo', label: 'Fecha de préstamo', type: 'date', hint: 'Opcional; si se omite, la API define la fecha.' },
          { name: 'dias', label: 'Duración (días)', type: 'number', min: 1, max: 30, placeholder: '14', hint: 'Opcional; valor predeterminado 14, rango de 1 a 30.' },
        ],
      },
      {
        key: 'return',
        label: 'Devolución',
        title: `Registrar devolución${selectedLoan.value ? ` · préstamo ${selectedLoan.value.id}` : ''}`,
        submitLabel: 'Registrar devolución',
        note: 'La API recibe una fecha opcional y calcula la multa correspondiente.',
        fields: [{ name: 'fecha_devolucion', label: 'Fecha de devolución', type: 'date', hint: 'Opcional; si se omite, la API define la fecha.' }],
      },
    ]
  : [])

onMounted(async () => {
  await load()
  if (authStore.isStaff) await loadOptions()
})

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const params = { estado: selectedState.value, skip: skip.value, limit }
    page.value = isMemberAccount.value
      ? await sociosService.loansForMe(params)
      : await prestamosService.list(params)
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar los préstamos.')
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  optionsError.value = ''
  try {
    const [bookPage, memberPage] = await Promise.all([
      librosService.list({ skip: 0, limit: 100 }),
      sociosService.list({ skip: 0, limit: 100, activo: true }),
    ])
    books.value = bookPage.items
    members.value = memberPage.items
  } catch (error) {
    optionsError.value = getApiErrorMessage(error, 'No se pudieron cargar libros y socios para el préstamo.')
  }
}

function selectState(value) {
  selectedState.value = value
  skip.value = 0
  load()
}

function changePage(nextSkip) {
  skip.value = nextSkip
  load()
}

function openCreate() {
  selectedLoan.value = null
  initialValues.value = {}
  dialogMode.value = 'create'
  formError.value = optionsError.value
  dialogOpen.value = true
}

function handleRowAction({ action, row }) {
  if (action !== 'return' || !authStore.isStaff) return
  selectedLoan.value = row
  initialValues.value = {}
  dialogMode.value = 'return'
  formError.value = ''
  dialogOpen.value = true
}

async function save({ mode, values }) {
  if (saving.value) return
  saving.value = true
  formError.value = ''
  try {
    if (mode === 'return') {
      if (!selectedLoan.value) throw new Error('Selecciona el préstamo que se va a devolver.')
      const payload = values.fecha_devolucion ? { fecha_devolucion: values.fecha_devolucion } : {}
      await prestamosService.returnLoan(selectedLoan.value.id, payload)
      notice.value = `Devolución del préstamo ${selectedLoan.value.id} registrada.`
    } else {
      const payload = {
        libro_id: Number(values.libro_id),
        socio_id: Number(values.socio_id),
        ...(values.fecha_prestamo ? { fecha_prestamo: values.fecha_prestamo } : {}),
        ...(values.dias !== '' && values.dias !== undefined ? { dias: Number(values.dias) } : {}),
      }
      await prestamosService.create(payload)
      notice.value = 'Préstamo registrado correctamente.'
    }
    dialogOpen.value = false
    await load()
    await loadOptions()
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'No se pudo guardar el préstamo.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppShell>
    <ModuleHeading
      eyebrow="ACCESO · MEMBRESÍAS"
      title="Solicitudes"
      description="Revisa las solicitudes de membresía y registra una decisión."
    />

    <ModuleToolbar v-model="search" search-placeholder="Buscar en solicitudes cargadas">
      <label class="sr-only" for="request-state-filter">Filtrar por estado</label>
      <select id="request-state-filter" v-model="stateFilter" class="module-filter" @change="applyFilters">
        <option value="pendiente">Pendientes</option>
        <option value="aprobada">Aprobadas</option>
        <option value="rechazada">Rechazadas</option>
      </select>
      <span class="filter-hint"><ClipboardList :size="15" /> Estado de revisión</span>
    </ModuleToolbar>

    <p v-if="notice" class="form-notice module-feedback" role="status">{{ notice }}</p>
    <section class="table-section request-table-section" aria-label="Solicitudes de registro">
      <div class="table-section-heading">
        <div><h2>{{ stateTitle }}</h2><p>Datos proporcionados para la solicitud de membresía.</p></div>
        <span class="record-count"><UsersRound :size="15" /> {{ page.total }} solicitudes</span>
      </div>
      <ModuleTable
        aria-label="Solicitudes de registro"
        :columns="columns"
        :rows="filteredRequests"
        :actions="actions"
        :icon="ClipboardList"
        :loading="loading"
        :error="loadError"
        :total="page.total"
        :skip="skip"
        :limit="limit"
        empty-title="No hay solicitudes para mostrar"
        empty-description="No se encontraron solicitudes con este estado."
        @row-action="openReview"
        @page-change="changePage"
        @retry="load"
      />
    </section>

    <div v-if="selectedRequest" class="dialog-overlay" @click.self="closeReview">
      <section
        class="preview-dialog request-review-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="request-review-title"
        @keydown.esc="closeReview"
      >
        <header class="dialog-heading">
          <span class="confirm-icon"><ShieldCheck :size="19" /></span>
          <button class="dialog-close" type="button" aria-label="Cerrar confirmación" :disabled="processing" @click="closeReview">
            <X :size="18" />
          </button>
        </header>
        <h2 id="request-review-title">{{ reviewTitle }}</h2>
        <p class="confirm-description">{{ reviewDescription }}</p>
        <label v-if="reviewAction === 'reject'" class="preview-field request-reason" for="request-rejection-reason">
          Motivo del rechazo <span>(opcional)</span>
          <textarea
            id="request-rejection-reason"
            v-model.trim="rejectionReason"
            rows="3"
            maxlength="500"
            placeholder="Agrega un mensaje breve si es necesario."
          />
        </label>
        <p v-if="actionError" class="form-notice" role="alert">{{ actionError }}</p>
        <footer class="dialog-actions">
          <button class="button button-secondary" type="button" :disabled="processing" @click="closeReview">Cancelar</button>
          <button class="button button-primary" type="button" :disabled="processing" @click="confirmReview">
            <LoaderCircle v-if="processing" class="loading-icon" :size="15" />
            {{ processing ? 'Procesando…' : reviewAction === 'approve' ? 'Aprobar solicitud' : 'Rechazar solicitud' }}
          </button>
        </footer>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ClipboardList, LoaderCircle, ShieldCheck, UsersRound, X } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import { getApiErrorMessage } from '../services/api'
import { solicitudesService } from '../services/solicitudes.service'
import { formatDate } from '../utils/format'

const limit = 10
const skip = ref(0)
const page = ref({ items: [], total: 0 })
const loading = ref(false)
const processing = ref(false)
const loadError = ref('')
const actionError = ref('')
const notice = ref('')
const search = ref('')
const stateFilter = ref('pendiente')
const selectedRequest = ref(null)
const reviewAction = ref('')
const rejectionReason = ref('')
const stateTitle = computed(() => ({
  pendiente: 'Pendientes',
  aprobada: 'Aprobadas',
  rechazada: 'Rechazadas',
}[stateFilter.value]))
const reviewTitle = computed(() => reviewAction.value === 'approve'
  ? '¿Aprobar esta solicitud?'
  : '¿Rechazar esta solicitud?')
const reviewDescription = computed(() => reviewAction.value === 'approve'
  ? `Se creará una cuenta de socio activa para ${selectedRequest.value?.nombre}.`
  : `La solicitud de ${selectedRequest.value?.nombre} quedará rechazada y no podrá iniciar sesión.`)
const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Correo electrónico' },
  { key: 'telefono', label: 'Teléfono' },
  { key: 'estado', label: 'Estado', format: (row) => ({ pendiente: 'Pendiente', aprobada: 'Aprobada', rechazada: 'Rechazada' }[row.estado]) },
  { key: 'creado_en', label: 'Solicitada', format: (row) => formatDate(row.creado_en) },
  { key: 'acciones', label: 'Acciones' },
]
const actions = [
  { key: 'approve', label: 'Aprobar solicitud', icon: ShieldCheck, visible: (row) => row.estado === 'pendiente' },
  { key: 'reject', label: 'Rechazar solicitud', icon: X, visible: (row) => row.estado === 'pendiente' },
]
const filteredRequests = computed(() => page.value.items.filter((item) => (
  `${item.nombre} ${item.email}`.toLowerCase().includes(search.value.trim().toLowerCase())
)))

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    page.value = await solicitudesService.list({
      estado: stateFilter.value,
      skip: skip.value,
      limit,
    })
  } catch (error) {
    loadError.value = getApiErrorMessage(error, 'No se pudieron cargar las solicitudes.')
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

function openReview({ action, row }) {
  if (row.estado !== 'pendiente') return
  selectedRequest.value = row
  reviewAction.value = action
  rejectionReason.value = ''
  actionError.value = ''
}

function closeReview() {
  if (processing.value) return
  selectedRequest.value = null
  reviewAction.value = ''
  actionError.value = ''
}

async function confirmReview() {
  if (!selectedRequest.value || processing.value) return
  processing.value = true
  actionError.value = ''
  try {
    if (reviewAction.value === 'approve') {
      await solicitudesService.approve(selectedRequest.value.id)
      notice.value = 'Solicitud aprobada y cuenta de socio creada.'
    } else {
      await solicitudesService.reject(selectedRequest.value.id, rejectionReason.value)
      notice.value = 'Solicitud rechazada.'
    }
    window.dispatchEvent(new CustomEvent('biblioteca:requests-updated'))
    selectedRequest.value = null
    reviewAction.value = ''
    if (skip.value > 0 && page.value.items.length === 1 && stateFilter.value === 'pendiente') {
      skip.value = Math.max(0, skip.value - limit)
    }
    await load()
  } catch (error) {
    actionError.value = getApiErrorMessage(error, 'No se pudo procesar la solicitud.')
  } finally {
    processing.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="welcome-row">
      <div>
        <div class="eyebrow"><span class="eyebrow-line"></span> TU BIBLIOTECA, CON CALMA</div>
        <h1>Un día lleno de<br class="welcome-break" /> buenas historias.</h1>
        <p class="welcome-copy">Aquí comienza el pulso de tu biblioteca.</p>
      </div>
      <div class="date-card">
        <span class="date-icon"><CalendarDays :size="18" /></span>
        <span><small>HOY</small><strong>{{ today }}</strong></span>
      </div>
    </section>

    <div class="section-heading">
      <div><h2>{{ isMember ? 'Mi actividad' : 'Vista general' }}</h2><p>{{ isMember ? 'Tus préstamos y tu membresía.' : 'Indicadores actualizados desde la biblioteca.' }}</p></div>
      <button class="button button-secondary module-action" type="button" :disabled="loading" @click="load">
        <LoaderCircle v-if="loading" class="loading-icon" :size="15" />
        <RefreshCw v-else :size="15" /> Actualizar
      </button>
    </div>

    <p v-if="loadError" class="form-notice module-feedback" role="alert">{{ loadError }}</p>
    <section class="stats-grid" aria-label="Indicadores de biblioteca" :aria-busy="loading">
      <article v-for="stat in stats" :key="stat.title" class="stat-card">
        <div class="stat-card-top">
          <span class="stat-icon" :class="stat.tone"><component :is="stat.icon" :size="19" /></span>
          <span class="stat-kicker">{{ stat.kicker }}</span>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <h3>{{ stat.title }}</h3>
        <p>{{ stat.description }}</p>
        <div class="stat-foot"><span class="stat-foot-line"></span>{{ stat.source }}</div>
      </article>
    </section>

    <section class="lower-grid">
      <article v-if="authStore.isStaff" class="content-card activity-card">
        <div class="card-heading">
          <div><span class="card-overline">CIRCULACIÓN</span><h2>Últimos préstamos registrados</h2></div>
          <span class="card-heading-icon"><Clock3 :size="17" /></span>
        </div>
        <div class="dashboard-shortcuts">
          <RouterLink class="button button-primary" :to="{ name: 'loans', query: { nuevo: '1' } }">
            <Plus :size="16" /> Nuevo préstamo
          </RouterLink>
          <RouterLink class="button button-secondary" :to="{ name: 'requests' }">
            <ClipboardList :size="16" /> Revisar solicitudes
          </RouterLink>
        </div>
        <div v-if="activityLoading" class="table-loading" role="status">
          <LoaderCircle class="loading-icon" :size="18" />Cargando préstamos…
        </div>
        <div v-else-if="activityError" class="empty-state" role="alert">
          <strong>No se pudieron cargar los préstamos recientes</strong>
          <p>{{ activityError }}</p>
        </div>
        <div v-else-if="latestLoans.length" class="dashboard-loan-list">
          <div v-for="loan in latestLoans" :key="loan.id" class="dashboard-loan-row">
            <span class="dashboard-loan-icon"><BookOpenCheck :size="17" /></span>
            <span class="dashboard-loan-copy">
              <strong>{{ loan.libro?.titulo || `Préstamo ${loan.id}` }}</strong>
              <small>{{ loan.socio?.nombre || 'Socio' }} · {{ formatDate(loan.fecha_prestamo) }}</small>
            </span>
            <span class="dashboard-loan-id">#{{ loan.id }}</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-illustration"><BookOpenCheck :size="24" /></span>
          <strong>Aún no hay préstamos registrados</strong>
          <p>Los nuevos préstamos aparecerán aquí.</p>
        </div>
      </article>

      <article v-else class="content-card activity-card">
        <div class="card-heading">
          <div><span class="card-overline">CIRCULACIÓN</span><h2>Mis préstamos en curso</h2></div>
          <span class="card-heading-icon"><ArrowLeftRight :size="17" /></span>
        </div>
        <div v-if="activityLoading" class="table-loading" role="status">
          <LoaderCircle class="loading-icon" :size="18" />Cargando tus préstamos…
        </div>
        <div v-else-if="activityError" class="empty-state" role="alert">
          <strong>No se pudieron cargar tus préstamos</strong>
          <p>{{ activityError }}</p>
        </div>
        <div v-else-if="memberLoans.length" class="dashboard-loan-list">
          <div v-for="loan in memberLoans" :key="loan.id" class="dashboard-loan-row">
            <span class="dashboard-loan-icon"><BookOpenCheck :size="17" /></span>
            <span class="dashboard-loan-copy">
              <strong>{{ loan.libro?.titulo || `Préstamo ${loan.id}` }}</strong>
              <small>Fecha límite: {{ formatDate(loan.fecha_limite) }}</small>
            </span>
            <span class="dashboard-loan-id">#{{ loan.id }}</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-illustration"><BookOpenCheck :size="24" /></span>
          <strong>No tienes préstamos en curso</strong>
          <p>Cuando tengas un préstamo activo, aparecerá aquí.</p>
        </div>
      </article>

      <article class="content-card reading-card">
        <div class="card-heading">
          <div><span class="card-overline">COLECCIÓN</span><h2>Libros recientes</h2></div>
          <span class="card-heading-icon"><LibraryBig :size="17" /></span>
        </div>
        <div v-if="booksLoading" class="table-loading" role="status"><LoaderCircle class="loading-icon" :size="18" />Cargando libros…</div>
        <div v-else-if="recentBooks.length" class="dashboard-book-list">
          <div v-for="book in recentBooks" :key="book.id" class="dashboard-book-row">
            <span class="dashboard-book-cover">
              <img v-if="book.portada_thumbnail_url || book.portada_url" :src="book.portada_thumbnail_url || book.portada_url" :alt="`Portada de ${book.titulo}`" loading="lazy" />
              <BookOpen v-else :size="17" />
            </span>
            <span class="dashboard-book-copy">
              <strong>{{ book.titulo }}</strong>
              <small>{{ book.autor?.nombre || 'Autor no disponible' }} · {{ book.anio_publicacion }}</small>
            </span>
          </div>
        </div>
        <div v-else class="collection-placeholder">
          <div class="shelf-illustration" aria-hidden="true">
            <span class="shelf-book shelf-book-one"></span><span class="shelf-book shelf-book-two"></span>
            <span class="shelf-book shelf-book-three"></span><span class="shelf-book shelf-book-four"></span>
            <span class="shelf-line"></span>
          </div>
          <strong>{{ booksError || 'No hay libros para mostrar' }}</strong>
          <p>Los títulos provienen del catálogo real.</p>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ArrowLeftRight,
  BookOpen,
  BookOpenCheck,
  CalendarDays,
  ClipboardList,
  Clock3,
  LibraryBig,
  LoaderCircle,
  Plus,
  RefreshCw,
  UsersRound,
} from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import { getApiErrorMessage } from '../services/api'
import { librosService } from '../services/libros.service'
import { prestamosService } from '../services/prestamos.service'
import { reportesService } from '../services/reportes.service'
import { sociosService } from '../services/socios.service'
import { authStore } from '../stores/auth'
import { formatCurrency, formatDate } from '../utils/format'

const today = new Intl.DateTimeFormat('es-CO', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
}).format(new Date())
const isMember = computed(() => authStore.user?.rol === 'socio')
const loading = ref(false)
const booksLoading = ref(false)
const activityLoading = ref(false)
const loadError = ref('')
const activityError = ref('')
const booksError = ref('')
const summary = ref(null)
const memberProfile = ref(null)
const memberActiveLoans = ref(null)
const memberOverdueLoans = ref(null)
const memberFines = ref(null)
const memberLoans = ref([])
const latestLoans = ref([])
const recentBooks = ref([])
const stats = computed(() => {
  if (isMember.value) {
    return [
      {
        title: 'Estado de afiliación',
        description: 'Estado de tu cuenta de socio',
        kicker: 'COMUNIDAD',
        source: 'Socios · mi perfil',
        icon: UsersRound,
        tone: 'tone-violet',
        value: memberProfile.value ? (memberProfile.value.activo ? 'Activo' : 'Inactivo') : '—',
      },
      {
        title: 'Préstamos activos',
        description: 'Lecturas en circulación',
        kicker: 'CIRCULACIÓN',
        source: 'Socios · mis préstamos',
        icon: ArrowLeftRight,
        tone: 'tone-lavender',
        value: memberActiveLoans.value?.total ?? '—',
      },
      {
        title: 'Préstamos vencidos',
        description: 'Revisa las fechas límite',
        kicker: 'SEGUIMIENTO',
        source: 'Socios · mis préstamos',
        icon: Clock3,
        tone: 'tone-navy',
        value: memberOverdueLoans.value?.total ?? '—',
      },
      {
        title: 'Multas pendientes',
        description: 'Total de multas no pagadas',
        kicker: 'CUENTA',
        source: 'Socios · mis multas',
        icon: UsersRound,
        tone: 'tone-violet',
        value: memberFines.value ? formatCurrency(memberFines.value.total_adeudado) : '—',
      },
    ]
  }
  return [
    { title: 'Libros en colección', description: 'Títulos registrados', kicker: 'CATÁLOGO', source: 'Reportes · resumen', icon: BookOpen, tone: 'tone-violet', value: summary.value?.total_libros ?? '—' },
    { title: 'Préstamos activos', description: 'Lecturas en circulación', kicker: 'CIRCULACIÓN', source: 'Reportes · resumen', icon: ArrowLeftRight, tone: 'tone-lavender', value: summary.value?.total_prestados ?? '—' },
    { title: 'Socios activos', description: 'Comunidad lectora', kicker: 'COMUNIDAD', source: 'Reportes · resumen', icon: UsersRound, tone: 'tone-navy', value: summary.value?.total_socios_activos ?? '—' },
    { title: 'Préstamos vencidos', description: 'Para revisar con cuidado', kicker: 'SEGUIMIENTO', source: 'Reportes · resumen', icon: Clock3, tone: 'tone-violet', value: summary.value?.total_vencidos ?? '—' },
  ]
})

onMounted(load)

async function load() {
  loading.value = true
  booksLoading.value = true
  activityLoading.value = true
  loadError.value = ''
  activityError.value = ''
  booksError.value = ''

  const booksRequest = librosService.list({ skip: 0, limit: 4, orden: '-anio' })
    .then((page) => { recentBooks.value = page.items })
    .catch((error) => { booksError.value = getApiErrorMessage(error, 'No se pudieron cargar los libros.') })
    .finally(() => { booksLoading.value = false })

  const summaryRequest = isMember.value
    ? Promise.all([
        sociosService.me(),
        sociosService.loansForMe({ estado: 'activo', skip: 0, limit: 1 }),
        sociosService.loansForMe({ estado: 'vencido', skip: 0, limit: 1 }),
        sociosService.finesForMe({ skip: 0, limit: 1 }),
      ]).then(([profile, active, overdue, fines]) => {
        memberProfile.value = profile
        memberActiveLoans.value = active
        memberOverdueLoans.value = overdue
        memberFines.value = fines
      })
    : reportesService.summary().then((data) => { summary.value = data })

  const activityRequest = isMember.value
    ? sociosService.loansForMe({ estado: 'activo', skip: 0, limit: 5 })
      .then((page) => { memberLoans.value = page.items })
    : prestamosService.list({ skip: 0, limit: 5 })
      .then(async (firstPage) => {
        const page = firstPage.total > firstPage.items.length
          ? await prestamosService.list({
              skip: firstPage.total - firstPage.items.length,
              limit: 5,
            })
          : firstPage
        latestLoans.value = [...page.items].sort((a, b) => b.id - a.id)
      })

  try {
    const results = await Promise.allSettled([summaryRequest, booksRequest, activityRequest])
    if (results[0].status === 'rejected') {
      loadError.value = getApiErrorMessage(results[0].reason, 'No se pudo cargar el resumen.')
    }
    if (results[2].status === 'rejected') {
      activityError.value = getApiErrorMessage(results[2].reason, 'No se pudieron cargar los préstamos.')
    }
  } finally {
    loading.value = false
    activityLoading.value = false
  }
}
</script>

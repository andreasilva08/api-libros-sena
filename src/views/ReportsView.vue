<template>
  <AppShell>
    <ModuleHeading
      eyebrow="BIBLIOTECA · INDICADORES"
      title="Reportes"
      description="Una lectura clara de la colección, la comunidad y el movimiento de préstamos."
    >
      <template #actions>
        <button class="button button-secondary module-action" type="button" :disabled="loading" @click="load">
          <LoaderCircle v-if="loading" class="loading-icon" :size="16" />
          <RefreshCw v-else :size="16" /> Actualizar
        </button>
      </template>
    </ModuleHeading>

    <p v-if="loadError" class="form-notice module-feedback" role="alert">{{ loadError }}</p>
    <section class="report-summary" aria-label="Resumen de estadísticas" :aria-busy="loading">
      <article v-for="stat in summaryCards" :key="stat.key" class="stat-card report-stat-card">
        <div class="stat-card-top">
          <span class="stat-icon" :class="stat.tone"><component :is="stat.icon" :size="19" /></span>
          <span class="stat-kicker">{{ stat.kicker }}</span>
        </div>
        <div class="stat-value">{{ formatStat(stat.key) }}</div>
        <h3>{{ stat.title }}</h3>
        <p>{{ stat.description }}</p>
        <div class="stat-foot"><span class="stat-foot-line"></span>GET /reportes/resumen · {{ stat.key }}</div>
      </article>
    </section>

    <section class="report-panels" aria-label="Gráficos de reportes">
      <article class="content-card report-chart-card">
        <div class="card-heading">
          <div><span class="card-overline">COLECCIÓN</span><h2>Libros más prestados</h2></div>
          <span class="card-heading-icon"><TrendingUp :size="17" /></span>
        </div>
        <div v-if="loading && !mostBorrowed.length" class="table-loading" role="status"><LoaderCircle class="loading-icon" :size="18" />Cargando reporte…</div>
        <div v-else-if="mostBorrowed.length" class="report-list">
          <div v-for="item in mostBorrowed" :key="`${item.titulo_libro}-${item.nombre_autor}`" class="report-list-row">
            <strong :title="`${item.titulo_libro} · ${item.nombre_autor}`">{{ item.titulo_libro }} · {{ item.nombre_autor }}</strong>
            <span>{{ item.total_prestamos }} préstamos</span>
            <div class="report-bar-track"><span class="report-bar" :style="{ width: barWidth(item.total_prestamos, maxBorrowed) }"></span></div>
          </div>
        </div>
        <div v-else class="chart-empty">
          <span class="empty-illustration"><ChartNoAxesColumn :size="23" /></span>
          <strong>Sin datos para mostrar</strong>
          <p>El reporte devuelve título, autor y total de préstamos.</p>
        </div>
      </article>

      <article class="content-card report-chart-card">
        <div class="card-heading">
          <div><span class="card-overline">CATEGORÍAS</span><h2>Libros por categoría</h2></div>
          <span class="card-heading-icon"><ChartPie :size="17" /></span>
        </div>
        <div v-if="loading && !categoryReport.length" class="table-loading" role="status"><LoaderCircle class="loading-icon" :size="18" />Cargando reporte…</div>
        <div v-else-if="categoryReport.length" class="report-list">
          <div v-for="item in categoryReport" :key="item.nombre_categoria" class="report-list-row">
            <strong>{{ item.nombre_categoria }}</strong><span>{{ item.total_libros }} libros</span>
            <div class="report-bar-track"><span class="report-bar" :style="{ width: barWidth(item.total_libros, maxCategory) }"></span></div>
          </div>
        </div>
        <div v-else class="chart-empty">
          <span class="empty-illustration"><ChartPie :size="23" /></span>
          <strong>Sin categorías reportadas</strong>
          <p>La distribución procede del reporte de categorías.</p>
        </div>
      </article>

      <article class="content-card report-chart-card report-wide-card">
        <div class="card-heading">
          <div><span class="card-overline">SEGUIMIENTO</span><h2>Préstamos y multas</h2></div>
          <span class="card-heading-icon"><ArrowLeftRight :size="17" /></span>
        </div>
        <div class="report-links">
          <div><CalendarDays :size="17" /><span><strong>Préstamos vencidos</strong><small>GET /reportes/prestamos-vencidos</small></span><span class="report-value">{{ overdueLoans.length }}</span></div>
          <div><CircleDollarSign :size="17" /><span><strong>Socios con multas</strong><small>GET /reportes/socios-con-multas</small></span><span class="report-value">{{ membersWithFines.length }}</span></div>
          <div><Feather :size="17" /><span><strong>Autores reportados</strong><small>GET /reportes/autores</small></span><span class="report-value">{{ authorReport.length }}</span></div>
        </div>
        <div v-if="overdueLoans.length" class="report-list">
          <div v-for="loan in overdueLoans" :key="loan.prestamo_id" class="report-list-row">
            <strong>{{ loan.titulo_libro }} · {{ loan.nombre_socio }}</strong>
            <span>{{ loan.dias_retraso }} días de retraso</span>
          </div>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  ArrowLeftRight,
  BookOpen,
  CalendarDays,
  ChartNoAxesColumn,
  ChartPie,
  CircleDollarSign,
  Feather,
  LoaderCircle,
  RefreshCw,
  TrendingUp,
  UsersRound,
} from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import { getApiErrorMessage } from '../services/api'
import { reportesService } from '../services/reportes.service'
import { formatCurrency } from '../utils/format'

const loading = ref(false)
const loadError = ref('')
const summary = ref(null)
const mostBorrowed = ref([])
const categoryReport = ref([])
const overdueLoans = ref([])
const membersWithFines = ref([])
const authorReport = ref([])
const summaryCards = [
  { key: 'total_libros', title: 'Libros registrados', description: 'Títulos en catálogo', kicker: 'COLECCIÓN', icon: BookOpen, tone: 'tone-violet' },
  { key: 'total_ejemplares', title: 'Ejemplares', description: 'Copias registradas', kicker: 'INVENTARIO', icon: BookOpen, tone: 'tone-lavender' },
  { key: 'total_prestados', title: 'En préstamo', description: 'Ejemplares prestados', kicker: 'CIRCULACIÓN', icon: ArrowLeftRight, tone: 'tone-navy' },
  { key: 'total_socios_activos', title: 'Socios activos', description: 'Comunidad afiliada', kicker: 'COMUNIDAD', icon: UsersRound, tone: 'tone-violet' },
  { key: 'total_vencidos', title: 'Vencidos', description: 'Préstamos fuera de fecha', kicker: 'SEGUIMIENTO', icon: CalendarDays, tone: 'tone-lavender' },
  { key: 'total_multas_recaudadas', title: 'Multas registradas', description: 'Total de multas en préstamos', kicker: 'MULTAS', icon: CircleDollarSign, tone: 'tone-navy' },
]
const maxBorrowed = computed(() => Math.max(0, ...mostBorrowed.value.map((item) => item.total_prestamos)))
const maxCategory = computed(() => Math.max(0, ...categoryReport.value.map((item) => item.total_libros)))

onMounted(load)

async function load() {
  loading.value = true
  loadError.value = ''
  const requests = [
    reportesService.summary(),
    reportesService.mostBorrowedBooks({ limite: 5 }),
    reportesService.categories(),
    reportesService.overdueLoans(),
    reportesService.membersWithFines(),
    reportesService.authors(),
  ]
  const results = await Promise.allSettled(requests)
  const setters = [
    (value) => { summary.value = value },
    (value) => { mostBorrowed.value = value },
    (value) => { categoryReport.value = value },
    (value) => { overdueLoans.value = value },
    (value) => { membersWithFines.value = value },
    (value) => { authorReport.value = value },
  ]
  const failures = []
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') setters[index](result.value)
    else failures.push(getApiErrorMessage(result.reason, 'No se pudo cargar un reporte.'))
  })
  if (failures.length) loadError.value = [...new Set(failures)].join(' ')
  loading.value = false
}

function formatStat(key) {
  const value = summary.value?.[key]
  return value === undefined ? '—' : key === 'total_multas_recaudadas' ? formatCurrency(value) : value
}

function barWidth(value, maximum) {
  if (!maximum) return '0%'
  return `${Math.max(3, (Number(value) / maximum) * 100)}%`
}
</script>

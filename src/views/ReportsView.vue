<template>
  <AppShell>
    <ModuleHeading
      eyebrow="BIBLIOTECA · INDICADORES"
      title="Reportes"
      description="Una lectura clara de la colección, la comunidad y el movimiento de préstamos."
    >
      <template #actions>
        <span class="report-source"><span></span> Indicadores desde API</span>
      </template>
    </ModuleHeading>

    <section class="report-summary" aria-label="Resumen de estadísticas">
      <article v-for="stat in summary" :key="stat.key" class="stat-card report-stat-card">
        <div class="stat-card-top">
          <span class="stat-icon" :class="stat.tone"><component :is="stat.icon" :size="19" /></span>
          <span class="stat-kicker">{{ stat.kicker }}</span>
        </div>
        <div class="stat-value">—</div>
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
        <div class="chart-empty">
          <span class="empty-illustration"><ChartNoAxesColumn :size="23" /></span>
          <strong>El gráfico aparecerá con los datos del reporte</strong>
          <p>La API devuelve título, autor y total de préstamos.</p>
          <span class="report-endpoint">GET /reportes/libros-mas-prestados</span>
        </div>
      </article>
      <article class="content-card report-chart-card">
        <div class="card-heading">
          <div><span class="card-overline">CATEGORÍAS</span><h2>Libros por categoría</h2></div>
          <span class="card-heading-icon"><Tags :size="17" /></span>
        </div>
        <div class="chart-empty">
          <span class="empty-illustration"><ChartPie :size="23" /></span>
          <strong>Distribución pendiente de datos reales</strong>
          <p>Las categorías se mostrarán al conectar el reporte.</p>
          <span class="report-endpoint">GET /reportes/categorias</span>
        </div>
      </article>
      <article class="content-card report-chart-card report-wide-card">
        <div class="card-heading">
          <div><span class="card-overline">SEGUIMIENTO</span><h2>Préstamos y multas</h2></div>
          <span class="card-heading-icon"><ArrowLeftRight :size="17" /></span>
        </div>
        <div class="report-links">
          <div><CalendarDays :size="17" /><span><strong>Préstamos vencidos</strong><small>GET /reportes/prestamos-vencidos</small></span><span class="report-value">—</span></div>
          <div><CircleDollarSign :size="17" /><span><strong>Socios con multas</strong><small>GET /reportes/socios-con-multas</small></span><span class="report-value">—</span></div>
          <div><Feather :size="17" /><span><strong>Actividad por autor</strong><small>GET /reportes/autores</small></span><span class="report-value">—</span></div>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup>
import {
  ArrowLeftRight,
  BookOpen,
  CalendarDays,
  ChartNoAxesColumn,
  ChartPie,
  CircleDollarSign,
  Feather,
  Tags,
  TrendingUp,
  UsersRound,
} from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'

const summary = [
  { key: 'total_libros', title: 'Libros registrados', description: 'Títulos en catálogo', kicker: 'COLECCIÓN', icon: BookOpen, tone: 'tone-violet' },
  { key: 'total_ejemplares', title: 'Ejemplares', description: 'Copias registradas', kicker: 'INVENTARIO', icon: BookOpen, tone: 'tone-lavender' },
  { key: 'total_prestados', title: 'En préstamo', description: 'Ejemplares prestados', kicker: 'CIRCULACIÓN', icon: ArrowLeftRight, tone: 'tone-navy' },
  { key: 'total_socios_activos', title: 'Socios activos', description: 'Comunidad afiliada', kicker: 'COMUNIDAD', icon: UsersRound, tone: 'tone-violet' },
  { key: 'total_vencidos', title: 'Vencidos', description: 'Préstamos fuera de fecha', kicker: 'SEGUIMIENTO', icon: CalendarDays, tone: 'tone-lavender' },
  { key: 'total_multas_recaudadas', title: 'Multas recaudadas', description: 'Total reportado', kicker: 'RECAUDO', icon: CircleDollarSign, tone: 'tone-navy' },
]
</script>

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
      <div><h2>Vista general</h2><p>Indicadores que se cargarán desde los reportes de la API.</p></div>
      <span class="data-source"><span></span> Fuente prevista: API</span>
    </div>

    <section class="stats-grid" aria-label="Indicadores de biblioteca">
      <article v-for="stat in stats" :key="stat.title" class="stat-card">
        <div class="stat-card-top">
          <span class="stat-icon" :class="stat.tone"><component :is="stat.icon" :size="19" /></span>
          <span class="stat-kicker">{{ stat.kicker }}</span>
        </div>
        <div class="stat-value">—</div>
        <h3>{{ stat.title }}</h3>
        <p>{{ stat.description }}</p>
        <div class="stat-foot"><span class="stat-foot-line"></span>{{ stat.source }}</div>
      </article>
    </section>

    <section class="lower-grid">
      <article class="content-card activity-card">
        <div class="card-heading">
          <div><span class="card-overline">MOVIMIENTO</span><h2>Actividad reciente</h2></div>
          <span class="card-heading-icon"><Clock3 :size="17" /></span>
        </div>
        <div class="empty-state">
          <span class="empty-illustration"><BookOpenCheck :size="24" /></span>
          <strong>Las historias empiezan aquí</strong>
          <p>La actividad aparecerá cuando la API esté conectada y haya datos disponibles.</p>
        </div>
      </article>

      <article class="content-card reading-card">
        <div class="card-heading">
          <div><span class="card-overline">COLECCIÓN</span><h2>En los estantes</h2></div>
          <span class="card-heading-icon"><LibraryBig :size="17" /></span>
        </div>
        <div class="collection-placeholder">
          <div class="shelf-illustration" aria-hidden="true">
            <span class="shelf-book shelf-book-one"></span><span class="shelf-book shelf-book-two"></span>
            <span class="shelf-book shelf-book-three"></span><span class="shelf-book shelf-book-four"></span>
            <span class="shelf-line"></span>
          </div>
          <strong>Tu colección, a un clic</strong>
          <p>Los libros recientes se mostrarán aquí al conectar el catálogo.</p>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup>
import AppShell from '../components/layout/AppShell.vue'
import {
  ArrowLeftRight,
  BookOpen,
  BookOpenCheck,
  CalendarDays,
  Clock3,
  LibraryBig,
  UsersRound,
} from '@lucide/vue'

const today = new Intl.DateTimeFormat('es-CO', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
}).format(new Date())

const stats = [
  {
    title: 'Libros en colección',
    description: 'Títulos registrados',
    kicker: 'CATÁLOGO',
    source: 'Reportes · resumen',
    icon: BookOpen,
    tone: 'tone-violet',
  },
  {
    title: 'Préstamos activos',
    description: 'Lecturas en circulación',
    kicker: 'CIRCULACIÓN',
    source: 'Reportes · resumen',
    icon: ArrowLeftRight,
    tone: 'tone-lavender',
  },
  {
    title: 'Socios activos',
    description: 'Comunidad lectora',
    kicker: 'COMUNIDAD',
    source: 'Reportes · resumen',
    icon: UsersRound,
    tone: 'tone-navy',
  },
  {
    title: 'Préstamos vencidos',
    description: 'Para revisar con cuidado',
    kicker: 'SEGUIMIENTO',
    source: 'Reportes · resumen',
    icon: Clock3,
    tone: 'tone-violet',
  },
]
</script>

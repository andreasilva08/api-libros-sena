<template>
  <main class="dashboard-shell">
    <aside class="sidebar" :class="{ 'sidebar-open': menuOpen }">
      <RouterLink class="brand sidebar-brand" to="/preview" aria-label="Biblioteca Segura, resumen">
        <span class="brand-mark"><BookOpenCheck :size="22" :stroke-width="1.8" /></span>
        <span class="brand-name">biblioteca<span>segura</span></span>
      </RouterLink>

      <div class="sidebar-label">ESPACIO DE TRABAJO</div>
      <nav class="side-nav" aria-label="Navegación principal">
        <template v-for="item in navItems" :key="item.route">
        <button v-if="item.disabled" class="nav-item nav-item-disabled" type="button" disabled>
          <component :is="item.icon" :size="18" /><span>{{ item.label }}</span>
        </button>
        <RouterLink
          v-else
          :to="item.to"
          class="nav-item"
          :class="{ 'nav-item-active': route.name === item.route }"
          @click="menuOpen = false"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
          <span v-if="route.name === item.route" class="nav-active-mark"></span>
        </RouterLink>
        </template>
      </nav>

      <div class="sidebar-bottom">
        <div class="sidebar-book-note">
          <span class="note-icon"><Sparkles :size="15" /></span>
          <p>Un buen libro siempre encuentra su lector.</p>
          <span class="note-caption">BIBLIOTECA SEGURA</span>
        </div>
        <RouterLink to="/" class="sidebar-signout"><LogIn :size="16" /> Volver al acceso</RouterLink>
      </div>
    </aside>

    <div v-if="menuOpen" class="mobile-scrim" @click="menuOpen = false"></div>

    <section class="dashboard-main">
      <header class="topbar">
        <button
          class="icon-button mobile-menu-button"
          type="button"
          :aria-label="menuOpen ? 'Cerrar menú' : 'Abrir menú'"
          @click="menuOpen = !menuOpen"
        ><Menu v-if="!menuOpen" :size="20" /><X v-else :size="20" /></button>
        <div class="breadcrumb"><span>Biblioteca</span><ChevronRight :size="14" /><strong>{{ pageTitle }}</strong></div>
        <div class="topbar-right">
          <span class="preview-pill"><span></span> Modo vista previa</span>
          <div class="topbar-divider"></div>
          <div class="profile-placeholder">
            <span class="avatar"><UserRound :size="17" /></span>
            <span class="profile-copy"><strong>Sin sesión</strong><small>Propuesta visual</small></span>
          </div>
        </div>
      </header>

      <div class="dashboard-content">
        <div class="preview-banner">
          <span class="banner-icon"><Eye :size="17" /></span>
          <div><strong>Estás viendo una propuesta de diseño</strong><p>Sin sesión activa y sin datos ficticios. El contenido se conectará a la API después.</p></div>
          <RouterLink to="/" class="banner-link">Volver al acceso <ArrowUpRight :size="14" /></RouterLink>
        </div>
        <slot />
        <footer class="dashboard-footer"><span>Biblioteca Segura</span><span>Propuesta visual · Datos reales al conectar la API</span></footer>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  ArrowLeftRight,
  ArrowUpRight,
  BookOpen,
  BookOpenCheck,
  ChartNoAxesColumn,
  ChevronRight,
  Eye,
  Feather,
  LayoutDashboard,
  LogIn,
  Menu,
  Sparkles,
  Tags,
  UserRound,
  UserRoundCog,
  UsersRound,
  X,
} from '@lucide/vue'

const route = useRoute()
const menuOpen = ref(false)
const navItems = [
  { label: 'Resumen', route: 'dashboard-preview', to: '/preview', icon: LayoutDashboard },
  { label: 'Libros', route: 'books-preview', to: '/preview/libros', icon: BookOpen },
  { label: 'Autores', route: 'authors-preview', to: '/preview/autores', icon: Feather },
  { label: 'Categorías', route: 'categories-disabled', icon: Tags, disabled: true },
  { label: 'Socios', route: 'members-preview', to: '/preview/socios', icon: UsersRound },
  { label: 'Préstamos', route: 'loans-preview', to: '/preview/prestamos', icon: ArrowLeftRight },
  { label: 'Usuarios', route: 'users-preview', to: '/preview/usuarios', icon: UserRoundCog },
  { label: 'Reportes', route: 'reports-preview', to: '/preview/reportes', icon: ChartNoAxesColumn },
]
const pageTitle = computed(() => route.meta.title || 'Resumen')
</script>

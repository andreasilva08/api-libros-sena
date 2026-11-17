<template>
  <main class="dashboard-shell">
    <aside class="sidebar" :class="{ 'sidebar-open': menuOpen }">
      <RouterLink class="brand sidebar-brand" to="/dashboard" aria-label="Biblioteca Segura, resumen">
        <span class="brand-mark"><BookOpenCheck :size="22" :stroke-width="1.8" /></span>
        <span class="brand-name">biblioteca<span>segura</span></span>
      </RouterLink>

      <div class="sidebar-label">ESPACIO DE TRABAJO</div>
      <nav class="side-nav" aria-label="Navegación principal">
        <RouterLink
          v-for="item in visibleNavItems"
          :key="item.route"
          :to="item.to"
          class="nav-item"
          :class="{ 'nav-item-active': route.name === item.route }"
          @click="menuOpen = false"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
          <span v-if="route.name === item.route" class="nav-active-mark"></span>
        </RouterLink>
      </nav>

      <div class="sidebar-bottom">
        <div class="sidebar-book-note">
          <span class="note-icon"><Sparkles :size="15" /></span>
          <p>Un buen libro siempre encuentra su lector.</p>
          <span class="note-caption">BIBLIOTECA SEGURA</span>
        </div>
        <button class="sidebar-signout" type="button" :disabled="signingOut" @click="signOut">
          <LoaderCircle v-if="signingOut" class="loading-icon" :size="16" />
          <LogOut v-else :size="16" /> {{ signingOut ? 'Cerrando sesión…' : 'Cerrar sesión' }}
        </button>
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
          <span class="preview-pill"><span></span> Sesión activa</span>
          <div class="topbar-divider"></div>
          <div class="profile-placeholder">
            <span class="avatar"><UserRound :size="17" /></span>
            <span class="profile-copy"><strong>{{ authStore.user?.nombre || authStore.user?.email }}</strong><small>{{ roleLabel }}</small></span>
          </div>
        </div>
      </header>

      <div class="dashboard-content">
        <slot />
        <footer class="dashboard-footer"><span>Biblioteca Segura</span><span>Información sincronizada con la API</span></footer>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { authStore } from '../../stores/auth'
import {
  ArrowLeftRight,
  BookOpen,
  BookOpenCheck,
  ChartNoAxesColumn,
  ChevronRight,
  Feather,
  LayoutDashboard,
  LoaderCircle,
  LogOut,
  Menu,
  Sparkles,
  Tags,
  UserRound,
  UserRoundCog,
  UsersRound,
  X,
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
const signingOut = ref(false)
const navItems = [
  { label: 'Resumen', route: 'dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Libros', route: 'books', to: '/libros', icon: BookOpen },
  { label: 'Autores', route: 'authors', to: '/autores', icon: Feather },
  { label: 'Categorías', route: 'categories', to: '/categorias', icon: Tags },
  { label: 'Socios', route: 'members', to: '/socios', icon: UsersRound },
  { label: 'Préstamos', route: 'loans', to: '/prestamos', icon: ArrowLeftRight },
  { label: 'Usuarios', route: 'users', to: '/usuarios', icon: UserRoundCog, roles: ['admin'] },
  { label: 'Reportes', route: 'reports', to: '/reportes', icon: ChartNoAxesColumn, roles: ['admin', 'bibliotecario'] },
]
const pageTitle = computed(() => route.meta.title || 'Resumen')
const visibleNavItems = computed(() => navItems.filter(
  (item) => !item.roles || item.roles.includes(authStore.user?.rol),
))
const roleLabel = computed(() => ({
  admin: 'Administración',
  bibliotecario: 'Bibliotecario',
  socio: 'Socio',
}[authStore.user?.rol] || 'Sesión'))

async function signOut() {
  if (signingOut.value) return
  signingOut.value = true
  try {
    await authStore.logout()
    await router.replace({ name: 'login' })
  } catch {
    await router.replace({ name: 'login', query: { logout: 'pending' } })
  } finally {
    signingOut.value = false
  }
}
</script>

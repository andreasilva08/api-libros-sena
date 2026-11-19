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
          <span class="nav-item-label">{{ item.label }}</span>
          <span
            v-if="item.route === 'requests' && pendingRequestCount > 0"
            class="requests-count"
            :aria-label="`${pendingRequestCount} solicitudes pendientes`"
          >{{ pendingRequestCount }}</span>
          <span v-if="route.name === item.route" class="nav-active-mark"></span>
        </RouterLink>
      </nav>
      <p v-if="pendingRequestsError" class="sidebar-nav-error" role="status">
        {{ pendingRequestsError }}
      </p>

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
          <span class="role-badge" :class="`role-badge-${authStore.user?.rol}`">{{ roleLabel }}</span>
          <div class="topbar-divider"></div>
          <div class="profile-placeholder">
            <span class="avatar"><UserRound :size="17" /></span>
            <span class="profile-copy"><strong>{{ authStore.user?.nombre || authStore.user?.email }}</strong><small>Cuenta activa</small></span>
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { authStore } from '../../stores/auth'
import { getApiErrorMessage } from '../../services/api'
import { solicitudesService } from '../../services/solicitudes.service'
import {
  ArrowLeftRight,
  BookOpen,
  BookOpenCheck,
  ChartNoAxesColumn,
  ChevronRight,
  ClipboardList,
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
const pendingRequestCount = ref(0)
const pendingRequestsError = ref('')
const navItems = [
  { label: 'Resumen', route: 'dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Libros', route: 'books', to: '/libros', icon: BookOpen },
  { label: 'Autores', route: 'authors', to: '/autores', icon: Feather },
  { label: 'Categorías', route: 'categories', to: '/categorias', icon: Tags },
  { label: 'Socios', route: 'members', to: '/socios', icon: UsersRound },
  { label: 'Préstamos', route: 'loans', to: '/prestamos', icon: ArrowLeftRight },
  { label: 'Usuarios', route: 'users', to: '/usuarios', icon: UserRoundCog, roles: ['admin'] },
  { label: 'Solicitudes', route: 'requests', to: '/solicitudes', icon: ClipboardList, roles: ['admin', 'bibliotecario'] },
  { label: 'Reportes', route: 'reports', to: '/reportes', icon: ChartNoAxesColumn, roles: ['admin', 'bibliotecario'] },
]
const pageTitle = computed(() => (
  authStore.user?.rol === 'socio' && route.name === 'members'
    ? 'Mi perfil'
    : route.meta.title || 'Resumen'
))
const visibleNavItems = computed(() => {
  const role = authStore.user?.rol
  const memberLabels = {
    dashboard: 'Mi Resumen',
    books: 'Catálogo',
    loans: 'Mis Préstamos',
    members: 'Mi Perfil',
  }
  const memberRoutes = Object.keys(memberLabels)
  return navItems
    .filter((item) => role === 'socio'
      ? memberRoutes.includes(item.route)
      : !item.roles || item.roles.includes(role))
    .map((item) => ({
      ...item,
      label: role === 'socio' ? memberLabels[item.route] : item.label,
    }))
})
const roleLabel = computed(() => ({
  admin: 'Administrador',
  bibliotecario: 'Bibliotecario',
  socio: 'Socio',
}[authStore.user?.rol] || 'Sesión'))

onMounted(() => {
  loadPendingRequests()
  window.addEventListener('biblioteca:requests-updated', loadPendingRequests)
})
onBeforeUnmount(() => {
  window.removeEventListener('biblioteca:requests-updated', loadPendingRequests)
})

async function loadPendingRequests() {
  if (!authStore.isStaff) return
  pendingRequestsError.value = ''
  try {
    const page = await solicitudesService.list({
      estado: 'pendiente',
      skip: 0,
      limit: 1,
    })
    pendingRequestCount.value = page.total
  } catch (error) {
    pendingRequestsError.value = getApiErrorMessage(
      error,
      'No se pudo consultar el número de solicitudes pendientes.',
    )
  }
}

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

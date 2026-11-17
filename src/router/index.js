import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../stores/auth'
import { getAccessToken } from '../services/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardPreview.vue'),
      meta: { title: 'Resumen', requiresAuth: true },
    },
    {
      path: '/libros',
      name: 'books',
      component: () => import('../views/BooksView.vue'),
      meta: { title: 'Libros', requiresAuth: true },
    },
    {
      path: '/autores',
      name: 'authors',
      component: () => import('../views/AuthorsView.vue'),
      meta: { title: 'Autores', requiresAuth: true },
    },
    {
      path: '/categorias',
      name: 'categories',
      component: () => import('../views/CategoriesView.vue'),
      meta: { title: 'Categorías', requiresAuth: true },
    },
    {
      path: '/socios',
      name: 'members',
      component: () => import('../views/MembersView.vue'),
      meta: { title: 'Socios', requiresAuth: true },
    },
    {
      path: '/prestamos',
      name: 'loans',
      component: () => import('../views/LoansView.vue'),
      meta: { title: 'Préstamos', requiresAuth: true },
    },
    {
      path: '/usuarios',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { title: 'Usuarios', requiresAuth: true, roles: ['admin'] },
    },
    {
      path: '/reportes',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { title: 'Reportes', requiresAuth: true, roles: ['admin', 'bibliotecario'] },
    },
    { path: '/preview', redirect: { name: 'dashboard' } },
    { path: '/preview/libros', redirect: { name: 'books' } },
    { path: '/preview/autores', redirect: { name: 'authors' } },
    { path: '/preview/socios', redirect: { name: 'members' } },
    { path: '/preview/prestamos', redirect: { name: 'loans' } },
    { path: '/preview/usuarios', redirect: { name: 'users' } },
    { path: '/preview/reportes', redirect: { name: 'reports' } },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (!to.meta.requiresAuth) return true

  if (!getAccessToken()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  try {
    await authStore.loadUser()
  } catch {
    authStore.clearUser()
    return { name: 'login', query: { expired: '1' } }
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.user?.rol)) {
    return { name: 'dashboard', query: { forbidden: '1' } }
  }

  return true
})

export default router

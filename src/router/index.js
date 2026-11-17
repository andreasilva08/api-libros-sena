import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/preview',
      name: 'dashboard-preview',
      component: () => import('../views/DashboardPreview.vue'),
      meta: { title: 'Resumen' },
    },
    {
      path: '/preview/libros',
      name: 'books-preview',
      component: () => import('../views/BooksView.vue'),
      meta: { title: 'Libros' },
    },
    {
      path: '/preview/autores',
      name: 'authors-preview',
      component: () => import('../views/AuthorsView.vue'),
      meta: { title: 'Autores' },
    },
    {
      path: '/preview/socios',
      name: 'members-preview',
      component: () => import('../views/MembersView.vue'),
      meta: { title: 'Socios' },
    },
    {
      path: '/preview/prestamos',
      name: 'loans-preview',
      component: () => import('../views/LoansView.vue'),
      meta: { title: 'Préstamos' },
    },
    {
      path: '/preview/usuarios',
      name: 'users-preview',
      component: () => import('../views/UsersView.vue'),
      meta: { title: 'Usuarios' },
    },
    {
      path: '/preview/reportes',
      name: 'reports-preview',
      component: () => import('../views/ReportsView.vue'),
      meta: { title: 'Reportes' },
    },
  ],
})

export default router

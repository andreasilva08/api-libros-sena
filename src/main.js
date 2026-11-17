import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { authStore } from './stores/auth'
import './styles.css'
import './module-styles.css'

window.addEventListener('biblioteca:session-expired', (event) => {
  authStore.clearUser()
  if (router.currentRoute.value.meta.requiresAuth) {
    const query = event.detail?.status === 403 ? { forbidden: '1' } : { expired: '1' }
    router.replace({ name: 'login', query })
  }
})

createApp(App).use(router).mount('#app')

<template>
  <main class="login-page">
    <section class="login-story" aria-label="Biblioteca Segura">
      <RouterLink class="brand brand-on-dark" to="/" aria-label="Biblioteca Segura, inicio">
        <span class="brand-mark"><BookOpenCheck :size="23" :stroke-width="1.8" /></span>
        <span class="brand-name">biblioteca<span>segura</span></span>
      </RouterLink>

      <div class="story-content">
        <div class="eyebrow eyebrow-on-dark"><span class="eyebrow-line"></span> Un espacio para descubrir</div>
        <h1>Cada libro<br />abre un <em>camino.</em></h1>
        <p>Un lugar tranquilo para cuidar historias, acompañar lectores y mantener cada préstamo en orden.</p>

        <div class="story-illustration" aria-hidden="true">
          <div class="orbit orbit-one"></div>
          <div class="orbit orbit-two"></div>
          <div class="book-stack">
            <div class="book book-back"></div>
            <div class="book book-mid"></div>
            <div class="book book-front"><span></span><i></i></div>
            <div class="book-pages"></div>
          </div>
          <span class="spark spark-one">✳</span>
          <span class="spark spark-two">✦</span>
          <span class="story-note">un capítulo<br />a la vez</span>
        </div>
      </div>

      <div class="story-footer">
        <span class="footer-dot"></span>
        <span>Gestión cercana. Lecturas sin límites.</span>
      </div>
    </section>

    <section class="login-panel">
      <div class="login-panel-top">
        <span class="mobile-brand"><BookOpenCheck :size="20" /> Biblioteca Segura</span>
        <span class="secure-label"><ShieldCheck :size="15" /> Acceso seguro</span>
      </div>

      <div class="login-card">
        <div class="welcome-mark"><LibraryBig :size="22" :stroke-width="1.8" /></div>
        <p class="overline">Tu biblioteca, en un solo lugar</p>
        <h2>Qué bueno tenerte<br />de vuelta.</h2>
        <p class="login-intro">Ingresa con tu cuenta para continuar.</p>

        <form class="login-form" @submit.prevent="submitLogin">
          <label for="email">Correo electrónico</label>
          <div class="input-wrap">
            <Mail :size="17" aria-hidden="true" />
            <input
              id="email"
              v-model.trim="email"
              type="email"
              autocomplete="username"
              placeholder="nombre@biblioteca.com"
              required
            />
          </div>

          <div class="password-label">
            <label for="password">Contraseña</label>
          </div>
          <div class="input-wrap">
            <LockKeyhole :size="17" aria-hidden="true" />
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Ingresa tu contraseña"
              required
            />
            <button
              class="input-action"
              type="button"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" :size="17" />
              <Eye v-else :size="17" />
            </button>
          </div>

          <p v-if="notice" class="form-notice" role="alert">{{ notice }}</p>
          <button class="button button-primary login-submit" type="submit" :disabled="loading">
            <LoaderCircle v-if="loading" class="loading-icon" :size="17" />
            <template v-else>Iniciar sesión <ArrowRight :size="17" /></template>
          </button>
        </form>
        <p class="login-register-prompt">
          ¿Aún no tienes cuenta?
          <RouterLink to="/registro">Crear cuenta</RouterLink>
        </p>
      </div>

      <footer class="login-footer">
        <span>Biblioteca Segura</span>
        <span class="footer-separator">·</span>
        <span>Una experiencia hecha para leer</span>
      </footer>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  BookOpenCheck,
  Eye,
  EyeOff,
  LibraryBig,
  LoaderCircle,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from '@lucide/vue'
import { authStore } from '../stores/auth'
import { getApiErrorMessage } from '../services/api'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const notice = ref('')
const loading = ref(false)
const route = useRoute()
const router = useRouter()

onMounted(() => {
  if (route.query.expired) notice.value = 'Tu sesión venció. Inicia sesión nuevamente.'
  else if (route.query.forbidden) notice.value = 'Tu cuenta no tiene acceso a esa sección.'
  else if (route.query.logout === 'pending') {
    notice.value = 'Se cerró la sesión local, pero no se pudo confirmar su revocación en el servidor.'
  }
})

async function submitLogin() {
  if (loading.value) return
  loading.value = true
  notice.value = ''
  try {
    await authStore.login(email.value, password.value)
    const redirect = route.query.redirect
    const safeRedirect = typeof redirect === 'string'
      && redirect.startsWith('/')
      && !redirect.startsWith('//')
      ? redirect
      : { name: 'dashboard' }
    await router.replace(safeRedirect)
  } catch (error) {
    notice.value = getApiErrorMessage(error, 'No fue posible iniciar sesión.')
  } finally {
    loading.value = false
  }
}
</script>

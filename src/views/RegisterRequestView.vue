<template>
  <main class="login-page">
    <section class="login-story" aria-label="Biblioteca Segura">
      <RouterLink class="brand brand-on-dark" to="/" aria-label="Biblioteca Segura, inicio">
        <span class="brand-mark"><BookOpenCheck :size="23" :stroke-width="1.8" /></span>
        <span class="brand-name">biblioteca<span>segura</span></span>
      </RouterLink>
      <div class="story-content">
        <div class="eyebrow eyebrow-on-dark"><span class="eyebrow-line"></span> Una comunidad para descubrir</div>
        <h1>Tu próxima<br />historia <em>empieza aquí.</em></h1>
        <p>Solicita tu membresía y, cuando la biblioteca la apruebe, podrás consultar tu perfil y tus préstamos.</p>
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
      <div class="story-footer"><span class="footer-dot"></span><span>Gestión cercana. Lecturas sin límites.</span></div>
    </section>

    <section class="login-panel">
      <div class="login-panel-top">
        <span class="mobile-brand"><BookOpenCheck :size="20" /> Biblioteca Segura</span>
        <span class="secure-label"><ShieldCheck :size="15" /> Solicitud segura</span>
      </div>

      <div class="login-card register-card">
        <template v-if="submitted">
          <div class="welcome-mark"><CircleCheck :size="22" :stroke-width="1.8" /></div>
          <p class="overline">Solicitud recibida</p>
          <h2>Revisaremos tu<br />solicitud.</h2>
          <p class="login-intro">Tu cuenta quedará pendiente de aprobación. Podrás iniciar sesión cuando la biblioteca la apruebe.</p>
          <RouterLink class="button button-primary register-submit" to="/">Volver al inicio de sesión</RouterLink>
        </template>
        <template v-else>
          <div class="welcome-mark"><UsersRound :size="22" :stroke-width="1.8" /></div>
          <p class="overline">Únete a la comunidad</p>
          <h2>Solicita tu cuenta.</h2>
          <p class="login-intro">Completa tus datos para que el equipo de la biblioteca revise tu solicitud.</p>

          <form class="login-form" @submit.prevent="submitRequest">
            <label for="request-name">Nombre completo</label>
            <div class="input-wrap">
              <UserRound :size="17" aria-hidden="true" />
              <input id="request-name" v-model.trim="form.nombre" type="text" autocomplete="name" minlength="3" maxlength="100" required />
            </div>

            <label class="register-field-label" for="request-email">Correo electrónico</label>
            <div class="input-wrap">
              <Mail :size="17" aria-hidden="true" />
              <input id="request-email" v-model.trim="form.email" type="email" autocomplete="email" maxlength="100" required />
            </div>

            <label class="register-field-label" for="request-phone">Teléfono <span>(opcional)</span></label>
            <div class="input-wrap">
              <Phone :size="17" aria-hidden="true" />
              <input id="request-phone" v-model.trim="form.telefono" type="tel" autocomplete="tel" maxlength="20" pattern="[0-9 +]{7,15}" />
            </div>

            <label class="register-field-label" for="request-password">Contraseña</label>
            <div class="input-wrap">
              <LockKeyhole :size="17" aria-hidden="true" />
              <input id="request-password" v-model="form.password" type="password" autocomplete="new-password" minlength="8" maxlength="64" pattern="(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,64}" required />
            </div>
            <small class="register-hint">Usa entre 8 y 64 caracteres, con mayúscula, minúscula y número.</small>

            <label class="register-field-label" for="request-confirm-password">Confirmar contraseña</label>
            <div class="input-wrap">
              <LockKeyhole :size="17" aria-hidden="true" />
              <input id="request-confirm-password" v-model="form.confirm_password" type="password" autocomplete="new-password" minlength="8" maxlength="64" required />
            </div>

            <p class="request-privacy-note">
              Usaremos tu nombre, correo y, si lo proporcionas, teléfono para gestionar tu solicitud y validar la membresía. La contraseña se almacenará como hash; la cuenta solo se habilitará si se aprueba.
            </p>
            <p v-if="notice" class="form-notice" role="alert">{{ notice }}</p>
            <button class="button button-primary login-submit" type="submit" :disabled="loading">
              <LoaderCircle v-if="loading" class="loading-icon" :size="17" />
              <template v-else>Enviar solicitud <ArrowRight :size="17" /></template>
            </button>
          </form>
          <p class="login-register-prompt">¿Ya tienes cuenta? <RouterLink to="/">Iniciar sesión</RouterLink></p>
        </template>
      </div>

      <footer class="login-footer"><span>Biblioteca Segura</span><span class="footer-separator">·</span><span>Una experiencia hecha para leer</span></footer>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ArrowRight,
  BookOpenCheck,
  CircleCheck,
  LoaderCircle,
  LockKeyhole,
  Mail,
  Phone,
  ShieldCheck,
  UserRound,
  UsersRound,
} from '@lucide/vue'
import { getApiErrorMessage } from '../services/api'
import { authService } from '../services/auth.service'

const form = reactive({
  nombre: '',
  email: '',
  telefono: '',
  password: '',
  confirm_password: '',
})
const loading = ref(false)
const submitted = ref(false)
const notice = ref('')

async function submitRequest() {
  if (loading.value) return
  loading.value = true
  notice.value = ''
  try {
    await authService.requestAccount({
      nombre: form.nombre,
      email: form.email,
      ...(form.telefono ? { telefono: form.telefono } : {}),
      password: form.password,
      confirm_password: form.confirm_password,
    })
    submitted.value = true
  } catch (error) {
    notice.value = getApiErrorMessage(error, 'No fue posible enviar la solicitud.')
  } finally {
    loading.value = false
  }
}

</script>

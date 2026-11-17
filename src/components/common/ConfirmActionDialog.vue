<template>
  <div v-if="open" class="dialog-overlay" @click.self="$emit('cancel')">
    <section
      class="preview-dialog confirm-dialog"
      role="alertdialog"
      aria-modal="true"
      :aria-labelledby="`${dialogId}-title`"
      :aria-describedby="`${dialogId}-description`"
      @keydown.esc="$emit('cancel')"
    >
      <header class="dialog-heading">
        <span class="confirm-icon"><TriangleAlert :size="19" /></span>
        <button class="dialog-close" type="button" aria-label="Cerrar confirmación" @click="$emit('cancel')">
          <X :size="18" />
        </button>
      </header>
      <h2 :id="`${dialogId}-title`">{{ title }}</h2>
      <p :id="`${dialogId}-description`" class="confirm-description">{{ description }}</p>
      <div class="dialog-preview-note"><Info :size="16" /><p>La confirmación solo continúa si la vista está conectada a una operación disponible.</p></div>
      <footer class="dialog-actions">
        <button class="button button-secondary" type="button" @click="$emit('cancel')">{{ cancelLabel }}</button>
        <button class="button button-primary" type="button" :disabled="!enabled" @click="$emit('confirm')">{{ confirmLabel }}</button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { Info, TriangleAlert, X } from '@lucide/vue'

defineProps({
  open: { type: Boolean, default: false },
  dialogId: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  enabled: { type: Boolean, default: false },
})

defineEmits(['confirm', 'cancel'])
</script>

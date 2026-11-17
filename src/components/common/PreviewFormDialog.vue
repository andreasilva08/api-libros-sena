<template>
  <div v-if="open" class="dialog-overlay" @click.self="$emit('close')">
    <section
      class="preview-dialog"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`${dialogId}-title`"
      @keydown.esc="$emit('close')"
    >
      <header class="dialog-heading">
        <div>
          <span class="card-overline">FORMULARIO DE {{ moduleName.toUpperCase() }}</span>
          <h2 :id="`${dialogId}-title`">{{ activeMode.title }}</h2>
        </div>
        <button class="dialog-close" type="button" aria-label="Cerrar formulario" @click="$emit('close')">
          <X :size="18" />
        </button>
      </header>

      <div v-if="modes.length > 1" class="dialog-mode-tabs" role="tablist" :aria-label="`Acciones de ${moduleName}`">
        <button
          v-for="mode in modes"
          :key="mode.key"
          type="button"
          role="tab"
          :aria-selected="selectedMode === mode.key"
          :class="{ 'dialog-mode-active': selectedMode === mode.key }"
          @click="selectedMode = mode.key"
        >{{ mode.label }}</button>
      </div>

      <p v-if="activeMode.note" class="dialog-mode-note"><Info :size="15" />{{ activeMode.note }}</p>

      <form class="preview-form" @submit.prevent>
        <label v-for="field in activeMode.fields" :key="field.name" class="preview-field">
          <span>{{ field.label }}<span v-if="field.required" class="required-mark"> *</span></span>
          <select v-if="field.type === 'select'" :required="field.required">
            <option value="" selected>{{ field.placeholder || 'Selecciona una opción' }}</option>
            <option v-for="option in field.options" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
          <textarea
            v-else-if="field.type === 'textarea'"
            :name="field.name"
            :placeholder="field.placeholder"
            :required="field.required"
            :rows="field.rows || 3"
          ></textarea>
          <input
            v-else
            :name="field.name"
            :type="field.type || 'text'"
            :placeholder="field.placeholder"
            :required="field.required"
            :min="field.min"
            :max="field.max"
            :minlength="field.minlength"
            :maxlength="field.maxlength"
            :pattern="field.pattern"
            :accept="field.accept"
            :multiple="field.multiple"
          />
          <small v-if="field.hint">{{ field.hint }}</small>
        </label>
      </form>

      <div class="dialog-preview-note"><Info :size="16" /><p>Vista previa: este formulario no envía ni guarda cambios.</p></div>
      <footer class="dialog-actions">
        <button class="button button-secondary" type="button" @click="$emit('close')">Cerrar</button>
        <button class="button button-primary" type="button" disabled :title="saveHint">
          {{ activeMode.submitLabel || 'Guardar' }}
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Info, X } from '@lucide/vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  dialogId: { type: String, required: true },
  moduleName: { type: String, required: true },
  modes: { type: Array, required: true },
  saveHint: { type: String, default: 'Disponible en la fase de integración.' },
})

defineEmits(['close'])
const selectedMode = ref(props.modes[0]?.key)
const activeMode = computed(() => props.modes.find((mode) => mode.key === selectedMode.value) || props.modes[0])

watch(() => props.open, (isOpen) => {
  if (isOpen) selectedMode.value = props.modes[0]?.key
})
</script>

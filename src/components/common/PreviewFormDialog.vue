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

      <form class="preview-form" @submit.prevent="submit">
        <label v-for="field in activeMode.fields" :key="field.name" class="preview-field">
          <span>{{ field.label }}<span v-if="field.required" class="required-mark"> *</span></span>
          <select
            v-if="field.type === 'select'"
            v-model="values[field.name]"
            :required="field.required"
            :multiple="field.multiple"
            :disabled="field.disabled"
          >
            <option v-if="!field.multiple" value="" disabled>{{ field.placeholder || 'Selecciona una opción' }}</option>
            <option v-for="option in field.options" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
          <textarea
            v-else-if="field.type === 'textarea'"
            :name="field.name"
            v-model="values[field.name]"
            :placeholder="field.placeholder"
            :required="field.required"
            :rows="field.rows || 3"
            :maxlength="field.maxlength"
          ></textarea>
          <input
            v-else-if="field.type === 'file'"
            :name="field.name"
            type="file"
            :required="field.required"
            :accept="field.accept"
            :multiple="field.multiple"
            :disabled="field.disabled"
            @change="setFile(field.name, $event)"
          />
          <input
            v-else
            :name="field.name"
            :type="field.type || 'text'"
            v-model="values[field.name]"
            :placeholder="field.placeholder"
            :required="field.required"
            :min="field.min"
            :max="field.max"
            :minlength="field.minlength"
            :maxlength="field.maxlength"
            :pattern="field.pattern"
            :readonly="field.readonly"
            :disabled="field.disabled"
          />
          <small v-if="field.hint">{{ field.hint }}</small>
        </label>

        <p v-if="error" class="form-notice" role="alert">{{ error }}</p>
        <div class="dialog-preview-note"><Info :size="16" /><p>Los cambios se guardarán en la biblioteca y se actualizará el listado.</p></div>
        <footer class="dialog-actions">
          <button class="button button-secondary" type="button" :disabled="loading" @click="$emit('close')">Cancelar</button>
          <button class="button button-primary" type="submit" :disabled="loading">
            <LoaderCircle v-if="loading" class="loading-icon" :size="15" />
            {{ loading ? 'Guardando…' : activeMode.submitLabel || 'Guardar' }}
          </button>
        </footer>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Info, LoaderCircle, X } from '@lucide/vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  dialogId: { type: String, required: true },
  moduleName: { type: String, required: true },
  modes: { type: Array, required: true },
  initialMode: { type: String, default: '' },
  initialValues: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])
const selectedMode = ref(props.initialMode || props.modes[0]?.key)
const values = ref({})
const activeMode = computed(() => props.modes.find((mode) => mode.key === selectedMode.value) || props.modes[0])

function initializeValues() {
  const next = { ...props.initialValues }
  for (const field of activeMode.value?.fields || []) {
    if (next[field.name] === undefined) {
      next[field.name] = field.multiple ? [] : field.default ?? ''
    }
  }
  values.value = next
}

function setFile(name, event) {
  values.value[name] = event.target.files?.[0] || null
}

function submit() {
  emit('submit', { mode: selectedMode.value, values: { ...values.value } })
}

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    selectedMode.value = props.initialMode || props.modes[0]?.key
    initializeValues()
  }
})
watch(selectedMode, initializeValues)
watch(() => props.initialValues, () => {
  if (props.open) initializeValues()
}, { deep: true })
</script>

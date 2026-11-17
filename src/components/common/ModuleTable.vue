<template>
  <div class="module-table-wrap">
    <table class="module-table" :aria-label="ariaLabel" :aria-busy="loading">
      <thead>
        <tr><th v-for="column in columns" :key="column.key">{{ column.label }}</th></tr>
      </thead>
      <tbody>
        <tr>
          <td :colspan="columns.length">
            <div v-if="loading" class="table-loading" role="status" aria-live="polite">
              <LoaderCircle :size="20" />
              <span>{{ loadingMessage }}</span>
            </div>
            <div v-else class="table-empty">
              <span class="empty-illustration"><component :is="icon" :size="23" /></span>
              <strong>{{ emptyTitle }}</strong>
              <p>{{ emptyDescription }}</p>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { LoaderCircle } from '@lucide/vue'

defineProps({
  ariaLabel: { type: String, required: true },
  columns: { type: Array, required: true },
  emptyTitle: { type: String, required: true },
  emptyDescription: { type: String, required: true },
  icon: { type: [Object, Function], required: true },
  loading: { type: Boolean, default: false },
  loadingMessage: { type: String, default: 'Cargando registros...' },
})
</script>

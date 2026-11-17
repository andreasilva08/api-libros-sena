<template>
  <div class="module-table-wrap">
    <table class="module-table" :aria-label="ariaLabel" :aria-busy="loading">
      <thead>
        <tr><th v-for="column in columns" :key="column.key">{{ column.label }}</th></tr>
      </thead>
      <tbody>
        <tr v-if="loading || error || !rows.length" class="module-empty-row">
          <td :colspan="columns.length">
            <div v-if="loading" class="table-loading" role="status" aria-live="polite">
              <LoaderCircle :size="20" />
              <span>{{ loadingMessage }}</span>
            </div>
            <div v-else-if="error" class="table-empty" role="alert">
              <span class="empty-illustration"><component :is="icon" :size="23" /></span>
              <strong>No se pudieron cargar los registros</strong>
              <p>{{ error }}</p>
              <button class="button button-secondary table-retry" type="button" @click="$emit('retry')">Reintentar</button>
            </div>
            <div v-else class="table-empty">
              <span class="empty-illustration"><component :is="icon" :size="23" /></span>
              <strong>{{ emptyTitle }}</strong>
              <p>{{ emptyDescription }}</p>
            </div>
          </td>
        </tr>
        <tr v-for="(row, rowIndex) in rows" v-else :key="row.id ?? rowIndex">
          <td v-for="column in columns" :key="column.key">
            <div v-if="column.key === 'acciones'" class="row-actions">
              <button
                v-for="action in actions"
                :key="action.key"
                v-show="isActionVisible(action, row)"
                class="row-action"
                type="button"
                :title="action.label"
                :aria-label="`${action.label}: ${row.nombre || row.titulo || row.id}`"
                :disabled="action.disabled && action.disabled(row)"
                @click="$emit('row-action', { action: action.key, row })"
              >
                <component :is="action.icon" :size="15" />
              </button>
            </div>
            <span
              v-else-if="column.type === 'status'"
              class="status-pill"
              :class="cellValue(row, column) ? 'status-pill-active' : 'status-pill-inactive'"
            >{{ cellValue(row, column) ? 'Activo' : 'Inactivo' }}</span>
            <span v-else>{{ cellValue(row, column) }}</span>
          </td>
        </tr>
      </tbody>
    </table>
    <footer v-if="total > limit" class="module-pagination">
      <span>{{ skip + 1 }}–{{ Math.min(skip + limit, total) }} de {{ total }}</span>
      <div>
        <button
          class="button button-secondary"
          type="button"
          :disabled="skip <= 0 || loading"
          aria-label="Página anterior"
          @click="$emit('page-change', Math.max(0, skip - limit))"
        >Anterior</button>
        <button
          class="button button-secondary"
          type="button"
          :disabled="skip + limit >= total || loading"
          aria-label="Página siguiente"
          @click="$emit('page-change', skip + limit)"
        >Siguiente</button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { LoaderCircle } from '@lucide/vue'

const props = defineProps({
  ariaLabel: { type: String, required: true },
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  actions: { type: Array, default: () => [] },
  emptyTitle: { type: String, required: true },
  emptyDescription: { type: String, required: true },
  icon: { type: [Object, Function], required: true },
  loading: { type: Boolean, default: false },
  loadingMessage: { type: String, default: 'Cargando registros...' },
  error: { type: String, default: '' },
  total: { type: Number, default: 0 },
  skip: { type: Number, default: 0 },
  limit: { type: Number, default: 10 },
})

defineEmits(['row-action', 'page-change', 'retry'])

function cellValue(row, column) {
  if (typeof column.format === 'function') return column.format(row)
  const value = row[column.key]
  return value === null || value === undefined || value === '' ? '—' : value
}

function isActionVisible(action, row) {
  return typeof action.visible !== 'function' || action.visible(row)
}
</script>

<template>
  <AppShell>
    <ModuleHeading
      eyebrow="CIRCULACIÓN · LECTURAS"
      title="Préstamos"
      description="Revisa los préstamos, sus fechas límite y las devoluciones pendientes."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="dialogOpen = true">
          <Plus :size="17" /> Registrar préstamo
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar search-placeholder="Buscar por socio, libro o identificador">
      <div class="loan-state-tabs" role="group" aria-label="Estado del préstamo">
        <button
          v-for="state in states"
          :key="state.value"
          type="button"
          :aria-pressed="selectedState === state.value"
          :class="{ 'loan-state-active': selectedState === state.value }"
          @click="selectedState = state.value"
        >{{ state.label }}</button>
      </div>
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Estado admitido por la API</span>
    </ModuleToolbar>

    <section class="table-section" aria-label="Listado de préstamos">
      <div class="table-section-heading">
        <div><h2>{{ selectedTitle }}</h2><p>Fechas de préstamo, vencimiento, devolución y multa.</p></div>
        <span class="record-count"><ArrowLeftRight :size="15" /> Registros desde API</span>
      </div>
      <ModuleTable
        aria-label="Préstamos"
        :columns="columns"
        :icon="BookOpenCheck"
        empty-title="No hay préstamos para mostrar"
        empty-description="Los préstamos y su estado aparecerán cuando los datos reales estén disponibles."
      />
    </section>

    <div class="loan-note"><CalendarDays :size="17" /><p>La API calcula y devuelve la fecha límite y la multa del préstamo. El personal responsable no forma parte del modelo de respuesta actual.</p></div>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="loan-form"
      module-name="préstamos"
      :modes="formModes"
      @close="dialogOpen = false"
    />
  </AppShell>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ArrowLeftRight, BookOpenCheck, CalendarDays, Plus, SlidersHorizontal } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'

const dialogOpen = ref(false)
const selectedState = ref('activo')
const states = [
  { value: 'activo', label: 'Activos' },
  { value: 'vencido', label: 'Vencidos' },
  { value: 'devuelto', label: 'Devueltos' },
]
const selectedTitle = computed(() => states.find((state) => state.value === selectedState.value)?.label || 'Préstamos')
const columns = [
  { key: 'libro', label: 'Libro' },
  { key: 'socio', label: 'Socio' },
  { key: 'fecha_prestamo', label: 'Fecha de préstamo' },
  { key: 'fecha_limite', label: 'Fecha límite' },
  { key: 'fecha_devolucion', label: 'Devolución' },
  { key: 'multa', label: 'Multa' },
  { key: 'acciones', label: 'Acciones' },
]
const formModes = [
  {
    key: 'create',
    label: 'Nuevo préstamo',
    title: 'Registrar préstamo',
    submitLabel: 'Registrar préstamo',
    fields: [
      { name: 'libro_id', label: 'ID del libro', type: 'number', required: true, min: 1, placeholder: 'Se seleccionará del catálogo' },
      { name: 'socio_id', label: 'ID del socio', type: 'number', required: true, min: 1, placeholder: 'Se seleccionará del directorio' },
      { name: 'fecha_prestamo', label: 'Fecha de préstamo', type: 'date', hint: 'Opcional; si se omite, la API define la fecha.' },
      { name: 'dias', label: 'Duración (días)', type: 'number', min: 1, max: 30, placeholder: '14', hint: 'Opcional; valor predeterminado 14, rango de 1 a 30.' },
    ],
  },
  {
    key: 'return',
    label: 'Registrar devolución',
    title: 'Registrar devolución',
    submitLabel: 'Registrar devolución',
    note: 'La devolución usa POST /prestamos/{id}/devolucion; la fecha en el cuerpo es opcional.',
    fields: [
      { name: 'prestamo_id', label: 'ID del préstamo', type: 'number', required: true, min: 1, placeholder: 'Identificador del préstamo' },
      { name: 'fecha_devolucion', label: 'Fecha de devolución', type: 'date', hint: 'Opcional; la ruta acepta una fecha de devolución.' },
    ],
  },
]
</script>

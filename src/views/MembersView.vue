<template>
  <AppShell>
    <ModuleHeading
      eyebrow="COMUNIDAD · AFILIACIÓN"
      title="Socios"
      description="Acompaña a tu comunidad lectora y mantén sus datos al día."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="dialogOpen = true">
          <Plus :size="17" /> Registrar socio
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar search-placeholder="Buscar por nombre o correo">
      <label class="sr-only" for="member-status-filter">Filtrar por estado</label>
      <select id="member-status-filter" class="module-filter" disabled>
        <option>Todos los estados</option><option>Activo</option><option>Inactivo</option>
      </select>
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Estado de afiliación</span>
    </ModuleToolbar>

    <section class="table-section" aria-label="Listado de socios">
      <div class="table-section-heading">
        <div><h2>Comunidad lectora</h2><p>Contacto, estado de afiliación y fecha de alta.</p></div>
        <span class="record-count"><UsersRound :size="15" /> Registros desde API</span>
      </div>
      <ModuleTable
        aria-label="Socios"
        :columns="columns"
        :icon="UsersRound"
        empty-title="La comunidad aparecerá aquí"
        empty-description="Los socios se mostrarán al conectar el servicio de biblioteca."
      />
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="member-form"
      module-name="socios"
      :modes="formModes"
      @close="dialogOpen = false"
    />
  </AppShell>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, SlidersHorizontal, UsersRound } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'

const dialogOpen = ref(false)
const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Correo electrónico' },
  { key: 'telefono', label: 'Teléfono' },
  { key: 'activo', label: 'Estado' },
  { key: 'fecha_alta', label: 'Fecha de afiliación' },
  { key: 'acciones', label: 'Acciones' },
]
const memberFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 100, placeholder: 'Nombre del socio', hint: 'Entre 2 y 100 caracteres.' },
  { name: 'email', label: 'Correo electrónico', type: 'email', required: true, maxlength: 100, placeholder: 'persona@correo.com' },
  { name: 'telefono', label: 'Teléfono', maxlength: 15, pattern: '[0-9 +]{7,15}', placeholder: 'Teléfono (opcional)', hint: 'Entre 7 y 15 dígitos, espacios o signo +.' },
  {
    name: 'activo',
    label: 'Estado de afiliación',
    type: 'select',
    placeholder: 'Selecciona un estado',
    options: [{ value: 'true', label: 'Activo' }, { value: 'false', label: 'Inactivo' }],
  },
]
const formModes = [
  { key: 'create', label: 'Nuevo socio', title: 'Registrar socio', submitLabel: 'Registrar socio', fields: memberFields },
  { key: 'edit', label: 'Editar socio', title: 'Editar socio', submitLabel: 'Guardar cambios', note: 'La fecha de alta es un dato de consulta; el formulario se completará al seleccionar un socio.', fields: memberFields },
]
</script>

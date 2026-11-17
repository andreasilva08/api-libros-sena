<template>
  <AppShell>
    <ModuleHeading
      eyebrow="PERSONAS · AUTORÍA"
      title="Autores"
      description="Consulta y organiza la información de quienes dan vida a cada historia."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="dialogOpen = true">
          <Plus :size="17" /> Registrar autor
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar search-placeholder="Buscar por nombre">
      <label class="sr-only" for="author-nationality-filter">Filtrar por nacionalidad</label>
      <input id="author-nationality-filter" class="module-filter" type="search" placeholder="Nacionalidad" disabled />
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Filtro disponible en la API</span>
    </ModuleToolbar>

    <section class="table-section" aria-label="Listado de autores">
      <div class="table-section-heading">
        <div><h2>Directorio de autores</h2><p>Nombre, nacionalidad y año de nacimiento.</p></div>
        <span class="record-count"><Feather :size="15" /> Registros desde API</span>
      </div>
      <ModuleTable
        aria-label="Autores"
        :columns="columns"
        :icon="Feather"
        empty-title="Aún no hay autores para mostrar"
        empty-description="Los autores registrados aparecerán aquí cuando se conecte la API."
      />
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="author-form"
      module-name="autores"
      :modes="formModes"
      @close="dialogOpen = false"
    />
  </AppShell>
</template>

<script setup>
import { ref } from 'vue'
import { Feather, Plus, SlidersHorizontal } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'

const dialogOpen = ref(false)
const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'nacionalidad', label: 'Nacionalidad' },
  { key: 'anio_naci', label: 'Año de nacimiento' },
  { key: 'acciones', label: 'Acciones' },
]
const authorFields = [
  { name: 'nombre', label: 'Nombre', required: true, minlength: 2, maxlength: 100, placeholder: 'Nombre del autor', hint: 'Entre 2 y 100 caracteres.' },
  { name: 'nacionalidad', label: 'Nacionalidad', maxlength: 60, placeholder: 'Nacionalidad (opcional)' },
  { name: 'anio_naci', label: 'Año de nacimiento', type: 'number', min: 1000, max: 2026, placeholder: 'Año (opcional)' },
]
const formModes = [
  { key: 'create', label: 'Nuevo autor', title: 'Registrar autor', submitLabel: 'Registrar autor', fields: authorFields },
  { key: 'edit', label: 'Editar autor', title: 'Editar autor', submitLabel: 'Guardar cambios', note: 'El formulario se completará al seleccionar un autor.', fields: authorFields },
]
</script>

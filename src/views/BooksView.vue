<template>
  <AppShell>
    <ModuleHeading
      eyebrow="CATÁLOGO · COLECCIÓN"
      title="Libros"
      description="Explora el catálogo, sus portadas y la disponibilidad de cada título."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="dialogOpen = true">
          <Plus :size="17" /> Registrar libro
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar search-placeholder="Buscar por título o ISBN">
      <label class="sr-only" for="book-author-filter">Filtrar por autor</label>
      <select id="book-author-filter" class="module-filter" disabled><option>Todos los autores</option></select>
      <label class="sr-only" for="book-category-filter">Filtrar por categoría</label>
      <select id="book-category-filter" class="module-filter" disabled><option>Todas las categorías</option></select>
      <span class="filter-hint"><SlidersHorizontal :size="15" /> Filtros de catálogo</span>
    </ModuleToolbar>

    <section class="catalog-section" aria-label="Catálogo de libros">
      <div class="catalog-section-heading">
        <div><h2>Catálogo visual</h2><p>Portadas, autoría y ejemplares disponibles.</p></div>
        <span class="catalog-view-label"><LayoutGrid :size="15" /> Vista de tarjetas</span>
      </div>
      <article class="book-card-template" aria-label="Plantilla visual de libro, sin datos reales">
        <div class="book-cover-template">
          <BookOpen :size="32" :stroke-width="1.4" />
          <span>PORTADA</span>
        </div>
        <div class="book-template-content">
          <span class="card-overline">FICHA DE CATÁLOGO · PLANTILLA</span>
          <h3>Título del libro</h3>
          <p class="book-template-author"><Feather :size="14" /> Nombre del autor</p>
          <div class="book-template-meta">
            <span><small>ISBN</small><strong>—</strong></span>
            <span><small>AÑO</small><strong>—</strong></span>
            <span><small>CATEGORÍAS</small><strong>—</strong></span>
          </div>
          <div class="book-availability">
            <span><span class="availability-dot"></span>Disponibilidad</span>
            <strong>— disponibles / — ejemplares</strong>
          </div>
          <div class="book-template-footer">
            <span>La ficha se completa con datos de la API.</span>
            <span class="book-cover-actions"><ImagePlus :size="16" /><PencilLine :size="16" /></span>
          </div>
        </div>
      </article>
    </section>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="book-form"
      module-name="libros"
      :modes="formModes"
      @close="dialogOpen = false"
    />
  </AppShell>
</template>

<script setup>
import { ref } from 'vue'
import { BookOpen, Feather, ImagePlus, LayoutGrid, PencilLine, Plus, SlidersHorizontal } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'

const dialogOpen = ref(false)
const bookFields = [
  { name: 'titulo', label: 'Título', required: true, minlength: 1, maxlength: 150, placeholder: 'Título del libro' },
  { name: 'isbn', label: 'ISBN', required: true, maxlength: 13, pattern: '[0-9]{13}', placeholder: '13 dígitos', hint: 'Debe contener exactamente 13 dígitos.' },
  { name: 'anio_publicacion', label: 'Año de publicación', type: 'number', required: true, min: 1450, max: 2026 },
  { name: 'ejemplares', label: 'Ejemplares', type: 'number', required: true, min: 1, max: 50 },
  { name: 'autor_id', label: 'ID del autor', type: 'number', required: true, min: 1, placeholder: 'Se seleccionará desde Autores' },
  { name: 'categoria_ids', label: 'IDs de categorías', placeholder: 'Se seleccionarán desde Categorías', hint: 'La API recibe de 1 a 5 identificadores sin repetir.' },
  { name: 'portada', label: 'Portada', type: 'file', accept: 'image/jpeg,image/png,image/webp', hint: 'JPEG, PNG o WebP · máximo 5 MB. Se envía por separado.' },
]
const formModes = [
  { key: 'create', label: 'Nuevo libro', title: 'Registrar libro', submitLabel: 'Registrar libro', fields: bookFields },
  { key: 'edit', label: 'Editar libro', title: 'Editar libro', submitLabel: 'Guardar cambios', note: 'El formulario se completará al seleccionar un libro del catálogo.', fields: bookFields },
]
</script>

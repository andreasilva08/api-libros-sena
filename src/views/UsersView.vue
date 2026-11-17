<template>
  <AppShell>
    <ModuleHeading
      eyebrow="ACCESO · EQUIPO"
      title="Usuarios"
      description="Administra las cuentas, los roles y el estado de acceso del sistema."
    >
      <template #actions>
        <button class="button button-primary module-action" type="button" @click="dialogOpen = true">
          <Plus :size="17" /> Registrar usuario
        </button>
      </template>
    </ModuleHeading>

    <ModuleToolbar search-placeholder="Buscar por nombre o correo">
      <label class="sr-only" for="user-role-filter">Filtrar por rol</label>
      <select id="user-role-filter" class="module-filter" disabled>
        <option>Todos los roles</option><option>Administrador</option><option>Bibliotecario</option><option>Socio</option>
      </select>
      <span class="filter-hint"><ShieldCheck :size="15" /> Administración de usuarios</span>
    </ModuleToolbar>

    <section class="table-section" aria-label="Listado de usuarios">
      <div class="table-section-heading">
        <div><h2>Cuentas de usuario</h2><p>Correo, rol, estado y socio asociado cuando corresponda.</p></div>
        <span class="record-count"><UserRoundCog :size="15" /> Solo administración</span>
      </div>
      <ModuleTable
        aria-label="Usuarios"
        :columns="columns"
        :icon="UsersRound"
        empty-title="Las cuentas aparecerán aquí"
        empty-description="El listado requiere permisos de administrador y conexión a la API."
      />
    </section>

    <div class="loan-note"><Info :size="17" /><p>La API permite crear usuarios y cambiar rol o estado por separado. No ofrece eliminación ni consulta individual de usuarios.</p></div>

    <PreviewFormDialog
      :open="dialogOpen"
      dialog-id="user-form"
      module-name="usuarios"
      :modes="formModes"
      @close="dialogOpen = false"
    />
  </AppShell>
</template>

<script setup>
import { ref } from 'vue'
import { Info, Plus, ShieldCheck, UserRoundCog, UsersRound } from '@lucide/vue'
import AppShell from '../components/layout/AppShell.vue'
import ModuleHeading from '../components/common/ModuleHeading.vue'
import ModuleTable from '../components/common/ModuleTable.vue'
import ModuleToolbar from '../components/common/ModuleToolbar.vue'
import PreviewFormDialog from '../components/common/PreviewFormDialog.vue'

const dialogOpen = ref(false)
const columns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Correo electrónico' },
  { key: 'rol', label: 'Rol' },
  { key: 'activo', label: 'Estado' },
  { key: 'socio_id', label: 'Socio asociado' },
  { key: 'creado_en', label: 'Creado' },
  { key: 'acciones', label: 'Acciones' },
]
const formModes = [
  {
    key: 'create',
    label: 'Crear usuario',
    title: 'Registrar usuario',
    submitLabel: 'Registrar usuario',
    fields: [
      { name: 'nombre', label: 'Nombre', required: true, minlength: 3, maxlength: 100, placeholder: 'Nombre de usuario', hint: 'Entre 3 y 100 caracteres.' },
      { name: 'email', label: 'Correo electrónico', type: 'email', required: true, maxlength: 100, placeholder: 'persona@correo.com' },
      { name: 'password', label: 'Contraseña', type: 'password', required: true, minlength: 8, maxlength: 64, pattern: '(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,64}', placeholder: 'Contraseña segura', hint: 'De 8 a 64 caracteres; debe incluir mayúscula, minúscula y número.' },
      { name: 'rol', label: 'Rol', type: 'select', required: true, options: [
        { value: 'admin', label: 'Administrador' },
        { value: 'bibliotecario', label: 'Bibliotecario' },
        { value: 'socio', label: 'Socio' },
      ] },
      { name: 'socio_id', label: 'ID del socio vinculado', type: 'number', min: 1, placeholder: 'Opcional; requerido para rol socio' },
    ],
  },
  {
    key: 'role',
    label: 'Cambiar rol',
    title: 'Actualizar rol',
    submitLabel: 'Actualizar rol',
    note: 'La API requiere PATCH /usuarios/{id}/rol.',
    fields: [
      { name: 'id', label: 'ID del usuario', type: 'number', required: true, min: 1 },
      { name: 'rol', label: 'Nuevo rol', type: 'select', required: true, options: [
        { value: 'admin', label: 'Administrador' },
        { value: 'bibliotecario', label: 'Bibliotecario' },
        { value: 'socio', label: 'Socio' },
      ] },
    ],
  },
  {
    key: 'status',
    label: 'Cambiar estado',
    title: 'Actualizar estado',
    submitLabel: 'Actualizar estado',
    note: 'La API requiere PATCH /usuarios/{id}/activo.',
    fields: [
      { name: 'id', label: 'ID del usuario', type: 'number', required: true, min: 1 },
      { name: 'activo', label: 'Estado de la cuenta', type: 'select', required: true, options: [
        { value: 'true', label: 'Activo' },
        { value: 'false', label: 'Inactivo' },
      ] },
    ],
  },
]
</script>

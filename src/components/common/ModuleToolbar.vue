<template>
  <div class="module-toolbar">
    <label class="module-search">
      <Search :size="17" aria-hidden="true" />
      <input type="search" :placeholder="searchPlaceholder" disabled />
    </label>
    <div class="module-filters">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { Search } from '@lucide/vue'

defineProps({
  searchPlaceholder: { type: String, required: true },
})
</script>

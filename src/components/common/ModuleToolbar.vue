<template>
  <div class="module-toolbar">
    <label class="module-search">
      <Search :size="17" aria-hidden="true" />
      <input
        type="search"
        :value="modelValue"
        :placeholder="searchPlaceholder"
        @input="$emit('update:modelValue', $event.target.value)"
      />
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
  modelValue: { type: String, default: '' },
})

defineEmits(['update:modelValue'])
</script>

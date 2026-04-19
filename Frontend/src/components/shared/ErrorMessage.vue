<!-- src/components/shared/ErrorMessage.vue -->
<template>
  <div v-if="message" class="error-message">
    <span class="error-message__icon">⚠️</span>
    <span class="error-message__text">{{ message }}</span>
    <button
      v-if="dismissible"
      class="error-message__close"
      @click="$emit('dismiss')"
    >
      ✕
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string | null
  dismissible?: boolean
}>()

defineEmits<{
  dismiss: []
}>()
</script>

<style scoped>
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: var(--radius);
  font-size: 14px;
}

.error-message__icon {
  flex-shrink: 0;
}

.error-message__text {
  flex: 1;
}

.error-message__close {
  background: none;
  border: none;
  color: #991b1b;
  cursor: pointer;
  font-size: 14px;
  padding: 0 4px;
}
</style>
<!-- src/components/shared/LoadingSpinner.vue -->
<template>
  <div class="spinner-wrap" :class="{ 'spinner-wrap--full': fullScreen }">
    <div class="spinner" :class="`spinner--${size}`" />
    <p v-if="message" class="spinner__message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
  message?: string
  fullScreen?: boolean
}>()
</script>

<style scoped>
.spinner-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
}

.spinner-wrap--full {
  height: 100%;
  min-height: 200px;
}

.spinner {
  border-radius: 50%;
  border-style: solid;
  border-color: var(--color-primary) transparent transparent transparent;
  animation: spin 0.7s linear infinite;
}

.spinner--sm { width: 20px; height: 20px; border-width: 2px; }
.spinner--md { width: 36px; height: 36px; border-width: 3px; }
.spinner--lg { width: 52px; height: 52px; border-width: 4px; }

.spinner:not([class*="spinner--"]) {
  width: 36px;
  height: 36px;
  border-width: 3px;
}

.spinner__message {
  font-size: 14px;
  color: var(--color-subtext);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
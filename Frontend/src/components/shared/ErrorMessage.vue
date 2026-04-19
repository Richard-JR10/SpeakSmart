<template>
  <div v-if="message" class="error-message">
    <span class="error-message__icon">
      <AppIcon name="alert" :size="18" />
    </span>
    <span class="error-message__text">{{ message }}</span>
    <button
      v-if="dismissible"
      class="error-message__close"
      @click="$emit('dismiss')"
    >
      <AppIcon name="close" :size="16" />
    </button>
  </div>
</template>

<script setup lang="ts">
import AppIcon from './AppIcon.vue'

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
  align-items: flex-start;
  gap: 10px;
  background: rgba(198, 85, 73, 0.12);
  color: #8b2f26;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(198, 85, 73, 0.18);
  box-shadow: var(--shadow-inset);
  font-size: 14px;
}

.error-message__icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.error-message__text {
  flex: 1;
  line-height: 1.5;
}

.error-message__close {
  min-width: 28px;
  min-height: 28px;
  color: inherit;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}
</style>

<template>
  <div v-if="authStore.loading" class="app-loading">
    <div class="app-loading__card surface-card surface-card--accent">
      <div class="app-loading__spinner" />
      <p class="app-loading__eyebrow">SpeakSmart</p>
      <p class="app-loading__copy">Loading your practice space...</p>
    </div>
  </div>
  <RouterView v-else />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initAuth()
})
</script>

<style scoped>
.app-loading {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.app-loading__card {
  width: min(100%, 320px);
  padding: 28px 24px;
  display: grid;
  justify-items: center;
  gap: 12px;
  text-align: center;
}

.app-loading__spinner {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 4px solid rgba(168, 31, 93, 0.16);
  border-top-color: var(--color-primary);
  animation: spin 0.8s linear infinite;
}

.app-loading__eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.app-loading__copy {
  margin: 0;
  color: var(--color-subtext);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

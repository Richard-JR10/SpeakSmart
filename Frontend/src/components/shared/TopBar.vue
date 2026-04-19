<!-- src/components/shared/TopBar.vue -->
<template>
  <header class="topbar">
    <button
      v-if="showBack"
      class="topbar__back"
      @click="$emit('back')"
    >
      ←
    </button>
    <h1 class="topbar__title">{{ title }}</h1>
    <div class="topbar__right">
      <slot name="right" />
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  showBack?: boolean
}>()

defineEmits<{
  back: []
}>()
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 56px;
  min-height: 56px;
  background: #ffffff;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar__back {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--color-primary);
  padding: 4px 8px 4px 0;
  line-height: 1;
}

.topbar__title {
  flex: 1;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
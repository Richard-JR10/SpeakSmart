<template>
  <header class="topbar">
    <button
      v-if="showBack"
      class="topbar__back"
      @click="$emit('back')"
    >
      <AppIcon name="back" :size="18" />
    </button>
    <div class="topbar__title-block">
      <p class="topbar__kicker">SpeakSmart</p>
      <h1 class="topbar__title">{{ title }}</h1>
    </div>
    <div class="topbar__right">
      <slot name="right" />
    </div>
  </header>
</template>

<script setup lang="ts">
import AppIcon from './AppIcon.vue'

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
  gap: 12px;
  padding: max(14px, env(safe-area-inset-top)) 18px 16px;
  min-height: 84px;
  background:
    linear-gradient(180deg, rgba(255, 252, 246, 0.98), rgba(247, 243, 234, 0.92));
  border-bottom: 1px solid rgba(215, 225, 218, 0.9);
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: blur(14px);
}

.topbar__back {
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
  color: var(--color-primary-dark);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(46, 138, 103, 0.1);
}

.topbar__title-block {
  flex: 1;
  min-width: 0;
}

.topbar__kicker {
  margin: 0 0 2px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-subtext);
}

.topbar__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 22px;
  line-height: 1.05;
  color: var(--color-heading);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

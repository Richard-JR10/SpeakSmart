<!-- src/components/shared/BottomNav.vue -->
<template>
  <nav class="bottom-nav">
    <RouterLink
      v-for="item in navItems"
      :key="item.name"
      :to="item.to"
      class="bottom-nav__item"
      :class="{ 'bottom-nav__item--active': route.name === item.name }"
    >
      <span class="bottom-nav__icon">{{ item.icon }}</span>
      <span class="bottom-nav__label">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { name: 'home',     label: 'Home',     icon: '🏠', to: '/home' },
  { name: 'lessons',  label: 'Lessons',  icon: '📚', to: '/lessons' },
  { name: 'progress', label: 'Progress', icon: '📈', to: '/progress' },
  { name: 'settings', label: 'Settings', icon: '⚙️', to: '/settings' },
]
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: 64px;
  background: #ffffff;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 20;
  padding-bottom: env(safe-area-inset-bottom);
}

.bottom-nav__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-decoration: none;
  color: var(--color-subtext);
  flex: 1;
  padding: 6px 0;
  transition: color 0.15s;
}

.bottom-nav__item--active {
  color: var(--color-primary);
}

.bottom-nav__icon {
  font-size: 20px;
  line-height: 1;
}

.bottom-nav__label {
  font-size: 10px;
  font-weight: 500;
}
</style>
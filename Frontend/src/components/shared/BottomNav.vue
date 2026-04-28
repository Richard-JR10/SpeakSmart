<template>
  <nav class="bottom-nav">
    <RouterLink
      v-for="item in navItems"
      :key="item.name"
      :to="item.to"
      class="bottom-nav__item"
      :class="{ 'bottom-nav__item--active': route.name === item.name }"
    >
      <span class="bottom-nav__icon">
        <AppIcon :name="item.icon" :size="20" />
      </span>
      <span class="bottom-nav__label">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppIcon from './AppIcon.vue'

const route = useRoute()

const navItems = [
  { name: 'home', label: 'Home', icon: 'home', to: '/home' },
  { name: 'lessons', label: 'Lessons', icon: 'book', to: '/lessons' },
  { name: 'progress', label: 'Progress', icon: 'chart', to: '/progress' },
  { name: 'settings', label: 'Settings', icon: 'settings', to: '/settings' },
]
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: max(12px, env(safe-area-inset-bottom));
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 24px);
  max-width: 480px;
  min-height: 72px;
  background: rgba(255, 253, 251, 0.92);
  border: 1px solid rgba(234, 209, 220, 0.9);
  border-radius: 24px;
  box-shadow: 0 18px 38px rgba(58, 20, 39, 0.14);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 20;
  padding: 8px;
}

.bottom-nav__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  color: var(--color-subtext);
  flex: 1;
  min-height: 56px;
  padding: 8px 0;
  border-radius: 18px;
  transition: color var(--transition-fast), background var(--transition-fast), transform var(--transition-fast);
}

.bottom-nav__item--active {
  color: var(--color-primary-dark);
  background: linear-gradient(180deg, rgba(168, 31, 93, 0.13), rgba(253, 232, 242, 0.9));
  transform: translateY(-1px);
}

.bottom-nav__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.bottom-nav__label {
  font-size: 11px;
  font-weight: 700;
}

@media (min-width: 768px) {
  .bottom-nav {
    width: min(520px, calc(100% - 40px));
  }
}
</style>

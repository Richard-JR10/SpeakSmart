<!-- src/layouts/InstructorLayout.vue -->
<template>
  <div class="instructor-layout">

    <!-- Sidebar -->
    <aside class="instructor-layout__sidebar">
      <div class="sidebar__logo">
        <span class="text-primary font-bold text-lg">SpeakSmart</span>
        <span class="text-xs text-gray-400 block">Instructor</span>
      </div>

      <nav class="sidebar__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="sidebar__link"
          :class="{ 'sidebar__link--active': route.name === item.name }"
        >
          <span class="sidebar__link-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <button
        class="sidebar__signout"
        @click="handleSignOut"
      >
        <span>Sign out</span>
      </button>
    </aside>

    <!-- Main content -->
    <main class="instructor-layout__content">
      <div class="instructor-layout__inner">
        <slot />
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems = [
  { name: 'instructor-overview',  label: 'Overview',  icon: '📊', to: '/instructor' },
  { name: 'instructor-students',  label: 'Students',  icon: '👥', to: '/instructor/students' },
  { name: 'instructor-heatmap',   label: 'Heatmap',   icon: '🗺️', to: '/instructor/heatmap' },
  { name: 'instructor-exercises', label: 'Exercises', icon: '📝', to: '/instructor/exercises' },
]

async function handleSignOut() {
  await authStore.signOut()
  router.push('/')
}
</script>

<style scoped>
.instructor-layout {
  display: flex;
  height: 100dvh;
  max-width: 100%;
  overflow: hidden;
}

.instructor-layout__sidebar {
  width: 200px;
  min-width: 200px;
  background: #ffffff;
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  gap: 4px;
}

.sidebar__logo {
  padding: 0 20px 20px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 8px;
}

.sidebar__nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 12px;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-subtext);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.sidebar__link:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.sidebar__link--active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.sidebar__link-icon {
  font-size: 16px;
}

.sidebar__signout {
  margin: 0 12px;
  padding: 10px 12px;
  border-radius: 8px;
  border: none;
  background: none;
  color: var(--color-subtext);
  font-size: 14px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.sidebar__signout:hover {
  background: #fee2e2;
  color: #ef4444;
}

.instructor-layout__content {
  flex: 1;
  overflow-y: auto;
  background: var(--color-bg);
}

.instructor-layout__inner {
  padding: 32px;
  max-width: 1200px;
}
</style>
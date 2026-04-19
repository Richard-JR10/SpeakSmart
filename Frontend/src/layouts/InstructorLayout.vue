<template>
  <div class="instructor-layout">
    <aside class="instructor-layout__sidebar">
      <div class="sidebar__brand surface-card surface-card--accent">
        <p class="sidebar__brand-kicker">SpeakSmart</p>
        <h1 class="sidebar__brand-title">Instructor Studio</h1>
        <p class="sidebar__brand-copy">
          Calm analytics and targeted follow-up for pronunciation coaching.
        </p>
      </div>

      <nav class="sidebar__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="sidebar__link"
          :class="{ 'sidebar__link--active': route.name === item.name }"
        >
          <span class="sidebar__link-icon">
            <AppIcon :name="item.icon" :size="18" />
          </span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <button
        class="sidebar__signout"
        @click="handleSignOut"
      >
        <AppIcon name="logout" :size="18" />
        <span>Sign out</span>
      </button>
    </aside>

    <main class="instructor-layout__content">
      <div class="instructor-layout__inner">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/shared/AppIcon.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems = [
  { name: 'instructor-overview', label: 'Overview', icon: 'chart', to: '/instructor' },
  { name: 'instructor-students', label: 'Students', icon: 'users', to: '/instructor/students' },
  { name: 'instructor-heatmap', label: 'Heatmap', icon: 'grid', to: '/instructor/heatmap' },
  { name: 'instructor-exercises', label: 'Exercises', icon: 'clipboard', to: '/instructor/exercises' },
]

async function handleSignOut() {
  await authStore.signOut()
  router.push('/')
}
</script>

<style scoped>
.instructor-layout {
  display: flex;
  min-height: 100dvh;
  max-width: 100%;
  background:
    radial-gradient(circle at top left, rgba(46, 138, 103, 0.1), transparent 22%),
    radial-gradient(circle at top right, rgba(184, 141, 70, 0.12), transparent 18%),
    linear-gradient(180deg, #f7f3eb 0%, #f3efe7 100%);
}

.instructor-layout__sidebar {
  width: 290px;
  min-width: 290px;
  background: rgba(251, 249, 242, 0.9);
  border-right: 1px solid rgba(215, 225, 218, 0.9);
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 20px;
  backdrop-filter: blur(14px);
}

.sidebar__brand {
  padding: 22px;
}

.sidebar__brand-kicker {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.sidebar__brand-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 30px;
  line-height: 1;
  color: var(--color-heading);
}

.sidebar__brand-copy {
  margin: 12px 0 0;
  color: var(--color-subtext);
  font-size: 14px;
  line-height: 1.55;
}

.sidebar__nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-x: auto;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-subtext);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast), transform var(--transition-fast);
}

.sidebar__link:hover {
  background: rgba(46, 138, 103, 0.1);
  color: var(--color-primary-dark);
  transform: translateY(-1px);
}

.sidebar__link--active {
  background: linear-gradient(180deg, rgba(46, 138, 103, 0.16), rgba(255, 252, 246, 0.9));
  color: var(--color-primary-dark);
  box-shadow: var(--shadow-soft);
}

.sidebar__link-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.sidebar__signout {
  margin-top: auto;
  min-height: 48px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(198, 85, 73, 0.1);
  color: var(--color-subtext);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar__signout:hover {
  background: rgba(198, 85, 73, 0.14);
  color: #8b2f26;
}

.instructor-layout__content {
  flex: 1;
  overflow-y: auto;
}

.instructor-layout__inner {
  padding: 28px;
  max-width: 1280px;
}

@media (max-width: 1023px) {
  .instructor-layout {
    flex-direction: column;
  }

  .instructor-layout__sidebar {
    width: 100%;
    min-width: 0;
    padding: 18px;
    border-right: none;
    border-bottom: 1px solid rgba(215, 225, 218, 0.9);
  }

  .sidebar__nav {
    flex-direction: row;
  }

  .sidebar__link {
    min-width: fit-content;
  }

  .sidebar__signout {
    margin-top: 0;
    align-self: flex-start;
  }
}

@media (max-width: 767px) {
  .instructor-layout__inner {
    padding: 18px;
  }

  .sidebar__brand-title {
    font-size: 26px;
  }
}
</style>

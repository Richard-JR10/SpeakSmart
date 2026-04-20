import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

function getHomeRouteName(role?: 'student' | 'instructor') {
  return role === 'instructor' ? 'instructor-overview' : 'home'
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'onboarding',
      component: () => import('@/views/OnboardingView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/complete-profile',
      name: 'complete-profile',
      component: () => import('@/views/CompleteProfileView.vue'),
      meta: { requiresAuth: true, allowPendingProfile: true },
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/student/HomeView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/lessons',
      name: 'lessons',
      component: () => import('@/views/student/LessonsView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/practice/:moduleId/:phraseId',
      name: 'practice',
      component: () => import('@/views/student/PracticeView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('@/views/student/ResultsView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/progress',
      name: 'progress',
      component: () => import('@/views/student/ProgressView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/student/SettingsView.vue'),
      meta: { requiresAuth: true, role: 'student' },
    },
    {
      path: '/instructor',
      name: 'instructor-overview',
      component: () => import('@/views/instructor/OverviewView.vue'),
      meta: { requiresAuth: true, role: 'instructor' },
    },
    {
      path: '/instructor/students',
      name: 'instructor-students',
      component: () => import('@/views/instructor/StudentsView.vue'),
      meta: { requiresAuth: true, role: 'instructor' },
    },
    {
      path: '/instructor/heatmap',
      name: 'instructor-heatmap',
      component: () => import('@/views/instructor/HeatmapView.vue'),
      meta: { requiresAuth: true, role: 'instructor' },
    },
    {
      path: '/instructor/exercises',
      name: 'instructor-exercises',
      component: () => import('@/views/instructor/ExercisesView.vue'),
      meta: { requiresAuth: true, role: 'instructor' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (authStore.loading) {
    await authStore.initAuth()
  }

  const isAuthenticated = authStore.isAuthenticated
  const role = authStore.profile?.role

  if (!isAuthenticated) {
    if (to.meta.requiresAuth) {
      return { name: 'onboarding' }
    }
    return true
  }

  if (authStore.needsProfileSetup && !to.meta.allowPendingProfile) {
    return { name: 'complete-profile' }
  }

  if (to.meta.allowPendingProfile && !authStore.needsProfileSetup) {
    return { name: getHomeRouteName(role) }
  }

  if (!to.meta.requiresAuth) {
    return { name: authStore.needsProfileSetup ? 'complete-profile' : getHomeRouteName(role) }
  }

  if (to.meta.role && to.meta.role !== role) {
    return { name: getHomeRouteName(role) }
  }

  return true
})

export default router

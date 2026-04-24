import { onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import type { AuthFlowResult } from '@/types'

type UseAuthRedirectOptions = {
  onPageRestore?: () => void
}

export function useAuthRedirect(options: UseAuthRedirectOptions = {}) {
  const router = useRouter()
  const authStore = useAuthStore()

  let redirecting = false

  async function redirectAfterAuth(result: AuthFlowResult = 'signed-in') {
    if (result === 'redirect' || redirecting) return

    if (result === 'profile-setup') {
      redirecting = true
      try {
        await router.replace('/complete-profile')
      } finally {
        redirecting = false
      }
      return
    }

    if (authStore.loading) {
      await authStore.initAuth()
    }

    if (!authStore.isAuthenticated) return
    if (!authStore.needsProfileSetup && !authStore.profile) return

    redirecting = true
    try {
      if (authStore.needsProfileSetup) {
        await router.replace('/complete-profile')
        return
      }

      await router.replace(authStore.isInstructor ? '/instructor' : '/home')
    } finally {
      redirecting = false
    }
  }

  async function redirectIfAuthenticated() {
    if (authStore.loading) {
      await authStore.initAuth()
    }

    if (authStore.isAuthenticated) {
      await redirectAfterAuth(authStore.needsProfileSetup ? 'profile-setup' : 'signed-in')
    }
  }

  function handlePageShow(event: PageTransitionEvent) {
    if (event.persisted) {
      options.onPageRestore?.()
      void redirectIfAuthenticated()
    }
  }

  onMounted(() => {
    void redirectIfAuthenticated()
    window.addEventListener('pageshow', handlePageShow)
  })

  onUnmounted(() => {
    window.removeEventListener('pageshow', handlePageShow)
  })

  watch(
    () => [
      authStore.isAuthenticated,
      authStore.needsProfileSetup,
      authStore.profile?.role,
      authStore.loading,
    ],
    () => {
      if (!authStore.loading && authStore.isAuthenticated) {
        void redirectIfAuthenticated()
      }
    },
  )

  return {
    redirectAfterAuth,
    redirectIfAuthenticated,
  }
}

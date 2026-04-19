<template>
  <AuthShell
    eyebrow="Welcome back"
    title="Sign in to your account"
    subtitle="Use your SpeakSmart email and password, or continue with Google."
    back-to="/"
  >
    <ErrorMessage
      v-if="visibleError"
      :message="visibleError"
      dismissible
      @dismiss="dismissError"
    />

    <form class="auth-form" @submit.prevent="handleEmailLogin">
      <div class="auth-field">
        <label class="auth-label" for="login-email">Email</label>
        <input
          id="login-email"
          v-model.trim="email"
          type="email"
          class="auth-input"
          placeholder="name@example.com"
          autocomplete="email"
        />
      </div>

      <div class="auth-field">
        <label class="auth-label" for="login-password">Password</label>
        <div class="auth-input-wrap">
          <input
            id="login-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="auth-input auth-input--with-action"
            placeholder="Enter your password"
            autocomplete="current-password"
          />
          <button
            type="button"
            class="auth-input-action"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
      </div>

      <button class="auth-button auth-button--primary" :disabled="submitDisabled">
        <LoadingSpinner v-if="loading" size="sm" />
        <span v-else>Sign in</span>
      </button>
    </form>

    <div class="auth-separator">
      <span>or</span>
    </div>

    <button
      type="button"
      class="auth-button auth-button--secondary"
      :disabled="loading"
      @click="handleGoogleLogin"
    >
      Continue with Google
    </button>

    <template #footer>
      <p class="auth-footer-copy">
        New to SpeakSmart?
        <RouterLink class="auth-inline-link" to="/signup">Create an account</RouterLink>
      </p>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import type { AuthFlowResult } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const formError = ref<string | null>(null)

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(() => loading.value || !email.value || !password.value)

function dismissError() {
  formError.value = null
  authStore.clearError()
}

async function handleEmailLogin() {
  dismissError()

  if (!email.value || !password.value) {
    formError.value = 'Enter your email and password.'
    return
  }

  loading.value = true
  try {
    const result = await authStore.signInWithEmail(email.value, password.value)
    await redirectAfterAuth(result)
  } finally {
    loading.value = false
  }
}

async function handleGoogleLogin() {
  dismissError()

  loading.value = true
  try {
    const result = await authStore.signInWithGoogle()
    await redirectAfterAuth(result)
  } finally {
    loading.value = false
  }
}

async function redirectAfterAuth(result: AuthFlowResult) {
  if (result === 'redirect') return

  if (result === 'profile-setup' || authStore.needsProfileSetup) {
    await router.push('/complete-profile')
    return
  }

  await router.push(authStore.isInstructor ? '/instructor' : '/home')
}
</script>

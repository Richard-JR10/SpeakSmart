<template>
  <AuthShell
    eyebrow="Create account"
    title="Sign up for SpeakSmart"
    subtitle="Choose your role, set a strong password, and start using SpeakSmart on web or mobile."
    back-to="/"
  >
    <ErrorMessage
      v-if="visibleError"
      :message="visibleError"
      dismissible
      @dismiss="dismissError"
    />

    <form class="auth-form" @submit.prevent="handleSignup">
      <div class="auth-field">
        <label class="auth-label" for="signup-name">Name</label>
        <input
          id="signup-name"
          v-model.trim="displayName"
          type="text"
          class="auth-input"
          placeholder="Enter your full name"
          autocomplete="name"
        />
      </div>

      <div class="auth-field">
        <label class="auth-label" for="signup-email">Email</label>
        <input
          id="signup-email"
          v-model.trim="email"
          type="email"
          class="auth-input"
          placeholder="name@example.com"
          autocomplete="email"
        />
      </div>

      <div class="auth-field">
        <span class="auth-label">Role</span>
        <div class="auth-role-grid">
          <button
            v-for="option in roleOptions"
            :key="option.value"
            type="button"
            class="auth-role-button"
            :class="{ 'auth-role-button--active': role === option.value }"
            @click="role = option.value"
          >
            <span class="auth-role-button__title">{{ option.label }}</span>
            <span class="auth-role-button__copy">{{ option.copy }}</span>
          </button>
        </div>
      </div>

      <div class="auth-field">
        <label class="auth-label" for="signup-password">Password</label>
        <div class="auth-input-wrap">
          <input
            id="signup-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="auth-input auth-input--with-action"
            placeholder="Create a strong password"
            autocomplete="new-password"
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

      <PasswordChecklist :password="password" />

      <button class="auth-button auth-button--primary" :disabled="submitDisabled">
        <LoadingSpinner v-if="loading" size="sm" />
        <span v-else>Create account</span>
      </button>
    </form>

    <div class="auth-separator">
      <span>or</span>
    </div>

    <button
      type="button"
      class="auth-button auth-button--secondary"
      :disabled="loading"
      @click="handleGoogleSignup"
    >
      Continue with Google
    </button>

    <template #footer>
      <p class="auth-footer-copy">
        Already have an account?
        <RouterLink class="auth-inline-link" to="/login">Sign in</RouterLink>
      </p>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordChecklist from '@/components/auth/PasswordChecklist.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import type { AuthFlowResult, UserRole } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref('')
const email = ref('')
const password = ref('')
const role = ref<UserRole>('student')
const showPassword = ref(false)
const loading = ref(false)
const formError = ref<string | null>(null)

const roleOptions: Array<{ value: UserRole; label: string; copy: string }> = [
  {
    value: 'student',
    label: 'Student',
    copy: 'Practice lessons, record attempts, and track progress.',
  },
  {
    value: 'instructor',
    label: 'Instructor',
    copy: 'Review student analytics and manage class exercises.',
  },
]

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(
  () => loading.value || !displayName.value || !email.value || !password.value,
)

function dismissError() {
  formError.value = null
  authStore.clearError()
}

function isPasswordValid(value: string) {
  return (
    value.length >= 8 &&
    /[A-Z]/.test(value) &&
    /\d/.test(value) &&
    /[^A-Za-z0-9]/.test(value)
  )
}

function validateForm() {
  if (!displayName.value.trim()) {
    return 'Enter your name.'
  }

  if (!email.value.trim()) {
    return 'Enter your email address.'
  }

  if (!isPasswordValid(password.value)) {
    return 'Password does not meet the required strength rules.'
  }

  return null
}

async function handleSignup() {
  dismissError()

  const validationError = validateForm()
  if (validationError) {
    formError.value = validationError
    return
  }

  loading.value = true
  try {
    const result = await authStore.signUpWithEmail({
      displayName: displayName.value,
      email: email.value,
      password: password.value,
      role: role.value,
    })
    await redirectAfterAuth(result)
  } finally {
    loading.value = false
  }
}

async function handleGoogleSignup() {
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

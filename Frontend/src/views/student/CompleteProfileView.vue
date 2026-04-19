<template>
  <AuthShell
    eyebrow="Complete profile"
    title="Finish setting up your account"
    subtitle="Confirm your name and choose the role SpeakSmart should use for your profile."
    back-to="/login"
    back-label="Sign in"
  >
    <ErrorMessage
      v-if="visibleError"
      :message="visibleError"
      dismissible
      @dismiss="dismissError"
    />

    <form class="auth-form" @submit.prevent="handleCompleteProfile">
      <div class="auth-field">
        <label class="auth-label" for="complete-email">Signed-in account</label>
        <input
          id="complete-email"
          :value="authStore.firebaseUser?.email ?? ''"
          type="text"
          class="auth-input auth-input--readonly"
          readonly
        />
      </div>

      <div class="auth-field">
        <label class="auth-label" for="complete-name">Name</label>
        <input
          id="complete-name"
          v-model.trim="displayName"
          type="text"
          class="auth-input"
          placeholder="Enter your full name"
          autocomplete="name"
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

      <button class="auth-button auth-button--primary" :disabled="submitDisabled">
        <LoadingSpinner v-if="loading" size="sm" />
        <span v-else>Complete setup</span>
      </button>
    </form>

    <template #footer>
      <p class="auth-footer-copy">
        Signed in with the wrong account?
        <button type="button" class="auth-inline-button" @click="handleSignOut">
          Sign out
        </button>
      </p>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref(authStore.firebaseUser?.displayName?.trim() ?? '')
const role = ref<UserRole>('student')
const loading = ref(false)
const formError = ref<string | null>(null)

const roleOptions: Array<{ value: UserRole; label: string; copy: string }> = [
  {
    value: 'student',
    label: 'Student',
    copy: 'Use practice lessons, scores, and progress tracking.',
  },
  {
    value: 'instructor',
    label: 'Instructor',
    copy: 'Use analytics dashboards and exercise assignment tools.',
  },
]

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(() => loading.value || !displayName.value.trim())

function dismissError() {
  formError.value = null
  authStore.clearError()
}

async function handleCompleteProfile() {
  dismissError()

  if (!displayName.value.trim()) {
    formError.value = 'Enter your name to finish setup.'
    return
  }

  loading.value = true
  try {
    await authStore.completeProfile({
      displayName: displayName.value,
      role: role.value,
    })
    await router.push(authStore.isInstructor ? '/instructor' : '/home')
  } finally {
    loading.value = false
  }
}

async function handleSignOut() {
  await authStore.signOut()
  await router.push('/login')
}
</script>

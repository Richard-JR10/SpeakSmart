<template>
  <section class="min-h-dvh bg-background text-foreground">
    <a
      href="#login-main"
      class="sr-only absolute left-4 top-4 z-60 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-lg focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20"
    >
      Skip to main content
    </a>

    <main id="login-main" tabindex="-1">
      <div class="mx-auto flex min-h-dvh w-full max-w-6xl items-center px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid w-full gap-6 lg:grid-cols-[minmax(0,1fr)_440px] lg:items-center">
          <div class="flex flex-col gap-6 order-1">
            <Button as-child variant="outline" size="lg" class="w-fit">
              <RouterLink to="/">
                <ArrowLeft data-icon="inline-start" />
                Back
              </RouterLink>
            </Button>

            <div class="hidden lg:flex flex-col gap-4">
              <div class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                <Sparkles class="size-5" />
              </div>

              <div class="flex flex-col gap-3">
                <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                  Welcome Back
                </p>
                <h1 class="text-balance font-(--font-display) text-5xl leading-[0.95] tracking-[-0.04em] text-(--color-heading) sm:text-6xl">
                  Sign in and continue with <span translate="no">SpeakSmart</span>.
                </h1>
                <p class="max-w-xl text-base leading-8 text-muted-foreground sm:text-lg">
                  Keep your practice, progress, and tourism-focused Japanese lessons in one
                  calm workflow on desktop or mobile.
                </p>
              </div>
            </div>

            <div class="hidden lg:grid gap-4 sm:grid-cols-3">
              <Card v-for="item in infoCards" :key="item.title">
                <CardHeader>
                  <div class="flex size-10 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <component :is="item.icon" class="size-5" />
                  </div>
                  <CardTitle>{{ item.title }}</CardTitle>
                  <CardDescription>{{ item.copy }}</CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>

          <Card class="order-1 lg:order-2">
            <CardHeader>
              <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                Account access
              </p>
              <CardTitle class="text-balance font-(--font-display) text-4xl leading-none text-(--color-heading)">
                Sign in to <span translate="no">SpeakSmart</span>
              </CardTitle>
              <CardDescription>
                Use your email and password, or continue with Google.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert v-if="visibleError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Sign-in problem</AlertTitle>
                <AlertDescription>{{ visibleError }}</AlertDescription>
              </Alert>

              <form class="flex flex-col gap-4" novalidate @submit.prevent="handleEmailLogin">
                <div class="flex flex-col gap-2">
                  <Label for="login-email">Email</Label>
                  <Input
                    ref="emailInput"
                    id="login-email"
                    v-model="email"
                    name="email"
                    type="email"
                    inputmode="email"
                    placeholder="name@example.com"
                    autocomplete="email"
                    spellcheck="false"
                    :aria-describedby="fieldErrors.email ? 'login-email-error' : undefined"
                    :aria-invalid="Boolean(fieldErrors.email)"
                  />
                  <p
                    v-if="fieldErrors.email"
                    id="login-email-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.email }}
                  </p>
                </div>

                <div class="flex flex-col gap-2">
                  <Label for="login-password">Password</Label>
                  <div class="relative">
                    <Input
                      ref="passwordInput"
                      id="login-password"
                      v-model="password"
                      name="password"
                      :type="showPassword ? 'text' : 'password'"
                      placeholder="Enter your password"
                      autocomplete="current-password"
                      class="pr-11"
                      :aria-describedby="fieldErrors.password ? 'login-password-error' : undefined"
                      :aria-invalid="Boolean(fieldErrors.password)"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      class="absolute right-1 top-1/2 -translate-y-1/2"
                      :aria-label="showPassword ? 'Hide password' : 'Show password'"
                      @click="showPassword = !showPassword"
                    >
                      <EyeOff v-if="showPassword" />
                      <Eye v-else />
                    </Button>
                  </div>
                  <p
                    v-if="fieldErrors.password"
                    id="login-password-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.password }}
                  </p>
                </div>

                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm text-muted-foreground">
                    Use the same account you use for practice or teaching.
                  </p>
                </div>

                <Button variant="default" size="lg" type="submit" class="w-full" :disabled="submitDisabled">
                  <LoaderCircle v-if="loading" class="animate-spin" data-icon="inline-start" />
                  <span>{{ loading ? 'Signing in...' : 'Sign in' }}</span>
                </Button>
              </form>

              <div class="flex items-center gap-4 text-sm text-muted-foreground">
                <Separator class="flex-1" />
                <span>or</span>
                <Separator class="flex-1" />
              </div>

              <Button
                variant="outline"
                size="lg"
                class="w-full"
                :disabled="loading"
                @click="handleGoogleLogin"
              >
                Continue with Google
              </Button>
            </CardContent>

            <CardFooter class="flex-row items-center">
              <p class="text-sm text-muted-foreground">
                New to <span translate="no">SpeakSmart</span>?
              </p>
              <Button as-child variant="link">
                <RouterLink to="/signup">
                  Create an account
                </RouterLink>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch, type ComponentPublicInstance } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ArrowLeft,
  Building2,
  ChartColumn,
  Eye,
  EyeOff,
  LoaderCircle,
  Mic,
  Sparkles,
  TriangleAlert,
} from 'lucide-vue-next'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { useAuthRedirect } from '@/composables/useAuthRedirect'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const emailInput = ref<ComponentPublicInstance | null>(null)
const passwordInput = ref<ComponentPublicInstance | null>(null)
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const { redirectAfterAuth } = useAuthRedirect({
  onPageRestore: () => {
    loading.value = false
  },
})
const formError = ref<string | null>(null)
const fieldErrors = ref({
  email: null as string | null,
  password: null as string | null,
})

const infoCards = [
  {
    icon: Mic,
    title: 'Practice',
    copy: 'Return to guided speaking exercises without extra steps.',
  },
  {
    icon: ChartColumn,
    title: 'Progress',
    copy: 'Review scores and recent work from the same account.',
  },
  {
    icon: Building2,
    title: 'Course fit',
    copy: 'Keep everything tied to the tourism-learning flow.',
  },
]

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(() => loading.value)

function dismissError() {
  formError.value = null
  fieldErrors.value.email = null
  fieldErrors.value.password = null
  authStore.clearError()
}

function validateForm() {
  fieldErrors.value.email = email.value.trim() ? null : 'Enter your email.'
  fieldErrors.value.password = password.value ? null : 'Enter your password.'

  return !fieldErrors.value.email && !fieldErrors.value.password
}

function getInputElement(instance: ComponentPublicInstance | null) {
  return instance?.$el instanceof HTMLInputElement ? instance.$el : null
}

async function focusFirstInvalidField() {
  await nextTick()

  if (fieldErrors.value.email) {
    getInputElement(emailInput.value)?.focus()
    return
  }

  if (fieldErrors.value.password) {
    getInputElement(passwordInput.value)?.focus()
  }
}

watch(email, (value) => {
  if (value.trim()) fieldErrors.value.email = null
})

watch(password, (value) => {
  if (value) fieldErrors.value.password = null
})

async function handleEmailLogin() {
  dismissError()

  if (!validateForm()) {
    await focusFirstInvalidField()
    return
  }

  loading.value = true
  try {
    const result = await authStore.signInWithEmail(email.value, password.value)
    await redirectAfterAuth(result)
  } catch {
    // The auth store owns the user-facing error message.
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
  } catch {
    // The auth store owns the user-facing error message.
  } finally {
    loading.value = false
  }
}

</script>

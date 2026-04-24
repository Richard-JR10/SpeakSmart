<template>
  <section class="min-h-dvh bg-background text-foreground">
    <a
      href="#signup-main"
      class="sr-only absolute left-4 top-4 z-60 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-lg focus-visible:not-sr-only focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20"
    >
      Skip to main content
    </a>

    <main id="signup-main" tabindex="-1">
      <div class="mx-auto flex min-h-dvh w-full max-w-6xl items-center px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid w-full gap-6 lg:grid-cols-[minmax(0,1fr)_460px] lg:items-start">
          <div class="order-1 flex flex-col gap-6 lg:pt-8">
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
                  Create account
                </p>
                <h1 class="text-balance font-(--font-display) text-5xl leading-[0.95] tracking-[-0.04em] text-(--color-heading) sm:text-6xl">
                  Start your <span translate="no">SpeakSmart</span> journey with the right role.
                </h1>
                <p class="max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
                  Set up a student or instructor account in one clean flow. The page stays
                  simple, but the account is ready for practice, tracking, and class use.
                </p>
              </div>
            </div>

            <div class="hidden lg:grid gap-4 sm:grid-cols-3">
              <Card v-for="item in highlightCards" :key="item.title">
                <CardHeader>
                  <div class="flex size-10 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <component :is="item.icon" class="size-5" />
                  </div>
                  <CardTitle>{{ item.title }}</CardTitle>
                  <CardDescription>{{ item.copy }}</CardDescription>
                </CardHeader>
              </Card>
            </div>

            <Card class="hidden lg:block border-none bg-primary text-primary-foreground shadow-sm">
              <CardHeader class="gap-3">
                <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary-foreground/70">
                  Account setup
                </p>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-primary-foreground">
                  Choose your role once, then move straight into practice or oversight.
                </CardTitle>
                <CardDescription class="text-primary-foreground/75">
                  Students use the account for lessons, attempts, and progress. Instructors
                  use it for analytics, flagged learners, and exercises.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          <Card class="order-1 lg:order-2">
            <CardHeader>
              <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                New account
              </p>
              <CardTitle class="text-balance font-(--font-display) text-4xl leading-none text-(--color-heading)">
                Sign up for <span translate="no">SpeakSmart</span>
              </CardTitle>
              <CardDescription>
                Choose your role, create a secure password, and continue with email or Google.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert v-if="visibleError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Signup problem</AlertTitle>
                <AlertDescription>{{ visibleError }}</AlertDescription>
              </Alert>

              <form class="flex flex-col gap-4" novalidate @submit.prevent="handleSignup">
                <div class="flex flex-col gap-2">
                  <Label for="signup-name">Name</Label>
                  <Input
                    ref="nameInput"
                    id="signup-name"
                    v-model="displayName"
                    name="name"
                    type="text"
                    autocomplete="name"
                    placeholder="Enter your full name"
                    :aria-describedby="fieldErrors.displayName ? 'signup-name-error' : undefined"
                    :aria-invalid="Boolean(fieldErrors.displayName)"
                  />
                  <p
                    v-if="fieldErrors.displayName"
                    id="signup-name-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.displayName }}
                  </p>
                </div>

                <div class="flex flex-col gap-2">
                  <Label for="signup-email">Email</Label>
                  <Input
                    ref="emailInput"
                    id="signup-email"
                    v-model="email"
                    name="email"
                    type="email"
                    inputmode="email"
                    autocomplete="email"
                    spellcheck="false"
                    placeholder="name@example.com"
                    :aria-describedby="fieldErrors.email ? 'signup-email-error' : undefined"
                    :aria-invalid="Boolean(fieldErrors.email)"
                  />
                  <p
                    v-if="fieldErrors.email"
                    id="signup-email-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.email }}
                  </p>
                </div>

                <div class="flex flex-col gap-2">
                  <Label>Role</Label>
                  <ToggleGroup
                    v-model="role"
                    type="single"
                    variant="outline"
                    class="grid w-full grid-cols-1 gap-3 sm:grid-cols-2"
                    :spacing="1"
                  >
                    <ToggleGroupItem
                      v-for="option in roleOptions"
                      :key="option.value"
                      :value="option.value"
                      class="h-full w-full flex-col justify-start items-start gap-1 rounded-xl px-4 py-4 whitespace-normal border-border bg-background text-left shadow-none transition data-[state=on]:border-primary data-[state=on]:bg-secondary data-[state=on]:text-primary hover:bg-muted"
                    >
                      <span class="text-sm font-semibold">
                        {{ option.label }}
                      </span>
                      <span
                        class="whitespace-normal text-xs leading-6"
                        :class="role === option.value ? 'text-primary/80' : 'text-muted-foreground'"
                      >
                        {{ option.copy }}
                      </span>
                    </ToggleGroupItem>
                  </ToggleGroup>
                  <p
                    v-if="fieldErrors.role"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.role }}
                  </p>
                </div>

                <div class="flex flex-col gap-2">
                  <Label for="signup-password">Password</Label>
                  <div class="relative">
                    <Input
                      ref="passwordInput"
                      id="signup-password"
                      v-model="password"
                      name="password"
                      :type="showPassword ? 'text' : 'password'"
                      autocomplete="new-password"
                      placeholder="Create a strong password"
                      class="pr-11"
                      :aria-describedby="fieldErrors.password ? 'signup-password-error' : 'password-guide'"
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
                    id="signup-password-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ fieldErrors.password }}
                  </p>
                </div>

                <div id="password-guide" class="flex flex-col gap-2">
                  <p class="text-xs font-semibold uppercase tracking-[0.14em] text-(--color-heading)">
                    Password requirements
                  </p>
                  <div class="grid gap-2 sm:grid-cols-2">
                    <div
                      v-for="item in passwordChecklist"
                      :key="item.label"
                      class="flex items-center gap-2"
                    >
                      <div
                        class="flex size-5 items-center justify-center rounded-full"
                        :class="item.met ? 'bg-secondary text-primary' : 'bg-border/60 text-muted-foreground'"
                      >
                        <Check v-if="item.met" class="size-3.5" />
                        <Dot v-else class="size-3.5" />
                      </div>
                      <span
                        class="text-xs leading-5"
                        :class="item.met ? 'text-(--color-heading)' : 'text-muted-foreground'"
                      >
                        {{ item.label }}
                      </span>
                    </div>
                  </div>
                </div>

                <Button variant="default" size="lg" type="submit" class="w-full" :disabled="submitDisabled">
                  <LoaderCircle v-if="isEmailLoading" class="animate-spin" data-icon="inline-start" />
                  <span>{{ isEmailLoading ? 'Creating account...' : 'Create account' }}</span>
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
                @click="handleGoogleSignup"
              >
                <LoaderCircle v-if="isGoogleLoading" class="animate-spin" data-icon="inline-start" />
                <span>{{ isGoogleLoading ? 'Continuing with Google...' : 'Continue with Google' }}</span>
              </Button>
            </CardContent>

            <CardFooter class="flex-row items-center">
              <p class="text-sm text-muted-foreground">
                Already have a <span translate="no">SpeakSmart</span> account?
              </p>
              <Button as-child variant="link">
                <RouterLink to="/login">
                  Sign in
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
  BookOpen,
  Check,
  ChartColumn,
  ClipboardCheck,
  Dot,
  Eye,
  EyeOff,
  LoaderCircle,
  Sparkles,
  TriangleAlert,
} from 'lucide-vue-next'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { useAuthRedirect } from '@/composables/useAuthRedirect'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const authStore = useAuthStore()

const nameInput = ref<ComponentPublicInstance | null>(null)
const emailInput = ref<ComponentPublicInstance | null>(null)
const passwordInput = ref<ComponentPublicInstance | null>(null)
const displayName = ref('')
const email = ref('')
const password = ref('')
const role = ref<UserRole | undefined>(undefined)
const showPassword = ref(false)
const loading = ref(false)
const activeAuthMethod = ref<'email' | 'google' | null>(null)
const { redirectAfterAuth } = useAuthRedirect({
  onPageRestore: () => {
    loading.value = false
    activeAuthMethod.value = null
  },
})
const formError = ref<string | null>(null)
const fieldErrors = ref({
  displayName: null as string | null,
  email: null as string | null,
  role: null as string | null,
  password: null as string | null,
})

const roleOptions: Array<{ value: UserRole; label: string; copy: string }> = [
  {
    value: 'student',
    label: 'Student',
    copy: 'Practice lessons, submit attempts, and follow your progress.',
  },
  {
    value: 'instructor',
    label: 'Instructor',
    copy: 'Review analytics, learners, and classroom exercises.',
  },
]

const highlightCards = [
  {
    icon: BookOpen,
    title: 'Role-based access',
    copy: 'Start with the right experience for student practice or instructor review.',
  },
  {
    icon: ChartColumn,
    title: 'Progress-ready',
    copy: 'Your account connects directly to scores, attempts, and tracking.',
  },
  {
    icon: ClipboardCheck,
    title: 'Simple setup',
    copy: 'Account creation stays short, responsive, and easy to complete on mobile.',
  },
]

const passwordChecklist = computed(() => [
  {
    label: 'At least 8 characters',
    met: password.value.length >= 8,
  },
  {
    label: 'At least one uppercase letter',
    met: /[A-Z]/.test(password.value),
  },
  {
    label: 'At least one number',
    met: /\d/.test(password.value),
  },
  {
    label: 'At least one special character',
    met: /[^A-Za-z0-9]/.test(password.value),
  },
])

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(() => loading.value || !role.value)
const isEmailLoading = computed(() => loading.value && activeAuthMethod.value === 'email')
const isGoogleLoading = computed(() => loading.value && activeAuthMethod.value === 'google')

function dismissError() {
  formError.value = null
  fieldErrors.value.displayName = null
  fieldErrors.value.email = null
  fieldErrors.value.role = null
  fieldErrors.value.password = null
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
  fieldErrors.value.displayName = displayName.value.trim() ? null : 'Enter your name.'
  fieldErrors.value.email = email.value.trim() ? null : 'Enter your email address.'
  fieldErrors.value.role = role.value ? null : 'Select a role.'
  fieldErrors.value.password = isPasswordValid(password.value)
    ? null
    : 'Password does not meet the required strength rules.'

  return (
    !fieldErrors.value.displayName &&
    !fieldErrors.value.email &&
    !fieldErrors.value.role &&
    !fieldErrors.value.password
  )
}

function getInputElement(instance: ComponentPublicInstance | null) {
  return instance?.$el instanceof HTMLInputElement ? instance.$el : null
}

async function focusFirstInvalidField() {
  await nextTick()

  if (fieldErrors.value.displayName) {
    getInputElement(nameInput.value)?.focus()
    return
  }

  if (fieldErrors.value.email) {
    getInputElement(emailInput.value)?.focus()
    return
  }

  if (fieldErrors.value.password) {
    getInputElement(passwordInput.value)?.focus()
  }
}

watch(displayName, (value) => {
  if (value.trim()) fieldErrors.value.displayName = null
})

watch(email, (value) => {
  if (value.trim()) fieldErrors.value.email = null
})

watch(role, (value) => {
  if (value) fieldErrors.value.role = null
})

watch(password, (value) => {
  if (value && isPasswordValid(value)) fieldErrors.value.password = null
})

async function handleSignup() {
  dismissError()

  if (!validateForm()) {
    await focusFirstInvalidField()
    return
  }

  loading.value = true
  activeAuthMethod.value = 'email'
  try {
    const result = await authStore.signUpWithEmail({
      displayName: displayName.value,
      email: email.value,
      password: password.value,
      role: role.value!,
    })
    await redirectAfterAuth(result)
  } catch {
    // The auth store owns the user-facing error message.
  } finally {
    loading.value = false
    activeAuthMethod.value = null
  }
}

async function handleGoogleSignup() {
  dismissError()

  loading.value = true
  activeAuthMethod.value = 'google'
  try {
    const result = await authStore.signInWithGoogle()
    await redirectAfterAuth(result)
  } catch {
    // The auth store owns the user-facing error message.
  } finally {
    loading.value = false
    activeAuthMethod.value = null
  }
}

</script>

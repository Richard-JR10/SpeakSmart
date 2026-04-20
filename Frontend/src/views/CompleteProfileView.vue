<template>
  <section class="relative min-h-dvh overflow-hidden bg-background text-foreground">
    <div
      class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(184,141,70,0.12),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(46,138,103,0.14),transparent_28%),linear-gradient(180deg,#faf7f0_0%,#f4f0e8_100%)]"
    />

    <main class="relative">
      <div class="mx-auto flex min-h-dvh w-full max-w-6xl items-center px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid w-full gap-6 lg:grid-cols-[minmax(0,1fr)_460px] lg:items-center">
          <div class="order-2 flex flex-col gap-6 lg:order-1 lg:pr-6">
            <Button as-child variant="outline" size="lg" class="w-fit">
              <RouterLink to="/login">
                <ArrowLeft data-icon="inline-start" />
                Sign in
              </RouterLink>
            </Button>

            <div class="flex flex-col gap-4">
              <div class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                <Sparkles class="size-5" />
              </div>

              <div class="flex flex-col gap-3">
                <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                  Complete profile
                </p>
                <h1 class="text-balance font-[var(--font-display)] text-5xl leading-[0.95] tracking-[-0.04em] text-[var(--color-heading)] sm:text-6xl">
                  Finish your <span translate="no">SpeakSmart</span> setup in one clean step.
                </h1>
                <p class="max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
                  Confirm the name attached to your account, choose the right role, and
                  continue directly into the workspace that matches how you will use the app.
                </p>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-3">
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

            <Card class="border-none bg-primary text-primary-foreground shadow-sm">
              <CardHeader class="gap-3">
                <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary-foreground/70">
                  Account access
                </p>
                <CardTitle class="font-[var(--font-display)] text-3xl leading-none text-primary-foreground">
                  Pick the role once, then move straight into practice or oversight.
                </CardTitle>
                <CardDescription class="text-primary-foreground/75">
                  Students continue to lessons, scoring, and progress. Instructors continue
                  to analytics, student monitoring, and exercise management.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          <Card class="order-1 border-border/80 bg-card/95 backdrop-blur lg:order-2">
            <CardHeader class="gap-3">
              <p class="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
                Finish setting up
              </p>
              <CardTitle class="text-balance font-[var(--font-display)] text-4xl leading-none text-[var(--color-heading)]">
                Complete your profile
              </CardTitle>
              <CardDescription>
                Use the name you want to see in <span translate="no">SpeakSmart</span>, then
                select the role for your account.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert v-if="visibleError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Profile setup problem</AlertTitle>
                <AlertDescription>{{ visibleError }}</AlertDescription>
              </Alert>

              <form class="flex flex-col gap-4" novalidate @submit.prevent="handleCompleteProfile">
                <div class="flex flex-col gap-2">
                  <Label for="complete-email">Signed-in account</Label>
                  <Input
                    id="complete-email"
                    :model-value="authStore.firebaseUser?.email ?? ''"
                    type="text"
                    disabled
                  />
                </div>

                <div class="flex flex-col gap-2">
                  <Label for="complete-name">Name</Label>
                  <Input
                    id="complete-name"
                    v-model.trim="displayName"
                    name="name"
                    type="text"
                    autocomplete="name"
                    placeholder="Enter your full name"
                    :aria-describedby="nameError ? 'complete-name-error' : 'complete-name-hint'"
                    :aria-invalid="Boolean(nameError)"
                  />
                  <p
                    v-if="nameError"
                    id="complete-name-error"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ nameError }}
                  </p>
                  <p
                    v-else
                    id="complete-name-hint"
                    class="text-sm text-muted-foreground"
                  >
                    This is the name shown in the app after setup.
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
                      class="h-full w-full flex-col items-start justify-start gap-2 rounded-xl px-4 py-4 text-left whitespace-normal border-border bg-background shadow-none transition data-[state=on]:border-primary data-[state=on]:bg-secondary data-[state=on]:text-primary hover:bg-muted"
                    >
                      <span class="text-sm font-semibold">
                        {{ option.label }}
                      </span>
                      <span
                        class="whitespace-normal text-left text-xs leading-6"
                        :class="role === option.value ? 'text-primary/80' : 'text-muted-foreground'"
                      >
                        {{ option.copy }}
                      </span>
                    </ToggleGroupItem>
                  </ToggleGroup>
                  <p
                    v-if="roleError"
                    class="text-sm font-medium text-destructive"
                  >
                    {{ roleError }}
                  </p>
                  <p
                    v-else
                    class="text-sm text-muted-foreground"
                  >
                    You will continue to the dashboard that matches the selected role.
                  </p>
                </div>

                <Button variant="default" size="lg" type="submit" class="w-full" :disabled="submitDisabled">
                  <LoaderCircle v-if="loading" class="animate-spin" data-icon="inline-start" />
                  <span>{{ loading ? 'Saving profile...' : 'Complete setup' }}</span>
                </Button>
              </form>
            </CardContent>

            <CardFooter class="flex-col items-start gap-4 border-t">
              <div class="flex w-full items-center gap-4 text-sm text-muted-foreground">
                <Separator class="flex-1" />
                <span>Need a different account?</span>
                <Separator class="flex-1" />
              </div>

              <div class="flex w-full flex-col gap-2 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
                <p>Signed in with the wrong account?</p>
                <Button variant="link" class="h-auto p-0" :disabled="loading" @click="handleSignOut">
                  <LogOut data-icon="inline-start" />
                  Sign out
                </Button>
              </div>
            </CardFooter>
          </Card>
        </div>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  ArrowLeft,
  BookOpen,
  ChartColumn,
  ClipboardCheck,
  LoaderCircle,
  LogOut,
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
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

type RoleOption = {
  value: UserRole
  label: string
  copy: string
}

type HighlightCard = {
  title: string
  copy: string
  icon: Component
}

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref(authStore.firebaseUser?.displayName?.trim() ?? '')
const role = ref<UserRole | undefined>(undefined)
const loading = ref(false)
const formError = ref<string | null>(null)
const nameError = ref<string | null>(null)
const roleError = ref<string | null>(null)

const roleOptions: RoleOption[] = [
  {
    value: 'student',
    label: 'Student',
    copy: 'Use guided lessons, attempts, scores, and progress tracking.',
  },
  {
    value: 'instructor',
    label: 'Instructor',
    copy: 'Use analytics dashboards, student oversight, and exercise tools.',
  },
]

const highlightCards: HighlightCard[] = [
  {
    icon: BookOpen,
    title: 'Practice-ready',
    copy: 'Start with the correct experience for speaking lessons and review.',
  },
  {
    icon: ChartColumn,
    title: 'Progress-aware',
    copy: 'Keep the account connected to role-specific tracking and insights.',
  },
  {
    icon: ClipboardCheck,
    title: 'Short setup',
    copy: 'Finish profile details without going through a long onboarding form.',
  },
]

const visibleError = computed(() => formError.value ?? authStore.error)
const submitDisabled = computed(() => loading.value || !displayName.value.trim())

watch(displayName, (value) => {
  if (value.trim()) {
    nameError.value = null
  }
})

watch(role, (value) => {
  if (value) {
    roleError.value = null
  }
})

function dismissError() {
  formError.value = null
  nameError.value = null
  roleError.value = null
  authStore.clearError()
}

async function handleCompleteProfile() {
  dismissError()

  if (!displayName.value.trim()) {
    nameError.value = 'Enter your name to finish setup.'
    return
  }

  if (!role.value) {
    roleError.value = 'Choose a role to finish setup.'
    return
  }

  loading.value = true
  try {
    await authStore.completeProfile({
      displayName: displayName.value.trim(),
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

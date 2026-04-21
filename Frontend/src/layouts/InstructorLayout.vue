<template>
  <div class="min-h-screen bg-background">
    <div class="flex min-h-screen">
      <aside
        :class="desktopSidebarClass"
        class="relative hidden h-screen overflow-visible border-r border-border/70 bg-card/90 transition-[width] duration-300 ease-in-out lg:sticky lg:top-0 lg:z-50 lg:flex lg:flex-col"
      >
        <Button
          variant="outline"
          size="icon"
          class="absolute top-6 right-0 hidden size-8 translate-x-1/2 rounded-full bg-background shadow-sm lg:inline-flex"
          @click="toggleSidebar"
        >
          <ChevronLeft v-if="!sidebarCollapsed" />
          <ChevronRight v-else />
          <span class="sr-only">Toggle sidebar</span>
        </Button>

        <div class="flex h-full flex-col overflow-hidden">
          <div class="border-b border-border/70 px-3 py-4">
            <div :class="desktopBrandClass">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground">
                S
              </div>

              <div :class="desktopBrandTextClass">
                <p class="truncate text-sm font-semibold text-(--color-heading)">
                  SpeakSmart
                </p>
                <p class="truncate text-xs text-muted-foreground">
                  Instructor Studio
                </p>
              </div>
            </div>

            <div class="mt-4 flex flex-col gap-2">
              <Label
                for="desktop-active-class"
                :class="desktopMetaLabelClass"
              >
                Active class
              </Label>
              <select
                id="desktop-active-class"
                :value="classesStore.activeClassId ?? ''"
                :class="desktopSelectClass"
                @change="handleClassChange"
              >
                <option value="" disabled>
                  {{ classSelectLabel }}
                </option>
                <option
                  v-for="item in classesStore.classes"
                  :key="item.class_id"
                  :value="item.class_id"
                >
                  {{ item.name }}
                </option>
              </select>
            </div>
          </div>

          <nav class="flex flex-1 flex-col gap-2 px-3 py-4" aria-label="Instructor navigation">
            <Button
              v-for="item in navItems"
              :key="item.name"
              as-child
              :variant="navButtonVariant(item.name)"
              :class="desktopNavButtonClass"
            >
              <RouterLink :to="item.to" :aria-label="item.label">
                <span class="flex size-10 shrink-0 items-center justify-center">
                  <component :is="item.icon" />
                </span>
                <span :class="desktopLabelClass">{{ item.label }}</span>
              </RouterLink>
            </Button>
          </nav>

          <div class="border-t border-border/70 p-3">
            <Button
              variant="outline"
              :class="desktopNavButtonClass"
              class="w-full"
              :aria-label="sidebarCollapsed ? 'Sign out' : undefined"
              @click="openSignOutDialog"
            >
              <span class="flex size-10 shrink-0 items-center justify-center">
                <LogOut />
              </span>
              <span :class="desktopLabelClass">Sign out</span>
            </Button>
          </div>
        </div>
      </aside>

      <div class="relative z-0 flex min-h-screen min-w-0 flex-1 flex-col">
        <header class="sticky top-0 z-20 border-b border-border/70 bg-background/90 backdrop-blur">
          <div class="flex flex-col gap-3 px-4 py-3 sm:px-6 lg:px-8">
            <div class="flex items-center gap-3 lg:hidden">
              <Sheet v-model:open="mobileNavOpen">
                <Button
                  variant="outline"
                  size="icon"
                  class="shrink-0 rounded-xl"
                  @click="mobileNavOpen = true"
                >
                  <Menu />
                  <span class="sr-only">Open navigation</span>
                </Button>

                <SheetContent side="left" class="w-[18rem] border-r border-border/70 bg-card p-0">
                  <SheetHeader class="border-b border-border/70 px-4 py-4 text-left">
                    <SheetTitle class="flex items-center gap-3 text-lg">
                      <span class="flex size-10 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground">
                        SS
                      </span>
                      <span class="flex flex-col">
                        <span class="font-semibold text-(--color-heading)">SpeakSmart</span>
                        <span class="text-xs font-normal text-muted-foreground">Instructor Studio</span>
                      </span>
                    </SheetTitle>
                    <SheetDescription class="sr-only">
                      Instructor navigation
                    </SheetDescription>
                  </SheetHeader>

                  <div class="flex h-full flex-col">
                    <div class="border-b border-border/70 px-4 py-4">
                      <Label
                        for="mobile-active-class"
                        class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground"
                      >
                        Active class
                      </Label>
                      <select
                        id="mobile-active-class"
                        :value="classesStore.activeClassId ?? ''"
                        class="mt-2 h-11 w-full rounded-xl border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition focus:border-primary"
                        @change="handleMobileClassChange"
                      >
                        <option value="" disabled>
                          {{ classSelectLabel }}
                        </option>
                        <option
                          v-for="item in classesStore.classes"
                          :key="item.class_id"
                          :value="item.class_id"
                        >
                          {{ item.name }}
                        </option>
                      </select>
                    </div>

                    <nav class="flex flex-1 flex-col gap-2 px-3 py-4" aria-label="Instructor navigation">
                      <Button
                        v-for="item in navItems"
                        :key="item.name"
                        as-child
                        :variant="navButtonVariant(item.name)"
                        class="h-11 w-full justify-start rounded-xl px-3"
                      >
                        <RouterLink :to="item.to" @click="mobileNavOpen = false">
                          <component :is="item.icon" data-icon="inline-start" />
                          <span>{{ item.label }}</span>
                        </RouterLink>
                      </Button>
                    </nav>

                    <div class="border-t border-border/70 p-3">
                      <Button
                        variant="outline"
                        class="h-11 w-full justify-start rounded-xl px-3"
                        @click="openSignOutDialog"
                      >
                        <LogOut data-icon="inline-start" />
                        <span>Sign out</span>
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>

              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-(--color-heading)">SpeakSmart</p>
                <p class="truncate text-xs text-muted-foreground">Instructor Studio</p>
              </div>
            </div>

            <div class="flex flex-wrap items-start justify-between gap-3">
              <div class="min-w-0">
                <h1 class="truncate font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ currentTitle }}
                </h1>
                <p class="mt-2 max-w-3xl text-sm leading-7 text-muted-foreground">
                  {{ currentDescription }}
                </p>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1">
                  Instructor workspace
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  <Building2 />
                  {{ classesStore.activeClass?.name ?? 'No active class' }}
                </Badge>
              </div>
            </div>

            <Alert v-if="classesStore.error" variant="destructive">
              <TriangleAlert />
              <AlertTitle>Class data unavailable</AlertTitle>
              <AlertDescription>{{ classesStore.error }}</AlertDescription>
            </Alert>
          </div>
        </header>

        <main class="flex-1">
          <div class="mx-auto flex w-full max-w-[1400px] min-w-0 flex-col gap-6 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
            <slot />
          </div>
        </main>
      </div>

      <DialogRoot v-model:open="signOutConfirm">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-border/80 bg-card shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95"
          >
            <div class="flex flex-col gap-5 p-6">
              <div class="flex items-start gap-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
                  <TriangleAlert />
                </div>

                <div class="min-w-0">
                  <DialogTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    Confirm Sign Out
                  </DialogTitle>
                  <DialogDescription class="mt-2 text-sm leading-6 text-muted-foreground">
                    You will need to sign in again to continue managing your classes and analytics.
                  </DialogDescription>
                </div>
              </div>

              <Alert v-if="signOutError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Sign out failed</AlertTitle>
                <AlertDescription>{{ signOutError }}</AlertDescription>
              </Alert>

              <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  class="w-full sm:w-auto"
                  :disabled="signingOut"
                  @click="signOutConfirm = false"
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  class="w-full sm:w-auto"
                  :disabled="signingOut"
                  @click="confirmSignOut"
                >
                  <LoaderCircle v-if="signingOut" class="animate-spin" data-icon="inline-start" />
                  <LogOut v-else data-icon="inline-start" />
                  <span>{{ signingOut ? 'Signing Out...' : 'Confirm Sign Out' }}</span>
                </Button>
              </div>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  BookMarked,
  Building2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LoaderCircle,
  LogOut,
  Menu,
  School,
  TriangleAlert,
  Users,
} from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'

type NavItem = {
  name: string
  label: string
  icon: Component
  to: string
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const SIDEBAR_COLLAPSED_KEY = 'instructor-layout-sidebar-collapsed'

const mobileNavOpen = ref(false)
const sidebarCollapsed = ref(getInitialSidebarCollapsed())
const signOutConfirm = ref(false)
const signingOut = ref(false)
const signOutError = ref<string | null>(null)

const navItems: NavItem[] = [
  { name: 'instructor-overview', label: 'Overview', icon: LayoutDashboard, to: '/instructor' },
  { name: 'instructor-students', label: 'Students', icon: Users, to: '/instructor/students' },
  { name: 'instructor-heatmap', label: 'Heatmap', icon: BookMarked, to: '/instructor/heatmap' },
  { name: 'instructor-exercises', label: 'Exercises', icon: ClipboardList, to: '/instructor/exercises' },
  { name: 'classes', label: 'Classes', icon: School, to: '/classes' },
]

const pageContent: Record<string, { title: string; description: string }> = {
  'instructor-overview': {
    title: 'Instructor Overview',
    description: 'Track class averages, recent activity, and the learners who need attention next.',
  },
  'instructor-students': {
    title: 'Student Directory',
    description: 'Search your roster, inspect individual progress, and review recent attempts without losing context.',
  },
  'instructor-heatmap': {
    title: 'Analytics Heatmap',
    description: 'Compare module performance across pronunciation categories to focus coaching effort faster.',
  },
  'instructor-exercises': {
    title: 'Practice Assignments',
    description: 'Create phrase-based assignments, review submissions, and release teacher feedback in one workspace.',
  },
  classes: {
    title: 'Classes',
    description: 'Create classes, regenerate join codes, and change your active roster context when needed.',
  },
}

const currentPage = computed(
  () => pageContent[String(route.name ?? '')] ?? pageContent['instructor-overview'],
)
const currentTitle = computed(() => currentPage.value.title)
const currentDescription = computed(() => currentPage.value.description)
const classSelectLabel = computed(() => {
  if (classesStore.loading) return 'Loading classes...'
  if (classesStore.classes.length) return 'Select a class'
  return 'No classes yet'
})

const desktopSidebarClass = computed(() => [
  sidebarCollapsed.value ? 'w-16' : 'w-72',
])

const desktopBrandClass = computed(() => [
  'grid w-full grid-cols-[2.5rem_minmax(0,1fr)] items-center gap-0',
])

const desktopBrandTextClass = computed(() => [
  'flex min-w-0 flex-col justify-center overflow-hidden px-2 text-left transition-[max-width,opacity] duration-300 ease-in-out',
  sidebarCollapsed.value ? 'max-w-0 opacity-0 pointer-events-none' : 'max-w-40 opacity-100',
])

const desktopMetaLabelClass = computed(() => [
  'text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground transition-[max-width,opacity] duration-300 ease-in-out',
  sidebarCollapsed.value ? 'max-w-0 opacity-0 pointer-events-none overflow-hidden' : 'max-w-40 opacity-100',
])

const desktopSelectClass = computed(() => [
  'h-11 w-full rounded-xl border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition focus:border-primary',
  sidebarCollapsed.value ? 'pointer-events-none hidden' : 'block',
])

const desktopNavButtonClass = computed(() => [
  'grid h-fit w-full grid-cols-[2.5rem_minmax(0,1fr)] items-center justify-start gap-0 overflow-hidden rounded-xl p-0 text-left transition-none',
])

const desktopLabelClass = computed(() => [
  'flex h-10 min-w-0 items-center overflow-hidden whitespace-nowrap text-left transition-[max-width,opacity] duration-300 ease-in-out',
  sidebarCollapsed.value ? 'max-w-0 opacity-0 pointer-events-none' : 'max-w-32 opacity-100',
])

onMounted(async () => {
  if (authStore.profile?.role === 'instructor') {
    try {
      await classesStore.ensureLoaded()
    } catch {
      // The store already exposes a user-facing error state.
    }
  }
})

watch(
  () => route.fullPath,
  () => {
    mobileNavOpen.value = false
    signOutConfirm.value = false
  },
)

watch(sidebarCollapsed, (value) => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(value))
})

watch(signOutConfirm, (open) => {
  if (open) return
  if (signingOut.value) return
  signOutError.value = null
})

function navButtonVariant(name: string): 'default' | 'ghost' {
  return route.name === name ? 'default' : 'ghost'
}

function getInitialSidebarCollapsed() {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true'
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleClassChange(event: Event) {
  const target = event.target as HTMLSelectElement
  classesStore.setActiveClass(target.value || null)
}

function handleMobileClassChange(event: Event) {
  handleClassChange(event)
  mobileNavOpen.value = false
}

function openSignOutDialog() {
  mobileNavOpen.value = false
  signOutError.value = null
  signOutConfirm.value = true
}

async function confirmSignOut() {
  signOutError.value = null
  signingOut.value = true

  try {
    await authStore.signOut()
    classesStore.reset()
    signOutConfirm.value = false
    await router.push('/')
  } catch (error) {
    console.error('Failed to sign out:', error)
    signOutError.value = 'We could not sign you out right now. Please try again.'
  } finally {
    signingOut.value = false
  }
}
</script>

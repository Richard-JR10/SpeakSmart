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
          class="absolute top-6 right-0 z-60 hidden size-8 translate-x-1/2 rounded-full bg-background shadow-sm lg:inline-flex"
          @click="toggleSidebar"
        >
          <ChevronLeft v-if="!sidebarCollapsed" />
          <ChevronRight v-else />
          <span class="sr-only">Toggle sidebar</span>
        </Button>

        <div class="flex h-full flex-col overflow-hidden">
          <div :class="desktopBrandClass" class="border-b border-border/70">
            <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground">
              S
            </div>

            <div :class="desktopBrandTextClass">
              <p class="w-fit truncate text-sm font-semibold text-(--color-heading)">
                SpeakSmart
              </p>
              <p class="w-fit truncate text-xs text-muted-foreground">
                Student Portal
              </p>
            </div>
          </div>

          <nav class="flex flex-1 flex-col gap-2 px-3 py-4" aria-label="Student navigation">
            <Button
              v-for="item in navItems"
              :key="item.section"
              as-child
              :variant="navButtonVariant(item.section)"
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
              @click="handleSignOut"
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
          <div class="flex items-center gap-3 px-4 py-2 sm:px-6 lg:px-8">
            <Sheet v-model:open="mobileNavOpen">
              <Button
                variant="outline"
                size="icon"
                class="shrink-0 rounded-xl lg:hidden"
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
                      <span class="text-xs font-normal text-muted-foreground">Student Portal</span>
                    </span>
                  </SheetTitle>
                  <SheetDescription class="sr-only">
                    Student navigation
                  </SheetDescription>
                </SheetHeader>

                <div class="flex h-full flex-col">
                  <nav class="flex flex-1 flex-col gap-2 px-3 py-4" aria-label="Student navigation">
                    <Button
                      v-for="item in navItems"
                      :key="item.section"
                      as-child
                      :variant="navButtonVariant(item.section)"
                      class="h-11 w-full justify-start rounded-xl px-3"
                    >
                      <RouterLink :to="item.to" @click="mobileNavOpen = false">
                        <span class="flex size-10 shrink-0 items-center justify-center">
                          <component :is="item.icon" />
                        </span>
                        <span>{{ item.label }}</span>
                      </RouterLink>
                    </Button>
                  </nav>

                  <div class="border-t border-border/70 p-3">
                    <Button variant="outline" class="h-11 w-full justify-start rounded-xl px-3" @click="handleSignOut">
                      <span class="flex size-10 shrink-0 items-center justify-center">
                        <LogOut />
                      </span>
                      <span>Sign out</span>
                    </Button>
                  </div>
                </div>
              </SheetContent>
            </Sheet>

            <Button
              v-if="props.showBack"
              variant="outline"
              size="icon"
              class="shrink-0 rounded-xl"
              @click="router.back()"
            >
              <ChevronLeft />
              <span class="sr-only">Go back</span>
            </Button>

            <div class="min-w-0">
              <h1 class="truncate font-(--font-display) text-3xl leading-none text-(--color-heading)">
                {{ props.title }}
              </h1>
              <p class="mt-2 max-w-3xl text-sm leading-7 text-muted-foreground">
                {{ currentSectionCopy }}
              </p>
            </div>
          </div>
        </header>

        <main class="flex-1">
          <div :class="contentClass">
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
                    You will need to sign in again to continue.
                  </DialogDescription>
                </div>
              </div>

              <Alert v-if="signOutError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Sign out failed</AlertTitle>
                <AlertDescription>{{ signOutError }}</AlertDescription>
              </Alert>

              <Alert v-else variant="destructive">
                <TriangleAlert />
                <AlertTitle>Leaving this session</AlertTitle>
                <AlertDescription>
                  Use sign out when you are done practicing, especially on a shared computer.
                </AlertDescription>
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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  BookOpen,
  ChartColumn,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  House,
  LoaderCircle,
  LogOut,
  Menu,
  School,
  Settings,
  TriangleAlert,
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
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'

type StudentSection = 'home' | 'lessons' | 'assignments' | 'progress' | 'classes' | 'settings'

type NavItem = {
  section: StudentSection
  label: string
  icon: Component
  to: string
}

const props = defineProps<{
  title: string
  showBack?: boolean
  wide?: boolean
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const SIDEBAR_COLLAPSED_KEY = 'student-layout-sidebar-collapsed'

const mobileNavOpen = ref(false)
const sidebarCollapsed = ref(getInitialSidebarCollapsed())
const signOutConfirm = ref(false)
const signingOut = ref(false)
const signOutError = ref<string | null>(null)

const navItems: NavItem[] = [
  { section: 'home', label: 'Home', icon: House, to: '/home' },
  { section: 'lessons', label: 'Lessons', icon: BookOpen, to: '/lessons' },
  { section: 'assignments', label: 'Assignments', icon: ClipboardList, to: '/assignments' },
  { section: 'progress', label: 'Progress', icon: ChartColumn, to: '/progress' },
  { section: 'classes', label: 'Classes', icon: School, to: '/classes' },
  { section: 'settings', label: 'Settings', icon: Settings, to: '/settings' },
]

const sectionRouteNames: Record<StudentSection, string[]> = {
  home: ['home'],
  lessons: ['lessons', 'practice', 'results'],
  assignments: ['assignments', 'assignment-submission'],
  progress: ['progress'],
  classes: ['classes'],
  settings: ['settings'],
}

const sectionCopy: Record<StudentSection, string> = {
  home: 'See your current pace, recent attempts, and next speaking checkpoint at a glance.',
  lessons: 'Move through guided practice modules and keep your topic progress easy to scan.',
  assignments: 'Open assigned work, record submissions, and review teacher-released feedback in one place.',
  progress: 'Review accuracy trends, streaks, and module performance in one student view.',
  classes: 'Join classes, review where you are enrolled, and keep classroom access easy to manage.',
  settings: 'Manage your profile, preferences, and account access without leaving the app shell.',
}

const activeSection = computed<StudentSection>(() => {
  const routeName = String(route.name ?? '')

  if (sectionRouteNames.lessons.includes(routeName)) {
    return 'lessons'
  }

  if (sectionRouteNames.progress.includes(routeName)) {
    return 'progress'
  }

  if (sectionRouteNames.assignments.includes(routeName)) {
    return 'assignments'
  }

  if (sectionRouteNames.classes.includes(routeName)) {
    return 'classes'
  }

  if (sectionRouteNames.settings.includes(routeName)) {
    return 'settings'
  }

  return 'home'
})

const currentSectionCopy = computed(() => sectionCopy[activeSection.value])

const contentClass = computed(() => [
  'mx-auto flex w-full min-w-0 flex-col gap-6 px-4 py-4 sm:px-6 sm:py-6 lg:px-8',
  props.wide ? 'max-w-[1400px]' : 'max-w-5xl',
])

const desktopSidebarClass = computed(() => [
  sidebarCollapsed.value ? 'w-16' : 'w-72',
])

const desktopBrandClass = computed(() => [
  'grid w-full grid-cols-[2.5rem_minmax(0,1fr)] items-center gap-0 px-3 py-4',
])

const desktopBrandTextClass = computed(() => [
  'flex p-2 min-w-0 flex-col justify-center overflow-hidden whitespace-nowrap text-left transition-[max-width,opacity] duration-300 ease-in-out',
  sidebarCollapsed.value ? 'max-w-0 opacity-0 pointer-events-none' : 'max-w-40 opacity-100',
])

const desktopNavButtonClass = computed(() => [
  'grid h-fit w-full grid-cols-[2.5rem_minmax(0,1fr)] items-center justify-start gap-0 overflow-hidden rounded-xl p-0 text-left transition-none',
])

const desktopLabelClass = computed(() => [
  'flex h-10 min-w-0 items-center overflow-hidden whitespace-nowrap text-left transition-[max-width,opacity] duration-300 ease-in-out',
  sidebarCollapsed.value ? 'max-w-0 opacity-0 pointer-events-none' : 'max-w-32 opacity-100',
])

watch(
  () => route.fullPath,
  () => {
    mobileNavOpen.value = false
  },
)

watch(sidebarCollapsed, (value) => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(value))
})

function navButtonVariant(section: StudentSection): 'default' | 'ghost' {
  return activeSection.value === section ? 'default' : 'ghost'
}

function getInitialSidebarCollapsed() {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true'
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleSignOut() {
  mobileNavOpen.value = false
  signOutError.value = null
  signOutConfirm.value = true
}

async function confirmSignOut() {
  signOutError.value = null
  signingOut.value = true

  try {
    await authStore.signOut()
    signOutConfirm.value = false
    await router.push('/')
  } catch (error) {
    console.error('Failed to sign out:', error)
    signOutError.value = 'We could not sign you out right now. Please try again.'
  } finally {
    signingOut.value = false
  }
}

watch(signOutConfirm, (open) => {
  if (open) return
  if (signingOut.value) return
  signOutError.value = null
})

watch(
  () => route.fullPath,
  () => {
    signOutConfirm.value = false
  },
)
</script>

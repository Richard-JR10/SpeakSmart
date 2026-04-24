<template>
  <StudentLayout title="Lessons">
    <div class="flex flex-col gap-4">
      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Course path
            </Badge>
            <Badge variant="outline" class="rounded-full px-3 py-1">
              {{ filteredModules.length }} shown
            </Badge>
          </div>

          <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
            <div class="flex flex-col gap-2">
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading) sm:text-4xl">
                Japanese modules
              </CardTitle>
              <CardDescription class="max-w-3xl text-sm leading-7 text-foreground/80 sm:text-base">
                Search modules, start from the first phrase, or continue from your latest
                recorded phrase in that topic.
              </CardDescription>
            </div>

            <div class="grid gap-3 grid-cols-1 h-full">
              <div class="grid grid-cols-3 gap-3">
                <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                  <CardHeader class="gap-1 px-4 py-4 h-full">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Modules
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ modulesStore.modules.length }}
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                  <CardHeader class="gap-1 px-4 py-4 h-full">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Started
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ startedModules }}
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                  <CardHeader class="gap-1 px-4 py-4 h-full">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Average
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ overallAverageText }}
                    </CardTitle>
                  </CardHeader>
                </Card>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card class="border-border/80 bg-card/95 py-3">
        <CardContent class="flex flex-col gap-3 px-4 py-4 sm:px-5">
          <div class="relative">
            <Search class="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-muted-foreground" />
            <Input
              v-model="searchQuery"
              type="text"
              placeholder="Search modules, topics, or descriptions…"
              class="h-11 pr-11 pl-10"
            />
            <Button
              v-if="searchQuery"
              type="button"
              variant="ghost"
              size="icon-sm"
              class="absolute top-1/2 right-1 -translate-y-1/2"
              @click="searchQuery = ''"
            >
              <X />
              <span class="sr-only">Clear search</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card v-if="isLoading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-56 flex-col items-center justify-center gap-4 py-10 text-center">
          <LoaderCircle class="animate-spin text-primary" />
          <div class="flex flex-col gap-1">
            <p class="font-semibold text-(--color-heading)">Loading lessons</p>
            <p class="text-sm text-muted-foreground">
              Preparing modules, phrases, progress, and recent attempts.
            </p>
          </div>
        </CardContent>
      </Card>

      <Alert v-else-if="modulesStore.error || progressStore.error || attemptsStore.error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Lesson data could not fully load</AlertTitle>
        <AlertDescription>
          {{ modulesStore.error ?? progressStore.error ?? attemptsStore.error }}
        </AlertDescription>
      </Alert>

      <Alert v-else-if="!modulesStore.modules.length">
        <BookOpen />
        <AlertTitle>No modules available yet</AlertTitle>
        <AlertDescription>
          Lesson content will appear here once the course modules are available.
        </AlertDescription>
      </Alert>

      <Alert v-else-if="!filteredModules.length">
        <Search />
        <AlertTitle>No matching modules</AlertTitle>
        <AlertDescription>
          Try a different keyword or clear the search to see the full lesson list.
        </AlertDescription>
      </Alert>

      <div v-else class="grid gap-3">
        <Card
          v-for="module in filteredModules"
          :key="module.module_id"
          class="border-border/80 bg-card/95 transition-colors hover:border-primary/35 py-3"
        >
          <CardContent class="flex flex-col gap-4 px-4 py-4 sm:px-5">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div class="flex min-w-0 items-start gap-3">
                <div class="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-secondary text-primary">
                  <component :is="moduleIcon(module.module_id)" />
                </div>

                <div class="flex min-w-0 flex-col gap-2">
                  <div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
                    <p class="truncate text-lg font-semibold text-(--color-heading)">
                      {{ module.title }}
                    </p>
                    <div class="flex flex-wrap gap-2">
                      <Badge variant="secondary" class="rounded-full px-2.5 py-1">
                        {{ phraseCount(module.module_id) }} phrases
                      </Badge>
                      <Badge
                        v-if="moduleProgress(module.module_id)?.total_attempts"
                        :variant="progressPercent(module.module_id) >= 70 ? 'default' : 'outline'"
                        class="rounded-full px-2.5 py-1"
                      >
                        {{ moduleProgress(module.module_id)?.average_accuracy.toFixed(0) }}% average
                      </Badge>
                    </div>
                  </div>

                  <p class="text-sm leading-6 text-foreground/80">
                    {{ module.description || 'Practice a guided set of tourism-focused phrases in this module.' }}
                  </p>

                  <p class="text-sm leading-6 text-muted-foreground">
                    {{ progressSummaryCopy(module.module_id) }}
                  </p>
                </div>
              </div>

              <div class="grid gap-2 rounded-2xl border border-border/70 bg-muted/35 px-3 py-3 lg:min-w-56">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-semibold text-muted-foreground">Progress</span>
                  <span class="text-sm font-semibold text-(--color-heading)">
                    {{ progressPercent(module.module_id).toFixed(0) }}%
                  </span>
                </div>

                <div class="h-2 overflow-hidden rounded-full bg-border/70">
                  <div
                    class="h-full rounded-full bg-primary transition-[width]"
                    :style="{ width: `${progressPercent(module.module_id)}%` }"
                  />
                </div>

                <div class="flex flex-wrap gap-2">
                  <Badge variant="outline" class="rounded-full px-2.5 py-1">
                    {{ moduleProgress(module.module_id)?.total_attempts ?? 0 }} attempts
                  </Badge>
                  <Badge
                    v-if="latestAttemptForModule(module.module_id)"
                    variant="outline"
                    class="rounded-full px-2.5 py-1"
                  >
                    Latest phrase ready
                  </Badge>
                </div>
              </div>
            </div>

            <Separator />

          <div class="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
              <p class="text-sm leading-6 text-muted-foreground">
                {{ actionCopy(module.module_id) }}
              </p>

              <Button
                size="sm"
                class="w-full sm:w-auto"
                :disabled="!phraseCount(module.module_id)"
                @click="openModuleAction(module.module_id)"
              >
                <Play v-if="!canContinueModule(module.module_id)" data-icon="inline-start" />
                <ArrowRight v-else data-icon="inline-start" />
                <span>{{ canContinueModule(module.module_id) ? 'Continue Module' : 'Start Module' }}</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  BookOpen,
  Building2,
  Globe2,
  Hand,
  LoaderCircle,
  MapPinned,
  Play,
  Search,
  ShieldAlert,
  TriangleAlert,
  UtensilsCrossed,
  X,
} from 'lucide-vue-next'

import StudentLayout from '@/layouts/StudentLayout.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import { useAuthStore } from '@/stores/auth'
import { useAttemptsStore } from '@/stores/attempts'
import { setLastPracticeSession } from '@/utils/studentSession'

const MODULE_ICONS: Record<string, Component> = {
  module_greetings: Hand,
  module_hotel: Building2,
  module_directions: MapPinned,
  module_food: UtensilsCrossed,
  module_emergency: ShieldAlert,
  module_tour_guide: Globe2,
}

const router = useRouter()
const modulesStore = useModulesStore()
const progressStore = useProgressStore()
const attemptsStore = useAttemptsStore()
const authStore = useAuthStore()

const searchQuery = ref('')

const isLoading = computed(() =>
  modulesStore.loading || progressStore.loading || attemptsStore.loading,
)
const normalizedSearch = computed(() => searchQuery.value.trim().toLowerCase())
const filteredModules = computed(() => {
  if (!normalizedSearch.value) return modulesStore.modules

  return modulesStore.modules.filter((module) => {
    const haystack = [
      module.title,
      module.description ?? '',
      module.module_id,
    ]
      .join(' ')
      .toLowerCase()

    return haystack.includes(normalizedSearch.value)
  })
})
const startedModules = computed(() =>
  modulesStore.modules.filter((module) => (moduleProgress(module.module_id)?.total_attempts ?? 0) > 0).length,
)
const overallAverageText = computed(() => {
  const average = progressStore.dashboard?.overall_average
  return average == null ? '--' : `${average.toFixed(0)}%`
})

function moduleIcon(moduleId: string) {
  return MODULE_ICONS[moduleId] ?? BookOpen
}

function phraseCount(moduleId: string) {
  return modulesStore.getPhrasesForModule(moduleId).length
}

function moduleProgress(moduleId: string) {
  return progressStore.getProgressForModule(moduleId)
}

function progressPercent(moduleId: string) {
  const progress = moduleProgress(moduleId)
  if (!progress) return 0
  return Math.min(100, progress.average_accuracy)
}

function latestAttemptForModule(moduleId: string) {
  const phrases = modulesStore.getPhrasesForModule(moduleId)
  if (!phrases.length) return null

  const phraseIds = new Set(phrases.map((phrase) => phrase.phrase_id))
  return attemptsStore.attemptHistory.find((attempt) => phraseIds.has(attempt.phrase_id)) ?? null
}

function canContinueModule(moduleId: string) {
  return Boolean(latestAttemptForModule(moduleId))
}

function progressSummaryCopy(moduleId: string) {
  const progress = moduleProgress(moduleId)
  if (!progress || progress.total_attempts === 0) {
    return 'No attempts yet. Start this module to create your first accuracy signal.'
  }

  const latestAttempt = latestAttemptForModule(moduleId)
  if (latestAttempt) {
    return `Last attempted phrase on ${formatShortDate(latestAttempt.attempted_at)}. Resume from that exact prompt or restart the module.`
  }

  if (progress.last_attempted_at) {
    return `Last active ${formatShortDate(progress.last_attempted_at)} with ${progress.total_attempts} recorded attempts.`
  }

  return `${progress.total_attempts} recorded attempts so far in this module.`
}

function actionCopy(moduleId: string) {
  if (canContinueModule(moduleId)) {
    return 'Continue from the most recent phrase you attempted in this module.'
  }

  return 'Start this module from the first phrase and build your speaking baseline in this topic.'
}

function formatShortDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

async function startModule(moduleId: string) {
  await modulesStore.fetchPhrases(moduleId)
  const phrases = modulesStore.getPhrasesForModule(moduleId)
  if (phrases.length > 0) {
    setLastPracticeSession(authStore.uid, {
      moduleId,
      phraseId: phrases[0].phrase_id,
    })
    await router.push(`/practice/${moduleId}/${phrases[0].phrase_id}`)
  }
}

async function continueModule(moduleId: string) {
  await modulesStore.fetchPhrases(moduleId)
  const latestAttempt = latestAttemptForModule(moduleId)

  if (latestAttempt) {
    setLastPracticeSession(authStore.uid, {
      moduleId,
      phraseId: latestAttempt.phrase_id,
    })
    await router.push(`/practice/${moduleId}/${latestAttempt.phrase_id}`)
    return
  }

  await startModule(moduleId)
}

async function openModuleAction(moduleId: string) {
  if (canContinueModule(moduleId)) {
    await continueModule(moduleId)
    return
  }

  await startModule(moduleId)
}

onMounted(async () => {
  await modulesStore.fetchModules()
  await Promise.all(modulesStore.modules.map((module) => modulesStore.fetchPhrases(module.module_id)))
  await Promise.all([
    progressStore.fetchDashboard(authStore.uid!),
    attemptsStore.fetchHistory(authStore.uid!),
  ])
})
</script>

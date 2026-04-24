<template>
  <StudentLayout title="Dashboard" wide>
    <div class="mx-auto flex w-full max-w-7xl flex-col gap-5">
      <LoadingSpinner
        v-if="progressStore.loading && !dashboard"
        full-screen
        message="Loading your dashboard..."
      />

      <template v-else>
        <Alert v-if="progressStore.error || attemptsStore.error" variant="destructive">
          <AlertTriangle />
          <AlertTitle>Dashboard data could not fully load</AlertTitle>
          <AlertDescription>
            {{ progressStore.error ?? attemptsStore.error }}
          </AlertDescription>
        </Alert>

        <section
          class="overflow-hidden rounded-3xl border border-border/80 bg-[radial-gradient(circle_at_15%_20%,rgba(184,141,70,0.16),transparent_28%),linear-gradient(135deg,#fffdf9_0%,#edf4ef_54%,#fbf6ea_100%)] shadow-(--shadow-soft)"
          aria-labelledby="student-home-title"
        >
          <div class="grid gap-6 p-4 sm:p-6 lg:grid-cols-[minmax(0,1fr)_22rem] xl:grid-cols-[minmax(0,1fr)_25rem]">
            <div class="flex min-w-0 flex-col justify-between gap-8">
              <div class="flex flex-col gap-6">
                <div class="flex items-center gap-3">
                  <LogoMark size="lg" class="border-primary/20 bg-card/90" />
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-(--color-heading)" translate="no">
                      SpeakSmart
                    </p>
                    <p class="text-sm text-muted-foreground">
                      Learning studio
                    </p>
                  </div>
                </div>

                <div class="max-w-3xl">
                  <h2
                    id="student-home-title"
                    class="text-balance font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl lg:text-6xl"
                  >
                    Good {{ timeOfDay }}, {{ studentName }}.
                  </h2>
                  <p class="mt-4 text-pretty text-base leading-8 text-muted-foreground sm:text-lg">
                    Start the next speaking set, clear teacher-assigned work, and use your score patterns to practice with purpose.
                  </p>
                </div>
              </div>

              <div class="flex flex-col gap-3 sm:flex-row">
                <Button size="lg" class="min-h-12 rounded-2xl px-5" @click="continueSession">
                  <component :is="continueModule ? RefreshCcw : Mic" data-icon="inline-start" />
                  <span>{{ continueModule ? 'Resume practice' : 'Start practicing' }}</span>
                </Button>
                <Button variant="outline" size="lg" class="min-h-12 rounded-2xl bg-card/80 px-5" @click="router.push('/assignments')">
                  <ClipboardList data-icon="inline-start" />
                  <span>View assignments</span>
                </Button>
              </div>
            </div>

            <aside class="rounded-3xl border border-border/70 bg-card/80 p-4 shadow-xs">
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-muted-foreground">
                    Overall average
                  </p>
                  <p class="mt-2 font-(--font-display) text-6xl leading-none text-(--color-heading)">
                    {{ dashboard?.overall_average?.toFixed(0) ?? '--' }}%
                  </p>
                  <p class="mt-3 text-sm leading-6 text-muted-foreground">
                    {{ latestAttempt ? `Last submission ${formatRelativeDate(latestAttempt.attempted_at)}` : 'Your first score will appear here.' }}
                  </p>
                </div>
                <span class="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                  <CircleGauge class="size-5" aria-hidden="true" />
                </span>
              </div>

              <div class="mt-5 grid gap-3">
                <div class="h-2 overflow-hidden rounded-full bg-secondary">
                  <div
                    class="h-full rounded-full bg-primary"
                    :style="{ width: overallAverageWidth }"
                  />
                </div>

                <div class="grid grid-cols-3 gap-2">
                  <div class="rounded-2xl bg-secondary/60 p-3">
                    <p class="text-2xl font-semibold tabular-nums text-(--color-heading)">
                      {{ activeModulesCount }}
                    </p>
                    <p class="mt-1 text-xs leading-5 text-muted-foreground">
                      Active modules
                    </p>
                  </div>
                  <div class="rounded-2xl bg-secondary/60 p-3">
                    <p class="text-2xl font-semibold tabular-nums text-(--color-heading)">
                      {{ pendingAssignmentsCount }}
                    </p>
                    <p class="mt-1 text-xs leading-5 text-muted-foreground">
                      Pending
                    </p>
                  </div>
                  <div class="rounded-2xl bg-secondary/60 p-3">
                    <p class="text-2xl font-semibold tabular-nums text-(--color-heading)">
                      {{ releasedAssignmentPhrases }}
                    </p>
                    <p class="mt-1 text-xs leading-5 text-muted-foreground">
                      Released
                    </p>
                  </div>
                </div>

                <Badge v-if="weeklyDeltaText" :variant="weeklyDeltaVariant" class="mt-1 w-fit rounded-full px-3 py-1">
                  {{ weeklyDeltaText }}
                </Badge>
              </div>
            </aside>
          </div>
        </section>

        <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Student practice metrics">
          <div
            v-for="item in metricCards"
            :key="item.label"
            class="rounded-2xl border border-border/70 bg-card/90 p-4 shadow-xs transition-transform duration-200 ease-out hover:-translate-y-0.5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex min-w-0 flex-col gap-2">
                <p class="text-sm font-semibold text-muted-foreground">
                  {{ item.label }}
                </p>
                <p class="truncate font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ item.value }}
                </p>
                <p class="text-pretty text-sm leading-6 text-muted-foreground">
                  {{ item.copy }}
                </p>
              </div>
              <span :class="['flex size-10 shrink-0 items-center justify-center rounded-2xl', item.iconClass]">
                <component :is="item.icon" class="size-5" aria-hidden="true" />
              </span>
            </div>
          </div>
        </section>

        <div class="grid items-stretch gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(22rem,0.85fr)]">
          <Card class="order-1 flex h-full border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1">
                  Next session
                </Badge>
                <Clock3 class="size-5 text-muted-foreground" aria-hidden="true" />
              </div>
              <div class="flex flex-col gap-2">
                <CardTitle class="text-balance font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ continueModule ? continueModule.title : 'Choose your first module' }}
                </CardTitle>
                <CardDescription>
                  {{ continueModule ? 'Return to your most recently active topic and keep building repetition.' : 'Pick a module to begin your first guided pronunciation set.' }}
                </CardDescription>
              </div>
            </CardHeader>

            <CardContent class="flex flex-1 flex-col">
              <div v-if="continueModule" class="flex flex-1 flex-col justify-between gap-5 rounded-2xl border border-border/70 bg-muted/40 p-4">
                <div class="flex min-w-0 items-start gap-4">
                  <span class="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-secondary text-primary">
                    <component :is="moduleIcon(continueModule.module_id)" class="size-5" aria-hidden="true" />
                  </span>
                  <div class="flex min-w-0 flex-col gap-2">
                    <p class="text-pretty text-sm leading-6 text-muted-foreground">
                      {{ continueSessionCopy }}
                    </p>
                    <p class="text-xs font-medium text-muted-foreground">
                      {{ continueSessionSource }}
                    </p>
                  </div>
                </div>

                <div class="grid gap-3 sm:grid-cols-2">
                  <div class="rounded-2xl border border-border/60 bg-background/70 p-3">
                    <p class="text-xs font-semibold text-muted-foreground">
                      Session type
                    </p>
                    <p class="mt-1 text-sm font-semibold text-(--color-heading)">
                      Short speaking set
                    </p>
                  </div>
                  <div class="rounded-2xl border border-border/60 bg-background/70 p-3">
                    <p class="text-xs font-semibold text-muted-foreground">
                      Next action
                    </p>
                    <p class="mt-1 text-sm font-semibold text-(--color-heading)">
                      Record next phrase
                    </p>
                  </div>
                </div>
              </div>

              <Alert v-else class="flex-1">
                <BookOpen />
                <AlertTitle>No recent module yet</AlertTitle>
                <AlertDescription>
                  Start with any lesson module and your quick-return shortcut will appear here.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button class="w-full rounded-2xl md:w-auto" @click="continueSession">
                <ArrowRight data-icon="inline-start" />
                <span>{{ continueModule ? 'Open module' : 'Browse lessons' }}</span>
              </Button>
            </CardFooter>
          </Card>

            <Card class="order-3 border-border/80 bg-card/95 shadow-(--shadow-soft) xl:col-span-2">
              <CardHeader class="gap-3">
                <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start">
                  <div class="flex min-w-0 flex-col gap-3">
                    <div class="flex flex-wrap items-center gap-3">
                      <Badge variant="secondary" class="w-fit rounded-full px-3 py-1">
                        Teacher assignments
                      </Badge>
                      <ClipboardList class="size-5 text-muted-foreground" aria-hidden="true" />
                    </div>
                    <div class="flex flex-col gap-2">
                      <CardTitle class="text-balance font-(--font-display) text-2xl leading-none text-(--color-heading) sm:text-3xl">
                        Assigned practice queue
                      </CardTitle>
                      <CardDescription>
                        Teacher-assigned phrases stay separate from normal practice scores.
                      </CardDescription>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 gap-2 sm:w-64">
                    <div :class="['rounded-2xl border p-3', pendingSummaryCardClass]">
                      <p :class="['text-xs font-semibold', pendingSummaryLabelClass]">
                        Pending
                      </p>
                      <p class="mt-2 font-(--font-display) text-3xl leading-none">
                        {{ pendingAssignmentsCount }}
                      </p>
                    </div>
                    <div :class="['rounded-2xl border p-3', releasedSummaryCardClass]">
                      <p :class="['text-xs font-semibold', releasedSummaryLabelClass]">
                        Released
                      </p>
                      <p class="mt-2 font-(--font-display) text-3xl leading-none">
                        {{ releasedAssignmentPhrases }}
                      </p>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent class="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_180px]">
                <div class="flex flex-col gap-3">
                  <LoadingSpinner v-if="assignmentsLoading" size="sm" />

                  <Alert v-else-if="assignmentsError" variant="destructive">
                    <AlertTriangle />
                    <AlertTitle>Assignments could not load</AlertTitle>
                    <AlertDescription>
                      {{ assignmentsError }}
                    </AlertDescription>
                  </Alert>

                  <template v-else-if="assignmentPreview.length">
                    <div
                      v-for="assignment in assignmentPreview"
                      :key="assignment.exercise_id"
                      class="grid gap-3 rounded-2xl border border-border/70 bg-muted/25 p-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center"
                    >
                      <div class="flex min-w-0 flex-col gap-2">
                        <div class="flex flex-wrap items-center gap-2">
                          <p class="font-semibold text-(--color-heading)">
                            {{ assignment.title }}
                          </p>
                          <Badge
                            variant="outline"
                            :class="assignmentStatusClass(assignment)"
                          >
                            {{ assignment.completed_at ? 'Submitted' : assignment.is_overdue ? 'Overdue' : 'Open' }}
                          </Badge>
                        </div>

                        <p class="text-sm leading-6 text-muted-foreground">
                          {{ submittedPhraseCount(assignment) }}/{{ assignment.phrases.length }} phrases submitted
                          <span v-if="assignment.due_date">
                            , due {{ formatDueDate(assignment.due_date) }}
                          </span>
                        </p>
                      </div>

                      <Badge
                        variant="outline"
                        :class="releasedPhraseBadgeClass(assignment)"
                      >
                        {{ releasedPhraseCount(assignment) }} released
                      </Badge>
                    </div>
                  </template>

                  <Alert v-else>
                    <BookOpen />
                    <AlertTitle>No teacher assignments yet</AlertTitle>
                    <AlertDescription>
                      Assigned work from your teachers will appear here once it is sent to your account.
                    </AlertDescription>
                  </Alert>
                </div>

                <div class="rounded-2xl border border-dashed border-border/80 bg-background/70 p-4">
                  <div class="flex flex-col gap-3">
                    <span class="flex size-10 items-center justify-center rounded-2xl bg-secondary text-primary">
                      <FileCheck2 class="size-5" aria-hidden="true" />
                    </span>
                    <p class="text-sm leading-6 text-muted-foreground">
                      Record pending phrases or review released feedback.
                    </p>
                    <Button class="w-full rounded-2xl lg:px-3" @click="router.push('/assignments')">
                      <span>Open</span>
                      <ArrowRight data-icon="inline-end" />
                      <span class="sr-only">Assignments</span>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

          <Card class="order-2 h-full border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1">
                  Focus area
                </Badge>
                <Target class="size-5 text-muted-foreground" aria-hidden="true" />
              </div>
              <div class="flex flex-col gap-2">
                <CardTitle class="text-balance font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  What deserves your next repetition
                </CardTitle>
                <CardDescription>
                  Focus modules help you raise your overall average faster than spreading effort randomly.
                </CardDescription>
              </div>
            </CardHeader>

            <CardContent class="flex flex-1 flex-col gap-4">
              <Alert
                v-if="dashboard?.weakest_module_id"
                class="border-amber-200 bg-amber-50 text-amber-950"
              >
                <Target />
                <AlertTitle>{{ weakestModuleTitle }}</AlertTitle>
                <AlertDescription class="text-amber-900">
                  {{ weakestModuleTitle }} is currently averaging
                  {{ dashboard.weakest_module_score?.toFixed(0) }}%.
                </AlertDescription>
              </Alert>

              <Alert v-else class="border-sky-200 bg-sky-50 text-sky-950">
                <Sparkles />
                <AlertTitle>Focus module not available yet</AlertTitle>
                <AlertDescription class="text-sky-900">
                  Complete a few speaking checks and the dashboard will identify where extra reps help most.
                </AlertDescription>
              </Alert>

              <div :class="['rounded-2xl border p-4', focusPlanClass]">
                <div class="flex flex-col gap-2">
                  <p :class="['text-xs font-semibold', focusPlanLabelClass]">
                    Repetition plan
                  </p>
                  <p class="text-lg font-semibold">
                    {{ dashboard?.weakest_module_id ? `Start with ${weakestModuleTitle}` : 'Build enough signal first' }}
                  </p>
                  <p :class="['text-sm leading-6', focusPlanCopyClass]">
                    {{ dashboard?.weakest_module_id
                      ? 'Practice the lowest-scoring topic next so the dashboard recommendation stays action-oriented.'
                      : 'After a few completed recordings, this card will point to the topic that needs the clearest next rep.' }}
                  </p>
                </div>
              </div>
            </CardContent>

            <CardFooter class="border-t">
              <Button
                variant="outline"
                :disabled="!dashboard?.weakest_module_id"
                class="w-full rounded-2xl sm:w-auto"
                @click="practiceWeakest"
              >
                <Mic data-icon="inline-start" />
                <span>Practice focus area</span>
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1">
                  Module atlas
                </Badge>
                <BookOpen class="size-5 text-muted-foreground" aria-hidden="true" />
              </div>
              <CardTitle class="text-balance font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Where you sound strongest
              </CardTitle>
              <CardDescription>
                Ranked by accuracy so you can see which topics feel natural and which need more reps.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-1">
              <template v-if="rankedModules.length">
                <template v-for="(summary, index) in rankedModules" :key="summary.module_id">
                  <div class="flex flex-col gap-3 rounded-2xl p-3 sm:flex-row sm:items-start sm:justify-between">
                    <div class="flex min-w-0 items-start gap-3">
                      <span class="flex size-10 items-center justify-center rounded-2xl bg-secondary text-primary">
                        <component :is="moduleIcon(summary.module_id)" class="size-5" aria-hidden="true" />
                      </span>
                      <div class="flex min-w-0 flex-col gap-2">
                        <p class="font-semibold text-(--color-heading)">
                          {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                        </p>
                        <p class="text-sm text-muted-foreground">
                          {{ summary.total_attempts }} attempts recorded
                        </p>
                      </div>
                    </div>

                    <Badge
                      variant="outline"
                      :class="scoreBadgeClass(summary.average_accuracy)"
                    >
                      {{ summary.average_accuracy.toFixed(0) }}%
                    </Badge>
                  </div>
                  <Separator v-if="index < rankedModules.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <ChartColumn />
                <AlertTitle>No module ranking yet</AlertTitle>
                <AlertDescription>
                  Complete a module to build your first accuracy leaderboard.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button variant="outline" class="w-full rounded-2xl sm:w-auto" @click="router.push('/lessons')">
                <BookOpen data-icon="inline-start" />
                <span>Explore all modules</span>
              </Button>
            </CardFooter>
          </Card>

          <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1">
                  Recent work
                </Badge>
                <MessageSquareText class="size-5 text-muted-foreground" aria-hidden="true" />
              </div>
              <CardTitle class="text-balance font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Latest speaking checks
              </CardTitle>
              <CardDescription>
                Keep an eye on your most recent pronunciations and how they are landing.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-1">
              <LoadingSpinner v-if="attemptsStore.loading" size="sm" />

              <template v-else-if="recentAttempts.length">
                <template v-for="(attempt, index) in recentAttempts" :key="attempt.attempt_id">
                  <div class="flex flex-col gap-3 rounded-2xl p-3 sm:flex-row sm:items-start sm:justify-between">
                    <div class="flex min-w-0 flex-col gap-2">
                      <p class="font-semibold text-(--color-heading)">{{ attempt.phrase_id }}</p>
                      <p class="text-sm text-muted-foreground">
                        {{ formatAttemptDate(attempt.attempted_at) }}
                      </p>
                    </div>
                    <Badge
                      variant="outline"
                      :class="scoreBadgeClass(attempt.accuracy_score)"
                    >
                      {{ attempt.accuracy_score.toFixed(0) }}%
                    </Badge>
                  </div>
                  <Separator v-if="index < recentAttempts.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <Mic />
                <AlertTitle>No attempts yet</AlertTitle>
                <AlertDescription>
                  Start with a lesson and submit your first recording to populate this list.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button class="w-full rounded-2xl sm:w-auto" @click="router.push('/lessons')">
                <Mic data-icon="inline-start" />
                <span>Start a new session</span>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </template>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { computed, onMounted, ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Building2,
  ChartColumn,
  CircleGauge,
  ClipboardList,
  Clock3,
  FileCheck2,
  Flame,
  Globe2,
  Hand,
  MapPinned,
  MessageSquareText,
  Mic,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  Target,
  Trophy,
  UtensilsCrossed,
} from 'lucide-vue-next'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import LogoMark from '@/components/shared/LogoMark.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { getStudentAssignments } from '@/api/assignments'
import { useAttemptsStore } from '@/stores/attempts'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import {
  getLastPracticeSession,
  setLastPracticeSession,
  type LastPracticeSession,
} from '@/utils/studentSession'
import type { ProgressSummary, StudentAssignment } from '@/types'

const MODULE_ICONS: Record<string, Component> = {
  module_greetings: Hand,
  module_hotel: Building2,
  module_directions: MapPinned,
  module_food: UtensilsCrossed,
  module_emergency: ShieldCheck,
  module_tour_guide: Globe2,
}

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const progressStore = useProgressStore()
const modulesStore = useModulesStore()
const attemptsStore = useAttemptsStore()
const assignmentsLoading = shallowRef(false)
const assignmentsError = shallowRef<string | null>(null)
const studentAssignments = ref<StudentAssignment[]>([])
const lastPracticeSession = ref<LastPracticeSession | null>(null)

const dashboard = computed(() => progressStore.dashboard)
const overallAverageWidth = computed(() => {
  const average = Math.min(Math.max(dashboard.value?.overall_average ?? 0, 0), 100)
  return `${average}%`
})
const latestAttempt = computed(() => attemptsStore.attemptHistory[0] ?? null)
const recentAttempts = computed(() => attemptsStore.attemptHistory.slice(0, 4))
const weeklyAccuracy = computed(() => dashboard.value?.weekly_accuracy.slice(-6) ?? [])
const studentName = computed(() => authStore.profile?.display_name ?? 'Student')
const pendingAssignmentsCount = computed(() =>
  studentAssignments.value.filter((assignment) => !assignment.completed_at).length,
)
const assignmentPreview = computed(() =>
  [
    ...studentAssignments.value.filter((assignment) => !assignment.completed_at),
    ...studentAssignments.value.filter((assignment) => assignment.completed_at),
  ].slice(0, 3),
)
const releasedAssignmentPhrases = computed(() =>
  studentAssignments.value.flatMap((assignment) => assignment.phrases)
    .filter((phrase) => phrase.released_at).length,
)

const timeOfDay = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'morning'
  if (hour < 18) return 'afternoon'
  return 'evening'
})

const latestProgressModule = computed(() => {
  const attemptedModules = (dashboard.value?.progress_by_module ?? []).filter(
    (summary) => summary.total_attempts > 0 && summary.last_attempted_at,
  )

  if (!attemptedModules.length) return null

  const lastProgress = [...attemptedModules].sort(
    (a, b) =>
      new Date(b.last_attempted_at ?? 0).getTime()
      - new Date(a.last_attempted_at ?? 0).getTime(),
  )[0]

  return modulesStore.getModuleById(lastProgress?.module_id) ?? null
})

const rememberedModule = computed(() => {
  if (!lastPracticeSession.value?.moduleId) return null
  return modulesStore.getModuleById(lastPracticeSession.value.moduleId) ?? null
})

const continueModule = computed(() => rememberedModule.value ?? latestProgressModule.value)

const continueProgress = computed(() => {
  if (!continueModule.value) return null
  return progressStore.getProgressForModule(continueModule.value.module_id)
})

const continueSessionCopy = computed(() => {
  if (!continueModule.value) return ''

  if (rememberedModule.value) {
    const attemptCount = continueProgress.value?.total_attempts ?? 0
    return attemptCount > 0
      ? `${attemptCount} attempts logged in this module.`
      : 'You opened this module recently. Start a recording to create its first progress signal.'
  }

  return `${continueProgress.value?.total_attempts ?? 0} attempts logged${
    continueProgress.value?.last_attempted_at
      ? `, last active ${formatRelativeDate(continueProgress.value.last_attempted_at)}`
      : ''
  }.`
})

const continueSessionSource = computed(() => {
  if (!continueModule.value) return ''
  return rememberedModule.value ? 'Last opened lesson' : 'Latest recorded attempt'
})

const activeModulesCount = computed(
  () =>
    dashboard.value?.progress_by_module.filter((summary) => summary.total_attempts > 0).length ?? 0,
)

const rankedModules = computed(() =>
  [...(dashboard.value?.progress_by_module ?? [])]
    .sort((a, b) => {
      if (b.average_accuracy === a.average_accuracy) {
        return b.total_attempts - a.total_attempts
      }
      return b.average_accuracy - a.average_accuracy
    })
    .slice(0, 4),
)

const strongestModule = computed<ProgressSummary | null>(() => rankedModules.value[0] ?? null)

const strongestModuleTitle = computed(() => {
  if (!strongestModule.value) return 'Warming up'
  return modulesStore.getModuleById(strongestModule.value.module_id)?.title ?? strongestModule.value.module_id
})

const weakestModuleTitle = computed(() => {
  if (!dashboard.value?.weakest_module_id) return ''
  return modulesStore.getModuleById(dashboard.value.weakest_module_id)?.title ?? ''
})

const weeklyDelta = computed(() => {
  const weeks = weeklyAccuracy.value.filter((week) => week.attempt_count > 0)
  if (weeks.length < 2) return null
  return weeks[weeks.length - 1].average_accuracy - weeks[weeks.length - 2].average_accuracy
})

const weeklyDeltaText = computed(() => {
  if (weeklyDelta.value == null) return null
  const prefix = weeklyDelta.value > 0 ? '+' : ''
  return `${prefix}${weeklyDelta.value.toFixed(1)}% from last week`
})

const weeklyDeltaVariant = computed(() => {
  if (weeklyDelta.value == null) return 'outline'
  if (weeklyDelta.value < 0) return 'destructive'
  if (weeklyDelta.value === 0) return 'secondary'
  return 'default'
})

const focusPlanClass = computed(() =>
  dashboard.value?.weakest_module_id
    ? 'border-amber-200 bg-amber-50 text-amber-950'
    : 'border-sky-200 bg-sky-50 text-sky-950',
)

const focusPlanLabelClass = computed(() =>
  dashboard.value?.weakest_module_id ? 'text-amber-800' : 'text-sky-800',
)

const focusPlanCopyClass = computed(() =>
  dashboard.value?.weakest_module_id ? 'text-amber-900' : 'text-sky-900',
)

const pendingSummaryCardClass = computed(() =>
  pendingAssignmentsCount.value > 0
    ? 'border-amber-200 bg-amber-50 text-amber-950'
    : 'border-border/70 bg-muted/35 text-card-foreground',
)

const pendingSummaryLabelClass = computed(() =>
  pendingAssignmentsCount.value > 0 ? 'text-amber-800' : 'text-muted-foreground',
)

const releasedSummaryCardClass = computed(() =>
  releasedAssignmentPhrases.value > 0
    ? 'border-emerald-200 bg-emerald-50 text-emerald-950'
    : 'border-border/70 bg-muted/35 text-card-foreground',
)

const releasedSummaryLabelClass = computed(() =>
  releasedAssignmentPhrases.value > 0 ? 'text-emerald-800' : 'text-muted-foreground',
)

const metricCards = computed(() => [
  {
    label: 'Streak',
    value: `${dashboard.value?.streak_days ?? 0}`,
    copy: (dashboard.value?.streak_days ?? 0) > 0 ? 'days in a row' : 'start a daily rhythm',
    icon: Flame,
    iconClass: 'bg-amber-50 text-amber-800 ring-1 ring-amber-200',
  },
  {
    label: 'Attempts',
    value: `${dashboard.value?.total_attempts ?? 0}`,
    copy: 'submitted speaking checks',
    icon: Mic,
    iconClass: 'bg-secondary text-primary ring-1 ring-primary/15',
  },
  {
    label: 'Modules active',
    value: `${activeModulesCount.value}`,
    copy: 'topics you have already touched',
    icon: BookOpen,
    iconClass: 'bg-sky-50 text-sky-800 ring-1 ring-sky-200',
  },
  {
    label: 'Strongest module',
    value: strongestModuleTitle.value,
    copy: strongestModule.value
      ? `${strongestModule.value.average_accuracy.toFixed(0)}% average accuracy`
      : 'Complete a few reps to unlock this insight.',
    icon: Trophy,
    iconClass: 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200',
  },
])

function scoreBadgeClass(score: number) {
  if (score >= 85) {
    return 'rounded-full border-emerald-700 bg-emerald-700 px-3 py-1 text-white'
  }
  if (score >= 70) {
    return 'rounded-full border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-950'
  }
  if (score >= 55) {
    return 'rounded-full border-amber-300 bg-amber-50 px-3 py-1 text-amber-950'
  }
  return 'rounded-full border-red-200 bg-red-50 px-3 py-1 text-red-950'
}

function assignmentStatusClass(assignment: StudentAssignment) {
  if (assignment.completed_at) {
    return 'rounded-full border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-950'
  }
  if (assignment.is_overdue) {
    return 'rounded-full border-red-700 bg-red-700 px-2.5 py-1 text-white'
  }
  return 'rounded-full border-amber-300 bg-amber-50 px-2.5 py-1 text-amber-950'
}

function releasedPhraseBadgeClass(assignment: StudentAssignment) {
  return releasedPhraseCount(assignment) > 0
    ? 'rounded-full border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-950'
    : 'rounded-full border-border/70 bg-card px-2.5 py-1 text-card-foreground'
}

function formatAttemptDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatRelativeDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function formatDueDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function submittedPhraseCount(assignment: StudentAssignment) {
  return assignment.phrases.filter((phrase) => phrase.submitted_at).length
}

function releasedPhraseCount(assignment: StudentAssignment) {
  return assignment.phrases.filter((phrase) => phrase.released_at).length
}

function moduleIcon(moduleId: string) {
  return MODULE_ICONS[moduleId] ?? BookOpen
}

async function loadStudentAssignments(uid: string) {
  assignmentsError.value = null
  studentAssignments.value = await getStudentAssignments(uid)
}

async function openModule(moduleId?: string | null) {
  if (!moduleId) {
    await router.push('/lessons')
    return
  }

  const rememberedPhraseId = lastPracticeSession.value?.moduleId === moduleId
    ? lastPracticeSession.value.phraseId
    : null
  if (rememberedPhraseId) {
    setLastPracticeSession(authStore.uid, {
      moduleId,
      phraseId: rememberedPhraseId,
    })
    await router.push(`/practice/${moduleId}/${rememberedPhraseId}`)
    return
  }

  await modulesStore.fetchPhrases(moduleId)
  const phrases = modulesStore.getPhrasesForModule(moduleId)

  if (phrases.length) {
    setLastPracticeSession(authStore.uid, {
      moduleId,
      phraseId: phrases[0].phrase_id,
    })
    await router.push(`/practice/${moduleId}/${phrases[0].phrase_id}`)
    return
  }

  await router.push('/lessons')
}

async function continueSession() {
  await openModule(continueModule.value?.module_id)
}

async function practiceWeakest() {
  await openModule(dashboard.value?.weakest_module_id)
}

onMounted(async () => {
  const uid = authStore.uid!
  assignmentsLoading.value = true

  try {
    await Promise.all([
      modulesStore.fetchModules(),
      progressStore.fetchDashboard(uid),
      attemptsStore.fetchHistory(uid),
      classesStore.ensureLoaded(),
    ])
    lastPracticeSession.value = getLastPracticeSession(uid)
    await loadStudentAssignments(uid)
  } catch (error) {
    console.error('Failed to load student dashboard assignments:', error)
    assignmentsError.value = 'We could not load your teacher assignments right now.'
  } finally {
    assignmentsLoading.value = false
  }
})
</script>

<template>
  <StudentLayout title="Dashboard" wide>
    <div class="flex flex-col gap-5">
      <LoadingSpinner
        v-if="progressStore.loading && !dashboard"
        full-screen
        message="Loading your dashboard..."
      />

      <template v-else>
        <Alert v-if="progressStore.error || attemptsStore.error" variant="destructive">
          <AppIcon name="alert" :size="18" />
          <AlertTitle>Dashboard data could not fully load</AlertTitle>
          <AlertDescription>
            {{ progressStore.error ?? attemptsStore.error }}
          </AlertDescription>
        </Alert>

        <Card>
          <CardHeader class="flex flex-col gap-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Student dashboard
              </Badge>
              <Badge v-if="weeklyDeltaText" :variant="weeklyDeltaVariant" class="rounded-full px-3 py-1">
                {{ weeklyDeltaText }}
              </Badge>
            </div>

            <div class="grid gap-5 lg:grid-cols-[minmax(0,1.25fr)_260px] lg:items-start">
              <div class="flex min-w-0 flex-col gap-4">
                <div class="flex flex-col gap-3">
                  <CardTitle class="text-balance font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
                    Good {{ timeOfDay }}, {{ authStore.profile?.display_name ?? 'Student' }}
                  </CardTitle>
                  <CardDescription class="max-w-3xl text-base leading-8">
                    Practice with short, repeatable speaking checks and keep your
                    progress visible across modules, attempts, and weekly rhythm.
                  </CardDescription>
                </div>

                <div class="flex flex-col gap-3 sm:flex-row">
                  <Button size="lg" @click="continueSession">
                    <AppIcon :name="continueModule ? 'refresh' : 'mic'" :size="18" data-icon="inline-start" />
                    <span>{{ continueModule ? 'Resume practice' : 'Start practicing' }}</span>
                  </Button>
                  <Button variant="outline" size="lg" @click="router.push('/progress')">
                    <AppIcon name="chart" :size="18" data-icon="inline-start" />
                    <span>Open progress</span>
                  </Button>
                </div>
              </div>

              <Card class="border-dashed">
                <CardHeader class="gap-2">
                  <p class="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Overall average
                  </p>
                  <CardTitle class="font-(--font-display) text-5xl leading-none text-(--color-heading)">
                    {{ dashboard?.overall_average?.toFixed(0) ?? '--' }}%
                  </CardTitle>
                  <CardDescription>
                    {{ latestAttempt ? `Last submission ${formatRelativeDate(latestAttempt.attempted_at)}` : 'Your latest speaking check will appear here.' }}
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </CardHeader>

          <CardContent class="grid gap-4 lg:grid-cols-4">
            <Card v-for="item in metricCards" :key="item.label" class="gap-0 shadow-none">
              <CardHeader class="gap-2">
                <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  {{ item.label }}
                </p>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ item.value }}
                </CardTitle>
                <CardDescription>
                  {{ item.copy }}
                </CardDescription>
              </CardHeader>
            </Card>
          </CardContent>
        </Card>

        <div class="grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)]">
          <Card>
            <CardHeader class="flex flex-col gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Next session
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Continue where your speech rhythm left off
              </CardTitle>
              <CardDescription>
                {{ continueModule ? 'Return to your most recently active topic and keep building repetition.' : 'Pick a module to begin your first guided pronunciation set.' }}
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-4">
              <div v-if="continueModule" class="flex min-w-0 items-start gap-4 rounded-xl border bg-muted/50 p-4">
                <span class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
                  <AppIcon :name="moduleIconName(continueModule.module_id)" :size="22" />
                </span>
                <div class="flex min-w-0 flex-col gap-2">
                  <p class="text-lg font-semibold text-(--color-heading)">
                    {{ continueModule.title }}
                  </p>
                  <p class="text-sm leading-7 text-muted-foreground">
                    {{ continueProgress?.total_attempts ?? 0 }} attempts logged
                    <span v-if="continueProgress?.last_attempted_at">
                      , last active {{ formatRelativeDate(continueProgress.last_attempted_at) }}
                    </span>
                  </p>
                </div>
              </div>

              <Alert v-else>
                <AppIcon name="book" :size="18" />
                <AlertTitle>No recent module yet</AlertTitle>
                <AlertDescription>
                  Start with any lesson module and your quick-return shortcut will appear here.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button @click="continueSession">
                <AppIcon name="forward" :size="18" data-icon="inline-start" />
                <span>{{ continueModule ? 'Open module' : 'Browse lessons' }}</span>
              </Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader class="flex flex-col gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Focus area
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                What deserves your next repetition
              </CardTitle>
              <CardDescription>
                Focus modules help you raise your overall average faster than spreading effort randomly.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-4">
              <Alert v-if="dashboard?.weakest_module_id">
                <AppIcon name="alert" :size="18" />
                <AlertTitle>{{ weakestModuleTitle }}</AlertTitle>
                <AlertDescription>
                  {{ weakestModuleTitle }} is currently averaging
                  {{ dashboard.weakest_module_score?.toFixed(0) }}%.
                </AlertDescription>
              </Alert>

              <Alert v-else>
                <AppIcon name="spark" :size="18" />
                <AlertTitle>Focus module not available yet</AlertTitle>
                <AlertDescription>
                  Complete a few speaking checks and the dashboard will identify where extra reps help most.
                </AlertDescription>
              </Alert>

              <div class="grid gap-3 sm:grid-cols-2">
                <Card class="gap-0 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      Strongest module
                    </p>
                    <CardTitle class="text-xl text-(--color-heading)">
                      {{ strongestModuleTitle }}
                    </CardTitle>
                    <CardDescription>
                      {{ strongestModule ? `${strongestModule.average_accuracy.toFixed(0)}% average accuracy` : 'Finish a module to unlock this insight.' }}
                    </CardDescription>
                  </CardHeader>
                </Card>

                <Card class="gap-0 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      Weekly rhythm
                    </p>
                    <CardTitle class="text-xl text-(--color-heading)">
                      {{ weeklyAccuracy.length ? `${weeklyAccuracy.length} tracked weeks` : 'No trend yet' }}
                    </CardTitle>
                    <CardDescription>
                      {{ weeklyAccuracy.length ? 'Short, frequent practice makes your trend steadier.' : 'Weekly rhythm appears after your first completed week.' }}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
            </CardContent>

            <CardFooter class="border-t">
              <Button
                variant="outline"
                :disabled="!dashboard?.weakest_module_id"
                @click="practiceWeakest"
              >
                <AppIcon name="mic" :size="18" data-icon="inline-start" />
                <span>Practice focus area</span>
              </Button>
            </CardFooter>
          </Card>
        </div>

        <Card>
          <CardHeader class="flex flex-col gap-3">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div class="flex flex-col gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Teacher assignments
                </Badge>
                <div class="flex flex-col gap-2">
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    Assignment work stays separate from practice
                  </CardTitle>
                  <CardDescription>
                    Record assigned phrases in the dedicated Assignments tab and wait for teacher review there instead of using the normal practice results flow.
                  </CardDescription>
                </div>
              </div>

              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ pendingAssignmentsCount }} pending
              </Badge>
            </div>
          </CardHeader>

          <CardContent class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px] lg:items-start">
            <div class="flex flex-col gap-3">
              <LoadingSpinner v-if="assignmentsLoading" size="sm" />

              <Alert v-else-if="assignmentsError" variant="destructive">
                <AppIcon name="alert" :size="18" />
                <AlertTitle>Assignments could not load</AlertTitle>
                <AlertDescription>
                  {{ assignmentsError }}
                </AlertDescription>
              </Alert>

              <template v-else-if="assignmentPreview.length">
                <template
                  v-for="(assignment, index) in assignmentPreview"
                  :key="assignment.exercise_id"
                >
                  <div class="flex items-start justify-between gap-4 rounded-xl p-3">
                    <div class="flex min-w-0 flex-col gap-2">
                      <div class="flex flex-wrap items-center gap-2">
                        <p class="font-semibold text-(--color-heading)">
                          {{ assignment.title }}
                        </p>
                        <Badge
                          :variant="assignment.completed_at ? 'secondary' : assignment.is_overdue ? 'destructive' : 'outline'"
                          class="rounded-full px-2.5 py-1"
                        >
                          {{ assignment.completed_at ? 'Submitted' : assignment.is_overdue ? 'Overdue' : 'Open' }}
                        </Badge>
                      </div>

                      <p class="text-sm leading-7 text-muted-foreground">
                        {{ submittedPhraseCount(assignment) }}/{{ assignment.phrases.length }} phrases submitted
                        <span v-if="assignment.due_date">
                          , due {{ formatDueDate(assignment.due_date) }}
                        </span>
                      </p>
                    </div>

                    <Badge variant="outline" class="rounded-full px-2.5 py-1">
                      {{ releasedPhraseCount(assignment) }} released
                    </Badge>
                  </div>
                  <Separator v-if="index < assignmentPreview.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <AppIcon name="book" :size="18" />
                <AlertTitle>No teacher assignments yet</AlertTitle>
                <AlertDescription>
                  Assigned work from your teachers will appear here once it is sent to your account.
                </AlertDescription>
              </Alert>
            </div>

            <Card class="border-dashed shadow-none">
              <CardHeader class="gap-2">
                <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Released feedback
                </p>
                <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                  {{ releasedAssignmentPhrases }}
                </CardTitle>
                <CardDescription>
                  Reviewed assignment phrases already released back to your student view.
                </CardDescription>
              </CardHeader>
              <CardFooter class="border-t">
                <Button class="w-full" @click="router.push('/assignments')">
                  <AppIcon name="forward" :size="18" data-icon="inline-start" />
                  <span>Open Assignments</span>
                </Button>
              </CardFooter>
            </Card>
          </CardContent>
        </Card>

        <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Card>
            <CardHeader class="flex flex-col gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Module atlas
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Where you sound strongest
              </CardTitle>
              <CardDescription>
                Ranked by accuracy so you can see which topics feel natural and which need more reps.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-1">
              <template v-if="rankedModules.length">
                <template v-for="(summary, index) in rankedModules" :key="summary.module_id">
                  <div class="flex items-start justify-between gap-4 rounded-xl p-3">
                    <div class="flex min-w-0 items-start gap-3">
                      <span class="flex size-10 items-center justify-center rounded-2xl bg-secondary text-primary">
                        <AppIcon :name="moduleIconName(summary.module_id)" :size="20" />
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

                    <Badge :variant="scoreBadgeVariant(summary.average_accuracy)" class="rounded-full px-3 py-1">
                      {{ summary.average_accuracy.toFixed(0) }}%
                    </Badge>
                  </div>
                  <Separator v-if="index < rankedModules.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <AppIcon name="chart" :size="18" />
                <AlertTitle>No module ranking yet</AlertTitle>
                <AlertDescription>
                  Complete a module to build your first accuracy leaderboard.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button variant="outline" @click="router.push('/lessons')">
                <AppIcon name="book" :size="18" data-icon="inline-start" />
                <span>Explore all modules</span>
              </Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader class="flex flex-col gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Recent work
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
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
                  <div class="flex items-start justify-between gap-4 rounded-xl p-3">
                    <div class="flex min-w-0 flex-col gap-2">
                      <p class="font-semibold text-(--color-heading)">
                        {{ attempt.phrase_id }}
                      </p>
                      <p class="text-sm text-muted-foreground">
                        {{ formatAttemptDate(attempt.attempted_at) }}
                      </p>
                    </div>
                    <Badge :variant="scoreBadgeVariant(attempt.accuracy_score)" class="rounded-full px-3 py-1">
                      {{ attempt.accuracy_score.toFixed(0) }}%
                    </Badge>
                  </div>
                  <Separator v-if="index < recentAttempts.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <AppIcon name="mic" :size="18" />
                <AlertTitle>No attempts yet</AlertTitle>
                <AlertDescription>
                  Start with a lesson and submit your first recording to populate this list.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button @click="router.push('/lessons')">
                <AppIcon name="mic" :size="18" data-icon="inline-start" />
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppIcon from '@/components/shared/AppIcon.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
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
import { moduleIconName } from '@/constants/modules'
import { useAttemptsStore } from '@/stores/attempts'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import type { ProgressSummary, StudentAssignment } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const progressStore = useProgressStore()
const modulesStore = useModulesStore()
const attemptsStore = useAttemptsStore()
const assignmentsLoading = ref(false)
const assignmentsError = ref<string | null>(null)
const studentAssignments = ref<StudentAssignment[]>([])

const dashboard = computed(() => progressStore.dashboard)
const latestAttempt = computed(() => attemptsStore.attemptHistory[0] ?? null)
const recentAttempts = computed(() => attemptsStore.attemptHistory.slice(0, 4))
const weeklyAccuracy = computed(() => dashboard.value?.weekly_accuracy.slice(-6) ?? [])
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

const continueModule = computed(() => {
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

const continueProgress = computed(() => {
  if (!continueModule.value) return null
  return progressStore.getProgressForModule(continueModule.value.module_id)
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
  if (weeklyDelta.value < 0) return 'outline'
  if (weeklyDelta.value === 0) return 'secondary'
  return 'default'
})

const metricCards = computed(() => [
  {
    label: 'Streak',
    value: `${dashboard.value?.streak_days ?? 0}`,
    copy: (dashboard.value?.streak_days ?? 0) > 0 ? 'days in a row' : 'start a daily rhythm',
  },
  {
    label: 'Attempts',
    value: `${dashboard.value?.total_attempts ?? 0}`,
    copy: 'submitted speaking checks',
  },
  {
    label: 'Modules active',
    value: `${activeModulesCount.value}`,
    copy: 'topics you have already touched',
  },
  {
    label: 'Strongest module',
    value: strongestModuleTitle.value,
    copy: strongestModule.value
      ? `${strongestModule.value.average_accuracy.toFixed(0)}% average accuracy`
      : 'Complete a few reps to unlock this insight.',
  },
])

function scoreBadgeVariant(score: number): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
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

async function loadStudentAssignments(uid: string) {
  assignmentsError.value = null
  studentAssignments.value = await getStudentAssignments(uid)
}

async function openModule(moduleId?: string | null) {
  if (!moduleId) {
    await router.push('/lessons')
    return
  }

  await modulesStore.fetchPhrases(moduleId)
  const phrases = modulesStore.getPhrasesForModule(moduleId)

  if (phrases.length) {
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
    await loadStudentAssignments(uid)
  } catch (error) {
    console.error('Failed to load student dashboard assignments:', error)
    assignmentsError.value = 'We could not load your teacher assignments right now.'
  } finally {
    assignmentsLoading.value = false
  }
})
</script>

<template>
  <InstructorLayout>
    <div class="flex flex-col gap-5">
      <LoadingSpinner
        v-if="loading && !overview"
        full-screen
        message="Loading analytics..."
      />

      <template v-else>
        <Alert v-if="error" variant="destructive">
          <TriangleAlert />
          <AlertTitle>Overview unavailable</AlertTitle>
          <AlertDescription>{{ error }}</AlertDescription>
        </Alert>

        <template v-else-if="overview">
          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-4">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Live class pulse
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ classesStore.activeClass?.name ?? 'No active class' }}
                </Badge>
              </div>

              <div class="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_300px] lg:items-start">
                <div class="flex min-w-0 flex-col gap-4">
                  <div class="flex flex-col gap-3">
                    <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
                      Teach from the class trend, not from guesswork
                    </CardTitle>
                    <CardDescription class="max-w-3xl text-base leading-8">
                      Review weekly movement, scan pronunciation category averages, and surface students who need intervention before the next assignment cycle.
                    </CardDescription>
                  </div>

                  <div class="flex flex-col gap-3 sm:flex-row">
                    <Button size="lg" @click="router.push('/instructor/students')">
                      <Users data-icon="inline-start" />
                      <span>Open student directory</span>
                    </Button>
                    <Button variant="outline" size="lg" @click="router.push('/instructor/exercises')">
                      <ClipboardList data-icon="inline-start" />
                      <span>Manage assignments</span>
                    </Button>
                  </div>
                </div>

                <Card class="border-dashed shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Today
                    </p>
                    <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                      {{ todayLabel }}
                    </CardTitle>
                    <CardDescription>
                      {{ authStore.profile?.display_name ?? 'Instructor' }} is currently viewing
                      {{ overview.total_students }} students in this class.
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
            </CardHeader>

            <CardContent class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <Card
                v-for="item in metricCards"
                :key="item.label"
                class="gap-0 shadow-none"
              >
                <CardHeader class="gap-2">
                  <div class="flex items-center justify-between gap-3">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      {{ item.label }}
                    </p>
                    <component :is="item.icon" class="text-muted-foreground" />
                  </div>
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

          <div class="grid gap-5 xl:grid-cols-[minmax(0,1.18fr)_minmax(320px,0.82fr)]">
            <Card class="border-border/80 bg-card/95">
              <CardHeader class="gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Weekly trend
                </Badge>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Accuracy movement
                </CardTitle>
                <CardDescription>
                  Use the weekly curve to see whether the class is stabilizing or drifting before you plan the next set of guided reps.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div class="grid min-h-[240px] grid-cols-6 items-end gap-3 rounded-3xl border border-border/70 bg-muted/30 p-4">
                  <div
                    v-for="week in displayTrend"
                    :key="week.week_start"
                    class="flex min-w-0 flex-col items-center justify-end gap-3"
                  >
                    <p class="text-xs font-medium text-muted-foreground">
                      {{ week.attempt_count ? `${week.average_accuracy.toFixed(0)}%` : '--' }}
                    </p>
                    <div class="flex h-36 w-full items-end justify-center">
                      <div
                        class="w-full rounded-t-2xl bg-primary transition-[height,background-color] duration-300"
                        :class="week.attempt_count ? '' : 'bg-border/80'"
                        :style="{ height: `${barHeight(week.average_accuracy)}px` }"
                      />
                    </div>
                    <p class="text-center text-xs text-muted-foreground">
                      {{ formatWeekLabel(week.week_start) }}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card class="border-border/80 bg-card/95">
              <CardHeader class="gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Phoneme profile
                </Badge>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Class pronunciation profile
                </CardTitle>
                <CardDescription>
                  These averages make it easier to decide whether timing, consonants, or vowels deserve the next coaching push.
                </CardDescription>
              </CardHeader>

              <CardContent class="flex flex-col gap-4">
                <div
                  v-for="item in phonemeRows"
                  :key="item.label"
                  class="flex flex-col gap-2 rounded-2xl border border-border/70 bg-muted/30 p-4"
                >
                  <div class="flex items-center justify-between gap-3">
                    <p class="font-semibold text-(--color-heading)">{{ item.label }}</p>
                    <Badge :variant="scoreVariant(item.value)" class="rounded-full px-3 py-1">
                      {{ item.value.toFixed(1) }}%
                    </Badge>
                  </div>
                  <div class="h-2 overflow-hidden rounded-full bg-border/70">
                    <div
                      class="h-full rounded-full bg-primary transition-[width] duration-300"
                      :style="{ width: `${item.value}%` }"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex flex-col gap-3">
                  <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    Needs attention
                  </Badge>
                  <div class="flex flex-col gap-2">
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      Flagged students
                    </CardTitle>
                    <CardDescription>
                      Learners below {{ flagThreshold }}% are surfaced here first so you can move directly into drilldown review.
                    </CardDescription>
                  </div>
                </div>

                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ overview.flagged_students.length }} flagged
                </Badge>
              </div>
            </CardHeader>

            <CardContent class="grid gap-3 lg:grid-cols-2">
              <template v-if="overview.flagged_students.length">
                <button
                  v-for="student in overview.flagged_students"
                  :key="student.uid"
                  type="button"
                  class="flex w-full items-center gap-4 rounded-2xl border border-border/70 bg-muted/30 p-4 text-left transition hover:border-primary/30 hover:bg-muted/50"
                  @click="router.push('/instructor/students')"
                >
                  <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-destructive/10 font-semibold text-destructive">
                    {{ student.display_name.slice(0, 1).toUpperCase() }}
                  </div>

                  <div class="min-w-0 flex-1">
                    <p class="truncate font-semibold text-(--color-heading)">
                      {{ student.display_name }}
                    </p>
                    <p class="truncate text-sm text-muted-foreground">
                      {{ student.email }}
                    </p>
                  </div>

                  <Badge variant="destructive" class="rounded-full px-3 py-1">
                    {{ student.overall_average.toFixed(0) }}%
                  </Badge>
                </button>
              </template>

              <Alert v-else>
                <CheckCircle2 />
                <AlertTitle>No flagged students</AlertTitle>
                <AlertDescription>
                  Everyone in the active class is currently above the review threshold.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </template>
      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity,
  CheckCircle2,
  ClipboardList,
  TrendingUp,
  TriangleAlert,
  UserRoundCheck,
  Users,
} from 'lucide-vue-next'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
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
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { getClassOverview } from '@/api/analytics'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import type { ClassOverview } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()

const overview = ref<ClassOverview | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const flagThreshold = 60

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }),
)

const metricCards = computed(() => {
  if (!overview.value) return []

  return [
    {
      label: 'Class average',
      value: `${overview.value.class_average.toFixed(1)}%`,
      copy: 'overall pronunciation accuracy in the active class',
      icon: TrendingUp,
    },
    {
      label: 'Total students',
      value: `${overview.value.total_students}`,
      copy: 'learners currently enrolled in this roster',
      icon: Users,
    },
    {
      label: 'Active this week',
      value: `${overview.value.active_students}`,
      copy: 'students who practiced recently',
      icon: UserRoundCheck,
    },
    {
      label: 'Weekly attempts',
      value: `${overview.value.weekly_attempts}`,
      copy: 'submissions recorded inside the current week window',
      icon: Activity,
    },
  ]
})

const phonemeRows = computed(() => {
  if (!overview.value) return []

  return [
    { label: 'Mora timing', value: overview.value.phoneme_breakdown.mora_timing_avg },
    { label: 'Consonants', value: overview.value.phoneme_breakdown.consonant_avg },
    { label: 'Vowel purity', value: overview.value.phoneme_breakdown.vowel_avg },
  ]
})

const displayTrend = computed(() => overview.value?.weekly_trend.slice(-6) ?? [])

function barHeight(accuracy: number) {
  return Math.max(12, (accuracy / 100) * 144)
}

function formatWeekLabel(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}

async function loadOverview(classId: string | null) {
  overview.value = null
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load analytics.'
    return
  }

  loading.value = true
  try {
    overview.value = await getClassOverview(classId, flagThreshold)
  } catch {
    error.value = 'Failed to load class analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
  } catch {
    error.value = 'Failed to load your classes.'
  }
  await loadOverview(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadOverview(classId)
  },
)
</script>

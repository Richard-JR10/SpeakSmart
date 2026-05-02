<template>
  <StudentLayout title="My Progress">
    <div class="mx-auto flex w-full max-w-6xl flex-col gap-3">
      <LoadingSpinner v-if="progressStore.loading" full-screen message="Loading progress..." />

      <template v-else-if="dashboard">
        <Card class="overflow-hidden border-border/80 bg-card/95 shadow-(--shadow-soft)">
          <CardHeader class="gap-3 px-4 py-4 sm:px-5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <div class="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" class="w-fit rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                    Progress overview
                  </Badge>
                </div>
                <CardTitle class="font-(--font-display) text-2xl leading-tight text-(--color-heading) sm:text-3xl">
                  Your pronunciation trend
                </CardTitle>
                <CardDescription class="mt-1 max-w-3xl text-sm leading-6">
                  Current average, practice rhythm, and the next place to focus.
                </CardDescription>
              </div>

              <Badge :variant="deltaBadgeVariant" class="w-fit rounded-full px-3 py-1">
                {{ deltaText || 'Tracking weekly change' }}
              </Badge>
            </div>
          </CardHeader>

          <CardContent class="border-t border-border/70 px-4 py-3 sm:px-5">
            <div class="grid gap-0 rounded-xl border border-border/70 bg-secondary/30 sm:grid-cols-3">
              <div class="min-w-0 px-4 py-3">
                <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Overall accuracy
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.overall_average.toFixed(1) }}%
                </p>
                <p class="mt-1 truncate text-xs text-muted-foreground">
                  Completed submissions
                </p>
              </div>

              <div class="min-w-0 border-t border-border/70 px-4 py-3 sm:border-t-0 sm:border-l">
                <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Total attempts
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.total_attempts }}
                </p>
                <p class="mt-1 truncate text-xs text-muted-foreground">
                  Practice submissions
                </p>
              </div>

              <div class="min-w-0 border-t border-border/70 px-4 py-3 sm:border-t-0 sm:border-l">
                <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Current streak
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.streak_days }}
                </p>
                <p class="mt-1 truncate text-xs text-muted-foreground">
                  Consecutive practice days
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
          <CardHeader class="flex flex-col gap-2 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
            <div>
              <Badge variant="secondary" class="w-fit rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                Weekly accuracy
              </Badge>
              <CardTitle class="mt-2 font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                Consistency over time
              </CardTitle>
            </div>
            <CardDescription class="text-sm sm:text-right">
              Weekly average accuracy
            </CardDescription>
          </CardHeader>

          <CardContent class="px-4 pb-4 sm:px-5">
            <div v-if="weeklyChartPoints.length" class="overflow-x-auto">
              <div class="min-w-160">
                <svg
                  class="h-44 w-full"
                  :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`"
                  role="img"
                  aria-label="Weekly accuracy line chart"
                >
                  <defs>
                    <linearGradient id="weeklyAccuracyFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stop-color="var(--color-chart-1)" stop-opacity="0.24" />
                      <stop offset="100%" stop-color="var(--color-chart-1)" stop-opacity="0.02" />
                    </linearGradient>
                  </defs>

                  <g v-for="tick in chartTickLines" :key="tick.value">
                    <line
                      :x1="CHART_PADDING.left"
                      :x2="CHART_WIDTH - CHART_PADDING.right"
                      :y1="tick.y"
                      :y2="tick.y"
                      stroke="var(--color-border)"
                      stroke-dasharray="4 6"
                    />
                    <text
                      :x="CHART_PADDING.left - 10"
                      :y="tick.y + 4"
                      text-anchor="end"
                      font-size="11"
                      fill="var(--color-muted-foreground)"
                    >
                      {{ tick.value }}%
                    </text>
                  </g>

                  <path
                    v-if="weeklyChartAreaPath"
                    :d="weeklyChartAreaPath"
                    fill="url(#weeklyAccuracyFill)"
                  />

                  <polyline
                    :points="weeklyChartLinePoints"
                    fill="none"
                    stroke="var(--color-chart-1)"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="4"
                  />

                  <g v-for="point in weeklyChartPoints" :key="point.weekStart">
                    <circle
                      :cx="point.x"
                      :cy="point.y"
                      r="6"
                      fill="var(--color-background)"
                      stroke="var(--color-chart-1)"
                      stroke-width="3"
                    />

                    <text
                      :x="point.x"
                      :y="point.y - 12"
                      text-anchor="middle"
                      font-size="11"
                      fill="var(--color-muted-foreground)"
                    >
                      {{ point.value.toFixed(0) }}%
                    </text>

                    <text
                      :x="point.x"
                      :y="CHART_HEIGHT - 12"
                      text-anchor="middle"
                      font-size="11"
                      fill="var(--color-muted-foreground)"
                    >
                      {{ point.label }}
                    </text>
                  </g>
                </svg>
              </div>
            </div>

            <Alert v-else>
              <AppIcon name="chart" :size="18" />
              <AlertTitle>No weekly accuracy data yet</AlertTitle>
              <AlertDescription>
                Weekly accuracy trends will appear once you have recorded practice activity.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <Card
          v-if="dashboard.weakest_module_id"
          class="border-border/80 bg-[linear-gradient(145deg,rgba(46,138,103,0.12),rgba(184,141,70,0.12))] shadow-(--shadow-soft)"
        >
          <CardContent class="flex flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between sm:px-5">
            <div class="min-w-0">
              <Badge variant="outline" class="w-fit rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                Recommended focus
              </Badge>
              <h3 class="mt-2 truncate font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                {{ weakestTitle }}
              </h3>
              <p class="mt-1 max-w-3xl text-sm leading-6 text-muted-foreground">
                This module is averaging {{ dashboard.weakest_module_score?.toFixed(0) }}%.
                A short replay session here should lift your overall score fastest.
              </p>
            </div>

            <Button size="sm" class="w-full shrink-0 md:w-auto" @click="practiceWeakest">
              <AppIcon name="mic" :size="18" data-icon="inline-start" />
              Practice module
            </Button>
          </CardContent>
        </Card>

        <div class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="gap-2 px-4 py-4 sm:px-5">
              <Badge variant="secondary" class="w-fit rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                By module
              </Badge>
              <CardTitle class="font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                Where you are strongest
              </CardTitle>
            </CardHeader>

            <CardContent class="flex flex-col gap-1 px-4 pb-4 sm:px-5">
              <template v-for="(summary, index) in dashboard.progress_by_module" :key="summary.module_id">
                <div class="flex items-center justify-between gap-3 rounded-xl bg-secondary/35 px-3 py-2.5">
                  <div class="flex min-w-0 items-center gap-3">
                    <span class="flex size-9 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary">
                      <AppIcon :name="moduleIconName(summary.module_id)" :size="18" />
                    </span>
                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-(--color-heading)">
                        {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                      </p>
                      <p class="mt-0.5 text-xs text-muted-foreground">
                        {{ summary.total_attempts }} attempts
                      </p>
                    </div>
                  </div>

                  <ScoreCircle :score="summary.average_accuracy" size="sm" />
                </div>
                <Separator v-if="index < dashboard.progress_by_module.length - 1" />
              </template>
            </CardContent>
          </Card>

          <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="gap-2 px-4 py-4 sm:px-5">
              <Badge variant="secondary" class="w-fit rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                Attempt history
              </Badge>
              <CardTitle class="font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                Recent submissions
              </CardTitle>
              <CardDescription class="text-sm">
                Showing your 5 most recent attempts.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-1 px-4 pb-4 sm:px-5">
              <LoadingSpinner v-if="attemptsStore.loading" size="sm" />

              <template v-else-if="visibleAttempts.length">
                <template v-for="(attempt, index) in visibleAttempts" :key="attempt.attempt_id">
                  <div class="flex items-center justify-between gap-3 rounded-xl bg-secondary/35 px-3 py-2.5">
                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-(--color-heading)">
                        {{ attempt.phrase_id }}
                      </p>
                      <p class="mt-0.5 text-xs text-muted-foreground">
                        {{ formatDate(attempt.attempted_at) }}
                      </p>
                    </div>

                    <Badge :variant="scoreBadgeVariant(attempt.accuracy_score)" class="shrink-0 rounded-full px-2.5 py-1">
                      {{ attempt.accuracy_score.toFixed(0) }}%
                    </Badge>
                  </div>
                  <Separator v-if="index < visibleAttempts.length - 1" />
                </template>
              </template>

              <Alert v-else>
                <AppIcon name="chart" :size="18" />
                <AlertTitle>No attempts recorded yet</AlertTitle>
                <AlertDescription>
                  Start practicing to build the first entry in your history.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>
      </template>

      <Card v-else class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
        <CardContent class="flex flex-col items-center gap-4 p-8 text-center">
          <p class="max-w-xl text-sm leading-7 text-muted-foreground">
            No progress data yet. Start practicing to build your first trend line.
          </p>
          <Button @click="router.push('/lessons')">
            <AppIcon name="book" :size="18" data-icon="inline-start" />
            Go to lessons
          </Button>
        </CardContent>
      </Card>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ScoreCircle from '@/components/shared/ScoreCircle.vue'
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
import { Separator } from '@/components/ui/separator'
import { useProgressStore } from '@/stores/progress'
import { useAttemptsStore } from '@/stores/attempts'
import { useModulesStore } from '@/stores/modules'
import { useAuthStore } from '@/stores/auth'
import { moduleIconName } from '@/constants/modules'

const router = useRouter()
const progressStore = useProgressStore()
const attemptsStore = useAttemptsStore()
const modulesStore = useModulesStore()
const authStore = useAuthStore()

const CHART_WIDTH = 680
const CHART_HEIGHT = 180
const CHART_PADDING = {
  top: 18,
  right: 16,
  bottom: 34,
  left: 40,
}
const CHART_TICKS = [0, 25, 50, 75, 100]

const dashboard = computed(() => progressStore.dashboard)
const visibleAttempts = computed(() => attemptsStore.attemptHistory.slice(0, 5))
const chartInnerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right
const chartInnerHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom

const chartTickLines = computed(() =>
  CHART_TICKS.map((value) => ({
    value,
    y: CHART_PADDING.top + chartInnerHeight - (value / 100) * chartInnerHeight,
  })),
)

const weeklyChartPoints = computed(() => {
  const weeklyAccuracy = dashboard.value?.weekly_accuracy ?? []
  if (!weeklyAccuracy.length) return []

  const slotWidth = weeklyAccuracy.length > 1
    ? chartInnerWidth / (weeklyAccuracy.length - 1)
    : 0

  return weeklyAccuracy.map((week, index) => {
    const value = Math.max(0, Math.min(100, week.average_accuracy))
    const x = weeklyAccuracy.length > 1
      ? CHART_PADDING.left + index * slotWidth
      : CHART_PADDING.left + chartInnerWidth / 2
    const y = CHART_PADDING.top + chartInnerHeight - (value / 100) * chartInnerHeight

    return {
      weekStart: week.week_start,
      value,
      x,
      y,
      label: formatWeekLabel(week.week_start),
    }
  })
})

const weeklyChartLinePoints = computed(() =>
  weeklyChartPoints.value.map((point) => `${point.x},${point.y}`).join(' '),
)

const weeklyChartAreaPath = computed(() => {
  const points = weeklyChartPoints.value
  if (points.length < 2) return ''

  const baseline = CHART_HEIGHT - CHART_PADDING.bottom
  const line = points.map((point) => `L ${point.x} ${point.y}`).join(' ')
  const first = points[0]
  const last = points[points.length - 1]

  return `M ${first.x} ${baseline} ${line} L ${last.x} ${baseline} Z`
})

const weakestTitle = computed(() => {
  if (!dashboard.value?.weakest_module_id) return ''
  return modulesStore.getModuleById(dashboard.value.weakest_module_id)?.title ?? ''
})

const deltaText = computed(() => {
  if (!dashboard.value?.weekly_accuracy?.length) return ''
  const weeks = dashboard.value.weekly_accuracy
  const last = weeks[weeks.length - 1]?.average_accuracy ?? 0
  const prev = weeks[weeks.length - 2]?.average_accuracy ?? 0
  const diff = (last - prev).toFixed(1)
  return last >= prev ? `+${diff}% this week` : `${diff}% this week`
})

const deltaBadgeVariant = computed(() => {
  if (!dashboard.value?.weekly_accuracy?.length) return 'outline'
  const weeks = dashboard.value.weekly_accuracy
  const last = weeks[weeks.length - 1]?.average_accuracy ?? 0
  const prev = weeks[weeks.length - 2]?.average_accuracy ?? 0
  if (last > prev) return 'default'
  if (last === prev) return 'secondary'
  return 'outline'
})

function formatWeekLabel(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function scoreBadgeVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}

async function practiceWeakest() {
  if (!dashboard.value?.weakest_module_id) return
  await modulesStore.fetchPhrases(dashboard.value.weakest_module_id)
  const phrases = modulesStore.getPhrasesForModule(dashboard.value.weakest_module_id)
  if (phrases.length) {
    router.push(`/practice/${dashboard.value.weakest_module_id}/${phrases[0].phrase_id}`)
  }
}

onMounted(async () => {
  const uid = authStore.uid!
  await Promise.all([
    modulesStore.fetchModules(),
    progressStore.fetchDashboard(uid),
    attemptsStore.fetchHistory(uid),
  ])
})
</script>

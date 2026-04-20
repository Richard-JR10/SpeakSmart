<template>
  <StudentLayout title="My Progress">
    <div class="mx-auto flex w-full max-w-6xl flex-col gap-5">
      <LoadingSpinner v-if="progressStore.loading" full-screen message="Loading progress..." />

      <template v-else-if="dashboard">
        <Card class="overflow-hidden border-border/80 bg-card/95 shadow-(--shadow-soft)">
          <CardHeader class="gap-5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex flex-col gap-3">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Progress overview
                </Badge>
                <div>
                  <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading) sm:text-5xl">
                    Your pronunciation trend
                  </CardTitle>
                  <CardDescription class="mt-3 max-w-3xl text-base leading-8">
                    Review your current average, how often you practice, and where your speech is getting stronger.
                  </CardDescription>
                </div>
              </div>

              <Badge :variant="deltaBadgeVariant" class="w-fit rounded-full px-3 py-1">
                {{ deltaText || 'Tracking weekly change' }}
              </Badge>
            </div>
          </CardHeader>

          <CardContent class="grid gap-4 md:grid-cols-3">
            <Card class="gap-0 bg-secondary/50 shadow-none">
              <CardHeader class="gap-2">
                <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Overall accuracy
                </p>
                <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                  {{ dashboard.overall_average.toFixed(1) }}%
                </CardTitle>
                <CardDescription>
                  Your average across all completed submissions.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card class="gap-0 bg-secondary/50 shadow-none">
              <CardHeader class="gap-2">
                <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Total attempts
                </p>
                <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                  {{ dashboard.total_attempts }}
                </CardTitle>
                <CardDescription>
                  Practice submissions recorded so far.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card class="gap-0 bg-secondary/50 shadow-none">
              <CardHeader class="gap-2">
                <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Current streak
                </p>
                <CardTitle class="font-(--font-display) text-4xl leading-none text-(--color-heading)">
                  {{ dashboard.streak_days }}
                </CardTitle>
                <CardDescription>
                  Consecutive days with recorded speaking work.
                </CardDescription>
              </CardHeader>
            </Card>
          </CardContent>
        </Card>

        <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
          <CardHeader class="gap-3">
            <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Weekly accuracy
            </Badge>
            <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
              Consistency over time
            </CardTitle>
            <CardDescription>
              Weekly average accuracy shown as a bar chart.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div v-if="weeklyChartBars.length" class="overflow-x-auto">
              <div class="min-w-160">
                <svg
                  class="h-65 w-full"
                  :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`"
                  role="img"
                  aria-label="Weekly accuracy bar chart"
                >
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

                  <g v-for="bar in weeklyChartBars" :key="bar.weekStart">
                    <rect
                      :x="bar.x"
                      :y="bar.y"
                      :width="bar.width"
                      :height="bar.height"
                      rx="12"
                      :fill="bar.value > 0 ? 'var(--color-chart-1)' : 'var(--color-border)'"
                    />

                    <text
                      :x="bar.labelX"
                      :y="bar.y - 8"
                      text-anchor="middle"
                      font-size="11"
                      fill="var(--color-muted-foreground)"
                    >
                      {{ bar.value > 0 ? `${bar.value.toFixed(0)}%` : '' }}
                    </text>

                    <text
                      :x="bar.labelX"
                      :y="CHART_HEIGHT - 12"
                      text-anchor="middle"
                      font-size="11"
                      fill="var(--color-muted-foreground)"
                    >
                      {{ bar.label }}
                    </text>
                  </g>
                </svg>
              </div>
            </div>

            <Alert v-else>
              <AppIcon name="chart" :size="18" />
              <AlertTitle>No weekly accuracy data yet</AlertTitle>
              <AlertDescription>
                Weekly accuracy bars will appear once you have recorded practice activity.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <Card
          v-if="dashboard.weakest_module_id"
          class="border-border/80 bg-[linear-gradient(145deg,rgba(46,138,103,0.12),rgba(184,141,70,0.12))] shadow-(--shadow-soft)"
        >
          <CardContent class="flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
            <div class="flex flex-col gap-2">
              <Badge variant="outline" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Recommended focus
              </Badge>
              <h3 class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                {{ weakestTitle }}
              </h3>
              <p class="max-w-3xl text-sm leading-7 text-muted-foreground">
                This module is averaging {{ dashboard.weakest_module_score?.toFixed(0) }}%.
                A short replay session here should lift your overall score fastest.
              </p>
            </div>

            <Button size="lg" class="w-full md:w-auto" @click="practiceWeakest">
              <AppIcon name="mic" :size="18" data-icon="inline-start" />
              Practice module
            </Button>
          </CardContent>
        </Card>

        <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Card class="border-border/80 bg-card/95 shadow-(--shadow-soft)">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                By module
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Where you are strongest
              </CardTitle>
            </CardHeader>

            <CardContent class="flex flex-col gap-1">
              <template v-for="(summary, index) in dashboard.progress_by_module" :key="summary.module_id">
                <div class="flex items-center justify-between gap-4 rounded-[22px] bg-secondary/35 p-4">
                  <div class="flex min-w-0 items-center gap-4">
                    <span class="flex size-12 items-center justify-center rounded-[18px] bg-secondary text-primary">
                      <AppIcon :name="moduleIconName(summary.module_id)" :size="22" />
                    </span>
                    <div class="min-w-0">
                      <p class="truncate font-semibold text-(--color-heading)">
                        {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
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
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Attempt history
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Recent submissions
              </CardTitle>
              <CardDescription>
                Showing your 5 most recent attempts.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-1">
              <LoadingSpinner v-if="attemptsStore.loading" size="sm" />

              <template v-else-if="visibleAttempts.length">
                <template v-for="(attempt, index) in visibleAttempts" :key="attempt.attempt_id">
                  <div class="flex items-center justify-between gap-4 rounded-[22px] bg-secondary/35 p-4">
                    <div class="min-w-0">
                      <p class="truncate font-semibold text-(--color-heading)">
                        {{ attempt.phrase_id }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
                        {{ formatDate(attempt.attempted_at) }}
                      </p>
                    </div>

                    <Badge :variant="scoreBadgeVariant(attempt.accuracy_score)" class="rounded-full px-3 py-1">
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
const CHART_HEIGHT = 260
const CHART_PADDING = {
  top: 20,
  right: 18,
  bottom: 42,
  left: 44,
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

const weeklyChartBars = computed(() => {
  const weeklyAccuracy = dashboard.value?.weekly_accuracy ?? []
  if (!weeklyAccuracy.length) return []

  const slotWidth = chartInnerWidth / weeklyAccuracy.length
  const barWidth = Math.min(48, Math.max(22, slotWidth * 0.52))

  return weeklyAccuracy.map((week, index) => {
    const value = Math.max(0, Math.min(100, week.average_accuracy))
    const height = value === 0
      ? 8
      : Math.max(14, (value / 100) * chartInnerHeight)
    const x = CHART_PADDING.left + index * slotWidth + (slotWidth - barWidth) / 2
    const y = CHART_PADDING.top + chartInnerHeight - height

    return {
      weekStart: week.week_start,
      value,
      x,
      y,
      width: barWidth,
      height,
      labelX: x + barWidth / 2,
      label: formatWeekLabel(week.week_start),
    }
  })
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

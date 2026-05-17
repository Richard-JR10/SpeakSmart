<template>
  <StudentLayout title="My Progress">
    <div class="mx-auto flex w-full max-w-6xl flex-col gap-4">
      <LoadingSpinner v-if="progressStore.loading" full-screen message="Loading progress..." />

      <template v-else-if="dashboard">

        <!-- Zone 1 — Hero stat banner -->
        <Card class="overflow-hidden border-border/80 bg-card/95">
          <CardContent class="p-0">

            <!-- Top: label + delta -->
            <div class="flex items-center justify-between gap-3 px-5 pt-4 pb-3">
              <Badge variant="secondary" class="rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                Progress overview
              </Badge>
              <Badge :variant="deltaBadgeVariant" class="rounded-full px-3 py-1 text-xs">
                {{ deltaText || 'Tracking weekly change' }}
              </Badge>
            </div>

            <!-- Stats row -->
            <div class="grid grid-cols-3 divide-x divide-border/60 border-t border-border/60">

              <!-- Accuracy -->
              <div class="flex flex-col gap-0.5 px-5 py-4">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">Accuracy</p>
                <p class="font-(--font-display) text-[clamp(2rem,6vw,3rem)] leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.overall_average.toFixed(1) }}<span class="text-lg font-normal text-primary">%</span>
                </p>
              </div>

              <!-- Attempts -->
              <div class="flex flex-col gap-0.5 px-5 py-4">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">Attempts</p>
                <p class="font-(--font-display) text-[clamp(2rem,6vw,3rem)] leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.total_attempts }}
                </p>
              </div>

              <!-- Streak -->
              <div class="flex flex-col gap-0.5 px-5 py-4">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">Streak</p>
                <p class="font-(--font-display) text-[clamp(2rem,6vw,3rem)] leading-none tabular-nums text-(--color-heading)">
                  {{ dashboard.streak_days }}<span class="text-lg font-normal text-muted-foreground">d</span>
                </p>
              </div>

            </div>
          </CardContent>
        </Card>

        <!-- Zone 2 — Focus banner -->
        <div
          v-if="dashboard.weakest_module_id"
          class="flex flex-col gap-3 rounded-2xl border border-amber-200/80 border-l-4 border-l-amber-400 bg-amber-50/60 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="flex size-9 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
              <Zap class="size-4" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-amber-700">Recommended focus</p>
              <p class="truncate font-semibold text-(--color-heading)">{{ weakestTitle }}</p>
              <p class="text-xs text-muted-foreground">
                Averaging {{ dashboard.weakest_module_score?.toFixed(0) }}% — a short session here lifts your score fastest.
              </p>
            </div>
          </div>
          <Button size="sm" class="w-full shrink-0 sm:w-auto" @click="practiceWeakest">
            <AppIcon name="mic" :size="14" data-icon="inline-start" />
            Practice now
          </Button>
        </div>

        <!-- Zone 3 — Module mastery list -->
        <Card class="border-border/80 bg-card/95">
          <CardHeader class="px-5 pt-5 pb-3">
            <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Where you stand</p>
            <CardTitle class="mt-1 font-(--font-display) text-2xl leading-tight text-(--color-heading)">
              Module mastery
            </CardTitle>
          </CardHeader>

          <CardContent class="flex flex-col gap-1 px-3 pb-3">
            <div
              v-for="summary in dashboard.progress_by_module"
              :key="summary.module_id"
              class="flex items-center gap-3 rounded-xl px-3 py-3 transition-colors"
              :class="summary.total_phrases > 0 && summary.completed_phrases === summary.total_phrases
                ? 'bg-emerald-50/60'
                : 'hover:bg-secondary/30'"
            >
              <!-- Module icon -->
              <span class="flex size-9 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary">
                <AppIcon :name="moduleIconName(summary.module_id)" :size="16" />
              </span>

              <!-- Title + progress bar -->
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-(--color-heading)">
                  {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                </p>
                <div class="mt-1.5 flex items-center gap-2">
                  <div class="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-border/50">
                    <div
                      class="h-full rounded-full transition-[width] duration-500"
                      :class="summary.total_phrases > 0 && summary.completed_phrases === summary.total_phrases
                        ? 'bg-emerald-500'
                        : 'bg-primary'"
                      :style="{
                        width: summary.total_phrases > 0
                          ? `${(summary.completed_phrases / summary.total_phrases) * 100}%`
                          : '0%'
                      }"
                    />
                  </div>
                  <span class="shrink-0 text-[11px] tabular-nums text-muted-foreground">
                    {{ summary.completed_phrases }}/{{ summary.total_phrases }}
                  </span>
                </div>
              </div>

              <!-- Score circle -->
              <ScoreCircle :score="summary.average_accuracy" size="sm" />

              <!-- Action: badge if done, button if not -->
              <Badge
                v-if="summary.total_phrases > 0 && summary.completed_phrases === summary.total_phrases"
                class="shrink-0 rounded-full bg-emerald-100 px-2.5 py-1 text-[11px] uppercase tracking-[0.12em] text-emerald-700"
              >
                Completed
              </Badge>
              <Button
                v-else
                variant="outline"
                size="sm"
                class="shrink-0 rounded-xl"
                @click="practiceModule(summary.module_id)"
              >
                Practice
              </Button>
            </div>
          </CardContent>
        </Card>

        <!-- Zone 4 — Full-width combo chart -->
        <Card class="border-border/80 bg-card/95">
          <CardHeader class="px-5 pt-5 pb-0">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Trend</p>
                <CardTitle class="mt-1 font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                  Accuracy &amp; activity
                </CardTitle>
              </div>
              <!-- Legend -->
              <div class="flex items-center gap-4 text-xs text-muted-foreground">
                <span class="flex items-center gap-1.5">
                  <span class="inline-block h-0.5 w-5 rounded-full bg-(--color-chart-1)" />
                  Accuracy
                </span>
                <span class="flex items-center gap-1.5">
                  <span class="inline-block h-3 w-3 rounded-sm bg-(--color-chart-2) opacity-70" />
                  Attempts
                </span>
              </div>
            </div>

            <!-- Inline stats row -->
            <div class="mt-4 grid grid-cols-3 divide-x divide-border/50 border-t border-border/50">
              <div class="px-4 py-3">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">This week</p>
                <p class="mt-0.5 font-(--font-display) text-2xl leading-none tabular-nums text-(--color-heading)">
                  {{ currentWeekAccuracy }}<span class="text-sm font-normal text-muted-foreground">%</span>
                </p>
              </div>
              <div class="px-4 py-3">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">8-week peak</p>
                <p class="mt-0.5 font-(--font-display) text-2xl leading-none tabular-nums text-(--color-heading)">
                  {{ peakAccuracy }}<span class="text-sm font-normal text-muted-foreground">%</span>
                </p>
              </div>
              <div class="px-4 py-3">
                <p class="text-[11px] font-semibold uppercase tracking-[0.13em] text-muted-foreground">Period attempts</p>
                <p class="mt-0.5 font-(--font-display) text-2xl leading-none tabular-nums text-(--color-heading)">
                  {{ totalAttempts8W }}
                </p>
              </div>
            </div>
          </CardHeader>

          <CardContent class="px-5 pb-5 pt-4">
            <div v-if="weeklyChartPoints.length">
              <svg
                class="h-72 w-full"
                :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`"
                preserveAspectRatio="none"
                role="img"
                aria-label="Weekly accuracy and attempt volume chart"
              >
                  <defs>
                    <linearGradient id="weeklyAccuracyFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stop-color="var(--color-chart-1)" stop-opacity="0.28" />
                      <stop offset="100%" stop-color="var(--color-chart-1)" stop-opacity="0.03" />
                    </linearGradient>
                  </defs>

                  <!-- Accuracy tick lines -->
                  <g v-for="tick in chartTickLines" :key="tick.value">
                    <line
                      :x1="CHART_PAD_L" :x2="CHART_WIDTH - CHART_PAD_R"
                      :y1="tick.y" :y2="tick.y"
                      stroke="var(--color-border)" stroke-dasharray="4 6"
                    />
                    <text
                      :x="CHART_PAD_L - 10" :y="tick.y + 4"
                      text-anchor="end" font-size="11" fill="var(--color-muted-foreground)"
                    >{{ tick.value }}%</text>
                  </g>

                  <!-- Area fill -->
                  <path v-if="weeklyChartAreaPath" :d="weeklyChartAreaPath" fill="url(#weeklyAccuracyFill)" />

                  <!-- Accuracy line -->
                  <polyline
                    :points="weeklyChartLinePoints"
                    fill="none"
                    stroke="var(--color-chart-1)"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                  />

                  <!-- Accuracy data points + value labels -->
                  <g v-for="point in weeklyChartPoints" :key="point.weekStart">
                    <circle :cx="point.x" :cy="point.y" r="5" fill="var(--color-background)" stroke="var(--color-chart-1)" stroke-width="2.5" />
                    <text :x="point.x" :y="point.y - 10" text-anchor="middle" font-size="11" fill="var(--color-muted-foreground)">{{ point.value.toFixed(0) }}%</text>
                  </g>

                  <!-- Divider line between accuracy and volume -->
                  <line
                    :x1="CHART_PAD_L" :x2="CHART_WIDTH - CHART_PAD_R"
                    :y1="VOL_TOP - 8" :y2="VOL_TOP - 8"
                    stroke="var(--color-border)" stroke-opacity="0.6"
                  />
                  <!-- Volume label -->
                  <text :x="CHART_PAD_L - 10" :y="VOL_TOP + VOL_MAX_H / 2 + 4" text-anchor="end" font-size="9" fill="var(--color-muted-foreground)">Vol</text>

                  <!-- Attempt volume bars -->
                  <g v-for="bar in volumeBars" :key="`bar-${bar.cx}`">
                    <rect
                      :x="bar.x" :y="bar.y"
                      :width="bar.w" :height="bar.h"
                      rx="2"
                      fill="var(--color-chart-2)"
                      fill-opacity="0.65"
                    />
                    <text
                      v-if="bar.count > 0"
                      :x="bar.cx" :y="bar.y - 3"
                      text-anchor="middle" font-size="9" fill="var(--color-muted-foreground)"
                    >{{ bar.count }}</text>
                  </g>

                  <!-- Week date labels (shared) -->
                  <text
                    v-for="point in weeklyChartPoints"
                    :key="`lbl-${point.weekStart}`"
                    :x="point.x" :y="LABEL_Y"
                    text-anchor="middle" font-size="11" fill="var(--color-muted-foreground)"
                  >{{ point.label }}</text>
              </svg>
            </div>

            <Alert v-else>
              <AppIcon name="chart" :size="18" />
              <AlertTitle>No weekly data yet</AlertTitle>
              <AlertDescription>Practice activity will build your trend line here.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <!-- Zone 5 — Recent attempts -->
        <Card class="border-border/80 bg-card/95">
          <CardHeader class="flex flex-row items-center justify-between px-5 pt-5 pb-4">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">History</p>
              <CardTitle class="mt-1 font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                Recent attempts
              </CardTitle>
            </div>
            <span class="rounded-full bg-secondary px-3 py-1 text-xs font-semibold tabular-nums text-muted-foreground">
              {{ visibleAttempts.length }} shown
            </span>
          </CardHeader>

          <CardContent class="px-0 pb-2">
            <LoadingSpinner v-if="attemptsStore.loading" size="sm" />

            <template v-else-if="visibleAttempts.length">
              <Table>
                <TableHeader>
                  <TableRow class="hover:bg-transparent border-border/40">
                    <TableHead class="pl-5 text-[10px] uppercase tracking-[0.14em]">When</TableHead>
                    <TableHead class="text-[10px] uppercase tracking-[0.14em]">Phrase</TableHead>
                    <TableHead class="text-[10px] uppercase tracking-[0.14em]">Status</TableHead>
                    <TableHead class="pr-5 text-right text-[10px] uppercase tracking-[0.14em]">Score</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="attempt in visibleAttempts"
                    :key="attempt.attempt_id"
                    class="border-border/30"
                  >
                    <!-- Date -->
                    <TableCell class="pl-5 text-xs tabular-nums text-muted-foreground">
                      {{ formatDate(attempt.attempted_at) }}
                    </TableCell>

                    <!-- Phrase -->
                    <TableCell class="font-semibold text-(--color-heading)">
                      {{ attempt.phrase_id }}
                    </TableCell>

                    <!-- Status -->
                    <TableCell>
                      <span
                        class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold"
                        :class="{
                          'bg-emerald-100 text-emerald-700': attempt.verification_status === 'accepted',
                          'bg-amber-100 text-amber-700': attempt.verification_status === 'retry_needed',
                          'bg-secondary text-muted-foreground': attempt.verification_status === 'no_clear_speech' || attempt.verification_status === 'wrong_phrase_detected',
                        }"
                      >
                        {{ attempt.verification_status === 'accepted' ? 'Accepted'
                          : attempt.verification_status === 'retry_needed' ? 'Retry'
                          : attempt.verification_status === 'no_clear_speech' ? 'No speech'
                          : 'Wrong phrase' }}
                      </span>
                    </TableCell>

                    <!-- Score bar -->
                    <TableCell class="pr-5">
                      <div class="relative ml-auto h-6 w-20 overflow-hidden rounded-full bg-border/30">
                        <div
                          class="absolute inset-y-0 left-0 rounded-full transition-[width] duration-500"
                          :class="{
                            'bg-emerald-500/80': attempt.accuracy_score >= 85,
                            'bg-primary/70': attempt.accuracy_score >= 70 && attempt.accuracy_score < 85,
                            'bg-amber-400/80': attempt.accuracy_score >= 55 && attempt.accuracy_score < 70,
                            'bg-rose-400/80': attempt.accuracy_score < 55,
                          }"
                          :style="{ width: `${attempt.accuracy_score}%` }"
                        />
                        <span class="absolute inset-0 flex items-center justify-center text-[11px] font-bold tabular-nums text-(--color-heading)">
                          {{ attempt.accuracy_score.toFixed(0) }}%
                        </span>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </template>

            <Alert v-else class="mx-5 my-3">
              <AppIcon name="chart" :size="18" />
              <AlertTitle>No attempts yet</AlertTitle>
              <AlertDescription>Start practicing to build your first history entry.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </template>

      <!-- Empty state -->
      <Card v-else class="border-border/80 bg-card/95">
        <CardContent class="flex flex-col items-center gap-4 p-10 text-center">
          <div class="flex size-14 items-center justify-center rounded-3xl bg-secondary text-primary">
            <Target class="size-6" />
          </div>
          <div class="flex flex-col gap-2">
            <p class="font-(--font-display) text-2xl text-(--color-heading)">No progress yet</p>
            <p class="max-w-sm text-sm leading-6 text-muted-foreground">
              Start practicing to build your first trend line.
            </p>
          </div>
          <Button @click="router.push('/lessons')">
            <AppIcon name="book" :size="16" data-icon="inline-start" />
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
import { Flame, Mic, Target, Zap } from 'lucide-vue-next'

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
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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

// Chart layout constants
const CHART_WIDTH = 680
const CHART_HEIGHT = 300
const CHART_PAD_L = 44
const CHART_PAD_R = 16
const CHART_INNER_W = CHART_WIDTH - CHART_PAD_L - CHART_PAD_R
// Accuracy zone: top band
const ACC_TOP = 20
const ACC_BOTTOM = 185
const ACC_INNER_H = ACC_BOTTOM - ACC_TOP
// Volume zone: bottom band
const VOL_TOP = 210
const VOL_MAX_H = 55
const LABEL_Y = 292
const CHART_TICKS = [0, 25, 50, 75, 100]

const dashboard = computed(() => progressStore.dashboard)
const visibleAttempts = computed(() => attemptsStore.attemptHistory.slice(0, 10))

const chartTickLines = computed(() =>
  CHART_TICKS.map((value) => ({
    value,
    y: ACC_TOP + ACC_INNER_H - (value / 100) * ACC_INNER_H,
  })),
)

const weeklyChartPoints = computed(() => {
  const weeks = dashboard.value?.weekly_accuracy ?? []
  if (!weeks.length) return []
  const slotWidth = weeks.length > 1 ? CHART_INNER_W / (weeks.length - 1) : 0
  return weeks.map((week, index) => {
    const value = Math.max(0, Math.min(100, week.average_accuracy))
    const x = weeks.length > 1
      ? CHART_PAD_L + index * slotWidth
      : CHART_PAD_L + CHART_INNER_W / 2
    const y = ACC_TOP + ACC_INNER_H - (value / 100) * ACC_INNER_H
    return { weekStart: week.week_start, value, x, y, label: formatWeekLabel(week.week_start) }
  })
})

const weeklyChartLinePoints = computed(() =>
  weeklyChartPoints.value.map((p) => `${p.x},${p.y}`).join(' '),
)

const weeklyChartAreaPath = computed(() => {
  const points = weeklyChartPoints.value
  if (points.length < 2) return ''
  const line = points.map((p) => `L ${p.x} ${p.y}`).join(' ')
  return `M ${points[0].x} ${ACC_BOTTOM} ${line} L ${points[points.length - 1].x} ${ACC_BOTTOM} Z`
})

const volumeBars = computed(() => {
  const weeks = dashboard.value?.weekly_accuracy ?? []
  if (!weeks.length) return []
  const maxCount = Math.max(...weeks.map((w) => w.attempt_count), 1)
  const slotWidth = weeks.length > 1 ? CHART_INNER_W / (weeks.length - 1) : CHART_INNER_W
  const barW = Math.max(6, slotWidth * 0.45)
  return weeks.map((week, index) => {
    const cx = weeks.length > 1
      ? CHART_PAD_L + index * slotWidth
      : CHART_PAD_L + CHART_INNER_W / 2
    const h = Math.max(2, (week.attempt_count / maxCount) * VOL_MAX_H)
    const y = VOL_TOP + VOL_MAX_H - h
    return { cx, x: cx - barW / 2, y, w: barW, h, count: week.attempt_count }
  })
})

const currentWeekAccuracy = computed(() => {
  const weeks = dashboard.value?.weekly_accuracy ?? []
  if (!weeks.length) return '—'
  return weeks[weeks.length - 1].average_accuracy.toFixed(1)
})

const peakAccuracy = computed(() => {
  const weeks = dashboard.value?.weekly_accuracy ?? []
  if (!weeks.length) return '—'
  return Math.max(...weeks.map((w) => w.average_accuracy)).toFixed(1)
})

const totalAttempts8W = computed(() => {
  const weeks = dashboard.value?.weekly_accuracy ?? []
  if (!weeks.length) return 0
  return weeks.reduce((sum, w) => sum + w.attempt_count, 0)
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
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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

async function practiceModule(moduleId: string) {
  await modulesStore.fetchPhrases(moduleId)
  const phrases = modulesStore.getPhrasesForModule(moduleId)
  if (phrases.length) {
    router.push(`/practice/${moduleId}/${phrases[0].phrase_id}`)
  }
}

async function practiceWeakest() {
  if (!dashboard.value?.weakest_module_id) return
  await practiceModule(dashboard.value.weakest_module_id)
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

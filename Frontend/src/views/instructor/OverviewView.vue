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

            <CardContent class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
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
                  <CardTitle
                    class="font-(--font-display) text-3xl leading-none"
                    :class="item.tone ?? 'text-(--color-heading)'"
                  >
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
                <div
                  v-if="trendChartData.length"
                  class="rounded-3xl border border-border/70 bg-muted/30 px-3 pt-4 pb-2"
                >
                  <ChartContainer
                    :config="trendChartConfig"
                    class="h-[230px] min-h-[230px] w-full"
                    cursor
                  >
                    <VisXYContainer
                      :data="trendChartData"
                      :margin="{ top: 12, right: 12, bottom: 0, left: 8 }"
                      :y-domain="[0, 100]"
                    >
                      <VisAxis
                        type="x"
                        :tick-values="trendChartData.map((point) => point.timestamp)"
                        :tick-format="formatTrendTick"
                        :grid-line="false"
                        :tick-line="false"
                        :domain-line="false"
                        tick-text-font-size="12px"
                      />
                      <VisAxis
                        type="y"
                        :num-ticks="4"
                        :tick-format="formatPercentTick"
                        :tick-line="false"
                        :domain-line="false"
                        tick-text-font-size="12px"
                      />
                      <VisArea
                        :x="(point: TrendChartPoint) => point.timestamp"
                        :y="(point: TrendChartPoint) => point.accuracy"
                        :color="trendChartConfig.accuracy.color"
                        :opacity="0.22"
                        :line="true"
                        :line-color="trendChartConfig.accuracy.color"
                        :line-width="3"
                      />
                      <VisLine
                        :x="(point: TrendChartPoint) => point.timestamp"
                        :y="(point: TrendChartPoint) => point.participation"
                        :color="trendChartConfig.participation.color"
                        :line-width="2"
                      />
                      <VisLine
                        :x="(point: TrendChartPoint) => point.timestamp"
                        :y="(point: TrendChartPoint) => point.practiceVolume"
                        :color="trendChartConfig.practiceVolume.color"
                        :line-width="2"
                      />
                      <ChartCrosshair
                        :template="componentToString(trendChartConfig, ChartTooltipContent, {
                          labelFormatter: formatTrendTooltipLabel,
                          valueFormatter: formatTrendTooltipValue,
                        })"
                        :color="trendChartColors"
                      />
                      <ChartTooltip />
                    </VisXYContainer>
                  </ChartContainer>

                  <div class="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 pb-2 text-xs text-muted-foreground">
                    <div
                      v-for="item in trendLegendItems"
                      :key="item.key"
                      class="flex items-center gap-1.5"
                    >
                      <span
                        class="size-2.5 rounded-sm"
                        :style="{ backgroundColor: item.color }"
                      />
                      <span>{{ item.label }}</span>
                    </div>
                  </div>
                  <p class="px-5 pb-2 text-xs leading-5 text-muted-foreground">
                    Practice volume compares each week's submissions against the busiest week shown.
                  </p>
                </div>

                <Alert v-else>
                  <Activity />
                  <AlertTitle>No weekly trend yet</AlertTitle>
                  <AlertDescription>
                    Weekly accuracy movement will appear once this class has recorded practice activity.
                  </AlertDescription>
                </Alert>
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
                      class="h-full rounded-full transition-[width] duration-300"
                      :class="item.value >= 85
                        ? 'bg-emerald-500'
                        : item.value >= 70
                          ? 'bg-primary'
                          : item.value >= 55
                            ? 'bg-amber-500'
                            : 'bg-destructive'"
                      :style="{ width: `${item.value}%` }"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card v-if="sortedModuleHeatmap.length" class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Module difficulty
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Hardest modules this class
              </CardTitle>
              <CardDescription>
                Ranked by overall class accuracy â€” weakest modules surface first so you know where to focus your next coaching session.
              </CardDescription>
            </CardHeader>

            <CardContent class="grid gap-3 lg:grid-cols-2">
              <div
                v-for="module in sortedModuleHeatmap"
                :key="module.moduleId"
                class="flex flex-col gap-3 rounded-2xl border border-border/70 bg-muted/30 p-4"
              >
                <div class="flex items-center justify-between gap-3">
                  <div class="flex min-w-0 items-center gap-2">
                    <BookMarked class="size-4 shrink-0 text-muted-foreground" />
                    <p class="truncate font-semibold text-(--color-heading)">{{ module.title }}</p>
                  </div>
                  <Badge :variant="scoreVariant(module.overall)" class="shrink-0 rounded-full px-3 py-1">
                    {{ module.overall.toFixed(1) }}%
                  </Badge>
                </div>

                <div class="grid grid-cols-3 gap-3">
                  <div
                    v-for="bar in [
                      { label: 'Mora', value: module.mora },
                      { label: 'Consonant', value: module.consonant },
                      { label: 'Vowel', value: module.vowel },
                    ]"
                    :key="bar.label"
                    class="flex flex-col gap-1"
                  >
                    <div class="flex items-center justify-between gap-1">
                      <span class="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                        {{ bar.label }}
                      </span>
                      <span class="text-[10px] tabular-nums text-muted-foreground">
                        {{ bar.value.toFixed(0) }}%
                      </span>
                    </div>
                    <div class="h-1.5 overflow-hidden rounded-full bg-border/70">
                      <div
                        class="h-full rounded-full transition-[width] duration-300"
                        :class="bar.value >= 85
                          ? 'bg-emerald-500'
                          : bar.value >= 70
                            ? 'bg-primary'
                            : bar.value >= 55
                              ? 'bg-amber-500'
                              : 'bg-destructive'"
                        :style="{ width: `${bar.value}%` }"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div class="grid gap-5 lg:grid-cols-2">
            <Card class="border-border/80 bg-card/95">
              <CardHeader class="gap-3">
                <div class="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    Needs attention
                  </Badge>
                  <Badge variant="outline" class="rounded-full px-3 py-1">
                    {{ overview.flagged_students.length }} flagged
                  </Badge>
                </div>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Flagged students
                </CardTitle>
                <CardDescription>
                  Learners below {{ flagThreshold }}% are surfaced here first so you can move directly into drilldown review.
                </CardDescription>
              </CardHeader>

              <CardContent class="flex flex-col gap-2">
                <template v-if="overview.flagged_students.length">
                  <button
                    v-for="student in overview.flagged_students"
                    :key="student.uid"
                    type="button"
                    class="group flex w-full items-center gap-4 rounded-2xl border border-border/70 bg-muted/30 p-4 text-left transition hover:cursor-pointer hover:border-rose-200/80! hover:bg-rose-50/70! active:scale-[0.99]"
                    @click="openStudentDetail(student.uid)"
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
                      <p class="mt-0.5 text-xs text-muted-foreground">
                        {{ student.total_attempts }} attempts · {{ student.streak_days }}d streak
                      </p>
                    </div>

                    <div class="flex shrink-0 items-center gap-2">
                      <Badge variant="destructive" class="rounded-full px-3 py-1">
                        {{ student.overall_average.toFixed(0) }}%
                      </Badge>
                      <ChevronRight class="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                    </div>
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

            <Card class="border-border/80 bg-card/95">
              <CardHeader class="gap-3">
                <div class="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    Excelling
                  </Badge>
                  <Badge variant="outline" class="rounded-full px-3 py-1">
                    {{ topPerformers.length }} excelling
                  </Badge>
                </div>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Top performers
                </CardTitle>
                <CardDescription>
                  Students scoring {{ topPerfThreshold }}% or above, ranked highest first.
                </CardDescription>
              </CardHeader>

              <CardContent class="flex flex-col gap-2">
                <template v-if="topPerformers.length">
                  <button
                    v-for="student in topPerformers"
                    :key="student.uid"
                    type="button"
                    class="group flex w-full items-center gap-4 rounded-2xl border border-border/70 bg-muted/30 p-4 text-left transition hover:cursor-pointer hover:border-emerald-200/80! hover:bg-emerald-50/70! active:scale-[0.99]"
                    @click="openStudentDetail(student.uid)"
                  >
                    <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-emerald-500/10 font-semibold text-emerald-700">
                      {{ student.display_name.slice(0, 1).toUpperCase() }}
                    </div>

                    <div class="min-w-0 flex-1">
                      <p class="truncate font-semibold text-(--color-heading)">
                        {{ student.display_name }}
                      </p>
                      <p class="truncate text-sm text-muted-foreground">
                        {{ student.email }}
                      </p>
                      <p class="mt-0.5 text-xs text-muted-foreground">
                        {{ student.total_attempts }} attempts Â· {{ student.streak_days }}d streak
                      </p>
                    </div>

                    <div class="flex shrink-0 items-center gap-2">
                      <Badge
                        variant="outline"
                        class="rounded-full border-emerald-300/70 bg-emerald-100 px-3 py-1 text-emerald-800"
                      >
                        {{ student.overall_average.toFixed(0) }}%
                      </Badge>
                      <ChevronRight class="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </button>
                </template>

                <Alert v-else>
                  <Trophy />
                  <AlertTitle>No top performers yet</AlertTitle>
                  <AlertDescription>
                    Students who reach {{ topPerfThreshold }}% or above will be shown here.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </template>
      </template>
    </div>

    <StudentDetailDialog
      v-model:open="detailModalOpen"
      :student="selectedStudent"
      :drilldown="drilldown"
      :loading="drilldownLoading"
    />
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { VisArea, VisAxis, VisLine, VisXYContainer } from '@unovis/vue'
import {
  Activity,
  BookMarked,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  TrendingUp,
  TriangleAlert,
  Trophy,
  UserRoundCheck,
  UserRoundX,
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
import StudentDetailDialog from '@/components/instructor/StudentDetailDialog.vue'
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
  type ChartConfig,
} from '@/components/ui/chart'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { getAllStudents, getClassOverview, getPhonemeHeatmap, getStudentDrillDown } from '@/api/analytics'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { ClassOverview, PhonemeBreakdown, StudentDrillDown, StudentStat } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const overview = ref<ClassOverview | null>(null)
const students = ref<StudentStat[]>([])
const heatmap = ref<Record<string, PhonemeBreakdown>>({})
const loading = ref(false)
const error = ref<string | null>(null)
const selectedStudentUid = ref<string | null>(null)
const drilldown = ref<StudentDrillDown | null>(null)
const drilldownLoading = ref(false)
const detailModalOpen = ref(false)
const flagThreshold = 60
const topPerfThreshold = 85
const trendChartConfig = {
  accuracy: {
    label: 'Accuracy',
    color: 'var(--color-chart-1)',
  },
  participation: {
    label: 'Active students',
    color: 'var(--color-chart-2)',
  },
  practiceVolume: {
    label: 'Practice volume',
    color: 'var(--color-chart-3)',
  },
} satisfies ChartConfig
const trendChartColors = [
  trendChartConfig.accuracy.color,
  trendChartConfig.participation.color,
  trendChartConfig.practiceVolume.color,
]
const trendLegendItems = Object.entries(trendChartConfig).map(([key, item]) => ({
  key,
  label: item.label,
  color: item.color,
}))

type TrendChartPoint = {
  week_start: string
  timestamp: number
  accuracy: number
  participation: number
  practiceVolume: number
}

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }),
)

const neverPracticedCount = computed(
  () => students.value.filter((s) => s.total_attempts === 0).length,
)

const topPerformers = computed(() =>
  students.value
    .filter((s) => s.overall_average >= topPerfThreshold && s.total_attempts > 0)
    .sort((a, b) => b.overall_average - a.overall_average)
    .slice(0, 6),
)

const sortedModuleHeatmap = computed(() =>
  Object.entries(heatmap.value)
    .map(([moduleId, scores]) => ({
      moduleId,
      title: modulesStore.modules.find((m) => m.module_id === moduleId)?.title ?? moduleId,
      overall: scores.overall_avg,
      mora: scores.mora_timing_avg,
      consonant: scores.consonant_avg,
      vowel: scores.vowel_avg,
    }))
    .sort((a, b) => a.overall - b.overall),
)

const metricCards = computed(() => {
  if (!overview.value) return []

  return [
    {
      label: 'Class average',
      value: `${overview.value.class_average.toFixed(1)}%`,
      copy: 'overall pronunciation accuracy in the active class',
      icon: TrendingUp,
      tone: null as string | null,
    },
    {
      label: 'Total students',
      value: `${overview.value.total_students}`,
      copy: 'learners currently enrolled in this roster',
      icon: Users,
      tone: null as string | null,
    },
    {
      label: 'Active this week',
      value: `${overview.value.active_students}`,
      copy: 'students who practiced recently',
      icon: UserRoundCheck,
      tone: null as string | null,
    },
    {
      label: 'Weekly attempts',
      value: `${overview.value.weekly_attempts}`,
      copy: 'submissions recorded inside the current week window',
      icon: Activity,
      tone: null as string | null,
    },
    {
      label: 'Never practiced',
      value: `${neverPracticedCount.value}`,
      copy: 'enrolled students with no practice attempts yet',
      icon: UserRoundX,
      tone: neverPracticedCount.value > 0 ? 'text-destructive' : (null as string | null),
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

const displayTrend = computed(() => overview.value?.weekly_trend.slice(-8) ?? [])
const trendChartData = computed<TrendChartPoint[]>(() => {
  const weeks = displayTrend.value
  if (!weeks.length) return []

  const maxAttempts = Math.max(...weeks.map((week) => week.attempt_count), 1)
  const totalStudents = Math.max(overview.value?.total_students ?? 0, 1)

  return weeks.map((week) => ({
    week_start: week.week_start,
    timestamp: new Date(week.week_start).getTime(),
    accuracy: week.attempt_count ? week.average_accuracy : 0,
    participation: Math.min(100, ((week.active_students ?? 0) / totalStudents) * 100),
    practiceVolume: Math.min(100, (week.attempt_count / maxAttempts) * 100),
  }))
})

const selectedStudent = computed(() =>
  overview.value?.flagged_students.find((s) => s.uid === selectedStudentUid.value)
  ?? students.value.find((s) => s.uid === selectedStudentUid.value)
  ?? null,
)


async function openStudentDetail(uid: string) {
  selectedStudentUid.value = uid
  drilldown.value = null
  drilldownLoading.value = true
  detailModalOpen.value = true
  try {
    drilldown.value = await getStudentDrillDown(uid, classesStore.activeClassId!)
  } catch {
    // dialog handles null drilldown gracefully
  } finally {
    drilldownLoading.value = false
  }
}


function formatWeekLabel(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function formatTrendTick(value: number | Date) {
  return formatWeekLabel(new Date(value).toISOString())
}

function formatPercentTick(value: number | Date) {
  const numericValue = typeof value === 'number' ? value : value.getTime()
  return `${numericValue.toFixed(0)}%`
}

function formatTrendTooltipLabel(value: number | Date) {
  return `Week of ${formatWeekLabel(new Date(value).toISOString())}`
}

function formatTrendTooltipValue(value: unknown) {
  if (typeof value !== 'number') return String(value ?? '')
  return `${value.toFixed(0)}%`
}

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}

async function loadOverview(classId: string | null) {
  overview.value = null
  students.value = []
  heatmap.value = {}
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load analytics.'
    return
  }

  loading.value = true
  try {
    const [overviewData, studentsData, heatmapData] = await Promise.all([
      getClassOverview(classId, flagThreshold),
      getAllStudents(classId, flagThreshold),
      getPhonemeHeatmap(classId),
    ])
    overview.value = overviewData
    students.value = studentsData
    heatmap.value = heatmapData
  } catch {
    error.value = 'Failed to load class analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
    await modulesStore.fetchModules()
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

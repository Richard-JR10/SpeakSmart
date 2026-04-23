<template>
  <InstructorLayout>
    <div class="flex flex-col gap-5">
      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Student directory
            </Badge>
            <Badge variant="outline" class="rounded-full px-3 py-1">
              {{ filteredStudents.length }} visible
            </Badge>
          </div>

          <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-end">
            <div class="flex flex-col gap-2">
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading) sm:text-4xl">
                Search the roster and open individual drilldown quickly
              </CardTitle>
              <CardDescription class="max-w-3xl text-sm leading-7 text-foreground/80 sm:text-base">
                Track who is falling behind, compare learner rhythm, and inspect recent attempts without leaving the class context.
              </CardDescription>
            </div>

            <div class="rounded-3xl border border-border/70 bg-muted/30 p-4">
              <Label for="student-search" class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Search students
              </Label>
              <div class="mt-2 flex items-center gap-2 rounded-2xl border border-border bg-background px-3">
                <Search class="text-muted-foreground" />
                <Input
                  id="student-search"
                  v-model="search"
                  class="border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
                  placeholder="Search by name or email"
                />
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent class="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
          <Card
            v-for="item in summaryCards"
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

      <LoadingSpinner
        v-if="loading && !students.length"
        full-screen
        message="Loading students..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Students unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <div v-else class="grid gap-5 xl:grid-cols-[minmax(0,0.92fr)_minmax(360px,0.68fr)]">
        <Card class="border-border/80 bg-card/95">
          <CardHeader class="gap-3">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div class="flex flex-col gap-2">
                <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Class roster
                </Badge>
                <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ filteredStudents.length }} learners
                </CardTitle>
                <CardDescription>
                  Select any learner to inspect their averages, weakest area, and recent attempts.
                </CardDescription>
              </div>

              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ flaggedCount }} flagged
              </Badge>
            </div>
          </CardHeader>

          <CardContent class="flex flex-col gap-3">
            <template v-if="filteredStudents.length">
              <button
                v-for="student in filteredStudents"
                :key="student.uid"
                type="button"
                class="flex w-full items-start gap-4 rounded-2xl border p-4 text-left transition"
                :class="selectedStudentUid === student.uid
                  ? 'border-primary/35 bg-primary/5'
                  : student.is_flagged
                    ? 'border-destructive/20 bg-destructive/5 hover:border-destructive/35'
                    : 'border-border/70 bg-muted/30 hover:border-primary/30 hover:bg-muted/45'"
                @click="selectStudent(student.uid)"
              >
                <div
                  class="flex size-11 shrink-0 items-center justify-center rounded-2xl font-semibold"
                  :class="student.is_flagged ? 'bg-destructive/10 text-destructive' : 'bg-secondary text-primary'"
                >
                  {{ student.display_name.slice(0, 1).toUpperCase() }}
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="truncate font-semibold text-(--color-heading)">
                      {{ student.display_name }}
                    </p>
                    <Badge :variant="student.is_flagged ? 'destructive' : 'secondary'" class="rounded-full px-2.5 py-1">
                      {{ student.is_flagged ? 'Needs review' : 'On track' }}
                    </Badge>
                  </div>

                  <p class="mt-1 truncate text-sm text-muted-foreground">
                    {{ student.email }}
                  </p>

                  <div class="mt-3 grid gap-3 sm:grid-cols-3">
                    <div class="flex flex-col gap-1">
                      <span class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                        Accuracy
                      </span>
                      <div class="flex items-center gap-2">
                        <div class="h-2 flex-1 overflow-hidden rounded-full bg-border/70">
                          <div
                            class="h-full rounded-full bg-primary"
                            :style="{ width: `${student.overall_average}%` }"
                          />
                        </div>
                        <span class="text-sm font-semibold text-(--color-heading)">
                          {{ student.overall_average.toFixed(0) }}%
                        </span>
                      </div>
                    </div>

                    <div class="flex flex-col gap-1">
                      <span class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                        Attempts
                      </span>
                      <span class="text-sm font-semibold text-(--color-heading)">
                        {{ student.total_attempts }}
                      </span>
                    </div>

                    <div class="flex flex-col gap-1">
                      <span class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                        Streak
                      </span>
                      <span class="text-sm font-semibold text-(--color-heading)">
                        {{ student.streak_days }} days
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            </template>

            <Alert v-else>
              <UserRoundSearch />
              <AlertTitle>No matching students</AlertTitle>
              <AlertDescription>
                Adjust the search input or switch the active class to see a different roster.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <Card class="border-border/80 bg-card/95">
          <CardHeader class="gap-3">
            <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Learner detail
            </Badge>

            <template v-if="selectedStudent">
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                {{ selectedStudent.display_name }}
              </CardTitle>
              <CardDescription>
                {{ selectedStudent.email }}
              </CardDescription>
            </template>

            <template v-else>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Select a student
              </CardTitle>
              <CardDescription>
                Choose a learner from the roster to inspect their drilldown summary.
              </CardDescription>
            </template>
          </CardHeader>

          <CardContent class="flex flex-col gap-4">
            <LoadingSpinner v-if="drilldownLoading" size="sm" />

            <template v-else-if="selectedStudent && drilldown">
              <div class="grid gap-3 sm:grid-cols-3">
                <Card class="gap-0 bg-muted/30 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Average
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ drilldown.overall_average.toFixed(1) }}%
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="gap-0 bg-muted/30 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Attempts
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ drilldown.total_attempts }}
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="gap-0 bg-muted/30 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Streak
                    </p>
                    <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                      {{ drilldown.streak_days }}
                    </CardTitle>
                  </CardHeader>
                </Card>
              </div>

              <Separator />

              <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between gap-3">
                  <p class="font-semibold text-(--color-heading)">Weakest module</p>
                  <Badge :variant="selectedStudent.is_flagged ? 'destructive' : 'outline'" class="rounded-full px-3 py-1">
                    {{ formatModuleId(drilldown.weakest_module_id) }}
                  </Badge>
                </div>

                <div class="grid gap-3">
                  <div
                    v-for="item in phonemeRows"
                    :key="item.label"
                    class="rounded-2xl border border-border/70 bg-muted/30 p-4"
                  >
                    <div class="flex items-center justify-between gap-3">
                      <p class="font-semibold text-(--color-heading)">{{ item.label }}</p>
                      <Badge :variant="scoreVariant(item.value)" class="rounded-full px-3 py-1">
                        {{ item.value.toFixed(0) }}%
                      </Badge>
                    </div>
                    <div class="mt-3 h-2 overflow-hidden rounded-full bg-border/70">
                      <div
                        class="h-full rounded-full bg-primary"
                        :style="{ width: `${item.value}%` }"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between gap-3">
                  <p class="font-semibold text-(--color-heading)">Recent attempts</p>
                  <Badge variant="outline" class="rounded-full px-3 py-1">
                    {{ drilldown.recent_attempts.length }} shown
                  </Badge>
                </div>

                <template v-if="drilldown.recent_attempts.length">
                  <div
                    v-for="attempt in drilldown.recent_attempts"
                    :key="attempt.attempt_id"
                    class="rounded-2xl border border-border/70 bg-muted/30 p-4"
                  >
                    <div class="flex flex-wrap items-start justify-between gap-3">
                      <div class="min-w-0">
                        <p class="font-semibold text-(--color-heading)">
                          {{ attempt.phrase_id }}
                        </p>
                        <p class="mt-1 text-sm text-muted-foreground">
                          {{ formatAttemptDate(attempt.attempted_at) }}
                        </p>
                      </div>

                      <Badge :variant="scoreVariant(attempt.accuracy_score)" class="rounded-full px-3 py-1">
                        {{ attempt.accuracy_score.toFixed(0) }}%
                      </Badge>
                    </div>

                    <p v-if="attempt.feedback_text" class="mt-3 text-sm leading-7 text-muted-foreground">
                      {{ attempt.feedback_text }}
                    </p>
                  </div>
                </template>

                <Alert v-else>
                  <Clock3 />
                  <AlertTitle>No recent attempts</AlertTitle>
                  <AlertDescription>
                    This learner has not recorded any recent speaking attempts for the selected class.
                  </AlertDescription>
                </Alert>
              </div>
            </template>

            <Alert v-else>
              <UserRoundSearch />
              <AlertTitle>No learner selected</AlertTitle>
              <AlertDescription>
                Pick a student from the roster to open their progress summary here.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  ChartColumn,
  Clock3,
  Search,
  TriangleAlert,
  UserRoundCheck,
  UserRoundSearch,
  Users,
} from 'lucide-vue-next'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { getAllStudents, getStudentDrillDown } from '@/api/analytics'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { useClassesStore } from '@/stores/classes'
import type { StudentDrillDown, StudentStat } from '@/types'

const classesStore = useClassesStore()

const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const search = ref('')
const selectedStudentUid = ref<string | null>(null)
const drilldown = ref<StudentDrillDown | null>(null)
const drilldownLoading = ref(false)

const filteredStudents = computed(() => {
  if (!search.value) return students.value
  const query = search.value.toLowerCase()
  return students.value.filter((student) =>
    student.display_name.toLowerCase().includes(query)
    || student.email.toLowerCase().includes(query),
  )
})

const selectedStudent = computed(
  () => students.value.find((student) => student.uid === selectedStudentUid.value) ?? null,
)

const flaggedCount = computed(() => students.value.filter((student) => student.is_flagged).length)

const summaryCards = computed(() => [
  {
    label: 'Students',
    value: `${students.value.length}`,
    copy: 'learners currently visible in this class roster',
    icon: Users,
  },
  {
    label: 'Flagged',
    value: `${flaggedCount.value}`,
    copy: 'students currently below the review threshold',
    icon: TriangleAlert,
  },
  {
    label: 'Selected',
    value: selectedStudent.value?.display_name ?? 'None',
    copy: selectedStudent.value ? 'active learner in the drilldown panel' : 'choose a learner to inspect detail',
    icon: UserRoundCheck,
  },
  {
    label: 'Search results',
    value: `${filteredStudents.value.length}`,
    copy: 'matching learners after the current roster filter',
    icon: ChartColumn,
  },
])

const phonemeRows = computed(() => {
  if (!drilldown.value) return []

  return [
    { label: 'Mora timing', value: drilldown.value.phoneme_breakdown.mora_timing_avg },
    { label: 'Consonants', value: drilldown.value.phoneme_breakdown.consonant_avg },
    { label: 'Vowel purity', value: drilldown.value.phoneme_breakdown.vowel_avg },
  ]
})

function formatModuleId(moduleId: string | null | undefined) {
  if (!moduleId) return 'Not enough data'
  return moduleId.replace('module_', '').replace(/_/g, ' ')
}

function formatAttemptDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}

async function selectStudent(uid: string) {
  const classId = classesStore.activeClassId
  if (!classId) return

  selectedStudentUid.value = uid
  drilldown.value = null
  drilldownLoading.value = true

  try {
    drilldown.value = await getStudentDrillDown(uid, classId)
  } catch {
    drilldown.value = null
  } finally {
    drilldownLoading.value = false
  }
}

async function loadStudents(classId: string | null) {
  students.value = []
  selectedStudentUid.value = null
  drilldown.value = null
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load students.'
    return
  }

  loading.value = true
  try {
    students.value = await getAllStudents(classId)
    if (students.value.length) {
      await selectStudent(students.value[0].uid)
    }
  } catch {
    error.value = 'Failed to load students.'
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
  await loadStudents(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadStudents(classId)
  },
)
</script>

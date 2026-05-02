<template>
  <InstructorLayout>
    <div class="flex flex-col gap-4">
      <Card class="border-rose-200/80 bg-gradient-to-br from-card via-card to-rose-50/70 shadow-sm shadow-rose-900/5">
        <CardHeader class="gap-3 p-4 sm:p-5">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <Badge class="rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary uppercase tracking-[0.18em] hover:bg-primary/10">
                  Student directory
                </Badge>
                <Badge variant="outline" class="rounded-full border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">
                  {{ filteredStudents.length }} visible
                </Badge>
              </div>

              <CardTitle class="mt-3 font-(--font-display) text-2xl leading-none text-(--color-heading) sm:text-3xl">
                Roster scan
              </CardTitle>
              <CardDescription class="mt-1 max-w-2xl text-sm">
                Search learners, spot review needs, and open details only when you need the drilldown.
              </CardDescription>
            </div>

            <div class="w-full lg:max-w-sm">
              <Label for="student-search" class="sr-only">Search students</Label>
              <div class="flex h-11 items-center gap-2 rounded-xl border border-rose-200 bg-white/85 px-3 shadow-xs shadow-rose-900/5 transition focus-within:border-primary/60 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background">
                <Search class="size-4 text-muted-foreground" />
                <Input
                  id="student-search"
                  v-model="search"
                  class="h-9 rounded-none border-0 bg-transparent px-0 text-sm shadow-none ring-0 outline-none focus-visible:!border-transparent focus-visible:!shadow-none focus-visible:!ring-0 focus-visible:!ring-offset-0 focus-visible:!outline-none"
                  placeholder="Search by name or email"
                />
              </div>
            </div>
          </div>

          <div class="grid overflow-hidden rounded-2xl border border-rose-200/80 bg-white/70 shadow-inner shadow-rose-900/5 sm:grid-cols-3">
            <div
              v-for="item in summaryCards"
              :key="item.label"
              class="flex items-center justify-between gap-3 border-b border-rose-200/80 px-4 py-3 last:border-b-0 sm:border-r sm:border-b-0 sm:last:border-r-0"
              :class="item.surfaceClass"
            >
              <div class="min-w-0">
                <p class="truncate text-[11px] font-semibold uppercase tracking-[0.16em]" :class="item.labelClass">
                  {{ item.label }}
                </p>
                <p class="mt-1 truncate font-(--font-display) text-2xl leading-none text-(--color-heading)">
                  {{ item.value }}
                </p>
              </div>
              <component :is="item.icon" class="size-5 shrink-0" :class="item.iconClass" />
            </div>
          </div>
        </CardHeader>
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

      <Card v-else class="gap-0 overflow-hidden border-rose-200/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
        <CardHeader class="border-b border-rose-200/80 bg-linear-to-r from-white via-rose-50/60 to-white p-0!">
          <div class="flex min-h-14 flex-wrap items-center justify-between gap-3 px-5 py-3">
            <div class="flex min-w-0 flex-wrap items-center gap-3">
              <CardTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
                Class roster
              </CardTitle>
              <Badge class="rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary hover:bg-primary/10">
                {{ filteredStudents.length }} {{ filteredStudents.length === 1 ? 'learner' : 'learners' }}
              </Badge>
              <span class="hidden truncate text-sm text-muted-foreground lg:inline">
                Open learner details in a modal without leaving the list.
              </span>
            </div>

            <Badge
              variant="outline"
              class="rounded-full px-3 py-1"
              :class="flaggedCount ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'"
            >
              {{ flaggedCount }} flagged
            </Badge>
          </div>
        </CardHeader>

        <CardContent class="p-0">
          <template v-if="filteredStudents.length">
            <Table class="min-w-205 table-fixed">
                <colgroup>
                  <col class="w-[40%]">
                  <col class="w-[30%]">
                  <col class="w-[20%]">
                  <col class="w-[10%]">
                </colgroup>
                <TableHeader class="bg-rose-50/60">
                  <TableRow class="hover:bg-transparent">
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Learner
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Progress
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Activity
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Action
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="student in filteredStudents"
                    :key="student.uid"
                    class="transition hover:bg-rose-50/45"
                  >
                    <TableCell class="px-5 py-3 align-middle">
                      <div class="flex min-w-0 items-center gap-3">
                        <div
                          class="flex size-9 shrink-0 items-center justify-center rounded-xl border text-sm font-semibold"
                          :class="student.is_flagged ? 'border-red-200 bg-red-50 text-red-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'"
                        >
                          {{ student.display_name.slice(0, 1).toUpperCase() }}
                        </div>

                        <div class="min-w-0">
                          <div class="flex min-w-0 flex-wrap items-center gap-2">
                            <p class="truncate font-semibold text-(--color-heading)">
                              {{ student.display_name }}
                            </p>
                            <Badge
                              class="rounded-full border px-2.5 py-1 text-xs"
                              :class="student.is_flagged ? 'border-red-200 bg-red-50 text-red-700 hover:bg-red-50' : 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50'"
                            >
                              {{ student.is_flagged ? 'Needs review' : 'On track' }}
                            </Badge>
                          </div>
                          <p class="truncate text-xs text-muted-foreground">
                            {{ student.email }}
                          </p>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell class="px-5 py-3 align-middle">
                      <div class="w-full max-w-72">
                        <div class="grid grid-cols-[minmax(120px,220px)_3rem] items-center gap-3">
                          <div class="h-1.5 overflow-hidden rounded-full bg-rose-100">
                            <div
                              class="h-full rounded-full"
                              :class="progressToneClass(student)"
                              :style="{ width: `${student.overall_average}%` }"
                            />
                          </div>
                          <span class="text-left text-sm font-semibold leading-none tabular-nums text-(--color-heading)">
                            {{ student.overall_average.toFixed(0) }}%
                          </span>
                        </div>
                        <p class="mt-1 text-xs text-muted-foreground">Overall accuracy</p>
                      </div>
                    </TableCell>

                    <TableCell class="px-5 py-3 align-middle">
                      <p class="font-semibold tabular-nums text-(--color-heading)">
                        {{ student.total_attempts }}
                        <span class="font-normal text-muted-foreground">attempts</span>
                      </p>
                      <p class="mt-1 text-xs text-muted-foreground">
                        {{ student.streak_days }} day streak
                      </p>
                    </TableCell>

                    <TableCell class="px-5 py-3 text-left align-middle">
                      <div class="flex justify-start">
                        <Button class="border-primary/25 bg-white text-primary shadow-xs shadow-rose-900/5 hover:bg-primary/10 hover:text-primary" variant="outline" size="sm" @click="openStudentDetail(student.uid)">
                          <Eye data-icon="inline-start" />
                          <span>View</span>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
          </template>

          <div v-else class="p-5">
            <Alert class="border-sky-200 bg-sky-50 text-sky-950">
              <UserRoundSearch />
              <AlertTitle>No matching students</AlertTitle>
              <AlertDescription>
                Adjust the search input or switch the active class to see a different roster.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>

      <DialogRoot :open="detailModalOpen" @update:open="handleDetailModalOpenChange">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-rose-950/25 backdrop-blur-sm" />
          <DialogContent class="fixed top-1/2 left-1/2 z-50 grid max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-5xl -translate-x-1/2 -translate-y-1/2 gap-4 overflow-y-auto rounded-2xl border border-rose-200 bg-gradient-to-br from-background via-card to-rose-50 p-5 shadow-lg shadow-rose-950/15 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 sm:p-6">
            <button
              type="button"
              class="absolute top-4 right-4 rounded-full p-1 text-muted-foreground transition hover:bg-muted hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
              aria-label="Close learner detail"
              @click="detailModalOpen = false"
            >
              <X class="size-5" />
            </button>

            <div class="pr-10">
              <Badge class="w-fit rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary uppercase tracking-[0.18em] hover:bg-primary/10">
                Learner detail
              </Badge>

              <template v-if="selectedStudent">
                <DialogTitle class="mt-3 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ selectedStudent.display_name }}
                </DialogTitle>
                <DialogDescription class="mt-1 text-sm text-muted-foreground">
                  {{ selectedStudent.email }}
                </DialogDescription>
              </template>

              <template v-else>
                <DialogTitle class="mt-3 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Learner detail
                </DialogTitle>
                <DialogDescription class="mt-1 text-sm text-muted-foreground">
                  Loading selected learner.
                </DialogDescription>
              </template>
            </div>

            <LoadingSpinner v-if="drilldownLoading" size="sm" />

            <template v-else-if="selectedStudent && drilldown">
              <div class="grid gap-3 sm:grid-cols-3">
                <div class="rounded-2xl border border-emerald-200 bg-emerald-50/70 px-4 py-3">
                  <p class="text-[11px] font-semibold text-emerald-800/70 uppercase tracking-[0.16em]">
                    Average
                  </p>
                  <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ drilldown.overall_average.toFixed(1) }}%
                  </p>
                </div>

                <div class="rounded-2xl border border-sky-200 bg-sky-50/70 px-4 py-3">
                  <p class="text-[11px] font-semibold text-sky-800/70 uppercase tracking-[0.16em]">
                    Attempts
                  </p>
                  <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ drilldown.total_attempts }}
                  </p>
                </div>

                <div class="rounded-2xl border border-amber-200 bg-amber-50/70 px-4 py-3">
                  <p class="text-[11px] font-semibold text-amber-800/70 uppercase tracking-[0.16em]">
                    Streak
                  </p>
                  <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ drilldown.streak_days }}
                  </p>
                </div>
              </div>

              <Separator />

              <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between gap-3">
                  <p class="font-semibold text-(--color-heading)">Weakest module</p>
                  <Badge :variant="selectedStudent.is_flagged ? 'destructive' : 'outline'" class="rounded-full px-3 py-1">
                    {{ formatModuleId(drilldown.weakest_module_id) }}
                  </Badge>
                </div>

                <div class="grid gap-3 md:grid-cols-3">
                  <div
                    v-for="item in phonemeRows"
                    :key="item.label"
                    class="rounded-2xl border border-rose-200/80 bg-white/75 p-3"
                  >
                    <div class="flex items-center justify-between gap-3">
                      <p class="font-semibold text-(--color-heading)">{{ item.label }}</p>
                      <Badge :variant="scoreVariant(item.value)" class="rounded-full px-3 py-1">
                        {{ item.value.toFixed(0) }}%
                      </Badge>
                    </div>
                    <div class="mt-3 h-2 overflow-hidden rounded-full bg-rose-100">
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
                    class="rounded-2xl border border-rose-200/80 bg-white/75 p-3"
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

                    <p v-if="attempt.feedback_text" class="mt-3 text-sm leading-6 text-muted-foreground">
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
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  ChartColumn,
  Clock3,
  Eye,
  Search,
  TriangleAlert,
  UserRoundSearch,
  Users,
  X,
} from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { getAllStudents, getStudentDrillDown } from '@/api/analytics'
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
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
const detailModalOpen = ref(false)

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
    icon: Users,
    surfaceClass: 'bg-emerald-50/40',
    labelClass: 'text-emerald-800/70',
    iconClass: 'text-emerald-700',
  },
  {
    label: 'Flagged',
    value: `${flaggedCount.value}`,
    icon: TriangleAlert,
    surfaceClass: flaggedCount.value ? 'bg-amber-50/55' : 'bg-rose-50/25',
    labelClass: flaggedCount.value ? 'text-amber-800/75' : 'text-rose-900/55',
    iconClass: flaggedCount.value ? 'text-amber-700' : 'text-rose-700/60',
  },
  {
    label: 'Search results',
    value: `${filteredStudents.value.length}`,
    icon: ChartColumn,
    surfaceClass: 'bg-sky-50/45',
    labelClass: 'text-sky-800/70',
    iconClass: 'text-sky-700',
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

function progressToneClass(student: StudentStat) {
  if (student.is_flagged || student.overall_average < 55) return 'bg-red-500'
  if (student.overall_average < 70) return 'bg-amber-500'
  return 'bg-emerald-600'
}

function handleDetailModalOpenChange(open: boolean) {
  detailModalOpen.value = open
}

async function openStudentDetail(uid: string) {
  const classId = classesStore.activeClassId
  if (!classId) return

  selectedStudentUid.value = uid
  drilldown.value = null
  detailModalOpen.value = true
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
  detailModalOpen.value = false
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load students.'
    return
  }

  loading.value = true
  try {
    students.value = await getAllStudents(classId)
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

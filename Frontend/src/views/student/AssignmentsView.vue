<template>
  <StudentLayout title="Assignments" wide>
    <div class="flex flex-col gap-4">
      <section class="flex flex-col gap-4 rounded-2xl border border-border/80 bg-card/95 px-4 py-4 shadow-sm sm:px-5">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div class="flex min-w-0 flex-col gap-2">
            <div class="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Assigned work
              </Badge>
              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ assignments.length }} total
              </Badge>
            </div>
            <div class="flex flex-col gap-1">
              <h1 class="font-(--font-display) text-2xl leading-tight text-(--color-heading) sm:text-3xl">
                Classroom submissions
              </h1>
              <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
                Scan your assigned phrase work, jump into the next recording, and keep review-ready submissions moving.
              </p>
            </div>
          </div>

          <ToggleGroup
            :model-value="assignmentFilter"
            type="single"
            variant="outline"
            class="grid w-full grid-cols-2 gap-2 sm:grid-cols-4 lg:w-auto"
            :spacing="1"
            @update:model-value="updateAssignmentFilter"
          >
            <ToggleGroupItem
              v-for="option in assignmentFilterOptions"
              :key="option.value"
              :value="option.value"
              class="h-10 justify-between rounded-full border-border bg-background px-3 text-xs font-semibold transition-[background-color,border-color,color,box-shadow] hover:bg-muted data-[state=on]:border-primary data-[state=on]:bg-primary data-[state=on]:text-primary-foreground sm:min-w-32"
              :aria-label="`${option.label}: ${assignmentFilterCount(option.value)} assignments`"
            >
              <span>{{ option.label }}</span>
              <span
                class="rounded-full px-2 py-0.5 text-[11px]"
                :class="assignmentFilter === option.value ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
              >
                {{ assignmentFilterCount(option.value) }}
              </span>
            </ToggleGroupItem>
          </ToggleGroup>
        </div>
      </section>

      <Card v-if="loading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-44 flex-col items-center justify-center gap-4 py-10 text-center">
          <LoaderCircle class="animate-spin text-primary" />
          <div class="flex flex-col gap-1">
            <p class="font-semibold text-(--color-heading)">Loading assignments</p>
            <p class="text-sm text-muted-foreground">
              Preparing assigned phrases, submission state, and released review feedback.
            </p>
          </div>
        </CardContent>
      </Card>

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Assignments could not load</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Alert v-else-if="!assignments.length">
        <ClipboardList />
        <AlertTitle>No assignments yet</AlertTitle>
        <AlertDescription>
          Teacher-assigned phrase work will appear here once something is assigned to your account.
        </AlertDescription>
      </Alert>

      <Alert v-else-if="!filteredAssignments.length">
        <SlidersHorizontal />
        <AlertTitle>No {{ currentFilterLabel.toLowerCase() }} assignments</AlertTitle>
        <AlertDescription>{{ emptyFilterDescription }}</AlertDescription>
      </Alert>

      <div v-else class="grid gap-2.5">
        <Card
          v-for="assignment in filteredAssignments"
          :key="assignment.exercise_id"
          class="overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm transition-[border-color,box-shadow] duration-200 hover:border-primary/35 hover:shadow-md"
        >
          <CardContent class="p-0">
            <article class="grid lg:grid-cols-[minmax(220px,0.85fr)_minmax(320px,1.15fr)_220px]">
              <section class="flex min-w-0 flex-col gap-3 border-b border-border/70 p-4 lg:border-r lg:border-b-0">
                <div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div class="flex min-w-0 flex-wrap items-center gap-2">
                    <Badge :class="assignmentStatusClass(assignment)">
                      <component
                        :is="assignmentStatusIcon(assignment)"
                        class="size-3.5"
                        aria-hidden="true"
                      />
                      {{ assignmentStatusLabel(assignment) }}
                    </Badge>
                    <Badge v-if="assignment.is_overdue && assignmentStatus(assignment) !== 'submitted'" variant="destructive" class="rounded-full px-2.5 py-1">
                      Overdue
                    </Badge>
                  </div>

                  <div :class="dueDateClass(assignment)">
                    <CalendarClock class="size-3.5" aria-hidden="true" />
                    <span>{{ dueDateLabel(assignment) }}</span>
                  </div>
                </div>

                <div class="min-w-0">
                  <h2 class="truncate text-base font-semibold text-(--color-heading)">
                    {{ assignment.title }}
                  </h2>
                  <p class="mt-1 truncate text-xs leading-5 text-muted-foreground">
                    <span v-if="classNameForAssignment(assignment)">
                      {{ classNameForAssignment(assignment) }}
                    </span>
                    <span v-else>
                      Classroom assignment
                    </span>
                  </p>
                </div>
              </section>

              <section class="grid min-w-0 content-start gap-2 border-b border-border/70 bg-muted/15 p-4 lg:border-r lg:border-b-0">
                <div class="flex items-center justify-between gap-3">
                  <p class="text-[11px] font-semibold uppercase text-muted-foreground">
                    Phrase work
                  </p>
                  <span class="text-xs font-medium tabular-nums text-muted-foreground">
                    {{ submittedPhraseCount(assignment) }}/{{ assignment.phrases.length }} submitted
                  </span>
                </div>

                <div class="grid gap-2 xl:grid-cols-2">
                  <article
                    v-for="phraseStatus in assignment.phrases"
                    :key="phraseStatus.phrase_id"
                    class="grid min-w-0 grid-cols-[minmax(0,1fr)_auto] items-center gap-3 rounded-xl border border-border/70 bg-background px-3 py-2.5"
                  >
                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-(--color-heading)">
                        {{ phraseLabel(phraseStatus.phrase_id) }}
                      </p>
                      <p class="truncate text-[11px] leading-4 text-muted-foreground">
                        {{ phraseSecondaryLabel(phraseStatus.phrase_id) }}
                      </p>
                    </div>
                    <span :class="phraseStatusClass(phraseStatus)">
                      <span class="sr-only">{{ phraseStatusText(phraseStatus) }}</span>
                      <span v-if="phraseStatus.released_at && phraseStatus.teacher_accuracy_score != null">
                        {{ phraseStatus.teacher_accuracy_score.toFixed(0) }}%
                      </span>
                      <component
                        v-else
                        :is="phraseStatusIcon(phraseStatus)"
                        class="size-3.5"
                        aria-hidden="true"
                      />
                    </span>
                  </article>
                </div>
              </section>

              <aside class="flex flex-col justify-between gap-4 bg-muted/20 p-4">
                <div class="grid gap-2">
                  <div class="flex items-center justify-between gap-3 text-xs">
                    <span class="font-medium text-muted-foreground">Progress</span>
                    <span class="font-semibold tabular-nums text-(--color-heading)">
                      {{ Math.round(assignmentCompletion(assignment)) }}%
                    </span>
                  </div>
                  <div class="h-2 overflow-hidden rounded-full bg-border/70">
                    <div
                      class="h-full rounded-full"
                      :class="assignmentProgressClass(assignment)"
                      :style="{ width: `${assignmentCompletion(assignment)}%` }"
                    />
                  </div>
                </div>

                <Button
                  size="sm"
                  class="w-full justify-center"
                  @click="openAssignment(assignment)"
                >
                  <ArrowRight data-icon="inline-start" />
                  <span>{{ assignmentStatus(assignment) === 'submitted' ? 'View Feedback' : 'Open' }}</span>
                </Button>
              </aside>
            </article>
          </CardContent>
        </Card>
      </div>
    </div>

    <DialogRoot :open="feedbackModalOpen" @update:open="handleFeedbackModalOpenChange">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/45 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent class="fixed top-1/2 left-1/2 z-50 grid max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-3xl -translate-x-1/2 -translate-y-1/2 gap-5 overflow-y-auto rounded-2xl border border-border bg-background p-5 shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 sm:p-6">
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex min-w-0 flex-col gap-2">
                <div class="flex flex-wrap items-center gap-2">
                  <Badge class="gap-1.5 rounded-full border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-950">
                    <MessageSquareText class="size-3.5" aria-hidden="true" />
                    {{ selectedReleasedFeedbackCount }}/{{ selectedFeedbackPhrases.length }} released
                  </Badge>
                  <Badge v-if="selectedFeedbackClassName" variant="outline" class="max-w-full truncate rounded-full px-2.5 py-1">
                    {{ selectedFeedbackClassName }}
                  </Badge>
                  <Badge v-if="selectedFeedbackDueLabel" variant="outline" class="gap-1.5 rounded-full px-2.5 py-1">
                    <CalendarClock class="size-3.5" aria-hidden="true" />
                    {{ selectedFeedbackDueLabel }}
                  </Badge>
                </div>

                <DialogTitle class="text-balance font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                  Assignment feedback
                </DialogTitle>
                <DialogDescription class="text-pretty text-sm leading-6 text-muted-foreground">
                  {{ selectedFeedbackAssignment?.title ?? 'Assignment review' }}
                </DialogDescription>
              </div>

              <div class="flex shrink-0 items-start justify-between gap-2 sm:justify-end">
                <div class="flex w-fit flex-col rounded-xl border border-border/70 bg-muted/30 px-4 py-3 text-(--color-heading)">
                  <span class="text-[11px] font-semibold uppercase text-muted-foreground">
                    Overall score
                  </span>
                  <span class="mt-1 font-(--font-display) text-4xl leading-none tabular-nums">
                    {{ selectedOverallScore == null ? 'Pending' : `${selectedOverallScore}%` }}
                  </span>
                </div>

                <DialogClose class="rounded-full p-2 text-muted-foreground transition-opacity hover:bg-muted hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-hidden">
                  <X class="size-4" aria-hidden="true" />
                  <span class="sr-only">Close feedback</span>
                </DialogClose>
              </div>
            </div>

            <section class="grid gap-3">
              <article
                v-for="phraseStatus in selectedFeedbackPhrases"
                :key="phraseStatus.phrase_id"
                class="grid gap-3 rounded-2xl border border-border/70 bg-muted/15 p-4 sm:grid-cols-[minmax(0,1fr)_auto]"
              >
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="truncate text-base font-semibold text-(--color-heading)">
                      {{ phraseLabel(phraseStatus.phrase_id) }}
                    </p>
                    <Badge :class="feedbackRowStatusClass(phraseStatus)">
                      {{ feedbackRowStatusText(phraseStatus) }}
                    </Badge>
                  </div>
                  <p class="mt-1 truncate text-xs leading-5 text-muted-foreground">
                    {{ phraseSecondaryLabel(phraseStatus.phrase_id) }}
                  </p>
                  <p class="mt-3 text-sm leading-6 text-muted-foreground">
                    {{ feedbackRowMessage(phraseStatus) }}
                  </p>
                </div>

                <div
                  v-if="phraseStatus.released_at && phraseStatus.teacher_accuracy_score != null"
                  class="flex h-11 min-w-16 items-center justify-center rounded-xl border border-emerald-200 bg-emerald-50 px-3 text-sm font-semibold tabular-nums text-emerald-950"
                >
                  {{ phraseStatus.teacher_accuracy_score.toFixed(0) }}%
                </div>
              </article>
            </section>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'
import {
  ArrowRight,
  CalendarClock,
  CheckCircle2,
  CircleDashed,
  ClipboardList,
  Clock3,
  LoaderCircle,
  MessageSquareText,
  SlidersHorizontal,
  TriangleAlert,
  X,
} from 'lucide-vue-next'

import { getStudentAssignments } from '@/api/assignments'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { AssignmentPhraseStatus, StudentAssignment } from '@/types'

type AssignmentFilter = 'all' | 'submitted' | 'ongoing' | 'no_submission'
type AssignmentStatus = Exclude<AssignmentFilter, 'all'>

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const assignments = ref<StudentAssignment[]>([])
const loading = shallowRef(false)
const error = shallowRef<string | null>(null)
const assignmentFilter = shallowRef<AssignmentFilter>('all')
const feedbackModalOpen = shallowRef(false)
const selectedFeedbackAssignment = shallowRef<StudentAssignment | null>(null)

const assignmentFilterOptions: { value: AssignmentFilter, label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'no_submission', label: 'No submission' },
]

const assignmentFilterValues = new Set<AssignmentFilter>(
  assignmentFilterOptions.map((option) => option.value),
)

const assignmentStatusCounts = computed<Record<AssignmentStatus, number>>(() => ({
  submitted: assignments.value.filter((assignment) => assignmentStatus(assignment) === 'submitted').length,
  ongoing: assignments.value.filter((assignment) => assignmentStatus(assignment) === 'ongoing').length,
  no_submission: assignments.value.filter((assignment) => assignmentStatus(assignment) === 'no_submission').length,
}))

const filteredAssignments = computed(() => {
  if (assignmentFilter.value === 'all') {
    return assignments.value
  }

  return assignments.value.filter((assignment) => assignmentStatus(assignment) === assignmentFilter.value)
})

const currentFilterLabel = computed(() =>
  assignmentFilterOptions.find((option) => option.value === assignmentFilter.value)?.label ?? 'Filtered',
)

const emptyFilterDescription = computed(() => {
  if (assignmentFilter.value === 'submitted') {
    return 'Submitted assignments will appear here after every phrase has a recording.'
  }
  if (assignmentFilter.value === 'ongoing') {
    return 'Partially submitted assignments will appear here once recording is underway.'
  }
  if (assignmentFilter.value === 'no_submission') {
    return 'Past-due assignments with no recordings will appear here.'
  }
  return 'Teacher-assigned phrase work will appear here once something is assigned to your account.'
})
const selectedFeedbackClassName = computed(() =>
  selectedFeedbackAssignment.value
    ? classNameForAssignment(selectedFeedbackAssignment.value)
    : null,
)
const selectedFeedbackDueLabel = computed(() =>
  selectedFeedbackAssignment.value?.due_date
    ? dueDateLabel(selectedFeedbackAssignment.value)
    : null,
)
const selectedFeedbackPhrases = computed(() => selectedFeedbackAssignment.value?.phrases ?? [])
const selectedReleasedFeedbackCount = computed(() =>
  selectedFeedbackPhrases.value.filter((phrase) => phrase.released_at).length,
)
const selectedScoredReleasedPhrases = computed(() =>
  selectedFeedbackPhrases.value.filter((phrase) =>
    phrase.released_at && phrase.teacher_accuracy_score != null,
  ),
)
const selectedOverallScore = computed(() => {
  const scoredPhrases = selectedScoredReleasedPhrases.value
  if (!scoredPhrases.length) return null

  const totalScore = scoredPhrases.reduce((total, phrase) => total + (phrase.teacher_accuracy_score ?? 0), 0)
  return Math.round(totalScore / scoredPhrases.length)
})

onMounted(async () => {
  const uid = authStore.uid
  if (!uid) return

  loading.value = true
  error.value = null

  try {
    await Promise.all([
      classesStore.ensureLoaded(),
      modulesStore.fetchModules(),
    ])
    await Promise.all(modulesStore.modules.map((module) => modulesStore.fetchPhrases(module.module_id)))
    assignments.value = await getStudentAssignments(uid)
  } catch (err) {
    console.error('Failed to load assignments:', err)
    error.value = 'We could not load your assignment list right now.'
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr: string) {
  return parseAssignmentDate(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function parseAssignmentDate(dateStr: string) {
  const dateOnlyMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr)
  if (dateOnlyMatch) {
    const [, year, month, day] = dateOnlyMatch
    return new Date(Number(year), Number(month) - 1, Number(day))
  }

  return new Date(dateStr)
}

function dueDateDeadline(dateStr: string) {
  const deadline = parseAssignmentDate(dateStr)
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    deadline.setHours(23, 59, 59, 999)
  }
  return deadline
}

function isPastDueDeadline(assignment: StudentAssignment) {
  if (!assignment.due_date) return false
  return assignment.is_overdue || Date.now() > dueDateDeadline(assignment.due_date).getTime()
}

function submittedPhraseCount(assignment: StudentAssignment) {
  return assignment.phrases.filter((phrase) => phrase.submitted_at).length
}

function assignmentStatus(assignment: StudentAssignment): AssignmentStatus {
  const submittedCount = submittedPhraseCount(assignment)
  const phraseCount = assignment.phrases.length

  if (assignment.completed_at || (phraseCount > 0 && submittedCount === phraseCount)) {
    return 'submitted'
  }
  if (submittedCount === 0 && isPastDueDeadline(assignment)) {
    return 'no_submission'
  }
  return 'ongoing'
}

function assignmentStatusLabel(assignment: StudentAssignment) {
  const status = assignmentStatus(assignment)
  if (status === 'submitted') return 'Submitted'
  if (status === 'ongoing') return 'Ongoing'
  return 'No submission'
}

function assignmentFilterCount(filter: AssignmentFilter) {
  if (filter === 'all') {
    return assignments.value.length
  }

  return assignmentStatusCounts.value[filter]
}

function updateAssignmentFilter(value: unknown) {
  if (typeof value === 'string' && assignmentFilterValues.has(value as AssignmentFilter)) {
    assignmentFilter.value = value as AssignmentFilter
  }
}

function assignmentCompletion(assignment: StudentAssignment) {
  if (!assignment.phrases.length) return 0
  return (submittedPhraseCount(assignment) / assignment.phrases.length) * 100
}

function assignmentStatusClass(assignment: StudentAssignment) {
  const status = assignmentStatus(assignment)
  if (status === 'submitted') {
    return 'gap-1.5 rounded-full border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-950'
  }
  if (status === 'ongoing') {
    return 'gap-1.5 rounded-full border-amber-300 bg-amber-50 px-2.5 py-1 text-amber-950'
  }
  return 'gap-1.5 rounded-full border-red-200 bg-red-50 px-2.5 py-1 text-red-950'
}

function dueDateLabel(assignment: StudentAssignment) {
  if (!assignment.due_date) return 'No due date'
  const label = isPastDueDeadline(assignment) && assignmentStatus(assignment) !== 'submitted'
    ? 'Past due'
    : 'Due'
  return `${label} ${formatDate(assignment.due_date)}`
}

function dueDateClass(assignment: StudentAssignment) {
  if (!assignment.due_date) {
    return 'inline-flex w-fit shrink-0 items-center gap-1.5 rounded-full border border-border/70 bg-muted px-2.5 py-1 text-xs font-semibold text-muted-foreground'
  }
  if (isPastDueDeadline(assignment) && assignmentStatus(assignment) !== 'submitted') {
    return 'inline-flex w-fit shrink-0 items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-semibold tabular-nums text-red-950'
  }
  return 'inline-flex w-fit shrink-0 items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-semibold tabular-nums text-amber-950'
}

function assignmentProgressClass(assignment: StudentAssignment) {
  const status = assignmentStatus(assignment)
  if (status === 'submitted') return 'bg-emerald-600'
  if (status === 'ongoing') return 'bg-amber-500'
  return 'bg-muted-foreground/50'
}

function assignmentStatusIcon(assignment: StudentAssignment) {
  const status = assignmentStatus(assignment)
  if (status === 'submitted') return CheckCircle2
  if (status === 'ongoing') return Clock3
  return CircleDashed
}

function classNameForAssignment(assignment: StudentAssignment) {
  if (!assignment.class_id) return null
  return classesStore.classes.find((item) => item.class_id === assignment.class_id)?.name ?? null
}

function nextPhraseForAssignment(assignment: StudentAssignment) {
  return assignment.phrases.find((phrase) => !phrase.submitted_at)
    ?? assignment.phrases.find((phrase) => !phrase.released_at)
    ?? assignment.phrases.find((phrase) => phrase.released_at)
    ?? assignment.phrases[0]
    ?? null
}

function phraseLabel(phraseId: string) {
  for (const module of modulesStore.modules) {
    const phrase = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === phraseId)
    if (phrase) return phrase.japanese_text
  }
  return phraseId
}

function phraseSecondaryLabel(phraseId: string) {
  for (const module of modulesStore.modules) {
    const phrase = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === phraseId)
    if (phrase) return `${phrase.romaji} - ${phrase.english_translation}`
  }
  return 'Phrase details unavailable'
}

function phraseStatusText(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) return 'Released'
  if (phrase.reviewed_at) return 'Reviewed'
  if (phrase.submitted_at) return 'Submitted'
  return 'Not started'
}

function feedbackRowStatusText(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) return 'Released'
  if (phrase.reviewed_at) return 'Scored by teacher, waiting for release'
  if (phrase.submitted_at) return 'Waiting to be scored by teacher'
  return 'Not submitted'
}

function feedbackRowMessage(phrase: AssignmentPhraseStatus) {
  if (!phrase.released_at) {
    return feedbackRowStatusText(phrase)
  }

  return phrase.teacher_feedback_text?.trim()
    || 'Teacher review is available for this phrase.'
}

function feedbackRowStatusClass(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) {
    return 'rounded-full border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-950'
  }
  if (phrase.reviewed_at) {
    return 'rounded-full border-primary/20 bg-primary/10 px-2.5 py-1 text-primary'
  }
  if (phrase.submitted_at) {
    return 'rounded-full border-amber-300 bg-amber-50 px-2.5 py-1 text-amber-950'
  }
  return 'rounded-full border-border/70 bg-background px-2.5 py-1 text-muted-foreground'
}

function phraseStatusClass(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) {
    return 'inline-flex h-7 min-w-7 items-center justify-center rounded-full border border-emerald-200 bg-emerald-50 px-2 text-[11px] font-semibold text-emerald-950'
  }
  if (phrase.reviewed_at) {
    return 'inline-flex size-7 items-center justify-center rounded-full border border-primary/20 bg-primary/10 text-primary'
  }
  if (phrase.submitted_at) {
    return 'inline-flex size-7 items-center justify-center rounded-full border border-amber-300 bg-amber-50 text-amber-950'
  }
  return 'inline-flex size-7 items-center justify-center rounded-full border border-border/70 bg-background text-muted-foreground'
}

function phraseStatusIcon(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) return MessageSquareText
  if (phrase.reviewed_at) return CheckCircle2
  if (phrase.submitted_at) return Clock3
  return CircleDashed
}

function openFeedbackModal(assignment: StudentAssignment) {
  selectedFeedbackAssignment.value = assignment
  feedbackModalOpen.value = true
}

function closeFeedbackModal() {
  feedbackModalOpen.value = false
  selectedFeedbackAssignment.value = null
}

function handleFeedbackModalOpenChange(open: boolean) {
  if (!open) {
    closeFeedbackModal()
    return
  }
  feedbackModalOpen.value = true
}

async function openAssignment(assignment: StudentAssignment) {
  if (assignmentStatus(assignment) === 'submitted') {
    openFeedbackModal(assignment)
    return
  }

  const nextPhrase = nextPhraseForAssignment(assignment)
  if (!nextPhrase) {
    return
  }

  await router.push(`/assignments/${assignment.exercise_id}/${nextPhrase.phrase_id}`)
}
</script>

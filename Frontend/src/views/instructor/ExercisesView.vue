<template>
  <InstructorLayout>
    <div class="flex flex-col gap-5">
      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Practice assignments
              </Badge>
              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ exercises.length }} total
              </Badge>
            </div>

            <Button size="lg" @click="showForm = true">
              <Plus data-icon="inline-start" />
              <span>New exercise</span>
            </Button>
          </div>

          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
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
          </div>
        </CardHeader>
      </Card>

      <LoadingSpinner
        v-if="loading && !exercises.length"
        full-screen
        message="Loading exercises..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Exercises unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Alert v-else-if="!exercises.length">
        <ClipboardList />
        <AlertTitle>No exercises yet</AlertTitle>
        <AlertDescription>
          Create your first assignment to send phrase work to the active class and review submissions here.
        </AlertDescription>
      </Alert>

      <div v-else class="grid gap-4">
        <Card
          v-for="exercise in exercises"
          :key="exercise.exercise_id"
          class="border-border/80 bg-card/95"
        >
          <CardHeader class="gap-4">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div class="min-w-0 flex flex-col gap-2">
                <div class="flex flex-wrap items-center gap-2">
                  <CardTitle class="text-2xl text-(--color-heading)">
                    {{ exercise.title }}
                  </CardTitle>
                  <Badge variant="secondary" class="rounded-full px-2.5 py-1">
                    {{ exercise.phrases.length }} phrases
                  </Badge>
                  <Badge variant="outline" class="rounded-full px-2.5 py-1">
                    {{ exercise.assignments.length }} students
                  </Badge>
                  <Badge
                    v-if="exercise.due_date"
                    :variant="isOverdue(exercise.due_date) ? 'destructive' : 'outline'"
                    class="rounded-full px-2.5 py-1"
                  >
                    Due {{ formatDate(exercise.due_date) }}
                  </Badge>
                </div>

                <CardDescription class="max-w-3xl">
                  {{ completedCount(exercise) }}/{{ exercise.assignments.length }} assigned students have submitted all phrases in this exercise.
                </CardDescription>
              </div>

              <Button
                variant="outline"
                size="icon"
                class="rounded-xl"
                @click="handleDelete(exercise.exercise_id)"
              >
                <Trash2 />
                <span class="sr-only">Delete exercise</span>
              </Button>
            </div>

            <div class="flex flex-col gap-2">
              <div class="h-2 overflow-hidden rounded-full bg-border/70">
                <div
                  class="h-full rounded-full bg-primary transition-[width] duration-300"
                  :style="{ width: `${completionPercent(exercise)}%` }"
                />
              </div>
              <div class="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                <span>{{ completionPercent(exercise).toFixed(0) }}% completion</span>
                <span>•</span>
                <span>{{ submissionsForExercise(exercise.exercise_id).length }} submitted phrases</span>
                <span>•</span>
                <span>{{ pendingReviewCount(exercise.exercise_id) }} pending review</span>
                <span>•</span>
                <span>{{ releasedCount(exercise.exercise_id) }} released</span>
              </div>
            </div>
          </CardHeader>

          <CardContent class="flex flex-col gap-5">
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="phrase in exercise.phrases"
                :key="phrase.id"
                variant="outline"
                class="rounded-full px-3 py-1"
              >
                {{ phraseLabel(phrase.phrase_id) }}
              </Badge>
            </div>

            <Separator />

            <div class="flex flex-col gap-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Submission review
                  </p>
                  <p class="mt-1 text-sm text-muted-foreground">
                    Suggested backend scores stay hidden from the student until you release your review.
                  </p>
                </div>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ submissionsForExercise(exercise.exercise_id).length }} submissions
                </Badge>
              </div>

              <LoadingSpinner v-if="submissionsLoading[exercise.exercise_id]" size="sm" />

              <Alert
                v-else-if="submissionErrors[exercise.exercise_id]"
                variant="destructive"
              >
                <TriangleAlert />
                <AlertTitle>Submission review unavailable</AlertTitle>
                <AlertDescription>{{ submissionErrors[exercise.exercise_id] }}</AlertDescription>
              </Alert>

              <template v-else-if="submissionsForExercise(exercise.exercise_id).length">
                <Card
                  v-for="submission in submissionsForExercise(exercise.exercise_id)"
                  :key="submission.submission_id"
                  class="border-border/70 bg-muted/25 shadow-none"
                >
                  <CardContent class="flex flex-col gap-4 px-4 py-4">
                    <div class="flex flex-wrap items-start justify-between gap-3">
                      <div class="min-w-0">
                        <p class="font-semibold text-(--color-heading)">
                          {{ submission.student_display_name }}
                        </p>
                        <p class="mt-1 text-sm text-muted-foreground">
                          {{ phraseLabel(submission.phrase_id) }} • Submitted {{ formatDate(submission.submitted_at) }}
                        </p>
                      </div>

                      <div class="flex flex-wrap gap-2">
                        <Badge variant="outline" class="rounded-full px-2.5 py-1">
                          Suggested {{ submission.suggested_accuracy_score.toFixed(0) }}%
                        </Badge>
                        <Badge
                          :variant="submission.released_at ? 'default' : submission.reviewed_at ? 'secondary' : 'destructive'"
                          class="rounded-full px-2.5 py-1"
                        >
                          {{ submission.released_at ? 'Released' : submission.reviewed_at ? 'Reviewed' : 'Pending review' }}
                        </Badge>
                      </div>
                    </div>

                    <audio
                      class="w-full"
                      :src="submission.audio_file_url"
                      controls
                      preload="metadata"
                    />

                    <div class="rounded-2xl border border-border/70 bg-background/80 p-4">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Suggested feedback
                      </p>
                      <p class="mt-2 text-sm leading-7 text-foreground/85">
                        {{ submission.suggested_feedback_text || 'No suggested feedback was generated for this submission.' }}
                      </p>
                    </div>

                    <div class="grid gap-4 lg:grid-cols-[180px_minmax(0,1fr)]">
                      <div class="flex flex-col gap-2">
                        <Label :for="`score-${submission.submission_id}`">Teacher score</Label>
                        <Input
                          :id="`score-${submission.submission_id}`"
                          v-model="reviewForms[submission.submission_id].teacher_accuracy_score"
                          type="number"
                          min="0"
                          max="100"
                        />
                      </div>

                      <div class="flex flex-col gap-2">
                        <Label :for="`feedback-${submission.submission_id}`">Teacher feedback</Label>
                        <textarea
                          :id="`feedback-${submission.submission_id}`"
                          v-model="reviewForms[submission.submission_id].teacher_feedback_text"
                          rows="4"
                          class="min-h-28 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground shadow-xs outline-none transition focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
                        />
                      </div>
                    </div>

                    <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                      <Button
                        variant="outline"
                        :disabled="reviewSaving[submission.submission_id]"
                        @click="saveReview(submission, false)"
                      >
                        <LoaderCircle
                          v-if="reviewSaving[submission.submission_id]"
                          class="animate-spin"
                          data-icon="inline-start"
                        />
                        <SquarePen v-else data-icon="inline-start" />
                        <span>Save review</span>
                      </Button>

                      <Button
                        :disabled="reviewSaving[submission.submission_id]"
                        @click="saveReview(submission, true)"
                      >
                        <Send data-icon="inline-start" />
                        <span>Save & Release</span>
                      </Button>

                      <Button
                        v-if="submission.reviewed_at && !submission.released_at"
                        variant="secondary"
                        :disabled="reviewSaving[submission.submission_id]"
                        @click="releaseReview(submission)"
                      >
                        <CheckCheck data-icon="inline-start" />
                        <span>Release existing review</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </template>

              <Alert v-else>
                <AudioLines />
                <AlertTitle>No student submissions yet</AlertTitle>
                <AlertDescription>
                  Assigned phrases will appear here after students record their work.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
      </div>

      <DialogRoot v-model:open="showForm">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 flex max-h-[90dvh] w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-3xl border border-border/80 bg-card shadow-lg"
          >
            <div class="flex items-start justify-between gap-3 border-b border-border/70 px-6 py-5">
              <div class="min-w-0">
                <DialogTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Build an assignment
                </DialogTitle>
                <DialogDescription class="mt-2 text-sm leading-6 text-muted-foreground">
                  Choose the phrases, assign the students, and review their submissions back in this page.
                </DialogDescription>
              </div>

              <Button variant="outline" size="icon" class="rounded-xl" @click="showForm = false">
                <X />
                <span class="sr-only">Close exercise form</span>
              </Button>
            </div>

            <div class="flex-1 overflow-y-auto px-6 py-5">
              <div class="flex flex-col gap-5">
                <div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
                  <div class="flex flex-col gap-2">
                    <Label for="exercise-title">Title</Label>
                    <Input
                      id="exercise-title"
                      v-model="form.title"
                      placeholder="Greetings drill set"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <Label for="exercise-due-date">Due date</Label>
                    <Input
                      id="exercise-due-date"
                      v-model="form.due_date"
                      type="datetime-local"
                    />
                  </div>
                </div>

                <div class="grid gap-5 lg:grid-cols-2">
                  <div class="flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <p class="font-semibold text-(--color-heading)">Select phrases</p>
                        <p class="text-sm text-muted-foreground">
                          {{ form.phrase_ids.length }} selected
                        </p>
                      </div>
                    </div>

                    <div class="max-h-96 overflow-y-auto rounded-3xl border border-border/70 bg-muted/25 p-4">
                      <div class="flex flex-col gap-4">
                        <div
                          v-for="module in modulesStore.modules"
                          :key="module.module_id"
                          class="rounded-2xl border border-border/70 bg-background/80 p-4"
                        >
                          <div class="flex items-center gap-2">
                            <BookMarked class="text-muted-foreground" />
                            <p class="font-semibold text-(--color-heading)">
                              {{ module.title }}
                            </p>
                          </div>

                          <div class="mt-3 flex flex-col gap-2">
                            <label
                              v-for="phrase in modulesStore.getPhrasesForModule(module.module_id)"
                              :key="phrase.phrase_id"
                              class="flex cursor-pointer items-start gap-3 rounded-2xl border border-border/70 bg-muted/30 p-3"
                            >
                              <input
                                v-model="form.phrase_ids"
                                type="checkbox"
                                :value="phrase.phrase_id"
                                class="mt-1 accent-[var(--color-primary)]"
                              >
                              <div class="min-w-0">
                                <p class="font-semibold text-(--color-heading)">
                                  {{ phrase.japanese_text }}
                                </p>
                                <p class="text-sm text-muted-foreground">
                                  {{ phrase.romaji }} • {{ phrase.english_translation }}
                                </p>
                              </div>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-3">
                    <div>
                      <p class="font-semibold text-(--color-heading)">Assign to students</p>
                      <p class="text-sm text-muted-foreground">
                        {{ form.student_uids.length }} selected
                      </p>
                    </div>

                    <div class="max-h-96 overflow-y-auto rounded-3xl border border-border/70 bg-muted/25 p-4">
                      <div class="flex flex-col gap-2">
                        <label
                          v-for="student in students"
                          :key="student.uid"
                          class="flex cursor-pointer items-start gap-3 rounded-2xl border border-border/70 bg-background/80 p-3"
                        >
                          <input
                            v-model="form.student_uids"
                            type="checkbox"
                            :value="student.uid"
                            class="mt-1 accent-[var(--color-primary)]"
                          >
                          <div class="min-w-0">
                            <p class="font-semibold text-(--color-heading)">
                              {{ student.display_name }}
                            </p>
                            <p class="truncate text-sm text-muted-foreground">
                              {{ student.email }}
                            </p>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <Alert v-if="formError" variant="destructive">
                  <TriangleAlert />
                  <AlertTitle>Could not create assignment</AlertTitle>
                  <AlertDescription>{{ formError }}</AlertDescription>
                </Alert>
              </div>
            </div>

            <div class="border-t border-border/70 px-6 py-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
                <Button variant="outline" :disabled="submitting" @click="showForm = false">
                  Cancel
                </Button>
                <Button
                  :disabled="submitting || !form.title || !form.phrase_ids.length || !form.student_uids.length"
                  @click="handleCreate"
                >
                  <LoaderCircle v-if="submitting" class="animate-spin" data-icon="inline-start" />
                  <Plus v-else data-icon="inline-start" />
                  <span>{{ submitting ? 'Creating...' : 'Create and assign' }}</span>
                </Button>
              </div>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  AudioLines,
  BookMarked,
  CheckCheck,
  ClipboardList,
  LoaderCircle,
  Plus,
  Send,
  SquarePen,
  TriangleAlert,
  Trash2,
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
import {
  getExerciseSubmissions,
  releaseAssignmentSubmission,
  reviewAssignmentSubmission,
} from '@/api/assignments'
import { getAllStudents } from '@/api/analytics'
import { createExercise, deleteExercise, getMyExercises } from '@/api/exercises'
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
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { Exercise, InstructorAssignmentSubmission, StudentStat } from '@/types'

const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const exercises = ref<Exercise[]>([])
const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showForm = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const exerciseSubmissions = ref<Record<string, InstructorAssignmentSubmission[]>>({})
const submissionsLoading = ref<Record<string, boolean>>({})
const submissionErrors = ref<Record<string, string | null>>({})
const reviewSaving = ref<Record<string, boolean>>({})
const reviewForms = ref<Record<string, {
  teacher_accuracy_score: string
  teacher_feedback_text: string
}>>({})

const form = ref({
  title: '',
  phrase_ids: [] as string[],
  student_uids: [] as string[],
  due_date: '',
})

const summaryCards = computed(() => [
  {
    label: 'Exercises',
    value: `${exercises.value.length}`,
    copy: 'assignment sets currently active in this class',
    icon: ClipboardList,
  },
  {
    label: 'Students',
    value: `${students.value.length}`,
    copy: 'learners available for the current assignment form',
    icon: Users,
  },
  {
    label: 'Pending review',
    value: `${Object.values(exerciseSubmissions.value).flat().filter((submission) => !submission.reviewed_at).length}`,
    copy: 'submitted phrases still waiting for teacher review',
    icon: TriangleAlert,
  },
  {
    label: 'Released',
    value: `${Object.values(exerciseSubmissions.value).flat().filter((submission) => submission.released_at).length}`,
    copy: 'reviews already visible to students',
    icon: CheckCheck,
  },
])

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function isOverdue(dateStr: string) {
  return new Date(dateStr).getTime() < Date.now()
}

function completedCount(exercise: Exercise) {
  return exercise.assignments.filter((assignment) => assignment.completed_at).length
}

function completionPercent(exercise: Exercise) {
  if (!exercise.assignments.length) return 0
  return (completedCount(exercise) / exercise.assignments.length) * 100
}

function submissionsForExercise(exerciseId: string) {
  return exerciseSubmissions.value[exerciseId] ?? []
}

function pendingReviewCount(exerciseId: string) {
  return submissionsForExercise(exerciseId).filter((submission) => !submission.reviewed_at).length
}

function releasedCount(exerciseId: string) {
  return submissionsForExercise(exerciseId).filter((submission) => submission.released_at).length
}

function phraseLabel(phraseId: string) {
  for (const module of modulesStore.modules) {
    const phrase = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === phraseId)
    if (phrase) {
      return `${phrase.japanese_text} • ${phrase.romaji}`
    }
  }
  return phraseId
}

function ensureReviewForm(submission: InstructorAssignmentSubmission) {
  if (reviewForms.value[submission.submission_id]) return

  reviewForms.value[submission.submission_id] = {
    teacher_accuracy_score: String(
      Math.round(submission.teacher_accuracy_score ?? submission.suggested_accuracy_score),
    ),
    teacher_feedback_text: submission.teacher_feedback_text ?? submission.suggested_feedback_text ?? '',
  }
}

async function loadExerciseSubmissions(exerciseId: string) {
  submissionsLoading.value = {
    ...submissionsLoading.value,
    [exerciseId]: true,
  }
  submissionErrors.value = {
    ...submissionErrors.value,
    [exerciseId]: null,
  }

  try {
    const submissions = await getExerciseSubmissions(exerciseId)
    exerciseSubmissions.value = {
      ...exerciseSubmissions.value,
      [exerciseId]: submissions,
    }
    for (const submission of submissions) {
      ensureReviewForm(submission)
    }
  } catch (errorValue: any) {
    submissionErrors.value = {
      ...submissionErrors.value,
      [exerciseId]: errorValue.response?.data?.detail ?? 'Failed to load submissions.',
    }
  } finally {
    submissionsLoading.value = {
      ...submissionsLoading.value,
      [exerciseId]: false,
    }
  }
}

async function saveReview(
  submission: InstructorAssignmentSubmission,
  releaseToStudent: boolean,
) {
  ensureReviewForm(submission)

  const reviewForm = reviewForms.value[submission.submission_id]
  reviewSaving.value = {
    ...reviewSaving.value,
    [submission.submission_id]: true,
  }

  try {
    await reviewAssignmentSubmission(submission.submission_id, {
      teacher_accuracy_score: Number(reviewForm.teacher_accuracy_score),
      teacher_feedback_text: reviewForm.teacher_feedback_text.trim(),
      release_to_student: releaseToStudent,
    })
    await loadExerciseSubmissions(submission.exercise_id)
  } catch (errorValue: any) {
    submissionErrors.value = {
      ...submissionErrors.value,
      [submission.exercise_id]: errorValue.response?.data?.detail ?? 'Failed to save review.',
    }
  } finally {
    reviewSaving.value = {
      ...reviewSaving.value,
      [submission.submission_id]: false,
    }
  }
}

async function releaseReview(submission: InstructorAssignmentSubmission) {
  reviewSaving.value = {
    ...reviewSaving.value,
    [submission.submission_id]: true,
  }

  try {
    await releaseAssignmentSubmission(submission.submission_id)
    await loadExerciseSubmissions(submission.exercise_id)
  } catch (errorValue: any) {
    submissionErrors.value = {
      ...submissionErrors.value,
      [submission.exercise_id]: errorValue.response?.data?.detail ?? 'Failed to release review.',
    }
  } finally {
    reviewSaving.value = {
      ...reviewSaving.value,
      [submission.submission_id]: false,
    }
  }
}

async function handleCreate() {
  const classId = classesStore.activeClassId
  if (!classId) {
    formError.value = 'Select a class before creating an exercise.'
    return
  }

  formError.value = null
  submitting.value = true

  try {
    const exerciseId = `ex_${Date.now()}`
    const created = await createExercise({
      exercise_id: exerciseId,
      class_id: classId,
      title: form.value.title,
      phrase_ids: form.value.phrase_ids,
      student_uids: form.value.student_uids,
      due_date: form.value.due_date || undefined,
    })

    exercises.value.unshift(created)
    showForm.value = false
    form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
    await loadExerciseSubmissions(created.exercise_id)
  } catch (errorValue: any) {
    formError.value = errorValue.response?.data?.detail ?? 'Failed to create exercise.'
  } finally {
    submitting.value = false
  }
}

async function handleDelete(exerciseId: string) {
  if (!window.confirm('Delete this exercise and all assignments?')) return

  try {
    await deleteExercise(exerciseId)
    exercises.value = exercises.value.filter((exercise) => exercise.exercise_id !== exerciseId)
  } catch {
    error.value = 'Failed to delete exercise.'
  }
}

async function loadExercises(classId: string | null) {
  exercises.value = []
  students.value = []
  error.value = null
  form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
  exerciseSubmissions.value = {}
  submissionsLoading.value = {}
  submissionErrors.value = {}
  reviewForms.value = {}

  if (!classId) {
    error.value = 'Create or select a class from Classes to manage exercises.'
    return
  }

  loading.value = true
  try {
    exercises.value = await getMyExercises(classId)
    students.value = await getAllStudents(classId)
    await Promise.all(exercises.value.map((exercise) => loadExerciseSubmissions(exercise.exercise_id)))
  } catch {
    error.value = 'Failed to load exercises.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
    await modulesStore.fetchModules()
    await Promise.all(modulesStore.modules.map((module) => modulesStore.fetchPhrases(module.module_id)))
  } catch {
    error.value = 'Failed to load your classes.'
  }

  await loadExercises(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadExercises(classId)
  },
)

watch(showForm, (open) => {
  if (open) return
  if (submitting.value) return
  formError.value = null
})
</script>

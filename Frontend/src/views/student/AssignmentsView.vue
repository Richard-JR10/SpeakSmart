<template>
  <StudentLayout title="Assignments" wide>
    <div class="flex flex-col gap-5">
      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Assigned work
            </Badge>
            <Badge variant="outline" class="rounded-full px-3 py-1">
              {{ assignments.length }} total
            </Badge>
          </div>

          <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
            <div class="flex flex-col gap-2">
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading) sm:text-4xl">
                Classroom submissions
              </CardTitle>
              <CardDescription class="max-w-3xl text-sm leading-7 text-foreground/80 sm:text-base">
                Record assigned phrases for teacher review. These submissions stay separate from your normal practice scores and progress.
              </CardDescription>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                <CardHeader class="gap-1 px-4 py-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Pending
                  </p>
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ pendingAssignments }}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                <CardHeader class="gap-1 px-4 py-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Reviewed
                  </p>
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ reviewedPhrases }}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card class="border-border/70 bg-muted/40 shadow-none py-0">
                <CardHeader class="gap-1 px-4 py-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Released
                  </p>
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ releasedPhrases }}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card v-if="loading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-56 flex-col items-center justify-center gap-4 py-10 text-center">
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

      <div v-else class="grid gap-4">
        <Card
          v-for="assignment in assignments"
          :key="assignment.exercise_id"
          class="border-border/80 bg-card/95 py-2"
        >
          <CardContent class="flex flex-col gap-4 px-4 py-4 sm:px-5">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div class="flex min-w-0 flex-col gap-3">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-lg font-semibold text-(--color-heading)">
                    {{ assignment.title }}
                  </p>
                  <Badge
                    :variant="assignment.completed_at ? 'secondary' : assignment.is_overdue ? 'destructive' : 'outline'"
                    class="rounded-full px-2.5 py-1"
                  >
                    {{ assignment.completed_at ? 'Submitted' : assignment.is_overdue ? 'Overdue' : 'Open' }}
                  </Badge>
                  <Badge
                    v-if="classNameForAssignment(assignment)"
                    variant="outline"
                    class="rounded-full px-2.5 py-1"
                  >
                    {{ classNameForAssignment(assignment) }}
                  </Badge>
                </div>

                <p class="text-sm leading-7 text-muted-foreground">
                  {{ submittedPhraseCount(assignment) }}/{{ assignment.phrases.length }} phrases submitted
                  <span v-if="assignment.due_date">
                    , due {{ formatDate(assignment.due_date) }}
                  </span>
                </p>

                <div class="h-2 max-w-xl overflow-hidden rounded-full bg-border/70">
                  <div
                    class="h-full rounded-full bg-primary transition-[width] duration-300 ease-out"
                    :style="{ width: `${assignmentCompletion(assignment)}%` }"
                  />
                </div>
              </div>

              <Button
                class="w-full lg:w-auto"
                @click="openAssignment(assignment)"
              >
                <ArrowRight data-icon="inline-start" />
                <span>{{ nextPhraseForAssignment(assignment) ? 'Open assignment' : 'Review released work' }}</span>
              </Button>
            </div>

            <Separator />

            <div class="grid gap-3">
              <div
                v-for="phraseStatus in assignment.phrases"
                :key="phraseStatus.phrase_id"
                class="rounded-2xl border border-border/70 bg-muted/30 p-4"
              >
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div class="flex min-w-0 flex-col gap-1">
                    <p class="font-semibold text-(--color-heading)">
                      {{ phraseLabel(phraseStatus.phrase_id) }}
                    </p>
                    <p class="text-sm text-muted-foreground">
                      {{ phraseSecondaryLabel(phraseStatus.phrase_id) }}
                    </p>
                  </div>

                  <Badge :variant="phraseStatusVariant(phraseStatus)" class="rounded-full px-2.5 py-1">
                    {{ phraseStatusText(phraseStatus) }}
                  </Badge>
                </div>

                <div
                  v-if="phraseStatus.released_at && phraseStatus.teacher_accuracy_score != null"
                  class="mt-4 grid gap-3 rounded-2xl border border-primary/20 bg-background/90 p-4 sm:grid-cols-[120px_minmax(0,1fr)]"
                >
                  <div>
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Released score
                    </p>
                    <p class="mt-2 font-(--font-display) text-4xl leading-none text-(--color-heading)">
                      {{ phraseStatus.teacher_accuracy_score.toFixed(0) }}%
                    </p>
                  </div>
                  <div class="flex min-w-0 flex-col gap-2">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Teacher feedback
                    </p>
                    <p class="text-sm leading-7 text-foreground/85">
                      {{ phraseStatus.teacher_feedback_text || 'Teacher review is available for this phrase.' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, ClipboardList, LoaderCircle, TriangleAlert } from 'lucide-vue-next'

import { getStudentAssignments } from '@/api/assignments'
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
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { AssignmentPhraseStatus, StudentAssignment } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const assignments = ref<StudentAssignment[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const pendingAssignments = computed(() =>
  assignments.value.filter((assignment) => !assignment.completed_at).length,
)
const reviewedPhrases = computed(() =>
  assignments.value.flatMap((assignment) => assignment.phrases)
    .filter((phrase) => phrase.reviewed_at).length,
)
const releasedPhrases = computed(() =>
  assignments.value.flatMap((assignment) => assignment.phrases)
    .filter((phrase) => phrase.released_at).length,
)

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
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function submittedPhraseCount(assignment: StudentAssignment) {
  return assignment.phrases.filter((phrase) => phrase.submitted_at).length
}

function assignmentCompletion(assignment: StudentAssignment) {
  if (!assignment.phrases.length) return 0
  return (submittedPhraseCount(assignment) / assignment.phrases.length) * 100
}

function classNameForAssignment(assignment: StudentAssignment) {
  if (!assignment.class_id) return null
  return classesStore.classes.find((item) => item.class_id === assignment.class_id)?.name ?? null
}

function nextPhraseForAssignment(assignment: StudentAssignment) {
  return assignment.phrases.find((phrase) => !phrase.submitted_at)
    ?? assignment.phrases.find((phrase) => !phrase.released_at)
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
    if (phrase) return `${phrase.romaji} · ${phrase.english_translation}`
  }
  return 'Phrase details unavailable'
}

function phraseStatusText(phrase: AssignmentPhraseStatus) {
  if (phrase.released_at) return 'Released'
  if (phrase.reviewed_at) return 'Reviewed'
  if (phrase.submitted_at) return 'Submitted'
  return 'Not started'
}

function phraseStatusVariant(phrase: AssignmentPhraseStatus): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (phrase.released_at) return 'default'
  if (phrase.reviewed_at) return 'secondary'
  if (phrase.submitted_at) return 'outline'
  return 'destructive'
}

async function openAssignment(assignment: StudentAssignment) {
  const nextPhrase = nextPhraseForAssignment(assignment)
  if (!nextPhrase) {
    return
  }

  await router.push(`/assignments/${assignment.exercise_id}/${nextPhrase.phrase_id}`)
}
</script>

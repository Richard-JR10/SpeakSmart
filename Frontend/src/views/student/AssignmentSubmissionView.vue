<template>
  <StudentLayout :title="assignment?.title ?? 'Assignment'" show-back>
    <div class="mx-auto flex w-full max-w-5xl flex-col gap-5">
      <Card v-if="loading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-72 flex-col items-center justify-center gap-4 py-12 text-center">
          <LoaderCircle class="animate-spin text-primary" />
          <div class="flex flex-col gap-1">
            <p class="font-semibold text-(--color-heading)">Loading assignment phrase</p>
            <p class="text-sm text-muted-foreground">
              Preparing the assigned prompt and submission tools.
            </p>
          </div>
        </CardContent>
      </Card>

      <template v-else-if="assignment && phrase && assignmentPhraseStatus">
        <Card class="border-border/80 bg-card/95">
          <CardContent class="flex flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex min-w-0 flex-col gap-3">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Assignment submission
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ phraseIndex + 1 }} of {{ assignment.phrases.length }}
                </Badge>
                <Badge
                  v-if="className"
                  variant="outline"
                  class="rounded-full px-3 py-1"
                >
                  {{ className }}
                </Badge>
              </div>

              <div class="flex flex-col gap-1">
                <p class="text-lg font-semibold text-(--color-heading)">
                  {{ assignment.title }}
                </p>
                <p class="text-sm leading-7 text-muted-foreground">
                  Submit this phrase for teacher review. It will not show an immediate score like normal practice.
                </p>
              </div>
            </div>

            <Badge :variant="phraseStatusVariant(assignmentPhraseStatus)" class="rounded-full px-3 py-1">
              {{ phraseStatusText(assignmentPhraseStatus) }}
            </Badge>
          </CardContent>
        </Card>

        <div class="grid gap-5 xl:grid-cols-[minmax(0,1.08fr)_minmax(340px,0.92fr)]">
          <Card class="w-full overflow-hidden border-border/80 bg-card/95">
            <CardHeader class="gap-4">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  Phrase prompt
                </Badge>
                <Badge v-if="assignment.due_date" variant="outline" class="rounded-full px-3 py-1">
                  Due {{ formatDate(assignment.due_date) }}
                </Badge>
              </div>

              <div class="flex flex-col gap-3">
                <CardTitle class="font-(--font-display) text-[clamp(2.35rem,7vw,4.5rem)] leading-none text-(--color-heading)">
                  {{ phrase.japanese_text }}
                </CardTitle>
                <CardDescription class="text-lg font-semibold text-primary">
                  {{ phrase.romaji }}
                </CardDescription>
                <p class="max-w-2xl text-sm leading-8 text-muted-foreground">
                  {{ phrase.english_translation }}
                </p>
              </div>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert v-if="assignmentPhraseStatus.released_at && assignmentPhraseStatus.teacher_accuracy_score != null">
                <ClipboardList />
                <AlertTitle>Teacher review released</AlertTitle>
                <AlertDescription>
                  {{ assignmentPhraseStatus.teacher_accuracy_score.toFixed(0) }}% ·
                  {{ assignmentPhraseStatus.teacher_feedback_text || 'Teacher feedback is available for this phrase.' }}
                </AlertDescription>
              </Alert>

              <Alert v-else-if="assignmentPhraseStatus.reviewed_at">
                <ClipboardList />
                <AlertTitle>Reviewed by teacher</AlertTitle>
                <AlertDescription>
                  This phrase has been reviewed already, but the result has not been released to your student view yet.
                </AlertDescription>
              </Alert>

              <Alert v-else-if="assignmentPhraseStatus.submitted_at">
                <ClipboardList />
                <AlertTitle>Already submitted</AlertTitle>
                <AlertDescription>
                  Your recording is already waiting for teacher review. You can keep the current submission unless your teacher asks for another take.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          <Card class="w-full border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Submission booth
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Record your assignment
              </CardTitle>
              <CardDescription>
                Submit one clear recording. The backend will score it for teacher review, but no score is shown to you immediately.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert :variant="recorder.error.value || error ? 'destructive' : 'default'">
                <TriangleAlert v-if="recorder.error.value || error" />
                <ClipboardList v-else />
                <AlertTitle>{{ submissionStateTitle }}</AlertTitle>
                <AlertDescription>
                  {{ recorder.error.value ?? error ?? successMessage ?? submissionStateCopy }}
                </AlertDescription>
              </Alert>

              <div class="flex flex-col items-center gap-5 rounded-3xl border border-dashed border-border/80 bg-muted/30 px-5 py-6 text-center">
                <Button
                  :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                  size="icon-lg"
                  class="size-24 rounded-full shadow-sm"
                  :disabled="submitting || assignmentPhraseStatus.released_at !== null"
                  @click="toggleRecording"
                >
                  <Square v-if="recorder.isRecording.value" />
                  <Mic v-else />
                  <span class="sr-only">{{ recorder.isRecording.value ? 'Stop recording' : 'Start recording' }}</span>
                </Button>

                <div class="flex flex-col gap-1">
                  <p class="text-lg font-semibold text-(--color-heading)">
                    {{ recorder.isRecording.value ? `Recording live - ${recorder.duration.value}s` : recorder.audioBlob.value ? 'Recording captured' : 'Ready to record' }}
                  </p>
                  <p class="text-sm leading-7 text-muted-foreground">
                    {{ recorderHint }}
                  </p>
                </div>

                <div class="flex h-28 w-full items-end justify-center gap-1 overflow-hidden rounded-2xl bg-secondary/50 px-4 py-4">
                  <div
                    v-for="(bar, index) in waveformBars"
                    :key="index"
                    class="w-1.5 shrink-0 rounded-full transition-[height,background] duration-75"
                    :class="recorder.isRecording.value ? 'bg-primary' : 'bg-primary/20'"
                    :style="{ height: `${bar}px` }"
                  />
                </div>
              </div>

              <template v-if="recorder.audioUrl.value">
                <Separator />
                <div class="flex flex-col gap-3">
                  <div class="flex items-center gap-2">
                    <AudioLines class="text-primary" />
                    <p class="font-semibold text-(--color-heading)">Preview before submission</p>
                  </div>
                  <audio class="w-full" :src="recorder.audioUrl.value" controls preload="metadata" />
                </div>
              </template>
            </CardContent>

            <CardFooter class="flex flex-col gap-3 border-t sm:flex-row sm:flex-wrap">
              <Button
                :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                size="lg"
                class="w-full sm:w-auto"
                :disabled="submitting || assignmentPhraseStatus.released_at !== null"
                @click="toggleRecording"
              >
                <Square v-if="recorder.isRecording.value" data-icon="inline-start" />
                <Mic v-else data-icon="inline-start" />
                <span>{{ recorder.isRecording.value ? 'Stop recording' : recorder.audioBlob.value ? 'Record again' : 'Start recording' }}</span>
              </Button>

              <Button
                variant="outline"
                size="lg"
                class="w-full sm:w-auto"
                :disabled="!recorder.audioBlob.value || submitting || recorder.isRecording.value"
                @click="clearRecording"
              >
                <RotateCcw data-icon="inline-start" />
                <span>Clear take</span>
              </Button>

              <Button
                size="lg"
                class="w-full sm:w-auto"
                :disabled="!recorder.audioBlob.value || submitting || recorder.isRecording.value || assignmentPhraseStatus.released_at !== null"
                @click="submitAssignment"
              >
                <LoaderCircle v-if="submitting" class="animate-spin" data-icon="inline-start" />
                <Send v-else data-icon="inline-start" />
                <span>{{ submitting ? 'Submitting...' : 'Submit for teacher review' }}</span>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </template>

      <Card v-else class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-72 flex-col items-center justify-center gap-4 py-12 text-center">
          <TriangleAlert class="text-destructive" />
          <div class="flex flex-col gap-2">
            <p class="font-semibold text-(--color-heading)">Assigned phrase unavailable</p>
            <p class="max-w-lg text-sm leading-7 text-muted-foreground">
              {{ error ?? 'This assigned phrase could not be loaded. Return to your assignments list and try again.' }}
            </p>
          </div>
          <Button variant="outline" @click="router.push('/assignments')">
            <ClipboardList data-icon="inline-start" />
            <span>Back to assignments</span>
          </Button>
        </CardContent>
      </Card>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AudioLines,
  ClipboardList,
  LoaderCircle,
  Mic,
  RotateCcw,
  Send,
  Square,
  TriangleAlert,
} from 'lucide-vue-next'

import { getStudentAssignments, submitAssignmentPhrase } from '@/api/assignments'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useAudioRecorder } from '@/composables/useAudioRecorder'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { AssignmentPhraseStatus, StudentAssignment } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const modulesStore = useModulesStore()
const recorder = useAudioRecorder()

const exerciseId = computed(() => String(route.params.exerciseId ?? ''))
const phraseId = computed(() => String(route.params.phraseId ?? ''))

const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const assignments = ref<StudentAssignment[]>([])
const waveformTick = ref(0)

const assignment = computed(() =>
  assignments.value.find((item) => item.exercise_id === exerciseId.value) ?? null,
)
const assignmentPhraseStatus = computed<AssignmentPhraseStatus | null>(() =>
  assignment.value?.phrases.find((item) => item.phrase_id === phraseId.value) ?? null,
)
const phrase = computed(() => {
  for (const module of modulesStore.modules) {
    const found = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === phraseId.value)
    if (found) return found
  }
  return null
})
const phraseIndex = computed(() =>
  assignment.value?.phrases.findIndex((item) => item.phrase_id === phraseId.value) ?? -1,
)
const className = computed(() => {
  if (!assignment.value?.class_id) return null
  return classesStore.classes.find((item) => item.class_id === assignment.value?.class_id)?.name ?? null
})
const waveformBars = computed(() =>
  Array.from({ length: 28 }, (_, index) => {
    if (!recorder.isRecording.value) return 10
    return Math.max(10, Math.sin(index * 0.55 + waveformTick.value * 0.6) * 18 + 30)
  }),
)
const recorderHint = computed(() => {
  if (assignmentPhraseStatus.value?.released_at) {
    return 'This phrase has already been released with teacher feedback, so new submissions are locked.'
  }
  if (recorder.isRecording.value) {
    return 'Speak clearly, then stop the recording when you finish the assigned phrase.'
  }
  if (recorder.audioBlob.value) {
    return 'Preview the take below, then submit it for teacher review.'
  }
  return 'This submission stays separate from normal practice scoring and will wait for teacher review.'
})
const submissionStateTitle = computed(() => {
  if (error.value || recorder.error.value) return 'Submission problem'
  if (successMessage.value) return 'Submission sent'
  if (submitting.value) return 'Submitting recording'
  if (assignmentPhraseStatus.value?.released_at) return 'Teacher review released'
  if (assignmentPhraseStatus.value?.reviewed_at) return 'Reviewed by teacher'
  if (assignmentPhraseStatus.value?.submitted_at) return 'Waiting for teacher review'
  return 'Submission ready'
})
const submissionStateCopy = computed(() => {
  if (submitting.value) {
    return 'Your assignment recording is being uploaded and prepared for teacher review.'
  }
  if (assignmentPhraseStatus.value?.released_at) {
    return 'Teacher feedback has been released and is shown on this page.'
  }
  if (assignmentPhraseStatus.value?.reviewed_at) {
    return 'Your teacher reviewed this phrase already, but the result is not yet released to your student view.'
  }
  if (assignmentPhraseStatus.value?.submitted_at) {
    return 'This phrase is already submitted and waiting for review.'
  }
  return 'Submit one clear recording. No immediate score will appear here.'
})

let waveformInterval: ReturnType<typeof setInterval> | null = null

watch(
  () => recorder.isRecording.value,
  (recording) => {
    if (recording) {
      waveformInterval = setInterval(() => {
        waveformTick.value += 1
      }, 70)
      return
    }

    if (waveformInterval) {
      clearInterval(waveformInterval)
      waveformInterval = null
    }
  },
)

watch(
  () => route.fullPath,
  async () => {
    await loadAssignmentPage()
  },
)

onMounted(async () => {
  await loadAssignmentPage()
})

onBeforeUnmount(() => {
  if (waveformInterval) {
    clearInterval(waveformInterval)
  }
  if (recorder.isRecording.value) {
    recorder.stopRecording()
  }
  recorder.clearRecording()
})

async function loadAssignmentPage() {
  const uid = authStore.uid
  if (!uid) return

  loading.value = true
  error.value = null
  successMessage.value = null
  recorder.clearRecording()

  try {
    await Promise.all([
      classesStore.ensureLoaded(),
      modulesStore.fetchModules(),
    ])
    await Promise.all(modulesStore.modules.map((module) => modulesStore.fetchPhrases(module.module_id)))
    assignments.value = await getStudentAssignments(uid)

    if (!assignment.value || !assignmentPhraseStatus.value || !phrase.value) {
      error.value = 'The assigned phrase could not be found.'
    }
  } catch (err) {
    console.error('Failed to load assignment submission page:', err)
    error.value = 'We could not load this assignment right now.'
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function phraseStatusText(status: AssignmentPhraseStatus) {
  if (status.released_at) return 'Released'
  if (status.reviewed_at) return 'Reviewed'
  if (status.submitted_at) return 'Submitted'
  return 'Not started'
}

function phraseStatusVariant(status: AssignmentPhraseStatus): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (status.released_at) return 'default'
  if (status.reviewed_at) return 'secondary'
  if (status.submitted_at) return 'outline'
  return 'destructive'
}

async function toggleRecording() {
  if (assignmentPhraseStatus.value?.released_at) return

  if (recorder.isRecording.value) {
    recorder.stopRecording()
    return
  }

  successMessage.value = null
  error.value = null
  recorder.clearRecording()
  await recorder.startRecording()
}

function clearRecording() {
  recorder.clearRecording()
  successMessage.value = null
}

async function submitAssignment() {
  if (!assignment.value || !recorder.audioBlob.value || !phrase.value) return

  submitting.value = true
  error.value = null
  successMessage.value = null

  try {
    await submitAssignmentPhrase(
      assignment.value.exercise_id,
      phrase.value.phrase_id,
      recorder.audioBlob.value,
    )
    recorder.clearRecording()
    successMessage.value = 'Your assignment recording was submitted for teacher review.'
    assignments.value = await getStudentAssignments(authStore.uid!)
  } catch (err: any) {
    error.value = err.response?.data?.detail ?? 'Failed to submit this assignment phrase.'
  } finally {
    submitting.value = false
  }
}
</script>

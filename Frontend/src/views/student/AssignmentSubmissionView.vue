<template>
  <StudentLayout :title="assignment?.title ?? 'Assignment'" show-back wide>
    <div class="mx-auto flex w-full max-w-7xl flex-col gap-3">
      <Card v-if="loading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-72 flex-col items-center justify-center gap-4 py-12 text-center">
          <LoaderCircle class="animate-spin text-primary" />
          <div class="flex flex-col gap-1">
            <p class="font-semibold text-(--color-heading)">Loading assignment</p>
            <p class="text-sm text-muted-foreground">
              Preparing the assigned phrase set and recording tools.
            </p>
          </div>
        </CardContent>
      </Card>

      <template v-else-if="assignment && phrase && assignmentPhraseStatus">
        <Card class="overflow-hidden border-border/80 bg-card/95 shadow-sm">
          <CardContent class="p-0">
            <div class="grid gap-3 border-b border-border/70 px-4 py-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
              <div class="flex min-w-0 flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.16em]">
                  Assignment submission
                </Badge>
                <Badge variant="outline" class="rounded-full px-2.5 py-1 text-xs">
                  {{ phraseIndex + 1 }} of {{ requiredPhraseIds.length }}
                </Badge>
                <Badge variant="outline" class="rounded-full px-2.5 py-1 text-xs">
                  {{ completionCount }}/{{ requiredPhraseIds.length }} ready
                </Badge>
                <span class="hidden h-4 w-px bg-border sm:block" aria-hidden="true" />
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-(--color-heading)">
                    {{ assignment.title }}
                  </p>
                  <p class="truncate text-xs text-muted-foreground">
                    {{ className ?? 'Classroom assignment' }}
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-2 lg:justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  class="h-9 rounded-xl px-3"
                  :disabled="phraseIndex <= 0 || submitting || recorder.isRecording.value"
                  @click="goToAssignmentPhrase(phraseIndex - 1)"
                >
                  <ChevronLeft data-icon="inline-start" />
                  <span>Previous</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  class="h-9 rounded-xl px-3"
                  :disabled="phraseIndex >= requiredPhraseIds.length - 1 || submitting || recorder.isRecording.value"
                  @click="goToAssignmentPhrase(phraseIndex + 1)"
                >
                  <span>Next</span>
                  <ChevronRight data-icon="inline-end" />
                </Button>
              </div>
            </div>

            <div class="relative">
            <div class="grid gap-0 lg:grid-cols-[minmax(0,1fr)_minmax(380px,0.78fr)]">
              <section class="flex min-w-0 flex-col gap-4 px-4 py-4 lg:min-h-[520px] lg:px-5 lg:py-5">
                <div class="flex min-w-0 flex-wrap items-center gap-2">
                  <Badge :variant="phraseStatusVariant(assignmentPhraseStatus)" class="rounded-full px-2.5 py-1 text-xs">
                    {{ phraseStatusText(assignmentPhraseStatus) }}
                  </Badge>
                  <Badge variant="outline" class="rounded-full px-2.5 py-1 text-xs">
                    Prompt
                  </Badge>
                  <Badge v-if="assignment.due_date" variant="outline" class="rounded-full px-2.5 py-1 text-xs">
                    Due {{ formatDate(assignment.due_date) }}
                  </Badge>
                </div>

                <div class="flex flex-1 flex-col justify-between gap-4">
                  <div class="flex min-h-[300px] min-w-0 flex-col justify-center gap-4 rounded-2xl bg-muted/20 px-3 py-5 sm:px-5 lg:min-h-[360px]">
                    <h2 class="font-(--font-display) text-[clamp(2.65rem,7vw,5.25rem)] leading-none text-(--color-heading)">
                      {{ phrase.japanese_text }}
                    </h2>
                    <div class="flex flex-col gap-1 border-l-2 border-primary/30 pl-4">
                      <p class="text-[clamp(1.5rem,3vw,2.5rem)] font-semibold leading-tight text-primary">
                        {{ phrase.romaji }}
                      </p>
                      <p class="max-w-2xl text-base leading-6 text-muted-foreground">
                        {{ phrase.english_translation }}
                      </p>
                    </div>
                  </div>

                  <div class="grid gap-2 rounded-2xl border border-border/70 bg-muted/25 p-3">
                    <div class="grid gap-2 text-sm sm:grid-cols-2">
                      <div class="min-w-0">
                        <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                          Assignment
                        </p>
                        <p class="truncate font-semibold text-(--color-heading)">
                          {{ completionCount }}/{{ requiredPhraseIds.length }} phrases ready
                        </p>
                      </div>

                      <div class="min-w-0">
                        <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                          Recording
                        </p>
                        <p class="truncate font-semibold text-(--color-heading)">
                          {{ currentRecordingLabel }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <Alert v-if="allRequiredWorkComplete">
                    <ClipboardList />
                    <AlertTitle>Assignment already submitted</AlertTitle>
                    <AlertDescription>
                      Every phrase has been submitted and is waiting for teacher review or feedback release.
                    </AlertDescription>
                  </Alert>
                </div>
              </section>

              <section class="flex min-w-0 flex-col border-t border-border/70 bg-muted/20 lg:border-l lg:border-t-0">
                <div class="flex flex-col gap-3 px-4 py-4 lg:px-5 lg:py-5">
                  <div class="flex items-center gap-1.5">
                    <template v-for="(step, i) in ['Record', 'Review', 'Submit']" :key="step">
                      <div class="flex items-center gap-1.5">
                        <span
                          :class="[
                            'flex size-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold transition-colors',
                            assignmentStep >= i + 1
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-secondary text-muted-foreground',
                          ]"
                        >{{ i + 1 }}</span>
                        <span
                          :class="[
                            'text-xs font-semibold transition-colors',
                            assignmentStep === i + 1 ? 'text-(--color-heading)' : 'text-muted-foreground',
                          ]"
                        >{{ step }}</span>
                      </div>
                      <span v-if="i < 2" class="h-px w-4 shrink-0 bg-border" aria-hidden="true" />
                    </template>
                  </div>
                  <div class="flex flex-col gap-1">
                    <h3 class="font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                      Record all assigned phrases
                    </h3>
                    <p class="text-sm leading-6 text-muted-foreground">
                      Capture each missing phrase, move through the set, then submit everything for teacher review.
                    </p>
                  </div>
                </div>

                <div class="flex flex-1 flex-col gap-3 px-4 pb-4 lg:px-5">
                  <Alert :variant="recorder.error.value || error || recorder.hasSpeech.value === false ? 'destructive' : 'default'">
                    <TriangleAlert v-if="recorder.error.value || error || recorder.hasSpeech.value === false" />
                    <Mic v-else />
                    <AlertTitle>{{ submissionStateTitle }}</AlertTitle>
                    <AlertDescription>
                      {{ recorder.error.value ?? (recorder.hasSpeech.value === false ? 'No speech detected in this recording. Please record again so your teacher can score it.' : null) ?? error ?? successMessage ?? submissionStateCopy }}
                    </AlertDescription>
                  </Alert>

                  <div
                    :class="[
                      'flex flex-col items-center gap-3 rounded-2xl border px-4 py-5 text-center transition-colors duration-300',
                      currentPhraseLocked
                        ? 'border-primary/20 bg-primary/5'
                        : currentHasRecording && !recorder.isRecording.value
                          ? 'border-emerald-500/30 bg-emerald-500/5'
                          : 'border-dashed border-border/80 bg-card/80',
                    ]"
                  >
                    <Button
                      :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                      size="icon-lg"
                      class="size-16 rounded-full shadow-sm transition-transform duration-200 hover:scale-105"
                      :disabled="recordingDisabled"
                      @click="toggleRecording"
                    >
                      <Square v-if="recorder.isRecording.value" />
                      <Mic v-else />
                      <span class="sr-only">{{ recorder.isRecording.value ? 'Stop recording' : 'Start recording' }}</span>
                    </Button>

                    <div class="flex flex-col gap-1">
                      <p class="text-base font-semibold text-(--color-heading)" :class="{ 'text-destructive': recorder.isRecording.value && timeRemaining <= 3 }">
                        {{ recordingStatusLabel }}
                      </p>
                      <p class="text-xs leading-5 text-muted-foreground">
                        {{ recorderHint }}
                      </p>
                    </div>

                    <div class="flex h-14 w-full items-end justify-center gap-1 overflow-hidden rounded-xl bg-secondary/50 px-3 py-3">
                      <div
                        v-for="(bar, index) in waveformBars"
                        :key="index"
                        class="w-1.5 shrink-0 rounded-full transition-[height,background] duration-75"
                        :class="recorder.isRecording.value ? 'bg-primary' : 'bg-primary/20'"
                        :style="{ height: `${bar}px` }"
                      />
                    </div>
                  </div>

                  <template v-if="currentPreviewUrl">
                    <Separator />
                    <div class="flex flex-col gap-2">
                      <div class="flex items-center gap-2">
                        <AudioLines class="size-4 text-primary" />
                        <p class="text-sm font-semibold text-(--color-heading)">Preview saved take</p>
                      </div>
                      <audio
                        class="w-full"
                        :src="currentPreviewUrl"
                        controls
                        preload="metadata"
                      />
                    </div>
                  </template>

                  <div class="grid gap-2 rounded-2xl border border-border/70 bg-background/70 p-3">
                    <div class="flex items-center justify-between gap-3 text-xs">
                      <span class="font-medium text-muted-foreground">Ready to submit</span>
                      <span class="font-semibold tabular-nums text-(--color-heading)">
                        {{ completionCount }}/{{ requiredPhraseIds.length }}
                      </span>
                    </div>
                    <div class="h-2 overflow-hidden rounded-full bg-border/70">
                      <div
                        class="h-full rounded-full transition-colors duration-300"
                        :class="missingPhraseIds.length ? 'bg-amber-500' : 'bg-emerald-600'"
                        :style="{ width: `${assignmentCompletion}%` }"
                      />
                    </div>
                  </div>

                  <Alert v-if="!allRequiredWorkComplete && missingPhraseIds.length > 0" variant="destructive">
                    <TriangleAlert />
                    <AlertTitle>Record all phrases before submitting</AlertTitle>
                    <AlertDescription>
                      Phrase{{ missingPhraseNumbers.length === 1 ? '' : 's' }}
                      {{ missingPhraseNumbers.join(', ') }}
                      still need{{ missingPhraseNumbers.length === 1 ? 's' : '' }} a recording.
                      Navigate to each and tap Record.
                    </AlertDescription>
                  </Alert>

                  <Alert v-else-if="!allRequiredWorkComplete && recordedPhraseIds.length > 0 && missingPhraseIds.length === 0">
                    <CircleCheck class="text-emerald-600" />
                    <AlertTitle>All phrases recorded</AlertTitle>
                    <AlertDescription>
                      Ready to submit — click "Submit assignment" when you're ready.
                    </AlertDescription>
                  </Alert>
                </div>

                <div class="mt-auto flex flex-col gap-2 border-t border-border/70 bg-card/70 px-4 py-3 sm:flex-row sm:flex-wrap lg:px-5">
                  <Button
                    :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                    size="sm"
                    class="w-full rounded-xl sm:w-auto"
                    :disabled="recordingDisabled"
                    @click="toggleRecording"
                  >
                    <Square v-if="recorder.isRecording.value" data-icon="inline-start" />
                    <Mic v-else data-icon="inline-start" />
                    <span>{{ recordButtonLabel }}</span>
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    class="w-full rounded-xl sm:w-auto"
                    :disabled="!currentHasRecording || submitting || recorder.isRecording.value || currentPhraseLocked"
                    @click="clearRecording"
                  >
                    <RotateCcw data-icon="inline-start" />
                    <span>Clear take</span>
                  </Button>

                  <span
                    class="w-full sm:w-auto"
                    :title="!canFinalSubmit && missingPhraseIds.length
                      ? `${missingPhraseIds.length} phrase${missingPhraseIds.length === 1 ? '' : 's'} still need a recording`
                      : undefined"
                  >
                    <Button
                      size="sm"
                      class="w-full rounded-xl sm:w-auto"
                      :disabled="!canFinalSubmit"
                      @click="openSubmitConfirm"
                    >
                      <Send data-icon="inline-start" />
                      <span>Submit assignment</span>
                    </Button>
                  </span>
                </div>
              </section>
            </div>

            <Transition
              enter-active-class="transition-opacity duration-200"
              enter-from-class="opacity-0"
              leave-active-class="transition-opacity duration-200"
              leave-to-class="opacity-0"
            >
              <div
                v-if="submitting"
                class="absolute inset-0 z-10 flex flex-col items-center justify-center gap-5 rounded-b-[inherit] bg-background/90 backdrop-blur-sm"
              >
                <div class="relative flex items-center justify-center">
                  <span class="absolute size-20 animate-ping rounded-full bg-primary/15" />
                  <span class="flex size-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <LoaderCircle class="size-7 animate-spin" />
                  </span>
                </div>
                <div class="flex flex-col items-center gap-1 text-center">
                  <p class="font-(--font-display) text-xl font-semibold text-(--color-heading)">
                    Submitting your assignment
                  </p>
                  <p class="text-sm text-muted-foreground">{{ submitProgressLabel }} — please wait.</p>
                </div>
                <div class="h-2 w-52 overflow-hidden rounded-full bg-border/70">
                  <div
                    class="h-full rounded-full bg-primary transition-[width] duration-300"
                    :style="{ width: `${submitProgressTotal ? (submitProgressCurrent / submitProgressTotal) * 100 : 0}%` }"
                  />
                </div>
                <p class="text-xs text-muted-foreground">Do not close this page.</p>
              </div>
            </Transition>
            </div>
          </CardContent>
        </Card>
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

    <DialogRoot :open="submitConfirmOpen" @update:open="handleSubmitConfirmOpenChange">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/45 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent class="fixed top-1/2 left-1/2 z-50 grid max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-5 overflow-y-auto rounded-2xl border border-border bg-background p-5 shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 sm:p-6">
          <div class="flex flex-col gap-2">
            <DialogTitle class="font-(--font-display) text-2xl leading-tight text-(--color-heading)">
              Submit assignment?
            </DialogTitle>
            <DialogDescription class="text-sm leading-6 text-muted-foreground">
              All {{ requiredPhraseIds.length }} phrase{{ requiredPhraseIds.length === 1 ? '' : 's' }} are recorded and will be uploaded for teacher review. This action cannot be undone.
            </DialogDescription>
          </div>

          <div class="grid gap-2 rounded-2xl border border-border/70 bg-muted/20 p-4 text-sm">
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">Total phrases</span>
              <span class="font-semibold tabular-nums text-(--color-heading)">{{ requiredPhraseIds.length }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">Already submitted</span>
              <span class="font-semibold tabular-nums text-(--color-heading)">{{ completedPhraseIds.length }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">New recordings</span>
              <span class="font-semibold tabular-nums text-(--color-heading)">{{ recordedPhraseIds.length }}</span>
            </div>
          </div>

          <Alert v-if="submitting">
            <LoaderCircle class="animate-spin" />
            <AlertTitle>{{ submissionStateTitle }}</AlertTitle>
            <AlertDescription>{{ submissionStateCopy }}</AlertDescription>
          </Alert>

          <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <DialogClose as-child>
              <Button variant="outline" class="w-full sm:w-auto" :disabled="submitting">
                Cancel
              </Button>
            </DialogClose>
            <Button class="w-full sm:w-auto" :disabled="submitting" @click="submitRecordedAssignment">
              <LoaderCircle v-if="submitting" class="animate-spin" data-icon="inline-start" />
              <Send v-else data-icon="inline-start" />
              <span>{{ submitting ? submitProgressLabel : 'Submit finally' }}</span>
            </Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
  AudioLines,
  ChevronLeft,
  ChevronRight,
  CircleCheck,
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
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useAudioRecorder, MAX_RECORDING_SECONDS } from '@/composables/useAudioRecorder'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { AssignmentPhraseStatus, Phrase, StudentAssignment } from '@/types'

type RecordedTake = {
  blob: Blob
  audioUrl: string
  duration: number
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const classesStore = useClassesStore()
const modulesStore = useModulesStore()
const recorder = useAudioRecorder()

const exerciseId = computed(() => String(route.params.exerciseId ?? ''))
const phraseId = computed(() => String(route.params.phraseId ?? ''))

const loading = shallowRef(false)
const submitting = shallowRef(false)
const submitConfirmOpen = shallowRef(false)
const error = shallowRef<string | null>(null)
const successMessage = shallowRef<string | null>(null)
const assignments = ref<StudentAssignment[]>([])
const recordedTakes = ref<Record<string, RecordedTake>>({})
const waveformTick = shallowRef(0)
const submitProgressCurrent = shallowRef(0)
const submitProgressTotal = shallowRef(0)

const assignment = computed(() =>
  assignments.value.find((item) => item.exercise_id === exerciseId.value) ?? null,
)
const requiredPhraseIds = computed(() => assignment.value?.phrases.map((item) => item.phrase_id) ?? [])
const assignmentPhraseStatus = computed<AssignmentPhraseStatus | null>(() =>
  assignment.value?.phrases.find((item) => item.phrase_id === phraseId.value) ?? null,
)
const phrase = computed<Phrase | null>(() => phraseById(phraseId.value))
const phraseIndex = computed(() => requiredPhraseIds.value.findIndex((item) => item === phraseId.value))
const className = computed(() => {
  if (!assignment.value?.class_id) return null
  return classesStore.classes.find((item) => item.class_id === assignment.value?.class_id)?.name ?? null
})
const completedPhraseIds = computed(() =>
  assignment.value?.phrases
    .filter((item) => item.submitted_at || item.reviewed_at || item.released_at)
    .map((item) => item.phrase_id) ?? [],
)
const recordedPhraseIds = computed(() =>
  requiredPhraseIds.value.filter((id) => recordedTakes.value[id] && !completedPhraseIds.value.includes(id)),
)
const missingPhraseIds = computed(() =>
  requiredPhraseIds.value.filter((id) =>
    !completedPhraseIds.value.includes(id) && !recordedTakes.value[id],
  ),
)
const missingPhraseNumbers = computed(() =>
  missingPhraseIds.value.map((id) => requiredPhraseIds.value.indexOf(id) + 1),
)
const completionCount = computed(() => completedPhraseIds.value.length + recordedPhraseIds.value.length)
const assignmentCompletion = computed(() => {
  if (!requiredPhraseIds.value.length) return 0
  return (completionCount.value / requiredPhraseIds.value.length) * 100
})
const allRequiredWorkComplete = computed(() =>
  requiredPhraseIds.value.length > 0 && completedPhraseIds.value.length === requiredPhraseIds.value.length,
)
const currentRecordedTake = computed(() => recordedTakes.value[phraseId.value] ?? null)
const currentPreviewUrl = computed(() => recorder.audioUrl.value ?? currentRecordedTake.value?.audioUrl ?? null)
const currentHasRecording = computed(() => Boolean(recorder.audioBlob.value || currentRecordedTake.value))
const currentPhraseLocked = computed(() =>
  Boolean(assignmentPhraseStatus.value?.submitted_at || assignmentPhraseStatus.value?.reviewed_at || assignmentPhraseStatus.value?.released_at),
)
const recordingDisabled = computed(() =>
  submitting.value || currentPhraseLocked.value,
)
const canFinalSubmit = computed(() =>
  recordedPhraseIds.value.length > 0 &&
  missingPhraseIds.value.length === 0 &&
  !recorder.isRecording.value &&
  !submitting.value,
)
const waveformBars = computed(() =>
  Array.from({ length: 28 }, (_, index) => {
    if (!recorder.isRecording.value) return 10
    return Math.max(10, Math.sin(index * 0.55 + waveformTick.value * 0.6) * 18 + 30)
  }),
)
const currentRecordingLabel = computed(() => {
  if (currentPhraseLocked.value) return 'Already submitted'
  if (recorder.isRecording.value) return 'Recording live'
  if (currentHasRecording.value) return 'Saved locally'
  return 'Waiting'
})
const timeRemaining = computed(() => MAX_RECORDING_SECONDS - recorder.duration.value)

const assignmentStep = computed(() => {
  if (missingPhraseIds.value.length === 0 && recordedPhraseIds.value.length > 0) return 3
  if (currentHasRecording.value || currentPhraseLocked.value || recorder.isRecording.value) return 2
  return 1
})
const recordingStatusLabel = computed(() => {
  if (recorder.isRecording.value) {
    return timeRemaining.value <= 3
      ? `Recording — ${timeRemaining.value}s left`
      : `Recording — ${recorder.duration.value}s / ${MAX_RECORDING_SECONDS}s`
  }
  if (recorder.stoppedAtLimit.value) return 'Recording saved — limit reached'
  if (currentHasRecording.value) return 'Recording saved for final submit'
  if (currentPhraseLocked.value) return 'Phrase already submitted'
  return 'Ready to record'
})
const recordButtonLabel = computed(() => {
  if (recorder.isRecording.value) return 'Stop recording'
  if (currentHasRecording.value) return 'Record again'
  return 'Start recording'
})
const recorderHint = computed(() => {
  if (currentPhraseLocked.value) {
    return 'This phrase already has a submitted recording and counts toward this assignment.'
  }
  if (recorder.isRecording.value) {
    return `Speak clearly. Recording stops automatically at ${MAX_RECORDING_SECONDS}s.`
  }
  if (recorder.stoppedAtLimit.value) {
    return `Recording reached the ${MAX_RECORDING_SECONDS}s limit and was saved automatically. Record again if you need another take.`
  }
  if (currentHasRecording.value) {
    return 'Preview the take below, move to the next phrase, or record again before final submission.'
  }
  return 'Record this phrase before final assignment submission.'
})
const submissionStateTitle = computed(() => {
  if (error.value || recorder.error.value) return 'Submission problem'
  if (recorder.hasSpeech.value === false) return 'No speech detected'
  if (successMessage.value) return 'Submission sent'
  if (submitting.value) return submitProgressLabel.value
  if (allRequiredWorkComplete.value) return 'Assignment complete'
  if (currentPhraseLocked.value) return phraseStatusText(assignmentPhraseStatus.value!)
  if (currentHasRecording.value) return 'Recording saved'
  return 'Microphone ready'
})
const submissionStateCopy = computed(() => {
  if (submitting.value) {
    return 'Your saved phrase recordings are being uploaded for teacher review.'
  }
  if (allRequiredWorkComplete.value) {
    return 'All assigned phrases are already submitted and waiting for teacher review or feedback release.'
  }
  if (currentPhraseLocked.value) {
    return 'Move to another phrase that still needs a recording, or return to assignments.'
  }
  if (missingPhraseIds.value.length) {
    return `${missingPhraseIds.value.length} phrase${missingPhraseIds.value.length === 1 ? '' : 's'} still need a recording before final submission.`
  }
  if (currentHasRecording.value) {
    return 'All missing phrases are recorded. Submit the assignment when you are ready.'
  }
  return 'Start recording when you are ready.'
})
const submitProgressLabel = computed(() => {
  if (!submitProgressTotal.value) return 'Submitting...'
  return `Submitting ${submitProgressCurrent.value} of ${submitProgressTotal.value}`
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
  () => recorder.audioBlob.value,
  (blob) => {
    if (blob && !currentPhraseLocked.value) {
      saveCurrentRecording(blob)
    }
  },
)

watch(exerciseId, async () => {
  await loadAssignmentPage()
})

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
  clearRecordedTakes()
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

function phraseById(targetPhraseId: string) {
  for (const module of modulesStore.modules) {
    const found = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === targetPhraseId)
    if (found) return found
  }
  return null
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
  if (recordingDisabled.value) return

  if (recorder.isRecording.value) {
    recorder.stopRecording()
    return
  }

  successMessage.value = null
  error.value = null
  recorder.clearRecording()
  await recorder.startRecording()
}

function saveCurrentRecording(blob: Blob) {
  const targetPhraseId = phraseId.value
  if (!targetPhraseId) return

  revokeRecordedTake(targetPhraseId)
  recordedTakes.value = {
    ...recordedTakes.value,
    [targetPhraseId]: {
      blob,
      audioUrl: URL.createObjectURL(blob),
      duration: recorder.duration.value,
    },
  }
}

function revokeRecordedTake(targetPhraseId: string) {
  const existing = recordedTakes.value[targetPhraseId]
  if (existing) {
    URL.revokeObjectURL(existing.audioUrl)
  }
}

function clearRecordedTakes() {
  Object.values(recordedTakes.value).forEach((take) => {
    URL.revokeObjectURL(take.audioUrl)
  })
  recordedTakes.value = {}
}

function clearRecording() {
  revokeRecordedTake(phraseId.value)
  const nextTakes = { ...recordedTakes.value }
  delete nextTakes[phraseId.value]
  recordedTakes.value = nextTakes
  recorder.clearRecording()
  successMessage.value = null
}

async function goToAssignmentPhrase(index: number) {
  const targetPhraseId = requiredPhraseIds.value[index]
  if (!targetPhraseId || recorder.isRecording.value || submitting.value) return

  recorder.clearRecording()
  await router.push(`/assignments/${exerciseId.value}/${targetPhraseId}`)
}

function openSubmitConfirm() {
  if (!canFinalSubmit.value) return
  submitConfirmOpen.value = true
}

function handleSubmitConfirmOpenChange(open: boolean) {
  if (!open && submitting.value) return
  submitConfirmOpen.value = open
}

async function submitRecordedAssignment() {
  if (!assignment.value || !canFinalSubmit.value) return

  const pendingPhraseIds = recordedPhraseIds.value
  submitting.value = true
  error.value = null
  successMessage.value = null
  submitProgressCurrent.value = 0
  submitProgressTotal.value = pendingPhraseIds.length

  try {
    for (const [index, targetPhraseId] of pendingPhraseIds.entries()) {
      const take = recordedTakes.value[targetPhraseId]
      if (!take) continue

      submitProgressCurrent.value = index + 1
      await submitAssignmentPhrase(assignment.value.exercise_id, targetPhraseId, take.blob)
      revokeRecordedTake(targetPhraseId)
      const nextTakes = { ...recordedTakes.value }
      delete nextTakes[targetPhraseId]
      recordedTakes.value = nextTakes
    }

    recorder.clearRecording()
    assignments.value = await getStudentAssignments(authStore.uid!)
    successMessage.value = 'Your assignment recordings were submitted for teacher review.'
    submitConfirmOpen.value = false
    await router.push('/assignments')
  } catch (err: any) {
    error.value = err?.rateLimited
      ? (err.rateLimitMessage ?? 'Too many submissions. Please wait before trying again.')
      : (err.response?.data?.detail ?? 'Failed to submit one of the recorded assignment phrases.')
  } finally {
    submitting.value = false
    submitProgressCurrent.value = 0
    submitProgressTotal.value = 0
  }
}
</script>

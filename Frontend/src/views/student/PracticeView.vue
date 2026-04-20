<template>
  <StudentLayout :title="module?.title ?? 'Practice'" show-back>
    <div class="mx-auto flex w-full max-w-5xl flex-col gap-5">
      <Card v-if="loading" class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-72 flex-col items-center justify-center gap-4 py-12 text-center">
          <LoaderCircle class="animate-spin text-primary" />
          <div class="flex flex-col gap-1">
            <p class="font-semibold text-(--color-heading)">Loading phrase</p>
            <p class="text-sm text-muted-foreground">
              Preparing the practice prompt and recording tools.
            </p>
          </div>
        </CardContent>
      </Card>

      <template v-else-if="phrase">
        <Card class="border-border/80 bg-card/95">
          <CardContent class="flex flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex min-w-0 flex-col gap-3">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Practice session
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ phraseIndex + 1 }} of {{ phrases.length }}
                </Badge>
              </div>

              <div class="flex flex-col gap-1">
                <p class="text-lg font-semibold text-(--color-heading)">
                  {{ module?.title ?? 'Module' }}
                </p>
                <p class="text-sm leading-7 text-muted-foreground">
                  Move phrase by phrase and keep your recording focused on one prompt at a time.
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2 self-start sm:self-auto">
              <Button
                variant="outline"
                size="icon"
                :disabled="phraseIndex <= 0 || attemptsStore.submitting"
                @click="goToPhrase(phraseIndex - 1)"
              >
                <ChevronLeft />
                <span class="sr-only">Previous phrase</span>
              </Button>
              <Button
                variant="outline"
                size="icon"
                :disabled="phraseIndex >= phrases.length - 1 || attemptsStore.submitting"
                @click="goToPhrase(phraseIndex + 1)"
              >
                <ChevronRight />
                <span class="sr-only">Next phrase</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        <div class="grid w-full grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.08fr)_minmax(340px,0.92fr)]">
          <Card class="w-full overflow-hidden border-border/80 bg-card/95">
            <CardHeader class="gap-4 ">
              <div class="flex flex-wrap items-center gap-2">
                <Badge :variant="difficultyBadgeVariant" class="rounded-full px-3 py-1">
                  {{ difficultyLabel }}
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  Prompt
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
              <div class="grid gap-3 sm:grid-cols-3">
                <Card class="gap-0 border-border/70 bg-muted/40 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      Reference
                    </p>
                    <CardTitle class="text-base text-(--color-heading)">
                      {{ phrase.reference_audio_url ? 'Available' : 'Unavailable' }}
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="gap-0 border-border/70 bg-muted/40 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      Module
                    </p>
                    <CardTitle class="text-base text-(--color-heading)">
                      {{ module?.title ?? 'Current lesson' }}
                    </CardTitle>
                  </CardHeader>
                </Card>

                <Card class="gap-0 border-border/70 bg-muted/40 shadow-none">
                  <CardHeader class="gap-2">
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      Recording
                    </p>
                    <CardTitle class="text-base text-(--color-heading)">
                      {{ recorder.audioBlob.value ? 'Ready to submit' : recorder.isRecording.value ? 'Recording live' : 'Waiting' }}
                    </CardTitle>
                  </CardHeader>
                </Card>
              </div>

              <Alert v-if="!phrase.reference_audio_url">
                <CircleAlert />
                <AlertTitle>Reference audio unavailable</AlertTitle>
                <AlertDescription>
                  You can still record this phrase, but there is no model audio attached to it yet.
                </AlertDescription>
              </Alert>
            </CardContent>

            <CardFooter class="border-t">
              <Button
                variant="outline"
                size="lg"
                class="w-full sm:w-auto"
                :disabled="!phrase.reference_audio_url || playingReference || recorder.isRecording.value || attemptsStore.submitting"
                @click="playReference"
              >
                <LoaderCircle v-if="playingReference" class="animate-spin" data-icon="inline-start" />
                <Volume2 v-else data-icon="inline-start" />
                <span>{{ playingReference ? 'Playing reference...' : 'Play reference audio' }}</span>
              </Button>
            </CardFooter>
          </Card>

          <Card class="w-full border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Recording booth
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Record your response
              </CardTitle>
              <CardDescription>
                Listen first if needed, then record one clear attempt before sending it for scoring.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-5">
              <Alert :variant="recorder.error.value || attemptsStore.error ? 'destructive' : 'default'">
                <TriangleAlert v-if="recorder.error.value || attemptsStore.error" />
                <Mic v-else />
                <AlertTitle>{{ recordingStateTitle }}</AlertTitle>
                <AlertDescription>
                  {{ recorder.error.value ?? attemptsStore.error ?? recordingStateCopy }}
                </AlertDescription>
              </Alert>

              <div class="flex flex-col items-center gap-5 rounded-3xl border border-dashed border-border/80 bg-muted/30 px-5 py-6 text-center">
                <Button
                  :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                  size="icon-lg"
                  class="size-24 rounded-full shadow-sm"
                  :disabled="attemptsStore.submitting"
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
                    v-for="(bar, i) in waveformBars"
                    :key="i"
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
                  <audio
                    class="w-full"
                    :src="recorder.audioUrl.value"
                    controls
                    preload="metadata"
                  />
                </div>
              </template>
            </CardContent>

            <CardFooter class="flex flex-col gap-3 border-t sm:flex-row sm:flex-wrap">
              <Button
                :variant="recorder.isRecording.value ? 'destructive' : 'default'"
                size="lg"
                class="w-full sm:w-auto"
                :disabled="attemptsStore.submitting"
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
                :disabled="!recorder.audioBlob.value || attemptsStore.submitting || recorder.isRecording.value"
                @click="clearRecording"
              >
                <RotateCcw data-icon="inline-start" />
                <span>Clear take</span>
              </Button>

              <Button
                size="lg"
                class="w-full sm:w-auto"
                :disabled="!recorder.audioBlob.value || attemptsStore.submitting || recorder.isRecording.value"
                @click="submitAttempt"
              >
                <LoaderCircle v-if="attemptsStore.submitting" class="animate-spin" data-icon="inline-start" />
                <Send v-else data-icon="inline-start" />
                <span>{{ attemptsStore.submitting ? 'Submitting...' : 'Submit for scoring' }}</span>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </template>

      <Card v-else class="border-border/80 bg-card/95">
        <CardContent class="flex min-h-72 flex-col items-center justify-center gap-4 py-12 text-center">
          <TriangleAlert class="text-destructive" />
          <div class="flex flex-col gap-2">
            <p class="font-semibold text-(--color-heading)">Practice prompt unavailable</p>
            <p class="max-w-lg text-sm leading-7 text-muted-foreground">
              {{ modulesStore.error ?? 'This phrase could not be loaded. Return to the lesson list and choose another prompt.' }}
            </p>
          </div>
          <Button variant="outline" @click="router.push('/lessons')">
            <BookOpen data-icon="inline-start" />
            <span>Back to lessons</span>
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
  BookOpen,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  LoaderCircle,
  Mic,
  RotateCcw,
  Send,
  Square,
  TriangleAlert,
  Volume2,
} from 'lucide-vue-next'

import StudentLayout from '@/layouts/StudentLayout.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useModulesStore } from '@/stores/modules'
import { useAttemptsStore } from '@/stores/attempts'
import { useAudioRecorder } from '@/composables/useAudioRecorder'
import type { Module, Phrase } from '@/types'

const route = useRoute()
const router = useRouter()
const modulesStore = useModulesStore()
const attemptsStore = useAttemptsStore()
const recorder = useAudioRecorder()

const loading = ref(false)
const playingReference = ref(false)
const waveformTick = ref(0)

const moduleId = computed(() => String(route.params.moduleId ?? ''))
const phraseId = computed(() => String(route.params.phraseId ?? ''))

const module = computed<Module | undefined>(() =>
  modulesStore.getModuleById(moduleId.value),
)
const phrases = computed<Phrase[]>(() =>
  modulesStore.getPhrasesForModule(moduleId.value),
)
const phrase = computed<Phrase | undefined>(() =>
  phrases.value.find((item) => item.phrase_id === phraseId.value),
)
const phraseIndex = computed(() =>
  phrases.value.findIndex((item) => item.phrase_id === phraseId.value),
)

const difficultyLabel = computed(() => {
  const labels = ['', 'Beginner', 'Easy', 'Medium', 'Hard', 'Expert']
  return labels[phrase.value?.difficulty_level ?? 1]
})

const difficultyBadgeVariant = computed(() => {
  const level = phrase.value?.difficulty_level ?? 1
  if (level >= 4) return 'default'
  if (level === 3) return 'secondary'
  return 'outline'
})

const waveformBars = computed(() =>
  Array.from({ length: 28 }, (_, index) => {
    if (!recorder.isRecording.value) return 10
    return Math.max(10, Math.sin(index * 0.55 + waveformTick.value * 0.6) * 18 + 30)
  }),
)

const recorderHint = computed(() => {
  if (recorder.isRecording.value) {
    return 'Speak clearly, then stop the recording when you finish the phrase.'
  }

  if (recorder.audioBlob.value) {
    return 'Preview the take below. Clear it and record again if you want a cleaner attempt.'
  }

  return 'Use a quiet space if possible, and keep the microphone close enough for a clear capture.'
})

const recordingStateTitle = computed(() => {
  if (recorder.error.value || attemptsStore.error) {
    return 'Recording problem'
  }

  if (attemptsStore.submitting) {
    return 'Submitting attempt'
  }

  if (recorder.isRecording.value) {
    return 'Recording in progress'
  }

  if (recorder.audioBlob.value) {
    return 'Recording ready'
  }

  return 'Microphone ready'
})

const recordingStateCopy = computed(() => {
  if (attemptsStore.submitting) {
    return 'Your pronunciation is being uploaded and analyzed now.'
  }

  if (recorder.isRecording.value) {
    return `Live capture is running. Current duration: ${recorder.duration.value}s.`
  }

  if (recorder.audioBlob.value) {
    return 'You can preview the audio, clear it, or send it for scoring.'
  }

  return 'Start a recording when you are ready to practice this phrase.'
})

let waveformInterval: ReturnType<typeof setInterval> | null = null
let referenceAudio: HTMLAudioElement | null = null

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

watch(moduleId, async () => {
  await loadPracticeData()
})

onMounted(async () => {
  await loadPracticeData()
})

onBeforeUnmount(() => {
  if (waveformInterval) {
    clearInterval(waveformInterval)
  }
  if (recorder.isRecording.value) {
    recorder.stopRecording()
  }
  stopReferenceAudio()
  recorder.clearRecording()
})

async function loadPracticeData() {
  loading.value = true
  try {
    await modulesStore.fetchModules()
    await modulesStore.fetchPhrases(moduleId.value)
  } finally {
    loading.value = false
  }
}

function stopReferenceAudio() {
  if (referenceAudio) {
    referenceAudio.pause()
    referenceAudio.currentTime = 0
    referenceAudio = null
  }
  playingReference.value = false
}

async function playReference() {
  if (!phrase.value?.reference_audio_url) return

  stopReferenceAudio()
  playingReference.value = true

  try {
    referenceAudio = new Audio(phrase.value.reference_audio_url)
    referenceAudio.onended = () => {
      playingReference.value = false
      referenceAudio = null
    }
    referenceAudio.onerror = () => {
      playingReference.value = false
      referenceAudio = null
    }
    await referenceAudio.play()
  } catch {
    playingReference.value = false
    referenceAudio = null
  }
}

async function toggleRecording() {
  stopReferenceAudio()

  if (recorder.isRecording.value) {
    recorder.stopRecording()
    return
  }

  recorder.clearRecording()
  attemptsStore.clearLastAttempt()
  await recorder.startRecording()
}

function clearRecording() {
  recorder.clearRecording()
  attemptsStore.clearLastAttempt()
}

async function submitAttempt() {
  if (!recorder.audioBlob.value || !phrase.value) return

  try {
    await attemptsStore.submit(phrase.value.phrase_id, recorder.audioBlob.value)
    await router.push({
      path: '/results',
      query: {
        moduleId: moduleId.value,
        phraseId: phrase.value.phrase_id,
      },
    })
  } catch {
    // Submission errors are shown inline.
  }
}

async function goToPhrase(index: number) {
  const target = phrases.value[index]
  if (!target) return

  stopReferenceAudio()
  recorder.clearRecording()
  attemptsStore.clearLastAttempt()
  await router.push(`/practice/${moduleId.value}/${target.phrase_id}`)
}
</script>

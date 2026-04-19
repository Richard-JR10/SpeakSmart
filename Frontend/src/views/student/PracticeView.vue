<!-- src/views/student/PracticeView.vue -->
<template>
  <StudentLayout :title="module?.title ?? 'Practice'" show-back>

    <div class="practice">

      <LoadingSpinner v-if="loading" full-screen message="Loading phrase..." />

      <template v-else-if="phrase">

        <!-- Phrase navigation -->
        <div class="practice__nav">
          <button
            class="practice__nav-btn"
            :disabled="phraseIndex === 0"
            @click="goToPhrase(phraseIndex - 1)"
          >←</button>
          <span class="practice__nav-count">
            {{ phraseIndex + 1 }} / {{ phrases.length }}
          </span>
          <button
            class="practice__nav-btn"
            :disabled="phraseIndex === phrases.length - 1"
            @click="goToPhrase(phraseIndex + 1)"
          >→</button>
        </div>

        <!-- Difficulty badge -->
        <div class="practice__difficulty">
          <span
            v-for="i in 5"
            :key="i"
            class="practice__dot"
            :class="{ 'practice__dot--active': i <= phrase.difficulty_level }"
          />
          <span class="practice__difficulty-label">
            {{ difficultyLabel }}
          </span>
        </div>

        <!-- Phrase card -->
        <div class="practice__card">
          <p class="practice__japanese">{{ phrase.japanese_text }}</p>
          <p class="practice__romaji">{{ phrase.romaji }}</p>
          <p class="practice__english">{{ phrase.english_translation }}</p>
        </div>

        <!-- Hear reference button -->
        <button
          class="practice__reference-btn"
          :disabled="!phrase.reference_audio_url || playingReference"
          @click="playReference"
        >
          <span>{{ playingReference ? '🔊 Playing...' : '▶ Hear Reference' }}</span>
        </button>

        <!-- Waveform visualizer -->
        <div class="practice__waveform">
          <div
            v-for="(bar, i) in waveformBars"
            :key="i"
            class="practice__waveform-bar"
            :class="{ 'practice__waveform-bar--active': recorder.isRecording.value }"
            :style="{ height: bar + 'px' }"
          />
        </div>

        <!-- Recording duration -->
        <p v-if="recorder.isRecording.value" class="practice__duration">
          {{ recorder.duration.value }}s
        </p>

        <!-- Record button -->
        <div class="practice__record-wrap">
          <button
            class="practice__record-btn"
            :class="{ 'practice__record-btn--recording': recorder.isRecording.value }"
            @click="toggleRecording"
          >
            <span v-if="recorder.isRecording.value">⏹</span>
            <span v-else>🎙️</span>
          </button>
          <p class="practice__record-hint">
            {{ recorder.isRecording.value
                ? 'Tap to stop'
                : recorder.audioBlob.value
                  ? 'Recorded — tap to re-record'
                  : 'Tap to record' }}
          </p>
        </div>

        <!-- Recorder error -->
        <ErrorMessage :message="recorder.error.value" />

        <div v-if="recorder.audioUrl.value" class="practice__playback">
          <p class="practice__playback-label">Playback your recording</p>
          <audio
            class="practice__audio-player"
            :src="recorder.audioUrl.value"
            controls
            preload="metadata"
          />
        </div>

        <!-- Submit button -->
        <button
          v-if="recorder.audioBlob.value && !attemptsStore.submitting"
          class="practice__submit-btn"
          @click="submitAttempt"
        >
          Submit for Scoring →
        </button>

        <LoadingSpinner
          v-if="attemptsStore.submitting"
          message="Analyzing pronunciation..."
        />

        <ErrorMessage
          v-if="attemptsStore.error"
          :message="attemptsStore.error"
          dismissible
        />

      </template>

    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useModulesStore } from '@/stores/modules'
import { useAttemptsStore } from '@/stores/attempts'
import { useAudioRecorder } from '@/composables/useAudioRecorder'
import type { Phrase, Module } from '@/types'

const route = useRoute()
const router = useRouter()
const modulesStore = useModulesStore()
const attemptsStore = useAttemptsStore()
const recorder = useAudioRecorder()

const loading = ref(false)
const playingReference = ref(false)

const moduleId = computed(() => route.params.moduleId as string)
const phraseId = computed(() => route.params.phraseId as string)

const module = computed<Module | undefined>(() =>
  modulesStore.getModuleById(moduleId.value)
)
const phrases = computed<Phrase[]>(() =>
  modulesStore.getPhrasesForModule(moduleId.value)
)
const phrase = computed<Phrase | undefined>(() =>
  phrases.value.find((p) => p.phrase_id === phraseId.value)
)
const phraseIndex = computed(() =>
  phrases.value.findIndex((p) => p.phrase_id === phraseId.value)
)

const difficultyLabel = computed(() => {
  const labels = ['', 'Beginner', 'Easy', 'Medium', 'Hard', 'Expert']
  return labels[phrase.value?.difficulty_level ?? 1]
})

// Animated waveform bars
const waveformBars = computed(() => {
  return Array.from({ length: 30 }, (_, i) => {
    if (!recorder.isRecording.value) return 4
    return Math.max(4, Math.sin(i * 0.5 + Date.now() * 0.005) * 20 + 20)
  })
})

// Auto-animate waveform while recording
let waveformInterval: ReturnType<typeof setInterval> | null = null
watch(() => recorder.isRecording.value, (recording) => {
  if (recording) {
    waveformInterval = setInterval(() => {}, 50)
  } else {
    if (waveformInterval) clearInterval(waveformInterval)
  }
})

async function playReference() {
  if (!phrase.value?.reference_audio_url) return
  playingReference.value = true
  try {
    const audio = new Audio(phrase.value.reference_audio_url)
    audio.onended = () => { playingReference.value = false }
    audio.onerror = () => { playingReference.value = false }
    await audio.play()
  } catch {
    playingReference.value = false
  }
}

async function toggleRecording() {
  if (recorder.isRecording.value) {
    recorder.stopRecording()
  } else {
    recorder.clearRecording()
    attemptsStore.clearLastAttempt()
    await recorder.startRecording()
  }
}

async function submitAttempt() {
  if (!recorder.audioBlob.value || !phrase.value) return
  try {
    await attemptsStore.submit(phrase.value.phrase_id, recorder.audioBlob.value)
    router.push('/results')
  } catch {
    // error shown via ErrorMessage
  }
}

function goToPhrase(index: number) {
  const target = phrases.value[index]
  if (target) {
    recorder.clearRecording()
    attemptsStore.clearLastAttempt()
    router.push(`/practice/${moduleId.value}/${target.phrase_id}`)
  }
}

onMounted(async () => {
  loading.value = true
  await modulesStore.fetchModules()
  await modulesStore.fetchPhrases(moduleId.value)
  loading.value = false
})
</script>

<style scoped>
.practice {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.practice__nav {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  justify-content: center;
}

.practice__nav-btn {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
  color: var(--color-text);
  transition: background 0.15s;
}

.practice__nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.practice__nav-count {
  font-size: 14px;
  color: var(--color-subtext);
  font-weight: 600;
}

.practice__difficulty {
  display: flex;
  align-items: center;
  gap: 4px;
}

.practice__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
}

.practice__dot--active {
  background: var(--color-primary);
}

.practice__difficulty-label {
  font-size: 12px;
  color: var(--color-subtext);
  margin-left: 6px;
}

.practice__card {
  width: 100%;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center;
}

.practice__japanese {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.4;
}

.practice__romaji {
  font-size: 18px;
  color: var(--color-primary);
  font-weight: 600;
  margin-top: 8px;
}

.practice__english {
  font-size: 14px;
  color: var(--color-subtext);
  margin-top: 8px;
}

.practice__reference-btn {
  padding: 12px 24px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.practice__reference-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.practice__waveform {
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  background: var(--color-bg);
  border-radius: var(--radius);
  padding: 8px;
}

.practice__waveform-bar {
  width: 4px;
  background: var(--color-border);
  border-radius: 2px;
  min-height: 4px;
  transition: height 0.05s ease;
}

.practice__waveform-bar--active {
  background: var(--color-primary);
}

.practice__duration {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 600;
}

.practice__record-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.practice__record-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-primary);
  border: none;
  font-size: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.1s, background 0.15s;
  box-shadow: 0 4px 20px rgba(29, 158, 117, 0.4);
}

.practice__record-btn--recording {
  background: #EF4444;
  animation: pulse 1s infinite;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.practice__record-btn:active {
  transform: scale(0.93);
}

.practice__record-hint {
  font-size: 13px;
  color: var(--color-subtext);
}

.practice__playback {
  width: 100%;
  padding: 14px 16px;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.practice__playback-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 10px;
}

.practice__audio-player {
  width: 100%;
}

.practice__submit-btn {
  width: 100%;
  padding: 18px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.practice__submit-btn:hover {
  background: var(--color-primary-dark);
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
}
</style>

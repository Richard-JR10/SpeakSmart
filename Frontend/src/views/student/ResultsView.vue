<!-- src/views/student/ResultsView.vue -->
<template>
  <StudentLayout title="Your Results" show-back>

    <div class="results">

      <!-- No attempt guard -->
      <div v-if="!attempt" class="results__empty">
        <p class="results__empty-text">No result to show.</p>
        <button class="results__btn results__btn--primary" @click="router.push('/lessons')">
          Go to Lessons
        </button>
      </div>

      <template v-else>

        <!-- Score circle -->
        <div class="results__score-wrap">
          <ScoreCircle :score="attempt.accuracy_score" size="lg" />
        </div>

        <!-- Feedback text -->
        <div class="results__feedback">
          <p class="results__feedback-text">{{ attempt.feedback_text }}</p>
        </div>

        <div v-if="submittedAudioUrl" class="results__section results__section--card">
          <h3 class="results__section-title">Your Recording</h3>
          <audio
            class="results__audio-player"
            :src="submittedAudioUrl"
            controls
            preload="metadata"
          />
        </div>

        <!-- Phoneme breakdown -->
        <div class="results__section">
          <h3 class="results__section-title">Phoneme Breakdown</h3>
          <div class="results__chips">
            <PhonemeChip
              v-for="(data, key) in attempt.phoneme_error_map"
              :key="key"
              :label="data.label"
              :score="data.score"
              :error="data.error"
            />
          </div>
        </div>

        <!-- Score breakdown -->
        <div class="results__section">
          <h3 class="results__section-title">Score Breakdown</h3>
          <div class="results__breakdown">

            <div class="results__breakdown-row">
              <span class="results__breakdown-label">Mora Timing</span>
              <div class="results__breakdown-bar-wrap">
                <div
                  class="results__breakdown-bar"
                  :style="{ width: attempt.mora_timing_score + '%' }"
                  :class="barClass(attempt.mora_timing_score)"
                />
              </div>
              <span class="results__breakdown-value">
                {{ attempt.mora_timing_score.toFixed(0) }}%
              </span>
            </div>

            <div class="results__breakdown-row">
              <span class="results__breakdown-label">Consonants</span>
              <div class="results__breakdown-bar-wrap">
                <div
                  class="results__breakdown-bar"
                  :style="{ width: attempt.consonant_score + '%' }"
                  :class="barClass(attempt.consonant_score)"
                />
              </div>
              <span class="results__breakdown-value">
                {{ attempt.consonant_score.toFixed(0) }}%
              </span>
            </div>

            <div class="results__breakdown-row">
              <span class="results__breakdown-label">Vowel Purity</span>
              <div class="results__breakdown-bar-wrap">
                <div
                  class="results__breakdown-bar"
                  :style="{ width: attempt.vowel_score + '%' }"
                  :class="barClass(attempt.vowel_score)"
                />
              </div>
              <span class="results__breakdown-value">
                {{ attempt.vowel_score.toFixed(0) }}%
              </span>
            </div>

          </div>
        </div>

        <!-- Phrase reference -->
        <div class="results__phrase">
          <p class="results__phrase-label">Phrase practiced</p>
          <button
            class="results__play-btn"
            @click="playReference"
          >
            ▶ Hear reference again
          </button>
        </div>

        <!-- Action buttons -->
        <div class="results__actions">
          <button
            class="results__btn results__btn--ghost"
            @click="tryAgain"
          >
            🔄 Try Again
          </button>
          <button
            class="results__btn results__btn--primary"
            @click="nextPhrase"
          >
            Next Phrase →
          </button>
        </div>

      </template>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import ScoreCircle from '@/components/shared/ScoreCircle.vue'
import PhonemeChip from '@/components/shared/PhonemeChip.vue'
import { useAttemptsStore } from '@/stores/attempts'
import { useModulesStore } from '@/stores/modules'

const router = useRouter()
const attemptsStore = useAttemptsStore()
const modulesStore = useModulesStore()

const attempt = computed(() => attemptsStore.lastAttempt)
const submittedAudioUrl = computed(() => attemptsStore.lastSubmittedAudioUrl)

const currentPhrase = computed(() => {
  if (!attempt.value) return null
  const phraseId = attempt.value.phrase_id
  for (const phrases of Object.values(modulesStore.phrases)) {
    const found = phrases.find((p) => p.phrase_id === phraseId)
    if (found) return found
  }
  return null
})

const currentModule = computed(() => {
  if (!currentPhrase.value) return null
  return modulesStore.getModuleById(currentPhrase.value.module_id)
})

function barClass(score: number) {
  if (score >= 85) return 'results__breakdown-bar--excellent'
  if (score >= 70) return 'results__breakdown-bar--good'
  if (score >= 55) return 'results__breakdown-bar--fair'
  return 'results__breakdown-bar--poor'
}

function playReference() {
  if (!currentPhrase.value?.reference_audio_url) return
  const audio = new Audio(currentPhrase.value.reference_audio_url)
  audio.play()
}

function tryAgain() {
  if (!currentPhrase.value) return router.push('/lessons')
  attemptsStore.clearLastAttempt()
  router.push(`/practice/${currentPhrase.value.module_id}/${currentPhrase.value.phrase_id}`)
}

function nextPhrase() {
  if (!currentPhrase.value || !currentModule.value) return router.push('/lessons')
  const phrases = modulesStore.getPhrasesForModule(currentPhrase.value.module_id)
  const currentIndex = phrases.findIndex((p) => p.phrase_id === currentPhrase.value!.phrase_id)
  const next = phrases[currentIndex + 1]
  if (next) {
    attemptsStore.clearLastAttempt()
    router.push(`/practice/${currentPhrase.value.module_id}/${next.phrase_id}`)
  } else {
    router.push('/lessons')
  }
}
</script>

<style scoped>
.results {
  padding: 24px 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.results__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 0;
}

.results__empty-text {
  font-size: 16px;
  color: var(--color-subtext);
}

.results__score-wrap {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.results__feedback {
  background: var(--color-primary-light);
  border-left: 4px solid var(--color-primary);
  border-radius: 0 var(--radius) var(--radius) 0;
  padding: 16px;
}

.results__feedback-text {
  font-size: 15px;
  color: var(--color-text);
  line-height: 1.6;
}

.results__section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 14px;
}

.results__section--card {
  padding: 16px;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.results__audio-player {
  width: 100%;
}

.results__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.results__breakdown {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.results__breakdown-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.results__breakdown-label {
  font-size: 13px;
  color: var(--color-subtext);
  width: 90px;
  flex-shrink: 0;
}

.results__breakdown-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.results__breakdown-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.results__breakdown-bar--excellent,
.results__breakdown-bar--good      { background: var(--color-primary); }
.results__breakdown-bar--fair      { background: #F59E0B; }
.results__breakdown-bar--poor      { background: #EF4444; }

.results__breakdown-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  width: 36px;
  text-align: right;
  flex-shrink: 0;
}

.results__phrase {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--color-bg);
  border-radius: var(--radius);
}

.results__phrase-label {
  font-size: 13px;
  color: var(--color-subtext);
}

.results__play-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.results__actions {
  display: flex;
  gap: 12px;
}

.results__btn {
  flex: 1;
  padding: 16px;
  border-radius: var(--radius);
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}

.results__btn:active { transform: scale(0.98); }

.results__btn--primary {
  background: var(--color-primary);
  color: #ffffff;
}

.results__btn--primary:hover {
  background: var(--color-primary-dark);
}

.results__btn--ghost {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
</style>

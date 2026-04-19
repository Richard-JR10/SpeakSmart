<!-- src/views/student/ProgressView.vue -->
<template>
  <StudentLayout title="My Progress">

    <div class="progress-view">

      <LoadingSpinner v-if="progressStore.loading" full-screen message="Loading progress..." />

      <template v-else-if="dashboard">

        <!-- Overall stats -->
        <div class="progress-view__stats">
          <div class="progress-view__stat">
            <p class="progress-view__stat-value">
              {{ dashboard.overall_average.toFixed(1) }}%
            </p>
            <p class="progress-view__stat-label">Overall Accuracy</p>
            <p
              class="progress-view__stat-delta"
              :class="deltaClass"
            >
              {{ deltaText }}
            </p>
          </div>
          <div class="progress-view__stat">
            <p class="progress-view__stat-value">{{ dashboard.total_attempts }}</p>
            <p class="progress-view__stat-label">Total Attempts</p>
          </div>
          <div class="progress-view__stat">
            <p class="progress-view__stat-value">🔥 {{ dashboard.streak_days }}</p>
            <p class="progress-view__stat-label">Day Streak</p>
          </div>
        </div>

        <!-- Weekly bar chart -->
        <div class="progress-view__section">
          <h3 class="progress-view__section-title">Weekly Accuracy</h3>
          <div class="progress-view__chart">
            <div
              v-for="week in dashboard.weekly_accuracy"
              :key="week.week_start"
              class="progress-view__chart-col"
            >
              <p class="progress-view__chart-value">
                {{ week.average_accuracy > 0 ? week.average_accuracy.toFixed(0) + '%' : '' }}
              </p>
              <div class="progress-view__chart-bar-wrap">
                <div
                  class="progress-view__chart-bar"
                  :style="{ height: barHeight(week.average_accuracy) + 'px' }"
                  :class="{ 'progress-view__chart-bar--empty': week.average_accuracy === 0 }"
                />
              </div>
              <p class="progress-view__chart-label">
                {{ formatWeekLabel(week.week_start) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Weakest area alert -->
        <div v-if="dashboard.weakest_module_id" class="progress-view__alert">
          <span class="progress-view__alert-icon">⚠️</span>
          <div>
            <p class="progress-view__alert-title">Weakest Area</p>
            <p class="progress-view__alert-desc">
              {{ weakestTitle }} —
              {{ dashboard.weakest_module_score?.toFixed(0) }}% average
            </p>
          </div>
          <button
            class="progress-view__alert-btn"
            @click="practiceWeakest"
          >
            Practice
          </button>
        </div>

        <!-- Per-module breakdown -->
        <div class="progress-view__section">
          <h3 class="progress-view__section-title">By Module</h3>
          <div class="progress-view__modules">
            <div
              v-for="summary in dashboard.progress_by_module"
              :key="summary.module_id"
              class="progress-view__module"
            >
              <div class="progress-view__module-left">
                <span class="progress-view__module-icon">
                  {{ moduleIcon(summary.module_id) }}
                </span>
                <div>
                  <p class="progress-view__module-title">
                    {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                  </p>
                  <p class="progress-view__module-meta">
                    {{ summary.total_attempts }} attempts
                  </p>
                </div>
              </div>
              <div class="progress-view__module-right">
                <ScoreCircle :score="summary.average_accuracy" size="sm" />
              </div>
            </div>
          </div>
        </div>

        <!-- Recent attempts -->
        <div class="progress-view__section">
          <h3 class="progress-view__section-title">Recent Attempts</h3>
          <LoadingSpinner v-if="attemptsStore.loading" size="sm" />
          <div v-else class="progress-view__attempts">
            <div
              v-for="attempt in attemptsStore.attemptHistory"
              :key="attempt.attempt_id"
              class="progress-view__attempt"
            >
              <div class="progress-view__attempt-left">
                <p class="progress-view__attempt-phrase">{{ attempt.phrase_id }}</p>
                <p class="progress-view__attempt-date">
                  {{ formatDate(attempt.attempted_at) }}
                </p>
              </div>
              <span
                class="progress-view__attempt-score"
                :class="scoreClass(attempt.accuracy_score)"
              >
                {{ attempt.accuracy_score.toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>

      </template>

      <div v-else class="progress-view__empty">
        <p>No progress data yet — start practicing!</p>
        <button
          class="progress-view__start-btn"
          @click="router.push('/lessons')"
        >
          Go to Lessons
        </button>
      </div>

    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ScoreCircle from '@/components/shared/ScoreCircle.vue'
import { useProgressStore } from '@/stores/progress'
import { useAttemptsStore } from '@/stores/attempts'
import { useModulesStore } from '@/stores/modules'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const progressStore = useProgressStore()
const attemptsStore = useAttemptsStore()
const modulesStore = useModulesStore()
const authStore = useAuthStore()

const dashboard = computed(() => progressStore.dashboard)

const MODULE_ICONS: Record<string, string> = {
  module_greetings:  '👋',
  module_hotel:      '🏨',
  module_directions: '🗺️',
  module_food:       '🍜',
  module_emergency:  '🚨',
  module_tour_guide: '🎌',
}

function moduleIcon(id: string) {
  return MODULE_ICONS[id] ?? '📚'
}

const weakestTitle = computed(() => {
  if (!dashboard.value?.weakest_module_id) return ''
  return modulesStore.getModuleById(dashboard.value.weakest_module_id)?.title ?? ''
})

// Delta vs last week
const deltaClass = computed(() => {
  if (!dashboard.value?.weekly_accuracy?.length) return ''
  const weeks = dashboard.value.weekly_accuracy
  const last = weeks[weeks.length - 1]?.average_accuracy ?? 0
  const prev = weeks[weeks.length - 2]?.average_accuracy ?? 0
  return last >= prev ? 'progress-view__stat-delta--up' : 'progress-view__stat-delta--down'
})

const deltaText = computed(() => {
  if (!dashboard.value?.weekly_accuracy?.length) return ''
  const weeks = dashboard.value.weekly_accuracy
  const last = weeks[weeks.length - 1]?.average_accuracy ?? 0
  const prev = weeks[weeks.length - 2]?.average_accuracy ?? 0
  const diff = (last - prev).toFixed(1)
  return last >= prev ? `+${diff}% this week` : `${diff}% this week`
})

function barHeight(accuracy: number) {
  return Math.max(4, (accuracy / 100) * 80)
}

function formatWeekLabel(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function scoreClass(score: number) {
  if (score >= 85) return 'progress-view__attempt-score--excellent'
  if (score >= 70) return 'progress-view__attempt-score--good'
  if (score >= 55) return 'progress-view__attempt-score--fair'
  return 'progress-view__attempt-score--poor'
}

async function practiceWeakest() {
  if (!dashboard.value?.weakest_module_id) return
  await modulesStore.fetchPhrases(dashboard.value.weakest_module_id)
  const phrases = modulesStore.getPhrasesForModule(dashboard.value.weakest_module_id)
  if (phrases.length) {
    router.push(`/practice/${dashboard.value.weakest_module_id}/${phrases[0].phrase_id}`)
  }
}

onMounted(async () => {
  const uid = authStore.uid!
  await Promise.all([
    modulesStore.fetchModules(),
    progressStore.fetchDashboard(uid),
    attemptsStore.fetchHistory(uid),
  ])
})
</script>

<style scoped>
.progress-view {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.progress-view__stats {
  display: flex;
  justify-content: space-around;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
}

.progress-view__stat {
  text-align: center;
}

.progress-view__stat-value {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text);
}

.progress-view__stat-label {
  font-size: 11px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.progress-view__stat-delta {
  font-size: 11px;
  font-weight: 600;
  margin-top: 4px;
}

.progress-view__stat-delta--up   { color: var(--color-primary); }
.progress-view__stat-delta--down { color: #EF4444; }

.progress-view__section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 14px;
}

.progress-view__chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 120px;
  padding: 0 4px;
}

.progress-view__chart-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}

.progress-view__chart-value {
  font-size: 9px;
  color: var(--color-subtext);
  height: 14px;
}

.progress-view__chart-bar-wrap {
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.progress-view__chart-bar {
  width: 80%;
  background: var(--color-primary);
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: height 0.4s ease;
}

.progress-view__chart-bar--empty {
  background: var(--color-border);
}

.progress-view__chart-label {
  font-size: 9px;
  color: var(--color-subtext);
  text-align: center;
}

.progress-view__alert {
  background: #fffbeb;
  border: 1.5px solid #F59E0B;
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-view__alert-icon { font-size: 22px; }

.progress-view__alert-title {
  font-size: 14px;
  font-weight: 700;
  color: #92400e;
}

.progress-view__alert-desc {
  font-size: 12px;
  color: #92400e;
  margin-top: 2px;
}

.progress-view__alert-btn {
  margin-left: auto;
  background: #F59E0B;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

.progress-view__modules {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-view__module {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.progress-view__module-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-view__module-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  background: var(--color-primary-light);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-view__module-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.progress-view__module-meta {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.progress-view__attempts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-view__attempt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--color-bg);
  border-radius: 8px;
}

.progress-view__attempt-phrase {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.progress-view__attempt-date {
  font-size: 11px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.progress-view__attempt-score {
  font-size: 13px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

.progress-view__attempt-score--excellent,
.progress-view__attempt-score--good { background: #d1fae5; color: #065f46; }
.progress-view__attempt-score--fair { background: #fef3c7; color: #92400e; }
.progress-view__attempt-score--poor { background: #fee2e2; color: #991b1b; }

.progress-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 0;
  color: var(--color-subtext);
}

.progress-view__start-btn {
  padding: 12px 28px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
</style>
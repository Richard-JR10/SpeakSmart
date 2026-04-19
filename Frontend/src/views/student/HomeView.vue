<!-- src/views/student/HomeView.vue -->
<template>
  <StudentLayout title="SpeakSmart">

    <div class="home">

      <!-- Greeting -->
      <div class="home__greeting">
        <p class="home__greeting-sub">Good {{ timeOfDay }},</p>
        <h2 class="home__greeting-name">{{ authStore.profile?.display_name ?? 'Student' }}</h2>
      </div>

      <!-- Streak card -->
      <div class="home__streak-card">
        <div class="home__streak-left">
          <span class="home__streak-icon">🔥</span>
          <div>
            <p class="home__streak-count">{{ dashboard?.streak_days ?? 0 }} day streak</p>
            <p class="home__streak-sub">Keep practicing daily!</p>
          </div>
        </div>
        <div class="home__streak-badge">
          {{ dashboard?.streak_days ?? 0 }}
        </div>
      </div>

      <!-- Stats row -->
      <div class="home__stats">
        <div class="home__stat">
          <p class="home__stat-value">
            {{ dashboard?.overall_average?.toFixed(1) ?? '—' }}%
          </p>
          <p class="home__stat-label">Avg Accuracy</p>
        </div>
        <div class="home__stat-divider" />
        <div class="home__stat">
          <p class="home__stat-value">{{ dashboard?.total_attempts ?? 0 }}</p>
          <p class="home__stat-label">Attempts</p>
        </div>
        <div class="home__stat-divider" />
        <div class="home__stat">
          <p class="home__stat-value">{{ modulesStore.modules.length }}</p>
          <p class="home__stat-label">Modules</p>
        </div>
      </div>

      <!-- Continue card -->
      <div
        v-if="continueModule"
        class="home__continue"
        @click="router.push('/lessons')"
      >
        <div class="home__continue-left">
          <p class="home__continue-label">Continue Learning</p>
          <p class="home__continue-module">{{ continueModule.title }}</p>
          <p class="home__continue-sub">
            {{ continueProgress?.total_attempts ?? 0 }} attempts so far
          </p>
        </div>
        <span class="home__continue-arrow">→</span>
      </div>

      <!-- Weakest area alert -->
      <div
        v-if="dashboard?.weakest_module_id"
        class="home__alert"
      >
        <span class="home__alert-icon">⚠️</span>
        <div>
          <p class="home__alert-title">Needs Attention</p>
          <p class="home__alert-desc">
            {{ weakestModuleTitle }} — {{ dashboard.weakest_module_score?.toFixed(0) }}% avg
          </p>
        </div>
      </div>

      <!-- Recent scores -->
      <div class="home__section">
        <h3 class="home__section-title">Recent Attempts</h3>
        <LoadingSpinner v-if="attemptsStore.loading" size="sm" />
        <div v-else-if="attemptsStore.attemptHistory.length" class="home__attempts">
          <div
            v-for="attempt in attemptsStore.attemptHistory.slice(0, 5)"
            :key="attempt.attempt_id"
            class="home__attempt"
          >
            <div class="home__attempt-phrase">{{ attempt.phrase_id }}</div>
            <div
              class="home__attempt-score"
              :class="scoreClass(attempt.accuracy_score)"
            >
              {{ attempt.accuracy_score.toFixed(0) }}%
            </div>
          </div>
        </div>
        <p v-else class="home__empty">
          No attempts yet — start practicing!
        </p>
      </div>

      <!-- Start practice CTA -->
      <button
        class="home__cta"
        @click="router.push('/lessons')"
      >
        Start Practicing 🎙️
      </button>

    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useAuthStore } from '@/stores/auth'
import { useProgressStore } from '@/stores/progress'
import { useModulesStore } from '@/stores/modules'
import { useAttemptsStore } from '@/stores/attempts'

const router = useRouter()
const authStore = useAuthStore()
const progressStore = useProgressStore()
const modulesStore = useModulesStore()
const attemptsStore = useAttemptsStore()

const dashboard = computed(() => progressStore.dashboard)

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 18) return 'afternoon'
  return 'evening'
})

const continueModule = computed(() => {
  if (!dashboard.value?.progress_by_module?.length) return null
  const lastProgress = [...dashboard.value.progress_by_module]
    .sort((a, b) =>
      new Date(b.last_attempted_at ?? 0).getTime() -
      new Date(a.last_attempted_at ?? 0).getTime()
    )[0]
  return modulesStore.getModuleById(lastProgress?.module_id)
})

const continueProgress = computed(() => {
  if (!continueModule.value) return null
  return progressStore.getProgressForModule(continueModule.value.module_id)
})

const weakestModuleTitle = computed(() => {
  if (!dashboard.value?.weakest_module_id) return ''
  return modulesStore.getModuleById(dashboard.value.weakest_module_id)?.title ?? ''
})

function scoreClass(score: number) {
  if (score >= 85) return 'home__attempt-score--excellent'
  if (score >= 70) return 'home__attempt-score--good'
  if (score >= 55) return 'home__attempt-score--fair'
  return 'home__attempt-score--poor'
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
.home {
  padding: 20px 20px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.home__greeting-sub {
  font-size: 14px;
  color: var(--color-subtext);
}

.home__greeting-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
}

.home__streak-card {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #ffffff;
}

.home__streak-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.home__streak-icon {
  font-size: 32px;
}

.home__streak-count {
  font-size: 16px;
  font-weight: 700;
}

.home__streak-sub {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

.home__streak-badge {
  width: 52px;
  height: 52px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
}

.home__stats {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.home__stat {
  text-align: center;
}

.home__stat-value {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text);
}

.home__stat-label {
  font-size: 11px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.home__stat-divider {
  width: 1px;
  height: 36px;
  background: var(--color-border);
}

.home__continue {
  background: var(--color-primary-light);
  border: 1.5px solid var(--color-primary);
  border-radius: var(--radius);
  padding: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: background 0.15s;
}

.home__continue:hover {
  background: #c7f0e2;
}

.home__continue-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.home__continue-module {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
  margin-top: 4px;
}

.home__continue-sub {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.home__continue-arrow {
  font-size: 22px;
  color: var(--color-primary);
}

.home__alert {
  background: #fffbeb;
  border: 1.5px solid #F59E0B;
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.home__alert-icon {
  font-size: 22px;
}

.home__alert-title {
  font-size: 14px;
  font-weight: 700;
  color: #92400e;
}

.home__alert-desc {
  font-size: 13px;
  color: #92400e;
  margin-top: 2px;
}

.home__section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 12px;
}

.home__attempts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.home__attempt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--color-bg);
  border-radius: 8px;
}

.home__attempt-phrase {
  font-size: 13px;
  color: var(--color-subtext);
}

.home__attempt-score {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

.home__attempt-score--excellent { background: #d1fae5; color: #065f46; }
.home__attempt-score--good      { background: #d1fae5; color: #065f46; }
.home__attempt-score--fair      { background: #fef3c7; color: #92400e; }
.home__attempt-score--poor      { background: #fee2e2; color: #991b1b; }

.home__empty {
  font-size: 14px;
  color: var(--color-subtext);
  text-align: center;
  padding: 20px 0;
}

.home__cta {
  width: 100%;
  padding: 18px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.home__cta:active {
  transform: scale(0.98);
}

.home__cta:hover {
  background: var(--color-primary-dark);
}
</style>
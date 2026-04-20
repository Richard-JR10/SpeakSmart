<template>
  <InstructorLayout>
    <div class="overview page-shell">
      <section class="overview__header">
        <p class="eyebrow">Instructor overview</p>
        <h1 class="display-title">Class progress at a glance</h1>
        <p class="overview__subtitle">
          {{ authStore.profile?.display_name }} -
          {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) }}
        </p>
      </section>

      <LoadingSpinner v-if="loading" full-screen message="Loading analytics..." />

      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else-if="overview">
        <section class="metric-grid">
          <article class="surface-card metric-card">
            <p class="metric-card__label">Class average</p>
            <p class="metric-card__value">{{ overview.class_average.toFixed(1) }}%</p>
            <p class="metric-card__hint">Overall pronunciation accuracy.</p>
          </article>
          <article class="surface-card metric-card">
            <p class="metric-card__label">Total students</p>
            <p class="metric-card__value">{{ overview.total_students }}</p>
            <p class="metric-card__hint">Students assigned to this class.</p>
          </article>
          <article class="surface-card metric-card">
            <p class="metric-card__label">Active this week</p>
            <p class="metric-card__value">{{ overview.active_students }}</p>
            <p class="metric-card__hint">Students who practiced recently.</p>
          </article>
          <article class="surface-card metric-card">
            <p class="metric-card__label">Flagged students</p>
            <p class="metric-card__value">{{ overview.flagged_students.length }}</p>
            <p class="metric-card__hint">Below {{ flagThreshold }}% accuracy.</p>
          </article>
        </section>

        <section class="overview__grid">
          <article class="surface-card overview__panel">
            <div class="section-heading">
              <div class="section-heading__text">
                <p class="eyebrow">Weekly trend</p>
                <h2 class="section-title">Accuracy movement</h2>
              </div>
            </div>

            <div class="overview__trend-chart">
              <div
                v-for="week in overview.weekly_trend"
                :key="week.week_start"
                class="overview__trend-col"
              >
                <p class="overview__trend-value">
                  {{ week.average_accuracy > 0 ? week.average_accuracy.toFixed(0) + '%' : '' }}
                </p>
                <div class="overview__trend-bar-wrap">
                  <div
                    class="overview__trend-bar"
                    :style="{ height: barHeight(week.average_accuracy) + 'px' }"
                    :class="{ 'overview__trend-bar--empty': week.average_accuracy === 0 }"
                  />
                </div>
                <p class="overview__trend-label">{{ formatWeekLabel(week.week_start) }}</p>
              </div>
            </div>
          </article>

          <article class="surface-card overview__panel">
            <div class="section-heading">
              <div class="section-heading__text">
                <p class="eyebrow">Phoneme averages</p>
                <h2 class="section-title">Class pronunciation profile</h2>
              </div>
            </div>

            <div class="overview__phoneme-list">
              <div class="overview__phoneme-item">
                <div class="overview__phoneme-head">
                  <span>Mora timing</span>
                  <span>{{ overview.phoneme_breakdown.mora_timing_avg.toFixed(1) }}%</span>
                </div>
                <div class="progress-track">
                  <div
                    class="overview__phoneme-fill"
                    :style="{ width: overview.phoneme_breakdown.mora_timing_avg + '%' }"
                    :class="phonemeBarClass(overview.phoneme_breakdown.mora_timing_avg)"
                  />
                </div>
              </div>

              <div class="overview__phoneme-item">
                <div class="overview__phoneme-head">
                  <span>Consonants</span>
                  <span>{{ overview.phoneme_breakdown.consonant_avg.toFixed(1) }}%</span>
                </div>
                <div class="progress-track">
                  <div
                    class="overview__phoneme-fill"
                    :style="{ width: overview.phoneme_breakdown.consonant_avg + '%' }"
                    :class="phonemeBarClass(overview.phoneme_breakdown.consonant_avg)"
                  />
                </div>
              </div>

              <div class="overview__phoneme-item">
                <div class="overview__phoneme-head">
                  <span>Vowel purity</span>
                  <span>{{ overview.phoneme_breakdown.vowel_avg.toFixed(1) }}%</span>
                </div>
                <div class="progress-track">
                  <div
                    class="overview__phoneme-fill"
                    :style="{ width: overview.phoneme_breakdown.vowel_avg + '%' }"
                    :class="phonemeBarClass(overview.phoneme_breakdown.vowel_avg)"
                  />
                </div>
              </div>
            </div>
          </article>
        </section>

        <section v-if="overview.flagged_students.length" class="surface-card overview__panel">
          <div class="section-heading">
            <div class="section-heading__text">
              <p class="eyebrow">Needs attention</p>
              <h2 class="section-title">Flagged students</h2>
            </div>
            <span class="pill-badge pill-badge--warning">
              Below {{ flagThreshold }}%
            </span>
          </div>

          <div class="overview__flagged-list">
            <button
              v-for="student in overview.flagged_students"
              :key="student.uid"
              type="button"
              class="overview__flagged-row"
              @click="router.push('/instructor/students')"
            >
              <div class="overview__flagged-avatar">
                {{ student.display_name[0].toUpperCase() }}
              </div>
              <div class="overview__flagged-info">
                <p class="overview__flagged-name">{{ student.display_name }}</p>
                <p class="overview__flagged-email">{{ student.email }}</p>
              </div>
              <span class="pill-badge pill-badge--danger">
                {{ student.overall_average.toFixed(0) }}%
              </span>
            </button>
          </div>
        </section>
      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useAuthStore } from '@/stores/auth'
import { getClassOverview } from '@/api/analytics'
import type { ClassOverview } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const overview = ref<ClassOverview | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const flagThreshold = 60

function barHeight(accuracy: number) {
  return Math.max(8, (accuracy / 100) * 140)
}

function formatWeekLabel(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric',
  })
}

function phonemeBarClass(score: number) {
  if (score >= 85) return 'overview__phoneme-fill--excellent'
  if (score >= 70) return 'overview__phoneme-fill--good'
  if (score >= 55) return 'overview__phoneme-fill--fair'
  return 'overview__phoneme-fill--poor'
}

onMounted(async () => {
  const classId = authStore.profile?.class_id
  if (!classId) {
    error.value = 'No class assigned to your account. Contact the administrator.'
    return
  }
  loading.value = true
  try {
    overview.value = await getClassOverview(classId, flagThreshold)
  } catch {
    error.value = 'Failed to load class analytics.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.overview {
  gap: 24px;
}

.overview__subtitle {
  margin: 12px 0 0;
  color: var(--color-subtext);
  font-size: 16px;
}

.overview__grid {
  display: grid;
  gap: 18px;
}

.overview__panel {
  padding: 24px;
}

.overview__trend-chart {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(58px, 1fr));
  gap: 10px;
  align-items: end;
  margin-top: 20px;
  min-height: 210px;
}

.overview__trend-col {
  display: grid;
  gap: 6px;
  justify-items: center;
  align-content: end;
}

.overview__trend-value,
.overview__trend-label {
  font-size: 11px;
  color: var(--color-subtext);
}

.overview__trend-bar-wrap {
  width: 100%;
  min-height: 144px;
  display: flex;
  align-items: end;
  justify-content: center;
}

.overview__trend-bar {
  width: 70%;
  border-radius: 14px 14px 4px 4px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-accent));
}

.overview__trend-bar--empty {
  background: rgba(215, 225, 218, 0.92);
}

.overview__phoneme-list {
  display: grid;
  gap: 18px;
  margin-top: 20px;
}

.overview__phoneme-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  font-weight: 700;
  color: var(--color-heading);
}

.overview__phoneme-fill {
  height: 100%;
  border-radius: inherit;
}

.overview__phoneme-fill--excellent,
.overview__phoneme-fill--good {
  background: linear-gradient(90deg, var(--color-primary), #4ca07e);
}

.overview__phoneme-fill--fair {
  background: linear-gradient(90deg, #d4a257, #b87b26);
}

.overview__phoneme-fill--poor {
  background: linear-gradient(90deg, #d86a5d, #b9473a);
}

.overview__flagged-list {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.overview__flagged-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: var(--radius-sm);
  background: rgba(240, 244, 238, 0.72);
  cursor: pointer;
  text-align: left;
}

.overview__flagged-avatar {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: rgba(198, 85, 73, 0.14);
  color: #8b2f26;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.overview__flagged-info {
  flex: 1;
}

.overview__flagged-name {
  margin: 0;
  font-weight: 700;
  color: var(--color-heading);
}

.overview__flagged-email {
  margin: 4px 0 0;
  color: var(--color-subtext);
}

@media (min-width: 1024px) {
  .overview__grid {
    grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  }
}
</style>

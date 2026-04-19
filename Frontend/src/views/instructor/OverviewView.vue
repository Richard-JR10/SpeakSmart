<!-- src/views/instructor/OverviewView.vue -->
<template>
  <InstructorLayout>

    <div class="overview">

      <div class="overview__header">
        <h1 class="overview__title">Class Overview</h1>
        <p class="overview__subtitle">
          {{ authStore.profile?.display_name }} ·
          {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) }}
        </p>
      </div>

      <LoadingSpinner v-if="loading" full-screen message="Loading analytics..." />

      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else-if="overview">

        <!-- Stat cards -->
        <div class="overview__stat-cards">
          <div class="overview__stat-card">
            <p class="overview__stat-label">Class Average</p>
            <p class="overview__stat-value">{{ overview.class_average.toFixed(1) }}%</p>
            <p class="overview__stat-sub">overall accuracy</p>
          </div>
          <div class="overview__stat-card">
            <p class="overview__stat-label">Total Students</p>
            <p class="overview__stat-value">{{ overview.total_students }}</p>
            <p class="overview__stat-sub">enrolled</p>
          </div>
          <div class="overview__stat-card">
            <p class="overview__stat-label">Active This Week</p>
            <p class="overview__stat-value">{{ overview.active_students }}</p>
            <p class="overview__stat-sub">students practiced</p>
          </div>
          <div class="overview__stat-card overview__stat-card--warning">
            <p class="overview__stat-label">Flagged</p>
            <p class="overview__stat-value">{{ overview.flagged_students.length }}</p>
            <p class="overview__stat-sub">below {{ flagThreshold }}%</p>
          </div>
        </div>

        <!-- Weekly trend chart -->
        <div class="overview__card">
          <h3 class="overview__card-title">Weekly Accuracy Trend</h3>
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
              <p class="overview__trend-label">
                {{ formatWeekLabel(week.week_start) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Phoneme error breakdown -->
        <div class="overview__card">
          <h3 class="overview__card-title">Class Phoneme Averages</h3>
          <div class="overview__phoneme-grid">

            <div class="overview__phoneme-item">
              <div class="overview__phoneme-bar-wrap">
                <div
                  class="overview__phoneme-bar"
                  :style="{ width: overview.phoneme_breakdown.mora_timing_avg + '%' }"
                  :class="phonemeBarClass(overview.phoneme_breakdown.mora_timing_avg)"
                />
              </div>
              <div class="overview__phoneme-info">
                <span class="overview__phoneme-label">Mora Timing</span>
                <span class="overview__phoneme-value">
                  {{ overview.phoneme_breakdown.mora_timing_avg.toFixed(1) }}%
                </span>
              </div>
            </div>

            <div class="overview__phoneme-item">
              <div class="overview__phoneme-bar-wrap">
                <div
                  class="overview__phoneme-bar"
                  :style="{ width: overview.phoneme_breakdown.consonant_avg + '%' }"
                  :class="phonemeBarClass(overview.phoneme_breakdown.consonant_avg)"
                />
              </div>
              <div class="overview__phoneme-info">
                <span class="overview__phoneme-label">Consonants / R-sound</span>
                <span class="overview__phoneme-value">
                  {{ overview.phoneme_breakdown.consonant_avg.toFixed(1) }}%
                </span>
              </div>
            </div>

            <div class="overview__phoneme-item">
              <div class="overview__phoneme-bar-wrap">
                <div
                  class="overview__phoneme-bar"
                  :style="{ width: overview.phoneme_breakdown.vowel_avg + '%' }"
                  :class="phonemeBarClass(overview.phoneme_breakdown.vowel_avg)"
                />
              </div>
              <div class="overview__phoneme-info">
                <span class="overview__phoneme-label">Vowel Purity</span>
                <span class="overview__phoneme-value">
                  {{ overview.phoneme_breakdown.vowel_avg.toFixed(1) }}%
                </span>
              </div>
            </div>

          </div>
        </div>

        <!-- Flagged students -->
        <div v-if="overview.flagged_students.length" class="overview__card">
          <h3 class="overview__card-title">
            ⚠️ Flagged Students
            <span class="overview__card-subtitle">below {{ flagThreshold }}% accuracy</span>
          </h3>
          <div class="overview__flagged-list">
            <div
              v-for="student in overview.flagged_students"
              :key="student.uid"
              class="overview__flagged-row"
              @click="router.push(`/instructor/students`)"
            >
              <div class="overview__flagged-avatar">
                {{ student.display_name[0].toUpperCase() }}
              </div>
              <div class="overview__flagged-info">
                <p class="overview__flagged-name">{{ student.display_name }}</p>
                <p class="overview__flagged-email">{{ student.email }}</p>
              </div>
              <span class="overview__flagged-score">
                {{ student.overall_average.toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>

      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  return Math.max(4, (accuracy / 100) * 100)
}

function formatWeekLabel(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric',
  })
}

function phonemeBarClass(score: number) {
  if (score >= 85) return 'overview__phoneme-bar--excellent'
  if (score >= 70) return 'overview__phoneme-bar--good'
  if (score >= 55) return 'overview__phoneme-bar--fair'
  return 'overview__phoneme-bar--poor'
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
  } catch (e) {
    error.value = 'Failed to load class analytics.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.overview {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.overview__title {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-text);
}

.overview__subtitle {
  font-size: 14px;
  color: var(--color-subtext);
  margin-top: 4px;
}

.overview__stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview__stat-card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
}

.overview__stat-card--warning {
  border-color: #F59E0B;
  background: #fffbeb;
}

.overview__stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-subtext);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.overview__stat-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--color-text);
  margin-top: 8px;
  line-height: 1;
}

.overview__stat-sub {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 4px;
}

.overview__card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 24px;
}

.overview__card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview__card-subtitle {
  font-size: 13px;
  color: var(--color-subtext);
  font-weight: 400;
}

.overview__trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 140px;
  padding: 0 4px;
}

.overview__trend-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}

.overview__trend-value {
  font-size: 10px;
  color: var(--color-subtext);
  height: 14px;
}

.overview__trend-bar-wrap {
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.overview__trend-bar {
  width: 70%;
  background: var(--color-primary);
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: height 0.4s ease;
}

.overview__trend-bar--empty {
  background: var(--color-border);
}

.overview__trend-label {
  font-size: 10px;
  color: var(--color-subtext);
  text-align: center;
}

.overview__phoneme-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview__phoneme-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.overview__phoneme-bar-wrap {
  height: 10px;
  background: var(--color-border);
  border-radius: 5px;
  overflow: hidden;
}

.overview__phoneme-bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.overview__phoneme-bar--excellent,
.overview__phoneme-bar--good { background: var(--color-primary); }
.overview__phoneme-bar--fair { background: #F59E0B; }
.overview__phoneme-bar--poor { background: #EF4444; }

.overview__phoneme-info {
  display: flex;
  justify-content: space-between;
}

.overview__phoneme-label {
  font-size: 13px;
  color: var(--color-subtext);
}

.overview__phoneme-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}

.overview__flagged-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.overview__flagged-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.overview__flagged-row:hover {
  background: var(--color-bg);
}

.overview__flagged-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fee2e2;
  color: #991b1b;
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.overview__flagged-info { flex: 1; }

.overview__flagged-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.overview__flagged-email {
  font-size: 12px;
  color: var(--color-subtext);
}

.overview__flagged-score {
  font-size: 14px;
  font-weight: 700;
  color: #EF4444;
  background: #fee2e2;
  padding: 4px 10px;
  border-radius: 20px;
}
</style>
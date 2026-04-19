<!-- src/views/instructor/StudentsView.vue -->
<template>
  <InstructorLayout>
    <div class="students">

      <div class="students__header">
        <h1 class="students__title">Students</h1>
        <input
          v-model="search"
          type="text"
          class="students__search"
          placeholder="Search by name or email..."
        />
      </div>

      <LoadingSpinner v-if="loading" full-screen message="Loading students..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>

        <!-- Student table -->
        <div class="students__card">
          <table class="students__table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Accuracy</th>
                <th>Attempts</th>
                <th>Streak</th>
                <th>Weakest Module</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="student in filteredStudents"
                :key="student.uid"
                class="students__row"
                :class="{ 'students__row--flagged': student.is_flagged }"
                @click="selectStudent(student.uid)"
              >
                <td>
                  <div class="students__student-cell">
                    <div class="students__avatar">
                      {{ student.display_name[0].toUpperCase() }}
                    </div>
                    <div>
                      <p class="students__name">{{ student.display_name }}</p>
                      <p class="students__email">{{ student.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="students__accuracy-cell">
                    <div class="students__accuracy-bar-wrap">
                      <div
                        class="students__accuracy-bar"
                        :style="{ width: student.overall_average + '%' }"
                        :class="accuracyBarClass(student.overall_average)"
                      />
                    </div>
                    <span class="students__accuracy-value">
                      {{ student.overall_average.toFixed(0) }}%
                    </span>
                  </div>
                </td>
                <td class="students__td-center">{{ student.total_attempts }}</td>
                <td class="students__td-center">🔥 {{ student.streak_days }}</td>
                <td class="students__td-muted">
                  {{ student.weakest_module_id?.replace('module_', '') ?? '—' }}
                </td>
                <td>
                  <span
                    class="students__status"
                    :class="student.is_flagged
                      ? 'students__status--flagged'
                      : 'students__status--ok'"
                  >
                    {{ student.is_flagged ? '⚠️ Flagged' : '✓ OK' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Drill-down panel -->
        <div v-if="selectedStudent" class="students__drilldown">
          <div class="students__drilldown-header">
            <h3 class="students__drilldown-title">
              {{ selectedStudent.display_name }}
            </h3>
            <button
              class="students__drilldown-close"
              @click="selectedStudentUid = null"
            >✕</button>
          </div>

          <LoadingSpinner v-if="drilldownLoading" size="sm" />

          <template v-else-if="drilldown">

            <!-- Stats row -->
            <div class="students__drilldown-stats">
              <div class="students__drilldown-stat">
                <p class="students__drilldown-stat-value">
                  {{ drilldown.overall_average.toFixed(1) }}%
                </p>
                <p class="students__drilldown-stat-label">Avg Accuracy</p>
              </div>
              <div class="students__drilldown-stat">
                <p class="students__drilldown-stat-value">
                  {{ drilldown.total_attempts }}
                </p>
                <p class="students__drilldown-stat-label">Attempts</p>
              </div>
              <div class="students__drilldown-stat">
                <p class="students__drilldown-stat-value">
                  🔥 {{ drilldown.streak_days }}
                </p>
                <p class="students__drilldown-stat-label">Streak</p>
              </div>
            </div>

            <!-- Phoneme breakdown -->
            <div class="students__drilldown-section">
              <p class="students__drilldown-section-title">Phoneme Scores</p>
              <div class="students__drilldown-phonemes">
                <div class="students__drilldown-phoneme">
                  <span>Mora Timing</span>
                  <span class="students__drilldown-phoneme-score">
                    {{ drilldown.phoneme_breakdown.mora_timing_avg.toFixed(0) }}%
                  </span>
                </div>
                <div class="students__drilldown-phoneme">
                  <span>Consonants</span>
                  <span class="students__drilldown-phoneme-score">
                    {{ drilldown.phoneme_breakdown.consonant_avg.toFixed(0) }}%
                  </span>
                </div>
                <div class="students__drilldown-phoneme">
                  <span>Vowel Purity</span>
                  <span class="students__drilldown-phoneme-score">
                    {{ drilldown.phoneme_breakdown.vowel_avg.toFixed(0) }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- Recent attempts -->
            <div class="students__drilldown-section">
              <p class="students__drilldown-section-title">Recent Attempts</p>
              <div class="students__drilldown-attempts">
                <div
                  v-for="attempt in drilldown.recent_attempts"
                  :key="attempt.attempt_id"
                  class="students__drilldown-attempt"
                >
                  <span class="students__drilldown-attempt-phrase">
                    {{ attempt.phrase_id }}
                  </span>
                  <span
                    class="students__drilldown-attempt-score"
                    :class="accuracyBadgeClass(attempt.accuracy_score)"
                  >
                    {{ attempt.accuracy_score.toFixed(0) }}%
                  </span>
                </div>
              </div>
            </div>

          </template>
        </div>

      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useAuthStore } from '@/stores/auth'
import { getAllStudents, getStudentDrillDown } from '@/api/analytics'
import type { StudentStat, StudentDrillDown } from '@/types'

const authStore = useAuthStore()

const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const search = ref('')

const selectedStudentUid = ref<string | null>(null)
const drilldown = ref<StudentDrillDown | null>(null)
const drilldownLoading = ref(false)

const filteredStudents = computed(() => {
  if (!search.value) return students.value
  const q = search.value.toLowerCase()
  return students.value.filter(
    (s) =>
      s.display_name.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q),
  )
})

const selectedStudent = computed(() =>
  students.value.find((s) => s.uid === selectedStudentUid.value) ?? null
)

function accuracyBarClass(score: number) {
  if (score >= 85) return 'students__accuracy-bar--excellent'
  if (score >= 70) return 'students__accuracy-bar--good'
  if (score >= 55) return 'students__accuracy-bar--fair'
  return 'students__accuracy-bar--poor'
}

function accuracyBadgeClass(score: number) {
  if (score >= 70) return 'students__drilldown-attempt-score--good'
  if (score >= 55) return 'students__drilldown-attempt-score--fair'
  return 'students__drilldown-attempt-score--poor'
}

async function selectStudent(uid: string) {
  selectedStudentUid.value = uid
  drilldown.value = null
  drilldownLoading.value = true
  try {
    drilldown.value = await getStudentDrillDown(uid)
  } catch {
    drilldown.value = null
  } finally {
    drilldownLoading.value = false
  }
}

onMounted(async () => {
  const classId = authStore.profile?.class_id
  if (!classId) {
    error.value = 'No class assigned to your account.'
    return
  }
  loading.value = true
  try {
    students.value = await getAllStudents(classId)
  } catch {
    error.value = 'Failed to load students.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.students {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.students__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.students__title {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-text);
}

.students__search {
  padding: 10px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 14px;
  outline: none;
  width: 280px;
  transition: border-color 0.15s;
}

.students__search:focus {
  border-color: var(--color-primary);
}

.students__card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.students__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.students__table thead tr {
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}

.students__table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-subtext);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.students__row {
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background 0.1s;
}

.students__row:last-child {
  border-bottom: none;
}

.students__row:hover {
  background: var(--color-bg);
}

.students__row--flagged {
  background: #fffbeb;
}

.students__table td {
  padding: 14px 16px;
  vertical-align: middle;
}

.students__student-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.students__avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.students__name {
  font-weight: 600;
  color: var(--color-text);
}

.students__email {
  font-size: 12px;
  color: var(--color-subtext);
}

.students__accuracy-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.students__accuracy-bar-wrap {
  width: 80px;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.students__accuracy-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.students__accuracy-bar--excellent,
.students__accuracy-bar--good { background: var(--color-primary); }
.students__accuracy-bar--fair { background: #F59E0B; }
.students__accuracy-bar--poor { background: #EF4444; }

.students__accuracy-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  min-width: 36px;
}

.students__td-center {
  text-align: center;
}

.students__td-muted {
  color: var(--color-subtext);
  text-transform: capitalize;
}

.students__status {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.students__status--ok {
  background: #d1fae5;
  color: #065f46;
}

.students__status--flagged {
  background: #fef3c7;
  color: #92400e;
}

/* Drilldown panel */
.students__drilldown {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 24px;
}

.students__drilldown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.students__drilldown-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
}

.students__drilldown-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-subtext);
}

.students__drilldown-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.students__drilldown-stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
}

.students__drilldown-stat-label {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.students__drilldown-section {
  margin-bottom: 20px;
}

.students__drilldown-section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-subtext);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 12px;
}

.students__drilldown-phonemes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.students__drilldown-phoneme {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  padding: 8px 12px;
  background: var(--color-bg);
  border-radius: 8px;
  color: var(--color-text);
}

.students__drilldown-phoneme-score {
  font-weight: 700;
  color: var(--color-primary);
}

.students__drilldown-attempts {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.students__drilldown-attempt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--color-bg);
  border-radius: 8px;
  font-size: 13px;
}

.students__drilldown-attempt-phrase {
  color: var(--color-subtext);
}

.students__drilldown-attempt-score {
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.students__drilldown-attempt-score--good { background: #d1fae5; color: #065f46; }
.students__drilldown-attempt-score--fair { background: #fef3c7; color: #92400e; }
.students__drilldown-attempt-score--poor { background: #fee2e2; color: #991b1b; }
</style>

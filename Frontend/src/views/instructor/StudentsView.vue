<template>
  <InstructorLayout>
    <div class="students page-shell">
      <section class="students__header">
        <div>
          <p class="eyebrow">Student directory</p>
          <h1 class="display-title">Monitor individual progress</h1>
          <p class="students__subtitle">
            Search students, review scores, and open detailed drilldowns without
            leaving the instructor workspace.
          </p>
        </div>

        <label class="students__search">
          <AppIcon name="search" :size="18" />
          <input
            v-model="search"
            type="text"
            placeholder="Search by name or email"
          />
        </label>
      </section>

      <LoadingSpinner v-if="loading" full-screen message="Loading students..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>
        <section class="surface-card students__table-card">
          <div class="section-heading">
            <div class="section-heading__text">
              <p class="eyebrow">Class roster</p>
              <h2 class="section-title">{{ filteredStudents.length }} learners</h2>
            </div>
            <span class="pill-badge">
              {{ students.filter((student) => student.is_flagged).length }} flagged
            </span>
          </div>

          <div class="data-table-wrap students__table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Accuracy</th>
                  <th>Attempts</th>
                  <th>Streak</th>
                  <th>Weakest module</th>
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
                      <div class="students__avatar">{{ student.display_name[0].toUpperCase() }}</div>
                      <div>
                        <p class="students__name">{{ student.display_name }}</p>
                        <p class="students__email">{{ student.email }}</p>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="students__accuracy-cell">
                      <div class="progress-track">
                        <div
                          class="students__accuracy-fill"
                          :style="{ width: student.overall_average + '%' }"
                          :class="accuracyBarClass(student.overall_average)"
                        />
                      </div>
                      <span class="students__accuracy-value">{{ student.overall_average.toFixed(0) }}%</span>
                    </div>
                  </td>
                  <td>{{ student.total_attempts }}</td>
                  <td>{{ student.streak_days }} days</td>
                  <td>{{ formatModuleId(student.weakest_module_id) }}</td>
                  <td>
                    <span
                      class="pill-badge"
                      :class="student.is_flagged ? 'pill-badge--warning' : ''"
                    >
                      {{ student.is_flagged ? 'Needs review' : 'On track' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="selectedStudent" class="surface-card students__drilldown">
          <div class="students__drilldown-header">
            <div>
              <p class="eyebrow">Student detail</p>
              <h2 class="section-title">{{ selectedStudent.display_name }}</h2>
              <p class="students__drilldown-sub">{{ selectedStudent.email }}</p>
            </div>
            <button
              type="button"
              class="students__close"
              @click="selectedStudentUid = null"
            >
              <AppIcon name="close" :size="18" />
            </button>
          </div>

          <LoadingSpinner v-if="drilldownLoading" size="sm" />

          <template v-else-if="drilldown">
            <div class="metric-grid">
              <article class="surface-card surface-card--muted metric-card">
                <p class="metric-card__label">Average accuracy</p>
                <p class="metric-card__value">{{ drilldown.overall_average.toFixed(1) }}%</p>
              </article>
              <article class="surface-card surface-card--muted metric-card">
                <p class="metric-card__label">Attempts</p>
                <p class="metric-card__value">{{ drilldown.total_attempts }}</p>
              </article>
              <article class="surface-card surface-card--muted metric-card">
                <p class="metric-card__label">Streak</p>
                <p class="metric-card__value">{{ drilldown.streak_days }}</p>
              </article>
            </div>

            <div class="students__drilldown-grid">
              <div class="surface-card surface-card--muted students__subpanel">
                <p class="eyebrow">Phoneme scores</p>
                <div class="students__phoneme-list">
                  <div class="students__phoneme-row">
                    <span>Mora timing</span>
                    <span>{{ drilldown.phoneme_breakdown.mora_timing_avg.toFixed(0) }}%</span>
                  </div>
                  <div class="students__phoneme-row">
                    <span>Consonants</span>
                    <span>{{ drilldown.phoneme_breakdown.consonant_avg.toFixed(0) }}%</span>
                  </div>
                  <div class="students__phoneme-row">
                    <span>Vowel purity</span>
                    <span>{{ drilldown.phoneme_breakdown.vowel_avg.toFixed(0) }}%</span>
                  </div>
                </div>
              </div>

              <div class="surface-card surface-card--muted students__subpanel">
                <p class="eyebrow">Recent attempts</p>
                <div class="students__attempts">
                  <div
                    v-for="attempt in drilldown.recent_attempts"
                    :key="attempt.attempt_id"
                    class="students__attempt"
                  >
                    <span>{{ attempt.phrase_id }}</span>
                    <span class="pill-badge" :class="attemptBadgeClass(attempt.accuracy_score)">
                      {{ attempt.accuracy_score.toFixed(0) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </section>
      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useAuthStore } from '@/stores/auth'
import { getAllStudents, getStudentDrillDown } from '@/api/analytics'
import type { StudentDrillDown, StudentStat } from '@/types'

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
  students.value.find((s) => s.uid === selectedStudentUid.value) ?? null,
)

function accuracyBarClass(score: number) {
  if (score >= 85) return 'students__accuracy-fill--excellent'
  if (score >= 70) return 'students__accuracy-fill--good'
  if (score >= 55) return 'students__accuracy-fill--fair'
  return 'students__accuracy-fill--poor'
}

function attemptBadgeClass(score: number) {
  if (score >= 70) return ''
  if (score >= 55) return 'pill-badge--warning'
  return 'pill-badge--danger'
}

function formatModuleId(moduleId: string | null | undefined) {
  if (!moduleId) return 'Not enough data'
  return moduleId.replace('module_', '').replace(/_/g, ' ')
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
  gap: 24px;
}

.students__header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.students__subtitle {
  margin: 12px 0 0;
  color: var(--color-subtext);
  max-width: 760px;
}

.students__search {
  min-width: 280px;
  min-height: 54px;
  padding: 0 16px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  border: 1px solid rgba(189, 203, 194, 0.95);
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--color-subtext);
}

.students__search input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-heading);
}

.students__table-card,
.students__drilldown {
  padding: 24px;
}

.students__table-wrap {
  margin-top: 20px;
}

.students__row {
  cursor: pointer;
}

.students__row--flagged {
  background: rgba(251, 246, 234, 0.7);
}

.students__student-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.students__avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: rgba(46, 138, 103, 0.12);
  color: var(--color-primary-dark);
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.students__name,
.students__drilldown-sub {
  margin: 0;
  font-weight: 700;
  color: var(--color-heading);
}

.students__email {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--color-subtext);
}

.students__accuracy-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
}

.students__accuracy-fill {
  height: 100%;
  border-radius: inherit;
}

.students__accuracy-fill--excellent,
.students__accuracy-fill--good {
  background: linear-gradient(90deg, var(--color-primary), #4ca07e);
}

.students__accuracy-fill--fair {
  background: linear-gradient(90deg, #d4a257, #b87b26);
}

.students__accuracy-fill--poor {
  background: linear-gradient(90deg, #d86a5d, #b9473a);
}

.students__accuracy-value {
  font-weight: 800;
  color: var(--color-heading);
}

.students__drilldown-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.students__close {
  min-width: 44px;
  min-height: 44px;
  border-radius: 999px;
  background: rgba(46, 138, 103, 0.1);
  color: var(--color-primary-dark);
  cursor: pointer;
}

.students__drilldown-grid {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

.students__subpanel {
  padding: 18px;
}

.students__phoneme-list,
.students__attempts {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.students__phoneme-row,
.students__attempt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(255, 253, 249, 0.92);
  color: var(--color-heading);
}

@media (min-width: 1024px) {
  .students__drilldown-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .students__header {
    flex-direction: column;
    align-items: stretch;
  }

  .students__search {
    min-width: 0;
  }
}
</style>

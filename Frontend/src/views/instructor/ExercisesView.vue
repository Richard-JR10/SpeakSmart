<template>
  <InstructorLayout>
    <div class="exercises page-shell">
      <section class="exercises__header">
        <div>
          <p class="eyebrow">Practice assignments</p>
          <h1 class="display-title">Create and track exercises</h1>
          <p class="exercises__subtitle">
            Build curated phrase sets, assign them to students, and review
            completion at a glance.
          </p>
        </div>
        <button type="button" class="button-primary" @click="showForm = true">
          <AppIcon name="plus" :size="16" />
          <span>New exercise</span>
        </button>
      </section>

      <LoadingSpinner v-if="loading" full-screen message="Loading exercises..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>
        <section v-if="exercises.length" class="exercises__list">
          <article
            v-for="exercise in exercises"
            :key="exercise.exercise_id"
            class="surface-card exercises__card"
          >
            <div class="exercises__card-header">
              <div>
                <p class="exercises__card-title">{{ exercise.title }}</p>
                <p class="exercises__card-meta">
                  {{ exercise.phrases.length }} phrases -
                  {{ exercise.assignments.length }} students assigned
                  <span v-if="exercise.due_date">
                    - Due {{ formatDate(exercise.due_date) }}
                  </span>
                </p>
              </div>
              <button
                type="button"
                class="exercises__delete-btn"
                @click="handleDelete(exercise.exercise_id)"
              >
                <AppIcon name="trash" :size="16" />
              </button>
            </div>

            <div class="exercises__completion">
              <div class="progress-track">
                <div
                  class="progress-fill"
                  :style="{ width: completionPercent(exercise) + '%' }"
                />
              </div>
              <span class="exercises__completion-label">
                {{ completedCount(exercise) }}/{{ exercise.assignments.length }} completed
              </span>
            </div>
          </article>
        </section>

        <section v-else class="surface-card empty-block">
          <p>No exercises yet. Create one to assign a guided practice set to students.</p>
        </section>
      </template>

      <div v-if="showForm" class="exercises__modal-overlay" @click.self="showForm = false">
        <div class="exercises__modal surface-card">
          <div class="exercises__modal-header">
            <div>
              <p class="eyebrow">New exercise</p>
              <h2 class="section-title">Build an assignment</h2>
            </div>
            <button type="button" class="exercises__modal-close" @click="showForm = false">
              <AppIcon name="close" :size="18" />
            </button>
          </div>

          <div class="exercises__form">
            <div class="exercises__form-field">
              <label class="exercises__form-label" for="exercise-title">Title</label>
              <input
                id="exercise-title"
                v-model="form.title"
                type="text"
                class="exercises__form-input"
                placeholder="Greetings drill set"
              />
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label">Select phrases</label>
              <div class="exercises__picker">
                <label
                  v-for="module in modulesStore.modules"
                  :key="module.module_id"
                  class="exercises__picker-group"
                >
                  <p class="exercises__picker-title">
                    <AppIcon :name="moduleIconName(module.module_id)" :size="16" />
                    <span>{{ module.title }}</span>
                  </p>
                  <div
                    v-for="phrase in modulesStore.getPhrasesForModule(module.module_id)"
                    :key="phrase.phrase_id"
                    class="exercises__picker-item"
                  >
                    <input
                      type="checkbox"
                      :value="phrase.phrase_id"
                      v-model="form.phrase_ids"
                    />
                    <span>{{ phrase.romaji }} - {{ phrase.english_translation }}</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label" for="exercise-due-date">Due date</label>
              <input
                id="exercise-due-date"
                v-model="form.due_date"
                type="datetime-local"
                class="exercises__form-input"
              />
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label">Assign to students</label>
              <div class="exercises__picker">
                <label
                  v-for="student in students"
                  :key="student.uid"
                  class="exercises__picker-item"
                >
                  <input
                    type="checkbox"
                    :value="student.uid"
                    v-model="form.student_uids"
                  />
                  <span>{{ student.display_name }}</span>
                </label>
              </div>
            </div>

            <ErrorMessage :message="formError" />

            <button
              type="button"
              class="button-primary exercises__submit"
              :disabled="submitting || !form.title || !form.phrase_ids.length || !form.student_uids.length"
              @click="handleCreate"
            >
              <LoadingSpinner v-if="submitting" size="sm" />
              <span v-else>Create and assign</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useAuthStore } from '@/stores/auth'
import { useModulesStore } from '@/stores/modules'
import { getMyExercises, createExercise, deleteExercise } from '@/api/exercises'
import { getAllStudents } from '@/api/analytics'
import { moduleIconName } from '@/constants/modules'
import type { Exercise, StudentStat } from '@/types'

const authStore = useAuthStore()
const modulesStore = useModulesStore()

const exercises = ref<Exercise[]>([])
const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showForm = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)

const form = ref({
  title: '',
  phrase_ids: [] as string[],
  student_uids: [] as string[],
  due_date: '',
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

function completedCount(exercise: Exercise) {
  return exercise.assignments.filter((a) => a.completed_at).length
}

function completionPercent(exercise: Exercise) {
  if (!exercise.assignments.length) return 0
  return (completedCount(exercise) / exercise.assignments.length) * 100
}

async function handleCreate() {
  formError.value = null
  submitting.value = true
  try {
    const exerciseId = `ex_${Date.now()}`
    const created = await createExercise({
      exercise_id: exerciseId,
      title: form.value.title,
      phrase_ids: form.value.phrase_ids,
      student_uids: form.value.student_uids,
      due_date: form.value.due_date || undefined,
    })
    exercises.value.unshift(created)
    showForm.value = false
    form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
  } catch (e: any) {
    formError.value = e.response?.data?.detail ?? 'Failed to create exercise.'
  } finally {
    submitting.value = false
  }
}

async function handleDelete(exerciseId: string) {
  if (!confirm('Delete this exercise and all assignments?')) return
  try {
    await deleteExercise(exerciseId)
    exercises.value = exercises.value.filter((e) => e.exercise_id !== exerciseId)
  } catch {
    error.value = 'Failed to delete exercise.'
  }
}

onMounted(async () => {
  const classId = authStore.profile?.class_id
  loading.value = true
  try {
    await modulesStore.fetchModules()
    for (const module of modulesStore.modules) {
      await modulesStore.fetchPhrases(module.module_id)
    }
    exercises.value = await getMyExercises()
    if (classId) {
      students.value = await getAllStudents(classId)
    }
  } catch {
    error.value = 'Failed to load exercises.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.exercises__header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.exercises__subtitle {
  margin: 12px 0 0;
  color: var(--color-subtext);
  max-width: 760px;
}

.exercises__list {
  display: grid;
  gap: 16px;
}

.exercises__card {
  padding: 22px;
  display: grid;
  gap: 18px;
}

.exercises__card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.exercises__card-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-heading);
}

.exercises__card-meta {
  margin: 8px 0 0;
  color: var(--color-subtext);
}

.exercises__delete-btn,
.exercises__modal-close {
  min-width: 44px;
  min-height: 44px;
  border-radius: 999px;
  background: rgba(198, 85, 73, 0.1);
  color: #8b2f26;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.exercises__completion {
  display: grid;
  gap: 10px;
}

.exercises__completion-label {
  color: var(--color-subtext);
  font-size: 13px;
}

.exercises__modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(23, 35, 29, 0.34);
  display: grid;
  place-items: center;
  z-index: 120;
  padding: 24px;
}

.exercises__modal {
  width: min(100%, 760px);
  max-height: 90dvh;
  overflow: auto;
}

.exercises__modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 0;
}

.exercises__form {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.exercises__form-field {
  display: grid;
  gap: 8px;
}

.exercises__form-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-heading);
}

.exercises__form-input {
  width: 100%;
  min-height: 54px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(189, 203, 194, 0.95);
  background: rgba(255, 253, 249, 0.98);
  color: var(--color-heading);
}

.exercises__picker {
  display: grid;
  gap: 14px;
  max-height: 240px;
  overflow: auto;
  padding: 16px;
  border-radius: 20px;
  background: rgba(240, 244, 238, 0.72);
}

.exercises__picker-group {
  display: grid;
  gap: 10px;
}

.exercises__picker-title {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: var(--color-heading);
}

.exercises__picker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  color: var(--color-text);
}

.exercises__picker-item input {
  accent-color: var(--color-primary);
}

.exercises__submit {
  width: 100%;
}

@media (max-width: 900px) {
  .exercises__header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

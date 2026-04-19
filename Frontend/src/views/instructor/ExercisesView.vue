<!-- src/views/instructor/ExercisesView.vue -->
<template>
  <InstructorLayout>
    <div class="exercises">

      <div class="exercises__header">
        <h1 class="exercises__title">Exercises</h1>
        <button class="exercises__new-btn" @click="showForm = true">
          + New Exercise
        </button>
      </div>

      <LoadingSpinner v-if="loading" full-screen message="Loading exercises..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>

        <!-- Exercise list -->
        <div v-if="exercises.length" class="exercises__list">
          <div
            v-for="exercise in exercises"
            :key="exercise.exercise_id"
            class="exercises__card"
          >
            <div class="exercises__card-header">
              <div>
                <p class="exercises__card-title">{{ exercise.title }}</p>
                <p class="exercises__card-meta">
                  {{ exercise.phrases.length }} phrases ·
                  {{ exercise.assignments.length }} students assigned
                  <span v-if="exercise.due_date">
                    · Due {{ formatDate(exercise.due_date) }}
                  </span>
                </p>
              </div>
              <button
                class="exercises__delete-btn"
                @click="handleDelete(exercise.exercise_id)"
              >
                🗑️
              </button>
            </div>

            <!-- Completion progress -->
            <div class="exercises__completion">
              <div class="exercises__completion-bar-wrap">
                <div
                  class="exercises__completion-bar"
                  :style="{ width: completionPercent(exercise) + '%' }"
                />
              </div>
              <span class="exercises__completion-label">
                {{ completedCount(exercise) }}/{{ exercise.assignments.length }} completed
              </span>
            </div>

          </div>
        </div>

        <div v-else class="exercises__empty">
          <p>No exercises yet — create one to assign practice sets to students.</p>
        </div>

      </template>

      <!-- New exercise form modal -->
      <div v-if="showForm" class="exercises__modal-overlay" @click.self="showForm = false">
        <div class="exercises__modal">

          <div class="exercises__modal-header">
            <h3 class="exercises__modal-title">New Exercise</h3>
            <button class="exercises__modal-close" @click="showForm = false">✕</button>
          </div>

          <div class="exercises__form">

            <div class="exercises__form-field">
              <label class="exercises__form-label">Title</label>
              <input
                v-model="form.title"
                type="text"
                class="exercises__form-input"
                placeholder="e.g. Greetings Drill Set"
              />
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label">Select Phrases</label>
              <div class="exercises__phrase-list">
                <label
                  v-for="module in modulesStore.modules"
                  :key="module.module_id"
                  class="exercises__phrase-group"
                >
                  <p class="exercises__phrase-group-title">
                    {{ moduleIcon(module.module_id) }} {{ module.title }}
                  </p>
                  <div
                    v-for="phrase in modulesStore.getPhrasesForModule(module.module_id)"
                    :key="phrase.phrase_id"
                    class="exercises__phrase-item"
                  >
                    <input
                      type="checkbox"
                      :value="phrase.phrase_id"
                      v-model="form.phrase_ids"
                    />
                    <span>{{ phrase.romaji }} — {{ phrase.english_translation }}</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label">Due Date (optional)</label>
              <input
                v-model="form.due_date"
                type="datetime-local"
                class="exercises__form-input"
              />
            </div>

            <div class="exercises__form-field">
              <label class="exercises__form-label">Assign to Students</label>
              <div class="exercises__student-list">
                <label
                  v-for="student in students"
                  :key="student.uid"
                  class="exercises__student-item"
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
              class="exercises__form-submit"
              :disabled="submitting || !form.title || !form.phrase_ids.length || !form.student_uids.length"
              @click="handleCreate"
            >
              <LoadingSpinner v-if="submitting" size="sm" />
              <span v-else>Create &amp; Assign</span>
            </button>

          </div>
        </div>
      </div>

    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useAuthStore } from '@/stores/auth'
import { useModulesStore } from '@/stores/modules'
import { getMyExercises, createExercise, deleteExercise } from '@/api/exercises'
import { getAllStudents } from '@/api/analytics'
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
.exercises {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.exercises__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.exercises__title {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-text);
}

.exercises__new-btn {
  padding: 10px 20px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.exercises__new-btn:hover {
  background: var(--color-primary-dark);
}

.exercises__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exercises__card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.exercises__card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.exercises__card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.exercises__card-meta {
  font-size: 13px;
  color: var(--color-subtext);
  margin-top: 4px;
}

.exercises__delete-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.exercises__delete-btn:hover {
  opacity: 1;
}

.exercises__completion {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exercises__completion-bar-wrap {
  flex: 1;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.exercises__completion-bar {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.exercises__completion-label {
  font-size: 12px;
  color: var(--color-subtext);
  white-space: nowrap;
}

.exercises__empty {
  padding: 60px 0;
  text-align: center;
  color: var(--color-subtext);
  font-size: 14px;
}

/* Modal */
.exercises__modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}

.exercises__modal {
  background: #ffffff;
  border-radius: var(--radius);
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
}

.exercises__modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  background: #ffffff;
}

.exercises__modal-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
}

.exercises__modal-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-subtext);
}

.exercises__form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exercises__form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
}

.exercises__form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}

.exercises__form-input:focus {
  border-color: var(--color-primary);
}

.exercises__phrase-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 12px;
}

.exercises__phrase-group-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-subtext);
  margin-bottom: 6px;
}

.exercises__phrase-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
  padding: 4px 0;
  cursor: pointer;
}

.exercises__phrase-item input {
  accent-color: var(--color-primary);
}

.exercises__student-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 160px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 12px;
}

.exercises__student-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text);
  cursor: pointer;
}

.exercises__student-item input {
  accent-color: var(--color-primary);
}

.exercises__form-submit {
  width: 100%;
  padding: 16px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s;
}

.exercises__form-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.exercises__form-submit:not(:disabled):hover {
  background: var(--color-primary-dark);
}
</style>
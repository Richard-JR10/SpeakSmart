<!-- src/views/student/LessonsView.vue -->
<template>
  <StudentLayout title="Lessons">

    <div class="lessons">

      <LoadingSpinner v-if="modulesStore.loading" full-screen message="Loading lessons..." />

      <ErrorMessage
        v-else-if="modulesStore.error"
        :message="modulesStore.error"
      />

      <template v-else>
        <p class="lessons__subtitle">
          {{ modulesStore.modules.length }} modules · Tourism Japanese
        </p>

        <div class="lessons__list">
          <div
            v-for="module in modulesStore.modules"
            :key="module.module_id"
            class="lessons__card"
            @click="selectModule(module.module_id)"
          >
            <!-- Module icon + info -->
            <div class="lessons__card-left">
              <div class="lessons__card-icon">
                {{ moduleIcon(module.module_id) }}
              </div>
              <div class="lessons__card-info">
                <p class="lessons__card-title">{{ module.title }}</p>
                <p class="lessons__card-desc">{{ module.description }}</p>
                <p class="lessons__card-meta">
                  {{ phraseCount(module.module_id) }} phrases
                  <span v-if="moduleProgress(module.module_id)">
                    · {{ moduleProgress(module.module_id)?.average_accuracy.toFixed(0) }}% avg
                  </span>
                </p>
              </div>
            </div>

            <!-- Progress indicator -->
            <div class="lessons__card-right">
              <div class="lessons__card-progress">
                <div
                  class="lessons__card-progress-fill"
                  :style="{ width: progressPercent(module.module_id) + '%' }"
                />
              </div>
              <span class="lessons__card-arrow">›</span>
            </div>

          </div>
        </div>
      </template>

    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorMessage from '@/components/shared/ErrorMessage.vue'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const modulesStore = useModulesStore()
const progressStore = useProgressStore()
const authStore = useAuthStore()

const MODULE_ICONS: Record<string, string> = {
  module_greetings:  '👋',
  module_hotel:      '🏨',
  module_directions: '🗺️',
  module_food:       '🍜',
  module_emergency:  '🚨',
  module_tour_guide: '🎌',
}

function moduleIcon(moduleId: string) {
  return MODULE_ICONS[moduleId] ?? '📚'
}

function phraseCount(moduleId: string) {
  return modulesStore.getPhrasesForModule(moduleId).length
}

function moduleProgress(moduleId: string) {
  return progressStore.getProgressForModule(moduleId)
}

function progressPercent(moduleId: string) {
  const progress = moduleProgress(moduleId)
  if (!progress) return 0
  return Math.min(100, progress.average_accuracy)
}

async function selectModule(moduleId: string) {
  await modulesStore.fetchPhrases(moduleId)
  const phrases = modulesStore.getPhrasesForModule(moduleId)
  if (phrases.length > 0) {
    router.push(`/practice/${moduleId}/${phrases[0].phrase_id}`)
  }
}

onMounted(async () => {
  await modulesStore.fetchModules()
  for (const module of modulesStore.modules) {
    await modulesStore.fetchPhrases(module.module_id)
  }
  await progressStore.fetchDashboard(authStore.uid!)
})
</script>

<style scoped>
.lessons {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lessons__subtitle {
  font-size: 13px;
  color: var(--color-subtext);
}

.lessons__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lessons__card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.lessons__card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 12px rgba(29, 158, 117, 0.1);
}

.lessons__card-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.lessons__card-icon {
  width: 48px;
  height: 48px;
  background: var(--color-primary-light);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.lessons__card-info {
  min-width: 0;
}

.lessons__card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.lessons__card-desc {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lessons__card-meta {
  font-size: 12px;
  color: var(--color-primary);
  font-weight: 600;
  margin-top: 6px;
}

.lessons__card-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  padding-left: 12px;
}

.lessons__card-progress {
  width: 60px;
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.lessons__card-progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.lessons__card-arrow {
  font-size: 20px;
  color: var(--color-subtext);
}
</style>
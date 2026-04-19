<!-- src/views/instructor/HeatmapView.vue -->
<template>
  <InstructorLayout>
    <div class="heatmap">

      <div class="heatmap__header">
        <h1 class="heatmap__title">Phoneme Error Heatmap</h1>
        <p class="heatmap__subtitle">
          Color shows class average score per phoneme type per module.
          Red = needs work · Teal = strong
        </p>
      </div>

      <LoadingSpinner v-if="loading" full-screen message="Building heatmap..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>

        <!-- Legend -->
        <div class="heatmap__legend">
          <div class="heatmap__legend-gradient" />
          <div class="heatmap__legend-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
          <div class="heatmap__legend-text">
            <span style="color: #EF4444">Poor</span>
            <span style="color: #F59E0B">Fair</span>
            <span style="color: var(--color-primary)">Excellent</span>
          </div>
        </div>

        <!-- Heatmap grid -->
        <div class="heatmap__card">
          <table class="heatmap__table">
            <thead>
              <tr>
                <th class="heatmap__th-module">Module</th>
                <th v-for="phoneme in phonemeKeys" :key="phoneme">
                  {{ phonemeLabels[phoneme] }}
                </th>
                <th>Overall</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="moduleId in moduleIds" :key="moduleId">
                <td class="heatmap__td-module">
                  <span class="heatmap__module-icon">{{ moduleIcon(moduleId) }}</span>
                  {{ moduleName(moduleId) }}
                </td>
                <td
                  v-for="phoneme in phonemeKeys"
                  :key="phoneme"
                  class="heatmap__cell"
                  :style="{ background: cellColor(heatmapData[moduleId]?.[phoneme] ?? 0) }"
                >
                  <span class="heatmap__cell-value">
                    {{ heatmapData[moduleId]?.[phoneme]?.toFixed(0) ?? '—' }}%
                  </span>
                </td>
                <td
                  class="heatmap__cell heatmap__cell--overall"
                  :style="{ background: cellColor(heatmapData[moduleId]?.overall_avg ?? 0) }"
                >
                  <span class="heatmap__cell-value">
                    {{ heatmapData[moduleId]?.overall_avg?.toFixed(0) ?? '—' }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Top errors summary -->
        <div class="heatmap__card">
          <h3 class="heatmap__card-title">Top Error Areas</h3>
          <div class="heatmap__errors">
            <div
              v-for="item in topErrors"
              :key="item.key"
              class="heatmap__error-item"
            >
              <div class="heatmap__error-left">
                <span class="heatmap__error-icon">{{ moduleIcon(item.moduleId) }}</span>
                <div>
                  <p class="heatmap__error-title">
                    {{ moduleName(item.moduleId) }} — {{ phonemeLabels[item.phoneme] }}
                  </p>
                  <p class="heatmap__error-desc">Class average {{ item.score.toFixed(0) }}%</p>
                </div>
              </div>
              <div
                class="heatmap__error-badge"
                :style="{ background: cellColor(item.score) }"
              >
                {{ item.score.toFixed(0) }}%
              </div>
            </div>
          </div>
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
import { useModulesStore } from '@/stores/modules'
import { getPhonemeHeatmap } from '@/api/analytics'

const authStore = useAuthStore()
const modulesStore = useModulesStore()

const heatmapData = ref<Record<string, any>>({})
const loading = ref(false)
const error = ref<string | null>(null)

const phonemeKeys = ['mora_timing_avg', 'consonant_avg', 'vowel_avg']
const phonemeLabels: Record<string, string> = {
  mora_timing_avg: 'Mora Timing',
  consonant_avg:   'Consonants',
  vowel_avg:       'Vowel Purity',
}

const MODULE_ICONS: Record<string, string> = {
  module_greetings:  '👋',
  module_hotel:      '🏨',
  module_directions: '🗺️',
  module_food:       '🍜',
  module_emergency:  '🚨',
  module_tour_guide: '🎌',
}

const moduleIds = computed(() =>
  modulesStore.modules.map((m) => m.module_id)
)

function moduleIcon(id: string) {
  return MODULE_ICONS[id] ?? '📚'
}

function moduleName(id: string) {
  return modulesStore.getModuleById(id)?.title ?? id
}

// Interpolates color from red → amber → teal based on score
function cellColor(score: number): string {
  if (score === 0) return '#F3F4F6'
  if (score < 55)  return '#fecaca'  // red-200
  if (score < 70)  return '#fde68a'  // amber-200
  if (score < 85)  return '#a7f3d0'  // emerald-200
  return '#6ee7b7'                   // emerald-300
}

const topErrors = computed(() => {
  const items: { key: string; moduleId: string; phoneme: string; score: number }[] = []
  for (const moduleId of moduleIds.value) {
    for (const phoneme of phonemeKeys) {
      const score = heatmapData.value[moduleId]?.[phoneme] ?? 0
      if (score > 0) {
        items.push({ key: `${moduleId}-${phoneme}`, moduleId, phoneme, score })
      }
    }
  }
  return items.sort((a, b) => a.score - b.score).slice(0, 5)
})

onMounted(async () => {
  const classId = authStore.profile?.class_id
  if (!classId) {
    error.value = 'No class assigned to your account.'
    return
  }
  loading.value = true
  try {
    await modulesStore.fetchModules()
    heatmapData.value = await getPhonemeHeatmap(classId)
  } catch {
    error.value = 'Failed to load heatmap data.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.heatmap {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.heatmap__title {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-text);
}

.heatmap__subtitle {
  font-size: 14px;
  color: var(--color-subtext);
  margin-top: 4px;
}

.heatmap__legend {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 280px;
}

.heatmap__legend-gradient {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(to right, #fecaca, #fde68a, #6ee7b7);
}

.heatmap__legend-labels,
.heatmap__legend-text {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-subtext);
}

.heatmap__card {
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.heatmap__card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  padding: 20px 20px 0;
  margin-bottom: 16px;
}

.heatmap__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.heatmap__table thead tr {
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}

.heatmap__table th {
  padding: 12px 16px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-subtext);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.heatmap__th-module {
  text-align: left !important;
  width: 180px;
}

.heatmap__table tbody tr {
  border-bottom: 1px solid var(--color-border);
}

.heatmap__table tbody tr:last-child {
  border-bottom: none;
}

.heatmap__td-module {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
}

.heatmap__module-icon {
  font-size: 18px;
}

.heatmap__cell {
  padding: 14px 16px;
  text-align: center;
  transition: background 0.3s;
}

.heatmap__cell--overall {
  font-weight: 700;
}

.heatmap__cell-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.heatmap__errors {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.heatmap__error-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 8px;
}

.heatmap__error-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.heatmap__error-icon {
  font-size: 20px;
}

.heatmap__error-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.heatmap__error-desc {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.heatmap__error-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}
</style>
<template>
  <InstructorLayout>
    <div class="heatmap page-shell">
      <section class="heatmap__header">
        <p class="eyebrow">Analytics heatmap</p>
        <h1 class="display-title">See where the class struggles most</h1>
        <p class="heatmap__subtitle">
          Compare module performance across phoneme categories to find where
          coaching effort will have the highest impact.
        </p>
      </section>

      <LoadingSpinner v-if="loading" full-screen message="Building heatmap..." />
      <ErrorMessage v-else-if="error" :message="error" />

      <template v-else>
        <section class="surface-card heatmap__legend-card">
          <div class="section-heading">
            <div class="section-heading__text">
              <p class="eyebrow">Legend</p>
              <h2 class="section-title">Color intensity by score</h2>
            </div>
          </div>
          <div class="heatmap__legend">
            <div class="heatmap__legend-gradient" />
            <div class="heatmap__legend-labels">
              <span>Low</span>
              <span>Moderate</span>
              <span>Strong</span>
            </div>
          </div>
        </section>

        <section class="surface-card heatmap__table-card">
          <div class="section-heading">
            <div class="section-heading__text">
              <p class="eyebrow">Module by phoneme</p>
              <h2 class="section-title">Class heatmap</h2>
            </div>
          </div>

          <div class="data-table-wrap heatmap__table-wrap">
            <table class="data-table heatmap__table">
              <thead>
                <tr>
                  <th>Module</th>
                  <th v-for="phoneme in phonemeKeys" :key="phoneme">
                    {{ phonemeLabels[phoneme] }}
                  </th>
                  <th>Overall</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="moduleId in moduleIds" :key="moduleId">
                  <td>
                    <div class="heatmap__module-cell">
                      <span class="heatmap__module-icon">
                        <AppIcon :name="moduleIconName(moduleId)" :size="18" />
                      </span>
                      <span>{{ moduleName(moduleId) }}</span>
                    </div>
                  </td>
                  <td
                    v-for="phoneme in phonemeKeys"
                    :key="phoneme"
                    class="heatmap__cell"
                    :style="{ background: cellColor(heatmapData[moduleId]?.[phoneme] ?? 0) }"
                  >
                    {{ heatmapData[moduleId]?.[phoneme]?.toFixed(0) ?? '--' }}%
                  </td>
                  <td
                    class="heatmap__cell heatmap__cell--overall"
                    :style="{ background: cellColor(heatmapData[moduleId]?.overall_avg ?? 0) }"
                  >
                    {{ heatmapData[moduleId]?.overall_avg?.toFixed(0) ?? '--' }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="surface-card heatmap__errors-card">
          <div class="section-heading">
            <div class="section-heading__text">
              <p class="eyebrow">Lowest performing areas</p>
              <h2 class="section-title">Top error clusters</h2>
            </div>
          </div>

          <div class="heatmap__errors">
            <div
              v-for="item in topErrors"
              :key="item.key"
              class="heatmap__error-item"
            >
              <div class="heatmap__error-left">
                <span class="heatmap__error-icon">
                  <AppIcon :name="moduleIconName(item.moduleId)" :size="18" />
                </span>
                <div>
                  <p class="heatmap__error-title">
                    {{ moduleName(item.moduleId) }} - {{ phonemeLabels[item.phoneme] }}
                  </p>
                  <p class="heatmap__error-desc">Class average {{ item.score.toFixed(0) }}%</p>
                </div>
              </div>
              <span class="pill-badge pill-badge--warning">{{ item.score.toFixed(0) }}%</span>
            </div>
          </div>
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
import { useModulesStore } from '@/stores/modules'
import { getPhonemeHeatmap } from '@/api/analytics'
import { moduleIconName } from '@/constants/modules'

const authStore = useAuthStore()
const modulesStore = useModulesStore()

const heatmapData = ref<Record<string, any>>({})
const loading = ref(false)
const error = ref<string | null>(null)

const phonemeKeys = ['mora_timing_avg', 'consonant_avg', 'vowel_avg']
const phonemeLabels: Record<string, string> = {
  mora_timing_avg: 'Mora timing',
  consonant_avg: 'Consonants',
  vowel_avg: 'Vowel purity',
}

const moduleIds = computed(() =>
  modulesStore.modules.map((m) => m.module_id),
)

function moduleName(id: string) {
  return modulesStore.getModuleById(id)?.title ?? id
}

function cellColor(score: number): string {
  if (score === 0) return 'rgba(240, 244, 238, 0.86)'
  if (score < 55) return 'rgba(198, 85, 73, 0.18)'
  if (score < 70) return 'rgba(184, 123, 38, 0.18)'
  if (score < 85) return 'rgba(46, 138, 103, 0.14)'
  return 'rgba(46, 138, 103, 0.24)'
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
.heatmap__subtitle {
  margin: 12px 0 0;
  color: var(--color-subtext);
  max-width: 760px;
}

.heatmap__legend-card,
.heatmap__table-card,
.heatmap__errors-card {
  padding: 24px;
}

.heatmap__legend {
  margin-top: 20px;
  max-width: 360px;
}

.heatmap__legend-gradient {
  height: 16px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(198, 85, 73, 0.55), rgba(184, 123, 38, 0.55), rgba(46, 138, 103, 0.55));
}

.heatmap__legend-labels {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  color: var(--color-subtext);
  font-size: 12px;
}

.heatmap__table-wrap {
  margin-top: 20px;
}

.heatmap__module-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: var(--color-heading);
}

.heatmap__module-icon,
.heatmap__error-icon {
  width: 36px;
  height: 36px;
  border-radius: 14px;
  background: rgba(46, 138, 103, 0.12);
  color: var(--color-primary-dark);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.heatmap__cell {
  text-align: center;
  font-weight: 700;
  color: var(--color-heading);
}

.heatmap__cell--overall {
  font-weight: 800;
}

.heatmap__errors {
  margin-top: 20px;
  display: grid;
  gap: 12px;
}

.heatmap__error-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  border-radius: var(--radius-sm);
  background: rgba(240, 244, 238, 0.72);
}

.heatmap__error-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.heatmap__error-title {
  margin: 0;
  font-weight: 700;
  color: var(--color-heading);
}

.heatmap__error-desc {
  margin: 4px 0 0;
  color: var(--color-subtext);
}
</style>

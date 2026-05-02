<template>
  <InstructorLayout>
    <div class="flex flex-col gap-4">
      <Card class="border-border/80 bg-card/95 shadow-sm shadow-rose-900/5">
        <CardHeader class="gap-3 p-4 sm:p-5">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Analytics heatmap
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ moduleIds.length }} modules
                </Badge>
              </div>

              <CardTitle class="mt-3 font-(--font-display) text-2xl leading-none text-(--color-heading) sm:text-3xl">
                Pronunciation heatmap
              </CardTitle>
              <CardDescription class="mt-1 max-w-3xl text-sm">
                Scan timing, consonants, vowels, and overall scores across every module.
              </CardDescription>
            </div>

            <div class="w-full rounded-2xl border border-border/70 bg-muted/25 px-4 py-3 lg:max-w-xs">
              <div class="flex items-center justify-between gap-3">
                <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  Score range
                </p>
                <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <span>Low</span>
                  <span class="h-2.5 w-20 rounded-full bg-gradient-to-r from-red-500 via-amber-400 to-emerald-600" />
                  <span>Strong</span>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      <LoadingSpinner
        v-if="loading && !moduleIds.length"
        full-screen
        message="Building heatmap..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Heatmap unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <template v-else>
        <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
          <Card class="gap-0 overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
            <CardHeader class="border-b border-border/70 p-4">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      Module matrix
                    </Badge>
                    <Badge variant="outline" class="rounded-full px-3 py-1">
                      {{ topErrors.length }} weak clusters
                    </Badge>
                  </div>
                  <CardTitle class="mt-2 font-(--font-display) text-xl leading-none text-(--color-heading)">
                    Class heatmap
                  </CardTitle>
                  <CardDescription class="mt-1 text-sm">
                    Compact rows keep all module scores visible for faster comparison.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent class="p-0">
              <template v-if="moduleIds.length">
                <div class="overflow-x-auto">
                  <div class="min-w-[760px]">
                    <div class="grid grid-cols-[minmax(200px,1.4fr)_repeat(4,minmax(118px,0.7fr))] border-b border-border/70 bg-muted/20 px-4 py-2">
                      <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Module
                      </p>
                      <p
                        v-for="label in heatmapColumnLabels"
                        :key="label"
                        class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground"
                      >
                        {{ label }}
                      </p>
                    </div>

                    <div
                      v-for="moduleId in moduleIds"
                      :key="moduleId"
                      class="grid grid-cols-[minmax(200px,1.4fr)_repeat(4,minmax(118px,0.7fr))] items-stretch gap-2 border-b border-border/60 px-4 py-2 last:border-b-0 hover:bg-muted/20"
                    >
                      <div class="flex min-w-0 items-center gap-3 pr-2">
                        <div class="flex size-9 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary">
                          <BookMarked class="size-4" />
                        </div>
                        <div class="min-w-0">
                          <p class="truncate text-sm font-semibold text-(--color-heading)">
                            {{ moduleName(moduleId) }}
                          </p>
                          <p class="truncate text-xs text-muted-foreground">
                            Module performance snapshot
                          </p>
                        </div>
                      </div>

                      <div
                        v-for="item in scoreRows(moduleId)"
                        :key="item.label"
                        class="rounded-xl border px-3 py-2"
                        :class="item.label === 'Overall' ? 'ring-1 ring-primary/15' : ''"
                        :style="cellStyle(item.value)"
                      >
                        <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                          {{ item.label }}
                        </p>
                        <p class="mt-1 font-(--font-display) text-2xl leading-none text-(--color-heading)">
                          {{ item.value.toFixed(0) }}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <div v-else class="p-4">
                <Alert>
                  <ChartNoAxesCombined />
                  <AlertTitle>No heatmap data yet</AlertTitle>
                  <AlertDescription>
                    This class needs more attempt history before module comparisons can be shown.
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>

          <Card class="gap-0 border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
            <CardHeader class="gap-2 border-b border-border/70 p-4">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Lowest performing areas
              </Badge>
              <CardTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
                Top error clusters
              </CardTitle>
              <CardDescription class="text-sm">
                These are the lowest scoring module-category combinations in the active class.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-2 p-4">
              <template v-if="topErrors.length">
                <div
                  v-for="item in topErrors"
                  :key="item.key"
                  class="rounded-xl border border-border/70 bg-muted/25 px-3 py-2.5"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-(--color-heading)">
                        {{ moduleName(item.moduleId) }}
                      </p>
                      <p class="mt-0.5 text-xs text-muted-foreground">
                        {{ phonemeLabels[item.phoneme] }}
                      </p>
                    </div>
                    <Badge variant="destructive" class="rounded-full px-2.5 py-1">
                      {{ item.score.toFixed(0) }}%
                    </Badge>
                  </div>
                </div>
              </template>

              <Alert v-else>
                <ShieldCheck />
                <AlertTitle>No weak clusters detected</AlertTitle>
                <AlertDescription>
                  There is not enough low-score data yet to surface a focused error list.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>
      </template>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  BookMarked,
  ChartNoAxesCombined,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-vue-next'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { getPhonemeHeatmap } from '@/api/analytics'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'

type HeatmapRow = {
  mora_timing_avg: number
  consonant_avg: number
  vowel_avg: number
  overall_avg: number
}

const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const heatmapData = ref<Record<string, HeatmapRow>>({})
const loading = ref(false)
const error = ref<string | null>(null)

const phonemeKeys = ['mora_timing_avg', 'consonant_avg', 'vowel_avg'] as const
const phonemeLabels: Record<(typeof phonemeKeys)[number], string> = {
  mora_timing_avg: 'Mora timing',
  consonant_avg: 'Consonants',
  vowel_avg: 'Vowel purity',
}
const heatmapColumnLabels = ['Timing', 'Consonants', 'Vowels', 'Overall']

const moduleIds = computed(() => modulesStore.modules.map((module) => module.module_id))

const topErrors = computed(() => {
  const items: { key: string; moduleId: string; phoneme: (typeof phonemeKeys)[number]; score: number }[] = []

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

function moduleName(moduleId: string) {
  return modulesStore.getModuleById(moduleId)?.title ?? moduleId
}

function moduleScore(moduleId: string, key: keyof HeatmapRow) {
  return heatmapData.value[moduleId]?.[key] ?? 0
}

function scoreRows(moduleId: string) {
  return [
    { label: 'Timing', value: moduleScore(moduleId, 'mora_timing_avg') },
    { label: 'Consonants', value: moduleScore(moduleId, 'consonant_avg') },
    { label: 'Vowels', value: moduleScore(moduleId, 'vowel_avg') },
    { label: 'Overall', value: moduleScore(moduleId, 'overall_avg') },
  ]
}

function cellStyle(score: number) {
  if (score === 0) {
    return {
      backgroundColor: 'rgba(244, 247, 245, 0.9)',
      borderColor: 'rgba(208, 214, 210, 0.9)',
    }
  }

  if (score < 55) {
    return {
      backgroundColor: 'rgba(198, 85, 73, 0.24)',
      borderColor: 'rgba(198, 85, 73, 0.42)',
    }
  }

  if (score < 70) {
    return {
      backgroundColor: 'rgba(184, 123, 38, 0.26)',
      borderColor: 'rgba(184, 123, 38, 0.44)',
    }
  }

  if (score < 85) {
    return {
      backgroundColor: 'rgba(35, 116, 92, 0.22)',
      borderColor: 'rgba(35, 116, 92, 0.38)',
    }
  }

  return {
    backgroundColor: 'rgba(35, 116, 92, 0.34)',
    borderColor: 'rgba(35, 116, 92, 0.54)',
  }
}

async function loadHeatmap(classId: string | null) {
  heatmapData.value = {}
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load the heatmap.'
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
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
    await modulesStore.fetchModules()
  } catch {
    error.value = 'Failed to load your classes.'
  }
  await loadHeatmap(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadHeatmap(classId)
  },
)
</script>

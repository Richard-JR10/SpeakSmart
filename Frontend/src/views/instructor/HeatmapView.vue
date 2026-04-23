<template>
  <InstructorLayout>
    <div class="flex flex-col gap-5">
      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
              Analytics heatmap
            </Badge>
            <Badge variant="outline" class="rounded-full px-3 py-1">
              {{ moduleIds.length }} modules
            </Badge>
          </div>

          <div class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-end">
            <div class="flex flex-col gap-2">
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading) sm:text-4xl">
                Compare module performance across pronunciation categories
              </CardTitle>
              <CardDescription class="max-w-3xl text-sm leading-7 text-foreground/80 sm:text-base">
                Use the heatmap to see where class averages are strongest, where scores soften, and which modules deserve direct intervention first.
              </CardDescription>
            </div>

            <div class="rounded-3xl border border-border/70 bg-muted/30 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Legend
              </p>
              <div class="mt-3 h-3 rounded-full bg-gradient-to-r from-destructive/60 via-amber-400/55 to-primary/70" />
              <div class="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>Low</span>
                <span>Moderate</span>
                <span>Strong</span>
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
        <div class="grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)]">
          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex flex-col gap-2">
                  <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    Module matrix
                  </Badge>
                  <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    Class heatmap
                  </CardTitle>
                  <CardDescription>
                    Each module is split into timing, consonants, vowels, and overall score so weak clusters are easy to compare.
                  </CardDescription>
                </div>

                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ topErrors.length }} weak clusters
                </Badge>
              </div>
            </CardHeader>

            <CardContent class="grid gap-3">
              <template v-if="moduleIds.length">
                <Card
                  v-for="moduleId in moduleIds"
                  :key="moduleId"
                  class="border-border/70 bg-muted/25 shadow-none"
                >
                  <CardContent class="flex flex-col gap-4 px-4 py-4">
                    <div class="flex flex-wrap items-center justify-between gap-3">
                      <div class="flex min-w-0 items-center gap-3">
                        <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-secondary text-primary">
                          <BookMarked />
                        </div>
                        <div class="min-w-0">
                          <p class="truncate font-semibold text-(--color-heading)">
                            {{ moduleName(moduleId) }}
                          </p>
                          <p class="text-sm text-muted-foreground">
                            Module performance snapshot
                          </p>
                        </div>
                      </div>

                      <Badge :variant="scoreVariant(moduleScore(moduleId, 'overall_avg'))" class="rounded-full px-3 py-1">
                        {{ moduleScore(moduleId, 'overall_avg').toFixed(0) }}% overall
                      </Badge>
                    </div>

                    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                      <div
                        v-for="item in scoreRows(moduleId)"
                        :key="item.label"
                        class="rounded-2xl border border-border/70 p-4"
                        :style="{ backgroundColor: cellColor(item.value) }"
                      >
                        <p class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                          {{ item.label }}
                        </p>
                        <p class="mt-2 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                          {{ item.value.toFixed(0) }}%
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </template>

              <Alert v-else>
                <ChartNoAxesCombined />
                <AlertTitle>No heatmap data yet</AlertTitle>
                <AlertDescription>
                  This class needs more attempt history before module comparisons can be shown.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          <Card class="border-border/80 bg-card/95">
            <CardHeader class="gap-3">
              <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                Lowest performing areas
              </Badge>
              <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Top error clusters
              </CardTitle>
              <CardDescription>
                These are the lowest scoring module-category combinations in the active class.
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-3">
              <template v-if="topErrors.length">
                <div
                  v-for="item in topErrors"
                  :key="item.key"
                  class="rounded-2xl border border-border/70 bg-muted/30 p-4"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="font-semibold text-(--color-heading)">
                        {{ moduleName(item.moduleId) }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
                        {{ phonemeLabels[item.phoneme] }}
                      </p>
                    </div>
                    <Badge variant="destructive" class="rounded-full px-3 py-1">
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

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}

function cellColor(score: number) {
  if (score === 0) return 'rgba(244, 247, 245, 0.85)'
  if (score < 55) return 'rgba(198, 85, 73, 0.10)'
  if (score < 70) return 'rgba(184, 123, 38, 0.12)'
  if (score < 85) return 'rgba(46, 138, 103, 0.09)'
  return 'rgba(46, 138, 103, 0.16)'
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

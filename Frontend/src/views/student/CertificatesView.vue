<template>
  <StudentLayout title="Certificates" show-back>
    <div class="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <LoadingSpinner v-if="progressStore.loading || modulesStore.loading" />

      <template v-else>
        <Card v-if="!completedModules.length" class="border-border/80 bg-card/95">
          <CardContent class="flex flex-col items-center gap-4 p-8 text-center">
            <span class="flex size-12 items-center justify-center rounded-2xl bg-secondary text-primary">
              <Award aria-hidden="true" class="size-6" />
            </span>
            <div class="flex flex-col gap-2">
              <p class="font-semibold text-(--color-heading)">No certificates yet</p>
              <p class="max-w-sm text-sm leading-6 text-muted-foreground">
                Complete all phrases in a module to earn your first certificate.
                A phrase is complete when you submit one accepted recording.
              </p>
            </div>
            <Button variant="outline" @click="router.push('/lessons')">
              <BookOpen data-icon="inline-start" />
              <span>Browse lessons</span>
            </Button>
          </CardContent>
        </Card>

        <template v-else>
          <div class="flex flex-col gap-1">
            <p class="text-sm font-semibold text-(--color-heading)">
              {{ completedModules.length }} module{{ completedModules.length !== 1 ? 's' : '' }} completed
            </p>
            <p class="text-xs text-muted-foreground">
              Download a certificate for each module you have fully completed.
            </p>
          </div>

          <Card
            v-for="summary in completedModules"
            :key="summary.module_id"
            class="border-emerald-200 bg-card/95"
          >
            <CardContent class="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div class="flex items-center gap-3">
                <span class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
                  <Award aria-hidden="true" class="size-5" />
                </span>
                <div class="min-w-0">
                  <p class="truncate font-semibold text-(--color-heading)">
                    {{ modulesStore.getModuleById(summary.module_id)?.title ?? summary.module_id }}
                  </p>
                  <p class="mt-0.5 text-xs text-muted-foreground">
                    {{ summary.completed_phrases }} of {{ summary.total_phrases }} phrases completed
                  </p>
                </div>
              </div>

              <Button
                size="sm"
                class="w-full shrink-0 rounded-xl sm:w-auto"
                :disabled="downloadingModuleId === summary.module_id"
                @click="handleDownload(summary.module_id)"
              >
                <LoaderCircle
                  v-if="downloadingModuleId === summary.module_id"
                  class="animate-spin"
                  data-icon="inline-start"
                />
                <Download v-else data-icon="inline-start" />
                <span>{{ downloadingModuleId === summary.module_id ? 'Preparing...' : 'Download' }}</span>
              </Button>
            </CardContent>
          </Card>
        </template>
      </template>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Award, BookOpen, Download, LoaderCircle } from 'lucide-vue-next'

import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuthStore } from '@/stores/auth'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import { downloadCertificate } from '@/api/certificates'

const router = useRouter()
const authStore = useAuthStore()
const progressStore = useProgressStore()
const modulesStore = useModulesStore()

const downloadingModuleId = ref<string | null>(null)

const completedModules = computed(() =>
  (progressStore.dashboard?.progress_by_module ?? []).filter(
    (s) => s.total_phrases > 0 && s.completed_phrases === s.total_phrases,
  ),
)

async function handleDownload(moduleId: string) {
  if (!authStore.uid) return
  downloadingModuleId.value = moduleId
  try {
    await downloadCertificate(authStore.uid, moduleId)
  } catch (e) {
    console.error('Certificate download failed:', e)
  } finally {
    downloadingModuleId.value = null
  }
}

onMounted(async () => {
  const uid = authStore.uid!
  await Promise.all([
    modulesStore.fetchModules(),
    progressStore.dashboard ? Promise.resolve() : progressStore.fetchDashboard(uid),
  ])
})
</script>

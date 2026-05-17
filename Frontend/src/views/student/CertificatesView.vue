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
              View or download a certificate for each module you have fully completed.
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

              <div class="flex w-full gap-2 sm:w-auto">
                <Button
                  variant="outline"
                  size="sm"
                  class="flex-1 rounded-xl sm:flex-none"
                  :disabled="viewingModuleId === summary.module_id || downloadingModuleId === summary.module_id"
                  @click="handleView(summary.module_id)"
                >
                  <LoaderCircle
                    v-if="viewingModuleId === summary.module_id"
                    class="animate-spin"
                    data-icon="inline-start"
                  />
                  <Eye v-else data-icon="inline-start" />
                  <span>{{ viewingModuleId === summary.module_id ? 'Rendering...' : 'View' }}</span>
                </Button>

                <Button
                  size="sm"
                  class="flex-1 rounded-xl sm:flex-none"
                  :disabled="downloadingModuleId === summary.module_id || viewingModuleId === summary.module_id"
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
              </div>
            </CardContent>
          </Card>
        </template>
      </template>
    </div>

    <!-- Certificate preview modal -->
    <DialogRoot :open="previewOpen" @update:open="closePreview">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogContent class="fixed top-1/2 left-1/2 z-50 flex max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-3xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border bg-background shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div class="flex shrink-0 items-center justify-between gap-3 border-b px-5 py-4">
            <div class="flex items-center gap-3">
              <span class="flex size-9 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                <Award class="size-4" />
              </span>
              <div>
                <DialogTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
                  {{ previewTitle }}
                </DialogTitle>
                <DialogDescription class="mt-0.5 text-xs text-muted-foreground">
                  Certificate of Completion
                </DialogDescription>
              </div>
            </div>
            <Button variant="outline" size="icon" class="shrink-0 rounded-xl" @click="closePreview(false)">
              <X />
              <span class="sr-only">Close</span>
            </Button>
          </div>

          <div class="flex-1 overflow-auto bg-muted/30 p-4">
            <img
              v-if="previewImageUrl"
              :src="previewImageUrl"
              alt="Certificate preview"
              class="mx-auto w-full rounded-xl shadow-md"
            />
          </div>

          <div class="flex shrink-0 justify-end gap-2 border-t px-5 py-3">
            <Button
              size="sm"
              class="rounded-xl"
              :disabled="downloadingModuleId === previewModuleId"
              @click="handleDownload(previewModuleId!)"
            >
              <LoaderCircle v-if="downloadingModuleId === previewModuleId" class="animate-spin" data-icon="inline-start" />
              <Download v-else data-icon="inline-start" />
              <span>{{ downloadingModuleId === previewModuleId ? 'Preparing...' : 'Download' }}</span>
            </Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Award, BookOpen, Download, Eye, LoaderCircle, X } from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'
import * as pdfjsLib from 'pdfjs-dist'

import StudentLayout from '@/layouts/StudentLayout.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuthStore } from '@/stores/auth'
import { useModulesStore } from '@/stores/modules'
import { useProgressStore } from '@/stores/progress'
import { downloadCertificate, fetchCertificateBlob } from '@/api/certificates'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).href

const router = useRouter()
const authStore = useAuthStore()
const progressStore = useProgressStore()
const modulesStore = useModulesStore()

const downloadingModuleId = ref<string | null>(null)
const viewingModuleId = ref<string | null>(null)
const previewOpen = ref(false)
const previewModuleId = ref<string | null>(null)
const previewTitle = ref('')
const previewImageUrl = ref<string | null>(null)

const completedModules = computed(() =>
  (progressStore.dashboard?.progress_by_module ?? []).filter(
    (s) => s.total_phrases > 0 && s.completed_phrases === s.total_phrases,
  ),
)

function closePreview(_open: boolean) {
  previewOpen.value = false
  previewImageUrl.value = null
  previewModuleId.value = null
  previewTitle.value = ''
}

async function renderPdfToImage(blob: Blob): Promise<string> {
  const arrayBuffer = await blob.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise
  const page = await pdf.getPage(1)
  const viewport = page.getViewport({ scale: 2.5 })
  const canvas = document.createElement('canvas')
  canvas.width = viewport.width
  canvas.height = viewport.height
  const ctx = canvas.getContext('2d')!
  await page.render({ canvasContext: ctx, canvas, viewport }).promise
  return canvas.toDataURL('image/png')
}

async function handleView(moduleId: string) {
  if (!authStore.uid) return
  viewingModuleId.value = moduleId
  try {
    const blob = await fetchCertificateBlob(authStore.uid, moduleId)
    const imageUrl = await renderPdfToImage(blob)
    previewImageUrl.value = imageUrl
    previewModuleId.value = moduleId
    previewTitle.value = modulesStore.getModuleById(moduleId)?.title ?? moduleId
    previewOpen.value = true
  } catch (e) {
    console.error('Certificate view failed:', e)
  } finally {
    viewingModuleId.value = null
  }
}

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

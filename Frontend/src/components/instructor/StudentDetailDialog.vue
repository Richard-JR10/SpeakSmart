<template>
  <DialogRoot :open="open" @update:open="$emit('update:open', $event)">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-rose-950/25 backdrop-blur-sm" />
      <DialogContent class="fixed top-1/2 left-1/2 z-50 flex max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-5xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border border-rose-200 bg-linear-to-br from-background via-card to-rose-50 shadow-lg shadow-rose-950/15 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">

        <div class="flex items-start justify-between gap-3 p-5 sm:p-6">
          <div class="min-w-0">
            <Badge class="w-fit rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary uppercase tracking-[0.18em] hover:bg-primary/10">
              Learner detail
            </Badge>

            <template v-if="student">
              <DialogTitle class="mt-3 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                {{ student.display_name }}
              </DialogTitle>
              <DialogDescription class="mt-1 text-sm text-muted-foreground">
                {{ student.email }}
              </DialogDescription>
            </template>

            <template v-else>
              <DialogTitle class="mt-3 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                Learner detail
              </DialogTitle>
              <DialogDescription class="mt-1 text-sm text-muted-foreground">
                Loading selected learner.
              </DialogDescription>
            </template>
          </div>

          <Button variant="outline" size="icon" class="rounded-xl shrink-0" @click="$emit('update:open', false)">
            <X />
            <span class="sr-only">Close</span>
          </Button>
        </div>

        <div class="flex flex-col gap-4 flex-1 overflow-y-auto px-5 pb-5 sm:px-6 sm:pb-6">
          <LoadingSpinner v-if="loading" size="sm" />

          <template v-else-if="student && drilldown">
            <div class="grid gap-3 sm:grid-cols-3">
              <div class="rounded-2xl border border-emerald-200 bg-emerald-50/70 px-4 py-3">
                <p class="text-[11px] font-semibold text-emerald-800/70 uppercase tracking-[0.16em]">
                  Average
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ drilldown.overall_average.toFixed(1) }}%
                </p>
              </div>

              <div class="rounded-2xl border border-sky-200 bg-sky-50/70 px-4 py-3">
                <p class="text-[11px] font-semibold text-sky-800/70 uppercase tracking-[0.16em]">
                  Attempts
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ drilldown.total_attempts }}
                </p>
              </div>

              <div class="rounded-2xl border border-amber-200 bg-amber-50/70 px-4 py-3">
                <p class="text-[11px] font-semibold text-amber-800/70 uppercase tracking-[0.16em]">
                  Streak
                </p>
                <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  {{ drilldown.streak_days }}
                </p>
              </div>
            </div>

            <Separator />

            <div class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <p class="font-semibold text-(--color-heading)">Weakest module</p>
                <Badge :variant="student.is_flagged ? 'destructive' : 'outline'" class="rounded-full px-3 py-1">
                  {{ formatModuleId(drilldown.weakest_module_id) }}
                </Badge>
              </div>

              <div class="grid gap-3 md:grid-cols-3">
                <div
                  v-for="item in phonemeRows"
                  :key="item.label"
                  class="rounded-2xl border border-rose-200/80 bg-white/75 p-3"
                >
                  <div class="flex items-center justify-between gap-3">
                    <p class="font-semibold text-(--color-heading)">{{ item.label }}</p>
                    <Badge :variant="scoreVariant(item.value)" class="rounded-full px-3 py-1">
                      {{ item.value.toFixed(0) }}%
                    </Badge>
                  </div>
                  <div class="mt-3 h-2 overflow-hidden rounded-full bg-rose-100">
                    <div
                      class="h-full rounded-full bg-primary"
                      :style="{ width: `${item.value}%` }"
                    />
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            <div class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <p class="font-semibold text-(--color-heading)">Recent attempts</p>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ drilldown.recent_attempts.length }} shown
                </Badge>
              </div>

              <template v-if="drilldown.recent_attempts.length">
                <div
                  v-for="attempt in drilldown.recent_attempts"
                  :key="attempt.attempt_id"
                  class="rounded-2xl border border-rose-200/80 bg-white/75 p-3"
                >
                  <div class="flex flex-wrap items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="font-semibold text-(--color-heading)">
                        {{ attempt.phrase_id }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">
                        {{ formatAttemptDate(attempt.attempted_at) }}
                      </p>
                    </div>

                    <Badge :variant="scoreVariant(attempt.accuracy_score)" class="rounded-full px-3 py-1">
                      {{ attempt.accuracy_score.toFixed(0) }}%
                    </Badge>
                  </div>

                  <p v-if="attempt.feedback_text" class="mt-3 text-sm leading-6 text-muted-foreground">
                    {{ attempt.feedback_text }}
                  </p>
                </div>
              </template>

              <Alert v-else>
                <Clock3 />
                <AlertTitle>No recent attempts</AlertTitle>
                <AlertDescription>
                  This learner has not recorded any recent speaking attempts for the selected class.
                </AlertDescription>
              </Alert>
            </div>
          </template>

          <Alert v-else>
            <UserRoundSearch />
            <AlertTitle>No learner selected</AlertTitle>
            <AlertDescription>
              Pick a student from the class to open their progress summary here.
            </AlertDescription>
          </Alert>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Clock3, UserRoundSearch, X } from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import type { StudentDrillDown, StudentStat } from '@/types'

const props = defineProps<{
  open: boolean
  student: StudentStat | null
  drilldown: StudentDrillDown | null
  loading: boolean
}>()

defineEmits<{
  'update:open': [value: boolean]
}>()

const phonemeRows = computed(() => {
  if (!props.drilldown) return []
  return [
    { label: 'Mora timing', value: props.drilldown.phoneme_breakdown.mora_timing_avg },
    { label: 'Consonants', value: props.drilldown.phoneme_breakdown.consonant_avg },
    { label: 'Vowel purity', value: props.drilldown.phoneme_breakdown.vowel_avg },
  ]
})

function formatModuleId(moduleId: string | null | undefined) {
  if (!moduleId) return 'Not enough data'
  return moduleId.replace('module_', '').replace(/_/g, ' ')
}

function formatAttemptDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function scoreVariant(score: number): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (score >= 85) return 'default'
  if (score >= 70) return 'secondary'
  if (score >= 55) return 'outline'
  return 'destructive'
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { ChevronDown, LoaderCircle, Send, TriangleAlert, X } from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import {
  assignmentDraftOverall,
  assignmentGroupStatus,
  assignmentSuggestedOverall,
  gradeableSubmissions,
  phraseDisplayLabel,
  type AssignmentPhraseReviewDraft,
  type AssignmentReviewGroup,
  type AssignmentReviewStatus,
} from './assignmentReview'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const props = defineProps<{
  open: boolean
  assignmentTitle: string | null
  group: AssignmentReviewGroup | null
  drafts: Record<string, AssignmentPhraseReviewDraft>
  saving: boolean
  error: string | null
  saveProgress: string | null
}>()

const emit = defineEmits<{
  'update:open': [open: boolean]
  updateDraft: [
    submissionId: string,
    field: keyof AssignmentPhraseReviewDraft,
    value: string,
  ]
  submit: []
}>()

const canSubmit = computed(() => {
  if (!props.group) return false
  if (props.saving) return false
  return props.group.submittedCount > 0 && props.group.submittedCount === props.group.requiredCount
})

function statusLabel(status: AssignmentReviewStatus) {
  if (status === 'ready') return 'Ready to grade'
  if (status === 'partial') return 'Partially graded'
  if (status === 'graded') return 'Graded'
  return 'Incomplete'
}

function statusVariant(status: AssignmentReviewStatus): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (status === 'graded') return 'default'
  if (status === 'ready') return 'destructive'
  if (status === 'partial') return 'secondary'
  return 'outline'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function draftFor(submissionId: string): AssignmentPhraseReviewDraft {
  return props.drafts[submissionId] ?? {
    teacher_accuracy_score: '',
    teacher_feedback_text: '',
  }
}

function onScoreInput(submissionId: string, value: string | number) {
  emit('updateDraft', submissionId, 'teacher_accuracy_score', String(value))
}

function onFeedbackInput(submissionId: string, event: Event) {
  emit(
    'updateDraft',
    submissionId,
    'teacher_feedback_text',
    (event.target as HTMLTextAreaElement).value,
  )
}
</script>

<template>
  <DialogRoot :open="open" @update:open="emit('update:open', $event)">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
      <DialogContent
        class="fixed top-1/2 left-1/2 z-50 flex max-h-[92dvh] w-[calc(100%-2rem)] max-w-5xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-3xl border border-border/80 bg-card shadow-lg"
      >
        <div class="flex items-start justify-between gap-3 border-b border-border/70 px-5 py-4">
          <div class="min-w-0">
            <Badge
              v-if="group"
              :variant="statusVariant(assignmentGroupStatus(group))"
              class="w-fit rounded-full px-3 py-1"
            >
              {{ statusLabel(assignmentGroupStatus(group)) }}
            </Badge>
            <DialogTitle class="mt-2 font-(--font-display) text-2xl leading-none text-(--color-heading)">
              {{ group?.studentDisplayName ?? 'Review student assignment' }}
            </DialogTitle>
            <DialogDescription v-if="group" class="mt-1 text-sm text-muted-foreground">
              {{ assignmentTitle ?? 'Selected assignment' }} - {{ group.submittedCount }}/{{ group.requiredCount }} phrases submitted
            </DialogDescription>
          </div>

          <Button variant="outline" size="icon" class="rounded-xl" @click="emit('update:open', false)">
            <X />
            <span class="sr-only">Close grade modal</span>
          </Button>
        </div>

        <div v-if="group" class="flex-1 overflow-y-auto px-5 py-4">
          <div class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
              <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Suggested overall
              </p>
              <p class="mt-2 font-(--font-display) text-4xl leading-none text-(--color-heading)">
                {{ assignmentSuggestedOverall(group) == null ? '-' : `${assignmentSuggestedOverall(group)}%` }}
              </p>
            </div>
            <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
              <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Teacher overall
              </p>
              <p class="mt-2 font-(--font-display) text-4xl leading-none text-(--color-heading)">
                {{ assignmentDraftOverall(group, drafts) == null ? '-' : `${assignmentDraftOverall(group, drafts)}%` }}
              </p>
            </div>
            <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
              <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Submitted
              </p>
              <p class="mt-2 font-(--font-display) text-4xl leading-none text-(--color-heading)">
                {{ group.submittedCount }}/{{ group.requiredCount }}
              </p>
            </div>
          </div>

          <Alert v-if="group.submittedCount < group.requiredCount" class="mt-4">
            <TriangleAlert />
            <AlertTitle>Assignment is not complete yet</AlertTitle>
            <AlertDescription>
              The student still needs to submit every required phrase before you can submit all grades.
            </AlertDescription>
          </Alert>

          <Alert v-if="error" class="mt-4" variant="destructive">
            <TriangleAlert />
            <AlertTitle>Grade update failed</AlertTitle>
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>

          <div class="mt-4 flex flex-col gap-3">
            <details
              v-for="phrase in group.phrases"
              :key="phrase.phraseId"
              class="group overflow-hidden rounded-2xl border border-border/70 bg-background/80"
            >
              <summary class="flex cursor-pointer list-none flex-col gap-2 px-4 py-3 transition hover:bg-muted/30 sm:flex-row sm:items-center sm:justify-between">
                <div class="flex min-w-0 items-start gap-3">
                  <span class="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full border border-border bg-muted/35 text-muted-foreground transition group-open:rotate-180 group-open:border-primary/30 group-open:bg-secondary group-open:text-primary">
                    <ChevronDown class="size-4" />
                  </span>
                  <div class="min-w-0">
                  <p class="truncate font-semibold text-(--color-heading)">
                    {{ phraseDisplayLabel(phrase) }}
                  </p>
                  <p v-if="phrase.phrase" class="truncate text-sm text-muted-foreground">
                    {{ phrase.phrase.english_translation }}
                  </p>
                  </div>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                  <Badge v-if="phrase.submission" variant="outline" class="rounded-full px-2.5 py-1">
                    {{ phrase.submission.suggested_accuracy_score.toFixed(0) }}%
                  </Badge>
                  <Badge v-if="phrase.submission?.released_at" variant="default" class="rounded-full px-2.5 py-1">
                    Released
                  </Badge>
                  <Badge v-else-if="phrase.submission" variant="destructive" class="rounded-full px-2.5 py-1">
                    Pending
                  </Badge>
                  <Badge v-else variant="outline" class="rounded-full px-2.5 py-1">
                    Missing
                  </Badge>
                </div>
              </summary>

              <div class="border-t border-border/70 bg-muted/10 px-4 py-4">
                <div v-if="phrase.submission" class="grid gap-4 xl:grid-cols-[minmax(280px,0.9fr)_minmax(360px,1.1fr)]">
                  <div class="flex min-w-0 flex-col gap-3">
                    <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                      <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                            System suggestion
                          </p>
                          <p class="mt-2 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                            {{ phrase.submission.suggested_accuracy_score.toFixed(0) }}%
                          </p>
                        </div>
                        <div class="grid grid-cols-3 gap-2 text-center text-xs text-muted-foreground sm:min-w-56">
                          <div class="rounded-xl border border-border/70 bg-background/70 px-2 py-2">
                            <p class="font-semibold tabular-nums text-(--color-heading)">
                              {{ phrase.submission.suggested_mora_timing_score.toFixed(0) }}%
                            </p>
                            <p>Mora</p>
                          </div>
                          <div class="rounded-xl border border-border/70 bg-background/70 px-2 py-2">
                            <p class="font-semibold tabular-nums text-(--color-heading)">
                              {{ phrase.submission.suggested_consonant_score.toFixed(0) }}%
                            </p>
                            <p>Consonants</p>
                          </div>
                          <div class="rounded-xl border border-border/70 bg-background/70 px-2 py-2">
                            <p class="font-semibold tabular-nums text-(--color-heading)">
                              {{ phrase.submission.suggested_vowel_score.toFixed(0) }}%
                            </p>
                            <p>Vowels</p>
                          </div>
                        </div>
                      </div>
                      <div class="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
                        <span>Verification: {{ phrase.submission.verification_status.replaceAll('_', ' ') }}</span>
                        <span v-if="phrase.submission.submitted_at">Submitted {{ formatDate(phrase.submission.submitted_at) }}</span>
                      </div>
                    </div>

                    <audio
                      class="w-full"
                      :src="phrase.submission.audio_file_url"
                      controls
                      preload="metadata"
                    />
                  </div>

                  <div class="grid min-w-0 gap-4 rounded-2xl border border-border/70 bg-background/70 p-4 lg:grid-cols-[160px_minmax(0,1fr)]">
                    <div class="flex flex-col gap-2 lg:sticky lg:top-0 lg:self-start">
                      <Label :for="`score-${phrase.submission.submission_id}`">Teacher score</Label>
                      <Input
                        :id="`score-${phrase.submission.submission_id}`"
                        :model-value="draftFor(phrase.submission.submission_id).teacher_accuracy_score"
                        type="number"
                        min="0"
                        max="100"
                        @update:model-value="onScoreInput(phrase.submission.submission_id, $event)"
                      />
                    </div>

                    <div class="flex min-w-0 flex-col gap-2">
                      <Label :for="`feedback-${phrase.submission.submission_id}`">Teacher feedback</Label>
                      <textarea
                        :id="`feedback-${phrase.submission.submission_id}`"
                        :value="draftFor(phrase.submission.submission_id).teacher_feedback_text"
                        rows="9"
                        class="min-h-56 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm leading-6 text-foreground shadow-xs outline-none transition focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
                        @input="onFeedbackInput(phrase.submission.submission_id, $event)"
                      />
                    </div>
                  </div>
                </div>

                <Alert v-else>
                  <TriangleAlert />
                  <AlertTitle>No submission yet</AlertTitle>
                  <AlertDescription>
                    This required phrase will become gradeable after the student submits a recording.
                  </AlertDescription>
                </Alert>
              </div>
            </details>
          </div>
        </div>

        <div v-if="group" class="border-t border-border/70 px-5 py-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p class="text-sm text-muted-foreground">
              {{ saveProgress ?? `${gradeableSubmissions(group).length} phrase grades will be released to the student.` }}
            </p>
            <Button :disabled="!canSubmit" @click="emit('submit')">
              <LoaderCircle v-if="saving" class="animate-spin" data-icon="inline-start" />
              <Send v-else data-icon="inline-start" />
              <span>{{ saving ? 'Submitting grades...' : 'Submit all grades' }}</span>
            </Button>
          </div>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

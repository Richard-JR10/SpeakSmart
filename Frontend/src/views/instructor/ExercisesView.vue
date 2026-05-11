<template>
  <InstructorLayout>
    <div class="flex flex-col gap-4">
      <Card class="border-border/80 bg-card/95 shadow-sm shadow-rose-900/5">
        <CardHeader class="gap-3 p-4 sm:p-5">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                  Practice assignments
                </Badge>
                <Badge variant="outline" class="rounded-full px-3 py-1">
                  {{ exercises.length }} total
                </Badge>
              </div>
              <CardTitle class="mt-3 font-(--font-display) text-2xl leading-none text-(--color-heading) sm:text-3xl">
                Assignment grading queue
              </CardTitle>
              <CardDescription class="mt-1 max-w-3xl text-sm">
                Scan assignment progress, open one assignment queue, and grade submissions without filling the page with audio players.
              </CardDescription>
            </div>

            <Button @click="showForm = true">
              <Plus data-icon="inline-start" />
              <span>New assignment</span>
            </Button>
          </div>

          <div class="grid overflow-hidden rounded-2xl border border-border/70 bg-muted/20 md:grid-cols-4">
            <div
              v-for="item in summaryCards"
              :key="item.label"
              class="flex items-center justify-between gap-3 border-b border-border/70 px-4 py-3 last:border-b-0 md:border-r md:border-b-0 md:last:border-r-0"
            >
              <div class="min-w-0">
                <p class="truncate text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                  {{ item.label }}
                </p>
                <p class="mt-1 font-(--font-display) text-2xl leading-none text-(--color-heading)">
                  {{ item.value }}
                </p>
              </div>
              <component :is="item.icon" class="size-5 shrink-0 text-muted-foreground" />
            </div>
          </div>
        </CardHeader>
      </Card>

      <LoadingSpinner
        v-if="loading && !exercises.length"
        full-screen
        message="Loading assignments..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Assignments unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Alert v-else-if="!exercises.length">
        <ClipboardList />
        <AlertTitle>No assignments yet</AlertTitle>
        <AlertDescription>
          Create your first assignment to send phrase work to the active class and review submissions here.
        </AlertDescription>
      </Alert>

      <template v-else>
        <div class="grid gap-4 xl:grid-cols-[22rem_minmax(0,1fr)]">
          <AssignmentSetNavigator
            v-model:search="assignmentSearch"
            v-model:filter="assignmentFilter"
            :items="sortedAssignmentItems"
            :selected-exercise-id="selectedExerciseId"
            :filter-options="assignmentFilterOptions"
            @select-assignment="selectExercise"
            @delete-assignment="handleDelete"
          />

          <Card class="gap-0 overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
          <CardHeader class="border-b border-border/70 p-4">
            <div class="flex flex-col gap-4">
              <div class="flex flex-col gap-3 2xl:flex-row 2xl:items-end 2xl:justify-between">
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                      Student review queue
                    </Badge>
                    <Badge variant="outline" class="rounded-full px-3 py-1">
                      {{ filteredReviewGroups.length }} visible
                    </Badge>
                    <Badge
                      v-if="selectedAssignmentItem"
                      variant="outline"
                      class="rounded-full px-3 py-1"
                      :class="assignmentStatusTone(selectedAssignmentItem.status)"
                    >
                      {{ assignmentStatusLabel(selectedAssignmentItem.status) }}
                    </Badge>
                  </div>
                  <CardTitle class="mt-2 font-(--font-display) text-xl leading-none text-(--color-heading)">
                    {{ selectedExercise?.title ?? 'Select an assignment' }}
                  </CardTitle>
                </div>

                <div class="grid w-full grid-cols-[minmax(0,1fr)_2.5rem] items-center gap-2 md:max-w-84 2xl:w-auto">
                  <div class="flex h-10 min-w-0 items-center gap-2 rounded-xl border border-border bg-background px-3">
                    <Search class="size-4 text-muted-foreground" />
                    <Input
                      v-model="submissionSearch"
                      class="h-8 rounded-none border-0 bg-transparent px-0 text-sm shadow-none ring-0 outline-none focus-visible:!border-transparent focus-visible:!shadow-none focus-visible:!ring-0 focus-visible:!ring-offset-0 focus-visible:!outline-none"
                      placeholder="Search student"
                    />
                  </div>

                  <SelectRoot
                    :model-value="submissionFilter"
                    @update:model-value="handleSubmissionFilterUpdate"
                  >
                    <SelectTrigger
                      aria-label="Filter student review queue"
                      class="inline-flex size-10 items-center justify-center rounded-xl border border-primary/35 bg-secondary text-primary shadow-sm shadow-primary/10 outline-none ring-1 ring-primary/10 transition hover:border-primary/60 hover:bg-primary/10 focus-visible:ring-2 focus-visible:ring-primary/30 disabled:cursor-not-allowed disabled:opacity-60 data-[state=open]:border-primary/70 data-[state=open]:bg-secondary data-[state=open]:text-primary data-[state=open]:ring-primary/25"
                    >
                      <Funnel class="size-4 shrink-0" />
                    </SelectTrigger>

                    <SelectPortal>
                      <SelectContent
                        position="popper"
                        side="bottom"
                        align="end"
                        :side-offset="8"
                        :align-offset="0"
                        :collision-padding="12"
                        class="z-50 min-w-56 overflow-hidden rounded-xl border bg-popover text-popover-foreground shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
                      >
                        <SelectViewport class="p-1">
                          <SelectItem
                            v-for="option in submissionFilterOptions"
                            :key="option.value"
                            :value="option.value"
                            class="group relative flex cursor-default select-none items-center rounded-lg py-2 pr-9 pl-3 text-sm outline-none transition-colors focus-visible:outline-none! focus-visible:ring-0! focus-visible:ring-offset-0! data-[highlighted]:bg-muted data-[highlighted]:outline-none data-[highlighted]:ring-0 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                          >
                            <SelectItemText>
                              <span class="flex min-w-0 items-center gap-2">
                                <span class="truncate">{{ option.label }}</span>
                                <span class="rounded-full border border-primary/20 bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold leading-none tabular-nums text-primary group-data-[state=checked]:border-primary-foreground/35 group-data-[state=checked]:bg-primary-foreground/20 group-data-[state=checked]:text-primary-foreground">
                                  {{ option.count }}
                                </span>
                              </span>
                            </SelectItemText>
                            <SelectItemIndicator class="absolute right-2 flex size-4 items-center justify-center">
                              <Check class="size-4" />
                            </SelectItemIndicator>
                          </SelectItem>
                        </SelectViewport>
                      </SelectContent>
                    </SelectPortal>
                  </SelectRoot>
                </div>
              </div>

              <div
                v-if="selectedAssignmentItem"
                class="grid gap-2 rounded-2xl border border-border/70 bg-muted/20 p-2 sm:grid-cols-2 xl:grid-cols-5"
              >
                <div
                  v-for="item in selectedAssignmentSummaryCards"
                  :key="item.label"
                  class="flex min-w-0 items-center gap-3 rounded-xl bg-background/60 px-3 py-2.5"
                >
                  <div
                    class="flex size-9 shrink-0 items-center justify-center rounded-xl"
                    :class="item.tone"
                  >
                    <component :is="item.icon" class="size-4" />
                  </div>
                  <div class="min-w-0">
                    <p class="truncate text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                      {{ item.label }}
                    </p>
                    <p class="truncate text-sm font-semibold tabular-nums text-(--color-heading)">
                      {{ item.value }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardHeader>

          <CardContent class="p-0">
            <LoadingSpinner v-if="selectedExerciseId && submissionsLoading[selectedExerciseId]" size="sm" />

            <div v-else-if="selectedExerciseId && submissionErrors[selectedExerciseId]" class="p-4">
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Submission grades unavailable</AlertTitle>
                <AlertDescription>{{ submissionErrors[selectedExerciseId] }}</AlertDescription>
              </Alert>
            </div>

            <template v-else-if="selectedExercise">
              <template v-if="paginatedReviewGroups.length">
                <div
                  v-if="bulkGradeableGroups.length || bulkReviewError"
                  class="flex flex-col gap-3 border-b border-border/70 bg-muted/15 px-4 py-3 lg:flex-row lg:items-center lg:justify-between"
                >
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-(--color-heading)">
                      Bulk suggested grades
                    </p>
                    <p class="text-xs text-muted-foreground">
                      {{ selectedBulkReviewGroups.length }} selected - {{ selectedBulkPhraseCount }} phrase grades to release
                    </p>
                    <p v-if="bulkReviewProgress" class="mt-1 text-xs font-medium text-primary">
                      {{ bulkReviewProgress }}
                    </p>
                    <p v-if="bulkReviewError" class="mt-1 text-xs font-medium text-destructive">
                      {{ bulkReviewError }}
                    </p>
                  </div>

                  <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      :disabled="bulkReviewSaving || !selectedBulkReviewKeys.length"
                      @click="clearBulkReviewSelection"
                    >
                      Clear selection
                    </Button>
                    <Button
                      size="sm"
                      :disabled="bulkReviewSaving || !selectedBulkReviewGroups.length"
                      @click="openBulkReviewConfirm"
                    >
                      <LoaderCircle v-if="bulkReviewSaving" class="animate-spin" data-icon="inline-start" />
                      <span>{{ bulkReviewSaving ? 'Submitting...' : 'Submit grades' }}</span>
                    </Button>
                  </div>
                </div>

                <AssignmentStudentQueueTable
                  :groups="paginatedReviewGroups"
                  :selected-keys="selectedBulkReviewKeys"
                  :selectable-keys="bulkGradeableKeys"
                  :bulk-disabled="bulkReviewSaving"
                  @toggle-group="toggleBulkReviewGroup"
                  @toggle-all-eligible="toggleAllBulkReviewGroups"
                  @review-student="openReviewModal"
                />

                <div class="flex flex-col gap-2 border-t border-border/70 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <p class="text-sm text-muted-foreground">
                    Showing {{ paginationStart }}-{{ paginationEnd }} of {{ filteredReviewGroups.length }} students
                  </p>
                  <div class="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      :disabled="submissionPage === 1"
                      @click="submissionPage -= 1"
                    >
                      <ChevronLeft data-icon="inline-start" />
                      <span>Previous</span>
                    </Button>
                    <Badge variant="outline" class="rounded-full px-3 py-1">
                      Page {{ submissionPage }} of {{ submissionPageCount }}
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      :disabled="submissionPage === submissionPageCount"
                      @click="submissionPage += 1"
                    >
                      <span>Next</span>
                      <ChevronRight data-icon="inline-end" />
                    </Button>
                  </div>
                </div>
              </template>

              <div v-else class="p-4">
                <Alert>
                  <Users />
                  <AlertTitle>{{ selectedExerciseReviewGroups.length ? 'No matching students' : 'No assigned students yet' }}</AlertTitle>
                  <AlertDescription>
                    {{ selectedExerciseReviewGroups.length ? 'Adjust the filter or search to see more students.' : 'Assigned students will appear here after you create an assignment.' }}
                  </AlertDescription>
                </Alert>
              </div>
            </template>

            <div v-else class="p-4">
              <Alert>
                <ClipboardList />
                <AlertTitle>Select an assignment</AlertTitle>
                <AlertDescription>
                  Choose an assignment set from the navigator to load its student review queue.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
        </div>
      </template>

      <AssignmentStudentReviewDialog
        :open="reviewModalOpen"
        :assignment-title="selectedExercise?.title ?? null"
        :group="selectedReviewGroup"
        :drafts="reviewForms"
        :saving="selectedReviewGroup ? Boolean(reviewSaving[selectedReviewGroup.key]) : false"
        :error="batchReviewError"
        :save-progress="batchReviewProgress"
        @update:open="handleReviewModalOpenChange"
        @update-draft="updateReviewDraft"
        @submit="submitStudentGrades"
      />

      <DialogRoot v-model:open="bulkReviewConfirmOpen">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-3xl border border-border/80 bg-card shadow-lg"
          >
            <div class="border-b border-border/70 px-6 py-5">
              <DialogTitle class="font-(--font-display) text-2xl leading-none text-(--color-heading)">
                Submit suggested grades?
              </DialogTitle>
              <DialogDescription class="mt-2 text-sm leading-6 text-muted-foreground">
                The system suggested scores and feedback will be released to students as-is.
              </DialogDescription>
            </div>

            <div class="flex flex-col gap-4 px-6 py-5">
              <div class="grid gap-2 sm:grid-cols-2">
                <div class="rounded-2xl border border-border/70 bg-muted/20 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Students
                  </p>
                  <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ selectedBulkReviewGroups.length }}
                  </p>
                </div>
                <div class="rounded-2xl border border-border/70 bg-muted/20 p-4">
                  <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    Phrase grades
                  </p>
                  <p class="mt-1 font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    {{ selectedBulkPhraseCount }}
                  </p>
                </div>
              </div>

              <Alert v-if="bulkReviewError" variant="destructive">
                <TriangleAlert />
                <AlertTitle>Bulk submit stopped</AlertTitle>
                <AlertDescription>{{ bulkReviewError }}</AlertDescription>
              </Alert>

              <Alert v-if="bulkReviewProgress">
                <LoaderCircle class="animate-spin" />
                <AlertTitle>Submitting grades</AlertTitle>
                <AlertDescription>{{ bulkReviewProgress }}</AlertDescription>
              </Alert>
            </div>

            <div class="flex flex-col gap-2 border-t border-border/70 px-6 py-4 sm:flex-row sm:justify-end">
              <Button
                variant="outline"
                :disabled="bulkReviewSaving"
                @click="bulkReviewConfirmOpen = false"
              >
                Cancel
              </Button>
              <Button
                :disabled="bulkReviewSaving || !selectedBulkReviewGroups.length"
                @click="submitSuggestedGradesForGroups"
              >
                <LoaderCircle v-if="bulkReviewSaving" class="animate-spin" data-icon="inline-start" />
                <CheckCheck v-else data-icon="inline-start" />
                <span>{{ bulkReviewSaving ? 'Submitting...' : 'Submit suggested grades' }}</span>
              </Button>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>

      <DialogRoot v-model:open="showForm">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 flex max-h-[90dvh] w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-3xl border border-border/80 bg-card shadow-lg"
          >
            <div class="flex items-start justify-between gap-3 border-b border-border/70 px-6 py-5">
              <div class="min-w-0">
                <DialogTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                  Build an assignment
                </DialogTitle>
                <DialogDescription class="mt-2 text-sm leading-6 text-muted-foreground">
                  Choose the phrases, assign the students, and grade their submissions back in this page.
                </DialogDescription>
              </div>

              <Button variant="outline" size="icon" class="rounded-xl" @click="showForm = false">
                <X />
                <span class="sr-only">Close assignment form</span>
              </Button>
            </div>

            <div class="flex-1 overflow-y-auto px-6 py-5">
              <div class="flex flex-col gap-5">
                <div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
                  <div class="flex flex-col gap-2">
                    <Label for="assignment-title">Title</Label>
                    <Input
                      id="assignment-title"
                      v-model="form.title"
                      placeholder="Greetings drill set"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <Label for="assignment-due-date">Due date</Label>
                    <Input
                      id="assignment-due-date"
                      v-model="form.due_date"
                      type="datetime-local"
                    />
                  </div>
                </div>

                <div class="grid gap-5 lg:grid-cols-2">
                  <div class="flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <p class="font-semibold text-(--color-heading)">Select phrases</p>
                        <p class="text-sm text-muted-foreground">
                          {{ form.phrase_ids.length }} selected
                        </p>
                      </div>
                    </div>

                    <div class="max-h-96 overflow-y-auto rounded-3xl border border-border/70 bg-muted/25 p-4">
                      <div class="flex flex-col gap-4">
                        <div
                          v-for="module in modulesStore.modules"
                          :key="module.module_id"
                          class="rounded-2xl border border-border/70 bg-background/80 p-4"
                        >
                          <div class="flex items-center gap-2">
                            <BookMarked class="text-muted-foreground" />
                            <p class="font-semibold text-(--color-heading)">
                              {{ module.title }}
                            </p>
                          </div>

                          <div class="mt-3 flex flex-col gap-2">
                            <label
                              v-for="phrase in modulesStore.getPhrasesForModule(module.module_id)"
                              :key="phrase.phrase_id"
                              class="flex cursor-pointer items-start gap-3 rounded-2xl border border-border/70 bg-muted/30 p-3"
                            >
                              <input
                                v-model="form.phrase_ids"
                                type="checkbox"
                                :value="phrase.phrase_id"
                                class="mt-1 accent-[var(--color-primary)]"
                              >
                              <div class="min-w-0">
                                <p class="font-semibold text-(--color-heading)">
                                  {{ phrase.japanese_text }}
                                </p>
                                <p class="text-sm text-muted-foreground">
                                  {{ phrase.romaji }} - {{ phrase.english_translation }}
                                </p>
                              </div>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-3">
                    <div>
                      <p class="font-semibold text-(--color-heading)">Assign to students</p>
                      <p class="text-sm text-muted-foreground">
                        {{ form.student_uids.length }} selected
                      </p>
                    </div>

                    <div class="max-h-96 overflow-y-auto rounded-3xl border border-border/70 bg-muted/25 p-4">
                      <div class="flex flex-col gap-2">
                        <label
                          v-for="student in students"
                          :key="student.uid"
                          class="flex cursor-pointer items-start gap-3 rounded-2xl border border-border/70 bg-background/80 p-3"
                        >
                          <input
                            v-model="form.student_uids"
                            type="checkbox"
                            :value="student.uid"
                            class="mt-1 accent-[var(--color-primary)]"
                          >
                          <div class="min-w-0">
                            <p class="font-semibold text-(--color-heading)">
                              {{ student.display_name }}
                            </p>
                            <p class="truncate text-sm text-muted-foreground">
                              {{ student.email }}
                            </p>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <Alert v-if="formError" variant="destructive">
                  <TriangleAlert />
                  <AlertTitle>Could not create assignment</AlertTitle>
                  <AlertDescription>{{ formError }}</AlertDescription>
                </Alert>
              </div>
            </div>

            <div class="border-t border-border/70 px-6 py-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
                <Button variant="outline" :disabled="submitting" @click="showForm = false">
                  Cancel
                </Button>
                <Button
                  :disabled="submitting || !form.title || !form.phrase_ids.length || !form.student_uids.length"
                  @click="handleCreate"
                >
                  <LoaderCircle v-if="submitting" class="animate-spin" data-icon="inline-start" />
                  <Plus v-else data-icon="inline-start" />
                  <span>{{ submitting ? 'Creating...' : 'Create and assign' }}</span>
                </Button>
              </div>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  BookMarked,
  Check,
  CalendarClock,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LoaderCircle,
  Plus,
  Funnel,
  Search,
  TriangleAlert,
  Users,
  X,
} from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  SelectContent,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectViewport,
} from 'reka-ui'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import AssignmentSetNavigator from '@/components/instructor/assignments/AssignmentSetNavigator.vue'
import AssignmentStudentQueueTable from '@/components/instructor/assignments/AssignmentStudentQueueTable.vue'
import AssignmentStudentReviewDialog from '@/components/instructor/assignments/AssignmentStudentReviewDialog.vue'
import {
  assignmentGroupStatus,
  buildAssignmentReviewGroups,
  gradeableSubmissions,
  isBulkSuggestedGradeableGroup,
  phraseDisplayLabel,
  unreleasedGradeableSubmissions,
  type AssignmentPhraseReviewDraft,
  type AssignmentReviewGroup,
} from '@/components/instructor/assignments/assignmentReview'
import {
  getExerciseSubmissions,
  reviewAssignmentSubmission,
} from '@/api/assignments'
import { getAllStudents } from '@/api/analytics'
import { createExercise, deleteExercise, getMyExercises } from '@/api/exercises'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { Exercise, InstructorAssignmentSubmission, Phrase, StudentStat } from '@/types'

type SubmissionFilter = 'all' | 'pending' | 'graded'
type AssignmentSetFilter = 'needs-grading' | 'active' | 'completed' | 'all'
type AssignmentSetStatus = 'needs-grading' | 'active' | 'completed'

interface AssignmentSetNavigatorItem {
  exerciseId: string
  title: string
  dueDate: string | null
  phraseCount: number
  studentCount: number
  submittedCount: number
  completionPercent: number
  pendingCount: number
  gradedCount: number
  status: AssignmentSetStatus
  createdAt: string
}

const PAGE_SIZE = 12

const classesStore = useClassesStore()
const modulesStore = useModulesStore()

const exercises = ref<Exercise[]>([])
const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showForm = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const exerciseSubmissions = ref<Record<string, InstructorAssignmentSubmission[]>>({})
const submissionsLoading = ref<Record<string, boolean>>({})
const submissionErrors = ref<Record<string, string | null>>({})
const reviewSaving = ref<Record<string, boolean>>({})
const reviewForms = ref<Record<string, AssignmentPhraseReviewDraft>>({})
const selectedExerciseId = ref<string | null>(null)
const selectedReviewStudentUid = ref<string | null>(null)
const reviewModalOpen = ref(false)
const submissionFilter = ref<SubmissionFilter>('all')
const submissionSearch = ref('')
const submissionPage = ref(1)
const assignmentSearch = ref('')
const assignmentFilter = ref<AssignmentSetFilter>('all')
const batchReviewError = ref<string | null>(null)
const batchReviewProgress = ref<string | null>(null)
const selectedBulkReviewKeys = ref<string[]>([])
const bulkReviewConfirmOpen = ref(false)
const bulkReviewSaving = ref(false)
const bulkReviewProgress = ref<string | null>(null)
const bulkReviewError = ref<string | null>(null)

const form = ref({
  title: '',
  phrase_ids: [] as string[],
  student_uids: [] as string[],
  due_date: '',
})

const selectedExercise = computed(
  () => exercises.value.find((exercise) => exercise.exercise_id === selectedExerciseId.value) ?? null,
)

const phraseById = computed<Record<string, Phrase>>(() => {
  const phrases: Record<string, Phrase> = {}
  for (const module of modulesStore.modules) {
    for (const phrase of modulesStore.getPhrasesForModule(module.module_id)) {
      phrases[phrase.phrase_id] = phrase
    }
  }
  return phrases
})

const allReviewGroups = computed(() => exercises.value.flatMap((exercise) => (
  buildAssignmentReviewGroups(
    exercise,
    students.value,
    submissionsForExercise(exercise.exercise_id),
    phraseById.value,
  )
)))

const selectedExerciseReviewGroups = computed(() => {
  if (!selectedExerciseId.value) return []
  return allReviewGroups.value.filter((group) => group.exerciseId === selectedExerciseId.value)
})

const selectedReviewGroup = computed(
  () => selectedExerciseReviewGroups.value.find((group) => group.studentUid === selectedReviewStudentUid.value) ?? null,
)

const bulkGradeableGroups = computed(() => selectedExerciseReviewGroups.value.filter(isBulkSuggestedGradeableGroup))
const bulkGradeableKeys = computed(() => bulkGradeableGroups.value.map((group) => group.key))
const bulkGradeableKeySet = computed(() => new Set(bulkGradeableKeys.value))
const selectedBulkReviewGroups = computed(() => (
  bulkGradeableGroups.value.filter((group) => selectedBulkReviewKeys.value.includes(group.key))
))
const selectedBulkPhraseCount = computed(() => (
  selectedBulkReviewGroups.value.reduce(
    (total, group) => total + unreleasedGradeableSubmissions(group).length,
    0,
  )
))

const filteredReviewGroups = computed(() => {
  const query = submissionSearch.value.trim().toLowerCase()

  return selectedExerciseReviewGroups.value.filter((group) => {
    const matchesFilter = groupMatchesFilter(group, submissionFilter.value)
    const matchesSearch = !query
      || group.studentDisplayName.toLowerCase().includes(query)
      || group.studentUid.toLowerCase().includes(query)

    return matchesFilter && matchesSearch
  })
})

const submissionPageCount = computed(() => Math.max(1, Math.ceil(filteredReviewGroups.value.length / PAGE_SIZE)))

const paginatedReviewGroups = computed(() => {
  const start = (submissionPage.value - 1) * PAGE_SIZE
  return filteredReviewGroups.value.slice(start, start + PAGE_SIZE)
})

const paginationStart = computed(() => {
  if (!filteredReviewGroups.value.length) return 0
  return (submissionPage.value - 1) * PAGE_SIZE + 1
})

const paginationEnd = computed(() => Math.min(submissionPage.value * PAGE_SIZE, filteredReviewGroups.value.length))

const summaryCards = computed(() => [
  {
    label: 'Assignments',
    value: `${exercises.value.length}`,
    icon: ClipboardList,
  },
  {
    label: 'Students',
    value: `${students.value.length}`,
    icon: Users,
  },
  {
    label: 'Pending grade',
    value: `${allReviewGroups.value.filter((group) => ['ready', 'partial'].includes(assignmentGroupStatus(group))).length}`,
    icon: TriangleAlert,
  },
  {
    label: 'Graded',
    value: `${allReviewGroups.value.filter((group) => assignmentGroupStatus(group) === 'graded').length}`,
    icon: CheckCheck,
  },
])

const assignmentItems = computed<AssignmentSetNavigatorItem[]>(() => exercises.value.map((exercise) => ({
  exerciseId: exercise.exercise_id,
  title: exercise.title,
  dueDate: exercise.due_date,
  phraseCount: exercise.phrases.length,
  studentCount: exercise.assignments.length,
  submittedCount: submissionsForExercise(exercise.exercise_id).length,
  completionPercent: completionPercent(exercise),
  pendingCount: pendingGradeCount(exercise.exercise_id),
  gradedCount: gradedCount(exercise.exercise_id),
  status: assignmentStatus(exercise),
  createdAt: exercise.created_at,
})))

const assignmentFilterOptions = computed(() => [
  {
    value: 'needs-grading' as const,
    label: 'Needs grading',
    count: assignmentItems.value.filter((item) => item.status === 'needs-grading').length,
  },
  {
    value: 'active' as const,
    label: 'Active',
    count: assignmentItems.value.filter((item) => item.status === 'active').length,
  },
  {
    value: 'completed' as const,
    label: 'Completed',
    count: assignmentItems.value.filter((item) => item.status === 'completed').length,
  },
  {
    value: 'all' as const,
    label: 'All',
    count: assignmentItems.value.length,
  },
])

const sortedAssignmentItems = computed(() => {
  const query = assignmentSearch.value.trim().toLowerCase()

  return assignmentItems.value
    .filter((item) => {
      const matchesSearch = !query || item.title.toLowerCase().includes(query)
      const matchesFilter = assignmentFilter.value === 'all' || item.status === assignmentFilter.value
      return matchesSearch && matchesFilter
    })
    .sort((left, right) => {
      const statusRank = assignmentStatusRank(left.status) - assignmentStatusRank(right.status)
      if (statusRank !== 0) return statusRank

      const leftDue = left.dueDate ? new Date(left.dueDate).getTime() : Number.POSITIVE_INFINITY
      const rightDue = right.dueDate ? new Date(right.dueDate).getTime() : Number.POSITIVE_INFINITY
      if (leftDue !== rightDue) return leftDue - rightDue

      return new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime()
    })
})

const selectedAssignmentItem = computed(
  () => assignmentItems.value.find((item) => item.exerciseId === selectedExerciseId.value) ?? null,
)

const selectedAssignmentSummaryCards = computed(() => {
  const item = selectedAssignmentItem.value
  if (!item) return []

  return [
    {
      label: 'Due',
      value: item.dueDate ? `${isAssignmentOverdue(item) ? 'Overdue ' : ''}${formatAssignmentDate(item.dueDate)}` : 'No due date',
      icon: CalendarClock,
      tone: isAssignmentOverdue(item)
        ? 'bg-red-50 text-red-700'
        : 'bg-sky-50 text-sky-700',
    },
    {
      label: 'Complete',
      value: `${item.completionPercent.toFixed(0)}%`,
      icon: Users,
      tone: item.status === 'completed'
        ? 'bg-emerald-50 text-emerald-700'
        : 'bg-sky-50 text-sky-700',
    },
    {
      label: 'Submissions',
      value: `${item.submittedCount}`,
      icon: ClipboardList,
      tone: 'bg-muted text-muted-foreground',
    },
    {
      label: 'Pending',
      value: `${item.pendingCount}`,
      icon: TriangleAlert,
      tone: item.pendingCount > 0
        ? 'bg-amber-50 text-amber-800'
        : 'bg-muted text-muted-foreground',
    },
    {
      label: 'Graded',
      value: `${item.gradedCount}`,
      icon: CheckCheck,
      tone: item.gradedCount > 0
        ? 'bg-emerald-50 text-emerald-800'
        : 'bg-muted text-muted-foreground',
    },
  ]
})

const submissionFilterOptions = computed(() => [
  {
    value: 'all' as const,
    label: 'All',
    count: selectedExerciseReviewGroups.value.length,
  },
  {
    value: 'pending' as const,
    label: 'Pending',
    count: selectedExerciseReviewGroups.value.filter((group) => groupMatchesFilter(group, 'pending')).length,
  },
  {
    value: 'graded' as const,
    label: 'Graded',
    count: selectedExerciseReviewGroups.value.filter((group) => groupMatchesFilter(group, 'graded')).length,
  },
])

function completedCount(exercise: Exercise) {
  return exercise.assignments.filter((assignment) => assignment.completed_at).length
}

function completionPercent(exercise: Exercise) {
  if (!exercise.assignments.length) return 0
  return (completedCount(exercise) / exercise.assignments.length) * 100
}

function submissionsForExercise(exerciseId: string) {
  return exerciseSubmissions.value[exerciseId] ?? []
}

function pendingGradeCount(exerciseId: string) {
  return allReviewGroups.value.filter((group) => (
    group.exerciseId === exerciseId
    && ['ready', 'partial'].includes(assignmentGroupStatus(group))
  )).length
}

function gradedCount(exerciseId: string) {
  return allReviewGroups.value.filter((group) => (
    group.exerciseId === exerciseId
    && assignmentGroupStatus(group) === 'graded'
  )).length
}

function assignmentStatusLabel(status: AssignmentSetStatus) {
  if (status === 'needs-grading') return 'Needs grading'
  if (status === 'completed') return 'Completed'
  return 'Active'
}

function assignmentStatusTone(status: AssignmentSetStatus) {
  if (status === 'needs-grading') return 'border-amber-300/70 bg-amber-100/80 text-amber-900'
  if (status === 'completed') return 'border-emerald-300/70 bg-emerald-100/80 text-emerald-900'
  return 'border-sky-300/70 bg-sky-100/80 text-sky-900'
}

function formatAssignmentDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function isAssignmentOverdue(item: AssignmentSetNavigatorItem) {
  return Boolean(item.dueDate && item.status !== 'completed' && new Date(item.dueDate).getTime() < Date.now())
}

function assignmentStatus(exercise: Exercise): AssignmentSetStatus {
  if (pendingGradeCount(exercise.exercise_id) > 0) return 'needs-grading'
  if (exercise.assignments.length > 0 && completedCount(exercise) === exercise.assignments.length) {
    return 'completed'
  }
  return 'active'
}

function assignmentStatusRank(status: AssignmentSetStatus) {
  if (status === 'needs-grading') return 0
  if (status === 'active') return 1
  return 2
}

function groupMatchesFilter(
  group: AssignmentReviewGroup,
  filter: SubmissionFilter,
) {
  const status = assignmentGroupStatus(group)
  if (filter === 'pending') return status !== 'graded'
  if (filter === 'graded') return status === 'graded'
  return true
}

function setSubmissionFilter(filter: SubmissionFilter) {
  submissionFilter.value = filter
  submissionPage.value = 1
}

function handleSubmissionFilterUpdate(value: unknown) {
  setSubmissionFilter((typeof value === 'string' ? value : 'all') as SubmissionFilter)
}

function clearBulkReviewSelection() {
  selectedBulkReviewKeys.value = []
  bulkReviewError.value = null
}

function resetBulkReviewState() {
  selectedBulkReviewKeys.value = []
  bulkReviewConfirmOpen.value = false
  bulkReviewProgress.value = null
  bulkReviewError.value = null
}

function pruneBulkReviewSelection() {
  selectedBulkReviewKeys.value = selectedBulkReviewKeys.value.filter((key) => bulkGradeableKeySet.value.has(key))
}

function toggleBulkReviewGroup(group: AssignmentReviewGroup) {
  if (bulkReviewSaving.value || !bulkGradeableKeySet.value.has(group.key)) return

  bulkReviewError.value = null
  selectedBulkReviewKeys.value = selectedBulkReviewKeys.value.includes(group.key)
    ? selectedBulkReviewKeys.value.filter((key) => key !== group.key)
    : [...selectedBulkReviewKeys.value, group.key]
}

function toggleAllBulkReviewGroups() {
  if (bulkReviewSaving.value || !bulkGradeableKeys.value.length) return

  bulkReviewError.value = null
  const allSelected = bulkGradeableKeys.value.every((key) => selectedBulkReviewKeys.value.includes(key))
  selectedBulkReviewKeys.value = allSelected ? [] : [...bulkGradeableKeys.value]
}

function openBulkReviewConfirm() {
  if (!selectedBulkReviewGroups.value.length || bulkReviewSaving.value) return
  bulkReviewError.value = null
  bulkReviewConfirmOpen.value = true
}

function selectExercise(exerciseId: string) {
  selectedExerciseId.value = exerciseId
  submissionFilter.value = 'all'
  submissionSearch.value = ''
  submissionPage.value = 1
  resetBulkReviewState()
}

function selectDefaultExercise() {
  const pendingExercise = exercises.value.find((exercise) => pendingGradeCount(exercise.exercise_id) > 0)
  selectedExerciseId.value = pendingExercise?.exercise_id ?? exercises.value[0]?.exercise_id ?? null
  submissionPage.value = 1
  resetBulkReviewState()
}

function openReviewModal(group: AssignmentReviewGroup) {
  for (const submission of gradeableSubmissions(group)) {
    ensureReviewForm(submission)
  }
  selectedReviewStudentUid.value = group.studentUid
  batchReviewError.value = null
  batchReviewProgress.value = null
  reviewModalOpen.value = true
}

function handleReviewModalOpenChange(open: boolean) {
  if (selectedReviewGroup.value && reviewSaving.value[selectedReviewGroup.value.key]) return
  reviewModalOpen.value = open
  if (open) return

  selectedReviewStudentUid.value = null
  batchReviewError.value = null
  batchReviewProgress.value = null
}

function ensureReviewForm(submission: InstructorAssignmentSubmission) {
  if (reviewForms.value[submission.submission_id]) return

  reviewForms.value[submission.submission_id] = {
    teacher_accuracy_score: String(
      Math.round(submission.teacher_accuracy_score ?? submission.suggested_accuracy_score),
    ),
    teacher_feedback_text: submission.teacher_feedback_text ?? submission.suggested_feedback_text ?? '',
  }
}

async function loadExerciseSubmissions(exerciseId: string) {
  submissionsLoading.value = {
    ...submissionsLoading.value,
    [exerciseId]: true,
  }
  submissionErrors.value = {
    ...submissionErrors.value,
    [exerciseId]: null,
  }

  try {
    const submissions = await getExerciseSubmissions(exerciseId)
    exerciseSubmissions.value = {
      ...exerciseSubmissions.value,
      [exerciseId]: submissions,
    }
    for (const submission of submissions) {
      ensureReviewForm(submission)
    }
  } catch (errorValue: any) {
    submissionErrors.value = {
      ...submissionErrors.value,
      [exerciseId]: errorValue.response?.data?.detail ?? 'Failed to load submissions.',
    }
  } finally {
    submissionsLoading.value = {
      ...submissionsLoading.value,
      [exerciseId]: false,
    }
  }
}

function updateReviewDraft(
  submissionId: string,
  field: keyof AssignmentPhraseReviewDraft,
  value: string,
) {
  reviewForms.value = {
    ...reviewForms.value,
    [submissionId]: {
      ...(reviewForms.value[submissionId] ?? {
        teacher_accuracy_score: '',
        teacher_feedback_text: '',
      }),
      [field]: value,
    },
  }
}

async function submitStudentGrades() {
  const group = selectedReviewGroup.value
  if (!group) return
  if (group.submittedCount < group.requiredCount) return

  const submissions = gradeableSubmissions(group)
  if (!submissions.length) return

  reviewSaving.value = {
    ...reviewSaving.value,
    [group.key]: true,
  }
  batchReviewError.value = null
  let failedSubmission: InstructorAssignmentSubmission | null = null

  try {
    for (const [index, submission] of submissions.entries()) {
      failedSubmission = submission
      ensureReviewForm(submission)
      const reviewForm = reviewForms.value[submission.submission_id]
      const teacherScore = Number(reviewForm.teacher_accuracy_score)

      if (!Number.isFinite(teacherScore)) {
        throw new Error(`Add a valid score for phrase ${submission.phrase_id}.`)
      }

      batchReviewProgress.value = `Submitting ${index + 1} of ${submissions.length}`
      await reviewAssignmentSubmission(submission.submission_id, {
        teacher_accuracy_score: teacherScore,
        teacher_feedback_text: reviewForm.teacher_feedback_text.trim(),
        release_to_student: true,
      })
    }

    await loadExerciseSubmissions(group.exerciseId)
    reviewModalOpen.value = false
    selectedReviewStudentUid.value = null
    batchReviewError.value = null
  } catch (errorValue: any) {
    const detail = errorValue.response?.data?.detail ?? errorValue.message ?? 'Failed to submit grades.'
    batchReviewError.value = failedSubmission
      ? `Failed on phrase ${failedSubmission.phrase_id}: ${detail}`
      : detail
  } finally {
    batchReviewProgress.value = null
    reviewSaving.value = {
      ...reviewSaving.value,
      [group.key]: false,
    }
  }
}

async function submitSuggestedGradesForGroups() {
  const groups = selectedBulkReviewGroups.value
  if (!groups.length || bulkReviewSaving.value) return

  bulkReviewSaving.value = true
  bulkReviewError.value = null
  let failedGroup: AssignmentReviewGroup | null = null
  let failedSubmission: InstructorAssignmentSubmission | null = null

  try {
    for (const [studentIndex, group] of groups.entries()) {
      failedGroup = group
      const submissions = unreleasedGradeableSubmissions(group)

      for (const [phraseIndex, submission] of submissions.entries()) {
        failedSubmission = submission
        bulkReviewProgress.value = `Submitting student ${studentIndex + 1} of ${groups.length}, phrase ${phraseIndex + 1} of ${submissions.length}`

        await reviewAssignmentSubmission(submission.submission_id, {
          teacher_accuracy_score: Math.round(submission.suggested_accuracy_score),
          teacher_feedback_text: submission.suggested_feedback_text ?? '',
          release_to_student: true,
        })
      }
    }

    if (selectedExerciseId.value) {
      await loadExerciseSubmissions(selectedExerciseId.value)
    }
    resetBulkReviewState()
  } catch (errorValue: any) {
    const detail = errorValue.response?.data?.detail ?? errorValue.message ?? 'Failed to submit suggested grades.'
    const failedPhrase = failedGroup?.phrases.find((phrase) => phrase.submission?.submission_id === failedSubmission?.submission_id)
    const failedPhraseLabel = failedPhrase ? phraseDisplayLabel(failedPhrase) : failedSubmission?.phrase_id
    bulkReviewError.value = failedGroup && failedPhraseLabel
      ? `Failed on ${failedGroup.studentDisplayName}, ${failedPhraseLabel}: ${detail}`
      : detail
  } finally {
    bulkReviewProgress.value = null
    bulkReviewSaving.value = false
  }
}

async function handleCreate() {
  const classId = classesStore.activeClassId
  if (!classId) {
    formError.value = 'Select a class before creating an assignment.'
    return
  }

  formError.value = null
  submitting.value = true

  try {
    const exerciseId = `ex_${Date.now()}`
    const created = await createExercise({
      exercise_id: exerciseId,
      class_id: classId,
      title: form.value.title,
      phrase_ids: form.value.phrase_ids,
      student_uids: form.value.student_uids,
      due_date: form.value.due_date || undefined,
    })

    exercises.value.unshift(created)
    showForm.value = false
    form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
    await loadExerciseSubmissions(created.exercise_id)
    selectExercise(created.exercise_id)
  } catch (errorValue: any) {
    formError.value = errorValue.response?.data?.detail ?? 'Failed to create assignment.'
  } finally {
    submitting.value = false
  }
}

async function handleDelete(exerciseId: string) {
  if (!window.confirm('Delete this assignment and all submissions?')) return

  try {
    const deletedSubmissionIds = submissionsForExercise(exerciseId).map((submission) => submission.submission_id)
    await deleteExercise(exerciseId)
    exercises.value = exercises.value.filter((exercise) => exercise.exercise_id !== exerciseId)

    const nextSubmissions = { ...exerciseSubmissions.value }
    delete nextSubmissions[exerciseId]
    exerciseSubmissions.value = nextSubmissions

    const nextSubmissionErrors = { ...submissionErrors.value }
    delete nextSubmissionErrors[exerciseId]
    submissionErrors.value = nextSubmissionErrors

    const nextSubmissionsLoading = { ...submissionsLoading.value }
    delete nextSubmissionsLoading[exerciseId]
    submissionsLoading.value = nextSubmissionsLoading

    const nextReviewForms = { ...reviewForms.value }
    for (const submissionId of deletedSubmissionIds) {
      delete nextReviewForms[submissionId]
    }
    reviewForms.value = nextReviewForms

    if (selectedReviewGroup.value?.exerciseId === exerciseId) {
      selectedReviewStudentUid.value = null
      reviewModalOpen.value = false
    }

    if (selectedExerciseId.value === exerciseId) {
      resetBulkReviewState()
    } else {
      pruneBulkReviewSelection()
    }

    if (selectedExerciseId.value === exerciseId) {
      selectDefaultExercise()
    }
  } catch {
    error.value = 'Failed to delete assignment.'
  }
}

async function loadExercises(classId: string | null) {
  exercises.value = []
  students.value = []
  selectedExerciseId.value = null
  selectedReviewStudentUid.value = null
  reviewModalOpen.value = false
  batchReviewError.value = null
  batchReviewProgress.value = null
  resetBulkReviewState()
  error.value = null
  form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
  exerciseSubmissions.value = {}
  submissionsLoading.value = {}
  submissionErrors.value = {}
  reviewForms.value = {}
  reviewSaving.value = {}

  if (!classId) {
    error.value = 'Create or select a class from Classes to manage assignments.'
    return
  }

  loading.value = true
  try {
    exercises.value = await getMyExercises(classId)
    students.value = await getAllStudents(classId)
    await Promise.all(exercises.value.map((exercise) => loadExerciseSubmissions(exercise.exercise_id)))
    selectDefaultExercise()
  } catch {
    error.value = 'Failed to load assignments.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
    await modulesStore.fetchModules()
    await Promise.all(modulesStore.modules.map((module) => modulesStore.fetchPhrases(module.module_id)))
  } catch {
    error.value = 'Failed to load your classes.'
  }

  await loadExercises(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadExercises(classId)
  },
)

watch(showForm, (open) => {
  if (open) return
  if (submitting.value) return
  formError.value = null
})

watch([submissionSearch, selectedExerciseId], () => {
  submissionPage.value = 1
})

watch(filteredReviewGroups, () => {
  if (submissionPage.value > submissionPageCount.value) {
    submissionPage.value = submissionPageCount.value
  }
})

watch(bulkGradeableKeys, () => {
  pruneBulkReviewSelection()
})
</script>

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
                Exercise grading queue
              </CardTitle>
              <CardDescription class="mt-1 max-w-3xl text-sm">
                Scan assignment progress, open one exercise queue, and grade submissions without filling the page with audio players.
              </CardDescription>
            </div>

            <Button @click="showForm = true">
              <Plus data-icon="inline-start" />
              <span>New exercise</span>
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
        message="Loading exercises..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Exercises unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Alert v-else-if="!exercises.length">
        <ClipboardList />
        <AlertTitle>No exercises yet</AlertTitle>
        <AlertDescription>
          Create your first assignment to send phrase work to the active class and review submissions here.
        </AlertDescription>
      </Alert>

      <template v-else>
        <Card class="gap-0 overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
          <CardHeader class="border-b border-border/70 p-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
                  Assignment sets
                </CardTitle>
                <CardDescription class="mt-1 text-sm">
                  Pick an exercise to load its focused grading queue.
                </CardDescription>
              </div>
              <Badge variant="outline" class="rounded-full px-3 py-1">
                {{ selectedExercise?.title ?? 'No exercise selected' }}
              </Badge>
            </div>
          </CardHeader>

          <CardContent class="p-0">
            <div class="overflow-x-auto">
              <Table class="min-w-[1120px] table-fixed">
                <colgroup>
                  <col class="w-[24%]">
                  <col class="w-[11%]">
                  <col class="w-[8%]">
                  <col class="w-[10%]">
                  <col class="w-[15%]">
                  <col class="w-[10%]">
                  <col class="w-[10%]">
                  <col class="w-[12%]">
                </colgroup>
                <TableHeader class="bg-muted/20">
                  <TableRow class="hover:bg-transparent">
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Exercise</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Due</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Phrases</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Students</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Completion</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Submitted</TableHead>
                    <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Grade</TableHead>
                    <TableHead class="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="exercise in exercises"
                    :key="exercise.exercise_id"
                    class="transition hover:bg-muted/25"
                    :class="selectedExerciseId === exercise.exercise_id ? 'bg-primary/5' : ''"
                  >
                    <TableCell class="px-4 py-3 align-middle">
                      <div class="min-w-0">
                        <p class="truncate font-semibold text-(--color-heading)">
                          {{ exercise.title }}
                        </p>
                        <p class="truncate text-xs text-muted-foreground">
                          {{ completedCount(exercise) }}/{{ exercise.assignments.length }} students complete
                        </p>
                      </div>
                    </TableCell>
                    <TableCell class="px-4 py-3 align-middle">
                      <Badge
                        v-if="exercise.due_date"
                        :variant="isOverdue(exercise.due_date) ? 'destructive' : 'outline'"
                        class="rounded-full px-2.5 py-1"
                      >
                        {{ formatDate(exercise.due_date) }}
                      </Badge>
                      <span v-else class="text-sm text-muted-foreground">No due date</span>
                    </TableCell>
                    <TableCell class="px-4 py-3 text-sm font-semibold text-(--color-heading) align-middle">
                      {{ exercise.phrases.length }}
                    </TableCell>
                    <TableCell class="px-4 py-3 text-sm font-semibold text-(--color-heading) align-middle">
                      {{ exercise.assignments.length }}
                    </TableCell>
                    <TableCell class="px-4 py-3 align-middle">
                      <div class="grid grid-cols-[minmax(80px,1fr)_2.5rem] items-center gap-2">
                        <div class="h-1.5 overflow-hidden rounded-full bg-border/70">
                          <div
                            class="h-full rounded-full bg-primary transition-[width] duration-300"
                            :style="{ width: `${completionPercent(exercise)}%` }"
                          />
                        </div>
                        <span class="text-xs font-semibold tabular-nums text-(--color-heading)">
                          {{ completionPercent(exercise).toFixed(0) }}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell class="px-4 py-3 text-sm font-semibold text-(--color-heading) align-middle">
                      {{ submissionsForExercise(exercise.exercise_id).length }}
                    </TableCell>
                    <TableCell class="px-4 py-3 align-middle">
                      <div class="flex flex-wrap gap-1.5">
                        <Badge
                          :variant="pendingGradeCount(exercise.exercise_id) ? 'destructive' : 'outline'"
                          class="rounded-full px-2.5 py-1"
                        >
                          {{ pendingGradeCount(exercise.exercise_id) }} pending
                        </Badge>
                        <Badge variant="secondary" class="rounded-full px-2.5 py-1">
                          {{ gradedCount(exercise.exercise_id) }} graded
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell class="px-4 py-3 align-middle">
                      <div class="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          @click="selectExercise(exercise.exercise_id)"
                        >
                          <ClipboardList data-icon="inline-start" />
                          <span>Grade queue</span>
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          class="size-9 rounded-xl"
                          @click="handleDelete(exercise.exercise_id)"
                        >
                          <Trash2 />
                          <span class="sr-only">Delete exercise</span>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card class="gap-0 overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
          <CardHeader class="border-b border-border/70 p-4">
            <div class="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" class="rounded-full px-3 py-1 uppercase tracking-[0.18em]">
                    Submission queue
                  </Badge>
                  <Badge variant="outline" class="rounded-full px-3 py-1">
                    {{ filteredSubmissions.length }} visible
                  </Badge>
                </div>
                <CardTitle class="mt-2 font-(--font-display) text-xl leading-none text-(--color-heading)">
                  {{ selectedExercise?.title ?? 'Select an exercise' }}
                </CardTitle>
                <CardDescription class="mt-1 text-sm">
                  Suggested backend scores stay hidden until you submit a grade.
                </CardDescription>
              </div>

              <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                <div class="flex h-10 items-center gap-2 rounded-xl border border-border bg-background px-3">
                  <Search class="size-4 text-muted-foreground" />
                  <Input
                    v-model="submissionSearch"
                    class="h-8 rounded-none border-0 bg-transparent px-0 text-sm shadow-none ring-0 outline-none focus-visible:!border-transparent focus-visible:!shadow-none focus-visible:!ring-0 focus-visible:!ring-offset-0 focus-visible:!outline-none"
                    placeholder="Search student or phrase"
                  />
                </div>

                <div class="flex rounded-xl border border-border bg-muted/20 p-1">
                  <button
                    v-for="option in submissionFilterOptions"
                    :key="option.value"
                    type="button"
                    data-slot="submission-filter"
                    class="rounded-lg px-3 py-1.5 text-sm font-semibold transition"
                    :class="submissionFilter === option.value ? '!bg-primary !text-primary-foreground shadow-sm shadow-primary/15' : 'text-muted-foreground hover:bg-background hover:text-foreground'"
                    @click="setSubmissionFilter(option.value)"
                  >
                    {{ option.label }}
                    <span class="ml-1 text-xs opacity-80">{{ option.count }}</span>
                  </button>
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
              <template v-if="paginatedSubmissions.length">
                <div class="overflow-x-auto">
                  <Table class="min-w-[900px] table-fixed">
                    <colgroup>
                      <col class="w-[24%]">
                      <col class="w-[28%]">
                      <col class="w-[14%]">
                      <col class="w-[12%]">
                      <col class="w-[12%]">
                      <col class="w-[10%]">
                    </colgroup>
                    <TableHeader class="bg-muted/20">
                      <TableRow class="hover:bg-transparent">
                        <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Student</TableHead>
                        <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Phrase</TableHead>
                        <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Submitted</TableHead>
                        <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Score</TableHead>
                        <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Status</TableHead>
                        <TableHead class="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow
                        v-for="submission in paginatedSubmissions"
                        :key="submission.submission_id"
                        class="transition hover:bg-muted/25"
                      >
                        <TableCell class="px-4 py-3 align-middle">
                          <p class="truncate font-semibold text-(--color-heading)">
                            {{ submission.student_display_name }}
                          </p>
                        </TableCell>
                        <TableCell class="px-4 py-3 align-middle">
                          <p class="truncate text-sm text-muted-foreground">
                            {{ phraseLabel(submission.phrase_id) }}
                          </p>
                        </TableCell>
                        <TableCell class="px-4 py-3 text-sm text-muted-foreground align-middle">
                          {{ formatDate(submission.submitted_at) }}
                        </TableCell>
                        <TableCell class="px-4 py-3 align-middle">
                          <Badge variant="outline" class="rounded-full px-2.5 py-1">
                            {{ submission.suggested_accuracy_score.toFixed(0) }}%
                          </Badge>
                        </TableCell>
                        <TableCell class="px-4 py-3 align-middle">
                          <Badge :variant="submissionStatusVariant(submission)" class="rounded-full px-2.5 py-1">
                            {{ submissionStatusLabel(submission) }}
                          </Badge>
                        </TableCell>
                        <TableCell class="px-4 py-3 align-middle">
                          <div class="flex justify-end">
                            <Button size="sm" @click="openReviewModal(submission)">
                              <SquarePen data-icon="inline-start" />
                              <span>{{ submission.released_at ? 'Edit' : 'Grade' }}</span>
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>

                <div class="flex flex-col gap-2 border-t border-border/70 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <p class="text-sm text-muted-foreground">
                    Showing {{ paginationStart }}-{{ paginationEnd }} of {{ filteredSubmissions.length }} submissions
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
                  <AudioLines />
                  <AlertTitle>{{ selectedExerciseSubmissions.length ? 'No matching submissions' : 'No student submissions yet' }}</AlertTitle>
                  <AlertDescription>
                    {{ selectedExerciseSubmissions.length ? 'Adjust the filter or search to see more submissions.' : 'Assigned phrases will appear here after students record their work.' }}
                  </AlertDescription>
                </Alert>
              </div>
            </template>
          </CardContent>
        </Card>
      </template>

      <DialogRoot v-model:open="reviewModalOpen">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 flex max-h-[90dvh] w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-3xl border border-border/80 bg-card shadow-lg"
          >
            <div class="flex items-start justify-between gap-3 border-b border-border/70 px-5 py-4">
              <div class="min-w-0">
                <Badge v-if="selectedSubmission" :variant="submissionStatusVariant(selectedSubmission)" class="w-fit rounded-full px-3 py-1">
                  {{ submissionStatusLabel(selectedSubmission) }}
                </Badge>
                <DialogTitle class="mt-2 font-(--font-display) text-2xl leading-none text-(--color-heading)">
                  {{ selectedSubmission?.released_at ? 'Edit grade' : 'Grade submission' }}
                </DialogTitle>
                <DialogDescription v-if="selectedSubmission" class="mt-1 text-sm text-muted-foreground">
                  {{ selectedSubmission.student_display_name }} - {{ phraseLabel(selectedSubmission.phrase_id) }} - submitted {{ formatDate(selectedSubmission.submitted_at) }}
                </DialogDescription>
              </div>

              <Button variant="outline" size="icon" class="rounded-xl" @click="reviewModalOpen = false">
                <X />
                <span class="sr-only">Close grade modal</span>
              </Button>
            </div>

            <div v-if="selectedSubmission" class="flex-1 overflow-y-auto px-5 py-4">
              <div class="grid gap-4 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
                <div class="flex flex-col gap-3">
                  <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Suggested score
                    </p>
                    <p class="mt-2 font-(--font-display) text-4xl leading-none text-(--color-heading)">
                      {{ selectedSubmission.suggested_accuracy_score.toFixed(0) }}%
                    </p>
                    <div class="mt-3 grid gap-2 text-sm text-muted-foreground sm:grid-cols-3">
                      <span>Mora {{ selectedSubmission.suggested_mora_timing_score.toFixed(0) }}%</span>
                      <span>Consonants {{ selectedSubmission.suggested_consonant_score.toFixed(0) }}%</span>
                      <span>Vowels {{ selectedSubmission.suggested_vowel_score.toFixed(0) }}%</span>
                    </div>
                  </div>

                  <audio
                    class="w-full"
                    :src="selectedSubmission.audio_file_url"
                    controls
                    preload="metadata"
                  />

                  <div class="rounded-2xl border border-border/70 bg-background/80 p-4">
                    <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                      Suggested feedback
                    </p>
                    <p class="mt-2 text-sm leading-6 text-foreground/85">
                      {{ selectedSubmission.suggested_feedback_text || 'No suggested feedback was generated for this submission.' }}
                    </p>
                  </div>
                </div>

                <div class="flex flex-col gap-4">
                  <div class="grid gap-4 sm:grid-cols-[160px_minmax(0,1fr)]">
                    <div class="flex flex-col gap-2">
                      <Label :for="`score-${selectedSubmission.submission_id}`">Teacher score</Label>
                      <Input
                        :id="`score-${selectedSubmission.submission_id}`"
                        v-model="reviewForms[selectedSubmission.submission_id].teacher_accuracy_score"
                        type="number"
                        min="0"
                        max="100"
                      />
                    </div>

                    <div class="flex flex-col gap-2">
                      <Label :for="`feedback-${selectedSubmission.submission_id}`">Teacher feedback</Label>
                      <textarea
                        :id="`feedback-${selectedSubmission.submission_id}`"
                        v-model="reviewForms[selectedSubmission.submission_id].teacher_feedback_text"
                        rows="7"
                        class="min-h-40 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground shadow-xs outline-none transition focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
                      />
                    </div>
                  </div>

                  <Alert v-if="submissionErrors[selectedSubmission.exercise_id]" variant="destructive">
                    <TriangleAlert />
                    <AlertTitle>Grade update failed</AlertTitle>
                    <AlertDescription>{{ submissionErrors[selectedSubmission.exercise_id] }}</AlertDescription>
                  </Alert>
                </div>
              </div>
            </div>

            <div v-if="selectedSubmission" class="border-t border-border/70 px-5 py-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
                <Button
                  :disabled="reviewSaving[selectedSubmission.submission_id]"
                  @click="submitGrade(selectedSubmission)"
                >
                  <LoaderCircle
                    v-if="reviewSaving[selectedSubmission.submission_id]"
                    class="animate-spin"
                    data-icon="inline-start"
                  />
                  <Send v-else data-icon="inline-start" />
                  <span>{{ selectedSubmission.released_at ? 'Update grade' : 'Submit grade' }}</span>
                </Button>
              </div>
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
                <span class="sr-only">Close exercise form</span>
              </Button>
            </div>

            <div class="flex-1 overflow-y-auto px-6 py-5">
              <div class="flex flex-col gap-5">
                <div class="grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
                  <div class="flex flex-col gap-2">
                    <Label for="exercise-title">Title</Label>
                    <Input
                      id="exercise-title"
                      v-model="form.title"
                      placeholder="Greetings drill set"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <Label for="exercise-due-date">Due date</Label>
                    <Input
                      id="exercise-due-date"
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
  AudioLines,
  BookMarked,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LoaderCircle,
  Plus,
  Search,
  Send,
  SquarePen,
  TriangleAlert,
  Trash2,
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
} from 'reka-ui'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import { useClassesStore } from '@/stores/classes'
import { useModulesStore } from '@/stores/modules'
import type { Exercise, InstructorAssignmentSubmission, StudentStat } from '@/types'

type SubmissionFilter = 'all' | 'pending' | 'graded'

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
const reviewForms = ref<Record<string, {
  teacher_accuracy_score: string
  teacher_feedback_text: string
}>>({})
const selectedExerciseId = ref<string | null>(null)
const selectedSubmissionId = ref<string | null>(null)
const reviewModalOpen = ref(false)
const submissionFilter = ref<SubmissionFilter>('all')
const submissionSearch = ref('')
const submissionPage = ref(1)

const form = ref({
  title: '',
  phrase_ids: [] as string[],
  student_uids: [] as string[],
  due_date: '',
})

const allSubmissions = computed(() => Object.values(exerciseSubmissions.value).flat())

const selectedExercise = computed(
  () => exercises.value.find((exercise) => exercise.exercise_id === selectedExerciseId.value) ?? null,
)

const selectedExerciseSubmissions = computed(() => {
  if (!selectedExerciseId.value) return []
  return submissionsForExercise(selectedExerciseId.value)
})

const selectedSubmission = computed(
  () => allSubmissions.value.find((submission) => submission.submission_id === selectedSubmissionId.value) ?? null,
)

const filteredSubmissions = computed(() => {
  const query = submissionSearch.value.trim().toLowerCase()

  return selectedExerciseSubmissions.value.filter((submission) => {
    const matchesFilter = submissionMatchesFilter(submission, submissionFilter.value)
    const label = phraseLabel(submission.phrase_id).toLowerCase()
    const matchesSearch = !query
      || submission.student_display_name.toLowerCase().includes(query)
      || label.includes(query)
      || submission.phrase_id.toLowerCase().includes(query)

    return matchesFilter && matchesSearch
  })
})

const submissionPageCount = computed(() => Math.max(1, Math.ceil(filteredSubmissions.value.length / PAGE_SIZE)))

const paginatedSubmissions = computed(() => {
  const start = (submissionPage.value - 1) * PAGE_SIZE
  return filteredSubmissions.value.slice(start, start + PAGE_SIZE)
})

const paginationStart = computed(() => {
  if (!filteredSubmissions.value.length) return 0
  return (submissionPage.value - 1) * PAGE_SIZE + 1
})

const paginationEnd = computed(() => Math.min(submissionPage.value * PAGE_SIZE, filteredSubmissions.value.length))

const summaryCards = computed(() => [
  {
    label: 'Exercises',
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
    value: `${allSubmissions.value.filter((submission) => !submission.released_at).length}`,
    icon: TriangleAlert,
  },
  {
    label: 'Graded',
    value: `${allSubmissions.value.filter((submission) => submission.released_at).length}`,
    icon: CheckCheck,
  },
])

const submissionFilterOptions = computed(() => [
  {
    value: 'all' as const,
    label: 'All',
    count: selectedExerciseSubmissions.value.length,
  },
  {
    value: 'pending' as const,
    label: 'Pending',
    count: selectedExerciseSubmissions.value.filter((submission) => submissionMatchesFilter(submission, 'pending')).length,
  },
  {
    value: 'graded' as const,
    label: 'Graded',
    count: selectedExerciseSubmissions.value.filter((submission) => submissionMatchesFilter(submission, 'graded')).length,
  },
])

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function isOverdue(dateStr: string) {
  return new Date(dateStr).getTime() < Date.now()
}

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
  return submissionsForExercise(exerciseId).filter((submission) => !submission.released_at).length
}

function gradedCount(exerciseId: string) {
  return submissionsForExercise(exerciseId).filter((submission) => submission.released_at).length
}

function phraseLabel(phraseId: string) {
  for (const module of modulesStore.modules) {
    const phrase = modulesStore.getPhrasesForModule(module.module_id).find((item) => item.phrase_id === phraseId)
    if (phrase) {
      return `${phrase.japanese_text} - ${phrase.romaji}`
    }
  }
  return phraseId
}

function submissionMatchesFilter(
  submission: InstructorAssignmentSubmission,
  filter: SubmissionFilter,
) {
  if (filter === 'pending') return !submission.released_at
  if (filter === 'graded') return Boolean(submission.released_at)
  return true
}

function submissionStatusLabel(submission: InstructorAssignmentSubmission) {
  if (submission.released_at) return 'Graded'
  return 'Pending grade'
}

function submissionStatusVariant(
  submission: InstructorAssignmentSubmission,
): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (submission.released_at) return 'default'
  return 'destructive'
}

function setSubmissionFilter(filter: SubmissionFilter) {
  submissionFilter.value = filter
  submissionPage.value = 1
}

function selectExercise(exerciseId: string) {
  selectedExerciseId.value = exerciseId
  submissionFilter.value = 'all'
  submissionSearch.value = ''
  submissionPage.value = 1
}

function selectDefaultExercise() {
  const pendingExercise = exercises.value.find((exercise) => pendingGradeCount(exercise.exercise_id) > 0)
  selectedExerciseId.value = pendingExercise?.exercise_id ?? exercises.value[0]?.exercise_id ?? null
  submissionPage.value = 1
}

function openReviewModal(submission: InstructorAssignmentSubmission) {
  ensureReviewForm(submission)
  selectedSubmissionId.value = submission.submission_id
  reviewModalOpen.value = true
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

async function submitGrade(submission: InstructorAssignmentSubmission) {
  ensureReviewForm(submission)

  const reviewForm = reviewForms.value[submission.submission_id]
  reviewSaving.value = {
    ...reviewSaving.value,
    [submission.submission_id]: true,
  }

  try {
    await reviewAssignmentSubmission(submission.submission_id, {
      teacher_accuracy_score: Number(reviewForm.teacher_accuracy_score),
      teacher_feedback_text: reviewForm.teacher_feedback_text.trim(),
      release_to_student: true,
    })
    await loadExerciseSubmissions(submission.exercise_id)
  } catch (errorValue: any) {
    submissionErrors.value = {
      ...submissionErrors.value,
      [submission.exercise_id]: errorValue.response?.data?.detail ?? 'Failed to submit grade.',
    }
  } finally {
    reviewSaving.value = {
      ...reviewSaving.value,
      [submission.submission_id]: false,
    }
  }
}

async function handleCreate() {
  const classId = classesStore.activeClassId
  if (!classId) {
    formError.value = 'Select a class before creating an exercise.'
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
    formError.value = errorValue.response?.data?.detail ?? 'Failed to create exercise.'
  } finally {
    submitting.value = false
  }
}

async function handleDelete(exerciseId: string) {
  if (!window.confirm('Delete this exercise and all assignments?')) return

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

    if (selectedSubmissionId.value && deletedSubmissionIds.includes(selectedSubmissionId.value)) {
      selectedSubmissionId.value = null
      reviewModalOpen.value = false
    }

    if (selectedExerciseId.value === exerciseId) {
      selectDefaultExercise()
    }
  } catch {
    error.value = 'Failed to delete exercise.'
  }
}

async function loadExercises(classId: string | null) {
  exercises.value = []
  students.value = []
  selectedExerciseId.value = null
  selectedSubmissionId.value = null
  reviewModalOpen.value = false
  error.value = null
  form.value = { title: '', phrase_ids: [], student_uids: [], due_date: '' }
  exerciseSubmissions.value = {}
  submissionsLoading.value = {}
  submissionErrors.value = {}
  reviewForms.value = {}
  reviewSaving.value = {}

  if (!classId) {
    error.value = 'Create or select a class from Classes to manage exercises.'
    return
  }

  loading.value = true
  try {
    exercises.value = await getMyExercises(classId)
    students.value = await getAllStudents(classId)
    await Promise.all(exercises.value.map((exercise) => loadExerciseSubmissions(exercise.exercise_id)))
    selectDefaultExercise()
  } catch {
    error.value = 'Failed to load exercises.'
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

watch(filteredSubmissions, () => {
  if (submissionPage.value > submissionPageCount.value) {
    submissionPage.value = submissionPageCount.value
  }
})
</script>

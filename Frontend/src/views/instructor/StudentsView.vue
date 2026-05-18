<template>
  <InstructorLayout>
    <div class="flex flex-col gap-4">
      <Card class="border-rose-200/80 bg-linear-to-br from-card via-card to-rose-50/70 shadow-sm shadow-rose-900/5">
        <CardHeader class="gap-3 p-4 sm:p-5">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <Badge class="rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary uppercase tracking-[0.18em] hover:bg-primary/10">
                  Student directory
                </Badge>
                <Badge variant="outline" class="rounded-full border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">
                  {{ filteredStudents.length }} visible
                </Badge>
              </div>

              <CardTitle class="mt-3 font-(--font-display) text-2xl leading-none text-(--color-heading) sm:text-3xl">
                Class scan
              </CardTitle>
              <CardDescription class="mt-1 max-w-2xl text-sm">
                Search learners, spot review needs, and open details only when you need the drilldown.
              </CardDescription>
            </div>

            <div class="grid w-full grid-cols-[minmax(0,1fr)_2.75rem] items-center gap-2 lg:max-w-md">
              <Label for="student-search" class="sr-only">Search students</Label>
              <div class="flex h-11 items-center gap-2 rounded-xl border border-rose-200 bg-white/85 px-3 shadow-xs shadow-rose-900/5 transition focus-within:border-primary/60 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background">
                <Search class="size-4 text-muted-foreground" />
                <Input
                  id="student-search"
                  v-model="search"
                  class="h-9 rounded-none border-0 bg-transparent px-0 text-sm shadow-none ring-0 outline-none focus-visible:border-transparent! focus-visible:shadow-none! focus-visible:ring-0! focus-visible:ring-offset-0! focus-visible:outline-none!"
                  placeholder="Search by name or email"
                />
              </div>

              <!-- Mobile: plain button opens Sheet -->
              <button
                class="sm:hidden relative inline-flex size-11 items-center justify-center rounded-xl border border-primary/35 bg-white text-primary shadow-sm shadow-rose-900/5 outline-none ring-1 ring-primary/10 transition hover:cursor-pointer hover:border-primary/60 hover:bg-primary/10 focus-visible:ring-2 focus-visible:ring-primary/30"
                aria-label="Filter class list"
                @click="filterSheetOpen = true"
              >
                <Funnel class="size-4" />
                <span
                  v-if="activeFilterCount"
                  class="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full border border-white bg-primary text-[10px] font-semibold leading-none text-primary-foreground"
                >
                  {{ activeFilterCount }}
                </span>
              </button>

              <!-- Desktop: Popover -->
              <div class="hidden sm:block">
                <PopoverRoot>
                  <PopoverTrigger
                    aria-label="Filter class list"
                    class="relative inline-flex size-11 items-center justify-center rounded-xl border border-primary/35 bg-white text-primary shadow-sm shadow-rose-900/5 outline-none ring-1 ring-primary/10 transition hover:cursor-pointer hover:border-primary/60 hover:bg-primary/10 focus-visible:ring-2 focus-visible:ring-primary/30"
                  >
                    <Funnel class="size-4" />
                    <span
                      v-if="activeFilterCount"
                      class="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full border border-white bg-primary text-[10px] font-semibold leading-none text-primary-foreground"
                    >
                      {{ activeFilterCount }}
                    </span>
                  </PopoverTrigger>

                  <PopoverPortal>
                    <PopoverContent
                      side="bottom"
                      align="end"
                      :side-offset="8"
                      :collision-padding="12"
                      class="z-50 flex max-h-[calc(100svh-6rem)] w-76 flex-col overflow-y-auto rounded-2xl border border-rose-200 bg-popover p-2.5 text-popover-foreground shadow-lg shadow-rose-950/10 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
                    >
                      <div class="flex items-center justify-between gap-3">
                        <div>
                          <p class="text-sm font-semibold text-(--color-heading)">Filters</p>
                          <p class="text-xs text-muted-foreground">{{ filteredStudents.length }} visible</p>
                        </div>
                        <Button
                          v-if="activeFilterCount"
                          variant="ghost"
                          size="sm"
                          class="h-8 px-2 text-xs text-muted-foreground hover:text-primary"
                          @click="clearStudentFilters"
                        >
                          Clear
                        </Button>
                      </div>

                      <Separator class="my-2" />

                      <div class="flex flex-col gap-2">
                        <div class="grid grid-cols-2 gap-1.5">
                          <div>
                            <p class="mb-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Status</p>
                            <div class="grid gap-0.5">
                              <button
                                v-for="option in statusFilterOptions"
                                :key="option.value"
                                type="button"
                                class="flex items-center justify-between rounded-lg px-2 py-1 text-left text-xs transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                                :class="studentStatusFilter === option.value ? 'bg-primary text-primary-foreground hover:bg-primary' : 'text-(--color-heading) hover:bg-rose-50'"
                                @click="studentStatusFilter = option.value"
                              >
                                <span class="flex min-w-0 items-center gap-1.5">
                                  <span class="size-1.5 shrink-0 rounded-full" :class="studentStatusFilter === option.value ? 'bg-primary-foreground/70' : option.value === 'needs-review' ? 'bg-red-500' : option.value === 'on-track' ? 'bg-emerald-500' : 'bg-muted-foreground/40'" />
                                  <span class="truncate">{{ option.label }}</span>
                                </span>
                                <span class="ml-1 shrink-0 rounded-full border px-1 py-0.5 text-[9px] font-semibold leading-none tabular-nums" :class="studentStatusFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                              </button>
                            </div>
                          </div>
                          <div>
                            <p class="mb-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Activity</p>
                            <div class="grid gap-0.5">
                              <button
                                v-for="option in activityFilterOptions"
                                :key="option.value"
                                type="button"
                                class="flex items-center justify-between rounded-lg px-2 py-1 text-left text-xs transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                                :class="activityFilter === option.value ? 'bg-primary text-primary-foreground hover:bg-primary' : 'text-(--color-heading) hover:bg-rose-50'"
                                @click="activityFilter = option.value"
                              >
                                <span class="flex min-w-0 items-center gap-1.5">
                                  <span class="size-1.5 shrink-0 rounded-full" :class="activityFilter === option.value ? 'bg-primary-foreground/70' : option.value === 'active' ? 'bg-sky-500' : option.value === 'no-attempts' ? 'bg-rose-400' : 'bg-muted-foreground/40'" />
                                  <span class="truncate">{{ option.label }}</span>
                                </span>
                                <span class="ml-1 shrink-0 rounded-full border px-1 py-0.5 text-[9px] font-semibold leading-none tabular-nums" :class="activityFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                              </button>
                            </div>
                          </div>
                        </div>

                        <div>
                          <p class="mb-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Score</p>
                          <div class="grid grid-cols-2 gap-0.5">
                            <button
                              v-for="option in scoreFilterOptions"
                              :key="option.value"
                              type="button"
                              class="flex items-center justify-between rounded-lg px-2 py-1 text-left text-xs transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                              :class="scoreBandFilter === option.value ? 'bg-primary text-primary-foreground hover:bg-primary' : 'text-(--color-heading) hover:bg-rose-50'"
                              @click="scoreBandFilter = option.value"
                            >
                              <span class="flex min-w-0 items-center gap-1.5">
                                <span class="size-1.5 shrink-0 rounded-full" :class="scoreBandDotClass(option.value, scoreBandFilter === option.value)" />
                                <span class="truncate">{{ option.label }}</span>
                              </span>
                              <span class="ml-1 shrink-0 rounded-full border px-1 py-0.5 text-[9px] font-semibold leading-none tabular-nums" :class="scoreBandFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                            </button>
                          </div>
                        </div>

                        <div>
                          <p class="mb-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Sort</p>
                          <div class="grid grid-cols-2 gap-0.5">
                            <button
                              v-for="option in sortOptions"
                              :key="option.value"
                              type="button"
                              class="flex items-center justify-between gap-1 rounded-lg px-2 py-1 text-left text-xs transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                              :class="studentSort === option.value ? 'bg-primary text-primary-foreground hover:bg-primary' : 'text-(--color-heading) hover:bg-rose-50'"
                              @click="studentSort = option.value"
                            >
                              <span class="truncate">{{ option.label }}</span>
                              <Check v-if="studentSort === option.value" class="size-3 shrink-0" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </PopoverContent>
                  </PopoverPortal>
                </PopoverRoot>
              </div>
            </div>
          </div>

          <div class="grid overflow-hidden rounded-2xl border border-rose-200/80 bg-white/70 shadow-inner shadow-rose-900/5 sm:grid-cols-3">
            <div
              v-for="item in summaryCards"
              :key="item.label"
              class="flex items-center justify-between gap-3 border-b border-rose-200/80 px-4 py-3 last:border-b-0 sm:border-r sm:border-b-0 sm:last:border-r-0"
              :class="item.surfaceClass"
            >
              <div class="min-w-0">
                <p class="truncate text-[11px] font-semibold uppercase tracking-[0.16em]" :class="item.labelClass">
                  {{ item.label }}
                </p>
                <p class="mt-1 truncate font-(--font-display) text-2xl leading-none text-(--color-heading)">
                  {{ item.value }}
                </p>
              </div>
              <component :is="item.icon" class="size-5 shrink-0" :class="item.iconClass" />
            </div>
          </div>
        </CardHeader>
      </Card>

      <LoadingSpinner
        v-if="loading && !students.length"
        full-screen
        message="Loading students..."
      />

      <Alert v-else-if="error" variant="destructive">
        <TriangleAlert />
        <AlertTitle>Students unavailable</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Card v-else class="gap-0 overflow-hidden border-rose-200/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5">
        <CardHeader class="border-b border-rose-200/80 bg-linear-to-r from-white via-rose-50/60 to-white p-0!">
          <div class="flex min-h-14 flex-wrap items-center justify-between gap-3 px-5 py-3">
            <div class="flex min-w-0 flex-wrap items-center gap-3">
              <CardTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
                Class Lists
              </CardTitle>
              <Badge class="rounded-full border border-primary/15 bg-primary/10 px-3 py-1 text-primary hover:bg-primary/10">
                {{ filteredStudents.length }} {{ filteredStudents.length === 1 ? 'learner' : 'learners' }}
              </Badge>
              <span class="hidden truncate text-sm text-muted-foreground lg:inline">
                Open learner details in a modal without leaving the list.
              </span>
            </div>

            <Badge
              variant="outline"
              class="rounded-full px-3 py-1"
              :class="flaggedCount ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'"
            >
              {{ flaggedCount }} flagged
            </Badge>
          </div>
        </CardHeader>

        <CardContent class="p-0">
          <template v-if="filteredStudents.length">
            <Table class="min-w-205 table-fixed">
                <colgroup>
                  <col class="w-[40%]">
                  <col class="w-[30%]">
                  <col class="w-[20%]">
                  <col class="w-[10%]">
                </colgroup>
                <TableHeader class="bg-rose-50/60">
                  <TableRow class="hover:bg-transparent">
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Learner
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Progress
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Activity
                    </TableHead>
                    <TableHead class="px-5 py-2 text-left text-[11px] font-semibold text-rose-900/60 uppercase tracking-[0.16em]">
                      Action
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="student in filteredStudents"
                    :key="student.uid"
                    class="transition hover:bg-rose-50/45"
                  >
                    <TableCell class="px-5 py-3 align-middle">
                      <div class="flex min-w-0 items-center gap-3">
                        <div
                          class="flex size-9 shrink-0 items-center justify-center rounded-xl border text-sm font-semibold"
                          :class="student.is_flagged ? 'border-red-200 bg-red-50 text-red-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'"
                        >
                          {{ student.display_name.slice(0, 1).toUpperCase() }}
                        </div>

                        <div class="min-w-0">
                          <div class="flex min-w-0 flex-wrap items-center gap-2">
                            <p class="truncate font-semibold text-(--color-heading)">
                              {{ student.display_name }}
                            </p>
                            <Badge
                              class="rounded-full border px-2.5 py-1 text-xs"
                              :class="student.is_flagged ? 'border-red-200 bg-red-50 text-red-700 hover:bg-red-50' : 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50'"
                            >
                              {{ student.is_flagged ? 'Needs review' : 'On track' }}
                            </Badge>
                          </div>
                          <p class="truncate text-xs text-muted-foreground">
                            {{ student.email }}
                          </p>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell class="px-5 py-3 align-middle">
                      <div class="w-full max-w-72">
                        <div class="grid grid-cols-[minmax(120px,220px)_3rem] items-center gap-3">
                          <div class="h-1.5 overflow-hidden rounded-full bg-rose-100">
                            <div
                              class="h-full rounded-full"
                              :class="progressToneClass(student)"
                              :style="{ width: `${student.overall_average}%` }"
                            />
                          </div>
                          <span class="text-left text-sm font-semibold leading-none tabular-nums text-(--color-heading)">
                            {{ student.overall_average.toFixed(0) }}%
                          </span>
                        </div>
                        <p class="mt-1 text-xs text-muted-foreground">Overall accuracy</p>
                      </div>
                    </TableCell>

                    <TableCell class="px-5 py-3 align-middle">
                      <p class="font-semibold tabular-nums text-(--color-heading)">
                        {{ student.total_attempts }}
                        <span class="font-normal text-muted-foreground">attempts</span>
                      </p>
                      <p class="mt-1 text-xs text-muted-foreground">
                        {{ student.streak_days }} day streak
                      </p>
                    </TableCell>

                    <TableCell class="px-5 py-3 text-left align-middle">
                      <div class="flex justify-start">
                        <Button class="border-primary/25 bg-white text-primary shadow-xs shadow-rose-900/5 hover:bg-primary/10 hover:text-primary" variant="outline" size="sm" @click="openStudentDetail(student.uid)">
                          <Eye data-icon="inline-start" />
                          <span>View</span>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
          </template>

          <div v-else class="p-5">
            <Alert class="border-sky-200 bg-sky-50 text-sky-950">
              <UserRoundSearch />
              <AlertTitle>{{ students.length ? 'No students match these filters' : 'No students in this class' }}</AlertTitle>
              <AlertDescription>
                {{ students.length ? 'Adjust the search input or clear filters to see more learners.' : 'Switch the active class or invite learners before scanning progress.' }}
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>

      <StudentDetailDialog
        v-model:open="detailModalOpen"
        :student="selectedStudent"
        :drilldown="drilldown"
        :loading="drilldownLoading"
      />

      <!-- Mobile filter sheet -->
      <Sheet v-model:open="filterSheetOpen">
        <SheetContent side="bottom" class="flex max-h-[85svh] flex-col gap-0 rounded-t-2xl border-border/80 p-0">
          <!-- Handle -->
          <div class="flex shrink-0 justify-center pb-2 pt-3">
            <div class="h-1 w-10 rounded-full bg-border" />
          </div>

          <!-- Header -->
          <div class="flex shrink-0 items-center justify-between gap-3 px-4 pb-3">
            <div>
              <SheetTitle class="text-sm font-semibold text-(--color-heading)">Filters</SheetTitle>
              <p class="text-xs text-muted-foreground">{{ filteredStudents.length }} visible</p>
            </div>
            <Button
              v-if="activeFilterCount"
              variant="ghost"
              size="sm"
              class="h-8 px-2 text-xs text-muted-foreground hover:text-primary"
              @click="clearStudentFilters"
            >
              Clear
            </Button>
          </div>

          <Separator class="shrink-0" />

          <!-- Filter groups — scrollable -->
          <div class="flex flex-1 flex-col gap-3 overflow-y-auto p-4 pb-8">
            <!-- Status -->
            <div>
              <p class="mb-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Status</p>
              <div class="grid gap-1">
                <button
                  v-for="option in statusFilterOptions"
                  :key="option.value"
                  type="button"
                  class="flex items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                  :class="studentStatusFilter === option.value ? 'bg-primary text-primary-foreground' : 'text-(--color-heading) hover:bg-rose-50'"
                  @click="studentStatusFilter = option.value"
                >
                  <span class="flex min-w-0 items-center gap-2">
                    <span class="size-2 shrink-0 rounded-full" :class="studentStatusFilter === option.value ? 'bg-primary-foreground/70' : option.value === 'needs-review' ? 'bg-red-500' : option.value === 'on-track' ? 'bg-emerald-500' : 'bg-muted-foreground/40'" />
                    <span class="truncate">{{ option.label }}</span>
                  </span>
                  <span class="ml-2 shrink-0 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold leading-none tabular-nums" :class="studentStatusFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                </button>
              </div>
            </div>

            <!-- Activity -->
            <div>
              <p class="mb-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Activity</p>
              <div class="grid gap-1">
                <button
                  v-for="option in activityFilterOptions"
                  :key="option.value"
                  type="button"
                  class="flex items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                  :class="activityFilter === option.value ? 'bg-primary text-primary-foreground' : 'text-(--color-heading) hover:bg-rose-50'"
                  @click="activityFilter = option.value"
                >
                  <span class="flex min-w-0 items-center gap-2">
                    <span class="size-2 shrink-0 rounded-full" :class="activityFilter === option.value ? 'bg-primary-foreground/70' : option.value === 'active' ? 'bg-sky-500' : option.value === 'no-attempts' ? 'bg-rose-400' : 'bg-muted-foreground/40'" />
                    <span class="truncate">{{ option.label }}</span>
                  </span>
                  <span class="ml-2 shrink-0 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold leading-none tabular-nums" :class="activityFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                </button>
              </div>
            </div>

            <!-- Score -->
            <div>
              <p class="mb-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Score</p>
              <div class="grid grid-cols-2 gap-1">
                <button
                  v-for="option in scoreFilterOptions"
                  :key="option.value"
                  type="button"
                  class="flex items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                  :class="scoreBandFilter === option.value ? 'bg-primary text-primary-foreground' : 'text-(--color-heading) hover:bg-rose-50'"
                  @click="scoreBandFilter = option.value"
                >
                  <span class="flex min-w-0 items-center gap-2">
                    <span class="size-2 shrink-0 rounded-full" :class="scoreBandDotClass(option.value, scoreBandFilter === option.value)" />
                    <span class="truncate">{{ option.label }}</span>
                  </span>
                  <span class="ml-2 shrink-0 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold leading-none tabular-nums" :class="scoreBandFilter === option.value ? 'border-primary-foreground/35 bg-primary-foreground/20 text-primary-foreground' : 'border-primary/20 bg-primary/10 text-primary'">{{ option.count }}</span>
                </button>
              </div>
            </div>

            <!-- Sort -->
            <div>
              <p class="mb-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Sort</p>
              <div class="grid grid-cols-2 gap-1">
                <button
                  v-for="option in sortOptions"
                  :key="option.value"
                  type="button"
                  class="flex items-center justify-between gap-2 rounded-xl px-3 py-2.5 text-left text-sm transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer"
                  :class="studentSort === option.value ? 'bg-primary text-primary-foreground' : 'text-(--color-heading) hover:bg-rose-50'"
                  @click="studentSort = option.value"
                >
                  <span class="truncate">{{ option.label }}</span>
                  <Check v-if="studentSort === option.value" class="size-3.5 shrink-0" />
                </button>
              </div>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  </InstructorLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  ChartColumn,
  Check,
  Eye,
  Funnel,
  Search,
  TriangleAlert,
  UserRoundSearch,
  Users,
} from 'lucide-vue-next'
import {
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
} from 'reka-ui'

import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import StudentDetailDialog from '@/components/instructor/StudentDetailDialog.vue'
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from '@/components/ui/sheet'
import { getAllStudents, getStudentDrillDown } from '@/api/analytics'
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
import { Separator } from '@/components/ui/separator'
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
import type { StudentDrillDown, StudentStat } from '@/types'

type StudentStatusFilter = 'all' | 'needs-review' | 'on-track'
type ScoreBandFilter = 'all' | 'high' | 'steady' | 'watch' | 'at-risk'
type ActivityFilter = 'all' | 'active' | 'no-attempts'
type StudentSort = 'name-asc' | 'score-asc' | 'score-desc' | 'attempts-desc' | 'streak-desc'

const classesStore = useClassesStore()

const students = ref<StudentStat[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const search = ref('')
const studentStatusFilter = ref<StudentStatusFilter>('all')
const scoreBandFilter = ref<ScoreBandFilter>('all')
const activityFilter = ref<ActivityFilter>('all')
const studentSort = ref<StudentSort>('name-asc')
const filterSheetOpen = ref(false)
const selectedStudentUid = ref<string | null>(null)
const drilldown = ref<StudentDrillDown | null>(null)
const drilldownLoading = ref(false)
const detailModalOpen = ref(false)

const filteredStudents = computed(() => {
  const query = search.value.trim().toLowerCase()

  return students.value
    .filter((student) => (
      !query
      || student.display_name.toLowerCase().includes(query)
      || student.email.toLowerCase().includes(query)
    ))
    .filter((student) => studentMatchesStatus(student, studentStatusFilter.value))
    .filter((student) => studentMatchesScoreBand(student, scoreBandFilter.value))
    .filter((student) => studentMatchesActivity(student, activityFilter.value))
    .slice()
    .sort(sortStudents)
})

const selectedStudent = computed(
  () => students.value.find((student) => student.uid === selectedStudentUid.value) ?? null,
)

const flaggedCount = computed(() => students.value.filter((student) => student.is_flagged).length)
const activeFilterCount = computed(() => [
  studentStatusFilter.value !== 'all',
  scoreBandFilter.value !== 'all',
  activityFilter.value !== 'all',
  studentSort.value !== 'name-asc',
].filter(Boolean).length)

const statusFilterOptions = computed(() => [
  {
    value: 'all' as const,
    label: 'All',
    count: students.value.length,
  },
  {
    value: 'needs-review' as const,
    label: 'Needs review',
    count: students.value.filter((student) => student.is_flagged).length,
  },
  {
    value: 'on-track' as const,
    label: 'On track',
    count: students.value.filter((student) => !student.is_flagged).length,
  },
])

const scoreFilterOptions = computed(() => [
  {
    value: 'all' as const,
    label: 'All scores',
    count: students.value.length,
  },
  {
    value: 'high' as const,
    label: 'High',
    count: students.value.filter((student) => scoreBand(student) === 'high').length,
  },
  {
    value: 'steady' as const,
    label: 'Steady',
    count: students.value.filter((student) => scoreBand(student) === 'steady').length,
  },
  {
    value: 'watch' as const,
    label: 'Watch',
    count: students.value.filter((student) => scoreBand(student) === 'watch').length,
  },
  {
    value: 'at-risk' as const,
    label: 'At risk',
    count: students.value.filter((student) => scoreBand(student) === 'at-risk').length,
  },
])

const activityFilterOptions = computed(() => [
  {
    value: 'all' as const,
    label: 'All activity',
    count: students.value.length,
  },
  {
    value: 'active' as const,
    label: 'Has attempts',
    count: students.value.filter((student) => student.total_attempts > 0).length,
  },
  {
    value: 'no-attempts' as const,
    label: 'No attempts',
    count: students.value.filter((student) => student.total_attempts === 0).length,
  },
])

const sortOptions = [
  {
    value: 'name-asc' as const,
    label: 'Name A-Z',
  },
  {
    value: 'score-desc' as const,
    label: 'Highest score',
  },
  {
    value: 'score-asc' as const,
    label: 'Lowest score',
  },
  {
    value: 'attempts-desc' as const,
    label: 'Most attempts',
  },
  {
    value: 'streak-desc' as const,
    label: 'Longest streak',
  },
]

const summaryCards = computed(() => [
  {
    label: 'Students',
    value: `${students.value.length}`,
    icon: Users,
    surfaceClass: 'bg-emerald-50/40',
    labelClass: 'text-emerald-800/70',
    iconClass: 'text-emerald-700',
  },
  {
    label: 'Flagged',
    value: `${flaggedCount.value}`,
    icon: TriangleAlert,
    surfaceClass: flaggedCount.value ? 'bg-amber-50/55' : 'bg-rose-50/25',
    labelClass: flaggedCount.value ? 'text-amber-800/75' : 'text-rose-900/55',
    iconClass: flaggedCount.value ? 'text-amber-700' : 'text-rose-700/60',
  },
  {
    label: 'Search results',
    value: `${filteredStudents.value.length}`,
    icon: ChartColumn,
    surfaceClass: 'bg-sky-50/45',
    labelClass: 'text-sky-800/70',
    iconClass: 'text-sky-700',
  },
])


function scoreBandDotClass(band: ScoreBandFilter, active: boolean): string {
  if (active) return 'bg-primary-foreground/70'
  if (band === 'high') return 'bg-emerald-500'
  if (band === 'steady') return 'bg-sky-500'
  if (band === 'watch') return 'bg-amber-500'
  if (band === 'at-risk') return 'bg-red-500'
  return 'bg-muted-foreground/40'
}

function scoreBand(student: StudentStat): Exclude<ScoreBandFilter, 'all'> {
  if (student.overall_average >= 85) return 'high'
  if (student.overall_average >= 70) return 'steady'
  if (student.overall_average >= 55) return 'watch'
  return 'at-risk'
}

function studentMatchesStatus(student: StudentStat, filter: StudentStatusFilter) {
  if (filter === 'needs-review') return student.is_flagged
  if (filter === 'on-track') return !student.is_flagged
  return true
}

function studentMatchesScoreBand(student: StudentStat, filter: ScoreBandFilter) {
  if (filter === 'all') return true
  return scoreBand(student) === filter
}

function studentMatchesActivity(student: StudentStat, filter: ActivityFilter) {
  if (filter === 'active') return student.total_attempts > 0
  if (filter === 'no-attempts') return student.total_attempts === 0
  return true
}

function sortStudents(left: StudentStat, right: StudentStat) {
  if (studentSort.value === 'score-desc') {
    return right.overall_average - left.overall_average || left.display_name.localeCompare(right.display_name)
  }
  if (studentSort.value === 'score-asc') {
    return left.overall_average - right.overall_average || left.display_name.localeCompare(right.display_name)
  }
  if (studentSort.value === 'attempts-desc') {
    return right.total_attempts - left.total_attempts || left.display_name.localeCompare(right.display_name)
  }
  if (studentSort.value === 'streak-desc') {
    return right.streak_days - left.streak_days || left.display_name.localeCompare(right.display_name)
  }
  return left.display_name.localeCompare(right.display_name)
}

function clearStudentFilters() {
  studentStatusFilter.value = 'all'
  scoreBandFilter.value = 'all'
  activityFilter.value = 'all'
  studentSort.value = 'name-asc'
}


function progressToneClass(student: StudentStat) {
  if (student.is_flagged || student.overall_average < 55) return 'bg-red-500'
  if (student.overall_average < 70) return 'bg-amber-500'
  return 'bg-emerald-600'
}


async function openStudentDetail(uid: string) {
  const classId = classesStore.activeClassId
  if (!classId) return

  selectedStudentUid.value = uid
  drilldown.value = null
  detailModalOpen.value = true
  drilldownLoading.value = true

  try {
    drilldown.value = await getStudentDrillDown(uid, classId)
  } catch {
    drilldown.value = null
  } finally {
    drilldownLoading.value = false
  }
}

async function loadStudents(classId: string | null) {
  students.value = []
  selectedStudentUid.value = null
  drilldown.value = null
  detailModalOpen.value = false
  error.value = null

  if (!classId) {
    error.value = 'Create or select a class from Classes to load students.'
    return
  }

  loading.value = true
  try {
    students.value = await getAllStudents(classId)
  } catch {
    error.value = 'Failed to load students.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
  } catch {
    error.value = 'Failed to load your classes.'
  }
  await loadStudents(classesStore.activeClassId)
})

watch(
  () => classesStore.activeClassId,
  (classId, previousClassId) => {
    if (classId === previousClassId) return
    void loadStudents(classId)
  },
)
</script>

<script setup lang="ts">
import { CalendarClock, Check, Funnel, Search, Trash2 } from 'lucide-vue-next'
import {
  SelectContent,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectViewport,
} from 'reka-ui'

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

const props = defineProps<{
  items: AssignmentSetNavigatorItem[]
  selectedExerciseId: string | null
  search: string
  filter: AssignmentSetFilter
  filterOptions: {
    value: AssignmentSetFilter
    label: string
    count: number
  }[]
}>()

const emit = defineEmits<{
  'update:search': [value: string]
  'update:filter': [value: AssignmentSetFilter]
  selectAssignment: [exerciseId: string]
  deleteAssignment: [exerciseId: string]
}>()

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function statusLabel(status: AssignmentSetStatus) {
  if (status === 'needs-grading') return 'Needs grading'
  if (status === 'completed') return 'Completed'
  return 'Active'
}

function assignmentStatusTone(status: AssignmentSetStatus) {
  if (status === 'needs-grading') {
    return {
      badge: 'border-amber-300/70 bg-amber-100/80 text-amber-900',
      rail: 'bg-amber-500',
      progress: 'bg-amber-500',
    }
  }

  if (status === 'completed') {
    return {
      badge: 'border-emerald-300/70 bg-emerald-100/80 text-emerald-900',
      rail: 'bg-emerald-500',
      progress: 'bg-emerald-500',
    }
  }

  return {
    badge: 'border-sky-300/70 bg-sky-100/80 text-sky-900',
    rail: 'bg-sky-500',
    progress: 'bg-sky-500',
  }
}

function isOverdue(item: AssignmentSetNavigatorItem) {
  return Boolean(item.dueDate && item.status !== 'completed' && new Date(item.dueDate).getTime() < Date.now())
}

function dueDateTone(item: AssignmentSetNavigatorItem) {
  return isOverdue(item)
    ? 'border-red-300/70 bg-red-50 text-red-800'
    : 'border-border/80 bg-background/75 text-muted-foreground'
}

function handleFilterUpdate(value: unknown) {
  emit('update:filter', (typeof value === 'string' ? value : 'all') as AssignmentSetFilter)
}
</script>

<template>
  <Card class="gap-0 overflow-hidden border-border/80 bg-card/95 py-0 shadow-sm shadow-rose-900/5 xl:sticky xl:top-4 xl:self-start">
    <CardHeader class="border-b border-border/70 p-4">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <CardTitle class="font-(--font-display) text-xl leading-none text-(--color-heading)">
            Assignment sets
          </CardTitle>
          <CardDescription class="mt-1 text-sm">
            Choose one assignment to review.
          </CardDescription>
        </div>
        <Badge variant="outline" class="shrink-0 rounded-full px-3 py-1">
          {{ items.length }} shown
        </Badge>
      </div>

      <div class="mt-4 grid grid-cols-[minmax(0,1fr)_2.5rem] items-center gap-2">
        <div class="flex h-10 min-w-0 items-center gap-2 rounded-xl border border-border bg-background px-3">
          <Search class="size-4 shrink-0 text-muted-foreground" />
          <Input
            :model-value="search"
            class="h-8 rounded-none border-0 bg-transparent px-0 text-sm shadow-none ring-0 outline-none focus-visible:border-transparent! focus-visible:shadow-none! focus-visible:ring-0! focus-visible:ring-offset-0! focus-visible:outline-none!"
            placeholder="Search assignments"
            @update:model-value="emit('update:search', String($event))"
          />
        </div>

        <SelectRoot
          :model-value="filter"
          @update:model-value="handleFilterUpdate"
        >
          <SelectTrigger
            aria-label="Filter assignment sets"
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
              class="z-50 w-64 overflow-hidden rounded-xl border bg-popover text-popover-foreground shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
            >
              <SelectViewport class="p-1">
                <SelectItem
                  v-for="option in filterOptions"
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
    </CardHeader>

    <CardContent class="p-0">
      <div v-if="items.length" class="max-h-136 overflow-y-auto xl:max-h-[calc(100dvh-20rem)]">
        <div class="divide-y divide-border/60">
          <div
            v-for="item in items"
            :key="item.exerciseId"
            class="relative grid grid-cols-[minmax(0,1fr)_2rem] gap-2 px-3 py-2.5 transition"
            :class="selectedExerciseId === item.exerciseId ? 'bg-secondary/80 ring-2 ring-inset ring-primary/25' : 'hover:bg-muted/20'"
          >
            <span
              aria-hidden="true"
              class="absolute left-0 top-3 h-[calc(100%-1.5rem)] w-1 rounded-r-full"
              :class="selectedExerciseId === item.exerciseId ? 'bg-primary' : assignmentStatusTone(item.status).rail"
            />
            <span
              v-if="selectedExerciseId === item.exerciseId"
              aria-hidden="true"
              class="absolute left-2 top-2 z-10 flex size-6 items-center justify-center rounded-full border border-primary/25 bg-primary text-primary-foreground shadow-sm shadow-primary/20"
            >
              <Check class="size-3.5" />
            </span>
            <button
              type="button"
              class="min-w-0 rounded-xl py-1 pr-1 text-left focus-visible:ring-ring/50 focus-visible:ring-[3px] focus-visible:outline-none"
              :class="selectedExerciseId === item.exerciseId ? 'pl-8' : 'pl-2'"
              :aria-current="selectedExerciseId === item.exerciseId ? 'true' : undefined"
              @click="emit('selectAssignment', item.exerciseId)"
            >
              <div class="flex min-w-0 items-start justify-between gap-2">
                <div class="min-w-0">
                  <p
                    class="truncate font-semibold"
                    :class="selectedExerciseId === item.exerciseId ? 'text-primary' : 'text-(--color-heading)'"
                  >
                    {{ item.title }}
                  </p>
                  <p class="mt-0.5 truncate text-xs text-muted-foreground tabular-nums">
                    {{ item.submittedCount }} submissions · {{ item.phraseCount }} phrases · {{ item.studentCount }} students
                  </p>
                </div>
                <div class="flex shrink-0 flex-col items-end gap-1">
                  <Badge
                    variant="outline"
                    class="rounded-full px-2 py-0.5 text-[11px]"
                    :class="assignmentStatusTone(item.status).badge"
                  >
                    {{ statusLabel(item.status) }}
                  </Badge>
                </div>
              </div>

              <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
                <Badge
                  variant="outline"
                  class="rounded-full px-2 py-0.5 text-[11px]"
                  :class="dueDateTone(item)"
                >
                  <CalendarClock class="mr-1 size-3" />
                  {{ item.dueDate ? `${isOverdue(item) ? 'Overdue ' : ''}${formatDate(item.dueDate)}` : 'No due date' }}
                </Badge>
                <Badge variant="outline" class="rounded-full border-amber-300/60 bg-amber-50/75 px-2 py-0.5 text-[11px] text-amber-900">
                  {{ item.pendingCount }} pending
                </Badge>
                <Badge variant="outline" class="rounded-full border-emerald-300/60 bg-emerald-50/75 px-2 py-0.5 text-[11px] text-emerald-900">
                  {{ item.gradedCount }} graded
                </Badge>
              </div>

              <div class="mt-2.5 grid grid-cols-[minmax(0,1fr)_2.75rem] items-center gap-2">
                <div class="h-1.5 overflow-hidden rounded-full bg-border/70">
                  <div
                    class="h-full rounded-full transition-[width]"
                    :class="assignmentStatusTone(item.status).progress"
                    :style="{ width: `${item.completionPercent}%` }"
                  />
                </div>
                <span class="text-right text-xs font-semibold tabular-nums text-(--color-heading)">
                  {{ item.completionPercent.toFixed(0) }}%
                </span>
              </div>
            </button>

            <Button
              variant="outline"
              size="icon"
              class="mt-1 size-8 rounded-xl text-muted-foreground hover:border-red-200 hover:bg-red-50 hover:text-red-700"
              @click="emit('deleteAssignment', item.exerciseId)"
            >
              <Trash2 />
              <span class="sr-only">Delete assignment</span>
            </Button>
          </div>
        </div>
      </div>

      <div v-else class="p-4">
        <div class="rounded-2xl border border-border/70 bg-muted/25 p-4">
          <p class="font-semibold text-(--color-heading)">No matching assignments</p>
          <p class="mt-1 text-sm text-muted-foreground">
            Adjust the search or filter to find another assignment.
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

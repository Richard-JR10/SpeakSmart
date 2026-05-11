<script setup lang="ts">
import { SquarePen } from 'lucide-vue-next'

import {
  assignmentGroupStatus,
  assignmentSuggestedOverall,
  assignmentTeacherOverall,
  type AssignmentReviewGroup,
  type AssignmentReviewStatus,
} from './assignmentReview'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

defineProps<{
  groups: AssignmentReviewGroup[]
}>()

const emit = defineEmits<{
  reviewStudent: [group: AssignmentReviewGroup]
}>()

function statusLabel(status: AssignmentReviewStatus) {
  if (status === 'ready') return 'Ready to grade'
  if (status === 'partial') return 'Partially graded'
  if (status === 'graded') return 'Graded'
  return 'Incomplete'
}

function reviewStatusTone(status: AssignmentReviewStatus) {
  if (status === 'graded') return 'border-emerald-300/70 bg-emerald-100/80 text-emerald-900'
  if (status === 'ready') return 'border-amber-300/70 bg-amber-100/80 text-amber-900'
  if (status === 'partial') return 'border-sky-300/70 bg-sky-100/80 text-sky-900'
  return 'border-border/80 bg-background text-muted-foreground'
}

function teacherScoreTone(group: AssignmentReviewGroup) {
  return assignmentTeacherOverall(group) == null
    ? 'border-amber-300/60 bg-amber-50/75 text-amber-900'
    : 'border-emerald-300/60 bg-emerald-50/75 text-emerald-900'
}
</script>

<template>
  <div class="overflow-x-auto">
    <Table class="min-w-[900px] table-fixed">
      <colgroup>
        <col class="w-[26%]">
        <col class="w-[16%]">
        <col class="w-[16%]">
        <col class="w-[16%]">
        <col class="w-[16%]">
        <col class="w-[10%]">
      </colgroup>
      <TableHeader class="bg-muted/20">
        <TableRow class="hover:bg-transparent">
          <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Student</TableHead>
          <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Submitted</TableHead>
          <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Suggested</TableHead>
          <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Teacher</TableHead>
          <TableHead class="px-4 py-2 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Status</TableHead>
          <TableHead class="px-4 py-2 text-right text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Action</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow
          v-for="group in groups"
          :key="group.key"
          class="transition hover:bg-muted/25"
        >
          <TableCell class="px-4 py-3 align-middle">
            <p class="truncate font-semibold text-(--color-heading)">
              {{ group.studentDisplayName }}
            </p>
            <p v-if="group.studentEmail" class="truncate text-xs text-muted-foreground">
              {{ group.studentEmail }}
            </p>
          </TableCell>
          <TableCell class="px-4 py-3 align-middle">
            <span class="text-sm font-semibold text-(--color-heading)">
              {{ group.submittedCount }}/{{ group.requiredCount }}
            </span>
            <span class="ml-1 text-xs text-muted-foreground">phrases</span>
          </TableCell>
          <TableCell class="px-4 py-3 align-middle">
            <Badge variant="outline" class="rounded-full px-2.5 py-1">
              {{ assignmentSuggestedOverall(group) == null ? 'Not ready' : `${assignmentSuggestedOverall(group)}%` }}
            </Badge>
          </TableCell>
          <TableCell class="px-4 py-3 align-middle">
            <Badge
              variant="outline"
              class="rounded-full px-2.5 py-1"
              :class="teacherScoreTone(group)"
            >
              {{ assignmentTeacherOverall(group) == null ? 'Unreleased' : `${assignmentTeacherOverall(group)}%` }}
            </Badge>
          </TableCell>
          <TableCell class="px-4 py-3 align-middle">
            <Badge
              variant="outline"
              class="rounded-full px-2.5 py-1"
              :class="reviewStatusTone(assignmentGroupStatus(group))"
            >
              {{ statusLabel(assignmentGroupStatus(group)) }}
            </Badge>
          </TableCell>
          <TableCell class="px-4 py-3 align-middle">
            <div class="flex justify-end">
              <Button
                size="sm"
                :variant="assignmentGroupStatus(group) === 'graded' ? 'outline' : 'default'"
                :disabled="group.submittedCount === 0"
                @click="emit('reviewStudent', group)"
              >
                <SquarePen data-icon="inline-start" />
                <span>{{ assignmentGroupStatus(group) === 'graded' ? 'Edit' : 'Review' }}</span>
              </Button>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>

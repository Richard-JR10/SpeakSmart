import type { Exercise, InstructorAssignmentSubmission, Phrase, StudentStat } from '@/types'

export type AssignmentReviewStatus = 'incomplete' | 'ready' | 'partial' | 'graded'

export interface AssignmentPhraseReviewDraft {
  teacher_accuracy_score: string
  teacher_feedback_text: string
}

export interface AssignmentReviewPhrase {
  phraseId: string
  phrase: Phrase | null
  submission: InstructorAssignmentSubmission | null
}

export interface AssignmentReviewGroup {
  key: string
  exerciseId: string
  studentUid: string
  studentDisplayName: string
  studentEmail: string | null
  requiredCount: number
  submittedCount: number
  phrases: AssignmentReviewPhrase[]
}

export function buildAssignmentReviewGroups(
  exercise: Exercise,
  students: StudentStat[],
  submissions: InstructorAssignmentSubmission[],
  phraseById: Record<string, Phrase>,
): AssignmentReviewGroup[] {
  const studentByUid = new Map(students.map((student) => [student.uid, student]))
  const submissionsByStudent = new Map<string, InstructorAssignmentSubmission[]>()

  for (const submission of submissions) {
    const studentSubmissions = submissionsByStudent.get(submission.student_uid) ?? []
    studentSubmissions.push(submission)
    submissionsByStudent.set(submission.student_uid, studentSubmissions)
  }

  const assignedStudentUids = new Set(exercise.assignments.map((assignment) => assignment.student_uid))
  for (const submission of submissions) {
    assignedStudentUids.add(submission.student_uid)
  }

  const requiredPhraseIds = exercise.phrases.map((phrase) => phrase.phrase_id)

  return Array.from(assignedStudentUids)
    .map((studentUid) => {
      const studentSubmissions = submissionsByStudent.get(studentUid) ?? []
      const submissionsByPhrase = new Map(
        studentSubmissions.map((submission) => [submission.phrase_id, submission]),
      )
      const student = studentByUid.get(studentUid)
      const firstSubmission = studentSubmissions[0]
      const phrases = requiredPhraseIds.map((phraseId) => ({
        phraseId,
        phrase: phraseById[phraseId] ?? null,
        submission: submissionsByPhrase.get(phraseId) ?? null,
      }))

      return {
        key: `${exercise.exercise_id}:${studentUid}`,
        exerciseId: exercise.exercise_id,
        studentUid,
        studentDisplayName: student?.display_name ?? firstSubmission?.student_display_name ?? studentUid,
        studentEmail: student?.email ?? null,
        requiredCount: requiredPhraseIds.length,
        submittedCount: phrases.filter((phrase) => phrase.submission).length,
        phrases,
      }
    })
    .sort((left, right) => {
      const statusRank = statusSortRank(assignmentGroupStatus(left)) - statusSortRank(assignmentGroupStatus(right))
      if (statusRank !== 0) return statusRank
      return left.studentDisplayName.localeCompare(right.studentDisplayName)
    })
}

export function assignmentGroupStatus(group: AssignmentReviewGroup): AssignmentReviewStatus {
  if (group.submittedCount < group.requiredCount) return 'incomplete'

  const submittedPhrases = group.phrases.filter((phrase) => phrase.submission)
  const releasedCount = submittedPhrases.filter((phrase) => phrase.submission?.released_at).length

  if (releasedCount === submittedPhrases.length && submittedPhrases.length > 0) return 'graded'
  if (releasedCount > 0) return 'partial'
  return 'ready'
}

export function assignmentSuggestedOverall(group: AssignmentReviewGroup): number | null {
  const scores = group.phrases
    .map((phrase) => phrase.submission?.suggested_accuracy_score)
    .filter((score): score is number => score != null)

  return averageRounded(scores)
}

export function assignmentTeacherOverall(group: AssignmentReviewGroup): number | null {
  const scores = group.phrases
    .filter((phrase) => phrase.submission?.released_at)
    .map((phrase) => phrase.submission?.teacher_accuracy_score)
    .filter((score): score is number => score != null)

  return averageRounded(scores)
}

export function assignmentDraftOverall(
  group: AssignmentReviewGroup,
  drafts: Record<string, AssignmentPhraseReviewDraft>,
): number | null {
  const scores = group.phrases
    .map((phrase) => {
      if (!phrase.submission) return null
      const draftScore = Number(drafts[phrase.submission.submission_id]?.teacher_accuracy_score)
      return Number.isFinite(draftScore) ? draftScore : null
    })
    .filter((score): score is number => score != null)

  return averageRounded(scores)
}

export function gradeableSubmissions(group: AssignmentReviewGroup): InstructorAssignmentSubmission[] {
  return group.phrases
    .map((phrase) => phrase.submission)
    .filter((submission): submission is InstructorAssignmentSubmission => Boolean(submission))
}

export function unreleasedGradeableSubmissions(group: AssignmentReviewGroup): InstructorAssignmentSubmission[] {
  return group.phrases
    .map((phrase) => phrase.submission)
    .filter((submission): submission is InstructorAssignmentSubmission => Boolean(submission && !submission.released_at))
}

export function isBulkSuggestedGradeableGroup(group: AssignmentReviewGroup): boolean {
  return assignmentGroupStatus(group) === 'ready' && unreleasedGradeableSubmissions(group).length > 0
}

export function phraseDisplayLabel(phrase: AssignmentReviewPhrase): string {
  if (!phrase.phrase) return phrase.phraseId
  return `${phrase.phrase.japanese_text} - ${phrase.phrase.romaji}`
}

function averageRounded(scores: number[]): number | null {
  if (!scores.length) return null
  return Math.round(scores.reduce((total, score) => total + score, 0) / scores.length)
}

function statusSortRank(status: AssignmentReviewStatus) {
  if (status === 'ready') return 0
  if (status === 'partial') return 1
  if (status === 'incomplete') return 2
  return 3
}

import api from './axios'
import type {
  AssignmentSubmission,
  InstructorAssignmentSubmission,
  StudentAssignment,
} from '@/types'
import { convertAudioBlobToWav } from '@/utils/audio'

export const getStudentAssignments = async (
  studentUid: string,
): Promise<StudentAssignment[]> => {
  const res = await api.get(`/api/v1/exercises/student/${studentUid}/assignments`)
  return res.data
}

export const submitAssignmentPhrase = async (
  exerciseId: string,
  phraseId: string,
  audioBlob: Blob,
): Promise<AssignmentSubmission> => {
  const wavBlob = await convertAudioBlobToWav(audioBlob)
  const formData = new FormData()
  formData.append('phrase_id', phraseId)
  formData.append('audio_file', wavBlob, 'assignment-recording.wav')

  const res = await api.post(`/api/v1/exercises/${exerciseId}/submissions`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
  return res.data
}

export const getExerciseSubmissions = async (
  exerciseId: string,
): Promise<InstructorAssignmentSubmission[]> => {
  const res = await api.get(`/api/v1/exercises/${exerciseId}/submissions`)
  return res.data
}

export const reviewAssignmentSubmission = async (
  submissionId: string,
  data: {
    teacher_accuracy_score: number
    teacher_feedback_text: string
    release_to_student?: boolean
  },
): Promise<InstructorAssignmentSubmission> => {
  const res = await api.patch(`/api/v1/exercises/submissions/${submissionId}/review`, data)
  return res.data
}

export const releaseAssignmentSubmission = async (
  submissionId: string,
): Promise<InstructorAssignmentSubmission> => {
  const res = await api.post(`/api/v1/exercises/submissions/${submissionId}/release`)
  return res.data
}

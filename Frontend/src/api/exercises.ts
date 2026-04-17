// src/api/exercises.ts
import api from './axios'
import type { Exercise, StudentExercise } from '@/types'

export const createExercise = async (data: {
  exercise_id: string
  title: string
  phrase_ids: string[]
  student_uids: string[]
  due_date?: string
}): Promise<Exercise> => {
  const res = await api.post('/api/v1/exercises', data)
  return res.data
}

export const assignExercise = async (
  exerciseId: string,
  studentUids: string[],
): Promise<void> => {
  await api.post(`/api/v1/exercises/${exerciseId}/assign`, studentUids)
}

export const getMyExercises = async (): Promise<Exercise[]> => {
  const res = await api.get('/api/v1/exercises/instructor/mine')
  return res.data
}

export const getStudentExercises = async (
  studentUid: string,
): Promise<StudentExercise[]> => {
  const res = await api.get(`/api/v1/exercises/student/${studentUid}`)
  return res.data
}

export const markExerciseComplete = async (
  exerciseId: string,
): Promise<void> => {
  await api.patch(`/api/v1/exercises/${exerciseId}/complete`)
}

export const deleteExercise = async (exerciseId: string): Promise<void> => {
  await api.delete(`/api/v1/exercises/${exerciseId}`)
}
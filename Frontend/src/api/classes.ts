import api from './axios'
import type { ClassSummary, JoinCodeResponse } from '@/types'

export const getMyClasses = async (): Promise<ClassSummary[]> => {
  const res = await api.get('/api/v1/classes')
  return res.data
}

export const createClass = async (name: string): Promise<ClassSummary> => {
  const res = await api.post('/api/v1/classes', { name })
  return res.data
}

export const joinClass = async (joinCode: string): Promise<ClassSummary> => {
  const res = await api.post('/api/v1/classes/join', { join_code: joinCode })
  return res.data
}

export const leaveClass = async (classId: string): Promise<void> => {
  await api.delete(`/api/v1/classes/${classId}/members/me`)
}

export const removeStudentFromClass = async (
  classId: string,
  studentUid: string,
): Promise<void> => {
  await api.delete(`/api/v1/classes/${classId}/students/${studentUid}`)
}

export const regenerateJoinCode = async (
  classId: string,
): Promise<JoinCodeResponse> => {
  const res = await api.post(`/api/v1/classes/${classId}/join-code/regenerate`)
  return res.data
}

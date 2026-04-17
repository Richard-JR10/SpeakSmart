import api from './axios'
import type { ClassOverview, StudentStat, StudentDrillDown } from '@/types'

export const getClassOverview = async (
  classId: string,
  flagThreshold = 60,
): Promise<ClassOverview> => {
  const res = await api.get(`/api/v1/analytics/class/${classId}`, {
    params: { flag_threshold: flagThreshold },
  })
  return res.data
}

export const getAllStudents = async (
  classId: string,
  flagThreshold = 60,
): Promise<StudentStat[]> => {
  const res = await api.get(`/api/v1/analytics/students/${classId}`, {
    params: { flag_threshold: flagThreshold },
  })
  return res.data
}

export const getStudentDrillDown = async (
  studentUid: string,
): Promise<StudentDrillDown> => {
  const res = await api.get(`/api/v1/analytics/student/${studentUid}`)
  return res.data
}

export const getPhonemeHeatmap = async (
  classId: string,
): Promise<Record<string, {
  mora_timing_avg: number
  consonant_avg: number
  vowel_avg: number
  overall_avg: number
}>> => {
  const res = await api.get(`/api/v1/analytics/heatmap/${classId}`)
  return res.data
}
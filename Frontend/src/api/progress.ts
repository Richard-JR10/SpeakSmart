import api from "./axios"
import type { StudentDashboard, ProgressSummary } from "@/types"

export const getStudentProgress = async (
    studentUid: string,
): Promise<StudentDashboard> => {
    const res = await api.get(`/api/v1/progress/${studentUid}`)
    return res.data
}

export const getModuleProgress = async (
    studentUid: string,
    moduleId: string,
): Promise<ProgressSummary> => {
    const res = await api.get(`/api/v1/progress/${studentUid}/module/${moduleId}`)
    return res.data
}
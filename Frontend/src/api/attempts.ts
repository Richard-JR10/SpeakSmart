import api from "./axios"
import type { Attempt, AttemptSummary } from "@/types"

export const submitAttempt = async (
    phraseId: string,
    audioBlob: Blob
): Promise<Attempt> => {
    const formData = new FormData()
    formData.append("phraseId", phraseId)
    formData.append("audio", audioBlob, "recording.wav")

    const res = await api.post("/api/v1/attempts", formData,{
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000, // 60 seconds timeout for the request
    })
    return res.data;
}

export const getAttempts = async (
    studentUid: string,
    phraseId?: string,
    limit = 20,
): Promise<AttemptSummary[]> => {
    const res = await api.get(`/api/v1/atempts/${studentUid}`, {
        params: { phrase_id: phraseId, limit },
    })
    return res.data;
}


export const getAttemptDetail = async (
    studentUid: string,
    attemptId: string,
): Promise<Attempt> => {
    const res = await api.get(`/api/v1/attempts/${studentUid}/${attemptId}`)
    return res.data
}
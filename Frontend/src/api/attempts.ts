import api from "./axios"
import type { Attempt, AttemptSummary } from "@/types"
import { convertAudioBlobToWav } from "@/utils/audio"

export const submitAttempt = async (
    phraseId: string,
    audioBlob: Blob
): Promise<Attempt> => {
    const wavBlob = await convertAudioBlobToWav(audioBlob)
    const formData = new FormData()
    formData.append("phrase_id", phraseId)
    formData.append("audio_file", wavBlob, "recording.wav")

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
    const res = await api.get(`/api/v1/attempts/${studentUid}`, {
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

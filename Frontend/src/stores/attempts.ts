// src/stores/attempts.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { submitAttempt, getAttempts } from '@/api/attempts'
import type { Attempt, AttemptSummary } from '@/types'

export const useAttemptsStore = defineStore('attempts', () => {
  // State
  const lastAttempt = ref<Attempt | null>(null)
  const attemptHistory = ref<AttemptSummary[]>([])
  const submitting = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function submit(phraseId: string, audioBlob: Blob): Promise<Attempt> {
    submitting.value = true
    error.value = null
    try {
      const attempt = await submitAttempt(phraseId, audioBlob)
      lastAttempt.value = attempt
      return attempt
    } catch (e: any) {
      error.value =
        e.response?.data?.detail ?? 'Submission failed. Please try again.'
      throw e
    } finally {
      submitting.value = false
    }
  }

  async function fetchHistory(studentUid: string, phraseId?: string) {
    loading.value = true
    error.value = null
    try {
      attemptHistory.value = await getAttempts(studentUid, phraseId)
    } catch (e) {
      error.value = 'Failed to load attempt history.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  function clearLastAttempt() {
    lastAttempt.value = null
  }

  function clearHistory() {
    attemptHistory.value = []
  }

  return {
    lastAttempt,
    attemptHistory,
    submitting,
    loading,
    error,
    submit,
    fetchHistory,
    clearLastAttempt,
    clearHistory,
  }
})
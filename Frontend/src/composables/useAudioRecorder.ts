// src/composables/useAudioRecorder.ts
import { ref } from 'vue'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const audioBlob = ref<Blob | null>(null)
  const audioUrl = ref<string | null>(null)
  const error = ref<string | null>(null)
  const duration = ref(0)

  let mediaRecorder: MediaRecorder | null = null
  let chunks: BlobPart[] = []
  let durationTimer: ReturnType<typeof setInterval> | null = null

  async function startRecording() {
    error.value = null
    audioBlob.value = null
    audioUrl.value = null
    duration.value = 0
    chunks = []

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      })

      // Use webm/opus if supported, fallback to whatever browser supports
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'

      mediaRecorder = new MediaRecorder(stream, { mimeType })

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mimeType })
        audioBlob.value = blob
        audioUrl.value = URL.createObjectURL(blob)

        // Stop all microphone tracks
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start(100) // collect data every 100ms
      isRecording.value = true

      // Duration counter
      durationTimer = setInterval(() => {
        duration.value += 1
      }, 1000)

    } catch (e: any) {
      if (e.name === 'NotAllowedError') {
        error.value = 'Microphone access denied. Please allow microphone in browser settings.'
      } else if (e.name === 'NotFoundError') {
        error.value = 'No microphone found on this device.'
      } else {
        error.value = 'Could not start recording. Please try again.'
      }
    }
  }

  function stopRecording() {
    if (mediaRecorder && isRecording.value) {
      mediaRecorder.stop()
      isRecording.value = false
      if (durationTimer) {
        clearInterval(durationTimer)
        durationTimer = null
      }
    }
  }

  function clearRecording() {
    audioBlob.value = null
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = null
    }
    duration.value = 0
    error.value = null
  }

  return {
    isRecording,
    audioBlob,
    audioUrl,
    duration,
    error,
    startRecording,
    stopRecording,
    clearRecording,
  }
}
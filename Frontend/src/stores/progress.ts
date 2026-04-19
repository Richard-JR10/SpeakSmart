// src/stores/progress.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getStudentProgress, getModuleProgress } from '@/api/progress'
import type { StudentDashboard, ProgressSummary } from '@/types'

export const useProgressStore = defineStore('progress', () => {
  // State
  const dashboard = ref<StudentDashboard | null>(null)
  const moduleProgress = ref<Record<string, ProgressSummary>>({}) // keyed by module_id
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchDashboard(studentUid: string) {
    loading.value = true
    error.value = null
    try {
      dashboard.value = await getStudentProgress(studentUid)

      // Also cache per-module progress from the dashboard response
      for (const summary of dashboard.value.progress_by_module) {
        moduleProgress.value[summary.module_id] = summary
      }
    } catch (e) {
      error.value = 'Failed to load progress data.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchModuleProgress(studentUid: string, moduleId: string) {
    try {
      moduleProgress.value[moduleId] = await getModuleProgress(
        studentUid,
        moduleId,
      )
    } catch (e) {
      console.error('Failed to load module progress:', e)
    }
  }

  function getProgressForModule(moduleId: string): ProgressSummary | null {
    return moduleProgress.value[moduleId] ?? null
  }

  function clearProgress() {
    dashboard.value = null
    moduleProgress.value = {}
  }

  return {
    dashboard,
    moduleProgress,
    loading,
    error,
    fetchDashboard,
    fetchModuleProgress,
    getProgressForModule,
    clearProgress,
  }
})
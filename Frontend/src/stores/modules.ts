// src/stores/modules.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getModules, getModulePhrases } from '@/api/modules'
import type { Module, Phrase } from '@/types'

export const useModulesStore = defineStore('modules', () => {
  // State
  const modules = ref<Module[]>([])
  const phrases = ref<Record<string, Phrase[]>>({}) // keyed by module_id
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchModules() {
    loading.value = true
    error.value = null
    try {
      modules.value = await getModules()
    } catch (e) {
      error.value = 'Failed to load lesson modules.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchPhrases(moduleId: string) {
    // Return cached if already loaded
    if (phrases.value[moduleId]) return

    loading.value = true
    error.value = null
    try {
      phrases.value[moduleId] = await getModulePhrases(moduleId)
    } catch (e) {
      error.value = 'Failed to load phrases.'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  function getPhrasesForModule(moduleId: string): Phrase[] {
    return phrases.value[moduleId] ?? []
  }

  function getModuleById(moduleId: string): Module | undefined {
    return modules.value.find((m) => m.module_id === moduleId)
  }

  function clearCache() {
    modules.value = []
    phrases.value = {}
  }

  return {
    modules,
    phrases,
    loading,
    error,
    fetchModules,
    fetchPhrases,
    getPhrasesForModule,
    getModuleById,
    clearCache,
  }
})
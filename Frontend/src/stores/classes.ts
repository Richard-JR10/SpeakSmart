import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

import {
  createClass as createClassRequest,
  getClassStudents,
  getMyClasses,
  joinClass as joinClassRequest,
  leaveClass as leaveClassRequest,
  regenerateJoinCode as regenerateJoinCodeRequest,
} from '@/api/classes'
import { useAuthStore } from '@/stores/auth'
import type { ClassStudent, ClassSummary } from '@/types'

export const useClassesStore = defineStore('classes', () => {
  const authStore = useAuthStore()

  const classes = ref<ClassSummary[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref<string | null>(null)
  const activeClassId = ref<string | null>(null)
  const classStudents = ref<Record<string, ClassStudent[]>>({})

  const activeClass = computed(() =>
    classes.value.find((item) => item.class_id === activeClassId.value) ?? null,
  )

  watch(
    () => authStore.uid,
    () => {
      reset()
    },
  )

  async function ensureLoaded() {
    if (loaded.value) return
    await fetchClasses()
  }

  async function fetchClasses() {
    if (!authStore.profile) {
      reset()
      return
    }

    loading.value = true
    error.value = null

    try {
      classes.value = await getMyClasses()
      loaded.value = true
      syncActiveClass()
    } catch (err) {
      error.value = getErrorMessage(err, 'Failed to load classes.')
      throw err
    } finally {
      loading.value = false
    }
  }

  function setActiveClass(classId: string | null) {
    activeClassId.value = classId
    persistActiveClassId()
  }

  async function createClass(name: string) {
    const created = await createClassRequest(name.trim())
    classes.value = [created, ...classes.value]
    loaded.value = true
    setActiveClass(created.class_id)
    return created
  }

  async function joinClass(joinCode: string) {
    const joined = await joinClassRequest(joinCode.trim())
    const existingIndex = classes.value.findIndex((item) => item.class_id === joined.class_id)
    if (existingIndex >= 0) {
      classes.value.splice(existingIndex, 1, joined)
    } else {
      classes.value = [joined, ...classes.value]
    }
    loaded.value = true
    if (!activeClassId.value) {
      setActiveClass(joined.class_id)
    }
    return joined
  }

  async function fetchClassStudents(classId: string) {
    const students = await getClassStudents(classId)
    classStudents.value = {
      ...classStudents.value,
      [classId]: students,
    }
    return students
  }

  async function leaveClass(classId: string) {
    await leaveClassRequest(classId)
    classes.value = classes.value.filter((item) => item.class_id !== classId)
    const remainingStudents = { ...classStudents.value }
    delete remainingStudents[classId]
    classStudents.value = remainingStudents
    syncActiveClass()
  }

  async function regenerateJoinCode(classId: string) {
    const response = await regenerateJoinCodeRequest(classId)
    classes.value = classes.value.map((item) =>
      item.class_id === classId
        ? { ...item, join_code: response.join_code }
        : item,
    )
    return response
  }

  function reset() {
    classes.value = []
    loading.value = false
    loaded.value = false
    error.value = null
    activeClassId.value = null
    classStudents.value = {}
  }

  function syncActiveClass() {
    const availableIds = new Set(classes.value.map((item) => item.class_id))
    const storedActiveClassId = getStoredActiveClassId()

    if (!classes.value.length) {
      setActiveClass(null)
      return
    }

    if (activeClassId.value && availableIds.has(activeClassId.value)) {
      persistActiveClassId()
      return
    }

    if (storedActiveClassId && availableIds.has(storedActiveClassId)) {
      activeClassId.value = storedActiveClassId
      persistActiveClassId()
      return
    }

    setActiveClass(classes.value[0].class_id)
  }

  function getStorageKey() {
    if (!authStore.uid || !authStore.profile) return null
    return `speaksmart-active-class:${authStore.profile.role}:${authStore.uid}`
  }

  function getStoredActiveClassId() {
    if (typeof window === 'undefined') return null

    const storageKey = getStorageKey()
    if (!storageKey) return null

    return window.localStorage.getItem(storageKey)
  }

  function persistActiveClassId() {
    if (typeof window === 'undefined') return

    const storageKey = getStorageKey()
    if (!storageKey) return

    if (!activeClassId.value) {
      window.localStorage.removeItem(storageKey)
      return
    }

    window.localStorage.setItem(storageKey, activeClassId.value)
  }

  function getErrorMessage(errorValue: unknown, fallback: string) {
    const detail = (errorValue as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    return typeof detail === 'string' ? detail : fallback
  }

  return {
    classes,
    loading,
    loaded,
    error,
    activeClassId,
    activeClass,
    classStudents,
    ensureLoaded,
    fetchClasses,
    setActiveClass,
    createClass,
    joinClass,
    fetchClassStudents,
    leaveClass,
    regenerateJoinCode,
    reset,
  }
})

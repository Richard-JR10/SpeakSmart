import axios from 'axios'
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  createUserWithEmailAndPassword,
  getRedirectResult,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signInWithRedirect,
  signOut as firebaseSignOut,
  updateProfile as updateFirebaseProfile,
  type User as FirebaseUser,
} from 'firebase/auth'

import { auth, googleProvider } from '@/firebase'
import { getMe, registerProfile } from '@/api/auth'
import type { AuthFlowResult, User, UserRole } from '@/types'

const PROFILE_SETUP_REQUIRED = 'PROFILE_SETUP_REQUIRED'

type ProfilePayload = {
  displayName: string
  role: UserRole
}

export const useAuthStore = defineStore('auth', () => {
  const firebaseUser = ref<FirebaseUser | null>(null)
  const profile = ref<User | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)
  const needsProfileSetup = ref(false)

  const isAuthenticated = computed(() => !!firebaseUser.value)
  const isStudent = computed(() => profile.value?.role === 'student')
  const isInstructor = computed(() => profile.value?.role === 'instructor')
  const uid = computed(() => firebaseUser.value?.uid ?? null)

  let authInitialized = false
  let initPromise: Promise<void> | null = null

  function initAuth(): Promise<void> {
    if (initPromise) return initPromise

    initPromise = (async () => {
      try {
        const credential = await getRedirectResult(auth)
        if (credential?.user) {
          firebaseUser.value = credential.user
        }
      } catch (e) {
        error.value = parseError(e)
      }

      await new Promise<void>((resolve) => {
        onAuthStateChanged(auth, async (user) => {
          firebaseUser.value = user

          try {
            if (user) {
              await fetchProfile()
            } else {
              profile.value = null
              needsProfileSetup.value = false
            }
          } catch (e) {
            error.value = parseError(e)
          } finally {
            loading.value = false
            if (!authInitialized) {
              authInitialized = true
              resolve()
            }
          }
        })
      })
    })()

    return initPromise
  }

  async function fetchProfile(): Promise<User | null> {
    if (!auth.currentUser) {
      profile.value = null
      needsProfileSetup.value = false
      return null
    }

    try {
      const currentProfile = await getMe()
      profile.value = currentProfile
      needsProfileSetup.value = false
      return currentProfile
    } catch (e) {
      if (isProfileSetupRequired(e)) {
        profile.value = null
        needsProfileSetup.value = true
        return null
      }

      profile.value = null
      needsProfileSetup.value = false
      throw e
    }
  }

  async function signUpWithEmail(payload: {
    displayName: string
    email: string
    password: string
    role: UserRole
  }): Promise<AuthFlowResult> {
    error.value = null

    try {
      const credential = await createUserWithEmailAndPassword(
        auth,
        payload.email,
        payload.password,
      )

      await updateFirebaseProfile(credential.user, {
        displayName: payload.displayName.trim(),
      })

      profile.value = await registerProfile({
        display_name: payload.displayName.trim(),
        role: payload.role,
      })
      needsProfileSetup.value = false

      return 'signed-in'
    } catch (e) {
      error.value = parseError(e)
      throw e
    }
  }

  async function signInWithEmail(
    email: string,
    password: string,
  ): Promise<AuthFlowResult> {
    error.value = null

    try {
      await signInWithEmailAndPassword(auth, email, password)
      await fetchProfile()
      return needsProfileSetup.value ? 'profile-setup' : 'signed-in'
    } catch (e) {
      error.value = parseError(e)
      throw e
    }
  }

  async function signInWithGoogle(): Promise<AuthFlowResult> {
    error.value = null

    try {
      if (shouldUseGoogleRedirectOnly()) {
        await signInWithRedirect(auth, googleProvider)
        return 'redirect'
      }

      const credential = await signInWithPopup(auth, googleProvider).catch(async (e) => {
        if (shouldFallbackToGoogleRedirect(e)) {
          await signInWithRedirect(auth, googleProvider)
          return null
        }

        throw e
      })

      if (!credential) return 'redirect'

      firebaseUser.value = credential.user
      await fetchProfile()
      return needsProfileSetup.value ? 'profile-setup' : 'signed-in'
    } catch (e) {
      error.value = parseError(e)
      throw e
    }
  }

  async function completeProfile(
    payload: ProfilePayload,
  ): Promise<AuthFlowResult> {
    error.value = null

    const currentUser = auth.currentUser
    if (!currentUser) {
      const authError = new Error('Missing authenticated user.')
      error.value = authError.message
      throw authError
    }

    try {
      await updateFirebaseProfile(currentUser, {
        displayName: payload.displayName.trim(),
      })

      profile.value = await registerProfile({
        display_name: payload.displayName.trim(),
        role: payload.role,
      })
      needsProfileSetup.value = false
      return 'signed-in'
    } catch (e) {
      error.value = parseError(e)
      throw e
    }
  }

  async function signOut() {
    error.value = null
    await firebaseSignOut(auth)
    profile.value = null
    firebaseUser.value = null
    needsProfileSetup.value = false
  }

  function clearError() {
    error.value = null
  }

  function isProfileSetupRequired(errorValue: unknown) {
    if (!axios.isAxiosError(errorValue)) return false
    return (
      errorValue.response?.status === 404 &&
      errorValue.response?.data?.detail === PROFILE_SETUP_REQUIRED
    )
  }

  function shouldUseGoogleRedirectOnly() {
    if (typeof window === 'undefined') return false

    const navigatorWithStandalone = window.navigator as Navigator & {
      standalone?: boolean
    }
    const isStandalone =
      window.matchMedia?.('(display-mode: standalone)').matches ||
      navigatorWithStandalone.standalone === true

    return Boolean(isStandalone)
  }

  function shouldFallbackToGoogleRedirect(errorValue: unknown) {
    const code = (errorValue as { code?: string } | null)?.code
    return code === 'auth/popup-blocked'
  }

  function parseError(errorValue: unknown): string {
    if (axios.isAxiosError(errorValue)) {
      if (errorValue.response?.data?.detail === PROFILE_SETUP_REQUIRED) {
        return 'Finish setting up your profile to continue.'
      }

      if (typeof errorValue.response?.data?.detail === 'string') {
        return errorValue.response.data.detail
      }

      return 'We could not reach the server. Please try again.'
    }

    const code = (errorValue as { code?: string } | null)?.code
    const messages: Record<string, string> = {
      'auth/email-already-in-use': 'This email is already registered.',
      'auth/invalid-credential': 'Incorrect email or password.',
      'auth/invalid-email': 'Enter a valid email address.',
      'auth/network-request-failed': 'Network error. Check your connection.',
      'auth/popup-blocked': 'Allow pop-ups for Google sign-in and try again.',
      'auth/popup-closed-by-user': 'Google sign-in was cancelled.',
      'auth/too-many-requests': 'Too many attempts. Please try again later.',
      'auth/user-not-found': 'No account found with this email.',
      'auth/wrong-password': 'Incorrect email or password.',
    }

    if (code && messages[code]) {
      return messages[code]
    }

    return 'An unexpected error occurred. Please try again.'
  }

  return {
    firebaseUser,
    profile,
    loading,
    error,
    needsProfileSetup,
    isAuthenticated,
    isStudent,
    isInstructor,
    uid,
    initAuth,
    fetchProfile,
    signUpWithEmail,
    signInWithEmail,
    signInWithGoogle,
    completeProfile,
    signOut,
    clearError,
  }
})

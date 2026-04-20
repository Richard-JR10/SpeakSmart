<template>
  <StudentLayout title="Settings">
    <div class="mx-auto flex w-full max-w-4xl flex-col gap-4">
      <Card class="overflow-hidden border-border/80 bg-card/95">
        <CardContent class="flex flex-col gap-4 py-6 sm:flex-row sm:items-center">
          <div class="flex size-22 shrink-0 items-center justify-center rounded-3xl bg-primary text-xl font-bold text-primary-foreground shadow-sm">
            {{ initials }}
          </div>

          <div class="min-w-0 flex-1">
            <p class="truncate font-(--font-display) text-3xl leading-none text-(--color-heading)">
              {{ displayNameValue }}
            </p>
            <p class="mt-2 truncate text-sm text-muted-foreground">
              {{ emailValue }}
            </p>
            <div class="mt-3 flex flex-wrap gap-2">
              <Badge variant="secondary" class="rounded-full px-3 py-1">
                {{ roleLabel }}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-3">
          <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
            Profile
          </Badge>
          <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
            Update Display Name
          </CardTitle>
          <CardDescription>
            Change the name shown across your student pages.
          </CardDescription>
        </CardHeader>

        <CardContent class="flex flex-col gap-4">
          <Alert v-if="saveError" variant="destructive">
            <TriangleAlert />
            <AlertTitle>Could not save your profile</AlertTitle>
            <AlertDescription>{{ saveError }}</AlertDescription>
          </Alert>

          <Alert v-else-if="saveSuccess">
            <CheckCircle2 />
            <AlertTitle>Display name updated</AlertTitle>
            <AlertDescription>
              Your profile name was saved successfully.
            </AlertDescription>
          </Alert>

          <div class="flex flex-col gap-2">
            <Label for="settings-display-name">Display Name</Label>
            <Input
              id="settings-display-name"
              v-model="displayName"
              type="text"
              placeholder="Enter your display name"
              autocomplete="name"
              :aria-invalid="Boolean(nameError)"
              :aria-describedby="nameError ? 'settings-display-name-error' : 'settings-display-name-hint'"
            />
            <p
              v-if="nameError"
              id="settings-display-name-error"
              class="text-sm font-medium text-destructive"
            >
              {{ nameError }}
            </p>
            <p
              v-else
              id="settings-display-name-hint"
              class="text-sm text-muted-foreground"
            >
              Use the name you want to appear throughout your student account.
            </p>
          </div>
        </CardContent>

        <CardFooter class="flex-col items-start gap-3 border-t sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-muted-foreground" aria-live="polite">
            {{ saveStatusCopy }}
          </p>

          <Button
            size="lg"
            class="w-full sm:w-auto"
            :disabled="saveDisabled"
            @click="saveDisplayName"
          >
            <LoaderCircle v-if="saving" class="animate-spin" data-icon="inline-start" />
            <Save v-else data-icon="inline-start" />
            <span>{{ saving ? 'Saving...' : 'Save Changes' }}</span>
          </Button>
        </CardFooter>
      </Card>

      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-3">
          <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
            Preferences
          </Badge>
          <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
            Practice Preferences
          </CardTitle>
          <CardDescription>
            Saved on this device.
          </CardDescription>
        </CardHeader>

        <CardContent class="grid gap-4">
          <div class="flex flex-col gap-4 rounded-2xl border border-border/70 bg-muted/25 p-4 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="font-semibold text-(--color-heading)">Auto-Play Reference Audio</p>
                <Badge :variant="autoPlay ? 'secondary' : 'outline'" class="rounded-full px-2.5 py-1">
                  {{ autoPlay ? 'On' : 'Off' }}
                </Badge>
              </div>
              <p class="mt-1 text-sm leading-6 text-muted-foreground">
                Play the model audio before practice starts.
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              class="w-full sm:w-auto sm:shrink-0"
              @click="togglePreference('autoPlay')"
            >
              <Volume2 data-icon="inline-start" />
              <span>{{ autoPlay ? 'Turn Off' : 'Turn On' }}</span>
            </Button>
          </div>

          <div class="flex flex-col gap-4 rounded-2xl border border-border/70 bg-muted/25 p-4 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="font-semibold text-(--color-heading)">Daily Reminder</p>
                <Badge :variant="dailyReminder ? 'secondary' : 'outline'" class="rounded-full px-2.5 py-1">
                  {{ dailyReminder ? 'On' : 'Off' }}
                </Badge>
              </div>
              <p class="mt-1 text-sm leading-6 text-muted-foreground">
                Keep a reminder preference for this browser.
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              class="w-full sm:w-auto sm:shrink-0"
              @click="togglePreference('dailyReminder')"
            >
              <Bell data-icon="inline-start" />
              <span>{{ dailyReminder ? 'Turn Off' : 'Turn On' }}</span>
            </Button>
          </div>
        </CardContent>

        <CardFooter class="justify-end border-t">
          <Button
            variant="outline"
            size="sm"
            class="w-full sm:w-auto"
            :disabled="!autoPlay && !dailyReminder"
            @click="resetPreferences"
          >
            <RotateCcw data-icon="inline-start" />
            <span>Reset</span>
          </Button>
        </CardFooter>
      </Card>

      <Card class="border-border/80 bg-card/95">
        <CardHeader class="gap-3">
          <Badge variant="secondary" class="w-fit rounded-full px-3 py-1 uppercase tracking-[0.18em]">
            Session
          </Badge>
          <CardTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
            Sign Out
          </CardTitle>
          <CardDescription>
            End the current session on this device.
          </CardDescription>
        </CardHeader>

        <CardContent class="flex flex-col gap-4">
          <Alert v-if="signOutError" variant="destructive">
            <TriangleAlert />
            <AlertTitle>Sign out failed</AlertTitle>
            <AlertDescription>{{ signOutError }}</AlertDescription>
          </Alert>

          <Button
            variant="outline"
            size="lg"
            class="w-full sm:w-auto"
            :disabled="signingOut"
            @click="signOutConfirm = true"
          >
            <LogOut data-icon="inline-start" />
            <span>Sign Out</span>
          </Button>
        </CardContent>
      </Card>

      <DialogRoot v-model:open="signOutConfirm">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" />
          <DialogContent
            class="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-border/80 bg-card shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95"
          >
            <div class="flex flex-col gap-5 p-6">
              <div class="flex items-start gap-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
                  <TriangleAlert />
                </div>

                <div class="min-w-0">
                  <DialogTitle class="font-(--font-display) text-3xl leading-none text-(--color-heading)">
                    Confirm Sign Out
                  </DialogTitle>
                  <DialogDescription class="mt-2 text-sm leading-6 text-muted-foreground">
                    You will need to sign in again to continue.
                  </DialogDescription>
                </div>
              </div>

              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Leaving this session</AlertTitle>
                <AlertDescription>
                  Use sign out when you are done practicing, especially on a shared computer.
                </AlertDescription>
              </Alert>

              <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  class="w-full sm:w-auto"
                  :disabled="signingOut"
                  @click="signOutConfirm = false"
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  class="w-full sm:w-auto"
                  :disabled="signingOut"
                  @click="confirmSignOut"
                >
                  <LoaderCircle v-if="signingOut" class="animate-spin" data-icon="inline-start" />
                  <LogOut v-else data-icon="inline-start" />
                  <span>{{ signingOut ? 'Signing Out...' : 'Confirm Sign Out' }}</span>
                </Button>
              </div>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bell,
  CheckCircle2,
  LoaderCircle,
  LogOut,
  RotateCcw,
  Save,
  TriangleAlert,
  Volume2,
} from 'lucide-vue-next'
import {
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

import { updateProfile } from '@/api/auth'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/auth'

const AUTO_PLAY_STORAGE_KEY = 'student-settings:auto-play-reference'
const DAILY_REMINDER_STORAGE_KEY = 'student-settings:daily-reminder'

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref(authStore.profile?.display_name ?? '')
const autoPlay = ref(false)
const dailyReminder = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref<string | null>(null)
const nameError = ref<string | null>(null)
const signOutConfirm = ref(false)
const signingOut = ref(false)
const signOutError = ref<string | null>(null)
const preferencesReady = ref(false)

let saveSuccessTimeout: ReturnType<typeof setTimeout> | null = null

const displayNameValue = computed(() =>
  authStore.profile?.display_name?.trim() || authStore.firebaseUser?.displayName?.trim() || 'Student',
)
const emailValue = computed(() =>
  authStore.profile?.email || authStore.firebaseUser?.email || 'No email available',
)
const normalizedCurrentDisplayName = computed(() =>
  authStore.profile?.display_name?.trim() ?? '',
)
const normalizedDisplayName = computed(() => displayName.value.trim())
const roleLabel = computed(() => {
  const role = authStore.profile?.role ?? 'student'
  return `${role.charAt(0).toUpperCase()}${role.slice(1)}`
})
const initials = computed(() => {
  const name = displayNameValue.value
  return name
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})
const saveDisabled = computed(() =>
  saving.value ||
  !normalizedDisplayName.value ||
  normalizedDisplayName.value === normalizedCurrentDisplayName.value,
)
const saveStatusCopy = computed(() => {
  if (saving.value) return 'Saving your updated display name now.'
  if (saveSuccess.value) return 'Profile changes saved.'
  if (saveError.value) return 'Review the message above and try again.'
  return 'Only real profile changes can be saved.'
})

watch(
  () => authStore.profile?.display_name,
  (value) => {
    displayName.value = value ?? ''
  },
)

watch(displayName, () => {
  if (normalizedDisplayName.value) {
    nameError.value = null
  }

  if (saveError.value) {
    saveError.value = null
  }
})

watch(autoPlay, (value) => {
  if (!preferencesReady.value) return
  writeStoredPreference(AUTO_PLAY_STORAGE_KEY, value)
})

watch(dailyReminder, (value) => {
  if (!preferencesReady.value) return
  writeStoredPreference(DAILY_REMINDER_STORAGE_KEY, value)
})

onMounted(() => {
  autoPlay.value = readStoredPreference(AUTO_PLAY_STORAGE_KEY)
  dailyReminder.value = readStoredPreference(DAILY_REMINDER_STORAGE_KEY)
  preferencesReady.value = true
})

onBeforeUnmount(() => {
  if (saveSuccessTimeout) {
    clearTimeout(saveSuccessTimeout)
  }
})

function readStoredPreference(key: string) {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(key) === 'true'
}

function writeStoredPreference(key: string, value: boolean) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(key, String(value))
}

function clearSaveSuccess() {
  if (saveSuccessTimeout) {
    clearTimeout(saveSuccessTimeout)
  }

  saveSuccessTimeout = setTimeout(() => {
    saveSuccess.value = false
    saveSuccessTimeout = null
  }, 2200)
}

function togglePreference(key: 'autoPlay' | 'dailyReminder') {
  if (key === 'autoPlay') {
    autoPlay.value = !autoPlay.value
    return
  }

  dailyReminder.value = !dailyReminder.value
}

function resetPreferences() {
  autoPlay.value = false
  dailyReminder.value = false
}

async function saveDisplayName() {
  saveError.value = null
  saveSuccess.value = false
  signOutError.value = null

  if (!normalizedDisplayName.value) {
    nameError.value = 'Enter a display name before saving.'
    return
  }

  if (normalizedDisplayName.value === normalizedCurrentDisplayName.value) {
    return
  }

  saving.value = true
  try {
    const updatedProfile = await updateProfile({
      display_name: normalizedDisplayName.value,
    })

    if (authStore.profile) {
      authStore.profile.display_name = updatedProfile.display_name
    }

    displayName.value = updatedProfile.display_name
    saveSuccess.value = true
    clearSaveSuccess()
  } catch (error) {
    console.error('Failed to save display name:', error)
    saveError.value = authStore.error ?? 'Your display name could not be updated. Please try again.'
  } finally {
    saving.value = false
  }
}

async function confirmSignOut() {
  signOutError.value = null
  signingOut.value = true

  try {
    await authStore.signOut()
    signOutConfirm.value = false
    await router.push('/')
  } catch (error) {
    console.error('Failed to sign out:', error)
    signOutError.value = 'We could not sign you out right now. Please try again.'
  } finally {
    signingOut.value = false
  }
}
</script>

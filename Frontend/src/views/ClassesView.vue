<template>
  <component :is="layoutComponent" v-bind="layoutProps">
    <div class="flex flex-col gap-6">
      <Card class="border-border/70">
        <CardHeader>
          <CardTitle class="text-xl">
            {{ isInstructor ? 'Create a class' : 'Join a class' }}
          </CardTitle>
          <CardDescription>
            {{
              isInstructor
                ? 'Each class gets its own join code and can be switched independently in instructor analytics.'
                : 'Enter the join code from your teacher to add another class to your account.'
            }}
          </CardDescription>
        </CardHeader>

        <CardContent class="flex flex-col gap-4">
          <Input
            v-if="isInstructor"
            v-model="createName"
            placeholder="Grade 8 - Section A"
            maxlength="255"
          />

          <Input
            v-else
            v-model="joinCode"
            placeholder="AB12CD"
            maxlength="32"
          />

          <Alert
            v-if="!isInstructor && actionError"
            variant="destructive"
          >
            <AlertTitle>Action failed</AlertTitle>
            <AlertDescription>{{ actionError }}</AlertDescription>
          </Alert>
        </CardContent>

        <CardFooter class="justify-end">
          <Button
            v-if="isInstructor"
            :disabled="createSubmitting"
            @click="handleCreateClass"
          >
            <LoaderCircle v-if="createSubmitting" class="mr-2 size-4 animate-spin" />
            <School v-else class="mr-2 size-4" />
            <span>{{ createSubmitting ? 'Creating...' : 'Create class' }}</span>
          </Button>

          <Button
            v-else
            :disabled="joinSubmitting"
            @click="handleJoinClass"
          >
            <LoaderCircle v-if="joinSubmitting" class="mr-2 size-4 animate-spin" />
            <School v-else class="mr-2 size-4" />
            <span>{{ joinSubmitting ? 'Joining...' : 'Join class' }}</span>
          </Button>
        </CardFooter>
      </Card>

      <Alert v-if="isInstructor && actionError" variant="destructive">
        <AlertTitle>Action failed</AlertTitle>
        <AlertDescription>{{ actionError }}</AlertDescription>
      </Alert>

      <Alert v-else-if="actionMessage">
        <AlertTitle>Updated</AlertTitle>
        <AlertDescription>{{ actionMessage }}</AlertDescription>
      </Alert>

      <section class="grid gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-(--color-heading)">
              {{ isInstructor ? 'Your classes' : 'Joined classes' }}
            </h2>
            <p class="text-sm text-muted-foreground">
              {{
                isInstructor
                  ? 'Switch the active class any time. Analytics and exercises follow that selection.'
                  : 'Keep track of every class you have joined.'
              }}
            </p>
          </div>

          <Badge variant="secondary">
            {{ classesStore.classes.length }}
            {{ classesStore.classes.length === 1 ? 'class' : 'classes' }}
          </Badge>
        </div>

        <Card
          v-if="!classesStore.classes.length"
          class="border-dashed border-border/70"
        >
          <CardHeader>
            <CardTitle class="text-xl">
              {{ isInstructor ? 'No classes yet' : 'No joined classes yet' }}
            </CardTitle>
            <CardDescription>
              {{
                isInstructor
                  ? 'Create your first class to start inviting students and switching analytics by roster.'
                  : 'Join a class with a teacher code to start seeing all your classroom access in one place.'
              }}
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          v-for="item in classesStore.classes"
          :key="item.class_id"
          class="border-border/70"
        >
          <CardHeader class="gap-3 sm:flex sm:flex-row sm:items-start sm:justify-between">
            <div class="space-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <CardTitle class="text-xl">{{ item.name }}</CardTitle>
                <Badge v-if="classesStore.activeClassId === item.class_id">
                  Active
                </Badge>
                <Badge variant="secondary">
                  {{ item.is_owner ? 'Instructor' : 'Student' }}
                </Badge>
              </div>

              <CardDescription>
                {{
                  item.is_owner
                    ? item.student_count + ' students joined'
                    : 'Teacher: ' + (item.instructor_name ?? 'Unknown instructor')
                }}
              </CardDescription>
            </div>

            <div class="flex flex-wrap gap-2">
              <Button
                v-if="classesStore.activeClassId !== item.class_id"
                variant="outline"
                size="sm"
                @click="classesStore.setActiveClass(item.class_id)"
              >
                Set active
              </Button>

              <Button
                v-if="isInstructor && item.join_code"
                variant="outline"
                size="sm"
                :disabled="busyClassId === item.class_id"
                @click="copyJoinCode(item.class_id, item.join_code)"
              >
                <Check v-if="copiedClassId === item.class_id" class="mr-2 size-4" />
                <Copy v-else class="mr-2 size-4" />
                <span>{{ copiedClassId === item.class_id ? 'Copied' : 'Copy code' }}</span>
              </Button>
            </div>
          </CardHeader>

          <CardContent class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-border/70 bg-muted/30 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                Class ID
              </p>
              <p class="mt-2 break-all text-sm font-medium text-foreground">
                {{ item.class_id }}
              </p>
            </div>

            <div class="rounded-2xl border border-border/70 bg-muted/30 p-4">
              <p class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                {{ isInstructor ? 'Join code' : 'Joined' }}
              </p>
              <div class="mt-2 flex items-center gap-2 text-sm font-medium text-foreground">
                <span
                  v-if="isInstructor"
                  class="font-mono tracking-[0.2em]"
                >
                  {{ item.join_code ?? 'Unavailable' }}
                </span>
                <span v-else>
                  {{
                    item.joined_at
                      ? new Date(item.joined_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : 'Recently'
                  }}
                </span>
              </div>
            </div>
          </CardContent>

          <CardFooter class="flex flex-wrap justify-between gap-3">
            <div class="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <Users class="size-4" />
              <span>
                {{ item.student_count }}
                {{ item.student_count === 1 ? 'student' : 'students' }}
              </span>
            </div>

            <div class="flex flex-wrap gap-2">
              <Button
                v-if="isInstructor"
                variant="outline"
                size="sm"
                :disabled="busyClassId === item.class_id"
                @click="handleRegenerateCode(item.class_id, item.name)"
              >
                <LoaderCircle
                  v-if="busyClassId === item.class_id"
                  class="mr-2 size-4 animate-spin"
                />
                <RefreshCcw v-else class="mr-2 size-4" />
                <span>Regenerate code</span>
              </Button>

              <Button
                variant="outline"
                size="sm"
                :disabled="rosterLoading && selectedRosterClassId === item.class_id"
                @click="openRosterModal(item.class_id)"
              >
                <LoaderCircle
                  v-if="rosterLoading && selectedRosterClassId === item.class_id"
                  class="mr-2 size-4 animate-spin"
                />
                <Eye v-else class="mr-2 size-4" />
                <span>View class</span>
              </Button>

              <Button
                v-if="!isInstructor"
                variant="outline"
                size="sm"
                :disabled="busyClassId === item.class_id"
                @click="handleLeaveClass(item.class_id, item.name)"
              >
                <LoaderCircle
                  v-if="busyClassId === item.class_id"
                  class="mr-2 size-4 animate-spin"
                />
                <Trash2 v-else class="mr-2 size-4" />
                <span>Leave class</span>
              </Button>
            </div>
          </CardFooter>
        </Card>
      </section>

      <DialogRoot :open="rosterModalOpen" @update:open="handleRosterModalOpenChange">
        <DialogPortal>
          <DialogOverlay class="fixed inset-0 z-50 bg-black/45 data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
          <DialogContent class="fixed top-1/2 left-1/2 z-50 grid max-h-[calc(100vh-2rem)] w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 -translate-y-1/2 gap-4 overflow-y-auto rounded-2xl border border-border bg-background p-5 shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 sm:p-6">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0 space-y-2">
                <Badge variant="secondary" class="rounded-full">
                  {{ selectedClassStudents.length }}
                  {{ selectedClassStudents.length === 1 ? 'student' : 'students' }}
                </Badge>
                <DialogTitle class="text-balance font-(--font-display) text-2xl leading-tight text-(--color-heading)">
                  {{ selectedRosterClass?.name ?? 'Class list' }}
                </DialogTitle>
                <DialogDescription class="text-pretty text-sm leading-6 text-muted-foreground">
                  See who is enrolled in this class.
                </DialogDescription>
              </div>

              <DialogClose class="rounded-full p-2 text-muted-foreground transition-opacity hover:bg-muted hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-hidden">
                <X class="size-4" />
                <span class="sr-only">Close class list</span>
              </DialogClose>
            </div>

            <Alert v-if="rosterError" variant="destructive">
              <AlertTitle>Could not load class list</AlertTitle>
              <AlertDescription>{{ rosterError }}</AlertDescription>
            </Alert>

            <div
              v-if="rosterLoading"
              class="flex min-h-40 items-center justify-center rounded-2xl border border-dashed border-border/70 bg-muted/30 text-sm text-muted-foreground"
            >
              <LoaderCircle class="mr-2 size-4 animate-spin" />
              Loading classmates...
            </div>

            <div
              v-else-if="!selectedClassStudents.length && !rosterError"
              class="rounded-2xl border border-dashed border-border/70 bg-muted/30 p-5 text-sm text-muted-foreground"
            >
              No students are enrolled in this class yet.
            </div>

            <div v-else class="grid gap-2">
              <div
                v-for="student in selectedClassStudents"
                :key="student.uid"
                class="flex items-center justify-between gap-3 rounded-2xl border border-border/70 bg-muted/25 px-3 py-3"
              >
                <div class="flex min-w-0 items-center gap-3">
                  <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                    {{ getInitials(student.display_name) }}
                  </div>
                  <div class="min-w-0">
                    <div class="flex min-w-0 flex-wrap items-center gap-2">
                      <p class="truncate font-semibold text-(--color-heading)">
                        {{ student.display_name }}
                      </p>
                      <Badge
                        v-if="student.uid === authStore.uid"
                        variant="secondary"
                        class="rounded-full"
                      >
                        You
                      </Badge>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Joined {{ formatShortDate(student.joined_at) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Check,
  Copy,
  Eye,
  LoaderCircle,
  RefreshCcw,
  School,
  Trash2,
  Users,
  X,
} from 'lucide-vue-next'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'

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
import InstructorLayout from '@/layouts/InstructorLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useClassesStore } from '@/stores/classes'

const authStore = useAuthStore()
const classesStore = useClassesStore()

const createName = ref('')
const joinCode = ref('')
const createSubmitting = ref(false)
const joinSubmitting = ref(false)
const actionError = ref<string | null>(null)
const actionMessage = ref<string | null>(null)
const busyClassId = ref<string | null>(null)
const copiedClassId = ref<string | null>(null)
const rosterModalOpen = ref(false)
const selectedRosterClassId = ref<string | null>(null)
const rosterLoading = ref(false)
const rosterError = ref<string | null>(null)

const isStudent = computed(() => authStore.profile?.role === 'student')
const isInstructor = computed(() => authStore.profile?.role === 'instructor')
const layoutComponent = computed(() => (isStudent.value ? StudentLayout : InstructorLayout))
const layoutProps = computed(() =>
  isStudent.value
    ? { title: 'Classes', wide: true }
    : {},
)
const selectedRosterClass = computed(() =>
  classesStore.classes.find((item) => item.class_id === selectedRosterClassId.value) ?? null,
)
const selectedClassStudents = computed(() => {
  if (!selectedRosterClassId.value) return []
  return classesStore.classStudents[selectedRosterClassId.value] ?? []
})

onMounted(async () => {
  try {
    await classesStore.ensureLoaded()
  } catch {
    // The store already exposes the user-facing error.
  }
})

async function handleCreateClass() {
  const trimmedName = createName.value.trim()
  if (!trimmedName) {
    actionError.value = 'Enter a class name before creating it.'
    return
  }

  createSubmitting.value = true
  actionError.value = null
  actionMessage.value = null

  try {
    const created = await classesStore.createClass(trimmedName)
    createName.value = ''
    actionMessage.value = `${created.name} is ready. Share its join code with students.`
  } catch (error) {
    actionError.value = getErrorMessage(error, 'Failed to create class.')
  } finally {
    createSubmitting.value = false
  }
}

async function handleJoinClass() {
  const trimmedCode = joinCode.value.trim().toUpperCase()
  if (!trimmedCode) {
    actionError.value = 'Enter a join code before joining a class.'
    return
  }

  joinSubmitting.value = true
  actionError.value = null
  actionMessage.value = null

  try {
    const joined = await classesStore.joinClass(trimmedCode)
    joinCode.value = ''
    actionMessage.value = `You joined ${joined.name}.`
  } catch (error) {
    actionError.value = getErrorMessage(error, 'Failed to join class.')
  } finally {
    joinSubmitting.value = false
  }
}

async function handleLeaveClass(classId: string, className: string) {
  if (!window.confirm(`Leave ${className}?`)) return

  busyClassId.value = classId
  actionError.value = null
  actionMessage.value = null

  try {
    await classesStore.leaveClass(classId)
    actionMessage.value = `You left ${className}.`
  } catch (error) {
    actionError.value = getErrorMessage(error, 'Failed to leave class.')
  } finally {
    busyClassId.value = null
  }
}

async function handleRegenerateCode(classId: string, className: string) {
  busyClassId.value = classId
  actionError.value = null
  actionMessage.value = null

  try {
    const response = await classesStore.regenerateJoinCode(classId)
    actionMessage.value = `Join code updated for ${className}: ${response.join_code}`
  } catch (error) {
    actionError.value = getErrorMessage(error, 'Failed to regenerate join code.')
  } finally {
    busyClassId.value = null
  }
}

async function openRosterModal(classId: string) {
  selectedRosterClassId.value = classId
  rosterModalOpen.value = true
  rosterLoading.value = true
  rosterError.value = null

  try {
    await classesStore.fetchClassStudents(classId)
  } catch (error) {
    rosterError.value = getErrorMessage(error, 'Failed to load the class list.')
  } finally {
    rosterLoading.value = false
  }
}

function closeRosterModal() {
  rosterModalOpen.value = false
  selectedRosterClassId.value = null
  rosterError.value = null
}

function handleRosterModalOpenChange(open: boolean) {
  if (!open) {
    closeRosterModal()
    return
  }

  rosterModalOpen.value = true
}

async function copyJoinCode(classId: string, joinCodeValue: string | null) {
  if (!joinCodeValue || typeof navigator === 'undefined' || !navigator.clipboard) {
    return
  }

  await navigator.clipboard.writeText(joinCodeValue)
  copiedClassId.value = classId
  window.setTimeout(() => {
    if (copiedClassId.value === classId) {
      copiedClassId.value = null
    }
  }, 1800)
}

function formatShortDate(value: string | null) {
  if (!value) return 'recently'

  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function getInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || 'S'
}

function getErrorMessage(errorValue: unknown, fallback: string) {
  const detail = (errorValue as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : fallback
}
</script>

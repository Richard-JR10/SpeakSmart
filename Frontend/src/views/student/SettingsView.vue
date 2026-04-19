<!-- src/views/student/SettingsView.vue -->
<template>
  <StudentLayout title="Settings">

    <div class="settings">

      <!-- Profile card -->
      <div class="settings__profile">
        <div class="settings__avatar">
          {{ initials }}
        </div>
        <div class="settings__profile-info">
          <p class="settings__profile-name">{{ authStore.profile?.display_name }}</p>
          <p class="settings__profile-email">{{ authStore.profile?.email }}</p>
          <span class="settings__profile-role">{{ authStore.profile?.role }}</span>
        </div>
      </div>

      <!-- Edit display name -->
      <div class="settings__section">
        <h3 class="settings__section-title">Profile</h3>
        <div class="settings__field">
          <label class="settings__label">Display Name</label>
          <div class="settings__input-row">
            <input
              v-model="displayName"
              type="text"
              class="settings__input"
              placeholder="Your full name"
            />
            <button
              class="settings__save-btn"
              :disabled="saving || displayName === authStore.profile?.display_name"
              @click="saveDisplayName"
            >
              {{ saving ? '...' : 'Save' }}
            </button>
          </div>
          <p v-if="saveSuccess" class="settings__save-success">✓ Saved</p>
        </div>
      </div>

      <!-- Preferences -->
      <div class="settings__section">
        <h3 class="settings__section-title">Preferences</h3>

        <div class="settings__toggle-row">
          <div class="settings__toggle-info">
            <p class="settings__toggle-label">Auto-play Reference Audio</p>
            <p class="settings__toggle-desc">Play reference before each practice</p>
          </div>
          <button
            class="settings__toggle"
            :class="{ 'settings__toggle--on': autoPlay }"
            @click="autoPlay = !autoPlay"
          >
            <div class="settings__toggle-thumb" />
          </button>
        </div>

        <div class="settings__toggle-row">
          <div class="settings__toggle-info">
            <p class="settings__toggle-label">Daily Reminder</p>
            <p class="settings__toggle-desc">Remind me to practice every day</p>
          </div>
          <button
            class="settings__toggle"
            :class="{ 'settings__toggle--on': dailyReminder }"
            @click="dailyReminder = !dailyReminder"
          >
            <div class="settings__toggle-thumb" />
          </button>
        </div>

      </div>

      <!-- App info -->
      <div class="settings__section">
        <h3 class="settings__section-title">About</h3>
        <div class="settings__info-row">
          <span class="settings__info-label">App</span>
          <span class="settings__info-value">SpeakSmart v1.0</span>
        </div>
        <div class="settings__info-row">
          <span class="settings__info-label">Institution</span>
          <span class="settings__info-value">Gordon College</span>
        </div>
        <div class="settings__info-row">
          <span class="settings__info-label">Department</span>
          <span class="settings__info-value">Tourism</span>
        </div>
        <div class="settings__info-row">
          <span class="settings__info-label">Target Language</span>
          <span class="settings__info-value">Japanese 🇯🇵</span>
        </div>
      </div>

      <!-- Sign out -->
      <button class="settings__signout" @click="handleSignOut">
        Sign Out
      </button>

    </div>
  </StudentLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { updateProfile } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const displayName = ref(authStore.profile?.display_name ?? '')
const autoPlay = ref(false)
const dailyReminder = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)

const initials = computed(() => {
  const name = authStore.profile?.display_name ?? ''
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

async function saveDisplayName() {
  saving.value = true
  saveSuccess.value = false
  try {
    const updated = await updateProfile({ display_name: displayName.value })
    if (authStore.profile) {
      authStore.profile.display_name = updated.display_name
    }
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 2000)
  } catch (e) {
    console.error('Failed to save display name:', e)
  } finally {
    saving.value = false
  }
}

async function handleSignOut() {
  await authStore.signOut()
  router.push('/')
}
</script>

<style scoped>
.settings {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings__profile {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #ffffff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
}

.settings__avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #ffffff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.settings__profile-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
}

.settings__profile-email {
  font-size: 13px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.settings__profile-role {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
}

.settings__section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-subtext);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.settings__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings__label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.settings__input-row {
  display: flex;
  gap: 8px;
}

.settings__input {
  flex: 1;
  padding: 12px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 14px;
  outline: none;
}

.settings__input:focus {
  border-color: var(--color-primary);
}

.settings__save-btn {
  padding: 12px 18px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.settings__save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.settings__save-success {
  font-size: 13px;
  color: var(--color-primary);
  font-weight: 600;
}

.settings__toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
}

.settings__toggle-row:last-child {
  border-bottom: none;
}

.settings__toggle-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.settings__toggle-desc {
  font-size: 12px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.settings__toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  background: var(--color-border);
  border: none;
  cursor: pointer;
  padding: 3px;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.settings__toggle--on {
  background: var(--color-primary);
  justify-content: flex-end;
}

.settings__toggle-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}

.settings__info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
}

.settings__info-row:last-child {
  border-bottom: none;
}

.settings__info-label {
  color: var(--color-subtext);
}

.settings__info-value {
  font-weight: 600;
  color: var(--color-text);
}

.settings__signout {
  width: 100%;
  padding: 16px;
  background: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: var(--radius);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 8px;
}

.settings__signout:hover {
  background: #fecaca;
}
</style>
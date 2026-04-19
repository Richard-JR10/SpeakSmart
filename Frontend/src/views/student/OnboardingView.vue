<!-- src/views/student/OnboardingView.vue -->
<template>
  <div class="onboarding">

    <!-- Background decoration -->
    <div class="onboarding__bg-circle" />

    <!-- Logo + branding -->
    <div class="onboarding__hero">
      <div class="onboarding__logo">
        <span class="onboarding__logo-icon">🎌</span>
      </div>
      <h1 class="onboarding__title">SpeakSmart</h1>
      <p class="onboarding__subtitle">
        Japanese Pronunciation Training
      </p>
      <p class="onboarding__college">
        Gordon College — Tourism Department
      </p>
    </div>

    <!-- Feature highlights -->
    <div class="onboarding__features">
      <div
        v-for="feature in features"
        :key="feature.label"
        class="onboarding__feature"
      >
        <span class="onboarding__feature-icon">{{ feature.icon }}</span>
        <div>
          <p class="onboarding__feature-title">{{ feature.label }}</p>
          <p class="onboarding__feature-desc">{{ feature.desc }}</p>
        </div>
      </div>
    </div>

    <!-- CTA buttons -->
    <div class="onboarding__actions">
      <button class="btn btn--primary" @click="router.push('/signup')">
        Create Account
      </button>
      <button class="btn btn--ghost" @click="router.push('/login')">
        Sign In
      </button>
    </div>

    <!-- SDG note -->
    <p class="onboarding__sdg">
      Supporting SDG 4 · Quality Education &amp; SDG 8 · Decent Work
    </p>

  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    icon: '🎙️',
    label: 'Record & Score',
    desc: 'Get instant pronunciation feedback',
  },
  {
    icon: '🔤',
    label: 'Japanese-specific',
    desc: 'Mora timing, R-sound, vowel purity',
  },
  {
    icon: '📊',
    label: 'Track Progress',
    desc: 'See your improvement week by week',
  },
]
</script>

<style scoped>
.onboarding {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: 40px 28px 32px;
  background: #ffffff;
  position: relative;
  overflow: hidden;
}

.onboarding__bg-circle {
  position: absolute;
  top: -120px;
  right: -80px;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: var(--color-primary-light);
  z-index: 0;
}

.onboarding__hero {
  position: relative;
  z-index: 1;
  margin-top: 40px;
  margin-bottom: 40px;
}

.onboarding__logo {
  width: 72px;
  height: 72px;
  background: var(--color-primary);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.onboarding__logo-icon {
  font-size: 36px;
}

.onboarding__title {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-text);
  line-height: 1.1;
}

.onboarding__subtitle {
  font-size: 16px;
  color: var(--color-subtext);
  margin-top: 8px;
}

.onboarding__college {
  font-size: 13px;
  color: var(--color-primary);
  font-weight: 600;
  margin-top: 6px;
}

.onboarding__features {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.onboarding__feature {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.onboarding__feature-icon {
  font-size: 28px;
  width: 44px;
  height: 44px;
  background: var(--color-primary-light);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.onboarding__feature-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.onboarding__feature-desc {
  font-size: 13px;
  color: var(--color-subtext);
  margin-top: 2px;
}

.onboarding__actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.onboarding__sdg {
  text-align: center;
  font-size: 11px;
  color: var(--color-subtext);
  margin-top: 20px;
}

/* Shared button styles — add to style.css later */
.btn {
  width: 100%;
  padding: 16px;
  border-radius: var(--radius);
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}

.btn:active {
  transform: scale(0.98);
}

.btn--primary {
  background: var(--color-primary);
  color: #ffffff;
}

.btn--primary:hover {
  background: var(--color-primary-dark);
}

.btn--ghost {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
</style>

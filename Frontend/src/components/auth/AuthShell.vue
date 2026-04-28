<template>
  <section class="auth-page">
    <div class="auth-page__backdrop" />

    <div class="auth-page__container">
      <div class="auth-page__hero">
        <button
          v-if="backTo"
          type="button"
          class="auth-page__back button-secondary"
          @click="router.push(backTo)"
        >
          <AppIcon name="back" :size="16" />
          <span>{{ backLabel }}</span>
        </button>

        <p class="auth-page__eyebrow">{{ eyebrow }}</p>
        <h1 class="auth-page__headline">Calm practice. Clear progress.</h1>
        <p class="auth-page__copy">
          SpeakSmart brings guided Japanese pronunciation practice, responsive
          student workflows, and instructor analytics into one grounded learning
          environment.
        </p>

        <div class="auth-page__feature-grid">
          <div class="auth-page__feature surface-card surface-card--accent">
            <span class="auth-page__feature-kicker">Practice</span>
            <h2>Reference audio, recording, and scoring in one loop.</h2>
            <p>Students can listen, record, review playback, and keep moving.</p>
          </div>
          <div class="auth-page__feature surface-card">
            <span class="auth-page__feature-kicker">Teaching</span>
            <h2>Instructor dashboards stay clear and action-focused.</h2>
            <p>Track accuracy trends, weak areas, and exercise completion.</p>
          </div>
        </div>
      </div>

      <div class="auth-card surface-card">
        <div class="auth-card__header">
          <p class="auth-card__eyebrow">{{ eyebrow }}</p>
          <h2 class="auth-card__title">{{ title }}</h2>
          <p class="auth-card__subtitle">{{ subtitle }}</p>
        </div>

        <slot />

        <div v-if="$slots.footer" class="auth-card__footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppIcon from '@/components/shared/AppIcon.vue'

withDefaults(
  defineProps<{
    title: string
    subtitle: string
    eyebrow?: string
    backTo?: string
    backLabel?: string
  }>(),
  {
    eyebrow: 'Welcome',
    backTo: '/',
    backLabel: 'Back',
  },
)

const router = useRouter()
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(168, 31, 93, 0.16), transparent 28%),
    radial-gradient(circle at bottom right, rgba(193, 120, 150, 0.14), transparent 26%),
    linear-gradient(180deg, #fff7fa 0%, #fceef4 52%, #fff8fb 100%);
}

.auth-page__backdrop {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.62), transparent 42%),
    radial-gradient(circle at center right, rgba(168, 31, 93, 0.06), transparent 24%);
  pointer-events: none;
}

.auth-page__container {
  position: relative;
  z-index: 1;
  min-height: 100dvh;
  width: min(1140px, calc(100% - 32px));
  margin: 0 auto;
  display: grid;
  align-items: center;
  gap: 28px;
  padding: 24px 0;
}

.auth-page__hero {
  display: none;
  color: var(--color-heading);
}

.auth-page__back {
  width: fit-content;
  margin-bottom: 24px;
}

.auth-page__eyebrow,
.auth-card__eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.auth-page__headline {
  margin: 16px 0 0;
  font-family: var(--font-display);
  font-size: clamp(42px, 6vw, 68px);
  line-height: 0.96;
}

.auth-page__copy {
  margin: 18px 0 0;
  max-width: 520px;
  font-size: 18px;
  line-height: 1.65;
  color: var(--color-subtext);
}

.auth-page__feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 32px;
  max-width: 620px;
}

.auth-page__feature {
  padding: 20px;
}

.auth-page__feature-kicker {
  display: inline-block;
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-primary-dark);
}

.auth-page__feature h2 {
  margin: 0;
  font-size: 20px;
  line-height: 1.15;
  color: var(--color-heading);
}

.auth-page__feature p {
  margin: 12px 0 0;
  color: var(--color-subtext);
  line-height: 1.6;
}

.auth-card {
  width: min(100%, 580px);
  margin: 0 auto;
  padding: 30px 22px;
  backdrop-filter: blur(12px);
}

.auth-card__header {
  margin-bottom: 24px;
}

.auth-card__title {
  margin: 10px 0 0;
  font-family: var(--font-display);
  font-size: 34px;
  line-height: 1.03;
  color: var(--color-heading);
}

.auth-card__subtitle {
  margin: 10px 0 0;
  color: var(--color-subtext);
  line-height: 1.6;
}

.auth-card__footer {
  margin-top: 20px;
}

@media (min-width: 900px) {
  .auth-page__container {
    grid-template-columns: minmax(0, 1fr) minmax(430px, 560px);
    gap: 40px;
    width: min(1220px, calc(100% - 64px));
    padding: 40px 0;
  }

  .auth-page__hero {
    display: block;
  }

  .auth-card {
    margin: 0;
    padding: 36px 32px;
  }
}
</style>

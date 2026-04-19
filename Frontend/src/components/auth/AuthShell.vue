<template>
  <section class="auth-page">
    <div class="auth-page__backdrop" />

    <div class="auth-page__container">
      <div class="auth-page__hero">
        <button
          v-if="backTo"
          type="button"
          class="auth-page__back"
          @click="router.push(backTo)"
        >
          {{ backLabel }}
        </button>

        <p class="auth-page__eyebrow">{{ eyebrow }}</p>
        <h1 class="auth-page__headline">SpeakSmart</h1>
        <p class="auth-page__copy">
          Practice Japanese pronunciation with a role-based experience for
          students and instructors across web and mobile.
        </p>

        <div class="auth-page__feature-list">
          <div class="auth-page__feature">
            <span class="auth-page__feature-kicker">Feedback</span>
            <p>AI-assisted scoring and guided pronunciation practice.</p>
          </div>
          <div class="auth-page__feature">
            <span class="auth-page__feature-kicker">Progress</span>
            <p>Track student growth and view instructor analytics.</p>
          </div>
        </div>
      </div>

      <div class="auth-card">
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
    radial-gradient(circle at top right, rgba(29, 158, 117, 0.18), transparent 34%),
    linear-gradient(180deg, #f3fbf7 0%, #eff4f1 52%, #f7f8f7 100%);
}

.auth-page__backdrop {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.55), transparent 42%),
    radial-gradient(circle at bottom left, rgba(21, 122, 90, 0.08), transparent 28%);
  pointer-events: none;
}

.auth-page__container {
  position: relative;
  z-index: 1;
  min-height: 100dvh;
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  display: grid;
  align-items: center;
  gap: 28px;
  padding: 24px 0;
}

.auth-page__hero {
  display: none;
  color: #113127;
}

.auth-page__back {
  width: fit-content;
  margin-bottom: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.7);
  color: #155d46;
  padding: 10px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.auth-page__eyebrow,
.auth-card__eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #157a5a;
}

.auth-page__headline {
  margin-top: 14px;
  font-size: clamp(40px, 6vw, 64px);
  line-height: 0.95;
  font-weight: 900;
}

.auth-page__copy {
  margin-top: 18px;
  max-width: 480px;
  font-size: 18px;
  line-height: 1.6;
  color: #33574a;
}

.auth-page__feature-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 32px;
  max-width: 560px;
}

.auth-page__feature {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(17, 49, 39, 0.08);
  box-shadow: 0 18px 40px rgba(17, 49, 39, 0.08);
}

.auth-page__feature-kicker {
  display: inline-block;
  margin-bottom: 8px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #157a5a;
}

.auth-page__feature p {
  color: #33574a;
  line-height: 1.5;
}

.auth-card {
  width: min(100%, 560px);
  margin: 0 auto;
  padding: 28px 22px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(17, 49, 39, 0.08);
  box-shadow: 0 24px 60px rgba(17, 49, 39, 0.14);
  backdrop-filter: blur(12px);
}

.auth-card__header {
  margin-bottom: 24px;
}

.auth-card__title {
  margin-top: 10px;
  font-size: 30px;
  line-height: 1.05;
  font-weight: 800;
  color: #102419;
}

.auth-card__subtitle {
  margin-top: 10px;
  color: #52695e;
  line-height: 1.55;
}

.auth-card__footer {
  margin-top: 20px;
}

@media (min-width: 900px) {
  .auth-page__container {
    grid-template-columns: minmax(0, 1fr) minmax(420px, 520px);
    gap: 40px;
    width: min(1200px, calc(100% - 64px));
    padding: 40px 0;
  }

  .auth-page__hero {
    display: block;
  }

  .auth-card {
    margin: 0;
    padding: 34px 32px;
  }
}
</style>

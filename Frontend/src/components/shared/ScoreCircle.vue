<template>
  <div class="score-circle" :class="scoreClass">
    <svg viewBox="0 0 120 120" class="score-circle__svg">
      <circle
        cx="60" cy="60" r="50"
        fill="none"
        stroke="var(--color-border)"
        stroke-width="10"
      />
      <circle
        cx="60" cy="60" r="50"
        fill="none"
        :stroke="strokeColor"
        stroke-width="10"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        transform="rotate(-90 60 60)"
        style="transition: stroke-dashoffset 0.8s ease"
      />
    </svg>
    <div class="score-circle__content">
      <span class="score-circle__value">{{ Math.round(score) }}</span>
      <span class="score-circle__unit">%</span>
      <span class="score-circle__label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  size?: 'sm' | 'md' | 'lg'
}>()

const circumference = 2 * Math.PI * 50

const dashOffset = computed(() =>
  circumference - (props.score / 100) * circumference,
)

const strokeColor = computed(() => {
  if (props.score >= 85) return 'var(--color-success)'
  if (props.score >= 70) return '#4f9a7d'
  if (props.score >= 55) return '#b87b26'
  return '#c65549'
})

const label = computed(() => {
  if (props.score >= 85) return 'Excellent'
  if (props.score >= 70) return 'Good'
  if (props.score >= 55) return 'Needs Practice'
  return 'Keep Trying'
})

const scoreClass = computed(() => ({
  'score-circle--sm': props.size === 'sm',
  'score-circle--lg': props.size === 'lg',
}))
</script>

<style scoped>
.score-circle {
  position: relative;
  width: 160px;
  height: 160px;
  filter: drop-shadow(0 18px 28px rgba(58, 20, 39, 0.08));
}

.score-circle--sm {
  width: 80px;
  height: 80px;
}

.score-circle--lg {
  width: 200px;
  height: 200px;
}

.score-circle__svg {
  width: 100%;
  height: 100%;
}

.score-circle__content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-circle__value {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
  color: var(--color-heading);
}

.score-circle--sm .score-circle__value {
  font-size: 18px;
}

.score-circle__unit {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-subtext);
}

.score-circle--sm .score-circle__unit {
  font-size: 10px;
}

.score-circle__label {
  font-size: 11px;
  color: var(--color-subtext);
  margin-top: 6px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.score-circle--sm .score-circle__label {
  display: none;
}
</style>

<!-- src/components/shared/ScoreCircle.vue -->
<template>
  <div class="score-circle" :class="scoreClass">
    <svg viewBox="0 0 120 120" class="score-circle__svg">
      <!-- Background ring -->
      <circle
        cx="60" cy="60" r="50"
        fill="none"
        stroke="#E5E7EB"
        stroke-width="10"
      />
      <!-- Score arc -->
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

const circumference = 2 * Math.PI * 50  // 314.16

const dashOffset = computed(() =>
  circumference - (props.score / 100) * circumference
)

const strokeColor = computed(() => {
  if (props.score >= 85) return '#1D9E75'
  if (props.score >= 70) return '#10B981'
  if (props.score >= 55) return '#F59E0B'
  return '#EF4444'
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
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  color: var(--color-text);
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
  margin-top: 2px;
}

.score-circle--sm .score-circle__label {
  display: none;
}
</style>
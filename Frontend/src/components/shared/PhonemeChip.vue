<!-- src/components/shared/PhonemeChip.vue -->
<template>
  <div class="phoneme-chip" :class="chipClass">
    <span class="phoneme-chip__label">{{ label }}</span>
    <span class="phoneme-chip__score">{{ Math.round(score) }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  score: number
  error: boolean
}>()

const chipClass = computed(() => ({
  'phoneme-chip--error': props.error,
  'phoneme-chip--ok': !props.error,
}))
</script>

<style scoped>
.phoneme-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.phoneme-chip--ok {
  background: #d1fae5;
  color: #065f46;
}

.phoneme-chip--error {
  background: #fee2e2;
  color: #991b1b;
}

.phoneme-chip__score {
  font-weight: 700;
}
</style>
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
  min-height: 34px;
  padding: 7px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid transparent;
}

.phoneme-chip--ok {
  background: rgba(46, 138, 103, 0.12);
  color: #185843;
  border-color: rgba(46, 138, 103, 0.16);
}

.phoneme-chip--error {
  background: rgba(198, 85, 73, 0.12);
  color: #8b2f26;
  border-color: rgba(198, 85, 73, 0.16);
}

.phoneme-chip__score {
  font-weight: 700;
}
</style>

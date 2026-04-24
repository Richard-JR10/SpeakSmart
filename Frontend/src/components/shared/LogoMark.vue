<script setup lang="ts">
import { computed, type HTMLAttributes } from 'vue'

import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg'
    class?: HTMLAttributes['class']
  }>(),
  {
    size: 'md',
  },
)

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'size-9'
  if (props.size === 'lg') return 'size-14'
  return 'size-11'
})
</script>

<template>
  <span
    :class="
      cn(
        'inline-flex shrink-0 items-center justify-center overflow-hidden rounded-xl border border-border/70 bg-card shadow-xs',
        sizeClass,
        props.class,
      )
    "
  >
    <img
      src="/logo.png"
      alt="SpeakSmart logo"
      class="h-full w-full object-contain p-1"
      width="56"
      height="56"
    >
  </span>
</template>

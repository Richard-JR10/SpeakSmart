<template>
  <svg
    class="app-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <template v-if="name === 'home'">
      <path d="M3.5 10.5 12 4l8.5 6.5" />
      <path d="M5.5 9.5V20h13V9.5" />
      <path d="M9.5 20v-5.5h5V20" />
    </template>
    <template v-else-if="name === 'book'">
      <path d="M5 5.5a2.5 2.5 0 0 1 2.5-2.5H19v16H7.5A2.5 2.5 0 0 0 5 21.5" />
      <path d="M5 5.5v16" />
      <path d="M8.5 7.5H15" />
      <path d="M8.5 11h7.5" />
    </template>
    <template v-else-if="name === 'chart'">
      <path d="M5 19.5h14" />
      <path d="M7.5 17V11.5" />
      <path d="M12 17V7.5" />
      <path d="M16.5 17V9.5" />
    </template>
    <template v-else-if="name === 'settings'">
      <path d="M12 9.25A2.75 2.75 0 1 0 12 14.75A2.75 2.75 0 1 0 12 9.25Z" />
      <path d="M4.75 13.5 3.5 12l1.25-1.5 1.05-2.4L8.15 8l1.3-1.75L12 5.75l2.55.5L15.85 8l2.35.1 1.05 2.4L20.5 12l-1.25 1.5-1.05 2.4-2.35.1-1.3 1.75-2.55.5-2.55-.5L8.15 16l-2.35-.1-1.05-2.4Z" />
    </template>
    <template v-else-if="name === 'users'">
      <path d="M9 12.5a3 3 0 1 0 0-6a3 3 0 0 0 0 6Z" />
      <path d="M16.5 10.5a2.25 2.25 0 1 0 0-4.5a2.25 2.25 0 0 0 0 4.5Z" />
      <path d="M4.75 19c.7-2.3 2.5-3.5 4.75-3.5S13.55 16.7 14.25 19" />
      <path d="M14.75 18c.45-1.45 1.65-2.25 3.15-2.25 1.2 0 2.2.45 2.85 1.4" />
    </template>
    <template v-else-if="name === 'grid'">
      <rect x="4" y="4" width="6.5" height="6.5" rx="1.5" />
      <rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5" />
      <rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5" />
      <rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5" />
    </template>
    <template v-else-if="name === 'clipboard'">
      <rect x="5" y="5.5" width="14" height="15" rx="2" />
      <path d="M9 5.5V4.75A1.75 1.75 0 0 1 10.75 3h2.5A1.75 1.75 0 0 1 15 4.75v.75" />
      <path d="M9 10h6" />
      <path d="M9 14h6" />
    </template>
    <template v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="5.5" />
      <path d="m19 19-3.5-3.5" />
    </template>
    <template v-else-if="name === 'play'">
      <path d="M8 6.5v11l8-5.5-8-5.5Z" />
    </template>
    <template v-else-if="name === 'mic'">
      <rect x="9" y="4" width="6" height="10" rx="3" />
      <path d="M6.5 11.5a5.5 5.5 0 0 0 11 0" />
      <path d="M12 17v3.5" />
      <path d="M9 20.5h6" />
    </template>
    <template v-else-if="name === 'refresh'">
      <path d="M19 8.5V4.75h-3.75" />
      <path d="M18.5 11a6.5 6.5 0 1 0-1.9 4.6" />
    </template>
    <template v-else-if="name === 'alert'">
      <path d="m12 4 8 14H4l8-14Z" />
      <path d="M12 9v4.5" />
      <path d="M12 17h.01" />
    </template>
    <template v-else-if="name === 'spark'">
      <path d="m12 3 1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3Z" />
      <path d="m18.5 15 .8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z" />
      <path d="M4.5 14.5 5 16l1.5.5L5 17l-.5 1.5L4 17l-1.5-.5L4 16l.5-1.5Z" />
    </template>
    <template v-else-if="name === 'wave'">
      <path d="M6 18c2-5 2-9 0-12" />
      <path d="M12 20c2-6.5 2-9.5 0-16" />
      <path d="M18 18c2-5 2-9 0-12" />
    </template>
    <template v-else-if="name === 'building'">
      <path d="M6 20V6.5L12 4l6 2.5V20" />
      <path d="M9 9.5h.01" />
      <path d="M12 9.5h.01" />
      <path d="M15 9.5h.01" />
      <path d="M9 13h.01" />
      <path d="M12 13h.01" />
      <path d="M15 13h.01" />
      <path d="M10.5 20v-3.5h3V20" />
    </template>
    <template v-else-if="name === 'compass'">
      <circle cx="12" cy="12" r="8" />
      <path d="m14.75 9.25-2.15 5.5-5.35 2.1 2.15-5.45 5.35-2.15Z" />
    </template>
    <template v-else-if="name === 'bowl'">
      <path d="M5 11.5h14" />
      <path d="M6 11.5c.45 4.2 2.8 6.5 6 6.5s5.55-2.3 6-6.5" />
      <path d="M8.5 8.5c0-1 .6-1.4 1.1-1.8.55-.4 1.1-.8 1.1-1.9" />
      <path d="M12 8.5c0-1 .6-1.4 1.1-1.8.55-.4 1.1-.8 1.1-1.9" />
    </template>
    <template v-else-if="name === 'shield'">
      <path d="M12 4 18.5 6.5v5.3c0 4.1-2.4 6.8-6.5 8.2-4.1-1.4-6.5-4.1-6.5-8.2V6.5L12 4Z" />
      <path d="m9.5 12 1.8 1.8 3.7-4" />
    </template>
    <template v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="8" />
      <path d="M4.5 12h15" />
      <path d="M12 4a12.2 12.2 0 0 1 0 16" />
      <path d="M12 4a12.2 12.2 0 0 0 0 16" />
    </template>
    <template v-else-if="name === 'logout'">
      <path d="M10.5 5H7.75A1.75 1.75 0 0 0 6 6.75v10.5C6 18.22 6.78 19 7.75 19h2.75" />
      <path d="M13 8.5 17 12l-4 3.5" />
      <path d="M9.5 12H17" />
    </template>
    <template v-else-if="name === 'close'">
      <path d="m6 6 12 12" />
      <path d="M18 6 6 18" />
    </template>
    <template v-else-if="name === 'plus'">
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </template>
    <template v-else-if="name === 'trash'">
      <path d="M5 7.5h14" />
      <path d="M9 7.5V5.75A1.75 1.75 0 0 1 10.75 4h2.5A1.75 1.75 0 0 1 15 5.75V7.5" />
      <path d="m8 7.5.7 10.25A1.5 1.5 0 0 0 10.2 19h3.6a1.5 1.5 0 0 0 1.5-1.25L16 7.5" />
      <path d="M10.25 10.5v5" />
      <path d="M13.75 10.5v5" />
    </template>
    <template v-else-if="name === 'back'">
      <path d="m14.5 6-6 6 6 6" />
    </template>
    <template v-else-if="name === 'forward'">
      <path d="m9.5 6 6 6-6 6" />
    </template>
  </svg>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    name: string
    size?: number
  }>(),
  {
    size: 20,
  },
)
</script>

<style scoped>
.app-icon {
  stroke: currentColor;
  stroke-width: 1.85;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}
</style>

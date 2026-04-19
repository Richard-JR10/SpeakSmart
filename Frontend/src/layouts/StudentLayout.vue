<!-- src/layouts/StudentLayout.vue -->
<template>
  <div class="student-layout">

    <!-- Top bar -->
    <TopBar :title="title" :show-back="showBack" @back="router.back()" />

    <!-- Main content -->
    <main class="student-layout__content">
      <slot />
    </main>

    <!-- Bottom navigation -->
    <BottomNav />

  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import TopBar from '@/components/shared/TopBar.vue'
import BottomNav from '@/components/shared/BottomNav.vue'

defineProps<{
  title: string
  showBack?: boolean
}>()

const router = useRouter()
</script>

<style scoped>
.student-layout {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  width: min(100%, 480px);
  margin: 0 auto;
  background: #ffffff;
  overflow: hidden;
}

.student-layout__content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 80px; /* space for bottom nav */
  -webkit-overflow-scrolling: touch;
}
</style>

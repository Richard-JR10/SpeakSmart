<template>
  <div class="student-layout">
    <TopBar :title="title" :show-back="showBack" @back="router.back()" />
    <main class="student-layout__content">
      <div class="student-layout__content-inner">
        <slot />
      </div>
    </main>
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
  min-height: 100dvh;
  width: min(100%, 500px);
  margin: 0 auto;
  background:
    radial-gradient(circle at top, rgba(46, 138, 103, 0.08), transparent 28%),
    linear-gradient(180deg, rgba(250, 247, 239, 0.96), rgba(242, 238, 230, 0.98));
  overflow: hidden;
}

.student-layout__content {
  flex: 1;
  overflow-y: auto;
  padding: 0 0 110px;
  -webkit-overflow-scrolling: touch;
}

.student-layout__content-inner {
  min-height: 100%;
}
</style>

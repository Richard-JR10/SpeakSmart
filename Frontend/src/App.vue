<template>
  <div v-if="authStore.loading" class="flex items-center justify-center h-screen">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      <p class="text-sm text-gray-400">Loading SpeakSmart...</p>
    </div>
  </div>
  <RouterView v-else />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import {RouterView} from 'vue-router'
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
onMounted(() => {
  authStore.initAuth();
});
</script>
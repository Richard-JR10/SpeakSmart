<template>
  <div class="password-checklist">
    <p class="password-checklist__title">Password requirements</p>

    <ul class="password-checklist__list">
      <li
        v-for="item in checklist"
        :key="item.label"
        class="password-checklist__item"
        :class="{ 'password-checklist__item--met': item.met }"
      >
        <span class="password-checklist__indicator" />
        <span>{{ item.label }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  password: string
}>()

const checklist = computed(() => [
  {
    label: 'At least 8 characters',
    met: props.password.length >= 8,
  },
  {
    label: 'At least one uppercase letter',
    met: /[A-Z]/.test(props.password),
  },
  {
    label: 'At least one number',
    met: /\d/.test(props.password),
  },
  {
    label: 'At least one special character',
    met: /[^A-Za-z0-9]/.test(props.password),
  },
])
</script>

<style scoped>
.password-checklist {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f6faf8;
  border: 1px solid #ddebe4;
}

.password-checklist__title {
  font-size: 13px;
  font-weight: 700;
  color: #26473a;
}

.password-checklist__list {
  list-style: none;
  display: grid;
  gap: 8px;
  margin-top: 12px;
  padding: 0;
}

.password-checklist__item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #5f776b;
  font-size: 14px;
}

.password-checklist__item--met {
  color: #146649;
}

.password-checklist__indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #c3d2ca;
  flex-shrink: 0;
}

.password-checklist__item--met .password-checklist__indicator {
  background: var(--color-primary);
}
</style>

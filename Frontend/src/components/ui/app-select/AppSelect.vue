<template>
  <SelectRoot
    :model-value="props.modelValue ?? undefined"
    :disabled="props.disabled"
    @update:model-value="handleUpdate"
  >
    <SelectTrigger
      :aria-label="props.ariaLabel"
      :class="cn(
        'inline-flex h-9 min-w-0 items-center justify-between gap-2 rounded-xl border-2 border-primary/65 bg-card px-3 text-sm font-semibold text-foreground shadow-sm shadow-primary/10 ring-1 ring-primary/25 outline-none transition hover:border-primary hover:bg-primary/5 hover:ring-primary/35 focus-visible:ring-2 focus-visible:ring-primary/35 disabled:cursor-not-allowed disabled:opacity-60 data-[state=open]:border-primary data-[state=open]:bg-primary/5 data-[state=open]:ring-2 data-[state=open]:ring-primary/30',
        props.triggerClass,
      )"
    >
      <span class="flex min-w-0 items-center gap-2">
        <slot name="icon" />
        <SelectValue
          :placeholder="props.placeholder"
          class="truncate"
        />
      </span>
      <ChevronDown class="size-4 shrink-0 text-muted-foreground transition-transform duration-200 data-[state=open]:rotate-180" />
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        position="popper"
        :side-offset="6"
        :class="cn(
          'z-50 max-h-72 min-w-[var(--reka-select-trigger-width)] overflow-hidden rounded-xl border border-border bg-popover text-popover-foreground shadow-lg data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          props.contentClass,
        )"
      >
        <SelectViewport class="p-1">
          <SelectItem
            v-for="option in props.options"
            :key="option.value"
            :value="option.value"
            :disabled="option.disabled"
            class="relative flex cursor-default select-none items-center rounded-lg py-2 pr-9 pl-3 text-sm outline-none transition-colors data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[highlighted]:bg-muted data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
          >
            <SelectItemText class="truncate">
              {{ option.label }}
            </SelectItemText>
            <SelectItemIndicator class="absolute right-2 flex size-4 items-center justify-center">
              <Check class="size-4" />
            </SelectItemIndicator>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>

<script setup lang="ts">
import { Check, ChevronDown } from 'lucide-vue-next'
import {
  SelectContent,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from 'reka-ui'

import { cn } from '@/lib/utils'

export interface AppSelectOption {
  value: string
  label: string
  disabled?: boolean
}

const props = withDefaults(defineProps<{
  modelValue: string | null
  options: AppSelectOption[]
  placeholder?: string
  disabled?: boolean
  ariaLabel?: string
  triggerClass?: string
  contentClass?: string
}>(), {
  placeholder: 'Select an option',
  disabled: false,
  ariaLabel: undefined,
  triggerClass: '',
  contentClass: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

function handleUpdate(value: unknown) {
  emit('update:modelValue', typeof value === 'string' && value ? value : null)
}
</script>

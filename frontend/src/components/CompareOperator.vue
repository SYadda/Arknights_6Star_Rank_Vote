<script setup>
defineProps({
  operator: Object,
})

const emit = defineEmits(['select'])

function handleSelect(operator) {
  emit('select', operator)
}
</script>

<template>
  <Operator class="operator" :avatar="operator.avatar" :name="operator.name" @click="handleSelect(operator)" />
</template>

<style scoped>
.operator:hover {
    filter: var(--drop-shadow-1);
    transition: filter .1s ease-in-out;
}
</style>

<script setup>
const { name, avatar } = defineProps({
  avatar: String,
  name: String,
})
</script>

<template>
  <div class="operator">
    <img class="avatar" :src="avatar" width="180" height="360">
    <div class="zh name">
      {{ name }}
    </div>
  </div>
</template>

<style scoped>
.operator {
    position: relative;
}

.avatar {
    width: 100%;
    object-fit: cover;
}

.name {
    position: absolute;
    width: 100%;
    left: 0;
    bottom: 1px;
    text-align: center;
    color: var(--c-bg-elv);
}
</style>

<script setup>
defineProps({
  /** {key, label}[] */
  nav: Array,
})

const selectIndex = defineModel()

function handleSelect(index) {
  selectIndex.value = index
}
</script>

<template>
  <Container class="menu">
    <ul class="nav">
      <li v-for="(item, index) in nav" :key="item.key" @click="handleSelect(index)">
        {{ item.text }}
      </li>
    </ul>
  </Container>
</template>

<style scoped>
.menu {
    text-align: center;
}

.nav li {
    display: inline-block;
    margin: 0 10px;
    cursor: pointer;
}

.nav li:hover {
    text-decoration: underline;
}
</style>

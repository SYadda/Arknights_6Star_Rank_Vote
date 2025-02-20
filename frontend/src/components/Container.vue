<template>
  <div class="container">
    <slot />
  </div>
</template>

<style scoped>
.container {
    box-shadow: var(--shadow-1);
    border-radius: 8px;
    padding: 20px;
    margin: 10px;
    background-color: var(--c-bg-soft);
    /* background-color: rgba(0, 0, 0, 0.01); */
    backdrop-filter: blur(5px);
}
</style>

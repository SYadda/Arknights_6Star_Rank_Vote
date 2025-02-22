<template>
  <MouseFollower />
  <div class="main">
    <router-view />
  </div>
</template>

<style>
body {
    background-color: var(--c-bg-1);
    background: var(--img-bg) center top no-repeat fixed;
    background-size: cover;
}

#app {
    max-width: var(--layout-max-width);
    margin: 0 auto;
    display: flex;
    flex-flow: column nowrap;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}
</style>

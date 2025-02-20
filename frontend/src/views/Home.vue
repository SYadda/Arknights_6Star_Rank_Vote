<script setup>
const navIndex = ref(0)
const nav = [
  {
    key: 'main',
    text: '投票',
  },
  {
    key: 'final',
    text: '投票结果',
  },
  {
    key: 'own',
    text: '您的投票结果',
  },
  {
    key: 'matrix',
    text: '1v1对位矩阵',
  },
]

const visible = reactive({
  final: false,
  own: false,
  matrix: false,
})
const panelVisible = ref(false)

function openPanel() {
  panelVisible.value = true
}

function closePanel() {
  panelVisible.value = false
  navIndex.value = 0
}

function closeAllPanel() {
  visible.final = false
  visible.own = false
  visible.matrix = false
}

watch(navIndex, (i) => {
  if (i === 0) {
    return
  }
  closeAllPanel()
  const key = nav[i].key
  visible[key] = true

  openPanel()
})
</script>

<template>
  <div class="container">
    <div class="main" :class="{ 'hide-main': panelVisible }">
      <SiteTitle />
      <Compare />
      <Menu v-model="navIndex" :nav="nav" />
    </div>
  </div>

  <Panel v-model="panelVisible" @close="closePanel">
    <template #default>
      <div class="panel-content">
        <FinalOrder v-show="visible.final" :tbody-style="{ height: '70vh' }" />
        <FinalOrderOwn v-show="visible.own" :tbody-style="{ height: '70vh' }" />

        <div v-show="visible.matrix">
          待重构...
        </div>
      </div>
    </template>
    <template #footer>
      <div class="panel-menu">
        <button
          v-for="(menu, index) in nav.slice(1)" :key="menu.key" class="panel-menu-btn"
          :class="{ active: navIndex === index + 1 }" @click="navIndex = index + 1"
        >
          {{ menu.text }}
        </button>
      </div>
    </template>
  </Panel>
</template>

<style scoped>
.container {
    perspective: 500px;
}

.main {
    transition: all .5s ease;
    transform-origin: left;
}

.hide-main {
    transform: translateX(-50%) rotateY(45deg);
}

.menu {
    transition: all .5s ease;
    transform-origin: right;
}

.hide-main .menu {
    transform: rotateZ(90deg);
    color: var(--c-bg-soft);
}

/*
 * --------------------------
 */

.panel-content {
    display: flex;
    flex-flow: column nowrap;
    gap: 20px;
}

.panel-menu {
    margin-right: 1em;
}

.panel-menu-btn {
    display: inline-block;
    padding: .5em 1em;
    background-color: transparent;
    position: relative;
}

.panel-menu .active::before {
    display: block;
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    height: .2em;
    width: 100%;
    background-color: var(--c-text-1);
}
</style>

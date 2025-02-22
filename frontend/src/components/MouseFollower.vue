<script setup>
const { width: screenWidth, height: screenHeight } = useWindowSize()
const { x, y } = usePointer()

const el = useTemplateRef('el')
const { width, height } = useElementSize(el)

const left = ref(0)
const top = ref(0)

const update = useThrottleFn(() => {
  if (!el.value)
    return

  left.value = x.value + width.value + 21 > screenWidth.value ? x.value - width.value - 21 : x.value
  top.value = y.value + height.value + 21 > screenHeight.value ? y.value - height.value - 21 : y.value
}, 60)

watch([width, height, x, y], update)
</script>

<template>
  <img
    ref="el"
    class="mouse-follower"
    src="../assets/images/夕trans.gif"
    :style="{
      left: `${left}px`,
      top: `${top}px`,
    }"
  >
</template>

<style scoped>
.mouse-follower {
    position: fixed;
    z-index: 99999;
    width: 100px;
    vertical-align: middle;
    transition: left 0.3s ease, top 0.3s ease;
    user-select: none;
    pointer-events: none;
}
</style>

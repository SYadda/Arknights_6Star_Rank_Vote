<script setup>
const { operator1, operator2, voteForWinner } = useCompareStore()
</script>

<template>
  <Container class="compare-operator">
    <CompareOperator :operator="operator1" @select="() => voteForWinner(operator1)" />
    <slot />
    <CompareOperator :operator="operator2" @select="() => voteForWinner(operator2)" />
  </Container>
</template>

<style scoped>
.compare-operator {
    display: flex;
    justify-content: space-between;
    gap: 50px;
    height: 100%;
    align-self: center;
}

.vs {
    height: 100%;
    align-self: center;
    font-size: 2.5em;
    font-weight: 700;
}
</style>

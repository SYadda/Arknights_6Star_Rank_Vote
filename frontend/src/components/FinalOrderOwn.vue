<script setup>
defineProps(['tbodyStyle'])

const { getFinalOrder } = useLocalVoteStore()

const labels = [
  { text: '干员代号', key: 'name', style: { width: '9em' } },
  { text: '胜率', key: 'rate', style: { width: '6em' } },
  { text: '得分', key: 'score', style: { width: '9em' } },
]
</script>

<template>
  <div>
    <VoteTable :data="getFinalOrder()" :labels="labels" cluster-key="rate" :tbody-style="tbodyStyle" />
  </div>
</template>

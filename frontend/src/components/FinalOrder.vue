<script setup>
import { apiViewFinalOrder } from '@/api/view_final_order'

defineProps(['tbodyStyle'])

const data = shallowRef({})

const labels = [
  { text: '干员代号', key: 'name', style: { width: '9em' } },
  { text: '胜率', key: 'rate', style: { width: '6em' } },
  { text: '得分', key: 'score', style: { width: '9em' } },
]

onMounted(() => {
  apiViewFinalOrder((res) => {
    data.value = res
  })
})
</script>

<template>
  <VoteTable :data="data" :labels="labels" cluster-key="rate" :tbody-style="tbodyStyle" />
</template>

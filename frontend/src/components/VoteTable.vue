<script setup>
const { data, labels, clusterKey = 'rate', tbodyStyle = {} } = defineProps({
  /**
   * { name[], rate[], score[] }
   */
  data: Object,

  /**
   * { text, key?: data 的 key, transform?: (col)=> string }[]
   */
  labels: Array,

  /**
   * clusterKey
   */
  clusterKey: String,

  tbodyStyle: [String, Object],
})

const cupLevels = ['超大杯上', '超大杯中', '超大杯下', '大杯上', '大杯中', '大杯下', '中杯上', '中杯中', '中杯下']

const GVF = ref(0)
const colors = shallowRef([])
const showLables = shallowRef([])
const showData = shallowRef({})
//
// order
// -----------------------------------------

const orderLabel = {
  text: '排名',
  transform: i => i + 1,
  style: { width: '3em' },
}

//
// cup level
// -----------------------------------------

const cupLabel = {
  text: '杯级',
  key: 'cup',
  style: {
    width: '6em',
  },
}

function buildCupData(clusterItems) {
  const data = []
  clusterItems.forEach((items, i) => {
    items.forEach(() => {
      data.push(cupLevels[i])
    })
  })

  return {
    cup: data,
  }
}

//
//
// -----------------------------------------
function updateLabels() {
  showLables.value = [
    cupLabel,
    orderLabel,
    ...labels,
  ]
}

function updateData(clusterItems) {
  showData.value = { ...buildCupData(clusterItems), ...data }
}

//
// -----------------------------------------

watch(() => data, (v) => {
  if (!v || !Object.keys(v).length)
    return

  const { data: items, GVF: gvf } = getBestCluster(data[clusterKey].map(r => Number.parseFloat(r)))

  colors.value = getColors(items.reverse())
  GVF.value = gvf

  updateLabels()
  updateData(items)
})

function getValueByPos(col, label) {
  if (label.key) {
    return showData.value[label.key][col]
  }
  else {
    return label.transform ? label.transform(col) : ''
  }
}
</script>

<template>
  <table>
    <caption>区分度: {{ parseFloat(GVF).toFixed(4) * 100 }}%</caption>
    <thead>
      <tr>
        <th v-for="label in showLables" :key="label.text" :style="label.style">
          {{ label.text }}
        </th>
      </tr>
    </thead>
    <tbody :style="tbodyStyle">
      <tr
        v-for="(_, col) in data[clusterKey]" :key="col"
        :style="{ backgroundColor: `#${colors[col]}` }"
      >
        <td v-for="(label, index) in showLables" :key="index" :style="label.style">
          {{ getValueByPos(col, label) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
table,
caption,
thead,
tbody,
tfoot {
    display: block;
}

table {
    border-collapse: collapse;
    margin: 0;
    padding: 0;
    overflow: auto;
}

caption {
    text-align: right;
}

thead {
    position: sticky;
    top: 0;
}

tbody {
    overflow: hidden;
    overflow: auto;
}

th,
td {
    margin: 0;
    padding: 8px;
    text-align: center;
    border: 1px solid #ccc;
    border: none;
}
</style>

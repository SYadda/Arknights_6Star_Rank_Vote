import Geostats from 'geostats'

function getClusterList(data_array, bound_list) {
  let i
  let j
  let k = 0
  let first
  let last

  const cluster_list = []
  if (bound_list[1] === data_array[1]) {
    k = 1
    cluster_list.push(data_array.slice(0, k))
  }
  for (i = 1, j = k; i < bound_list.length - 1; i++, j = k) {
    first = data_array.indexOf(bound_list[i], j)
    last = data_array.lastIndexOf(bound_list[i])
    if (bound_list[i] === bound_list[i + 1]) {
      k = first + 1
    }
    else {
      k = last + 1
    }
    cluster_list.push(data_array.slice(j, k))
  }
  cluster_list.push(data_array.slice(j))

  return cluster_list
}

function getSDCM(cluster_list) {
  const serie = new Geostats(cluster_list[0])
  let SDCM = serie.variance() // the Sum of squared Deviations about Class Mean

  for (let i = 1; i < cluster_list.length; i++) {
    serie.setSerie(cluster_list[i])
    SDCM += serie.variance()
  }
  return SDCM
}

export function getBestCluster(data_array) {
  const serie = new Geostats(data_array)
  const SDAM = serie.variance()

  let cluster_list
  let nclasses = 3 // 聚类簇数
  let GVF // The Goodness of Variance Fit 方差拟合优度
  do {
    cluster_list = getClusterList(serie.serie, serie.getClassJenks2(nclasses++))
    GVF = 1 - getSDCM(cluster_list) / SDAM
  } while (GVF < 0.8)

  return {
    data: cluster_list,
    GVF,
  }
}

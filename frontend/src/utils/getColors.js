import palette from 'google-palette'

export function getColors(cluster_list) {
  const color_list = []
  palette('rainbow', cluster_list.length, 0, 0.5, 0.95).forEach((color, i) => {
    color_list.push(...Array.from({ length: cluster_list[i].length }).fill(color))
  })
  return color_list
}

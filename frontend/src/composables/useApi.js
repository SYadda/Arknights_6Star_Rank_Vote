import { createFetch } from '@vueuse/core'

export const useApi = createFetch({
  baseUrl: 'https://vote.ltsc.vip',
  options: {
    headers: {
      'Content-Type': 'application/json',
    },
  },
})

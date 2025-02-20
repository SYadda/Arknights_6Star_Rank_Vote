import { getCode, updateCode } from './new_compare'

/**
 * `{ win_id: number, lose_id: number }`
 */
export function apiSaveScore(body, onResponse) {
  body.code = getCode()
  const { data, onFetchResponse, onFetchError } = useApi('/save_score', { data: body }).post().json()

  onFetchResponse(() => {
    updateCode(data.value.code)
    onResponse && onResponse(data.value)
  })

  // mock
  onFetchError(() => {
    onResponse && onResponse({ mock: true })
  })
}

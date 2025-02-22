const CODE_KEY = 'compare_code'

export function getCode() {
  return localStorage.getItem(CODE_KEY) || '000'
}

export function updateCode(code) {
  localStorage.setItem(CODE_KEY, code)
}

export function apiNewCompare(onResponse) {
  const code = getCode()
  const { data, onFetchResponse, onFetchError } = useApi('/new_compare', { data: { code } }).post().json()

  onFetchResponse(() => {
    updateCode(data.value.code)
    onResponse && onResponse(data.value)
  })

  // mock
  const mock = [
    { left: 437, right: 291, code: '910894249787269120' },
    { left: 1014, right: 420, code: '910894249787269121' },
    { left: 1013, right: 2015, code: '910894249787269122' },
  ]
  onFetchError(() => {
    const res = mock[~~(Math.random() * mock.length)]
    updateCode(res.code)
    onResponse && onResponse({ ...res, mock: true })
  })
}

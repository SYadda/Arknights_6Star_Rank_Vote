import { readonly } from 'vue'
import operators from './data/operators.json'

/**
 * readonly( { data, total } )
 */
let _operators = null
const _idMapCache = {}

function getIdKey(id) {
  return `id${id}`
}

function initInfo() {
  if (_operators)
    return
  const info = {
    data: operators,
    total: Object.keys(operators).length,
  }

  _operators = readonly(info)

  Object.entries(operators).forEach(([k, v]) => {
    _idMapCache[getIdKey(v.id)] = k
  })
}

export function toOperatorKey(nameOrId) {
  return !nameOrId
    ? null
    : typeof nameOrId === 'string' ? nameOrId : _idMapCache[getIdKey(nameOrId)]
}

/**
 * Information of operators
 */
export function useOperators() {
  initInfo()
  return _operators
}

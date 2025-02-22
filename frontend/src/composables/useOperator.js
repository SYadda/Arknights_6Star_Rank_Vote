import { toOperatorKey } from './useOperators'

/**
 * Get data of operator by name or id
 *
 * @example
 *
 * ```js
 * // Basic
 * const { update, operator } = useOperator()
 * console.log(operator)                  // { name: null, id: null, avatar: null }
 *
 * // use name
 * update("荒芜拉普兰德")                 // { name: "荒芜拉普兰德", ... }
 *
 * // use id
 * update(4026)                           // { name: "忍冬", ... }
 *
 * // Initial data
 * const { update, operator } = useOperator("荒芜拉普兰德")
 * console.log(operator)                  // { name: "荒芜拉普兰德", ... }
 * ```
 */
export function useOperator(nameOrId) {
  const { data: operators } = useOperators()

  const nameRef = ref(toOperatorKey(nameOrId))

  const operator = reactive({})

  function up(name) {
    const data = name ? operators[name] : { id: null, avatar: null }
    operator.name = name
    operator.id = data.id
    operator.avatar = data.avatar
  }

  watch(nameRef, up)

  return {
    update: name => (nameRef.value = toOperatorKey(name)),
    operator: readonly(operator),
  }
}

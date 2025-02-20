import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
}, {
  rules: {
    'no-undef': 'off',
  },
})

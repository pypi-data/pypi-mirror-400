module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat','fix','test','chore','docs','refactor','perf','ci','build','revert']],
    'header-max-length': [2, 'always', 72]
  }
}

import tsParser from '@typescript-eslint/parser'

export default [
  // Ignore build artifacts
  { ignores: ['dist/**', 'node_modules/**', 'public/**'] },

  // JS/TS files
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      quotes: ['warn', 'single', { avoidEscape: true }],
      semi: ['warn', 'never']
    },
  },
]

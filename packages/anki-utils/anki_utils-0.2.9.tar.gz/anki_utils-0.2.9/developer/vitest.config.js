import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./developer/tests/setup.js'],
    include: ['developer/tests/**/*.test.{js,jsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['anki_utils/assets/**/*.{js,jsx}'],
    },
  },
});

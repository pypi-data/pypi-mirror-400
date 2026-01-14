export default {
  testEnvironment: 'jsdom',
  testMatch: ['**/tests/frontend/**/*.test.js'],
  collectCoverageFrom: ['markdeck/static/**/*.js'],
  coveragePathIgnorePatterns: ['/node_modules/'],
  moduleFileExtensions: ['js'],
  transform: {},
  setupFilesAfterEnv: ['./tests/frontend/setup.js'],
  globals: {
    'window': {},
    TextEncoder: TextEncoder,
    TextDecoder: TextDecoder
  }
};

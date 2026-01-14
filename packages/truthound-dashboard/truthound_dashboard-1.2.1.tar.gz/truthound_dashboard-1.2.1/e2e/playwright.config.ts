/**
 * Playwright configuration for E2E testing.
 */

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  // Test directory
  testDir: './tests',

  // Test timeout
  timeout: 30000,

  // Expect timeout
  expect: {
    timeout: 5000,
  },

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [['html', { open: 'never' }], ['list']],

  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: 'http://localhost:8765',

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Take screenshot on failure
    screenshot: 'only-on-failure',

    // Video on first retry
    video: 'on-first-retry',
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile viewports
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Run your local dev server before starting the tests
  webServer: {
    command: 'cd .. && truthound serve --no-browser',
    url: 'http://localhost:8765',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})

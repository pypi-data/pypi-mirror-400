/**
 * E2E tests for Notifications page.
 */

import { test, expect } from '@playwright/test'

test.describe('Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/notifications')
  })

  test('should load notifications page', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText(/notifications/i)
  })

  test('should display tabs for channels, rules, and logs', async ({ page }) => {
    // Check tabs are visible
    await expect(page.getByRole('tab', { name: /channels/i })).toBeVisible()
    await expect(page.getByRole('tab', { name: /rules/i })).toBeVisible()
    await expect(page.getByRole('tab', { name: /logs/i })).toBeVisible()
  })

  test('should switch between tabs', async ({ page }) => {
    // Click Rules tab
    await page.getByRole('tab', { name: /rules/i }).click()
    await expect(page.getByRole('tab', { name: /rules/i })).toHaveAttribute(
      'data-state',
      'active'
    )

    // Click Logs tab
    await page.getByRole('tab', { name: /logs/i }).click()
    await expect(page.getByRole('tab', { name: /logs/i })).toHaveAttribute(
      'data-state',
      'active'
    )

    // Back to Channels tab
    await page.getByRole('tab', { name: /channels/i }).click()
    await expect(page.getByRole('tab', { name: /channels/i })).toHaveAttribute(
      'data-state',
      'active'
    )
  })

  test('should display add channel button', async ({ page }) => {
    const addButton = page.getByRole('button', { name: /add channel/i })
    await expect(addButton).toBeVisible()
  })

  test('should display add rule button on rules tab', async ({ page }) => {
    // Switch to rules tab
    await page.getByRole('tab', { name: /rules/i }).click()

    const addButton = page.getByRole('button', { name: /add rule/i })
    await expect(addButton).toBeVisible()
  })

  test('should display stats cards', async ({ page }) => {
    // Stats cards should be visible
    await expect(page.getByText(/total.*24h/i)).toBeVisible()
    await expect(page.getByText(/success rate/i)).toBeVisible()
  })
})

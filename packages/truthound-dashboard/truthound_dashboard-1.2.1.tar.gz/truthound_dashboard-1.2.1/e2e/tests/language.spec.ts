/**
 * E2E tests for Language switching.
 */

import { test, expect } from '@playwright/test'

test.describe('Language', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should toggle between English and Korean', async ({ page }) => {
    // Find the language toggle button
    const langButton = page.locator('button[title="Change language"]')
    await expect(langButton).toBeVisible()

    // Check initial navigation text (should be in one language)
    const dashboardLink = page.getByRole('link').filter({ hasText: /(Dashboard|대시보드)/ })
    await expect(dashboardLink).toBeVisible()

    const initialText = await dashboardLink.textContent()

    // Click to toggle language
    await langButton.click()
    await page.waitForTimeout(300)

    // Check that text changed
    const newText = await dashboardLink.textContent()
    expect(newText).not.toBe(initialText)
  })

  test('should persist language preference', async ({ page }) => {
    // Click language toggle
    const langButton = page.locator('button[title="Change language"]')
    await langButton.click()
    await page.waitForTimeout(300)

    // Get current text
    const dashboardLink = page.getByRole('link').filter({ hasText: /(Dashboard|대시보드)/ })
    const currentText = await dashboardLink.textContent()

    // Reload page
    await page.reload()

    // Check language persisted
    await expect(dashboardLink).toHaveText(currentText || '')
  })
})

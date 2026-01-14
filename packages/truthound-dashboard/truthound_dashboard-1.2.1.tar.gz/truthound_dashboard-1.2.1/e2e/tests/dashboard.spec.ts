/**
 * E2E tests for Dashboard page.
 */

import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should load dashboard page', async ({ page }) => {
    // Check page title or main heading
    await expect(page.locator('h1, h2').first()).toBeVisible()
  })

  test('should display navigation sidebar', async ({ page }) => {
    // Check sidebar is visible (desktop)
    const sidebar = page.locator('aside')
    await expect(sidebar).toBeVisible()

    // Check navigation links
    await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /sources/i })).toBeVisible()
  })

  test('should navigate to sources page', async ({ page }) => {
    await page.getByRole('link', { name: /sources/i }).click()
    await expect(page).toHaveURL(/.*sources/)
  })

  test('should navigate to notifications page', async ({ page }) => {
    await page.getByRole('link', { name: /notifications/i }).click()
    await expect(page).toHaveURL(/.*notifications/)
  })
})

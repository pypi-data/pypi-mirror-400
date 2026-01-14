/**
 * E2E tests for Theme switching.
 */

import { test, expect } from '@playwright/test'

test.describe('Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should toggle between light and dark themes', async ({ page }) => {
    // Get the html element to check class
    const html = page.locator('html')

    // Find and click the theme toggle button
    const themeButton = page.locator('button[title="Toggle theme"]')
    await expect(themeButton).toBeVisible()

    // Get initial theme
    const initialClass = await html.getAttribute('class')

    // Click to toggle theme
    await themeButton.click()

    // Wait for class to change
    await page.waitForTimeout(300)

    // Check that class changed
    const newClass = await html.getAttribute('class')
    expect(newClass).not.toBe(initialClass)
  })

  test('should persist theme preference', async ({ page }) => {
    // Click theme toggle to change theme
    const themeButton = page.locator('button[title="Toggle theme"]')
    await themeButton.click()
    await page.waitForTimeout(300)

    // Get current theme
    const html = page.locator('html')
    const currentClass = await html.getAttribute('class')

    // Reload page
    await page.reload()

    // Check theme persisted
    await expect(html).toHaveAttribute('class', currentClass || '')
  })
})

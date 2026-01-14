/**
 * Test utilities for rendering components with providers
 */

import { ReactElement, ReactNode } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Wrapper that includes all providers needed for testing
function AllProviders({ children }: { children: ReactNode }) {
  return <BrowserRouter>{children}</BrowserRouter>
}

// Custom render function that includes providers
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllProviders, ...options })
}

// Re-export everything from testing-library
export * from '@testing-library/react'

// Override render with custom render
export { customRender as render }

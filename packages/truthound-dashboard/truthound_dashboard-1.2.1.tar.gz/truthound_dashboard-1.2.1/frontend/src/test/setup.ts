/**
 * Vitest setup file - configures testing environment
 */

import '@testing-library/jest-dom'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock window.matchMedia for components using media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})

// Mock ResizeObserver for components using it
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock IntersectionObserver for infinite scroll, lazy loading, etc.
global.IntersectionObserver = class IntersectionObserver {
  root = null
  rootMargin = ''
  thresholds: number[] = []

  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
}

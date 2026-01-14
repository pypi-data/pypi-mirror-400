/**
 * MSW Browser Worker Setup
 * Initializes mock service worker for browser environment
 */

import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)

/**
 * Initialize MSW worker
 * Call this before rendering the app in mock mode
 */
export async function initMockWorker(): Promise<void> {
  // Only enable in development or when VITE_MOCK_API is set
  if (import.meta.env.VITE_MOCK_API !== 'true') {
    return
  }

  await worker.start({
    onUnhandledRequest: 'bypass', // Don't warn about unhandled requests
    serviceWorker: {
      url: '/mockServiceWorker.js',
    },
  })

  console.log('[MSW] Mock API enabled')
}

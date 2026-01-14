/**
 * Health endpoint handlers
 */

import { http, HttpResponse, delay } from 'msw'

const API_BASE = '/api/v1'

export const healthHandlers = [
  http.get(`${API_BASE}/health`, async () => {
    await delay(100)

    return HttpResponse.json({
      status: 'healthy',
      version: '1.0.1-demo',
      timestamp: new Date().toISOString(),
      mock: true,
    })
  }),
]

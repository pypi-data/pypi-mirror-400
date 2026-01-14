/**
 * Profile API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import { getStore, getById } from '../data/store'
import { createProfileResult } from '../factories'

const API_BASE = '/api/v1'

export const profileHandlers = [
  // Profile a source
  http.post(`${API_BASE}/sources/:sourceId/profile`, async ({ params }) => {
    await delay(1200) // Simulate profiling time

    const sourceId = params.sourceId as string
    const source = getById(getStore().sources, sourceId)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    const profile = createProfileResult({ sourceName: source.name })

    return HttpResponse.json({
      success: true,
      data: profile,
    })
  }),
]

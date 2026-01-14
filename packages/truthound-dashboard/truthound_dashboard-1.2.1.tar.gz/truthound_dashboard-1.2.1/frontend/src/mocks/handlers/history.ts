/**
 * History API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import { getStore, getById } from '../data/store'
import { createHistoryResponse } from '../factories'

const API_BASE = '/api/v1'

export const historyHandlers = [
  // Get validation history for a source
  http.get(`${API_BASE}/sources/:sourceId/history`, async ({ params, request }) => {
    await delay(300)

    const sourceId = params.sourceId as string
    const source = getById(getStore().sources, sourceId)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    const url = new URL(request.url)
    const period = (url.searchParams.get('period') ?? '30d') as '7d' | '30d' | '90d'
    const granularity = (url.searchParams.get('granularity') ?? 'daily') as
      | 'hourly'
      | 'daily'
      | 'weekly'

    const history = createHistoryResponse(period, granularity)

    return HttpResponse.json(history)
  }),
]

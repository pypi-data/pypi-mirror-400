/**
 * Validations API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import {
  getStore,
  getById,
  create,
  getValidationsBySourceId,
} from '../data/store'
import { createValidation, createId } from '../factories'

const API_BASE = '/api/v1'

export const validationsHandlers = [
  // Run validation for a source
  http.post(`${API_BASE}/validations/sources/:sourceId/validate`, async ({ params }) => {
    await delay(800) // Simulate validation time

    const sourceId = params.sourceId as string
    const source = getById(getStore().sources, sourceId)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    // Create new validation
    const validation = createValidation({
      id: createId(),
      sourceId,
    })

    create(getStore().validations, validation)

    // Update source's last_validated_at
    const sources = getStore().sources
    const existingSource = sources.get(sourceId)
    if (existingSource) {
      sources.set(sourceId, {
        ...existingSource,
        last_validated_at: new Date().toISOString(),
        latest_validation_status: validation.passed ? 'success' : 'failed',
      })
    }

    return HttpResponse.json({
      success: true,
      data: validation,
    })
  }),

  // Get validation by ID
  http.get(`${API_BASE}/validations/:id`, async ({ params }) => {
    await delay(150)

    const validation = getById(getStore().validations, params.id as string)

    if (!validation) {
      return HttpResponse.json(
        { detail: 'Validation not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: validation,
    })
  }),

  // List validations for a source
  http.get(`${API_BASE}/validations/sources/:sourceId/validations`, async ({ params, request }) => {
    await delay(200)

    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') ?? '20')
    const offset = parseInt(url.searchParams.get('offset') ?? '0')

    const sourceId = params.sourceId as string
    const allValidations = getValidationsBySourceId(sourceId)
    const total = allValidations.length
    const validations = allValidations.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: validations,
      total,  // Return total count of ALL validations, not just the sliced ones
      offset,
      limit,
    })
  }),
]

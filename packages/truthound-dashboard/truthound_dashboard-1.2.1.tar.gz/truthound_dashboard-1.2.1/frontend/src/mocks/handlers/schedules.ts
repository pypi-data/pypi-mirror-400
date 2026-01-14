/**
 * Schedules API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import {
  getStore,
  getAll,
  getById,
  create,
  update,
  remove,
} from '../data/store'
import { createSchedule, createValidation, createId } from '../factories'

const API_BASE = '/api/v1'

export const schedulesHandlers = [
  // List schedules
  http.get(`${API_BASE}/schedules`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const sourceId = url.searchParams.get('source_id')
    const activeOnly = url.searchParams.get('active_only') === 'true'
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const offset = parseInt(url.searchParams.get('offset') ?? '0')

    let schedules = getAll(getStore().schedules)

    if (sourceId) {
      schedules = schedules.filter((s) => s.source_id === sourceId)
    }

    if (activeOnly) {
      schedules = schedules.filter((s) => s.is_active)
    }

    // Sort by created_at desc
    schedules.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    const total = schedules.length
    const paginated = schedules.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: paginated,
      total,
      offset,
      limit,
    })
  }),

  // Get schedule by ID
  http.get(`${API_BASE}/schedules/:id`, async ({ params }) => {
    await delay(150)

    const schedule = getById(getStore().schedules, params.id as string)

    if (!schedule) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: schedule,
    })
  }),

  // Create schedule
  http.post(`${API_BASE}/schedules`, async ({ request }) => {
    await delay(300)

    let body: {
      source_id: string
      name: string
      cron_expression: string
      notify_on_failure?: boolean
      config?: Record<string, unknown>
    }

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    const source = getById(getStore().sources, body.source_id)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    // Validate cron expression format (basic validation: 5 or 6 space-separated parts)
    const cronParts = body.cron_expression.trim().split(/\s+/)
    if (cronParts.length < 5 || cronParts.length > 6) {
      return HttpResponse.json(
        { detail: 'Invalid cron expression. Must have 5 or 6 space-separated parts.' },
        { status: 400 }
      )
    }

    const schedule = createSchedule({
      id: createId(),
      sourceId: body.source_id,
    })

    schedule.name = body.name
    schedule.cron_expression = body.cron_expression
    schedule.notify_on_failure = body.notify_on_failure ?? false
    schedule.config = body.config
    schedule.source_name = source.name
    schedule.created_at = new Date().toISOString()

    create(getStore().schedules, schedule)

    return HttpResponse.json({
      success: true,
      data: schedule,
    })
  }),

  // Update schedule
  http.put(`${API_BASE}/schedules/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      cron_expression: string
      notify_on_failure: boolean
      config: Record<string, unknown>
    }>

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    const updated = update(getStore().schedules, params.id as string, body)

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: updated,
    })
  }),

  // Delete schedule
  http.delete(`${API_BASE}/schedules/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().schedules, params.id as string)

    if (!deleted) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      message: 'Schedule deleted successfully',
    })
  }),

  // Pause schedule
  http.post(`${API_BASE}/schedules/:id/pause`, async ({ params }) => {
    await delay(200)

    const updated = update(getStore().schedules, params.id as string, {
      is_active: false,
      next_run_at: undefined,
    })

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      message: 'Schedule paused',
      schedule: updated,
    })
  }),

  // Resume schedule
  http.post(`${API_BASE}/schedules/:id/resume`, async ({ params }) => {
    await delay(200)

    const nextRun = new Date()
    nextRun.setHours(nextRun.getHours() + 1)

    const updated = update(getStore().schedules, params.id as string, {
      is_active: true,
      next_run_at: nextRun.toISOString(),
    })

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      message: 'Schedule resumed',
      schedule: updated,
    })
  }),

  // Run schedule now
  http.post(`${API_BASE}/schedules/:id/run`, async ({ params }) => {
    await delay(800)

    const schedule = getById(getStore().schedules, params.id as string)

    if (!schedule) {
      return HttpResponse.json(
        { detail: 'Schedule not found' },
        { status: 404 }
      )
    }

    // Create a validation
    const validation = createValidation({
      id: createId(),
      sourceId: schedule.source_id,
    })

    create(getStore().validations, validation)

    // Update schedule's last_run_at
    update(getStore().schedules, params.id as string, {
      last_run_at: new Date().toISOString(),
    })

    return HttpResponse.json({
      success: true,
      message: 'Schedule executed successfully',
      validation_id: validation.id,
      passed: validation.passed,
    })
  }),
]

/**
 * Sources API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import {
  getStore,
  getAll,
  getById,
  create,
  update,
  remove,
  cleanupOrphanedData,
} from '../data/store'
import { createId } from '../factories'

const API_BASE = '/api/v1'

export const sourcesHandlers = [
  // List sources
  http.get(`${API_BASE}/sources`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const offset = parseInt(url.searchParams.get('offset') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const activeOnly = url.searchParams.get('active_only') === 'true'

    let sources = getAll(getStore().sources)

    if (activeOnly) {
      sources = sources.filter((s) => s.is_active)
    }

    // Sort by created_at desc
    sources.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    const total = sources.length
    const paginated = sources.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: paginated,
      total,
      offset,
      limit,
    })
  }),

  // Get source by ID
  http.get(`${API_BASE}/sources/:id`, async ({ params }) => {
    await delay(150)

    const source = getById(getStore().sources, params.id as string)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: source,
    })
  }),

  // Create source
  http.post(`${API_BASE}/sources`, async ({ request }) => {
    await delay(300)

    let body: {
      name: string
      type: string
      config: Record<string, unknown>
      description?: string
    }

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    const now = new Date().toISOString()

    // Create source with all provided data directly, not using factory defaults for user-provided fields
    const newSource = {
      id: createId(),
      name: body.name,
      type: body.type,
      config: body.config,
      description: body.description ?? '',
      is_active: true,
      has_schema: false,
      created_at: now,
      updated_at: now,
      last_validated_at: undefined,
      latest_validation_status: undefined,
    }

    create(getStore().sources, newSource)

    return HttpResponse.json({
      success: true,
      data: newSource,
    }, { status: 201 })
  }),

  // Update source
  http.put(`${API_BASE}/sources/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      config: Record<string, unknown>
      description: string
      is_active: boolean
    }>

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    const updated = update(getStore().sources, params.id as string, body)

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: updated,
    })
  }),

  // Delete source
  http.delete(`${API_BASE}/sources/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().sources, params.id as string)

    if (!deleted) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    // Clean up orphaned data (schedules, validations, schemas) referencing this source
    cleanupOrphanedData()

    return HttpResponse.json({ success: true, message: 'Source deleted successfully' })
  }),

  // Test source connection
  http.post(`${API_BASE}/sources/:id/test`, async ({ params }) => {
    await delay(500)

    const source = getById(getStore().sources, params.id as string)

    if (!source) {
      return HttpResponse.json(
        { detail: 'Source not found' },
        { status: 404 }
      )
    }

    // Simulate 90% success rate
    const success = Math.random() > 0.1

    return HttpResponse.json({
      success: true,
      data: {
        success,
        message: success ? 'Connection successful' : undefined,
        error: success ? undefined : 'Connection timeout after 30s',
      },
    })
  }),

  // Get supported source types
  // Backend SourceType: 'file' | 'postgresql' | 'mysql' | 'snowflake' | 'bigquery'
  http.get(`${API_BASE}/sources/types/supported`, async () => {
    await delay(100)

    return HttpResponse.json({
      success: true,
      data: [
        {
          type: 'file',
          name: 'File',
          description: 'Local file (CSV, Parquet, JSON, Excel)',
          required_fields: ['path'],
          optional_fields: ['format', 'delimiter', 'encoding', 'header', 'sheet'],
        },
        {
          type: 'postgresql',
          name: 'PostgreSQL',
          description: 'PostgreSQL database connection',
          required_fields: ['host', 'port', 'database', 'table'],
          optional_fields: ['schema', 'user', 'password'],
        },
        {
          type: 'mysql',
          name: 'MySQL',
          description: 'MySQL database connection',
          required_fields: ['host', 'port', 'database', 'table'],
          optional_fields: ['user', 'password'],
        },
        {
          type: 'snowflake',
          name: 'Snowflake',
          description: 'Snowflake data warehouse',
          required_fields: ['account', 'warehouse', 'database', 'schema', 'table'],
          optional_fields: ['user', 'password', 'role'],
        },
        {
          type: 'bigquery',
          name: 'BigQuery',
          description: 'Google BigQuery',
          required_fields: ['project', 'dataset', 'table'],
          optional_fields: ['location', 'credentials'],
        },
      ],
    })
  }),
]

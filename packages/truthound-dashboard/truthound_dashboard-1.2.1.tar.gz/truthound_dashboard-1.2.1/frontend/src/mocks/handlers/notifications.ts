/**
 * Notifications API handlers
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
import {
  createNotificationChannel,
  createNotificationRule,
  createNotificationStats,
  createId,
} from '../factories'

const API_BASE = '/api/v1'

export const notificationsHandlers = [
  // ============================================================================
  // Channels
  // ============================================================================

  // List channels
  http.get(`${API_BASE}/notifications/channels`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const offset = parseInt(url.searchParams.get('offset') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const activeOnly = url.searchParams.get('active_only') === 'true'
    const channelType = url.searchParams.get('channel_type')

    let channels = getAll(getStore().notificationChannels)

    if (activeOnly) {
      channels = channels.filter((c) => c.is_active)
    }

    if (channelType) {
      channels = channels.filter((c) => c.type === channelType)
    }

    const total = channels.length
    const paginated = channels.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: paginated,
      total,
      offset,
      limit,
    })
  }),

  // Get channel by ID
  http.get(`${API_BASE}/notifications/channels/:id`, async ({ params }) => {
    await delay(150)

    const channel = getById(getStore().notificationChannels, params.id as string)

    if (!channel) {
      return HttpResponse.json(
        { detail: 'Channel not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: channel,
    })
  }),

  // Create channel
  http.post(`${API_BASE}/notifications/channels`, async ({ request }) => {
    await delay(300)

    let body: {
      name: string
      type: string
      config: Record<string, unknown>
      is_active?: boolean
    }

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    // Validate channel type
    const validTypes = ['slack', 'email', 'webhook']
    if (!validTypes.includes(body.type)) {
      return HttpResponse.json(
        { detail: `Invalid channel type. Must be one of: ${validTypes.join(', ')}` },
        { status: 400 }
      )
    }

    const channel = createNotificationChannel({
      id: createId(),
      type: body.type as 'slack' | 'email' | 'webhook',
      isActive: body.is_active,
    })

    channel.name = body.name
    channel.created_at = new Date().toISOString()
    channel.updated_at = new Date().toISOString()

    create(getStore().notificationChannels, channel)

    return HttpResponse.json({
      success: true,
      data: channel,
    })
  }),

  // Update channel
  http.put(`${API_BASE}/notifications/channels/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      config: Record<string, unknown>
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

    const updated = update(
      getStore().notificationChannels,
      params.id as string,
      body
    )

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Channel not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: updated,
    })
  }),

  // Delete channel
  http.delete(`${API_BASE}/notifications/channels/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().notificationChannels, params.id as string)

    if (!deleted) {
      return HttpResponse.json(
        { detail: 'Channel not found' },
        { status: 404 }
      )
    }

    // Clean up rules and logs referencing this channel
    cleanupOrphanedData()

    return HttpResponse.json({ success: true })
  }),

  // Test channel
  http.post(`${API_BASE}/notifications/channels/:id/test`, async ({ params }) => {
    await delay(600)

    const channel = getById(getStore().notificationChannels, params.id as string)

    if (!channel) {
      return HttpResponse.json(
        { detail: 'Channel not found' },
        { status: 404 }
      )
    }

    // Simulate 85% success rate
    const success = Math.random() > 0.15

    return HttpResponse.json({
      success,
      message: success ? 'Test notification sent successfully' : undefined,
      error: success ? undefined : 'Connection failed: timeout after 10s',
    })
  }),

  // Get channel types
  http.get(`${API_BASE}/notifications/channels/types`, async () => {
    await delay(100)

    return HttpResponse.json({
      success: true,
      data: {
        slack: {
          name: 'Slack',
          required_fields: ['webhook_url'],
          optional_fields: ['channel', 'username', 'icon_emoji'],
        },
        email: {
          name: 'Email',
          required_fields: ['recipients'],
          optional_fields: ['smtp_host', 'smtp_port', 'from_address'],
        },
        webhook: {
          name: 'Webhook',
          required_fields: ['url'],
          optional_fields: ['method', 'headers', 'auth'],
        },
      },
    })
  }),

  // ============================================================================
  // Rules
  // ============================================================================

  // List rules
  http.get(`${API_BASE}/notifications/rules`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const offset = parseInt(url.searchParams.get('offset') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const activeOnly = url.searchParams.get('active_only') === 'true'
    const condition = url.searchParams.get('condition')

    let rules = getAll(getStore().notificationRules)

    if (activeOnly) {
      rules = rules.filter((r) => r.is_active)
    }

    if (condition) {
      rules = rules.filter((r) => r.condition === condition)
    }

    const total = rules.length
    const paginated = rules.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: paginated,
      total,
      offset,
      limit,
    })
  }),

  // Get rule by ID
  http.get(`${API_BASE}/notifications/rules/:id`, async ({ params }) => {
    await delay(150)

    const rule = getById(getStore().notificationRules, params.id as string)

    if (!rule) {
      return HttpResponse.json(
        { detail: 'Rule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: rule,
    })
  }),

  // Create rule
  http.post(`${API_BASE}/notifications/rules`, async ({ request }) => {
    await delay(300)

    let body: {
      name: string
      condition: string
      channel_ids: string[]
      condition_config?: Record<string, unknown>
      source_ids?: string[]
      is_active?: boolean
    }

    try {
      body = await request.json() as typeof body
    } catch {
      return HttpResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      )
    }

    // Validate that all channel_ids exist
    const channels = getStore().notificationChannels
    const invalidChannelIds = body.channel_ids.filter((id) => !channels.has(id))
    if (invalidChannelIds.length > 0) {
      return HttpResponse.json(
        { detail: `Invalid channel IDs: ${invalidChannelIds.join(', ')}` },
        { status: 400 }
      )
    }

    const rule = createNotificationRule({
      id: createId(),
      condition: body.condition,
      channelIds: body.channel_ids,
      isActive: body.is_active,
    })

    rule.name = body.name
    rule.condition_config = body.condition_config
    rule.source_ids = body.source_ids
    rule.created_at = new Date().toISOString()
    rule.updated_at = new Date().toISOString()

    create(getStore().notificationRules, rule)

    return HttpResponse.json({
      success: true,
      data: rule,
    })
  }),

  // Update rule
  http.put(`${API_BASE}/notifications/rules/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      condition: string
      channel_ids: string[]
      condition_config: Record<string, unknown>
      source_ids: string[]
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

    const updated = update(
      getStore().notificationRules,
      params.id as string,
      body
    )

    if (!updated) {
      return HttpResponse.json(
        { detail: 'Rule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: updated,
    })
  }),

  // Delete rule
  http.delete(`${API_BASE}/notifications/rules/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().notificationRules, params.id as string)

    if (!deleted) {
      return HttpResponse.json(
        { detail: 'Rule not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({ success: true })
  }),

  // Get rule conditions - all 9 conditions matching factory/notifications.ts
  http.get(`${API_BASE}/notifications/rules/conditions`, async () => {
    await delay(100)

    return HttpResponse.json({
      success: true,
      data: [
        'on_failure',
        'on_critical',
        'on_high',
        'on_drift',
        'on_success',
        'always',
        'on_warning',
        'on_error',
        'on_threshold',
      ],
    })
  }),

  // ============================================================================
  // Logs
  // ============================================================================

  // List logs
  http.get(`${API_BASE}/notifications/logs`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const offset = parseInt(url.searchParams.get('offset') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')
    const channelId = url.searchParams.get('channel_id')
    const status = url.searchParams.get('status')

    let logs = getAll(getStore().notificationLogs)

    if (channelId) {
      logs = logs.filter((l) => l.channel_id === channelId)
    }

    if (status) {
      logs = logs.filter((l) => l.status === status)
    }

    // Sort by created_at desc
    logs.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    const total = logs.length
    const paginated = logs.slice(offset, offset + limit)

    return HttpResponse.json({
      success: true,
      data: paginated,
      total,
      offset,
      limit,
    })
  }),

  // Get log by ID
  http.get(`${API_BASE}/notifications/logs/:id`, async ({ params }) => {
    await delay(150)

    const log = getById(getStore().notificationLogs, params.id as string)

    if (!log) {
      return HttpResponse.json(
        { detail: 'Log not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      success: true,
      data: {
        ...log,
        message: log.message_preview,
        event_data: {
          source_id: 'source-123',
          validation_id: 'validation-456',
        },
      },
    })
  }),

  // Get notification stats
  http.get(`${API_BASE}/notifications/logs/stats`, async ({ request }) => {
    await delay(150)

    const url = new URL(request.url)
    const hours = parseInt(url.searchParams.get('hours') ?? '24')

    const stats = createNotificationStats({ hours })

    return HttpResponse.json({
      success: true,
      data: stats,
    })
  }),
]

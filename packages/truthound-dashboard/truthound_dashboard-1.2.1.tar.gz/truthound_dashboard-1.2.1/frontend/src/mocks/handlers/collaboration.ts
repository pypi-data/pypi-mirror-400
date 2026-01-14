/**
 * Collaboration API handlers (Comments & Activities)
 */

import { http, HttpResponse, delay } from 'msw'
import type { Comment, Activity, ResourceType, ActivityAction } from '@/api/client'
import {
  getStore,
  getAll,
  getById,
  create,
  update,
  remove,
} from '../data/store'
import { createId } from '../factories'

const API_BASE = '/api/v1'

export const collaborationHandlers = [
  // ========== Comments ==========

  // List comments
  http.get(`${API_BASE}/comments`, async ({ request }) => {
    await delay(150)

    const url = new URL(request.url)
    const resourceType = url.searchParams.get('resource_type')
    const resourceId = url.searchParams.get('resource_id')

    if (!resourceType || !resourceId) {
      return HttpResponse.json(
        { detail: 'resource_type and resource_id are required' },
        { status: 400 }
      )
    }

    // Get top-level comments (no parent_id)
    const comments = getAll(getStore().comments)
      .filter(
        (c) =>
          c.resource_type === resourceType &&
          c.resource_id === resourceId &&
          !c.parent_id
      )
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    // Add replies to each comment
    const commentsWithReplies = comments.map((comment) => ({
      ...comment,
      replies: getAll(getStore().comments)
        .filter((c) => c.parent_id === comment.id)
        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()),
    }))

    return HttpResponse.json(commentsWithReplies)
  }),

  // Create comment
  http.post(`${API_BASE}/comments`, async ({ request }) => {
    await delay(200)

    let body: {
      resource_type: string
      resource_id: string
      content: string
      author_id?: string
      parent_id?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const now = new Date().toISOString()
    const newComment: Comment = {
      id: createId(),
      resource_type: body.resource_type as ResourceType,
      resource_id: body.resource_id,
      content: body.content,
      author_id: body.author_id ?? 'current_user',
      parent_id: body.parent_id,
      created_at: now,
      updated_at: now,
      replies: [],
    }

    create(getStore().comments, newComment)

    // Create activity for comment
    const activity: Activity = {
      id: createId(),
      resource_type: body.resource_type as ResourceType,
      resource_id: body.resource_id,
      action: 'commented' as ActivityAction,
      actor_id: newComment.author_id,
      description: `Commented on ${body.resource_type}`,
      metadata: { comment_id: newComment.id },
      created_at: now,
    }
    create(getStore().activities, activity)

    return HttpResponse.json(newComment, { status: 201 })
  }),

  // Update comment
  http.put(`${API_BASE}/comments/:id`, async ({ params, request }) => {
    await delay(150)

    let body: { content: string }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const updated = update(getStore().comments, params.id as string, {
      content: body.content,
    })

    if (!updated) {
      return HttpResponse.json({ detail: 'Comment not found' }, { status: 404 })
    }

    return HttpResponse.json({ ...updated, replies: [] })
  }),

  // Delete comment
  http.delete(`${API_BASE}/comments/:id`, async ({ params }) => {
    await delay(150)

    const comment = getById(getStore().comments, params.id as string)

    if (!comment) {
      return HttpResponse.json({ detail: 'Comment not found' }, { status: 404 })
    }

    // Delete replies first
    getAll(getStore().comments)
      .filter((c) => c.parent_id === params.id)
      .forEach((c) => remove(getStore().comments, c.id))

    remove(getStore().comments, params.id as string)

    return HttpResponse.json({ ok: true })
  }),

  // ========== Activities ==========

  // List activities
  http.get(`${API_BASE}/activities`, async ({ request }) => {
    await delay(150)

    const url = new URL(request.url)
    const resourceType = url.searchParams.get('resource_type')
    const resourceId = url.searchParams.get('resource_id')
    const skip = parseInt(url.searchParams.get('skip') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')

    let activities = getAll(getStore().activities)

    // Apply filters
    if (resourceType) {
      activities = activities.filter((a) => a.resource_type === resourceType)
    }
    if (resourceId) {
      activities = activities.filter((a) => a.resource_id === resourceId)
    }

    // Sort by created_at desc
    activities.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    // Paginate
    const paginated = activities.slice(skip, skip + limit)

    return HttpResponse.json(paginated)
  }),
]

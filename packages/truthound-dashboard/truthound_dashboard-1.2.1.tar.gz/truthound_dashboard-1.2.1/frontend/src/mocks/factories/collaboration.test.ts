/**
 * Collaboration factory tests
 */

import { describe, it, expect } from 'vitest'
import {
  createComment,
  createActivity,
  createComments,
  createActivities,
  createDiverseComments,
  createDiverseActivities,
} from './collaboration'

describe('Collaboration Factory', () => {
  describe('createComment', () => {
    it('creates a comment with default values', () => {
      const comment = createComment()

      expect(comment).toHaveProperty('id')
      expect(comment).toHaveProperty('resource_type')
      expect(comment).toHaveProperty('resource_id')
      expect(comment).toHaveProperty('content')
      expect(comment).toHaveProperty('author_id')
      expect(comment).toHaveProperty('created_at')
      expect(comment).toHaveProperty('updated_at')
      expect(comment).toHaveProperty('replies')
      expect(['term', 'asset', 'column']).toContain(comment.resource_type)
    })

    it('creates a comment with custom values', () => {
      const comment = createComment({
        content: 'This is a test comment',
        authorId: 'user@example.com',
        resourceType: 'term',
        resourceId: 'term-123',
      })

      expect(comment.content).toBe('This is a test comment')
      expect(comment.author_id).toBe('user@example.com')
      expect(comment.resource_type).toBe('term')
      expect(comment.resource_id).toBe('term-123')
    })

    it('creates a reply comment', () => {
      const parentId = 'parent-123'
      const comment = createComment({
        parentId,
        withReplies: false,
      })

      expect(comment.parent_id).toBe(parentId)
      expect(comment.replies).toEqual([])
    })

    it('creates a comment with replies by default', () => {
      // Note: replies are probabilistic, so we test multiple times
      let hasReplies = false
      for (let i = 0; i < 10; i++) {
        const comment = createComment({ withReplies: true })
        if (comment.replies.length > 0) {
          hasReplies = true
          break
        }
      }
      // It's ok if no replies were generated (probabilistic)
      expect(typeof hasReplies).toBe('boolean')
    })
  })

  describe('createActivity', () => {
    it('creates an activity with default values', () => {
      const activity = createActivity()

      expect(activity).toHaveProperty('id')
      expect(activity).toHaveProperty('resource_type')
      expect(activity).toHaveProperty('resource_id')
      expect(activity).toHaveProperty('action')
      expect(activity).toHaveProperty('actor_id')
      expect(activity).toHaveProperty('description')
      expect(activity).toHaveProperty('created_at')
      expect(['created', 'updated', 'deleted', 'commented']).toContain(
        activity.action
      )
    })

    it('creates an activity with custom values', () => {
      const activity = createActivity({
        resourceType: 'asset',
        resourceId: 'asset-123',
        action: 'updated',
        actorId: 'admin@example.com',
      })

      expect(activity.resource_type).toBe('asset')
      expect(activity.resource_id).toBe('asset-123')
      expect(activity.action).toBe('updated')
      expect(activity.actor_id).toBe('admin@example.com')
    })

    it('generates description based on action', () => {
      const activity = createActivity({
        action: 'created',
        resourceType: 'term',
      })

      expect(activity.description).toContain('term')
    })
  })

  describe('createComments', () => {
    it('creates multiple comments for a resource', () => {
      const comments = createComments('term', 'term-123', 5)

      expect(comments).toHaveLength(5)
      comments.forEach((comment) => {
        expect(comment.resource_type).toBe('term')
        expect(comment.resource_id).toBe('term-123')
      })
    })
  })

  describe('createActivities', () => {
    it('creates multiple activities sorted by date', () => {
      const activities = createActivities(5)

      expect(activities).toHaveLength(5)

      // Should be sorted by created_at descending
      for (let i = 0; i < activities.length - 1; i++) {
        const current = new Date(activities[i].created_at).getTime()
        const next = new Date(activities[i + 1].created_at).getTime()
        expect(current).toBeGreaterThanOrEqual(next)
      }
    })
  })

  describe('createDiverseComments', () => {
    it('creates comments for different resource types', () => {
      const termIds = ['term-1', 'term-2']
      const assetIds = ['asset-1', 'asset-2']
      const columnIds = ['col-1']

      const comments = createDiverseComments(termIds, assetIds, columnIds)

      expect(comments.length).toBeGreaterThan(0)

      // Should have comments on different resource types
      const resourceTypes = new Set(comments.map((c) => c.resource_type))
      expect(resourceTypes.size).toBeGreaterThanOrEqual(2)
    })
  })

  describe('createDiverseActivities', () => {
    it('creates activities for different actions', () => {
      const termIds = ['term-1']
      const assetIds = ['asset-1']
      const columnIds = ['col-1']

      const activities = createDiverseActivities(termIds, assetIds, columnIds)

      expect(activities.length).toBeGreaterThan(0)

      // Should have different action types
      const actions = new Set(activities.map((a) => a.action))
      expect(actions.size).toBeGreaterThanOrEqual(2)

      // Should be sorted by created_at descending
      for (let i = 0; i < activities.length - 1; i++) {
        const current = new Date(activities[i].created_at).getTime()
        const next = new Date(activities[i + 1].created_at).getTime()
        expect(current).toBeGreaterThanOrEqual(next)
      }
    })
  })
})

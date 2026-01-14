/**
 * Collaboration factory - generates comments and activity mock data
 */

import type {
  Comment,
  Activity,
  ResourceType,
  ActivityAction,
} from '@/api/client'
import {
  createId,
  createRecentTimestamp,
  randomChoice,
  randomInt,
  faker,
} from './base'

// ============================================================================
// Constants
// ============================================================================

const RESOURCE_TYPES: ResourceType[] = ['term', 'asset', 'column']
const ACTIVITY_ACTIONS: ActivityAction[] = ['created', 'updated', 'deleted', 'commented']

const COMMENT_TEMPLATES = [
  'This definition needs to be reviewed.',
  'Can we add more context here?',
  'Great work on this documentation!',
  'I suggest we update this to reflect the latest changes.',
  'This term is used differently in our department.',
  'We should deprecate this soon.',
  'Approved for production use.',
  'Please add examples for clarity.',
  'This needs alignment with the data governance team.',
  'The business owner should validate this.',
  'Consider adding related terms.',
  'The sensitivity level should be updated.',
  'This mapping looks correct.',
  'We use this column for reporting.',
]

const ACTIVITY_DESCRIPTIONS: Record<ActivityAction, string[]> = {
  created: [
    'Created new {resource}',
    'Added {resource}',
    'Initialized {resource}',
  ],
  updated: [
    'Updated {resource}',
    'Modified {resource}',
    'Changed {resource}',
  ],
  deleted: [
    'Deleted {resource}',
    'Removed {resource}',
  ],
  commented: [
    'Commented on {resource}',
    'Added a comment to {resource}',
  ],
}

// ============================================================================
// Comments
// ============================================================================

export interface CommentFactoryOptions {
  id?: string
  resourceType?: ResourceType
  resourceId?: string
  content?: string
  authorId?: string
  parentId?: string
  withReplies?: boolean
}

export function createComment(options: CommentFactoryOptions = {}): Comment {
  const id = options.id ?? createId()
  const createdAt = createRecentTimestamp()

  const replies: Comment[] =
    options.withReplies !== false && !options.parentId && faker.datatype.boolean(0.3)
      ? Array.from({ length: randomInt(1, 2) }, () =>
          createComment({
            resourceType: options.resourceType,
            resourceId: options.resourceId,
            parentId: id,
            withReplies: false,
          })
        )
      : []

  return {
    id,
    resource_type: options.resourceType ?? randomChoice(RESOURCE_TYPES),
    resource_id: options.resourceId ?? createId(),
    content: options.content ?? randomChoice(COMMENT_TEMPLATES),
    author_id: options.authorId ?? faker.person.fullName(),
    parent_id: options.parentId,
    created_at: createdAt,
    updated_at: createdAt,
    replies,
  }
}

export function createComments(
  resourceType: ResourceType,
  resourceId: string,
  count: number
): Comment[] {
  return Array.from({ length: count }, () =>
    createComment({ resourceType, resourceId })
  )
}

// ============================================================================
// Activities
// ============================================================================

export interface ActivityFactoryOptions {
  id?: string
  resourceType?: string
  resourceId?: string
  action?: ActivityAction
  actorId?: string
  description?: string
  metadata?: Record<string, unknown>
}

export function createActivity(options: ActivityFactoryOptions = {}): Activity {
  const resourceType = options.resourceType ?? randomChoice(RESOURCE_TYPES)
  const action = options.action ?? randomChoice(ACTIVITY_ACTIONS)
  const descTemplates = ACTIVITY_DESCRIPTIONS[action]
  const description =
    options.description ??
    randomChoice(descTemplates).replace('{resource}', resourceType)

  return {
    id: options.id ?? createId(),
    resource_type: resourceType,
    resource_id: options.resourceId ?? createId(),
    action,
    actor_id: options.actorId ?? faker.person.fullName(),
    description,
    metadata: options.metadata ?? (faker.datatype.boolean(0.3) ? { field: faker.lorem.word() } : undefined),
    created_at: createRecentTimestamp(),
  }
}

export function createActivities(count: number): Activity[] {
  return Array.from({ length: count }, () => createActivity())
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
}

// ============================================================================
// Diverse Data Sets
// ============================================================================

export function createDiverseComments(
  termIds: string[],
  assetIds: string[],
  columnIds: string[]
): Comment[] {
  const comments: Comment[] = []

  // Comments on terms
  termIds.slice(0, 3).forEach((termId) => {
    const count = randomInt(1, 3)
    for (let i = 0; i < count; i++) {
      comments.push(createComment({ resourceType: 'term', resourceId: termId }))
    }
  })

  // Comments on assets
  assetIds.slice(0, 3).forEach((assetId) => {
    const count = randomInt(1, 2)
    for (let i = 0; i < count; i++) {
      comments.push(createComment({ resourceType: 'asset', resourceId: assetId }))
    }
  })

  // Comments on columns
  columnIds.slice(0, 2).forEach((columnId) => {
    comments.push(createComment({ resourceType: 'column', resourceId: columnId }))
  })

  return comments
}

export function createDiverseActivities(
  termIds: string[],
  assetIds: string[],
  columnIds: string[]
): Activity[] {
  const activities: Activity[] = []

  // Activities for each action type
  ACTIVITY_ACTIONS.forEach((action) => {
    activities.push(
      createActivity({
        action,
        resourceType: randomChoice(RESOURCE_TYPES),
        resourceId: randomChoice([...termIds, ...assetIds, ...columnIds]),
      })
    )
  })

  // Activities for terms
  termIds.slice(0, 4).forEach((termId) => {
    activities.push(
      createActivity({
        resourceType: 'term',
        resourceId: termId,
      })
    )
  })

  // Activities for assets
  assetIds.slice(0, 4).forEach((assetId) => {
    activities.push(
      createActivity({
        resourceType: 'asset',
        resourceId: assetId,
      })
    )
  })

  // Add more random activities
  for (let i = 0; i < 15; i++) {
    activities.push(createActivity())
  }

  return activities.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

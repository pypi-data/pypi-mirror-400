/**
 * In-memory data store for mock API
 * Provides CRUD operations with persistence during session
 * Extended for comprehensive test coverage
 */

import type {
  Source,
  Validation,
  Schema,
  Schedule,
  DriftComparison,
  NotificationChannel,
  NotificationRule,
  NotificationLog,
  GlossaryTerm,
  GlossaryCategory,
  TermRelationship,
  TermHistory,
  CatalogAsset,
  AssetColumn,
  AssetTag,
  Comment,
  Activity,
} from '@/api/client'
import {
  createDiverseSources,
  createDiverseValidations,
  createSchema,
  createDiverseSchedules,
  createDiverseDriftComparisons,
  createDiverseChannels,
  createDiverseRules,
  createDiverseLogs,
  setAvailableChannelIds,
  createDiverseCategories,
  createDiverseTerms,
  createTermsWithRelationships,
  createTermHistories,
  createDiverseAssets,
  createDiverseComments,
  createDiverseActivities,
} from '../factories'

// ============================================================================
// Store State
// ============================================================================

interface MockStore {
  sources: Map<string, Source>
  validations: Map<string, Validation>
  schemas: Map<string, Schema> // keyed by source_id
  schedules: Map<string, Schedule>
  driftComparisons: Map<string, DriftComparison>
  notificationChannels: Map<string, NotificationChannel>
  notificationRules: Map<string, NotificationRule>
  notificationLogs: Map<string, NotificationLog>
  // Phase 5: Business Glossary & Data Catalog
  glossaryTerms: Map<string, GlossaryTerm>
  glossaryCategories: Map<string, GlossaryCategory>
  termRelationships: Map<string, TermRelationship>
  termHistory: Map<string, TermHistory>
  catalogAssets: Map<string, CatalogAsset>
  assetColumns: Map<string, AssetColumn>
  assetTags: Map<string, AssetTag>
  comments: Map<string, Comment>
  activities: Map<string, Activity>
}

let store: MockStore | null = null

// ============================================================================
// Initialize Store
// ============================================================================

function initializeStore(): MockStore {
  // Create diverse sources covering all test scenarios
  const sources = createDiverseSources()
  const sourcesMap = new Map(sources.map((s) => [s.id, s]))

  // Create diverse validations for each source
  const validations: Validation[] = []
  sources.forEach((source) => {
    const sourceValidations = createDiverseValidations(source.id)
    validations.push(...sourceValidations)
  })
  const validationsMap = new Map(validations.map((v) => [v.id, v]))

  // Create schemas for sources with has_schema = true
  const schemasMap = new Map<string, Schema>()
  sources.filter((s) => s.has_schema).forEach((source) => {
    const schema = createSchema({ sourceId: source.id })
    schemasMap.set(source.id, schema)
  })

  // Create diverse schedules linked to sources
  const schedules = createDiverseSchedules(sources.map((s) => ({ id: s.id, name: s.name })))
  const schedulesMap = new Map(schedules.map((s) => [s.id, s]))

  // Create diverse drift comparisons with real source references
  const sourceIds = sources.map((s) => s.id)
  const driftComparisons = createDiverseDriftComparisons(sourceIds, sourceIds)
  const driftComparisonsMap = new Map(driftComparisons.map((d) => [d.id, d]))

  // Create diverse notification channels
  const channels = createDiverseChannels()
  const channelsMap = new Map(channels.map((c) => [c.id, c]))

  // Set available channel IDs for rule creation (ensures rules reference existing channels)
  const channelIds = channels.map((c) => c.id)
  setAvailableChannelIds(channelIds)

  // Create diverse notification rules linked to channels
  const rules = createDiverseRules(channelIds, sourceIds)
  const rulesMap = new Map(rules.map((r) => [r.id, r]))

  // Create diverse notification logs
  const ruleIds = rules.map((r) => r.id)
  const logs = createDiverseLogs(channelIds, ruleIds)
  const logsMap = new Map(logs.map((l) => [l.id, l]))

  // ========== Phase 5: Business Glossary ==========
  const categories = createDiverseCategories()
  const categoriesMap = new Map(categories.map((c) => [c.id, c]))

  const termsWithoutRelations = createDiverseTerms(categories)
  const { terms, relationships } = createTermsWithRelationships(termsWithoutRelations)
  const termsMap = new Map(terms.map((t) => [t.id, t]))
  const relationshipsMap = new Map(relationships.map((r) => [r.id, r]))

  // Create history for some terms
  const historyItems: TermHistory[] = []
  terms.slice(0, 5).forEach((term) => {
    historyItems.push(...createTermHistories(term.id, 2))
  })
  const historyMap = new Map(historyItems.map((h) => [h.id, h]))

  // ========== Phase 5: Data Catalog ==========
  const assets = createDiverseAssets(sourceIds)
  const assetsMap = new Map(assets.map((a) => [a.id, a]))

  // Extract columns and tags from assets
  const columnsMap = new Map<string, AssetColumn>()
  const tagsMap = new Map<string, AssetTag>()
  assets.forEach((asset) => {
    asset.columns.forEach((col) => columnsMap.set(col.id, col))
    asset.tags.forEach((tag) => tagsMap.set(tag.id, tag))
  })

  // ========== Phase 5: Collaboration ==========
  const termIds = terms.map((t) => t.id)
  const assetIds = assets.map((a) => a.id)
  const columnIds = Array.from(columnsMap.keys())

  const comments = createDiverseComments(termIds, assetIds, columnIds)
  const commentsMap = new Map(comments.map((c) => [c.id, c]))

  const activities = createDiverseActivities(termIds, assetIds, columnIds)
  const activitiesMap = new Map(activities.map((a) => [a.id, a]))

  return {
    sources: sourcesMap,
    validations: validationsMap,
    schemas: schemasMap,
    schedules: schedulesMap,
    driftComparisons: driftComparisonsMap,
    notificationChannels: channelsMap,
    notificationRules: rulesMap,
    notificationLogs: logsMap,
    // Phase 5
    glossaryTerms: termsMap,
    glossaryCategories: categoriesMap,
    termRelationships: relationshipsMap,
    termHistory: historyMap,
    catalogAssets: assetsMap,
    assetColumns: columnsMap,
    assetTags: tagsMap,
    comments: commentsMap,
    activities: activitiesMap,
  }
}

// ============================================================================
// Store Access
// ============================================================================

export function getStore(): MockStore {
  if (!store) {
    store = initializeStore()
  }
  return store
}

export function resetStore(): void {
  // Clear reference before reinitializing
  store = null
  store = initializeStore()
}

// ============================================================================
// Data Integrity Helpers
// ============================================================================

/**
 * Validate that a notification rule references existing channels
 */
export function validateRuleChannels(rule: NotificationRule): boolean {
  const channels = getStore().notificationChannels
  return rule.channel_ids.every((id) => channels.has(id))
}

/**
 * Validate that a notification log references existing channel
 */
export function validateLogChannel(log: NotificationLog): boolean {
  return getStore().notificationChannels.has(log.channel_id)
}

/**
 * Validate that a schedule references an existing source
 */
export function validateScheduleSource(schedule: Schedule): boolean {
  return getStore().sources.has(schedule.source_id)
}

/**
 * Clean up orphaned data (schedules/validations referencing deleted sources)
 */
export function cleanupOrphanedData(): void {
  const store = getStore()
  const sourceIds = new Set(store.sources.keys())

  // Remove schedules referencing non-existent sources
  for (const [id, schedule] of store.schedules) {
    if (!sourceIds.has(schedule.source_id)) {
      store.schedules.delete(id)
    }
  }

  // Remove validations referencing non-existent sources
  for (const [id, validation] of store.validations) {
    if (!sourceIds.has(validation.source_id)) {
      store.validations.delete(id)
    }
  }

  // Remove schemas for non-existent sources
  for (const sourceId of store.schemas.keys()) {
    if (!sourceIds.has(sourceId)) {
      store.schemas.delete(sourceId)
    }
  }

  // Clean up notification rules referencing non-existent channels
  const channelIds = new Set(store.notificationChannels.keys())
  for (const [id, rule] of store.notificationRules) {
    rule.channel_ids = rule.channel_ids.filter((cid) => channelIds.has(cid))
    if (rule.channel_ids.length === 0) {
      store.notificationRules.delete(id)
    }
  }

  // Clean up notification logs referencing non-existent channels
  for (const [id, log] of store.notificationLogs) {
    if (!channelIds.has(log.channel_id)) {
      store.notificationLogs.delete(id)
    }
  }
}

// ============================================================================
// Generic CRUD Helpers
// ============================================================================

export function getAll<T>(map: Map<string, T>): T[] {
  return Array.from(map.values())
}

export function getById<T>(map: Map<string, T>, id: string): T | undefined {
  return map.get(id)
}

export function create<T extends { id: string }>(map: Map<string, T>, item: T): T {
  map.set(item.id, item)
  return item
}

export function update<T extends { id: string }>(
  map: Map<string, T>,
  id: string,
  updates: Partial<T>
): T | undefined {
  const existing = map.get(id)
  if (!existing) return undefined

  const updated = { ...existing, ...updates, updated_at: new Date().toISOString() }
  map.set(id, updated)
  return updated
}

export function remove<T>(map: Map<string, T>, id: string): boolean {
  return map.delete(id)
}

// ============================================================================
// Specific Query Helpers
// ============================================================================

export function getValidationsBySourceId(sourceId: string): Validation[] {
  return getAll(getStore().validations)
    .filter((v) => v.source_id === sourceId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
}

export function getSchemaBySourceId(sourceId: string): Schema | undefined {
  return getStore().schemas.get(sourceId)
}

export function getSchedulesBySourceId(sourceId: string): Schedule[] {
  return getAll(getStore().schedules).filter((s) => s.source_id === sourceId)
}

export function getLogsByChannelId(channelId: string): NotificationLog[] {
  return getAll(getStore().notificationLogs)
    .filter((l) => l.channel_id === channelId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
}

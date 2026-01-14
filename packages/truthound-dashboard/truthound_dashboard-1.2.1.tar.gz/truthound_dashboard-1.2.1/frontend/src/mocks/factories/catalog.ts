/**
 * Catalog factory - generates realistic data catalog mock data
 */

import type {
  CatalogAsset,
  AssetListItem,
  AssetColumn,
  AssetTag,
  AssetType,
  SensitivityLevel,
  GlossaryTermSummary,
} from '@/api/client'
import {
  createId,
  createTimestamp,
  createRecentTimestamp,
  randomChoice,
  randomInt,
  faker,
} from './base'

// ============================================================================
// Constants
// ============================================================================

const ASSET_TYPES: AssetType[] = ['table', 'file', 'api']

const SENSITIVITY_LEVELS: SensitivityLevel[] = [
  'public',
  'internal',
  'confidential',
  'restricted',
]

const DATA_TYPES = [
  'string',
  'integer',
  'bigint',
  'float',
  'double',
  'decimal',
  'boolean',
  'date',
  'timestamp',
  'json',
  'array',
  'uuid',
]

const ASSET_NAMES = [
  'customers',
  'orders',
  'products',
  'transactions',
  'users',
  'events',
  'sessions',
  'payments',
  'invoices',
  'subscriptions',
  'logs',
  'metrics',
  'reports',
  'analytics',
  'inventory',
]

const COLUMN_NAMES: Record<string, string[]> = {
  customers: ['id', 'email', 'name', 'phone', 'address', 'created_at', 'status'],
  orders: ['id', 'customer_id', 'total', 'status', 'created_at', 'shipped_at'],
  products: ['id', 'name', 'sku', 'price', 'category', 'stock', 'description'],
  transactions: ['id', 'amount', 'currency', 'type', 'status', 'timestamp'],
  users: ['id', 'username', 'email', 'role', 'last_login', 'is_active'],
  events: ['id', 'event_type', 'user_id', 'properties', 'timestamp'],
  sessions: ['id', 'user_id', 'device', 'ip_address', 'started_at', 'ended_at'],
  payments: ['id', 'order_id', 'method', 'amount', 'status', 'processed_at'],
  invoices: ['id', 'customer_id', 'amount', 'due_date', 'paid_at', 'status'],
  subscriptions: ['id', 'user_id', 'plan', 'start_date', 'end_date', 'status'],
  logs: ['id', 'level', 'message', 'context', 'timestamp'],
  metrics: ['id', 'name', 'value', 'tags', 'timestamp'],
  reports: ['id', 'name', 'type', 'data', 'generated_at'],
  analytics: ['id', 'metric', 'dimension', 'value', 'date'],
  inventory: ['id', 'product_id', 'warehouse', 'quantity', 'last_updated'],
}

const TAG_NAMES = [
  'pii',
  'financial',
  'sensitive',
  'public',
  'archived',
  'deprecated',
  'critical',
  'reporting',
  'analytics',
  'compliance',
]

// ============================================================================
// Tags
// ============================================================================

export interface TagFactoryOptions {
  id?: string
  assetId?: string
  tagName?: string
  tagValue?: string
}

export function createAssetTag(options: TagFactoryOptions = {}): AssetTag {
  return {
    id: options.id ?? createId(),
    asset_id: options.assetId ?? createId(),
    tag_name: options.tagName ?? randomChoice(TAG_NAMES),
    tag_value: options.tagValue ?? (faker.datatype.boolean(0.5) ? faker.lorem.word() : undefined),
    created_at: createRecentTimestamp(),
  }
}

// ============================================================================
// Columns
// ============================================================================

export interface ColumnFactoryOptions {
  id?: string
  assetId?: string
  name?: string
  dataType?: string
  description?: string
  isNullable?: boolean
  isPrimaryKey?: boolean
  termId?: string
  sensitivityLevel?: SensitivityLevel
  term?: GlossaryTermSummary
}

export function createAssetColumn(options: ColumnFactoryOptions = {}): AssetColumn {
  const name = options.name ?? faker.database.column()
  const isPrimaryKey = options.isPrimaryKey ?? (name === 'id')

  return {
    id: options.id ?? createId(),
    asset_id: options.assetId ?? createId(),
    name,
    data_type: options.dataType ?? randomChoice(DATA_TYPES),
    description: options.description ?? faker.lorem.sentence(),
    is_nullable: options.isNullable ?? !isPrimaryKey,
    is_primary_key: isPrimaryKey,
    term_id: options.termId,
    sensitivity_level: options.sensitivityLevel ?? randomChoice([...SENSITIVITY_LEVELS, undefined]),
    created_at: createRecentTimestamp(),
    term: options.term,
  }
}

export function createAssetColumns(assetId: string, assetName: string): AssetColumn[] {
  const baseName = assetName.toLowerCase().replace(/[^a-z]/g, '')
  const columnNames = COLUMN_NAMES[baseName] ?? ['id', 'name', 'created_at', 'updated_at']

  return columnNames.map((name) =>
    createAssetColumn({
      assetId,
      name,
      isPrimaryKey: name === 'id',
      dataType:
        name.includes('id')
          ? 'uuid'
          : name.includes('_at')
          ? 'timestamp'
          : name.includes('amount') || name.includes('price') || name.includes('total')
          ? 'decimal'
          : name.includes('is_') || name.includes('has_')
          ? 'boolean'
          : 'string',
    })
  )
}

// ============================================================================
// Assets
// ============================================================================

export interface AssetFactoryOptions {
  id?: string
  name?: string
  assetType?: AssetType
  sourceId?: string
  sourceName?: string
  description?: string
  ownerId?: string
  qualityScore?: number
  withColumns?: boolean
  withTags?: boolean
}

export function createCatalogAsset(options: AssetFactoryOptions = {}): CatalogAsset {
  const id = options.id ?? createId()
  const name = options.name ?? randomChoice(ASSET_NAMES) + `_${faker.string.alphanumeric(4)}`
  const assetType = options.assetType ?? randomChoice(ASSET_TYPES)

  const columns = options.withColumns !== false ? createAssetColumns(id, name) : []
  const tags =
    options.withTags !== false
      ? Array.from({ length: randomInt(0, 3) }, () => createAssetTag({ assetId: id }))
      : []

  return {
    id,
    name,
    asset_type: assetType,
    source_id: options.sourceId,
    description: options.description ?? faker.lorem.sentences(1),
    owner_id: options.ownerId ?? faker.person.fullName(),
    quality_score: options.qualityScore ?? faker.number.float({ min: 50, max: 100, fractionDigits: 1 }),
    created_at: createTimestamp(faker.number.int({ min: 7, max: 180 })),
    updated_at: createRecentTimestamp(),
    source: options.sourceId
      ? {
          id: options.sourceId,
          name: options.sourceName ?? faker.lorem.words(2),
          type: randomChoice(['file', 'postgresql', 'mysql']),
        }
      : undefined,
    columns,
    tags,
  }
}

export function createAssetListItem(asset: CatalogAsset): AssetListItem {
  return {
    id: asset.id,
    name: asset.name,
    asset_type: asset.asset_type,
    source_id: asset.source_id,
    source_name: asset.source?.name,
    quality_score: asset.quality_score,
    tag_count: asset.tags.length,
    column_count: asset.columns.length,
    updated_at: asset.updated_at,
  }
}

export function createCatalogAssets(count: number): CatalogAsset[] {
  return Array.from({ length: count }, () => createCatalogAsset())
}

// ============================================================================
// Diverse Data Sets
// ============================================================================

export function createDiverseAssets(sourceIds: string[]): CatalogAsset[] {
  const assets: CatalogAsset[] = []

  // Create one asset for each type
  ASSET_TYPES.forEach((assetType) => {
    assets.push(
      createCatalogAsset({
        assetType,
        sourceId: sourceIds.length > 0 ? randomChoice(sourceIds) : undefined,
      })
    )
  })

  // Create assets with varying quality scores
  const scores = [95, 80, 65, 45]
  scores.forEach((score) => {
    assets.push(
      createCatalogAsset({
        qualityScore: score,
        sourceId: sourceIds.length > 0 ? randomChoice(sourceIds) : undefined,
      })
    )
  })

  // Create assets linked to specific sources
  sourceIds.slice(0, 3).forEach((sourceId) => {
    assets.push(createCatalogAsset({ sourceId }))
  })

  // Add more random assets
  for (let i = 0; i < 8; i++) {
    assets.push(
      createCatalogAsset({
        sourceId: faker.datatype.boolean(0.6) && sourceIds.length > 0
          ? randomChoice(sourceIds)
          : undefined,
      })
    )
  }

  return assets
}

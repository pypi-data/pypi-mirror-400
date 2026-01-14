/**
 * Source factory - generates realistic data source mock data
 * Extended for comprehensive test coverage
 */

import type { Source } from '@/api/client'
import {
  createId,
  createTimestamp,
  createRecentTimestamp,
  randomChoice,
  faker,
} from './base'

export interface SourceFactoryOptions {
  id?: string
  name?: string
  type?: string
  isActive?: boolean
  hasSchema?: boolean
  validated?: boolean
  // Backend uses: 'success' | 'failed' | 'error' | 'pending' | 'running' | null
  // For latest_validation_status, typically completed validations: 'success' | 'failed' | null
  validationStatus?: 'success' | 'failed' | null
}

// Backend SourceType: 'file' | 'postgresql' | 'mysql' | 'snowflake' | 'bigquery'
const SOURCE_TYPES = ['file', 'postgresql', 'mysql', 'snowflake', 'bigquery'] as const

const SOURCE_CONFIGS: Record<string, () => Record<string, unknown>> = {
  file: () => ({
    path: faker.system.filePath().replace(/\.[^.]+$/, randomChoice(['.csv', '.parquet', '.json', '.xlsx'])),
    format: randomChoice(['csv', 'parquet', 'json', 'excel']),
    delimiter: randomChoice([',', ';', '\t', '|']),
    encoding: randomChoice(['utf-8', 'utf-16', 'iso-8859-1']),
    has_header: faker.datatype.boolean(0.9),
  }),
  postgresql: () => ({
    host: randomChoice(['localhost', 'db.example.com', 'postgres.internal']),
    port: 5432,
    database: faker.database.column(),
    table: faker.database.column(),
    schema: randomChoice(['public', 'analytics', 'raw', 'staging']),
  }),
  mysql: () => ({
    host: randomChoice(['localhost', 'mysql.example.com', 'db.internal']),
    port: 3306,
    database: faker.database.column(),
    table: faker.database.column(),
  }),
  snowflake: () => ({
    account: faker.string.alphanumeric(8),
    warehouse: randomChoice(['COMPUTE_WH', 'ANALYTICS_WH', 'ETL_WH']),
    database: faker.database.column().toUpperCase(),
    schema: randomChoice(['PUBLIC', 'RAW', 'ANALYTICS']),
    table: faker.database.column().toUpperCase(),
  }),
  bigquery: () => ({
    project: faker.string.alphanumeric(12),
    dataset: faker.database.column(),
    table: faker.database.column(),
    location: randomChoice(['US', 'EU', 'asia-northeast1']),
  }),
}

// More diverse source names covering various domains
const SOURCE_NAMES = [
  // Business/Finance
  'Sales Transactions',
  'Financial Reports',
  'Revenue Analytics',
  'Budget Forecasts',
  'Invoice Records',
  // Customer
  'Customer Master Data',
  'User Analytics',
  'Customer Segments',
  'Churn Analysis',
  'Customer Feedback',
  // Product/Inventory
  'Product Inventory',
  'Product Catalog',
  'Stock Levels',
  'Warehouse Data',
  // Operations
  'Order History',
  'Shipping Logs',
  'Delivery Tracking',
  'Supply Chain',
  // HR
  'Employee Records',
  'Payroll Data',
  'Performance Reviews',
  // Marketing
  'Marketing Campaigns',
  'Ad Performance',
  'Lead Generation',
  'Email Analytics',
  // Technical
  'Server Logs',
  'API Metrics',
  'Error Logs',
  'System Health',
  // External
  'Supplier Data',
  'Partner API',
  'Market Data',
  'Weather Feed',
]

export function createSource(options: SourceFactoryOptions = {}): Source {
  const type = options.type ?? randomChoice([...SOURCE_TYPES])
  const configGenerator = SOURCE_CONFIGS[type] ?? SOURCE_CONFIGS.file

  const createdAt = createTimestamp(faker.number.int({ min: 7, max: 180 }))
  const validated = options.validated ?? faker.datatype.boolean(0.7)

  // Handle validationStatus: null means "explicitly no status", undefined means "generate randomly"
  let validationStatus: 'success' | 'failed' | undefined
  if (options.validationStatus === null) {
    // Explicitly set to null - means no validation status (never validated)
    validationStatus = undefined
  } else if (options.validationStatus !== undefined) {
    // Explicitly set to a status value
    validationStatus = options.validationStatus
  } else if (validated) {
    // No explicit value - generate randomly for validated sources
    // Weight towards success (70% success, 30% failed)
    validationStatus = faker.datatype.boolean(0.7) ? 'success' : 'failed'
  }
  // If not validated and no explicit status, validationStatus remains undefined

  return {
    id: options.id ?? createId(),
    name: options.name ?? randomChoice(SOURCE_NAMES) + ` (${faker.string.alphanumeric(4)})`,
    type,
    config: configGenerator(),
    description: faker.lorem.sentences({ min: 1, max: 3 }),
    is_active: options.isActive ?? faker.datatype.boolean(0.85),
    created_at: createdAt,
    updated_at: createRecentTimestamp(),
    last_validated_at: validated ? createRecentTimestamp() : undefined,
    has_schema: options.hasSchema ?? faker.datatype.boolean(0.6),
    latest_validation_status: validationStatus,
  }
}

export function createSources(count: number): Source[] {
  return Array.from({ length: count }, () => createSource())
}

/**
 * Create sources with guaranteed coverage of all test scenarios
 */
export function createDiverseSources(): Source[] {
  const sources: Source[] = []

  // 1. One source for each type (file, postgresql, mysql, snowflake, bigquery)
  SOURCE_TYPES.forEach((type) => {
    sources.push(createSource({ type }))
  })

  // 2. Sources with each validation status (success, failed, null/never validated)
  const statuses: Array<'success' | 'failed' | null> = ['success', 'failed', null]
  statuses.forEach((status) => {
    sources.push(createSource({
      validated: status !== null,
      validationStatus: status,
    }))
  })

  // 3. Active vs Inactive sources
  sources.push(createSource({ isActive: true, name: 'Active Production Source' }))
  sources.push(createSource({ isActive: false, name: 'Inactive Archive Source' }))

  // 4. With schema vs without schema
  sources.push(createSource({ hasSchema: true, name: 'Fully Configured Source' }))
  sources.push(createSource({ hasSchema: false, name: 'Pending Schema Setup' }))

  // 5. Recently validated vs never validated
  sources.push(createSource({ validated: true, name: 'Recently Validated Data' }))
  sources.push(createSource({ validated: false, name: 'Never Validated Source' }))

  // 6. Edge cases - long names, special characters
  sources.push(createSource({
    name: 'Very Long Source Name That Should Test UI Truncation Behavior (2024-Q4-Final)',
    type: 'file',
  }))
  sources.push(createSource({
    name: 'Source_with_underscores_and-dashes',
    type: 'postgresql',
  }))

  // 7. Add more random sources for volume
  for (let i = 0; i < 10; i++) {
    sources.push(createSource())
  }

  return sources
}

/**
 * Profile factory - generates data profiling results
 * Extended for comprehensive test coverage
 */

import type { ProfileResult, ColumnProfile } from '@/api/client'
import { randomInt, randomChoice, faker } from './base'

export interface ProfileFactoryOptions {
  sourceName?: string
  columnCount?: number
  rowCount?: number
  sizeBytes?: number
  // Scenario presets
  scenario?: 'normal' | 'large' | 'small' | 'empty' | 'wide' | 'highNulls' | 'lowCardinality'
}

// Expanded column specs covering all common data types
const COLUMN_SPECS: Array<{
  name: string
  dtype: string
  hasStats: boolean
}> = [
  // Numeric - integers
  { name: 'id', dtype: 'int64', hasStats: true },
  { name: 'user_id', dtype: 'int64', hasStats: true },
  { name: 'order_id', dtype: 'int64', hasStats: true },
  { name: 'quantity', dtype: 'int64', hasStats: true },
  { name: 'count', dtype: 'int64', hasStats: true },
  // Numeric - floats
  { name: 'amount', dtype: 'float64', hasStats: true },
  { name: 'price', dtype: 'float64', hasStats: true },
  { name: 'total', dtype: 'float64', hasStats: true },
  { name: 'score', dtype: 'float64', hasStats: true },
  { name: 'rating', dtype: 'float64', hasStats: true },
  { name: 'percentage', dtype: 'float64', hasStats: true },
  // String - contact
  { name: 'email', dtype: 'object', hasStats: false },
  { name: 'phone', dtype: 'object', hasStats: false },
  { name: 'address', dtype: 'object', hasStats: false },
  // String - identifiers
  { name: 'name', dtype: 'object', hasStats: false },
  { name: 'first_name', dtype: 'object', hasStats: false },
  { name: 'last_name', dtype: 'object', hasStats: false },
  { name: 'company', dtype: 'object', hasStats: false },
  // String - categorical
  { name: 'status', dtype: 'object', hasStats: false },
  { name: 'category', dtype: 'object', hasStats: false },
  { name: 'type', dtype: 'object', hasStats: false },
  { name: 'tier', dtype: 'object', hasStats: false },
  // Datetime
  { name: 'date', dtype: 'datetime64[ns]', hasStats: false },
  { name: 'created_at', dtype: 'datetime64[ns]', hasStats: false },
  { name: 'updated_at', dtype: 'datetime64[ns]', hasStats: false },
  { name: 'timestamp', dtype: 'datetime64[ns]', hasStats: false },
  // Boolean
  { name: 'is_active', dtype: 'bool', hasStats: false },
  { name: 'is_verified', dtype: 'bool', hasStats: false },
  { name: 'is_deleted', dtype: 'bool', hasStats: false },
  // Complex types
  { name: 'metadata', dtype: 'object', hasStats: false },
  { name: 'tags', dtype: 'object', hasStats: false },
]

function createColumnProfile(
  spec: (typeof COLUMN_SPECS)[0],
  options?: { highNulls?: boolean; lowCardinality?: boolean }
): ColumnProfile {
  // Vary null percentage based on options
  let nullPct: number
  if (options?.highNulls) {
    nullPct = faker.number.float({ min: 30, max: 80, fractionDigits: 1 })
  } else {
    nullPct = faker.number.float({ min: 0, max: 15, fractionDigits: 1 })
  }

  // Vary unique percentage based on options
  let uniquePct: number
  if (options?.lowCardinality) {
    uniquePct = faker.number.float({ min: 1, max: 10, fractionDigits: 1 })
  } else {
    uniquePct = faker.number.float({ min: 20, max: 100, fractionDigits: 1 })
  }

  const profile: ColumnProfile = {
    name: spec.name,
    dtype: spec.dtype,
    null_pct: `${nullPct}%`,
    unique_pct: `${uniquePct}%`,
  }

  if (spec.hasStats) {
    const mean = faker.number.float({ min: 0, max: 10000, fractionDigits: 2 })
    const std = faker.number.float({ min: 0, max: mean * 0.3, fractionDigits: 2 })
    profile.min = mean - std * 2
    profile.max = mean + std * 2
    profile.mean = mean
    profile.std = std
  }

  return profile
}

export function createProfileResult(options: ProfileFactoryOptions = {}): ProfileResult {
  // Handle scenario presets
  let columnCount: number
  let rowCount: number
  let sizeBytes: number
  let profileOptions: { highNulls?: boolean; lowCardinality?: boolean } = {}

  switch (options.scenario) {
    case 'empty':
      columnCount = options.columnCount ?? randomInt(3, 8)
      rowCount = 0
      sizeBytes = randomInt(100, 1000)
      break
    case 'small':
      columnCount = options.columnCount ?? randomInt(3, 6)
      rowCount = options.rowCount ?? randomInt(10, 100)
      sizeBytes = options.sizeBytes ?? randomInt(1000, 10000)
      break
    case 'large':
      columnCount = options.columnCount ?? randomInt(15, 25)
      rowCount = options.rowCount ?? randomInt(10000000, 100000000)
      sizeBytes = options.sizeBytes ?? randomInt(1000000000, 10000000000) // 1-10 GB
      break
    case 'wide':
      columnCount = options.columnCount ?? randomInt(50, 100)
      rowCount = options.rowCount ?? randomInt(10000, 100000)
      sizeBytes = options.sizeBytes ?? randomInt(100000000, 500000000)
      break
    case 'highNulls':
      columnCount = options.columnCount ?? randomInt(6, 12)
      rowCount = options.rowCount ?? randomInt(10000, 1000000)
      sizeBytes = options.sizeBytes ?? randomInt(1000000, 100000000)
      profileOptions = { highNulls: true }
      break
    case 'lowCardinality':
      columnCount = options.columnCount ?? randomInt(6, 12)
      rowCount = options.rowCount ?? randomInt(10000, 1000000)
      sizeBytes = options.sizeBytes ?? randomInt(1000000, 100000000)
      profileOptions = { lowCardinality: true }
      break
    default: // 'normal'
      columnCount = options.columnCount ?? randomInt(6, 12)
      rowCount = options.rowCount ?? randomInt(10000, 1000000)
      sizeBytes = options.sizeBytes ?? randomInt(1000000, 100000000)
  }

  // Ensure we don't request more columns than available
  const safeColumnCount = Math.min(columnCount, COLUMN_SPECS.length)
  const selectedSpecs = faker.helpers
    .shuffle([...COLUMN_SPECS])
    .slice(0, safeColumnCount)

  return {
    source: options.sourceName ?? faker.system.fileName(),
    row_count: rowCount,
    column_count: safeColumnCount,
    size_bytes: sizeBytes,
    columns: selectedSpecs.map((spec) => createColumnProfile(spec, profileOptions)),
  }
}

/**
 * Create diverse profile results for testing all scenarios
 */
export function createDiverseProfiles(sourceNames: string[]): ProfileResult[] {
  const profiles: ProfileResult[] = []
  const scenarios: ProfileFactoryOptions['scenario'][] = [
    'normal',
    'large',
    'small',
    'empty',
    'wide',
    'highNulls',
    'lowCardinality',
  ]

  // Create one profile for each scenario
  scenarios.forEach((scenario, i) => {
    const sourceName = sourceNames[i % sourceNames.length] ?? `Source ${i + 1}`
    profiles.push(createProfileResult({ scenario, sourceName }))
  })

  // Add a few more random profiles
  for (let i = scenarios.length; i < Math.max(scenarios.length, sourceNames.length); i++) {
    const sourceName = sourceNames[i % sourceNames.length]
    profiles.push(createProfileResult({
      sourceName,
      scenario: randomChoice(scenarios),
    }))
  }

  return profiles
}

/**
 * Drift detection factory - generates drift comparison results
 * Extended for comprehensive test coverage
 */

import type { DriftComparison, ColumnDriftResult, DriftResult } from '@/api/client'
import { createId, createTimestamp, randomChoice, randomInt, faker } from './base'

export interface DriftFactoryOptions {
  id?: string
  baselineSourceId?: string
  currentSourceId?: string
  hasDrift?: boolean
  hasHighDrift?: boolean
  driftPercentage?: number
  method?: 'ks' | 'psi' | 'chi2' | 'js' | 'auto'
  threshold?: number
  totalColumns?: number
}

const DRIFT_METHODS = ['ks', 'psi', 'chi2', 'js'] as const
const DTYPES = ['int64', 'float64', 'object', 'datetime64', 'bool', 'category'] as const

/**
 * Generate a unique column name, supporting more columns than the base array
 * Prevents infinite loop when totalColumns > COLUMN_NAMES_BASE.length
 */
function generateUniqueColumnName(usedColumns: Set<string>): string {
  // First try to use base names
  for (const baseName of COLUMN_NAMES_BASE) {
    if (!usedColumns.has(baseName)) {
      return baseName
    }
  }

  // Generate synthetic column names for large datasets
  const prefixes = ['metric', 'value', 'stat', 'measure', 'indicator', 'data', 'field', 'col']
  let attempt = 0
  while (attempt < 1000) {
    const prefix = prefixes[attempt % prefixes.length]
    const suffix = Math.floor(attempt / prefixes.length) + 1
    const name = `${prefix}_${suffix}`
    if (!usedColumns.has(name)) {
      return name
    }
    attempt++
  }

  // Fallback: use UUID-based name (guaranteed unique)
  return `column_${faker.string.alphanumeric(8)}`
}

// Base column names for drift detection
const COLUMN_NAMES_BASE = [
  // Revenue/Financial metrics
  'revenue',
  'gross_revenue',
  'net_revenue',
  'mrr',
  'arr',
  'aov',
  'ltv',
  'cac',
  'arpu',
  // User metrics
  'user_count',
  'active_users',
  'new_users',
  'dau',
  'mau',
  'wau',
  // Transaction metrics
  'transaction_amount',
  'transaction_count',
  'avg_transaction',
  'payment_volume',
  // Engagement metrics
  'engagement_score',
  'session_duration',
  'page_views',
  'bounce_rate',
  'click_rate',
  'open_rate',
  // Conversion metrics
  'conversion_rate',
  'checkout_rate',
  'signup_rate',
  'activation_rate',
  // Retention metrics
  'churn_rate',
  'retention_rate',
  'cohort_retention',
  // Satisfaction metrics
  'nps_score',
  'csat_score',
  'satisfaction_index',
  // Performance metrics
  'response_time',
  'latency_p50',
  'latency_p95',
  'latency_p99',
  'error_rate',
  'uptime',
  // Inventory metrics
  'stock_level',
  'turnover_rate',
  'days_on_hand',
]

// Alias for backward compatibility
const COLUMN_NAMES = COLUMN_NAMES_BASE

interface ColumnDriftOptions {
  column?: string
  dtype?: string
  drifted?: boolean
  level?: 'none' | 'low' | 'medium' | 'high'
  method?: 'ks' | 'psi' | 'chi2' | 'js'
}

function createColumnDriftResult(options: ColumnDriftOptions = {}): ColumnDriftResult {
  const drifted = options.drifted ?? faker.datatype.boolean(0.3)
  const method = options.method ?? randomChoice([...DRIFT_METHODS])
  const level = options.level ?? (drifted
    ? randomChoice(['medium', 'high'] as const)
    : randomChoice(['none', 'low'] as const))

  // Generate realistic statistics based on drift level
  const baselineMean = faker.number.float({ min: 10, max: 1000, fractionDigits: 2 })
  const baselineStd = faker.number.float({ min: 1, max: baselineMean * 0.3, fractionDigits: 2 })

  // Drift amount based on level
  const driftMultiplier = level === 'high' ? 0.5 : level === 'medium' ? 0.25 : level === 'low' ? 0.1 : 0
  const currentMean = baselineMean * (1 + (faker.datatype.boolean() ? driftMultiplier : -driftMultiplier))
  const currentStd = baselineStd * (1 + faker.number.float({ min: -0.2, max: 0.3 }))

  // P-value based on drift detection
  const pValue = drifted
    ? faker.number.float({ min: 0.0001, max: 0.04, fractionDigits: 4 })
    : faker.number.float({ min: 0.06, max: 0.99, fractionDigits: 4 })

  return {
    column: options.column ?? randomChoice(COLUMN_NAMES),
    dtype: options.dtype ?? randomChoice([...DTYPES]),
    drifted,
    level,
    method,
    statistic: faker.number.float({ min: 0, max: 1, fractionDigits: 4 }),
    p_value: pValue,
    baseline_stats: {
      mean: baselineMean,
      std: baselineStd,
      min: baselineMean - baselineStd * 2,
      max: baselineMean + baselineStd * 2,
      count: randomInt(10000, 1000000),
      null_count: randomInt(0, 100),
    },
    current_stats: {
      mean: currentMean,
      std: currentStd,
      min: currentMean - currentStd * 2,
      max: currentMean + currentStd * 2,
      count: randomInt(10000, 1000000),
      null_count: randomInt(0, 100),
    },
  }
}

export function createDriftResult(
  baselineSourceId: string,
  currentSourceId: string,
  options: { hasDrift?: boolean; hasHighDrift?: boolean; totalColumns?: number; driftPercentage?: number } = {}
): DriftResult {
  // Ensure totalColumns is at least 1 to avoid division by zero
  const totalColumns = Math.max(1, options.totalColumns ?? randomInt(5, 25))
  const hasDrift = options.hasDrift ?? faker.datatype.boolean(0.4)
  const hasHighDrift = options.hasHighDrift ?? (hasDrift && faker.datatype.boolean(0.5))

  let driftedCount: number
  if (options.driftPercentage !== undefined) {
    driftedCount = Math.round(totalColumns * (options.driftPercentage / 100))
  } else {
    driftedCount = hasDrift ? randomInt(1, Math.ceil(totalColumns * 0.6)) : 0
  }

  // Ensure driftedCount is at least 1 if hasHighDrift is true
  if (hasHighDrift && driftedCount < 1) {
    driftedCount = 1
  }

  // Ensure at least one high drift if hasHighDrift is true
  const highDriftCount = hasHighDrift ? randomInt(1, Math.max(1, Math.floor(driftedCount / 2) || 1)) : 0

  const usedColumns = new Set<string>()
  const columns: ColumnDriftResult[] = []

  // Add high drift columns
  for (let i = 0; i < highDriftCount; i++) {
    const column = generateUniqueColumnName(usedColumns)
    usedColumns.add(column)
    columns.push(createColumnDriftResult({ column, drifted: true, level: 'high' }))
  }

  // Add medium drift columns
  const mediumDriftCount = driftedCount - highDriftCount
  for (let i = 0; i < mediumDriftCount; i++) {
    const column = generateUniqueColumnName(usedColumns)
    usedColumns.add(column)
    columns.push(createColumnDriftResult({ column, drifted: true, level: 'medium' }))
  }

  // Add non-drifted columns
  const remainingColumns = totalColumns - driftedCount
  for (let i = 0; i < remainingColumns; i++) {
    const column = generateUniqueColumnName(usedColumns)
    usedColumns.add(column)
    columns.push(createColumnDriftResult({ column, drifted: false }))
  }

  return {
    baseline_source: baselineSourceId,
    current_source: currentSourceId,
    baseline_rows: randomInt(10000, 5000000),
    current_rows: randomInt(10000, 5000000),
    has_drift: driftedCount > 0,
    has_high_drift: highDriftCount > 0,
    total_columns: totalColumns,
    drifted_columns: columns.filter((c) => c.drifted).map((c) => c.column),
    columns,
  }
}

export function createDriftComparison(
  options: DriftFactoryOptions = {}
): DriftComparison {
  const baselineSourceId = options.baselineSourceId ?? createId()
  const currentSourceId = options.currentSourceId ?? createId()
  const hasDrift = options.hasDrift ?? faker.datatype.boolean(0.4)
  const hasHighDrift = options.hasHighDrift ?? (hasDrift && faker.datatype.boolean(0.5))

  const result = createDriftResult(baselineSourceId, currentSourceId, {
    hasDrift,
    hasHighDrift,
    totalColumns: options.totalColumns,
    driftPercentage: options.driftPercentage,
  })

  return {
    id: options.id ?? createId(),
    baseline_source_id: baselineSourceId,
    current_source_id: currentSourceId,
    has_drift: result.has_drift,
    has_high_drift: result.has_high_drift,
    total_columns: result.total_columns,
    drifted_columns: result.drifted_columns.length,
    drift_percentage:
      (result.drifted_columns.length / result.total_columns) * 100,
    result,
    config: {
      method: options.method ?? 'auto',
      threshold: options.threshold ?? 0.05,
    },
    created_at: createTimestamp(randomInt(0, 30)),
    updated_at: createTimestamp(randomInt(0, 7)),
  }
}

export function createDriftComparisons(count: number): DriftComparison[] {
  return Array.from({ length: count }, () => createDriftComparison())
}

/**
 * Create drift comparisons with guaranteed coverage of all test scenarios
 */
export function createDiverseDriftComparisons(
  baselineSourceIds: string[],
  currentSourceIds: string[]
): DriftComparison[] {
  // Guard against empty arrays
  if (!baselineSourceIds || baselineSourceIds.length === 0 ||
      !currentSourceIds || currentSourceIds.length === 0) {
    return []
  }

  const comparisons: DriftComparison[] = []
  const safeBaselineId = (index: number) => baselineSourceIds[index % baselineSourceIds.length]
  const safeCurrentId = (index: number) => currentSourceIds[index % currentSourceIds.length]

  // 1. No drift at all
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(0),
    currentSourceId: safeCurrentId(0),
    hasDrift: false,
    totalColumns: 10,
  }))

  // 2. Low drift (few columns, no high severity)
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(1),
    currentSourceId: safeCurrentId(1),
    hasDrift: true,
    hasHighDrift: false,
    driftPercentage: 10,
    totalColumns: 15,
  }))

  // 3. Medium drift
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(2),
    currentSourceId: safeCurrentId(2),
    hasDrift: true,
    hasHighDrift: false,
    driftPercentage: 30,
    totalColumns: 20,
  }))

  // 4. High drift (critical)
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(3),
    currentSourceId: safeCurrentId(3),
    hasDrift: true,
    hasHighDrift: true,
    driftPercentage: 50,
    totalColumns: 12,
  }))

  // 5. Severe drift (many columns affected)
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(4),
    currentSourceId: safeCurrentId(4),
    hasDrift: true,
    hasHighDrift: true,
    driftPercentage: 80,
    totalColumns: 25,
  }))

  // 6. Different detection methods
  const methods: Array<'ks' | 'psi' | 'chi2' | 'js'> = ['ks', 'psi', 'chi2', 'js']
  methods.forEach((method, i) => {
    comparisons.push(createDriftComparison({
      baselineSourceId: safeBaselineId(5 + i),
      currentSourceId: safeCurrentId(5 + i),
      method,
      hasDrift: faker.datatype.boolean(0.5),
    }))
  })

  // 7. Different thresholds - lower threshold = more likely to detect drift
  const thresholds = [0.01, 0.05, 0.10, 0.20]
  thresholds.forEach((threshold, i) => {
    // Lower threshold means more sensitive detection, so more drift detected
    const driftLikelihood = threshold <= 0.01 ? 0.9 : threshold <= 0.05 ? 0.7 : threshold <= 0.10 ? 0.4 : 0.2
    comparisons.push(createDriftComparison({
      baselineSourceId: safeBaselineId(9 + i),
      currentSourceId: safeCurrentId(9 + i),
      threshold,
      hasDrift: faker.datatype.boolean(driftLikelihood),
      driftPercentage: threshold <= 0.05 ? randomInt(30, 60) : randomInt(10, 30),
    }))
  })

  // 8. Large number of columns
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(0),
    currentSourceId: safeCurrentId(1),
    totalColumns: 50,
    hasDrift: true,
    driftPercentage: 25,
  }))

  // 9. Small number of columns
  comparisons.push(createDriftComparison({
    baselineSourceId: safeBaselineId(1),
    currentSourceId: safeCurrentId(2),
    totalColumns: 3,
    hasDrift: true,
  }))

  return comparisons
}

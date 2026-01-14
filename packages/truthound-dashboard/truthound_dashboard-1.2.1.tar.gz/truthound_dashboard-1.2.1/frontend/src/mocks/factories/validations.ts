/**
 * Validation factory - generates realistic validation results
 * Extended for comprehensive test coverage
 */

import type { Validation, ValidationIssue } from '@/api/client'
import {
  createId,
  createTimestamp,
  randomChoice,
  randomInt,
  faker,
} from './base'

export interface ValidationFactoryOptions {
  id?: string
  sourceId?: string
  status?: Validation['status']
  passed?: boolean
  issueCount?: number
  hasCritical?: boolean
  hasHigh?: boolean
  lowSeverityOnly?: boolean
  durationMs?: number
  rowCount?: number
  columnCount?: number
}

const ISSUE_TYPES = [
  'null_values',
  'type_mismatch',
  'out_of_range',
  'format_error',
  'duplicate_values',
  'missing_required',
  'constraint_violation',
  'pattern_mismatch',
  'referential_integrity',
  'encoding_error',
  // Additional realistic issue types
  'whitespace_issues',
  'invalid_date',
  'negative_value',
  'string_length_exceeded',
  'invalid_enum',
  'missing_foreign_key',
  'precision_loss',
  'timezone_inconsistency',
]

// More realistic column names for different domains
const COLUMN_NAMES = [
  // Common
  'id', 'uuid', 'external_id',
  // User
  'user_id', 'customer_id', 'email', 'phone', 'name', 'first_name', 'last_name',
  // Financial
  'amount', 'price', 'total', 'subtotal', 'tax', 'discount', 'balance',
  // Quantity
  'quantity', 'stock', 'count', 'items',
  // Status/Category
  'status', 'state', 'category', 'type', 'tier', 'priority',
  // Address
  'address', 'city', 'country', 'zip_code', 'postal_code',
  // Dates
  'date', 'created_at', 'updated_at', 'deleted_at', 'expires_at', 'due_date',
  // Technical
  'ip_address', 'user_agent', 'session_id', 'request_id',
  // Metrics
  'score', 'rating', 'percentage', 'conversion_rate',
]

const SEVERITIES: ValidationIssue['severity'][] = [
  'critical',
  'high',
  'medium',
  'low',
]

// Issue type specific details for more realistic data
const ISSUE_DETAILS: Record<string, () => { details: string; expected?: string; actual?: string }> = {
  null_values: () => ({
    details: `Found ${randomInt(1, 50)}% null values in non-nullable column`,
  }),
  type_mismatch: () => ({
    details: 'Column contains values with unexpected data type',
    expected: randomChoice(['integer', 'float', 'string', 'boolean', 'date']),
    actual: randomChoice(['string', 'null', 'mixed', 'object']),
  }),
  out_of_range: () => ({
    details: `Value ${randomInt(-1000, 1000)} is outside allowed range`,
    expected: `[${randomInt(0, 100)}, ${randomInt(1000, 10000)}]`,
    actual: String(randomInt(-1000, 50000)),
  }),
  format_error: () => ({
    details: randomChoice([
      'Invalid email format detected',
      'Phone number does not match expected pattern',
      'Date format is incorrect (expected YYYY-MM-DD)',
      'Invalid UUID format',
      'URL format validation failed',
    ]),
    expected: randomChoice(['email', 'phone', 'date', 'uuid', 'url']),
    actual: faker.string.alphanumeric(10),
  }),
  duplicate_values: () => ({
    details: `Found ${randomInt(10, 1000)} duplicate values in unique column`,
  }),
  missing_required: () => ({
    details: `${randomInt(1, 20)}% of rows missing required value`,
  }),
  constraint_violation: () => ({
    details: randomChoice([
      'Value violates check constraint',
      'Foreign key constraint violation',
      'Unique constraint violation',
      'Not null constraint violation',
    ]),
  }),
  pattern_mismatch: () => ({
    details: 'Value does not match expected pattern',
    expected: randomChoice(['^[A-Z]{2}\\d{4}$', '^\\d{3}-\\d{2}-\\d{4}$', '^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$']),
    actual: faker.string.alphanumeric(8),
  }),
  referential_integrity: () => ({
    details: `${randomInt(5, 100)} orphaned records found - referenced record does not exist`,
  }),
  encoding_error: () => ({
    details: randomChoice([
      'Invalid UTF-8 sequence detected',
      'Mixed encoding detected in column',
      'BOM character found in data',
      'Control characters found in string',
    ]),
  }),
  whitespace_issues: () => ({
    details: randomChoice([
      'Leading/trailing whitespace detected',
      'Multiple consecutive spaces found',
      'Tab characters in string data',
      'Non-breaking space characters detected',
    ]),
  }),
  invalid_date: () => ({
    details: randomChoice([
      'Date is in the future where not allowed',
      'Date before allowed minimum',
      'Invalid day for month (e.g., Feb 30)',
      'Date format inconsistent',
    ]),
  }),
  negative_value: () => ({
    details: 'Negative value found where only positive values allowed',
    expected: '>= 0',
    actual: String(-randomInt(1, 1000)),
  }),
  string_length_exceeded: () => ({
    details: `String length ${randomInt(256, 10000)} exceeds maximum allowed ${randomInt(100, 255)}`,
    expected: `<= ${randomInt(100, 255)}`,
    actual: String(randomInt(256, 10000)),
  }),
  invalid_enum: () => ({
    details: 'Value not in allowed enum list',
    expected: randomChoice([
      'active|inactive|pending',
      'low|medium|high|critical',
      'draft|published|archived',
    ]),
    actual: faker.word.noun(),
  }),
  missing_foreign_key: () => ({
    details: `Referenced ${faker.database.column()} does not exist in parent table`,
  }),
  precision_loss: () => ({
    details: 'Decimal precision loss detected during conversion',
    expected: '2 decimal places',
    actual: `${randomInt(3, 10)} decimal places`,
  }),
  timezone_inconsistency: () => ({
    details: randomChoice([
      'Mixed timezone formats in datetime column',
      'Missing timezone information',
      'Unexpected timezone offset',
    ]),
  }),
}

function createIssue(options?: { severity?: ValidationIssue['severity']; issueType?: string }): ValidationIssue {
  const severity = options?.severity ?? randomChoice(SEVERITIES)
  const issueType = options?.issueType ?? randomChoice(ISSUE_TYPES)
  const detailsGenerator = ISSUE_DETAILS[issueType] ?? (() => ({ details: faker.lorem.sentence() }))
  const { details, expected, actual } = detailsGenerator()

  return {
    column: randomChoice(COLUMN_NAMES),
    issue_type: issueType,
    count: randomInt(1, 5000),
    severity,
    details,
    expected,
    actual,
  }
}

function createIssues(
  count: number,
  options?: {
    guaranteeCritical?: boolean
    guaranteeHigh?: boolean
    lowSeverityOnly?: boolean
  }
): ValidationIssue[] {
  const issues: ValidationIssue[] = []

  // Guarantee at least one critical issue if requested
  if (options?.guaranteeCritical && count > 0) {
    issues.push(createIssue({ severity: 'critical' }))
  }

  // Guarantee at least one high issue if requested
  if (options?.guaranteeHigh && count > issues.length) {
    issues.push(createIssue({ severity: 'high' }))
  }

  // Fill remaining with issues
  while (issues.length < count) {
    if (options?.lowSeverityOnly) {
      // Only low severity issues (for "success with warnings" scenario)
      issues.push(createIssue({ severity: 'low' }))
    } else {
      issues.push(createIssue())
    }
  }

  return issues
}

export function createValidation(
  options: ValidationFactoryOptions = {}
): Validation {
  const status = options.status ?? randomChoice(['success', 'failed', 'error'])
  const passed = options.passed ?? status === 'success'

  let issueCount: number
  if (options.issueCount !== undefined) {
    issueCount = options.issueCount
  } else {
    issueCount = passed ? randomInt(0, 2) : randomInt(3, 25)
  }

  const issues = createIssues(issueCount, {
    guaranteeCritical: options.hasCritical,
    guaranteeHigh: options.hasHigh,
    lowSeverityOnly: options.lowSeverityOnly,
  })

  const criticalIssues = issues.filter((i) => i.severity === 'critical').length
  const highIssues = issues.filter((i) => i.severity === 'high').length
  const mediumIssues = issues.filter((i) => i.severity === 'medium').length
  const lowIssues = issues.filter((i) => i.severity === 'low').length

  const durationMs = options.durationMs ?? randomInt(200, 30000)
  const startedAt = createTimestamp(randomInt(0, 60))
  const completedAt = new Date(
    new Date(startedAt).getTime() + durationMs
  ).toISOString()

  return {
    id: options.id ?? createId(),
    source_id: options.sourceId ?? createId(),
    status,
    passed,
    has_critical: criticalIssues > 0,
    has_high: highIssues > 0,
    total_issues: issues.length,
    critical_issues: criticalIssues,
    high_issues: highIssues,
    medium_issues: mediumIssues,
    low_issues: lowIssues,
    row_count: options.rowCount ?? randomInt(100, 5000000),
    column_count: options.columnCount ?? randomInt(3, 100),
    issues,
    error_message: status === 'error' ? faker.lorem.sentence() : undefined,
    duration_ms: durationMs,
    started_at: startedAt,
    completed_at: completedAt,
    created_at: startedAt,
  }
}

export function createValidations(
  count: number,
  sourceId?: string
): Validation[] {
  return Array.from({ length: count }, () =>
    createValidation({ sourceId })
  ).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

/**
 * Create validations with guaranteed coverage of all test scenarios
 */
export function createDiverseValidations(sourceId: string): Validation[] {
  const validations: Validation[] = []

  // 1. Perfect validation - no issues
  validations.push(createValidation({
    sourceId,
    status: 'success',
    passed: true,
    issueCount: 0,
  }))

  // 2. Success with minor warnings (low severity only - no critical/high issues)
  validations.push(createValidation({
    sourceId,
    status: 'success',
    passed: true,
    issueCount: 3,
    lowSeverityOnly: true,
  }))

  // 3. Failed with critical issues
  validations.push(createValidation({
    sourceId,
    status: 'failed',
    passed: false,
    hasCritical: true,
    issueCount: 5,
  }))

  // 4. Failed with high severity issues (no critical)
  validations.push(createValidation({
    sourceId,
    status: 'failed',
    passed: false,
    hasHigh: true,
    issueCount: 8,
  }))

  // 5. Failed with many issues
  validations.push(createValidation({
    sourceId,
    status: 'failed',
    passed: false,
    issueCount: 50,
  }))

  // 6. Error status (validation crashed)
  validations.push(createValidation({
    sourceId,
    status: 'error',
    passed: false,
    issueCount: 0,
  }))

  // 7. Large dataset validation
  validations.push(createValidation({
    sourceId,
    rowCount: 10000000,
    columnCount: 150,
    durationMs: 120000,
  }))

  // 8. Small dataset validation (fast)
  validations.push(createValidation({
    sourceId,
    rowCount: 50,
    columnCount: 5,
    durationMs: 150,
  }))

  // 9. Medium with mixed severities
  validations.push(createValidation({
    sourceId,
    status: 'failed',
    passed: false,
    hasCritical: true,
    hasHigh: true,
    issueCount: 12,
  }))

  // 10. Additional random validations for history
  for (let i = 0; i < 5; i++) {
    validations.push(createValidation({ sourceId }))
  }

  return validations.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

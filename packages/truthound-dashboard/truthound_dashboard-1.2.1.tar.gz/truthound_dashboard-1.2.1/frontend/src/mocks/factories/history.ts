/**
 * History factory - generates validation history and trends
 */

import type {
  HistoryResponse,
  HistorySummary,
  TrendDataPoint,
  FailureFrequencyItem,
  RecentValidation,
} from '@/api/client'
import { createId, randomChoice, randomInt, faker } from './base'

const ISSUE_TYPES = [
  'null_values',
  'type_mismatch',
  'out_of_range',
  'format_error',
  'duplicate_values',
  'missing_required',
  'constraint_violation',
]

function createSummary(totalRuns: number): HistorySummary {
  // Guard against zero or negative totalRuns
  if (totalRuns <= 0) {
    return {
      total_runs: 0,
      passed_runs: 0,
      failed_runs: 0,
      success_rate: 0,
    }
  }

  const passedRuns = Math.floor(totalRuns * faker.number.float({ min: 0.6, max: 0.95 }))
  const failedRuns = totalRuns - passedRuns

  return {
    total_runs: totalRuns,
    passed_runs: passedRuns,
    failed_runs: failedRuns,
    success_rate: (passedRuns / totalRuns) * 100,
  }
}

function createTrendData(
  period: '7d' | '30d' | '90d',
  granularity: 'hourly' | 'daily' | 'weekly'
): TrendDataPoint[] {
  const points: TrendDataPoint[] = []
  let days: number

  switch (period) {
    case '7d':
      days = 7
      break
    case '30d':
      days = 30
      break
    case '90d':
      days = 90
      break
  }

  // Guard against zero days (shouldn't happen but be safe)
  if (days <= 0) {
    return []
  }

  // Calculate intervals, ensuring at least 1
  let intervals: number
  if (granularity === 'hourly') {
    intervals = days * 24
  } else if (granularity === 'daily') {
    intervals = days
  } else {
    // weekly: ensure at least 1 interval
    intervals = Math.max(1, Math.ceil(days / 7))
  }

  for (let i = intervals - 1; i >= 0; i--) {
    const date = new Date()
    if (granularity === 'hourly') {
      date.setHours(date.getHours() - i)
    } else if (granularity === 'daily') {
      date.setDate(date.getDate() - i)
    } else {
      date.setDate(date.getDate() - i * 7)
    }

    const runCount = randomInt(5, 30)
    const passedCount = Math.floor(runCount * faker.number.float({ min: 0.6, max: 0.98 }))
    const failedCount = runCount - passedCount

    points.push({
      date: date.toISOString().split('T')[0],
      success_rate: runCount > 0 ? (passedCount / runCount) * 100 : 0,
      run_count: runCount,
      passed_count: passedCount,
      failed_count: failedCount,
    })
  }

  return points
}

function createFailureFrequency(): FailureFrequencyItem[] {
  return faker.helpers
    .shuffle([...ISSUE_TYPES])
    .slice(0, randomInt(3, 6))
    .map((issue) => ({
      issue,
      count: randomInt(5, 100),
    }))
    .sort((a, b) => b.count - a.count)
}

function createRecentValidations(count: number): RecentValidation[] {
  const validations: RecentValidation[] = []

  for (let i = 0; i < count; i++) {
    const date = new Date()
    date.setHours(date.getHours() - i * randomInt(1, 6))

    const passed = faker.datatype.boolean(0.75)

    validations.push({
      id: createId(),
      status: passed ? 'success' : randomChoice(['failed', 'error']),
      passed,
      has_critical: !passed && faker.datatype.boolean(0.3),
      has_high: !passed && faker.datatype.boolean(0.5),
      total_issues: passed ? randomInt(0, 2) : randomInt(3, 20),
      created_at: date.toISOString(),
    })
  }

  return validations
}

export function createHistoryResponse(
  period: '7d' | '30d' | '90d' = '30d',
  granularity: 'hourly' | 'daily' | 'weekly' = 'daily'
): HistoryResponse {
  const totalRuns = randomInt(50, 500)

  return {
    success: true,
    data: {
      summary: createSummary(totalRuns),
      trend: createTrendData(period, granularity),
      failure_frequency: createFailureFrequency(),
      recent_validations: createRecentValidations(10),
    },
  }
}

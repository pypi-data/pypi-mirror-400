/**
 * Base factory utilities for generating mock data
 * Provides consistent ID generation, timestamps, and random helpers
 */

import { faker } from '@faker-js/faker'

// Set seed for reproducible data in demos
faker.seed(12345)

export function createId(): string {
  return faker.string.uuid()
}

export function createTimestamp(daysAgo = 0): string {
  const date = new Date()
  date.setDate(date.getDate() - daysAgo)
  return date.toISOString()
}

export function createRecentTimestamp(): string {
  return createTimestamp(faker.number.int({ min: 0, max: 30 }))
}

export function randomChoice<T>(items: T[]): T {
  if (items.length === 0) {
    throw new Error('randomChoice: items array cannot be empty')
  }
  if (items.length === 1) {
    return items[0]
  }
  return items[faker.number.int({ min: 0, max: items.length - 1 })]
}

export function randomSubset<T>(items: T[], min = 1, max?: number): T[] {
  // Handle empty array
  if (items.length === 0) {
    return []
  }

  // Ensure min doesn't exceed items length
  const safeMin = Math.min(min, items.length)
  // Ensure max doesn't exceed items length
  const safeMax = Math.min(max ?? items.length, items.length)
  // Ensure min <= max
  const finalMin = Math.min(safeMin, safeMax)
  const finalMax = Math.max(safeMin, safeMax)

  const count = faker.number.int({ min: finalMin, max: finalMax })
  return faker.helpers.shuffle([...items]).slice(0, count)
}

export function randomPercent(): number {
  return faker.number.float({ min: 0, max: 100, fractionDigits: 1 })
}

export function randomInt(min: number, max: number): number {
  return faker.number.int({ min, max })
}

export { faker }

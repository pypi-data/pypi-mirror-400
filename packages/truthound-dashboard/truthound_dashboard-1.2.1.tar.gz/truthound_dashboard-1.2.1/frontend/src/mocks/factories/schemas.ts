/**
 * Schema factory - generates realistic schema definitions
 * Extended for comprehensive test coverage
 */

import type { Schema } from '@/api/client'
import { createId, createTimestamp, randomInt, randomChoice, faker } from './base'

export interface SchemaFactoryOptions {
  id?: string
  sourceId?: string
  columns?: string[]
  columnCount?: number
  version?: string
  isActive?: boolean
}

// Comprehensive column definitions covering various data types and constraints
const COLUMN_DEFINITIONS = [
  // Primary keys
  { name: 'id', dtype: 'integer', constraints: ['not_null', 'unique', 'primary_key'] },
  { name: 'uuid', dtype: 'string', constraints: ['not_null', 'unique', 'uuid_format'] },

  // Foreign keys
  { name: 'user_id', dtype: 'integer', constraints: ['not_null', 'foreign_key:users.id'] },
  { name: 'customer_id', dtype: 'integer', constraints: ['foreign_key:customers.id'] },
  { name: 'order_id', dtype: 'integer', constraints: ['not_null', 'foreign_key:orders.id'] },
  { name: 'product_id', dtype: 'integer', constraints: ['foreign_key:products.id'] },

  // Contact info
  { name: 'email', dtype: 'string', constraints: ['not_null', 'email_format', 'unique'] },
  { name: 'phone', dtype: 'string', constraints: ['phone_format', 'regex:^\\+?[1-9]\\d{1,14}$'] },
  { name: 'mobile', dtype: 'string', constraints: ['phone_format'] },

  // Names
  { name: 'name', dtype: 'string', constraints: ['not_null', 'min_length:1', 'max_length:255'] },
  { name: 'first_name', dtype: 'string', constraints: ['not_null', 'min_length:1'] },
  { name: 'last_name', dtype: 'string', constraints: ['not_null', 'min_length:1'] },
  { name: 'company_name', dtype: 'string', constraints: ['max_length:500'] },
  { name: 'display_name', dtype: 'string', constraints: [] },

  // Financial
  { name: 'amount', dtype: 'decimal', constraints: ['not_null', 'min:0', 'precision:10,2'] },
  { name: 'price', dtype: 'decimal', constraints: ['not_null', 'min:0', 'precision:10,2'] },
  { name: 'total', dtype: 'decimal', constraints: ['min:0', 'precision:12,2'] },
  { name: 'subtotal', dtype: 'decimal', constraints: ['min:0'] },
  { name: 'tax', dtype: 'decimal', constraints: ['min:0', 'max:1000000'] },
  { name: 'discount', dtype: 'decimal', constraints: ['min:0', 'max:100'] },
  { name: 'balance', dtype: 'decimal', constraints: ['precision:15,2'] },
  { name: 'currency', dtype: 'string', constraints: ['enum:USD,EUR,GBP,JPY,KRW,CNY'] },

  // Quantities
  { name: 'quantity', dtype: 'integer', constraints: ['not_null', 'min:0', 'max:1000000'] },
  { name: 'stock', dtype: 'integer', constraints: ['min:0'] },
  { name: 'count', dtype: 'integer', constraints: ['min:0'] },

  // Status/Enum fields
  { name: 'status', dtype: 'string', constraints: ['not_null', 'enum:active,inactive,pending,archived'] },
  { name: 'state', dtype: 'string', constraints: ['enum:draft,submitted,approved,rejected'] },
  { name: 'category', dtype: 'string', constraints: ['enum:electronics,clothing,food,services,other'] },
  { name: 'type', dtype: 'string', constraints: ['not_null'] },
  { name: 'tier', dtype: 'string', constraints: ['enum:free,basic,premium,enterprise'] },
  { name: 'priority', dtype: 'string', constraints: ['enum:low,medium,high,critical'] },

  // Address fields
  { name: 'address', dtype: 'string', constraints: ['max_length:1000'] },
  { name: 'address_line1', dtype: 'string', constraints: ['not_null', 'max_length:255'] },
  { name: 'address_line2', dtype: 'string', constraints: ['max_length:255'] },
  { name: 'city', dtype: 'string', constraints: ['max_length:100'] },
  { name: 'state_province', dtype: 'string', constraints: ['max_length:100'] },
  { name: 'country', dtype: 'string', constraints: ['iso_country_code'] },
  { name: 'zip_code', dtype: 'string', constraints: ['regex:^\\d{5}(-\\d{4})?$'] },
  { name: 'postal_code', dtype: 'string', constraints: ['max_length:20'] },

  // Dates and times
  { name: 'date', dtype: 'date', constraints: ['date_format:YYYY-MM-DD'] },
  { name: 'created_at', dtype: 'datetime', constraints: ['not_null'] },
  { name: 'updated_at', dtype: 'datetime', constraints: [] },
  { name: 'deleted_at', dtype: 'datetime', constraints: [] },
  { name: 'expires_at', dtype: 'datetime', constraints: [] },
  { name: 'due_date', dtype: 'date', constraints: [] },
  { name: 'birth_date', dtype: 'date', constraints: ['date_format:YYYY-MM-DD'] },
  { name: 'timestamp', dtype: 'datetime', constraints: ['not_null', 'timezone:UTC'] },

  // Boolean flags
  { name: 'is_active', dtype: 'boolean', constraints: ['not_null'] },
  { name: 'is_verified', dtype: 'boolean', constraints: [] },
  { name: 'is_deleted', dtype: 'boolean', constraints: [] },
  { name: 'is_primary', dtype: 'boolean', constraints: [] },
  { name: 'has_subscription', dtype: 'boolean', constraints: [] },
  { name: 'email_verified', dtype: 'boolean', constraints: [] },

  // Text/Content
  { name: 'description', dtype: 'string', constraints: ['max_length:5000'] },
  { name: 'notes', dtype: 'text', constraints: [] },
  { name: 'comment', dtype: 'text', constraints: ['max_length:10000'] },
  { name: 'content', dtype: 'text', constraints: [] },

  // Technical fields
  { name: 'ip_address', dtype: 'string', constraints: ['ip_format'] },
  { name: 'user_agent', dtype: 'string', constraints: ['max_length:1000'] },
  { name: 'session_id', dtype: 'string', constraints: ['uuid_format'] },
  { name: 'request_id', dtype: 'string', constraints: ['uuid_format'] },
  { name: 'api_key', dtype: 'string', constraints: ['min_length:32'] },

  // Metrics
  { name: 'score', dtype: 'float', constraints: ['min:0', 'max:100'] },
  { name: 'rating', dtype: 'float', constraints: ['min:0', 'max:5'] },
  { name: 'percentage', dtype: 'float', constraints: ['min:0', 'max:100'] },
  { name: 'conversion_rate', dtype: 'float', constraints: ['min:0', 'max:1'] },
  { name: 'weight', dtype: 'float', constraints: ['min:0'] },
  { name: 'height', dtype: 'float', constraints: ['min:0'] },

  // JSON/Complex types
  { name: 'metadata', dtype: 'json', constraints: [] },
  { name: 'settings', dtype: 'json', constraints: [] },
  { name: 'tags', dtype: 'array', constraints: [] },
  { name: 'options', dtype: 'json', constraints: [] },

  // URLs and references
  { name: 'url', dtype: 'string', constraints: ['url_format'] },
  { name: 'image_url', dtype: 'string', constraints: ['url_format'] },
  { name: 'callback_url', dtype: 'string', constraints: ['url_format'] },
  { name: 'reference_code', dtype: 'string', constraints: ['regex:^[A-Z]{2,4}-\\d{6,10}$'] },
]

function generateSchemaYaml(columns: typeof COLUMN_DEFINITIONS, version: string): string {
  const lines = ['schema:', `  version: "${version}"`, '  columns:']

  columns.forEach((col) => {
    lines.push(`    ${col.name}:`)
    lines.push(`      dtype: ${col.dtype}`)
    if (col.constraints.length > 0) {
      lines.push('      constraints:')
      col.constraints.forEach((c) => lines.push(`        - ${c}`))
    }
  })

  return lines.join('\n')
}

export function createSchema(options: SchemaFactoryOptions = {}): Schema {
  const columnCount = options.columnCount ?? randomInt(5, 20)
  const version = options.version ?? randomChoice(['1.0', '1.1', '2.0'])
  const createdAt = createTimestamp(randomInt(7, 90))

  // If specific columns are provided, find matching definitions or create defaults
  let selectedColumns: typeof COLUMN_DEFINITIONS
  let columns: string[]

  if (options.columns && options.columns.length > 0) {
    // Map provided column names to definitions, create defaults for unknown columns
    selectedColumns = options.columns.map((colName) => {
      const found = COLUMN_DEFINITIONS.find((c) => c.name === colName)
      if (found) return found
      // Create a default definition for unknown column names
      return { name: colName, dtype: 'string', constraints: [] as string[] }
    })
    columns = options.columns
  } else {
    // Random selection
    selectedColumns = faker.helpers
      .shuffle([...COLUMN_DEFINITIONS])
      .slice(0, columnCount)
    columns = selectedColumns.map((c) => c.name)
  }

  return {
    id: options.id ?? createId(),
    source_id: options.sourceId ?? createId(),
    schema_yaml: generateSchemaYaml(selectedColumns, version),
    schema_json: {
      version,
      columns: selectedColumns.reduce(
        (acc, col) => {
          acc[col.name] = { dtype: col.dtype, constraints: col.constraints }
          return acc
        },
        {} as Record<string, unknown>
      ),
    },
    row_count: randomInt(100, 10000000),
    column_count: columns.length,
    columns,
    version,
    is_active: options.isActive ?? true,
    created_at: createdAt,
    updated_at: createdAt,
  }
}

/**
 * Create schemas with guaranteed coverage of all test scenarios
 */
export function createDiverseSchema(sourceId: string): Schema {
  // Create a schema with diverse column types covering all data types
  const diverseColumns = [
    // One of each major data type
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'integer')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'float')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'decimal')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'string' && c.constraints.includes('email_format'))!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'boolean')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'date')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'datetime')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'text')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'json')!,
    COLUMN_DEFINITIONS.find((c) => c.dtype === 'array')!,
    // Various constraint types
    COLUMN_DEFINITIONS.find((c) => c.constraints.includes('unique'))!,
    COLUMN_DEFINITIONS.find((c) => c.constraints.some((cn) => cn.startsWith('enum:')))!,
    COLUMN_DEFINITIONS.find((c) => c.constraints.some((cn) => cn.startsWith('regex:')))!,
    COLUMN_DEFINITIONS.find((c) => c.constraints.some((cn) => cn.startsWith('min:')))!,
  ].filter(Boolean)

  return createSchema({
    sourceId,
    columnCount: diverseColumns.length,
  })
}

// Create schema presets for different domain scenarios
export const SCHEMA_PRESETS = {
  ecommerce: () => createSchema({
    columnCount: 15,
    columns: ['id', 'order_id', 'customer_id', 'product_id', 'quantity', 'price', 'total', 'tax', 'discount', 'status', 'created_at', 'updated_at', 'currency', 'notes', 'is_deleted'],
  }),
  userManagement: () => createSchema({
    columnCount: 12,
    columns: ['id', 'uuid', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'is_verified', 'created_at', 'updated_at', 'tier', 'metadata'],
  }),
  financial: () => createSchema({
    columnCount: 10,
    columns: ['id', 'amount', 'balance', 'currency', 'status', 'created_at', 'due_date', 'reference_code', 'description', 'metadata'],
  }),
  logging: () => createSchema({
    columnCount: 8,
    columns: ['id', 'timestamp', 'ip_address', 'user_agent', 'session_id', 'request_id', 'status', 'content'],
  }),
  minimal: () => createSchema({
    columnCount: 3,
    columns: ['id', 'name', 'created_at'],
  }),
  large: () => createSchema({
    columnCount: 30,
  }),
}

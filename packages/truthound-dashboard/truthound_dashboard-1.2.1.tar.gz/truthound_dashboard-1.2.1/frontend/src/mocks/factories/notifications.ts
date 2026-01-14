/**
 * Notification factory - generates notification channels, rules, and logs
 * Extended for comprehensive test coverage
 */

import type {
  NotificationChannel,
  NotificationRule,
  NotificationLog,
  NotificationStats,
} from '@/api/client'
import { createId, createTimestamp, randomChoice, randomInt, faker } from './base'

// ============================================================================
// Channels
// ============================================================================

export interface ChannelFactoryOptions {
  id?: string
  name?: string
  type?: NotificationChannel['type']
  isActive?: boolean
  configSummary?: string
}

// Realistic Slack channel names
const SLACK_CHANNELS = [
  '#alerts',
  '#data-quality',
  '#monitoring',
  '#data-ops',
  '#engineering-alerts',
  '#on-call',
  '#incidents',
  '#data-platform',
  '#quality-alerts',
  '#pipeline-status',
  '#critical-alerts',
  '#data-team',
]

// Realistic webhook endpoints
const WEBHOOK_SERVICES = [
  'PagerDuty',
  'OpsGenie',
  'Datadog',
  'ServiceNow',
  'Jira',
  'Custom Integration',
  'Microsoft Teams',
  'Discord',
  'Zapier',
  'n8n',
]

const CHANNEL_CONFIGS: Record<string, (options?: { configSummary?: string }) => { summary: string }> = {
  slack: (options) => ({
    summary: options?.configSummary ?? `Slack: ${faker.helpers.arrayElement(SLACK_CHANNELS)}`,
  }),
  email: (options) => {
    if (options?.configSummary) return { summary: options.configSummary }
    const emails = Array.from(
      { length: randomInt(1, 5) },
      () => faker.internet.email()
    )
    return {
      summary: `Email: ${emails.slice(0, 2).join(', ')}${emails.length > 2 ? ` (+${emails.length - 2} more)` : ''}`,
    }
  },
  webhook: (options) => ({
    summary: options?.configSummary ?? `Webhook: ${faker.helpers.arrayElement(WEBHOOK_SERVICES)} - ${faker.internet.domainName()}`,
  }),
}

// Realistic channel names
const CHANNEL_NAME_TEMPLATES = {
  slack: [
    'Production Alerts',
    'Data Quality Team',
    'Engineering On-Call',
    'Critical Notifications',
    'Daily Summary',
    'Incident Response',
    'Platform Monitoring',
  ],
  email: [
    'Data Team Distribution',
    'Management Reports',
    'Compliance Notifications',
    'Daily Digest',
    'Critical Alerts',
    'Weekly Summary',
    'Stakeholder Updates',
  ],
  webhook: [
    'PagerDuty Integration',
    'OpsGenie Alerts',
    'ServiceNow Tickets',
    'Datadog Events',
    'Custom Webhook',
    'Teams Notifications',
    'ITSM Integration',
  ],
}

export function createNotificationChannel(
  options: ChannelFactoryOptions = {}
): NotificationChannel {
  const type = options.type ?? randomChoice(['slack', 'email', 'webhook'] as const)
  const { summary } = CHANNEL_CONFIGS[type]({ configSummary: options.configSummary })
  const nameTemplates = CHANNEL_NAME_TEMPLATES[type]

  return {
    id: options.id ?? createId(),
    name: options.name ?? `${randomChoice(nameTemplates)} (${faker.string.alphanumeric(3)})`,
    type,
    is_active: options.isActive ?? faker.datatype.boolean(0.85),
    config_summary: summary,
    created_at: createTimestamp(randomInt(14, 180)),
    updated_at: createTimestamp(randomInt(0, 14)),
  }
}

export function createNotificationChannels(count: number): NotificationChannel[] {
  return Array.from({ length: count }, () => createNotificationChannel())
}

/**
 * Create notification channels with guaranteed coverage of all test scenarios
 */
export function createDiverseChannels(): NotificationChannel[] {
  const channels: NotificationChannel[] = []

  // 1. Active Slack channel
  channels.push(createNotificationChannel({
    name: 'Production Alerts (Slack)',
    type: 'slack',
    isActive: true,
    configSummary: 'Slack: #production-alerts',
  }))

  // 2. Active Email channel (single recipient)
  channels.push(createNotificationChannel({
    name: 'Admin Email',
    type: 'email',
    isActive: true,
    configSummary: 'Email: admin@company.com',
  }))

  // 3. Active Email channel (multiple recipients)
  channels.push(createNotificationChannel({
    name: 'Data Team Distribution',
    type: 'email',
    isActive: true,
    configSummary: 'Email: team@company.com, lead@company.com (+3 more)',
  }))

  // 4. Active Webhook channel
  channels.push(createNotificationChannel({
    name: 'PagerDuty Integration',
    type: 'webhook',
    isActive: true,
    configSummary: 'Webhook: PagerDuty - events.pagerduty.com',
  }))

  // 5. Inactive Slack channel
  channels.push(createNotificationChannel({
    name: 'Legacy Slack Channel',
    type: 'slack',
    isActive: false,
    configSummary: 'Slack: #old-alerts',
  }))

  // 6. Inactive Email channel
  channels.push(createNotificationChannel({
    name: 'Deprecated Mailing List',
    type: 'email',
    isActive: false,
    configSummary: 'Email: deprecated@company.com',
  }))

  // 7. Inactive Webhook
  channels.push(createNotificationChannel({
    name: 'Old OpsGenie Integration',
    type: 'webhook',
    isActive: false,
    configSummary: 'Webhook: OpsGenie - api.opsgenie.com',
  }))

  // 8. Multiple active channels of same type
  channels.push(createNotificationChannel({
    name: 'Secondary Slack Alert',
    type: 'slack',
    isActive: true,
    configSummary: 'Slack: #data-quality-alerts',
  }))

  channels.push(createNotificationChannel({
    name: 'Executive Summary Emails',
    type: 'email',
    isActive: true,
    configSummary: 'Email: exec@company.com, cto@company.com',
  }))

  channels.push(createNotificationChannel({
    name: 'Datadog Events',
    type: 'webhook',
    isActive: true,
    configSummary: 'Webhook: Datadog - app.datadoghq.com',
  }))

  // Add a few random channels
  for (let i = 0; i < 5; i++) {
    channels.push(createNotificationChannel())
  }

  return channels
}

// ============================================================================
// Rules
// ============================================================================

export interface RuleFactoryOptions {
  id?: string
  name?: string
  condition?: string
  conditionConfig?: Record<string, unknown>
  channelIds?: string[]
  sourceIds?: string[]
  isActive?: boolean
}

// Backend NotificationRule conditions from models.py:
// 'validation_failed', 'critical_issues', 'high_issues', 'schedule_failed', 'drift_detected'
const CONDITIONS = [
  'validation_failed',
  'critical_issues',
  'high_issues',
  'schedule_failed',
  'drift_detected',
]

const RULE_NAMES = [
  'Critical Alert',
  'Failure Notification',
  'Daily Summary',
  'Drift Detection Alert',
  'Success Confirmation',
  'High Priority Issues',
  'Warning Notification',
  'Error Alert',
  'Threshold Breach Alert',
  'All Events Logger',
  'Business Critical Alert',
  'SLA Breach Warning',
]

// Condition-specific configurations matching backend
const CONDITION_CONFIGS: Record<string, () => Record<string, unknown> | undefined> = {
  validation_failed: () => undefined,
  critical_issues: () => ({ min_issues: randomInt(1, 5) }),
  high_issues: () => ({ min_issues: randomInt(1, 10) }),
  schedule_failed: () => undefined,
  drift_detected: () => ({
    drift_level: randomChoice(['medium', 'high']),
    min_columns: randomInt(1, 5),
  }),
}

// Store reference to available channel IDs for rule creation
let _availableChannelIds: string[] = []

/**
 * Set available channel IDs for rule creation
 * This ensures rules reference existing channels
 */
export function setAvailableChannelIds(ids: string[]): void {
  _availableChannelIds = ids
}

export function createNotificationRule(
  options: RuleFactoryOptions = {}
): NotificationRule {
  const condition = options.condition ?? randomChoice(CONDITIONS)
  const configGenerator = CONDITION_CONFIGS[condition] ?? (() => undefined)

  // Use provided channelIds, or fall back to available channels, or generate new IDs as last resort
  let channelIds: string[]
  if (options.channelIds) {
    channelIds = options.channelIds
  } else if (_availableChannelIds.length > 0) {
    // Use existing channel IDs
    const count = randomInt(1, Math.min(3, _availableChannelIds.length))
    channelIds = faker.helpers.shuffle([..._availableChannelIds]).slice(0, count)
  } else {
    // Fallback: generate new IDs (for backwards compatibility)
    channelIds = [createId()]
  }

  return {
    id: options.id ?? createId(),
    name: options.name ?? `${randomChoice(RULE_NAMES)} (${faker.string.alphanumeric(3)})`,
    condition,
    condition_config: options.conditionConfig ?? configGenerator(),
    channel_ids: channelIds,
    source_ids: options.sourceIds ?? (faker.datatype.boolean(0.3) ? [createId()] : undefined),
    is_active: options.isActive ?? faker.datatype.boolean(0.8),
    created_at: createTimestamp(randomInt(7, 90)),
    updated_at: createTimestamp(randomInt(0, 7)),
  }
}

export function createNotificationRules(count: number): NotificationRule[] {
  return Array.from({ length: count }, () => createNotificationRule())
}

/**
 * Create notification rules with guaranteed coverage of all test scenarios
 */
export function createDiverseRules(channelIds: string[], sourceIds?: string[]): NotificationRule[] {
  // Guard against empty channelIds
  if (!channelIds || channelIds.length === 0) {
    return []
  }

  const rules: NotificationRule[] = []
  const safeChannelId = (index: number) => channelIds[index % channelIds.length]

  // 1. Active rule for each condition type
  CONDITIONS.forEach((condition) => {
    rules.push(createNotificationRule({
      name: `${condition.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} Rule`,
      condition,
      channelIds: channelIds.length > 1 ? [safeChannelId(0), safeChannelId(1)] : [safeChannelId(0)],
      isActive: true,
    }))
  })

  // 2. Rule with single channel
  rules.push(createNotificationRule({
    name: 'Single Channel Alert',
    condition: 'validation_failed',
    channelIds: [safeChannelId(0)],
    isActive: true,
  }))

  // 3. Rule with multiple channels
  rules.push(createNotificationRule({
    name: 'Multi-Channel Alert',
    condition: 'critical_issues',
    channelIds: channelIds.slice(0, Math.min(4, channelIds.length)),
    isActive: true,
  }))

  // 4. Rule filtered to specific sources
  if (sourceIds && sourceIds.length > 0) {
    rules.push(createNotificationRule({
      name: 'Source-Specific Alert',
      condition: 'validation_failed',
      channelIds: [safeChannelId(0)],
      sourceIds: [sourceIds[0]],
      isActive: true,
    }))

    rules.push(createNotificationRule({
      name: 'Multi-Source Alert',
      condition: 'critical_issues',
      channelIds: channelIds.length > 1 ? [safeChannelId(0), safeChannelId(1)] : [safeChannelId(0)],
      sourceIds: sourceIds.slice(0, 3),
      isActive: true,
    }))
  }

  // 5. Rule applying to all sources
  rules.push(createNotificationRule({
    name: 'Global Alert Rule',
    condition: 'critical_issues',
    channelIds: [safeChannelId(0)],
    sourceIds: undefined,
    isActive: true,
  }))

  // 6. Inactive rules
  rules.push(createNotificationRule({
    name: 'Paused Alert Rule',
    condition: 'validation_failed',
    channelIds: [safeChannelId(0)],
    isActive: false,
  }))

  rules.push(createNotificationRule({
    name: 'Disabled Schedule Alert',
    condition: 'schedule_failed',
    channelIds: [safeChannelId(0)],
    isActive: false,
  }))

  // 7. Rule with custom condition config (high issues threshold)
  rules.push(createNotificationRule({
    name: 'High Issues Alert (>5 issues)',
    condition: 'high_issues',
    conditionConfig: {
      min_issues: 5,
    },
    channelIds: [safeChannelId(0)],
    isActive: true,
  }))

  // Add a few random rules
  for (let i = 0; i < 3; i++) {
    rules.push(createNotificationRule({
      channelIds: [safeChannelId(i)],
    }))
  }

  return rules
}

// ============================================================================
// Logs
// ============================================================================

export interface LogFactoryOptions {
  id?: string
  channelId?: string
  ruleId?: string
  eventType?: string
  status?: NotificationLog['status']
  errorMessage?: string
}

const EVENT_TYPES = [
  'validation_failed',
  'validation_success',
  'drift_detected',
  'critical_issue',
  'scheduled_run',
  'high_priority_issue',
  'threshold_breach',
  'schema_change',
  'source_offline',
  'source_recovered',
]

// Event-specific message templates
const EVENT_MESSAGES: Record<string, () => string> = {
  validation_failed: () => `Validation failed for ${faker.commerce.productName()} - ${randomInt(1, 50)} issues detected`,
  validation_success: () => `Validation passed for ${faker.commerce.productName()} - All checks passed`,
  drift_detected: () => `Data drift detected in ${randomInt(1, 10)} columns - ${randomChoice(['Medium', 'High'])} severity`,
  critical_issue: () => `Critical issue: ${randomChoice(['Null constraint violation', 'Type mismatch', 'Referential integrity failure'])} in ${faker.database.column()}`,
  scheduled_run: () => `Scheduled validation completed for ${faker.commerce.productName()}`,
  high_priority_issue: () => `High priority: ${randomInt(5, 20)} issues found in ${faker.commerce.productName()}`,
  threshold_breach: () => `Threshold breached: ${randomChoice(['Success rate', 'Issue count', 'Duration'])} exceeded limit`,
  schema_change: () => `Schema change detected: ${randomInt(1, 5)} columns ${randomChoice(['added', 'removed', 'modified'])}`,
  source_offline: () => `Data source offline: ${faker.commerce.productName()} - Connection failed`,
  source_recovered: () => `Data source recovered: ${faker.commerce.productName()} - Connection restored`,
}

// Error messages for failed notifications
const ERROR_MESSAGES = [
  'Connection timeout after 30s',
  'HTTP 401 Unauthorized - Invalid credentials',
  'HTTP 403 Forbidden - Access denied',
  'HTTP 404 Not Found - Endpoint not found',
  'HTTP 429 Too Many Requests - Rate limited',
  'HTTP 500 Internal Server Error',
  'HTTP 502 Bad Gateway',
  'HTTP 503 Service Unavailable',
  'SSL Certificate verification failed',
  'DNS resolution failed',
  'Network unreachable',
  'Invalid JSON payload',
  'Message too large (>64KB)',
  'Channel not found',
  'User not found in workspace',
]

export function createNotificationLog(
  options: LogFactoryOptions = {}
): NotificationLog {
  const status = options.status ?? randomChoice(['sent', 'sent', 'sent', 'sent', 'failed', 'pending'] as const)
  const eventType = options.eventType ?? randomChoice(EVENT_TYPES)
  const messageGenerator = EVENT_MESSAGES[eventType] ?? (() => faker.lorem.sentence())

  const createdAt = createTimestamp(randomInt(0, 14))
  const sentDelay = randomInt(100, 5000) // ms delay for sending

  return {
    id: options.id ?? createId(),
    channel_id: options.channelId ?? createId(),
    rule_id: options.ruleId ?? (faker.datatype.boolean(0.8) ? createId() : undefined),
    event_type: eventType,
    status,
    message_preview: `[${eventType.toUpperCase().replace(/_/g, ' ')}] ${messageGenerator()}`,
    error_message: status === 'failed' ? (options.errorMessage ?? randomChoice(ERROR_MESSAGES)) : undefined,
    created_at: createdAt,
    sent_at: status === 'sent' ? new Date(new Date(createdAt).getTime() + sentDelay).toISOString() : undefined,
  }
}

export function createNotificationLogs(count: number): NotificationLog[] {
  return Array.from({ length: count }, () => createNotificationLog()).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

/**
 * Create notification logs with guaranteed coverage of all test scenarios
 */
export function createDiverseLogs(channelIds: string[], ruleIds?: string[]): NotificationLog[] {
  // Guard against empty channelIds
  if (!channelIds || channelIds.length === 0) {
    return []
  }

  const logs: NotificationLog[] = []
  const safeChannelId = (index: number) => channelIds[index % channelIds.length]
  const safeRuleId = (index: number) => ruleIds && ruleIds.length > 0 ? ruleIds[index % ruleIds.length] : undefined

  // 1. One log for each event type (sent)
  EVENT_TYPES.forEach((eventType) => {
    logs.push(createNotificationLog({
      channelId: safeChannelId(0),
      ruleId: safeRuleId(0),
      eventType,
      status: 'sent',
    }))
  })

  // 2. Failed logs with different error types
  ERROR_MESSAGES.slice(0, 8).forEach((errorMessage, i) => {
    logs.push(createNotificationLog({
      channelId: safeChannelId(i),
      status: 'failed',
      errorMessage,
    }))
  })

  // 3. Pending logs
  for (let i = 0; i < 5; i++) {
    logs.push(createNotificationLog({
      channelId: safeChannelId(i),
      status: 'pending',
    }))
  }

  // 4. Logs without rule (triggered manually or by system)
  for (let i = 0; i < 3; i++) {
    const log = createNotificationLog({
      channelId: safeChannelId(i),
      status: 'sent',
    })
    log.rule_id = undefined
    logs.push(log)
  }

  // 5. Multiple logs for same channel (to test filtering)
  for (let i = 0; i < 10; i++) {
    logs.push(createNotificationLog({
      channelId: safeChannelId(0),
      status: randomChoice(['sent', 'sent', 'sent', 'failed', 'pending'] as const),
    }))
  }

  // 6. Add more random logs for volume
  for (let i = 0; i < 50; i++) {
    logs.push(createNotificationLog({
      channelId: safeChannelId(i),
      ruleId: safeRuleId(i),
    }))
  }

  return logs.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

// ============================================================================
// Stats
// ============================================================================

export interface StatsFactoryOptions {
  hours?: number
  total?: number
  successRate?: number
}

export function createNotificationStats(options: StatsFactoryOptions = {}): NotificationStats {
  const hours = options.hours ?? 24
  // Ensure total is at least 1 to avoid division by zero
  const total = Math.max(1, options.total ?? randomInt(50, 500))
  const successRate = options.successRate ?? faker.number.float({ min: 0.7, max: 0.99 })

  const sent = Math.floor(total * successRate)
  const failed = Math.floor(total * (1 - successRate) * 0.8)
  // Ensure pending is never negative
  const pending = Math.max(0, total - sent - failed)

  // Distribute by channel proportionally
  const slackPct = faker.number.float({ min: 0.3, max: 0.5 })
  const emailPct = faker.number.float({ min: 0.2, max: 0.4 })
  const webhookPct = 1 - slackPct - emailPct

  return {
    period_hours: hours,
    total,
    by_status: { sent, failed, pending },
    by_channel: {
      slack: Math.floor(total * slackPct),
      email: Math.floor(total * emailPct),
      webhook: Math.floor(total * webhookPct),
    },
    success_rate: (sent / total) * 100,
  }
}

/**
 * Create notification stats for different scenarios
 */
export function createDiverseStats(): NotificationStats[] {
  return [
    // High success rate
    createNotificationStats({ hours: 24, total: 200, successRate: 0.98 }),
    // Medium success rate
    createNotificationStats({ hours: 24, total: 150, successRate: 0.85 }),
    // Low success rate (issue scenario)
    createNotificationStats({ hours: 24, total: 100, successRate: 0.65 }),
    // Very low volume
    createNotificationStats({ hours: 24, total: 10, successRate: 0.9 }),
    // High volume
    createNotificationStats({ hours: 24, total: 1000, successRate: 0.92 }),
    // Different time periods
    createNotificationStats({ hours: 1 }),
    createNotificationStats({ hours: 6 }),
    createNotificationStats({ hours: 12 }),
    createNotificationStats({ hours: 24 }),
    createNotificationStats({ hours: 168 }), // 1 week
  ]
}

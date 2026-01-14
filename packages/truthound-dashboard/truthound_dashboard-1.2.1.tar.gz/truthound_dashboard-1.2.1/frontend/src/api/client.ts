/**
 * API client for truthound-dashboard backend
 */

const API_BASE = '/api/v1'

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>
}

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`)
    this.name = 'ApiError'
  }
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...init } = options

  // Build URL with query params
  let url = `${API_BASE}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  // Set default headers
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(url, {
    ...init,
    headers,
  })

  if (!response.ok) {
    let data
    try {
      data = await response.json()
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiError(response.status, response.statusText, data)
  }

  // Handle empty responses
  const contentType = response.headers.get('Content-Type')
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T
  }

  return response.json()
}

// Health
export async function getHealth() {
  return request<{
    status: string
    version: string
    timestamp: string
  }>('/health')
}

// Sources
export interface Source {
  id: string
  name: string
  type: string
  config: Record<string, unknown>
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
  last_validated_at?: string
  has_schema: boolean
  latest_validation_status?: string
}

export interface SourceListResponse {
  success: boolean
  data: Source[]
  total: number
  offset: number
  limit: number
}

export async function listSources(params?: {
  offset?: number
  limit?: number
  active_only?: boolean
}): Promise<SourceListResponse> {
  return request<SourceListResponse>('/sources', { params })
}

export async function getSource(id: string): Promise<Source> {
  const response = await request<{ success: boolean; data: Source }>(`/sources/${id}`)
  return response.data
}

export async function createSource(data: {
  name: string
  type: string
  config: Record<string, unknown>
  description?: string
}): Promise<Source> {
  const response = await request<{ success: boolean; data: Source }>('/sources', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return response.data
}

export async function updateSource(
  id: string,
  data: {
    name?: string
    config?: Record<string, unknown>
    description?: string
    is_active?: boolean
  }
): Promise<Source> {
  const response = await request<{ success: boolean; data: Source }>(`/sources/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  return response.data
}

export async function deleteSource(id: string): Promise<{ message: string }> {
  return request<{ message: string }>(`/sources/${id}`, {
    method: 'DELETE',
  })
}

// Validations
export interface ValidationIssue {
  column: string
  issue_type: string
  count: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  details?: string
  expected?: unknown
  actual?: unknown
}

export interface Validation {
  id: string
  source_id: string
  status: 'pending' | 'running' | 'success' | 'failed' | 'error'
  passed: boolean
  has_critical: boolean
  has_high: boolean
  total_issues: number
  critical_issues: number
  high_issues: number
  medium_issues: number
  low_issues: number
  row_count?: number
  column_count?: number
  issues: ValidationIssue[]
  error_message?: string
  duration_ms?: number
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface ValidationListResponse {
  success: boolean
  data: Validation[]
  total: number
  limit: number
}

export async function runValidation(
  sourceId: string,
  data?: {
    validators?: string[]
    schema_path?: string
    auto_schema?: boolean
  }
): Promise<Validation> {
  const response = await request<{ success: boolean; data: Validation }>(`/validations/sources/${sourceId}/validate`, {
    method: 'POST',
    body: JSON.stringify(data || {}),
  })
  return response.data
}

export async function getValidation(id: string): Promise<Validation> {
  const response = await request<{ success: boolean; data: Validation }>(`/validations/${id}`)
  return response.data
}

export async function listSourceValidations(
  sourceId: string,
  params?: { limit?: number }
): Promise<ValidationListResponse> {
  return request<ValidationListResponse>(
    `/validations/sources/${sourceId}/validations`,
    { params }
  )
}

// Schemas
export interface Schema {
  id: string
  source_id: string
  schema_yaml: string
  schema_json?: Record<string, unknown>
  row_count?: number
  column_count?: number
  columns: string[]
  version?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export async function getSourceSchema(sourceId: string): Promise<Schema | null> {
  const response = await request<{ success: boolean; data: Schema | null }>(`/sources/${sourceId}/schema`)
  return response.data
}

export async function learnSchema(
  sourceId: string,
  data?: { infer_constraints?: boolean }
): Promise<Schema> {
  const response = await request<{ success: boolean; data: Schema }>(`/sources/${sourceId}/learn`, {
    method: 'POST',
    body: JSON.stringify(data || {}),
  })
  return response.data
}

export async function updateSchema(
  sourceId: string,
  schemaYaml: string
): Promise<Schema> {
  const response = await request<{ success: boolean; data: Schema }>(`/sources/${sourceId}/schema`, {
    method: 'PUT',
    body: JSON.stringify({ schema_yaml: schemaYaml }),
  })
  return response.data
}

// Profile
export interface ColumnProfile {
  name: string
  dtype: string
  null_pct: string
  unique_pct: string
  min?: unknown
  max?: unknown
  mean?: number
  std?: number
}

export interface ProfileResult {
  source: string
  row_count: number
  column_count: number
  size_bytes: number
  columns: ColumnProfile[]
}

export async function profileSource(sourceId: string): Promise<ProfileResult> {
  const response = await request<{ success: boolean; data: ProfileResult }>(`/sources/${sourceId}/profile`, {
    method: 'POST',
  })
  return response.data
}

// Test source connection
export async function testSourceConnection(
  sourceId: string
): Promise<{ success: boolean; data: { success: boolean; message?: string; error?: string } }> {
  return request(`/sources/${sourceId}/test`, { method: 'POST' })
}

// Get supported source types
export async function getSupportedSourceTypes(): Promise<{
  success: boolean
  data: {
    type: string
    name: string
    description: string
    required_fields: string[]
    optional_fields: string[]
  }[]
}> {
  return request('/sources/types/supported')
}

// History
export interface HistorySummary {
  total_runs: number
  passed_runs: number
  failed_runs: number
  success_rate: number
}

export interface TrendDataPoint {
  date: string
  success_rate: number
  run_count: number
  passed_count: number
  failed_count: number
}

export interface FailureFrequencyItem {
  issue: string
  count: number
}

export interface RecentValidation {
  id: string
  status: string
  passed: boolean
  has_critical: boolean
  has_high: boolean
  total_issues: number
  created_at: string
}

export interface HistoryResponse {
  success: boolean
  data: {
    summary: HistorySummary
    trend: TrendDataPoint[]
    failure_frequency: FailureFrequencyItem[]
    recent_validations: RecentValidation[]
  }
}

export async function getValidationHistory(
  sourceId: string,
  params?: {
    period?: '7d' | '30d' | '90d'
    granularity?: 'hourly' | 'daily' | 'weekly'
  }
): Promise<HistoryResponse> {
  return request<HistoryResponse>(`/sources/${sourceId}/history`, { params })
}

// Drift Detection
export interface DriftCompareRequest {
  baseline_source_id: string
  current_source_id: string
  columns?: string[]
  method?: 'auto' | 'ks' | 'psi' | 'chi2' | 'js'
  threshold?: number
  sample_size?: number
}

export interface ColumnDriftResult {
  column: string
  dtype: string
  drifted: boolean
  level: string
  method: string
  statistic?: number
  p_value?: number
  baseline_stats: Record<string, unknown>
  current_stats: Record<string, unknown>
}

export interface DriftResult {
  baseline_source: string
  current_source: string
  baseline_rows: number
  current_rows: number
  has_drift: boolean
  has_high_drift: boolean
  total_columns: number
  drifted_columns: string[]
  columns: ColumnDriftResult[]
}

export interface DriftComparison {
  id: string
  baseline_source_id: string
  current_source_id: string
  has_drift: boolean
  has_high_drift: boolean
  total_columns: number
  drifted_columns: number
  drift_percentage: number
  result?: DriftResult
  config?: Record<string, unknown>
  created_at: string
  updated_at?: string
}

export async function compareDrift(
  data: DriftCompareRequest
): Promise<{ success: boolean; data: DriftComparison }> {
  return request('/drift/compare', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listDriftComparisons(params?: {
  baseline_source_id?: string
  current_source_id?: string
  limit?: number
}): Promise<{ success: boolean; data: DriftComparison[]; total: number }> {
  return request('/drift/comparisons', { params })
}

export async function getDriftComparison(
  id: string
): Promise<{ success: boolean; data: DriftComparison }> {
  return request(`/drift/comparisons/${id}`)
}

// Schedules
export interface Schedule {
  id: string
  name: string
  source_id: string
  cron_expression: string
  is_active: boolean
  notify_on_failure: boolean
  last_run_at?: string
  next_run_at?: string
  config?: Record<string, unknown>
  created_at: string
  updated_at?: string
  source_name?: string
}

export interface ScheduleCreateRequest {
  source_id: string
  name: string
  cron_expression: string
  notify_on_failure?: boolean
  config?: Record<string, unknown>
}

export interface ScheduleUpdateRequest {
  name?: string
  cron_expression?: string
  notify_on_failure?: boolean
  config?: Record<string, unknown>
}

export async function listSchedules(params?: {
  source_id?: string
  active_only?: boolean
  limit?: number
}): Promise<{ success: boolean; data: Schedule[]; total: number }> {
  return request('/schedules', { params })
}

export async function createSchedule(
  data: ScheduleCreateRequest
): Promise<{ success: boolean; data: Schedule }> {
  return request('/schedules', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getSchedule(
  id: string
): Promise<{ success: boolean; data: Schedule }> {
  return request(`/schedules/${id}`)
}

export async function updateSchedule(
  id: string,
  data: ScheduleUpdateRequest
): Promise<{ success: boolean; data: Schedule }> {
  return request(`/schedules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteSchedule(
  id: string
): Promise<{ success: boolean; message: string }> {
  return request(`/schedules/${id}`, { method: 'DELETE' })
}

export async function pauseSchedule(
  id: string
): Promise<{ success: boolean; message: string; schedule: Schedule }> {
  return request(`/schedules/${id}/pause`, { method: 'POST' })
}

export async function resumeSchedule(
  id: string
): Promise<{ success: boolean; message: string; schedule: Schedule }> {
  return request(`/schedules/${id}/resume`, { method: 'POST' })
}

export async function runScheduleNow(
  id: string
): Promise<{ success: boolean; message: string; validation_id: string; passed: boolean }> {
  return request(`/schedules/${id}/run`, { method: 'POST' })
}

// ============================================================================
// Notifications (Phase 3)
// ============================================================================

export interface NotificationChannel {
  id: string
  name: string
  type: 'slack' | 'email' | 'webhook'
  is_active: boolean
  config_summary: string
  created_at: string
  updated_at: string
}

export interface NotificationRule {
  id: string
  name: string
  condition: string
  condition_config?: Record<string, unknown>
  channel_ids: string[]
  source_ids?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface NotificationLog {
  id: string
  channel_id: string
  rule_id?: string
  event_type: string
  status: 'pending' | 'sent' | 'failed'
  message_preview: string
  error_message?: string
  created_at: string
  sent_at?: string
}

export interface NotificationStats {
  period_hours: number
  total: number
  by_status: Record<string, number>
  by_channel: Record<string, number>
  success_rate: number
}

// Notification Channels
export async function listNotificationChannels(params?: {
  offset?: number
  limit?: number
  active_only?: boolean
  channel_type?: string
}): Promise<{ success: boolean; data: NotificationChannel[]; count: number }> {
  return request('/notifications/channels', { params })
}

export async function getNotificationChannel(
  id: string
): Promise<{ success: boolean; data: NotificationChannel }> {
  return request(`/notifications/channels/${id}`)
}

export async function createNotificationChannel(data: {
  name: string
  type: string
  config: Record<string, unknown>
  is_active?: boolean
}): Promise<{ success: boolean; data: NotificationChannel }> {
  return request('/notifications/channels', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateNotificationChannel(
  id: string,
  data: {
    name?: string
    config?: Record<string, unknown>
    is_active?: boolean
  }
): Promise<{ success: boolean; data: NotificationChannel }> {
  return request(`/notifications/channels/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteNotificationChannel(
  id: string
): Promise<{ success: boolean }> {
  return request(`/notifications/channels/${id}`, { method: 'DELETE' })
}

export async function testNotificationChannel(
  id: string
): Promise<{ success: boolean; message: string; error?: string }> {
  return request(`/notifications/channels/${id}/test`, { method: 'POST' })
}

export async function getNotificationChannelTypes(): Promise<{
  success: boolean
  data: Record<string, Record<string, unknown>>
}> {
  return request('/notifications/channels/types')
}

// Notification Rules
export async function listNotificationRules(params?: {
  offset?: number
  limit?: number
  active_only?: boolean
  condition?: string
}): Promise<{ success: boolean; data: NotificationRule[]; count: number }> {
  return request('/notifications/rules', { params })
}

export async function getNotificationRule(
  id: string
): Promise<{ success: boolean; data: NotificationRule }> {
  return request(`/notifications/rules/${id}`)
}

export async function createNotificationRule(data: {
  name: string
  condition: string
  channel_ids: string[]
  condition_config?: Record<string, unknown>
  source_ids?: string[]
  is_active?: boolean
}): Promise<{ success: boolean; data: NotificationRule }> {
  return request('/notifications/rules', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateNotificationRule(
  id: string,
  data: {
    name?: string
    condition?: string
    channel_ids?: string[]
    condition_config?: Record<string, unknown>
    source_ids?: string[]
    is_active?: boolean
  }
): Promise<{ success: boolean; data: NotificationRule }> {
  return request(`/notifications/rules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteNotificationRule(
  id: string
): Promise<{ success: boolean }> {
  return request(`/notifications/rules/${id}`, { method: 'DELETE' })
}

export async function getNotificationRuleConditions(): Promise<{
  success: boolean
  data: string[]
}> {
  return request('/notifications/rules/conditions')
}

// Notification Logs
export async function listNotificationLogs(params?: {
  offset?: number
  limit?: number
  channel_id?: string
  status?: string
  hours?: number
}): Promise<{ success: boolean; data: NotificationLog[]; count: number }> {
  return request('/notifications/logs', { params })
}

export async function getNotificationLog(
  id: string
): Promise<{ success: boolean; data: NotificationLog & { message: string; event_data?: unknown } }> {
  return request(`/notifications/logs/${id}`)
}

export async function getNotificationStats(params?: {
  hours?: number
}): Promise<{ success: boolean; data: NotificationStats }> {
  return request('/notifications/logs/stats', { params })
}

// ============================================================================
// Glossary (Phase 5)
// ============================================================================

export interface GlossaryCategory {
  id: string
  name: string
  description?: string
  parent_id?: string
  created_at: string
  updated_at: string
  children?: GlossaryCategory[]
}

export interface GlossaryTermSummary {
  id: string
  name: string
  definition: string
}

export interface GlossaryTerm {
  id: string
  name: string
  definition: string
  category_id?: string
  status: 'draft' | 'approved' | 'deprecated'
  owner_id?: string
  created_at: string
  updated_at: string
  category?: GlossaryCategory
  synonyms: GlossaryTermSummary[]
  related_terms: GlossaryTermSummary[]
}

export interface TermRelationship {
  id: string
  source_term_id: string
  target_term_id: string
  relationship_type: 'synonym' | 'related' | 'parent' | 'child'
  created_at: string
  source_term: GlossaryTermSummary
  target_term: GlossaryTermSummary
}

export interface TermHistory {
  id: string
  term_id: string
  field_name: string
  old_value?: string
  new_value?: string
  changed_by?: string
  changed_at: string
}

export interface TermCreate {
  name: string
  definition: string
  category_id?: string
  status?: 'draft' | 'approved' | 'deprecated'
  owner_id?: string
}

export interface TermUpdate {
  name?: string
  definition?: string
  category_id?: string
  status?: 'draft' | 'approved' | 'deprecated'
  owner_id?: string
}

export interface CategoryCreate {
  name: string
  description?: string
  parent_id?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
  parent_id?: string
}

export interface RelationshipCreate {
  source_term_id: string
  target_term_id: string
  relationship_type: 'synonym' | 'related' | 'parent' | 'child'
}

// Glossary Terms
export async function getTerms(params?: {
  search?: string
  category_id?: string
  status?: string
  skip?: number
  limit?: number
}): Promise<GlossaryTerm[]> {
  return request<GlossaryTerm[]>('/glossary/terms', { params })
}

export async function getTerm(id: string): Promise<GlossaryTerm> {
  return request<GlossaryTerm>(`/glossary/terms/${id}`)
}

export async function createTerm(data: TermCreate): Promise<GlossaryTerm> {
  return request<GlossaryTerm>('/glossary/terms', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateTerm(id: string, data: TermUpdate): Promise<GlossaryTerm> {
  return request<GlossaryTerm>(`/glossary/terms/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteTerm(id: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/glossary/terms/${id}`, { method: 'DELETE' })
}

export async function getTermHistory(id: string): Promise<TermHistory[]> {
  return request<TermHistory[]>(`/glossary/terms/${id}/history`)
}

export async function getTermRelationships(id: string): Promise<TermRelationship[]> {
  return request<TermRelationship[]>(`/glossary/terms/${id}/relationships`)
}

// Glossary Categories
export async function getCategories(): Promise<GlossaryCategory[]> {
  return request<GlossaryCategory[]>('/glossary/categories')
}

export async function createCategory(data: CategoryCreate): Promise<GlossaryCategory> {
  return request<GlossaryCategory>('/glossary/categories', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateCategory(id: string, data: CategoryUpdate): Promise<GlossaryCategory> {
  return request<GlossaryCategory>(`/glossary/categories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteCategory(id: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/glossary/categories/${id}`, { method: 'DELETE' })
}

// Glossary Relationships
export async function createRelationship(data: RelationshipCreate): Promise<TermRelationship> {
  return request<TermRelationship>('/glossary/relationships', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteRelationship(id: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/glossary/relationships/${id}`, { method: 'DELETE' })
}

// ============================================================================
// Catalog (Phase 5)
// ============================================================================

export type AssetType = 'table' | 'file' | 'api'
export type SensitivityLevel = 'public' | 'internal' | 'confidential' | 'restricted'

export interface AssetTag {
  id: string
  asset_id: string
  tag_name: string
  tag_value?: string
  created_at: string
}

export interface AssetColumn {
  id: string
  asset_id: string
  name: string
  data_type?: string
  description?: string
  is_nullable: boolean
  is_primary_key: boolean
  term_id?: string
  sensitivity_level?: SensitivityLevel
  created_at: string
  term?: GlossaryTermSummary
}

export interface SourceSummary {
  id: string
  name: string
  type: string
}

export interface CatalogAsset {
  id: string
  name: string
  asset_type: AssetType
  source_id?: string
  description?: string
  owner_id?: string
  quality_score?: number
  created_at: string
  updated_at: string
  source?: SourceSummary
  columns: AssetColumn[]
  tags: AssetTag[]
}

export interface AssetListItem {
  id: string
  name: string
  asset_type: AssetType
  source_id?: string
  source_name?: string
  quality_score?: number
  tag_count: number
  column_count: number
  updated_at: string
}

export interface AssetCreate {
  name: string
  asset_type: AssetType
  source_id?: string
  description?: string
  owner_id?: string
}

export interface AssetUpdate {
  name?: string
  asset_type?: AssetType
  source_id?: string
  description?: string
  owner_id?: string
  quality_score?: number
}

export interface ColumnCreate {
  name: string
  data_type?: string
  description?: string
  is_nullable?: boolean
  is_primary_key?: boolean
  sensitivity_level?: SensitivityLevel
}

export interface ColumnUpdate {
  name?: string
  data_type?: string
  description?: string
  is_nullable?: boolean
  is_primary_key?: boolean
  sensitivity_level?: SensitivityLevel
}

export interface TagCreate {
  tag_name: string
  tag_value?: string
}

// Catalog Assets
export async function getAssets(params?: {
  search?: string
  asset_type?: string
  source_id?: string
  skip?: number
  limit?: number
}): Promise<AssetListItem[]> {
  return request<AssetListItem[]>('/catalog/assets', { params })
}

export async function getAsset(id: string): Promise<CatalogAsset> {
  return request<CatalogAsset>(`/catalog/assets/${id}`)
}

export async function createAsset(data: AssetCreate): Promise<CatalogAsset> {
  return request<CatalogAsset>('/catalog/assets', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateAsset(id: string, data: AssetUpdate): Promise<CatalogAsset> {
  return request<CatalogAsset>(`/catalog/assets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteAsset(id: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/catalog/assets/${id}`, { method: 'DELETE' })
}

// Asset Columns
export async function getAssetColumns(assetId: string): Promise<AssetColumn[]> {
  return request<AssetColumn[]>(`/catalog/assets/${assetId}/columns`)
}

export async function createColumn(assetId: string, data: ColumnCreate): Promise<AssetColumn> {
  return request<AssetColumn>(`/catalog/assets/${assetId}/columns`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateColumn(columnId: string, data: ColumnUpdate): Promise<AssetColumn> {
  return request<AssetColumn>(`/catalog/columns/${columnId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteColumn(columnId: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/catalog/columns/${columnId}`, { method: 'DELETE' })
}

export async function mapColumnToTerm(columnId: string, termId: string): Promise<AssetColumn> {
  return request<AssetColumn>(`/catalog/columns/${columnId}/term`, {
    method: 'PUT',
    body: JSON.stringify({ term_id: termId }),
  })
}

export async function unmapColumnFromTerm(columnId: string): Promise<AssetColumn> {
  return request<AssetColumn>(`/catalog/columns/${columnId}/term`, { method: 'DELETE' })
}

// Asset Tags
export async function getAssetTags(assetId: string): Promise<AssetTag[]> {
  return request<AssetTag[]>(`/catalog/assets/${assetId}/tags`)
}

export async function addTag(assetId: string, data: TagCreate): Promise<AssetTag> {
  return request<AssetTag>(`/catalog/assets/${assetId}/tags`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function removeTag(tagId: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/catalog/tags/${tagId}`, { method: 'DELETE' })
}

// ============================================================================
// Collaboration (Phase 5)
// ============================================================================

export type ResourceType = 'term' | 'asset' | 'column'
export type ActivityAction = 'created' | 'updated' | 'deleted' | 'commented'

export interface Comment {
  id: string
  resource_type: ResourceType
  resource_id: string
  content: string
  author_id?: string
  parent_id?: string
  created_at: string
  updated_at: string
  replies: Comment[]
}

export interface Activity {
  id: string
  resource_type: string
  resource_id: string
  action: ActivityAction
  actor_id?: string
  description?: string
  metadata?: Record<string, unknown>
  created_at: string
}

export interface CommentCreate {
  resource_type: ResourceType
  resource_id: string
  content: string
  author_id?: string
  parent_id?: string
}

export interface CommentUpdate {
  content: string
}

// Comments
export async function getComments(
  resourceType: ResourceType,
  resourceId: string
): Promise<Comment[]> {
  return request<Comment[]>('/comments', {
    params: { resource_type: resourceType, resource_id: resourceId },
  })
}

export async function createComment(data: CommentCreate): Promise<Comment> {
  return request<Comment>('/comments', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateComment(id: string, data: CommentUpdate): Promise<Comment> {
  return request<Comment>(`/comments/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteComment(id: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/comments/${id}`, { method: 'DELETE' })
}

// Activities
export async function getActivities(params?: {
  resource_type?: string
  resource_id?: string
  skip?: number
  limit?: number
}): Promise<Activity[]> {
  return request<Activity[]>('/activities', { params })
}

// API client helper for direct requests
export const apiClient = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
}

export { ApiError }

# API Reference

This document describes the Truthound Dashboard REST API.

## Base URL

```
http://localhost:8765/api/v1
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### Pagination Response

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

## Health

### GET /health

Check server status.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.1"
}
```

---

## Sources

### GET /sources

Retrieve all data sources.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "abc123",
      "name": "Sales Data",
      "type": "file",
      "config": { "path": "/data/sales.csv" },
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /sources

Create a new data source.

**Request:**
```json
{
  "name": "Sales Data",
  "type": "file",
  "config": {
    "path": "/data/sales.csv"
  }
}
```

**Source Types:**
- `file` - Local file (CSV, Parquet)
- `postgresql` - PostgreSQL
- `mysql` - MySQL
- `snowflake` - Snowflake
- `bigquery` - BigQuery

**Config by Type:**

**File:**
```json
{
  "path": "/path/to/file.csv"
}
```

**PostgreSQL / MySQL:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "password",
  "table": "my_table",
  "schema": "public"
}
```

**Snowflake:**
```json
{
  "account": "abc123.us-east-1",
  "warehouse": "COMPUTE_WH",
  "database": "MY_DB",
  "schema": "PUBLIC",
  "table": "MY_TABLE",
  "username": "user",
  "password": "password"
}
```

**BigQuery:**
```json
{
  "project": "my-project",
  "dataset": "my_dataset",
  "table": "my_table",
  "credentials_json": "{...}"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "name": "Sales Data",
    "type": "file",
    "config": { "path": "/data/sales.csv" },
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### GET /sources/{id}

Retrieve a specific source.

### PUT /sources/{id}

Update source information.

**Request:**
```json
{
  "name": "Updated Name",
  "config": { "path": "/new/path.csv" }
}
```

### DELETE /sources/{id}

Delete a source.

### POST /sources/{id}/test

Test source connection.

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "row_count": 10000,
  "column_count": 15
}
```

---

## Schema

### GET /sources/{id}/schema

Retrieve the learned schema for a source.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "schema123",
    "source_id": "abc123",
    "schema_yaml": "columns:\n  order_id:\n    dtype: int64\n    nullable: false\n    unique: true",
    "schema_json": {
      "columns": {
        "order_id": {
          "dtype": "int64",
          "nullable": false,
          "unique": true
        }
      }
    },
    "row_count": 10000,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### PUT /sources/{id}/schema

Save schema (manual edit).

**Request:**
```json
{
  "schema_yaml": "columns:\n  order_id:\n    dtype: int64\n    nullable: false"
}
```

### POST /sources/{id}/learn

Generate schema automatically (th.learn).

Analyzes data to automatically generate a schema.

**Response:**
```json
{
  "success": true,
  "data": {
    "columns": {
      "order_id": {
        "name": "order_id",
        "dtype": "int64",
        "nullable": false,
        "unique": true,
        "min_value": 1,
        "max_value": 99999
      },
      "status": {
        "name": "status",
        "dtype": "object",
        "nullable": false,
        "unique": false,
        "allowed_values": ["pending", "completed", "cancelled"]
      }
    },
    "row_count": 10000,
    "version": "1.0.0"
  }
}
```

---

## Validations

### POST /sources/{id}/validate

Run validation (th.check).

**Request:**
```json
{
  "validators": ["not_null", "unique", "dtype"],
  "schema_path": "/path/to/schema.yaml",
  "auto_schema": false
}
```

**Parameters:**
- `validators` (optional): List of validators to run
- `schema_path` (optional): Path to schema file
- `auto_schema` (optional): If true, auto-generate schema before validation

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "val123",
    "source_id": "abc123",
    "status": "success",
    "passed": false,
    "has_critical": true,
    "has_high": false,
    "total_issues": 3,
    "critical_issues": 1,
    "high_issues": 0,
    "row_count": 10000,
    "column_count": 15,
    "issues": [
      {
        "column": "email",
        "issue_type": "null_values",
        "count": 150,
        "severity": "critical",
        "details": "150 null values found in non-nullable column",
        "expected": "no null values",
        "actual": "150 null values (1.5%)"
      }
    ],
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:30:05Z"
  }
}
```

### GET /validations/{id}

Retrieve validation result details.

### GET /sources/{id}/validations

Retrieve validation history for a source.

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)
- `status` (optional): "success", "failed", "error"

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "val123",
      "status": "success",
      "passed": true,
      "total_issues": 0,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "total_pages": 3
  }
}
```

---

## Profile

### POST /sources/{id}/profile

Run data profiling (th.profile).

**Response:**
```json
{
  "success": true,
  "data": {
    "source": "sales.csv",
    "row_count": 10000,
    "column_count": 15,
    "size_bytes": 1048576,
    "columns": [
      {
        "name": "order_id",
        "dtype": "int64",
        "null_count": 0,
        "null_percentage": 0.0,
        "unique_count": 10000,
        "unique_percentage": 100.0,
        "min": 1,
        "max": 10000,
        "mean": 5000.5,
        "std": 2886.89
      },
      {
        "name": "status",
        "dtype": "object",
        "null_count": 0,
        "null_percentage": 0.0,
        "unique_count": 3,
        "unique_percentage": 0.03,
        "top_values": [
          { "value": "completed", "count": 7500, "percentage": 75.0 },
          { "value": "pending", "count": 2000, "percentage": 20.0 },
          { "value": "cancelled", "count": 500, "percentage": 5.0 }
        ]
      }
    ]
  }
}
```

### GET /sources/{id}/profile

Retrieve the most recent profile result.

---

## Drift Detection

### POST /drift/compare

Compare two datasets (th.compare).

**Request:**
```json
{
  "source_id": "abc123",
  "target_id": "def456"
}
```

Or:
```json
{
  "source_path": "/data/v1.csv",
  "target_path": "/data/v2.csv"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "drift123",
    "has_drift": true,
    "has_high_drift": false,
    "drifted_columns": ["price", "quantity"],
    "columns": [
      {
        "name": "order_id",
        "has_drift": false,
        "drift_score": 0.02
      },
      {
        "name": "price",
        "has_drift": true,
        "drift_score": 0.45,
        "drift_type": "distribution_shift",
        "source_stats": { "mean": 100.5, "std": 25.3 },
        "target_stats": { "mean": 145.2, "std": 32.1 }
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### GET /drift/{id}

Retrieve drift comparison result.

---

## Schedules

### GET /schedules

Retrieve all schedules.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "sched123",
      "name": "Daily Sales Check",
      "source_id": "abc123",
      "cron_expression": "0 9 * * *",
      "is_active": true,
      "notify_on_failure": true,
      "last_run_at": "2024-01-15T09:00:00Z",
      "next_run_at": "2024-01-16T09:00:00Z",
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

### POST /schedules

Create a new schedule.

**Request:**
```json
{
  "name": "Daily Sales Check",
  "source_id": "abc123",
  "cron_expression": "0 9 * * *",
  "notify_on_failure": true
}
```

**Cron Expression Examples:**
- `0 9 * * *` - Daily at 9 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight
- `0 0 1 * *` - First day of each month at midnight

### GET /schedules/{id}

Retrieve schedule details.

### PUT /schedules/{id}

Update a schedule.

### DELETE /schedules/{id}

Delete a schedule.

### POST /schedules/{id}/pause

Pause a schedule.

### POST /schedules/{id}/resume

Resume a schedule.

### POST /schedules/{id}/run

Run a schedule immediately.

---

## Notifications

### GET /notifications/channels

Retrieve notification channels.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "ch123",
      "name": "Dev Team Slack",
      "type": "slack",
      "is_active": true,
      "config_summary": "Webhook: ...abcdef",
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

### POST /notifications/channels

Create a new notification channel.

**Slack Channel:**
```json
{
  "name": "Dev Team Slack",
  "type": "slack",
  "config": {
    "webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"
  }
}
```

**Email Channel:**
```json
{
  "name": "Team Email",
  "type": "email",
  "config": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "user@gmail.com",
    "smtp_password": "app-password",
    "from_email": "alerts@company.com",
    "recipients": ["team@company.com", "lead@company.com"],
    "use_tls": true
  }
}
```

**Webhook Channel:**
```json
{
  "name": "Custom Webhook",
  "type": "webhook",
  "config": {
    "url": "https://api.example.com/webhook",
    "headers": {
      "Authorization": "Bearer token123"
    }
  }
}
```

### DELETE /notifications/channels/{id}

Delete a channel.

### POST /notifications/channels/{id}/test

Send a test notification.

**Response:**
```json
{
  "success": true,
  "message": "Test sent"
}
```

### GET /notifications/rules

Retrieve notification rules.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "rule123",
      "name": "Alert on Critical Issues",
      "condition": "validation_failed",
      "condition_value": null,
      "channel_ids": ["ch123", "ch456"],
      "is_active": true,
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

### POST /notifications/rules

Create a new notification rule.

**Request:**
```json
{
  "name": "Alert on Critical Issues",
  "condition": "validation_failed",
  "condition_value": null,
  "channel_ids": ["ch123"]
}
```

**Condition Types:**
- `validation_failed` - When validation fails
- `critical_issues` - When critical severity issues occur
- `high_issues` - When high severity issues occur
- `schedule_failed` - When scheduled execution fails

### DELETE /notifications/rules/{id}

Delete a rule.

### GET /notifications/logs

Retrieve notification delivery logs.

**Query Parameters:**
- `limit` (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "log123",
      "channel_id": "ch123",
      "status": "sent",
      "message": "Validation Failed: Sales Data...",
      "error": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## Business Glossary

### GET /glossary/terms

Retrieve glossary terms.

**Query Parameters:**
- `search` (optional): Search term names and definitions
- `category_id` (optional): Filter by category
- `status` (optional): Filter by status (`draft`, `approved`, `deprecated`)
- `page` (default: 1)
- `per_page` (default: 20)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "term123",
      "name": "Customer",
      "definition": "An individual or organization that purchases products",
      "category_id": "cat123",
      "category_name": "Business",
      "status": "approved",
      "owner": "data-team",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /glossary/terms

Create a new term.

**Request:**
```json
{
  "name": "Customer",
  "definition": "An individual or organization that purchases products",
  "category_id": "cat123",
  "status": "draft",
  "owner": "data-team"
}
```

### GET /glossary/terms/{id}

Retrieve term details including relationships.

### PUT /glossary/terms/{id}

Update a term. Changes are automatically tracked in history.

### DELETE /glossary/terms/{id}

Delete a term.

### GET /glossary/terms/{id}/history

Retrieve term change history.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "hist123",
      "term_id": "term123",
      "field_name": "definition",
      "old_value": "Previous definition",
      "new_value": "Updated definition",
      "changed_by": "user@example.com",
      "changed_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### GET /glossary/terms/{id}/relationships

Retrieve term relationships.

### GET /glossary/categories

Retrieve all categories.

### POST /glossary/categories

Create a new category.

**Request:**
```json
{
  "name": "Business",
  "description": "Business-related terms",
  "parent_id": null
}
```

### PUT /glossary/categories/{id}

Update a category.

### DELETE /glossary/categories/{id}

Delete a category.

### POST /glossary/relationships

Create a relationship between terms.

**Request:**
```json
{
  "source_term_id": "term123",
  "target_term_id": "term456",
  "relationship_type": "synonym"
}
```

**Relationship Types:**
- `synonym` - Terms with the same meaning
- `related` - Related terms

### DELETE /glossary/relationships/{id}

Delete a relationship.

---

## Data Catalog

### GET /catalog/assets

Retrieve data assets.

**Query Parameters:**
- `search` (optional): Search asset names and descriptions
- `asset_type` (optional): Filter by type (`table`, `file`, `api`)
- `source_id` (optional): Filter by data source
- `page` (default: 1)
- `per_page` (default: 20)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "asset123",
      "name": "customers",
      "asset_type": "table",
      "description": "Customer master data",
      "source_id": "src123",
      "source_name": "Production DB",
      "owner": "data-team",
      "quality_score": 85,
      "column_count": 12,
      "tag_count": 3,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /catalog/assets

Create a new asset.

**Request:**
```json
{
  "name": "customers",
  "asset_type": "table",
  "description": "Customer master data",
  "source_id": "src123",
  "owner": "data-team",
  "quality_score": 85
}
```

### GET /catalog/assets/{id}

Retrieve asset details including columns and tags.

### PUT /catalog/assets/{id}

Update an asset.

### DELETE /catalog/assets/{id}

Delete an asset.

### GET /catalog/assets/{id}/columns

Retrieve asset columns.

### POST /catalog/assets/{id}/columns

Add a column to an asset.

**Request:**
```json
{
  "name": "customer_id",
  "data_type": "integer",
  "description": "Unique customer identifier",
  "is_nullable": false,
  "is_primary_key": true,
  "sensitivity_level": "internal"
}
```

**Sensitivity Levels:**
- `public` - No restrictions
- `internal` - Internal use only
- `confidential` - Restricted access
- `restricted` - Highly sensitive

### PUT /catalog/columns/{id}

Update a column.

### DELETE /catalog/columns/{id}

Delete a column.

### PUT /catalog/columns/{id}/term

Map a column to a glossary term.

**Request:**
```json
{
  "term_id": "term123"
}
```

### DELETE /catalog/columns/{id}/term

Remove column-term mapping.

### GET /catalog/assets/{id}/tags

Retrieve asset tags.

### POST /catalog/assets/{id}/tags

Add a tag to an asset.

**Request:**
```json
{
  "tag_name": "domain",
  "tag_value": "sales"
}
```

### DELETE /catalog/tags/{id}

Delete a tag.

---

## Collaboration

### GET /comments

Retrieve comments for a resource.

**Query Parameters:**
- `resource_type` (required): `term`, `asset`, or `column`
- `resource_id` (required): ID of the resource

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "cmt123",
      "resource_type": "term",
      "resource_id": "term123",
      "content": "This definition needs clarification",
      "author": "user@example.com",
      "parent_id": null,
      "replies": [],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /comments

Create a comment.

**Request:**
```json
{
  "resource_type": "term",
  "resource_id": "term123",
  "content": "This definition needs clarification",
  "author": "user@example.com",
  "parent_id": null
}
```

### PUT /comments/{id}

Update a comment.

### DELETE /comments/{id}

Delete a comment.

### GET /activities

Retrieve activity feed.

**Query Parameters:**
- `resource_type` (optional): Filter by resource type
- `resource_id` (optional): Filter by resource ID
- `limit` (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "act123",
      "resource_type": "term",
      "resource_id": "term123",
      "action": "updated",
      "actor": "user@example.com",
      "description": "Updated term definition",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Action Types:**
- `created` - Resource created
- `updated` - Resource updated
- `deleted` - Resource deleted
- `commented` - Comment added

---

## Error Codes

| Code | Description |
|------|-------------|
| `SOURCE_NOT_FOUND` | Data source not found |
| `VALIDATION_ERROR` | Error during validation execution |
| `CONNECTION_ERROR` | Database connection failed |
| `SCHEDULE_ERROR` | Scheduled task failed |
| `NOTIFICATION_ERROR` | Notification delivery failed |
| `RATE_LIMIT_EXCEEDED` | Request limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

---

## Rate Limiting

By default, requests are limited to 120 per minute.

When rate limit is exceeded:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later."
  }
}
```

---

## Authentication (Optional)

When authentication is enabled, all API requests require Basic Auth headers:

```bash
curl -u :password http://localhost:8765/api/v1/health
```

Enable authentication via environment variables:
```bash
TRUTHOUND_AUTH_ENABLED=true
TRUTHOUND_AUTH_PASSWORD=your-secret-password
```

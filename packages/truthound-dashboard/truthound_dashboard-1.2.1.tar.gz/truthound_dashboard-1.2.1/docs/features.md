# Features

This document provides detailed descriptions of all Truthound Dashboard features.

## Data Sources

Connect and manage various data sources.

### Supported Source Types

| Type | Description | Config Fields |
|------|-------------|---------------|
| **File** | Local CSV, Parquet files | `path` |
| **PostgreSQL** | PostgreSQL database | `host`, `port`, `database`, `username`, `password`, `table` |
| **MySQL** | MySQL database | `host`, `port`, `database`, `username`, `password`, `table` |
| **Snowflake** | Snowflake data warehouse | `account`, `warehouse`, `database`, `schema`, `table` |
| **BigQuery** | Google BigQuery | `project`, `dataset`, `table`, `credentials_json` |

### Source Management

- **CRUD Operations**: Add, update, and delete data sources
- **Connection Testing**: Verify source connectivity
- **Table Listing**: Browse database tables
- **Activation Control**: Enable or disable sources

---

## Schema Management

Automatically learn or manually edit data schemas.

### Auto Schema Generation (th.learn)

Analyze data to automatically generate schemas using `th.learn`.

**Information Captured:**
- Column names and data types
- Nullable status (when null values exist)
- Unique constraints (when all values are unique)
- Numeric columns: min and max values
- String columns: allowed values for low-cardinality fields

**Example Output:**
```yaml
columns:
  order_id:
    dtype: int64
    nullable: false
    unique: true
    min_value: 1
    max_value: 99999

  status:
    dtype: object
    nullable: false
    allowed_values:
      - pending
      - completed
      - cancelled

  amount:
    dtype: float64
    nullable: true
    min_value: 0.0
    max_value: 10000.0
```

### Manual Schema Editing

Edit schemas directly in YAML format through the UI.

**Editable Properties:**
- `dtype`: Data type (int64, float64, object, datetime64, bool)
- `nullable`: Allow null values
- `unique`: Enforce unique values
- `min_value` / `max_value`: Numeric range
- `allowed_values`: List of allowed values
- `regex`: Regular expression pattern

---

## Validation

Execute data quality validations and review results.

### Validators

Validators provided by truthound:

| Validator | Description |
|-----------|-------------|
| `not_null` | Check for null values |
| `unique` | Check for duplicate values |
| `dtype` | Verify data types |
| `in_range` | Validate numeric ranges |
| `in_set` | Validate against allowed values |
| `regex` | Pattern matching |

### Validation Result

Validation results include:

```json
{
  "passed": false,
  "has_critical": true,
  "has_high": false,
  "total_issues": 3,
  "issues": [
    {
      "column": "email",
      "issue_type": "null_values",
      "count": 150,
      "severity": "critical",
      "details": "150 null values found",
      "expected": "no null values",
      "actual": "150 null values (1.5%)"
    }
  ]
}
```

### Issue Severity

| Severity | Description |
|----------|-------------|
| **Critical** | Requires immediate attention (e.g., null in required column) |
| **High** | Significant data quality issue |
| **Medium** | Issue requiring attention |
| **Low** | Minor issue |

---

## Validation History

Track data quality changes over time.

### Features

- **Trend Charts**: Visualize validation results
- **Failure Analysis**: Identify frequently failing validations
- **Filtering**: Filter by status and date range
- **Detail View**: Examine individual validation results

### Use Cases

1. **Quality Monitoring**: Track data quality trends
2. **Issue Tracking**: Analyze causes of quality degradation
3. **Reporting**: Generate periodic quality reports

---

## Data Profiling

Analyze statistical characteristics of data.

### Profile Information

**Overall Statistics:**
- Row count
- Column count
- File size (bytes)

**Per-Column Statistics:**
- Null count and percentage
- Unique value count and percentage
- Numeric: min, max, mean, std
- String: Top N values and frequencies

### Visualization

- Data type distribution charts
- Null percentage heatmap
- Numeric column distributions
- Categorical value frequencies

---

## Drift Detection

Compare two datasets to detect changes.

### Use Cases

1. **Version Comparison**: Compare yesterday vs. today data
2. **Environment Comparison**: Production vs. Staging
3. **Model Monitoring**: Training vs. Serving data

### Drift Types

| Type | Description |
|------|-------------|
| **Schema Drift** | Column additions, deletions, or type changes |
| **Distribution Drift** | Value distribution changes |
| **Volume Drift** | Row count changes |

### Comparison Result

```json
{
  "has_drift": true,
  "has_high_drift": false,
  "drifted_columns": ["price", "quantity"],
  "columns": [
    {
      "name": "price",
      "has_drift": true,
      "drift_score": 0.45,
      "drift_type": "distribution_shift",
      "source_stats": { "mean": 100.5 },
      "target_stats": { "mean": 145.2 }
    }
  ]
}
```

---

## Scheduled Validations

Configure automated validation runs using cron expressions.

### Cron Expression

Standard cron expression format:

```
minute hour day month weekday
*      *    *   *     *
```

**Examples:**
| Expression | Description |
|------------|-------------|
| `0 9 * * *` | Daily at 9 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 1` | Every Monday at midnight |
| `0 0 1 * *` | First day of each month |
| `*/30 * * * *` | Every 30 minutes |

### Schedule Management

- **Create**: Add new schedules
- **Update**: Modify schedule settings
- **Delete**: Remove schedules
- **Pause/Resume**: Toggle schedule activation
- **Run Now**: Execute immediately

### Failure Notification

Receive notifications via configured channels when scheduled validations fail.

---

## Notifications

Receive alerts through various channels when validations fail.

### Supported Channels

#### Slack

Send notifications to Slack channels via webhook URL.

**Configuration:**
```json
{
  "webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"
}
```

**Message Format:**
```
Validation Failed

Source: Sales Data
Severity: Critical
Total Issues: 3
Validation ID: val123
```

#### Email

Send email notifications via SMTP.

**Configuration:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "user@gmail.com",
  "smtp_password": "app-password",
  "from_email": "alerts@company.com",
  "recipients": ["team@company.com"],
  "use_tls": true
}
```

#### Webhook

Send JSON payloads to custom HTTP endpoints.

**Configuration:**
```json
{
  "url": "https://api.example.com/webhook",
  "headers": {
    "Authorization": "Bearer token"
  }
}
```

**Payload Format:**
```json
{
  "event": "validation_failed",
  "source": "Sales Data",
  "has_critical": true,
  "has_high": false,
  "total_issues": 3,
  "validation_id": "val123"
}
```

### Notification Rules

Configure rules to trigger notifications based on conditions.

| Condition | Description |
|-----------|-------------|
| `validation_failed` | When validation fails |
| `critical_issues` | When critical issues occur |
| `high_issues` | When high severity issues occur |
| `schedule_failed` | When scheduled execution fails |

---

## Business Glossary

Manage business terminology with definitions, categories, and relationships.

### Term Management

- **CRUD Operations**: Create, read, update, and delete business terms
- **Categories**: Organize terms into hierarchical categories
- **Status Tracking**: Track term lifecycle (draft, approved, deprecated)
- **Change History**: Automatic tracking of all term modifications

### Term Relationships

Define connections between terms:

| Relationship Type | Description |
|-------------------|-------------|
| **Synonym** | Terms with the same meaning |
| **Related** | Terms that are conceptually related |

### Search and Filter

- Full-text search across term names and definitions
- Filter by category
- Filter by status

---

## Data Catalog

Register and manage data assets with metadata.

### Asset Types

| Type | Description |
|------|-------------|
| **Table** | Database tables |
| **File** | Data files (CSV, Parquet, etc.) |
| **API** | API endpoints |

### Asset Management

- **Registration**: Register data assets with descriptions
- **Source Linking**: Link assets to data sources
- **Quality Score**: Track data quality (0-100 scale)
- **Ownership**: Assign asset owners

### Column Metadata

Manage column-level information:

- Column name and data type
- Description
- Nullable and primary key flags
- Term mapping (link columns to glossary terms)
- Sensitivity classification

### Sensitivity Levels

| Level | Description |
|-------|-------------|
| **Public** | No restrictions |
| **Internal** | Internal use only |
| **Confidential** | Restricted access |
| **Restricted** | Highly sensitive data |

### Tagging

Apply custom tags to assets for flexible categorization.

---

## Collaboration

Enable team collaboration on data assets.

### Comments

- Add comments to terms, assets, and columns
- Threaded replies for discussions
- Edit and delete own comments

### Activity Feed

Track all changes across the system:

- Term creation, updates, and deletion
- Asset modifications
- Comment activity
- Column-term mappings

---

## UI Features

### Dark Mode

Select theme manually or follow system settings.

- Light Mode
- Dark Mode
- System (automatic)

### Internationalization (i18n)

Multiple languages supported:

- English (en)
- Korean (ko)

Language is auto-detected from browser settings or can be changed manually.

### Responsive Design

Optimized for various screen sizes:

- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (< 768px)

---

## Security Features

### Connection Encryption

Database connection credentials (passwords, etc.) are encrypted at rest.

- Fernet symmetric encryption
- Device-specific keys auto-generated
- Automatic detection and encryption of sensitive fields

### Rate Limiting

API requests are limited to 120 per minute by default.

### Security Headers

All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### Optional Authentication

Enable password protection when needed.

---

## Performance

### Large Dataset Handling

Large datasets are automatically sampled:
- Files over 100MB: automatic sampling
- Default sample size: 100,000 rows
- Configurable via settings

### Caching

Frequently accessed data is cached:
- Source list: 30-second TTL
- Profile results: 5-minute TTL

### Database Maintenance

Automatic cleanup tasks are scheduled:
- Delete validation results older than 90 days
- Delete notification logs older than 30 days
- Weekly VACUUM execution

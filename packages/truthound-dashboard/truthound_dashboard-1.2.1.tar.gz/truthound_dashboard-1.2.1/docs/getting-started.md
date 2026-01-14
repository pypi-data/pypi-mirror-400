# Getting Started

This guide describes how to install Truthound Dashboard and run your first data validation.

## Requirements

- Python 3.11 or higher
- pip (Python package manager)

## Installation

### Install from PyPI (Recommended)

```bash
pip install truthound-dashboard
```

This command automatically installs [truthound](https://github.com/seadonggyun4/truthound) as a dependency.

### Install Development Version

```bash
git clone https://github.com/seadonggyun4/truthound-dashboard
cd truthound-dashboard
pip install -e ".[dev]"
```

## Quick Start

### 1. Start the Dashboard

```bash
truthound serve
```

The browser opens automatically and the dashboard is accessible at `http://localhost:8765`.

### 2. Add a Data Source

1. Click **Data Sources** in the left menu
2. Click the **Add Source** button
3. Enter source information:
   - **Name**: Source name (e.g., "Sales Data")
   - **Type**: Select file or database type
   - **Config**: Enter connection details

**File Source Example:**
```json
{
  "path": "/path/to/your/data.csv"
}
```

**PostgreSQL Example:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "password",
  "table": "sales"
}
```

### 3. Generate Schema Automatically

1. Click the **Schema** tab for the created source
2. Click the **Learn Schema** button
3. The schema is generated automatically by analyzing the data

The generated schema includes:
- Column data types
- Nullable status
- Unique constraints
- Min/max values for numeric columns
- Allowed values for low-cardinality columns

### 4. Run Validation

1. Click the **Validate** button on the source detail page
2. Review the results after validation completes

**Validation Result Fields:**
- **passed**: Whether validation passed
- **total_issues**: Total number of issues found
- **has_critical**: Whether critical severity issues exist
- **has_high**: Whether high severity issues exist
- **issues**: Detailed issue list

### 5. Configure Schedules (Optional)

To run validations periodically:

1. Navigate to the **Schedules** menu
2. Click **Add Schedule**
3. Set the schedule using a cron expression

**Cron Expression Examples:**
- `0 9 * * *` - Daily at 9 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight

### 6. Configure Notifications (Optional)

To receive alerts when validation fails:

1. Navigate to the **Notifications** menu
2. Click **Add Channel** to add a Slack/Email/Webhook channel
3. Click **Add Rule** to configure notification rules

## CLI Options

```bash
# Default execution (port 8765)
truthound serve

# Custom port
truthound serve --port 9000

# Allow external access
truthound serve --host 0.0.0.0

# Disable automatic browser opening
truthound serve --no-browser

# Development mode (hot reload)
truthound serve --reload

# Specify data directory
truthound serve --data-dir /path/to/data
```

## Data Directory

Truthound Dashboard stores data in `~/.truthound` by default:

```
~/.truthound/
├── dashboard.db    # SQLite database
├── logs/           # Log files
└── .key            # Encryption key (auto-generated)
```

## Next Steps

- [Features](./features.md) - Explore all features
- [API Reference](./api.md) - Use the REST API
- [Configuration](./configuration.md) - Detailed configuration options

## Troubleshooting

### Port Already in Use

```bash
truthound serve --port 9000
```

### Database Reset

```bash
rm -rf ~/.truthound
truthound serve
```

### View Logs

```bash
cat ~/.truthound/logs/dashboard.log
```

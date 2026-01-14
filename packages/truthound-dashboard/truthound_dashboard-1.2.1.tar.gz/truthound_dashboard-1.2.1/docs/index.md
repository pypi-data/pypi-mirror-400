# Truthound Dashboard

> **Open-source Data Quality Dashboard** - A GX Cloud Alternative

Truthound Dashboard is an open-source data quality monitoring platform that provides features comparable to [GX Cloud](https://greatexpectations.io/gx-cloud/) at no cost.

## Feature Comparison

| Feature | GX Cloud | Truthound Dashboard |
|---------|----------|---------------------|
| UI-based Rule Editing | Paid | **Free** |
| Validation History | Paid | **Free** |
| Scheduled Validations | Paid | **Free** |
| Slack/Email Notifications | Paid | **Free** |
| Auto Schema Generation | Paid | **Free** |
| Drift Detection | Paid | **Free** |
| Unlimited Users | Team Plan | **Free** |
| **Pricing** | **Subscription** | **$0** |

## Quick Start

```bash
# Installation
pip install truthound-dashboard

# Launch (opens browser automatically)
truthound serve
```

The dashboard will be accessible within seconds.

## Key Features

### Data Sources
Connect to CSV, Parquet, PostgreSQL, MySQL, Snowflake, BigQuery, and other data sources.

### Visual Schema Editor
Create and edit validation schemas through the UI without writing code.

### Validation History
Track data quality trends over time with historical validation records.

### Scheduled Validations
Configure automated validation runs using cron-based scheduling.

### Notifications
Receive alerts via Slack, Email, or Webhook when validations fail.

### Auto Schema Generation
Automatically generate schemas from your data using `th.learn`.

### Drift Detection
Compare two datasets to detect schema and distribution changes.

### Dark Mode & i18n
Support for dark/light themes and multiple languages (English, Korean).

### AI-Powered Translation
Translate the UI to any language using OpenAI, Anthropic, Ollama, or Mistral with a single command.

## Documentation

- [Getting Started](./getting-started.md) - Installation and quick start guide
- [Features](./features.md) - Detailed feature documentation
- [Internationalization](./internationalization.md) - i18n and AI translation guide
- [API Reference](./api.md) - REST API documentation
- [Configuration](./configuration.md) - Configuration options

## Live Demo

Experience the dashboard at:

**[https://truthound-dashboard.netlify.app](https://truthound-dashboard.netlify.app)**

> The demo operates in mock mode using MSW (Mock Service Worker) without a backend connection.
> For actual data validation, install the package locally.

## Links

- [GitHub Repository](https://github.com/seadonggyun4/truthound-dashboard)
- [PyPI Package](https://pypi.org/project/truthound-dashboard/)
- [truthound Core Library](https://github.com/seadonggyun4/truthound)

## License

Apache License 2.0

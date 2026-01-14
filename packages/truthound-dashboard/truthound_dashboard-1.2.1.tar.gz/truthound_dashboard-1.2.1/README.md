<img width="300" height="300" alt="Truthound_icon" src="https://github.com/user-attachments/assets/90d9e806-8895-45ec-97dc-f8300da4d997" />

# truthound-dashboard

[![PyPI version](https://img.shields.io/pypi/v/truthound-dashboard.svg)](https://pypi.org/project/truthound-dashboard/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)
[![Powered by Intlayer](https://img.shields.io/badge/Powered%20by-Intlayer-yellow.svg)](https://intlayer.org)
[![Downloads](https://img.shields.io/pepy/dt/truthound-dashboard?color=brightgreen)](https://pepy.tech/project/truthound-dashboard)

A web-based data quality monitoring dashboard for [truthound](https://github.com/seadonggyun4/truthound).

[Documentation](https://truthound.netlify.app) | [Live Demo](https://truthound-dashboard.netlify.app) | [PyPI](https://pypi.org/project/truthound-dashboard/)

## Overview

truthound-dashboard provides a graphical interface for managing data sources, executing validations, tracking historical results, scheduling automated checks, and configuring notifications. It serves as an alternative to commercial data quality platforms.

## Feature Comparison with GX Cloud

| Feature | GX Cloud (Paid) | truthound-dashboard |
|---------|-----------------|---------------------|
| Data Source Management | Available | Available |
| Schema Learning | Available | Available |
| Validation Execution | Available | Available |
| Validation History | Available | Available |
| Scheduled Validations | Available | Available |
| Slack Notifications | Available | Available |
| Email Notifications | Available | Available |
| Webhook Notifications | Available | Available |
| Drift Detection | Available | Available |
| Data Profiling | Available | Available |
| Business Glossary | Available | Available |
| Data Catalog | Available | Available |
| Dark Mode | Available | Available |
| Multi-language (en/ko) | Not Available | Available |
| License | Commercial | Apache 2.0 |

## Requirements

- Python 3.11 or higher
- truthound >= 1.0.5

## Installation

```bash
pip install truthound-dashboard
```

This command automatically installs [truthound](https://github.com/seadonggyun4/truthound) as a dependency.

## Usage

```bash
# Start the dashboard server (default port: 8765)
truthound serve

# Specify a custom port
truthound serve --port 9000

# Enable development mode with hot reload
truthound serve --reload

# Disable automatic browser opening
truthound serve --no-browser
```

The dashboard interface is accessible at `http://localhost:8765`.

## Implemented Features

### Data Source Management
- Supported file formats: CSV, Parquet
- Supported databases: PostgreSQL, MySQL, Snowflake, BigQuery
- Connection validation

### Schema Management
- Automated schema generation using `th.learn`
- Manual schema editing in YAML format

### Validation
- On-demand validation execution using `th.check`
- Persistent storage of validation results
- Issue classification by severity (Critical, High, Medium, Low)

### Validation History
- Historical record of validation results
- Trend visualization

### Scheduling
- Cron-based scheduling using APScheduler
- Schedule controls: pause, resume, immediate execution

### Notifications
- Supported channels: Slack, Email, Webhook
- Configurable notification rules based on validation outcomes
- Notification delivery logs

### Drift Detection
- Dataset comparison using `th.compare`
- Column-level drift analysis

### Data Profiling
- Statistical profiling using `th.profile`
- Column-level statistics

### Business Glossary
- Business term definitions with categories
- Term relationships (synonyms, related terms)
- Term lifecycle management (draft, approved, deprecated)
- Change history tracking

### Data Catalog
- Data asset registration (tables, files, APIs)
- Column-level metadata management
- Column-to-term mapping
- Quality score tracking
- Sensitivity classification (public, internal, confidential, restricted)
- Custom tagging

### Collaboration
- Comments on terms, assets, and columns
- Activity feed for tracking changes

### User Interface
- Light and dark theme support
- Internationalization: English, Korean
- AI-powered translation for additional languages

## Internationalization

truthound-dashboard implements internationalization using [Intlayer](https://intlayer.org), a modern i18n framework that provides type-safe translations with component-level content declaration. This architecture enables seamless multi-language support while maintaining code maintainability.

### Default Languages

The application ships with English and Korean translations. These languages are immediately available without additional configuration.

### Extending Language Support

For projects requiring additional language support, the `translate` command enables AI-powered translation of the user interface.

#### Supported AI Providers

| Provider | Environment Variable | Models |
|----------|---------------------|--------|
| OpenAI | `OPENAI_API_KEY` | GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5 |
| Anthropic | `ANTHROPIC_API_KEY` | Claude Sonnet 4, Claude Opus 4 |
| Mistral | `MISTRAL_API_KEY` | Mistral Large, Mistral Small |
| Ollama | Not required | Llama 3.2, Mistral, Qwen (local execution) |

#### Configuration

API credentials are configured through environment variables. This approach ensures that sensitive credentials are not exposed in command history or application logs.

**Temporary Session Configuration**

```bash
# OpenAI
export OPENAI_API_KEY=sk-xxxxxxxxxxxx
truthound translate -l fr -p openai

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
truthound translate -l fr -p anthropic

# Mistral
export MISTRAL_API_KEY=xxxxxxxxxxxx
truthound translate -l fr -p mistral
```

**Persistent Configuration**

```bash
# Add to shell configuration file (~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY=sk-xxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

**Inline Configuration**

```bash
OPENAI_API_KEY=sk-xxx truthound translate -l fr -p openai
```

#### Usage Examples

```bash
# Translate to French using OpenAI
truthound translate -l fr -p openai

# Translate to multiple languages
truthound translate -l ja,zh,de,fr -p anthropic

# Use local Ollama (no API key required)
truthound translate -l fr -p ollama

# Auto-detect available provider
truthound translate -l fr

# Preview files without making changes
truthound translate -l fr --dry-run

# List available providers and their status
truthound translate --list-providers

# List supported language codes
truthound translate --list-languages
```

#### Security Considerations

| Aspect | Risk Level | Description |
|--------|------------|-------------|
| Network transmission | None | API keys are used locally and transmitted only to the selected provider |
| Source code exposure | None | Credentials are injected via environment variables |
| Build artifact inclusion | None | Only translated content is persisted; credentials are not stored |
| API communication | Standard | Requests are made directly to provider endpoints using user credentials |

#### Supported Languages

The translation system supports 36 languages including: Arabic, Bulgarian, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Korean, Latvian, Lithuanian, Malay, Norwegian, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Spanish, Swedish, Thai, Turkish, Ukrainian, and Vietnamese.

Execute `truthound translate --list-languages` to view the complete list with language codes.

## Technology Stack

**Backend**
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite with aiosqlite
- APScheduler
- Pydantic 2.x

**Frontend**
- React 18
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui
- Zustand
- [Intlayer](https://intlayer.org) (internationalization)

## Development Setup

```bash
# Clone the repository
git clone https://github.com/seadonggyun4/truthound-dashboard
cd truthound-dashboard

# Install backend dependencies
pip install -e ".[dev]"

# Start the backend server
truthound serve --reload

# In a separate terminal, install frontend dependencies
cd frontend
npm install

# Start the frontend development server
npm run dev

# Alternative: run with mock API (backend not required)
npm run dev:mock
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage report
pytest --cov=truthound_dashboard
```

## Live Demo

A live demonstration is available at [https://truthound-dashboard.netlify.app](https://truthound-dashboard.netlify.app).

The demo instance operates using Mock Service Worker (MSW) with simulated data and does not require a backend connection.

## Documentation

Full documentation is available at [https://truthound.netlify.app](https://truthound.netlify.app).

- [Getting Started](./docs/getting-started.md)
- [Features](./docs/features.md)
- [API Reference](./docs/api.md)
- [Configuration](./docs/configuration.md)

## Related Projects

- [truthound](https://github.com/seadonggyun4/truthound) - Core data validation library
- [truthound-orchestration](https://github.com/seadonggyun4/truthound-orchestration) - Pipeline orchestration integration

## License

This project is licensed under the Apache License 2.0.

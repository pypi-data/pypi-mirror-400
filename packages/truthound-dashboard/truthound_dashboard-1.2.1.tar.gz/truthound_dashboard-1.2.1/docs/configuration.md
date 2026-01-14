# Configuration

This document describes the configuration options for Truthound Dashboard.

## Environment Variables

All settings can be specified via environment variables with the `TRUTHOUND_` prefix.

### Basic Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TRUTHOUND_PORT` | `8765` | Server port |
| `TRUTHOUND_HOST` | `127.0.0.1` | Binding host |
| `TRUTHOUND_DATA_DIR` | `~/.truthound` | Data storage directory |
| `TRUTHOUND_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `TRUTHOUND_AUTH_ENABLED` | `false` | Enable authentication |
| `TRUTHOUND_AUTH_PASSWORD` | - | Authentication password |

### Performance

| Variable | Default | Description |
|----------|---------|-------------|
| `TRUTHOUND_SAMPLE_SIZE` | `100000` | Sample size for large files |
| `TRUTHOUND_CACHE_TTL` | `60` | Cache TTL (seconds) |
| `TRUTHOUND_RATE_LIMIT` | `120` | Maximum requests per minute |

## CLI Options

```bash
truthound serve [OPTIONS]
```

| Option | Description | Example |
|--------|-------------|---------|
| `--port` | Server port | `--port 9000` |
| `--host` | Binding host | `--host 0.0.0.0` |
| `--data-dir` | Data directory | `--data-dir /var/truthound` |
| `--reload` | Development mode (hot reload) | `--reload` |
| `--no-browser` | Disable automatic browser opening | `--no-browser` |
| `--log-level` | Log level | `--log-level DEBUG` |

**Examples:**
```bash
# Production configuration
truthound serve --host 0.0.0.0 --port 8080 --no-browser

# Development mode
truthound serve --reload --log-level DEBUG
```

## Data Directory

The default data directory is `~/.truthound`.

```
~/.truthound/
├── dashboard.db    # SQLite database
├── logs/           # Log files
│   └── dashboard.log
└── .key            # Encryption key (auto-generated)
```

### Custom Data Directory

```bash
# Via environment variable
export TRUTHOUND_DATA_DIR=/var/truthound
truthound serve

# Via CLI option
truthound serve --data-dir /var/truthound
```

## Authentication Setup

To enable password protection:

```bash
# Set environment variables
export TRUTHOUND_AUTH_ENABLED=true
export TRUTHOUND_AUTH_PASSWORD=your-secret-password

# Start server
truthound serve
```

When authentication is enabled, all API requests require Basic Auth:

```bash
curl -u :your-secret-password http://localhost:8765/api/v1/health
```

## External Access

To allow external access, set the host to `0.0.0.0`:

```bash
truthound serve --host 0.0.0.0
```

**Security Considerations:**
- Always enable authentication when allowing external access
- Consider running behind a reverse proxy (Nginx, Caddy)
- Use HTTPS

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name truthound.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install truthound-dashboard

EXPOSE 8765

CMD ["truthound", "serve", "--host", "0.0.0.0", "--no-browser"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  truthound:
    build: .
    ports:
      - "8765:8765"
    volumes:
      - truthound-data:/root/.truthound
    environment:
      - TRUTHOUND_AUTH_ENABLED=true
      - TRUTHOUND_AUTH_PASSWORD=${TRUTHOUND_PASSWORD}

volumes:
  truthound-data:
```

### Running

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f truthound
```

## Systemd Service

To run as a system service on Linux:

### /etc/systemd/system/truthound.service

```ini
[Unit]
Description=Truthound Dashboard
After=network.target

[Service]
Type=simple
User=truthound
Group=truthound
WorkingDirectory=/opt/truthound
Environment=TRUTHOUND_DATA_DIR=/var/lib/truthound
Environment=TRUTHOUND_AUTH_ENABLED=true
Environment=TRUTHOUND_AUTH_PASSWORD=your-password
ExecStart=/usr/local/bin/truthound serve --host 127.0.0.1 --no-browser
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Service Management

```bash
# Enable and start service
sudo systemctl enable truthound
sudo systemctl start truthound

# Check status
sudo systemctl status truthound

# View logs
sudo journalctl -u truthound -f
```

## Database Configuration

The SQLite database is created automatically and requires no additional configuration.

### Database Location

```
$TRUTHOUND_DATA_DIR/dashboard.db
```

### Backup

```bash
# Simple file copy
cp ~/.truthound/dashboard.db ~/.truthound/dashboard.db.backup

# Using SQLite CLI
sqlite3 ~/.truthound/dashboard.db ".backup '~/.truthound/dashboard.db.backup'"
```

### Reset

To completely reset the database:

```bash
rm ~/.truthound/dashboard.db
truthound serve
```

## Logging Configuration

### Log Levels

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed debug information (includes SQL queries) |
| `INFO` | General informational messages |
| `WARNING` | Warning messages |
| `ERROR` | Error messages only |

### Log File

Logs are stored at `$TRUTHOUND_DATA_DIR/logs/dashboard.log`.

```bash
# View logs in real-time
tail -f ~/.truthound/logs/dashboard.log
```

### Log Rotation

Log files are not automatically rotated. Configure logrotate:

```
/var/lib/truthound/logs/dashboard.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 truthound truthound
}
```

## Performance Tuning

### Large Datasets

For large dataset processing:

```bash
# Increase sample size (increases memory usage)
export TRUTHOUND_SAMPLE_SIZE=500000

# Or decrease for faster processing
export TRUTHOUND_SAMPLE_SIZE=50000
```

### Rate Limiting

Adjust API request limits:

```bash
# Increase requests per minute
export TRUTHOUND_RATE_LIMIT=240
```

### Cache TTL

Adjust cache duration:

```bash
# Increase cache TTL (seconds)
export TRUTHOUND_CACHE_TTL=300
```

## Maintenance

### Database Cleanup

Old data is automatically cleaned up:
- Validation results: deleted after 90 days
- Notification logs: deleted after 30 days
- VACUUM: runs every Sunday at 4 AM

To clean up manually:

```python
from truthound_dashboard.core.maintenance import (
    cleanup_old_validations,
    cleanup_notification_logs,
    vacuum_database,
)

# Async execution
import asyncio

asyncio.run(cleanup_old_validations(days=30))
asyncio.run(cleanup_notification_logs(days=7))
asyncio.run(vacuum_database())
```

### Health Check

Check server status:

```bash
curl http://localhost:8765/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "1.0.1"
}
```

## Troubleshooting

### Port Conflict

```bash
# Use a different port
truthound serve --port 9000
```

### Permission Errors

```bash
# Check data directory permissions
chmod 755 ~/.truthound
chmod 600 ~/.truthound/.key
```

### Connection Errors

```bash
# Enable debug mode for detailed logs
truthound serve --log-level DEBUG
```

### Memory Issues

```bash
# Reduce sample size
export TRUTHOUND_SAMPLE_SIZE=10000
truthound serve
```

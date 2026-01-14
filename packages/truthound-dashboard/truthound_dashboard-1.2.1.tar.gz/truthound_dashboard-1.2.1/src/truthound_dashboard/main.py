"""FastAPI application entry point.

This module defines the main FastAPI application with all middleware,
routers, and lifecycle management.

The application serves both the API and the React SPA static files.

Features:
- Phase 4 production-ready components:
  - Rate limiting and security headers
  - Structured logging
  - Error handling with localization
  - Database maintenance scheduling
  - Cache management

Example:
    # Run with uvicorn
    uvicorn truthound_dashboard.main:app --reload

    # Or via CLI
    truthound serve --reload
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from truthound_dashboard import __version__
from truthound_dashboard.api.error_handlers import setup_error_handlers
from truthound_dashboard.api.middleware import (
    RateLimitConfig,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from truthound_dashboard.api.router import api_router
from truthound_dashboard.config import get_settings
from truthound_dashboard.core.cache import get_cache
from truthound_dashboard.core.logging import setup_logging
from truthound_dashboard.core.maintenance import get_maintenance_manager
from truthound_dashboard.core.scheduler import get_scheduler
from truthound_dashboard.db import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events:
    - Startup:
        - Configure logging
        - Initialize database tables
        - Start cache cleanup task
        - Start validation scheduler
        - Schedule maintenance tasks
    - Shutdown:
        - Stop scheduler
        - Stop cache cleanup
        - Cleanup resources

    Args:
        app: FastAPI application instance.

    Yields:
        None during application runtime.
    """
    settings = get_settings()

    # Configure logging
    setup_logging(level=settings.log_level)
    logger.info(f"Starting Truthound Dashboard v{__version__}")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start cache cleanup
    cache = get_cache()
    await cache.start_cleanup_task()
    logger.info("Cache cleanup task started")

    # Start scheduler
    scheduler = get_scheduler()
    await scheduler.start()
    logger.info("Validation scheduler started")

    # Register maintenance tasks with scheduler
    _register_maintenance_tasks()

    yield

    # Shutdown
    logger.info("Shutting down Truthound Dashboard")

    # Stop scheduler
    await scheduler.stop()
    logger.info("Scheduler stopped")

    # Stop cache cleanup
    await cache.stop_cleanup_task()
    logger.info("Cache cleanup stopped")


def _register_maintenance_tasks() -> None:
    """Register maintenance tasks with the scheduler.

    Schedules daily cleanup at 3 AM and weekly vacuum on Sunday at 4 AM.
    """
    from apscheduler.triggers.cron import CronTrigger

    from truthound_dashboard.core.maintenance import (
        cleanup_notification_logs,
        cleanup_old_profiles,
        cleanup_old_validations,
        vacuum_database,
    )

    scheduler = get_scheduler()

    # Daily cleanup at 3 AM
    scheduler._scheduler.add_job(
        cleanup_old_validations,
        trigger=CronTrigger.from_crontab("0 3 * * *"),
        id="maintenance_validations",
        replace_existing=True,
        name="Cleanup old validations",
    )

    scheduler._scheduler.add_job(
        cleanup_old_profiles,
        trigger=CronTrigger.from_crontab("0 3 * * *"),
        id="maintenance_profiles",
        replace_existing=True,
        name="Cleanup old profiles",
    )

    scheduler._scheduler.add_job(
        cleanup_notification_logs,
        trigger=CronTrigger.from_crontab("0 3 * * *"),
        id="maintenance_notification_logs",
        replace_existing=True,
        name="Cleanup notification logs",
    )

    # Weekly vacuum on Sunday at 4 AM
    scheduler._scheduler.add_job(
        vacuum_database,
        trigger=CronTrigger.from_crontab("0 4 * * 0"),
        id="maintenance_vacuum",
        replace_existing=True,
        name="Database vacuum",
    )

    logger.info("Maintenance tasks registered")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    This factory function creates a fully configured FastAPI app
    with all middleware, routes, and static file handling.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Truthound Dashboard",
        description="Open-source data quality dashboard - GX Cloud alternative",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json",
    )

    # Configure CORS (must be first middleware)
    configure_cors(app)

    # Add security middleware
    configure_middleware(app)

    # Register exception handlers
    setup_error_handlers(app)

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    # Mount static files for React SPA
    mount_static_files(app)

    return app


def configure_cors(app: FastAPI) -> None:
    """Configure CORS middleware.

    Allows requests from the Vite dev server during development.

    Args:
        app: FastAPI application.
    """
    settings = get_settings()

    origins = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        f"http://localhost:{settings.port}",  # Dashboard server
        f"http://127.0.0.1:{settings.port}",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_middleware(app: FastAPI) -> None:
    """Configure security and logging middleware.

    Adds:
    - Request logging
    - Rate limiting
    - Security headers

    Args:
        app: FastAPI application.
    """
    # Request logging (last added = first executed)
    app.add_middleware(RequestLoggingMiddleware)

    # Rate limiting
    rate_limit_config = RateLimitConfig(
        requests_per_minute=120,
        exclude_paths=[
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/openapi.json",
        ],
    )
    app.add_middleware(RateLimitMiddleware, config=rate_limit_config)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)


def mount_static_files(app: FastAPI) -> None:
    """Mount static files for React SPA.

    Serves the built React application from the static directory.
    Falls back to index.html for SPA routing.

    Args:
        app: FastAPI application.
    """
    static_dir = Path(__file__).parent / "static"

    if not static_dir.exists():
        return

    index_file = static_dir / "index.html"
    if not index_file.exists():
        return

    # Mount assets directory
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets",
        )

    # SPA fallback route - must be last
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve SPA for all non-API routes.

        Args:
            full_path: Requested path.

        Returns:
            Static file or index.html for SPA routing.
        """
        # Check if it's a static file
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Fall back to index.html for SPA routing
        return FileResponse(index_file)


# Create app instance
app = create_app()

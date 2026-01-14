"""Global error handlers for FastAPI application.

This module provides centralized error handling with consistent
response formats and proper logging.

Features:
- Maps custom exceptions to HTTP responses
- Handles unexpected errors gracefully
- Provides consistent error response format
- Logs errors appropriately

Example:
    from truthound_dashboard.api.error_handlers import setup_error_handlers

    app = FastAPI()
    setup_error_handlers(app)
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from truthound_dashboard.core.exceptions import (
    ErrorCode,
    TruthoundDashboardError,
    get_error_message,
)

logger = logging.getLogger(__name__)


def create_error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create standardized error response.

    Args:
        code: Error code string.
        message: Human-readable error message.
        details: Additional error details.

    Returns:
        Dictionary suitable for JSON response.
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details:
        response["error"]["details"] = details
    return response


def setup_error_handlers(app: FastAPI) -> None:
    """Configure global error handlers for FastAPI application.

    Registers handlers for:
    - TruthoundDashboardError and subclasses
    - Pydantic validation errors
    - FastAPI request validation errors
    - Starlette HTTP exceptions
    - Generic exceptions (catch-all)

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(TruthoundDashboardError)
    async def handle_dashboard_error(
        request: Request,
        exc: TruthoundDashboardError,
    ) -> JSONResponse:
        """Handle custom dashboard exceptions.

        Logs the error and returns a structured response.
        """
        # Log at appropriate level based on HTTP status
        if exc.http_status >= 500:
            logger.error(
                f"Dashboard error: {exc.code.value} - {exc.message}",
                extra={"details": exc.details, "path": request.url.path},
            )
        else:
            logger.warning(
                f"Dashboard error: {exc.code.value} - {exc.message}",
                extra={"details": exc.details, "path": request.url.path},
            )

        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_response(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle FastAPI request validation errors.

        Converts Pydantic validation errors to user-friendly format.
        """
        errors = []
        for error in exc.errors():
            location = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": location,
                "message": error["msg"],
                "type": error["type"],
            })

        logger.warning(
            f"Request validation error: {request.url.path}",
            extra={"errors": errors},
        )

        return JSONResponse(
            status_code=422,
            content=create_error_response(
                code=ErrorCode.VALIDATION_ERROR.value,
                message="Request validation failed",
                details={"validation_errors": errors},
            ),
        )

    @app.exception_handler(PydanticValidationError)
    async def handle_pydantic_validation_error(
        request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            location = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": location,
                "message": error["msg"],
                "type": error["type"],
            })

        logger.warning(
            f"Pydantic validation error: {request.url.path}",
            extra={"errors": errors},
        )

        return JSONResponse(
            status_code=422,
            content=create_error_response(
                code=ErrorCode.VALIDATION_ERROR.value,
                message="Data validation failed",
                details={"validation_errors": errors},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """Handle Starlette HTTP exceptions."""
        # Map common HTTP status codes to error codes
        status_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_REQUIRED,
            403: ErrorCode.AUTHORIZATION_FAILED,
            404: ErrorCode.SOURCE_NOT_FOUND,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_ERROR,
            502: ErrorCode.SOURCE_CONNECTION_FAILED,
            503: ErrorCode.DATABASE_CONNECTION_FAILED,
        }

        error_code = status_code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR)
        message = str(exc.detail) if exc.detail else get_error_message(error_code)

        if exc.status_code >= 500:
            logger.error(
                f"HTTP error {exc.status_code}: {message}",
                extra={"path": request.url.path},
            )
        else:
            logger.warning(
                f"HTTP error {exc.status_code}: {message}",
                extra={"path": request.url.path},
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=error_code.value,
                message=message,
            ),
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        """Handle ValueError as 400 Bad Request."""
        logger.warning(
            f"ValueError: {exc}",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=400,
            content=create_error_response(
                code=ErrorCode.VALIDATION_ERROR.value,
                message=str(exc),
            ),
        )

    @app.exception_handler(FileNotFoundError)
    async def handle_file_not_found_error(
        request: Request,
        exc: FileNotFoundError,
    ) -> JSONResponse:
        """Handle FileNotFoundError as 404 Not Found."""
        logger.warning(
            f"FileNotFoundError: {exc}",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=404,
            content=create_error_response(
                code=ErrorCode.SOURCE_NOT_FOUND.value,
                message=str(exc),
            ),
        )

    @app.exception_handler(PermissionError)
    async def handle_permission_error(
        request: Request,
        exc: PermissionError,
    ) -> JSONResponse:
        """Handle PermissionError as 403 Forbidden."""
        logger.warning(
            f"PermissionError: {exc}",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=403,
            content=create_error_response(
                code=ErrorCode.SOURCE_ACCESS_DENIED.value,
                message="Access denied to the requested resource",
            ),
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions.

        Logs the full traceback but returns a safe error message
        to avoid exposing internal details.
        """
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {exc}\n"
            f"{traceback.format_exc()}",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=500,
            content=create_error_response(
                code=ErrorCode.INTERNAL_ERROR.value,
                message=get_error_message(ErrorCode.INTERNAL_ERROR),
            ),
        )

"""Hierarchical exception system with error codes and localization.

This module provides a comprehensive exception hierarchy for the dashboard,
supporting error codes, localized messages, and HTTP status code mapping.

The design follows these principles:
- Clear exception hierarchy for different error types
- Unique error codes for each exception type
- Support for localized error messages
- Easy HTTP status code mapping

Example:
    try:
        source = await get_source(source_id)
    except SourceNotFoundError as e:
        return JSONResponse(
            status_code=e.http_status,
            content=e.to_response(),
        )
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Error codes for categorized exception types.

    Format: {CATEGORY}_{SPECIFIC_ERROR}
    """

    # Generic errors (1xx)
    UNKNOWN_ERROR = "E100"
    INTERNAL_ERROR = "E101"
    VALIDATION_ERROR = "E102"

    # Source errors (2xx)
    SOURCE_NOT_FOUND = "E200"
    SOURCE_CONNECTION_FAILED = "E201"
    SOURCE_INVALID_CONFIG = "E202"
    SOURCE_ACCESS_DENIED = "E203"

    # Schema errors (3xx)
    SCHEMA_NOT_FOUND = "E300"
    SCHEMA_INVALID = "E301"
    SCHEMA_PARSE_ERROR = "E302"

    # Rule errors (4xx)
    RULE_NOT_FOUND = "E400"
    RULE_INVALID = "E401"
    RULE_PARSE_ERROR = "E402"

    # Validation errors (5xx)
    VALIDATION_NOT_FOUND = "E500"
    VALIDATION_FAILED = "E501"
    VALIDATION_TIMEOUT = "E502"

    # Schedule errors (6xx)
    SCHEDULE_NOT_FOUND = "E600"
    SCHEDULE_INVALID_CRON = "E601"
    SCHEDULE_CONFLICT = "E602"

    # Notification errors (7xx)
    NOTIFICATION_CHANNEL_NOT_FOUND = "E700"
    NOTIFICATION_RULE_NOT_FOUND = "E701"
    NOTIFICATION_SEND_FAILED = "E702"
    NOTIFICATION_INVALID_CONFIG = "E703"

    # Security errors (8xx)
    AUTHENTICATION_REQUIRED = "E800"
    AUTHENTICATION_FAILED = "E801"
    AUTHORIZATION_FAILED = "E802"
    RATE_LIMIT_EXCEEDED = "E803"

    # Database errors (9xx)
    DATABASE_ERROR = "E900"
    DATABASE_CONNECTION_FAILED = "E901"
    DATABASE_INTEGRITY_ERROR = "E902"


# Localized error messages
ERROR_MESSAGES: dict[str, dict[str, str]] = {
    ErrorCode.UNKNOWN_ERROR: {
        "en": "An unknown error occurred",
        "ko": "알 수 없는 오류가 발생했습니다",
    },
    ErrorCode.INTERNAL_ERROR: {
        "en": "An internal server error occurred. Please try again later.",
        "ko": "내부 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    },
    ErrorCode.VALIDATION_ERROR: {
        "en": "Validation failed. Please check your input.",
        "ko": "검증에 실패했습니다. 입력을 확인해주세요.",
    },
    ErrorCode.SOURCE_NOT_FOUND: {
        "en": "The data source could not be found. It may have been deleted.",
        "ko": "데이터 소스를 찾을 수 없습니다. 삭제되었을 수 있습니다.",
    },
    ErrorCode.SOURCE_CONNECTION_FAILED: {
        "en": "Could not connect to the data source. Please verify your connection settings.",
        "ko": "데이터 소스에 연결할 수 없습니다. 연결 설정을 확인해주세요.",
    },
    ErrorCode.SOURCE_INVALID_CONFIG: {
        "en": "Invalid source configuration. Please check the settings.",
        "ko": "잘못된 소스 설정입니다. 설정을 확인해주세요.",
    },
    ErrorCode.SOURCE_ACCESS_DENIED: {
        "en": "Access to the data source was denied.",
        "ko": "데이터 소스에 대한 접근이 거부되었습니다.",
    },
    ErrorCode.SCHEMA_NOT_FOUND: {
        "en": "Schema not found for this source.",
        "ko": "이 소스에 대한 스키마를 찾을 수 없습니다.",
    },
    ErrorCode.SCHEMA_INVALID: {
        "en": "The schema is invalid.",
        "ko": "스키마가 유효하지 않습니다.",
    },
    ErrorCode.SCHEMA_PARSE_ERROR: {
        "en": "Failed to parse schema. Check YAML syntax.",
        "ko": "스키마 파싱에 실패했습니다. YAML 문법을 확인해주세요.",
    },
    ErrorCode.RULE_NOT_FOUND: {
        "en": "Rule not found.",
        "ko": "규칙을 찾을 수 없습니다.",
    },
    ErrorCode.RULE_INVALID: {
        "en": "The rule configuration is invalid.",
        "ko": "규칙 설정이 유효하지 않습니다.",
    },
    ErrorCode.RULE_PARSE_ERROR: {
        "en": "Failed to parse rule. Check YAML syntax.",
        "ko": "규칙 파싱에 실패했습니다. YAML 문법을 확인해주세요.",
    },
    ErrorCode.VALIDATION_NOT_FOUND: {
        "en": "Validation result not found.",
        "ko": "검증 결과를 찾을 수 없습니다.",
    },
    ErrorCode.VALIDATION_FAILED: {
        "en": "Validation failed. Please check your data and rules.",
        "ko": "검증에 실패했습니다. 데이터와 규칙을 확인해주세요.",
    },
    ErrorCode.VALIDATION_TIMEOUT: {
        "en": "Validation timed out. Try with a smaller dataset or increase timeout.",
        "ko": "검증 시간이 초과되었습니다. 더 작은 데이터셋을 사용하거나 타임아웃을 늘려주세요.",
    },
    ErrorCode.SCHEDULE_NOT_FOUND: {
        "en": "Schedule not found.",
        "ko": "스케줄을 찾을 수 없습니다.",
    },
    ErrorCode.SCHEDULE_INVALID_CRON: {
        "en": "Invalid cron expression. Please check the schedule syntax.",
        "ko": "잘못된 cron 표현식입니다. 스케줄 문법을 확인해주세요.",
    },
    ErrorCode.SCHEDULE_CONFLICT: {
        "en": "Schedule conflict detected.",
        "ko": "스케줄 충돌이 감지되었습니다.",
    },
    ErrorCode.NOTIFICATION_CHANNEL_NOT_FOUND: {
        "en": "Notification channel not found.",
        "ko": "알림 채널을 찾을 수 없습니다.",
    },
    ErrorCode.NOTIFICATION_RULE_NOT_FOUND: {
        "en": "Notification rule not found.",
        "ko": "알림 규칙을 찾을 수 없습니다.",
    },
    ErrorCode.NOTIFICATION_SEND_FAILED: {
        "en": "Failed to send notification. Please check your channel configuration.",
        "ko": "알림 발송에 실패했습니다. 채널 설정을 확인해주세요.",
    },
    ErrorCode.NOTIFICATION_INVALID_CONFIG: {
        "en": "Invalid notification configuration.",
        "ko": "잘못된 알림 설정입니다.",
    },
    ErrorCode.AUTHENTICATION_REQUIRED: {
        "en": "Authentication is required.",
        "ko": "인증이 필요합니다.",
    },
    ErrorCode.AUTHENTICATION_FAILED: {
        "en": "Authentication failed. Please check your credentials.",
        "ko": "인증에 실패했습니다. 자격 증명을 확인해주세요.",
    },
    ErrorCode.AUTHORIZATION_FAILED: {
        "en": "You do not have permission to perform this action.",
        "ko": "이 작업을 수행할 권한이 없습니다.",
    },
    ErrorCode.RATE_LIMIT_EXCEEDED: {
        "en": "Too many requests. Please try again later.",
        "ko": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
    },
    ErrorCode.DATABASE_ERROR: {
        "en": "A database error occurred.",
        "ko": "데이터베이스 오류가 발생했습니다.",
    },
    ErrorCode.DATABASE_CONNECTION_FAILED: {
        "en": "Failed to connect to the database.",
        "ko": "데이터베이스 연결에 실패했습니다.",
    },
    ErrorCode.DATABASE_INTEGRITY_ERROR: {
        "en": "Database integrity error. Data may be corrupted.",
        "ko": "데이터베이스 무결성 오류입니다. 데이터가 손상되었을 수 있습니다.",
    },
}


def get_error_message(code: ErrorCode | str, lang: str = "en") -> str:
    """Get localized error message for an error code.

    Args:
        code: Error code.
        lang: Language code ('en' or 'ko').

    Returns:
        Localized error message.
    """
    if isinstance(code, str):
        code = ErrorCode(code)
    messages = ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR])
    return messages.get(lang, messages.get("en", "An error occurred"))


class TruthoundDashboardError(Exception):
    """Base exception for truthound-dashboard.

    All custom exceptions should inherit from this class.

    Attributes:
        message: Human-readable error message.
        code: Error code enum.
        details: Additional error details.
        http_status: HTTP status code for API responses.
    """

    code: ErrorCode = ErrorCode.UNKNOWN_ERROR
    http_status: int = 500

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        lang: str = "en",
    ) -> None:
        """Initialize exception.

        Args:
            message: Custom error message. Uses default if not provided.
            details: Additional error details.
            lang: Language for default message.
        """
        self.message = message or get_error_message(self.code, lang)
        self.details = details or {}
        self.lang = lang
        super().__init__(self.message)

    def to_response(self) -> dict[str, Any]:
        """Convert exception to API response format.

        Returns:
            Dictionary suitable for JSON response.
        """
        response = {
            "success": False,
            "error": {
                "code": self.code.value,
                "message": self.message,
            },
        }
        if self.details:
            response["error"]["details"] = self.details
        return response

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code.value}, message={self.message!r})"


# =============================================================================
# Source Errors
# =============================================================================


class SourceError(TruthoundDashboardError):
    """Base class for source-related errors."""

    code = ErrorCode.SOURCE_NOT_FOUND
    http_status = 404


class SourceNotFoundError(SourceError):
    """Raised when a data source cannot be found."""

    code = ErrorCode.SOURCE_NOT_FOUND
    http_status = 404

    def __init__(self, source_id: str, **kwargs: Any) -> None:
        """Initialize with source ID.

        Args:
            source_id: ID of the source that was not found.
            **kwargs: Additional arguments for parent class.
        """
        super().__init__(details={"source_id": source_id}, **kwargs)


class SourceConnectionError(SourceError):
    """Raised when connection to a data source fails."""

    code = ErrorCode.SOURCE_CONNECTION_FAILED
    http_status = 502

    def __init__(
        self,
        source_type: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with source type and reason.

        Args:
            source_type: Type of source (file, postgresql, etc.).
            reason: Reason for connection failure.
            **kwargs: Additional arguments for parent class.
        """
        details = {"source_type": source_type}
        if reason:
            details["reason"] = reason
        super().__init__(details=details, **kwargs)


class SourceInvalidConfigError(SourceError):
    """Raised when source configuration is invalid."""

    code = ErrorCode.SOURCE_INVALID_CONFIG
    http_status = 400


class SourceAccessDeniedError(SourceError):
    """Raised when access to a source is denied."""

    code = ErrorCode.SOURCE_ACCESS_DENIED
    http_status = 403


# =============================================================================
# Schema Errors
# =============================================================================


class SchemaError(TruthoundDashboardError):
    """Base class for schema-related errors."""

    code = ErrorCode.SCHEMA_NOT_FOUND
    http_status = 404


class SchemaNotFoundError(SchemaError):
    """Raised when a schema cannot be found."""

    code = ErrorCode.SCHEMA_NOT_FOUND
    http_status = 404

    def __init__(self, source_id: str, **kwargs: Any) -> None:
        super().__init__(details={"source_id": source_id}, **kwargs)


class SchemaInvalidError(SchemaError):
    """Raised when a schema is invalid."""

    code = ErrorCode.SCHEMA_INVALID
    http_status = 400


class SchemaParseError(SchemaError):
    """Raised when schema parsing fails."""

    code = ErrorCode.SCHEMA_PARSE_ERROR
    http_status = 400

    def __init__(self, parse_error: str, **kwargs: Any) -> None:
        super().__init__(details={"parse_error": parse_error}, **kwargs)


# =============================================================================
# Rule Errors
# =============================================================================


class RuleError(TruthoundDashboardError):
    """Base class for rule-related errors."""

    code = ErrorCode.RULE_NOT_FOUND
    http_status = 404


class RuleNotFoundError(RuleError):
    """Raised when a rule cannot be found."""

    code = ErrorCode.RULE_NOT_FOUND
    http_status = 404

    def __init__(self, rule_id: str, **kwargs: Any) -> None:
        super().__init__(details={"rule_id": rule_id}, **kwargs)


class RuleInvalidError(RuleError):
    """Raised when a rule is invalid."""

    code = ErrorCode.RULE_INVALID
    http_status = 400


class RuleParseError(RuleError):
    """Raised when rule parsing fails."""

    code = ErrorCode.RULE_PARSE_ERROR
    http_status = 400

    def __init__(self, parse_error: str, **kwargs: Any) -> None:
        super().__init__(details={"parse_error": parse_error}, **kwargs)


# =============================================================================
# Validation Errors
# =============================================================================


class ValidationError(TruthoundDashboardError):
    """Base class for validation-related errors."""

    code = ErrorCode.VALIDATION_ERROR
    http_status = 400


class ValidationNotFoundError(ValidationError):
    """Raised when a validation result cannot be found."""

    code = ErrorCode.VALIDATION_NOT_FOUND
    http_status = 404

    def __init__(self, validation_id: str, **kwargs: Any) -> None:
        super().__init__(details={"validation_id": validation_id}, **kwargs)


class ValidationFailedError(ValidationError):
    """Raised when validation execution fails."""

    code = ErrorCode.VALIDATION_FAILED
    http_status = 500

    def __init__(self, reason: str, **kwargs: Any) -> None:
        super().__init__(details={"reason": reason}, **kwargs)


class ValidationTimeoutError(ValidationError):
    """Raised when validation times out."""

    code = ErrorCode.VALIDATION_TIMEOUT
    http_status = 504


# =============================================================================
# Schedule Errors
# =============================================================================


class ScheduleError(TruthoundDashboardError):
    """Base class for schedule-related errors."""

    code = ErrorCode.SCHEDULE_NOT_FOUND
    http_status = 404


class ScheduleNotFoundError(ScheduleError):
    """Raised when a schedule cannot be found."""

    code = ErrorCode.SCHEDULE_NOT_FOUND
    http_status = 404

    def __init__(self, schedule_id: str, **kwargs: Any) -> None:
        super().__init__(details={"schedule_id": schedule_id}, **kwargs)


class ScheduleInvalidCronError(ScheduleError):
    """Raised when a cron expression is invalid."""

    code = ErrorCode.SCHEDULE_INVALID_CRON
    http_status = 400

    def __init__(self, cron_expression: str, **kwargs: Any) -> None:
        super().__init__(details={"cron_expression": cron_expression}, **kwargs)


class ScheduleConflictError(ScheduleError):
    """Raised when there is a schedule conflict."""

    code = ErrorCode.SCHEDULE_CONFLICT
    http_status = 409


# =============================================================================
# Notification Errors
# =============================================================================


class NotificationError(TruthoundDashboardError):
    """Base class for notification-related errors."""

    code = ErrorCode.NOTIFICATION_SEND_FAILED
    http_status = 500


class NotificationChannelNotFoundError(NotificationError):
    """Raised when a notification channel cannot be found."""

    code = ErrorCode.NOTIFICATION_CHANNEL_NOT_FOUND
    http_status = 404

    def __init__(self, channel_id: str, **kwargs: Any) -> None:
        super().__init__(details={"channel_id": channel_id}, **kwargs)


class NotificationRuleNotFoundError(NotificationError):
    """Raised when a notification rule cannot be found."""

    code = ErrorCode.NOTIFICATION_RULE_NOT_FOUND
    http_status = 404

    def __init__(self, rule_id: str, **kwargs: Any) -> None:
        super().__init__(details={"rule_id": rule_id}, **kwargs)


class NotificationSendError(NotificationError):
    """Raised when notification delivery fails."""

    code = ErrorCode.NOTIFICATION_SEND_FAILED
    http_status = 502

    def __init__(
        self,
        channel_type: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"channel_type": channel_type}
        if reason:
            details["reason"] = reason
        super().__init__(details=details, **kwargs)


class NotificationInvalidConfigError(NotificationError):
    """Raised when notification configuration is invalid."""

    code = ErrorCode.NOTIFICATION_INVALID_CONFIG
    http_status = 400


# =============================================================================
# Security Errors
# =============================================================================


class SecurityError(TruthoundDashboardError):
    """Base class for security-related errors."""

    code = ErrorCode.AUTHENTICATION_REQUIRED
    http_status = 401


class AuthenticationRequiredError(SecurityError):
    """Raised when authentication is required but not provided."""

    code = ErrorCode.AUTHENTICATION_REQUIRED
    http_status = 401


class AuthenticationFailedError(SecurityError):
    """Raised when authentication fails."""

    code = ErrorCode.AUTHENTICATION_FAILED
    http_status = 401


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""

    code = ErrorCode.AUTHORIZATION_FAILED
    http_status = 403


class RateLimitExceededError(SecurityError):
    """Raised when rate limit is exceeded."""

    code = ErrorCode.RATE_LIMIT_EXCEEDED
    http_status = 429

    def __init__(self, retry_after: int | None = None, **kwargs: Any) -> None:
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(details=details, **kwargs)


# =============================================================================
# Database Errors
# =============================================================================


class DatabaseError(TruthoundDashboardError):
    """Base class for database-related errors."""

    code = ErrorCode.DATABASE_ERROR
    http_status = 500


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    code = ErrorCode.DATABASE_CONNECTION_FAILED
    http_status = 503


class DatabaseIntegrityError(DatabaseError):
    """Raised when database integrity is violated."""

    code = ErrorCode.DATABASE_INTEGRITY_ERROR
    http_status = 500

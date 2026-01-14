"""Core business logic module.

This module contains the core business logic for the dashboard,
including services, adapters, and domain models.

Exports:
    - Adapter: TruthoundAdapter, get_adapter
    - Services: SourceService, ValidationService, SchemaService, RuleService, ProfileService,
                HistoryService, DriftService, ScheduleService
    - Result types: CheckResult, LearnResult, ProfileResult, CompareResult
    - Scheduler: ValidationScheduler, get_scheduler, start_scheduler, stop_scheduler
    - Notifications: NotificationDispatcher, create_dispatcher, get_dispatcher
    - Cache: CacheBackend, MemoryCache, FileCache, get_cache, get_cache_manager
    - Maintenance: MaintenanceManager, get_maintenance_manager, cleanup_old_validations
    - Sampling: DataSampler, SamplingStrategy, get_sampler (Large Dataset Handling)
    - Exceptions: TruthoundDashboardError, SourceNotFoundError, ValidationError, etc.
    - Encryption: encrypt_value, decrypt_value, encrypt_config, decrypt_config
    - Logging: setup_logging, get_logger, get_audit_logger
"""

from .base import BaseService, CRUDService
from .cache import (
    CacheBackend,
    CacheManager,
    FileCache,
    MemoryCache,
    get_cache,
    get_cache_manager,
    reset_cache,
)
from .encryption import (
    EncryptionError,
    Encryptor,
    decrypt_config,
    decrypt_value,
    encrypt_config,
    encrypt_value,
    get_encryptor,
    is_sensitive_field,
    mask_sensitive_value,
)
from .exceptions import (
    AuthenticationFailedError,
    AuthenticationRequiredError,
    AuthorizationError,
    DatabaseConnectionError,
    DatabaseError,
    DatabaseIntegrityError,
    ErrorCode,
    NotificationChannelNotFoundError,
    NotificationError,
    NotificationInvalidConfigError,
    NotificationRuleNotFoundError,
    NotificationSendError,
    RateLimitExceededError,
    RuleError,
    RuleInvalidError,
    RuleNotFoundError,
    RuleParseError,
    ScheduleConflictError,
    ScheduleError,
    ScheduleInvalidCronError,
    ScheduleNotFoundError,
    SchemaError,
    SchemaInvalidError,
    SchemaNotFoundError,
    SchemaParseError,
    SecurityError,
    SourceAccessDeniedError,
    SourceConnectionError,
    SourceError,
    SourceInvalidConfigError,
    SourceNotFoundError,
    TruthoundDashboardError,
    ValidationError,
    ValidationFailedError,
    ValidationNotFoundError,
    ValidationTimeoutError,
    get_error_message,
)
from .logging import (
    AuditLogger,
    LogConfig,
    LoggerAdapter,
    get_audit_logger,
    get_logger,
    setup_logging,
)
from .maintenance import (
    CleanupResult,
    CleanupStrategy,
    MaintenanceConfig,
    MaintenanceManager,
    MaintenanceReport,
    cleanup_notification_logs,
    cleanup_old_profiles,
    cleanup_old_validations,
    get_maintenance_manager,
    reset_maintenance_manager,
    vacuum_database,
)
from .notifications import (
    NotificationDispatcher,
    create_dispatcher,
    get_dispatcher,
)
from .sampling import (
    DataSampler,
    HeadSamplingStrategy,
    RandomSamplingStrategy,
    SamplingConfig,
    SamplingMethod,
    SamplingResult,
    SamplingStrategy,
    StratifiedSamplingStrategy,
    TailSamplingStrategy,
    get_sampler,
    reset_sampler,
)
from .scheduler import (
    ValidationScheduler,
    get_scheduler,
    start_scheduler,
    stop_scheduler,
)
from .services import (
    DriftService,
    HistoryService,
    ProfileService,
    RuleService,
    ScheduleService,
    SchemaService,
    SourceService,
    ValidationService,
)
from .truthound_adapter import (
    CheckResult,
    CompareResult,
    LearnResult,
    ProfileResult,
    TruthoundAdapter,
    get_adapter,
    reset_adapter,
)
# Phase 5 Services
from .phase5 import (
    ActivityLogger,
    CatalogService,
    CollaborationService,
    GlossaryService,
)

__all__ = [
    # Base classes
    "BaseService",
    "CRUDService",
    # Services
    "SourceService",
    "ValidationService",
    "SchemaService",
    "RuleService",
    "ProfileService",
    "HistoryService",
    "DriftService",
    "ScheduleService",
    # Adapter
    "TruthoundAdapter",
    "get_adapter",
    "reset_adapter",
    # Result types
    "CheckResult",
    "LearnResult",
    "ProfileResult",
    "CompareResult",
    # Scheduler
    "ValidationScheduler",
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
    # Notifications
    "NotificationDispatcher",
    "create_dispatcher",
    "get_dispatcher",
    # Cache (Phase 4)
    "CacheBackend",
    "MemoryCache",
    "FileCache",
    "CacheManager",
    "get_cache",
    "get_cache_manager",
    "reset_cache",
    # Maintenance (Phase 4)
    "MaintenanceManager",
    "MaintenanceConfig",
    "MaintenanceReport",
    "CleanupResult",
    "CleanupStrategy",
    "get_maintenance_manager",
    "reset_maintenance_manager",
    "cleanup_old_validations",
    "cleanup_old_profiles",
    "cleanup_notification_logs",
    "vacuum_database",
    # Exceptions (Phase 4)
    "TruthoundDashboardError",
    "ErrorCode",
    "get_error_message",
    "SourceError",
    "SourceNotFoundError",
    "SourceConnectionError",
    "SourceInvalidConfigError",
    "SourceAccessDeniedError",
    "SchemaError",
    "SchemaNotFoundError",
    "SchemaInvalidError",
    "SchemaParseError",
    "RuleError",
    "RuleNotFoundError",
    "RuleInvalidError",
    "RuleParseError",
    "ValidationError",
    "ValidationNotFoundError",
    "ValidationFailedError",
    "ValidationTimeoutError",
    "ScheduleError",
    "ScheduleNotFoundError",
    "ScheduleInvalidCronError",
    "ScheduleConflictError",
    "NotificationError",
    "NotificationChannelNotFoundError",
    "NotificationRuleNotFoundError",
    "NotificationSendError",
    "NotificationInvalidConfigError",
    "SecurityError",
    "AuthenticationRequiredError",
    "AuthenticationFailedError",
    "AuthorizationError",
    "RateLimitExceededError",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseIntegrityError",
    # Encryption (Phase 4)
    "Encryptor",
    "EncryptionError",
    "get_encryptor",
    "encrypt_value",
    "decrypt_value",
    "encrypt_config",
    "decrypt_config",
    "is_sensitive_field",
    "mask_sensitive_value",
    # Logging (Phase 4)
    "LogConfig",
    "LoggerAdapter",
    "AuditLogger",
    "setup_logging",
    "get_logger",
    "get_audit_logger",
    # Sampling (Phase 4 - Large Dataset Handling)
    "DataSampler",
    "SamplingConfig",
    "SamplingMethod",
    "SamplingResult",
    "SamplingStrategy",
    "RandomSamplingStrategy",
    "HeadSamplingStrategy",
    "TailSamplingStrategy",
    "StratifiedSamplingStrategy",
    "get_sampler",
    "reset_sampler",
    # Phase 5 Services
    "GlossaryService",
    "CatalogService",
    "CollaborationService",
    "ActivityLogger",
]

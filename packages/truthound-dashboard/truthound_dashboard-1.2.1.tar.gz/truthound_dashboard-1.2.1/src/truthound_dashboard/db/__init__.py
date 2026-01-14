"""Database module.

This module provides database connectivity, models, and repository patterns
for the truthound dashboard.

Exports:
    - Database connection: get_session, get_db_session, init_db
    - Base classes: Base, UUIDMixin, TimestampMixin
    - Models: Source, Schema, Rule, Validation, Profile, Schedule, DriftComparison, AppSettings
    - Repository: BaseRepository
"""

from .base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from .database import (
    get_db_session,
    get_engine,
    get_session,
    get_session_factory,
    init_db,
    reset_connection,
    reset_db,
)
from .models import (
    # Phase 1-4 Models
    AppSettings,
    DriftComparison,
    NotificationChannel,
    NotificationLog,
    NotificationRule,
    Profile,
    Rule,
    Schedule,
    Schema,
    Source,
    Validation,
    # Phase 5 Enums
    ActivityAction,
    AssetType,
    RelationshipType,
    ResourceType,
    SensitivityLevel,
    TermStatus,
    # Phase 5 Models
    Activity,
    AssetColumn,
    AssetTag,
    CatalogAsset,
    Comment,
    GlossaryCategory,
    GlossaryTerm,
    TermHistory,
    TermRelationship,
)
from .repository import BaseRepository

__all__ = [
    # Base classes
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    # Database functions
    "get_session",
    "get_db_session",
    "get_engine",
    "get_session_factory",
    "init_db",
    "reset_db",
    "reset_connection",
    # Models
    "Source",
    "Schema",
    "Rule",
    "Validation",
    "Profile",
    "Schedule",
    "DriftComparison",
    "AppSettings",
    # Notification models (Phase 3)
    "NotificationChannel",
    "NotificationRule",
    "NotificationLog",
    # Phase 5 Enums
    "TermStatus",
    "RelationshipType",
    "AssetType",
    "SensitivityLevel",
    "ResourceType",
    "ActivityAction",
    # Phase 5 Models - Glossary
    "GlossaryCategory",
    "GlossaryTerm",
    "TermRelationship",
    "TermHistory",
    # Phase 5 Models - Catalog
    "CatalogAsset",
    "AssetColumn",
    "AssetTag",
    # Phase 5 Models - Collaboration
    "Comment",
    "Activity",
    # Repository
    "BaseRepository",
]

"""Pydantic schemas for API request/response validation.

This module exports all schemas used in the API layer.
Schemas follow consistent naming conventions:
- *Base: Common fields
- *Create: POST request bodies
- *Update: PUT/PATCH request bodies
- *Response: Response bodies
- *ListResponse: Paginated list responses
"""

from .base import (
    BaseSchema,
    ErrorResponse,
    IDMixin,
    ListResponseWrapper,
    MessageResponse,
    ResponseWrapper,
    TimestampMixin,
)
from .drift import (
    ColumnDriftResult,
    DriftCompareRequest,
    DriftComparisonListItem,
    DriftComparisonListResponse,
    DriftComparisonResponse,
    DriftResult,
    DriftSourceSummary,
)
from .history import (
    FailureFrequencyItem,
    HistoryQueryParams,
    HistoryResponse,
    HistorySummary,
    RecentValidation,
    TrendDataPoint,
)
from .profile import ColumnProfile, ProfileResponse
from .rule import (
    RuleBase,
    RuleCreate,
    RuleListItem,
    RuleListResponse,
    RuleResponse,
    RuleSummary,
    RuleUpdate,
)
from .schedule import (
    ScheduleActionResponse,
    ScheduleBase,
    ScheduleCreate,
    ScheduleListItem,
    ScheduleListResponse,
    ScheduleResponse,
    ScheduleUpdate,
)
# Phase 5: Glossary schemas
from .glossary import (
    CategoryBase,
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategorySummary,
    CategoryUpdate,
    RelatedTermSummary,
    RelationshipBase,
    RelationshipCreate,
    RelationshipListResponse,
    RelationshipResponse,
    RelationshipType,
    TermBase,
    TermCreate,
    TermHistoryListResponse,
    TermHistoryResponse,
    TermListItem,
    TermListResponse,
    TermResponse,
    TermStatus,
    TermSummary,
    TermUpdate,
)
# Phase 5: Catalog schemas
from .catalog import (
    AssetBase,
    AssetCreate,
    AssetListItem,
    AssetListResponse,
    AssetResponse,
    AssetType,
    AssetUpdate,
    ColumnBase,
    ColumnCreate,
    ColumnListResponse,
    ColumnResponse,
    ColumnTermMapping,
    ColumnUpdate,
    QualityLevel,
    SensitivityLevel,
    SourceSummary,
    TagBase,
    TagCreate,
    TagResponse,
)
# Phase 5: Collaboration schemas
from .collaboration import (
    ActivityAction,
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
    CommentBase,
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
    ResourceType,
)
from .schema import (
    ColumnSchema,
    SchemaLearnRequest,
    SchemaResponse,
    SchemaSummary,
    SchemaUpdateRequest,
)
from .source import (
    SourceBase,
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceSummary,
    SourceType,
    SourceUpdate,
)
from .validation import (
    IssueSeverity,
    ValidationIssue,
    ValidationListItem,
    ValidationListResponse,
    ValidationResponse,
    ValidationRunRequest,
    ValidationStatus,
    ValidationSummary,
)

__all__ = [
    # Base
    "BaseSchema",
    "IDMixin",
    "TimestampMixin",
    "ResponseWrapper",
    "ListResponseWrapper",
    "ErrorResponse",
    "MessageResponse",
    # Source
    "SourceType",
    "SourceBase",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "SourceListResponse",
    "SourceSummary",
    # Rule
    "RuleBase",
    "RuleCreate",
    "RuleUpdate",
    "RuleResponse",
    "RuleListItem",
    "RuleListResponse",
    "RuleSummary",
    # Validation
    "ValidationStatus",
    "IssueSeverity",
    "ValidationIssue",
    "ValidationRunRequest",
    "ValidationSummary",
    "ValidationResponse",
    "ValidationListItem",
    "ValidationListResponse",
    # Schema
    "ColumnSchema",
    "SchemaLearnRequest",
    "SchemaUpdateRequest",
    "SchemaResponse",
    "SchemaSummary",
    # Profile
    "ColumnProfile",
    "ProfileResponse",
    # History
    "TrendDataPoint",
    "FailureFrequencyItem",
    "RecentValidation",
    "HistorySummary",
    "HistoryResponse",
    "HistoryQueryParams",
    # Drift
    "DriftCompareRequest",
    "ColumnDriftResult",
    "DriftResult",
    "DriftSourceSummary",
    "DriftComparisonResponse",
    "DriftComparisonListItem",
    "DriftComparisonListResponse",
    # Schedule
    "ScheduleBase",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleListItem",
    "ScheduleListResponse",
    "ScheduleActionResponse",
    # Phase 5: Glossary
    "TermStatus",
    "RelationshipType",
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategorySummary",
    "CategoryResponse",
    "CategoryListResponse",
    "TermBase",
    "TermCreate",
    "TermUpdate",
    "TermSummary",
    "RelatedTermSummary",
    "TermResponse",
    "TermListItem",
    "TermListResponse",
    "RelationshipBase",
    "RelationshipCreate",
    "RelationshipResponse",
    "RelationshipListResponse",
    "TermHistoryResponse",
    "TermHistoryListResponse",
    # Phase 5: Catalog
    "AssetType",
    "SensitivityLevel",
    "QualityLevel",
    "TagBase",
    "TagCreate",
    "TagResponse",
    "ColumnBase",
    "ColumnCreate",
    "ColumnUpdate",
    "ColumnTermMapping",
    "ColumnResponse",
    "ColumnListResponse",
    "SourceSummary",
    "AssetBase",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetListItem",
    "AssetListResponse",
    # Phase 5: Collaboration
    "ResourceType",
    "ActivityAction",
    "CommentBase",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    "ActivityResponse",
    "ActivityListResponse",
    "ActivityCreate",
]

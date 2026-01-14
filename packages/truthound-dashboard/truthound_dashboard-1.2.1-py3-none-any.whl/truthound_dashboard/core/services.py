"""Business logic services.

This module contains service classes that implement business logic
for the dashboard, separating concerns from API handlers.

Services handle:
- Data source management
- Schema learning and storage
- Validation execution and tracking
- Data profiling with history
- Drift detection
- Schedule management
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Literal

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    BaseRepository,
    DriftComparison,
    Profile,
    Rule,
    Schedule,
    Schema,
    Source,
    Validation,
)

from .truthound_adapter import (
    CheckResult,
    get_adapter,
)


class SourceRepository(BaseRepository[Source]):
    """Repository for Source model operations."""

    model = Source

    async def get_active(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Source]:
        """Get active sources only.

        Args:
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of active sources.
        """
        return await self.list(
            offset=offset,
            limit=limit,
            filters=[Source.is_active],
        )

    async def get_by_name(self, name: str) -> Source | None:
        """Get source by name.

        Args:
            name: Source name to find.

        Returns:
            Source or None if not found.
        """
        result = await self.session.execute(select(Source).where(Source.name == name))
        return result.scalar_one_or_none()


class SchemaRepository(BaseRepository[Schema]):
    """Repository for Schema model operations."""

    model = Schema

    async def get_active_for_source(self, source_id: str) -> Schema | None:
        """Get active schema for a source.

        Args:
            source_id: Source ID.

        Returns:
            Active schema or None.
        """
        result = await self.session.execute(
            select(Schema)
            .where(Schema.source_id == source_id)
            .where(Schema.is_active)
            .order_by(Schema.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def deactivate_for_source(self, source_id: str) -> None:
        """Deactivate all schemas for a source.

        Args:
            source_id: Source ID.
        """
        result = await self.session.execute(
            select(Schema).where(Schema.source_id == source_id).where(Schema.is_active)
        )
        schemas = result.scalars().all()
        for schema in schemas:
            schema.is_active = False


class RuleRepository(BaseRepository[Rule]):
    """Repository for Rule model operations."""

    model = Rule

    async def get_for_source(
        self,
        source_id: str,
        *,
        limit: int = 50,
        active_only: bool = False,
    ) -> Sequence[Rule]:
        """Get rules for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.
            active_only: Only return active rules.

        Returns:
            Sequence of rules.
        """
        filters = [Rule.source_id == source_id]
        if active_only:
            filters.append(Rule.is_active)

        return await self.list(
            limit=limit,
            filters=filters,
            order_by=Rule.created_at.desc(),
        )

    async def get_active_for_source(self, source_id: str) -> Rule | None:
        """Get most recent active rule for a source.

        Args:
            source_id: Source ID.

        Returns:
            Active rule or None.
        """
        result = await self.session.execute(
            select(Rule)
            .where(Rule.source_id == source_id)
            .where(Rule.is_active)
            .order_by(Rule.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def deactivate_for_source(self, source_id: str) -> int:
        """Deactivate all rules for a source.

        Args:
            source_id: Source ID.

        Returns:
            Number of rules deactivated.
        """
        result = await self.session.execute(
            select(Rule).where(Rule.source_id == source_id).where(Rule.is_active)
        )
        rules = result.scalars().all()
        for rule in rules:
            rule.is_active = False
        return len(rules)


class ValidationRepository(BaseRepository[Validation]):
    """Repository for Validation model operations."""

    model = Validation

    async def get_for_source(
        self,
        source_id: str,
        *,
        limit: int = 20,
    ) -> Sequence[Validation]:
        """Get validations for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of validations.
        """
        return await self.list(
            limit=limit,
            filters=[Validation.source_id == source_id],
            order_by=Validation.created_at.desc(),
        )

    async def get_latest_for_source(self, source_id: str) -> Validation | None:
        """Get most recent validation for a source.

        Args:
            source_id: Source ID.

        Returns:
            Latest validation or None.
        """
        result = await self.session.execute(
            select(Validation)
            .where(Validation.source_id == source_id)
            .order_by(Validation.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class SourceService:
    """Service for managing data sources.

    Handles source CRUD operations and related business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.repository = SourceRepository(session)
        self.schema_repo = SchemaRepository(session)
        self.validation_repo = ValidationRepository(session)

    async def get_by_id(self, id: str) -> Source | None:
        """Get source by ID."""
        return await self.repository.get_by_id(id)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> Sequence[Source]:
        """List sources.

        Args:
            offset: Number to skip.
            limit: Maximum to return.
            active_only: Only return active sources.

        Returns:
            Sequence of sources.
        """
        if active_only:
            return await self.repository.get_active(offset=offset, limit=limit)
        return await self.repository.list(offset=offset, limit=limit)

    async def create(
        self,
        *,
        name: str,
        type: str,
        config: dict[str, Any],
        description: str | None = None,
    ) -> Source:
        """Create new source.

        Args:
            name: Source name.
            type: Source type (file, postgresql, etc.).
            config: Source configuration.
            description: Optional description.

        Returns:
            Created source.
        """
        return await self.repository.create(
            name=name,
            type=type,
            config=config,
            description=description,
        )

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> Source | None:
        """Update source.

        Args:
            id: Source ID.
            name: New name.
            config: New config.
            description: New description.
            is_active: New active status.

        Returns:
            Updated source or None.
        """
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if config is not None:
            update_data["config"] = config
        if description is not None:
            update_data["description"] = description
        if is_active is not None:
            update_data["is_active"] = is_active

        if not update_data:
            return await self.repository.get_by_id(id)

        return await self.repository.update(id, **update_data)

    async def delete(self, id: str) -> bool:
        """Delete source and related data.

        Args:
            id: Source ID.

        Returns:
            True if deleted.
        """
        return await self.repository.delete(id)

    async def get_schema(self, source_id: str) -> Schema | None:
        """Get active schema for source.

        Args:
            source_id: Source ID.

        Returns:
            Active schema or None.
        """
        return await self.schema_repo.get_active_for_source(source_id)

    async def get_validations(
        self,
        source_id: str,
        *,
        limit: int = 20,
    ) -> Sequence[Validation]:
        """Get validations for source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of validations.
        """
        return await self.validation_repo.get_for_source(source_id, limit=limit)


class ValidationService:
    """Service for running and managing validations.

    Handles validation execution, result storage, and history.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.schema_repo = SchemaRepository(session)
        self.validation_repo = ValidationRepository(session)
        self.adapter = get_adapter()

    async def run_validation(
        self,
        source_id: str,
        *,
        validators: list[str] | None = None,
        schema_path: str | None = None,
        auto_schema: bool = False,
    ) -> Validation:
        """Run validation on a source.

        Args:
            source_id: Source ID to validate.
            validators: Optional validator list.
            schema_path: Optional schema file path.
            auto_schema: Auto-learn schema if True.

        Returns:
            Validation record with results.

        Raises:
            ValueError: If source not found.
        """
        # Get source
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source '{source_id}' not found")

        # Create validation record
        validation = await self.validation_repo.create(
            source_id=source_id,
            status="running",
            started_at=datetime.utcnow(),
        )

        try:
            # Run validation
            result = await self.adapter.check(
                source.source_path or "",
                validators=validators,
                schema=schema_path,
                auto_schema=auto_schema,
            )

            # Update validation with results
            await self._update_validation_success(validation, result)

            # Update source last validated
            source.last_validated_at = datetime.utcnow()

        except Exception as e:
            # Update validation with error
            validation.mark_error(str(e))

        await self.session.flush()
        await self.session.refresh(validation)
        return validation

    async def _update_validation_success(
        self,
        validation: Validation,
        result: CheckResult,
    ) -> None:
        """Update validation with successful result.

        Args:
            validation: Validation record to update.
            result: Check result from adapter.
        """
        validation.status = "success" if result.passed else "failed"
        validation.passed = result.passed
        validation.has_critical = result.has_critical
        validation.has_high = result.has_high
        validation.total_issues = result.total_issues
        validation.critical_issues = result.critical_issues
        validation.high_issues = result.high_issues
        validation.medium_issues = result.medium_issues
        validation.low_issues = result.low_issues
        validation.row_count = result.row_count
        validation.column_count = result.column_count
        validation.result_json = result.to_dict()
        validation.completed_at = datetime.utcnow()

        if validation.started_at:
            delta = validation.completed_at - validation.started_at
            validation.duration_ms = int(delta.total_seconds() * 1000)

    async def get_validation(self, validation_id: str) -> Validation | None:
        """Get validation by ID.

        Args:
            validation_id: Validation ID.

        Returns:
            Validation or None.
        """
        return await self.validation_repo.get_by_id(validation_id)

    async def list_for_source(
        self,
        source_id: str,
        *,
        limit: int = 20,
    ) -> Sequence[Validation]:
        """List validations for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of validations.
        """
        return await self.validation_repo.get_for_source(source_id, limit=limit)


class SchemaService:
    """Service for schema learning and management.

    Handles schema learning, storage, and retrieval.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.schema_repo = SchemaRepository(session)
        self.adapter = get_adapter()

    async def learn_schema(
        self,
        source_id: str,
        *,
        infer_constraints: bool = True,
    ) -> Schema:
        """Learn and store schema for a source.

        Args:
            source_id: Source ID.
            infer_constraints: Infer constraints from data.

        Returns:
            Created schema record.

        Raises:
            ValueError: If source not found.
        """
        # Get source
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source '{source_id}' not found")

        # Learn schema
        result = await self.adapter.learn(
            source.source_path or "",
            infer_constraints=infer_constraints,
        )

        # Deactivate existing schemas
        await self.schema_repo.deactivate_for_source(source_id)

        # Create new schema
        schema = await self.schema_repo.create(
            source_id=source_id,
            schema_yaml=result.schema_yaml,
            schema_json=result.schema,
            row_count=result.row_count,
            column_count=result.column_count,
            is_active=True,
        )

        return schema

    async def get_schema(self, source_id: str) -> Schema | None:
        """Get active schema for source.

        Args:
            source_id: Source ID.

        Returns:
            Active schema or None.
        """
        return await self.schema_repo.get_active_for_source(source_id)

    async def update_schema(
        self,
        source_id: str,
        schema_yaml: str,
    ) -> Schema | None:
        """Update schema YAML for a source.

        Args:
            source_id: Source ID.
            schema_yaml: New schema YAML.

        Returns:
            Updated schema or None.
        """
        import yaml

        schema = await self.schema_repo.get_active_for_source(source_id)
        if schema is None:
            return None

        # Parse and update
        try:
            schema_json = yaml.safe_load(schema_yaml)
        except yaml.YAMLError:
            schema_json = None

        schema.schema_yaml = schema_yaml
        schema.schema_json = schema_json

        await self.session.flush()
        await self.session.refresh(schema)
        return schema


class RuleService:
    """Service for managing custom validation rules.

    Handles rule CRUD operations and YAML parsing.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.rule_repo = RuleRepository(session)

    async def get_rule(self, rule_id: str) -> Rule | None:
        """Get rule by ID.

        Args:
            rule_id: Rule ID.

        Returns:
            Rule or None.
        """
        return await self.rule_repo.get_by_id(rule_id)

    async def get_rules_for_source(
        self,
        source_id: str,
        *,
        limit: int = 50,
        active_only: bool = False,
    ) -> Sequence[Rule]:
        """Get all rules for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.
            active_only: Only return active rules.

        Returns:
            Sequence of rules.
        """
        return await self.rule_repo.get_for_source(
            source_id,
            limit=limit,
            active_only=active_only,
        )

    async def get_active_rule(self, source_id: str) -> Rule | None:
        """Get the active rule for a source.

        Args:
            source_id: Source ID.

        Returns:
            Active rule or None.
        """
        return await self.rule_repo.get_active_for_source(source_id)

    async def create_rule(
        self,
        source_id: str,
        *,
        rules_yaml: str,
        name: str = "Default Rules",
        description: str | None = None,
        version: str | None = None,
        activate: bool = True,
    ) -> Rule:
        """Create a new rule for a source.

        Args:
            source_id: Source ID.
            rules_yaml: YAML content defining rules.
            name: Human-readable name.
            description: Optional description.
            version: Optional version string.
            activate: Whether to make this the active rule.

        Returns:
            Created rule.

        Raises:
            ValueError: If source not found or YAML is invalid.
        """
        import yaml

        # Verify source exists
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source '{source_id}' not found")

        # Parse YAML
        try:
            rules_json = yaml.safe_load(rules_yaml)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        # Deactivate existing rules if activating this one
        if activate:
            await self.rule_repo.deactivate_for_source(source_id)

        # Create rule
        rule = await self.rule_repo.create(
            source_id=source_id,
            name=name,
            description=description,
            rules_yaml=rules_yaml,
            rules_json=rules_json,
            is_active=activate,
            version=version,
        )

        return rule

    async def update_rule(
        self,
        rule_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        rules_yaml: str | None = None,
        version: str | None = None,
        is_active: bool | None = None,
    ) -> Rule | None:
        """Update an existing rule.

        Args:
            rule_id: Rule ID.
            name: New name.
            description: New description.
            rules_yaml: New YAML content.
            version: New version.
            is_active: New active status.

        Returns:
            Updated rule or None if not found.

        Raises:
            ValueError: If YAML is invalid.
        """
        import yaml

        rule = await self.rule_repo.get_by_id(rule_id)
        if rule is None:
            return None

        # Update fields
        if name is not None:
            rule.name = name
        if description is not None:
            rule.description = description
        if version is not None:
            rule.version = version

        # Update YAML and parse
        if rules_yaml is not None:
            try:
                rules_json = yaml.safe_load(rules_yaml)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}")
            rule.rules_yaml = rules_yaml
            rule.rules_json = rules_json

        # Handle activation
        if is_active is not None:
            if is_active and not rule.is_active:
                # Deactivate other rules when activating this one
                await self.rule_repo.deactivate_for_source(rule.source_id)
            rule.is_active = is_active

        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule.

        Args:
            rule_id: Rule ID.

        Returns:
            True if deleted.
        """
        return await self.rule_repo.delete(rule_id)

    async def activate_rule(self, rule_id: str) -> Rule | None:
        """Activate a rule and deactivate others for the same source.

        Args:
            rule_id: Rule ID to activate.

        Returns:
            Activated rule or None if not found.
        """
        rule = await self.rule_repo.get_by_id(rule_id)
        if rule is None:
            return None

        # Deactivate other rules
        await self.rule_repo.deactivate_for_source(rule.source_id)

        # Activate this rule
        rule.is_active = True

        await self.session.flush()
        await self.session.refresh(rule)
        return rule


class ProfileRepository(BaseRepository[Profile]):
    """Repository for Profile model operations."""

    model = Profile

    async def get_for_source(
        self,
        source_id: str,
        *,
        limit: int = 20,
    ) -> Sequence[Profile]:
        """Get profiles for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of profiles.
        """
        return await self.list(
            limit=limit,
            filters=[Profile.source_id == source_id],
            order_by=Profile.created_at.desc(),
        )

    async def get_latest_for_source(self, source_id: str) -> Profile | None:
        """Get most recent profile for a source.

        Args:
            source_id: Source ID.

        Returns:
            Latest profile or None.
        """
        result = await self.session.execute(
            select(Profile)
            .where(Profile.source_id == source_id)
            .order_by(Profile.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ScheduleRepository(BaseRepository[Schedule]):
    """Repository for Schedule model operations."""

    model = Schedule

    async def get_active(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Schedule]:
        """Get active schedules only.

        Args:
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of active schedules.
        """
        return await self.list(
            offset=offset,
            limit=limit,
            filters=[Schedule.is_active],
        )

    async def get_for_source(
        self,
        source_id: str,
        *,
        limit: int = 50,
    ) -> Sequence[Schedule]:
        """Get schedules for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of schedules.
        """
        return await self.list(
            limit=limit,
            filters=[Schedule.source_id == source_id],
            order_by=Schedule.created_at.desc(),
        )


class DriftComparisonRepository(BaseRepository[DriftComparison]):
    """Repository for DriftComparison model operations."""

    model = DriftComparison

    async def get_for_sources(
        self,
        baseline_source_id: str | None = None,
        current_source_id: str | None = None,
        *,
        limit: int = 20,
    ) -> Sequence[DriftComparison]:
        """Get drift comparisons for sources.

        Args:
            baseline_source_id: Optional baseline source ID.
            current_source_id: Optional current source ID.
            limit: Maximum to return.

        Returns:
            Sequence of drift comparisons.
        """
        filters = []
        if baseline_source_id:
            filters.append(DriftComparison.baseline_source_id == baseline_source_id)
        if current_source_id:
            filters.append(DriftComparison.current_source_id == current_source_id)

        return await self.list(
            limit=limit,
            filters=filters if filters else None,
            order_by=DriftComparison.created_at.desc(),
        )

    async def get_latest(
        self,
        baseline_source_id: str,
        current_source_id: str,
    ) -> DriftComparison | None:
        """Get latest comparison between two sources.

        Args:
            baseline_source_id: Baseline source ID.
            current_source_id: Current source ID.

        Returns:
            Latest comparison or None.
        """
        result = await self.session.execute(
            select(DriftComparison)
            .where(
                and_(
                    DriftComparison.baseline_source_id == baseline_source_id,
                    DriftComparison.current_source_id == current_source_id,
                )
            )
            .order_by(DriftComparison.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ProfileService:
    """Service for data profiling with history tracking.

    Handles data profiling operations and stores results.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.adapter = get_adapter()

    async def profile_source(self, source_id: str, *, save: bool = True) -> Profile:
        """Profile a data source and optionally save result.

        Args:
            source_id: Source ID to profile.
            save: Whether to save profile to database.

        Returns:
            Profile model with results.

        Raises:
            ValueError: If source not found.
        """
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source '{source_id}' not found")

        result = await self.adapter.profile(source.source_path or "")

        if save:
            profile = await self.profile_repo.create(
                source_id=source_id,
                profile_json=result.to_dict(),
                row_count=result.row_count,
                column_count=result.column_count,
                size_bytes=result.size_bytes,
            )
            return profile

        # Return unsaved profile object
        profile = Profile(
            source_id=source_id,
            profile_json=result.to_dict(),
            row_count=result.row_count,
            column_count=result.column_count,
            size_bytes=result.size_bytes,
        )
        return profile

    async def get_latest_profile(self, source_id: str) -> Profile | None:
        """Get the latest profile for a source.

        Args:
            source_id: Source ID.

        Returns:
            Latest profile or None.
        """
        return await self.profile_repo.get_latest_for_source(source_id)

    async def list_profiles(
        self,
        source_id: str,
        *,
        limit: int = 20,
    ) -> Sequence[Profile]:
        """List profiles for a source.

        Args:
            source_id: Source ID.
            limit: Maximum to return.

        Returns:
            Sequence of profiles.
        """
        return await self.profile_repo.get_for_source(source_id, limit=limit)


class HistoryService:
    """Service for validation history and analytics.

    Provides aggregated views of validation history with trend analysis.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.validation_repo = ValidationRepository(session)

    async def get_history(
        self,
        source_id: str,
        *,
        period: Literal["7d", "30d", "90d"] = "30d",
        granularity: Literal["hourly", "daily", "weekly"] = "daily",
    ) -> dict[str, Any]:
        """Get validation history with trend data.

        Args:
            source_id: Source ID.
            period: Time period to analyze.
            granularity: Aggregation granularity.

        Returns:
            Dictionary with summary, trend, failure_frequency, and recent_validations.
        """
        days = {"7d": 7, "30d": 30, "90d": 90}[period]
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get validations in period
        result = await self.session.execute(
            select(Validation)
            .where(Validation.source_id == source_id)
            .where(Validation.created_at >= start_date)
            .order_by(Validation.created_at.desc())
        )
        validations = list(result.scalars().all())

        # Calculate statistics
        total_runs = len(validations)
        passed_runs = sum(1 for v in validations if v.passed)
        failed_runs = sum(1 for v in validations if v.passed is False)
        success_rate = (passed_runs / total_runs * 100) if total_runs > 0 else 0

        # Aggregate by granularity
        trend_data = self._aggregate_by_period(validations, granularity)

        # Calculate failure frequency
        failure_frequency = self._calculate_failure_frequency(validations)

        # Recent validations (top 10)
        recent_validations = [
            {
                "id": v.id,
                "status": v.status,
                "passed": v.passed,
                "has_critical": v.has_critical,
                "has_high": v.has_high,
                "total_issues": v.total_issues,
                "created_at": v.created_at.isoformat(),
            }
            for v in validations[:10]
        ]

        return {
            "summary": {
                "total_runs": total_runs,
                "passed_runs": passed_runs,
                "failed_runs": failed_runs,
                "success_rate": round(success_rate, 2),
            },
            "trend": trend_data,
            "failure_frequency": failure_frequency,
            "recent_validations": recent_validations,
        }

    def _aggregate_by_period(
        self,
        validations: list[Validation],
        granularity: Literal["hourly", "daily", "weekly"],
    ) -> list[dict[str, Any]]:
        """Aggregate validations by time period."""
        buckets: dict[str, list[Validation]] = defaultdict(list)

        for v in validations:
            if granularity == "hourly":
                key = v.created_at.strftime("%Y-%m-%d %H:00")
            elif granularity == "daily":
                key = v.created_at.strftime("%Y-%m-%d")
            else:  # weekly
                monday = v.created_at - timedelta(days=v.created_at.weekday())
                key = monday.strftime("%Y-%m-%d")

            buckets[key].append(v)

        trend = []
        for date, vals in sorted(buckets.items()):
            passed_count = sum(1 for v in vals if v.passed)
            success_rate = (passed_count / len(vals) * 100) if vals else 0
            trend.append(
                {
                    "date": date,
                    "success_rate": round(success_rate, 2),
                    "run_count": len(vals),
                    "passed_count": passed_count,
                    "failed_count": len(vals) - passed_count,
                }
            )

        return trend

    def _calculate_failure_frequency(
        self,
        validations: list[Validation],
    ) -> list[dict[str, Any]]:
        """Calculate failure frequency by issue type."""
        failures: Counter[str] = Counter()

        for v in validations:
            if v.result_json and "issues" in v.result_json:
                for issue in v.result_json["issues"]:
                    key = f"{issue.get('column', 'unknown')}.{issue.get('issue_type', 'unknown')}"
                    failures[key] += issue.get("count", 1)

        return [
            {"issue": issue, "count": count}
            for issue, count in failures.most_common(10)
        ]


class DriftService:
    """Service for drift detection.

    Handles drift comparison between datasets.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.drift_repo = DriftComparisonRepository(session)
        self.adapter = get_adapter()

    async def compare(
        self,
        baseline_source_id: str,
        current_source_id: str,
        *,
        columns: list[str] | None = None,
        method: str = "auto",
        threshold: float | None = None,
        sample_size: int | None = None,
        save: bool = True,
    ) -> DriftComparison:
        """Compare two datasets for drift detection.

        Args:
            baseline_source_id: Baseline source ID.
            current_source_id: Current source ID.
            columns: Optional list of columns to compare.
            method: Detection method.
            threshold: Optional custom threshold.
            sample_size: Optional sample size.
            save: Whether to save comparison to database.

        Returns:
            DriftComparison model with results.

        Raises:
            ValueError: If source not found.
        """
        baseline = await self.source_repo.get_by_id(baseline_source_id)
        if baseline is None:
            raise ValueError(f"Baseline source '{baseline_source_id}' not found")

        current = await self.source_repo.get_by_id(current_source_id)
        if current is None:
            raise ValueError(f"Current source '{current_source_id}' not found")

        result = await self.adapter.compare(
            baseline.source_path or "",
            current.source_path or "",
            columns=columns,
            method=method,
            threshold=threshold,
            sample_size=sample_size,
        )

        config = {
            "columns": columns,
            "method": method,
            "threshold": threshold,
            "sample_size": sample_size,
        }

        if save:
            comparison = await self.drift_repo.create(
                baseline_source_id=baseline_source_id,
                current_source_id=current_source_id,
                has_drift=result.has_drift,
                has_high_drift=result.has_high_drift,
                total_columns=result.total_columns,
                drifted_columns=len(result.drifted_columns),
                result_json=result.to_dict(),
                config=config,
            )
            return comparison

        # Return unsaved comparison object
        comparison = DriftComparison(
            baseline_source_id=baseline_source_id,
            current_source_id=current_source_id,
            has_drift=result.has_drift,
            has_high_drift=result.has_high_drift,
            total_columns=result.total_columns,
            drifted_columns=len(result.drifted_columns),
            result_json=result.to_dict(),
            config=config,
        )
        return comparison

    async def get_comparison(self, comparison_id: str) -> DriftComparison | None:
        """Get a drift comparison by ID.

        Args:
            comparison_id: Comparison ID.

        Returns:
            DriftComparison or None.
        """
        return await self.drift_repo.get_by_id(comparison_id)

    async def list_comparisons(
        self,
        *,
        baseline_source_id: str | None = None,
        current_source_id: str | None = None,
        limit: int = 20,
    ) -> Sequence[DriftComparison]:
        """List drift comparisons.

        Args:
            baseline_source_id: Optional baseline source ID filter.
            current_source_id: Optional current source ID filter.
            limit: Maximum to return.

        Returns:
            Sequence of drift comparisons.
        """
        return await self.drift_repo.get_for_sources(
            baseline_source_id=baseline_source_id,
            current_source_id=current_source_id,
            limit=limit,
        )


class ScheduleService:
    """Service for managing validation schedules.

    Handles schedule CRUD and integrates with APScheduler.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.source_repo = SourceRepository(session)
        self.schedule_repo = ScheduleRepository(session)

    async def create_schedule(
        self,
        source_id: str,
        *,
        name: str,
        cron_expression: str,
        notify_on_failure: bool = True,
        config: dict[str, Any] | None = None,
    ) -> Schedule:
        """Create a new schedule.

        Args:
            source_id: Source ID to schedule.
            name: Schedule name.
            cron_expression: Cron expression.
            notify_on_failure: Send notification on failure.
            config: Additional configuration.

        Returns:
            Created schedule.

        Raises:
            ValueError: If source not found or invalid cron expression.
        """
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Source '{source_id}' not found")

        # Validate cron expression
        next_run = self._get_next_run(cron_expression)

        schedule = await self.schedule_repo.create(
            name=name,
            source_id=source_id,
            cron_expression=cron_expression,
            is_active=True,
            notify_on_failure=notify_on_failure,
            next_run_at=next_run,
            config=config,
        )

        return schedule

    async def get_schedule(self, schedule_id: str) -> Schedule | None:
        """Get schedule by ID.

        Args:
            schedule_id: Schedule ID.

        Returns:
            Schedule or None.
        """
        return await self.schedule_repo.get_by_id(schedule_id)

    async def list_schedules(
        self,
        *,
        source_id: str | None = None,
        active_only: bool = False,
        limit: int = 100,
    ) -> Sequence[Schedule]:
        """List schedules.

        Args:
            source_id: Optional source ID filter.
            active_only: Only return active schedules.
            limit: Maximum to return.

        Returns:
            Sequence of schedules.
        """
        if source_id:
            return await self.schedule_repo.get_for_source(source_id, limit=limit)
        if active_only:
            return await self.schedule_repo.get_active(limit=limit)
        return await self.schedule_repo.list(limit=limit)

    async def update_schedule(
        self,
        schedule_id: str,
        *,
        name: str | None = None,
        cron_expression: str | None = None,
        notify_on_failure: bool | None = None,
        config: dict[str, Any] | None = None,
    ) -> Schedule | None:
        """Update a schedule.

        Args:
            schedule_id: Schedule ID.
            name: New name.
            cron_expression: New cron expression.
            notify_on_failure: New notification setting.
            config: New configuration.

        Returns:
            Updated schedule or None.
        """
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if schedule is None:
            return None

        if name is not None:
            schedule.name = name
        if cron_expression is not None:
            schedule.cron_expression = cron_expression
            schedule.next_run_at = self._get_next_run(cron_expression)
        if notify_on_failure is not None:
            schedule.notify_on_failure = notify_on_failure
        if config is not None:
            schedule.config = config

        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule

    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule.

        Args:
            schedule_id: Schedule ID.

        Returns:
            True if deleted.
        """
        return await self.schedule_repo.delete(schedule_id)

    async def pause_schedule(self, schedule_id: str) -> Schedule | None:
        """Pause a schedule.

        Args:
            schedule_id: Schedule ID.

        Returns:
            Updated schedule or None.
        """
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if schedule is None:
            return None

        schedule.pause()
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule

    async def resume_schedule(self, schedule_id: str) -> Schedule | None:
        """Resume a paused schedule.

        Args:
            schedule_id: Schedule ID.

        Returns:
            Updated schedule or None.
        """
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if schedule is None:
            return None

        schedule.resume()
        schedule.next_run_at = self._get_next_run(schedule.cron_expression)
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule

    def _get_next_run(self, cron_expression: str) -> datetime:
        """Calculate next run time from cron expression.

        Args:
            cron_expression: Cron expression.

        Returns:
            Next run datetime.

        Raises:
            ValueError: If invalid cron expression.
        """
        try:
            from apscheduler.triggers.cron import CronTrigger

            trigger = CronTrigger.from_crontab(cron_expression)
            next_fire = trigger.get_next_fire_time(None, datetime.utcnow())
            if next_fire is None:
                raise ValueError("Could not calculate next run time")
            return next_fire
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}")

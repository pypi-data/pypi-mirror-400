"""Tests for Phase 4 production-ready features.

This module tests the Phase 4 components:
- Cache system
- Maintenance tasks
- Exception handling
- Encryption utilities
- Logging configuration
- Middleware
"""

from __future__ import annotations

import logging
from datetime import datetime

import pytest

from truthound_dashboard.core.cache import (
    CacheEntry,
    MemoryCache,
    get_cache,
    reset_cache,
)
from truthound_dashboard.core.encryption import (
    decrypt_config,
    encrypt_config,
    is_sensitive_field,
    mask_sensitive_value,
)
from truthound_dashboard.core.exceptions import (
    ErrorCode,
    RateLimitExceededError,
    SourceNotFoundError,
    TruthoundDashboardError,
    ValidationError,
    get_error_message,
)
from truthound_dashboard.core.logging import (
    ColorFormatter,
    JsonFormatter,
    LogConfig,
    LoggerAdapter,
    get_logger,
)
from truthound_dashboard.core.maintenance import (
    CleanupResult,
    MaintenanceConfig,
    MaintenanceManager,
    MaintenanceReport,
    reset_maintenance_manager,
)


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_not_expired(self):
        """Test that new entry is not expired."""
        entry = CacheEntry("test_value", ttl_seconds=60)
        assert not entry.is_expired
        assert entry.value == "test_value"
        assert entry.remaining_ttl > 0

    def test_cache_entry_expired(self):
        """Test that entry expires after TTL."""
        entry = CacheEntry("test_value", ttl_seconds=0)
        assert entry.is_expired
        assert entry.remaining_ttl == 0


class TestMemoryCache:
    """Test MemoryCache class."""

    @pytest.fixture
    def cache(self):
        """Create a fresh cache instance."""
        return MemoryCache(max_size=100)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache: MemoryCache):
        """Test basic set and get operations."""
        await cache.set("key1", "value1", ttl_seconds=60)
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_missing_key(self, cache: MemoryCache):
        """Test getting a non-existent key."""
        result = await cache.get("missing_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, cache: MemoryCache):
        """Test delete operation."""
        await cache.set("key1", "value1", ttl_seconds=60)
        deleted = await cache.delete("key1")
        assert deleted is True

        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_clear(self, cache: MemoryCache):
        """Test clear operation."""
        await cache.set("key1", "value1", ttl_seconds=60)
        await cache.set("key2", "value2", ttl_seconds=60)
        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_exists(self, cache: MemoryCache):
        """Test exists operation."""
        await cache.set("key1", "value1", ttl_seconds=60)

        assert await cache.exists("key1") is True
        assert await cache.exists("missing_key") is False

    @pytest.mark.asyncio
    async def test_get_or_set(self, cache: MemoryCache):
        """Test get_or_set operation."""
        # First call should compute and cache
        result = await cache.get_or_set(
            "key1", lambda: "computed_value", ttl_seconds=60
        )
        assert result == "computed_value"

        # Second call should return cached value
        result = await cache.get_or_set("key1", lambda: "new_value", ttl_seconds=60)
        assert result == "computed_value"

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, cache: MemoryCache):
        """Test pattern-based invalidation."""
        await cache.set("user:1", "data1", ttl_seconds=60)
        await cache.set("user:2", "data2", ttl_seconds=60)
        await cache.set("other:1", "data3", ttl_seconds=60)

        count = await cache.invalidate_pattern("user:")
        assert count == 2

        assert await cache.get("user:1") is None
        assert await cache.get("user:2") is None
        assert await cache.get("other:1") == "data3"

    @pytest.mark.asyncio
    async def test_eviction_on_max_size(self, cache: MemoryCache):
        """Test that old entries are evicted when max size is reached."""
        small_cache = MemoryCache(max_size=5)

        for i in range(10):
            await small_cache.set(f"key{i}", f"value{i}", ttl_seconds=60)

        # Should have evicted some entries
        assert small_cache.size <= 5


class TestExceptions:
    """Test exception classes."""

    def test_base_exception(self):
        """Test TruthoundDashboardError."""
        exc = TruthoundDashboardError("Test error", details={"key": "value"})

        assert exc.message == "Test error"
        assert exc.code == ErrorCode.UNKNOWN_ERROR
        assert exc.http_status == 500
        assert exc.details == {"key": "value"}

    def test_source_not_found_error(self):
        """Test SourceNotFoundError."""
        exc = SourceNotFoundError("source-123")

        assert exc.code == ErrorCode.SOURCE_NOT_FOUND
        assert exc.http_status == 404
        assert "source-123" in str(exc.details)

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Validation failed")

        assert exc.code == ErrorCode.VALIDATION_ERROR
        assert exc.http_status == 400

    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError."""
        exc = RateLimitExceededError(retry_after=60)

        assert exc.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert exc.http_status == 429
        assert exc.details.get("retry_after") == 60

    def test_to_response(self):
        """Test exception to response conversion."""
        exc = SourceNotFoundError("source-123")
        response = exc.to_response()

        assert response["success"] is False
        assert response["error"]["code"] == ErrorCode.SOURCE_NOT_FOUND.value
        assert "message" in response["error"]

    def test_get_error_message_english(self):
        """Test getting error message in English."""
        message = get_error_message(ErrorCode.SOURCE_NOT_FOUND, lang="en")
        assert "source" in message.lower() or "found" in message.lower()

    def test_get_error_message_korean(self):
        """Test getting error message in Korean."""
        message = get_error_message(ErrorCode.SOURCE_NOT_FOUND, lang="ko")
        assert "소스" in message or "찾을" in message


class TestEncryption:
    """Test encryption utilities."""

    def test_is_sensitive_field(self):
        """Test sensitive field detection."""
        assert is_sensitive_field("password") is True
        assert is_sensitive_field("api_key") is True
        assert is_sensitive_field("database_password") is True
        assert is_sensitive_field("username") is False
        assert is_sensitive_field("host") is False

    def test_mask_sensitive_value(self):
        """Test value masking."""
        masked = mask_sensitive_value("mysecretpassword123", visible_chars=4)
        assert masked == "***d123"

        masked = mask_sensitive_value("abc", visible_chars=4)
        assert masked == "***"

    def test_encrypt_config(self):
        """Test config encryption."""
        config = {
            "host": "localhost",
            "port": 5432,
            "password": "secret123",
            "nested": {
                "api_key": "key123",
                "name": "test",
            },
        }

        encrypted = encrypt_config(config)

        # Non-sensitive fields unchanged
        assert encrypted["host"] == "localhost"
        assert encrypted["port"] == 5432

        # Sensitive fields encrypted
        assert "_encrypted" in encrypted.get("password", {})
        assert "_encrypted" in encrypted.get("nested", {}).get("api_key", {})
        assert encrypted["nested"]["name"] == "test"

    def test_decrypt_config(self):
        """Test config decryption (round-trip)."""
        config = {
            "host": "localhost",
            "password": "secret123",
        }

        encrypted = encrypt_config(config)
        decrypted = decrypt_config(encrypted)

        assert decrypted["host"] == "localhost"
        assert decrypted["password"] == "secret123"


class TestLogging:
    """Test logging utilities."""

    def test_log_config_defaults(self):
        """Test LogConfig default values."""
        config = LogConfig()

        assert config.level == "INFO"
        assert config.log_to_file is True
        assert config.json_format is False

    def test_json_formatter(self):
        """Test JsonFormatter output."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        assert "Test message" in output
        assert "INFO" in output

    def test_color_formatter(self):
        """Test ColorFormatter output."""
        formatter = ColorFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        assert "Test message" in output

    def test_logger_adapter(self):
        """Test LoggerAdapter with context."""
        base_logger = logging.getLogger("test")
        adapter = LoggerAdapter(base_logger, {"request_id": "abc123"})

        # Create new adapter with additional context
        new_adapter = adapter.with_context(user_id="user1")

        assert new_adapter.extra["request_id"] == "abc123"
        assert new_adapter.extra["user_id"] == "user1"

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger(__name__, component="test")

        assert isinstance(logger, LoggerAdapter)
        assert logger.extra["component"] == "test"


class TestMaintenance:
    """Test maintenance utilities."""

    def test_cleanup_result(self):
        """Test CleanupResult dataclass."""
        result = CleanupResult(
            task_name="test_cleanup",
            records_deleted=100,
            duration_ms=500,
            success=True,
        )

        assert result.task_name == "test_cleanup"
        assert result.records_deleted == 100
        assert result.success is True

        data = result.to_dict()
        assert data["task_name"] == "test_cleanup"

    def test_maintenance_config_defaults(self):
        """Test MaintenanceConfig default values."""
        config = MaintenanceConfig()

        assert config.validation_retention_days == 90
        assert config.profile_keep_per_source == 5
        assert config.notification_log_retention_days == 30
        assert config.run_vacuum is True
        assert config.enabled is True

    def test_maintenance_report(self):
        """Test MaintenanceReport aggregation."""
        report = MaintenanceReport(started_at=datetime.utcnow())
        report.results.append(
            CleanupResult(task_name="task1", records_deleted=50, success=True)
        )
        report.results.append(
            CleanupResult(task_name="task2", records_deleted=30, success=True)
        )
        report.completed_at = datetime.utcnow()

        assert report.total_deleted == 80
        assert report.success is True

    def test_maintenance_manager_registration(self):
        """Test MaintenanceManager strategy registration."""
        reset_maintenance_manager()
        manager = MaintenanceManager()

        assert len(manager._strategies) == 0

        manager.register_default_strategies()
        assert len(manager._strategies) == 3  # validation, profile, notification logs


class TestMiddleware:
    """Test middleware components."""

    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values."""
        from truthound_dashboard.api.middleware import RateLimitConfig

        config = RateLimitConfig()
        assert config.requests_per_minute == 60
        assert config.by_ip is True

    def test_security_headers_config_defaults(self):
        """Test SecurityHeadersConfig default values."""
        from truthound_dashboard.api.middleware import SecurityHeadersConfig

        config = SecurityHeadersConfig()
        assert config.content_type_options == "nosniff"
        assert config.frame_options == "DENY"
        assert config.xss_protection == "1; mode=block"


class TestSampling:
    """Test data sampling utilities."""

    def test_sampling_method_enum(self):
        """Test SamplingMethod enum values."""
        from truthound_dashboard.core.sampling import SamplingMethod

        assert SamplingMethod.RANDOM.value == "random"
        assert SamplingMethod.HEAD.value == "head"
        assert SamplingMethod.TAIL.value == "tail"
        assert SamplingMethod.STRATIFIED.value == "stratified"
        assert SamplingMethod.RESERVOIR.value == "reservoir"

    def test_sampling_config_defaults(self):
        """Test SamplingConfig default values."""
        from truthound_dashboard.core.sampling import SamplingConfig, SamplingMethod

        config = SamplingConfig()

        assert config.size_threshold_mb == 100.0
        assert config.row_threshold == 1_000_000
        assert config.default_sample_size == 10_000
        assert config.method == SamplingMethod.RANDOM
        assert config.seed == 42
        assert config.cleanup_after_hours == 24

    def test_sampling_result_to_dict(self):
        """Test SamplingResult conversion to dict."""
        from truthound_dashboard.core.sampling import SamplingMethod, SamplingResult

        result = SamplingResult(
            original_path="/path/to/data.csv",
            sampled_path="/path/to/sample.parquet",
            was_sampled=True,
            original_rows=1_000_000,
            sampled_rows=10_000,
            method=SamplingMethod.RANDOM,
            size_reduction_pct=95.5,
        )

        data = result.to_dict()

        assert data["original_path"] == "/path/to/data.csv"
        assert data["sampled_path"] == "/path/to/sample.parquet"
        assert data["was_sampled"] is True
        assert data["original_rows"] == 1_000_000
        assert data["sampled_rows"] == 10_000
        assert data["method"] == "random"
        assert data["size_reduction_pct"] == 95.5

    def test_sampling_result_not_sampled(self):
        """Test SamplingResult when no sampling occurred."""
        from truthound_dashboard.core.sampling import SamplingResult

        result = SamplingResult(
            original_path="/path/to/small.csv",
            sampled_path="/path/to/small.csv",
            was_sampled=False,
        )

        data = result.to_dict()

        assert data["was_sampled"] is False
        assert data["method"] is None
        assert data["original_rows"] is None

    def test_random_sampling_strategy(self):
        """Test RandomSamplingStrategy."""
        from truthound_dashboard.core.sampling import (
            RandomSamplingStrategy,
            SamplingMethod,
        )

        pytest.importorskip("polars")
        import polars as pl

        strategy = RandomSamplingStrategy()
        assert strategy.method == SamplingMethod.RANDOM

        # Create test dataframe
        df = pl.DataFrame({"a": range(100), "b": range(100)})

        # Sample should be smaller
        sampled = strategy.sample(df, n=10, seed=42)
        assert len(sampled) == 10

        # Same seed should give same result
        sampled2 = strategy.sample(df, n=10, seed=42)
        assert sampled.equals(sampled2)

    def test_head_sampling_strategy(self):
        """Test HeadSamplingStrategy."""
        from truthound_dashboard.core.sampling import (
            HeadSamplingStrategy,
            SamplingMethod,
        )

        pytest.importorskip("polars")
        import polars as pl

        strategy = HeadSamplingStrategy()
        assert strategy.method == SamplingMethod.HEAD

        df = pl.DataFrame({"a": range(100)})
        sampled = strategy.sample(df, n=10)

        assert len(sampled) == 10
        assert sampled["a"].to_list() == list(range(10))

    def test_tail_sampling_strategy(self):
        """Test TailSamplingStrategy."""
        from truthound_dashboard.core.sampling import (
            SamplingMethod,
            TailSamplingStrategy,
        )

        pytest.importorskip("polars")
        import polars as pl

        strategy = TailSamplingStrategy()
        assert strategy.method == SamplingMethod.TAIL

        df = pl.DataFrame({"a": range(100)})
        sampled = strategy.sample(df, n=10)

        assert len(sampled) == 10
        assert sampled["a"].to_list() == list(range(90, 100))

    def test_stratified_sampling_strategy(self):
        """Test StratifiedSamplingStrategy."""
        from truthound_dashboard.core.sampling import (
            SamplingMethod,
            StratifiedSamplingStrategy,
        )

        pytest.importorskip("polars")
        import polars as pl

        strategy = StratifiedSamplingStrategy()
        assert strategy.method == SamplingMethod.STRATIFIED

        # Create dataframe with categories
        df = pl.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 30 + ["C"] * 20,
                "value": range(100),
            }
        )

        # Without stratify column, falls back to random
        sampled = strategy.sample(df, n=20, seed=42)
        assert len(sampled) == 20

        # With stratify column, maintains proportions (approximately)
        sampled = strategy.sample(df, n=20, seed=42, stratify_column="category")
        assert len(sampled) <= 20

    def test_data_sampler_singleton(self):
        """Test DataSampler singleton functions."""
        from truthound_dashboard.core.sampling import (
            DataSampler,
            get_sampler,
            reset_sampler,
        )

        reset_sampler()

        sampler1 = get_sampler()
        sampler2 = get_sampler()

        assert sampler1 is sampler2
        assert isinstance(sampler1, DataSampler)

        reset_sampler()
        sampler3 = get_sampler()
        assert sampler3 is not sampler1

    def test_data_sampler_register_custom_strategy(self):
        """Test registering custom sampling strategy."""
        from truthound_dashboard.core.sampling import (
            DataSampler,
            SamplingMethod,
            SamplingStrategy,
        )

        class CustomStrategy(SamplingStrategy):
            @property
            def method(self) -> SamplingMethod:
                return SamplingMethod.RESERVOIR

            def sample(self, df, n, seed=42, **kwargs):
                return df.head(n)

        sampler = DataSampler()
        sampler.register_strategy(CustomStrategy())

        assert SamplingMethod.RESERVOIR in sampler._strategies

    def test_data_sampler_config(self):
        """Test DataSampler configuration."""
        from truthound_dashboard.core.sampling import (
            DataSampler,
            SamplingConfig,
            SamplingMethod,
        )

        config = SamplingConfig(
            size_threshold_mb=50.0,
            default_sample_size=5000,
            method=SamplingMethod.HEAD,
        )
        sampler = DataSampler(config=config)

        assert sampler.config.size_threshold_mb == 50.0
        assert sampler.config.default_sample_size == 5000
        assert sampler.config.method == SamplingMethod.HEAD


@pytest.mark.asyncio
class TestSamplingAsync:
    """Test async sampling operations."""

    async def test_sampler_sample_small_file(self, tmp_path):
        """Test that small files are not sampled."""
        pytest.importorskip("polars")
        import polars as pl

        from truthound_dashboard.core.sampling import (
            DataSampler,
            SamplingConfig,
            reset_sampler,
        )

        reset_sampler()

        # Create small CSV file
        csv_path = tmp_path / "small.csv"
        df = pl.DataFrame({"a": range(100), "b": range(100)})
        df.write_csv(csv_path)

        config = SamplingConfig(
            size_threshold_mb=1000.0,  # Very high threshold
            default_sample_size=50,
        )
        sampler = DataSampler(config=config)

        result = await sampler.auto_sample(str(csv_path))

        assert result.was_sampled is False
        assert result.original_path == str(csv_path)
        assert result.sampled_path == str(csv_path)

    async def test_sampler_file_info(self, tmp_path):
        """Test file info retrieval."""
        pytest.importorskip("polars")
        import polars as pl

        from truthound_dashboard.core.sampling import DataSampler, reset_sampler

        reset_sampler()

        csv_path = tmp_path / "test.csv"
        df = pl.DataFrame({"a": range(1000), "b": range(1000)})
        df.write_csv(csv_path)

        sampler = DataSampler()
        info = sampler.get_file_info(csv_path)

        assert info["path"] == str(csv_path)
        assert info["format"] == "csv"
        assert info["size_bytes"] > 0
        assert info["size_mb"] > 0

    async def test_sampler_needs_sampling(self, tmp_path):
        """Test needs_sampling check."""
        pytest.importorskip("polars")
        import polars as pl

        from truthound_dashboard.core.sampling import (
            DataSampler,
            SamplingConfig,
            reset_sampler,
        )

        reset_sampler()

        csv_path = tmp_path / "test.csv"
        df = pl.DataFrame({"a": range(100)})
        df.write_csv(csv_path)

        # Low threshold - should need sampling
        config_low = SamplingConfig(size_threshold_mb=0.00001)
        sampler_low = DataSampler(config=config_low)
        assert sampler_low.needs_sampling(csv_path) is True

        # High threshold - should not need sampling
        config_high = SamplingConfig(size_threshold_mb=1000.0)
        sampler_high = DataSampler(config=config_high)
        assert sampler_high.needs_sampling(csv_path) is False


# Integration tests would require a running server
# These are skipped by default


@pytest.mark.skip(reason="Requires running server")
class TestIntegration:
    """Integration tests for Phase 4 features."""

    @pytest.mark.asyncio
    async def test_cache_integration(self):
        """Test cache integration with real usage."""
        reset_cache()
        cache = get_cache()

        await cache.set("test_key", {"data": "value"}, ttl_seconds=60)
        result = await cache.get("test_key")

        assert result == {"data": "value"}

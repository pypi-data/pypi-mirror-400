"""Data sampling strategies for large dataset handling.

This module provides an extensible sampling system for handling large datasets
before validation. The Strategy pattern allows adding new sampling methods
without modifying existing code.

Supported formats:
- CSV files
- Parquet files
- JSON/JSONL files

Features:
- Automatic format detection
- Configurable size thresholds
- Multiple sampling strategies (random, head, stratified)
- Memory-efficient streaming for very large files

Example:
    sampler = get_sampler()

    # Check if sampling is needed
    if sampler.needs_sampling("/path/to/large.csv"):
        sampled_path = await sampler.sample("/path/to/large.csv", n=10000)
        # Use sampled_path for validation

    # Or use auto-sample which handles the logic
    data_path = await sampler.auto_sample("/path/to/data.csv")
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from truthound_dashboard.config import get_settings

logger = logging.getLogger(__name__)


class SamplingMethod(str, Enum):
    """Available sampling methods."""

    RANDOM = "random"  # Random sampling across entire dataset
    HEAD = "head"  # Take first N rows (fastest)
    TAIL = "tail"  # Take last N rows
    STRATIFIED = "stratified"  # Stratified sampling by column
    RESERVOIR = "reservoir"  # Reservoir sampling for streaming


@dataclass
class SamplingConfig:
    """Configuration for data sampling.

    Attributes:
        size_threshold_mb: File size threshold in MB to trigger sampling.
        row_threshold: Row count threshold to trigger sampling.
        default_sample_size: Default number of rows to sample.
        method: Default sampling method.
        seed: Random seed for reproducibility.
        temp_dir: Directory for temporary sampled files.
        cleanup_after_hours: Hours to keep temp files before cleanup.
    """

    size_threshold_mb: float = 100.0
    row_threshold: int = 1_000_000
    default_sample_size: int = 10_000
    method: SamplingMethod = SamplingMethod.RANDOM
    seed: int = 42
    temp_dir: Path | None = None
    cleanup_after_hours: int = 24


@dataclass
class SamplingResult:
    """Result of a sampling operation.

    Attributes:
        original_path: Path to original file.
        sampled_path: Path to sampled file (same as original if no sampling).
        was_sampled: Whether sampling was performed.
        original_rows: Number of rows in original file.
        sampled_rows: Number of rows in sampled file.
        method: Sampling method used.
        size_reduction_pct: Percentage reduction in file size.
    """

    original_path: str
    sampled_path: str
    was_sampled: bool
    original_rows: int | None = None
    sampled_rows: int | None = None
    method: SamplingMethod | None = None
    size_reduction_pct: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_path": self.original_path,
            "sampled_path": self.sampled_path,
            "was_sampled": self.was_sampled,
            "original_rows": self.original_rows,
            "sampled_rows": self.sampled_rows,
            "method": self.method.value if self.method else None,
            "size_reduction_pct": round(self.size_reduction_pct, 2),
        }


class SamplingStrategy(ABC):
    """Abstract base class for sampling strategies.

    Subclass this to implement custom sampling methods.
    """

    @property
    @abstractmethod
    def method(self) -> SamplingMethod:
        """Get the sampling method identifier."""
        ...

    @abstractmethod
    def sample(
        self,
        df: Any,
        n: int,
        seed: int = 42,
        **kwargs: Any,
    ) -> Any:
        """Sample data from a DataFrame.

        Args:
            df: DataFrame to sample from.
            n: Number of rows to sample.
            seed: Random seed for reproducibility.
            **kwargs: Additional strategy-specific arguments.

        Returns:
            Sampled DataFrame.
        """
        ...


class RandomSamplingStrategy(SamplingStrategy):
    """Random sampling strategy using reservoir sampling for efficiency."""

    @property
    def method(self) -> SamplingMethod:
        return SamplingMethod.RANDOM

    def sample(
        self,
        df: Any,
        n: int,
        seed: int = 42,
        **kwargs: Any,
    ) -> Any:
        """Perform random sampling."""

        if len(df) <= n:
            return df

        return df.sample(n=n, seed=seed)


class HeadSamplingStrategy(SamplingStrategy):
    """Head sampling strategy - take first N rows."""

    @property
    def method(self) -> SamplingMethod:
        return SamplingMethod.HEAD

    def sample(
        self,
        df: Any,
        n: int,
        seed: int = 42,
        **kwargs: Any,
    ) -> Any:
        """Take first N rows."""
        return df.head(n)


class TailSamplingStrategy(SamplingStrategy):
    """Tail sampling strategy - take last N rows."""

    @property
    def method(self) -> SamplingMethod:
        return SamplingMethod.TAIL

    def sample(
        self,
        df: Any,
        n: int,
        seed: int = 42,
        **kwargs: Any,
    ) -> Any:
        """Take last N rows."""
        return df.tail(n)


class StratifiedSamplingStrategy(SamplingStrategy):
    """Stratified sampling strategy by a categorical column."""

    @property
    def method(self) -> SamplingMethod:
        return SamplingMethod.STRATIFIED

    def sample(
        self,
        df: Any,
        n: int,
        seed: int = 42,
        stratify_column: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Perform stratified sampling.

        Args:
            df: DataFrame to sample from.
            n: Total number of rows to sample.
            seed: Random seed.
            stratify_column: Column to stratify by. If None, falls back to random.
            **kwargs: Additional arguments.

        Returns:
            Sampled DataFrame with proportional representation.
        """

        if len(df) <= n:
            return df

        if stratify_column is None or stratify_column not in df.columns:
            # Fall back to random sampling
            return df.sample(n=n, seed=seed)

        # Calculate proportion for each group
        total_rows = len(df)
        fraction = n / total_rows

        # Sample proportionally from each group
        sampled = df.group_by(stratify_column).map_groups(
            lambda group: group.sample(
                fraction=min(1.0, fraction * 1.1),  # Slight oversample
                seed=seed,
            )
        )

        # Trim to exact size if oversampled
        if len(sampled) > n:
            sampled = sampled.sample(n=n, seed=seed)

        return sampled


class DataSampler:
    """Main sampler class that coordinates sampling operations.

    Provides a high-level interface for sampling large datasets
    with automatic format detection and strategy selection.

    Usage:
        sampler = DataSampler()
        result = await sampler.auto_sample("/path/to/large.csv")
        # Use result.sampled_path for validation
    """

    def __init__(self, config: SamplingConfig | None = None) -> None:
        """Initialize data sampler.

        Args:
            config: Sampling configuration. Uses defaults if not provided.
        """
        self._config = config or SamplingConfig()
        self._strategies: dict[SamplingMethod, SamplingStrategy] = {}
        self._register_default_strategies()

        # Set up temp directory
        if self._config.temp_dir is None:
            settings = get_settings()
            self._config.temp_dir = settings.cache_dir / "samples"
        self._config.temp_dir.mkdir(parents=True, exist_ok=True)

    def _register_default_strategies(self) -> None:
        """Register all default sampling strategies."""
        self._strategies = {
            SamplingMethod.RANDOM: RandomSamplingStrategy(),
            SamplingMethod.HEAD: HeadSamplingStrategy(),
            SamplingMethod.TAIL: TailSamplingStrategy(),
            SamplingMethod.STRATIFIED: StratifiedSamplingStrategy(),
        }

    def register_strategy(self, strategy: SamplingStrategy) -> None:
        """Register a custom sampling strategy.

        Args:
            strategy: Sampling strategy to register.
        """
        self._strategies[strategy.method] = strategy

    @property
    def config(self) -> SamplingConfig:
        """Get sampling configuration."""
        return self._config

    def get_file_info(self, path: str | Path) -> dict[str, Any]:
        """Get file information for sampling decision.

        Args:
            path: Path to data file.

        Returns:
            Dictionary with file size, format, and estimated rows.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        # Detect format
        suffix = path.suffix.lower()
        format_map = {
            ".csv": "csv",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".json": "json",
            ".jsonl": "jsonl",
            ".ndjson": "jsonl",
        }
        file_format = format_map.get(suffix, "unknown")

        # Estimate row count for CSV (rough estimate based on average line size)
        estimated_rows = None
        if file_format == "csv" and size_mb > 0:
            # Sample first 10KB to estimate average line length
            with open(path, encoding="utf-8", errors="ignore") as f:
                sample = f.read(10240)
                lines = sample.count("\n")
                if lines > 0:
                    avg_line_size = len(sample) / lines
                    estimated_rows = int(size_bytes / avg_line_size)

        return {
            "path": str(path),
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "format": file_format,
            "estimated_rows": estimated_rows,
        }

    def needs_sampling(self, path: str | Path) -> bool:
        """Check if a file needs sampling based on size.

        Args:
            path: Path to data file.

        Returns:
            True if file exceeds size threshold.
        """
        info = self.get_file_info(path)
        return info["size_mb"] > self._config.size_threshold_mb

    def _load_dataframe(self, path: str | Path) -> Any:
        """Load data file into polars DataFrame.

        Args:
            path: Path to data file.

        Returns:
            Polars DataFrame.
        """
        import polars as pl

        path = Path(path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return pl.read_csv(path, infer_schema_length=10000)
        elif suffix in (".parquet", ".pq"):
            return pl.read_parquet(path)
        elif suffix == ".json":
            return pl.read_json(path)
        elif suffix in (".jsonl", ".ndjson"):
            return pl.read_ndjson(path)
        else:
            # Try CSV as fallback
            logger.warning(f"Unknown format {suffix}, trying CSV")
            return pl.read_csv(path, infer_schema_length=10000)

    def _save_dataframe(self, df: Any, path: Path, original_format: str) -> None:
        """Save DataFrame to file in specified format.

        Args:
            df: Polars DataFrame to save.
            path: Output path.
            original_format: Original file format.
        """
        if original_format in ("parquet", "pq"):
            df.write_parquet(path)
        elif original_format in ("json",):
            df.write_json(path)
        elif original_format in ("jsonl", "ndjson"):
            df.write_ndjson(path)
        else:
            # Default to CSV
            df.write_csv(path)

    def _generate_sample_path(self, original_path: Path) -> Path:
        """Generate a unique path for the sampled file.

        Args:
            original_path: Path to original file.

        Returns:
            Path for sampled file in temp directory.
        """
        # Create hash of original path for uniqueness
        path_hash = hashlib.md5(str(original_path).encode()).hexdigest()[:12]
        suffix = original_path.suffix

        # Use parquet for efficiency if original was CSV/JSON
        if suffix in (".csv", ".json", ".jsonl", ".ndjson"):
            suffix = ".parquet"

        return self._config.temp_dir / f"sample_{path_hash}{suffix}"

    async def sample(
        self,
        path: str | Path,
        n: int | None = None,
        method: SamplingMethod | None = None,
        **kwargs: Any,
    ) -> SamplingResult:
        """Sample data from a file.

        Args:
            path: Path to data file.
            n: Number of rows to sample. Uses config default if not provided.
            method: Sampling method. Uses config default if not provided.
            **kwargs: Additional arguments for specific strategies.

        Returns:
            SamplingResult with paths and statistics.
        """
        path = Path(path)
        n = n or self._config.default_sample_size
        method = method or self._config.method

        # Get strategy
        strategy = self._strategies.get(method)
        if strategy is None:
            raise ValueError(f"Unknown sampling method: {method}")

        # Run sampling in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._sample_sync,
            path,
            n,
            strategy,
            kwargs,
        )

        return result

    def _sample_sync(
        self,
        path: Path,
        n: int,
        strategy: SamplingStrategy,
        kwargs: dict[str, Any],
    ) -> SamplingResult:
        """Synchronous sampling implementation.

        Args:
            path: Path to data file.
            n: Number of rows to sample.
            strategy: Sampling strategy to use.
            kwargs: Additional strategy arguments.

        Returns:
            SamplingResult with sampling details.
        """
        file_info = self.get_file_info(path)

        # Load data
        logger.info(f"Loading {path} for sampling ({file_info['size_mb']:.1f} MB)")
        df = self._load_dataframe(path)
        original_rows = len(df)

        # Check if sampling is actually needed
        if original_rows <= n:
            logger.info(f"File has {original_rows} rows, no sampling needed")
            return SamplingResult(
                original_path=str(path),
                sampled_path=str(path),
                was_sampled=False,
                original_rows=original_rows,
                sampled_rows=original_rows,
            )

        # Perform sampling
        logger.info(
            f"Sampling {n} rows from {original_rows} using {strategy.method.value}"
        )
        sampled_df = strategy.sample(
            df,
            n=n,
            seed=self._config.seed,
            **kwargs,
        )
        sampled_rows = len(sampled_df)

        # Save sampled data
        sample_path = self._generate_sample_path(path)
        self._save_dataframe(sampled_df, sample_path, file_info["format"])

        # Calculate size reduction
        sampled_size = sample_path.stat().st_size
        size_reduction = (1 - sampled_size / file_info["size_bytes"]) * 100

        logger.info(
            f"Sampling complete: {original_rows} -> {sampled_rows} rows "
            f"({size_reduction:.1f}% size reduction)"
        )

        return SamplingResult(
            original_path=str(path),
            sampled_path=str(sample_path),
            was_sampled=True,
            original_rows=original_rows,
            sampled_rows=sampled_rows,
            method=strategy.method,
            size_reduction_pct=size_reduction,
        )

    async def auto_sample(
        self,
        path: str | Path,
        n: int | None = None,
        method: SamplingMethod | None = None,
        **kwargs: Any,
    ) -> SamplingResult:
        """Automatically sample if needed based on file size.

        This is the recommended entry point for most use cases.
        It checks file size and only samples if threshold is exceeded.

        Args:
            path: Path to data file.
            n: Number of rows to sample if needed.
            method: Sampling method if sampling is needed.
            **kwargs: Additional strategy arguments.

        Returns:
            SamplingResult (was_sampled=False if no sampling needed).
        """
        path = Path(path)

        if not self.needs_sampling(path):
            # No sampling needed
            return SamplingResult(
                original_path=str(path),
                sampled_path=str(path),
                was_sampled=False,
            )

        return await self.sample(path, n=n, method=method, **kwargs)

    async def cleanup_old_samples(self, max_age_hours: int | None = None) -> int:
        """Clean up old sample files.

        Args:
            max_age_hours: Maximum age in hours. Uses config default if not provided.

        Returns:
            Number of files cleaned up.
        """
        import time

        max_age_hours = max_age_hours or self._config.cleanup_after_hours
        max_age_seconds = max_age_hours * 3600
        now = time.time()

        cleaned = 0
        for sample_file in self._config.temp_dir.glob("sample_*"):
            if sample_file.is_file():
                age = now - sample_file.stat().st_mtime
                if age > max_age_seconds:
                    sample_file.unlink()
                    cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old sample files")

        return cleaned


# Singleton instance
_sampler: DataSampler | None = None


def get_sampler() -> DataSampler:
    """Get sampler singleton.

    Returns:
        DataSampler instance.
    """
    global _sampler
    if _sampler is None:
        _sampler = DataSampler()
    return _sampler


def reset_sampler() -> None:
    """Reset sampler singleton (for testing)."""
    global _sampler
    _sampler = None

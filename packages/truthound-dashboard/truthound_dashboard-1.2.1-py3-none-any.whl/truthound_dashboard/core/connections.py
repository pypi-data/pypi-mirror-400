"""Database connection factory and utilities.

Provides utilities for building connection strings and testing connections
for various database types supported by truthound.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


class ConnectionBuilder(ABC):
    """Abstract base class for connection string builders."""

    @abstractmethod
    def build(self, config: dict[str, Any]) -> str:
        """Build connection string from configuration.

        Args:
            config: Database-specific configuration.

        Returns:
            Connection string.

        Raises:
            ValueError: If required config is missing.
        """
        pass

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate configuration and return list of errors.

        Args:
            config: Configuration to validate.

        Returns:
            List of error messages (empty if valid).
        """
        pass


class FileConnectionBuilder(ConnectionBuilder):
    """Connection builder for file-based sources."""

    SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".xlsx", ".xls"}

    def build(self, config: dict[str, Any]) -> str:
        """Build file path from config."""
        return config.get("path", "")

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate file configuration."""
        errors = []
        path = config.get("path")

        if not path:
            errors.append("path is required")
        else:
            p = Path(path)
            if p.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                errors.append(
                    f"Unsupported file type: {p.suffix}. "
                    f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
                )

        return errors


class PostgreSQLConnectionBuilder(ConnectionBuilder):
    """Connection builder for PostgreSQL databases."""

    def build(self, config: dict[str, Any]) -> str:
        """Build PostgreSQL connection string."""
        host = config.get("host", "localhost")
        port = config.get("port", 5432)
        database = config.get("database", "")
        username = config.get("username", "")
        password = quote_plus(config.get("password", ""))
        schema = config.get("schema")

        conn = f"postgresql://{username}:{password}@{host}:{port}/{database}"

        if schema:
            conn += f"?options=-csearch_path%3D{schema}"

        return conn

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate PostgreSQL configuration."""
        errors = []
        required = ["host", "database", "username"]

        for field in required:
            if not config.get(field):
                errors.append(f"{field} is required")

        return errors


class MySQLConnectionBuilder(ConnectionBuilder):
    """Connection builder for MySQL databases."""

    def build(self, config: dict[str, Any]) -> str:
        """Build MySQL connection string."""
        host = config.get("host", "localhost")
        port = config.get("port", 3306)
        database = config.get("database", "")
        username = config.get("username", "")
        password = quote_plus(config.get("password", ""))

        return f"mysql://{username}:{password}@{host}:{port}/{database}"

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate MySQL configuration."""
        errors = []
        required = ["host", "database", "username"]

        for field in required:
            if not config.get(field):
                errors.append(f"{field} is required")

        return errors


class SnowflakeConnectionBuilder(ConnectionBuilder):
    """Connection builder for Snowflake databases."""

    def build(self, config: dict[str, Any]) -> str:
        """Build Snowflake connection string."""
        account = config.get("account", "")
        username = config.get("username", "")
        password = quote_plus(config.get("password", ""))
        database = config.get("database", "")
        schema = config.get("schema", "PUBLIC")
        warehouse = config.get("warehouse", "")
        role = config.get("role")

        conn = (
            f"snowflake://{username}:{password}@{account}"
            f"/{database}/{schema}?warehouse={warehouse}"
        )

        if role:
            conn += f"&role={role}"

        return conn

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate Snowflake configuration."""
        errors = []
        required = ["account", "database", "warehouse", "username"]

        for field in required:
            if not config.get(field):
                errors.append(f"{field} is required")

        return errors


class BigQueryConnectionBuilder(ConnectionBuilder):
    """Connection builder for BigQuery."""

    def build(self, config: dict[str, Any]) -> str:
        """Build BigQuery connection string."""
        project = config.get("project", "")
        dataset = config.get("dataset", "")

        conn = f"bigquery://{project}"
        if dataset:
            conn += f"/{dataset}"

        return conn

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate BigQuery configuration."""
        errors = []

        if not config.get("project"):
            errors.append("project is required")

        return errors


# Registry of connection builders
CONNECTION_BUILDERS: dict[str, type[ConnectionBuilder]] = {
    "file": FileConnectionBuilder,
    "postgresql": PostgreSQLConnectionBuilder,
    "mysql": MySQLConnectionBuilder,
    "snowflake": SnowflakeConnectionBuilder,
    "bigquery": BigQueryConnectionBuilder,
}


def get_connection_builder(source_type: str) -> ConnectionBuilder:
    """Get connection builder for source type.

    Args:
        source_type: Type of data source.

    Returns:
        ConnectionBuilder instance.

    Raises:
        ValueError: If source type is not supported.
    """
    builder_class = CONNECTION_BUILDERS.get(source_type)
    if builder_class is None:
        supported = ", ".join(CONNECTION_BUILDERS.keys())
        raise ValueError(f"Unknown source type: {source_type}. Supported: {supported}")

    return builder_class()


def build_connection_string(source_type: str, config: dict[str, Any]) -> str:
    """Build connection string from source type and configuration.

    Args:
        source_type: Type of data source.
        config: Source-specific configuration.

    Returns:
        Connection string.

    Raises:
        ValueError: If source type unknown or config invalid.
    """
    builder = get_connection_builder(source_type)
    errors = builder.validate_config(config)

    if errors:
        raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

    return builder.build(config)


async def test_connection(source_type: str, config: dict[str, Any]) -> dict[str, Any]:
    """Test database connection.

    Args:
        source_type: Type of data source.
        config: Source-specific configuration.

    Returns:
        Dictionary with success status and message or error.
    """
    try:
        # Validate config first
        builder = get_connection_builder(source_type)
        errors = builder.validate_config(config)

        if errors:
            return {
                "success": False,
                "error": f"Configuration errors: {'; '.join(errors)}",
            }

        connection_string = builder.build(config)

        if source_type == "file":
            # For files, just check if path exists
            path = Path(config["path"])
            if not path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            return {
                "success": True,
                "message": f"File exists: {path.name} ({path.stat().st_size:,} bytes)",
            }

        # For databases, use truthound to test connection
        import truthound as th

        # Quick profile to test connection
        result = th.profile(connection_string)
        return {
            "success": True,
            "message": f"Connected! Found {result.column_count} columns, {result.row_count:,} rows",
        }

    except ImportError:
        return {"success": False, "error": "truthound package not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_supported_source_types() -> list[dict[str, Any]]:
    """Get list of supported source types with their required fields.

    Returns:
        List of source type descriptions.
    """
    return [
        {
            "type": "file",
            "name": "File",
            "description": "CSV, Parquet, JSON, Excel files",
            "required_fields": ["path"],
            "optional_fields": [],
        },
        {
            "type": "postgresql",
            "name": "PostgreSQL",
            "description": "PostgreSQL database",
            "required_fields": ["host", "database", "username"],
            "optional_fields": ["port", "password", "schema"],
        },
        {
            "type": "mysql",
            "name": "MySQL",
            "description": "MySQL database",
            "required_fields": ["host", "database", "username"],
            "optional_fields": ["port", "password"],
        },
        {
            "type": "snowflake",
            "name": "Snowflake",
            "description": "Snowflake data warehouse",
            "required_fields": ["account", "database", "warehouse", "username"],
            "optional_fields": ["password", "schema", "role"],
        },
        {
            "type": "bigquery",
            "name": "BigQuery",
            "description": "Google BigQuery",
            "required_fields": ["project"],
            "optional_fields": ["dataset"],
        },
    ]

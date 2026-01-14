"""Database model tests."""

from datetime import datetime

from truthound_dashboard.db import Schema, Source, Validation


def test_source_model_creation():
    """Test Source model can be instantiated."""
    source = Source(
        id="test-id",
        name="Test Source",
        type="file",
        config={"path": "/data/test.csv"},
    )

    assert source.id == "test-id"
    assert source.name == "Test Source"
    assert source.type == "file"
    assert source.is_active is True
    assert source.source_path == "/data/test.csv"


def test_source_model_source_path_connection_string():
    """Test Source.source_path returns connection_string if path not set."""
    source = Source(
        id="test-id",
        name="Test DB",
        type="postgresql",
        config={"connection_string": "postgresql://localhost/test"},
    )

    assert source.source_path == "postgresql://localhost/test"


def test_schema_model_columns():
    """Test Schema model columns property."""
    schema = Schema(
        id="schema-id",
        source_id="source-id",
        schema_yaml="columns:\n  name:\n    dtype: string",
        schema_json={
            "columns": {
                "name": {"dtype": "string"},
                "age": {"dtype": "int"},
            }
        },
    )

    assert schema.columns == ["name", "age"]


def test_schema_model_columns_empty():
    """Test Schema.columns with no schema_json."""
    schema = Schema(
        id="schema-id",
        source_id="source-id",
        schema_yaml="",
        schema_json=None,
    )

    assert schema.columns == []


def test_validation_model_issues():
    """Test Validation model issues property."""
    validation = Validation(
        id="val-id",
        source_id="source-id",
        status="success",
        result_json={
            "issues": [
                {"column": "name", "issue_type": "null_values", "count": 5},
            ]
        },
    )

    assert len(validation.issues) == 1
    assert validation.issues[0]["column"] == "name"


def test_validation_model_is_complete():
    """Test Validation.is_complete property."""
    running = Validation(id="1", source_id="s", status="running")
    success = Validation(id="2", source_id="s", status="success")
    failed = Validation(id="3", source_id="s", status="failed")
    error = Validation(id="4", source_id="s", status="error")

    assert running.is_complete is False
    assert success.is_complete is True
    assert failed.is_complete is True
    assert error.is_complete is True


def test_validation_mark_started():
    """Test Validation.mark_started method."""
    validation = Validation(id="val-id", source_id="source-id", status="pending")

    validation.mark_started()

    assert validation.status == "running"
    assert validation.started_at is not None


def test_validation_mark_completed():
    """Test Validation.mark_completed method."""
    validation = Validation(id="val-id", source_id="source-id", status="running")
    validation.started_at = datetime.utcnow()

    result = {"passed": True, "issues": []}
    validation.mark_completed(passed=True, result=result)

    assert validation.status == "success"
    assert validation.passed is True
    assert validation.completed_at is not None
    assert validation.duration_ms is not None


def test_validation_mark_error():
    """Test Validation.mark_error method."""
    validation = Validation(id="val-id", source_id="source-id", status="running")
    validation.started_at = datetime.utcnow()

    validation.mark_error("Something went wrong")

    assert validation.status == "error"
    assert validation.error_message == "Something went wrong"
    assert validation.completed_at is not None

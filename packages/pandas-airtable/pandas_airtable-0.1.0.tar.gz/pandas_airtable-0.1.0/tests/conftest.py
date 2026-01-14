"""Shared fixtures for pandas-airtable tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pandas as pd
import pytest


@pytest.fixture
def mock_api():
    """Mock pyairtable.Api object."""
    api = Mock()
    api.table.return_value = Mock()
    api.base.return_value = Mock()
    return api


@pytest.fixture
def mock_table():
    """Mock pyairtable.Table object."""
    table = Mock()
    table.all.return_value = []
    table.batch_create.return_value = []
    table.batch_update.return_value = []
    table.batch_delete.return_value = []
    return table


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "active": [True, False, True],
            "joined": pd.to_datetime(["2023-01-01", "2023-02-15", "2023-03-20"]),
        }
    )


@pytest.fixture
def sample_airtable_records() -> list[dict[str, Any]]:
    """Sample Airtable API response."""
    return [
        {
            "id": "rec123",
            "createdTime": "2023-01-01T00:00:00.000Z",
            "fields": {"name": "Alice", "age": 30, "active": True},
        },
        {
            "id": "rec456",
            "createdTime": "2023-02-15T00:00:00.000Z",
            "fields": {"name": "Bob", "age": 25, "active": False},
        },
    ]


@pytest.fixture
def attachment_dataframe() -> pd.DataFrame:
    """DataFrame with attachment fields."""
    return pd.DataFrame(
        {
            "name": ["Doc1", "Doc2"],
            "file": [
                {"url": "https://example.com/file1.pdf", "filename": "file1.pdf"},
                {"url": "https://example.com/file2.pdf", "filename": "file2.pdf"},
            ],
        }
    )


@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """25-row DataFrame for batch testing."""
    return pd.DataFrame(
        {
            "id": range(1, 26),
            "name": [f"Item {i}" for i in range(1, 26)],
            "value": [i * 10.5 for i in range(1, 26)],
            "active": [i % 2 == 0 for i in range(1, 26)],
            "created": pd.date_range("2023-01-01", periods=25, freq="D"),
        }
    )


@pytest.fixture
def all_types_dataframe() -> pd.DataFrame:
    """DataFrame with all supported field types."""
    return pd.DataFrame(
        {
            "text_field": ["Hello", "World"],
            "number_int": [42, 100],
            "number_float": [3.14, 2.71],
            "checkbox": [True, False],
            "date_field": pd.to_datetime(["2023-01-01", "2023-12-31"]),
            "multi_select": [["a", "b"], ["c"]],
            "attachment": [
                {"url": "https://example.com/1.pdf", "filename": "1.pdf"},
                {"url": "https://example.com/2.pdf", "filename": "2.pdf"},
            ],
        }
    )


@pytest.fixture
def records_with_attachments() -> list[dict[str, Any]]:
    """Airtable records with attachment fields."""
    return [
        {
            "id": "rec001",
            "createdTime": "2023-01-01T00:00:00.000Z",
            "fields": {
                "name": "Document 1",
                "files": [
                    {
                        "id": "att001",
                        "url": "https://dl.airtable.com/file1.pdf",
                        "filename": "file1.pdf",
                        "size": 12345,
                        "type": "application/pdf",
                    }
                ],
            },
        },
        {
            "id": "rec002",
            "createdTime": "2023-01-02T00:00:00.000Z",
            "fields": {
                "name": "Document 2",
                "files": [
                    {
                        "id": "att002",
                        "url": "https://dl.airtable.com/file2.pdf",
                        "filename": "file2.pdf",
                        "size": 67890,
                        "type": "application/pdf",
                    },
                    {
                        "id": "att003",
                        "url": "https://dl.airtable.com/file3.pdf",
                        "filename": "file3.pdf",
                        "size": 11111,
                        "type": "application/pdf",
                    },
                ],
            },
        },
    ]


@pytest.fixture
def records_with_linked() -> list[dict[str, Any]]:
    """Airtable records with linked record fields."""
    return [
        {
            "id": "rec001",
            "createdTime": "2023-01-01T00:00:00.000Z",
            "fields": {
                "name": "Project A",
                "tasks": ["recTask1", "recTask2"],
            },
        },
        {
            "id": "rec002",
            "createdTime": "2023-01-02T00:00:00.000Z",
            "fields": {
                "name": "Project B",
                "tasks": ["recTask3"],
            },
        },
    ]


@pytest.fixture
def mock_base_schema():
    """Mock base schema with table info."""
    table = Mock()
    table.name = "TestTable"
    field1 = Mock()
    field1.name = "name"
    field1.type = "singleLineText"
    field2 = Mock()
    field2.name = "age"
    field2.type = "number"
    table.fields = [field1, field2]
    table.create_field = Mock()

    schema = Mock()
    schema.tables = [table]
    schema.table.return_value = table
    return schema

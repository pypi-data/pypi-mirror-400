"""Tests for read_airtable function."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableTableNotFoundError,
    AirtableValidationError,
)
from pandas_airtable.reader import read_airtable
from pandas_airtable.types import AIRTABLE_CREATED_TIME_COLUMN, AIRTABLE_ID_COLUMN


class TestReadAirtableBasic:
    """Test basic read_airtable functionality."""

    def test_read_airtable_basic(self, sample_airtable_records):
        """Test basic read with mocked records."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert len(df) == 2
            assert AIRTABLE_ID_COLUMN in df.columns
            assert AIRTABLE_CREATED_TIME_COLUMN in df.columns
            assert "name" in df.columns
            assert "age" in df.columns

    def test_read_airtable_with_view(self, sample_airtable_records):
        """Test read with view filter."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            read_airtable("app123", "TestTable", api_key="pat123", view="MyView")

            mock_table.all.assert_called_once()
            call_kwargs = mock_table.all.call_args[1]
            assert call_kwargs.get("view") == "MyView"

    def test_read_airtable_with_formula(self, sample_airtable_records):
        """Test read with formula filter."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            read_airtable("app123", "TestTable", api_key="pat123", formula="{age} > 25")

            mock_table.all.assert_called_once()
            call_kwargs = mock_table.all.call_args[1]
            assert call_kwargs.get("formula") == "{age} > 25"


class TestReadAirtableMetadata:
    """Test metadata column handling."""

    def test_preserves_airtable_id(self, sample_airtable_records):
        """Verify _airtable_id column is created."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert AIRTABLE_ID_COLUMN in df.columns
            assert df[AIRTABLE_ID_COLUMN].tolist() == ["rec123", "rec456"]

    def test_preserves_created_time(self, sample_airtable_records):
        """Verify _airtable_created_time column is created."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert AIRTABLE_CREATED_TIME_COLUMN in df.columns
            # Should be datetime type after coercion
            assert pd.api.types.is_datetime64_any_dtype(df[AIRTABLE_CREATED_TIME_COLUMN])


class TestReadAirtableSpecialFields:
    """Test handling of special field types."""

    def test_normalizes_attachments(self, records_with_attachments):
        """Test attachment field handling."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = records_with_attachments
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert "files" in df.columns
            # Attachments should be normalized to list of {url, filename}
            first_files = df.loc[0, "files"]
            assert isinstance(first_files, list)
            assert "url" in first_files[0]
            assert "filename" in first_files[0]

    def test_handles_linked_records(self, records_with_linked):
        """Test linked record field handling."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = records_with_linked
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert "tasks" in df.columns
            # Linked records should be list of IDs
            assert df.loc[0, "tasks"] == ["recTask1", "recTask2"]


class TestReadAirtableTypeCoercion:
    """Test type coercion of DataFrame columns."""

    def test_coerces_dates(self):
        """Test date string to datetime conversion."""
        records = [
            {
                "id": "rec1",
                "createdTime": "2023-01-01T00:00:00.000Z",
                "fields": {"date_field": "2023-06-15"},
            }
        ]

        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = records
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            # Date-like strings should be converted to datetime
            assert pd.api.types.is_datetime64_any_dtype(df["date_field"])


class TestReadAirtableEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_empty_table(self):
        """Test handling of empty result."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert len(df) == 0
            assert isinstance(df, pd.DataFrame)

    def test_invalid_api_key_raises(self):
        """Test authentication error for invalid API key."""
        with pytest.raises(AirtableAuthenticationError):
            read_airtable("app123", "TestTable", api_key="")

    def test_missing_base_id_raises(self):
        """Test validation error for missing base_id."""
        with pytest.raises(AirtableValidationError):
            read_airtable("", "TestTable", api_key="pat123")

    def test_missing_table_name_raises(self):
        """Test validation error for missing table_name."""
        with pytest.raises(AirtableValidationError):
            read_airtable("app123", "", api_key="pat123")

    def test_table_not_found_raises(self):
        """Test table not found error."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.side_effect = Exception("Table not found - 404")
            MockApi.return_value.table.return_value = mock_table

            with pytest.raises(AirtableTableNotFoundError):
                read_airtable("app123", "NonexistentTable", api_key="pat123")

    def test_page_size_clamped(self, sample_airtable_records):
        """Test page_size is clamped to valid range."""
        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = sample_airtable_records
            MockApi.return_value.table.return_value = mock_table

            # Page size > 100 should be clamped
            read_airtable("app123", "TestTable", api_key="pat123", page_size=500)

            call_kwargs = mock_table.all.call_args[1]
            assert call_kwargs.get("page_size") == 100


class TestReadAirtablePagination:
    """Test pagination handling."""

    def test_fetches_all_pages(self):
        """Verify all pages are fetched via pyairtable's all() method."""
        # pyairtable handles pagination internally - we just verify all() is called
        records = [
            {"id": f"rec{i}", "createdTime": "2023-01-01T00:00:00.000Z", "fields": {"n": i}}
            for i in range(150)
        ]

        with patch("pandas_airtable.reader.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = records
            MockApi.return_value.table.return_value = mock_table

            df = read_airtable("app123", "TestTable", api_key="pat123")

            assert len(df) == 150
            mock_table.all.assert_called_once()

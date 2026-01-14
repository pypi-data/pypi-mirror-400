"""Tests for batching utilities."""

from __future__ import annotations

import warnings
from unittest.mock import Mock

import pandas as pd
import pytest

from pandas_airtable.batch import (
    check_duplicate_keys,
    execute_batch_create,
    execute_batch_delete,
    execute_batch_update,
    execute_batch_upsert,
    prepare_records,
    prepare_update_records,
)
from pandas_airtable.exceptions import AirtableDuplicateKeyError
from pandas_airtable.types import MAX_RECORDS_PER_REQUEST
from pandas_airtable.utils import chunk_records


class TestChunkRecords:
    """Test record chunking utility."""

    def test_chunk_records_exact_batch(self):
        """Test 10 records = 1 batch."""
        records = list(range(10))
        result = chunk_records(records, 10)

        assert len(result) == 1
        assert len(result[0]) == 10

    def test_chunk_records_overflow(self):
        """Test 15 records = 2 batches."""
        records = list(range(15))
        result = chunk_records(records, 10)

        assert len(result) == 2
        assert len(result[0]) == 10
        assert len(result[1]) == 5

    def test_chunk_records_underflow(self):
        """Test 5 records = 1 batch."""
        records = list(range(5))
        result = chunk_records(records, 10)

        assert len(result) == 1
        assert len(result[0]) == 5

    def test_chunk_records_empty(self):
        """Test empty list."""
        records: list = []
        result = chunk_records(records, 10)

        assert len(result) == 0

    def test_chunk_25_records(self):
        """Test 25 records = 3 batches."""
        records = list(range(25))
        result = chunk_records(records, MAX_RECORDS_PER_REQUEST)

        assert len(result) == 3
        assert len(result[0]) == 10
        assert len(result[1]) == 10
        assert len(result[2]) == 5


class TestCheckDuplicateKeys:
    """Test duplicate key detection."""

    def test_no_duplicates_passes(self):
        """Test DataFrame without duplicates passes."""
        df = pd.DataFrame({"key": [1, 2, 3], "value": ["a", "b", "c"]})

        result = check_duplicate_keys(df, "key", allow_duplicates=False)

        assert len(result) == 3

    def test_duplicates_raises_error(self):
        """Test duplicate keys raise error when not allowed."""
        df = pd.DataFrame({"key": [1, 2, 1], "value": ["a", "b", "c"]})

        with pytest.raises(AirtableDuplicateKeyError) as exc_info:
            check_duplicate_keys(df, "key", allow_duplicates=False)

        assert 1 in exc_info.value.duplicate_values

    def test_duplicates_allowed_keeps_last(self):
        """Test allow_duplicates=True keeps last occurrence."""
        df = pd.DataFrame({"key": [1, 2, 1], "value": ["first", "b", "last"]})

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = check_duplicate_keys(df, "key", allow_duplicates=True)

            assert len(result) == 2
            # Should have kept "last" for key=1
            assert result[result["key"] == 1]["value"].iloc[0] == "last"
            # Should have issued warning
            assert len(w) == 1
            assert "duplicate" in str(w[0].message).lower()


class TestPrepareRecords:
    """Test record preparation for API."""

    def test_prepare_records_basic(self):
        """Test basic record preparation."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

        records = prepare_records(df)

        assert len(records) == 2
        assert records[0]["fields"]["name"] == "Alice"
        assert records[0]["fields"]["age"] == 30

    def test_prepare_records_skips_metadata(self):
        """Test metadata columns are skipped."""
        df = pd.DataFrame(
            {
                "_airtable_id": ["rec1", "rec2"],
                "_airtable_created_time": ["2023-01-01", "2023-02-01"],
                "name": ["Alice", "Bob"],
            }
        )

        records = prepare_records(df)

        assert "_airtable_id" not in records[0]["fields"]
        assert "_airtable_created_time" not in records[0]["fields"]

    def test_prepare_records_skips_nan(self):
        """Test NaN values are skipped."""
        df = pd.DataFrame({"name": ["Alice", None], "age": [30, 25]})

        records = prepare_records(df)

        assert "name" not in records[1]["fields"]
        assert records[1]["fields"]["age"] == 25

    def test_prepare_update_records(self):
        """Test update record preparation includes ID."""
        df = pd.DataFrame({"_airtable_id": ["rec1", "rec2"], "name": ["Alice", "Bob"]})

        records = prepare_update_records(df)

        assert len(records) == 2
        assert records[0]["id"] == "rec1"
        assert records[0]["fields"]["name"] == "Alice"

    def test_prepare_update_records_requires_id(self):
        """Test update records require _airtable_id column."""
        df = pd.DataFrame({"name": ["Alice", "Bob"]})

        with pytest.raises(ValueError, match="_airtable_id"):
            prepare_update_records(df)


class TestExecuteBatchCreate:
    """Test batch create execution."""

    def test_batch_create_success(self):
        """Test all batches succeed."""
        mock_table = Mock()
        mock_table.batch_create.return_value = [
            {"id": "rec1", "fields": {}},
            {"id": "rec2", "fields": {}},
        ]

        records = [{"fields": {"name": f"Item {i}"}} for i in range(2)]
        result = execute_batch_create(mock_table, records, batch_size=10)

        assert result.created_count == 2
        assert result.success is True
        assert "rec1" in result.created_ids

    def test_batch_create_multiple_batches(self, large_dataframe):
        """Test multiple batches are processed."""
        mock_table = Mock()
        created_records = [{"id": f"rec{i}", "fields": {}} for i in range(25)]

        # Return records for each batch call
        mock_table.batch_create.side_effect = [
            created_records[:10],
            created_records[10:20],
            created_records[20:25],
        ]

        records = [{"fields": {"name": f"Item {i}"}} for i in range(25)]
        result = execute_batch_create(mock_table, records, batch_size=10)

        assert result.created_count == 25
        assert mock_table.batch_create.call_count == 3

    def test_batch_create_partial_failure(self):
        """Test some batches fail."""
        mock_table = Mock()
        mock_table.batch_create.side_effect = [
            [{"id": "rec1", "fields": {}}],
            Exception("API Error"),
        ]

        records = [{"fields": {"name": f"Item {i}"}} for i in range(15)]
        result = execute_batch_create(mock_table, records, batch_size=10)

        assert result.created_count == 1
        assert len(result.errors) == 1
        assert result.success is False


class TestExecuteBatchUpdate:
    """Test batch update execution."""

    def test_batch_update_success(self):
        """Test successful batch update."""
        mock_table = Mock()
        mock_table.batch_update.return_value = [
            {"id": "rec1", "fields": {"name": "Updated1"}},
            {"id": "rec2", "fields": {"name": "Updated2"}},
        ]

        records = [
            {"id": "rec1", "fields": {"name": "Updated1"}},
            {"id": "rec2", "fields": {"name": "Updated2"}},
        ]
        result = execute_batch_update(mock_table, records, batch_size=10)

        assert result.updated_count == 2
        assert result.success is True
        assert "rec1" in result.updated_ids

    def test_batch_update_multiple_batches(self):
        """Test update with >10 records."""
        mock_table = Mock()
        # Return records for each batch
        mock_table.batch_update.side_effect = [
            [{"id": f"rec{i}", "fields": {}} for i in range(10)],
            [{"id": f"rec{i}", "fields": {}} for i in range(10, 15)],
        ]

        records = [{"id": f"rec{i}", "fields": {"name": f"Item {i}"}} for i in range(15)]
        result = execute_batch_update(mock_table, records, batch_size=10)

        assert result.updated_count == 15
        assert mock_table.batch_update.call_count == 2

    def test_batch_update_partial_failure(self):
        """Test when some batches fail."""
        mock_table = Mock()
        mock_table.batch_update.side_effect = [
            [{"id": "rec1", "fields": {}}],
            Exception("API Error"),
        ]

        records = [{"id": f"rec{i}", "fields": {"name": f"Item {i}"}} for i in range(15)]
        result = execute_batch_update(mock_table, records, batch_size=10)

        assert result.updated_count == 1
        assert len(result.errors) == 1
        assert result.success is False


class TestExecuteBatchDelete:
    """Test batch delete execution."""

    def test_batch_delete_success(self):
        """Test delete all records."""
        mock_table = Mock()
        mock_table.batch_delete.return_value = [{"id": "rec1", "deleted": True}]

        result = execute_batch_delete(mock_table, ["rec1", "rec2"], batch_size=10)

        assert result.deleted_count == 2

    def test_batch_delete_multiple_batches(self):
        """Test delete in multiple batches."""
        mock_table = Mock()
        record_ids = [f"rec{i}" for i in range(25)]

        result = execute_batch_delete(mock_table, record_ids, batch_size=10)

        assert result.deleted_count == 25
        assert mock_table.batch_delete.call_count == 3

    def test_batch_delete_failure(self):
        """Test delete operation failure handling."""
        mock_table = Mock()
        mock_table.batch_delete.side_effect = [
            None,  # First batch succeeds
            Exception("Delete failed"),  # Second batch fails
        ]

        record_ids = [f"rec{i}" for i in range(15)]
        result = execute_batch_delete(mock_table, record_ids, batch_size=10)

        assert result.deleted_count == 10  # Only first batch succeeded
        assert len(result.errors) == 1


class TestExecuteBatchUpsert:
    """Test batch upsert execution."""

    def test_batch_upsert_creates_and_updates(self):
        """Test upsert handles creates and updates."""
        mock_table = Mock()

        # Mock upsert result - records are dicts with "id" and "fields"
        mock_result = Mock()
        mock_result.created_records = [{"id": "rec_new", "fields": {"key": 1}}]
        mock_result.updated_records = [{"id": "rec_existing", "fields": {"key": 2}}]
        mock_table.batch_upsert.return_value = mock_result

        records = [{"fields": {"key": 1, "value": "a"}}]
        result = execute_batch_upsert(mock_table, records, ["key"], batch_size=10)

        assert result.created_count == 1
        assert result.updated_count == 1

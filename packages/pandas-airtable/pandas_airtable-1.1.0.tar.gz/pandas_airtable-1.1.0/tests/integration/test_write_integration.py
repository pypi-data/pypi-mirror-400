"""Integration tests for to_airtable() DataFrame accessor.

Tests writing data to Airtable with append, replace, and upsert modes.
"""

from __future__ import annotations

import warnings

import pandas as pd
import pytest
from pyairtable import Api

from pandas_airtable import read_airtable
from pandas_airtable.exceptions import (
    AirtableDuplicateKeyError,
    AirtableValidationError,
)

from .conftest import wait_for_api


class TestWriteAppendMode:
    """Test append mode (default) - adds new records."""

    def test_append_to_empty_table(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test appending data to an empty table."""
        table_name, _ = test_table

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="append",
        )

        assert result.success
        assert result.created_count == 3
        assert len(result.created_ids) == 3
        assert all(rid.startswith("rec") for rid in result.created_ids)

        # Verify data was written
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 3

    def test_append_to_existing_data(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test appending adds to existing records."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert initial data directly
        table.create({"Name": "Existing", "Value": 999})
        wait_for_api()

        # Append new data
        df = pd.DataFrame({"Name": ["New1", "New2"], "Value": [100, 200]})
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="append",
        )

        assert result.success
        assert result.created_count == 2

        # Should have 3 total records now
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 3
        assert "Existing" in df_read["Name"].values

    def test_append_returns_created_ids(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that append returns the IDs of created records."""
        table_name, _ = test_table

        df = pd.DataFrame({"Name": ["Test1", "Test2"], "Value": [1, 2]})
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="append",
        )

        assert len(result.created_ids) == 2
        # All IDs should be valid Airtable record IDs
        for rid in result.created_ids:
            assert rid.startswith("rec")
            assert len(rid) == 17  # rec + 14 chars


class TestWriteReplaceMode:
    """Test replace mode - deletes all existing, then creates new."""

    def test_replace_empty_table(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test replace on empty table just creates records."""
        table_name, _ = test_table

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="replace",
        )

        assert result.success
        assert result.created_count == 3
        assert result.deleted_count == 0

    def test_replace_deletes_existing(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test replace deletes all existing records first."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert 5 existing records
        for i in range(5):
            table.create({"Name": f"Old_{i}", "Value": i})
            wait_for_api(0.1)

        wait_for_api()

        # Replace with 2 new records
        df = pd.DataFrame({"Name": ["New1", "New2"], "Value": [100, 200]})
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="replace",
        )

        assert result.success
        assert result.deleted_count == 5
        assert result.created_count == 2

        # Verify only new records exist
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 2
        assert set(df_read["Name"].tolist()) == {"New1", "New2"}
        # Old records should not exist
        assert "Old_0" not in df_read["Name"].values

    def test_replace_with_empty_dataframe(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test replace with empty DataFrame clears the table."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert initial data
        table.batch_create(
            [
                {"Name": "Record1", "Value": 1},
                {"Name": "Record2", "Value": 2},
            ]
        )
        wait_for_api()

        # Replace with empty DataFrame
        df = pd.DataFrame({"Name": [], "Value": []})
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="replace",
        )

        assert result.deleted_count == 2
        assert result.created_count == 0

        # Table should be empty
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 0


class TestWriteUpsertMode:
    """Test upsert mode - update existing by key, create new."""

    def test_upsert_creates_new_records(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test upsert creates records when none exist."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Value": [100, 200, 300],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
        )

        assert result.success
        # All should be created (none existed)
        assert result.created_count + result.updated_count == 3

    def test_upsert_updates_existing(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test upsert updates records with matching key."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Create initial record
        table.create({"Name": "Alice", "Value": 50})
        wait_for_api()

        # Upsert with updated value
        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob"],
                "Value": [100, 200],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
        )

        assert result.success

        # Verify the update
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 2

        alice_row = df_read[df_read["Name"] == "Alice"].iloc[0]
        assert alice_row["Value"] == 100  # Updated from 50

    def test_upsert_mixed_create_update(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test upsert with mix of new and existing records."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Create some initial records
        table.batch_create(
            [
                {"Name": "Existing1", "Value": 10},
                {"Name": "Existing2", "Value": 20},
            ]
        )
        wait_for_api()

        # Upsert: update one, create two new
        df = pd.DataFrame(
            {
                "Name": ["Existing1", "New1", "New2"],
                "Value": [100, 200, 300],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
        )

        assert result.success

        # Verify results
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 4  # 2 original + 1 updated (same record) + 2 new = 4

        # Check Existing1 was updated
        existing1 = df_read[df_read["Name"] == "Existing1"].iloc[0]
        assert existing1["Value"] == 100

        # Check Existing2 is unchanged
        existing2 = df_read[df_read["Name"] == "Existing2"].iloc[0]
        assert existing2["Value"] == 20


class TestWriteDuplicateKeyHandling:
    """Test handling of duplicate keys in upsert mode."""

    def test_duplicate_keys_raises_error_by_default(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        dataframe_with_duplicates: pd.DataFrame,
    ):
        """Test that duplicate keys raise error when not allowed."""
        table_name, _ = test_table

        with pytest.raises(AirtableDuplicateKeyError) as exc_info:
            dataframe_with_duplicates.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                if_exists="upsert",
                key_field="email",
            )

        assert "duplicate" in str(exc_info.value).lower()
        assert "a@test.com" in str(exc_info.value)

    def test_duplicate_keys_allowed_keeps_last(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that allow_duplicate_keys=True keeps last occurrence."""
        table_name, _ = test_table

        # Create table with email field using table.create_field (not schema)
        base = airtable_api.base(base_id)
        try:
            # Get table ID from schema
            base_schema = base.schema()
            table_id = None
            for t in base_schema.tables:
                if t.name == table_name:
                    table_id = t.id
                    break
            if table_id:
                table = airtable_api.table(base_id, table_id)
                table.create_field("email", "singleLineText")
                wait_for_api()
        except Exception:
            pass  # Field might already exist

        df = pd.DataFrame(
            {
                "Name": ["First", "Second", "Third"],
                "email": ["a@test.com", "a@test.com", "b@test.com"],
                "Value": [100, 200, 300],
            }
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = df.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                if_exists="upsert",
                key_field="email",
                allow_duplicate_keys=True,
            )

            # Should have warning about dropped rows
            assert len(w) >= 1
            assert "duplicate" in str(w[0].message).lower()

        assert result.success

        # Verify only 2 records (duplicates merged)
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        # Should have the last occurrence values
        a_record = df_read[df_read["Name"] == "Second"]
        assert len(a_record) == 1


class TestWriteValidation:
    """Test input validation for write operations."""

    def test_upsert_requires_key_field(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test that upsert without key_field raises error."""
        table_name, _ = test_table

        with pytest.raises(AirtableValidationError) as exc_info:
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                if_exists="upsert",
                # key_field not provided
            )

        assert "key_field" in str(exc_info.value).lower()

    def test_key_field_must_exist_in_dataframe(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test that key_field must be a column in DataFrame."""
        table_name, _ = test_table

        with pytest.raises(AirtableValidationError) as exc_info:
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                if_exists="upsert",
                key_field="nonexistent_column",
            )

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_if_exists_raises_error(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test that invalid if_exists value raises error."""
        table_name, _ = test_table

        with pytest.raises(AirtableValidationError):
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                if_exists="invalid_mode",  # type: ignore
            )

    def test_batch_size_validation(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test that batch_size must be between 1 and 10."""
        table_name, _ = test_table

        with pytest.raises(AirtableValidationError) as exc_info:
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                batch_size=15,  # Invalid - max is 10
            )

        assert "batch_size" in str(exc_info.value).lower()


class TestWriteBatching:
    """Test batch processing for large datasets."""

    def test_write_more_than_batch_size(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        large_dataframe: pd.DataFrame,
    ):
        """Test writing 50 records (requires 5 batches)."""
        table_name, _ = test_table

        result = large_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="append",
            batch_size=10,
        )

        assert result.success
        assert result.created_count == 50

        # Verify all records were created
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 50

    def test_write_with_custom_batch_size(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test writing with smaller batch size."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": [f"Item_{i}" for i in range(15)],
                "Value": list(range(15)),
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            batch_size=5,  # Use smaller batches
        )

        assert result.success
        assert result.created_count == 15


class TestWriteDryRun:
    """Test dry run mode - preview without making changes."""

    def test_dry_run_returns_preview(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test dry run returns preview without writing."""
        table_name, _ = test_table

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            dry_run=True,
        )

        # Should return DryRunResult, not WriteResult
        assert hasattr(result, "operation")
        assert hasattr(result, "record_count")
        assert hasattr(result, "sample_records")

        assert result.operation == "append"
        assert result.record_count == 3
        assert len(result.sample_records) == 3

    def test_dry_run_does_not_write(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test dry run doesn't actually create records."""
        table_name, _ = test_table

        # Do dry run
        simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            dry_run=True,
        )

        # Table should still be empty
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 0

    def test_dry_run_replace_mode(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
        airtable_api: Api,
    ):
        """Test dry run in replace mode."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert some data
        table.create({"Name": "Existing", "Value": 999})
        wait_for_api()

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="replace",
            dry_run=True,
        )

        assert result.operation == "replace"
        assert result.record_count == 3

        # Data should NOT be deleted
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 1  # Original still exists

    def test_dry_run_upsert_mode(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test dry run in upsert mode."""
        table_name, _ = test_table

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
            dry_run=True,
        )

        assert result.operation == "upsert"
        assert result.record_count == 3

    def test_dry_run_includes_schema(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test dry run result includes schema info."""
        table_name, _ = test_table

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            dry_run=True,
        )

        assert hasattr(result, "schema")
        assert isinstance(result.schema, dict)
        assert "Name" in result.schema
        assert "Value" in result.schema

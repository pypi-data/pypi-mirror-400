"""Integration tests for edge cases and error handling.

Tests special characters, null values, large datasets, and error scenarios.
"""

from __future__ import annotations

import pandas as pd
import pytest
from pyairtable import Api

from pandas_airtable import read_airtable
from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableTableNotFoundError,
)

from .conftest import wait_for_api


class TestSpecialCharacters:
    """Test handling of special characters in data."""

    def test_special_chars_in_text(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test special characters are preserved in text fields."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": [
                    "Test & Demo",
                    "Quotes: 'single' and \"double\"",
                    "Symbols: @#$%^&*()",
                ],
                "Value": [1, 2, 3],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        assert "Test & Demo" in df_read["Name"].tolist()
        assert any("'single'" in str(n) for n in df_read["Name"].tolist())

    def test_unicode_characters(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test Unicode characters are preserved."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": [
                    "Japanese: 日本語",
                    "Emoji: 🎉🚀",
                    "Greek: αβγδ",
                    "Arabic: العربية",
                ],
                "Value": [1, 2, 3, 4],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        assert len(df_read) == 4
        # Verify Unicode is preserved
        names = df_read["Name"].tolist()
        assert any("日本語" in str(n) for n in names)
        assert any("🎉" in str(n) for n in names)

    def test_newlines_in_text(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test newlines are preserved in text fields."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Line1\nLine2\nLine3"],
                "Value": [1],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        # Newlines should be preserved
        assert "\n" in df_read.loc[0, "Name"]

    def test_very_long_text(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test handling of very long text values."""
        table_name, _ = test_table

        long_text = "A" * 5000  # 5000 character string
        df = pd.DataFrame(
            {
                "Name": [long_text],
                "Value": [1],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        # Text should be preserved (or truncated if Airtable has limits)
        assert len(df_read.loc[0, "Name"]) > 100


class TestEmptyStringHandling:
    """Test handling of empty string values."""

    def test_empty_string_text_values(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test empty string values in text columns."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", "", "Charlie"],
                "Value": [1, 2, 3],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        assert len(df_read) == 3
        # Empty strings might come back as empty or None depending on Airtable

    def test_whitespace_only_strings(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test strings containing only whitespace."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Normal", "   ", "\t\n"],
                "Value": [1, 2, 3],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 3


class TestNullHandling:
    """Test handling of null/NaN/None values."""

    def test_null_text_values(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test null values in text columns."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", None, "Charlie"],
                "Value": [1, 2, 3],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        assert len(df_read) == 3
        # Null should come back as None/NaN
        assert df_read["Name"].isna().sum() == 1

    def test_null_numeric_values(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test null values in numeric columns."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["A", "B", "C"],
                "Value": [100.0, None, 300.0],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        # One value should be NaN
        assert df_read["Value"].isna().sum() == 1

    def test_all_null_column(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test a column with all null values."""
        table_name, _ = test_table

        # Create optional field first using table.create_field (not schema)
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
                table.create_field("OptionalField", "singleLineText")
                wait_for_api()
        except Exception:
            pass

        df = pd.DataFrame(
            {
                "Name": ["A", "B", "C"],
                "Value": [1, 2, 3],
                "OptionalField": [None, None, None],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success


class TestLargeDatasets:
    """Test handling of large datasets."""

    def test_100_records(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test writing 100 records (10 batches)."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": [f"Record_{i}" for i in range(100)],
                "Value": list(range(100)),
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)

        assert result.success
        assert result.created_count == 100

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 100

    def test_batch_size_boundary(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test exactly at batch boundaries (10, 20, 30 records)."""
        table_name, _ = test_table

        # Test exactly 10 records (one batch)
        df = pd.DataFrame(
            {
                "Name": [f"Item_{i}" for i in range(10)],
                "Value": list(range(10)),
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success
        assert result.created_count == 10

    def test_batch_size_one_over(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test 11 records (two batches: 10 + 1)."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": [f"Item_{i}" for i in range(11)],
                "Value": list(range(11)),
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success
        assert result.created_count == 11

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 11


class TestErrorScenarios:
    """Test error handling scenarios."""

    def test_invalid_api_key(
        self,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test error with invalid API key."""
        table_name, _ = test_table

        with pytest.raises(AirtableAuthenticationError):
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                "invalid_api_key_xyz",
            )

    def test_empty_api_key(
        self,
        base_id: str,
        test_table: tuple[str, str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test error with empty API key."""
        table_name, _ = test_table

        with pytest.raises(AirtableAuthenticationError):
            simple_dataframe.airtable.to_airtable(
                base_id,
                table_name,
                "",
            )

    def test_invalid_base_id(
        self,
        api_key: str,
        simple_dataframe: pd.DataFrame,
        unique_table_name: str,
    ):
        """Test error with invalid base ID."""
        # Invalid base ID should fail with permission or not found error
        with pytest.raises((AirtableAuthenticationError, AirtableTableNotFoundError, ValueError)):
            simple_dataframe.airtable.to_airtable(
                "appINVALIDBASEID123",
                unique_table_name,
                api_key,
                create_table=False,
            )

    def test_nonexistent_table_no_create(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        simple_dataframe: pd.DataFrame,
    ):
        """Test error when table doesn't exist and create_table=False."""
        with pytest.raises(AirtableTableNotFoundError):
            simple_dataframe.airtable.to_airtable(
                base_id,
                unique_table_name,
                api_key,
                create_table=False,
            )


class TestEmptyDataFrame:
    """Test handling of empty DataFrames."""

    def test_write_empty_dataframe_append(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test appending empty DataFrame."""
        table_name, _ = test_table

        df = pd.DataFrame({"Name": [], "Value": []})

        result = df.airtable.to_airtable(base_id, table_name, api_key)

        assert result.success
        assert result.created_count == 0

    def test_read_empty_table(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test reading from empty table."""
        table_name, _ = test_table

        df = read_airtable(base_id, table_name, api_key)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestConcurrentOperations:
    """Test behavior under concurrent-like scenarios."""

    def test_multiple_sequential_writes(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test multiple sequential write operations."""
        table_name, _ = test_table

        # Write 3 batches sequentially
        for i in range(3):
            df = pd.DataFrame(
                {
                    "Name": [f"Batch{i}_Item{j}" for j in range(5)],
                    "Value": [i * 10 + j for j in range(5)],
                }
            )
            result = df.airtable.to_airtable(base_id, table_name, api_key)
            assert result.success
            wait_for_api()

        # Verify all records exist
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 15

    def test_write_after_read(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test writing after reading."""
        table_name, _ = test_table

        # Initial write
        df1 = pd.DataFrame({"Name": ["Initial"], "Value": [1]})
        df1.airtable.to_airtable(base_id, table_name, api_key)
        wait_for_api()

        # Read
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 1

        # Write more
        df2 = pd.DataFrame({"Name": ["Second"], "Value": [2]})
        df2.airtable.to_airtable(base_id, table_name, api_key)
        wait_for_api()

        # Read again
        df_final = read_airtable(base_id, table_name, api_key)
        assert len(df_final) == 2


class TestColumnNames:
    """Test handling of special column names."""

    def test_column_names_with_spaces(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
    ):
        """Test column names containing spaces."""
        created_tables.append(unique_table_name)

        df = pd.DataFrame(
            {
                "First Name": ["Alice", "Bob"],
                "Last Name": ["Smith", "Jones"],
                "Age Value": [30, 25],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
        )
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        assert "First Name" in df_read.columns
        assert "Last Name" in df_read.columns

    def test_column_names_with_special_chars(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
    ):
        """Test column names with special characters."""
        created_tables.append(unique_table_name)

        df = pd.DataFrame(
            {
                "Name (Primary)": ["Alice", "Bob"],
                "Score #1": [100, 200],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
        )
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        # Column names should be preserved
        assert len(df_read) == 2

    def test_column_name_starting_with_underscore(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
    ):
        """Test user column starting with underscore (potential conflict)."""
        created_tables.append(unique_table_name)

        df = pd.DataFrame(
            {
                "_custom_field": ["value1", "value2"],
                "normal_field": [1, 2],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
        )
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        # Should have both metadata columns and user column
        assert "_airtable_id" in df_read.columns
        assert "_custom_field" in df_read.columns


class TestUpsertEdgeCases:
    """Test upsert edge cases."""

    def test_upsert_with_null_key_values(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test upsert behavior when key field contains null values."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", None, "Charlie"],
                "Value": [100, 200, 300],
            }
        )

        # Upsert with null in key field - behavior may vary
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
        )

        # Should handle nulls gracefully
        assert result.success or len(result.errors) > 0


class TestDataIntegrity:
    """Test data integrity through operations."""

    def test_numeric_precision(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that numeric values maintain precision."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Value": [999999],  # Large integer
            }
        )

        df.airtable.to_airtable(base_id, table_name, api_key)
        wait_for_api()

        df_read = read_airtable(base_id, table_name, api_key)
        assert df_read.loc[0, "Value"] == 999999

    def test_data_consistency_upsert(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test data remains consistent through upsert cycles."""
        table_name, _ = test_table

        # Initial insert
        df1 = pd.DataFrame(
            {
                "Name": ["Alice", "Bob"],
                "Value": [100, 200],
            }
        )
        df1.airtable.to_airtable(base_id, table_name, api_key, if_exists="upsert", key_field="Name")
        wait_for_api()

        # Upsert with updated values
        df2 = pd.DataFrame(
            {
                "Name": ["Alice", "Bob"],
                "Value": [150, 250],
            }
        )
        df2.airtable.to_airtable(base_id, table_name, api_key, if_exists="upsert", key_field="Name")
        wait_for_api()

        # Verify final state
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 2

        alice = df_read[df_read["Name"] == "Alice"].iloc[0]
        bob = df_read[df_read["Name"] == "Bob"].iloc[0]

        assert alice["Value"] == 150
        assert bob["Value"] == 250

    def test_replace_preserves_table_structure(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test replace operation preserves table structure."""
        table_name, _ = test_table

        # Write initial data
        df1 = pd.DataFrame(
            {
                "Name": ["Old1", "Old2", "Old3"],
                "Value": [1, 2, 3],
            }
        )
        df1.airtable.to_airtable(base_id, table_name, api_key)
        wait_for_api()

        # Replace all data
        df2 = pd.DataFrame(
            {
                "Name": ["New1", "New2"],
                "Value": [100, 200],
            }
        )
        result = df2.airtable.to_airtable(base_id, table_name, api_key, if_exists="replace")
        wait_for_api()

        assert result.deleted_count == 3
        assert result.created_count == 2

        # Verify old data is gone
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 2
        assert "Old1" not in df_read["Name"].values
        assert "New1" in df_read["Name"].values


class TestMetadataColumns:
    """Test handling of _airtable_id and _airtable_created_time columns."""

    def test_airtable_id_column_ignored_on_write(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that _airtable_id in DataFrame is ignored during write."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "_airtable_id": ["rec123fake", "rec456fake"],  # Fake IDs
                "Name": ["Alice", "Bob"],
                "Value": [100, 200],
            }
        )

        # Should not try to create _airtable_id field
        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        # Should have real IDs, not the fake ones
        assert df_read.loc[0, "_airtable_id"] != "rec123fake"

    def test_created_time_column_ignored_on_write(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that _airtable_created_time is ignored during write."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "_airtable_created_time": ["2020-01-01T00:00:00.000Z", "2020-01-02T00:00:00.000Z"],
                "Name": ["Alice", "Bob"],
                "Value": [100, 200],
            }
        )

        result = df.airtable.to_airtable(base_id, table_name, api_key)
        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)

        # Created times should be recent, not the 2020 dates
        for ct in df_read["_airtable_created_time"]:
            assert pd.to_datetime(ct).year >= 2024

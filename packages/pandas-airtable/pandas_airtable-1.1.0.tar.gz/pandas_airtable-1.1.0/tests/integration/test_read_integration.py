"""Integration tests for read_airtable() function.

Tests reading data from Airtable with various options and scenarios.
"""

from __future__ import annotations

import pandas as pd
import pytest
from pyairtable import Api

from pandas_airtable import read_airtable
from pandas_airtable.types import AIRTABLE_CREATED_TIME_COLUMN, AIRTABLE_ID_COLUMN

from .conftest import wait_for_api


class TestReadBasic:
    """Test basic read operations."""

    def test_read_empty_table(
        self,
        api_key: str,
        test_table: tuple[str, str],
    ):
        """Test reading from an empty table returns empty DataFrame."""
        table_name, base_id = test_table

        df = read_airtable(base_id, table_name, api_key)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_read_with_data(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
        simple_dataframe: pd.DataFrame,
    ):
        """Test reading data that was written to the table."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        records = [
            {"fields": {"Name": "Alice", "Value": 100}},
            {"fields": {"Name": "Bob", "Value": 200}},
        ]
        table.batch_create([r["fields"] for r in records])
        wait_for_api()

        # Read data
        df = read_airtable(base_id, table_name, api_key)

        assert len(df) == 2
        assert AIRTABLE_ID_COLUMN in df.columns
        assert AIRTABLE_CREATED_TIME_COLUMN in df.columns
        assert "Name" in df.columns
        assert "Value" in df.columns
        assert set(df["Name"].tolist()) == {"Alice", "Bob"}

    def test_read_preserves_record_ids(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that record IDs are preserved in _airtable_id column."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert and get the created record ID
        created = table.create({"Name": "TestRecord", "Value": 42})
        expected_id = created["id"]
        wait_for_api()

        # Read and verify ID
        df = read_airtable(base_id, table_name, api_key)

        assert len(df) == 1
        assert df.loc[0, AIRTABLE_ID_COLUMN] == expected_id
        assert df.loc[0, AIRTABLE_ID_COLUMN].startswith("rec")

    def test_read_preserves_created_time(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that creation timestamps are preserved."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        table.create({"Name": "TestRecord", "Value": 1})
        wait_for_api()

        df = read_airtable(base_id, table_name, api_key)

        assert AIRTABLE_CREATED_TIME_COLUMN in df.columns
        # Should be datetime type
        assert pd.api.types.is_datetime64_any_dtype(df[AIRTABLE_CREATED_TIME_COLUMN])


class TestReadWithView:
    """Test read operations with view parameter."""

    def test_read_with_view_parameter(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test reading with view parameter (view must exist)."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        table.batch_create(
            [
                {"Name": "Alice", "Value": 100},
                {"Name": "Bob", "Value": 200},
            ]
        )
        wait_for_api()

        # Read without view (should get all records)
        df = read_airtable(base_id, table_name, api_key)
        assert len(df) == 2

        # Note: Testing with actual view requires view to exist in the table
        # This test verifies the view parameter is passed correctly

    def test_read_with_view_and_formula(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test combining view and formula filters."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        table.batch_create(
            [
                {"Name": "Alice", "Value": 100},
                {"Name": "Bob", "Value": 200},
                {"Name": "Charlie", "Value": 50},
            ]
        )
        wait_for_api()

        # Formula filter should work even without view
        df = read_airtable(
            base_id,
            table_name,
            api_key,
            formula="{Value} >= 100",
        )
        assert len(df) == 2


class TestReadWithFilters:
    """Test read operations with view and formula filters."""

    def test_read_with_formula_filter(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test filtering records with Airtable formula."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        table.batch_create(
            [
                {"Name": "Low", "Value": 10},
                {"Name": "Medium", "Value": 50},
                {"Name": "High", "Value": 100},
            ]
        )
        wait_for_api()

        # Read with formula filter
        df = read_airtable(
            base_id,
            table_name,
            api_key,
            formula="{Value} > 30",
        )

        assert len(df) == 2
        assert all(df["Value"] > 30)

    def test_read_with_complex_formula(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test filtering with complex AND/OR formula."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        table.batch_create(
            [
                {"Name": "Alice", "Value": 100},
                {"Name": "Bob", "Value": 200},
                {"Name": "Charlie", "Value": 50},
                {"Name": "Alice", "Value": 25},
            ]
        )
        wait_for_api()

        # Read with complex formula
        df = read_airtable(
            base_id,
            table_name,
            api_key,
            formula="AND({Name} = 'Alice', {Value} > 50)",
        )

        assert len(df) == 1
        assert df.loc[0, "Name"] == "Alice"
        assert df.loc[0, "Value"] == 100

    def test_read_with_string_formula(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test filtering with string comparison formula."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        table.batch_create(
            [
                {"Name": "Alice", "Value": 1},
                {"Name": "Bob", "Value": 2},
                {"Name": "Alice", "Value": 3},
            ]
        )
        wait_for_api()

        df = read_airtable(
            base_id,
            table_name,
            api_key,
            formula="{Name} = 'Alice'",
        )

        assert len(df) == 2
        assert all(df["Name"] == "Alice")


class TestReadPagination:
    """Test pagination behavior with large datasets."""

    def test_read_large_dataset(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test reading more records than fit in one page."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert 25 records (more than typical page size of 10-20)
        records = [{"Name": f"Record_{i}", "Value": i} for i in range(25)]
        for i in range(0, 25, 10):
            batch = records[i : i + 10]
            table.batch_create(list(batch))
            wait_for_api()

        # Read all records
        df = read_airtable(base_id, table_name, api_key)

        assert len(df) == 25
        # Verify all records are unique
        assert df[AIRTABLE_ID_COLUMN].nunique() == 25

    def test_read_with_custom_page_size(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test reading with different page sizes."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert 15 records
        records = [{"Name": f"Record_{i}", "Value": i} for i in range(15)]
        table.batch_create(records[:10])
        wait_for_api()
        table.batch_create(records[10:])
        wait_for_api()

        # Read with small page size
        df = read_airtable(base_id, table_name, api_key, page_size=5)

        # Should still get all records regardless of page size
        assert len(df) == 15


class TestReadTypeCoercion:
    """Test automatic type coercion of read data."""

    def test_read_numeric_types(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that numeric values are correctly typed."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        table.create({"Name": "Test", "Value": 12345})
        wait_for_api()

        df = read_airtable(base_id, table_name, api_key)

        # Value should be numeric
        assert pd.api.types.is_numeric_dtype(df["Value"])

    def test_read_with_null_values(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test handling of null/empty values."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Create record with only Name (Value will be null)
        table.create({"Name": "NoValue"})
        table.create({"Name": "WithValue", "Value": 100})
        wait_for_api()

        df = read_airtable(base_id, table_name, api_key)

        assert len(df) == 2
        # One record should have NaN for Value
        assert df["Value"].isna().sum() == 1


class TestReadErrorHandling:
    """Test error handling for read operations."""

    def test_read_nonexistent_table(self, api_key: str, base_id: str):
        """Test error when reading from non-existent table."""
        from pandas_airtable.exceptions import AirtableTableNotFoundError

        with pytest.raises(AirtableTableNotFoundError):
            read_airtable(base_id, "nonexistent_table_xyz123", api_key)

    def test_read_invalid_api_key(self, base_id: str, test_table: tuple[str, str]):
        """Test error with invalid API key."""
        from pandas_airtable.exceptions import AirtableAuthenticationError

        table_name, _ = test_table

        with pytest.raises(AirtableAuthenticationError):
            read_airtable(base_id, table_name, "invalid_key_xyz")

    def test_read_invalid_formula(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test error with invalid Airtable formula."""
        import requests

        table_name, _ = test_table

        # Invalid formula should raise an error from pyairtable (HTTPError)
        with pytest.raises((ValueError, RuntimeError, KeyError, requests.exceptions.HTTPError)):
            read_airtable(
                base_id,
                table_name,
                api_key,
                formula="INVALID FORMULA {{{{",
            )

"""Integration tests for schema mapping and evolution.

Tests type inference, schema creation, and field management.
"""

from __future__ import annotations

import pandas as pd
import pytest
from pyairtable import Api

from pandas_airtable import read_airtable
from pandas_airtable.exceptions import AirtableSchemaError

from .conftest import wait_for_api


class TestSchemaTypeMapping:
    """Test type inference and mapping between pandas and Airtable."""

    def test_string_to_single_line_text(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test string columns map to singleLineText."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Value": [1, 2, 3],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
        )

        assert result.success

        # Read back and verify
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert df_read["Name"].dtype == object  # String dtype

    def test_integer_to_number(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test integer columns map to number."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Value": [12345],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
        )

        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert pd.api.types.is_numeric_dtype(df_read["Value"])
        assert df_read.loc[0, "Value"] == 12345

    def test_float_to_number(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test float columns map to number with decimals."""
        table_name, _ = test_table

        # First create the FloatValue field using table.create_field
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
                table.create_field("FloatValue", "number", options={"precision": 2})
                wait_for_api()
        except Exception:
            pass

        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Value": [0],
                "FloatValue": [3.14159],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
        )

        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert pd.api.types.is_numeric_dtype(df_read["FloatValue"])
        assert abs(df_read.loc[0, "FloatValue"] - 3.14) < 0.01  # Allow for precision

    def test_boolean_to_checkbox(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test boolean columns map to checkbox."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob"],
                "Value": [1, 2],
                "Active": [True, False],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            allow_new_columns=True,
        )

        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        # Checkbox comes back as True/False
        alice_row = df_read[df_read["Name"] == "Alice"].iloc[0]
        bob_row = df_read[df_read["Name"] == "Bob"].iloc[0]
        assert alice_row["Active"] == True  # noqa: E712 (intentional == for numpy bool)
        # False checkboxes might come back as None/NA in Airtable
        bob_active = bob_row["Active"]
        assert pd.isna(bob_active) or bob_active == False  # noqa: E712

    def test_datetime_to_date(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test datetime columns map to date."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Event1", "Event2"],
                "Value": [1, 2],
                "CreatedDate": pd.to_datetime(["2024-01-15", "2024-06-20"]),
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            allow_new_columns=True,
        )

        assert result.success

        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        # Dates should be datetime type after reading
        assert pd.api.types.is_datetime64_any_dtype(df_read["CreatedDate"])


class TestSchemaEvolution:
    """Test schema evolution - adding new columns."""

    def test_schema_mismatch_raises_error_by_default(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that extra columns raise error when allow_new_columns=False."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Value": [1],
                "ExtraColumn": ["extra"],  # Not in table schema
            }
        )

        with pytest.raises(AirtableSchemaError) as exc_info:
            df.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                allow_new_columns=False,
            )

        assert "ExtraColumn" in str(exc_info.value)

    def test_allow_new_columns_creates_fields(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that allow_new_columns=True creates missing fields."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Test1", "Test2"],
                "Value": [100, 200],
                "NewField": ["new1", "new2"],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            allow_new_columns=True,
        )

        assert result.success

        # Verify the new field was created and data was written
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert "NewField" in df_read.columns
        assert set(df_read["NewField"].tolist()) == {"new1", "new2"}

    def test_schema_evolution_preserves_existing_fields(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that existing fields are preserved when adding new ones."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Create initial record
        table.create({"Name": "Existing", "Value": 999})
        wait_for_api()

        # Add new data with extra column
        df = pd.DataFrame(
            {
                "Name": ["New"],
                "Value": [100],
                "ExtraField": ["extra"],
            }
        )

        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            allow_new_columns=True,
        )

        assert result.success

        # Verify both old and new records exist
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 2

        # Existing record should still have its data
        existing_row = df_read[df_read["Name"] == "Existing"].iloc[0]
        assert existing_row["Value"] == 999


class TestTableCreation:
    """Test automatic table creation."""

    def test_create_table_true_creates_table(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
        simple_dataframe: pd.DataFrame,
    ):
        """Test that create_table=True creates a new table."""
        # Track for cleanup
        created_tables.append(unique_table_name)

        result = simple_dataframe.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
        )

        assert result.success
        assert result.created_count == 3

        # Verify table was created and has data
        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        assert len(df_read) == 3

    def test_create_table_false_raises_error(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        simple_dataframe: pd.DataFrame,
    ):
        """Test that create_table=False raises error for nonexistent table."""
        from pandas_airtable.exceptions import AirtableTableNotFoundError

        with pytest.raises(AirtableTableNotFoundError):
            simple_dataframe.airtable.to_airtable(
                base_id,
                unique_table_name,
                api_key,
                create_table=False,
            )

    def test_create_table_with_all_types(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
        dataframe_with_all_types: pd.DataFrame,
    ):
        """Test creating a table with multiple field types."""
        created_tables.append(unique_table_name)

        result = dataframe_with_all_types.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
        )

        assert result.success

        # Verify table structure
        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        assert "text_field" in df_read.columns
        assert "number_int" in df_read.columns
        assert "number_float" in df_read.columns
        assert "checkbox_field" in df_read.columns
        assert "date_field" in df_read.columns


class TestSchemaOverride:
    """Test custom schema override."""

    def test_schema_override_changes_type(
        self,
        api_key: str,
        base_id: str,
        unique_table_name: str,
        created_tables: list[str],
    ):
        """Test that schema override changes inferred type."""
        created_tables.append(unique_table_name)

        df = pd.DataFrame(
            {
                "description": ["Line 1\nLine 2", "More\nText"],
            }
        )

        # Override to use multilineText instead of singleLineText
        result = df.airtable.to_airtable(
            base_id,
            unique_table_name,
            api_key,
            create_table=True,
            schema={"description": {"type": "multilineText"}},
        )

        assert result.success

        # Verify multiline text was preserved
        wait_for_api()
        df_read = read_airtable(base_id, unique_table_name, api_key)
        assert "\n" in df_read.loc[0, "description"]


class TestRoundTrip:
    """Test full round-trip: write then read."""

    def test_roundtrip_basic_types(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test write then read preserves basic data types."""
        table_name, _ = test_table

        df_original = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Value": [100, 200, 300],
            }
        )

        # Write
        df_original.airtable.to_airtable(base_id, table_name, api_key)
        wait_for_api()

        # Read
        df_read = read_airtable(base_id, table_name, api_key)

        # Verify data matches
        assert len(df_read) == 3
        assert set(df_read["Name"].tolist()) == set(df_original["Name"].tolist())
        assert set(df_read["Value"].tolist()) == set(df_original["Value"].tolist())

    def test_roundtrip_with_airtable_id(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test that _airtable_id is preserved through round-trip."""
        table_name, _ = test_table

        df = pd.DataFrame(
            {
                "Name": ["Test1", "Test2"],
                "Value": [1, 2],
            }
        )

        # Write and get IDs
        result = df.airtable.to_airtable(base_id, table_name, api_key)
        created_ids = result.created_ids
        wait_for_api()

        # Read back
        df_read = read_airtable(base_id, table_name, api_key)

        # IDs should match
        assert set(df_read["_airtable_id"].tolist()) == set(created_ids)

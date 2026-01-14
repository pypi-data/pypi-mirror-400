"""Tests for DataFrame accessor."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandas_airtable.accessor import AirtableAccessor
from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableDuplicateKeyError,
    AirtableSchemaError,
    AirtableTableNotFoundError,
    AirtableValidationError,
)
from pandas_airtable.types import DryRunResult, WriteResult


class TestAccessorRegistration:
    """Test accessor registration."""

    def test_accessor_is_registered(self):
        """Verify accessor is registered on DataFrame."""
        import pandas_airtable  # noqa: F401 - triggers registration

        df = pd.DataFrame({"name": ["Alice"]})
        assert hasattr(df, "airtable")
        assert isinstance(df.airtable, AirtableAccessor)


class TestToAirtableValidation:
    """Test input validation for to_airtable."""

    def test_missing_api_key_raises(self):
        """Test empty API key raises error."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableAuthenticationError):
            df.airtable.to_airtable("app123", "TestTable", api_key="")

    def test_missing_base_id_raises(self):
        """Test empty base_id raises error."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="base_id"):
            df.airtable.to_airtable("", "TestTable", api_key="pat123")

    def test_missing_table_name_raises(self):
        """Test empty table_name raises error."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="table_name"):
            df.airtable.to_airtable("app123", "", api_key="pat123")

    def test_invalid_if_exists_raises(self):
        """Test invalid if_exists value raises error."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="if_exists"):
            df.airtable.to_airtable(
                "app123",
                "TestTable",
                api_key="pat123",
                if_exists="invalid",  # type: ignore
            )

    def test_upsert_requires_key_field(self):
        """Test upsert mode requires key_field."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="key_field"):
            df.airtable.to_airtable("app123", "TestTable", api_key="pat123", if_exists="upsert")

    def test_upsert_key_field_must_exist(self):
        """Test key_field must exist in DataFrame."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="nonexistent"):
            df.airtable.to_airtable(
                "app123",
                "TestTable",
                api_key="pat123",
                if_exists="upsert",
                key_field="nonexistent",
            )

    def test_batch_size_validation(self):
        """Test batch_size must be 1-10."""
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(AirtableValidationError, match="batch_size"):
            df.airtable.to_airtable("app123", "TestTable", api_key="pat123", batch_size=20)


class TestToAirtableAppend:
    """Test append mode."""

    def test_append_creates_records(self):
        """Test append creates new records."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            mock_table.batch_create.return_value = [
                {"id": "rec1", "fields": {}},
                {"id": "rec2", "fields": {}},
            ]
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema check - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_name = Mock()
            mock_field_name.name = "name"
            mock_field_name.type = "singleLineText"
            mock_field_age = Mock()
            mock_field_age.name = "age"
            mock_field_age.type = "number"
            mock_table_schema.fields = [mock_field_name, mock_field_age]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            result = df.airtable.to_airtable("app123", "TestTable", api_key="pat123")

            assert isinstance(result, WriteResult)
            assert result.created_count == 2
            mock_table.batch_create.assert_called_once()


class TestToAirtableReplace:
    """Test replace mode."""

    def test_replace_deletes_then_creates(self):
        """Test replace deletes existing then creates new."""
        df = pd.DataFrame({"name": ["Alice"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            # Existing records to delete
            mock_table.all.return_value = [{"id": "rec_old"}]
            mock_table.batch_delete.return_value = [{"id": "rec_old", "deleted": True}]
            mock_table.batch_create.return_value = [{"id": "rec_new", "fields": {}}]
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema check - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_name = Mock()
            mock_field_name.name = "name"
            mock_field_name.type = "singleLineText"
            mock_table_schema.fields = [mock_field_name]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            result = df.airtable.to_airtable(
                "app123", "TestTable", api_key="pat123", if_exists="replace"
            )

            assert result.deleted_count == 1
            assert result.created_count == 1


class TestToAirtableUpsert:
    """Test upsert mode."""

    def test_upsert_with_key_field(self):
        """Test upsert uses key_field for matching."""
        df = pd.DataFrame({"email": ["alice@example.com"], "name": ["Alice"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []

            # Mock upsert result
            mock_result = Mock()
            mock_result.created_records = [{"id": "rec1", "fields": {}}]
            mock_result.updated_records = []
            mock_table.batch_upsert.return_value = mock_result
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema check - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_email = Mock()
            mock_field_email.name = "email"
            mock_field_email.type = "email"
            mock_field_name = Mock()
            mock_field_name.name = "name"
            mock_field_name.type = "singleLineText"
            mock_table_schema.fields = [mock_field_email, mock_field_name]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            df.airtable.to_airtable(
                "app123",
                "TestTable",
                api_key="pat123",
                if_exists="upsert",
                key_field="email",
            )

            mock_table.batch_upsert.assert_called_once()
            call_kwargs = mock_table.batch_upsert.call_args[1]
            assert call_kwargs["key_fields"] == ["email"]


class TestToAirtableDuplicateKeys:
    """Test duplicate key handling."""

    def test_duplicate_keys_raises_error(self):
        """Test duplicate keys raise error by default."""
        df = pd.DataFrame({"email": ["a@b.com", "a@b.com"], "name": ["Alice", "Alice2"]})

        with patch("pandas_airtable.accessor.Api"), pytest.raises(AirtableDuplicateKeyError):
            df.airtable.to_airtable(
                "app123",
                "TestTable",
                api_key="pat123",
                if_exists="upsert",
                key_field="email",
            )

    def test_duplicate_keys_allowed(self):
        """Test allow_duplicate_keys uses last occurrence."""
        df = pd.DataFrame({"email": ["a@b.com", "a@b.com"], "name": ["First", "Last"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []

            mock_result = Mock()
            mock_result.created_records = [{"id": "rec1", "fields": {}}]
            mock_result.updated_records = []
            mock_table.batch_upsert.return_value = mock_result
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema check - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_email = Mock()
            mock_field_email.name = "email"
            mock_field_email.type = "email"
            mock_field_name = Mock()
            mock_field_name.name = "name"
            mock_field_name.type = "singleLineText"
            mock_table_schema.fields = [mock_field_email, mock_field_name]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            import warnings

            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                result = df.airtable.to_airtable(
                    "app123",
                    "TestTable",
                    api_key="pat123",
                    if_exists="upsert",
                    key_field="email",
                    allow_duplicate_keys=True,
                )

            # Should have only sent 1 record (the last one)
            assert result.created_count == 1


class TestToAirtableTableCreation:
    """Test table creation behavior."""

    def test_create_table_true_creates_table(self):
        """Test table is created when create_table=True."""
        df = pd.DataFrame({"name": ["Alice"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_base = Mock()

            # First schema call - table doesn't exist
            mock_schema = Mock()
            mock_schema.tables = []  # No tables
            mock_base.schema.return_value = mock_schema

            # create_table call
            mock_base.create_table.return_value = Mock()

            MockApi.return_value.base.return_value = mock_base

            # Table after creation
            mock_table = Mock()
            mock_table.all.return_value = []
            mock_table.batch_create.return_value = [{"id": "rec1", "fields": {}}]
            MockApi.return_value.table.return_value = mock_table

            df.airtable.to_airtable("app123", "TestTable", api_key="pat123", create_table=True)

            mock_base.create_table.assert_called_once()

    def test_create_table_false_raises_error(self):
        """Test error when table doesn't exist and create_table=False."""
        df = pd.DataFrame({"name": ["Alice"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_base = Mock()
            mock_schema = Mock()
            mock_schema.tables = []  # No tables
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            mock_table = Mock()
            mock_table.all.side_effect = Exception("Table not found")
            MockApi.return_value.table.return_value = mock_table

            with pytest.raises(AirtableTableNotFoundError):
                df.airtable.to_airtable("app123", "TestTable", api_key="pat123", create_table=False)


class TestToAirtableSchemaHandling:
    """Test schema handling."""

    def test_allow_new_columns_creates_fields(self):
        """Test new columns are created when allow_new_columns=True."""
        df = pd.DataFrame({"name": ["Alice"], "new_field": ["value"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            mock_table.batch_create.return_value = [{"id": "rec1", "fields": {}}]
            mock_table.create_field = Mock()  # create_field is on Table, not TableSchema
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema - table exists but missing new_field
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field = Mock()
            mock_field.name = "name"
            mock_field.type = "singleLineText"
            mock_table_schema.fields = [mock_field]
            mock_schema.tables = [mock_table_schema]

            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            df.airtable.to_airtable("app123", "TestTable", api_key="pat123", allow_new_columns=True)

            # Should have created the new field via Table.create_field()
            mock_table.create_field.assert_called()

    def test_schema_mismatch_raises_error(self):
        """Test schema mismatch raises error when allow_new_columns=False."""
        df = pd.DataFrame({"name": ["Alice"], "nonexistent_field": ["value"]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema - table exists but missing field
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field = Mock()
            mock_field.name = "name"
            mock_field.type = "singleLineText"
            mock_table_schema.fields = [mock_field]
            mock_schema.tables = [mock_table_schema]

            def table_lookup(name):
                return mock_table_schema

            mock_schema.table = table_lookup
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            with pytest.raises(AirtableSchemaError, match="nonexistent_field"):
                df.airtable.to_airtable(
                    "app123", "TestTable", api_key="pat123", allow_new_columns=False
                )


class TestToAirtableDryRun:
    """Test dry run mode."""

    def test_dry_run_returns_preview(self):
        """Test dry_run returns preview without making changes."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_name = Mock()
            mock_field_name.name = "name"
            mock_field_name.type = "singleLineText"
            mock_field_age = Mock()
            mock_field_age.name = "age"
            mock_field_age.type = "number"
            mock_table_schema.fields = [mock_field_name, mock_field_age]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            result = df.airtable.to_airtable("app123", "TestTable", api_key="pat123", dry_run=True)

            assert isinstance(result, DryRunResult)
            assert result.operation == "append"
            assert result.record_count == 2
            assert len(result.sample_records) <= 3

            # Verify no actual API calls for records
            mock_table.batch_create.assert_not_called()


class TestToAirtableSchemaOverride:
    """Test custom schema parameter."""

    def test_schema_override_applied(self):
        """Test custom schema is used for field mapping."""
        df = pd.DataFrame({"description": ["Long text here..."]})

        with patch("pandas_airtable.accessor.Api") as MockApi:
            mock_table = Mock()
            mock_table.all.return_value = []
            mock_table.batch_create.return_value = [{"id": "rec1", "fields": {}}]
            MockApi.return_value.table.return_value = mock_table

            # Mock base schema - include expected fields
            mock_base = Mock()
            mock_schema = Mock()
            mock_table_schema = Mock()
            mock_table_schema.name = "TestTable"
            mock_field_desc = Mock()
            mock_field_desc.name = "description"
            mock_field_desc.type = "multilineText"
            mock_table_schema.fields = [mock_field_desc]
            mock_schema.tables = [mock_table_schema]
            mock_base.schema.return_value = mock_schema
            MockApi.return_value.base.return_value = mock_base

            result = df.airtable.to_airtable(
                "app123",
                "TestTable",
                api_key="pat123",
                schema={"description": {"type": "multilineText"}},
            )

            assert result.success

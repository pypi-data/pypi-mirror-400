"""Tests for schema inference and type mapping."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest

from pandas_airtable.exceptions import AirtableSchemaError
from pandas_airtable.schema import (
    coerce_dtypes,
    compare_schemas,
    convert_to_airtable_value,
    infer_airtable_schema,
    merge_schema,
    normalize_attachments,
    prepare_attachment,
    prepare_datetime,
)
from pandas_airtable.types import (
    FIELD_TYPE_CHECKBOX,
    FIELD_TYPE_DATE,
    FIELD_TYPE_MULTIPLE_ATTACHMENTS,
    FIELD_TYPE_MULTIPLE_SELECTS,
    FIELD_TYPE_NUMBER,
    FIELD_TYPE_SINGLE_LINE_TEXT,
)


class TestInferAirtableSchema:
    """Test schema inference from DataFrames."""

    def test_infer_schema_string_column(self):
        """Test object dtype maps to singleLineText."""
        df = pd.DataFrame({"name": ["Alice", "Bob"]})
        schema = infer_airtable_schema(df)

        assert "name" in schema
        assert schema["name"]["type"] == FIELD_TYPE_SINGLE_LINE_TEXT

    def test_infer_schema_integer_column(self):
        """Test int64 maps to number."""
        df = pd.DataFrame({"count": [1, 2, 3]})
        schema = infer_airtable_schema(df)

        assert "count" in schema
        assert schema["count"]["type"] == FIELD_TYPE_NUMBER

    def test_infer_schema_float_column(self):
        """Test float64 maps to number with precision."""
        df = pd.DataFrame({"price": [1.99, 2.50, 3.14]})
        schema = infer_airtable_schema(df)

        assert "price" in schema
        assert schema["price"]["type"] == FIELD_TYPE_NUMBER
        assert "options" in schema["price"]

    def test_infer_schema_boolean_column(self):
        """Test bool maps to checkbox."""
        df = pd.DataFrame({"active": [True, False, True]})
        schema = infer_airtable_schema(df)

        assert "active" in schema
        assert schema["active"]["type"] == FIELD_TYPE_CHECKBOX

    def test_infer_schema_datetime_column(self):
        """Test datetime64 maps to date."""
        df = pd.DataFrame({"created": pd.to_datetime(["2023-01-01", "2023-02-01"])})
        schema = infer_airtable_schema(df)

        assert "created" in schema
        assert schema["created"]["type"] == FIELD_TYPE_DATE

    def test_infer_schema_list_column(self):
        """Test list columns map to multipleSelects."""
        df = pd.DataFrame({"tags": [["a", "b"], ["c"]]})
        schema = infer_airtable_schema(df)

        assert "tags" in schema
        assert schema["tags"]["type"] == FIELD_TYPE_MULTIPLE_SELECTS

    def test_infer_schema_attachment_column(self):
        """Test dict with url/filename maps to attachment."""
        df = pd.DataFrame(
            {
                "file": [
                    {"url": "http://example.com/1.pdf", "filename": "1.pdf"},
                    {"url": "http://example.com/2.pdf", "filename": "2.pdf"},
                ]
            }
        )
        schema = infer_airtable_schema(df)

        assert "file" in schema
        assert schema["file"]["type"] == FIELD_TYPE_MULTIPLE_ATTACHMENTS

    def test_skips_metadata_columns(self):
        """Test _airtable_ columns are skipped."""
        df = pd.DataFrame({"_airtable_id": ["rec1"], "_airtable_created_time": ["2023-01-01"]})
        schema = infer_airtable_schema(df)

        assert "_airtable_id" not in schema
        assert "_airtable_created_time" not in schema


class TestMergeSchema:
    """Test schema merging with overrides."""

    def test_merge_schema_override_takes_precedence(self):
        """Test user schema takes precedence."""
        inferred = {"name": {"type": "singleLineText"}}
        override = {"name": {"type": "multilineText"}}

        result = merge_schema(inferred, override)

        assert result["name"]["type"] == "multilineText"

    def test_merge_schema_adds_new_fields(self):
        """Test override can add new fields."""
        inferred = {"name": {"type": "singleLineText"}}
        override = {"email": {"type": "email"}}

        result = merge_schema(inferred, override)

        assert "name" in result
        assert "email" in result

    def test_merge_schema_none_override(self):
        """Test None override returns inferred."""
        inferred = {"name": {"type": "singleLineText"}}

        result = merge_schema(inferred, None)

        assert result == inferred

    def test_merge_schema_invalid_type_raises(self):
        """Test invalid field type raises error."""
        inferred = {"name": {"type": "singleLineText"}}
        override = {"name": {"type": "invalidType"}}

        with pytest.raises(AirtableSchemaError):
            merge_schema(inferred, override)


class TestCompareSchemas:
    """Test schema comparison."""

    def test_compare_schemas_matching(self):
        """Test identical schemas compare correctly."""
        df_schema = {"name": {"type": "singleLineText"}, "age": {"type": "number"}}

        field1 = Mock()
        field1.name = "name"
        field1.type = "singleLineText"
        field2 = Mock()
        field2.name = "age"
        field2.type = "number"
        airtable_fields = {"name": field1, "age": field2}

        result = compare_schemas(df_schema, airtable_fields, allow_new_columns=False)

        assert set(result.matching_fields) == {"name", "age"}
        assert result.missing_in_airtable == []
        assert result.can_proceed is True

    def test_compare_schemas_missing_fields(self):
        """Test missing fields are detected."""
        df_schema = {
            "name": {"type": "singleLineText"},
            "email": {"type": "email"},
        }

        field1 = Mock()
        field1.name = "name"
        field1.type = "singleLineText"
        airtable_fields = {"name": field1}

        result = compare_schemas(df_schema, airtable_fields, allow_new_columns=False)

        assert "email" in result.missing_in_airtable
        assert result.can_proceed is False

    def test_compare_schemas_allow_new_columns(self):
        """Test allow_new_columns enables proceeding."""
        df_schema = {"name": {"type": "singleLineText"}, "new_field": {"type": "number"}}

        field1 = Mock()
        field1.name = "name"
        field1.type = "singleLineText"
        airtable_fields = {"name": field1}

        result = compare_schemas(df_schema, airtable_fields, allow_new_columns=True)

        assert result.can_proceed is True
        assert len(result.fields_to_create) == 1
        assert result.fields_to_create[0]["name"] == "new_field"


class TestValueConversion:
    """Test value conversion functions."""

    def test_convert_datetime_to_iso(self):
        """Test datetime conversion to ISO 8601."""
        dt = datetime(2023, 6, 15, 10, 30, 0)
        result = prepare_datetime(dt)

        assert "2023-06-15" in result
        assert "10:30:00" in result

    def test_convert_pandas_timestamp(self):
        """Test pandas Timestamp conversion."""
        ts = pd.Timestamp("2023-06-15 10:30:00")
        result = prepare_datetime(ts)

        assert "2023-06-15" in result

    def test_convert_datetime_string(self):
        """Test datetime string passthrough."""
        result = prepare_datetime("2023-06-15T10:30:00")

        assert "2023-06-15" in result

    def test_convert_attachment_single(self):
        """Test single attachment dict formatting."""
        attachment = {"url": "http://example.com/file.pdf", "filename": "file.pdf"}
        result = prepare_attachment(attachment)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["url"] == "http://example.com/file.pdf"

    def test_convert_attachment_list(self):
        """Test attachment list formatting."""
        attachments = [
            {"url": "http://example.com/1.pdf", "filename": "1.pdf"},
            {"url": "http://example.com/2.pdf", "filename": "2.pdf"},
        ]
        result = prepare_attachment(attachments)

        assert len(result) == 2

    def test_normalize_attachments_full(self):
        """Test attachment normalization from API response."""
        attachments = [
            {
                "id": "att123",
                "url": "http://example.com/file.pdf",
                "filename": "file.pdf",
                "size": 12345,
                "type": "application/pdf",
            }
        ]

        result = normalize_attachments(attachments)

        assert len(result) == 1
        assert "url" in result[0]
        assert "filename" in result[0]
        # Extra fields should be stripped
        assert "id" not in result[0]
        assert "size" not in result[0]

    def test_convert_to_airtable_checkbox(self):
        """Test checkbox value conversion."""
        result = convert_to_airtable_value(1, FIELD_TYPE_CHECKBOX)
        assert result is True

        result = convert_to_airtable_value(0, FIELD_TYPE_CHECKBOX)
        assert result is False

    def test_convert_to_airtable_number(self):
        """Test number value conversion."""
        result = convert_to_airtable_value("42", FIELD_TYPE_NUMBER)
        assert result == 42.0

    def test_convert_to_airtable_none(self):
        """Test None/NaN handling."""
        import numpy as np

        result = convert_to_airtable_value(None, FIELD_TYPE_SINGLE_LINE_TEXT)
        assert result is None

        result = convert_to_airtable_value(np.nan, FIELD_TYPE_NUMBER)
        assert result is None


class TestCoerceDtypes:
    """Test DataFrame type coercion."""

    def test_coerce_datetime_column(self):
        """Test date-like strings are converted."""
        df = pd.DataFrame({"date": ["2023-01-01", "2023-02-01"]})
        result = coerce_dtypes(df)

        assert pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_coerce_numeric_column(self):
        """Test numeric strings are converted."""
        df = pd.DataFrame({"value": ["1", "2", "3"]})
        result = coerce_dtypes(df)

        assert pd.api.types.is_numeric_dtype(result["value"])

    def test_coerce_metadata_datetime(self):
        """Test _airtable_created_time is converted to datetime."""
        df = pd.DataFrame({"_airtable_created_time": ["2023-01-01T00:00:00.000Z"]})
        result = coerce_dtypes(df)

        assert pd.api.types.is_datetime64_any_dtype(result["_airtable_created_time"])

    def test_coerce_mixed_column_stays_object(self):
        """Test mixed types stay as object."""
        df = pd.DataFrame({"mixed": ["hello", 123, "world"]})
        result = coerce_dtypes(df)

        # Should not convert mixed column
        assert result["mixed"].dtype == object

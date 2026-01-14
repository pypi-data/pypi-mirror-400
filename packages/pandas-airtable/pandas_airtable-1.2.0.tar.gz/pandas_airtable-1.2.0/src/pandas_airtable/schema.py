"""Schema inference and type mapping for pandas-airtable."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from pandas_airtable.exceptions import AirtableSchemaError
from pandas_airtable.types import (
    FIELD_TYPE_CHECKBOX,
    FIELD_TYPE_DATE,
    FIELD_TYPE_MULTIPLE_ATTACHMENTS,
    FIELD_TYPE_MULTIPLE_SELECTS,
    FIELD_TYPE_NUMBER,
    FIELD_TYPE_SINGLE_LINE_TEXT,
    SchemaComparisonResult,
)


def infer_airtable_schema(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Infer Airtable schema from a pandas DataFrame.

    Type mapping rules:
    - object/str -> singleLineText
    - int/float -> number
    - bool -> checkbox
    - datetime64[ns] -> date (ISO 8601)
    - list[str] -> multipleSelects
    - dict with url/filename -> multipleAttachments

    Args:
        df: The DataFrame to infer schema from.

    Returns:
        Schema dict in format: {"FieldName": {"type": "...", "options": {...}}}
    """
    schema: dict[str, dict[str, Any]] = {}

    for col in df.columns:
        # Skip metadata columns
        if col.startswith("_airtable_"):
            continue

        dtype = df[col].dtype
        field_type = _infer_field_type(df[col], dtype)
        schema[col] = {"type": field_type}

        # Add options for number types that need decimal precision
        if field_type == FIELD_TYPE_NUMBER and pd.api.types.is_float_dtype(dtype):
            schema[col]["options"] = {"precision": 8}

    return schema


def _infer_field_type(series: pd.Series, dtype: Any) -> str:
    """Infer the Airtable field type for a pandas Series."""
    # Boolean check first (before numeric, since bool is numeric in numpy)
    if pd.api.types.is_bool_dtype(dtype):
        return FIELD_TYPE_CHECKBOX

    # Integer types
    if pd.api.types.is_integer_dtype(dtype):
        return FIELD_TYPE_NUMBER

    # Float types
    if pd.api.types.is_float_dtype(dtype):
        return FIELD_TYPE_NUMBER

    # Datetime types
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return FIELD_TYPE_DATE

    # Object dtype - need to inspect values
    if dtype == object:  # noqa: E721
        return _infer_object_field_type(series)

    # Default to text
    return FIELD_TYPE_SINGLE_LINE_TEXT


def _infer_object_field_type(series: pd.Series) -> str:
    """Infer field type for object dtype by sampling values."""
    # Get non-null values for inspection
    non_null = series.dropna()
    if len(non_null) == 0:
        return FIELD_TYPE_SINGLE_LINE_TEXT

    # Sample up to 100 values for type detection
    sample = non_null.head(100)

    # Check for lists (multipleSelects)
    if sample.apply(lambda x: isinstance(x, list)).any():
        return FIELD_TYPE_MULTIPLE_SELECTS

    # Check for attachment dicts (url/filename pattern)
    if sample.apply(_is_attachment_value).any():
        return FIELD_TYPE_MULTIPLE_ATTACHMENTS

    # Default to single line text
    return FIELD_TYPE_SINGLE_LINE_TEXT


def _is_attachment_value(value: Any) -> bool:
    """Check if a value looks like an attachment."""
    if isinstance(value, dict):
        return "url" in value or "filename" in value
    if isinstance(value, list) and len(value) > 0:
        first = value[0]
        if isinstance(first, dict):
            return "url" in first or "filename" in first
    return False


def merge_schema(
    inferred: dict[str, dict[str, Any]], override: dict[str, dict[str, Any]] | None
) -> dict[str, dict[str, Any]]:
    """Merge inferred schema with user-provided overrides.

    User overrides take precedence over inferred types.

    Args:
        inferred: Schema inferred from DataFrame.
        override: User-provided schema overrides.

    Returns:
        Merged schema dict.

    Raises:
        AirtableSchemaError: If override contains invalid field types.
    """
    if override is None:
        return inferred

    result = inferred.copy()

    valid_types = {
        "singleLineText",
        "multilineText",
        "richText",
        "email",
        "url",
        "phoneNumber",
        "number",
        "currency",
        "percent",
        "duration",
        "date",
        "dateTime",
        "checkbox",
        "singleSelect",
        "multipleSelects",
        "singleCollaborator",
        "multipleCollaborators",
        "multipleRecordLinks",
        "multipleAttachments",
        "formula",
        "rollup",
        "count",
        "lookup",
        "rating",
        "barcode",
        "autoNumber",
        "createdTime",
        "lastModifiedTime",
        "createdBy",
        "lastModifiedBy",
    }

    for field_name, field_spec in override.items():
        field_type = field_spec.get("type")
        if field_type and field_type not in valid_types:
            raise AirtableSchemaError(
                f"Invalid field type '{field_type}' for field '{field_name}'. "
                f"Valid types are: {sorted(valid_types)}"
            )
        result[field_name] = field_spec

    return result


def compare_schemas(
    df_schema: dict[str, dict[str, Any]],
    airtable_fields: dict[str, Any],
    allow_new_columns: bool,
) -> SchemaComparisonResult:
    """Compare DataFrame schema to Airtable table schema.

    Args:
        df_schema: Schema inferred from DataFrame.
        airtable_fields: Dict mapping field names to field info from Airtable.
        allow_new_columns: Whether to allow creating new columns.

    Returns:
        SchemaComparisonResult with comparison details.
    """
    df_field_names = set(df_schema.keys())
    airtable_field_names = set(airtable_fields.keys())

    matching = df_field_names & airtable_field_names
    missing_in_airtable = df_field_names - airtable_field_names
    missing_in_df = airtable_field_names - df_field_names

    # Check for type mismatches in matching fields
    type_mismatches: dict[str, tuple[str, str]] = {}
    for field in matching:
        df_type = df_schema[field].get("type", "")
        at_field = airtable_fields[field]
        at_type = at_field.type if hasattr(at_field, "type") else str(at_field)
        # Note: We don't enforce strict type matching, just record differences
        if df_type != at_type:
            type_mismatches[field] = (df_type, at_type)

    # Determine if we can proceed
    can_proceed = True
    if missing_in_airtable and not allow_new_columns:
        can_proceed = False

    # Build field definitions for fields to create
    fields_to_create: list[dict[str, Any]] = []
    if allow_new_columns:
        for field_name in missing_in_airtable:
            field_spec = df_schema[field_name]
            fields_to_create.append(
                {
                    "name": field_name,
                    "type": field_spec.get("type", FIELD_TYPE_SINGLE_LINE_TEXT),
                    "options": field_spec.get("options", {}),
                }
            )

    return SchemaComparisonResult(
        matching_fields=list(matching),
        missing_in_airtable=list(missing_in_airtable),
        missing_in_dataframe=list(missing_in_df),
        type_mismatches=type_mismatches,
        fields_to_create=fields_to_create,
        can_proceed=can_proceed,
    )


def convert_to_airtable_value(value: Any, field_type: str) -> Any:
    """Convert a pandas value to Airtable API format.

    Args:
        value: The value to convert.
        field_type: The target Airtable field type.

    Returns:
        Value in Airtable API format.
    """
    if pd.isna(value):
        return None

    if field_type in (FIELD_TYPE_DATE, "dateTime"):
        return prepare_datetime(value)

    if field_type == FIELD_TYPE_MULTIPLE_ATTACHMENTS:
        return prepare_attachment(value)

    if field_type == FIELD_TYPE_CHECKBOX:
        return bool(value)

    if field_type == FIELD_TYPE_NUMBER:
        if isinstance(value, (int, float)):
            return value
        return float(value)

    if field_type == FIELD_TYPE_MULTIPLE_SELECTS:
        if isinstance(value, list):
            return value
        return [str(value)]

    # Default: convert to string for text types
    if field_type == FIELD_TYPE_SINGLE_LINE_TEXT:
        return str(value)

    return value


def convert_from_airtable_value(value: Any, field_type: str | None = None) -> Any:
    """Convert an Airtable API value to pandas-compatible format.

    Args:
        value: The value from Airtable API.
        field_type: Optional field type hint.

    Returns:
        Value suitable for pandas DataFrame.
    """
    if value is None:
        return None

    # Attachments are already in list format
    if isinstance(value, list) and len(value) > 0:
        first = value[0]
        if isinstance(first, dict) and ("url" in first or "id" in first):
            # Normalize attachments to {url, filename} format
            return normalize_attachments(value)

    return value


def prepare_attachment(value: dict | list[dict]) -> list[dict[str, str]]:
    """Convert attachment dict(s) to Airtable format: [{"url": ...}].

    Args:
        value: Single attachment dict or list of attachment dicts.

    Returns:
        List of attachment objects with url field.
    """
    if isinstance(value, dict):
        value = [value]

    result = []
    for att in value:
        if isinstance(att, dict):
            # Only include url (required) and filename (optional)
            att_obj: dict[str, str] = {}
            if "url" in att:
                att_obj["url"] = att["url"]
            if "filename" in att:
                att_obj["filename"] = att["filename"]
            if att_obj:
                result.append(att_obj)

    return result


def prepare_datetime(value: Any) -> str:
    """Convert datetime to ISO 8601 string.

    Args:
        value: A datetime value (pandas Timestamp, datetime, or string).

    Returns:
        ISO 8601 formatted string.
    """
    if isinstance(value, str):
        # Already a string, try to parse and re-format
        try:
            dt = pd.to_datetime(value)
            return dt.isoformat()
        except (ValueError, TypeError):
            return value

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


def normalize_attachments(attachments: list[dict]) -> list[dict[str, str]]:
    """Normalize attachment response to {url, filename} format.

    Args:
        attachments: List of attachment dicts from Airtable API.

    Returns:
        List of normalized attachment dicts with url and filename.
    """
    result = []
    for att in attachments:
        normalized: dict[str, str] = {}
        if "url" in att:
            normalized["url"] = att["url"]
        if "filename" in att:
            normalized["filename"] = att["filename"]
        elif "url" in att:
            # Extract filename from URL if not provided
            url = att["url"]
            normalized["filename"] = url.split("/")[-1].split("?")[0]
        if normalized:
            result.append(normalized)
    return result


def coerce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce DataFrame column types based on value inspection.

    Args:
        df: DataFrame to coerce types for.

    Returns:
        DataFrame with coerced types.
    """
    df = df.copy()

    for col in df.columns:
        if col.startswith("_airtable_"):
            # Handle metadata columns specially
            if col == "_airtable_created_time":
                df[col] = pd.to_datetime(df[col], utc=True)
            continue

        # Try to convert object columns to more specific types
        if df[col].dtype == object:
            # Check for boolean values first (before numeric conversion)
            sample = df[col].dropna().head(10)
            if len(sample) > 0 and all(isinstance(v, bool) for v in sample):
                # Column contains booleans, convert to boolean dtype
                df[col] = df[col].astype("boolean")
                continue

            # Try datetime conversion
            try:
                # Check if values look like dates
                if len(sample) > 0 and all(
                    isinstance(v, str) and any(c in v for c in ["-", "/", "T"]) and len(v) >= 8
                    for v in sample
                ):
                    converted = pd.to_datetime(df[col], errors="coerce", format="mixed")
                    # Only use conversion if most values converted successfully
                    if converted.notna().sum() > len(converted) * 0.8:
                        df[col] = converted
                        continue
            except (ValueError, TypeError):
                pass

            # Try numeric conversion
            try:
                numeric = pd.to_numeric(df[col], errors="coerce")
                # Only use conversion if all non-null values converted
                if numeric.notna().sum() == df[col].notna().sum():
                    df[col] = numeric
            except (ValueError, TypeError):
                pass

    return df

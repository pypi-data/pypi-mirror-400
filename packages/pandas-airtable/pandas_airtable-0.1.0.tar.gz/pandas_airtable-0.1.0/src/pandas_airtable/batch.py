"""Batching utilities and record preparation for pandas-airtable."""

from __future__ import annotations

import warnings
from typing import Any

import pandas as pd
from pyairtable import Table

from pandas_airtable.exceptions import AirtableDuplicateKeyError
from pandas_airtable.schema import convert_to_airtable_value, infer_airtable_schema
from pandas_airtable.types import (
    AIRTABLE_CREATED_TIME_COLUMN,
    AIRTABLE_ID_COLUMN,
    MAX_RECORDS_PER_REQUEST,
    BatchError,
    WriteResult,
)
from pandas_airtable.utils import chunk_records, log_batch_operation


def check_duplicate_keys(df: pd.DataFrame, key_field: str, allow_duplicates: bool) -> pd.DataFrame:
    """Check for duplicate keys in DataFrame.

    If allow_duplicates=False and duplicates exist, raise AirtableDuplicateKeyError.
    If allow_duplicates=True, keep last occurrence and warn about dropped rows.

    Args:
        df: DataFrame to check.
        key_field: The field used as key for upsert.
        allow_duplicates: Whether to allow duplicates (keep last).

    Returns:
        DataFrame with duplicates handled.

    Raises:
        AirtableDuplicateKeyError: If duplicates found and not allowed.
    """
    duplicates = df[df[key_field].duplicated(keep=False)]

    if len(duplicates) > 0:
        duplicate_values = duplicates[key_field].unique().tolist()

        if not allow_duplicates:
            raise AirtableDuplicateKeyError(
                f"Found {len(duplicate_values)} duplicate values in key field "
                f"'{key_field}': {duplicate_values[:5]}{'...' if len(duplicate_values) > 5 else ''}. "
                f"Set allow_duplicate_keys=True to use last occurrence.",
                duplicate_values=duplicate_values,
            )
        else:
            # Keep last occurrence, warn about dropped rows
            original_len = len(df)
            df = df.drop_duplicates(subset=[key_field], keep="last")
            dropped_count = original_len - len(df)
            warnings.warn(
                f"Dropped {dropped_count} rows with duplicate keys. "
                f"Using last occurrence for each key.",
                UserWarning,
                stacklevel=2,
            )

    return df


def prepare_records(
    df: pd.DataFrame, schema: dict[str, dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Convert DataFrame rows to Airtable record format.

    Args:
        df: DataFrame to convert.
        schema: Optional schema for type conversion.

    Returns:
        List of {"fields": {...}} dicts ready for API.
    """
    if schema is None:
        schema = infer_airtable_schema(df)

    records: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        fields: dict[str, Any] = {}

        for col, value in row.items():
            # Skip metadata columns
            if col in (AIRTABLE_ID_COLUMN, AIRTABLE_CREATED_TIME_COLUMN):
                continue

            # Skip NaN/None values
            if pd.isna(value):
                continue

            # Convert based on schema type
            field_type = schema.get(str(col), {}).get("type", "singleLineText")
            fields[str(col)] = convert_to_airtable_value(value, field_type)

        records.append({"fields": fields})

    return records


def prepare_update_records(
    df: pd.DataFrame, schema: dict[str, dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Convert DataFrame rows to Airtable update record format.

    Requires _airtable_id column for record identification.

    Args:
        df: DataFrame with _airtable_id column.
        schema: Optional schema for type conversion.

    Returns:
        List of {"id": ..., "fields": {...}} dicts ready for API.
    """
    if AIRTABLE_ID_COLUMN not in df.columns:
        raise ValueError(f"DataFrame must have '{AIRTABLE_ID_COLUMN}' column for update operations")

    if schema is None:
        schema = infer_airtable_schema(df)

    records: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        record_id = row[AIRTABLE_ID_COLUMN]
        if pd.isna(record_id):
            continue

        fields: dict[str, Any] = {}
        for col, value in row.items():
            # Skip metadata columns
            if col in (AIRTABLE_ID_COLUMN, AIRTABLE_CREATED_TIME_COLUMN):
                continue

            # Skip NaN/None values
            if pd.isna(value):
                continue

            field_type = schema.get(str(col), {}).get("type", "singleLineText")
            fields[str(col)] = convert_to_airtable_value(value, field_type)

        records.append({"id": record_id, "fields": fields})

    return records


def execute_batch_create(
    table: Table, records: list[dict[str, Any]], batch_size: int = MAX_RECORDS_PER_REQUEST
) -> WriteResult:
    """Create records in batches.

    Args:
        table: pyairtable Table object.
        records: List of {"fields": {...}} dicts.
        batch_size: Records per batch (max 10).

    Returns:
        WriteResult with operation results.
    """
    batch_size = min(batch_size, MAX_RECORDS_PER_REQUEST)
    batches = chunk_records(records, batch_size)
    total_batches = len(batches)

    created_ids: list[str] = []
    errors: list[BatchError] = []

    for i, batch in enumerate(batches):
        log_batch_operation("create", i + 1, total_batches, len(batch))

        try:
            # Extract just the fields for batch_create
            fields_list = [r["fields"] for r in batch]
            created = table.batch_create(fields_list)
            created_ids.extend(r["id"] for r in created)
        except Exception as e:
            errors.append(BatchError(batch=batch, error=e))

    return WriteResult(
        created_count=len(created_ids),
        updated_count=0,
        deleted_count=0,
        created_ids=created_ids,
        errors=errors,
    )


def execute_batch_update(
    table: Table, records: list[dict[str, Any]], batch_size: int = MAX_RECORDS_PER_REQUEST
) -> WriteResult:
    """Update records in batches.

    Args:
        table: pyairtable Table object.
        records: List of {"id": ..., "fields": {...}} dicts.
        batch_size: Records per batch (max 10).

    Returns:
        WriteResult with operation results.
    """
    batch_size = min(batch_size, MAX_RECORDS_PER_REQUEST)
    batches = chunk_records(records, batch_size)
    total_batches = len(batches)

    updated_ids: list[str] = []
    errors: list[BatchError] = []

    for i, batch in enumerate(batches):
        log_batch_operation("update", i + 1, total_batches, len(batch))

        try:
            updated = table.batch_update(batch)
            updated_ids.extend(r["id"] for r in updated)
        except Exception as e:
            errors.append(BatchError(batch=batch, error=e))

    return WriteResult(
        created_count=0,
        updated_count=len(updated_ids),
        deleted_count=0,
        updated_ids=updated_ids,
        errors=errors,
    )


def execute_batch_upsert(
    table: Table,
    records: list[dict[str, Any]],
    key_fields: list[str],
    batch_size: int = MAX_RECORDS_PER_REQUEST,
) -> WriteResult:
    """Upsert records in batches.

    Args:
        table: pyairtable Table object.
        records: List of {"fields": {...}} dicts.
        key_fields: Fields used for matching existing records.
        batch_size: Records per batch (max 10).

    Returns:
        WriteResult with operation results.
    """
    batch_size = min(batch_size, MAX_RECORDS_PER_REQUEST)
    batches = chunk_records(records, batch_size)
    total_batches = len(batches)

    created_ids: list[str] = []
    updated_ids: list[str] = []
    errors: list[BatchError] = []

    for i, batch in enumerate(batches):
        log_batch_operation("upsert", i + 1, total_batches, len(batch))

        try:
            # batch_upsert expects records in {"fields": {...}} format
            result = table.batch_upsert(batch, key_fields=key_fields, replace=False)

            # pyairtable's batch_upsert returns a dict with:
            # - createdRecords: list of record IDs
            # - updatedRecords: list of record IDs
            # - records: list of full record objects
            if isinstance(result, dict):
                if "createdRecords" in result:
                    created_ids.extend(result["createdRecords"])
                if "updatedRecords" in result:
                    updated_ids.extend(result["updatedRecords"])
            else:
                # Fallback for object-based result (older pyairtable versions)
                if hasattr(result, "created_records") and result.created_records:
                    created_ids.extend(
                        r["id"] if isinstance(r, dict) else r.id for r in result.created_records
                    )
                if hasattr(result, "updated_records") and result.updated_records:
                    updated_ids.extend(
                        r["id"] if isinstance(r, dict) else r.id for r in result.updated_records
                    )
        except Exception as e:
            errors.append(BatchError(batch=batch, error=e))

    return WriteResult(
        created_count=len(created_ids),
        updated_count=len(updated_ids),
        deleted_count=0,
        created_ids=created_ids,
        updated_ids=updated_ids,
        errors=errors,
    )


def execute_batch_delete(
    table: Table, record_ids: list[str], batch_size: int = MAX_RECORDS_PER_REQUEST
) -> WriteResult:
    """Delete records in batches.

    Args:
        table: pyairtable Table object.
        record_ids: List of record IDs to delete.
        batch_size: Records per batch (max 10).

    Returns:
        WriteResult with operation results.
    """
    batch_size = min(batch_size, MAX_RECORDS_PER_REQUEST)
    batches = chunk_records(record_ids, batch_size)
    total_batches = len(batches)

    deleted_count = 0
    errors: list[BatchError] = []

    for i, batch in enumerate(batches):
        log_batch_operation("delete", i + 1, total_batches, len(batch))

        try:
            table.batch_delete(batch)
            deleted_count += len(batch)
        except Exception as e:
            errors.append(BatchError(batch=[{"id": rid} for rid in batch], error=e))

    return WriteResult(
        created_count=0,
        updated_count=0,
        deleted_count=deleted_count,
        errors=errors,
    )

"""DataFrame accessor for writing to Airtable."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pandas as pd
from pyairtable import Api

from pandas_airtable.batch import (
    check_duplicate_keys,
    execute_batch_create,
    execute_batch_delete,
    execute_batch_upsert,
    prepare_records,
)
from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableFieldCreationError,
    AirtablePermissionError,
    AirtableSchemaError,
    AirtableTableNotFoundError,
    AirtableValidationError,
)
from pandas_airtable.schema import compare_schemas, infer_airtable_schema, merge_schema
from pandas_airtable.types import (
    DEFAULT_BATCH_SIZE,
    MAX_RECORDS_PER_REQUEST,
    DryRunResult,
    IfExistsMode,
    WriteResult,
)
from pandas_airtable.utils import get_base_id_from_name

if TYPE_CHECKING:
    from pyairtable import Table

logger = logging.getLogger("pandas_airtable")


@pd.api.extensions.register_dataframe_accessor("airtable")
class AirtableAccessor:
    """Pandas DataFrame accessor for Airtable operations.

    Provides the `df.airtable.to_airtable()` method for writing DataFrames
    to Airtable tables.

    Examples:
        >>> import pandas as pd
        >>> import pandas_airtable
        >>> df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        >>> result = df.airtable.to_airtable(
        ...     base_id="appXXX",
        ...     table_name="Contacts",
        ...     api_key="patXXX"
        ... )
    """

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        """Initialize the accessor.

        Args:
            pandas_obj: The DataFrame this accessor is attached to.
        """
        self._obj = pandas_obj

    def to_airtable(
        self,
        base_id: str | None = None,
        table_name: str | None = None,
        api_key: str | None = None,
        if_exists: IfExistsMode = "append",
        key_field: str | None = None,
        schema: dict[str, dict[str, Any]] | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        create_table: bool = True,
        allow_new_columns: bool = False,
        allow_duplicate_keys: bool = False,
        dry_run: bool = False,
        base_name: str | None = None,
    ) -> WriteResult | DryRunResult:
        """Write DataFrame to an Airtable table.

        Args:
            base_id: The Airtable base ID (e.g., "appXXXXXXXXXXXXXX").
                Either base_id or base_name must be provided.
            table_name: The name of the table to write to.
            api_key: Airtable API key or personal access token.
            if_exists: How to handle existing data:
                - "append": Add new records (default)
                - "replace": Delete all existing records, then add new
                - "upsert": Update existing records by key, create new ones
            key_field: Field name used for upsert matching (required if if_exists="upsert").
            schema: Optional schema override. Dict mapping field names to
                {"type": "...", "options": {...}}.
            batch_size: Records per API batch (default 10, max 10).
            create_table: If True, create table if it doesn't exist (default True).
            allow_new_columns: If True, create missing fields in Airtable (default False).
            allow_duplicate_keys: If True, allow duplicate key values in upsert mode,
                using the last occurrence (default False).
            dry_run: If True, return preview without making changes (default False).
            base_name: The name of the Airtable base. If provided, the base_id
                will be looked up automatically. Note: If there are multiple bases
                with the same name, only the first one will be used. In such cases,
                use base_id instead of base_name to avoid ambiguity.

        Returns:
            WriteResult with created/updated/deleted counts and any errors,
            or DryRunResult if dry_run=True.

        Raises:
            AirtableAuthenticationError: If the API key is invalid.
            AirtableValidationError: If required parameters are missing or invalid.
            AirtableTableNotFoundError: If table doesn't exist and create_table=False.
            AirtableSchemaError: If schema mismatch and allow_new_columns=False.
            AirtableDuplicateKeyError: If duplicate keys in upsert mode.
            ValueError: If base_name is provided but no matching base is found.
        """
        df = self._obj.copy()

        # Handle base_id/base_name lookup
        if not base_id and not base_name:
            raise AirtableValidationError("Either base_id or base_name is required")
        if base_id and base_name:
            raise AirtableValidationError("Provide either base_id or base_name, not both")

        # Look up base_id from base_name if needed
        if base_name:
            if not api_key:
                raise AirtableAuthenticationError(
                    "API key is required. Provide an Airtable API key or personal access token."
                )
            base_id = get_base_id_from_name(api_key, base_name)

        # Step 1: Validate inputs
        _validate_write_inputs(
            base_id=base_id,
            table_name=table_name,
            api_key=api_key,
            if_exists=if_exists,
            key_field=key_field,
            batch_size=batch_size,
            df=df,
        )

        # Step 2: Handle duplicate keys for upsert mode
        if if_exists == "upsert" and key_field:
            df = check_duplicate_keys(df, key_field, allow_duplicate_keys)

        # Step 3: Infer/merge schema
        inferred_schema = infer_airtable_schema(df)
        final_schema = merge_schema(inferred_schema, schema)

        # Step 4: Initialize API
        api = Api(api_key)

        # Step 5: Ensure table exists and get schema
        table, table_exists = _ensure_table_exists(
            api, base_id, table_name, final_schema, create_table
        )

        # Step 6: Sync schema (create missing columns if allowed)
        if table_exists:
            _sync_schema(api, base_id, table_name, final_schema, allow_new_columns)

        # Step 7: Prepare records
        records = prepare_records(df, final_schema)

        # Step 8: Dry run - return preview without making changes
        if dry_run:
            return DryRunResult(
                operation=if_exists,
                record_count=len(records),
                schema=final_schema,
                sample_records=records[:3],
                fields_to_create=[],
                warnings=[],
            )

        # Step 9: Execute write operation
        if if_exists == "append":
            return execute_batch_create(table, records, batch_size)
        elif if_exists == "replace":
            return _execute_replace(table, records, batch_size)
        elif if_exists == "upsert":
            if not key_field:
                raise AirtableValidationError("key_field is required for upsert operation")
            return execute_batch_upsert(table, records, [key_field], batch_size)
        else:
            raise AirtableValidationError(f"Invalid if_exists value: {if_exists}")


def _validate_write_inputs(
    base_id: str,
    table_name: str,
    api_key: str,
    if_exists: str,
    key_field: str | None,
    batch_size: int,
    df: pd.DataFrame,
) -> None:
    """Validate inputs for to_airtable operation.

    Raises:
        AirtableAuthenticationError: If API key is missing.
        AirtableValidationError: If other validations fail.
    """
    if not api_key:
        raise AirtableAuthenticationError(
            "API key is required. Provide an Airtable API key or personal access token."
        )
    if not base_id:
        raise AirtableValidationError("base_id is required")
    if not table_name:
        raise AirtableValidationError("table_name is required")

    if batch_size < 1 or batch_size > MAX_RECORDS_PER_REQUEST:
        raise AirtableValidationError(
            f"batch_size must be between 1 and {MAX_RECORDS_PER_REQUEST} "
            f"(Airtable limit). Got: {batch_size}"
        )

    valid_modes = ("append", "replace", "upsert")
    if if_exists not in valid_modes:
        raise AirtableValidationError(f"if_exists must be one of {valid_modes}. Got: '{if_exists}'")

    if if_exists == "upsert":
        if not key_field:
            raise AirtableValidationError(
                "if_exists='upsert' requires a key_field parameter to identify records for update."
            )
        if key_field not in df.columns:
            raise AirtableValidationError(
                f"key_field '{key_field}' not found in DataFrame columns. "
                f"Available columns: {list(df.columns)}"
            )


def _ensure_table_exists(
    api: Api,
    base_id: str,
    table_name: str,
    schema: dict[str, dict[str, Any]],
    create_table: bool,
) -> tuple[Table, bool]:
    """Check if table exists; create if allowed and necessary.

    Args:
        api: pyairtable Api instance.
        base_id: The base ID.
        table_name: The table name.
        schema: Schema for table creation.
        create_table: Whether to create table if missing.

    Returns:
        Tuple of (Table object, whether table existed).

    Raises:
        AirtableTableNotFoundError: If table doesn't exist and create_table=False.
        AirtablePermissionError: If table creation fails due to permissions.
    """
    base = api.base(base_id)
    table = api.table(base_id, table_name)

    # Try to check if table exists by fetching schema
    try:
        base_schema = base.schema()
        table_names = [t.name for t in base_schema.tables]
        table_exists = table_name in table_names
    except Exception as schema_err:
        # If we can't get schema (API limitations), try a minimal read
        logger.debug(f"Could not fetch base schema: {schema_err}")
        try:
            table.all(max_records=1)
            table_exists = True
        except Exception as e:
            error_str = str(e).lower()
            if "not found" in error_str or "404" in error_str:
                table_exists = False
            elif "unauthorized" in error_str or "401" in error_str or "403" in error_str:
                # Re-raise authentication errors
                raise AirtableAuthenticationError() from e
            else:
                # Log and assume table exists for other errors
                logger.warning(f"Could not verify table existence: {e}")
                table_exists = True

    if not table_exists:
        if not create_table:
            raise AirtableTableNotFoundError(table_name, base_id)

        # Attempt to create table
        try:
            fields = []
            for name, spec in schema.items():
                field_def: dict[str, Any] = {
                    "name": name,
                    "type": spec.get("type", "singleLineText"),
                }
                # Include options for field types that require them
                options = _get_field_options(field_def["type"], spec.get("options"))
                if options:
                    field_def["options"] = options
                fields.append(field_def)

            # Ensure at least one field for table creation
            if not fields:
                fields = [{"name": "Name", "type": "singleLineText"}]

            base.create_table(table_name, fields)
            return api.table(base_id, table_name), False
        except Exception as e:
            raise AirtablePermissionError(
                f"Cannot create table '{table_name}'. This may require an Airtable "
                f"Pro/Enterprise plan or appropriate permissions. Error: {e}",
                base_id=base_id,
            ) from e

    return table, True


def _sync_schema(
    api: Api,
    base_id: str,
    table_name: str,
    df_schema: dict[str, dict[str, Any]],
    allow_new_columns: bool,
) -> None:
    """Compare DataFrame schema to Airtable table and create missing fields.

    Args:
        api: pyairtable Api instance.
        base_id: The base ID.
        table_name: The table name.
        df_schema: Schema inferred from DataFrame.
        allow_new_columns: Whether to create missing fields.

    Raises:
        AirtableSchemaError: If schema mismatch and allow_new_columns=False.
        AirtableFieldCreationError: If field creation fails.
    """
    base = api.base(base_id)

    try:
        base_schema = base.schema()
        table_schema = None
        for t in base_schema.tables:
            if t.name == table_name:
                table_schema = t
                break

        if table_schema is None:
            return  # Table doesn't exist in schema, skip validation

        # Build dict of existing fields
        existing_fields = {f.name: f for f in table_schema.fields}

        # Compare schemas
        comparison = compare_schemas(df_schema, existing_fields, allow_new_columns)

        if not comparison.can_proceed:
            raise AirtableSchemaError(
                f"Schema mismatch: DataFrame has columns {comparison.missing_in_airtable} "
                f"that don't exist in Airtable table '{table_name}'. "
                f"Set allow_new_columns=True to create them automatically.",
                missing_columns=comparison.missing_in_airtable,
            )

        # Create missing fields if allowed
        if comparison.fields_to_create and allow_new_columns:
            # Get the Table object using table ID (required for meta API)
            table_id = table_schema.id
            table = api.table(base_id, table_id)
            for field_def in comparison.fields_to_create:
                try:
                    # Get options for the field type
                    options = _get_field_options(field_def["type"], field_def.get("options"))
                    table.create_field(
                        name=field_def["name"],
                        field_type=field_def["type"],
                        options=options if options else None,
                    )
                except Exception as e:
                    raise AirtableFieldCreationError(field_def["name"], e) from e

    except AirtableSchemaError:
        raise
    except AirtableFieldCreationError:
        raise
    except Exception as e:
        # If we can't get schema (e.g., API limitations), log and skip validation
        logger.debug(f"Could not sync schema (API may not support metadata): {e}")


def _get_field_options(
    field_type: str, existing_options: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Get required options for a field type.

    Airtable API requires certain options for specific field types.

    Args:
        field_type: The Airtable field type.
        existing_options: Existing options from schema (if any).

    Returns:
        Dict of options to include in field definition.
    """
    options: dict[str, Any] = existing_options.copy() if existing_options else {}

    # Number fields require precision
    if field_type == "number" and "precision" not in options:
        options["precision"] = 0  # Default to integer precision

    # Date fields require dateFormat option
    if field_type == "date" and "dateFormat" not in options:
        options["dateFormat"] = {"name": "iso"}

    # Checkbox fields require icon and color options
    if field_type == "checkbox":
        if "icon" not in options:
            options["icon"] = "check"
        if "color" not in options:
            options["color"] = "greenBright"

    # Single/Multi select need options.choices but we can't know them ahead of time

    return options


def _execute_replace(
    table: Table,
    records: list[dict[str, Any]],
    batch_size: int,
) -> WriteResult:
    """Execute replace operation: delete all existing, then create new.

    Args:
        table: pyairtable Table object.
        records: Records to create after deletion.
        batch_size: Records per batch.

    Returns:
        WriteResult with operation counts.
    """
    # Step 1: Fetch all existing record IDs
    existing = table.all()
    existing_ids = [r["id"] for r in existing]

    # Step 2: Delete in batches
    delete_result = execute_batch_delete(table, existing_ids, batch_size)

    # Step 3: Create new records
    create_result = execute_batch_create(table, records, batch_size)

    # Combine results
    return WriteResult(
        created_count=create_result.created_count,
        updated_count=0,
        deleted_count=delete_result.deleted_count,
        created_ids=create_result.created_ids,
        errors=delete_result.errors + create_result.errors,
    )

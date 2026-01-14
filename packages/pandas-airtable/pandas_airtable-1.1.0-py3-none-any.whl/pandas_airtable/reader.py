"""Read Airtable tables into pandas DataFrames."""

from __future__ import annotations

from typing import Any

import pandas as pd
from pyairtable import Api

from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableTableNotFoundError,
    AirtableValidationError,
)
from pandas_airtable.schema import coerce_dtypes, normalize_attachments
from pandas_airtable.types import (
    AIRTABLE_CREATED_TIME_COLUMN,
    AIRTABLE_ID_COLUMN,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from pandas_airtable.utils import get_base_id_from_name


def read_airtable(
    base_id: str | None = None,
    table_name: str | None = None,
    api_key: str | None = None,
    view: str | None = None,
    formula: str | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    base_name: str | None = None,
) -> pd.DataFrame:
    """Read an Airtable table into a pandas DataFrame.

    Fetches all records from the specified Airtable table, handling pagination
    automatically. Records are normalized into a flat DataFrame structure with
    metadata columns for Airtable ID and creation time.

    Args:
        base_id: The Airtable base ID (e.g., "appXXXXXXXXXXXXXX").
            Either base_id or base_name must be provided.
        table_name: The name of the table to read.
        api_key: Airtable API key or personal access token.
        view: Optional view name to filter records.
        formula: Optional Airtable formula to filter records.
        page_size: Number of records per API request (default 100, max 100).
        base_name: The name of the Airtable base. If provided, the base_id
            will be looked up automatically. Note: If there are multiple bases
            with the same name, only the first one will be used. In such cases,
            use base_id instead of base_name to avoid ambiguity.

    Returns:
        DataFrame containing all records with columns:
        - _airtable_id: The Airtable record ID
        - _airtable_created_time: Record creation timestamp
        - [field columns]: One column per Airtable field

    Raises:
        AirtableAuthenticationError: If the API key is invalid.
        AirtableValidationError: If required parameters are missing.
        AirtableTableNotFoundError: If the table does not exist.
        ValueError: If base_name is provided but no matching base is found.

    Examples:
        >>> import pandas as pd
        >>> import pandas_airtable  # Registers accessor and read_airtable
        >>> # Using base_id
        >>> df = pd.read_airtable("appXXX", "Contacts", api_key="patXXX")
        >>> # Using base_name
        >>> df = pd.read_airtable(base_name="My Base", table_name="Contacts", api_key="patXXX")
        >>> df.head()
    """
    # Validate inputs
    if not api_key:
        raise AirtableAuthenticationError(
            "API key is required. Provide an Airtable API key or personal access token."
        )

    # Handle base_id/base_name
    if not base_id and not base_name:
        raise AirtableValidationError("Either base_id or base_name is required")
    if base_id and base_name:
        raise AirtableValidationError("Provide either base_id or base_name, not both")

    # Look up base_id from base_name if needed
    if base_name:
        base_id = get_base_id_from_name(api_key, base_name)

    if not table_name:
        raise AirtableValidationError("table_name is required")

    # Clamp page_size to valid range
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    # Initialize pyairtable
    api = Api(api_key)
    table = api.table(base_id, table_name)

    # Build query parameters
    query_params: dict[str, Any] = {"page_size": page_size}
    if view:
        query_params["view"] = view
    if formula:
        query_params["formula"] = formula

    # Fetch all records (pyairtable handles pagination internally)
    try:
        records = table.all(**query_params)
    except Exception as e:
        error_str = str(e).lower()
        if "not found" in error_str or "404" in error_str:
            raise AirtableTableNotFoundError(table_name, base_id) from e
        if "unauthorized" in error_str or "401" in error_str or "403" in error_str:
            raise AirtableAuthenticationError() from e
        raise

    # Handle empty result
    if not records:
        return pd.DataFrame()

    # Build list of row dicts
    rows = []
    for record in records:
        row = {
            AIRTABLE_ID_COLUMN: record.get("id"),
            AIRTABLE_CREATED_TIME_COLUMN: record.get("createdTime"),
        }

        # Normalize and add fields
        fields = record.get("fields", {})
        normalized_fields = _normalize_fields(fields)
        row.update(normalized_fields)

        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Ensure metadata columns come first
    cols = [AIRTABLE_ID_COLUMN, AIRTABLE_CREATED_TIME_COLUMN]
    other_cols = [c for c in df.columns if c not in cols]
    df = df[cols + other_cols]

    # Coerce dtypes
    df = coerce_dtypes(df)

    return df


def _normalize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Normalize Airtable field values for DataFrame compatibility.

    Handles special field types:
    - Attachments: Convert to list of {"url": ..., "filename": ...}
    - Linked records: Keep as list of record IDs
    - Collaborators: Extract relevant info
    - Other arrays: Flatten if single value

    Args:
        fields: Dictionary of field names to values from Airtable.

    Returns:
        Dictionary with normalized values.
    """
    result: dict[str, Any] = {}

    for field_name, value in fields.items():
        if value is None:
            result[field_name] = None
            continue

        # Handle lists (attachments, linked records, multiple selects, etc.)
        if isinstance(value, list):
            if len(value) == 0:
                result[field_name] = None
                continue

            # Check if it's a list of attachment dicts
            if isinstance(value[0], dict) and ("url" in value[0] or "id" in value[0]):
                # Check if it looks like attachments (has url/filename)
                if "url" in value[0]:
                    result[field_name] = normalize_attachments(value)
                else:
                    # Likely linked records - just keep as list of IDs
                    result[field_name] = [
                        v.get("id", v) if isinstance(v, dict) else v for v in value
                    ]
            elif isinstance(value[0], str):
                # Multiple select or linked record IDs
                result[field_name] = value
            else:
                # Other list types - keep as is
                result[field_name] = value
        elif isinstance(value, dict):
            # Handle single objects (collaborator, etc.)
            if "email" in value:
                result[field_name] = value.get("email")
            elif "name" in value:
                result[field_name] = value.get("name")
            else:
                result[field_name] = value
        else:
            # Scalar values - keep as is
            result[field_name] = value

    return result

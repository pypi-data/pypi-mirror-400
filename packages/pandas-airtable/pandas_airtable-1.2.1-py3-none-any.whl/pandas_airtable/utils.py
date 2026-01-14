"""Shared utility functions and logging for pandas-airtable."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pyairtable import Api

logger = logging.getLogger("pandas_airtable")


def log_batch_operation(
    operation: str, batch_num: int, total_batches: int, record_count: int
) -> None:
    """Log structured information about batch operations."""
    logger.info(
        json.dumps(
            {
                "event": "batch_operation",
                "operation": operation,
                "batch": batch_num,
                "total_batches": total_batches,
                "records": record_count,
            }
        )
    )


def log_retry(attempt: int, max_retries: int, delay: float, error: str) -> None:
    """Log retry attempts with backoff info."""
    logger.warning(
        json.dumps(
            {
                "event": "retry",
                "attempt": attempt,
                "max_retries": max_retries,
                "delay_seconds": delay,
                "error": error,
            }
        )
    )


def log_api_response(operation: str, status: str, record_count: int, duration_ms: float) -> None:
    """Log API response details."""
    logger.debug(
        json.dumps(
            {
                "event": "api_response",
                "operation": operation,
                "status": status,
                "records": record_count,
                "duration_ms": duration_ms,
            }
        )
    )


def chunk_records(records: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split a list of records into chunks of specified size."""
    return [records[i : i + chunk_size] for i in range(0, len(records), chunk_size)]


def to_snake_case(name: str) -> str:
    """Convert a field name to snake_case.

    Handles common patterns like CamelCase, spaces, and special characters.
    """
    # Replace spaces, hyphens, and other separators with underscores
    name = re.sub(r"[\s\-\.]+", "_", name)
    # Insert underscore before uppercase letters (for CamelCase)
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    # Convert to lowercase
    name = name.lower()
    # Remove any non-alphanumeric characters except underscore
    name = re.sub(r"[^a-z0-9_]", "", name)
    # Remove consecutive underscores
    name = re.sub(r"_+", "_", name)
    # Strip leading/trailing underscores
    name = name.strip("_")
    return name


def normalize_column_name(name: str) -> str:
    """Normalize an Airtable field name to a valid DataFrame column name."""
    return to_snake_case(name)


def get_base_id_from_name(api_key: str, base_name: str) -> str:
    """Get the base ID from the base name using the Airtable API.

    Note: If there are multiple bases with the same name, only the first one
    will be returned. In such cases, use base_id directly instead of base_name
    to avoid ambiguity.

    Args:
        api_key: Airtable API key or personal access token.
        base_name: The name of the base to look up.

    Returns:
        The base ID (e.g., "appXXXXXXXXXXXXXX").

    Raises:
        ValueError: If no base with the given name is found.

    Examples:
        >>> base_id = get_base_id_from_name("patXXX", "My Base")
        >>> print(base_id)
        appXXXXXXXXXXXXXX
    """
    api = Api(api_key=api_key)
    bases = api.bases()

    for base in bases:
        if base.name == base_name:
            logger.info(f"Found base '{base_name}' with ID: {base.id}")
            return base.id

    raise ValueError(f"Base with name '{base_name}' not found.")

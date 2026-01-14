"""Integration test fixtures and configuration.

These tests run against the real Airtable API and require:
- AIRTABLE_API_KEY: Valid API key or personal access token
- AIRTABLE_BASE_ID: Base ID to use for testing (will create/delete tables)
  OR
- AIRTABLE_BASE_NAME: Base name to look up the base ID automatically
  (Note: If there are multiple bases with the same name, only the first one
  will be used. In such cases, use AIRTABLE_BASE_ID instead for clarity.)

Tests are skipped if these environment variables are not set.
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Generator
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv
from pyairtable import Api

from pandas_airtable.utils import get_base_id_from_name

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_airtable_credentials() -> tuple[str, str] | None:
    """Get Airtable credentials from environment variables.

    Returns tuple of (api_key, base_id) if credentials are available.
    If AIRTABLE_BASE_NAME is provided instead of AIRTABLE_BASE_ID,
    the base_id will be looked up automatically.
    """
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    base_name = os.environ.get("AIRTABLE_BASE_NAME")

    if not api_key:
        return None

    if not base_id and not base_name:
        return None

    # If base_name is provided, look up the base_id
    if base_name and not base_id:
        try:
            base_id = get_base_id_from_name(api_key, base_name)
        except ValueError as e:
            print(f"Warning: Could not find base with name '{base_name}': {e}")
            return None

    return api_key, base_id


# Skip all integration tests if credentials are not available
pytestmark = pytest.mark.skipif(
    get_airtable_credentials() is None,
    reason="AIRTABLE_API_KEY and (AIRTABLE_BASE_ID or AIRTABLE_BASE_NAME) environment variables required",
)


@pytest.fixture(scope="session")
def airtable_credentials() -> tuple[str, str]:
    """Provide Airtable credentials for tests."""
    creds = get_airtable_credentials()
    if creds is None:
        pytest.skip("Airtable credentials not configured")
    return creds


@pytest.fixture(scope="session")
def api_key(airtable_credentials: tuple[str, str]) -> str:
    """Provide just the API key."""
    return airtable_credentials[0]


@pytest.fixture(scope="session")
def base_id(airtable_credentials: tuple[str, str]) -> str:
    """Provide just the base ID."""
    return airtable_credentials[1]


@pytest.fixture(scope="session")
def airtable_api(api_key: str) -> Api:
    """Create a pyairtable Api instance."""
    return Api(api_key)


@pytest.fixture
def unique_table_name() -> str:
    """Generate a unique table name for test isolation."""
    return f"test_{uuid.uuid4().hex[:8]}"


def _delete_table_by_name(base, table_name: str) -> bool:
    """Delete a table by name. Returns True if deleted.

    NOTE: The Airtable API does not support table deletion.
    Tables must be deleted manually via the Airtable web interface.
    This function is kept for documentation purposes but always returns False.
    """
    # Airtable API does not support table deletion - tables must be deleted manually
    return False


def _cleanup_test_tables(base) -> int:
    """Count tables matching test pattern (test_*).

    NOTE: The Airtable API does not support table deletion.
    This function only counts test tables and prints a warning if any exist.
    Tables must be deleted manually via the Airtable web interface.
    """
    count = 0
    try:
        schema = base.schema()
        for table in schema.tables:
            if table.name.startswith("test_"):
                count += 1
    except Exception as e:
        print(f"Warning: Could not check for test tables: {e}")
    return count


@pytest.fixture
def created_tables(airtable_api: Api, base_id: str) -> Generator[list[str]]:
    """Track created tables for cleanup after tests.

    Yields a list that tests can append table names to.
    All tables in the list are deleted after the test completes.
    """
    tables_to_cleanup: list[str] = []
    yield tables_to_cleanup

    # Cleanup: delete all created tables
    base = airtable_api.base(base_id)
    for table_name in tables_to_cleanup:
        _delete_table_by_name(base, table_name)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_tables_before_and_after_session(
    airtable_credentials: tuple[str, str],
) -> Generator[None]:
    """Session-scoped fixture that warns about test tables.

    NOTE: The Airtable API does not support table deletion.
    This fixture only counts test tables and prints warnings.
    Tables must be deleted manually via the Airtable web interface.

    BEFORE: Warns about any leftover test tables from previous runs.
    AFTER: Warns about any test tables created during this run.
    """
    api_key, base_id = airtable_credentials
    api = Api(api_key)
    base = api.base(base_id)

    # Pre-test check: count any leftover test tables
    count_before = _cleanup_test_tables(base)
    if count_before > 0:
        print(
            f"\nWARNING: Found {count_before} leftover test_* table(s). "
            "These must be deleted manually via Airtable web interface."
        )

    yield  # Run all tests

    # Post-test check: count any remaining test tables
    count_after = _cleanup_test_tables(base)
    if count_after > 0:
        print(
            f"\nWARNING: {count_after} test_* table(s) remain. "
            "Delete them manually via Airtable web interface."
        )


@pytest.fixture
def test_table(
    airtable_api: Api,
    base_id: str,
    unique_table_name: str,
    created_tables: list[str],
) -> Generator[tuple[str, str]]:
    """Create a fresh test table for each test.

    - Creates a new table with unique name
    - Registers it for cleanup after test
    - Yields (table_name, base_id) tuple
    - Table is deleted after each test that uses this fixture
    """
    base = airtable_api.base(base_id)

    # Create a basic table with Name and Value fields
    fields = [
        {"name": "Name", "type": "singleLineText"},
        {"name": "Value", "type": "number", "options": {"precision": 0}},
    ]

    try:
        base.create_table(unique_table_name, fields)
        created_tables.append(unique_table_name)
        # Small delay to ensure table is ready
        time.sleep(0.5)
        yield unique_table_name, base_id
    except Exception as e:
        pytest.skip(f"Could not create test table: {e}")


@pytest.fixture
def clean_test_table(
    airtable_api: Api,
    base_id: str,
    test_table: tuple[str, str],
) -> tuple[str, str]:
    """Ensure test table is empty before test runs.

    Use this fixture when you need a guaranteed empty table.
    """
    table_name, _ = test_table
    delete_all_records(airtable_api, base_id, table_name)
    return test_table


# Sample DataFrames for testing


@pytest.fixture
def simple_dataframe() -> pd.DataFrame:
    """Simple DataFrame with basic types."""
    return pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Charlie"],
            "Value": [100, 200, 300],
        }
    )


@pytest.fixture
def dataframe_with_all_types() -> pd.DataFrame:
    """DataFrame with all supported data types."""
    return pd.DataFrame(
        {
            "text_field": ["Hello", "World", "Test"],
            "number_int": [1, 2, 3],
            "number_float": [1.5, 2.5, 3.5],
            "checkbox_field": [True, False, True],
            "date_field": pd.to_datetime(["2024-01-15", "2024-06-20", "2024-12-25"]),
        }
    )


@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """DataFrame with 50 rows for batch testing."""
    return pd.DataFrame(
        {
            "Name": [f"Item_{i}" for i in range(50)],
            "Value": list(range(50)),
        }
    )


@pytest.fixture
def dataframe_with_duplicates() -> pd.DataFrame:
    """DataFrame with duplicate key values for upsert testing."""
    return pd.DataFrame(
        {
            "email": ["a@test.com", "b@test.com", "a@test.com", "c@test.com"],
            "name": ["Alice", "Bob", "Alice Updated", "Charlie"],
            "score": [100, 200, 150, 300],
        }
    )


@pytest.fixture
def dataframe_with_nulls() -> pd.DataFrame:
    """DataFrame with null/NaN values."""
    return pd.DataFrame(
        {
            "Name": ["Alice", None, "Charlie"],
            "Value": [100, 200, None],
            "Active": [True, None, False],
        }
    )


@pytest.fixture
def dataframe_with_special_chars() -> pd.DataFrame:
    """DataFrame with special characters in values."""
    return pd.DataFrame(
        {
            "Name": ["Test & Demo", "Line1\nLine2", 'Quote\'s "Test"'],
            "Value": [1, 2, 3],
        }
    )


@pytest.fixture
def dataframe_for_schema_evolution() -> pd.DataFrame:
    """DataFrame with extra columns for schema evolution testing."""
    return pd.DataFrame(
        {
            "Name": ["Test1", "Test2"],
            "Value": [100, 200],
            "NewTextField": ["extra1", "extra2"],
            "NewNumberField": [10, 20],
        }
    )


# Utility functions for tests


def wait_for_api(seconds: float = 0.3) -> None:
    """Wait to avoid rate limiting."""
    time.sleep(seconds)


def delete_all_records(api: Api, base_id: str, table_name: str) -> None:
    """Delete all records from a table."""
    table = api.table(base_id, table_name)
    records = table.all()
    if records:
        record_ids = [r["id"] for r in records]
        # Delete in batches of 10
        for i in range(0, len(record_ids), 10):
            batch = record_ids[i : i + 10]
            table.batch_delete(batch)
            wait_for_api()

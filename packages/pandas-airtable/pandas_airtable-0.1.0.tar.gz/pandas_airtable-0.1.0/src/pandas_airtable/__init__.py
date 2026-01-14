"""pandas-airtable: A pandas wrapper for Airtable.

This package provides seamless integration between pandas DataFrames and Airtable,
allowing you to read from and write to Airtable tables using familiar pandas patterns.

Usage:
    >>> import pandas as pd
    >>> import pandas_airtable
    >>>
    >>> # Read from Airtable
    >>> df = pd.read_airtable("appXXX", "TableName", api_key="patXXX")
    >>>
    >>> # Write to Airtable
    >>> df.airtable.to_airtable("appXXX", "TableName", api_key="patXXX")
"""

from __future__ import annotations

import pandas as pd

# Import accessor to trigger registration (side effect)
from pandas_airtable.accessor import AirtableAccessor
from pandas_airtable.exceptions import (
    AirtableAuthenticationError,
    AirtableBatchError,
    AirtableDuplicateKeyError,
    AirtableFieldCreationError,
    AirtablePermissionError,
    AirtableRateLimitError,
    AirtableSchemaError,
    AirtableTableNotFoundError,
    AirtableValidationError,
    PandasAirtableError,
)
from pandas_airtable.reader import read_airtable
from pandas_airtable.types import (
    BatchError,
    DryRunResult,
    SchemaComparisonResult,
    WriteResult,
)

# Attach read_airtable to pandas namespace
pd.read_airtable = read_airtable  # type: ignore[attr-defined]

__version__ = "0.1.0"

__all__ = [
    # Main functions
    "read_airtable",
    "AirtableAccessor",
    # Result types
    "WriteResult",
    "DryRunResult",
    "BatchError",
    "SchemaComparisonResult",
    # Exceptions
    "PandasAirtableError",
    "AirtableAuthenticationError",
    "AirtablePermissionError",
    "AirtableRateLimitError",
    "AirtableSchemaError",
    "AirtableValidationError",
    "AirtableBatchError",
    "AirtableDuplicateKeyError",
    "AirtableTableNotFoundError",
    "AirtableFieldCreationError",
]


def main() -> None:
    """CLI entry point."""
    print("pandas-airtable: A pandas wrapper for Airtable.")
    print("Use 'import pandas_airtable' in your Python code.")
    print()
    print("Quick start:")
    print("  >>> import pandas as pd")
    print("  >>> import pandas_airtable")
    print("  >>> df = pd.read_airtable('appXXX', 'Table', api_key='patXXX')")
    print("  >>> df.airtable.to_airtable('appXXX', 'Table', api_key='patXXX')")

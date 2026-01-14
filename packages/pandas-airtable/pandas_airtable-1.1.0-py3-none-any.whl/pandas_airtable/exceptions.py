"""Custom exception classes for pandas-airtable."""

from __future__ import annotations

from typing import Any


class PandasAirtableError(Exception):
    """Base exception class for pandas-airtable."""

    pass


class AirtableAuthenticationError(PandasAirtableError):
    """Raised when the API key is invalid or missing."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message
            or "Invalid Airtable API key. Please verify your API key or personal access token "
            "at https://airtable.com/create/tokens"
        )


class AirtablePermissionError(PandasAirtableError):
    """Raised when the user lacks permissions for an operation."""

    def __init__(self, message: str, base_id: str | None = None) -> None:
        if base_id:
            message = (
                f"{message} Check that your API key has access to base '{base_id}' "
                "and that your plan supports this feature."
            )
        super().__init__(message)
        self.base_id = base_id


class AirtableRateLimitError(PandasAirtableError):
    """Raised when rate limits are exceeded after all retries."""

    def __init__(self, retries: int, last_error: Exception | None = None) -> None:
        super().__init__(
            f"Rate limit exceeded after {retries} retries. Airtable allows 5 requests per "
            "second per base. Consider reducing batch frequency or using smaller batches."
        )
        self.retries = retries
        self.last_error = last_error


class AirtableSchemaError(PandasAirtableError):
    """Raised when there is a schema mismatch or invalid schema."""

    def __init__(
        self,
        message: str,
        missing_columns: list[str] | None = None,
        type_mismatches: dict[str, tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.missing_columns = missing_columns or []
        self.type_mismatches = type_mismatches or {}


class AirtableValidationError(PandasAirtableError):
    """Raised when input validation fails."""

    pass


class AirtableBatchError(PandasAirtableError):
    """Raised when a batch operation partially fails."""

    def __init__(
        self,
        message: str,
        failed_records: list[dict[str, Any]] | None = None,
        errors: list[Exception] | None = None,
    ) -> None:
        super().__init__(message)
        self.failed_records = failed_records or []
        self.errors = errors or []


class AirtableDuplicateKeyError(PandasAirtableError):
    """Raised when duplicate keys are found in upsert mode."""

    def __init__(self, message: str, duplicate_values: list[Any] | None = None) -> None:
        super().__init__(message)
        self.duplicate_values = duplicate_values or []


class AirtableTableNotFoundError(PandasAirtableError):
    """Raised when the specified table does not exist."""

    def __init__(self, table_name: str, base_id: str) -> None:
        super().__init__(
            f"Table '{table_name}' not found in base '{base_id}'. "
            "Verify the table name or set create_table=True to create it automatically."
        )
        self.table_name = table_name
        self.base_id = base_id


class AirtableFieldCreationError(PandasAirtableError):
    """Raised when field creation fails."""

    def __init__(self, field_name: str, error: Exception | None = None) -> None:
        msg = f"Failed to create field '{field_name}'"
        if error:
            msg = f"{msg}: {error}"
        super().__init__(msg)
        self.field_name = field_name
        self.original_error = error

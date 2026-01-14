"""Type definitions and constants for pandas-airtable."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# Airtable API limits
MAX_RECORDS_PER_REQUEST = 10
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 100
DEFAULT_BATCH_SIZE = 10
RATE_LIMIT_QPS = 5

# if_exists mode literals
IfExistsMode = Literal["append", "replace", "upsert"]
IF_EXISTS_APPEND = "append"
IF_EXISTS_REPLACE = "replace"
IF_EXISTS_UPSERT = "upsert"

# Reserved column names
AIRTABLE_ID_COLUMN = "_airtable_id"
AIRTABLE_CREATED_TIME_COLUMN = "_airtable_created_time"

# Airtable field type strings
FIELD_TYPE_SINGLE_LINE_TEXT = "singleLineText"
FIELD_TYPE_MULTILINE_TEXT = "multilineText"
FIELD_TYPE_NUMBER = "number"
FIELD_TYPE_CHECKBOX = "checkbox"
FIELD_TYPE_DATE = "date"
FIELD_TYPE_DATE_TIME = "dateTime"
FIELD_TYPE_MULTIPLE_SELECTS = "multipleSelects"
FIELD_TYPE_SINGLE_SELECT = "singleSelect"
FIELD_TYPE_MULTIPLE_ATTACHMENTS = "multipleAttachments"
FIELD_TYPE_MULTIPLE_RECORD_LINKS = "multipleRecordLinks"
FIELD_TYPE_EMAIL = "email"
FIELD_TYPE_URL = "url"
FIELD_TYPE_PHONE_NUMBER = "phoneNumber"
FIELD_TYPE_CURRENCY = "currency"
FIELD_TYPE_PERCENT = "percent"


@dataclass
class BatchError:
    """Structured error report for a failed batch."""

    batch: list[dict[str, Any]]
    error: Exception
    record_indices: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "affected_records": len(self.batch),
            "record_indices": self.record_indices,
        }


@dataclass
class WriteResult:
    """Result of a write operation to Airtable."""

    created_count: int
    updated_count: int
    deleted_count: int
    created_ids: list[str] = field(default_factory=list)
    updated_ids: list[str] = field(default_factory=list)
    errors: list[BatchError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def total_affected(self) -> int:
        return self.created_count + self.updated_count + self.deleted_count

    def __repr__(self) -> str:
        return (
            f"WriteResult(created={self.created_count}, updated={self.updated_count}, "
            f"deleted={self.deleted_count}, errors={len(self.errors)})"
        )


@dataclass
class DryRunResult:
    """Preview of changes without executing."""

    operation: str
    record_count: int
    schema: dict[str, dict[str, Any]]
    sample_records: list[dict[str, Any]]
    fields_to_create: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"DryRunResult(operation='{self.operation}', records={self.record_count}, "
            f"fields_to_create={self.fields_to_create})"
        )


@dataclass
class SchemaComparisonResult:
    """Result of comparing DataFrame schema to Airtable schema."""

    matching_fields: list[str]
    missing_in_airtable: list[str]
    missing_in_dataframe: list[str]
    type_mismatches: dict[str, tuple[str, str]]
    fields_to_create: list[dict[str, Any]]
    can_proceed: bool

    def __repr__(self) -> str:
        return (
            f"SchemaComparisonResult(matching={len(self.matching_fields)}, "
            f"missing_in_airtable={self.missing_in_airtable}, can_proceed={self.can_proceed})"
        )

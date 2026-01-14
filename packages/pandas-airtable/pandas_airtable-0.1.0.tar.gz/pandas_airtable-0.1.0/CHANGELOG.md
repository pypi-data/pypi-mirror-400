# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of pandas-airtable
- `pd.read_airtable()` function for reading Airtable tables into DataFrames
- `df.airtable.to_airtable()` accessor for writing DataFrames to Airtable
- Support for append, replace, and upsert write modes
- Automatic schema inference from pandas dtypes to Airtable field types
- Custom schema override support
- Automatic batching (10 records per request)
- Built-in rate limiting (5 QPS) with exponential backoff
- Table creation when table doesn't exist (`create_table=True`)
- Field creation for missing columns (`allow_new_columns=True`)
- Duplicate key handling for upsert mode (`allow_duplicate_keys`)
- Dry run mode for previewing changes
- View and formula filtering for reads
- Comprehensive exception hierarchy for error handling
- Full type hints throughout the codebase
- 97 unit tests and 90 integration tests

### Type Mappings
- `object`/`str` → Single line text
- `int64`/`int32` → Number (integer)
- `float64`/`float32` → Number (decimal)
- `bool` → Checkbox
- `datetime64[ns]` → Date
- `list[str]` → Multiple select
- `dict` with `url`/`filename` → Attachment

## [0.1.0] - 2025-01-09

### Added
- Initial public release

[Unreleased]: https://github.com/YOUR_USERNAME/pandas-airtable/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YOUR_USERNAME/pandas-airtable/releases/tag/v0.1.0

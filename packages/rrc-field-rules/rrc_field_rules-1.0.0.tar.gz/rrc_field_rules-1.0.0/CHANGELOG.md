# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-08

### Added

- 🎉 **Stable Release** - First production-ready release
- Comprehensive test coverage (34 tests)
- Full documentation and PyPI publication

## [0.2.0] - 2026-01-08

### Added

- **Human-Readable Code Expansion**
  - New `expand_codes` parameter in `ParserConfig` to expand coded values to text
  - CLI flag `--expand-codes` / `-e` for the `export` command
  - Supports all coded fields:
    - `field_class_code`: O → Oil, G → Gas, B → Both
    - `field_h2s_flag`: Y → Yes - H2S Present, N → No, E → Exempt
    - `oil_or_gas_code`, `rule_type_code`, `diagonal_type_code`
    - `derived_rule_type_code`, `std_field_rule_code`
    - `offshore_code`, `district_code`
    - All Y/N flags: `wildcat_flag`, `salt_dome_flag`, `dont_permit_flag`, etc.
- New `codes.py` module with `expand_code()` and `expand_record()` functions
- 21 new tests for code expansion functionality (34 total tests)

### Changed

- Environment variable `RRC_EXPAND_CODES` can enable code expansion globally

## [0.1.0] - 2026-01-08

### Added

- Initial release of the RRC Field Rules Parser module
- **Core Features**
  - `FieldRulesParser` class for database connectivity and data extraction
  - `ParserConfig` for Pydantic-based configuration with environment variable support
  - Connection pooling via `oracledb`
  - Health check functionality
- **Data Models** (Pydantic v2)
  - `OgField` - Oil & Gas Field master records
  - `OgFieldInfo` - Field information with discovery dates
  - `OgFieldRule` - Field-specific spacing rules
  - `OgStdFieldRule` - Statewide standard rules
- **CLI** (Typer + Rich)
  - `rrc-field-rules check` - Database health check with table counts
  - `rrc-field-rules export` - Export tables to JSON
  - `rrc-field-rules list-tables` - Display available tables
- **Export Capabilities**
  - Export single table or all tables to JSON
  - Optional record limit
  - ISO 8601 date serialization
- **Documentation**
  - Comprehensive README with usage examples
  - Full schema documentation
  - Python API reference
- **Modern Python Packaging**
  - `pyproject.toml` with PEP 621 metadata
  - `hatchling` build backend
  - Development dependencies: pytest, ruff, mypy

### Infrastructure

- Docker Compose setup for Oracle Free container
- Automated data import from Oracle `.dmp` files
- `OracleContainer` helper class for container management

[Unreleased]: https://github.com/jippylong12/rrc_field_rules/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jippylong12/rrc_field_rules/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/jippylong12/rrc_field_rules/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jippylong12/rrc_field_rules/releases/tag/v0.1.0

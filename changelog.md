# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-14

### Added
- **CLI Utility**: Introduced the `pint-glass` command-line tool.
- **Unit Configuration Export**: Added `export_dimensions` function to export unit systems and dimensions to JSON.
- **Frontend Synchronization**: New `pint-glass export` command allows bundling unit definitions into frontend builds for instant UI rendering.
- **API Cache Support**: Pre-calculated unit configurations are now available for backend caching.

## [0.3.0] - 2025-11-20

### Added
- Support for `engg_si` and `engg_field` unit systems.
- Context-aware unit conversion for FastAPI middleware.
- `PintGlass` field type for Pydantic models.

## [0.2.0] - 2025-09-15

### Added
- Basic unit conversion for Imperial and SI systems.
- Pydantic v2 compatibility.
- Initial release of core conversion logic.

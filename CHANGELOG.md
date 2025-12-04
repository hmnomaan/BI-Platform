# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1] - 2025-11-22

### Added
- Bumped package version to `1.0.1` in `setup.py`.
- Added `RELEASE.md` with planned enhancements and next steps.
- Added `bi_dashboard/config_loader.py` to load YAML/JSON configs with environment overrides.
- Added `bi_dashboard/factory.py` as a minimal chart factory (Plotly) to build charts from config.
- Added `api_engine/secrets_manager.py` as a simple secrets abstraction.
- Added `api_engine/providers/registry.py` to register and retrieve provider adapter classes by name.
- Updated `build_package.py` to dynamically read package version from `setup.py` when printing install hints.

### Changed
- Packaging instructions now reference the actual version parsed from `setup.py`.

## [1.0.0] - Initial release

- Initial project skeleton and modules.

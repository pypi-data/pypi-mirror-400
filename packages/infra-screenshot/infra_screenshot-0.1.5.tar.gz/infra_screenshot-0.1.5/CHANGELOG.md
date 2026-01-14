# Changelog

All notable changes to `infra-screenshot` will be documented in this file.

## [0.1.5] - 2026-01-07

### Added
- Added scroll tuning options (`scroll_step_delay_ms`, `max_scroll_steps`) to capture options and CLI flags (`--scroll-step-delay-ms`, `--max-scroll-steps`).
- Added performance harness documentation and script (`docs/perf-testing.md`, `scripts/perf_screenshot.py`).

### Changed
- Updated scroll tuning defaults to 250ms per step and 15 max steps.
- Introduced new timing field `post_scroll_wait_ms` to control delay after scrolling.

### Fixed
- Skipped the post-scroll wait when scrolling is disabled or `pre_capture_wait_s` already covers the delay.

## [0.1.4] - 2025-12-02

### Added
- Added `tablet` viewport preset (768x1024, 2x scale) to match README documentation.

### Changed
- Reorganized documentation: moved architecture and mutability notes from README to `docs/architecture.md`.
- Moved release readiness section from README to CONTRIBUTING.md.
- Updated `docs/index.md` to include architecture reference.

### Fixed
- Fixed CLI config file (`cli_v1.json`) missing from package distribution (MANIFEST.in only included `*.yaml`).
- Fixed `--max-viewport-concurrency` help text claiming default of 3 when actual default is 1.
- Fixed `ScreenshotService.capture_async` crashing entire batch on single job failure; now returns per-job error results.

### Removed
- Cleaned up outdated `.dev_docs/` files (verification reports, migration guides, issue tracking docs).

## [0.1.3] - 2025-11-23

### Changed
- Updated pre-commit hooks configuration.
- Minor documentation updates.

## [0.1.2] - 2025-11-18

### Changed
- Reference updates and style improvements.

## [0.1.1] - 2025-11-17

### Fixed
- Small fixes and renamings from initial release.

## [0.1.0] - 2025-11-17

### Added
- Initial public packaging of the shared screenshot models, services, and CLI.
- Bundled documentation and configuration assets for offline reference.
- Dual licensing clarified with updated `LICENSE` and `NOTICE` contents.
- Test isolation via autouse fixture to prevent environment pollution between tests.
- Documentation for test environment variables (RUN_E2E, RUN_REAL_SITES, SKIP_PLAYWRIGHT_NAV_TESTS).

### Changed
- **BREAKING**: `collect_job_specs()` now returns `list[ScreenshotJobSpec]` instead of `list[dict[str, object]]`.
- **BREAKING**: Reduced public API surface in `models.py` from 44 to 8 exports. Internal types are still importable but not in `__all__`.
- Minimum timeout for Playwright runner increased from 1.0 to 5.0 seconds for better real-world reliability.
- Improved type safety throughout the codebase (removed unnecessary type: ignore comments).
- Reorganized documentation: user docs moved to root `/docs` directory (standard Python convention), development docs in `.dev_docs/`. Documentation no longer ships with the package.

### Fixed
- Test pollution issue where PLAYWRIGHT_BROWSERS_PATH environment variable persisted across tests.
- FrozenInstanceError in E2E tests when modifying frozen dataclass fields.
- Generic type consistency in ScreenshotService with proper covariant type variables.
- Duplicate `from __future__ import annotations` import in storage.py.
- Incorrect return type annotation in `_default_json_serializer` (now uses `Any`).
- Test code duplication by extracting shared `create_capture_result` helper to `test_utils.py`.

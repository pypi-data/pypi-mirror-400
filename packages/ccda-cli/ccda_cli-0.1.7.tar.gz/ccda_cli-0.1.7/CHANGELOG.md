# Changelog

## [0.1.7] - 2026-01-05

### Fixed

- **Critical**: Fixed company affiliation enrichment silently failing
  - Company enrichment was not working due to async/await execution context issue
  - `_enrich_contributors()` was calling async code from within an executor thread
  - Added proper event loop detection and thread-safe async execution
  - Now correctly handles both standalone and executor-based execution contexts
  - Company data now properly populates in metrics output

## [0.1.6] - 2026-01-05

### Added

- **Company affiliation enrichment** via GitHub API (optional, requires GitHub token)
  - Automatically enriches contributor data with company information from GitHub user profiles
  - Extracts GitHub usernames from commit emails (e.g., `username@users.noreply.github.com`)
  - Fetches user profiles from GitHub API in batch to minimize API calls
  - Caches user profiles for 30 days to avoid duplicate requests
  - Normalizes company names using configurable mappings (e.g., "@google" → "Google")
  - Respects GitHub API rate limits and degrades gracefully
  - Falls back to email domain detection when API unavailable or rate limited
  - Provides more accurate elephant factor and company distribution metrics
- New `CompanyEnricher` class in `ccda_cli.enrichment.company` module
- Configuration option `github.enrich_company_affiliation` (default: true when token provided)
- Comprehensive test suite for company enrichment (16 unit tests)
- Enhanced documentation in `docs/github-token-setup.md` with company enrichment examples

### Changed

- `GitMetricsAnalyzer` now accepts optional `github_token` parameter for enrichment
- Company detection now prioritizes GitHub API data over email domain mapping (when token available)
- Updated README.md to highlight company affiliation enrichment feature

## [0.1.5] - 2026-01-05

### Added

- **osslili as required dependency** for professional license detection
  - Replaced brittle pattern-matching with osslili's Python API
  - Accurate SPDX license identification with confidence scores
  - Copyright statement extraction
  - Support for all osslili detection methods (metadata, file analysis, keyword matching)

### Fixed

- **Critical**: Cargo package tarball scanning now works correctly
  - Fixed `.crate` file download from crates.io (was downloading as `download` with no extension)
  - Added `.crate` extension support to archive extraction
  - Enhanced download URL detection to handle redirects properly (checks Content-Disposition header and final redirect URL)
- License file detection now works for all ecosystems
  - Removed incomplete `LICENSE_PATTERNS` that missed common patterns like `LICENSE-MIT`, `LICENSE-APACHE`
  - Now uses osslili for comprehensive license file discovery
- Relative path display in scan results (shows `serde-1.0.228/LICENSE-MIT` instead of full temp paths)

### Changed

- **Breaking**: osslili is now a required dependency (previously optional)
- **Breaking**: purl2src is now a required dependency (previously optional)
- Removed optional dependency groups `scanner` and `all`
- Tarball scanner completely refactored to use osslili Python API
  - Deleted 200+ lines of brittle pattern-matching code
  - Removed fallback license detection methods
  - Scan method now always reports `osslili`
- Cleaned up unused code and imports from tarball scanner

### Removed

- Removed obsolete methods: `_check_tool`, `_resolve_command`, `_build_command`, `_run_external_tool`, `_run_osslili`, `_run_upmex`, `_apply_osslili_results`, `_apply_upmex_results`, `_analyze_license_file`
- Removed `LICENSE_PATTERNS` and `COPYRIGHT_PATTERNS` constants
- Removed support for external tool command-line integration (now uses Python APIs directly)

## [0.1.4] - 2026-01-04

### Added

- **purl2src integration** for automatic download URL discovery
  - Integrated purl2src library as optional dependency
  - Tarball scanner now auto-discovers download URLs from PURLs
  - Fallback to PackageResolver if purl2src unavailable
  - New optional dependency group: `scanner` and `all`
- Crates.io (Rust Cargo) package discovery integration
  - Full metadata extraction from crates.io API
  - Registry data snapshot including downloads, keywords, and categories
  - Tarball URL resolution for package scanning
- Enhanced tarball scanner with external tool integration support
  - Support for osslili and upmex external scanning tools
  - Dynamic scan method tracking (builtin, osslili, upmex, or combined)
  - Improved license detection and binary file analysis

### Fixed

- Test suite compatibility with Python 3.14
- Virtual environment setup and package installation workflow

## [0.1.3] - 2026-01-04

### Added

- Dynamic API sampling based on GitHub token authentication status
  - Authenticated (5000 calls/hr): Fetches up to 5000 issues, 5000 PRs, 2000 closed issues
  - Unauthenticated (60 calls/hr): Conservative limits of 300 items per category
- Sampling metadata in JSON output for transparency
  - `_sampling` field in `IssueMetrics` showing sample size vs total count
  - `_sampling` field in `PullRequestMetrics` with coverage information
  - Coverage percentage indicator for quality assessment

### Fixed

- **Critical**: Metrics severely underreported due to hard-coded 300-item limit regardless of token
  - Issue sample size increased from 300 to 5000 when authenticated (16x improvement)
  - PR sample size increased from 300 to 5000 when authenticated (16x improvement)
  - Unlabeled rate now calculated from proper sample size
  - Unresponded rate now reflects larger sample for better accuracy
- Burnout score `issue_backlog` now uses adjusted full count instead of sampled count
- PR counts (open/merged/closed) now reflect comprehensive data instead of first 300 items

### Changed

- `IssueMetrics` dataclass now includes `sampled_open_count` and `sampled_closed_count` fields
- `PullRequestMetrics` dataclass now includes `sampled_count` field
- GitHub API collector now adapts page limits based on token availability

## [0.1.2] - 2026-01-04

### Fixed

- Use actual `open_issues_count` from GitHub repo API instead of sampled count (max 300)
- Subtract open PRs from issue count for accurate totals
- Fixes incorrect burnout score `issue_backlog` calculation

## [0.1.1] - 2026-01-04

### Added

- `chaoss_metrics` field to `HealthScoreResult` containing bus_factor, pony_factor, elephant_factor, and contributor_count
- `extended_metrics` field to `HealthScoreResult` containing commit_frequency, commits_per_day, pr_velocity, median_pr_merge_hours, branch_protected, and has_signed_releases
- Helper methods `_classify_frequency()` and `_classify_velocity()` for categorizing activity levels

### Fixed

- Dashboard template compatibility by exposing CHAOSS and extended metrics in health score output (#1)

## [0.1.0] - 2026-01-03

### Initial Release

First public release of ccda-cli - Supply Chain Security Metrics tool.

### Features

- Multi-ecosystem package analysis (npm, PyPI, Cargo, Maven, Go)
- Health score calculation (0-100) based on commit activity, contributor diversity, and community health
- Burnout score detection for maintainer sustainability risk assessment
- CHAOSS metrics computation (bus factor, pony factor, elephant factor)
- GitHub API integration for community health indicators (stars, forks, issues, PRs)
- Package tarball scanning for license compliance and binary detection
- Multiple discovery sources (deps.dev, ecosyste.ms, package registries, SerpAPI fallback)
- CLI commands: analyze, discover, cache management
- JSON output format for integration with other tools
- Comprehensive documentation and usage examples

### Documentation

- Complete README with installation and usage instructions
- Contribution guidelines (CONTRIBUTING.md)
- Code of Conduct (CODE_OF_CONDUCT.md)
- Authors and credits (AUTHORS.md)
- Detailed documentation for API integrations and configuration

### License

GNU Affero General Public License v3.0

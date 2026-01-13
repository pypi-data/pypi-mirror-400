# Changelog

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

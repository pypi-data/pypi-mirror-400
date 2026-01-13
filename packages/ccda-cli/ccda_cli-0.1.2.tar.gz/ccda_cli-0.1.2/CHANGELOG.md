# Changelog

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

# Command Reference

Complete reference for all ccda-cli commands.

---

## Table of Contents

- [analyze](#analyze) - Complete analysis pipeline
- [discover](#discover) - Package metadata discovery
- [git-metrics](#git-metrics) - Git repository analysis
- [github-metrics](#github-metrics) - GitHub API metrics
- [scan-tarball](#scan-tarball) - Tarball scanning
- [health-score](#health-score) - Calculate health score
- [burnout-score](#burnout-score) - Calculate burnout risk
- [cache](#cache) - Cache management
- [config-show](#config-show) - View configuration
- [config-init](#config-init) - Initialize configuration

---

## analyze

Run complete analysis pipeline for a package.

**Usage:**
```bash
ccda-cli analyze <PURL> [OPTIONS]
```

**Arguments:**
- `PURL` - Package URL (e.g., `pkg:npm/express`)

**Options:**
- `--output`, `-o` PATH - Save results to JSON file
- `--skip-clone` - Skip repository cloning
- `--skip-tarball` - Skip tarball scanning
- `--skip-github` - Skip GitHub API metrics
- `--force-refresh` - Ignore cached data
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Basic analysis
ccda-cli analyze pkg:npm/express

# Save to file
ccda-cli analyze pkg:npm/express --output analysis.json

# Skip cloning (use cached)
ccda-cli analyze pkg:npm/express --skip-clone

# Force fresh analysis
ccda-cli analyze pkg:npm/express --force-refresh

# Multiple ecosystems
ccda-cli analyze pkg:pypi/requests
ccda-cli analyze pkg:cargo/serde
ccda-cli analyze pkg:maven/org.opensearch/opensearch
ccda-cli analyze pkg:go/github.com/hashicorp/terraform
```

**Output:**
- Table summary with health/burnout scores
- Pipeline execution times
- Key metrics
- Optional JSON file with complete data

**Pipeline Steps:**
1. Discovery (metadata from multiple sources)
2. Clone repository (if GitHub URL found)
3. Git metrics analysis (CHAOSS metrics)
4. GitHub API metrics (stars, issues, PRs)
5. Tarball scan (licenses, binaries)
6. Health score calculation
7. Burnout score calculation

---

## discover

Discover package metadata from registries and APIs.

**Usage:**
```bash
ccda-cli discover <PURL> [OPTIONS]
```

**Arguments:**
- `PURL` - Package URL

**Options:**
- `--output`, `-o` PATH - Save discovery data to JSON file
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Discover npm package
ccda-cli discover pkg:npm/lodash

# Save discovery data
ccda-cli discover pkg:pypi/requests --output discovery.json

# Scoped npm package
ccda-cli discover pkg:npm/@babel/core
```

**Output:**
```json
{
  "purl": "pkg:npm/express",
  "name": "express",
  "version": null,
  "latest_version": "4.19.2",
  "description": "Fast, unopinionated, minimalist web framework",
  "license": "MIT",
  "repository_url": "https://github.com/expressjs/express",
  "tarball_url": "https://registry.npmjs.org/express/-/express-4.19.2.tgz",
  "homepage": "http://expressjs.com/",
  "sources": ["deps.dev", "ecosyste.ms", "npm"]
}
```

**Discovery Sources (in order):**
1. deps.dev API
2. ecosyste.ms API
3. ClearlyDefined API
4. Package registries (npm, PyPI, etc.)
5. SerpAPI fallback (if configured)

---

## git-metrics

Analyze git repository for CHAOSS metrics.

**Usage:**
```bash
ccda-cli git-metrics <PATH_OR_URL> [OPTIONS]
```

**Arguments:**
- `PATH_OR_URL` - Local repository path or GitHub URL

**Options:**
- `--output`, `-o` PATH - Save metrics to JSON file
- `--format` FORMAT - Output format: `table` (default), `json`
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Analyze local repository
ccda-cli git-metrics /path/to/repo

# Analyze from GitHub URL (will clone first)
ccda-cli git-metrics https://github.com/expressjs/express

# JSON output
ccda-cli git-metrics /path/to/repo --format json

# Save to file
ccda-cli git-metrics /path/to/repo --output metrics.json
```

**Metrics Calculated:**
- Bus factor - Minimum contributors for 50% of commits
- Pony factor - Minimum contributors for 50% of files
- Elephant factor - Largest contributing organization
- Contributor retention - Active contributors over time
- Company affiliation - Organization mapping via email domains
- License changes - Historical license modifications

**Table Output:**
```
Git Metrics Analysis
════════════════════

Summary Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bus Factor (90d):     3
Pony Factor (90d):    4
Elephant Factor:      Independent (45%)
Retention (90d):      67%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top 10 Contributors (90 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name              Commits    Files    Company
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
alice@example.com   145       87      Acme Corp
bob@company.com      98       45      Independent
...
```

---

## github-metrics

Fetch metrics from GitHub API.

**Usage:**
```bash
ccda-cli github-metrics <REPO_URL> [OPTIONS]
```

**Arguments:**
- `REPO_URL` - GitHub repository URL

**Options:**
- `--output`, `-o` PATH - Save metrics to JSON file
- `--github-token` TOKEN - GitHub API token (or use GITHUB_TOKEN env var)
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Fetch metrics
ccda-cli github-metrics https://github.com/expressjs/express

# With authentication
export GITHUB_TOKEN=ghp_your_token_here
ccda-cli github-metrics https://github.com/expressjs/express

# Save to file
ccda-cli github-metrics https://github.com/expressjs/express --output gh-metrics.json
```

**Metrics Collected:**
- Stars, forks, watchers
- Open issues, closed issues
- Open PRs, merged PRs
- Release count and latest release
- Default branch
- Branch protection status
- Topics/tags
- Creation and last updated dates

**Rate Limits:**
- Without token: 60 requests/hour
- With token: 5000 requests/hour

---

## scan-tarball

Scan package tarball for licenses and suspicious files.

**Usage:**
```bash
ccda-cli scan-tarball <PURL> [OPTIONS]
```

**Arguments:**
- `PURL` - Package URL

**Options:**
- `--output`, `-o` PATH - Save scan results to JSON file
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Scan tarball
ccda-cli scan-tarball pkg:npm/express

# Save results
ccda-cli scan-tarball pkg:pypi/requests --output scan.json
```

**Detects:**
- License files (LICENSE, COPYING, etc.)
- Binary files and executables
- Suspicious file patterns
- Package size and file count
- Top-level directory structure

---

## health-score

Calculate package health score.

**Usage:**
```bash
ccda-cli health-score <PURL> [OPTIONS]
```

**Arguments:**
- `PURL` - Package URL

**Options:**
- `--output`, `-o` PATH - Save score to JSON file
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Calculate health score
ccda-cli health-score pkg:npm/express

# Save to file
ccda-cli health-score pkg:pypi/requests --output health.json
```

**Scoring Components (100 points total):**
- Commit activity (15 pts)
- Bus factor (10 pts)
- Pony factor (10 pts)
- License stability (5 pts)
- Contributor retention (10 pts)
- Elephant factor (10 pts)
- Issue responsiveness (10 pts)
- PR velocity (10 pts)
- Branch protection (10 pts)
- Release frequency (10 pts)

**Output:**
```json
{
  "health_score": 67,
  "health_grade": "D",
  "components": {
    "commit_activity": 12,
    "bus_factor": 6,
    "pony_factor": 7,
    ...
  }
}
```

---

## burnout-score

Calculate maintainer burnout risk score.

**Usage:**
```bash
ccda-cli burnout-score <PURL> [OPTIONS]
```

**Arguments:**
- `PURL` - Package URL

**Options:**
- `--output`, `-o` PATH - Save score to JSON file
- `--verbose`, `-v` - Enable verbose output

**Examples:**
```bash
# Calculate burnout score
ccda-cli burnout-score pkg:cargo/serde

# Save to file
ccda-cli burnout-score pkg:pypi/requests --output burnout.json
```

**Scoring Components (100 points total):**
- Issue backlog pressure (20 pts)
- Response time gaps (20 pts)
- Triage overhead (20 pts)
- Workload concentration (20 pts)
- Activity decline (20 pts)

**Risk Levels:**
- 0-30: Low risk
- 31-40: Medium risk
- 41-60: High risk
- 61-100: Critical risk

---

## cache

Manage cached data (repositories, analysis results, user profiles).

**Subcommands:**
- `cache info` - Show cache statistics
- `cache clear` - Clear cached data

### cache info

Show cache statistics and disk usage.

**Usage:**
```bash
ccda-cli cache info
```

**Output:**
```
Cache Information
═══════════════════════════════════

Cache Directory: /Users/user/.ccda

Repositories: 15 (1.2 GB)
Analysis Data: 42 packages (3.5 MB)
User Profiles: 128 users (256 KB)

Total Size: 1.21 GB
```

### cache clear

Clear cached data.

**Usage:**
```bash
ccda-cli cache clear [OPTIONS]
```

**Options:**
- `--all` - Clear all cached data
- `--repos` - Clear only cloned repositories
- `--data` - Clear only analysis data
- `--users` - Clear only user profiles
- `--package` PURL - Clear data for specific package
- `--dry-run` - Show what would be deleted without deleting

**Examples:**
```bash
# Clear all cache
ccda-cli cache clear --all

# Clear only repositories
ccda-cli cache clear --repos

# Clear specific package
ccda-cli cache clear --package pkg:npm/express

# Dry run (show without deleting)
ccda-cli cache clear --all --dry-run
```

---

## config-show

Display current configuration.

**Usage:**
```bash
ccda-cli config-show
```

**Output:**
```yaml
github_token: ghp_****...
serpapi_key: null
cache:
  directory: /Users/user/.ccda
  repos_dir: /Users/user/.ccda/repos
  data_dir: /Users/user/.ccda/data
  users_dir: /Users/user/.ccda/users
ttl:
  discovery: null
  git_metrics: 24
  github_api: 6
  health_score: 6
  burnout_score: 6
git:
  clone_depth: 1000
  timeout_seconds: 300
  max_concurrent_clones: 3
```

---

## config-init

Initialize default configuration file.

**Usage:**
```bash
ccda-cli config-init [OPTIONS]
```

**Options:**
- `--force` - Overwrite existing configuration

**Examples:**
```bash
# Create default config
ccda-cli config-init

# Overwrite existing
ccda-cli config-init --force
```

**Creates:** `~/.ccda/config.yaml` with default settings

---

## Global Options

These options work with all commands:

- `--help`, `-h` - Show help message
- `--version` - Show version number
- `--verbose`, `-v` - Enable verbose output
- `--config` PATH - Use custom config file
- `--github-token` TOKEN - GitHub API token

**Examples:**
```bash
# Show help for any command
ccda-cli analyze --help

# Use custom config
ccda-cli --config /path/to/config.yaml analyze pkg:npm/express

# Verbose output
ccda-cli -v analyze pkg:npm/express
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Package not found
- `4` - Network error
- `5` - Cache error

---

## Environment Variables

- `GITHUB_TOKEN` - GitHub API token
- `CCDA_GITHUB_TOKEN` - CCDA-specific GitHub token (overrides GITHUB_TOKEN)
- `SERPAPI_KEY` - SerpAPI key for fallback search
- `CCDA_SERPAPI_KEY` - CCDA-specific SerpAPI key
- `CCDA_CACHE_DIR` - Cache directory path

---

## See Also

- [Getting Started](getting-started.md) - Installation and first steps
- [Configuration Guide](configuration.md) - Detailed configuration options
- [API Integrations](api-integrations.md) - Understanding data sources

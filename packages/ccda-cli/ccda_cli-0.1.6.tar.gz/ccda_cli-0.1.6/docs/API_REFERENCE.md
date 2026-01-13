# API Reference

This document provides a complete reference for using ccda-cli as a Python library.

## GitMetricsAnalyzer

Analyzes git repositories for community health metrics.

### Constructor

```python
GitMetricsAnalyzer(repo_path: Path)
```

**Parameters:**
- `repo_path` (Path): Path to local git repository

**Example:**
```python
from pathlib import Path
from ccda_cli.metrics.git import GitMetricsAnalyzer

analyzer = GitMetricsAnalyzer(Path("/path/to/repo"))
```

### Methods

#### `analyze(repo_url: str | None = None) -> GitMetricsResult`

Run full git metrics analysis across all configured time windows.

**Parameters:**
- `repo_url` (str, optional): Repository URL for metadata (doesn't affect analysis)

**Returns:**
- `GitMetricsResult`: Complete analysis results

**Example:**
```python
result = analyzer.analyze()
```

## GitMetricsResult

Complete git metrics analysis result with multiple time windows.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `repo_url` | str | Repository URL |
| `clone_path` | str | Local path to cloned repository |
| `analyzed_at` | datetime | Timestamp of analysis |
| `method` | str | Analysis method (default: "git_offline") |
| `ttl_hours` | int | Cache TTL in hours (default: 24) |
| `time_windows` | dict[str, TimeWindowMetrics] | Metrics for each time window |
| `license_changes` | LicenseHistory | License change tracking |

### Methods

#### `to_dict() -> dict[str, Any]`

Convert to dictionary for JSON serialization.

#### `from_dict(data: dict[str, Any]) -> GitMetricsResult`

Create from dictionary (class method).

### Example

```python
result = analyzer.analyze()

# Access different time windows
metrics_30d = result.time_windows["30d"]
metrics_90d = result.time_windows["90d"]
metrics_all = result.time_windows["all"]

# Check license
current_license = result.license_changes.current_license
```

## TimeWindowMetrics

Metrics for a specific time window.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start_date` | datetime | Window start date |
| `end_date` | datetime | Window end date |
| `total_commits` | int | Total commits in window |
| `total_contributors` | int | Unique contributors |
| `companies` | int | Number of companies contributing |
| `bus_factor` | int | Minimum developers to lose 50%+ commits |
| `pony_factor` | int | Developers contributing 50% of commits (CHAOSS) |
| `elephant_factor` | int | Companies contributing 50% of commits |
| `commits_per_day` | float | Average commits per day |
| `commit_frequency` | str | Activity level: "very_high", "high", "medium", "low", "very_low" |
| `top_contributors` | list[ContributorStats] | Top 10 contributors by commits |
| `top_companies` | list[CompanyStats] | Top 10 companies by commits |
| `contributor_retention` | float \| None | Retention rate (0-100%) compared to previous window |

### Methods

#### `to_dict() -> dict[str, Any]`

Convert to dictionary.

#### `from_dict(data: dict[str, Any]) -> TimeWindowMetrics`

Create from dictionary (class method).

### Example

```python
metrics = result.time_windows["90d"]

print(f"Period: {metrics.start_date} to {metrics.end_date}")
print(f"Commits: {metrics.total_commits}")
print(f"Contributors: {metrics.total_contributors}")
print(f"Bus factor: {metrics.bus_factor}")
print(f"Activity: {metrics.commit_frequency}")

# Top contributors
for contrib in metrics.top_contributors[:5]:
    print(f"  {contrib.name}: {contrib.commits} commits ({contrib.percentage}%)")
```

## LicenseHistory

License change tracking.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_license` | str \| None | Current detected license |
| `changes` | list[LicenseChange] | Historical license changes |

### Methods

#### `to_dict() -> dict[str, Any]`

Convert to dictionary.

#### `from_dict(data: dict[str, Any]) -> LicenseHistory`

Create from dictionary (class method).

### Example

```python
license_history = result.license_changes

print(f"Current: {license_history.current_license}")
print(f"Changes: {len(license_history.changes)}")

for change in license_history.changes:
    print(f"{change.date}: {change.old_license} → {change.new_license}")
```

## LicenseChange

Record of a license change event.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `commit_hash` | str | Git commit hash |
| `date` | datetime | Change date |
| `old_license` | str \| None | Previous license |
| `new_license` | str | New license |
| `author` | str | Commit author |

## ContributorStats

Statistics for a single contributor.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `email` | str | Contributor email |
| `name` | str | Contributor name |
| `commits` | int | Number of commits |
| `percentage` | float | Percentage of total commits |
| `company` | str | Affiliated company (default: "Independent") |
| `first_commit` | datetime \| None | First commit date |
| `last_commit` | datetime \| None | Last commit date |

## CompanyStats

Statistics for a company/organization.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `company` | str | Company name |
| `commits` | int | Total commits from company |
| `percentage` | float | Percentage of total commits |
| `contributors` | int | Number of contributors from company |

## Configuration

### TimeWindow

Configure analysis time windows.

```python
from ccda_cli.config import Config, TimeWindow

config = Config()
config.analysis.time_windows = [
    TimeWindow(name="7d", days=7),
    TimeWindow(name="30d", days=30),
    TimeWindow(name="90d", days=90),
    TimeWindow(name="365d", days=365),
    TimeWindow(name="all", days=None),  # All time
]
```

### Default Time Windows

By default, ccda-cli analyzes these windows:
- `30d`: Last 30 days
- `90d`: Last 90 days
- `365d`: Last 365 days
- `all`: All time (entire repository history)

## Complete Usage Example

```python
from pathlib import Path
from ccda_cli.metrics.git import GitMetricsAnalyzer

# Initialize analyzer
repo_path = Path("/path/to/repo")
analyzer = GitMetricsAnalyzer(repo_path)

# Run analysis
result = analyzer.analyze(repo_url="https://github.com/owner/repo")

# Access 90-day metrics
metrics_90d = result.time_windows["90d"]
print(f"Last 90 days:")
print(f"  Commits: {metrics_90d.total_commits}")
print(f"  Contributors: {metrics_90d.total_contributors}")
print(f"  Bus factor: {metrics_90d.bus_factor}")
print(f"  Pony factor: {metrics_90d.pony_factor}")
print(f"  Frequency: {metrics_90d.commit_frequency}")

# Check license
license_info = result.license_changes
print(f"\nLicense: {license_info.current_license}")
if license_info.changes:
    print(f"License has changed {len(license_info.changes)} times")

# Top contributors
print("\nTop 5 Contributors:")
for contrib in metrics_90d.top_contributors[:5]:
    print(f"  {contrib.name} ({contrib.company}): {contrib.commits} commits")

# Compare time windows
metrics_30d = result.time_windows["30d"]
metrics_365d = result.time_windows["365d"]

print(f"\nActivity comparison:")
print(f"  30 days: {metrics_30d.commits_per_day:.2f} commits/day")
print(f"  365 days: {metrics_365d.commits_per_day:.2f} commits/day")

# Serialize to JSON
import json
with open("metrics.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2, default=str)
```

## Error Handling

```python
from ccda_cli.metrics.git import GitMetricsAnalyzer
from pathlib import Path

repo_path = Path("/path/to/repo")

try:
    analyzer = GitMetricsAnalyzer(repo_path)
    result = analyzer.analyze()
except FileNotFoundError:
    print(f"Repository not found: {repo_path}")
except subprocess.TimeoutExpired:
    print("Git command timed out")
except Exception as e:
    print(f"Analysis failed: {e}")
```

## See Also

- [Migration Guide](./API_MIGRATION_GUIDE.md) - Upgrading from older versions
- [Getting Started](./getting-started.md) - CLI usage
- [Commands](./commands.md) - CLI reference

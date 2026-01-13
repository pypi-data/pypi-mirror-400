# API Migration Guide

This guide helps you migrate your code when using ccda-cli as a library.

## GitMetricsAnalyzer API Changes

### Breaking Changes in v0.1.0+

#### 1. `analyze()` Method Signature

**Before (Deprecated):**
```python
analyzer = GitMetricsAnalyzer(repo_path)
result = analyzer.analyze(lookback_days=90)  # ❌ No longer accepts lookback_days
```

**After (Current):**
```python
analyzer = GitMetricsAnalyzer(repo_path)
result = analyzer.analyze()  # ✅ No parameters needed
```

**Rationale:** Time windows are now configured via the `Config` object, allowing multiple time periods to be analyzed simultaneously.

#### 2. Accessing Metrics by Time Window

**Before (Deprecated):**
```python
result = analyzer.analyze()
metrics = result.window_90d  # ❌ No longer exists
print(f"Commits: {metrics.total_commits}")
```

**After (Current):**
```python
result = analyzer.analyze()
# Access metrics via time_windows dictionary
metrics = result.time_windows["90d"]  # ✅ Use window name as key
print(f"Commits: {metrics.total_commits}")

# Available windows (default):
# - "30d": Last 30 days
# - "90d": Last 90 days
# - "365d": Last 365 days
# - "all": All time
```

**Rationale:** Multiple time windows can now be analyzed in a single call, reducing computation time and providing more comprehensive insights.

#### 3. License Information

**Before (Deprecated):**
```python
result = analyzer.analyze()
current_license = result.license  # ❌ No longer exists
```

**After (Current):**
```python
result = analyzer.analyze()
# Access license history
license_history = result.license_changes  # ✅ LicenseHistory object
current_license = license_history.current_license
previous_changes = license_history.changes  # List of LicenseChange objects

# Check for license changes
if license_history.changes:
    print(f"License has changed {len(license_history.changes)} times")
    for change in license_history.changes:
        print(f"{change.date}: {change.old_license} → {change.new_license}")
```

**Rationale:** Tracking license changes over time provides important supply chain security insights.

## Complete Migration Example

### Old Code (v0.0.x)

```python
from ccda_cli.metrics.git import GitMetricsAnalyzer
from pathlib import Path

analyzer = GitMetricsAnalyzer(Path("/path/to/repo"))
result = analyzer.analyze(lookback_days=90)

# Access metrics
print(f"Commits: {result.window_90d.total_commits}")
print(f"Contributors: {result.window_90d.total_contributors}")
print(f"Bus factor: {result.window_90d.bus_factor}")
print(f"License: {result.license}")
```

### New Code (v0.1.0+)

```python
from ccda_cli.metrics.git import GitMetricsAnalyzer
from pathlib import Path

analyzer = GitMetricsAnalyzer(Path("/path/to/repo"))
result = analyzer.analyze()  # No lookback_days parameter

# Access metrics via time_windows
metrics_90d = result.time_windows["90d"]
print(f"Commits: {metrics_90d.total_commits}")
print(f"Contributors: {metrics_90d.total_contributors}")
print(f"Bus factor: {metrics_90d.bus_factor}")

# Access license information
print(f"Current license: {result.license_changes.current_license}")
if result.license_changes.changes:
    print(f"License changes: {len(result.license_changes.changes)}")
```

## TimeWindowMetrics Structure

```python
@dataclass
class TimeWindowMetrics:
    start_date: datetime
    end_date: datetime
    total_commits: int
    total_contributors: int
    companies: int

    # CHAOSS metrics
    bus_factor: int
    pony_factor: int
    elephant_factor: int

    # Activity metrics
    commits_per_day: float
    commit_frequency: str  # "very_high", "high", "medium", "low", "very_low"

    # Contributors and companies
    top_contributors: list[ContributorStats]
    top_companies: list[CompanyStats]

    # Retention
    contributor_retention: float | None  # Percentage (0-100)
```

## LicenseHistory Structure

```python
@dataclass
class LicenseHistory:
    current_license: str | None
    changes: list[LicenseChange]

@dataclass
class LicenseChange:
    commit_hash: str
    date: datetime
    old_license: str | None
    new_license: str
    author: str
```

## Configuring Time Windows

To customize time windows, modify your config:

```python
from ccda_cli.config import Config, TimeWindow

config = Config()
config.analysis.time_windows = [
    TimeWindow(name="14d", days=14),
    TimeWindow(name="30d", days=30),
    TimeWindow(name="90d", days=90),
    TimeWindow(name="all", days=None),  # All time
]

# Use custom config
analyzer = GitMetricsAnalyzer(repo_path)
result = analyzer.analyze()

# Access custom windows
metrics_14d = result.time_windows["14d"]
```

## Common Migration Issues

### Issue 1: AttributeError: 'GitMetricsResult' object has no attribute 'window_90d'

**Solution:** Use `result.time_windows["90d"]` instead.

### Issue 2: TypeError: analyze() got an unexpected keyword argument 'lookback_days'

**Solution:** Remove the `lookback_days` parameter. Configure time windows via Config instead.

### Issue 3: AttributeError: 'GitMetricsResult' object has no attribute 'license'

**Solution:** Use `result.license_changes.current_license` instead.

## Need Help?

If you encounter migration issues not covered here:

1. Check the [API Reference](./API_REFERENCE.md)
2. See [examples](../examples/) for complete usage patterns
3. Open an issue: https://github.com/SemClone/ccda-cli/issues

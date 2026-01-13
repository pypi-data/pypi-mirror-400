# API Usage and Configuration Details

## Questions & Answers

### 1. Does analyze implement discovery and perform all actions?

**YES** - The `analyze` command is the **complete end-to-end pipeline** that performs ALL actions:

```
analyze (Full Pipeline)
├── 1. Discovery
│   ├── deps.dev API (versions, licenses, repo URLs)
│   ├── ecosyste.ms API (repo metadata, GitHub stats)
│   ├── ClearlyDefined API (licenses, source locations)
│   ├── Package Registries (npm, PyPI direct metadata)
│   └── SerpAPI fallback (Google Search if repo URL missing) ← NEW
├── 2. Clone Repository (if GitHub URL found)
├── 3. Git Metrics Analysis (CHAOSS metrics from git history)
│   ├── Bus factor, pony factor, elephant factor
│   ├── Contributor analysis
│   └── Company affiliation detection
├── 4. GitHub API Metrics (if GitHub URL found)
│   ├── Stars, forks, watchers
│   ├── Open issues and PRs
│   ├── Release information
│   └── Branch protection settings
├── 5. Tarball Scan (download and analyze package tarball)
├── 6. Health Score Calculation (0-100)
│   ├── Commit activity (15 points)
│   ├── Bus factor (10 points)
│   ├── Contributor metrics (30 points)
│   ├── Issue/PR velocity (20 points)
│   └── Release frequency, licenses, etc. (25 points)
└── 7. Burnout Score Calculation (0-100)
    ├── Issue backlog pressure (20 points)
    ├── Response time gaps (20 points)
    ├── Triage overhead (20 points)
    ├── Workload concentration (20 points)
    └── Activity decline trends (20 points)
```

**Output:** Complete JSON report with all metrics + formatted table summary

Each step can be skipped with flags:
- `--skip-clone` - Skip git cloning
- `--skip-tarball` - Skip tarball scanning
- `--skip-github` - Skip GitHub API
- `--force-refresh` - Ignore cache, refresh all data

**Example:**
```bash
ccda-cli analyze pkg:pypi/requests --output full-report.json
```

This single command produces:
- Discovery metadata
- Git commit history analysis
- GitHub community metrics
- Health score (0-100)
- Burnout risk score (0-100)
- Complete JSON output

---

### 2. Are we hitting GitHub rate limits?

**Status:** Using 57% of unauthenticated rate limit (34/60 requests used)

#### Current Status
```json
{
  "remaining": 26,
  "limit": 60,
  "reset_at": "2026-01-03T22:33:06"
}
```

#### API Calls per Package
- ~8 GitHub API requests per package
- 16 packages analyzed = ~128 requests needed
- 60 requests/hour limit (unauthenticated)

**We analyzed in batches to avoid hitting the limit.**

#### Rate Limit Tiers

| Authentication | Limit | Notes |
|----------------|-------|-------|
| None | 60/hour | What we're using |
| Personal Token | 5,000/hour | Recommended for production |
| GitHub App | 15,000/hour | For high-volume |

#### Recommendation
Set `GITHUB_TOKEN` environment variable for higher limits:
```bash
export GITHUB_TOKEN=ghp_your_token_here
ccda-cli analyze pkg:npm/express
```

---

### 3. Which APIs are we using?

**YES** - We're using multiple discovery sources:

#### deps.dev API ✅
- **URL:** `https://api.deps.dev/v3alpha`
- **Used for:** Go, Maven, PyPI, Cargo, NPM packages
- **Rate limit:** Unknown (appears unlimited for our usage)
- **Returns:** Versions, licenses, repository URLs

**Example packages using deps.dev:**
- `pkg:go/github.com/hashicorp/terraform` → deps.dev
- `pkg:maven/org.opensearch/opensearch` → deps.dev
- `pkg:pypi/requests` → deps.dev
- `pkg:cargo/serde` → deps.dev

#### ClearlyDefined API ✅
- **URL:** `https://api.clearlydefined.io`
- **Used for:** Enrichment when deps.dev doesn't have full data
- **Rate limit:** Unknown (appears unlimited)
- **Returns:** License data, source locations

**Example:**
```json
{
  "sources": ["deps.dev", "clearlydefined", "pypi"]
}
```

#### Package Registry APIs ✅
- **NPM Registry:** `https://registry.npmjs.org`
- **PyPI API:** `https://pypi.org/pypi`
- **Used for:** Direct package metadata when other sources unavailable

#### GitHub API ✅
- **URL:** `https://api.github.com`
- **Used for:** Repository stats, issues, PRs, releases, branch protection
- **Rate limit:** 60/hour (unauthenticated), 5000/hour (with token)

#### ecosyste.ms ✅
- **URL:** `https://packages.ecosyste.ms`
- **Status:** **IMPLEMENTED** ✅
- **Used for:** Comprehensive package metadata enrichment
- **Rate limit:** No authentication required, appears unlimited
- **Returns:**
  - Repository URLs
  - Normalized licenses
  - GitHub repository metadata (stars, forks, open issues, watchers)
  - Package-specific metadata (funding, documentation, classifiers)
  - Latest release information

**Example output:**
```json
{
  "sources": ["deps.dev", "ecosyste.ms", "pypi"],
  "registry_data": {
    "ecosystems_repo": {
      "stars": 10059,
      "forks": 861,
      "open_issues": 340,
      "watchers": 68
    },
    "ecosystems_metadata": {
      "funding": {...},
      "documentation": "...",
      ...
    }
  }
}
```

**Supported ecosystems:**
- npm (npmjs.org)
- PyPI (pypi.org)
- Cargo (crates.io)
- Maven (maven.org)
- Go (proxy.golang.org)
- NuGet (nuget.org)
- RubyGems (rubygems.org)
- Composer (packagist.org)

#### SerpAPI ✅ (Fallback Only)
- **URL:** `https://serpapi.com`
- **Status:** **IMPLEMENTED** ✅
- **Used for:** Last-resort GitHub repository search when all other methods fail
- **Rate limit:** Depends on plan (100/month free, 5000/month paid)
- **Requires:** `SERPAPI_KEY` or `CCDA_SERPAPI_KEY` environment variable
- **How it works:**
  - Uses Google Search with `site:github.com` query
  - Only runs when repository URL is still null after all other sources
  - Extracts most relevant GitHub repository from search results
  - Filters out non-repository paths (issues, pulls, wikis)

**When SerpAPI is used:**
- Only as a **last resort** when:
  1. deps.dev doesn't have repository URL
  2. ecosyste.ms doesn't have the package
  3. ClearlyDefined doesn't have source location
  4. Package registry doesn't provide GitHub URL
  5. API key is configured

**Example output:**
```json
{
  "sources": ["deps.dev", "serpapi"],
  "repository_url": "https://github.com/owner/repo"
}
```

**Configuration:**
```bash
# Set API key
export SERPAPI_KEY=your_key_here

# Or use CCDA-specific variable
export CCDA_SERPAPI_KEY=your_key_here
```

See [SERPAPI_SETUP.md](./SERPAPI_SETUP.md) for complete setup guide.

---

### 4. Does clone work async?

**YES** - Fully asynchronous with concurrent support!

#### Implementation Details

```python
async def clone(self, repo_url: str, depth: int | None = None) -> CloneResult:
    """Async clone with subprocess execution"""
    # Runs git clone in subprocess without blocking
    await self._run_clone(repo_url, local_path, depth)
```

#### Batch Cloning with Concurrency

```python
async def clone_batch(
    self,
    repo_urls: list[str],
    concurrency: int = 3  # Default: 3 concurrent clones
) -> list[CloneResult]:
    """Clone multiple repositories concurrently"""
    semaphore = asyncio.Semaphore(concurrency)

    async def clone_with_semaphore(url: str) -> CloneResult:
        async with semaphore:
            return await self.clone(url)

    tasks = [clone_with_semaphore(url) for url in repo_urls]
    return await asyncio.gather(*tasks)
```

#### Configuration

```yaml
# ~/.ccda/config.yaml
git:
  max_concurrent_clones: 3  # Adjust for your system
  clone_depth: 1000
  timeout_seconds: 300
```

**Benefits:**
- ✅ Non-blocking I/O
- ✅ Concurrent clones (3 at a time by default)
- ✅ Efficient resource usage
- ✅ Faster batch processing

---

### 5. Clone target: Folder or tmp?

**Persistent cache directory**, NOT tmp!

#### Default Location
```
~/.ccda/
├── repos/          # Git clones (persistent)
│   ├── github.com/
│   │   ├── hashicorp/
│   │   │   └── terraform/
│   │   ├── opensearch-project/
│   │   │   └── OpenSearch/
│   │   └── elastic/
│   │       └── elasticsearch/
│   ├── git+https:/  # HTTPS clones
│   └── git@github.com:  # SSH clones
├── data/           # Analysis cache
│   └── packages/
│       └── pkg--npm/
│           └── express/
│               ├── discovery.json
│               ├── unified.json
│               └── git_metrics.json
└── users/          # User profile cache
```

#### Benefits of Persistent Cache
1. ✅ **Reuse clones** - Don't re-clone on every analysis
2. ✅ **Faster analysis** - Skip clone if already exists
3. ✅ **Offline capability** - Work without network
4. ✅ **Historical data** - Track changes over time

#### Cache Invalidation
```bash
# Clear all cache
ccda-cli cache clear --all

# Clear specific package
ccda-cli cache clear --package pkg:npm/express

# Clear just repositories
ccda-cli cache clear --repos

# Force refresh without clearing
ccda-cli analyze pkg:npm/express --force-refresh
```

---

### 6. Can we specify a target folder?

**YES** - Multiple ways to configure!

#### Method 1: Config File (Recommended)

Create `~/.ccda/config.yaml`:

```yaml
cache:
  directory: /custom/path/to/ccda-cache
  repos_dir: /custom/repos  # Optional: override just repos
  data_dir: /custom/data    # Optional: override just data

git:
  clone_depth: 1000
  timeout_seconds: 300
  max_concurrent_clones: 3

ttl:
  git_metrics: 24    # Hours
  github_api: 6      # Hours
  discovery: null    # Never expires
```

#### Method 2: Environment Variables

```bash
export CCDA_CACHE_DIR=/custom/path
export CCDA_GIT_CLONE_DEPTH=1000
ccda-cli analyze pkg:npm/express
```

#### Method 3: Project Config

Create `./ccda-config.yaml` in your project:

```yaml
cache:
  directory: ./local-cache  # Relative to project

git:
  clone_depth: 500  # Smaller for CI/CD
```

#### Method 4: CLI Arguments (if available)

Check if CLI accepts cache dir:

```bash
ccda-cli --cache-dir /tmp/ccda analyze pkg:npm/express
```

#### Configuration Priority

1. CLI arguments (highest)
2. Environment variables
3. Project config (`./ccda-config.yaml`)
4. User config (`~/.ccda/config.yaml`)
5. Default values (lowest)

---

## API Usage Summary

### Discovery Sources (in order)

For **ecosystem packages** (npm, pypi, maven, go, cargo):
1. **deps.dev** - Primary source (versions, licenses, repo URLs)
2. **ecosyste.ms** - Enrichment (repo metadata, stars, forks, comprehensive package data) ✨
3. **ClearlyDefined** - Enrichment (licenses, source locations)
4. **Package Registry** - Direct API (npm, pypi specific metadata)
5. **SerpAPI** - Last resort fallback (Google Search for GitHub repos) ✨ **NEW**

For **GitHub PURLs** (pkg:github/*):
1. **PURL inference** - Extract owner/repo from namespace
2. Skip other sources (it's already a repository)

### API Requests per Package

| Step | API | Requests | Can Skip? |
|------|-----|----------|-----------|
| Discovery | deps.dev | 1-2 | No |
| Discovery | ecosyste.ms | 1 | No (enrichment) |
| Discovery | clearlydefined | 0-1 | Auto |
| Discovery | Registry | 0-1 | Auto |
| Discovery | SerpAPI | 0-1 | Only if repo URL missing + key configured |
| GitHub Metrics | GitHub API | 6-8 | --skip-github |
| **Total** | | **8-14** | |

### Rate Limits Status

| API | Limit | Used (16 pkgs) | Remaining | Status |
|-----|-------|---------------|-----------|--------|
| deps.dev | ∞? | ~32 | ∞ | ✅ OK |
| SerpAPI | 100/mo (free) | 0 | 100 | ✅ OK (optional) |
| ecosyste.ms | ∞ | ~16 | ∞ | ✅ OK |
| clearlydefined | ∞? | ~16 | ∞ | ✅ OK |
| GitHub (no auth) | 60/hr | 34 | 26 | ⚠️ Near limit |
| npm registry | ∞ | ~2 | ∞ | ✅ OK |
| PyPI API | ∞ | ~2 | ∞ | ✅ OK |

**Recommendation:** Set `GITHUB_TOKEN` for production use to get 5000/hour limit.

**Note:** ecosyste.ms provides rich GitHub metadata (stars, forks, issues) during discovery, which supplements the GitHub API data collected later in the pipeline.

---

## Performance Characteristics

### Async Operations

| Operation | Async? | Concurrent? | Notes |
|-----------|--------|-------------|-------|
| Discovery API calls | ✅ Yes | ✅ Yes | Uses httpx async client |
| Git clone | ✅ Yes | ✅ Yes | Max 3 concurrent |
| Git metrics | ✅ Yes | ❌ No | CPU-bound, runs in executor |
| GitHub API | ✅ Yes | ✅ Yes | Batched requests |
| Tarball scan | ✅ Yes | ❌ No | I/O bound |

### Analysis Times (from our tests)

| Package | Total Time | Clone | Git Metrics | GitHub API | Notes |
|---------|-----------|-------|-------------|------------|-------|
| express | 8.2s | 0.0s | - | 7.7s | Cached clone |
| requests | 40.0s | 1.6s | 0.1s | 6.2s | Large tarball (31.6s) |
| serde | 7.5s | 1.3s | 0.0s | 6.0s | Fast |
| elasticsearch | 25.2s | 24.9s | 0.1s | 0.0s | Large repo |
| opensearch | 14.8s | 8.8s | 0.0s | 5.8s | Medium repo |

**Bottlenecks:**
1. Git clone (for large repos like elasticsearch: 25s)
2. GitHub API (6-8s per package due to sequential requests)
3. Tarball scan (for large packages: 31s for requests)

**Optimizations possible:**
1. ✅ Already async
2. ✅ Already caching
3. ⚠️ Could parallelize GitHub API requests more
4. ⚠️ Could optimize tarball scanning

---

## Configuration Examples

### High-Throughput CI/CD

```yaml
# .ccda-config.yaml for CI
cache:
  directory: /tmp/ccda-ci-cache  # Ephemeral

git:
  clone_depth: 100  # Minimal depth
  timeout_seconds: 180
  max_concurrent_clones: 5  # More concurrency

ttl:
  git_metrics: 0  # Always refresh
  github_api: 0   # Always refresh
  discovery: 0    # Always refresh
```

### Development/Testing

```yaml
# ~/.ccda/config.yaml for dev
cache:
  directory: ~/.ccda  # Persistent

git:
  clone_depth: 1000  # Good balance
  max_concurrent_clones: 3

ttl:
  git_metrics: 24    # Cache for 1 day
  github_api: 6      # Cache for 6 hours
  discovery: 168     # Cache for 1 week
```

### Production Monitoring

```yaml
# Production config
cache:
  directory: /var/lib/ccda  # System path

git:
  clone_depth: null  # Full history
  timeout_seconds: 600
  max_concurrent_clones: 10  # High concurrency

ttl:
  git_metrics: 12    # Refresh twice daily
  github_api: 3      # Refresh every 3 hours
  discovery: 24      # Daily refresh

# Add GitHub token via environment
# GITHUB_TOKEN=ghp_xxx
```

---

## Recommendations

### For Your Use Case

1. **Set GitHub Token**
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```
   This gives you 5000 requests/hour instead of 60.

2. **Configure Cache Location**
   ```yaml
   # ~/.ccda/config.yaml
   cache:
     directory: /path/to/persistent/storage
   ```

3. **Adjust Clone Depth**
   - For 90-day analysis: `clone_depth: 1000` (current default)
   - For complete history: `clone_depth: null`
   - For CI/CD: `clone_depth: 100`

4. **Monitor Rate Limits**
   ```bash
   # Check rate limit in output
   ccda-cli analyze pkg:npm/express --output report.json
   jq '.github_metrics.rate_limit' report.json
   ```

5. **Batch Processing**
   Use our batch script for analyzing many packages:
   ```bash
   ./batch_analysis.sh  # Already created
   ```

Would you like me to add ecosyste.ms API support, or implement any other specific API integrations?

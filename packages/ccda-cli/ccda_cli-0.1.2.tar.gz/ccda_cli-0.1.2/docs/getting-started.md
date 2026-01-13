# Getting Started with ccda-cli

This guide will help you install and start using ccda-cli for supply chain security analysis.

---

## Prerequisites

- **Python 3.9 or higher**
- **Git** (for repository cloning)
- **pip** (Python package manager)

Check your Python version:

```bash
python --version  # or python3 --version
```

---

## Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/SemClone/ccda-cli.git
cd ccda-cli

# Install in development mode
pip install -e .

# Verify installation
ccda-cli --version
```

### Option 2: Install with Development Dependencies

If you plan to contribute or run tests:

```bash
pip install -e ".[dev]"
```

This installs additional tools:
- pytest (testing)
- black (code formatting)
- ruff (linting)
- mypy (type checking)

---

## Your First Analysis

### 1. Analyze a Package

Let's analyze the popular Express.js package:

```bash
ccda-cli analyze pkg:npm/express
```

**What happens:**
1.  Discovers package metadata from npm registry
2.  Clones GitHub repository
3.  Analyzes git commit history
4.  Fetches GitHub API metrics
5.  Scans package tarball
6.  Calculates health score (0-100)
7.  Calculates burnout risk (0-100)

**Output:**
```
Full analysis: pkg:npm/express

Analysis Summary
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Step           ┃ Status    ┃ Duration ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ discovery      │ completed │ 0.2s     │
│ clone          │ completed │ 2.1s     │
│ git_metrics    │ completed │ 0.1s     │
│ github_metrics │ completed │ 7.2s     │
│ tarball_scan   │ completed │ 0.8s     │
│ health_score   │ completed │ 0.0s     │
│ burnout_score  │ completed │ 0.0s     │
└────────────────┴───────────┴──────────┘

Health Score: 67/100 (D)
Burnout Risk: 15/100 (low)

Key Metrics:
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric                  ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Health Score            │ 67    │
│ Burnout Score           │ 15    │
│ Stars                   │ 68477 │
│ Open Issues             │ 30    │
│ Open PRs                │ 32    │
└─────────────────────────┴───────┘
```

### 2. Save Results to File

```bash
ccda-cli analyze pkg:npm/express --output express-analysis.json
```

This creates a JSON file with complete analysis data.

### 3. View the JSON Output

```bash
# Pretty-print the JSON
cat express-analysis.json | jq

# Extract specific fields
jq '.health_score' express-analysis.json
jq '.burnout_score' express-analysis.json
jq '.git_metrics.bus_factor' express-analysis.json
```

---

## Analyzing Different Ecosystems

### Python Packages (PyPI)

```bash
ccda-cli analyze pkg:pypi/requests
```

### Rust Packages (Cargo)

```bash
ccda-cli analyze pkg:cargo/serde
```

### Java Packages (Maven)

```bash
ccda-cli analyze pkg:maven/org.opensearch/opensearch
```

### Go Modules

```bash
ccda-cli analyze pkg:go/github.com/hashicorp/terraform
```

### GitHub Repositories Directly

```bash
ccda-cli analyze pkg:github/expressjs/express
```

---

## Understanding the Output

### Health Score (0-100)

Measures overall package health:

| Score | Grade | Status |
|-------|-------|--------|
| 85-100 | A | Excellent |
| 70-84 | B | Good |
| 55-69 | C | Fair |
| 40-54 | D | Poor |
| 0-39 | F | Critical |

**Components:**
- Commit activity (15 pts)
- Bus factor (10 pts)
- Pony factor (10 pts)
- Contributor retention (10 pts)
- Elephant factor (10 pts)
- Issue responsiveness (10 pts)
- PR velocity (10 pts)
- Branch protection (10 pts)
- Release frequency (10 pts)
- License stability (5 pts)

### Burnout Score (0-100)

Measures maintainer sustainability risk:

| Score | Risk Level | Status |
|-------|------------|--------|
| 0-30 | Low |  Healthy |
| 31-40 | Medium |  Monitor |
| 41-60 | High |  Concerning |
| 61-100 | Critical |  Urgent |

**Components:**
- Issue backlog pressure (20 pts)
- Response time gaps (20 pts)
- Triage overhead (20 pts)
- Workload concentration (20 pts)
- Activity decline (20 pts)

---

## Common Commands

### Discovery Only

If you just want metadata without full analysis:

```bash
ccda-cli discover pkg:npm/lodash
```

### Check Cache

```bash
# View cache statistics
ccda-cli cache info

# Clear all cached data
ccda-cli cache clear --all
```

### Force Refresh

Re-analyze without using cached data:

```bash
ccda-cli analyze pkg:npm/express --force-refresh
```

### Skip Certain Steps

```bash
# Skip cloning (use cached clone)
ccda-cli analyze pkg:npm/express --skip-clone

# Skip tarball scanning
ccda-cli analyze pkg:npm/express --skip-tarball

# Skip GitHub API (save rate limit)
ccda-cli analyze pkg:npm/express --skip-github
```

---

## Setting Up GitHub Token (Recommended)

Without a GitHub token, you're limited to **60 requests/hour**. With a token, you get **5000 requests/hour**.

### Quick Setup

1. **Generate token**: https://github.com/settings/tokens
2. **Set environment variable**:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```
3. **Verify**:
   ```bash
   ccda-cli analyze pkg:npm/express --output test.json
   jq '.github_metrics.rate_limit.limit' test.json
   # Should show 5000, not 60
   ```

See [GITHUB_TOKEN_SETUP.md](../GITHUB_TOKEN_SETUP.md) for detailed instructions.

---

## Batch Analysis Example

Analyze multiple packages:

```bash
# Create package list
cat > packages.txt << EOF
pkg:npm/express
pkg:pypi/requests
pkg:cargo/serde
pkg:maven/org.opensearch/opensearch
EOF

# Analyze all
mkdir -p results
for purl in $(cat packages.txt); do
  name=$(echo $purl | sed 's/pkg://' | tr '/:' '_')
  ccda-cli analyze "$purl" --output "results/${name}.json"
done

# View results
ls -lh results/
```

---

## Next Steps

Now that you've completed basic analysis, explore:

1. **[Command Reference](commands.md)** - All available commands
2. **[Configuration Guide](configuration.md)** - Customize behavior
3. **[API Integrations](api-integrations.md)** - Understand data sources
4. **[Architecture](architecture.md)** - How ccda-cli works

---

## Troubleshooting

### "Package not found"

**Problem:** Package doesn't exist or PURL is malformed

**Solution:**
- Verify package exists in registry
- Check PURL format: `pkg:<ecosystem>/<name>[@version]`
- Try without version: `pkg:npm/express` instead of `pkg:npm/express@4.18.2`

### "Rate limit exceeded"

**Problem:** Hit GitHub's 60 requests/hour limit

**Solution:**
- Set up GitHub token (see above)
- Or wait for rate limit to reset
- Check reset time: `jq '.github_metrics.rate_limit.reset_at' output.json`

### "Repository not found"

**Problem:** Package metadata doesn't include repository URL

**Solution:**
- Package may not have repository field in metadata
- Set up SerpAPI for fallback search (see [SERPAPI_SETUP.md](../SERPAPI_SETUP.md))
- Or manually check package registry page for repository link

### "Clone failed"

**Problem:** Can't clone repository

**Solution:**
- Check internet connection
- Repository may be private or deleted
- Try `--skip-clone` to analyze without git history

---

## Getting Help

- **Documentation**: [docs/](.)
- **Issues**: [GitHub Issues](https://github.com/SemClone/ccda-cli/issues)
- **Examples**: [API_AND_CONFIG_DETAILS.md](../API_AND_CONFIG_DETAILS.md)

---

**Ready to analyze your supply chain!** 

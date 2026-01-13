# SerpAPI Setup Guide

## What is SerpAPI?

SerpAPI is a **fallback mechanism** for discovering GitHub repository URLs when all other discovery methods fail.

**How it works:**
- Uses Google Search with `site:github.com` to search for the package
- Extracts the most relevant GitHub repository URL from search results
- Only runs when: `repository_url` is still `null` after all other discovery attempts

**Discovery order:**
1. deps.dev API 
2. ecosyste.ms API 
3. ClearlyDefined API 
4. Package registries (npm, PyPI) 
5. **SerpAPI (last resort)** ← You are here

---

## Why You Need SerpAPI

**Without SerpAPI:**
- Packages without proper repository metadata in registries may fail discovery
- Obscure or misconfigured packages won't get repository URLs
- Manual intervention required for packages with missing metadata

**With SerpAPI:**
- Automatic fallback search for missing repository URLs
- Finds repositories even when package metadata is incomplete
- Higher success rate for discovery pipeline

---

## When SerpAPI is Used

SerpAPI is **only** used as a last resort when:

1.  Package metadata doesn't include a repository URL
2.  deps.dev doesn't have repository information
3.  ecosyste.ms doesn't have the package
4.  ClearlyDefined doesn't have source location
5.  Package registry doesn't provide GitHub URL
6.  `SERPAPI_KEY` or `CCDA_SERPAPI_KEY` is configured

**Example packages that might need SerpAPI:**
- New packages not yet indexed by ecosyste.ms
- Packages with broken metadata
- Private/enterprise packages with custom registries
- Packages published without proper repository field

---

## How to Get a SerpAPI Key

### Step 1: Sign Up

1. Go to https://serpapi.com/
2. Click "Sign Up" or "Get Started"
3. Create an account (free tier available)

### Step 2: Get Your API Key

1. After signing in, go to https://serpapi.com/manage-api-key
2. Copy your API key (starts with a long alphanumeric string)

### Free Tier Limits

| Plan | Searches/Month | Cost |
|------|---------------|------|
| Free | 100 | $0 |
| Developer | 5,000 | $50/mo |
| Production | 15,000+ | $125/mo+ |

**For ccda-cli:**
- Each package analysis that **fails to find a repository** will use **1 SerpAPI search**
- Most packages will NOT use SerpAPI (other sources work)
- 100 free searches/month is usually sufficient for testing and small-scale use

---

## How to Configure SerpAPI

### Method 1: Environment Variable (Recommended) ⭐

```bash
export SERPAPI_KEY=your_serpapi_key_here
```

Or use the CCDA-specific variable:

```bash
export CCDA_SERPAPI_KEY=your_serpapi_key_here
```

Add to your shell profile for persistence:

```bash
# ~/.bashrc or ~/.zshrc
export SERPAPI_KEY=your_serpapi_key_here
```

Then run ccda-cli:

```bash
source ~/.bashrc  # or restart terminal
ccda-cli analyze pkg:npm/some-obscure-package
```

### Method 2: Config File

Create `~/.ccda/config.yaml`:

```yaml
serpapi_key: your_serpapi_key_here
```

** Warning:** Storing keys in config files is less secure. Use environment variables instead.

### Method 3: Project Config

Create `./ccda-config.yaml` in your project:

```yaml
serpapi_key: your_serpapi_key_here
```

---

## Priority Order

When multiple methods are used, the priority is:

1. **Environment variable** (`CCDA_SERPAPI_KEY`)
2. **Environment variable** (`SERPAPI_KEY`)
3. **Project config** (`./ccda-config.yaml`)
4. **User config** (`~/.ccda/config.yaml`)
5. **No key** (SerpAPI fallback disabled)

---

## Testing SerpAPI Configuration

### Quick Test

Set your API key and analyze a package:

```bash
export SERPAPI_KEY=your_key_here
ccda-cli analyze pkg:npm/some-package --output test.json
```

Check if SerpAPI was used:

```bash
jq '.discovery.sources' test.json
```

If SerpAPI was used, you'll see:

```json
[
  "deps.dev",
  "serpapi"
]
```

### Force SerpAPI Usage (for testing)

To test SerpAPI without needing a package that actually lacks repository data, you can temporarily modify a package's discovery to skip other sources (not recommended for production):

```bash
# Analyze a package that typically has good metadata
# SerpAPI should NOT trigger
ccda-cli analyze pkg:pypi/requests --output test.json

# Check sources (should NOT include serpapi)
jq '.discovery.sources' test.json
```

Expected: `["deps.dev", "ecosyste.ms", "pypi"]` (no serpapi)

---

## Verifying SerpAPI Works

### Check Configuration

```bash
python3 << 'EOF'
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "src"))
from ccda_cli.config import get_config

print(f"SERPAPI_KEY env: {os.environ.get('SERPAPI_KEY', 'NOT SET')[:20]}...")
print(f"CCDA_SERPAPI_KEY env: {os.environ.get('CCDA_SERPAPI_KEY', 'NOT SET')[:20]}...")

config = get_config()
if config.serpapi_key:
    print(f"Config serpapi_key: {config.serpapi_key[:20]}...")
else:
    print("Config serpapi_key: NOT SET")
EOF
```

Expected output (with key):

```
SERPAPI_KEY env: 1234567890abcdef1234...
CCDA_SERPAPI_KEY env: NOT SET
Config serpapi_key: 1234567890abcdef1234...
```

### Manual SerpAPI Test

Run the test script:

```bash
python test_serpapi.py
```

Expected output:

```
Test 1 - Basic extraction:
  Expected: https://github.com/psf/requests
  Got:      https://github.com/psf/requests
  Status:    PASS

...

SerpAPI URL extraction tests completed!
```

---

## Usage Examples

### Example 1: Standard Analysis

```bash
export SERPAPI_KEY=your_key_here
ccda-cli analyze pkg:npm/express --output analysis.json
```

**What happens:**
1. deps.dev finds repository → SerpAPI **NOT** used 
2. Output: `"sources": ["deps.dev", "ecosyste.ms", "npm"]`

### Example 2: Package with Missing Metadata

```bash
export SERPAPI_KEY=your_key_here
ccda-cli analyze pkg:npm/some-obscure-package --output analysis.json
```

**What happens:**
1. deps.dev → no repository ❌
2. ecosyste.ms → package not found ❌
3. ClearlyDefined → no source location ❌
4. npm registry → no repository field ❌
5. SerpAPI → searches Google for "site:github.com some-obscure-package npm" 
6. Extracts repository URL from search results 
7. Output: `"sources": ["deps.dev", "serpapi"]`

### Example 3: Batch Analysis

```bash
#!/bin/bash
# batch_with_serpapi.sh

export SERPAPI_KEY=your_key_here

PACKAGES=(
    "pkg:npm/lodash"
    "pkg:npm/express"
    "pkg:pypi/requests"
    "pkg:npm/some-obscure-package"  # Might use SerpAPI
)

for purl in "${PACKAGES[@]}"; do
    echo "Analyzing: $purl"
    ccda-cli analyze "$purl" --output "results/$(basename $purl).json"

    # Check if SerpAPI was used
    if jq -e '.discovery.sources | index("serpapi")' "results/$(basename $purl).json" > /dev/null; then
        echo "   SerpAPI fallback used (1 search consumed)"
    fi
done
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: CCDA Analysis with SerpAPI

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install ccda-cli
        run: pip install ccda-cli

      - name: Run analysis with SerpAPI fallback
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SERPAPI_KEY: ${{ secrets.SERPAPI_KEY }}  # Add to repo secrets
        run: |
          ccda-cli analyze pkg:npm/express --output results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: ccda-results
          path: results.json
```

**Setup:**
1. Go to your repository settings
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SERPAPI_KEY`
5. Value: Your SerpAPI key
6. Click "Add secret"

---

## Troubleshooting

### "SerpAPI key not configured" Warning

**Problem:** SerpAPI is not being used even though you set the key

**Solution:**
1. Check environment variable: `echo $SERPAPI_KEY`
2. Verify config: `python -c "from ccda_cli.config import get_config; print(get_config().serpapi_key)"`
3. Restart terminal after setting env var

### "Rate limit exceeded" Error

**Problem:** Used all 100 free searches

**Solution:**
1. Check usage: https://serpapi.com/dashboard
2. Upgrade plan or wait for monthly reset
3. Optimize: Most packages should NOT trigger SerpAPI

### SerpAPI Returns Wrong Repository

**Problem:** Search results point to wrong GitHub repo

**Cause:** Package name is too generic (e.g., "utils", "helpers")

**Solution:**
- SerpAPI includes ecosystem in search query to improve relevance
- If results are still poor, the package likely has very poor metadata
- Consider manually specifying repository URL or fixing package metadata at source

### No Results from SerpAPI

**Problem:** SerpAPI search returns no GitHub URLs

**Possible causes:**
1. Package truly has no GitHub repository
2. Repository is private/internal
3. Search query too specific or too broad

**Debug:**
```bash
# Check what SerpAPI would search for:
# For pkg:npm/some-package
# Query: site:github.com "some-package" npm
```

---

## Cost Optimization

### Minimize SerpAPI Usage

SerpAPI is only called when absolutely necessary, but you can further optimize:

1. **Use comprehensive package registries**
   - npm packages usually have good metadata → no SerpAPI
   - PyPI packages usually have repository URLs → no SerpAPI

2. **Cache discovery results**
   - ccda-cli caches discovery by default
   - Re-analyzing same package won't call SerpAPI again

3. **Monitor usage**
   ```bash
   # Count SerpAPI uses in batch
   jq -s '[.[] | select(.discovery.sources | index("serpapi"))] | length' results/*.json
   ```

4. **Set CCDA_SERPAPI_KEY only when needed**
   ```bash
   # Analyze with SerpAPI fallback
   SERPAPI_KEY=your_key ccda-cli analyze pkg:npm/obscure-package

   # Analyze without SerpAPI (will skip if repo URL not found)
   ccda-cli analyze pkg:npm/obscure-package
   ```

---

## Security Best Practices

###  DO

-  Use environment variables for API keys
-  Add `.ccda/config.yaml` to `.gitignore` if storing keys there
-  Use repository secrets in CI/CD
-  Rotate API keys regularly
-  Use different keys for dev/staging/prod environments
-  Monitor SerpAPI dashboard for unusual usage

### ❌ DON'T

- ❌ Commit API keys to git repositories
- ❌ Share API keys in chat/email
- ❌ Use production keys for development
- ❌ Store keys in plaintext config files in public repos
- ❌ Hardcode keys in scripts

---

## Summary

**Quick Start:**

```bash
# 1. Get SerpAPI key from https://serpapi.com/
# 2. Export it
export SERPAPI_KEY=your_key_here

# 3. Run analysis (SerpAPI automatically used as fallback)
ccda-cli analyze pkg:npm/express

# 4. Check if SerpAPI was needed
ccda-cli analyze pkg:npm/express --output test.json
jq '.discovery.sources' test.json
```

**For CI/CD:** Use repository secrets (see CI/CD Integration section)

**For Local Development:** Add `export SERPAPI_KEY=...` to your shell profile

That's it! SerpAPI will automatically kick in when needed. 

# GitHub Token Setup Guide

## Why You Need a GitHub Token

**Without Token (Unauthenticated):**
- Rate limit: 60 requests/hour
- ~7 packages analyzed per hour
- Risk of hitting rate limit
- Company affiliation detection: Email domains only

**With Token (Authenticated):**
- Rate limit: 5,000 requests/hour
- ~625 packages analyzed per hour
- Much more reliable for production use
- **Company affiliation enrichment**: Fetches actual company data from GitHub profiles

---

## How to Get a GitHub Token

### Option 1: Personal Access Token (Classic)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "CCDA CLI")
4. Select scopes:
   - ✅ `public_repo` (read public repository data)
   - ✅ `read:org` (optional: for organization data)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Option 2: Fine-Grained Personal Access Token (Recommended)

1. Go to https://github.com/settings/personal-access-tokens/new
2. Give it a name and description
3. Set expiration (e.g., 90 days, 1 year)
4. Repository access: "Public Repositories (read-only)"
5. Permissions:
   - Repository permissions:
     - ✅ Contents: Read
     - ✅ Issues: Read
     - ✅ Pull requests: Read
     - ✅ Metadata: Read (auto-selected)
6. Click "Generate token"
7. **Copy the token**

---

## How to Use the Token

### Method 1: Environment Variable (Standard) ⭐ RECOMMENDED

This is the standard method used by most GitHub tools:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Add to your shell profile for persistence:

```bash
# ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN=ghp_your_token_here
```

Then run ccda-cli:

```bash
source ~/.bashrc  # or restart terminal
ccda-cli analyze pkg:npm/express
```

### Method 2: CCDA-Specific Environment Variable

For explicit override or when you have multiple GitHub tokens:

```bash
export CCDA_GITHUB_TOKEN=ghp_your_token_here
ccda-cli analyze pkg:npm/express
```

**Priority:** `CCDA_GITHUB_TOKEN` > `GITHUB_TOKEN`

### Method 3: Config File

Create `~/.ccda/config.yaml`:

```yaml
github_token: ghp_your_token_here
```

**⚠️ Warning:** Storing tokens in config files is less secure. Use environment variables instead.

### Method 4: CLI Argument

```bash
ccda-cli --github-token ghp_your_token_here analyze pkg:npm/express
```

---

## Priority Order

When multiple methods are used, the priority is:

1. **CLI argument** (`--github-token`)
2. **Environment variable** (`CCDA_GITHUB_TOKEN`)
3. **Environment variable** (`GITHUB_TOKEN`)
4. **Project config** (`./ccda-config.yaml`)
5. **User config** (`~/.ccda/config.yaml`)
6. **No token** (unauthenticated, 60 req/hour limit)

---

## Verifying Token Works

### Quick Test

```bash
export GITHUB_TOKEN=ghp_your_token_here
ccda-cli analyze pkg:npm/lodash --output test.json
```

Check the rate limit in output:

```bash
jq '.github_metrics.rate_limit' test.json
```

Expected output with token:

```json
{
  "remaining": 4992,  // Should be ~5000
  "limit": 5000,      // NOT 60
  "reset_at": "2026-01-03T23:30:00"
}
```

Without token, you'd see:

```json
{
  "remaining": 55,
  "limit": 60,       // Only 60!
  "reset_at": "..."
}
```

### Verify in Pipeline

Run an analysis and watch for rate limit messages:

```bash
ccda-cli analyze pkg:npm/express 2>&1 | grep -i "rate"
```

---

## Example: Batch Analysis with Token

```bash
#!/bin/bash
# batch_with_token.sh

export GITHUB_TOKEN=ghp_your_token_here

PACKAGES=(
    "pkg:npm/lodash"
    "pkg:npm/express"
    "pkg:pypi/requests"
    "pkg:cargo/serde"
    "pkg:maven/org.opensearch/opensearch"
)

for purl in "${PACKAGES[@]}"; do
    echo "Analyzing: $purl"
    ccda-cli analyze "$purl" --output "results/$(basename $purl).json"
done
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: CCDA Analysis

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

      - name: Run analysis
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Auto-provided by GitHub
        run: |
          ccda-cli analyze pkg:npm/express --output results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: ccda-results
          path: results.json
```

**Note:** GitHub Actions automatically provides `GITHUB_TOKEN` - no setup needed!

### GitLab CI

```yaml
analyze:
  image: python:3.11
  script:
    - pip install ccda-cli
    - export GITHUB_TOKEN=$GITHUB_API_TOKEN
    - ccda-cli analyze pkg:npm/express --output results.json
  artifacts:
    paths:
      - results.json
  variables:
    GITHUB_API_TOKEN: $GITHUB_TOKEN  # Set in GitLab CI/CD variables
```

### Jenkins

```groovy
pipeline {
    agent any

    environment {
        GITHUB_TOKEN = credentials('github-token-id')
    }

    stages {
        stage('Analyze') {
            steps {
                sh '''
                    pip install ccda-cli
                    ccda-cli analyze pkg:npm/express --output results.json
                '''
            }
        }
    }
}
```

---

## Troubleshooting

### "Rate limit exceeded" Error

**Problem:** You hit the 60 req/hour limit

**Solution:**
1. Check if token is set: `echo $GITHUB_TOKEN`
2. Verify token is valid (test on GitHub API directly)
3. Check rate limit: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit`

### Token Not Being Used

**Symptoms:**
- Still seeing 60 req/hour limit
- `rate_limit.limit` shows 60 in output

**Debugging:**

```bash
# Test token directly
python3 << 'EOF'
import os
from ccda_cli.config import get_config

print(f"GITHUB_TOKEN env: {os.environ.get('GITHUB_TOKEN', 'NOT SET')}")
print(f"CCDA_GITHUB_TOKEN env: {os.environ.get('CCDA_GITHUB_TOKEN', 'NOT SET')}")

config = get_config()
print(f"Config github_token: {config.github_token[:10] if config.github_token else 'NOT SET'}...")
EOF
```

Expected output:

```
GITHUB_TOKEN env: ghp_yourtoken...
CCDA_GITHUB_TOKEN env: NOT SET
Config github_token: ghp_yourto...
```

### Invalid Token

**Error:** "Bad credentials" or "401 Unauthorized"

**Solutions:**
1. **Regenerate token** - Token may have expired
2. **Check scopes** - Ensure `public_repo` or `repo` scope
3. **Test manually:**
   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user
   ```

---

## Security Best Practices

### ✅ DO

- ✅ Use environment variables for tokens
- ✅ Add tokens to `.gitignore` if in config files
- ✅ Use fine-grained tokens with minimal scopes
- ✅ Set expiration dates on tokens
- ✅ Rotate tokens regularly
- ✅ Use different tokens for different environments
- ✅ Store tokens in secret management (Vault, AWS Secrets Manager, etc.)

### ❌ DON'T

- ❌ Commit tokens to git repositories
- ❌ Share tokens in chat/email
- ❌ Use personal tokens for production (use GitHub App instead)
- ❌ Give more permissions than needed
- ❌ Use tokens without expiration

---

## Company Affiliation Enrichment

When a GitHub token is provided, ccda-cli automatically enriches contributor data with company affiliation information from GitHub user profiles.

### How It Works

1. **Extracts GitHub Usernames**: Detects contributors using GitHub noreply emails (e.g., `username@users.noreply.github.com`)
2. **Fetches User Profiles**: Makes GitHub API calls to get profile data
3. **Caches Profiles**: Stores profiles for 30 days to avoid duplicate API calls
4. **Normalizes Company Names**: Maps company strings to standardized names (e.g., "@google" → "Google")
5. **Falls Back to Email Domains**: Uses email domain mapping when API calls aren't available

### Example Output

**Without Token (Email Domain Only):**
```json
{
  "elephant_factor": 2,
  "company_distribution": [
    {
      "company": "Independent",
      "commits": 450,
      "percentage": 75.0,
      "contributors": 45
    },
    {
      "company": "Google",  // Only from @google.com emails
      "commits": 150,
      "percentage": 25.0,
      "contributors": 5
    }
  ]
}
```

**With Token (GitHub Profile Data):**
```json
{
  "elephant_factor": 3,
  "company_distribution": [
    {
      "company": "Independent",
      "commits": 300,
      "percentage": 50.0,
      "contributors": 30
    },
    {
      "company": "Google",  // From both emails AND GitHub profiles
      "commits": 200,
      "percentage": 33.3,
      "contributors": 15
    },
    {
      "company": "Microsoft",  // Discovered via GitHub API
      "commits": 100,
      "percentage": 16.7,
      "contributors": 5
    }
  ]
}
```

### Configuration

By default, company enrichment is enabled when a GitHub token is provided. You can disable it:

**Config File (`~/.ccda/config.yaml`):**
```yaml
github:
  enrich_company_affiliation: false
```

**Environment Variable:**
```bash
# Not directly configurable via env vars
# Must use config file to disable
```

### Benefits

- **More Accurate Elephant Factor**: Better understanding of organizational diversity
- **Better Risk Assessment**: Identify single-organization dependencies
- **Community Insights**: See actual company involvement beyond email domains

---

## Advanced: GitHub App (For Production)

For high-volume production use, consider GitHub App instead of PAT:

**Benefits:**
- 15,000 requests/hour
- Better audit trail
- Organization-wide management
- Fine-grained repository access

**Setup:**
1. Create GitHub App: https://github.com/settings/apps/new
2. Generate private key
3. Install app on repositories
4. Use app authentication instead of PAT

*Note: GitHub App support may require additional ccda-cli configuration.*

---

## Rate Limit Calculator

| Packages | Requests/Package | Total Requests | Time (no token) | Time (with token) |
|----------|------------------|----------------|-----------------|-------------------|
| 1 | 8 | 8 | ~1 min | ~1 min |
| 10 | 8 | 80 | ~80 min | ~1 min |
| 50 | 8 | 400 | ~400 min | ~5 min |
| 100 | 8 | 800 | ~800 min | ~10 min |
| 500 | 8 | 4000 | ~4000 min | ~50 min |

**Conclusion:** For analyzing more than 7 packages, a GitHub token is **essential**.

---

## Summary

**Quick Start:**

```bash
# 1. Get token from GitHub (see above)
# 2. Export it
export GITHUB_TOKEN=ghp_your_token_here

# 3. Run analysis
ccda-cli analyze pkg:npm/express

# 4. Verify (should show limit: 5000, not 60)
ccda-cli analyze pkg:npm/express --output test.json
jq '.github_metrics.rate_limit.limit' test.json
```

**For CI/CD:** Use `GITHUB_TOKEN` environment variable (often auto-provided)

**For Local Development:** Add `export GITHUB_TOKEN=...` to your shell profile

That's it! You're now ready for high-volume analysis. 🚀

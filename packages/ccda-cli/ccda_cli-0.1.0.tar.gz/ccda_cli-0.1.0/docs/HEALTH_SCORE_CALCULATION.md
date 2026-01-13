# Health Score Calculation

This document explains how the package health score (0-100) is calculated in CCDA.

## Overview

The health score is a comprehensive metric that evaluates packages across 5 key dimensions:

- **Vulnerability Score (0-25 points)**: Security vulnerabilities and exploitability
- **Maintenance Score (0-25 points)**: Activity, responsiveness, and maintainer diversity
- **Security Practices (0-25 points)**: Security tooling and best practices
- **Community Score (0-15 points)**: Engagement, growth, and backing
- **Stability Score (0-10 points)**: Maturity and consistency

**Total: 100 points maximum**

## Grading Scale

| Grade | Score Range | Risk Level |
|-------|-------------|------------|
| A     | 85-100      | LOW        |
| B     | 70-84       | LOW        |
| C     | 55-69       | MEDIUM     |
| D     | 40-54       | HIGH       |
| F     | 0-39        | CRITICAL   |

## Score Breakdown

### 1. Vulnerability Score (0-25 points)

**Higher is better** - Starts with 25 points, deductions for vulnerabilities.

#### Calculation
```
Base: 25 points
- Vulnerability count: up to -12 points (1.2 points per vulnerability)
- High/Critical severity: up to -8 points (2.5 points per high/critical vuln)
- High EPSS score (>0.1): up to -5 points (2 points per exploitable vuln)
- Known PoC exploits (B.4): up to -5 points (2.5 points per CVE with PoC)
```

The exploit detection (B.4) searches GitHub for proof-of-concept repositories for each CVE. When PoCs are found, it indicates higher real-world exploitability beyond the EPSS probability score.

#### Example
- 5 vulnerabilities: -6 points (5 × 1.2)
- 2 critical severity: -5 points (2 × 2.5)
- 1 high EPSS: -2 points
- 1 CVE with PoC: -2.5 points
- **Final: 9.5/25 points**

The breakdown includes `exploits_with_poc` showing how many CVEs have known exploit code.

### 2. Maintenance Score (0-25 points)

**Higher is better** - Measures active maintenance and contributor health.

#### Components

| Component | Max Points | Scoring |
|-----------|------------|---------|
| **Bus Factor** | 6 | ≥5 contributors = 6pts, ≥3 = 4pts, ≥2 = 2pts, 1 = 0pts |
| **Elephant Factor** | 3 | ≥4 companies = 3pts, ≥2 = 2pts, 1 = 0pts |
| **Commit Frequency** | 4 | very_high=4, high=3, moderate=2, low=1, unknown=0 |
| **Issue Responsiveness** | 4 | excellent=4, good=3, moderate=2, slow=0 |
| **PR Velocity** | 4 | fast=4, moderate=3, slow=1, very_slow=0 |
| **Review Turnaround** | 3 | very_fast=3, fast=2, moderate=1, slow=0 |
| **Contributor Retention** | 3 | healthy=3, moderate=2, concerning=1, critical=0 |
| **Contributor Diversity** | 4 | ≥10 unique authors = 4pts, ≥5 = 3pts, ≥2 = 1pt |

#### CHAOSS Metrics

- **Bus Factor**: Minimum number of contributors that need to leave before the project is at risk
- **Pony Factor**: Minimum contributors whose combined work represents 50% of contributions
- **Elephant Factor**: Minimum companies whose employees represent 50% of contributions

#### Example
```
Bus Factor (3): 4 points
Elephant Factor (2): 2 points
Commit Frequency (high): 3 points
Issue Responsiveness (good): 3 points
PR Velocity (moderate): 3 points
Review Turnaround (fast): 2 points
Contributor Retention (healthy): 3 points
Contributor Diversity (8 authors): 3 points
Total: 23/25 points
```

### 3. Security Practices Score (0-25 points)

**Higher is better** - Measures security tooling and best practices adoption.

#### Components

| Component | Max Points | Scoring |
|-----------|------------|---------|
| **SECURITY.md file** | 5 | Has security policy = 5pts |
| **Dependency Automation** | 4 | Dependabot or Renovate = 4pts |
| **CI/CD** | 3 | GitHub Actions = 3pts |
| **Branch Protection** | 5 | Protected with required reviews = 5pts<br>Protected with PR requirement = 4pts<br>Protected = 3pts<br>Likely protected = 2pts |
| **Signed Releases** | 4 | ≥80% signed = 4pts<br>≥50% signed = 2pts<br>Some signing = 1pt |
| **Has License** | 2 | License present = 2pts |
| **Has Lockfile** | 2 | Lockfile present = 2pts |

#### Example
```
SECURITY.md: 5 points
Dependabot enabled: 4 points
GitHub Actions: 3 points
Branch protected (no reviews): 3 points
No signed releases: 0 points
Has license: 2 points
Has lockfile: 2 points
Total: 19/25 points
```

### 4. Community Score (0-15 points)

**Higher is better** - Measures community engagement and backing.

#### Components

| Component | Max Points | Scoring |
|-----------|------------|---------|
| **Stars** | 5 | ≥10,000 = 5pts<br>≥1,000 = 4pts<br>≥100 = 2pts<br>≥10 = 1pt |
| **Forks** | 3 | ≥1,000 = 3pts<br>≥100 = 2pts<br>≥10 = 1pt |
| **Contributors** | 3 | ≥50 = 3pts<br>≥20 = 2pts<br>≥10 = 1pt |
| **Contributor Growth** | 2 | Rapid or healthy = 2pts<br>Moderate = 1pt |
| **Foundation Backing** | 4 | Member of OSS foundation = 4pts |

#### Example
```
Stars (5,200): 4 points
Forks (850): 2 points
Contributors (45): 2 points
Growth (healthy): 2 points
Not foundation-backed: 0 points
Total: 10/15 points
```

### 5. Stability Score (0-10 points)

**Higher is better** - Measures project maturity and consistency.

#### Components

| Component | Max Points | Scoring |
|-----------|------------|---------|
| **Not Archived** | 3 | Active repository = 3pts |
| **Has License** | 2 | License present = 2pts |
| **Project Age** | 3 | ≥5 years = 3pts<br>≥2 years = 2pts<br>≥1 year = 1pt |
| **PR Acceptance Rate** | 2 | ≥80% acceptance = 2pts<br>≥60% acceptance = 1pt |
| **License Stability** | ±2 | Stable license = +2pts<br>High risk/frequent changes = -2pts |

**Note**: License stability can add or subtract points, so the score is capped at 0-10.

#### Example
```
Not archived: 3 points
Has license: 2 points
Age (7 years): 3 points
PR acceptance (85%): 2 points
Stable license: 2 points
Total: 12 → 10/10 points (capped)
```

## Real-World Example: Express.js

Score: **73/100 (Grade B, LOW RISK)**

| Component | Score | Max | Notes |
|-----------|-------|-----|-------|
| Vulnerability | 18 | 25 | Some known vulnerabilities present |
| Maintenance | 18 | 25 | Active but could improve response times |
| Security Practices | 16 | 25 | Good practices but missing signed releases |
| Community | 11 | 15 | Strong community, not foundation-backed |
| Stability | 10 | 10 | Mature, stable project (10+ years old) |

## Recommendations

The health score calculation automatically generates recommendations based on low scores:

- **Vulnerability < 15**: "Update dependencies to fix known vulnerabilities"
- **Maintenance < 12**: "Low maintainer activity or slow response times"
- **Security Practices < 12**: "Package lacks security best practices"
- **Bus Factor ≤ 2**: "High bus factor risk - only X contributor(s) for 50% of commits"
- **Elephant Factor = 1**: "Single company dominance - consider corporate dependency risk"
- **Branch Protection = false**: "Main branch is not protected - risk of unauthorized changes"
- **No Signed Releases**: "Releases are not signed - cannot verify authenticity"
- **No Lockfile**: "No lockfile found - dependency versions may be unpinned"
- **Slow Issue Response**: "Slow issue response times - maintainers may be unavailable"
- **Slow PR Velocity**: "Slow PR merge times - contributions may not be reviewed promptly"
- **Low Retention**: "Low contributor retention - many past contributors have left"
- **Stagnant Growth**: "Stagnant contributor growth - few new contributors joining"
- **License Changes**: "License has changed multiple times or has concerning transitions"

## Implementation

The health score calculation is implemented in `ccda/packages.py` in the `calculate_health_score()` method (lines 3709-4112).

### Data Sources

- **Vulnerabilities**: OSV API
- **GitHub Metrics**: GitHub API (repository, contributors, activity, security)
- **EPSS Scores**: FIRST.org EPSS API
- **Foundation Data**: User-configurable foundation list
- **Commit/PR/Issue Data**: GitHub API with pagination
- **Branch Protection**: GitHub API (requires admin permissions)
- **Signed Releases**: GitHub API release data with GPG signature verification

### Caching

All metrics are cached in DigitalOcean Spaces storage to minimize API calls and improve performance. The health score is recalculated on-demand when metrics are refreshed.

## Related Documentation

- [METRICS_SPECIFICATION.md](./METRICS_SPECIFICATION.md) - Detailed metric definitions
- [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Feature implementation status
- [BUSINESS_OVERVIEW.md](./BUSINESS_OVERVIEW.md) - Business context and use cases

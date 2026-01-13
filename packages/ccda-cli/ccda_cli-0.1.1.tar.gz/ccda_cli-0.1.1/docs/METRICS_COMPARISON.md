# CCDA Metrics Comparison Analysis

## Detailed Overlap and Gap Analysis vs. Industry Tools

This document compares CCDA metrics against industry tools to identify gaps and implementation priorities.

### Key Principle

**CCDA uses only open data sources + AI agents. No commercial data integrations.**

- **Open Data Sources:** GitHub API, NVD, OSV, GitHub Advisories, RSS feeds, HackerNews, Reddit
- **AI/Agentic Approach:** GenAI agents synthesize metrics, advisories, and insights
- **Commercial Tools:** Referenced only for gap analysis (what metrics exist), not for data

---

## 1. CCDA Metrics Inventory

### What CCDA Currently Captures

#### A. Media Analysis Metrics (AI-Powered)

| Metric | Range | Source | Description |
|--------|-------|--------|-------------|
| `risk_score` | 0.0-1.0 | AI Agent | Severity of business/operational risks |
| `sentiment_score` | -1.0 to 1.0 | AI Agent | Positive/negative ecosystem impact |
| `relevance_score` | 0.0-1.0 | Calculated | How relevant to OSS monitoring |
| `action_priority` | 0.0-1.0 | Calculated | Urgency of response needed |
| `oss_health_indicator` | -1.0 to 1.0 | Formula | `sentiment - (risk × 0.5)` |
| `confidence` | high/medium/low | AI Agent | Analysis confidence level |
| `impact_level` | critical/high/medium/low | AI Agent | Significance for OSS |

#### B. Risk Categories Tracked

| Category | Description | Example Detection |
|----------|-------------|-------------------|
| `security` | Vulnerabilities, CVEs, breaches | "Critical RCE in Log4j" |
| `legal` | License changes, lawsuits | "Redis moves to SSPL" |
| `acquisition` | Mergers, buyouts | "Microsoft acquires npm" |
| `governance` | Leadership changes, disputes | "Maintainer stepping down" |
| `deprecation` | EOL, abandonment | "Python 2 sunset" |
| `maintainer` | Burnout, reduced activity | "Core developer leaves" |
| `funding` | Sponsorship changes | "Funding cuts" |
| `fork` | Community splits | "MariaDB forks MySQL" |
| `supply_chain` | Dependency hijacking | "Malicious package" |
| `performance` | Regressions | "50% slower" |
| `breaking_change` | API incompatibilities | "Breaking changes in v3" |
| `controversy` | Ethical concerns | "Community boycott" |

#### C. GitHub Repository Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `stars` | Integer | Repository star count |
| `watchers` | Integer | Repository watcher count |
| `forks` | Integer | Fork count |
| `open_issues` | Integer | Open issue count |
| `created_at` | DateTime | Repository creation date |
| `updated_at` | DateTime | Last update timestamp |
| `pushed_at` | DateTime | Last push timestamp |
| `language` | String | Primary language |
| `archived` | Boolean | Archive status |
| `disabled` | Boolean | Disabled status |
| `commit_count` | Integer | Commits in lookback period |
| `unique_authors` | Integer | Unique contributors (30 days) |
| `commits_per_day` | Float | Commit velocity |
| `commit_frequency` | Enum | very_high/high/moderate/low/very_low/minimal |
| `org_distribution` | Dict | Commits per author |
| `org_percentages` | Dict | Commit % per author |
| `total_contributors` | Integer | All-time contributors |
| `top_contributors` | List | Top 10 by commit count |
| `open_prs` | Integer | Open pull requests |
| `avg_issue_age_days` | Float | Average open issue age |
| `oldest_issue_days` | Integer | Oldest open issue |
| `avg_pr_age_days` | Float | Average open PR age |
| `oldest_pr_days` | Integer | Oldest open PR |
| `issue_close_rate` | Float | Closed/(open+closed) ratio |
| `recently_closed_issues` | Integer | Issues closed in 30 days |
| `total_releases` | Integer | Release count |
| `latest_release` | DateTime | Last release date |
| `days_since_release` | Integer | Days since last release |
| `release_frequency` | Enum | weekly/monthly/quarterly/biannual/sporadic |

#### D. Risk Indicators (Calculated)

| Indicator | Threshold | Weight |
|-----------|-----------|--------|
| `is_stale` | >30 days since push | +20 |
| `low_bus_factor` | <3 unique contributors | +25 |
| `org_dominance` | >70% commits from one org | +15 |
| `slow_response` | >14 days avg issue age | +15 |
| `pr_backlog` | >30 days avg PR age | +10 |
| `risk_discussions` | Keywords in issues | +20 |
| `low_commit_activity` | very_low/minimal/none | +15 |

**Risk Level Calculation:**
- Critical: score >= 60
- High: score >= 40
- Medium: score >= 20
- Low: score < 20

#### E. Package Identification

| Field | Description |
|-------|-------------|
| `name` | Package name |
| `type` | Registry (npm, pypi, gem, etc.) |
| `purl` | Package URL (pkg:npm/react) |
| `confidence` | Detection confidence |
| `keywords` | Associated terms |

#### F. Maintainer & Account Metrics (New in Spec)

| Metric | Type | Description |
|--------|------|-------------|
| `maintainers` | List | Discovered maintainers from registry + GitHub |
| `activity_status` | Enum | active/recently_active/reduced_activity/low_activity/inactive |
| `activity_score` | Float | 0-1 activity level |
| `access_level` | Enum | admin/write/read/unknown |
| `access_confidence` | Enum | high/medium (inferred) |
| `account_age_days` | Integer | GitHub account age |
| `reputation_score` | Float | 0-1 based on followers, repos, profile |
| `profile_completeness` | Float | 0-1 profile fields filled |
| `risk_signals` | List | new_account, sparse_profile, suspicious_ratio |
| `anomalies` | List | commit_spike, sensitive_file_changes, new_repo_access |
| `last_activity` | DateTime | Most recent GitHub activity |

See [METRICS_SPECIFICATION.md](./METRICS_SPECIFICATION.md) Category F for full details.

#### G. Organizational & Governance Metrics (New - OSBC Support)

| Metric | Type | Description |
|--------|------|-------------|
| `company_affiliations` | Dict | Contributor distribution by company |
| `controlling_company` | String | Company with >50% contributions (if any) |
| `license_change_detected` | Boolean | Has license changed since baseline? |
| `license_change_type` | Enum | permissive_to_copyleft, permissive_to_source_available, etc. |
| `foundation_membership` | Object | Foundation name, governance model, confidence |
| `pr_acceptance_rate` | Float | % of PRs merged vs closed |
| `refused_prs` | List | PRs closed without merge, with reasons |
| `governance_model` | Enum | BDFL, meritocracy, foundation_pmc, corporate, committee |
| `contributor_recognitions` | List | Recognitions in releases/changelogs |

See [METRICS_SPECIFICATION.md](./METRICS_SPECIFICATION.md) Category G for full details.

---

## 2. Comparison with CHAOSS

### CHAOSS Metric Categories

CHAOSS defines metrics across 4 relevant working groups:
- Common Metrics
- Evolution
- Risk
- Value

### Overlap Analysis

| CHAOSS Metric | CCDA Equivalent | Status |
|---------------|-----------------|--------|
| **Contributor Absence Factor** (Bus Factor) | `unique_authors`, `org_percentages` | **OVERLAP** - CCDA calculates from commit data |
| **Time to First Response** | `avg_issue_age_days` (partial) | **PARTIAL** - CCDA tracks age, not first response |
| **Time to Close** | `issue_close_rate`, `recently_closed_issues` | **PARTIAL** - CCDA tracks ratio, not time |
| **Change Request Closure Ratio** | `issue_close_rate` | **OVERLAP** |
| **Commit Activity** | `commit_count`, `commits_per_day`, `commit_frequency` | **OVERLAP** |
| **Contributors** | `unique_authors`, `total_contributors` | **OVERLAP** |
| **Release Frequency** | `release_frequency`, `days_since_release` | **OVERLAP** |
| **Project Popularity** | `stars`, `forks`, `watchers` | **OVERLAP** |
| **Code Review** | Not tracked | **GAP** |
| **Geographic Coverage** | Not tracked | **GAP** |
| **Organizational Affiliation** | `org_distribution` (partial) | **PARTIAL** - commits only, not full affiliation |

### What CCDA Has That CHAOSS Doesn't

| CCDA Unique | Description |
|-------------|-------------|
| **AI-Powered Media Analysis** | Real-time news/social analysis |
| **Multi-dimensional Scoring** | Combined risk/sentiment/priority |
| **12 Risk Categories** | Business-specific risk taxonomy |
| **Supply Chain Focus** | Dependency hijacking, upstream issues |
| **License Change Detection** | AI-detected license risk |
| **Sentiment Analysis** | Positive/negative ecosystem impact |
| **Package Identification** | Automatic PURL generation |

### Gaps to Implement with AI Agents

| CHAOSS Metric | AI Implementation Approach |
|---------------|----------------------------|
| **Time to First Response** | GitHub API: issue created_at vs first comment |
| **Time to Close** (actual days) | GitHub API: issue created_at vs closed_at |
| **Code Review metrics** | GitHub API: PR review timestamps |
| **Geographic Diversity** | AI infers from contributor profiles/timezones |
| **Technical Fork Impact** | GitHub API: fork activity + AI impact analysis |

---

## 3. Comparison with OpenSSF Scorecard

### OpenSSF Scorecard Checks (18 total)

| Check | Score | What It Measures |
|-------|-------|------------------|
| Binary-Artifacts | 0-10 | No binaries in repo |
| Branch-Protection | 0-10 | Branch protection rules |
| CI-Tests | 0-10 | Tests run in CI |
| CII-Best-Practices | 0-10 | OpenSSF badge level |
| Code-Review | 0-10 | Code review enforcement |
| Contributors | 0-10 | Multi-org contributors |
| Dangerous-Workflow | 0-10 | Risky GitHub Actions |
| Dependency-Update-Tool | 0-10 | Automated updates (Dependabot) |
| Fuzzing | 0-10 | OSS-Fuzz participation |
| License | 0-10 | License declared |
| Maintained | 0-10 | Recent activity (90 days) |
| Packaging | 0-10 | Automated packaging |
| Pinned-Dependencies | 0-10 | Version pinning |
| SAST | 0-10 | Static analysis tools |
| Security-Policy | 0-10 | SECURITY.md file |
| Signed-Releases | 0-10 | Cryptographic signing |
| Token-Permissions | 0-10 | Read-only workflow tokens |
| Vulnerabilities | 0-10 | OSV vulnerability check |

### Overlap Analysis

| Scorecard Check | CCDA Equivalent | Status |
|-----------------|-----------------|--------|
| **Maintained** | `pushed_at`, `is_stale`, `commit_frequency` | **OVERLAP** - CCDA uses 30 days, Scorecard uses 90 |
| **Contributors** | `unique_authors`, `org_distribution` | **OVERLAP** |
| **Vulnerabilities** | `security` risk category | **PARTIAL** - CCDA detects news, not OSV scan |
| **License** | `legal` risk category | **PARTIAL** - CCDA detects changes, not presence |
| Binary-Artifacts | Not tracked | **GAP** |
| Branch-Protection | Not tracked | **GAP** |
| CI-Tests | Not tracked | **GAP** |
| CII-Best-Practices | Not tracked | **GAP** |
| Code-Review | Not tracked | **GAP** |
| Dangerous-Workflow | Not tracked | **GAP** |
| Dependency-Update-Tool | Not tracked | **GAP** |
| Fuzzing | Not tracked | **GAP** |
| Packaging | Not tracked | **GAP** |
| Pinned-Dependencies | Not tracked | **GAP** |
| SAST | Not tracked | **GAP** |
| Security-Policy | Not tracked | **GAP** |
| Signed-Releases | Not tracked | **GAP** |
| Token-Permissions | Not tracked | **GAP** |

### What CCDA Has That Scorecard Doesn't

| CCDA Unique | Value Proposition |
|-------------|-------------------|
| **Real-time Media Monitoring** | Catches issues before CVE publication |
| **Business Continuity Focus** | Governance, legal, maintainer risks |
| **Sentiment Analysis** | Ecosystem impact assessment |
| **Multi-source Intelligence** | RSS, HackerNews, Reddit |
| **Natural Language Analysis** | AI-powered content understanding |
| **Package Mapping** | Automatic PURL generation |
| **12 Risk Dimensions** | Beyond security-only focus |

### Gaps to Implement with Open APIs + AI

| Scorecard Check | Open Data + AI Approach |
|-----------------|-------------------------|
| **Vulnerabilities** | OSV API (free) + AI correlation with packages |
| **Security-Policy** | GitHub API: check SECURITY.md existence |
| **Branch-Protection** | GitHub API (requires token) |
| **Signed-Releases** | GitHub API: check release signatures |
| **Dependency-Update-Tool** | GitHub API: detect .github/dependabot.yml |
| **CI-Tests** | GitHub API: detect .github/workflows/ |
| **Code-Review** | GitHub API: PR review requirements |
| **Pinned-Dependencies** | AI analyzes package-lock.json, yarn.lock |
| **SAST** | AI detects CodeQL, SonarCloud in workflows |
| **Fuzzing** | GitHub API: check OSS-Fuzz integration |

---

## 4. Comparison with Bitergia

> **Note:** Bitergia is a commercial service. Used here only as **reference for gap analysis**.
> CCDA will implement equivalent metrics using open source tools and AI agents.

### Bitergia Metrics Categories (Reference Only)

| Category | Metrics |
|----------|---------|
| **Activity** | Commits, issues, PRs, reviews |
| **Community** | Contributors, new contributors, retention |
| **Performance** | Lead time, cycle time, PR merge time |
| **Efficiency** | Review turnaround, backlog |

### Overlap Analysis

| Bitergia Metric | CCDA Equivalent | Status |
|-----------------|-----------------|--------|
| **Commit Activity** | `commit_count`, `commits_per_day` | **OVERLAP** |
| **Contributor Count** | `total_contributors`, `unique_authors` | **OVERLAP** |
| **Issue Activity** | `open_issues`, `recently_closed_issues` | **OVERLAP** |
| **PR Activity** | `open_prs`, `avg_pr_age_days` | **PARTIAL** |
| **Release Activity** | `total_releases`, `release_frequency` | **OVERLAP** |
| **Contributor Retention** | Maintainer activity tracking (Cat. F) | **PARTIAL** - via maintainer watchlist |
| **New Contributor Rate** | Specified (A.8) | **SPECIFIED** |
| **PR Merge Time** | Specified (A.5) | **SPECIFIED** |
| **Review Turnaround** | Specified (A.6) | **SPECIFIED** |
| **Multi-Platform Data** | RSS, HN, Reddit, GitHub | **DIFFERENT** - CCDA adds media sources |

### What CCDA Has That Bitergia Doesn't

| CCDA Unique | Description |
|-------------|-------------|
| **AI-Powered Analysis** | LLM-based content understanding |
| **Media Intelligence** | News/social monitoring |
| **Risk Taxonomy** | 12 business risk categories |
| **Sentiment Scoring** | Ecosystem impact measurement |
| **Business Continuity Focus** | Beyond development metrics |
| **Maintainer Monitoring** | Activity tracking, anomaly detection, watchlists |
| **Account Compromise Detection** | AI-powered behavioral anomaly detection |

### Gaps to Implement with AI Agents

CCDA will implement these metrics using GitHub API + AI analysis (no commercial tools):

| Metric | AI Implementation Approach |
|--------|----------------------------|
| **Contributor Retention** | AI agent tracks contributor history via GitHub API |
| **New Contributor Rate** | Calculate from commit/PR author timestamps |
| **PR Merge Time** | GitHub API: PR created_at vs merged_at |
| **Review Turnaround** | GitHub API: review request vs review submitted |

---

## 5. Comparison with Flexera (Secunia Research)

> **Note:** Flexera is a commercial service used here only as a **reference for gap analysis**.
> CCDA will produce equivalent advisory capabilities using **AI agents**, not by integrating with Flexera.

### Flexera Advisory Components (Reference Only)

| Component | Description |
|-----------|-------------|
| **Advisory ID** | Unique identifier (SA-XXXXX) |
| **CVE References** | Associated CVE IDs |
| **CVSS Score** | Standardized severity |
| **Attack Vector** | How exploited |
| **Criticality Rating** | 1-5 severity |
| **Impact** | Confidentiality/Integrity/Availability |
| **Affected Products** | Product + version ranges |
| **Solution** | Patch/workaround guidance |
| **Exploit Status** | PoC available, ITW |
| **References** | Vendor advisories, patches |

### Overlap Analysis

| Flexera Component | CCDA Equivalent | Status |
|-------------------|-----------------|--------|
| **Severity Rating** | `risk_score`, `severity` | **PARTIAL** - Different scales |
| **Impact Analysis** | `oss_health_indicator` | **PARTIAL** - Different focus |
| **Affected Products** | Package identification + PURL | **OVERLAP** |
| **Solution/Patch** | Not tracked | **GAP** |
| **CVE References** | `security` category detection | **PARTIAL** - Detects news, not CVE DB |
| **CVSS Score** | Not tracked | **GAP** |
| **Exploit Status** | Not tracked | **GAP** |
| **Attack Vector** | Not tracked | **GAP** |

### What CCDA Has That Flexera Doesn't

| CCDA Unique | Description |
|-------------|-------------|
| **Non-Security Risks** | Governance, legal, maintainer issues |
| **Real-time Media Monitoring** | News before advisory publication |
| **Sentiment Analysis** | Community reaction measurement |
| **Open Source** | Fully transparent methodology |
| **Business Continuity Focus** | Beyond CVE/vulnerability scope |

### CCDA Agentic Advisory Approach

CCDA will produce equivalent (or better) advisory data using:

1. **CCDA's Own Data Collection** - RSS feeds, HackerNews, Reddit, GitHub analysis
2. **Open Vulnerability Databases** - NVD, OSV, GitHub Security Advisories, Google CVE
3. **AI Agents** - Synthesize, correlate, and generate actionable advisories

| Component | Data Sources | AI Agent Role |
|-----------|--------------|---------------|
| **CVE References** | NVD, OSV, GitHub Advisories | Correlate with detected packages |
| **CVSS Scores** | NVD API | Enrich with business context |
| **Solution/Remediation** | GitHub commits, changelogs, READMEs | Generate actionable fix guidance |
| **Exploit Status** | GitHub PoC repos, security blogs (via RSS) | Detect and classify exploit availability |
| **Attack Vector** | CVE descriptions, security advisories | Extract and summarize for non-technical readers |
| **Affected Versions** | Package registries, GitHub releases | Map to PURLs in user's SBOM |
| **Workarounds** | GitHub issues, discussions, commits | Synthesize temporary mitigations |
| **Patch Detection** | GitHub releases, changelogs | Monitor and alert on fixes |
| **Early Warning** | CCDA media monitoring | Detect issues BEFORE CVE publication |

**Key Differentiator:** CCDA's media monitoring catches security issues in news/discussions *before* they appear in NVD/CVE databases, providing earlier warning than traditional vulnerability feeds.

---

## 6. Summary: Gap Analysis

### Critical Gaps - Now Specified

| Gap | Status | Specification Reference |
|-----|--------|------------------------|
| **CVE/Vulnerability DB** | ✅ Specified | Part 9 - Bulk Data Sources (OSV, NVD) |
| **CVSS Scores** | ✅ Specified | Category B.2 - CVSS Scores |
| **Remediation Guidance** | ✅ Specified | Part 5 - Remediation Knowledge Base |
| **Exploit Intelligence** | ✅ Specified | Category B.4 - Exploit Status Detection |
| **Time to First Response** | ✅ Specified | Category A.3 - Time to First Response |
| **Maintainer Tracking** | ✅ Specified | Category F - Maintainer & Account Metrics |

### High Priority Gaps - Status Update

| Gap | Status | Notes |
|-----|--------|-------|
| **Security Policy Detection** | ✅ Specified | Category B.5 |
| **Contributor Retention** | ✅ Specified | Category A.7 + F.2 (activity tracking) |
| **Branch Protection** | ✅ Specified | Category B.6 |
| **Signed Releases** | ✅ Specified | Category B.7 |
| **Actual Time to Close** | ✅ Specified | Category A.4 |
| **Account Compromise Detection** | ✅ Specified | Category F.5 |

### Medium Priority Gaps - Status Update

| Gap | Status | Notes |
|-----|--------|-------|
| **Dependency Update Tools** | ✅ Specified | Category C.1 |
| **Geographic Diversity** | ✅ Specified | Category A.9 |
| **PR Merge Time** | ✅ Specified | Category A.5 |
| **Code Review Metrics** | ✅ Specified | Category A.6 - Review Turnaround |

### Low Priority Gaps (Remaining)

| Gap | Source | Impact |
|-----|--------|--------|
| **Pinned Dependencies** | Scorecard | ✅ Specified (Category C.2) |
| **Fuzzing Participation** | Scorecard | Not prioritized - specialized testing |
| **Binary Artifacts Check** | Scorecard | Not prioritized - low SBOM relevance |
| **CII Best Practices Badge** | Scorecard | Not prioritized - external badge check |

---

## 7. CCDA Unique Differentiators

### What Only CCDA Does

| Capability | Value |
|------------|-------|
| **AI-Powered Content Analysis** | Understands natural language risk signals |
| **Real-time Media Intelligence** | 16+ RSS feeds, HackerNews, Reddit |
| **Multi-dimensional Scoring** | 5 scores vs single aggregates |
| **12 Business Risk Categories** | Beyond security-only focus |
| **Sentiment Analysis** | Ecosystem impact measurement |
| **Automatic Package Identification** | PURL generation from unstructured text |
| **Business Continuity Focus** | Governance, legal, maintainer tracking |
| **Maintainer Monitoring** | Activity tracking, watchlists, anomaly detection |
| **Account Compromise Detection** | AI-powered behavioral analysis for supply chain attacks |
| **SBOM-Driven Collection** | Only collect data for packages you actually use |
| **Open Source + Self-hosted** | Full transparency and control |

### Competitive Positioning

```
                    VULNERABILITY          BUSINESS CONTINUITY
                    FOCUS                  FOCUS
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    │   OpenSSF         │       CCDA        │
    │   Scorecard       │                   │
    │                   │                   │
    │   Flexera         │                   │
POINT-IN-TIME ─────────┼───────────────── CONTINUOUS
ASSESSMENT             │                   MONITORING
    │                   │                   │
    │                   │       CHAOSS      │
    │                   │       Bitergia    │
    │                   │                   │
    └───────────────────┼───────────────────┘
                        │
                    COMMUNITY HEALTH
                    FOCUS
```

---

## 8. Recommended Integration Priorities

### Phase 1: Critical Integrations

1. **OSV/NVD Integration**
   - Connect to OSV API for known vulnerabilities
   - Add CVE correlation to detected packages
   - Include CVSS scores in output

2. **SECURITY.md Detection**
   - Check for security policy file
   - Parse disclosure process

### Phase 2: High-Value Additions

3. **Exploit Intelligence**
   - Monitor exploit-db, GitHub PoCs
   - Track in-the-wild status

4. **Remediation Generation**
   - Parse changelogs for fixes
   - Generate upgrade paths
   - Suggest workarounds

5. **Time-based Metrics**
   - Time to first response
   - Actual time to close (not just ratio)

### Phase 3: Enhanced Analytics

6. **Contributor Dynamics**
   - New contributor rate
   - Retention metrics
   - Churn detection

7. **Security Checks**
   - Branch protection status
   - Signed release verification
   - Dependency update tools

---

## References

### Open Source / Free Tools
- [CHAOSS Metrics](https://chaoss.community/metrics/)
- [CHAOSS Contributor Absence Factor](https://chaoss.community/kb/metric-contributor-absence-factor/)
- [CHAOSS Responsiveness Guide](https://chaoss.community/practitioner-guide-responsiveness/)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [OpenSSF Scorecard Checks](https://securityscorecards.dev/)
- [GrimoireLab](https://chaoss.github.io/grimoirelab/) - Open source analytics (used by Bitergia)

### Public Vulnerability Data Sources (for AI integration)
- [OSV (Open Source Vulnerabilities)](https://osv.dev/)
- [NVD (National Vulnerability Database)](https://nvd.nist.gov/)
- [GitHub Security Advisories](https://github.com/advisories)
- [Exploit-DB](https://www.exploit-db.com/)

### Commercial Reference (gap analysis only, not for integration)
- Flexera/Secunia - advisory format best practices
- Bitergia - development analytics metrics reference

### Related CCDA Documents
- [METRICS_SPECIFICATION.md](./METRICS_SPECIFICATION.md) - Full technical specification for all metrics
- [BUSINESS_OVERVIEW.md](./BUSINESS_OVERVIEW.md) - High-level architecture and competitive positioning

---

*Document generated for CCDA Metrics Comparison - December 2025*

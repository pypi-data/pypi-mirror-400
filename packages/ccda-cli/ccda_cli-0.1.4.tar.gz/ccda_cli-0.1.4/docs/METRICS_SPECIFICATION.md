# CCDA Metrics Implementation Specification

> **Note:** This document has been split into multiple files for easier navigation. See the **[Metrics Specification Index](./specs/README.md)** for the organized version with complete examples.

## Early Technical Specification for Metric Collection and AI Analysis

**Version:** 0.1 (Draft)
**Date:** December 2025
**Status:** Specification for Development

---

## Split Documentation

This specification is also available as separate documents:

| Document | Description |
|----------|-------------|
| [Index](./specs/README.md) | Overview, navigation, design principles |
| [Data Sources](./specs/01_DATA_SOURCES.md) | API endpoints, rate limits, examples |
| [Repository Health](./specs/02A_REPO_HEALTH.md) | Category A metrics |
| [Security](./specs/02B_SECURITY.md) | Category B metrics |
| [Supply Chain & Media](./specs/02C_SUPPLY_CHAIN.md) | Categories C, D, E |
| [Maintainer Metrics](./specs/02D_MAINTAINERS.md) | Category F metrics |
| [Governance](./specs/02E_GOVERNANCE.md) | Category G metrics |
| [AI Agents](./specs/03_AI_AGENTS.md) | Agent architecture |
| [Output Schemas](./specs/04_OUTPUT_SCHEMAS.md) | JSON schemas |
| [Remediation KB](./specs/05_REMEDIATION.md) | Knowledge base |
| [Implementation](./specs/06_IMPLEMENTATION.md) | Phases, roadmap |

---

## About This Specification

This specification is **forward-looking** and describes the complete vision for CCDA metrics. All components are specifications for future development.

The `/guides/` folder contains proof-of-concept documentation that informed these specifications.

---

## Design Principles

1. **Open Data Only** - No commercial APIs or paid data sources
2. **AI-Native** - GenAI agents for analysis, synthesis, and correlation
3. **PURL-Centric** - All packages identified by Package URL for SBOM compatibility
4. **Continuous Monitoring** - Real-time collection, not point-in-time snapshots

---

## Part 1: Data Source Registry

### 1.1 GitHub API

| Endpoint | Data Retrieved | Rate Limit | Auth Required |
|----------|----------------|------------|---------------|
| `GET /repos/{owner}/{repo}` | Basic repo info, stars, forks | 60/hr (unauth) 5000/hr (auth) | Optional |
| `GET /repos/{owner}/{repo}/commits` | Commit history, authors | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/contributors` | Contributor list + counts | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/issues` | Issues + comments | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/pulls` | Pull requests | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/releases` | Release history | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/contents/{path}` | File contents | 60/hr (unauth) | Optional |
| `GET /repos/{owner}/{repo}/branches/{branch}/protection` | Branch protection | 5000/hr | **Required** |
| `GET /users/{username}` | User profile, location, company | 60/hr (unauth) | Optional |

**Base URL:** `https://api.github.com`
**Auth Header:** `Authorization: Bearer {token}`

### 1.2 Vulnerability Databases

| Source | API Endpoint | Data | Rate Limit | Cost |
|--------|--------------|------|------------|------|
| **OSV** | `https://api.osv.dev/v1/query` | Vulnerabilities by package | Unlimited | Free |
| **NVD** | `https://services.nvd.nist.gov/rest/json/cves/2.0` | CVE details, CVSS | 5 req/30s (unauth) | Free |
| **GitHub Advisories** | `https://api.github.com/advisories` | GHSA advisories | 60/hr | Free |
| **EPSS** | `https://api.first.org/data/v1/epss` | Exploit probability | Unlimited | Free |

### 1.3 Package Registries

| Registry | API Endpoint | Data Retrieved |
|----------|--------------|----------------|
| **npm** | `https://registry.npmjs.org/{package}` | Package metadata, versions, repo URL |
| **PyPI** | `https://pypi.org/pypi/{package}/json` | Package metadata, versions, repo URL |
| **RubyGems** | `https://rubygems.org/api/v1/gems/{package}.json` | Gem metadata |
| **crates.io** | `https://crates.io/api/v1/crates/{package}` | Crate metadata |
| **Go Proxy** | `https://proxy.golang.org/{module}/@v/list` | Module versions |
| **Maven Central** | `https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}` | Artifact metadata |

### 1.4 Media Sources

| Source | Collection Method | Data Retrieved |
|--------|-------------------|----------------|
| **RSS Feeds** | feedparser library | Articles with title, link, description, date |
| **HackerNews** | Firebase API `https://hacker-news.firebaseio.com/v0/` | Stories, comments, scores |
| **Reddit** | `https://www.reddit.com/r/{sub}/new.json` | Posts, comments, scores |

---

## Part 2: Metric Specifications

### Category A: Repository Health Metrics

---

#### A.1 Commit Activity

**Description:** Measures development velocity and activity patterns.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/commits
Parameters: since={ISO8601_date}, per_page=100
```

**Calculation:**
```python
def calculate_commit_metrics(commits, lookback_days=30):
    authors = set()
    commit_dates = []

    for commit in commits:
        if commit.get('author'):
            authors.add(commit['author']['login'])
        commit_dates.append(parse_date(commit['commit']['author']['date']))

    return {
        'commit_count': len(commits),
        'unique_authors': len(authors),
        'commits_per_day': len(commits) / lookback_days,
        'commit_frequency': classify_frequency(len(commits) / lookback_days)
    }

def classify_frequency(cpd):
    if cpd >= 5: return 'very_high'
    if cpd >= 1: return 'high'
    if cpd >= 0.2: return 'moderate'
    if cpd >= 0.05: return 'low'
    return 'very_low'
```

**AI Agent:** None required (pure calculation)

**Output:**
```json
{
  "commit_count": 45,
  "unique_authors": 8,
  "commits_per_day": 1.5,
  "commit_frequency": "high"
}
```

---

#### A.2 Contributor Absence Factor (Bus Factor)

**Description:** Identifies dependency on small number of contributors (risk if they leave).

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/stats/contributors
```

**Calculation:**
```python
def calculate_bus_factor(contributors):
    """
    Bus factor = minimum contributors responsible for 50% of commits
    """
    total_commits = sum(c['total'] for c in contributors)
    target = total_commits * 0.5

    # Sort by contribution count descending
    sorted_contributors = sorted(contributors, key=lambda x: x['total'], reverse=True)

    cumulative = 0
    bus_factor = 0

    for contributor in sorted_contributors:
        cumulative += contributor['total']
        bus_factor += 1
        if cumulative >= target:
            break

    return {
        'bus_factor': bus_factor,
        'total_contributors': len(contributors),
        'top_contributor_percentage': (sorted_contributors[0]['total'] / total_commits) * 100,
        'risk_level': 'high' if bus_factor <= 2 else 'medium' if bus_factor <= 4 else 'low'
    }
```

**AI Agent:** None required (pure calculation)

**Output:**
```json
{
  "bus_factor": 2,
  "total_contributors": 45,
  "top_contributor_percentage": 35.2,
  "risk_level": "high"
}
```

---

#### A.3 Time to First Response

**Description:** Average time until first maintainer response on issues.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100
GET https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments
```

**Calculation:**
```python
def calculate_time_to_first_response(issues, repo_owner):
    response_times = []

    for issue in issues:
        if issue.get('pull_request'):
            continue  # Skip PRs

        created_at = parse_date(issue['created_at'])
        issue_author = issue['user']['login']

        # Get comments
        comments = fetch_comments(issue['comments_url'])

        for comment in comments:
            commenter = comment['user']['login']
            # First response from someone other than issue author
            if commenter != issue_author:
                response_at = parse_date(comment['created_at'])
                response_time = (response_at - created_at).total_seconds() / 3600  # hours
                response_times.append(response_time)
                break

    if not response_times:
        return {'avg_hours': None, 'median_hours': None}

    return {
        'avg_hours': sum(response_times) / len(response_times),
        'median_hours': median(response_times),
        'issues_sampled': len(response_times),
        'responsiveness': classify_responsiveness(median(response_times))
    }

def classify_responsiveness(median_hours):
    if median_hours <= 24: return 'excellent'
    if median_hours <= 72: return 'good'
    if median_hours <= 168: return 'moderate'
    return 'slow'
```

**AI Agent:** None required (pure calculation)

**Output:**
```json
{
  "avg_hours": 18.5,
  "median_hours": 12.3,
  "issues_sampled": 50,
  "responsiveness": "excellent"
}
```

---

#### A.4 Time to Close

**Description:** Average time from issue creation to closure.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/issues?state=closed&per_page=100
```

**Calculation:**
```python
def calculate_time_to_close(closed_issues):
    close_times = []

    for issue in closed_issues:
        if issue.get('pull_request'):
            continue

        created_at = parse_date(issue['created_at'])
        closed_at = parse_date(issue['closed_at'])

        close_time_days = (closed_at - created_at).days
        close_times.append(close_time_days)

    return {
        'avg_days': sum(close_times) / len(close_times),
        'median_days': median(close_times),
        'p90_days': percentile(close_times, 90),
        'issues_sampled': len(close_times)
    }
```

**AI Agent:** None required

**Output:**
```json
{
  "avg_days": 14.2,
  "median_days": 7,
  "p90_days": 45,
  "issues_sampled": 100
}
```

---

#### A.5 PR Merge Time

**Description:** Time from PR creation to merge.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&per_page=100
```

**Calculation:**
```python
def calculate_pr_merge_time(closed_prs):
    merge_times = []

    for pr in closed_prs:
        if not pr.get('merged_at'):
            continue  # Skip closed-but-not-merged

        created_at = parse_date(pr['created_at'])
        merged_at = parse_date(pr['merged_at'])

        merge_time_hours = (merged_at - created_at).total_seconds() / 3600
        merge_times.append(merge_time_hours)

    return {
        'avg_hours': sum(merge_times) / len(merge_times),
        'median_hours': median(merge_times),
        'prs_sampled': len(merge_times),
        'velocity': classify_merge_velocity(median(merge_times))
    }

def classify_merge_velocity(median_hours):
    if median_hours <= 24: return 'fast'
    if median_hours <= 72: return 'moderate'
    if median_hours <= 168: return 'slow'
    return 'very_slow'
```

**AI Agent:** None required

**Output:**
```json
{
  "avg_hours": 36.5,
  "median_hours": 24.0,
  "prs_sampled": 75,
  "velocity": "fast"
}
```

---

#### A.6 Review Turnaround Time

**Description:** Time from review request to review submission.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/pulls/{number}/reviews
GET https://api.github.com/repos/{owner}/{repo}/pulls/{number}/requested_reviewers
```

**Calculation:**
```python
def calculate_review_turnaround(pr, reviews):
    # Get PR creation time (proxy for review request if no explicit request)
    pr_created = parse_date(pr['created_at'])

    review_times = []
    for review in reviews:
        if review['state'] in ['APPROVED', 'CHANGES_REQUESTED', 'COMMENTED']:
            review_submitted = parse_date(review['submitted_at'])
            turnaround = (review_submitted - pr_created).total_seconds() / 3600
            review_times.append(turnaround)
            break  # First review only

    return review_times
```

**AI Agent:** None required

---

#### A.7 Contributor Retention Rate

**Description:** Percentage of contributors active in previous period who remain active.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/commits?since={6_months_ago}&until={3_months_ago}
GET https://api.github.com/repos/{owner}/{repo}/commits?since={3_months_ago}
```

**Calculation:**
```python
def calculate_retention(period1_commits, period2_commits):
    period1_authors = set(c['author']['login'] for c in period1_commits if c.get('author'))
    period2_authors = set(c['author']['login'] for c in period2_commits if c.get('author'))

    retained = period1_authors.intersection(period2_authors)

    if not period1_authors:
        return {'retention_rate': None}

    return {
        'period1_contributors': len(period1_authors),
        'period2_contributors': len(period2_authors),
        'retained_contributors': len(retained),
        'retention_rate': len(retained) / len(period1_authors),
        'new_contributors': len(period2_authors - period1_authors),
        'churned_contributors': len(period1_authors - period2_authors)
    }
```

**AI Agent:** None required

**Output:**
```json
{
  "period1_contributors": 20,
  "period2_contributors": 18,
  "retained_contributors": 12,
  "retention_rate": 0.6,
  "new_contributors": 6,
  "churned_contributors": 8
}
```

---

#### A.8 New Contributor Rate

**Description:** Rate of new contributors joining the project.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/stats/contributors
```

**Calculation:**
```python
def calculate_new_contributor_rate(contributors, months=6):
    cutoff_date = datetime.now() - timedelta(days=months*30)

    new_contributors = []
    for contributor in contributors:
        # Find first contribution week
        weeks = contributor.get('weeks', [])
        for week in weeks:
            if week['c'] > 0:  # Has commits
                week_date = datetime.fromtimestamp(week['w'])
                if week_date >= cutoff_date:
                    new_contributors.append(contributor['author']['login'])
                break

    return {
        'new_contributors_count': len(new_contributors),
        'new_contributors_per_month': len(new_contributors) / months,
        'total_contributors': len(contributors),
        'growth_rate': len(new_contributors) / len(contributors) if contributors else 0
    }
```

**AI Agent:** None required

---

#### A.9 Geographic Diversity

**Description:** Distribution of contributors across timezones/regions.

**Data Source:**
```
GET https://api.github.com/users/{username}
Fields: location, company
```

**Calculation + AI:**
```python
def analyze_geographic_diversity(contributors):
    locations = []

    for contributor in contributors:
        user_data = fetch_user(contributor['login'])
        if user_data.get('location'):
            locations.append(user_data['location'])

    # Use AI to normalize and classify locations
    return ai_classify_locations(locations)
```

**AI Agent:** `LocationClassifierAgent`
- **Type:** Classification Agent
- **Model:** Small LLM (e.g., llama3-8b, gpt-4o-mini)
- **Prompt:**
```
Given these contributor locations, classify each into a region and timezone.
Return a summary of geographic distribution.

Locations: {locations}

Return JSON:
{
  "regions": {"North America": 10, "Europe": 5, "Asia": 3},
  "timezones": {"UTC-8 to UTC-5": 10, "UTC-1 to UTC+2": 5, "UTC+5 to UTC+9": 3},
  "diversity_score": 0.7,  // 0-1, higher = more diverse
  "single_region_risk": false
}
```

**Output:**
```json
{
  "regions": {"North America": 10, "Europe": 5, "Asia": 3},
  "diversity_score": 0.7,
  "single_region_risk": false,
  "contributors_with_location": 18,
  "contributors_without_location": 27
}
```

---

### Category B: Security Metrics

---

#### B.1 Known Vulnerabilities (CVE/GHSA)

**Description:** Known vulnerabilities affecting the package.

**Data Sources:**

**OSV API:**
```
POST https://api.osv.dev/v1/query
Body: {"package": {"name": "lodash", "ecosystem": "npm"}}
```

**NVD API:**
```
GET https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={package}
```

**GitHub Advisories:**
```
GET https://api.github.com/advisories?affects={package}
```

**Calculation:**
```python
def get_vulnerabilities(package_name, ecosystem):
    # Query OSV
    osv_response = requests.post(
        'https://api.osv.dev/v1/query',
        json={'package': {'name': package_name, 'ecosystem': ecosystem}}
    )
    vulns = osv_response.json().get('vulns', [])

    results = []
    for vuln in vulns:
        results.append({
            'id': vuln['id'],
            'summary': vuln.get('summary'),
            'severity': extract_severity(vuln),
            'fixed_versions': extract_fixed_versions(vuln),
            'published': vuln.get('published'),
            'aliases': vuln.get('aliases', [])  # CVE IDs
        })

    return {
        'total_vulnerabilities': len(results),
        'critical': len([v for v in results if v['severity'] == 'CRITICAL']),
        'high': len([v for v in results if v['severity'] == 'HIGH']),
        'medium': len([v for v in results if v['severity'] == 'MEDIUM']),
        'low': len([v for v in results if v['severity'] == 'LOW']),
        'vulnerabilities': results
    }
```

**AI Agent:** `VulnerabilityCorrelationAgent`
- **Type:** Correlation Agent
- **Role:** Match detected packages from media to vulnerability databases
- **Prompt:**
```
Given this news article about a security issue and the OSV/NVD data,
correlate the mentioned vulnerability with official CVE records.

Article: {article_text}
Package: {package_name}
OSV Data: {osv_data}

Return:
{
  "cve_ids": ["CVE-2024-1234"],
  "affected_versions": "<2.1.5",
  "severity": "CRITICAL",
  "exploitation_status": "PoC available",
  "correlation_confidence": "high"
}
```

---

#### B.2 CVSS Scores

**Description:** Standardized vulnerability severity scores.

**Data Source:**
```
GET https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={CVE-ID}
```

**Calculation:**
```python
def get_cvss_score(cve_id):
    response = requests.get(
        f'https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}'
    )
    cve_data = response.json()

    if not cve_data.get('vulnerabilities'):
        return None

    vuln = cve_data['vulnerabilities'][0]['cve']
    metrics = vuln.get('metrics', {})

    # Try CVSS 3.1, then 3.0, then 2.0
    if 'cvssMetricV31' in metrics:
        cvss = metrics['cvssMetricV31'][0]['cvssData']
    elif 'cvssMetricV30' in metrics:
        cvss = metrics['cvssMetricV30'][0]['cvssData']
    elif 'cvssMetricV2' in metrics:
        cvss = metrics['cvssMetricV2'][0]['cvssData']
    else:
        return None

    return {
        'base_score': cvss['baseScore'],
        'severity': cvss.get('baseSeverity'),
        'vector_string': cvss['vectorString'],
        'attack_vector': cvss.get('attackVector'),
        'attack_complexity': cvss.get('attackComplexity'),
        'privileges_required': cvss.get('privilegesRequired'),
        'user_interaction': cvss.get('userInteraction')
    }
```

**AI Agent:** None required (structured data)

---

#### B.3 Exploit Probability (EPSS)

**Description:** Probability that vulnerability will be exploited in the wild.

**Data Source:**
```
GET https://api.first.org/data/v1/epss?cve={CVE-ID}
```

**Calculation:**
```python
def get_epss_score(cve_id):
    response = requests.get(f'https://api.first.org/data/v1/epss?cve={cve_id}')
    data = response.json()

    if data.get('data'):
        epss = data['data'][0]
        return {
            'epss_score': float(epss['epss']),
            'percentile': float(epss['percentile']),
            'date': epss['date']
        }
    return None
```

**AI Agent:** None required

---

#### B.4 Exploit Status Detection

**Description:** Detect if PoC or in-the-wild exploits exist.

**Data Sources:**
- GitHub search for PoC repositories
- Security RSS feeds (The Register, Ars Technica, etc.)
- Exploit-DB

**GitHub PoC Search:**
```
GET https://api.github.com/search/repositories?q={CVE-ID}+poc+exploit
```

**Calculation + AI:**
```python
def detect_exploit_status(cve_id, media_articles):
    # Search GitHub for PoC
    poc_repos = search_github_poc(cve_id)

    # Check media for exploitation reports
    exploitation_mentions = search_media_for_exploitation(cve_id, media_articles)

    return ai_analyze_exploit_status(cve_id, poc_repos, exploitation_mentions)
```

**AI Agent:** `ExploitIntelligenceAgent`
- **Type:** Analysis Agent
- **Model:** Medium LLM (llama3-70b, gpt-4o)
- **Prompt:**
```
Analyze the exploit status for {cve_id}.

GitHub PoC repositories found: {poc_repos}
Media mentions: {media_articles}

Determine:
1. Is a proof-of-concept publicly available?
2. Is there evidence of in-the-wild exploitation?
3. How sophisticated is the exploit (trivial/moderate/complex)?

Return JSON:
{
  "poc_available": true,
  "poc_urls": ["https://github.com/..."],
  "in_the_wild": false,
  "exploitation_evidence": "PoC published on GitHub, no ITW reports",
  "exploit_complexity": "trivial",
  "urgency": "high"
}
```

---

#### B.5 Security Policy Detection

**Description:** Check if repository has SECURITY.md with disclosure process.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/contents/SECURITY.md
GET https://api.github.com/repos/{owner}/{repo}/contents/.github/SECURITY.md
```

**Calculation + AI:**
```python
def analyze_security_policy(repo):
    # Try to fetch SECURITY.md
    for path in ['SECURITY.md', '.github/SECURITY.md']:
        response = fetch_file(repo, path)
        if response:
            return ai_analyze_security_policy(response['content'])

    return {'has_security_policy': False}
```

**AI Agent:** `SecurityPolicyAnalyzerAgent`
- **Type:** Document Analysis Agent
- **Model:** Small LLM
- **Prompt:**
```
Analyze this SECURITY.md file and extract:
1. Does it describe a vulnerability reporting process?
2. Is there a security contact (email, form, etc.)?
3. Is there a bug bounty program?
4. What is the expected response time?

SECURITY.md content:
{content}

Return JSON:
{
  "has_disclosure_process": true,
  "security_contact": "security@example.com",
  "bug_bounty": false,
  "response_time_sla": "48 hours",
  "policy_quality": "good"
}
```

---

#### B.6 Branch Protection Status

**Description:** Check if main branch has protection rules.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection
Requires: Admin token or repo with public branch protection
```

**Calculation:**
```python
def check_branch_protection(owner, repo, branch='main'):
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code == 404:
        return {'protected': False, 'reason': 'No protection rules'}

    protection = response.json()

    return {
        'protected': True,
        'require_pr': protection.get('required_pull_request_reviews') is not None,
        'require_reviews': protection.get('required_pull_request_reviews', {}).get('required_approving_review_count', 0),
        'require_status_checks': protection.get('required_status_checks') is not None,
        'enforce_admins': protection.get('enforce_admins', {}).get('enabled', False),
        'require_signatures': protection.get('required_signatures', {}).get('enabled', False)
    }
```

**AI Agent:** None required

---

#### B.7 Signed Releases

**Description:** Check if releases are cryptographically signed.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/releases
```

**Calculation:**
```python
def check_signed_releases(owner, repo):
    releases = fetch_releases(owner, repo)

    signed_count = 0
    for release in releases[:10]:  # Check last 10
        assets = release.get('assets', [])

        # Look for signature files
        has_sig = any(
            a['name'].endswith(('.sig', '.asc', '.sign', '.sha256'))
            for a in assets
        )
        if has_sig:
            signed_count += 1

    return {
        'releases_checked': min(10, len(releases)),
        'signed_releases': signed_count,
        'signing_rate': signed_count / min(10, len(releases)) if releases else 0,
        'has_signing': signed_count > 0
    }
```

**AI Agent:** None required

---

### Category C: Dependency & Supply Chain Metrics

---

#### C.1 Dependency Update Tool Detection

**Description:** Check if automated dependency updates are configured.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/contents/.github/dependabot.yml
GET https://api.github.com/repos/{owner}/{repo}/contents/renovate.json
```

**Calculation:**
```python
def detect_dependency_tools(owner, repo):
    tools_found = []

    # Check Dependabot
    dependabot = fetch_file(owner, repo, '.github/dependabot.yml')
    if dependabot:
        tools_found.append('dependabot')

    # Check Renovate
    for path in ['renovate.json', '.renovaterc', '.renovaterc.json']:
        if fetch_file(owner, repo, path):
            tools_found.append('renovate')
            break

    return {
        'has_dependency_updates': len(tools_found) > 0,
        'tools': tools_found
    }
```

**AI Agent:** None required

---

#### C.2 Pinned Dependencies

**Description:** Check if dependencies are pinned to specific versions.

**Data Source:**
```
GET https://api.github.com/repos/{owner}/{repo}/contents/package-lock.json
GET https://api.github.com/repos/{owner}/{repo}/contents/yarn.lock
GET https://api.github.com/repos/{owner}/{repo}/contents/Pipfile.lock
GET https://api.github.com/repos/{owner}/{repo}/contents/poetry.lock
GET https://api.github.com/repos/{owner}/{repo}/contents/Gemfile.lock
GET https://api.github.com/repos/{owner}/{repo}/contents/go.sum
GET https://api.github.com/repos/{owner}/{repo}/contents/Cargo.lock
```

**Calculation:**
```python
def check_pinned_dependencies(owner, repo, language):
    lockfiles = {
        'javascript': ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
        'python': ['Pipfile.lock', 'poetry.lock', 'requirements.txt'],
        'ruby': ['Gemfile.lock'],
        'go': ['go.sum'],
        'rust': ['Cargo.lock']
    }

    files_to_check = lockfiles.get(language.lower(), [])
    found_lockfiles = []

    for lockfile in files_to_check:
        if fetch_file(owner, repo, lockfile):
            found_lockfiles.append(lockfile)

    return {
        'has_lockfile': len(found_lockfiles) > 0,
        'lockfiles_found': found_lockfiles,
        'pinned': len(found_lockfiles) > 0
    }
```

**AI Agent:** None required

---

### Category D: Media & Sentiment Analysis

---

#### D.1 Risk Detection from Media

**Description:** AI-powered detection of business continuity risks from news articles.

**Data Sources:**
- RSS feeds (16+ security/tech sources)
- HackerNews API
- Reddit API

**AI Agent:** `RiskRelevanceAgent` (Existing)
- **Type:** Classification Agent
- **Model:** Medium LLM (llama3-70b, gpt-4o)
- **Prompt:**
```
Analyze this article for OSS business/operational risks.

Risk categories:
- security: Vulnerabilities, CVEs, breaches
- legal: License changes, lawsuits
- acquisition: Mergers, buyouts
- governance: Leadership changes, disputes
- deprecation: EOL, abandonment
- maintainer: Burnout, reduced activity
- funding: Sponsorship changes
- fork: Community splits
- supply_chain: Dependency issues
- breaking_change: API incompatibilities

Article:
{article_text}

Return JSON:
{
  "is_relevant": true,
  "risk_categories": ["security", "supply_chain"],
  "severity": "critical",
  "affected_packages": ["log4j"],
  "risk_summary": "Critical RCE vulnerability discovered",
  "risk_score": 0.95
}
```

**Output:**
```json
{
  "is_relevant": true,
  "risk_categories": ["security", "supply_chain"],
  "severity": "critical",
  "risk_score": 0.95,
  "affected_packages": ["log4j"],
  "risk_summary": "Critical RCE vulnerability allows remote code execution"
}
```

---

#### D.2 Sentiment Analysis

**Description:** Determine positive/negative impact on OSS ecosystem.

**AI Agent:** `SentimentAnalyzerAgent` (Existing)
- **Type:** Classification Agent
- **Model:** Small LLM
- **Prompt:**
```
Analyze sentiment/polarity for open source ecosystem.

POSITIVE: Open sourcing, funding, new maintainers, performance improvements
NEGATIVE: Abandonment, vulnerabilities, license restrictions, maintainer burnout
NEUTRAL: Tutorials, minor updates, general discussions

Article:
{article_text}

Return JSON:
{
  "polarity": "negative",
  "confidence": "high",
  "impact_level": "critical",
  "sentiment_score": -0.85,
  "factors": ["critical vulnerability", "active exploitation"]
}
```

---

#### D.3 Package Identification from Text

**Description:** Extract OSS package mentions from unstructured text.

**AI Agent:** `PackageIdentifierAgent` (Existing)
- **Type:** Extraction Agent
- **Model:** Medium LLM
- **Prompt:**
```
Extract OSS packages mentioned in this text.

Supported ecosystems: npm, pypi, gem, crates, go, maven, nuget, packagist, cocoapods, hex

Text:
{article_text}

Return JSON:
{
  "packages": [
    {
      "name": "log4j",
      "ecosystem": "maven",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core",
      "confidence": "high",
      "context": "vulnerability mentioned"
    }
  ],
  "classification": "security-related"
}
```

---

### Category E: Advisory Generation

---

#### E.1 Remediation Synthesis

**Description:** Generate fix recommendations from changelogs and commits.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/releases
GET https://api.github.com/repos/{owner}/{repo}/contents/CHANGELOG.md
GET https://api.github.com/repos/{owner}/{repo}/commits?sha={tag}
```

**AI Agent:** `RemediationGeneratorAgent`
- **Type:** Synthesis Agent
- **Model:** Large LLM (llama3-70b, gpt-4o, claude-3)
- **Prompt:**
```
Generate remediation guidance for this vulnerability.

Vulnerability: {cve_id} - {summary}
Affected package: {package_name}
Affected versions: {affected_versions}

Available data:
- Release notes: {release_notes}
- Changelog entries: {changelog}
- Commit messages: {commits}
- GitHub issue discussions: {discussions}

Generate:
1. Primary fix (upgrade command)
2. Workaround if upgrade not possible
3. Detection method
4. Risk if unpatched

Return JSON:
{
  "primary_fix": {
    "action": "upgrade",
    "target_version": "2.17.0",
    "command": "npm install log4j@2.17.0",
    "breaking_changes": false
  },
  "workarounds": [
    {
      "description": "Set log4j2.formatMsgNoLookups=true",
      "effectiveness": "partial",
      "instructions": "Add -Dlog4j2.formatMsgNoLookups=true to JVM args"
    }
  ],
  "detection": "Check for log4j-core < 2.17.0 in dependencies",
  "unpatched_risk": "Remote code execution possible"
}
```

---

#### E.2 Attack Vector Summary

**Description:** Generate human-readable attack vector description.

**AI Agent:** `AttackVectorSummarizerAgent`
- **Type:** Summarization Agent
- **Model:** Small LLM
- **Prompt:**
```
Summarize this vulnerability's attack vector for a non-technical audience.

CVE: {cve_id}
CVSS Vector: {cvss_vector}
Technical description: {description}

Return JSON:
{
  "attack_summary": "An attacker can execute code remotely without authentication",
  "requires_user_action": false,
  "network_exploitable": true,
  "complexity": "low",
  "business_impact": "Complete system compromise possible"
}
```

---

#### E.3 Affected Version Range Detection

**Description:** Determine which versions are affected.

**Data Sources:**
- OSV API (has structured version ranges)
- Package registry APIs
- GitHub releases

**Calculation + AI:**
```python
def get_affected_versions(package, ecosystem, vuln_id):
    # Get from OSV first (structured data)
    osv_data = query_osv(package, ecosystem)

    for vuln in osv_data.get('vulns', []):
        if vuln['id'] == vuln_id or vuln_id in vuln.get('aliases', []):
            affected = vuln.get('affected', [])
            for a in affected:
                ranges = a.get('ranges', [])
                versions = a.get('versions', [])
                return {
                    'ranges': ranges,
                    'specific_versions': versions,
                    'fixed_version': extract_fixed(ranges)
                }

    # Fallback: AI extraction from advisory text
    return ai_extract_versions(advisory_text)
```

---

### Category F: Maintainer & Account Metrics

---

#### F.1 Maintainer Discovery

**Description:** Identify maintainers and contributors for packages in the SBOM.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/contributors
GET https://api.github.com/repos/{owner}/{repo}/collaborators  # Requires admin access
GET https://registry.npmjs.org/{package}  # maintainers field
GET https://pypi.org/pypi/{package}/json  # info.maintainer, info.author
```

**Calculation:**
```python
def discover_maintainers(purl: str) -> list[Maintainer]:
    """
    Build a list of maintainers for a package from multiple sources.
    """
    maintainers = []

    # 1. From package registry (npm, PyPI, etc.)
    registry_maintainers = get_registry_maintainers(purl)
    maintainers.extend(registry_maintainers)

    # 2. From GitHub repo (if linked)
    repo = resolve_github_repo(purl)
    if repo:
        # Top contributors by commit count
        contributors = fetch_contributors(repo)
        for c in contributors[:10]:  # Top 10
            maintainers.append({
                'username': c['login'],
                'platform': 'github',
                'role': 'contributor',
                'contributions': c['contributions']
            })

        # Repo owner/org
        owner = get_repo_owner(repo)
        maintainers.append({
            'username': owner['login'],
            'platform': 'github',
            'role': 'owner',
            'type': owner['type']  # 'User' or 'Organization'
        })

    return deduplicate_maintainers(maintainers)
```

**Output:**
```json
{
  "package": "pkg:npm/lodash",
  "maintainers": [
    {
      "username": "jdalton",
      "platform": "github",
      "role": "owner",
      "contributions": 5420,
      "first_contribution": "2012-04-01",
      "last_contribution": "2024-12-01"
    },
    {
      "username": "bnjmnt4n",
      "platform": "github",
      "role": "contributor",
      "contributions": 89
    }
  ],
  "registry_maintainers": ["jdalton", "mathias"]
}
```

---

#### F.2 Maintainer Activity Tracking

**Description:** Track activity levels of maintainers over time to detect inactivity or burnout.

**Data Sources:**
```
GET https://api.github.com/users/{username}/events/public
GET https://api.github.com/search/commits?q=author:{username}+repo:{owner}/{repo}
GET https://api.github.com/repos/{owner}/{repo}/commits?author={username}&since={date}
```

**Calculation:**
```python
def track_maintainer_activity(username: str, repos: list[str], lookback_days: int = 90):
    """
    Track maintainer activity across their maintained repositories.
    """
    activity = {
        'username': username,
        'period_start': (datetime.now() - timedelta(days=lookback_days)).isoformat(),
        'period_end': datetime.now().isoformat(),
        'commits': 0,
        'prs_merged': 0,
        'prs_reviewed': 0,
        'issues_responded': 0,
        'releases_published': 0,
        'last_activity': None,
        'active_days': set()
    }

    # Fetch public events (last 90 days, max 300 events)
    events = fetch_user_events(username)

    for event in events:
        event_date = parse_date(event['created_at'])
        activity['active_days'].add(event_date.date())

        if activity['last_activity'] is None:
            activity['last_activity'] = event_date

        if event['type'] == 'PushEvent':
            activity['commits'] += len(event['payload'].get('commits', []))
        elif event['type'] == 'PullRequestEvent':
            if event['payload']['action'] == 'closed' and event['payload']['pull_request']['merged']:
                activity['prs_merged'] += 1
        elif event['type'] == 'PullRequestReviewEvent':
            activity['prs_reviewed'] += 1
        elif event['type'] == 'IssueCommentEvent':
            activity['issues_responded'] += 1
        elif event['type'] == 'ReleaseEvent':
            activity['releases_published'] += 1

    activity['active_days_count'] = len(activity['active_days'])
    activity['activity_score'] = calculate_activity_score(activity)
    activity['status'] = classify_activity_status(activity)

    return activity

def classify_activity_status(activity):
    days_since_last = (datetime.now() - activity['last_activity']).days if activity['last_activity'] else 999

    if days_since_last <= 7:
        return 'active'
    elif days_since_last <= 30:
        return 'recently_active'
    elif days_since_last <= 90:
        return 'reduced_activity'
    elif days_since_last <= 180:
        return 'low_activity'
    else:
        return 'inactive'
```

**Output:**
```json
{
  "username": "jdalton",
  "period": "2024-09-15 to 2024-12-15",
  "commits": 23,
  "prs_merged": 5,
  "prs_reviewed": 12,
  "issues_responded": 34,
  "releases_published": 2,
  "active_days_count": 45,
  "last_activity": "2024-12-10T14:30:00Z",
  "activity_score": 0.78,
  "status": "active"
}
```

---

#### F.3 Access Level Detection

**Description:** Determine what access level maintainers have to a repository.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/collaborators  # Requires push access
GET https://api.github.com/orgs/{org}/members                  # Requires org membership
GET https://api.github.com/repos/{owner}/{repo}/teams          # Requires admin access
```

**Note:** Access level detection requires elevated permissions. For public repos without admin access, we infer from observable signals.

**Calculation:**
```python
def detect_access_levels(repo: str, known_maintainers: list[str]):
    """
    Detect or infer access levels for maintainers.
    """
    owner, repo_name = parse_repo(repo)
    access_levels = {}

    # 1. Repo owner always has admin
    access_levels[owner] = {
        'level': 'admin',
        'source': 'owner',
        'confidence': 'high'
    }

    # 2. Try to fetch collaborators (may fail without access)
    try:
        collaborators = fetch_collaborators(repo)
        for collab in collaborators:
            access_levels[collab['login']] = {
                'level': collab['permissions'],  # admin, push, pull
                'source': 'api',
                'confidence': 'high'
            }
    except PermissionError:
        # 3. Infer from observable behavior
        for username in known_maintainers:
            inferred = infer_access_level(repo, username)
            access_levels[username] = {
                'level': inferred,
                'source': 'inferred',
                'confidence': 'medium'
            }

    return access_levels

def infer_access_level(repo: str, username: str):
    """
    Infer access level from observable actions.
    """
    # Check if user has merged PRs (requires write access)
    merged_prs = search_merged_prs_by_user(repo, username)
    if merged_prs:
        return 'write'

    # Check if user has pushed directly to main
    main_commits = search_commits_on_main(repo, username)
    if main_commits:
        return 'write'

    # Check if user is in CODEOWNERS
    codeowners = fetch_codeowners(repo)
    if username in codeowners:
        return 'write'  # CODEOWNERS typically have write access

    # Check if user has created releases
    releases = fetch_releases_by_user(repo, username)
    if releases:
        return 'write'

    return 'unknown'
```

**Output:**
```json
{
  "repository": "lodash/lodash",
  "access_levels": {
    "jdalton": {
      "level": "admin",
      "source": "owner",
      "confidence": "high",
      "can_merge": true,
      "can_release": true,
      "can_admin": true
    },
    "bnjmnt4n": {
      "level": "write",
      "source": "inferred",
      "confidence": "medium",
      "evidence": ["merged_prs", "direct_commits"]
    }
  }
}
```

---

#### F.4 Account Age and Reputation

**Description:** Assess account age, history, and reputation signals.

**Data Sources:**
```
GET https://api.github.com/users/{username}
```

**Calculation:**
```python
def assess_account_reputation(username: str):
    """
    Gather reputation signals for a GitHub account.
    """
    user = fetch_user(username)

    account_age_days = (datetime.now() - parse_date(user['created_at'])).days

    reputation = {
        'username': username,
        'account_created': user['created_at'],
        'account_age_days': account_age_days,
        'account_age_years': round(account_age_days / 365, 1),

        # Public signals
        'public_repos': user['public_repos'],
        'public_gists': user['public_gists'],
        'followers': user['followers'],
        'following': user['following'],

        # Profile completeness
        'has_name': bool(user.get('name')),
        'has_company': bool(user.get('company')),
        'has_location': bool(user.get('location')),
        'has_bio': bool(user.get('bio')),
        'has_blog': bool(user.get('blog')),
        'has_twitter': bool(user.get('twitter_username')),
        'hireable': user.get('hireable'),

        # Account type
        'type': user['type'],  # 'User' or 'Organization'
        'is_site_admin': user.get('site_admin', False)
    }

    # Calculate reputation score
    reputation['profile_completeness'] = calculate_profile_completeness(reputation)
    reputation['reputation_score'] = calculate_reputation_score(reputation)
    reputation['risk_signals'] = detect_risk_signals(reputation)

    return reputation

def detect_risk_signals(reputation):
    """
    Detect potential risk signals that might indicate account issues.
    """
    signals = []

    # New account with maintainer access
    if reputation['account_age_days'] < 90:
        signals.append({
            'type': 'new_account',
            'severity': 'medium',
            'description': f"Account is only {reputation['account_age_days']} days old"
        })

    # Empty profile
    if reputation['profile_completeness'] < 0.3:
        signals.append({
            'type': 'sparse_profile',
            'severity': 'low',
            'description': 'Profile has minimal information'
        })

    # Low follower count for maintainer role
    if reputation['followers'] < 5 and reputation['public_repos'] > 0:
        signals.append({
            'type': 'low_visibility',
            'severity': 'low',
            'description': 'Low follower count relative to activity'
        })

    # Suspicious follower/following ratio (potential bot)
    if reputation['following'] > 1000 and reputation['followers'] < 10:
        signals.append({
            'type': 'suspicious_ratio',
            'severity': 'medium',
            'description': 'Unusual following/followers ratio'
        })

    return signals
```

**Output:**
```json
{
  "username": "jdalton",
  "account_created": "2008-03-15T00:00:00Z",
  "account_age_years": 16.8,
  "public_repos": 156,
  "followers": 5420,
  "profile_completeness": 0.95,
  "reputation_score": 0.92,
  "risk_signals": []
}
```

---

#### F.5 Account Compromise Detection

**Description:** Detect anomalous behavior that might indicate account compromise.

**Data Sources:**
```
GET https://api.github.com/users/{username}/events/public
GET https://api.github.com/repos/{owner}/{repo}/commits?author={username}
```

**AI Agent:** `AccountAnomalyDetectorAgent`
- **Type:** Anomaly Detection Agent
- **Model:** Medium LLM
- **Prompt:**
```
Analyze this GitHub account's recent activity for signs of compromise.

Account: {username}
Account age: {account_age}
Normal activity pattern: {baseline_activity}

Recent activity (last 7 days):
{recent_events}

Recent commits:
{recent_commits}

Look for:
1. Sudden spike in commit frequency
2. Commits to unusual repositories
3. Commits with obfuscated or suspicious code
4. Unusual commit times (different timezone)
5. Bulk changes to CI/CD configurations
6. Addition of new maintainers/collaborators
7. Changes to package publishing scripts
8. Removal of security features

Return JSON:
{
  "anomaly_detected": false,
  "confidence": "high",
  "anomalies": [],
  "risk_level": "low",
  "recommended_actions": []
}
```

**Calculation:**
```python
def detect_account_compromise(username: str, baseline: dict):
    """
    Compare recent activity against baseline to detect anomalies.
    """
    recent_events = fetch_recent_events(username, days=7)
    recent_commits = fetch_recent_commits(username, days=7)

    anomalies = []

    # 1. Commit frequency anomaly
    recent_commit_rate = len(recent_commits) / 7
    baseline_commit_rate = baseline.get('avg_commits_per_day', 1)
    if recent_commit_rate > baseline_commit_rate * 5:
        anomalies.append({
            'type': 'commit_spike',
            'severity': 'medium',
            'details': f'{recent_commit_rate:.1f} commits/day vs baseline {baseline_commit_rate:.1f}'
        })

    # 2. New repository access
    recent_repos = set(e['repo']['name'] for e in recent_events if 'repo' in e)
    baseline_repos = set(baseline.get('active_repos', []))
    new_repos = recent_repos - baseline_repos
    if new_repos:
        anomalies.append({
            'type': 'new_repo_access',
            'severity': 'low',
            'details': f'Activity in new repos: {list(new_repos)[:5]}'
        })

    # 3. Suspicious file changes (CI/CD, package configs)
    sensitive_files = ['.github/workflows/', 'package.json', 'setup.py',
                       '.npmrc', '.pypirc', 'Gemfile', 'Cargo.toml']
    sensitive_changes = []
    for commit in recent_commits:
        files = fetch_commit_files(commit['sha'])
        for f in files:
            if any(s in f['filename'] for s in sensitive_files):
                sensitive_changes.append(f['filename'])

    if sensitive_changes:
        anomalies.append({
            'type': 'sensitive_file_changes',
            'severity': 'high',
            'details': f'Changes to: {sensitive_changes[:10]}'
        })

    # 4. AI analysis for subtle patterns
    if anomalies or len(recent_commits) > 10:
        ai_analysis = ai_analyze_account_behavior(username, recent_events, recent_commits, baseline)
        anomalies.extend(ai_analysis.get('anomalies', []))

    return {
        'username': username,
        'analyzed_period': '7 days',
        'anomalies': anomalies,
        'risk_level': max((a['severity'] for a in anomalies), default='none'),
        'requires_review': len([a for a in anomalies if a['severity'] in ['high', 'critical']]) > 0
    }
```

**Output:**
```json
{
  "username": "maintainer123",
  "analyzed_period": "7 days",
  "anomalies": [
    {
      "type": "sensitive_file_changes",
      "severity": "high",
      "details": "Changes to: ['.github/workflows/publish.yml', 'package.json']"
    },
    {
      "type": "commit_spike",
      "severity": "medium",
      "details": "15.2 commits/day vs baseline 0.8"
    }
  ],
  "risk_level": "high",
  "requires_review": true,
  "recommended_actions": [
    "Review recent commits to publish workflow",
    "Verify with maintainer through secondary channel",
    "Check if 2FA is enabled on account"
  ]
}
```

---

#### F.6 Watchlist Management

**Description:** Maintain a watchlist of accounts to monitor across SBOM packages.

**Data Model:**
```json
{
  "watchlist": [
    {
      "username": "jdalton",
      "platform": "github",
      "reason": "maintainer",
      "packages": ["pkg:npm/lodash", "pkg:npm/lodash-es"],
      "added_at": "2024-01-15",
      "monitoring_level": "standard",
      "baseline": {
        "avg_commits_per_day": 0.8,
        "active_repos": ["lodash/lodash"],
        "typical_activity_hours": "09:00-18:00 UTC-6",
        "last_updated": "2024-12-01"
      },
      "alerts": []
    }
  ],
  "settings": {
    "auto_add_maintainers": true,
    "monitoring_frequency": "daily",
    "alert_on_inactivity_days": 90,
    "alert_on_new_maintainer": true
  }
}
```

**Watchlist Operations:**
```python
class MaintainerWatchlist:
    def __init__(self):
        self.watchlist = load_watchlist()

    def add_from_sbom(self, sbom_path: str):
        """
        Automatically add maintainers for all SBOM packages.
        """
        purls = extract_purls(sbom_path)
        for purl in purls:
            maintainers = discover_maintainers(purl)
            for m in maintainers:
                self.add_to_watchlist(m, purl)

    def add_to_watchlist(self, maintainer: dict, purl: str):
        """
        Add a maintainer to the watchlist.
        """
        existing = self.find_by_username(maintainer['username'])
        if existing:
            existing['packages'].append(purl)
        else:
            baseline = build_activity_baseline(maintainer['username'])
            self.watchlist.append({
                'username': maintainer['username'],
                'platform': maintainer['platform'],
                'reason': maintainer['role'],
                'packages': [purl],
                'added_at': datetime.now().isoformat(),
                'monitoring_level': 'standard',
                'baseline': baseline,
                'alerts': []
            })

    def run_daily_check(self):
        """
        Run daily monitoring checks on all watched accounts.
        """
        alerts = []
        for account in self.watchlist:
            # Check for anomalies
            anomalies = detect_account_compromise(account['username'], account['baseline'])
            if anomalies['requires_review']:
                alerts.append({
                    'type': 'anomaly',
                    'account': account['username'],
                    'details': anomalies
                })

            # Check for inactivity
            activity = track_maintainer_activity(account['username'], account['packages'])
            if activity['status'] in ['inactive', 'low_activity']:
                alerts.append({
                    'type': 'inactivity',
                    'account': account['username'],
                    'packages': account['packages'],
                    'last_activity': activity['last_activity']
                })

        return alerts
```

---

#### F.7 Maintainer Report Output

**Description:** Generate a maintainer health report for packages in the SBOM.

**Output Schema:**
```json
{
  "report_date": "2024-12-15",
  "sbom_packages_analyzed": 156,
  "unique_maintainers": 89,

  "summary": {
    "active_maintainers": 72,
    "reduced_activity": 12,
    "inactive": 5,
    "accounts_with_risk_signals": 3
  },

  "risk_packages": [
    {
      "purl": "pkg:npm/left-pad",
      "risk": "single_maintainer_inactive",
      "maintainers": [
        {
          "username": "azer",
          "status": "inactive",
          "last_activity": "2018-03-22"
        }
      ],
      "recommendation": "Consider alternative package or fork"
    }
  ],

  "alerts": [
    {
      "severity": "high",
      "type": "anomaly_detected",
      "account": "maintainer123",
      "packages_affected": ["pkg:npm/some-package"],
      "details": "Unusual CI/CD changes detected",
      "action_required": true
    }
  ],

  "maintainer_details": [
    {
      "username": "jdalton",
      "packages": ["pkg:npm/lodash"],
      "activity_status": "active",
      "reputation_score": 0.92,
      "access_level": "admin",
      "risk_signals": []
    }
  ]
}
```

---

### Category G: Organizational & Governance Metrics

*Inspired by enterprise Open Source Business Continuity (OSBC) reporting requirements.*

---

#### G.1 Company Affiliation Tracking

**Description:** Track contributors and their organizational affiliations to understand company involvement in a project.

**Data Sources:**
```
GET https://api.github.com/users/{username}  # company field
GET https://api.github.com/repos/{owner}/{repo}/contributors
```

**Calculation:**
```python
def track_company_involvement(repo: str, target_company: str = None):
    """
    Analyze contributor affiliations for a repository.
    Returns company distribution and tracks specific company involvement.
    """
    contributors = fetch_contributors(repo)
    affiliations = {}
    company_contributors = []

    for contributor in contributors:
        user = fetch_user(contributor['login'])
        company = normalize_company(user.get('company', ''))

        if company:
            if company not in affiliations:
                affiliations[company] = {
                    'contributors': [],
                    'total_contributions': 0
                }
            affiliations[company]['contributors'].append(contributor['login'])
            affiliations[company]['total_contributions'] += contributor['contributions']

            if target_company and company.lower() == target_company.lower():
                company_contributors.append({
                    'username': contributor['login'],
                    'contributions': contributor['contributions']
                })

    # Calculate percentages
    total_contributions = sum(c['contributions'] for c in contributors)
    for company in affiliations:
        affiliations[company]['percentage'] = round(
            affiliations[company]['total_contributions'] / total_contributions * 100, 1
        )

    # Identify controlling company (>50% contributions)
    controlling = None
    for company, data in affiliations.items():
        if data['percentage'] > 50:
            controlling = company
            break

    return {
        'affiliations': affiliations,
        'controlling_company': controlling,
        'target_company_contributors': company_contributors,
        'target_company_percentage': sum(c['contributions'] for c in company_contributors) / total_contributions * 100 if company_contributors else 0
    }

def normalize_company(company: str) -> str:
    """Normalize company names (handle @company, Inc, Corp variations)."""
    if not company:
        return None
    company = company.strip().lstrip('@')
    # Remove common suffixes
    for suffix in [', Inc.', ', Inc', ' Inc.', ' Corp.', ' LLC', ' Ltd.']:
        company = company.replace(suffix, '')
    return company
```

**Output:**
```json
{
  "repository": "apache/airflow",
  "affiliations": {
    "Astronomer": {
      "contributors": ["kaxil", "potiuk", "ephraimbuddy"],
      "total_contributions": 4521,
      "percentage": 35.2
    },
    "Amazon": {
      "contributors": ["ferruzzi", "vincbeck", "onikolas"],
      "total_contributions": 1823,
      "percentage": 14.2
    },
    "Google": {
      "contributors": ["mik-laj", "turbaszek"],
      "total_contributions": 1205,
      "percentage": 9.4
    }
  },
  "controlling_company": null,
  "target_company_contributors": [
    {"username": "ferruzzi", "contributions": 892},
    {"username": "vincbeck", "contributions": 654}
  ],
  "target_company_percentage": 14.2
}
```

---

#### G.2 License Change Detection

**Description:** Monitor for license changes in dependencies over time.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/license
GET https://registry.npmjs.org/{package}  # license field
GET https://pypi.org/pypi/{package}/json  # info.license
```

**Calculation:**
```python
def detect_license_changes(purl: str, history_db: dict):
    """
    Compare current license against stored history to detect changes.
    """
    current = get_current_license(purl)
    stored = history_db.get(purl)

    if stored is None:
        # First time seeing this package
        return {
            'purl': purl,
            'change_detected': False,
            'current_license': current,
            'action': 'store_baseline'
        }

    if current != stored['license']:
        return {
            'purl': purl,
            'change_detected': True,
            'previous_license': stored['license'],
            'previous_date': stored['detected_at'],
            'current_license': current,
            'change_type': classify_license_change(stored['license'], current),
            'risk_level': assess_license_risk(stored['license'], current)
        }

    return {
        'purl': purl,
        'change_detected': False,
        'current_license': current
    }

def classify_license_change(old: str, new: str):
    """Classify the type of license change."""
    permissive = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC']
    copyleft = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0']
    source_available = ['SSPL-1.0', 'BSL-1.1', 'Elastic-2.0']

    if old in permissive and new in copyleft:
        return 'permissive_to_copyleft'
    elif old in permissive and new in source_available:
        return 'permissive_to_source_available'
    elif old in copyleft and new in source_available:
        return 'copyleft_to_source_available'
    elif new == 'UNLICENSED' or new is None:
        return 'license_removed'
    else:
        return 'other'
```

**Output:**
```json
{
  "purl": "pkg:npm/redis",
  "change_detected": true,
  "previous_license": "BSD-3-Clause",
  "previous_date": "2024-01-15",
  "current_license": "SSPL-1.0",
  "change_type": "permissive_to_source_available",
  "risk_level": "high",
  "recommendation": "Review SSPL compatibility with your use case"
}
```

---

#### G.3 Foundation Membership Detection

**Description:** Detect if a project is part of a recognized open source foundation.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}
# Check owner organization, README, package.json, etc.
```

**Known Foundations:**
```python
FOUNDATIONS = {
    'apache': {
        'name': 'Apache Software Foundation',
        'github_orgs': ['apache'],
        'license_requirement': 'Apache-2.0',
        'governance': 'PMC'
    },
    'cncf': {
        'name': 'Cloud Native Computing Foundation',
        'github_orgs': ['cncf', 'kubernetes', 'prometheus', 'envoyproxy'],
        'levels': ['sandbox', 'incubating', 'graduated'],
        'governance': 'TOC'
    },
    'linux_foundation': {
        'name': 'Linux Foundation',
        'github_orgs': ['linuxfoundation'],
        'projects_url': 'https://www.linuxfoundation.org/projects'
    },
    'eclipse': {
        'name': 'Eclipse Foundation',
        'github_orgs': ['eclipse', 'eclipse-ee4j'],
        'governance': 'PMC'
    },
    'openssf': {
        'name': 'Open Source Security Foundation',
        'github_orgs': ['ossf'],
        'parent': 'linux_foundation'
    },
    'python': {
        'name': 'Python Software Foundation',
        'github_orgs': ['python', 'pypa', 'psf']
    }
}

def detect_foundation(repo: str):
    """
    Detect if repository belongs to a known foundation.
    """
    owner, repo_name = parse_repo(repo)

    # Check if owner is a known foundation org
    for foundation_id, foundation in FOUNDATIONS.items():
        if owner.lower() in [o.lower() for o in foundation.get('github_orgs', [])]:
            return {
                'is_foundation_project': True,
                'foundation_id': foundation_id,
                'foundation_name': foundation['name'],
                'governance_model': foundation.get('governance'),
                'confidence': 'high'
            }

    # Check README/description for foundation mentions
    repo_data = fetch_repo(repo)
    description = (repo_data.get('description', '') or '').lower()

    for foundation_id, foundation in FOUNDATIONS.items():
        if foundation['name'].lower() in description:
            return {
                'is_foundation_project': True,
                'foundation_id': foundation_id,
                'foundation_name': foundation['name'],
                'confidence': 'medium',
                'source': 'description'
            }

    return {
        'is_foundation_project': False,
        'foundation_id': None,
        'confidence': 'high'
    }
```

**Output:**
```json
{
  "repository": "apache/airflow",
  "is_foundation_project": true,
  "foundation_id": "apache",
  "foundation_name": "Apache Software Foundation",
  "governance_model": "PMC",
  "confidence": "high",
  "implications": {
    "license": "Apache-2.0 required",
    "cla_required": true,
    "voting_structure": "PMC consensus"
  }
}
```

---

#### G.4 PR Acceptance & Rejection Tracking

**Description:** Track pull request acceptance rates, especially for specific contributors or companies.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/pulls?state=all
GET https://api.github.com/repos/{owner}/{repo}/pulls/{number}
```

**Calculation:**
```python
def track_pr_acceptance(repo: str, lookback_days: int = 90, filter_author: str = None):
    """
    Track PR acceptance rates, optionally filtered by author.
    """
    cutoff = datetime.now() - timedelta(days=lookback_days)
    prs = fetch_prs(repo, state='all', since=cutoff)

    if filter_author:
        prs = [pr for pr in prs if pr['user']['login'] == filter_author]

    stats = {
        'total': len(prs),
        'merged': 0,
        'closed_unmerged': 0,
        'open': 0,
        'refused_prs': [],
        'avg_time_to_decision': None
    }

    decision_times = []

    for pr in prs:
        if pr['state'] == 'open':
            stats['open'] += 1
        elif pr['merged_at']:
            stats['merged'] += 1
            decision_times.append(
                (parse_date(pr['merged_at']) - parse_date(pr['created_at'])).days
            )
        else:
            stats['closed_unmerged'] += 1
            stats['refused_prs'].append({
                'number': pr['number'],
                'title': pr['title'],
                'author': pr['user']['login'],
                'created_at': pr['created_at'],
                'closed_at': pr['closed_at'],
                'reason': extract_close_reason(pr)
            })
            decision_times.append(
                (parse_date(pr['closed_at']) - parse_date(pr['created_at'])).days
            )

    if decision_times:
        stats['avg_time_to_decision'] = round(sum(decision_times) / len(decision_times), 1)

    stats['acceptance_rate'] = round(
        stats['merged'] / (stats['merged'] + stats['closed_unmerged']) * 100, 1
    ) if (stats['merged'] + stats['closed_unmerged']) > 0 else None

    return stats

def extract_close_reason(pr: dict) -> str:
    """
    Try to determine why a PR was closed without merging.
    """
    # Check for closing comment
    comments = fetch_pr_comments(pr['url'])
    if comments:
        last_comment = comments[-1]['body'].lower()
        if 'duplicate' in last_comment:
            return 'duplicate'
        elif 'stale' in last_comment:
            return 'stale'
        elif 'wontfix' in last_comment or "won't fix" in last_comment:
            return 'wontfix'
        elif 'closed by author' in last_comment:
            return 'author_closed'

    return 'unknown'
```

**Output:**
```json
{
  "repository": "apache/airflow",
  "period": "last 90 days",
  "filter_author": "vincbeck",
  "stats": {
    "total": 23,
    "merged": 19,
    "closed_unmerged": 2,
    "open": 2,
    "acceptance_rate": 90.5,
    "avg_time_to_decision": 4.2,
    "refused_prs": [
      {
        "number": 12345,
        "title": "Add multi-team configuration support",
        "created_at": "2025-07-01",
        "closed_at": "2025-07-15",
        "reason": "design_disagreement"
      }
    ]
  }
}
```

---

#### G.5 Governance Structure Detection

**Description:** Parse project governance files to understand decision-making structure.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/contents/GOVERNANCE.md
GET https://api.github.com/repos/{owner}/{repo}/contents/MAINTAINERS.md
GET https://api.github.com/repos/{owner}/{repo}/contents/CODEOWNERS
GET https://api.github.com/repos/{owner}/{repo}/contents/.github/CODEOWNERS
```

**AI Agent:** `GovernanceParserAgent`
- **Type:** Extraction Agent
- **Model:** Medium LLM
- **Prompt:**
```
Parse this project governance document and extract:

1. Governance model (BDFL, meritocracy, foundation, corporate, committee)
2. Decision-making process (consensus, voting, maintainer discretion)
3. Roles defined (maintainer, committer, PMC, TSC, contributor)
4. Current role holders (extract usernames)
5. Voting thresholds (if mentioned)

Document:
{governance_text}

Return JSON:
{
  "governance_model": "foundation_pmc",
  "decision_process": "lazy_consensus",
  "roles": [
    {"name": "PMC", "permissions": ["merge", "release", "vote"], "members": ["user1", "user2"]},
    {"name": "Committer", "permissions": ["merge"], "members": ["user3", "user4"]}
  ],
  "voting": {
    "required_for": ["releases", "new_committers", "architectural_changes"],
    "threshold": "majority",
    "veto_allowed": true
  }
}
```

**Output:**
```json
{
  "repository": "apache/airflow",
  "governance": {
    "model": "foundation_pmc",
    "foundation": "Apache Software Foundation",
    "decision_process": "lazy_consensus",
    "roles": {
      "PMC": {
        "description": "Project Management Committee",
        "permissions": ["vote", "release", "add_committer"],
        "member_count": 42
      },
      "Committer": {
        "description": "Write access to repository",
        "permissions": ["merge", "triage"],
        "member_count": 89
      }
    },
    "voting": {
      "required_for": ["releases", "new_pmc", "license_changes"],
      "threshold": "majority",
      "veto_power": true
    }
  },
  "company_representation": {
    "Astronomer": {"pmc": 8, "committer": 12},
    "Amazon": {"pmc": 1, "committer": 5},
    "Google": {"pmc": 3, "committer": 4}
  }
}
```

---

#### G.6 Contributor Recognition Tracking

**Description:** Track when contributors are publicly recognized in release notes, changelogs, or announcements.

**Data Sources:**
```
GET https://api.github.com/repos/{owner}/{repo}/releases
GET https://api.github.com/repos/{owner}/{repo}/contents/CHANGELOG.md
```

**AI Agent:** `RecognitionExtractorAgent`
- **Type:** Extraction Agent
- **Model:** Small LLM
- **Prompt:**
```
Extract contributor recognitions from this release note or changelog.
Look for:
- @mentions of usernames
- "Thanks to" or "contributed by" patterns
- "Special thanks" sections
- Named features with attributions

Text:
{release_text}

Return JSON:
{
  "recognitions": [
    {"username": "ferruzzi", "type": "feature", "description": "AIP-86 Deadline Alerts"},
    {"username": "vincbeck", "type": "thanks", "description": "Auth Manager improvements"}
  ]
}
```

**Calculation:**
```python
def track_recognitions(repo: str, target_users: list[str] = None, lookback_months: int = 6):
    """
    Track contributor recognitions in releases and changelogs.
    """
    recognitions = []

    # Parse releases
    releases = fetch_releases(repo)
    for release in releases:
        if is_within_lookback(release['published_at'], lookback_months):
            extracted = ai_extract_recognitions(release['body'])
            for rec in extracted:
                rec['source'] = 'release'
                rec['release_tag'] = release['tag_name']
                rec['date'] = release['published_at']
                recognitions.append(rec)

    # Parse changelog if exists
    changelog = fetch_file(repo, 'CHANGELOG.md')
    if changelog:
        extracted = ai_extract_recognitions(changelog)
        recognitions.extend(extracted)

    # Filter to target users if specified
    if target_users:
        recognitions = [r for r in recognitions if r['username'] in target_users]

    return {
        'repository': repo,
        'period': f'last {lookback_months} months',
        'total_recognitions': len(recognitions),
        'recognitions': recognitions,
        'users_recognized': list(set(r['username'] for r in recognitions))
    }
```

**Output:**
```json
{
  "repository": "apache/airflow",
  "period": "last 6 months",
  "total_recognitions": 12,
  "recognitions": [
    {
      "username": "ferruzzi",
      "type": "feature",
      "description": "Led AIP-86 Deadline Alerts implementation",
      "release_tag": "v3.1.0",
      "date": "2025-07-15"
    },
    {
      "username": "vincbeck",
      "type": "keynote",
      "description": "Keynote speaker for Airflow 3.0 at Summit",
      "source": "announcement",
      "date": "2025-10-10"
    }
  ],
  "target_company_recognitions": 5
}
```

---

#### G.7 OSBC Report Output

**Description:** Generate a structured report that can populate an OSBC-style business continuity assessment.

**Output Schema:**
```json
{
  "report_type": "osbc",
  "generated_at": "2025-12-18T12:00:00Z",
  "package": "pkg:pypi/apache-airflow",
  "repository": "apache/airflow",

  "project_information": {
    "name": "Apache Airflow",
    "url": "https://airflow.apache.org/",
    "description": "Platform to programmatically author, schedule and monitor workflows",
    "ecosystem": "pypi"
  },

  "organizational_structure": {
    "foundation": {
      "is_member": true,
      "name": "Apache Software Foundation",
      "governance_model": "PMC"
    },
    "controlling_company": null,
    "license": {
      "current": "Apache-2.0",
      "change_detected": false
    }
  },

  "community_composition": {
    "total_contributors": 2847,
    "active_contributors_90d": 156,
    "contributor_change_pct": 8.5,
    "bus_factor": 12,
    "company_distribution": {
      "Astronomer": {"percentage": 35.2, "contributors": 24},
      "Amazon": {"percentage": 14.2, "contributors": 5},
      "Google": {"percentage": 9.4, "contributors": 8}
    }
  },

  "company_involvement": {
    "target_company": "Amazon",
    "contributors": ["ferruzzi", "vincbeck", "onikolas", "ramitkat", "ghaeli"],
    "contribution_percentage": 14.2,
    "pr_acceptance_rate": 90.5,
    "recognitions_count": 5,
    "governance_positions": {
      "committer": 5,
      "pmc": 1
    }
  },

  "recent_developments": [
    {
      "date": "2025-04-22",
      "event": "Airflow 3.0 released",
      "sentiment": "positive"
    },
    {
      "date": "2025-07-01",
      "event": "Multi-team feature discussion - design disagreement",
      "sentiment": "negative",
      "details": "Contribution refused due to maintainer preference for managed services"
    }
  ],

  "risks": [
    {
      "type": "single_company_influence",
      "description": "Astronomer has 35% of contributions and majority PMC seats",
      "impact": 4,
      "probability": 4
    }
  ],

  "auto_generated": true,
  "requires_manual_input": [
    "internal_sponsors",
    "expertise_level",
    "how_product_uses_project",
    "goals_and_milestones",
    "mitigation_plans"
  ]
}
```

---

## Part 3: AI Agent Architecture

### Agent Types

| Agent Type | Purpose | Model Size | Latency |
|------------|---------|------------|---------|
| **Extraction** | Pull structured data from text | Small (8B) | Low |
| **Classification** | Categorize content | Small (8B) | Low |
| **Correlation** | Match across data sources | Medium (70B) | Medium |
| **Synthesis** | Generate new content | Large (70B+) | High |
| **Summarization** | Condense information | Small (8B) | Low |
| **Monitoring** | Detect anomalies, track activity | Medium (70B) | Medium |

### Recommended Models

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| **Ollama (Local)** | llama3:8b | Extraction, Classification | Free |
| **Ollama (Local)** | llama3:70b | Correlation, Synthesis | Free |
| **OpenAI** | gpt-4o-mini | Extraction, Classification | $0.15/1M tokens |
| **OpenAI** | gpt-4o | Synthesis, Complex analysis | $2.50/1M tokens |
| **Anthropic** | claude-3-haiku | Extraction, Classification | $0.25/1M tokens |
| **Anthropic** | claude-3-sonnet | Synthesis | $3.00/1M tokens |

### Agent Orchestration

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ RSS      │ │ GitHub   │ │ HN/Reddit│ │ Vuln DBs         │  │
│  │ Collector│ │ Analyzer │ │ Collector│ │ (OSV/NVD)        │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       └────────────┴────────────┴────────────────┘             │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     AI AGENT LAYER                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 EXTRACTION AGENTS                        │   │
│  │  PackageIdentifier │ RiskRelevance │ SentimentAnalyzer  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                CORRELATION AGENTS                        │   │
│  │  VulnerabilityCorrelator │ PackageToRepo Mapper         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 SYNTHESIS AGENTS                         │   │
│  │  RemediationGenerator │ AdvisorySynthesizer             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MONITORING AGENTS                           │   │
│  │  AccountAnomalyDetector │ MaintainerActivityTracker     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     OUTPUT LAYER                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │
│  │ JSON Reports │ │ Advisories   │ │ Jekyll Static Site   │   │
│  └──────────────┘ └──────────────┘ └──────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Maintainer Health Reports │ Account Watchlist Alerts     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 4: Output Schemas

### Advisory Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "advisory_id": {"type": "string", "pattern": "^CCDA-\\d{4}-\\d{4}$"},
    "published": {"type": "string", "format": "date-time"},
    "updated": {"type": "string", "format": "date-time"},
    "severity": {"enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},

    "summary": {"type": "string"},

    "affected_packages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "purl": {"type": "string"},
          "affected_versions": {"type": "string"},
          "fixed_version": {"type": "string"}
        }
      }
    },

    "scores": {
      "type": "object",
      "properties": {
        "cvss_v3": {"type": "number"},
        "cvss_vector": {"type": "string"},
        "epss": {"type": "number"},
        "ccda_risk_score": {"type": "number"},
        "ccda_priority": {"type": "number"}
      }
    },

    "exploit_status": {
      "type": "object",
      "properties": {
        "poc_available": {"type": "boolean"},
        "in_the_wild": {"type": "boolean"},
        "poc_urls": {"type": "array", "items": {"type": "string"}}
      }
    },

    "remediation": {
      "type": "object",
      "properties": {
        "primary_fix": {"type": "object"},
        "workarounds": {"type": "array"},
        "detection": {"type": "string"}
      }
    },

    "references": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"enum": ["CVE", "GHSA", "OSV", "VENDOR", "PATCH", "ARTICLE"]},
          "url": {"type": "string", "format": "uri"}
        }
      }
    },

    "timeline": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "date": {"type": "string", "format": "date"},
          "event": {"type": "string"}
        }
      }
    },

    "detection_source": {
      "type": "object",
      "properties": {
        "source": {"enum": ["media", "osv", "nvd", "github"]},
        "detected_at": {"type": "string", "format": "date-time"},
        "article_url": {"type": "string"}
      }
    }
  },
  "required": ["advisory_id", "published", "severity", "summary", "affected_packages"]
}
```

### Repository Health Output Schema

```json
{
  "repository": "owner/repo",
  "analyzed_at": "2025-01-15T10:30:00Z",
  "purl": "pkg:npm/react",

  "health_metrics": {
    "commit_activity": {...},
    "bus_factor": {...},
    "time_to_first_response": {...},
    "time_to_close": {...},
    "pr_merge_time": {...},
    "contributor_retention": {...}
  },

  "security_metrics": {
    "vulnerabilities": {...},
    "security_policy": {...},
    "branch_protection": {...},
    "signed_releases": {...},
    "dependency_updates": {...}
  },

  "risk_assessment": {
    "risk_score": 0.35,
    "risk_level": "medium",
    "risk_factors": [
      "Bus factor of 2 (high dependency on few contributors)",
      "No security policy found"
    ]
  }
}
```

---

## Part 5: Remediation Knowledge Base

### Overview

To provide actionable remediation guidance, CCDA needs to build and maintain a knowledge base that tracks:

1. **Package version history** - Which versions exist and their release dates
2. **Vulnerability fix mapping** - Which version fixes which CVE
3. **Alternative packages** - Similar packages that could replace a problematic one
4. **Alternative evaluation** - License compatibility, community health, feature parity

### 5.1 Package Version Intelligence

**Purpose:** Track all versions of monitored packages and their security status.

**Data Sources:**

| Registry | Version History Endpoint |
|----------|-------------------------|
| **npm** | `https://registry.npmjs.org/{package}` → `versions` object |
| **PyPI** | `https://pypi.org/pypi/{package}/json` → `releases` object |
| **RubyGems** | `https://rubygems.org/api/v1/versions/{gem}.json` |
| **crates.io** | `https://crates.io/api/v1/crates/{crate}/versions` |
| **Maven** | `https://search.maven.org/solrsearch/select?q=g:{g}+AND+a:{a}&core=gav&rows=100` |
| **Go** | `https://proxy.golang.org/{module}/@v/list` |

**Data Model:**
```json
{
  "package": "lodash",
  "ecosystem": "npm",
  "purl": "pkg:npm/lodash",
  "versions": [
    {
      "version": "4.17.21",
      "released_at": "2021-02-20T10:30:00Z",
      "is_latest": true,
      "is_deprecated": false,
      "vulnerabilities": [],
      "fixes_cves": ["CVE-2021-23337", "CVE-2020-28500"]
    },
    {
      "version": "4.17.20",
      "released_at": "2020-08-13T10:00:00Z",
      "is_latest": false,
      "is_deprecated": false,
      "vulnerabilities": ["CVE-2021-23337"],
      "fixes_cves": ["CVE-2020-28500"]
    }
  ]
}
```

**Collection Algorithm:**
```python
def build_version_intelligence(package, ecosystem):
    # 1. Fetch all versions from registry
    versions = fetch_versions_from_registry(package, ecosystem)

    # 2. For each version, check vulnerability status
    for version in versions:
        vulns = query_osv(package, ecosystem, version)
        version['vulnerabilities'] = [v['id'] for v in vulns]

    # 3. Determine which versions fix which CVEs
    # Compare adjacent versions - if vuln disappears, that version fixes it
    for i, version in enumerate(versions[:-1]):
        next_version = versions[i + 1]
        fixed_in_next = set(version['vulnerabilities']) - set(next_version['vulnerabilities'])
        next_version['fixes_cves'] = list(fixed_in_next)

    return versions
```

---

### 5.2 Verified Fix Mapping

**Purpose:** Map CVEs to the exact versions that fix them with verification.

**Data Sources:**

| Source | Fix Information |
|--------|-----------------|
| **OSV** | `affected[].ranges[].events[].fixed` - Exact fix version |
| **GitHub Advisories** | `vulnerabilities[].first_patched_version` |
| **NVD** | `configurations.nodes[].cpe_match[].versionEndExcluding` |
| **Changelogs** | AI-parsed fix mentions |
| **Commit Messages** | AI-parsed CVE references |

**OSV Fix Extraction:**
```python
def get_fix_version_from_osv(vuln_id, package, ecosystem):
    """
    OSV provides structured fix information in the 'ranges' field
    """
    osv_data = query_osv_by_id(vuln_id)

    for affected in osv_data.get('affected', []):
        if affected['package']['name'] == package:
            for range_info in affected.get('ranges', []):
                for event in range_info.get('events', []):
                    if 'fixed' in event:
                        return {
                            'fixed_version': event['fixed'],
                            'source': 'osv',
                            'verified': True,
                            'verification_method': 'structured_data'
                        }

    return None
```

**AI-Verified Fix Detection:**

When structured data is unavailable, use AI to verify fixes from changelogs:

**AI Agent:** `FixVerificationAgent`
- **Type:** Verification Agent
- **Model:** Medium LLM (llama3-70b, gpt-4o)
- **Prompt:**
```
Analyze this changelog/release notes to verify if {cve_id} is fixed.

Package: {package_name}
Version: {version}
CVE: {cve_id}
CVE Description: {cve_description}

Changelog content:
{changelog}

Determine:
1. Does this version explicitly mention fixing {cve_id}?
2. Does it mention fixing the vulnerability described (even without CVE ID)?
3. What is the confidence level of this fix?

Return JSON:
{
  "fixes_cve": true,
  "confidence": "high",
  "evidence": "Changelog mentions 'Fixed prototype pollution vulnerability (CVE-2021-23337)'",
  "fix_type": "patch",
  "breaking_changes": false,
  "verification_method": "changelog_analysis"
}
```

**Fix Mapping Data Model:**
```json
{
  "cve_id": "CVE-2021-23337",
  "package": "lodash",
  "ecosystem": "npm",
  "purl": "pkg:npm/lodash",

  "affected_versions": {
    "range": "<4.17.21",
    "specific": ["4.17.20", "4.17.19", "4.17.18"]
  },

  "fix": {
    "version": "4.17.21",
    "released_at": "2021-02-20",
    "verified": true,
    "verification_sources": ["osv", "changelog", "commit"],
    "fix_commit": "https://github.com/lodash/lodash/commit/...",
    "breaking_changes": false
  },

  "upgrade_path": {
    "from_4.17.20": {
      "target": "4.17.21",
      "semver_change": "patch",
      "breaking": false,
      "command": "npm install lodash@4.17.21"
    },
    "from_3.x": {
      "target": "4.17.21",
      "semver_change": "major",
      "breaking": true,
      "migration_guide": "https://github.com/lodash/lodash/wiki/Changelog#v400"
    }
  }
}
```

---

### 5.3 Alternative Package Discovery

**Purpose:** Find replacement packages when the original has unfixable issues (abandoned, license change, etc.).

**Data Sources:**

| Source | How to Find Alternatives |
|--------|-------------------------|
| **npm** | `https://www.npmjs.com/package/{pkg}` → "Related packages" |
| **Libraries.io** | `https://libraries.io/api/{platform}/{package}/suggestions` |
| **GitHub Topics** | Same topics/tags as original package |
| **Package READMEs** | AI-parsed "Alternatives" sections |
| **Awesome Lists** | Curated alternatives in awesome-* repos |
| **Migration Guides** | AI-parsed migration documentation |

**Alternative Discovery Algorithm:**
```python
def discover_alternatives(package, ecosystem, reason):
    """
    Find alternative packages based on:
    - reason: 'vulnerability', 'abandoned', 'license_change', 'deprecated'
    """
    alternatives = []

    # 1. Check if package README mentions alternatives
    readme = fetch_readme(package, ecosystem)
    ai_alternatives = ai_extract_alternatives(readme)
    alternatives.extend(ai_alternatives)

    # 2. Search for packages with similar keywords
    keywords = get_package_keywords(package, ecosystem)
    similar = search_by_keywords(ecosystem, keywords)
    alternatives.extend(similar)

    # 3. Check awesome lists
    awesome_alternatives = search_awesome_lists(package)
    alternatives.extend(awesome_alternatives)

    # 4. Check migration guides (e.g., "migrating from X to Y")
    migrations = search_migration_guides(package)
    alternatives.extend(migrations)

    # Deduplicate and rank
    return rank_alternatives(alternatives, package)
```

**AI Agent:** `AlternativeDiscoveryAgent`
- **Type:** Extraction + Ranking Agent
- **Model:** Medium LLM
- **Prompt:**
```
Find alternative packages for {package_name} ({ecosystem}).

Reason for seeking alternative: {reason}
Package description: {description}
Package keywords: {keywords}

README content:
{readme}

Search these sources for alternatives:
1. "Alternatives" or "Similar packages" sections in README
2. "Migrating from {package}" documentation
3. Packages with same keywords/functionality

Return JSON:
{
  "alternatives": [
    {
      "name": "alternative-pkg",
      "ecosystem": "npm",
      "purl": "pkg:npm/alternative-pkg",
      "reason_suggested": "Explicitly mentioned as alternative in README",
      "feature_parity": "high",
      "migration_effort": "low",
      "confidence": "high"
    }
  ],
  "migration_guides_found": [
    "https://example.com/migrating-from-x-to-y"
  ]
}
```

---

### 5.4 Alternative Evaluation

**Purpose:** Evaluate alternative packages for license compatibility, community health, and security.

**Evaluation Criteria:**

| Criterion | Data Source | Scoring |
|-----------|-------------|---------|
| **License Compatibility** | Package registry, GitHub | Compatible/Incompatible/Copyleft |
| **Community Health** | CCDA GitHub metrics | Bus factor, activity, responsiveness |
| **Security Posture** | OSV, GitHub security | Open vulns, security policy |
| **Maintenance Status** | GitHub commits, releases | Active/Slow/Abandoned |
| **Feature Parity** | AI analysis of docs | High/Medium/Low |
| **Migration Effort** | AI analysis | Low/Medium/High |

**License Compatibility Matrix:**
```python
LICENSE_COMPATIBILITY = {
    # Original license → Compatible alternatives
    'MIT': ['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'Apache-2.0', 'Unlicense'],
    'Apache-2.0': ['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'Apache-2.0'],
    'BSD-3-Clause': ['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC'],
    'GPL-3.0': ['GPL-3.0', 'AGPL-3.0'],  # Copyleft - limited compatibility
    'AGPL-3.0': ['AGPL-3.0'],  # Most restrictive
}

def check_license_compatibility(original_license, alternative_license):
    compatible = LICENSE_COMPATIBILITY.get(original_license, [])
    return alternative_license in compatible
```

**Full Evaluation Pipeline:**
```python
def evaluate_alternative(original_pkg, alternative_pkg):
    """
    Comprehensive evaluation of an alternative package
    """
    evaluation = {
        'package': alternative_pkg['name'],
        'purl': alternative_pkg['purl'],
        'recommendation': None,
        'scores': {}
    }

    # 1. License check
    alt_license = get_package_license(alternative_pkg)
    orig_license = get_package_license(original_pkg)
    evaluation['license'] = {
        'license': alt_license,
        'compatible': check_license_compatibility(orig_license, alt_license),
        'copyleft': alt_license in ['GPL-3.0', 'AGPL-3.0', 'LGPL-3.0']
    }

    # 2. Community health (use CCDA GitHub metrics)
    github_repo = get_github_repo(alternative_pkg)
    if github_repo:
        health = analyze_repository_health(github_repo)
        evaluation['community_health'] = {
            'bus_factor': health['bus_factor'],
            'commit_frequency': health['commit_frequency'],
            'responsiveness': health['time_to_first_response'],
            'score': calculate_health_score(health)
        }

    # 3. Security check
    vulns = get_vulnerabilities(alternative_pkg)
    evaluation['security'] = {
        'open_vulnerabilities': len(vulns),
        'critical_vulns': len([v for v in vulns if v['severity'] == 'CRITICAL']),
        'has_security_policy': check_security_policy(github_repo)
    }

    # 4. Maintenance status
    evaluation['maintenance'] = {
        'last_release': get_last_release_date(alternative_pkg),
        'release_frequency': calculate_release_frequency(alternative_pkg),
        'status': classify_maintenance_status(alternative_pkg)
    }

    # 5. AI-powered feature parity and migration analysis
    evaluation['compatibility'] = ai_analyze_compatibility(original_pkg, alternative_pkg)

    # Calculate overall recommendation
    evaluation['recommendation'] = calculate_recommendation(evaluation)

    return evaluation
```

**AI Agent:** `AlternativeEvaluatorAgent`
- **Type:** Analysis Agent
- **Model:** Large LLM
- **Prompt:**
```
Evaluate {alternative_pkg} as a replacement for {original_pkg}.

Original package:
- Name: {original_name}
- Description: {original_desc}
- API/Features: {original_api}

Alternative package:
- Name: {alt_name}
- Description: {alt_desc}
- API/Features: {alt_api}

Evaluate:
1. Feature parity - Does it provide same functionality?
2. API compatibility - How similar is the API?
3. Migration effort - How much code change needed?
4. Ecosystem fit - Does it integrate with same tools?

Return JSON:
{
  "feature_parity": "high",
  "feature_gaps": ["Feature X not available"],
  "feature_additions": ["Has feature Y that original lacks"],
  "api_compatibility": "medium",
  "api_differences": ["Uses async/await instead of callbacks"],
  "migration_effort": "medium",
  "migration_steps": [
    "Replace import statements",
    "Update function calls from X to Y",
    "Handle async/await conversion"
  ],
  "estimated_loc_changes": "50-100 lines per usage",
  "recommendation": "Recommended with minor migration effort"
}
```

---

### 5.5 Remediation Knowledge Graph

**Purpose:** Build a queryable knowledge graph for remediation decisions.

**Graph Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│                  REMEDIATION KNOWLEDGE GRAPH                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐         ┌─────────┐         ┌─────────────────┐  │
│  │ Package │────────▶│ Version │────────▶│ Vulnerability   │  │
│  │         │ has     │         │ has     │                 │  │
│  └────┬────┘         └────┬────┘         └────────┬────────┘  │
│       │                   │                        │           │
│       │ alternative       │ fixes                  │ fixed_by  │
│       ▼                   ▼                        ▼           │
│  ┌─────────┐         ┌─────────┐         ┌─────────────────┐  │
│  │ Package │         │ Version │         │ Version         │  │
│  │ (alt)   │         │ (fixed) │         │                 │  │
│  └─────────┘         └─────────┘         └─────────────────┘  │
│       │                                                        │
│       │ evaluated                                              │
│       ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Evaluation                                                │ │
│  │ - license_compatible: true                                │ │
│  │ - community_health: 0.85                                  │ │
│  │ - security_score: 0.92                                    │ │
│  │ - feature_parity: high                                    │ │
│  │ - migration_effort: low                                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Knowledge Graph Schema:**
```json
{
  "nodes": {
    "Package": {
      "properties": ["name", "ecosystem", "purl", "license", "description"]
    },
    "Version": {
      "properties": ["version", "released_at", "is_latest", "is_deprecated"]
    },
    "Vulnerability": {
      "properties": ["id", "severity", "cvss", "summary", "published"]
    },
    "Evaluation": {
      "properties": ["license_compatible", "health_score", "security_score",
                     "feature_parity", "migration_effort", "recommendation"]
    }
  },
  "edges": {
    "HAS_VERSION": {"from": "Package", "to": "Version"},
    "HAS_VULNERABILITY": {"from": "Version", "to": "Vulnerability"},
    "FIXES": {"from": "Version", "to": "Vulnerability"},
    "ALTERNATIVE_TO": {"from": "Package", "to": "Package"},
    "EVALUATED_AS": {"from": "Package", "to": "Evaluation"}
  }
}
```

---

### 5.6 Remediation Recommendation Engine

**Purpose:** Generate actionable remediation recommendations based on knowledge base.

**Recommendation Types:**

| Scenario | Recommendation Type |
|----------|---------------------|
| Vulnerable version, fix available | **Upgrade** to fixed version |
| Vulnerable, no fix, workaround exists | **Workaround** + monitor for fix |
| Abandoned package with vulns | **Replace** with evaluated alternative |
| License changed to incompatible | **Replace** with compatible alternative |
| Breaking changes in fix | **Upgrade with migration guide** |

**AI Agent:** `RemediationRecommenderAgent`
- **Type:** Decision Agent
- **Model:** Large LLM
- **Prompt:**
```
Generate remediation recommendation for this vulnerability.

Vulnerability:
- CVE: {cve_id}
- Severity: {severity}
- Package: {package_name}@{current_version}
- Description: {description}

Available options:
1. Upgrade path: {upgrade_options}
2. Workarounds: {workarounds}
3. Alternatives: {evaluated_alternatives}

User constraints:
- License requirements: {license_requirements}
- Breaking changes acceptable: {breaking_ok}
- Timeline: {urgency}

Generate prioritized recommendations:

Return JSON:
{
  "primary_recommendation": {
    "action": "upgrade",
    "target": "lodash@4.17.21",
    "command": "npm install lodash@4.17.21",
    "breaking_changes": false,
    "effort": "minimal",
    "rationale": "Patch version with security fix, no breaking changes"
  },

  "alternative_recommendations": [
    {
      "action": "replace",
      "target": "lodash-es@4.17.21",
      "rationale": "ESM alternative if migrating to ES modules",
      "effort": "medium",
      "migration_guide": "..."
    }
  ],

  "temporary_mitigation": {
    "action": "workaround",
    "steps": ["Validate all user input before passing to _.template()"],
    "effectiveness": "partial",
    "use_until": "upgrade is complete"
  },

  "not_recommended": [
    {
      "option": "underscore",
      "reason": "Also affected by similar vulnerabilities"
    }
  ]
}
```

---

### 5.7 Knowledge Base Update Pipeline

**Purpose:** Keep remediation knowledge current.

**Update Triggers:**

| Trigger | Action |
|---------|--------|
| New CVE published | Query affected packages, find fixes |
| New package version | Check if fixes known vulns |
| Package deprecated | Find and evaluate alternatives |
| License change detected | Re-evaluate compatibility |
| Media alert (CCDA) | Correlate to knowledge base |

**Update Pipeline:**
```python
class RemediationKnowledgeUpdater:
    def __init__(self):
        self.knowledge_base = KnowledgeGraph()
        self.agents = {
            'fix_verifier': FixVerificationAgent(),
            'alternative_finder': AlternativeDiscoveryAgent(),
            'evaluator': AlternativeEvaluatorAgent()
        }

    async def on_new_cve(self, cve_data):
        """Handle new CVE publication"""
        for affected in cve_data['affected_packages']:
            # Find fix version
            fix = await self.find_fix_version(cve_data['id'], affected)
            if fix:
                self.knowledge_base.add_fix(cve_data['id'], fix)

            # If no fix, find alternatives
            if not fix:
                alternatives = await self.find_alternatives(affected, 'vulnerability')
                for alt in alternatives:
                    evaluation = await self.evaluate_alternative(affected, alt)
                    self.knowledge_base.add_alternative(affected, alt, evaluation)

    async def on_new_version(self, package, version):
        """Handle new package version"""
        # Check if fixes any known vulns
        known_vulns = self.knowledge_base.get_unfixed_vulns(package)
        for vuln in known_vulns:
            is_fixed = await self.verify_fix(package, version, vuln)
            if is_fixed:
                self.knowledge_base.mark_fixed(vuln, version)

    async def on_package_abandoned(self, package):
        """Handle abandoned package"""
        alternatives = await self.find_alternatives(package, 'abandoned')
        for alt in alternatives:
            evaluation = await self.evaluate_alternative(package, alt)
            self.knowledge_base.add_alternative(package, alt, evaluation)

    async def on_license_change(self, package, new_license):
        """Handle license change"""
        if self.is_problematic_license(new_license):
            alternatives = await self.find_alternatives(package, 'license_change')
            # Filter to only compatible licenses
            compatible = [a for a in alternatives
                         if self.check_license_compatible(new_license, a['license'])]
            for alt in compatible:
                evaluation = await self.evaluate_alternative(package, alt)
                self.knowledge_base.add_alternative(package, alt, evaluation)
```

---

### 5.8 Remediation Output Format

**Advisory with Remediation:**
```json
{
  "advisory_id": "CCDA-2024-0042",
  "vulnerability": {
    "cve_id": "CVE-2021-23337",
    "severity": "HIGH",
    "summary": "Prototype pollution in lodash"
  },

  "affected": {
    "package": "lodash",
    "purl": "pkg:npm/lodash",
    "versions": "<4.17.21"
  },

  "remediation": {
    "recommended_action": "upgrade",

    "upgrade_options": [
      {
        "from_version": "4.17.20",
        "to_version": "4.17.21",
        "semver": "patch",
        "breaking_changes": false,
        "verified_fix": true,
        "verification_sources": ["osv", "changelog"],
        "command": "npm install lodash@4.17.21",
        "effort": "minimal"
      },
      {
        "from_version": "3.10.1",
        "to_version": "4.17.21",
        "semver": "major",
        "breaking_changes": true,
        "migration_guide": "https://github.com/lodash/lodash/wiki/Changelog",
        "effort": "significant"
      }
    ],

    "alternatives": [
      {
        "package": "lodash-es",
        "purl": "pkg:npm/lodash-es",
        "version": "4.17.21",
        "evaluation": {
          "license": "MIT",
          "license_compatible": true,
          "community_health": 0.85,
          "security_score": 0.95,
          "feature_parity": "high",
          "migration_effort": "low"
        },
        "recommendation": "Excellent alternative for ESM projects",
        "migration_steps": [
          "Replace 'lodash' with 'lodash-es' in imports",
          "Use named imports: import { map } from 'lodash-es'"
        ]
      },
      {
        "package": "remeda",
        "purl": "pkg:npm/remeda",
        "version": "1.29.0",
        "evaluation": {
          "license": "MIT",
          "license_compatible": true,
          "community_health": 0.72,
          "security_score": 1.0,
          "feature_parity": "medium",
          "migration_effort": "medium"
        },
        "recommendation": "Modern alternative with TypeScript-first design",
        "feature_gaps": ["Some lodash utilities not available"],
        "migration_steps": [
          "Review API differences at https://remedajs.com/",
          "Replace imports incrementally"
        ]
      }
    ],

    "not_recommended": [
      {
        "package": "underscore",
        "reason": "Has similar prototype pollution vulnerabilities",
        "reference": "CVE-2021-25949"
      }
    ],

    "workaround": {
      "available": true,
      "description": "Validate input before using _.template()",
      "effectiveness": "partial",
      "instructions": [
        "Never pass untrusted input directly to _.template()",
        "Sanitize template options object"
      ]
    }
  },

  "verification": {
    "fix_verified": true,
    "verification_date": "2024-01-15",
    "verification_method": "automated_testing",
    "test_results": "https://ccda.example.com/tests/CVE-2021-23337"
  }
}
```

---

## Part 6: Implementation Phases

### Phase 1: Foundation (Current + Enhancements)
- [x] Media collection (RSS, HN, Reddit)
- [x] Package identification agent
- [x] Risk relevance agent
- [x] Sentiment analyzer agent
- [x] GitHub repository metrics
- [ ] OSV/NVD integration
- [ ] CVSS score enrichment

### Phase 2: Security Metrics
- [ ] Security policy detection
- [ ] Branch protection check
- [ ] Signed release detection
- [ ] Dependency update tool detection
- [ ] Exploit status detection

### Phase 3: Remediation Knowledge Base
- [ ] Package version intelligence collector
- [ ] Verified fix mapping (OSV + AI verification)
- [ ] Fix verification agent
- [ ] Knowledge graph schema implementation
- [ ] Upgrade path generation

### Phase 4: Alternative Discovery & Evaluation
- [ ] Alternative discovery agent
- [ ] License compatibility checker
- [ ] Alternative evaluation agent
- [ ] Community health scoring for alternatives
- [ ] Migration effort estimation

### Phase 5: Advisory Generation
- [ ] Remediation recommendation engine
- [ ] Attack vector summarizer
- [ ] Advisory output format (JSON + Markdown)
- [ ] Timeline tracking
- [ ] "Not recommended" warnings

### Phase 6: Advanced Analytics
- [ ] Contributor retention
- [ ] Geographic diversity
- [ ] Time-to-first-response
- [ ] PR merge time analytics

### Phase 7: Knowledge Base Automation
- [ ] CVE feed monitoring → auto-update fixes
- [ ] New version monitoring → auto-verify fixes
- [ ] Abandoned package detection → auto-find alternatives
- [ ] License change detection → auto-evaluate alternatives
- [ ] Continuous knowledge base updates

### Phase 8: Maintainer & Account Monitoring
- [ ] Maintainer discovery from SBOM packages
- [ ] Activity tracking and baseline building
- [ ] Access level detection/inference
- [ ] Account age and reputation scoring
- [ ] Watchlist management
- [ ] Account anomaly detection agent
- [ ] Maintainer health reports
- [ ] Alert system for inactivity/compromise signals

### Phase 9: Organizational & Governance (OSBC Support)
- [ ] Company affiliation tracking from GitHub profiles
- [ ] License change detection with history tracking
- [ ] Foundation membership detection (ASF, CNCF, LF, Eclipse)
- [ ] PR acceptance/rejection tracking per author/company
- [ ] Governance structure parsing (GOVERNANCE.md, MAINTAINERS.md)
- [ ] Contributor recognition extraction from releases
- [ ] OSBC report output format
- [ ] Company-specific involvement dashboards

---

## Part 9: Data Acquisition Strategy

### 9.1 SBOM-Driven Collection Principle

Rather than building a universal database of all packages across all ecosystems (terabytes of data, API rate limit nightmares), CCDA operates on an **SBOM-first principle**:

```
User's SBOM → Extract unique PURLs → Collect metrics only for those packages
```

**Benefits:**
- Typical project scope: 100-500 packages vs millions in the wild
- GitHub API limits (5000/hr) become manageable
- Storage: megabytes instead of terabytes
- Update frequency can be hourly instead of weekly

**Implementation:**
```python
def collect_for_sbom(sbom_path: str):
    """
    Extract PURLs from SBOM and collect metrics only for those packages.
    """
    sbom = parse_sbom(sbom_path)  # CycloneDX or SPDX
    purls = extract_unique_purls(sbom)

    for purl in purls:
        # Query local bulk-loaded vulnerability database
        vulns = local_vuln_db.query(purl)

        # Query APIs only for packages we care about
        github_metrics = collect_github_metrics(purl)
        package_metadata = collect_registry_metadata(purl)

        yield PackageReport(purl, vulns, github_metrics, package_metadata)
```

---

### 9.2 Bulk Data Sources

These sources provide complete datasets for local querying, eliminating per-request API calls for vulnerability lookups.

#### OSV (Open Source Vulnerabilities)

| Attribute | Value |
|-----------|-------|
| **URL** | `gs://osv-vulnerabilities/all.zip` |
| **HTTP Access** | `https://storage.googleapis.com/osv-vulnerabilities/all.zip` |
| **Format** | JSON (one file per vulnerability) |
| **Size** | ~100-150 MB compressed |
| **Update Strategy** | Daily full download OR incremental via `modified_id.csv` |
| **License** | CC BY 4.0 |

**Per-Ecosystem Downloads:**
```bash
# Download only PyPI vulnerabilities
curl -O https://storage.googleapis.com/osv-vulnerabilities/PyPI/all.zip

# Or via gsutil
gsutil cp gs://osv-vulnerabilities/npm/all.zip .
```

**Incremental Sync:**
```python
def sync_osv_incremental():
    """
    Use modified_id.csv to fetch only changed vulnerabilities.
    CSV is sorted reverse-chronologically - stop when you hit a known timestamp.
    """
    modified = fetch_csv('gs://osv-vulnerabilities/modified_id.csv')

    for vuln_id, timestamp in modified:
        if timestamp <= last_sync_timestamp:
            break  # Already have this and everything before
        fetch_and_store_vulnerability(vuln_id)
```

---

#### NVD (National Vulnerability Database)

| Attribute | Value |
|-----------|-------|
| **URL** | `https://nvd.nist.gov/feeds/json/cve/2.0/` |
| **Format** | JSON (gzipped, one file per year + modified/recent) |
| **Size** | ~500 MB total (all years) |
| **Update Strategy** | Download yearly feeds once, sync "modified" feed every 2 hours |
| **License** | Public Domain |

**Feed Structure:**
```
nvdcve-2.0-2024.json.gz    (~18 MB) - All 2024 CVEs
nvdcve-2.0-2023.json.gz    (~15 MB) - All 2023 CVEs
...
nvdcve-2.0-modified.json.gz (~2 MB)  - Recently modified (rolling 8 days)
nvdcve-2.0-recent.json.gz   (~1 MB)  - Recently added (rolling 8 days)
```

**Sync Strategy:**
```python
def sync_nvd():
    """
    Initial: Download all yearly feeds.
    Daily: Download modified.json.gz and update changed CVEs.
    """
    # Check META file before downloading to avoid unnecessary requests
    meta = fetch(f'{NVD_BASE}/nvdcve-2.0-modified.meta')
    if meta['sha256'] != last_known_hash:
        modified = fetch_and_decompress(f'{NVD_BASE}/nvdcve-2.0-modified.json.gz')
        update_local_db(modified)
```

---

#### EPSS (Exploit Prediction Scoring System)

| Attribute | Value |
|-----------|-------|
| **URL** | `https://epss.cyentia.com/epss_scores-YYYY-MM-DD.csv.gz` |
| **Format** | CSV (gzipped) |
| **Size** | ~10 MB |
| **Update Strategy** | Daily download |
| **License** | Free to use |

**CSV Format:**
```csv
cve,epss,percentile
CVE-2024-1234,0.00123,0.45
CVE-2024-5678,0.89234,0.99
```

**Usage:**
```python
def load_epss_scores():
    """
    Load daily EPSS scores into local lookup table.
    """
    today = date.today().isoformat()
    url = f'https://epss.cyentia.com/epss_scores-{today}.csv.gz'

    scores = {}
    for row in read_gzipped_csv(url):
        scores[row['cve']] = {
            'epss': float(row['epss']),
            'percentile': float(row['percentile'])
        }
    return scores
```

---

#### Libraries.io (Historical Reference)

| Attribute | Value |
|-----------|-------|
| **URL** | [Zenodo](https://zenodo.org/records/3626071) / [Kaggle](https://www.kaggle.com/datasets/librariesdotio/libraries-io) |
| **Format** | CSV |
| **Size** | ~5 GB compressed, 25 GB uncompressed |
| **Last Updated** | January 2020 (stale) |
| **License** | CC BY-SA 4.0 |

**Contents:**
- 2.5M unique packages
- 9M tracked versions
- 39M tagged releases
- 25M repositories
- 100M declared dependencies

**Note:** This dataset is outdated but useful for historical analysis and as a seed for package discovery. For current data, use ecosyste.ms API.

---

### 9.3 API-Based Sources (SBOM-Scoped)

These sources require per-request API calls but should only be queried for packages in the user's SBOM.

#### ecosyste.ms

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://packages.ecosyste.ms/api/v1/` |
| **Coverage** | 12M+ packages across 78 registries |
| **Rate Limit** | Generous (undocumented, appears liberal) |
| **License** | CC BY-SA 4.0 (data), AGPL-3 (code) |

**Endpoints:**
```
GET /registries                           # List all supported registries
GET /registries/{registry}/packages/{name}  # Package metadata
GET /packages/{purl}                       # Query by PURL
```

**Key Data Provided:**
- Package metadata (description, keywords, license)
- Version history
- Maintainer information
- Download statistics
- Repository URL mapping
- Dependency information

**Usage:**
```python
def enrich_from_ecosystems(purl: str):
    """
    Fetch package metadata from ecosyste.ms
    """
    response = requests.get(
        f'https://packages.ecosyste.ms/api/v1/packages/{quote(purl)}'
    )
    if response.ok:
        return response.json()
    return None
```

---

#### GitHub API (Repository Metrics)

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://api.github.com/` |
| **Rate Limit** | 60/hr (unauth), 5000/hr (authenticated) |
| **Scope** | Only query repos referenced in SBOM |

**Optimization Strategy:**
```python
def batch_github_collection(purls: list[str]):
    """
    Collect GitHub metrics for all SBOM packages efficiently.
    """
    # 1. Resolve PURL → GitHub repo (use ecosyste.ms or registry APIs)
    repos = resolve_github_repos(purls)
    unique_repos = set(repos.values())

    # 2. Batch requests with rate limiting
    # Typical SBOM: 200 packages → 200 repos → ~40 minutes at 5000/hr
    for repo in unique_repos:
        metrics = collect_repo_metrics(repo)
        cache_metrics(repo, metrics)
```

---

#### Package Registries (Version Metadata)

| Registry | API | Bulk Alternative |
|----------|-----|------------------|
| **npm** | `registry.npmjs.org/{pkg}` | [Replicate API](https://github.com/npm/registry/blob/master/docs/REPLICATE-API.md) for full mirror |
| **PyPI** | `pypi.org/pypi/{pkg}/json` | [BigQuery dataset](https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads/) |
| **RubyGems** | `rubygems.org/api/v1/gems/{gem}.json` | [Data dump](https://rubygems.org/pages/data) (daily) |
| **crates.io** | `crates.io/api/v1/crates/{crate}` | [Database dump](https://static.crates.io/db-dump.tar.gz) (daily) |
| **Maven** | `search.maven.org/solrsearch/select` | No official bulk |
| **Go** | `proxy.golang.org/{module}/@v/list` | [Index](https://index.golang.org/index) (append-only log) |

---

### 9.4 Local Database Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LOCAL DATA LAYER                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 VULNERABILITY DATABASE                    │  │
│  │                    (DuckDB / SQLite)                      │  │
│  │                                                           │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │  │
│  │  │ OSV Table   │ │ NVD Table   │ │ EPSS Table          │ │  │
│  │  │ - vuln_id   │ │ - cve_id    │ │ - cve_id            │ │  │
│  │  │ - package   │ │ - cvss      │ │ - epss_score        │ │  │
│  │  │ - ecosystem │ │ - vector    │ │ - percentile        │ │  │
│  │  │ - versions  │ │ - published │ │ - date              │ │  │
│  │  │ - severity  │ │ - modified  │ │                     │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   QUERY INTERFACE                         │  │
│  │                                                           │  │
│  │  def get_vulnerabilities(purl: str) -> list[Vuln]:       │  │
│  │      osv_vulns = query_osv_table(purl)                   │  │
│  │      for vuln in osv_vulns:                              │  │
│  │          vuln.cvss = query_nvd_table(vuln.cve_id)        │  │
│  │          vuln.epss = query_epss_table(vuln.cve_id)       │  │
│  │      return osv_vulns                                     │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Recommended Database: DuckDB**
- Handles CSV/JSON ingestion natively
- Columnar storage efficient for analytical queries
- Single file, no server needed
- Fast PURL-based lookups

**Schema Example:**
```sql
CREATE TABLE osv_vulnerabilities (
    vuln_id VARCHAR PRIMARY KEY,
    ecosystem VARCHAR,
    package_name VARCHAR,
    affected_versions JSON,
    fixed_version VARCHAR,
    severity VARCHAR,
    summary TEXT,
    published TIMESTAMP,
    modified TIMESTAMP
);

CREATE INDEX idx_osv_package ON osv_vulnerabilities(ecosystem, package_name);

CREATE TABLE nvd_cves (
    cve_id VARCHAR PRIMARY KEY,
    cvss_v3_score DECIMAL(3,1),
    cvss_v3_vector VARCHAR,
    attack_vector VARCHAR,
    published TIMESTAMP,
    modified TIMESTAMP
);

CREATE TABLE epss_scores (
    cve_id VARCHAR PRIMARY KEY,
    epss_score DECIMAL(10,8),
    percentile DECIMAL(5,4),
    score_date DATE
);
```

---

### 9.5 Sync Schedule

| Source | Initial Load | Sync Frequency | Method |
|--------|--------------|----------------|--------|
| OSV | Full download | Daily | Incremental via modified_id.csv |
| NVD | All yearly feeds | Every 2 hours | modified.json.gz |
| EPSS | Full download | Daily | Full replacement |
| ecosyste.ms | On-demand | Per SBOM scan | API per package |
| GitHub | On-demand | Per SBOM scan | API per repo |

**Cron Schedule:**
```bash
# Daily at 2 AM: Sync OSV
0 2 * * * /opt/ccda/scripts/sync_osv.sh

# Every 2 hours: Sync NVD modified feed
0 */2 * * * /opt/ccda/scripts/sync_nvd_modified.sh

# Daily at 3 AM: Refresh EPSS scores
0 3 * * * /opt/ccda/scripts/sync_epss.sh
```

---

### 9.6 Data Tiering Summary

| Tier | Sources | Strategy | When |
|------|---------|----------|------|
| **Tier 1: Bulk Preload** | OSV, NVD, EPSS | Download to local DB | Background, scheduled |
| **Tier 2: SBOM-Scoped APIs** | GitHub, ecosyste.ms, registries | Query only for SBOM packages | On-demand per scan |
| **Tier 3: Media Monitoring** | RSS, HackerNews, Reddit | Continuous polling | Real-time |

This tiered approach ensures:
1. **Fast vulnerability lookups** - Local DB queries in milliseconds
2. **Minimal API usage** - Only query for packages you actually use
3. **Fresh data** - Daily/hourly syncs for security data
4. **Scalable** - Works for 50 packages or 5000 packages

---

## References

### APIs
- [GitHub REST API](https://docs.github.com/en/rest)
- [OSV API](https://osv.dev/docs/)
- [NVD API](https://nvd.nist.gov/developers/vulnerabilities)
- [EPSS API](https://www.first.org/epss/api)
- [ecosyste.ms](https://ecosyste.ms) - Package metadata across 78 registries

### Bulk Data Sources
- [OSV Bulk Data](https://google.github.io/osv.dev/data/) - GCS bucket `gs://osv-vulnerabilities/`
- [NVD Data Feeds](https://nvd.nist.gov/vuln/data-feeds) - JSON feeds by year
- [EPSS Daily Scores](https://www.first.org/epss/data_stats) - CSV downloads
- [Libraries.io on Zenodo](https://zenodo.org/records/3626071) - Historical package data
- [RubyGems Data Dumps](https://rubygems.org/pages/data) - Daily PostgreSQL dumps
- [crates.io Database Dump](https://static.crates.io/db-dump.tar.gz) - Daily
- [Go Module Index](https://index.golang.org/index) - Append-only log

### Standards
- [PURL Specification](https://github.com/package-url/purl-spec)
- [CVSS v3.1](https://www.first.org/cvss/v3.1/specification-document)
- [CycloneDX](https://cyclonedx.org/)

### Related CCDA Documents
- [BUSINESS_OVERVIEW.md](./BUSINESS_OVERVIEW.md) - High-level architecture, scoring model, competitive positioning
- [METRICS_COMPARISON.md](./METRICS_COMPARISON.md) - Gap analysis vs CHAOSS, OpenSSF Scorecard, Bitergia

### Implementation Guides (in /guides/)
- [scoring-system.md](../guides/scoring-system.md) - **Current scoring implementation** (risk, sentiment, relevance, action priority, OSS health)
- [ai-agent.md](../guides/ai-agent.md) - **AI package identification agent** details, PURL generation, multi-provider support
- [ai-package-identification.md](../guides/ai-package-identification.md) - Package extraction from text, confidence levels
- [data-collection-workflow.md](../guides/data-collection-workflow.md) - Complete data collection workflow, CLI commands
- [data-storage.md](../guides/data-storage.md) - **Storage structure**, file formats, retention policies
- [project-status.md](../guides/project-status.md) - Current implementation status, completed components
- [rss-feeds-list.md](../guides/rss-feeds-list.md) - Configured RSS feed sources
- [rotation-strategies.md](../guides/rotation-strategies.md) - Reddit/subreddit rotation strategy

### Industry Frameworks
- [CHAOSS Metrics](https://chaoss.community/metrics/) - Community health metrics definitions
- [OpenSSF Scorecard](https://securityscorecards.dev/) - Security best practices checks
- [SLSA Framework](https://slsa.dev/) - Supply chain security levels

---

*CCDA Metrics Implementation Specification - Draft v0.1 - December 2025*

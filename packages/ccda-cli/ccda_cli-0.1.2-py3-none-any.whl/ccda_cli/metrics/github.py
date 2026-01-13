"""GitHub API metrics collection.

Fetches metrics that cannot be extracted from git alone:
- Issues (open/closed, response times, labels)
- Pull requests (merge times, review activity)
- Releases (frequency, signatures)
- Branch protection status
- Repository metadata (stars, forks)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Any

from ccda_cli.config import get_config
from ccda_cli.core.http import GitHubClient, RateLimitInfo


@dataclass
class RepositoryMetrics:
    """Basic repository metadata."""

    stars: int = 0
    forks: int = 0
    watchers: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None
    default_branch: str = "main"
    license: str | None = None
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stars": self.stars,
            "forks": self.forks,
            "watchers": self.watchers,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "pushed_at": self.pushed_at.isoformat() if self.pushed_at else None,
            "default_branch": self.default_branch,
            "license": self.license,
            "topics": self.topics,
        }


@dataclass
class IssueMetrics:
    """Issue-related metrics."""

    open_count: int = 0
    closed_count: int = 0
    unresponded_rate_7d: float = 0.0
    unlabeled_rate: float = 0.0
    avg_response_hours: float = 0.0
    median_response_hours: float = 0.0
    avg_close_days: float = 0.0
    median_close_days: float = 0.0
    issue_backlog_score: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "open_count": self.open_count,
            "closed_count": self.closed_count,
            "unresponded_rate_7d": round(self.unresponded_rate_7d, 1),
            "unlabeled_rate": round(self.unlabeled_rate, 1),
            "avg_response_hours": round(self.avg_response_hours, 1),
            "median_response_hours": round(self.median_response_hours, 1),
            "avg_close_days": round(self.avg_close_days, 1),
            "median_close_days": round(self.median_close_days, 1),
            "issue_backlog_score": self.issue_backlog_score,
        }


@dataclass
class PullRequestMetrics:
    """Pull request metrics."""

    open_count: int = 0
    merged_count: int = 0
    closed_count: int = 0
    avg_merge_hours: float = 0.0
    median_merge_hours: float = 0.0
    avg_review_comments: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "open_count": self.open_count,
            "merged_count": self.merged_count,
            "closed_count": self.closed_count,
            "avg_merge_hours": round(self.avg_merge_hours, 1),
            "median_merge_hours": round(self.median_merge_hours, 1),
            "avg_review_comments": round(self.avg_review_comments, 1),
        }


@dataclass
class ReleaseMetrics:
    """Release-related metrics."""

    total_count: int = 0
    has_signed_releases: bool = False
    latest_release: dict[str, Any] | None = None
    release_frequency_days: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_count": self.total_count,
            "has_signed_releases": self.has_signed_releases,
            "latest_release": self.latest_release,
            "release_frequency_days": round(self.release_frequency_days, 1),
        }


@dataclass
class BranchProtection:
    """Branch protection status."""

    default_branch_protected: bool = False
    requires_pr_reviews: bool = False
    requires_status_checks: bool = False
    requires_signatures: bool = False
    enforces_admins: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "default_branch_protected": self.default_branch_protected,
            "requires_pr_reviews": self.requires_pr_reviews,
            "requires_status_checks": self.requires_status_checks,
            "requires_signatures": self.requires_signatures,
            "enforces_admins": self.enforces_admins,
        }


@dataclass
class GitHubMetricsResult:
    """Complete GitHub API metrics result."""

    repo_url: str
    fetched_at: datetime
    method: str = "github_api"
    ttl_hours: int = 6
    api_calls_used: int = 0
    rate_limit: RateLimitInfo | None = None

    repository: RepositoryMetrics = field(default_factory=RepositoryMetrics)
    issues: IssueMetrics = field(default_factory=IssueMetrics)
    pull_requests: PullRequestMetrics = field(default_factory=PullRequestMetrics)
    releases: ReleaseMetrics = field(default_factory=ReleaseMetrics)
    branch_protection: BranchProtection = field(default_factory=BranchProtection)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "repo_url": self.repo_url,
            "fetched_at": self.fetched_at.isoformat(),
            "method": self.method,
            "ttl_hours": self.ttl_hours,
            "api_calls_used": self.api_calls_used,
            "rate_limit": {
                "remaining": self.rate_limit.remaining if self.rate_limit else 0,
                "limit": self.rate_limit.limit if self.rate_limit else 0,
                "reset_at": (
                    self.rate_limit.reset_at.isoformat()
                    if self.rate_limit and self.rate_limit.reset_at
                    else None
                ),
            },
            "repository": self.repository.to_dict(),
            "issues": self.issues.to_dict(),
            "pull_requests": self.pull_requests.to_dict(),
            "releases": self.releases.to_dict(),
            "branch_protection": self.branch_protection.to_dict(),
        }


class GitHubMetricsCollector:
    """Collects metrics from GitHub API."""

    def __init__(self, token: str | None = None):
        """Initialize collector with optional token.

        Args:
            token: GitHub API token (uses config if not provided)
        """
        config = get_config()
        self.token = token or config.github_token
        self.client = GitHubClient(token=self.token)
        self._api_calls = 0

    async def collect(self, repo_url: str) -> GitHubMetricsResult:
        """Collect all GitHub metrics for a repository.

        Args:
            repo_url: GitHub repository URL

        Returns:
            GitHubMetricsResult with all metrics
        """
        owner, repo = self._parse_repo_url(repo_url)

        result = GitHubMetricsResult(
            repo_url=repo_url,
            fetched_at=datetime.now(),
        )

        async with self.client.session():
            # Get repository info
            await self._collect_repository_info(owner, repo, result)

            # Get issues
            await self._collect_issue_metrics(owner, repo, result)

            # Get pull requests
            await self._collect_pr_metrics(owner, repo, result)

            # Get releases
            await self._collect_release_metrics(owner, repo, result)

            # Get branch protection
            await self._collect_branch_protection(owner, repo, result)

            # Update API call count and rate limit
            result.api_calls_used = self._api_calls
            result.rate_limit = self.client.rate_limit

        return result

    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Parse owner and repo from GitHub URL."""
        patterns = [
            r"github\.com/([^/]+)/([^/\.]+)",
            r"github\.com/([^/]+)/([^/]+)\.git",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.groups()

        raise ValueError(f"Could not parse GitHub URL: {url}")

    async def _collect_repository_info(
        self, owner: str, repo: str, result: GitHubMetricsResult
    ) -> None:
        """Collect basic repository information."""
        try:
            response = await self.client.get_repo(owner, repo)
            self._api_calls += 1

            if response.status_code == 200:
                data = response.data

                result.repository = RepositoryMetrics(
                    stars=data.get("stargazers_count", 0),
                    forks=data.get("forks_count", 0),
                    watchers=data.get("subscribers_count", 0),
                    created_at=self._parse_date(data.get("created_at")),
                    updated_at=self._parse_date(data.get("updated_at")),
                    pushed_at=self._parse_date(data.get("pushed_at")),
                    default_branch=data.get("default_branch", "main"),
                    license=(
                        data.get("license", {}).get("spdx_id")
                        if data.get("license")
                        else None
                    ),
                    topics=data.get("topics", []),
                )
                # Store open_issues_count for later (includes PRs, but we'll adjust)
                result._repo_open_issues_count = data.get("open_issues_count", 0)

        except Exception:
            pass

    async def _collect_issue_metrics(
        self, owner: str, repo: str, result: GitHubMetricsResult
    ) -> None:
        """Collect issue metrics."""
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)

        open_issues = []
        closed_issues = []
        response_times = []
        close_times = []
        unresponded_count = 0
        unlabeled_count = 0

        try:
            # Get open issues (up to 300)
            for page in range(1, 4):
                response = await self.client.get_issues(
                    owner, repo, state="open", per_page=100, page=page
                )
                self._api_calls += 1

                if response.status_code != 200:
                    break

                issues = [i for i in response.data if "pull_request" not in i]
                if not issues:
                    break

                for issue in issues:
                    open_issues.append(issue)

                    # Check if unresponded (no comments, created > 7 days ago)
                    created = self._parse_date(issue.get("created_at"))
                    if created and created < seven_days_ago:
                        if issue.get("comments", 0) == 0:
                            unresponded_count += 1

                    # Check if unlabeled
                    if not issue.get("labels"):
                        unlabeled_count += 1

                if len(issues) < 100:
                    break

            # Get closed issues (sample for response/close times)
            for page in range(1, 3):
                response = await self.client.get_issues(
                    owner, repo, state="closed", per_page=100, page=page
                )
                self._api_calls += 1

                if response.status_code != 200:
                    break

                issues = [i for i in response.data if "pull_request" not in i]
                if not issues:
                    break

                for issue in issues:
                    closed_issues.append(issue)

                    created = self._parse_date(issue.get("created_at"))
                    closed = self._parse_date(issue.get("closed_at"))

                    if created and closed:
                        close_time = (closed - created).total_seconds() / 86400  # days
                        close_times.append(close_time)

                if len(issues) < 100:
                    break

            # Calculate metrics
            # Use actual count from repo API if available, otherwise use sampled count
            # Note: repo's open_issues_count includes PRs, we'll adjust after PR collection
            result.issues.open_count = getattr(result, '_repo_open_issues_count', len(open_issues))
            result.issues.closed_count = len(closed_issues)
            result.issues._sampled_open_count = len(open_issues)  # Keep sample for rate calculations

            if open_issues:
                result.issues.unresponded_rate_7d = (
                    unresponded_count / len(open_issues)
                ) * 100
                result.issues.unlabeled_rate = (
                    unlabeled_count / len(open_issues)
                ) * 100

            if close_times:
                result.issues.avg_close_days = mean(close_times)
                result.issues.median_close_days = median(close_times)

            # Calculate backlog score
            result.issues.issue_backlog_score = self._calculate_backlog_score(
                len(open_issues)
            )

        except Exception:
            pass

    async def _collect_pr_metrics(
        self, owner: str, repo: str, result: GitHubMetricsResult
    ) -> None:
        """Collect pull request metrics."""
        merge_times = []
        open_count = 0
        merged_count = 0
        closed_count = 0

        try:
            # Get PRs (up to 300)
            for page in range(1, 4):
                response = await self.client.get_pulls(
                    owner, repo, state="all", per_page=100, page=page
                )
                self._api_calls += 1

                if response.status_code != 200:
                    break

                prs = response.data
                if not prs:
                    break

                for pr in prs:
                    state = pr.get("state")
                    merged = pr.get("merged_at")

                    if state == "open":
                        open_count += 1
                    elif merged:
                        merged_count += 1
                        created = self._parse_date(pr.get("created_at"))
                        merged_at = self._parse_date(merged)
                        if created and merged_at:
                            hours = (merged_at - created).total_seconds() / 3600
                            merge_times.append(hours)
                    else:
                        closed_count += 1

                if len(prs) < 100:
                    break

            result.pull_requests.open_count = open_count
            result.pull_requests.merged_count = merged_count
            result.pull_requests.closed_count = closed_count

            # Adjust issue open_count: repo's open_issues_count includes PRs
            # Subtract open PRs to get actual issue count
            if hasattr(result, '_repo_open_issues_count') and result._repo_open_issues_count > 0:
                adjusted_issues = result._repo_open_issues_count - open_count
                if adjusted_issues > 0:
                    result.issues.open_count = adjusted_issues

            if merge_times:
                result.pull_requests.avg_merge_hours = mean(merge_times)
                result.pull_requests.median_merge_hours = median(merge_times)

        except Exception:
            pass

    async def _collect_release_metrics(
        self, owner: str, repo: str, result: GitHubMetricsResult
    ) -> None:
        """Collect release metrics."""
        releases = []
        has_signed = False

        try:
            for page in range(1, 3):
                response = await self.client.get_releases(
                    owner, repo, per_page=100, page=page
                )
                self._api_calls += 1

                if response.status_code != 200:
                    break

                page_releases = response.data
                if not page_releases:
                    break

                for release in page_releases:
                    releases.append(release)

                    # Check for signed assets
                    assets = release.get("assets", [])
                    for asset in assets:
                        name = asset.get("name", "").lower()
                        if ".sig" in name or ".asc" in name or "signature" in name:
                            has_signed = True
                            break

                if len(page_releases) < 100:
                    break

            result.releases.total_count = len(releases)
            result.releases.has_signed_releases = has_signed

            if releases:
                latest = releases[0]
                result.releases.latest_release = {
                    "tag": latest.get("tag_name"),
                    "published_at": latest.get("published_at"),
                    "prerelease": latest.get("prerelease", False),
                }

                # Calculate release frequency
                if len(releases) >= 2:
                    dates = []
                    for release in releases:
                        pub_date = self._parse_date(release.get("published_at"))
                        if pub_date:
                            dates.append(pub_date)

                    if len(dates) >= 2:
                        dates.sort(reverse=True)
                        intervals = []
                        for i in range(len(dates) - 1):
                            interval = (dates[i] - dates[i + 1]).days
                            intervals.append(interval)
                        if intervals:
                            result.releases.release_frequency_days = mean(intervals)

        except Exception:
            pass

    async def _collect_branch_protection(
        self, owner: str, repo: str, result: GitHubMetricsResult
    ) -> None:
        """Collect branch protection status."""
        default_branch = result.repository.default_branch

        try:
            response = await self.client.get_branch_protection(
                owner, repo, default_branch
            )
            self._api_calls += 1

            if response.status_code == 200:
                data = response.data
                result.branch_protection.default_branch_protected = True

                # Check PR reviews
                pr_reviews = data.get("required_pull_request_reviews", {})
                if pr_reviews:
                    result.branch_protection.requires_pr_reviews = True

                # Check status checks
                status_checks = data.get("required_status_checks", {})
                if status_checks:
                    result.branch_protection.requires_status_checks = True

                # Check signatures
                if data.get("required_signatures", {}).get("enabled"):
                    result.branch_protection.requires_signatures = True

                # Check admin enforcement
                if data.get("enforce_admins", {}).get("enabled"):
                    result.branch_protection.enforces_admins = True

            elif response.status_code == 404:
                # No protection configured
                result.branch_protection.default_branch_protected = False

        except Exception:
            pass

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse ISO date string to datetime."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            return None

    def _calculate_backlog_score(self, open_count: int) -> int:
        """Calculate issue backlog score (0-20 for burnout)."""
        if open_count <= 100:
            return 0
        elif open_count <= 500:
            return 5
        elif open_count <= 1000:
            return 10
        elif open_count <= 2500:
            return 15
        else:
            return 20

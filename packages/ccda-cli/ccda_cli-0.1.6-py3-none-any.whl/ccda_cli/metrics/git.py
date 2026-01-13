"""Git-based metrics analysis.

Analyzes git history to extract:
- Bus factor: Minimum developers needed to lose 50%+ of commits
- Pony factor: Number of developers contributing 50% of commits (CHAOSS)
- Elephant factor: Number of companies contributing 50% of commits
- Contributor retention: Percentage of contributors remaining active
- Commit activity and velocity
- License change history
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ccda_cli.config import get_config
from ccda_cli.enrichment.company import CompanyEnricher


@dataclass
class ContributorStats:
    """Statistics for a single contributor."""

    email: str
    name: str
    commits: int = 0
    percentage: float = 0.0
    company: str = "Independent"
    first_commit: datetime | None = None
    last_commit: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContributorStats":
        """Create from dictionary."""
        return cls(
            email=data.get("email", ""),
            name=data.get("name", ""),
            commits=data.get("commits", 0),
            percentage=data.get("percentage", 0.0),
            company=data.get("company", "Independent"),
        )


@dataclass
class CompanyStats:
    """Statistics for a company/organization."""

    company: str
    commits: int = 0
    percentage: float = 0.0
    contributors: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanyStats":
        """Create from dictionary."""
        return cls(
            company=data.get("company", "Unknown"),
            commits=data.get("commits", 0),
            percentage=data.get("percentage", 0.0),
            contributors=data.get("contributors", 0),
        )


@dataclass
class LicenseChange:
    """Record of a license change."""

    commit_hash: str
    date: datetime
    old_license: str | None
    new_license: str
    author: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LicenseChange":
        """Create from dictionary."""
        date = data.get("date", "")
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace("Z", "+00:00")) if date else datetime.now()
        return cls(
            commit_hash=data.get("commit_hash", ""),
            date=date,
            old_license=data.get("old_license"),
            new_license=data.get("new_license", ""),
            author=data.get("author", ""),
        )


@dataclass
class TimeWindowMetrics:
    """Metrics for a specific time window."""

    start_date: datetime
    end_date: datetime
    total_commits: int = 0
    unique_contributors: int = 0
    bus_factor: int = 0
    pony_factor: int = 0
    elephant_factor: int = 0
    contributor_retention: float = 0.0
    commits_per_day: float = 0.0
    days_since_last_commit: float = 0.0
    top_contributors: list[ContributorStats] = field(default_factory=list)
    company_distribution: list[CompanyStats] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_commits": self.total_commits,
            "unique_contributors": self.unique_contributors,
            "bus_factor": self.bus_factor,
            "pony_factor": self.pony_factor,
            "elephant_factor": self.elephant_factor,
            "contributor_retention": self.contributor_retention,
            "commits_per_day": round(self.commits_per_day, 2),
            "days_since_last_commit": round(self.days_since_last_commit, 1),
            "top_contributors": [
                {
                    "email": c.email,
                    "name": c.name,
                    "company": c.company,
                    "commits": c.commits,
                    "percentage": round(c.percentage, 2),
                }
                for c in self.top_contributors[:10]
            ],
            "company_distribution": [
                {
                    "company": c.company,
                    "commits": c.commits,
                    "percentage": round(c.percentage, 2),
                    "contributors": c.contributors,
                }
                for c in self.company_distribution
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimeWindowMetrics":
        """Create from dictionary."""
        start = data.get("start_date", "")
        end = data.get("end_date", "")
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00")) if start else datetime.now()
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace("Z", "+00:00")) if end else datetime.now()

        return cls(
            start_date=start,
            end_date=end,
            total_commits=data.get("total_commits", 0),
            unique_contributors=data.get("unique_contributors", 0),
            bus_factor=data.get("bus_factor", 0),
            pony_factor=data.get("pony_factor", 0),
            elephant_factor=data.get("elephant_factor", 0),
            contributor_retention=data.get("contributor_retention", 0.0),
            commits_per_day=data.get("commits_per_day", 0.0),
            days_since_last_commit=data.get("days_since_last_commit", 0.0),
            top_contributors=[
                ContributorStats.from_dict(c) for c in data.get("top_contributors", [])
            ],
            company_distribution=[
                CompanyStats.from_dict(c) for c in data.get("company_distribution", [])
            ],
        )


@dataclass
class LicenseHistory:
    """License change tracking."""

    license_file: str | None = None
    current_license: str | None = None
    change_count: int = 0
    changes: list[LicenseChange] = field(default_factory=list)
    risk_level: str = "low"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "license_file": self.license_file,
            "current_license": self.current_license,
            "change_count": self.change_count,
            "changes": [
                {
                    "commit_hash": c.commit_hash,
                    "date": c.date.isoformat(),
                    "old_license": c.old_license,
                    "new_license": c.new_license,
                }
                for c in self.changes
            ],
            "risk_level": self.risk_level,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LicenseHistory":
        """Create from dictionary."""
        return cls(
            license_file=data.get("license_file"),
            current_license=data.get("current_license"),
            change_count=data.get("change_count", 0),
            changes=[LicenseChange.from_dict(c) for c in data.get("changes", [])],
            risk_level=data.get("risk_level", "low"),
        )


@dataclass
class GitMetricsResult:
    """Complete git metrics analysis result."""

    repo_url: str
    clone_path: str
    analyzed_at: datetime
    method: str = "git_offline"
    ttl_hours: int = 24
    time_windows: dict[str, TimeWindowMetrics] = field(default_factory=dict)
    license_changes: LicenseHistory = field(default_factory=LicenseHistory)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "repo_url": self.repo_url,
            "analyzed_at": self.analyzed_at.isoformat(),
            "method": self.method,
            "clone_path": self.clone_path,
            "ttl_hours": self.ttl_hours,
            "time_windows": {k: v.to_dict() for k, v in self.time_windows.items()},
            "license_changes": self.license_changes.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GitMetricsResult":
        """Create from dictionary."""
        analyzed = data.get("analyzed_at", "")
        if isinstance(analyzed, str):
            analyzed = datetime.fromisoformat(analyzed.replace("Z", "+00:00")) if analyzed else datetime.now()

        return cls(
            repo_url=data.get("repo_url", ""),
            clone_path=data.get("clone_path", ""),
            analyzed_at=analyzed,
            method=data.get("method", "git_offline"),
            ttl_hours=data.get("ttl_hours", 24),
            time_windows={
                k: TimeWindowMetrics.from_dict(v)
                for k, v in data.get("time_windows", {}).items()
            },
            license_changes=LicenseHistory.from_dict(data.get("license_changes", {})),
        )


class GitMetricsAnalyzer:
    """Analyzes git repositories for community health metrics."""

    # License file patterns
    LICENSE_FILES = [
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENCE",
        "COPYING",
        "COPYING.txt",
    ]

    def __init__(self, repo_path: Path, github_token: str | None = None):
        """Initialize analyzer with repository path.

        Args:
            repo_path: Path to the git repository
            github_token: Optional GitHub token for company enrichment
        """
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

        self.config = get_config()
        self._company_cache: dict[str, str] = {}
        self._enricher = CompanyEnricher(github_token=github_token or self.config.github_token)

    def analyze(self, repo_url: str | None = None) -> GitMetricsResult:
        """Run full git metrics analysis.

        Args:
            repo_url: Optional repository URL for metadata

        Returns:
            GitMetricsResult with all metrics
        """
        now = datetime.now()

        # Get all commits
        commits = self._get_commits()

        if not commits:
            return GitMetricsResult(
                repo_url=repo_url or str(self.repo_path),
                clone_path=str(self.repo_path),
                analyzed_at=now,
            )

        # Enrich contributor data with GitHub company information
        self._enrich_contributors(commits)

        result = GitMetricsResult(
            repo_url=repo_url or self._get_remote_url() or str(self.repo_path),
            clone_path=str(self.repo_path),
            analyzed_at=now,
        )

        # Analyze time windows
        for window in self.config.analysis.time_windows:
            if window.days:
                start_date = now - timedelta(days=window.days)
            else:
                start_date = datetime.min

            window_commits = [c for c in commits if c["date"] >= start_date]
            metrics = self._analyze_window(window_commits, start_date, now)

            # Calculate retention (compare current window to previous)
            if window.days:
                prev_start = start_date - timedelta(days=window.days)
                prev_commits = [
                    c for c in commits if prev_start <= c["date"] < start_date
                ]
                metrics.contributor_retention = self._calculate_retention(
                    prev_commits, window_commits
                )

            result.time_windows[window.name] = metrics

        # Analyze license changes
        result.license_changes = self._analyze_license_history()

        return result

    def _get_commits(self) -> list[dict[str, Any]]:
        """Get all commits from git log."""
        # Format: hash|author_email|author_name|date
        cmd = [
            "git",
            "log",
            "--format=%H|%ae|%an|%aI",
            "--no-merges",
        ]

        try:
            output = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if output.returncode != 0:
                return []

            commits = []
            for line in output.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    try:
                        date = datetime.fromisoformat(parts[3].replace("Z", "+00:00"))
                        # Convert to naive datetime for comparison
                        date = date.replace(tzinfo=None)
                    except ValueError:
                        date = datetime.now()

                    commits.append(
                        {
                            "hash": parts[0],
                            "email": parts[1].lower(),
                            "name": parts[2],
                            "date": date,
                        }
                    )

            return commits

        except subprocess.TimeoutExpired:
            return []
        except Exception:
            return []

    def _analyze_window(
        self,
        commits: list[dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
    ) -> TimeWindowMetrics:
        """Analyze commits within a time window."""
        metrics = TimeWindowMetrics(start_date=start_date, end_date=end_date)

        if not commits:
            return metrics

        metrics.total_commits = len(commits)

        # Group commits by contributor
        contributor_commits: dict[str, ContributorStats] = {}
        for commit in commits:
            email = commit["email"]
            if email not in contributor_commits:
                contributor_commits[email] = ContributorStats(
                    email=email,
                    name=commit["name"],
                    company=self._get_company(email),
                    first_commit=commit["date"],
                    last_commit=commit["date"],
                )
            stats = contributor_commits[email]
            stats.commits += 1
            if commit["date"] < stats.first_commit:
                stats.first_commit = commit["date"]
            if commit["date"] > stats.last_commit:
                stats.last_commit = commit["date"]

        metrics.unique_contributors = len(contributor_commits)

        # Calculate percentages
        for stats in contributor_commits.values():
            stats.percentage = (stats.commits / metrics.total_commits) * 100

        # Sort by commits descending
        sorted_contributors = sorted(
            contributor_commits.values(), key=lambda x: x.commits, reverse=True
        )
        metrics.top_contributors = sorted_contributors

        # Calculate bus factor (min developers to lose 50%+ commits)
        metrics.bus_factor = self._calculate_factor(sorted_contributors, 50)

        # Pony factor is same as bus factor in CHAOSS
        metrics.pony_factor = metrics.bus_factor

        # Calculate elephant factor (companies contributing 50%)
        company_commits: dict[str, CompanyStats] = {}
        for stats in sorted_contributors:
            company = stats.company
            if company not in company_commits:
                company_commits[company] = CompanyStats(company=company)
            company_commits[company].commits += stats.commits
            company_commits[company].contributors += 1

        for company_stats in company_commits.values():
            company_stats.percentage = (
                company_stats.commits / metrics.total_commits
            ) * 100

        sorted_companies = sorted(
            company_commits.values(), key=lambda x: x.commits, reverse=True
        )
        metrics.company_distribution = sorted_companies

        company_list = [
            ContributorStats(
                email="",
                name=c.company,
                commits=c.commits,
                percentage=c.percentage,
            )
            for c in sorted_companies
        ]
        metrics.elephant_factor = self._calculate_factor(company_list, 50)

        # Calculate activity metrics
        days = (end_date - start_date).days or 1
        metrics.commits_per_day = metrics.total_commits / days

        if commits:
            last_commit_date = max(c["date"] for c in commits)
            metrics.days_since_last_commit = (end_date - last_commit_date).days

        return metrics

    def _calculate_factor(
        self, sorted_items: list[ContributorStats], threshold: float
    ) -> int:
        """Calculate bus/pony/elephant factor.

        Returns the minimum number of items needed to reach threshold% of commits.
        """
        if not sorted_items:
            return 0

        total = sum(item.commits for item in sorted_items)
        if total == 0:
            return 0

        cumulative = 0
        count = 0

        for item in sorted_items:
            cumulative += item.commits
            count += 1
            if (cumulative / total) * 100 >= threshold:
                return count

        return count

    def _calculate_retention(
        self,
        prev_commits: list[dict[str, Any]],
        current_commits: list[dict[str, Any]],
    ) -> float:
        """Calculate contributor retention between time windows."""
        if not prev_commits:
            return 0.0

        prev_contributors = {c["email"] for c in prev_commits}
        current_contributors = {c["email"] for c in current_commits}

        if not prev_contributors:
            return 0.0

        retained = prev_contributors & current_contributors
        return (len(retained) / len(prev_contributors)) * 100

    def _enrich_contributors(self, commits: list[dict[str, Any]]) -> None:
        """Enrich contributor data with GitHub company information.

        This method collects all unique contributors and enriches them
        in a batch operation to minimize API calls.

        Args:
            commits: List of commit dicts with email and name
        """
        if not self._enricher.is_enabled():
            return

        # Collect unique contributors
        contributors: dict[str, dict[str, Any]] = {}
        for commit in commits:
            email = commit["email"]
            if email not in contributors:
                contributors[email] = {
                    "name": commit["name"],
                    "company": "Independent",  # Default
                }

        # Run async enrichment
        try:
            asyncio.run(self._enricher.enrich_contributors(contributors))

            # Update cache with results
            for email, data in contributors.items():
                self._company_cache[email] = data["company"]

        except Exception:
            # If enrichment fails, fall back to email domain detection
            # This is already the default behavior in _get_company
            pass

    def _get_company(self, email: str) -> str:
        """Determine company affiliation.

        Uses enriched data from GitHub API if available, otherwise falls back
        to email domain mapping.

        Args:
            email: Contributor email

        Returns:
            Company name or "Independent"
        """
        if email in self._company_cache:
            return self._company_cache[email]

        # Use enricher to get company (will use cache or email domain)
        company = self._enricher.get_company(email)
        self._company_cache[email] = company
        return company

    def _get_remote_url(self) -> str | None:
        """Get the remote origin URL."""
        try:
            output = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if output.returncode == 0:
                url = output.stdout.strip()
                # Convert SSH to HTTPS
                if url.startswith("git@"):
                    url = re.sub(r"git@([^:]+):", r"https://\1/", url)
                if url.endswith(".git"):
                    url = url[:-4]
                return url
        except Exception:
            pass
        return None

    def _analyze_license_history(self) -> LicenseHistory:
        """Analyze license file changes in git history."""
        history = LicenseHistory()

        # Find current license file
        for license_file in self.LICENSE_FILES:
            license_path = self.repo_path / license_file
            if license_path.exists():
                history.license_file = license_file
                # Try to detect license type
                try:
                    content = license_path.read_text()[:1000].lower()
                    history.current_license = self._detect_license(content)
                except Exception:
                    pass
                break

        if not history.license_file:
            return history

        # Get commits that modified the license file
        try:
            cmd = [
                "git",
                "log",
                "--format=%H|%aI|%an",
                "--follow",
                "--",
                history.license_file,
            ]
            output = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if output.returncode == 0:
                commits = output.stdout.strip().split("\n")
                history.change_count = len([c for c in commits if c])

                # Analyze each change
                for line in commits[:10]:  # Limit to last 10 changes
                    if not line:
                        continue
                    parts = line.split("|", 2)
                    if len(parts) >= 3:
                        try:
                            date = datetime.fromisoformat(
                                parts[1].replace("Z", "+00:00")
                            ).replace(tzinfo=None)
                        except ValueError:
                            date = datetime.now()

                        change = LicenseChange(
                            commit_hash=parts[0][:7],
                            date=date,
                            old_license=None,  # Would need diff analysis
                            new_license=history.current_license or "Unknown",
                            author=parts[2],
                        )
                        history.changes.append(change)

        except Exception:
            pass

        # Assess risk level
        if history.change_count > 3:
            history.risk_level = "high"
        elif history.change_count > 1:
            history.risk_level = "medium"
        else:
            history.risk_level = "low"

        return history

    def _detect_license(self, content: str) -> str:
        """Detect license type from content."""
        content = content.lower()

        license_patterns = [
            ("MIT", ["mit license", "permission is hereby granted, free of charge"]),
            ("Apache-2.0", ["apache license", "version 2.0"]),
            ("GPL-3.0", ["gnu general public license", "version 3"]),
            ("GPL-2.0", ["gnu general public license", "version 2"]),
            ("BSD-3-Clause", ["redistribution and use", "3-clause", "three conditions"]),
            ("BSD-2-Clause", ["redistribution and use", "2-clause", "two conditions"]),
            ("ISC", ["isc license", "permission to use, copy, modify"]),
            ("MPL-2.0", ["mozilla public license", "version 2.0"]),
            ("LGPL-3.0", ["gnu lesser general public license", "version 3"]),
            ("Unlicense", ["unlicense", "public domain"]),
        ]

        for license_id, patterns in license_patterns:
            if all(p in content for p in patterns[:1]):
                return license_id

        return "Unknown"

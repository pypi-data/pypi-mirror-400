"""Developer burnout risk score calculation.

Analyzes workload, responsiveness, and sustainability to calculate
a burnout risk score (0-100, lower is better).

Components (each 0-20 points):
1. Issue Backlog: Based on open issues count
2. Response Gap: Percentage of issues unresponded >7 days
3. Triage Overhead: Percentage of unlabeled issues
4. Workload Concentration: How concentrated work is among contributors
5. Activity Decline: Trend in commit/PR activity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ccda_cli.config import get_config
from ccda_cli.metrics.git import GitMetricsResult
from ccda_cli.metrics.github import GitHubMetricsResult


@dataclass
class BurnoutComponent:
    """Score for a burnout risk component."""

    name: str
    score: int  # 0-20
    max_score: int = 20
    status: str = "healthy"  # healthy, moderate, warning, critical
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "max_score": self.max_score,
            "status": self.status,
            **self.details,
        }


@dataclass
class MaintainerHealth:
    """Maintainer health indicators."""

    contributor_retention_90d: float = 0.0
    pony_factor_90d: int = 0
    elephant_factor_90d: int = 0
    unique_contributors_90d: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "contributor_retention_90d": round(self.contributor_retention_90d, 1),
            "pony_factor_90d": self.pony_factor_90d,
            "elephant_factor_90d": self.elephant_factor_90d,
            "unique_contributors_90d": self.unique_contributors_90d,
        }


@dataclass
class BurnoutScoreResult:
    """Burnout score calculation result."""

    purl: str
    calculated_at: datetime
    ttl_hours: int = 6

    burnout_score: int = 0  # 0-100 (lower is better)
    grade: str = "A"
    risk_level: str = "low"

    components: dict[str, BurnoutComponent] = field(default_factory=dict)
    maintainer_health: MaintainerHealth = field(default_factory=MaintainerHealth)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "purl": self.purl,
            "calculated_at": self.calculated_at.isoformat(),
            "ttl_hours": self.ttl_hours,
            "burnout_score": self.burnout_score,
            "risk_level": self.risk_level,
            "grade": self.grade,
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "maintainer_health": self.maintainer_health.to_dict(),
            "recommendations": self.recommendations,
        }


class BurnoutScoreCalculator:
    """Calculates developer burnout risk score."""

    # Grade thresholds (lower score = better grade)
    GRADES = [
        (20, "A"),
        (40, "B"),
        (60, "C"),
        (80, "D"),
        (100, "F"),
    ]

    # Risk level thresholds
    RISK_LEVELS = [
        (20, "low"),
        (40, "medium"),
        (60, "high"),
        (100, "critical"),
    ]

    # Issue backlog thresholds
    ISSUE_BACKLOG_THRESHOLDS = [
        (100, 0),
        (500, 5),
        (1000, 10),
        (2500, 15),
        (float("inf"), 20),
    ]

    # Response gap thresholds (percentage)
    RESPONSE_GAP_THRESHOLDS = [
        (10, 0),
        (20, 5),
        (30, 10),
        (50, 15),
        (float("inf"), 20),
    ]

    # Triage overhead thresholds (percentage)
    TRIAGE_OVERHEAD_THRESHOLDS = [
        (5, 0),
        (15, 5),
        (30, 10),
        (50, 15),
        (float("inf"), 20),
    ]

    # Pony factor thresholds
    PONY_FACTOR_THRESHOLDS = [
        (10, 0),
        (6, 5),
        (3, 10),
        (2, 15),
        (1, 20),
    ]

    # Activity decline thresholds (percentage change)
    ACTIVITY_DECLINE_THRESHOLDS = [
        (-10, 0),  # Growing
        (10, 5),   # Stable
        (30, 10),  # Declining
        (50, 15),  # Significantly declining
        (float("inf"), 20),  # Severely declining
    ]

    def __init__(self):
        """Initialize calculator."""
        self.config = get_config()

    def calculate(
        self,
        purl: str,
        git_metrics: GitMetricsResult | None = None,
        github_metrics: GitHubMetricsResult | None = None,
    ) -> BurnoutScoreResult:
        """Calculate burnout risk score from metrics.

        Args:
            purl: Package URL
            git_metrics: Git analysis results
            github_metrics: GitHub API results

        Returns:
            BurnoutScoreResult with score and details
        """
        result = BurnoutScoreResult(
            purl=purl,
            calculated_at=datetime.now(),
        )

        # Calculate components
        if github_metrics:
            self._score_issue_backlog(github_metrics, result)
            self._score_response_gap(github_metrics, result)
            self._score_triage_overhead(github_metrics, result)

        if git_metrics:
            self._score_workload_concentration(git_metrics, result)
            self._score_activity_decline(git_metrics, result)
            self._extract_maintainer_health(git_metrics, result)

        # Calculate total score
        total_score = sum(c.score for c in result.components.values())
        result.burnout_score = min(100, total_score)

        # Assign grade and risk level
        result.grade = self._get_grade(result.burnout_score)
        result.risk_level = self._get_risk_level(result.burnout_score)

        # Generate recommendations
        self._generate_recommendations(result)

        return result

    def _score_issue_backlog(
        self, github_metrics: GitHubMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Score based on issue backlog size."""
        open_issues = github_metrics.issues.open_count

        score = 0
        for threshold, points in self.ISSUE_BACKLOG_THRESHOLDS:
            if open_issues <= threshold:
                score = points
                break

        status = self._get_status(score)

        result.components["issue_backlog"] = BurnoutComponent(
            name="issue_backlog",
            score=score,
            status=status,
            details={
                "open_issues": open_issues,
            },
        )

    def _score_response_gap(
        self, github_metrics: GitHubMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Score based on unresponded issues rate."""
        unresponded_rate = github_metrics.issues.unresponded_rate_7d

        score = 0
        for threshold, points in self.RESPONSE_GAP_THRESHOLDS:
            if unresponded_rate <= threshold:
                score = points
                break

        status = self._get_status(score)

        result.components["response_gap"] = BurnoutComponent(
            name="response_gap",
            score=score,
            status=status,
            details={
                "unresponded_rate_7d": round(unresponded_rate, 1),
            },
        )

    def _score_triage_overhead(
        self, github_metrics: GitHubMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Score based on unlabeled issues rate."""
        unlabeled_rate = github_metrics.issues.unlabeled_rate

        score = 0
        for threshold, points in self.TRIAGE_OVERHEAD_THRESHOLDS:
            if unlabeled_rate <= threshold:
                score = points
                break

        status = self._get_status(score)

        result.components["triage_overhead"] = BurnoutComponent(
            name="triage_overhead",
            score=score,
            status=status,
            details={
                "unlabeled_rate": round(unlabeled_rate, 1),
            },
        )

    def _score_workload_concentration(
        self, git_metrics: GitMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Score based on workload concentration (inverse pony factor)."""
        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        pony_factor = window.pony_factor

        score = 0
        for threshold, points in self.PONY_FACTOR_THRESHOLDS:
            if pony_factor >= threshold:
                score = points
                break

        # Also check top contributor concentration
        if window.top_contributors:
            top = window.top_contributors[0]
            if top.percentage > 70:
                score = min(20, score + 5)
            elif top.percentage > 50:
                score = min(20, score + 3)

        status = self._get_status(score)
        concentration_risk = "low" if score <= 5 else ("medium" if score <= 10 else "high")

        result.components["workload_concentration"] = BurnoutComponent(
            name="workload_concentration",
            score=score,
            status=status,
            details={
                "pony_factor_90d": pony_factor,
                "concentration_risk": concentration_risk,
            },
        )

    def _score_activity_decline(
        self, git_metrics: GitMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Score based on activity trend."""
        window_90 = git_metrics.time_windows.get("90_days")
        window_all = git_metrics.time_windows.get("all_time")

        if not window_90:
            return

        # Calculate activity change
        # This is a simplification - ideally we'd compare to previous 90-day window
        current_rate = window_90.commits_per_day

        # Estimate trend based on retention
        retention = window_90.contributor_retention

        # Calculate approximate decline percentage
        if retention >= 70:
            change_pct = -10  # Growing
        elif retention >= 50:
            change_pct = 5  # Stable
        elif retention >= 30:
            change_pct = 25  # Declining
        elif retention >= 10:
            change_pct = 45  # Significantly declining
        else:
            change_pct = 60  # Severely declining

        score = 0
        for threshold, points in self.ACTIVITY_DECLINE_THRESHOLDS:
            if change_pct <= threshold:
                score = points
                break

        status = self._get_status(score)

        # Determine trend label
        if change_pct < -10:
            trend = "growing"
        elif change_pct <= 10:
            trend = "stable"
        elif change_pct <= 30:
            trend = "declining"
        else:
            trend = "severely_declining"

        result.components["activity_decline"] = BurnoutComponent(
            name="activity_decline",
            score=score,
            status=status,
            details={
                "trend": trend,
                "change_percentage": round(change_pct, 1),
            },
        )

    def _extract_maintainer_health(
        self, git_metrics: GitMetricsResult, result: BurnoutScoreResult
    ) -> None:
        """Extract maintainer health indicators."""
        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        result.maintainer_health = MaintainerHealth(
            contributor_retention_90d=window.contributor_retention,
            pony_factor_90d=window.pony_factor,
            elephant_factor_90d=window.elephant_factor,
            unique_contributors_90d=window.unique_contributors,
        )

    def _get_grade(self, score: int) -> str:
        """Get letter grade from burnout score (lower = better)."""
        for threshold, grade in self.GRADES:
            if score <= threshold:
                return grade
        return "F"

    def _get_risk_level(self, score: int) -> str:
        """Get risk level from burnout score."""
        for threshold, level in self.RISK_LEVELS:
            if score <= threshold:
                return level
        return "critical"

    def _get_status(self, score: int) -> str:
        """Get status from component score (0-20)."""
        if score <= 5:
            return "healthy"
        elif score <= 10:
            return "moderate"
        elif score <= 15:
            return "warning"
        else:
            return "critical"

    def _generate_recommendations(self, result: BurnoutScoreResult) -> None:
        """Generate recommendations based on burnout components."""
        recommendations = []

        for name, component in result.components.items():
            if component.status in ("warning", "critical"):
                if name == "issue_backlog":
                    open_issues = component.details.get("open_issues", 0)
                    recommendations.append(
                        f"Issue backlog is elevated ({open_issues} open) - consider triage sprint"
                    )
                elif name == "response_gap":
                    rate = component.details.get("unresponded_rate_7d", 0)
                    recommendations.append(
                        f"Many issues unresponded ({rate:.1f}%) - improve response times"
                    )
                elif name == "triage_overhead":
                    recommendations.append(
                        "Many unlabeled issues - consider using GitHub Actions for auto-labeling"
                    )
                elif name == "workload_concentration":
                    recommendations.append(
                        "Work is concentrated among few contributors - encourage more participation"
                    )
                elif name == "activity_decline":
                    recommendations.append(
                        "Activity is declining - consider community outreach or mentorship programs"
                    )

        # Add positive recommendation if healthy
        if result.burnout_score <= 20:
            recommendations.append(
                "Workload distribution is healthy - maintain current practices"
            )

        result.recommendations = recommendations[:5]

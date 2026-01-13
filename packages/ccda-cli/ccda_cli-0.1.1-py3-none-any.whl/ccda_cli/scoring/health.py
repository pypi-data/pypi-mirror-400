"""Project health score calculation.

Combines git metrics and GitHub metrics to calculate an overall
project health score (0-100) with letter grade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ccda_cli.config import get_config
from ccda_cli.metrics.git import GitMetricsResult
from ccda_cli.metrics.github import GitHubMetricsResult


@dataclass
class CategoryScore:
    """Score for a single category."""

    name: str
    score: int  # 0-100
    weight: int
    weighted_score: float
    status: str  # healthy, moderate, warning, critical
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 1),
            "status": self.status,
            **self.details,
        }


@dataclass
class RiskFactor:
    """Identified risk factor."""

    factor: str
    severity: str  # low, medium, high, critical
    message: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "factor": self.factor,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass
class HealthScoreResult:
    """Health score calculation result."""

    purl: str
    calculated_at: datetime
    ttl_hours: int = 6

    health_score: int = 0  # 0-100
    grade: str = "F"
    risk_level: str = "high"

    category_scores: dict[str, CategoryScore] = field(default_factory=dict)
    risk_factors: list[RiskFactor] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # CHAOSS metrics for dashboard display
    chaoss_metrics: dict[str, Any] = field(default_factory=dict)
    # Extended metrics for dashboard display
    extended_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "purl": self.purl,
            "calculated_at": self.calculated_at.isoformat(),
            "ttl_hours": self.ttl_hours,
            "health_score": self.health_score,
            "grade": self.grade,
            "risk_level": self.risk_level,
            "category_scores": {k: v.to_dict() for k, v in self.category_scores.items()},
            "risk_factors": [r.to_dict() for r in self.risk_factors],
            "recommendations": self.recommendations,
            "chaoss_metrics": self.chaoss_metrics,
            "extended_metrics": self.extended_metrics,
        }


class HealthScoreCalculator:
    """Calculates project health score from metrics."""

    # Grade thresholds
    GRADES = [
        (90, "A"),
        (80, "B"),
        (70, "C"),
        (60, "D"),
        (0, "F"),
    ]

    # Risk level thresholds
    RISK_LEVELS = [
        (80, "low"),
        (60, "medium"),
        (40, "high"),
        (0, "critical"),
    ]

    def __init__(self):
        """Initialize calculator with config."""
        self.config = get_config()
        self.weights = self.config.scoring.health

    def calculate(
        self,
        purl: str,
        git_metrics: GitMetricsResult | None = None,
        github_metrics: GitHubMetricsResult | None = None,
    ) -> HealthScoreResult:
        """Calculate health score from metrics.

        Args:
            purl: Package URL
            git_metrics: Git analysis results
            github_metrics: GitHub API results

        Returns:
            HealthScoreResult with score and details
        """
        result = HealthScoreResult(
            purl=purl,
            calculated_at=datetime.now(),
        )

        # Calculate individual category scores
        if git_metrics:
            self._score_commit_activity(git_metrics, result)
            self._score_bus_factor(git_metrics, result)
            self._score_pony_factor(git_metrics, result)
            self._score_license_stability(git_metrics, result)
            self._score_contributor_retention(git_metrics, result)
            self._score_elephant_factor(git_metrics, result)

        if github_metrics:
            self._score_issue_responsiveness(github_metrics, result)
            self._score_pr_velocity(github_metrics, result)
            self._score_branch_protection(github_metrics, result)
            self._score_release_frequency(github_metrics, result)

        # Calculate overall score
        total_weight = 0
        total_weighted = 0.0

        for category in result.category_scores.values():
            total_weight += category.weight
            total_weighted += category.weighted_score

        if total_weight > 0:
            # Normalize to 100 if not all categories present
            result.health_score = int((total_weighted / total_weight) * 100)
        else:
            result.health_score = 0

        # Assign grade and risk level
        result.grade = self._get_grade(result.health_score)
        result.risk_level = self._get_risk_level(result.health_score)

        # Generate recommendations
        self._generate_recommendations(result)

        # Populate CHAOSS metrics for dashboard
        self._populate_chaoss_metrics(git_metrics, result)

        # Populate extended metrics for dashboard
        self._populate_extended_metrics(git_metrics, github_metrics, result)

        return result

    def _score_commit_activity(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on recent commit activity."""
        weight = self.weights.commit_activity

        # Get 90-day metrics
        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        commits = window.total_commits
        commits_per_day = window.commits_per_day
        days_since_last = window.days_since_last_commit

        # Score based on activity level
        if commits_per_day >= 1.0:
            score = 100
        elif commits_per_day >= 0.5:
            score = 90
        elif commits_per_day >= 0.2:
            score = 75
        elif commits_per_day >= 0.1:
            score = 60
        elif commits > 0:
            score = 40
        else:
            score = 0

        # Penalize for stale repos
        if days_since_last > 30:
            score = max(0, score - 20)
        elif days_since_last > 14:
            score = max(0, score - 10)

        status = self._get_status(score)

        result.category_scores["commit_activity"] = CategoryScore(
            name="commit_activity",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "commits_90d": commits,
                "commits_per_day": round(commits_per_day, 2),
                "days_since_last": round(days_since_last, 1),
            },
        )

        if score < 50:
            result.risk_factors.append(
                RiskFactor(
                    factor="commit_activity",
                    severity="medium" if score > 25 else "high",
                    message=f"Low commit activity ({commits} commits in 90 days)",
                )
            )

    def _score_bus_factor(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on bus factor."""
        weight = self.weights.bus_factor
        threshold = self.config.analysis.thresholds["bus_factor_min"]

        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        bus_factor = window.bus_factor

        # Score based on bus factor
        if bus_factor >= 10:
            score = 100
        elif bus_factor >= 5:
            score = 80
        elif bus_factor >= threshold:
            score = 60
        elif bus_factor >= 2:
            score = 40
        else:
            score = 20

        status = self._get_status(score)

        result.category_scores["bus_factor"] = CategoryScore(
            name="bus_factor",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "value": bus_factor,
                "threshold": threshold,
            },
        )

        if bus_factor < threshold:
            result.risk_factors.append(
                RiskFactor(
                    factor="bus_factor",
                    severity="high" if bus_factor <= 1 else "medium",
                    message=f"Low bus factor ({bus_factor}) - project depends on few contributors",
                )
            )

    def _score_pony_factor(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on pony factor (CHAOSS)."""
        weight = self.weights.pony_factor
        threshold = self.config.analysis.thresholds["pony_factor_min"]

        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        pony_factor = window.pony_factor

        # Similar to bus factor
        if pony_factor >= 10:
            score = 100
        elif pony_factor >= 5:
            score = 80
        elif pony_factor >= threshold:
            score = 60
        elif pony_factor >= 2:
            score = 40
        else:
            score = 20

        status = self._get_status(score)

        result.category_scores["pony_factor"] = CategoryScore(
            name="pony_factor",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "value": pony_factor,
                "threshold": threshold,
            },
        )

    def _score_license_stability(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on license change history."""
        weight = self.weights.license_stability

        license_history = git_metrics.license_changes
        change_count = license_history.change_count

        # Fewer license changes is better
        if change_count == 0:
            score = 100
        elif change_count == 1:
            score = 90
        elif change_count <= 3:
            score = 70
        elif change_count <= 5:
            score = 50
        else:
            score = 30

        status = self._get_status(score)

        result.category_scores["license_stability"] = CategoryScore(
            name="license_stability",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "change_count": change_count,
                "current_license": license_history.current_license,
                "risk_level": license_history.risk_level,
            },
        )

    def _score_contributor_retention(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on contributor retention."""
        weight = self.weights.contributor_retention

        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        retention = window.contributor_retention

        # Higher retention is better
        if retention >= 70:
            score = 100
        elif retention >= 50:
            score = 80
        elif retention >= 30:
            score = 60
        elif retention >= 10:
            score = 40
        else:
            score = 20

        status = self._get_status(score)

        result.category_scores["contributor_retention"] = CategoryScore(
            name="contributor_retention",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "retention_rate": round(retention, 1),
            },
        )

    def _score_elephant_factor(
        self, git_metrics: GitMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on company diversity (elephant factor)."""
        weight = self.weights.elephant_factor
        threshold = self.config.analysis.thresholds["elephant_factor_min"]

        window = git_metrics.time_windows.get("90_days")
        if not window:
            return

        elephant_factor = window.elephant_factor

        # More companies is better (but 1 is not terrible)
        if elephant_factor >= 5:
            score = 100
        elif elephant_factor >= 3:
            score = 80
        elif elephant_factor >= threshold:
            score = 60
        elif elephant_factor >= 1:
            score = 50
        else:
            score = 30

        status = self._get_status(score)

        result.category_scores["elephant_factor"] = CategoryScore(
            name="elephant_factor",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "value": elephant_factor,
                "threshold": threshold,
            },
        )

    def _score_issue_responsiveness(
        self, github_metrics: GitHubMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on issue response times."""
        weight = self.weights.issue_responsiveness

        issues = github_metrics.issues
        unresponded_rate = issues.unresponded_rate_7d
        avg_response = issues.avg_response_hours

        # Lower unresponded rate is better
        if unresponded_rate <= 5:
            score = 100
        elif unresponded_rate <= 15:
            score = 80
        elif unresponded_rate <= 30:
            score = 60
        elif unresponded_rate <= 50:
            score = 40
        else:
            score = 20

        # Adjust for response time
        if avg_response > 0:
            if avg_response <= 24:
                pass  # Good
            elif avg_response <= 72:
                score = max(0, score - 10)
            elif avg_response <= 168:  # 1 week
                score = max(0, score - 20)
            else:
                score = max(0, score - 30)

        status = self._get_status(score)

        result.category_scores["issue_responsiveness"] = CategoryScore(
            name="issue_responsiveness",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "unresponded_rate_7d": round(unresponded_rate, 1),
                "avg_response_hours": round(avg_response, 1),
            },
        )

        if unresponded_rate > 30:
            result.risk_factors.append(
                RiskFactor(
                    factor="issue_responsiveness",
                    severity="medium",
                    message=f"High unresponded issue rate ({unresponded_rate:.1f}%)",
                )
            )

    def _score_pr_velocity(
        self, github_metrics: GitHubMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on PR merge velocity."""
        weight = self.weights.pr_velocity

        prs = github_metrics.pull_requests
        avg_merge = prs.avg_merge_hours

        # Faster merges are better (within reason)
        if avg_merge <= 24:  # 1 day
            score = 100
        elif avg_merge <= 48:  # 2 days
            score = 90
        elif avg_merge <= 168:  # 1 week
            score = 70
        elif avg_merge <= 336:  # 2 weeks
            score = 50
        elif avg_merge > 0:
            score = 30
        else:
            score = 50  # No data

        status = self._get_status(score)

        result.category_scores["pr_velocity"] = CategoryScore(
            name="pr_velocity",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "avg_merge_hours": round(avg_merge, 1),
                "open_prs": prs.open_count,
                "merged_prs": prs.merged_count,
            },
        )

        if avg_merge > 168:
            result.risk_factors.append(
                RiskFactor(
                    factor="pr_velocity",
                    severity="low",
                    message=f"Slow PR merge time ({avg_merge:.0f} hours avg)",
                )
            )

    def _score_branch_protection(
        self, github_metrics: GitHubMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on branch protection settings."""
        weight = self.weights.branch_protection

        protection = github_metrics.branch_protection
        score = 0

        # Points for each protection measure
        if protection.default_branch_protected:
            score += 40
        if protection.requires_pr_reviews:
            score += 25
        if protection.requires_status_checks:
            score += 20
        if protection.requires_signatures:
            score += 10
        if protection.enforces_admins:
            score += 5

        status = self._get_status(score)

        result.category_scores["branch_protection"] = CategoryScore(
            name="branch_protection",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "protected": protection.default_branch_protected,
                "requires_reviews": protection.requires_pr_reviews,
                "requires_checks": protection.requires_status_checks,
            },
        )

        if not protection.default_branch_protected:
            result.risk_factors.append(
                RiskFactor(
                    factor="branch_protection",
                    severity="medium",
                    message="Default branch has no protection rules",
                )
            )

    def _score_release_frequency(
        self, github_metrics: GitHubMetricsResult, result: HealthScoreResult
    ) -> None:
        """Score based on release frequency."""
        weight = self.weights.release_frequency

        releases = github_metrics.releases
        frequency = releases.release_frequency_days
        total = releases.total_count

        # Regular releases are good
        if total == 0:
            score = 30  # No releases
        elif frequency <= 30:  # Monthly or better
            score = 100
        elif frequency <= 90:  # Quarterly
            score = 80
        elif frequency <= 180:  # Bi-annually
            score = 60
        elif frequency <= 365:  # Yearly
            score = 40
        else:
            score = 20

        status = self._get_status(score)

        result.category_scores["release_frequency"] = CategoryScore(
            name="release_frequency",
            score=score,
            weight=weight,
            weighted_score=(score / 100) * weight,
            status=status,
            details={
                "total_releases": total,
                "frequency_days": round(frequency, 1),
                "has_signed": releases.has_signed_releases,
            },
        )

    def _get_grade(self, score: int) -> str:
        """Get letter grade from score."""
        for threshold, grade in self.GRADES:
            if score >= threshold:
                return grade
        return "F"

    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score."""
        for threshold, level in self.RISK_LEVELS:
            if score >= threshold:
                return level
        return "critical"

    def _get_status(self, score: int) -> str:
        """Get status from category score."""
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "moderate"
        elif score >= 40:
            return "warning"
        else:
            return "critical"

    def _generate_recommendations(self, result: HealthScoreResult) -> None:
        """Generate recommendations based on scores."""
        recommendations = []

        for name, category in result.category_scores.items():
            if category.status in ("warning", "critical"):
                if name == "commit_activity":
                    recommendations.append("Increase commit activity and project maintenance")
                elif name == "bus_factor":
                    recommendations.append("Encourage more contributors to reduce bus factor risk")
                elif name == "issue_responsiveness":
                    recommendations.append("Improve issue triage and response times")
                elif name == "pr_velocity":
                    recommendations.append("Speed up pull request review process")
                elif name == "branch_protection":
                    recommendations.append("Enable branch protection rules for the default branch")
                elif name == "release_frequency":
                    recommendations.append("Consider more frequent releases")

        # Add positive recommendations for healthy projects
        if result.health_score >= 80:
            recommendations.append("Maintain current development practices")

        result.recommendations = recommendations[:5]  # Limit to top 5

    def _populate_chaoss_metrics(
        self, git_metrics: GitMetricsResult | None, result: HealthScoreResult
    ) -> None:
        """Populate CHAOSS metrics for dashboard display."""
        if not git_metrics:
            return

        window = git_metrics.time_windows.get("90_days")
        if window:
            result.chaoss_metrics = {
                "bus_factor": window.bus_factor,
                "pony_factor": window.pony_factor,
                "elephant_factor": window.elephant_factor,
                "contributor_count": window.unique_contributors,
            }

    def _populate_extended_metrics(
        self,
        git_metrics: GitMetricsResult | None,
        github_metrics: GitHubMetricsResult | None,
        result: HealthScoreResult,
    ) -> None:
        """Populate extended metrics for dashboard display."""
        result.extended_metrics = {}

        # Git-based metrics
        if git_metrics:
            window = git_metrics.time_windows.get("90_days")
            if window:
                result.extended_metrics["commit_frequency"] = self._classify_frequency(
                    window.commits_per_day
                )
                result.extended_metrics["commits_per_day"] = round(
                    window.commits_per_day, 2
                )

        # GitHub-based metrics
        if github_metrics:
            prs = github_metrics.pull_requests
            result.extended_metrics["pr_velocity"] = self._classify_velocity(
                prs.avg_merge_hours
            )
            result.extended_metrics["median_pr_merge_hours"] = round(
                prs.median_merge_hours, 1
            )

            result.extended_metrics[
                "branch_protected"
            ] = github_metrics.branch_protection.default_branch_protected
            result.extended_metrics[
                "has_signed_releases"
            ] = github_metrics.releases.has_signed_releases

            # These fields are not yet available in GitHubMetricsResult
            # Set sensible defaults for now
            result.extended_metrics["has_lockfile"] = False
            result.extended_metrics["is_foundation_project"] = False
            result.extended_metrics["foundation_name"] = None

    def _classify_frequency(self, commits_per_day: float) -> str:
        """Classify commit frequency level."""
        if commits_per_day >= 1.0:
            return "very_high"
        elif commits_per_day >= 0.5:
            return "high"
        elif commits_per_day >= 0.2:
            return "moderate"
        elif commits_per_day >= 0.1:
            return "low"
        else:
            return "very_low"

    def _classify_velocity(self, avg_hours: float) -> str:
        """Classify PR merge velocity."""
        if avg_hours <= 24:
            return "very_fast"
        elif avg_hours <= 72:
            return "fast"
        elif avg_hours <= 168:
            return "moderate"
        elif avg_hours <= 336:
            return "slow"
        else:
            return "very_slow"

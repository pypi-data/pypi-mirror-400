"""Full analysis pipeline for packages.

Orchestrates discovery, cloning, metrics collection, scanning, and scoring.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from ccda_cli.cache import CacheManager
from ccda_cli.config import get_config
from ccda_cli.core.git import GitManager, CloneResult
from ccda_cli.discovery import PackageResolver, PURLParser, DiscoveryResult
from ccda_cli.metrics.git import GitMetricsAnalyzer, GitMetricsResult
from ccda_cli.metrics.github import GitHubMetricsCollector, GitHubMetricsResult
from ccda_cli.scanner import TarballScanner, TarballScanResult
from ccda_cli.scoring.health import HealthScoreCalculator, HealthScoreResult
from ccda_cli.scoring.burnout import BurnoutScoreCalculator, BurnoutScoreResult


@dataclass
class AnalysisStep:
    """Represents a step in the analysis pipeline."""

    name: str
    status: str = "pending"  # pending, running, completed, skipped, failed
    duration_seconds: float = 0.0
    error: str | None = None


@dataclass
class AnalysisResult:
    """Complete analysis result for a package."""

    purl: str
    analyzed_at: datetime
    analysis_version: str = "1.0.0"

    # Results from each step
    discovery: DiscoveryResult | None = None
    clone: CloneResult | None = None
    git_metrics: GitMetricsResult | None = None
    github_metrics: GitHubMetricsResult | None = None
    tarball_scan: TarballScanResult | None = None
    health_score: HealthScoreResult | None = None
    burnout_score: BurnoutScoreResult | None = None

    # Pipeline metadata
    steps: list[AnalysisStep] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to unified JSON format matching the spec."""
        result = {
            "schema_version": "1.0.0",
            "purl": self.purl,
            "analyzed_at": self.analyzed_at.isoformat(),
            "analysis_version": self.analysis_version,
            "pipeline": {
                "steps": [
                    {
                        "name": s.name,
                        "status": s.status,
                        "duration_seconds": round(s.duration_seconds, 2),
                        "error": s.error,
                    }
                    for s in self.steps
                ],
                "total_duration_seconds": round(self.total_duration_seconds, 2),
                "errors": self.errors,
            },
        }

        # Discovery
        if self.discovery:
            result["discovery"] = self.discovery.to_dict()

        # Repository info
        if self.clone:
            result["repository"] = {
                "url": self.clone.repo_url,
                "local_path": str(self.clone.local_path),
                "cloned": self.clone.success,
                "last_commit": self.clone.last_commit_hash,
                "last_commit_date": self.clone.last_commit_date.isoformat() if self.clone.last_commit_date else None,
            }

        # Git metrics
        if self.git_metrics:
            result["git_metrics"] = self.git_metrics.to_dict()

        # GitHub metrics
        if self.github_metrics:
            result["github_metrics"] = self.github_metrics.to_dict()

        # Tarball scan
        if self.tarball_scan:
            result["tarball_scan"] = self.tarball_scan.to_dict()

        # Scores
        if self.health_score:
            result["health_score"] = self.health_score.to_dict()

        if self.burnout_score:
            result["burnout_score"] = self.burnout_score.to_dict()

        # Unified summary
        result["summary"] = self._build_summary()

        return result

    def _build_summary(self) -> dict[str, Any]:
        """Build unified summary section."""
        summary = {
            "package_name": None,
            "version": None,
            "github_url": None,
            "tarball_url": None,
            "license": None,
            "health_grade": None,
            "burnout_risk": None,
            "has_binaries": False,
            "key_metrics": {},
        }

        # From discovery
        if self.discovery:
            parsed = PURLParser.parse(self.purl)
            summary["package_name"] = parsed.full_name
            summary["version"] = parsed.version
            summary["github_url"] = self.discovery.github_url
            summary["tarball_url"] = self.discovery.tarball_url
            if self.discovery.metadata:
                summary["license"] = self.discovery.metadata.get("license")

        # From scores
        if self.health_score:
            summary["health_grade"] = self.health_score.grade
            summary["key_metrics"]["health_score"] = self.health_score.health_score

        if self.burnout_score:
            summary["burnout_risk"] = self.burnout_score.risk_level
            summary["key_metrics"]["burnout_score"] = self.burnout_score.burnout_score

        # From git metrics
        if self.git_metrics:
            window = self.git_metrics.time_windows.get("90_days")
            if window:
                summary["key_metrics"]["bus_factor"] = window.bus_factor
                summary["key_metrics"]["pony_factor"] = window.pony_factor
                summary["key_metrics"]["unique_contributors_90d"] = window.unique_contributors

        # From GitHub metrics
        if self.github_metrics:
            summary["key_metrics"]["stars"] = self.github_metrics.repository.stars
            summary["key_metrics"]["open_issues"] = self.github_metrics.issues.open_count
            summary["key_metrics"]["open_prs"] = self.github_metrics.pull_requests.open_count

        # From tarball scan
        if self.tarball_scan:
            summary["has_binaries"] = bool(self.tarball_scan.binaries.get("files"))
            if self.tarball_scan.license_files:
                # Use detected license if not in metadata
                if not summary["license"]:
                    for lf in self.tarball_scan.license_files:
                        if lf.spdx_id:
                            summary["license"] = lf.spdx_id
                            break

        return summary


class AnalysisPipeline:
    """Orchestrates the full analysis pipeline."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        progress_callback: Callable[[str, str], None] | None = None,
    ):
        """Initialize pipeline.

        Args:
            cache_dir: Custom cache directory
            progress_callback: Callback for progress updates (step_name, status)
        """
        self.config = get_config()
        self.cache = CacheManager(base_dir=cache_dir)
        self.git_manager = GitManager(cache_dir=cache_dir)
        self.progress_callback = progress_callback or (lambda *_: None)

    async def analyze(
        self,
        purl: str,
        skip_clone: bool = False,
        skip_tarball: bool = False,
        skip_github: bool = False,
        force_refresh: bool = False,
    ) -> AnalysisResult:
        """Run full analysis on a package.

        Args:
            purl: Package URL to analyze
            skip_clone: Skip git clone step
            skip_tarball: Skip tarball scanning
            skip_github: Skip GitHub API metrics
            force_refresh: Force refresh all cached data

        Returns:
            AnalysisResult with all collected data
        """
        start_time = datetime.now()
        result = AnalysisResult(purl=purl, analyzed_at=start_time)

        # Step 1: Discovery
        discovery_step = AnalysisStep(name="discovery")
        result.steps.append(discovery_step)
        await self._run_step(
            discovery_step,
            self._discovery_step,
            result,
            purl,
            force_refresh,
        )

        # Step 2: Clone (if GitHub URL found)
        if not skip_clone and result.discovery and result.discovery.github_url:
            clone_step = AnalysisStep(name="clone")
            result.steps.append(clone_step)
            await self._run_step(
                clone_step,
                self._clone_step,
                result,
                result.discovery.github_url,
            )

        # Step 3: Git Metrics (if cloned)
        if result.clone and result.clone.success:
            git_step = AnalysisStep(name="git_metrics")
            result.steps.append(git_step)
            await self._run_step(
                git_step,
                self._git_metrics_step,
                result,
                result.clone.local_path,
                result.clone.repo_url,
            )

        # Step 4: GitHub Metrics
        if not skip_github and result.discovery and result.discovery.github_url:
            github_step = AnalysisStep(name="github_metrics")
            result.steps.append(github_step)
            await self._run_step(
                github_step,
                self._github_metrics_step,
                result,
                result.discovery.github_url,
            )

        # Step 5: Tarball Scan
        if not skip_tarball:
            tarball_step = AnalysisStep(name="tarball_scan")
            result.steps.append(tarball_step)
            await self._run_step(
                tarball_step,
                self._tarball_step,
                result,
                purl,
            )

        # Step 6: Health Score
        health_step = AnalysisStep(name="health_score")
        result.steps.append(health_step)
        await self._run_step(
            health_step,
            self._health_score_step,
            result,
        )

        # Step 7: Burnout Score
        burnout_step = AnalysisStep(name="burnout_score")
        result.steps.append(burnout_step)
        await self._run_step(
            burnout_step,
            self._burnout_score_step,
            result,
        )

        # Calculate total duration
        result.total_duration_seconds = (datetime.now() - start_time).total_seconds()

        # Save to cache
        self.cache.save_package_data(purl, "unified.json", result.to_dict())

        return result

    async def _run_step(
        self,
        step: AnalysisStep,
        func: Callable,
        result: AnalysisResult,
        *args,
    ) -> None:
        """Run a step with timing and error handling."""
        step.status = "running"
        self.progress_callback(step.name, "running")
        start = datetime.now()

        try:
            await func(result, *args)
            step.status = "completed"
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            result.errors.append(f"{step.name}: {e}")

        step.duration_seconds = (datetime.now() - start).total_seconds()
        self.progress_callback(step.name, step.status)

    async def _discovery_step(
        self,
        result: AnalysisResult,
        purl: str,
        force_refresh: bool,
    ) -> None:
        """Run discovery step."""
        # Check cache first
        if not force_refresh:
            cached = self.cache.get_package_data(purl, "discovery.json")
            if cached:
                result.discovery = DiscoveryResult.from_dict(cached.data)
                return

        resolver = PackageResolver()
        result.discovery = await resolver.discover(purl)
        self.cache.save_package_data(purl, "discovery.json", result.discovery.to_dict())

    async def _clone_step(
        self,
        result: AnalysisResult,
        github_url: str,
    ) -> None:
        """Run clone step."""
        result.clone = await self.git_manager.clone(github_url)

    async def _git_metrics_step(
        self,
        result: AnalysisResult,
        local_path: Path,
        repo_url: str,
    ) -> None:
        """Run git metrics step."""
        # Run in executor since it's CPU-bound
        loop = asyncio.get_event_loop()
        analyzer = GitMetricsAnalyzer(local_path)
        result.git_metrics = await loop.run_in_executor(
            None, analyzer.analyze, repo_url
        )

    async def _github_metrics_step(
        self,
        result: AnalysisResult,
        github_url: str,
    ) -> None:
        """Run GitHub metrics step."""
        collector = GitHubMetricsCollector()
        result.github_metrics = await collector.collect(github_url)

    async def _tarball_step(
        self,
        result: AnalysisResult,
        purl: str,
    ) -> None:
        """Run tarball scan step."""
        scanner = TarballScanner()
        result.tarball_scan = await scanner.scan_purl(purl)

    async def _health_score_step(
        self,
        result: AnalysisResult,
    ) -> None:
        """Calculate health score."""
        calculator = HealthScoreCalculator()
        result.health_score = calculator.calculate(
            result.purl,
            result.git_metrics,
            result.github_metrics,
        )

    async def _burnout_score_step(
        self,
        result: AnalysisResult,
    ) -> None:
        """Calculate burnout score."""
        calculator = BurnoutScoreCalculator()
        result.burnout_score = calculator.calculate(
            result.purl,
            result.git_metrics,
            result.github_metrics,
        )

    async def analyze_batch(
        self,
        purls: list[str],
        concurrency: int = 3,
        **kwargs,
    ) -> list[AnalysisResult]:
        """Analyze multiple packages concurrently.

        Args:
            purls: List of PURLs to analyze
            concurrency: Max concurrent analyses
            **kwargs: Additional args passed to analyze()

        Returns:
            List of AnalysisResults
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def analyze_with_semaphore(purl: str) -> AnalysisResult:
            async with semaphore:
                return await self.analyze(purl, **kwargs)

        tasks = [analyze_with_semaphore(purl) for purl in purls]
        return await asyncio.gather(*tasks, return_exceptions=False)

"""Tests for analysis pipeline."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ccda_cli.analysis.pipeline import AnalysisPipeline, AnalysisResult, AnalysisStep


class TestAnalysisStep:
    """Tests for AnalysisStep dataclass."""

    def test_default_values(self):
        """Test default step values."""
        step = AnalysisStep(name="discovery")

        assert step.name == "discovery"
        assert step.status == "pending"
        assert step.duration_seconds == 0.0
        assert step.error is None

    def test_with_error(self):
        """Test step with error."""
        step = AnalysisStep(
            name="clone",
            status="failed",
            error="Repository not found",
        )

        assert step.status == "failed"
        assert step.error == "Repository not found"


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    @pytest.fixture
    def result(self):
        """Create a basic analysis result."""
        return AnalysisResult(
            purl="pkg:npm/express@4.18.2",
            analyzed_at=datetime(2024, 1, 1, 12, 0, 0),
        )

    def test_to_dict_minimal(self, result):
        """Test serialization with minimal data."""
        data = result.to_dict()

        assert data["purl"] == "pkg:npm/express@4.18.2"
        assert data["schema_version"] == "1.0.0"
        assert "pipeline" in data
        assert "summary" in data

    def test_to_dict_with_steps(self, result):
        """Test serialization with pipeline steps."""
        result.steps = [
            AnalysisStep(name="discovery", status="completed", duration_seconds=1.5),
            AnalysisStep(name="clone", status="failed", error="Not found"),
        ]

        data = result.to_dict()

        assert len(data["pipeline"]["steps"]) == 2
        assert data["pipeline"]["steps"][0]["status"] == "completed"
        assert data["pipeline"]["steps"][1]["error"] == "Not found"

    def test_to_dict_with_scores(self, result):
        """Test serialization with scores."""
        mock_health = MagicMock()
        mock_health.health_score = 85
        mock_health.grade = "B"
        mock_health.to_dict.return_value = {"health_score": 85, "grade": "B"}

        mock_burnout = MagicMock()
        mock_burnout.burnout_score = 25
        mock_burnout.risk_level = "low"
        mock_burnout.to_dict.return_value = {"burnout_score": 25, "risk_level": "low"}

        result.health_score = mock_health
        result.burnout_score = mock_burnout

        data = result.to_dict()

        assert data["health_score"]["health_score"] == 85
        assert data["burnout_score"]["burnout_score"] == 25

    def test_build_summary(self, result):
        """Test summary building."""
        data = result.to_dict()
        summary = data["summary"]

        assert "package_name" in summary
        assert "health_grade" in summary
        assert "has_binaries" in summary
        assert "key_metrics" in summary


class TestAnalysisPipeline:
    """Tests for AnalysisPipeline class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies."""
        with patch("ccda_cli.analysis.pipeline.get_config") as mock_config, \
             patch("ccda_cli.analysis.pipeline.CacheManager") as mock_cache, \
             patch("ccda_cli.analysis.pipeline.GitManager") as mock_git:

            mock_config.return_value = MagicMock()
            mock_cache_instance = MagicMock()
            mock_cache.return_value = mock_cache_instance
            mock_git_instance = MagicMock()
            mock_git.return_value = mock_git_instance

            yield {
                "config": mock_config,
                "cache": mock_cache_instance,
                "git": mock_git_instance,
            }

    @pytest.fixture
    def pipeline(self, mock_dependencies):
        """Create pipeline with mocked dependencies."""
        return AnalysisPipeline()

    @pytest.mark.asyncio
    async def test_analyze_discovery_only(self, pipeline, mock_dependencies):
        """Test analysis with just discovery step."""
        mock_cache = mock_dependencies["cache"]
        mock_cache.get_package_data.return_value = None

        mock_discovery = MagicMock()
        mock_discovery.github_url = None
        mock_discovery.tarball_url = None
        mock_discovery.to_dict.return_value = {}
        mock_discovery.metadata = {}

        with patch("ccda_cli.analysis.pipeline.PackageResolver") as mock_resolver:
            mock_resolver.return_value.discover = AsyncMock(return_value=mock_discovery)

            result = await pipeline.analyze(
                "pkg:npm/test@1.0.0",
                skip_clone=True,
                skip_tarball=True,
                skip_github=True,
            )

            assert result.purl == "pkg:npm/test@1.0.0"
            assert len(result.steps) >= 3  # discovery + health + burnout

    @pytest.mark.asyncio
    async def test_analyze_full_pipeline(self, pipeline, mock_dependencies):
        """Test full analysis pipeline."""
        mock_cache = mock_dependencies["cache"]
        mock_cache.get_package_data.return_value = None

        mock_git = mock_dependencies["git"]
        mock_clone_result = MagicMock()
        mock_clone_result.success = True
        mock_clone_result.local_path = Path("/tmp/repo")
        mock_clone_result.repo_url = "https://github.com/test/repo"
        mock_clone_result.last_commit_hash = "abc123"
        mock_clone_result.last_commit_date = datetime.now()
        mock_git.clone = AsyncMock(return_value=mock_clone_result)

        mock_discovery = MagicMock()
        mock_discovery.github_url = "https://github.com/test/repo"
        mock_discovery.tarball_url = "https://example.com/pkg.tar.gz"
        mock_discovery.to_dict.return_value = {}
        mock_discovery.metadata = {}

        with patch("ccda_cli.analysis.pipeline.PackageResolver") as mock_resolver, \
             patch("ccda_cli.analysis.pipeline.GitMetricsAnalyzer") as mock_git_analyzer, \
             patch("ccda_cli.analysis.pipeline.GitHubMetricsCollector") as mock_github, \
             patch("ccda_cli.analysis.pipeline.TarballScanner") as mock_tarball, \
             patch("ccda_cli.analysis.pipeline.HealthScoreCalculator") as mock_health, \
             patch("ccda_cli.analysis.pipeline.BurnoutScoreCalculator") as mock_burnout:

            mock_resolver.return_value.discover = AsyncMock(return_value=mock_discovery)
            mock_git_analyzer.return_value.analyze.return_value = MagicMock(to_dict=lambda: {})
            mock_github.return_value.collect = AsyncMock(return_value=MagicMock(to_dict=lambda: {}))
            mock_tarball.return_value.scan_purl = AsyncMock(return_value=MagicMock(to_dict=lambda: {}))
            mock_health.return_value.calculate.return_value = MagicMock(to_dict=lambda: {})
            mock_burnout.return_value.calculate.return_value = MagicMock(to_dict=lambda: {})

            result = await pipeline.analyze("pkg:npm/test@1.0.0")

            assert result.purl == "pkg:npm/test@1.0.0"
            # Should have all steps
            step_names = [s.name for s in result.steps]
            assert "discovery" in step_names

    @pytest.mark.asyncio
    async def test_analyze_handles_step_failure(self, pipeline, mock_dependencies):
        """Test that pipeline handles step failures gracefully."""
        mock_cache = mock_dependencies["cache"]
        mock_cache.get_package_data.return_value = None

        with patch("ccda_cli.analysis.pipeline.PackageResolver") as mock_resolver:
            mock_resolver.return_value.discover = AsyncMock(
                side_effect=Exception("Discovery failed")
            )

            result = await pipeline.analyze(
                "pkg:npm/test@1.0.0",
                skip_clone=True,
                skip_tarball=True,
                skip_github=True,
            )

            # Discovery step should be failed
            discovery_step = next(s for s in result.steps if s.name == "discovery")
            assert discovery_step.status == "failed"
            assert "Discovery failed" in discovery_step.error

    @pytest.mark.asyncio
    async def test_analyze_uses_cached_discovery(self, pipeline, mock_dependencies):
        """Test that pipeline uses cached discovery data."""
        mock_cache = mock_dependencies["cache"]
        cached_data = MagicMock()
        cached_data.data = {
            "purl": "pkg:npm/test@1.0.0",
            "name": "test",
            "version": "1.0.0",
            "repository_url": None,
            "tarball_url": None,
        }
        mock_cache.get_package_data.return_value = cached_data

        with patch("ccda_cli.analysis.pipeline.DiscoveryResult") as mock_result_cls:
            mock_result = MagicMock()
            mock_result.github_url = None
            mock_result.tarball_url = None
            mock_result_cls.from_dict.return_value = mock_result

            result = await pipeline.analyze(
                "pkg:npm/test@1.0.0",
                skip_clone=True,
                skip_tarball=True,
                skip_github=True,
            )

            mock_result_cls.from_dict.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_batch(self, pipeline, mock_dependencies):
        """Test batch analysis."""
        mock_cache = mock_dependencies["cache"]
        mock_cache.get_package_data.return_value = None

        mock_discovery = MagicMock()
        mock_discovery.github_url = None
        mock_discovery.tarball_url = None
        mock_discovery.to_dict.return_value = {}
        mock_discovery.metadata = {}

        with patch("ccda_cli.analysis.pipeline.PackageResolver") as mock_resolver:
            mock_resolver.return_value.discover = AsyncMock(return_value=mock_discovery)

            purls = [
                "pkg:npm/pkg1@1.0.0",
                "pkg:npm/pkg2@1.0.0",
                "pkg:npm/pkg3@1.0.0",
            ]

            results = await pipeline.analyze_batch(
                purls,
                concurrency=2,
                skip_clone=True,
                skip_tarball=True,
                skip_github=True,
            )

            assert len(results) == 3

    def test_progress_callback(self, mock_dependencies):
        """Test that progress callback is called."""
        callback_calls = []

        def callback(step: str, status: str):
            callback_calls.append((step, status))

        pipeline = AnalysisPipeline(progress_callback=callback)

        # The callback should be set
        assert pipeline.progress_callback is not None

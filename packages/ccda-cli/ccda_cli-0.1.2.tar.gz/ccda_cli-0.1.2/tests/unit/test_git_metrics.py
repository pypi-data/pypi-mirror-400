"""Unit tests for git metrics module."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

import pytest

from ccda_cli.metrics.git import (
    GitMetricsAnalyzer,
    GitMetricsResult,
    TimeWindowMetrics,
    ContributorStats,
    CompanyStats,
    LicenseHistory,
)


class TestContributorStats:
    """Test ContributorStats data class."""

    def test_basic_stats(self):
        """Test basic contributor stats."""
        stats = ContributorStats(
            email="test@example.com",
            name="Test User",
            commits=100,
            percentage=25.0,
            company="Test Corp",
        )

        assert stats.email == "test@example.com"
        assert stats.commits == 100
        assert stats.percentage == 25.0


class TestCompanyStats:
    """Test CompanyStats data class."""

    def test_basic_stats(self):
        """Test basic company stats."""
        stats = CompanyStats(
            company="Test Corp",
            commits=500,
            percentage=50.0,
            contributors=10,
        )

        assert stats.company == "Test Corp"
        assert stats.commits == 500


class TestTimeWindowMetrics:
    """Test TimeWindowMetrics data class."""

    def test_to_dict(self):
        """Test serialization."""
        now = datetime.now()
        metrics = TimeWindowMetrics(
            start_date=now - timedelta(days=90),
            end_date=now,
            total_commits=150,
            unique_contributors=35,
            bus_factor=8,
            pony_factor=8,
            elephant_factor=2,
        )

        d = metrics.to_dict()

        assert d["total_commits"] == 150
        assert d["unique_contributors"] == 35
        assert d["bus_factor"] == 8
        assert d["pony_factor"] == 8
        assert d["elephant_factor"] == 2


class TestLicenseHistory:
    """Test LicenseHistory data class."""

    def test_default_values(self):
        """Test default values."""
        history = LicenseHistory()

        assert history.license_file is None
        assert history.current_license is None
        assert history.change_count == 0
        assert history.risk_level == "low"

    def test_to_dict(self):
        """Test serialization."""
        history = LicenseHistory(
            license_file="LICENSE",
            current_license="MIT",
            change_count=1,
            risk_level="low",
        )

        d = history.to_dict()

        assert d["license_file"] == "LICENSE"
        assert d["current_license"] == "MIT"
        assert d["change_count"] == 1


class TestGitMetricsResult:
    """Test GitMetricsResult data class."""

    def test_to_dict(self):
        """Test serialization."""
        result = GitMetricsResult(
            repo_url="https://github.com/test/repo",
            clone_path="/tmp/repo",
            analyzed_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        d = result.to_dict()

        assert d["repo_url"] == "https://github.com/test/repo"
        assert d["method"] == "git_offline"
        assert d["ttl_hours"] == 24


class TestGitMetricsAnalyzer:
    """Test GitMetricsAnalyzer functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        with patch("ccda_cli.metrics.git.get_config") as mock:
            config = MagicMock()
            config.company_mappings.email_domains = {
                "amazon.com": "Amazon",
                "google.com": "Google",
            }
            config.analysis.time_windows = [
                MagicMock(name="90_days", days=90),
                MagicMock(name="all_time", days=None),
            ]
            mock.return_value = config
            yield mock

    def test_init_not_git_repo(self):
        """Should raise error for non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a git repository"):
                GitMetricsAnalyzer(Path(tmpdir))

    def test_calculate_factor_empty(self, mock_config):
        """Calculate factor with empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake git repo
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            result = analyzer._calculate_factor([], 50)

            assert result == 0

    def test_calculate_factor_single(self, mock_config):
        """Calculate factor with single contributor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            contributors = [
                ContributorStats(email="a@test.com", name="A", commits=100),
            ]
            result = analyzer._calculate_factor(contributors, 50)

            assert result == 1

    def test_calculate_factor_multiple(self, mock_config):
        """Calculate factor with multiple contributors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            contributors = [
                ContributorStats(email="a@test.com", name="A", commits=40),
                ContributorStats(email="b@test.com", name="B", commits=35),
                ContributorStats(email="c@test.com", name="C", commits=25),
            ]

            # Need 2 contributors to reach 50% (40 + 35 = 75 > 50)
            result = analyzer._calculate_factor(contributors, 50)
            assert result == 2

    def test_get_company_from_email(self, mock_config):
        """Get company from email domain."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))

            assert analyzer._get_company("user@amazon.com") == "Amazon"
            assert analyzer._get_company("user@google.com") == "Google"
            assert analyzer._get_company("user@unknown.com") == "Independent"

    def test_get_company_noreply(self, mock_config):
        """Noreply emails should be Independent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))

            assert analyzer._get_company("user@users.noreply.github.com") == "Independent"

    def test_calculate_retention(self, mock_config):
        """Calculate contributor retention."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))

            prev = [
                {"email": "a@test.com"},
                {"email": "b@test.com"},
            ]
            current = [
                {"email": "a@test.com"},
                {"email": "c@test.com"},
            ]

            retention = analyzer._calculate_retention(prev, current)
            assert retention == 50.0  # 1 of 2 retained

    def test_calculate_retention_empty(self, mock_config):
        """Retention with empty previous window."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            retention = analyzer._calculate_retention([], [{"email": "a@test.com"}])

            assert retention == 0.0

    def test_detect_license_mit(self, mock_config):
        """Detect MIT license."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            content = "MIT License\n\nPermission is hereby granted, free of charge"

            assert analyzer._detect_license(content) == "MIT"

    def test_detect_license_apache(self, mock_config):
        """Detect Apache license."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            content = "Apache License\nVersion 2.0"

            assert analyzer._detect_license(content) == "Apache-2.0"

    def test_detect_license_unknown(self, mock_config):
        """Unknown license returns Unknown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()

            analyzer = GitMetricsAnalyzer(Path(tmpdir))
            content = "Some custom license text"

            assert analyzer._detect_license(content) == "Unknown"

"""Unit tests for scoring module."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from ccda_cli.scoring.health import HealthScoreCalculator, HealthScoreResult, CategoryScore
from ccda_cli.scoring.burnout import BurnoutScoreCalculator, BurnoutScoreResult, BurnoutComponent


class TestHealthScoreCalculator:
    """Test health score calculation."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        with patch("ccda_cli.scoring.health.get_config") as mock:
            config = MagicMock()
            config.scoring.health.commit_activity = 15
            config.scoring.health.bus_factor = 10
            config.scoring.health.pony_factor = 10
            config.scoring.health.license_stability = 5
            config.scoring.health.contributor_retention = 10
            config.scoring.health.elephant_factor = 10
            config.scoring.health.issue_responsiveness = 10
            config.scoring.health.pr_velocity = 10
            config.scoring.health.branch_protection = 10
            config.scoring.health.release_frequency = 10
            config.analysis.thresholds = {
                "bus_factor_min": 3,
                "pony_factor_min": 3,
                "elephant_factor_min": 2,
            }
            mock.return_value = config
            yield mock

    def test_calculate_empty_metrics(self, mock_config):
        """Calculate with no metrics should return base score."""
        calculator = HealthScoreCalculator()
        result = calculator.calculate("pkg:npm/test@1.0.0")

        assert result.purl == "pkg:npm/test@1.0.0"
        assert isinstance(result.health_score, int)
        assert result.grade in ["A", "B", "C", "D", "F"]

    def test_grade_thresholds(self, mock_config):
        """Test grade assignment based on score."""
        calculator = HealthScoreCalculator()

        assert calculator._get_grade(95) == "A"
        assert calculator._get_grade(85) == "B"
        assert calculator._get_grade(75) == "C"
        assert calculator._get_grade(65) == "D"
        assert calculator._get_grade(50) == "F"

    def test_risk_level_thresholds(self, mock_config):
        """Test risk level assignment."""
        calculator = HealthScoreCalculator()

        assert calculator._get_risk_level(85) == "low"
        assert calculator._get_risk_level(65) == "medium"
        assert calculator._get_risk_level(45) == "high"
        assert calculator._get_risk_level(30) == "critical"

    def test_status_from_score(self, mock_config):
        """Test status assignment from category score."""
        calculator = HealthScoreCalculator()

        assert calculator._get_status(90) == "healthy"
        assert calculator._get_status(70) == "moderate"
        assert calculator._get_status(50) == "warning"
        assert calculator._get_status(30) == "critical"


class TestHealthScoreResult:
    """Test HealthScoreResult data class."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = HealthScoreResult(
            purl="pkg:npm/test@1.0.0",
            calculated_at=datetime(2024, 1, 1, 12, 0, 0),
            health_score=85,
            grade="B",
            risk_level="low",
        )
        result.category_scores["test"] = CategoryScore(
            name="test",
            score=85,
            weight=10,
            weighted_score=8.5,
            status="healthy",
        )

        d = result.to_dict()

        assert d["purl"] == "pkg:npm/test@1.0.0"
        assert d["health_score"] == 85
        assert d["grade"] == "B"
        assert "test" in d["category_scores"]


class TestCategoryScore:
    """Test CategoryScore data class."""

    def test_to_dict(self):
        """Test serialization."""
        score = CategoryScore(
            name="commit_activity",
            score=90,
            weight=15,
            weighted_score=13.5,
            status="healthy",
            details={"commits_90d": 150},
        )
        d = score.to_dict()

        assert d["score"] == 90
        assert d["weight"] == 15
        assert d["weighted_score"] == 13.5
        assert d["status"] == "healthy"
        assert d["commits_90d"] == 150


class TestBurnoutScoreCalculator:
    """Test burnout score calculation."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        with patch("ccda_cli.scoring.burnout.get_config") as mock:
            config = MagicMock()
            mock.return_value = config
            yield mock

    def test_calculate_empty_metrics(self, mock_config):
        """Calculate with no metrics."""
        calculator = BurnoutScoreCalculator()
        result = calculator.calculate("pkg:npm/test@1.0.0")

        assert result.purl == "pkg:npm/test@1.0.0"
        assert isinstance(result.burnout_score, int)
        assert result.grade in ["A", "B", "C", "D", "F"]

    def test_grade_thresholds(self, mock_config):
        """Test burnout grade assignment (lower score = better grade)."""
        calculator = BurnoutScoreCalculator()

        assert calculator._get_grade(15) == "A"
        assert calculator._get_grade(35) == "B"
        assert calculator._get_grade(55) == "C"
        assert calculator._get_grade(75) == "D"
        assert calculator._get_grade(95) == "F"

    def test_risk_level_thresholds(self, mock_config):
        """Test burnout risk level."""
        calculator = BurnoutScoreCalculator()

        assert calculator._get_risk_level(15) == "low"
        assert calculator._get_risk_level(35) == "medium"
        assert calculator._get_risk_level(55) == "high"
        assert calculator._get_risk_level(85) == "critical"

    def test_component_status(self, mock_config):
        """Test component status from score (0-20)."""
        calculator = BurnoutScoreCalculator()

        assert calculator._get_status(3) == "healthy"
        assert calculator._get_status(8) == "moderate"
        assert calculator._get_status(13) == "warning"
        assert calculator._get_status(18) == "critical"


class TestBurnoutScoreResult:
    """Test BurnoutScoreResult data class."""

    def test_to_dict(self):
        """Test serialization."""
        result = BurnoutScoreResult(
            purl="pkg:npm/test@1.0.0",
            calculated_at=datetime(2024, 1, 1, 12, 0, 0),
            burnout_score=25,
            grade="B",
            risk_level="medium",
        )
        result.components["issue_backlog"] = BurnoutComponent(
            name="issue_backlog",
            score=10,
            status="moderate",
            details={"open_issues": 500},
        )

        d = result.to_dict()

        assert d["purl"] == "pkg:npm/test@1.0.0"
        assert d["burnout_score"] == 25
        assert d["grade"] == "B"
        assert "issue_backlog" in d["components"]


class TestBurnoutComponent:
    """Test BurnoutComponent data class."""

    def test_to_dict(self):
        """Test serialization."""
        component = BurnoutComponent(
            name="issue_backlog",
            score=10,
            max_score=20,
            status="moderate",
            details={"open_issues": 500},
        )
        d = component.to_dict()

        assert d["score"] == 10
        assert d["max_score"] == 20
        assert d["status"] == "moderate"
        assert d["open_issues"] == 500

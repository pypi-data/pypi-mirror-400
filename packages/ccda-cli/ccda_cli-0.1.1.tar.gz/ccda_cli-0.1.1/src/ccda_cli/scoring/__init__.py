"""Scoring calculations for ccda-cli."""

from ccda_cli.scoring.health import HealthScoreCalculator, HealthScoreResult
from ccda_cli.scoring.burnout import BurnoutScoreCalculator, BurnoutScoreResult

__all__ = [
    "HealthScoreCalculator",
    "HealthScoreResult",
    "BurnoutScoreCalculator",
    "BurnoutScoreResult",
]

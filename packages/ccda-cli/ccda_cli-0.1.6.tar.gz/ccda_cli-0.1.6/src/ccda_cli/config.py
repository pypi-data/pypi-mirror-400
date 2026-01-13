"""Configuration management for ccda-cli.

Supports loading from:
1. Default values
2. User config (~/.ccda/config.yaml)
3. Project config (./ccda-config.yaml)
4. Environment variables (CCDA_*)
5. CLI arguments (highest priority)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class CacheConfig(BaseModel):
    """Cache directory settings."""

    directory: Path = Field(default_factory=lambda: Path.home() / ".ccda")
    repos_dir: Path | None = None
    data_dir: Path | None = None
    users_dir: Path | None = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        """Set derived paths after initialization."""
        super().__init__(**data)
        if self.repos_dir is None:
            object.__setattr__(self, "repos_dir", self.directory / "repos")
        if self.data_dir is None:
            object.__setattr__(self, "data_dir", self.directory / "data")
        if self.users_dir is None:
            object.__setattr__(self, "users_dir", self.directory / "users")


class TTLConfig(BaseModel):
    """Time-to-live settings in hours (None = never expires)."""

    discovery: int | None = None
    tarball_scan: int | None = None
    git_metrics: int = 24
    github_api: int = 6
    health_score: int = 6
    burnout_score: int = 6
    unified: int = 6
    user_profiles: int = 720  # 30 days


class GitConfig(BaseModel):
    """Git clone settings."""

    clone_depth: int = 1000
    timeout_seconds: int = 300
    max_concurrent_clones: int = 3


class GitHubConfig(BaseModel):
    """GitHub API settings."""

    rate_limit_buffer: int = 100
    max_retries: int = 3
    retry_delay_seconds: int = 5
    enrich_company_affiliation: bool = True  # Requires github_token


class CompanyMappings(BaseModel):
    """Company affiliation detection mappings."""

    email_domains: dict[str, str] = Field(
        default_factory=lambda: {
            "amazon.com": "Amazon",
            "aws.com": "AWS",
            "google.com": "Google",
            "microsoft.com": "Microsoft",
            "redhat.com": "Red Hat",
            "uber.com": "Uber",
            "netflix.com": "Netflix",
            "meta.com": "Meta",
            "bytedance.com": "ByteDance",
            "github.com": "GitHub",
            "apple.com": "Apple",
            "ibm.com": "IBM",
        }
    )
    github_companies: dict[str, str] = Field(
        default_factory=lambda: {
            "@github": "GitHub",
            "@amazon": "Amazon",
            "@aws": "AWS",
            "@google": "Google",
            "@microsoft": "Microsoft",
            "Independent": "Independent",
            "Freelance": "Independent",
            "Self-employed": "Independent",
        }
    )


class TimeWindow(BaseModel):
    """Time window for analysis."""

    name: str
    days: int | None  # None = all time


class AnalysisConfig(BaseModel):
    """Analysis settings."""

    time_windows: list[TimeWindow] = Field(
        default_factory=lambda: [
            TimeWindow(name="90_days", days=90),
            TimeWindow(name="all_time", days=None),
        ]
    )
    thresholds: dict[str, int] = Field(
        default_factory=lambda: {
            "bus_factor_min": 3,
            "pony_factor_min": 3,
            "elephant_factor_min": 2,
        }
    )


class HealthScoringWeights(BaseModel):
    """Health score weights (must sum to 100)."""

    commit_activity: int = 15
    bus_factor: int = 10
    pony_factor: int = 10
    license_stability: int = 5
    contributor_retention: int = 10
    elephant_factor: int = 10
    issue_responsiveness: int = 10
    pr_velocity: int = 10
    branch_protection: int = 10
    release_frequency: int = 10


class BurnoutScoringWeights(BaseModel):
    """Burnout score max values (each 0-20)."""

    issue_backlog_max: int = 20
    response_gap_max: int = 20
    triage_overhead_max: int = 20
    workload_concentration_max: int = 20
    activity_decline_max: int = 20


class ScoringConfig(BaseModel):
    """Scoring configuration."""

    health: HealthScoringWeights = Field(default_factory=HealthScoringWeights)
    burnout: BurnoutScoringWeights = Field(default_factory=BurnoutScoringWeights)


class Config(BaseModel):
    """Main configuration model."""

    # API Keys
    github_token: str | None = None
    serpapi_key: str | None = None

    # Sub-configurations
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ttl: TTLConfig = Field(default_factory=TTLConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    company_mappings: CompanyMappings = Field(default_factory=CompanyMappings)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)

    @classmethod
    def load(
        cls,
        config_file: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> Config:
        """Load configuration from files and environment.

        Priority (highest to lowest):
        1. CLI overrides
        2. Environment variables
        3. Project config (./ccda-config.yaml)
        4. User config (~/.ccda/config.yaml)
        5. Default values
        """
        config_data: dict[str, Any] = {}

        # Load user config
        user_config = Path.home() / ".ccda" / "config.yaml"
        if user_config.exists():
            config_data = _merge_dicts(config_data, _load_yaml(user_config))

        # Load project config
        project_config = Path("ccda-config.yaml")
        if project_config.exists():
            config_data = _merge_dicts(config_data, _load_yaml(project_config))

        # Load specified config file
        if config_file and config_file.exists():
            config_data = _merge_dicts(config_data, _load_yaml(config_file))

        # Apply environment variables
        config_data = _apply_env_vars(config_data)

        # Apply CLI overrides
        if cli_overrides:
            config_data = _merge_dicts(config_data, cli_overrides)

        return cls.parse_obj(config_data)


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents."""
    with open(path) as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_vars(config_data: dict[str, Any]) -> dict[str, Any]:
    """Apply environment variables to config."""
    env_mappings = {
        "CCDA_GITHUB_TOKEN": ("github_token",),
        "CCDA_SERPAPI_KEY": ("serpapi_key",),
        "CCDA_CACHE_DIR": ("cache", "directory"),
    }

    result = config_data.copy()

    # Also check standard GITHUB_TOKEN if CCDA_GITHUB_TOKEN not set
    if "CCDA_GITHUB_TOKEN" not in os.environ and "GITHUB_TOKEN" in os.environ:
        env_mappings["GITHUB_TOKEN"] = ("github_token",)

    for env_var, keys in env_mappings.items():
        value = os.environ.get(env_var)
        if value is not None:
            current = result
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value

    return result


# Global config instance (set by CLI)
_config: Config | None = None


def get_config() -> Config:
    """Get the current configuration."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration."""
    global _config
    _config = config

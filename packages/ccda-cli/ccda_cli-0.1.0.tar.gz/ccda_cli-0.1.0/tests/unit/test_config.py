"""Unit tests for configuration module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ccda_cli.config import (
    Config,
    CacheConfig,
    TTLConfig,
    GitConfig,
    GitHubConfig,
    CompanyMappings,
    AnalysisConfig,
    ScoringConfig,
    HealthScoringWeights,
    _merge_dicts,
    _apply_env_vars,
)


class TestDefaultConfig:
    """Test default configuration values."""

    def test_default_config_creates_successfully(self):
        """Default config should load without errors."""
        config = Config()
        assert config is not None

    def test_default_github_token_is_none(self):
        """GitHub token should be None by default."""
        config = Config()
        assert config.github_token is None

    def test_default_serpapi_key_is_none(self):
        """SerpAPI key should be None by default."""
        config = Config()
        assert config.serpapi_key is None

    def test_default_cache_directory(self):
        """Default cache directory should be ~/.ccda."""
        config = Config()
        assert config.cache.directory == Path.home() / ".ccda"

    def test_default_ttl_values(self):
        """Test default TTL values match spec."""
        config = Config()
        assert config.ttl.discovery is None  # Never expires
        assert config.ttl.tarball_scan is None  # Never expires
        assert config.ttl.git_metrics == 24
        assert config.ttl.github_api == 6
        assert config.ttl.health_score == 6
        assert config.ttl.burnout_score == 6
        assert config.ttl.unified == 6
        assert config.ttl.user_profiles == 720  # 30 days

    def test_default_git_settings(self):
        """Test default git settings."""
        config = Config()
        assert config.git.clone_depth == 1000
        assert config.git.timeout_seconds == 300
        assert config.git.max_concurrent_clones == 3

    def test_default_github_settings(self):
        """Test default GitHub API settings."""
        config = Config()
        assert config.github.rate_limit_buffer == 100
        assert config.github.max_retries == 3
        assert config.github.retry_delay_seconds == 5


class TestCacheConfig:
    """Test cache configuration."""

    def test_derived_paths(self):
        """Derived paths should be set automatically."""
        cache = CacheConfig(directory=Path("/tmp/test-cache"))
        assert cache.repos_dir == Path("/tmp/test-cache/repos")
        assert cache.data_dir == Path("/tmp/test-cache/data")
        assert cache.users_dir == Path("/tmp/test-cache/users")

    def test_explicit_paths_override_derived(self):
        """Explicit paths should override derived ones."""
        cache = CacheConfig(
            directory=Path("/tmp/test-cache"),
            repos_dir=Path("/custom/repos"),
            data_dir=Path("/custom/data"),
            users_dir=Path("/custom/users"),
        )
        assert cache.repos_dir == Path("/custom/repos")
        assert cache.data_dir == Path("/custom/data")
        assert cache.users_dir == Path("/custom/users")


class TestCompanyMappings:
    """Test company affiliation mappings."""

    def test_default_email_domains(self):
        """Test default email domain mappings."""
        mappings = CompanyMappings()
        assert "amazon.com" in mappings.email_domains
        assert mappings.email_domains["amazon.com"] == "Amazon"
        assert mappings.email_domains["google.com"] == "Google"
        assert mappings.email_domains["microsoft.com"] == "Microsoft"

    def test_default_github_companies(self):
        """Test default GitHub company mappings."""
        mappings = CompanyMappings()
        assert mappings.github_companies["@github"] == "GitHub"
        assert mappings.github_companies["Independent"] == "Independent"
        assert mappings.github_companies["Freelance"] == "Independent"


class TestHealthScoringWeights:
    """Test health scoring weights."""

    def test_weights_sum_to_100(self):
        """Health scoring weights should sum to 100."""
        weights = HealthScoringWeights()
        total = (
            weights.commit_activity +
            weights.bus_factor +
            weights.pony_factor +
            weights.license_stability +
            weights.contributor_retention +
            weights.elephant_factor +
            weights.issue_responsiveness +
            weights.pr_velocity +
            weights.branch_protection +
            weights.release_frequency
        )
        assert total == 100


class TestMergeDicts:
    """Test dictionary merging utility."""

    def test_simple_merge(self):
        """Simple merge should combine keys."""
        base = {"a": 1, "b": 2}
        override = {"c": 3}
        result = _merge_dicts(base, override)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_override_value(self):
        """Override should replace existing values."""
        base = {"a": 1, "b": 2}
        override = {"b": 3}
        result = _merge_dicts(base, override)
        assert result == {"a": 1, "b": 3}

    def test_deep_merge(self):
        """Deep merge should handle nested dicts."""
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"y": 3, "z": 4}}
        result = _merge_dicts(base, override)
        assert result == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_base_unchanged(self):
        """Original dicts should not be modified."""
        base = {"a": 1}
        override = {"b": 2}
        _merge_dicts(base, override)
        assert base == {"a": 1}
        assert override == {"b": 2}


class TestApplyEnvVars:
    """Test environment variable application."""

    def test_github_token_from_env(self):
        """CCDA_GITHUB_TOKEN should set github_token."""
        with patch.dict(os.environ, {"CCDA_GITHUB_TOKEN": "test-token"}):
            result = _apply_env_vars({})
            assert result["github_token"] == "test-token"

    def test_serpapi_key_from_env(self):
        """CCDA_SERPAPI_KEY should set serpapi_key."""
        with patch.dict(os.environ, {"CCDA_SERPAPI_KEY": "test-key"}):
            result = _apply_env_vars({})
            assert result["serpapi_key"] == "test-key"

    def test_cache_dir_from_env(self):
        """CCDA_CACHE_DIR should set cache.directory."""
        with patch.dict(os.environ, {"CCDA_CACHE_DIR": "/custom/cache"}):
            result = _apply_env_vars({})
            assert result["cache"]["directory"] == "/custom/cache"

    def test_env_does_not_override_existing(self):
        """Existing values should be preserved (env has higher priority)."""
        with patch.dict(os.environ, {"CCDA_GITHUB_TOKEN": "env-token"}):
            result = _apply_env_vars({"github_token": "existing-token"})
            # Env vars override existing values
            assert result["github_token"] == "env-token"


class TestConfigLoad:
    """Test configuration loading."""

    def test_load_from_file(self, sample_config_yaml: Path, temp_dir: Path):
        """Config should load from YAML file."""
        config = Config.load(config_file=sample_config_yaml)
        assert config.github_token == "test-github-token"
        assert config.serpapi_key == "test-serpapi-key"
        assert config.ttl.git_metrics == 12
        assert config.ttl.github_api == 3

    def test_load_with_cli_overrides(self, sample_config_yaml: Path):
        """CLI overrides should take highest priority."""
        config = Config.load(
            config_file=sample_config_yaml,
            cli_overrides={"github_token": "cli-token"},
        )
        assert config.github_token == "cli-token"

    def test_load_with_env_override(self, sample_config_yaml: Path):
        """Environment variables should override file config."""
        with patch.dict(os.environ, {"CCDA_GITHUB_TOKEN": "env-token"}):
            config = Config.load(config_file=sample_config_yaml)
            # Env takes priority over file
            assert config.github_token == "env-token"

    def test_load_defaults_without_file(self):
        """Config should load with defaults when no file exists."""
        config = Config.load(config_file=Path("/nonexistent/config.yaml"))
        assert config is not None
        assert config.ttl.git_metrics == 24  # Default value

    def test_custom_company_mapping_from_file(self, sample_config_yaml: Path):
        """Custom company mappings should be loaded from file."""
        config = Config.load(config_file=sample_config_yaml)
        assert "test.com" in config.company_mappings.email_domains
        assert config.company_mappings.email_domains["test.com"] == "Test Corp"


class TestAnalysisConfig:
    """Test analysis configuration."""

    def test_default_time_windows(self):
        """Default time windows should be 90 days and all time."""
        config = AnalysisConfig()
        assert len(config.time_windows) == 2
        assert config.time_windows[0].name == "90_days"
        assert config.time_windows[0].days == 90
        assert config.time_windows[1].name == "all_time"
        assert config.time_windows[1].days is None

    def test_default_thresholds(self):
        """Default thresholds should match spec."""
        config = AnalysisConfig()
        assert config.thresholds["bus_factor_min"] == 3
        assert config.thresholds["pony_factor_min"] == 3
        assert config.thresholds["elephant_factor_min"] == 2

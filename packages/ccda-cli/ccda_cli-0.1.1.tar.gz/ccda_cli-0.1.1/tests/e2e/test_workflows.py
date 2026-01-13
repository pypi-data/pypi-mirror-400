"""End-to-end workflow tests for ccda-cli.

These tests validate complete user workflows and require
proper environment setup (may make real API calls in some modes).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from click.testing import CliRunner

from ccda_cli.cli import cli
from ccda_cli.config import Config
from ccda_cli.cache.manager import CacheManager


class TestCacheWorkflow:
    """Test cache management workflow."""

    @pytest.fixture
    def isolated_env(self):
        """Create isolated environment for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".ccda"
            cache_dir.mkdir(parents=True)
            (cache_dir / "repos").mkdir()
            (cache_dir / "data").mkdir()
            (cache_dir / "users").mkdir()

            # Create mock config
            with patch("ccda_cli.cache.manager.get_config") as mock_config:
                config = MagicMock()
                config.cache.directory = cache_dir
                config.cache.repos_dir = cache_dir / "repos"
                config.cache.data_dir = cache_dir / "data"
                config.cache.users_dir = cache_dir / "users"
                config.ttl.discovery = None
                config.ttl.git_metrics = 24
                config.ttl.github_api = 6
                config.ttl.user_profiles = 720
                mock_config.return_value = config

                yield {
                    "cache_dir": cache_dir,
                    "config": config,
                    "mock_config": mock_config,
                }

    def test_cache_lifecycle(self, isolated_env):
        """Test full cache lifecycle: create, read, expire, clean."""
        cache_dir = isolated_env["cache_dir"]

        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=cache_dir)

            # 1. Save package data
            purl = "pkg:npm/express@4.18.2"
            manager.save_package_data(purl, "discovery.json", {
                "name": "express",
                "version": "4.18.2",
            })

            # 2. Verify it exists
            entry = manager.get_package_data(purl, "discovery.json")
            assert entry is not None
            assert entry.data["name"] == "express"

            # 3. Save user profile
            manager.save_user_profile("octocat", {
                "login": "octocat",
                "company": "@github",
            })

            # 4. Check stats
            stats = manager.get_stats()
            assert stats["packages"]["count"] == 1
            assert stats["users"]["count"] == 1

            # 5. List all cached items
            packages = manager.list_packages()
            assert len(packages) == 1
            assert packages[0]["name"] == "express"

            users = manager.list_users()
            assert len(users) == 1
            assert users[0]["username"] == "octocat"

            # 6. Clear specific items
            manager.clear_package(purl)
            assert manager.get_package_data(purl, "discovery.json") is None

            manager.clear_user("octocat")
            assert manager.get_user_profile("octocat") is None

            # 7. Verify cleanup
            stats = manager.get_stats()
            assert stats["packages"]["count"] == 0
            assert stats["users"]["count"] == 0


class TestConfigWorkflow:
    """Test configuration workflow."""

    def test_config_priority_chain(self):
        """Test config loading priority: defaults < file < env < cli."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""
github_token: "file-token"
ttl:
  git_metrics: 48
""")

            # Test 1: File overrides defaults
            config = Config.load(config_file=config_file)
            assert config.github_token == "file-token"
            assert config.ttl.git_metrics == 48
            assert config.ttl.github_api == 6  # Default

            # Test 2: Env overrides file
            with patch.dict(os.environ, {"CCDA_GITHUB_TOKEN": "env-token"}):
                config = Config.load(config_file=config_file)
                assert config.github_token == "env-token"

            # Test 3: CLI overrides everything
            with patch.dict(os.environ, {"CCDA_GITHUB_TOKEN": "env-token"}):
                config = Config.load(
                    config_file=config_file,
                    cli_overrides={"github_token": "cli-token"},
                )
                assert config.github_token == "cli-token"


class TestPURLHandling:
    """Test PURL handling across the system."""

    @pytest.fixture
    def isolated_env(self):
        """Create isolated environment for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".ccda"
            cache_dir.mkdir(parents=True)
            (cache_dir / "data").mkdir()

            with patch("ccda_cli.cache.manager.get_config") as mock_config:
                config = MagicMock()
                config.cache.directory = cache_dir
                config.cache.repos_dir = cache_dir / "repos"
                config.cache.data_dir = cache_dir / "data"
                config.cache.users_dir = cache_dir / "users"
                config.ttl.discovery = None
                mock_config.return_value = config

                yield {
                    "cache_dir": cache_dir,
                    "mock_config": mock_config,
                }

    def test_npm_purl_caching(self, isolated_env):
        """Test npm PURL resolution and caching."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            # Simple npm package
            purl = "pkg:npm/express@4.18.2"
            manager.save_package_data(purl, "discovery.json", {"name": "express"})

            pkg_dir = manager.get_package_dir(purl)
            assert "pkg--npm" in str(pkg_dir)
            assert "express" in str(pkg_dir)
            assert "4.18.2" in str(pkg_dir)

    def test_scoped_npm_purl_caching(self, isolated_env):
        """Test scoped npm PURL resolution."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            # Scoped npm package
            purl = "pkg:npm/@babel/core@7.0.0"
            manager.save_package_data(purl, "discovery.json", {"name": "@babel/core"})

            pkg_dir = manager.get_package_dir(purl)
            assert "pkg--npm" in str(pkg_dir)
            assert "@babel--core" in str(pkg_dir)

    def test_pypi_purl_caching(self, isolated_env):
        """Test PyPI PURL resolution."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            purl = "pkg:pypi/requests@2.28.0"
            manager.save_package_data(purl, "discovery.json", {"name": "requests"})

            pkg_dir = manager.get_package_dir(purl)
            assert "pkg--pypi" in str(pkg_dir)
            assert "requests" in str(pkg_dir)

    def test_maven_purl_caching(self, isolated_env):
        """Test Maven PURL resolution with namespace."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            purl = "pkg:maven/org.apache.commons/commons-lang3@3.12.0"
            manager.save_package_data(purl, "discovery.json", {"name": "commons-lang3"})

            pkg_dir = manager.get_package_dir(purl)
            assert "pkg--maven" in str(pkg_dir)
            assert "org.apache.commons--commons-lang3" in str(pkg_dir)


class TestCLIWorkflow:
    """Test CLI command workflows."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_help_commands(self, runner: CliRunner):
        """Test all help commands work."""
        commands = [
            ["--help"],
            ["discover", "--help"],
            ["clone", "--help"],
            ["clone-batch", "--help"],
            ["git-metrics", "--help"],
            ["github-metrics", "--help"],
            ["scan-tarball", "--help"],
            ["health-score", "--help"],
            ["burnout-score", "--help"],
            ["analyze", "--help"],
            ["report", "--help"],
            ["cache", "--help"],
            ["cache", "info", "--help"],
            ["cache", "clear", "--help"],
        ]

        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Failed for: {cmd}\n{result.output}"

    def test_config_roundtrip(self, runner: CliRunner):
        """Test config show produces valid output."""
        result = runner.invoke(cli, ["config-show"])
        assert result.exit_code == 0

        # Output should contain expected sections
        output = result.output
        assert "cache" in output or "github" in output

    def test_analyze_command_accepts_options(self, runner: CliRunner):
        """Test analyze command with all options."""
        result = runner.invoke(cli, [
            "analyze",
            "pkg:npm/express@4.18.2",
            "--skip-clone",
            "--skip-tarball",
        ])
        assert result.exit_code == 0
        assert "Full analysis:" in result.output


class TestErrorHandling:
    """Test error handling across the system."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_invalid_purl_format(self, runner: CliRunner):
        """Test handling of invalid PURL."""
        # Invalid PURL should cause an error during parsing
        result = runner.invoke(cli, ["discover", "invalid-purl"])
        # It will fail because of invalid PURL format
        assert result.exit_code != 0 or "Error" in result.output

    def test_nonexistent_input_file(self, runner: CliRunner):
        """Test handling of missing input file."""
        result = runner.invoke(cli, ["clone-batch", "nonexistent.txt"])
        assert result.exit_code != 0  # Click validates file exists

    def test_nonexistent_config_file(self, runner: CliRunner):
        """Test handling of missing config file."""
        result = runner.invoke(cli, [
            "--config", "/nonexistent/config.yaml",
            "discover", "pkg:npm/test@1.0.0"
        ])
        # Click validates file exists with exists=True
        assert result.exit_code != 0


class TestDataFormats:
    """Test data format consistency."""

    @pytest.fixture
    def isolated_env(self):
        """Create isolated environment for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".ccda"
            cache_dir.mkdir(parents=True)
            (cache_dir / "data").mkdir()
            (cache_dir / "users").mkdir()

            with patch("ccda_cli.cache.manager.get_config") as mock_config:
                config = MagicMock()
                config.cache.directory = cache_dir
                config.cache.repos_dir = cache_dir / "repos"
                config.cache.data_dir = cache_dir / "data"
                config.cache.users_dir = cache_dir / "users"
                config.ttl.discovery = None
                config.ttl.git_metrics = 24
                config.ttl.github_api = 6
                config.ttl.user_profiles = 720
                mock_config.return_value = config

                yield {
                    "cache_dir": cache_dir,
                    "mock_config": mock_config,
                }

    def test_cached_data_is_valid_json(self, isolated_env):
        """Test that cached data is valid JSON."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            # Save data
            purl = "pkg:npm/express@4.18.2"
            manager.save_package_data(purl, "test.json", {
                "name": "express",
                "nested": {"key": "value"},
                "list": [1, 2, 3],
            })

            # Read raw file
            pkg_dir = manager.get_package_dir(purl)
            file_path = pkg_dir / "test.json"

            with open(file_path) as f:
                data = json.load(f)

            assert data["name"] == "express"
            assert data["nested"]["key"] == "value"
            assert data["list"] == [1, 2, 3]
            assert "cached_at" in data  # Auto-added

    def test_user_profile_format(self, isolated_env):
        """Test user profile format matches spec."""
        with patch("ccda_cli.cache.manager.get_config", isolated_env["mock_config"]):
            manager = CacheManager(base_dir=isolated_env["cache_dir"])

            # Save profile matching spec format
            manager.save_user_profile("octocat", {
                "login": "octocat",
                "name": "The Octocat",
                "company": "@github",
                "location": "San Francisco",
                "email": "octocat@github.com",
                "public_repos": 8,
                "followers": 5000,
            })

            # Read and verify
            entry = manager.get_user_profile("octocat")
            assert entry is not None

            data = entry.data
            assert data["login"] == "octocat"
            assert data["company"] == "@github"
            assert "cached_at" in data

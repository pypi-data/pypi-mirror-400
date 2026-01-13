"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock

import pytest

# Note: Don't set CCDA_GITHUB_TOKEN here as it would override config file tests


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_cache_dir(temp_dir: Path) -> Path:
    """Create a temporary cache directory structure."""
    cache_dir = temp_dir / ".ccda"
    (cache_dir / "repos").mkdir(parents=True)
    (cache_dir / "data").mkdir(parents=True)
    (cache_dir / "users").mkdir(parents=True)
    return cache_dir


@pytest.fixture
def sample_config_yaml(temp_dir: Path) -> Path:
    """Create a sample config.yaml file."""
    config_path = temp_dir / "config.yaml"
    config_content = """
github_token: "test-github-token"
serpapi_key: "test-serpapi-key"

cache:
  directory: "{cache_dir}"

ttl:
  git_metrics: 12
  github_api: 3

git:
  clone_depth: 500
  timeout_seconds: 120

company_mappings:
  email_domains:
    "test.com": "Test Corp"
""".format(cache_dir=str(temp_dir / ".ccda"))

    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def sample_purl() -> str:
    """Sample PURL for testing."""
    return "pkg:npm/express@4.18.2"


@pytest.fixture
def sample_github_purl() -> str:
    """Sample GitHub PURL for testing."""
    return "pkg:github/expressjs/express@4.18.2"


@pytest.fixture
def sample_repo_url() -> str:
    """Sample repository URL."""
    return "https://github.com/expressjs/express"


@pytest.fixture
def sample_discovery_response() -> dict[str, Any]:
    """Sample discovery API response."""
    return {
        "purl": "pkg:npm/express@4.18.2",
        "name": "express",
        "version": "4.18.2",
        "latest_version": "4.18.2",
        "license": "MIT",
        "repository": "https://github.com/expressjs/express",
        "tarball_url": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
    }


@pytest.fixture
def sample_git_metrics() -> dict[str, Any]:
    """Sample git metrics response."""
    return {
        "repo_url": "https://github.com/expressjs/express",
        "analyzed_at": "2026-01-03T20:00:00Z",
        "method": "git_offline",
        "time_windows": {
            "90_days": {
                "total_commits": 150,
                "unique_contributors": 35,
                "bus_factor": 8,
                "pony_factor": 8,
                "elephant_factor": 2,
                "contributor_retention": 53.0,
                "commits_per_day": 1.67,
            },
            "all_time": {
                "total_commits": 5000,
                "unique_contributors": 200,
                "bus_factor": 10,
                "pony_factor": 10,
                "elephant_factor": 2,
            },
        },
    }


@pytest.fixture
def sample_github_api_response() -> dict[str, Any]:
    """Sample GitHub API response."""
    return {
        "repo_url": "https://github.com/expressjs/express",
        "fetched_at": "2026-01-03T20:00:00Z",
        "method": "github_api",
        "repository": {
            "stars": 60000,
            "forks": 10000,
            "watchers": 2000,
            "default_branch": "master",
            "license": "MIT",
        },
        "issues": {
            "open_count": 2511,
            "closed_count": 5000,
            "unresponded_rate_7d": 23.0,
            "unlabeled_rate": 0.0,
        },
        "pull_requests": {
            "open_count": 20,
            "merged_count": 3000,
            "avg_merge_hours": 48.5,
        },
    }


@pytest.fixture
def sample_user_profile() -> dict[str, Any]:
    """Sample GitHub user profile."""
    return {
        "login": "octocat",
        "name": "The Octocat",
        "company": "@github",
        "location": "San Francisco",
        "email": "octocat@github.com",
        "public_repos": 8,
        "followers": 5000,
    }


@pytest.fixture
def mock_httpx_response():
    """Factory for mock httpx responses."""
    def _create_response(
        status_code: int = 200,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = json.dumps(json_data or {})
        response.headers = headers or {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-used": "1",
        }
        return response

    return _create_response


@pytest.fixture
def mock_github_client(mock_httpx_response):
    """Mock GitHub client for testing."""
    from unittest.mock import patch, MagicMock

    with patch("ccda_cli.core.http.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = instance

        # Default successful response
        instance.request.return_value = mock_httpx_response(
            status_code=200,
            json_data={"login": "test"},
        )

        yield instance


# CLI test fixtures
@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture
def isolated_cli_runner():
    """Isolated Click CLI test runner with temp filesystem."""
    from click.testing import CliRunner

    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner

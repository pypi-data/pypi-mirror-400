"""Unit tests for cache management module."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ccda_cli.cache.manager import CacheManager, CacheEntry


class TestCacheEntry:
    """Test cache entry behavior."""

    def test_cache_entry_not_expired(self):
        """Entry with TTL in future should not be expired."""
        entry = CacheEntry(
            path=Path("/test"),
            data={"test": "data"},
            created_at=datetime.now(),
            ttl_hours=24,
        )
        assert entry.is_expired is False

    def test_cache_entry_expired(self):
        """Entry with TTL in past should be expired."""
        entry = CacheEntry(
            path=Path("/test"),
            data={"test": "data"},
            created_at=datetime.now() - timedelta(hours=25),
            ttl_hours=24,
        )
        assert entry.is_expired is True

    def test_cache_entry_no_ttl_never_expires(self):
        """Entry with None TTL should never expire."""
        entry = CacheEntry(
            path=Path("/test"),
            data={"test": "data"},
            created_at=datetime.now() - timedelta(days=365),
            ttl_hours=None,
        )
        assert entry.is_expired is False

    def test_cache_entry_age_hours(self):
        """age_hours should return correct value."""
        entry = CacheEntry(
            path=Path("/test"),
            data={"test": "data"},
            created_at=datetime.now() - timedelta(hours=5),
            ttl_hours=24,
        )
        assert 4.9 < entry.age_hours < 5.1


class TestCacheManager:
    """Test cache manager functionality."""

    @pytest.fixture
    def mock_config(self, temp_cache_dir: Path):
        """Create mock config for cache manager."""
        with patch("ccda_cli.cache.manager.get_config") as mock:
            config = MagicMock()
            config.cache.directory = temp_cache_dir
            config.cache.repos_dir = temp_cache_dir / "repos"
            config.cache.data_dir = temp_cache_dir / "data"
            config.cache.users_dir = temp_cache_dir / "users"
            config.ttl.discovery = None
            config.ttl.tarball_scan = None
            config.ttl.git_metrics = 24
            config.ttl.github_api = 6
            config.ttl.health_score = 6
            config.ttl.burnout_score = 6
            config.ttl.unified = 6
            config.ttl.user_profiles = 720
            mock.return_value = config
            yield mock

    def test_cache_manager_initialization(self, mock_config, temp_cache_dir: Path):
        """Cache manager should initialize directories."""
        manager = CacheManager(base_dir=temp_cache_dir)
        assert manager.base_dir == temp_cache_dir
        assert manager.repos_dir.exists()
        assert manager.data_dir.exists()
        assert manager.users_dir.exists()

    def test_get_package_dir_npm(self, mock_config, temp_cache_dir: Path):
        """Package dir should be constructed correctly for npm."""
        manager = CacheManager(base_dir=temp_cache_dir)
        pkg_dir = manager.get_package_dir("pkg:npm/express@4.18.2")
        assert pkg_dir == temp_cache_dir / "data" / "pkg--npm" / "express" / "4.18.2"

    def test_get_package_dir_scoped_npm(self, mock_config, temp_cache_dir: Path):
        """Package dir should handle scoped npm packages."""
        manager = CacheManager(base_dir=temp_cache_dir)
        pkg_dir = manager.get_package_dir("pkg:npm/@babel/core@7.0.0")
        assert pkg_dir == temp_cache_dir / "data" / "pkg--npm" / "@babel--core" / "7.0.0"

    def test_get_package_dir_no_version(self, mock_config, temp_cache_dir: Path):
        """Package dir should use 'latest' when no version specified."""
        manager = CacheManager(base_dir=temp_cache_dir)
        pkg_dir = manager.get_package_dir("pkg:npm/express")
        assert pkg_dir == temp_cache_dir / "data" / "pkg--npm" / "express" / "latest"

    def test_save_and_get_package_data(self, mock_config, temp_cache_dir: Path):
        """Should save and retrieve package data."""
        manager = CacheManager(base_dir=temp_cache_dir)
        purl = "pkg:npm/express@4.18.2"

        # Save data
        data = {"name": "express", "version": "4.18.2"}
        path = manager.save_package_data(purl, "discovery.json", data)
        assert path.exists()

        # Retrieve data
        entry = manager.get_package_data(purl, "discovery.json")
        assert entry is not None
        assert entry.data["name"] == "express"
        assert "cached_at" in entry.data

    def test_get_package_data_expired(self, mock_config, temp_cache_dir: Path):
        """Should return None for expired data."""
        manager = CacheManager(base_dir=temp_cache_dir)
        purl = "pkg:npm/express@4.18.2"

        # Save data with old timestamp
        data = {
            "name": "express",
            "cached_at": (datetime.now() - timedelta(hours=25)).isoformat(),
        }
        pkg_dir = manager.get_package_dir(purl)
        pkg_dir.mkdir(parents=True, exist_ok=True)
        file_path = pkg_dir / "git-metrics.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        # Should return None because TTL (24h) is exceeded
        entry = manager.get_package_data(purl, "git-metrics.json", ttl_hours=24)
        assert entry is None

    def test_get_package_data_not_found(self, mock_config, temp_cache_dir: Path):
        """Should return None for non-existent data."""
        manager = CacheManager(base_dir=temp_cache_dir)
        entry = manager.get_package_data("pkg:npm/nonexistent@1.0.0", "discovery.json")
        assert entry is None

    def test_save_and_get_user_profile(self, mock_config, temp_cache_dir: Path):
        """Should save and retrieve user profiles."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Save profile
        profile = {"login": "octocat", "name": "The Octocat"}
        path = manager.save_user_profile("octocat", profile)
        assert path.exists()

        # Retrieve profile
        entry = manager.get_user_profile("octocat")
        assert entry is not None
        assert entry.data["login"] == "octocat"

    def test_get_user_profile_not_found(self, mock_config, temp_cache_dir: Path):
        """Should return None for non-existent user."""
        manager = CacheManager(base_dir=temp_cache_dir)
        entry = manager.get_user_profile("nonexistent")
        assert entry is None

    def test_get_repo_path(self, mock_config, temp_cache_dir: Path):
        """Repo path should be constructed correctly."""
        manager = CacheManager(base_dir=temp_cache_dir)
        path = manager.get_repo_path("https://github.com/expressjs/express")
        assert path == temp_cache_dir / "repos" / "github.com" / "expressjs" / "express"

    def test_get_repo_path_with_git_suffix(self, mock_config, temp_cache_dir: Path):
        """Repo path should strip .git suffix."""
        manager = CacheManager(base_dir=temp_cache_dir)
        path = manager.get_repo_path("https://github.com/expressjs/express.git")
        assert path == temp_cache_dir / "repos" / "github.com" / "expressjs" / "express"

    def test_is_repo_cloned(self, mock_config, temp_cache_dir: Path):
        """Should detect cloned repositories."""
        manager = CacheManager(base_dir=temp_cache_dir)
        repo_url = "https://github.com/test/repo"

        # Not cloned yet
        assert manager.is_repo_cloned(repo_url) is False

        # Create fake clone
        repo_path = manager.get_repo_path(repo_url)
        (repo_path / ".git").mkdir(parents=True)
        assert manager.is_repo_cloned(repo_url) is True

    def test_save_and_get_repo_metadata(self, mock_config, temp_cache_dir: Path):
        """Should save and retrieve repo metadata."""
        manager = CacheManager(base_dir=temp_cache_dir)
        repo_url = "https://github.com/test/repo"

        # Create repo dir
        repo_path = manager.get_repo_path(repo_url)
        repo_path.mkdir(parents=True)

        # Save metadata
        metadata = {
            "repo_url": repo_url,
            "cloned_at": datetime.now().isoformat(),
            "clone_depth": 1000,
        }
        path = manager.save_repo_metadata(repo_url, metadata)
        assert path.exists()

        # Retrieve metadata
        entry = manager.get_repo_metadata(repo_url)
        assert entry is not None
        assert entry.data["clone_depth"] == 1000

    def test_clear_package(self, mock_config, temp_cache_dir: Path):
        """Should clear package cache."""
        manager = CacheManager(base_dir=temp_cache_dir)
        purl = "pkg:npm/express@4.18.2"

        # Save data
        manager.save_package_data(purl, "discovery.json", {"test": "data"})
        pkg_dir = manager.get_package_dir(purl)
        assert pkg_dir.exists()

        # Clear
        result = manager.clear_package(purl)
        assert result is True
        assert not pkg_dir.exists()

    def test_clear_user(self, mock_config, temp_cache_dir: Path):
        """Should clear user profile."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Save profile
        manager.save_user_profile("testuser", {"login": "testuser"})
        file_path = manager.users_dir / "testuser.json"
        assert file_path.exists()

        # Clear
        result = manager.clear_user("testuser")
        assert result is True
        assert not file_path.exists()

    def test_list_packages(self, mock_config, temp_cache_dir: Path):
        """Should list all cached packages."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Save some packages
        manager.save_package_data("pkg:npm/express@4.18.2", "discovery.json", {})
        manager.save_package_data("pkg:npm/lodash@4.17.21", "discovery.json", {})
        manager.save_package_data("pkg:pypi/requests@2.28.0", "discovery.json", {})

        packages = manager.list_packages()
        assert len(packages) == 3

    def test_list_repos(self, mock_config, temp_cache_dir: Path):
        """Should list all cloned repos."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Create fake clones
        for repo in ["repo1", "repo2"]:
            repo_path = manager.repos_dir / "github.com" / "owner" / repo
            (repo_path / ".git").mkdir(parents=True)

        repos = manager.list_repos()
        assert len(repos) == 2

    def test_list_users(self, mock_config, temp_cache_dir: Path):
        """Should list all cached users."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Save some users
        manager.save_user_profile("user1", {"login": "user1"})
        manager.save_user_profile("user2", {"login": "user2"})

        users = manager.list_users()
        assert len(users) == 2

    def test_get_stats(self, mock_config, temp_cache_dir: Path):
        """Should return cache statistics."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Add some data
        manager.save_package_data("pkg:npm/express@4.18.2", "discovery.json", {"data": "x" * 1000})
        manager.save_user_profile("testuser", {"login": "testuser"})

        stats = manager.get_stats()
        assert stats["packages"]["count"] == 1
        assert stats["users"]["count"] == 1
        assert stats["total_size_bytes"] > 0

    def test_clear_all(self, mock_config, temp_cache_dir: Path):
        """Should clear all cache data."""
        manager = CacheManager(base_dir=temp_cache_dir)

        # Add some data
        manager.save_package_data("pkg:npm/express@4.18.2", "discovery.json", {})
        manager.save_user_profile("testuser", {"login": "testuser"})

        # Clear all
        counts = manager.clear_all(data=True, users=True)
        assert counts["data"] >= 1
        assert counts["users"] >= 1

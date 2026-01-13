"""Tests for git repository management."""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ccda_cli.core.git import GitManager, CloneResult, GitCloneError


class TestCloneResult:
    """Tests for CloneResult dataclass."""

    def test_to_dict_success(self):
        """Test successful clone result serialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path(tmpdir) / "repo",
                success=True,
                cloned_at=datetime(2024, 1, 1, 12, 0, 0),
                clone_depth=1000,
                last_commit_hash="abc123",
                last_commit_date=datetime(2024, 1, 1, 10, 0, 0),
            )

            data = result.to_dict()

            assert data["repo_url"] == "https://github.com/test/repo"
            assert "repo" in data["local_path"]
            assert data["success"] is True
            assert data["clone_depth"] == 1000
            assert data["last_commit_hash"] == "abc123"
            assert data["error"] is None

    def test_to_dict_failure(self):
        """Test failed clone result serialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path(tmpdir) / "repo",
                success=False,
                cloned_at=datetime(2024, 1, 1, 12, 0, 0),
                clone_depth=1000,
                error="Clone failed: repository not found",
            )

            data = result.to_dict()

            assert data["success"] is False
            assert data["error"] == "Clone failed: repository not found"
            assert data["last_commit_hash"] is None


class TestGitManager:
    """Tests for GitManager class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = MagicMock()
        config.git.clone_depth = 1000
        config.git.timeout_seconds = 300
        config.git.max_concurrent_clones = 3
        return config

    @pytest.fixture
    def mock_cache(self, temp_cache_dir):
        """Create mock cache manager."""
        cache = MagicMock()
        cache.get_repo_path.return_value = temp_cache_dir / "repos" / "github.com" / "test" / "repo"
        cache.is_repo_cloned.return_value = False
        return cache

    @pytest.fixture
    def manager(self, mock_config, mock_cache):
        """Create GitManager with mocked dependencies."""
        with patch("ccda_cli.core.git.get_config", return_value=mock_config):
            with patch("ccda_cli.core.git.CacheManager", return_value=mock_cache):
                return GitManager()

    @pytest.mark.asyncio
    async def test_clone_success(self, manager, mock_cache):
        """Test successful clone."""
        mock_cache.is_repo_cloned.return_value = False

        with patch.object(manager, "_run_clone", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path("/tmp/repo"),
                success=True,
                cloned_at=datetime.now(),
                clone_depth=1000,
                last_commit_hash="abc123",
            )

            result = await manager.clone("https://github.com/test/repo")

            assert result.success is True
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_clone_existing_no_force(self, manager, mock_cache):
        """Test clone when repo already exists and force=False."""
        mock_cache.is_repo_cloned.return_value = True

        with patch.object(manager, "_get_existing_clone", new_callable=AsyncMock) as mock_existing:
            mock_existing.return_value = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path("/tmp/repo"),
                success=True,
                cloned_at=datetime.now(),
                clone_depth=1000,
            )

            result = await manager.clone("https://github.com/test/repo")

            assert result.success is True
            mock_existing.assert_called_once()

    @pytest.mark.asyncio
    async def test_clone_existing_with_force(self, manager, mock_cache):
        """Test clone when repo exists and force=True."""
        mock_cache.is_repo_cloned.return_value = True
        mock_cache.get_repo_path.return_value = Path("/tmp/nonexistent")

        with patch.object(manager, "_run_clone", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path("/tmp/repo"),
                success=True,
                cloned_at=datetime.now(),
                clone_depth=1000,
            )

            result = await manager.clone("https://github.com/test/repo", force=True)

            assert result.success is True
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_clone_failure(self, manager, mock_cache):
        """Test clone failure handling."""
        mock_cache.is_repo_cloned.return_value = False

        with patch.object(manager, "_run_clone", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = GitCloneError("Repository not found")

            result = await manager.clone("https://github.com/test/notfound")

            assert result.success is False
            assert "Repository not found" in result.error

    @pytest.mark.asyncio
    async def test_clone_batch(self, manager):
        """Test batch cloning."""
        urls = [
            "https://github.com/test/repo1",
            "https://github.com/test/repo2",
            "https://github.com/test/repo3",
        ]

        with patch.object(manager, "clone", new_callable=AsyncMock) as mock_clone:
            mock_clone.return_value = CloneResult(
                repo_url="https://github.com/test/repo",
                local_path=Path("/tmp/repo"),
                success=True,
                cloned_at=datetime.now(),
                clone_depth=1000,
            )

            results = await manager.clone_batch(urls, concurrency=2)

            assert len(results) == 3
            assert mock_clone.call_count == 3

    def test_list_clones(self, manager, mock_cache):
        """Test listing cloned repositories."""
        mock_cache.list_repos.return_value = [
            {"url": "https://github.com/test/repo1"},
            {"url": "https://github.com/test/repo2"},
        ]

        repos = manager.list_clones()

        assert len(repos) == 2
        mock_cache.list_repos.assert_called_once()

    def test_delete_clone(self, manager, mock_cache):
        """Test deleting a clone."""
        mock_cache.clear_repo.return_value = True

        result = manager.delete_clone("https://github.com/test/repo")

        assert result is True
        mock_cache.clear_repo.assert_called_once_with("https://github.com/test/repo")

    def test_get_stale_clones(self, manager, mock_cache):
        """Test getting stale clones."""
        mock_cache.list_repos.return_value = [
            {
                "url": "https://github.com/test/old",
                "cloned_at": "2020-01-01T00:00:00",
            },
            {
                "url": "https://github.com/test/recent",
                "cloned_at": datetime.now().isoformat(),
            },
        ]

        stale = manager.get_stale_clones(max_age_hours=24)

        # The old one should be stale
        assert len(stale) == 1
        assert stale[0]["url"] == "https://github.com/test/old"

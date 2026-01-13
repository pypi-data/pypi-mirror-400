"""Git repository management.

Handles cloning, updating, and managing local repository clones.
"""

from __future__ import annotations

import asyncio
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ccda_cli.cache import CacheManager
from ccda_cli.config import get_config


@dataclass
class CloneResult:
    """Result of a clone operation."""

    repo_url: str
    local_path: Path
    success: bool
    cloned_at: datetime
    clone_depth: int
    last_commit_hash: str | None = None
    last_commit_date: datetime | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repo_url": self.repo_url,
            "local_path": str(self.local_path),
            "success": self.success,
            "cloned_at": self.cloned_at.isoformat(),
            "clone_depth": self.clone_depth,
            "last_commit_hash": self.last_commit_hash,
            "last_commit_date": self.last_commit_date.isoformat() if self.last_commit_date else None,
            "error": self.error,
        }


class GitCloneError(Exception):
    """Git clone operation error."""

    pass


class GitManager:
    """Manages git repository operations."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize git manager.

        Args:
            cache_dir: Custom cache directory (uses config default if None)
        """
        self.config = get_config()
        self.cache = CacheManager(base_dir=cache_dir)

    async def clone(
        self,
        repo_url: str,
        depth: int | None = None,
        force: bool = False,
    ) -> CloneResult:
        """Clone a repository.

        Args:
            repo_url: Repository URL to clone
            depth: Clone depth (None for full clone)
            force: Force re-clone even if exists

        Returns:
            CloneResult with clone details
        """
        depth = depth or self.config.git.clone_depth
        local_path = self.cache.get_repo_path(repo_url)

        # Check if already cloned
        if self.cache.is_repo_cloned(repo_url) and not force:
            # Update metadata and return existing
            return await self._get_existing_clone(repo_url, local_path)

        # Create parent directories
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing if forcing
        if force and local_path.exists():
            import shutil
            shutil.rmtree(local_path)

        # Clone the repository
        try:
            result = await self._run_clone(repo_url, local_path, depth)

            # Save metadata
            self.cache.save_repo_metadata(repo_url, result.to_dict())

            return result

        except Exception as e:
            return CloneResult(
                repo_url=repo_url,
                local_path=local_path,
                success=False,
                cloned_at=datetime.now(),
                clone_depth=depth,
                error=str(e),
            )

    async def _run_clone(
        self,
        repo_url: str,
        local_path: Path,
        depth: int,
    ) -> CloneResult:
        """Execute git clone command."""
        cmd = [
            "git",
            "clone",
            "--depth", str(depth),
            repo_url,
            str(local_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.git.timeout_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            raise GitCloneError(f"Clone timed out after {self.config.git.timeout_seconds}s")

        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            raise GitCloneError(f"Clone failed: {error_msg}")

        # Get last commit info
        commit_hash, commit_date = await self._get_last_commit(local_path)

        return CloneResult(
            repo_url=repo_url,
            local_path=local_path,
            success=True,
            cloned_at=datetime.now(),
            clone_depth=depth,
            last_commit_hash=commit_hash,
            last_commit_date=commit_date,
        )

    async def _get_existing_clone(
        self,
        repo_url: str,
        local_path: Path,
    ) -> CloneResult:
        """Get info about existing clone."""
        metadata = self.cache.get_repo_metadata(repo_url)
        commit_hash, commit_date = await self._get_last_commit(local_path)

        if metadata:
            cloned_at = datetime.fromisoformat(metadata.data.get("cloned_at", datetime.now().isoformat()))
            depth = metadata.data.get("clone_depth", self.config.git.clone_depth)
        else:
            cloned_at = datetime.now()
            depth = self.config.git.clone_depth

        return CloneResult(
            repo_url=repo_url,
            local_path=local_path,
            success=True,
            cloned_at=cloned_at,
            clone_depth=depth,
            last_commit_hash=commit_hash,
            last_commit_date=commit_date,
        )

    async def _get_last_commit(self, repo_path: Path) -> tuple[str | None, datetime | None]:
        """Get the last commit hash and date."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "log", "-1", "--format=%H|%aI",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if process.returncode == 0 and stdout:
                parts = stdout.decode().strip().split("|")
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    commit_date = datetime.fromisoformat(parts[1].replace("Z", "+00:00")).replace(tzinfo=None)
                    return commit_hash, commit_date

        except Exception:
            pass

        return None, None

    async def update(
        self,
        repo_url: str,
    ) -> CloneResult:
        """Update an existing clone with git fetch/pull.

        Args:
            repo_url: Repository URL to update

        Returns:
            CloneResult with update details
        """
        local_path = self.cache.get_repo_path(repo_url)

        if not self.cache.is_repo_cloned(repo_url):
            raise GitCloneError(f"Repository not cloned: {repo_url}")

        try:
            # Fetch and reset to origin
            process = await asyncio.create_subprocess_exec(
                "git", "fetch", "--depth", str(self.config.git.clone_depth), "origin",
                cwd=local_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            # Get default branch
            process = await asyncio.create_subprocess_exec(
                "git", "symbolic-ref", "refs/remotes/origin/HEAD",
                cwd=local_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if stdout:
                default_branch = stdout.decode().strip().split("/")[-1]
            else:
                default_branch = "main"

            # Reset to origin
            process = await asyncio.create_subprocess_exec(
                "git", "reset", "--hard", f"origin/{default_branch}",
                cwd=local_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            commit_hash, commit_date = await self._get_last_commit(local_path)

            result = CloneResult(
                repo_url=repo_url,
                local_path=local_path,
                success=True,
                cloned_at=datetime.now(),
                clone_depth=self.config.git.clone_depth,
                last_commit_hash=commit_hash,
                last_commit_date=commit_date,
            )

            # Update metadata
            self.cache.save_repo_metadata(repo_url, {
                **result.to_dict(),
                "last_updated": datetime.now().isoformat(),
            })

            return result

        except Exception as e:
            return CloneResult(
                repo_url=repo_url,
                local_path=local_path,
                success=False,
                cloned_at=datetime.now(),
                clone_depth=self.config.git.clone_depth,
                error=str(e),
            )

    async def clone_batch(
        self,
        repo_urls: list[str],
        depth: int | None = None,
        concurrency: int | None = None,
    ) -> list[CloneResult]:
        """Clone multiple repositories concurrently.

        Args:
            repo_urls: List of repository URLs
            depth: Clone depth
            concurrency: Max concurrent clones

        Returns:
            List of CloneResults
        """
        concurrency = concurrency or self.config.git.max_concurrent_clones
        semaphore = asyncio.Semaphore(concurrency)

        async def clone_with_semaphore(url: str) -> CloneResult:
            async with semaphore:
                return await self.clone(url, depth=depth)

        tasks = [clone_with_semaphore(url) for url in repo_urls]
        return await asyncio.gather(*tasks)

    def list_clones(self) -> list[dict[str, Any]]:
        """List all cloned repositories."""
        return self.cache.list_repos()

    def get_stale_clones(self, max_age_hours: int = 24) -> list[dict[str, Any]]:
        """Get list of clones older than max_age_hours."""
        from datetime import timedelta

        now = datetime.now()
        stale = []

        for repo in self.cache.list_repos():
            last_updated = repo.get("last_updated") or repo.get("cloned_at")
            if last_updated:
                try:
                    updated_at = datetime.fromisoformat(last_updated)
                    age = now - updated_at
                    if age > timedelta(hours=max_age_hours):
                        repo["age_hours"] = age.total_seconds() / 3600
                        stale.append(repo)
                except (ValueError, TypeError):
                    pass

        return stale

    def delete_clone(self, repo_url: str) -> bool:
        """Delete a cloned repository."""
        return self.cache.clear_repo(repo_url)

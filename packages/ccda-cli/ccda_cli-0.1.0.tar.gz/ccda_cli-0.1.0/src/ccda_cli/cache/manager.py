"""Cache manager for analysis data and user profiles.

Handles TTL-based caching with the following structure:
~/.ccda/
  ├── repos/                    # Cloned repositories
  ├── users/                    # GitHub user profile cache
  └── data/                     # Analysis results per package
      └── pkg--npm/
          └── express/
              └── 4.18.2/
                  ├── discovery.json
                  ├── git-metrics.json
                  └── ...
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from ccda_cli.config import get_config

T = TypeVar("T", bound=BaseModel)


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""

    path: Path
    data: Any
    created_at: datetime
    ttl_hours: int | None
    exists: bool = True

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl_hours is None:
            return False
        expiry = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry

    @property
    def age_hours(self) -> float:
        """Get age in hours."""
        delta = datetime.now() - self.created_at
        return delta.total_seconds() / 3600


@dataclass
class CacheManager:
    """Manages cached data for ccda-cli."""

    base_dir: Path | None = None
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize cache directories."""
        if self.base_dir is None:
            config = get_config()
            self.base_dir = config.cache.directory

        self.base_dir = Path(self.base_dir).expanduser()
        self._ensure_dirs()
        self._initialized = True

    def _ensure_dirs(self) -> None:
        """Create cache directories if they don't exist."""
        config = get_config()
        dirs = [
            self.base_dir,
            config.cache.repos_dir,
            config.cache.data_dir,
            config.cache.users_dir,
        ]
        for d in dirs:
            if d:
                Path(d).expanduser().mkdir(parents=True, exist_ok=True)

    @property
    def repos_dir(self) -> Path:
        """Get the repositories cache directory."""
        config = get_config()
        return Path(config.cache.repos_dir).expanduser() if config.cache.repos_dir else self.base_dir / "repos"

    @property
    def data_dir(self) -> Path:
        """Get the data cache directory."""
        config = get_config()
        return Path(config.cache.data_dir).expanduser() if config.cache.data_dir else self.base_dir / "data"

    @property
    def users_dir(self) -> Path:
        """Get the users cache directory."""
        config = get_config()
        return Path(config.cache.users_dir).expanduser() if config.cache.users_dir else self.base_dir / "users"

    # =========================================================================
    # Package Data Cache
    # =========================================================================

    def get_package_dir(self, purl: str) -> Path:
        """Get the cache directory for a package.

        Converts PURL to path: pkg:npm/express@4.18.2 -> pkg--npm/express/4.18.2
        """
        from packageurl import PackageURL

        parsed = PackageURL.from_string(purl)
        ecosystem = f"pkg--{parsed.type}"

        # Handle namespaced packages (e.g., @babel/core)
        if parsed.namespace:
            name = f"{parsed.namespace}--{parsed.name}"
        else:
            name = parsed.name

        version = parsed.version or "latest"

        return self.data_dir / ecosystem / name / version

    def get_package_data(
        self,
        purl: str,
        filename: str,
        ttl_hours: int | None = None,
    ) -> CacheEntry | None:
        """Get cached data for a package.

        Args:
            purl: Package URL
            filename: Cache file name (e.g., 'discovery.json')
            ttl_hours: Override TTL (None uses config defaults)

        Returns:
            CacheEntry if exists and not expired, None otherwise
        """
        pkg_dir = self.get_package_dir(purl)
        file_path = pkg_dir / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        # Get created_at from file or data
        if "cached_at" in data:
            created_at = datetime.fromisoformat(data["cached_at"])
        else:
            stat = file_path.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime)

        # Determine TTL
        if ttl_hours is None:
            ttl_hours = self._get_ttl_for_file(filename)

        entry = CacheEntry(
            path=file_path,
            data=data,
            created_at=created_at,
            ttl_hours=ttl_hours,
        )

        if entry.is_expired:
            return None

        return entry

    def save_package_data(
        self,
        purl: str,
        filename: str,
        data: dict[str, Any],
    ) -> Path:
        """Save data to package cache.

        Automatically adds cached_at timestamp.
        """
        pkg_dir = self.get_package_dir(purl)
        pkg_dir.mkdir(parents=True, exist_ok=True)

        file_path = pkg_dir / filename

        # Add cache metadata
        data_with_meta = {
            **data,
            "cached_at": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(data_with_meta, f, indent=2, default=str)

        return file_path

    # =========================================================================
    # User Profile Cache
    # =========================================================================

    def get_user_profile(self, username: str) -> CacheEntry | None:
        """Get cached GitHub user profile."""
        file_path = self.users_dir / f"{username}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        created_at = datetime.fromisoformat(data.get("cached_at", datetime.now().isoformat()))
        config = get_config()

        entry = CacheEntry(
            path=file_path,
            data=data,
            created_at=created_at,
            ttl_hours=config.ttl.user_profiles,
        )

        if entry.is_expired:
            return None

        return entry

    def save_user_profile(self, username: str, data: dict[str, Any]) -> Path:
        """Save user profile to cache."""
        file_path = self.users_dir / f"{username}.json"

        data_with_meta = {
            **data,
            "cached_at": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(data_with_meta, f, indent=2, default=str)

        return file_path

    # =========================================================================
    # Repository Cache
    # =========================================================================

    def get_repo_path(self, repo_url: str) -> Path:
        """Get the local path for a cloned repository.

        Converts URL to path: github.com/expressjs/express -> github.com/expressjs/express
        """
        # Parse the URL to get owner/repo
        if repo_url.startswith("https://"):
            repo_url = repo_url[8:]
        elif repo_url.startswith("http://"):
            repo_url = repo_url[7:]

        # Remove trailing .git
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        return self.repos_dir / repo_url

    def get_repo_metadata(self, repo_url: str) -> CacheEntry | None:
        """Get metadata for a cloned repository."""
        repo_path = self.get_repo_path(repo_url)
        meta_path = repo_path / ".ccda-metadata.json"

        if not meta_path.exists():
            return None

        try:
            with open(meta_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        created_at = datetime.fromisoformat(data.get("cloned_at", datetime.now().isoformat()))

        return CacheEntry(
            path=meta_path,
            data=data,
            created_at=created_at,
            ttl_hours=None,  # Repos don't expire automatically
        )

    def save_repo_metadata(self, repo_url: str, data: dict[str, Any]) -> Path:
        """Save repository clone metadata."""
        repo_path = self.get_repo_path(repo_url)
        meta_path = repo_path / ".ccda-metadata.json"

        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return meta_path

    def is_repo_cloned(self, repo_url: str) -> bool:
        """Check if a repository is already cloned."""
        repo_path = self.get_repo_path(repo_url)
        git_dir = repo_path / ".git"
        return git_dir.exists()

    # =========================================================================
    # Cache Management
    # =========================================================================

    def list_packages(self) -> list[dict[str, Any]]:
        """List all cached packages."""
        packages = []

        if not self.data_dir.exists():
            return packages

        for ecosystem_dir in self.data_dir.iterdir():
            if not ecosystem_dir.is_dir():
                continue

            ecosystem = ecosystem_dir.name.replace("pkg--", "pkg:")

            for pkg_dir in ecosystem_dir.iterdir():
                if not pkg_dir.is_dir():
                    continue

                for version_dir in pkg_dir.iterdir():
                    if not version_dir.is_dir():
                        continue

                    # Count cached files
                    files = list(version_dir.glob("*.json"))

                    packages.append({
                        "ecosystem": ecosystem,
                        "name": pkg_dir.name.replace("--", "/"),
                        "version": version_dir.name,
                        "path": str(version_dir),
                        "files": [f.name for f in files],
                        "file_count": len(files),
                    })

        return packages

    def list_repos(self) -> list[dict[str, Any]]:
        """List all cloned repositories."""
        repos = []

        if not self.repos_dir.exists():
            return repos

        for host_dir in self.repos_dir.iterdir():
            if not host_dir.is_dir():
                continue

            for owner_dir in host_dir.iterdir():
                if not owner_dir.is_dir():
                    continue

                for repo_dir in owner_dir.iterdir():
                    if not repo_dir.is_dir():
                        continue

                    git_dir = repo_dir / ".git"
                    if not git_dir.exists():
                        continue

                    # Try to read metadata
                    meta_path = repo_dir / ".ccda-metadata.json"
                    metadata = {}
                    if meta_path.exists():
                        try:
                            with open(meta_path) as f:
                                metadata = json.load(f)
                        except (json.JSONDecodeError, OSError):
                            pass

                    repos.append({
                        "host": host_dir.name,
                        "owner": owner_dir.name,
                        "repo": repo_dir.name,
                        "path": str(repo_dir),
                        "url": f"https://{host_dir.name}/{owner_dir.name}/{repo_dir.name}",
                        **metadata,
                    })

        return repos

    def list_users(self) -> list[dict[str, Any]]:
        """List all cached user profiles."""
        users = []

        if not self.users_dir.exists():
            return users

        for user_file in self.users_dir.glob("*.json"):
            try:
                with open(user_file) as f:
                    data = json.load(f)
                    users.append({
                        "username": user_file.stem,
                        "name": data.get("name"),
                        "company": data.get("company"),
                        "cached_at": data.get("cached_at"),
                    })
            except (json.JSONDecodeError, OSError):
                continue

        return users

    def clear_package(self, purl: str) -> bool:
        """Clear cached data for a specific package."""
        pkg_dir = self.get_package_dir(purl)
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
            return True
        return False

    def clear_repo(self, repo_url: str) -> bool:
        """Clear a cloned repository."""
        repo_path = self.get_repo_path(repo_url)
        if repo_path.exists():
            shutil.rmtree(repo_path)
            return True
        return False

    def clear_user(self, username: str) -> bool:
        """Clear a cached user profile."""
        file_path = self.users_dir / f"{username}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def clear_all(self, repos: bool = False, data: bool = False, users: bool = False) -> dict[str, int]:
        """Clear cache directories.

        Returns count of items removed.
        """
        counts = {"repos": 0, "data": 0, "users": 0}

        if repos and self.repos_dir.exists():
            for item in self.repos_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    counts["repos"] += 1

        if data and self.data_dir.exists():
            for item in self.data_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    counts["data"] += 1

        if users and self.users_dir.exists():
            for item in self.users_dir.glob("*.json"):
                item.unlink()
                counts["users"] += 1

        return counts

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        packages = self.list_packages()
        repos = self.list_repos()
        users = self.list_users()

        # Calculate sizes
        def get_dir_size(path: Path) -> int:
            if not path.exists():
                return 0
            total = 0
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
            return total

        return {
            "packages": {
                "count": len(packages),
                "size_bytes": get_dir_size(self.data_dir),
            },
            "repos": {
                "count": len(repos),
                "size_bytes": get_dir_size(self.repos_dir),
            },
            "users": {
                "count": len(users),
                "size_bytes": get_dir_size(self.users_dir),
            },
            "total_size_bytes": (
                get_dir_size(self.data_dir) +
                get_dir_size(self.repos_dir) +
                get_dir_size(self.users_dir)
            ),
        }

    def _get_ttl_for_file(self, filename: str) -> int | None:
        """Get default TTL for a cache file type."""
        config = get_config()
        ttl_map = {
            "discovery.json": config.ttl.discovery,
            "tarball-scan.json": config.ttl.tarball_scan,
            "git-metrics.json": config.ttl.git_metrics,
            "github-api.json": config.ttl.github_api,
            "health-score.json": config.ttl.health_score,
            "burnout-score.json": config.ttl.burnout_score,
            "unified.json": config.ttl.unified,
        }
        return ttl_map.get(filename)

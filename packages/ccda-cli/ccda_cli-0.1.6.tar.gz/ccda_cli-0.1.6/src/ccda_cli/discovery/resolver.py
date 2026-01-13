"""Package discovery and resolution.

Resolves package metadata from:
- deps.dev API
- ClearlyDefined API
- ecosyste.ms API
- Package registries (npm, PyPI, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ccda_cli.config import get_config
from ccda_cli.core.http import (
    DepsDevClient,
    ClearlyDefinedClient,
    EcosystemsClient,
    SerpAPIClient,
    AsyncHTTPClient,
)
from ccda_cli.discovery.purl import ParsedPURL, PURLParser


@dataclass
class DiscoveryResult:
    """Result of package discovery."""

    purl: str
    name: str
    version: str | None
    latest_version: str | None = None
    description: str | None = None
    license: str | None = None
    repository_url: str | None = None
    tarball_url: str | None = None
    homepage: str | None = None

    # Package registry metadata
    registry_data: dict[str, Any] = field(default_factory=dict)

    # Discovery metadata
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sources: list[str] = field(default_factory=list)

    @property
    def github_url(self) -> str | None:
        """Alias for repository_url for convenience."""
        return self.repository_url

    @property
    def metadata(self) -> dict[str, Any]:
        """Get combined metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "license": self.license,
            "homepage": self.homepage,
            **self.registry_data,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "purl": self.purl,
            "name": self.name,
            "version": self.version,
            "latest_version": self.latest_version,
            "description": self.description,
            "license": self.license,
            "repository_url": self.repository_url,
            "tarball_url": self.tarball_url,
            "homepage": self.homepage,
            "registry_data": self.registry_data,
            "discovered_at": self.discovered_at,
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiscoveryResult":
        """Create from dictionary."""
        return cls(
            purl=data["purl"],
            name=data["name"],
            version=data.get("version"),
            latest_version=data.get("latest_version"),
            description=data.get("description"),
            license=data.get("license"),
            repository_url=data.get("repository_url"),
            tarball_url=data.get("tarball_url"),
            homepage=data.get("homepage"),
            registry_data=data.get("registry_data", {}),
            discovered_at=data.get("discovered_at", datetime.now().isoformat()),
            sources=data.get("sources", []),
        )


class PackageResolver:
    """Resolves package metadata from various sources."""

    def __init__(self):
        self.depsdev = DepsDevClient()
        self.clearlydefined = ClearlyDefinedClient()
        self.ecosystems = EcosystemsClient()

        # Initialize SerpAPI client if API key is available
        config = get_config()
        self.serpapi = SerpAPIClient(config.serpapi_key) if config.serpapi_key else None

    async def discover(self, purl_string: str) -> DiscoveryResult:
        """Discover package metadata from a PURL.

        Args:
            purl_string: Package URL string

        Returns:
            DiscoveryResult with package metadata
        """
        parsed = PURLParser.parse(purl_string)

        # Start with basic info from PURL
        result = DiscoveryResult(
            purl=purl_string,
            name=parsed.full_name,
            version=parsed.version,
        )

        # If it's a GitHub PURL, discover associated packages
        if parsed.is_github:
            await self._discover_from_github(parsed, result)
        else:
            # Try deps.dev first
            await self._discover_from_depsdev(parsed, result)

            # Enrich with ecosyste.ms
            await self._discover_from_ecosystems(parsed, result)

            # Enrich with ClearlyDefined if needed
            if not result.license or not result.repository_url:
                await self._discover_from_clearlydefined(parsed, result)

            # Try package registry as fallback
            if not result.tarball_url:
                await self._discover_from_registry(parsed, result)

            # Last resort: Use SerpAPI to search for repository on GitHub
            if not result.repository_url and self.serpapi:
                await self._discover_from_serpapi(parsed, result)

        return result

    async def _discover_from_depsdev(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover package info from deps.dev."""
        ecosystem = parsed.depsdev_ecosystem
        if not ecosystem:
            return

        # For Go packages with github.com in namespace, infer GitHub URL directly
        if parsed.type == "go" and parsed.namespace:
            if parsed.namespace.startswith("github.com/"):
                # Extract owner from namespace: github.com/hashicorp -> hashicorp
                owner = parsed.namespace.replace("github.com/", "")
                result.repository_url = f"https://github.com/{owner}/{parsed.name}"
                result.sources.append("purl_inference")

        try:
            async with self.depsdev.session():
                # Get package info (use correct name format for each ecosystem)
                pkg_response = await self.depsdev.get_package(ecosystem, parsed.depsdev_package_name)

                if pkg_response.status_code == 200:
                    data = pkg_response.data
                    result.sources.append("deps.dev")

                    # Extract versions
                    versions = data.get("versions", [])
                    if versions:
                        # Get latest version
                        latest = versions[-1] if versions else None
                        if latest:
                            result.latest_version = latest.get("versionKey", {}).get(
                                "version"
                            )

                    # Get version-specific info (use provided version or latest)
                    version_to_fetch = parsed.version or result.latest_version
                    if version_to_fetch:
                        version_response = await self.depsdev.get_version(
                            ecosystem, parsed.depsdev_package_name, version_to_fetch
                        )
                        if version_response.status_code == 200:
                            version_data = version_response.data

                            # Extract links
                            links = version_data.get("links", [])
                            for link in links:
                                label = link.get("label", "").lower()
                                url = link.get("url", "")
                                if "repo" in label or "source" in label:
                                    # Clean up .git suffix
                                    if url.endswith(".git"):
                                        url = url[:-4]
                                    result.repository_url = url
                                elif "home" in label:
                                    result.homepage = url

                            # Extract license
                            licenses = version_data.get("licenses", [])
                            if licenses:
                                result.license = licenses[0]

        except Exception:
            pass  # Continue with other sources

    async def _discover_from_ecosystems(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover package info from ecosyste.ms.

        ecosyste.ms provides comprehensive package metadata including:
        - Repository URLs and metadata
        - License information
        - GitHub stars, forks, issues
        - Package registry metadata
        """
        # Use the appropriate package name format
        package_name = parsed.depsdev_package_name

        try:
            async with self.ecosystems.session():
                response = await self.ecosystems.get_package(
                    parsed.type, package_name
                )

                if response and response.status_code == 200 and response.data:
                    data = response.data
                    result.sources.append("ecosyste.ms")

                    # Extract repository URL (primary value from ecosyste.ms)
                    if not result.repository_url:
                        repo_url = data.get("repository_url")
                        if repo_url:
                            # Clean up .git suffix
                            if repo_url.endswith(".git"):
                                repo_url = repo_url[:-4]
                            result.repository_url = repo_url

                    # Extract license information
                    if not result.license:
                        # ecosyste.ms provides normalized_licenses array
                        normalized_licenses = data.get("normalized_licenses", [])
                        if normalized_licenses:
                            result.license = normalized_licenses[0]
                        elif data.get("licenses"):
                            result.license = data.get("licenses")

                    # Extract description
                    if not result.description:
                        result.description = data.get("description")

                    # Extract homepage
                    if not result.homepage:
                        result.homepage = data.get("homepage")

                    # Extract latest version if not already set
                    if not result.latest_version:
                        result.latest_version = data.get("latest_release_number")

                    # Store rich metadata from ecosyste.ms
                    repo_metadata = data.get("repo_metadata", {})
                    if repo_metadata:
                        result.registry_data["ecosystems_repo"] = {
                            "stars": repo_metadata.get("stargazers_count"),
                            "forks": repo_metadata.get("forks_count"),
                            "open_issues": repo_metadata.get("open_issues_count"),
                            "watchers": repo_metadata.get("subscribers_count"),
                        }

                    # Store package metadata
                    metadata = data.get("metadata", {})
                    if metadata:
                        result.registry_data["ecosystems_metadata"] = metadata

        except Exception:
            pass  # Continue with other sources

    async def _discover_from_clearlydefined(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover package info from ClearlyDefined."""
        # Map PURL type to ClearlyDefined type/provider
        type_mapping = {
            "npm": ("npm", "npmjs"),
            "pypi": ("pypi", "pypi"),
            "maven": ("maven", "mavencentral"),
            "nuget": ("nuget", "nuget"),
            "gem": ("gem", "rubygems"),
        }

        if parsed.type not in type_mapping:
            return

        cd_type, provider = type_mapping[parsed.type]
        namespace = parsed.namespace or "-"
        version = parsed.version or "-"

        try:
            async with self.clearlydefined.session():
                response = await self.clearlydefined.get_definition(
                    cd_type, provider, namespace, parsed.name, version
                )

                if response.status_code == 200:
                    data = response.data
                    result.sources.append("clearlydefined")

                    # Extract license
                    licensed = data.get("licensed", {})
                    declared = licensed.get("declared")
                    if declared and not result.license:
                        result.license = declared

                    # Extract description
                    described = data.get("described", {})
                    if not result.description:
                        result.description = described.get("projectWebsite")

                    # Extract source location
                    source_location = described.get("sourceLocation", {})
                    if source_location and not result.repository_url:
                        sl_type = source_location.get("type")
                        if sl_type == "github":
                            namespace = source_location.get("namespace")
                            name = source_location.get("name")
                            if namespace and name:
                                result.repository_url = f"https://github.com/{namespace}/{name}"

        except Exception:
            pass

    async def _discover_from_registry(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover package info from package registry."""
        if parsed.type == "npm":
            await self._discover_from_npm(parsed, result)
        elif parsed.type == "pypi":
            await self._discover_from_pypi(parsed, result)
        elif parsed.type == "cargo":
            await self._discover_from_crates(parsed, result)

    async def _discover_from_npm(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover from npm registry."""
        client = AsyncHTTPClient(
            base_url="https://registry.npmjs.org",
            headers={"Accept": "application/json"},
        )

        try:
            async with client.session():
                # URL encode the package name for scoped packages
                package_name = parsed.full_name.replace("/", "%2F")
                response = await client.get(f"/{package_name}")

                if response.status_code == 200:
                    data = response.data
                    result.sources.append("npm")

                    # Get latest version
                    dist_tags = data.get("dist-tags", {})
                    result.latest_version = dist_tags.get("latest")

                    # Get description
                    if not result.description:
                        result.description = data.get("description")

                    # Get license
                    if not result.license:
                        result.license = data.get("license")

                    # Get repository
                    if not result.repository_url:
                        repo = data.get("repository", {})
                        if isinstance(repo, dict):
                            url = repo.get("url", "")
                            # Clean up git URL
                            url = re.sub(r"^git\+", "", url)
                            url = re.sub(r"\.git$", "", url)
                            url = re.sub(r"^git://", "https://", url)
                            if url:
                                result.repository_url = url

                    # Get tarball URL for specific version
                    version = parsed.version or result.latest_version
                    if version:
                        versions = data.get("versions", {})
                        version_data = versions.get(version, {})
                        dist = version_data.get("dist", {})
                        result.tarball_url = dist.get("tarball")

                    result.registry_data = {
                        "maintainers": data.get("maintainers", []),
                        "keywords": data.get("keywords", []),
                        "time": data.get("time", {}),
                    }

        except Exception:
            pass

    async def _discover_from_pypi(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover from PyPI registry."""
        client = AsyncHTTPClient(
            base_url="https://pypi.org",
            headers={"Accept": "application/json"},
        )

        try:
            async with client.session():
                url = f"/pypi/{parsed.name}/json"
                if parsed.version:
                    url = f"/pypi/{parsed.name}/{parsed.version}/json"

                response = await client.get(url)

                if response.status_code == 200:
                    data = response.data
                    result.sources.append("pypi")

                    info = data.get("info", {})

                    # Get latest version
                    result.latest_version = info.get("version")

                    # Get description
                    if not result.description:
                        result.description = info.get("summary")

                    # Get license
                    if not result.license:
                        result.license = info.get("license")

                    # Get repository/homepage
                    if not result.repository_url:
                        project_urls = info.get("project_urls", {}) or {}
                        for key, url in project_urls.items():
                            if "source" in key.lower() or "repository" in key.lower():
                                result.repository_url = url
                                break
                            elif "github" in url.lower() and not result.repository_url:
                                result.repository_url = url

                    if not result.homepage:
                        result.homepage = info.get("home_page") or info.get(
                            "project_url"
                        )

                    # Get tarball URL
                    urls = data.get("urls", [])
                    for url_info in urls:
                        if url_info.get("packagetype") == "sdist":
                            result.tarball_url = url_info.get("url")
                            break

                    result.registry_data = {
                        "author": info.get("author"),
                        "author_email": info.get("author_email"),
                        "classifiers": info.get("classifiers", []),
                        "requires_python": info.get("requires_python"),
                    }

        except Exception:
            pass

    async def _discover_from_crates(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover package metadata from crates.io."""
        client = AsyncHTTPClient(
            base_url="https://crates.io/api/v1",
            headers={
                "Accept": "application/json",
                "User-Agent": "ccda-cli/1.0",
            },
        )

        crate_name = parsed.name or parsed.full_name

        try:
            async with client.session():
                response = await client.get(f"/crates/{crate_name}")

                if response.status_code == 200 and response.data:
                    data = response.data or {}
                    crate_data = data.get("crate", {})
                    result.sources.append("crates.io")

                    if crate_data:
                        # Latest version information
                        if not result.latest_version:
                            result.latest_version = (
                                crate_data.get("newest_version")
                                or crate_data.get("max_version")
                            )

                        # Core metadata
                        if not result.description:
                            result.description = crate_data.get("description")

                        if not result.license:
                            result.license = crate_data.get("license")

                        if not result.homepage:
                            result.homepage = (
                                crate_data.get("homepage")
                                or crate_data.get("documentation")
                            )

                        if not result.repository_url:
                            repo_url = crate_data.get("repository")
                            if repo_url and repo_url.endswith(".git"):
                                repo_url = repo_url[:-4]
                            result.repository_url = repo_url

                        # Registry metadata snapshot
                        registry_snapshot = {
                            "downloads": crate_data.get("downloads"),
                            "recent_downloads": crate_data.get("recent_downloads"),
                            "documentation": crate_data.get("documentation"),
                            "homepage": crate_data.get("homepage"),
                            "repository": crate_data.get("repository"),
                            "created_at": crate_data.get("created_at"),
                            "updated_at": crate_data.get("updated_at"),
                            "keywords": [
                                kw.get("id")
                                for kw in data.get("keywords", [])
                                if kw.get("id")
                            ],
                            "categories": [
                                cat.get("slug")
                                for cat in data.get("categories", [])
                                if cat.get("slug")
                            ],
                        }

                        result.registry_data.setdefault("crates_io", {})
                        result.registry_data["crates_io"].update(
                            {k: v for k, v in registry_snapshot.items() if v is not None}
                        )

                    # Determine version for tarball URL
                    version = parsed.version or result.latest_version
                    if not version:
                        for version_info in data.get("versions", []):
                            num = version_info.get("num")
                            if num:
                                version = num
                                break

                    if version:
                        result.tarball_url = (
                            f"https://crates.io/api/v1/crates/{crate_name}/{version}/download"
                        )

        except Exception:
            pass

    async def _discover_from_serpapi(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Search for GitHub repository using SerpAPI as last resort fallback.

        This method is only called when:
        - No repository URL was found from other sources
        - SerpAPI key is configured

        Uses Google Search with site:github.com to find the most relevant
        repository for the package.
        """
        if not self.serpapi:
            return

        try:
            async with self.serpapi.session():
                # Search for repository
                response = await self.serpapi.search_github_repository(
                    parsed.name, parsed.type
                )

                if response.status_code == 200:
                    # Extract GitHub URL from search results
                    github_url = SerpAPIClient.extract_github_url(response)

                    if github_url:
                        result.repository_url = github_url
                        result.sources.append("serpapi")

        except Exception:
            # SerpAPI is optional fallback - don't fail if it errors
            pass

    async def _discover_from_github(
        self, parsed: ParsedPURL, result: DiscoveryResult
    ) -> None:
        """Discover packages from a GitHub repository.

        Scans for manifest files to find associated packages.
        """
        if not parsed.namespace:
            return

        result.repository_url = f"https://github.com/{parsed.namespace}/{parsed.name}"
        result.sources.append("github")

        # TODO: Clone repo and scan for manifest files
        # For now, just set basic info
        result.registry_data = {
            "owner": parsed.namespace,
            "repo": parsed.name,
            "manifest_files": [],  # Would be populated after scanning
        }

    async def discover_github_repo(self, purl_string: str) -> str | None:
        """Discover the GitHub repository URL for a package.

        Args:
            purl_string: Package URL string

        Returns:
            GitHub repository URL or None
        """
        result = await self.discover(purl_string)
        return result.repository_url

    async def discover_tarball_url(self, purl_string: str) -> str | None:
        """Discover the source tarball URL for a package.

        Args:
            purl_string: Package URL string

        Returns:
            Tarball URL or None
        """
        result = await self.discover(purl_string)
        return result.tarball_url

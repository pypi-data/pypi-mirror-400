"""Async HTTP client for API requests.

Provides a unified interface for making HTTP requests to:
- GitHub API
- deps.dev API
- ClearlyDefined API
- Package registries (npm, PyPI, Maven, etc.)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator

import httpx

from ccda_cli.config import get_config


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""

    limit: int = 5000
    remaining: int = 5000
    reset_at: datetime | None = None
    used: int = 0

    @classmethod
    def from_headers(cls, headers: httpx.Headers) -> RateLimitInfo:
        """Parse rate limit info from response headers."""
        limit = int(headers.get("x-ratelimit-limit", 5000))
        remaining = int(headers.get("x-ratelimit-remaining", 5000))
        reset_ts = headers.get("x-ratelimit-reset")
        reset_at = datetime.fromtimestamp(int(reset_ts)) if reset_ts else None
        used = int(headers.get("x-ratelimit-used", 0))

        return cls(limit=limit, remaining=remaining, reset_at=reset_at, used=used)


@dataclass
class APIResponse:
    """Wrapper for API responses."""

    status_code: int
    data: Any
    headers: dict[str, str]
    rate_limit: RateLimitInfo | None = None


class HTTPError(Exception):
    """HTTP request error."""

    def __init__(self, message: str, status_code: int | None = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(HTTPError):
    """GitHub API rate limit exceeded."""

    def __init__(self, reset_at: datetime | None = None):
        super().__init__("GitHub API rate limit exceeded", status_code=403)
        self.reset_at = reset_at


@dataclass
class AsyncHTTPClient:
    """Async HTTP client with rate limiting and retries."""

    base_url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0

    _client: httpx.AsyncClient | None = field(default=None, init=False, repr=False)
    _rate_limit: RateLimitInfo = field(default_factory=RateLimitInfo, init=False)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncHTTPClient]:
        """Context manager for HTTP session."""
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            self._client = client
            try:
                yield self
            finally:
                self._client = None

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make a GET request."""
        return await self._request("GET", url, params=params, headers=headers)

    async def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make a POST request."""
        return await self._request("POST", url, json=json, headers=headers)

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Make an HTTP request with retries."""
        if self._client is None:
            raise RuntimeError("HTTP client not initialized. Use 'async with client.session():'")

        merged_headers = {**self.headers, **(headers or {})}
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=merged_headers,
                )

                # Parse rate limit info if present
                rate_limit = None
                if "x-ratelimit-remaining" in response.headers:
                    rate_limit = RateLimitInfo.from_headers(response.headers)
                    self._rate_limit = rate_limit

                # Check for rate limiting
                if response.status_code == 403 and rate_limit and rate_limit.remaining == 0:
                    raise RateLimitError(reset_at=rate_limit.reset_at)

                # Check for server errors (retry)
                if response.status_code >= 500:
                    raise HTTPError(
                        f"Server error: {response.status_code}",
                        status_code=response.status_code,
                    )

                # Check for client errors (don't retry)
                if response.status_code >= 400:
                    raise HTTPError(
                        f"Client error: {response.status_code}",
                        status_code=response.status_code,
                        response=response.text,
                    )

                # Parse JSON response
                try:
                    data = response.json()
                except Exception:
                    data = response.text

                return APIResponse(
                    status_code=response.status_code,
                    data=data,
                    headers=dict(response.headers),
                    rate_limit=rate_limit,
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                continue

            except RateLimitError:
                raise

            except HTTPError as e:
                if e.status_code and e.status_code >= 500:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise

        raise HTTPError(f"Request failed after {self.max_retries} attempts: {last_error}")

    @property
    def rate_limit(self) -> RateLimitInfo:
        """Get current rate limit info."""
        return self._rate_limit


class GitHubClient(AsyncHTTPClient):
    """GitHub API client."""

    def __init__(self, token: str | None = None):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        config = get_config()
        super().__init__(
            base_url="https://api.github.com",
            headers=headers,
            max_retries=config.github.max_retries,
            retry_delay=config.github.retry_delay_seconds,
        )

    async def get_repo(self, owner: str, repo: str) -> APIResponse:
        """Get repository information."""
        return await self.get(f"/repos/{owner}/{repo}")

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        per_page: int = 100,
        page: int = 1,
    ) -> APIResponse:
        """Get repository issues."""
        return await self.get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page, "page": page},
        )

    async def get_pulls(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        per_page: int = 100,
        page: int = 1,
    ) -> APIResponse:
        """Get pull requests."""
        return await self.get(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page, "page": page},
        )

    async def get_releases(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
        page: int = 1,
    ) -> APIResponse:
        """Get releases."""
        return await self.get(
            f"/repos/{owner}/{repo}/releases",
            params={"per_page": per_page, "page": page},
        )

    async def get_user(self, username: str) -> APIResponse:
        """Get user profile."""
        return await self.get(f"/users/{username}")

    async def get_branch_protection(self, owner: str, repo: str, branch: str) -> APIResponse:
        """Get branch protection rules."""
        return await self.get(f"/repos/{owner}/{repo}/branches/{branch}/protection")

    def check_rate_limit(self) -> bool:
        """Check if we should stop making requests."""
        config = get_config()
        return self._rate_limit.remaining > config.github.rate_limit_buffer


class DepsDevClient(AsyncHTTPClient):
    """deps.dev API client."""

    def __init__(self):
        super().__init__(
            base_url="https://api.deps.dev",
            headers={"Accept": "application/json"},
        )

    async def get_package(self, ecosystem: str, name: str) -> APIResponse:
        """Get package information."""
        # deps.dev uses URL-encoded package names
        import urllib.parse

        encoded_name = urllib.parse.quote(name, safe="")
        return await self.get(f"/v3alpha/systems/{ecosystem}/packages/{encoded_name}")

    async def get_version(self, ecosystem: str, name: str, version: str) -> APIResponse:
        """Get specific version information."""
        import urllib.parse

        encoded_name = urllib.parse.quote(name, safe="")
        encoded_version = urllib.parse.quote(version, safe="")
        return await self.get(
            f"/v3alpha/systems/{ecosystem}/packages/{encoded_name}/versions/{encoded_version}"
        )


class ClearlyDefinedClient(AsyncHTTPClient):
    """ClearlyDefined API client."""

    def __init__(self):
        super().__init__(
            base_url="https://api.clearlydefined.io",
            headers={"Accept": "application/json"},
        )

    async def get_definition(
        self, type_: str, provider: str, namespace: str, name: str, revision: str
    ) -> APIResponse:
        """Get package definition.

        Example: npm/npmjs/-/lodash/4.17.21
        """
        path = f"/definitions/{type_}/{provider}/{namespace}/{name}/{revision}"
        return await self.get(path)


class EcosystemsClient(AsyncHTTPClient):
    """ecosyste.ms Packages API client.

    Provides comprehensive package metadata including repository URLs,
    licenses, GitHub metrics, and ecosystem-specific information.

    API Docs: https://packages.ecosyste.ms/api/v1/docs
    """

    # Mapping from PURL ecosystem types to ecosyste.ms registry names
    REGISTRY_MAP = {
        "npm": "npmjs.org",
        "pypi": "pypi.org",
        "cargo": "crates.io",
        "maven": "maven.org",
        "go": "proxy.golang.org",
        "nuget": "nuget.org",
        "gem": "rubygems.org",
        "composer": "packagist.org",
    }

    def __init__(self):
        super().__init__(
            base_url="https://packages.ecosyste.ms",
            headers={"Accept": "application/json"},
        )

    def get_registry_name(self, purl_type: str) -> str | None:
        """Get ecosyste.ms registry name for a PURL type.

        Args:
            purl_type: PURL type (npm, pypi, cargo, etc.)

        Returns:
            Registry name for ecosyste.ms API, or None if not supported
        """
        return self.REGISTRY_MAP.get(purl_type)

    async def get_package(self, purl_type: str, package_name: str) -> APIResponse | None:
        """Get package information from ecosyste.ms.

        Args:
            purl_type: PURL type (npm, pypi, cargo, etc.)
            package_name: Package name (for Maven, use colon format: org.group:artifact)

        Returns:
            APIResponse with package metadata, or None if unsupported package type

        Example:
            >>> client = EcosystemsClient()
            >>> response = await client.get_package("npm", "express")
        """
        registry = self.get_registry_name(purl_type)
        if not registry:
            # Return None for unsupported package types
            return None

        # URL encode package name for safety
        from urllib.parse import quote

        encoded_name = quote(package_name, safe="")
        path = f"/api/v1/registries/{registry}/packages/{encoded_name}"
        return await self.get(path)


class SerpAPIClient(AsyncHTTPClient):
    """SerpAPI client for GitHub repository search fallback.

    Uses Google Search with site:github.com to find repositories
    when other discovery methods fail to locate the source repository.

    Requires: SERPAPI_KEY or CCDA_SERPAPI_KEY environment variable
    API Docs: https://serpapi.com/
    """

    def __init__(self, api_key: str):
        """Initialize SerpAPI client.

        Args:
            api_key: SerpAPI API key
        """
        super().__init__(
            base_url="https://serpapi.com",
            headers={"Accept": "application/json"},
        )
        self.api_key = api_key

    async def search_github_repository(
        self, package_name: str, ecosystem: str | None = None
    ) -> APIResponse:
        """Search for a GitHub repository using Google Search via SerpAPI.

        Args:
            package_name: Name of the package to search for
            ecosystem: Optional ecosystem type (npm, pypi, cargo, etc.)

        Returns:
            APIResponse with search results

        Example:
            >>> client = SerpAPIClient(api_key="your_key")
            >>> async with client.session():
            ...     response = await client.search_github_repository("requests", "pypi")
            ...     # Extract first GitHub repository URL from results
        """
        # Build search query
        # Search for: site:github.com "package-name" ecosystem
        query_parts = [f"site:github.com", f'"{package_name}"']
        if ecosystem:
            query_parts.append(ecosystem)

        query = " ".join(query_parts)

        # SerpAPI parameters
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",  # Use Google Search engine
            "num": 5,  # Return top 5 results
        }

        return await self.get("/search", params=params)

    @staticmethod
    def extract_github_url(response: APIResponse) -> str | None:
        """Extract the most relevant GitHub repository URL from SerpAPI response.

        Args:
            response: APIResponse from search_github_repository

        Returns:
            GitHub repository URL (https://github.com/owner/repo) or None

        Logic:
        1. Look for organic_results in the response
        2. Filter for github.com URLs
        3. Extract owner/repo path (ignoring issues, pulls, etc.)
        4. Return the first valid repository URL
        """
        if not response.data:
            return None

        organic_results = response.data.get("organic_results", [])

        for result in organic_results:
            link = result.get("link", "")

            # Must be a github.com URL
            if "github.com" not in link:
                continue

            # Parse the URL to extract owner/repo
            # Format: https://github.com/owner/repo[/path]
            try:
                from urllib.parse import urlparse

                parsed = urlparse(link)
                if parsed.netloc != "github.com":
                    continue

                path_parts = parsed.path.strip("/").split("/")

                # Need at least owner/repo
                if len(path_parts) < 2:
                    continue

                owner, repo = path_parts[0], path_parts[1]

                # Skip non-repository paths
                if owner in ("orgs", "topics", "marketplace", "features"):
                    continue

                # Skip subpaths (issues, pulls, wiki, etc.)
                # Only accept: github.com/owner/repo or github.com/owner/repo/
                if len(path_parts) > 2 and path_parts[2] not in ("", "tree", "blob"):
                    continue

                # Construct clean repository URL
                return f"https://github.com/{owner}/{repo}"

            except Exception:
                continue

        return None

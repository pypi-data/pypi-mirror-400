"""Company affiliation enrichment using GitHub API.

This module enriches contributor data with company information from GitHub profiles.
Only activates when a GitHub token is provided to respect rate limits.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

from ccda_cli.cache.manager import CacheManager
from ccda_cli.config import get_config
from ccda_cli.core.http import GitHubClient, HTTPError, RateLimitError


@dataclass
class CompanyEnricher:
    """Enriches contributor data with GitHub company information.

    Features:
    - Extracts GitHub usernames from commit emails
    - Fetches user profiles from GitHub API
    - Caches profiles to avoid duplicate API calls
    - Normalizes company names using config mappings
    - Respects rate limits and degrades gracefully
    """

    github_token: str | None = None
    cache: CacheManager | None = None

    def __post_init__(self) -> None:
        """Initialize enricher."""
        if self.cache is None:
            self.cache = CacheManager()

        self.config = get_config()
        self._username_cache: dict[str, str] = {}  # email -> username
        self._company_cache: dict[str, str] = {}  # username -> company
        self._rate_limited = False

    def is_enabled(self) -> bool:
        """Check if enrichment is enabled.

        Returns:
            True if GitHub token is provided and enrichment is enabled in config
        """
        return (
            self.github_token is not None
            and self.config.github.enrich_company_affiliation
        )

    def get_company(self, email: str, name: str = "") -> str:
        """Get company affiliation for a contributor.

        Args:
            email: Contributor email from git commit
            name: Contributor name (optional, for logging)

        Returns:
            Company name or "Independent" if not found
        """
        if not self.is_enabled():
            return self._get_company_from_email_domain(email)

        # If rate limited, fall back to email domain
        if self._rate_limited:
            return self._get_company_from_email_domain(email)

        # Try to extract GitHub username from email
        username = self._extract_username(email)

        if not username:
            # No GitHub username, use email domain
            return self._get_company_from_email_domain(email)

        # Check cache first
        if username in self._company_cache:
            return self._company_cache[username]

        # Try to get from persistent cache
        cached_profile = self.cache.get_user_profile(username)
        if cached_profile and cached_profile.data:
            company = self._normalize_company(cached_profile.data.get("company"))
            self._company_cache[username] = company
            return company

        # Fall back to email domain (API call will be done in batch)
        return self._get_company_from_email_domain(email)

    async def enrich_contributors(
        self,
        contributors: dict[str, dict[str, Any]],
    ) -> None:
        """Enrich contributors with GitHub company data (async batch operation).

        This should be called once with all contributors to minimize API calls.
        Updates the contributors dict in-place with company information.

        Args:
            contributors: Dict of email -> contributor data
        """
        if not self.is_enabled():
            return

        if self._rate_limited:
            return

        # Extract usernames that need enrichment
        to_fetch: list[tuple[str, str]] = []  # (email, username)

        for email, data in contributors.items():
            username = self._extract_username(email)
            if not username:
                continue

            # Skip if already cached
            if username in self._company_cache:
                data["company"] = self._company_cache[username]
                continue

            # Check persistent cache
            cached = self.cache.get_user_profile(username)
            if cached and cached.data:
                company = self._normalize_company(cached.data.get("company"))
                self._company_cache[username] = company
                data["company"] = company
                continue

            # Need to fetch from API
            to_fetch.append((email, username))

        if not to_fetch:
            return

        # Batch fetch from GitHub API
        await self._batch_fetch_profiles(to_fetch, contributors)

    async def _batch_fetch_profiles(
        self,
        to_fetch: list[tuple[str, str]],
        contributors: dict[str, dict[str, Any]],
    ) -> None:
        """Fetch user profiles from GitHub API in batch.

        Args:
            to_fetch: List of (email, username) tuples to fetch
            contributors: Contributor dict to update
        """
        if not self.github_token:
            return

        client = GitHubClient(token=self.github_token)

        async with client.session():
            # Check rate limit before starting
            if not client.check_rate_limit():
                self._rate_limited = True
                return

            for email, username in to_fetch:
                try:
                    response = await client.get_user(username)

                    if response.status_code == 200:
                        profile_data = response.data

                        # Cache the profile
                        self.cache.save_user_profile(username, profile_data)

                        # Extract and normalize company
                        company = self._normalize_company(profile_data.get("company"))
                        self._company_cache[username] = company

                        # Update contributor
                        if email in contributors:
                            contributors[email]["company"] = company

                    # Check rate limit after each call
                    if not client.check_rate_limit():
                        self._rate_limited = True
                        break

                except RateLimitError:
                    self._rate_limited = True
                    break

                except HTTPError:
                    # Individual profile fetch failed, skip
                    continue

    def _extract_username(self, email: str) -> str | None:
        """Extract GitHub username from email.

        Handles patterns like:
        - username@users.noreply.github.com
        - 12345+username@users.noreply.github.com

        Args:
            email: Git commit email

        Returns:
            GitHub username or None if not a GitHub email
        """
        if email in self._username_cache:
            return self._username_cache[email]

        username = None

        # Pattern: username@users.noreply.github.com
        match = re.match(r"^([a-zA-Z0-9-]+)@users\.noreply\.github\.com$", email)
        if match:
            username = match.group(1)

        # Pattern: 12345+username@users.noreply.github.com
        if not username:
            match = re.match(r"^\d+\+([a-zA-Z0-9-]+)@users\.noreply\.github\.com$", email)
            if match:
                username = match.group(1)

        if username:
            self._username_cache[email] = username

        return username

    def _get_company_from_email_domain(self, email: str) -> str:
        """Get company from email domain mapping (fallback method).

        Args:
            email: Contributor email

        Returns:
            Company name or "Independent"
        """
        if "@" not in email:
            return "Independent"

        domain = email.split("@")[1].lower()

        # Check for common patterns first (noreply emails)
        if "noreply" in email or "users.noreply" in domain:
            return "Independent"

        # Check email domain mappings
        for pattern, company in self.config.company_mappings.email_domains.items():
            if domain.endswith(pattern):
                return company

        return "Independent"

    def _normalize_company(self, company: str | None) -> str:
        """Normalize company name using config mappings.

        Args:
            company: Raw company string from GitHub profile

        Returns:
            Normalized company name or "Independent"
        """
        if not company:
            return "Independent"

        company = company.strip()

        if not company:
            return "Independent"

        # Check github_companies mappings
        for pattern, normalized in self.config.company_mappings.github_companies.items():
            if pattern.lower() in company.lower():
                return normalized

        # Return the company as-is if no mapping found
        return company

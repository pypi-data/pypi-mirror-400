"""PURL (Package URL) parsing and validation.

Implements the PURL specification: https://github.com/package-url/purl-spec
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from packageurl import PackageURL


class PackageType(str, Enum):
    """Supported package ecosystems."""

    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    GOLANG = "go"  # PURL spec uses "go" not "golang"
    CARGO = "cargo"
    NUGET = "nuget"
    GEM = "gem"
    GITHUB = "github"
    COMPOSER = "composer"
    COCOAPODS = "cocoapods"
    SWIFT = "swift"
    PUB = "pub"
    HEX = "hex"


# Mapping of package types to their registry URLs
REGISTRY_URLS = {
    PackageType.NPM: "https://registry.npmjs.org",
    PackageType.PYPI: "https://pypi.org/pypi",
    PackageType.MAVEN: "https://repo1.maven.org/maven2",
    PackageType.CARGO: "https://crates.io/api/v1/crates",
    PackageType.NUGET: "https://api.nuget.org/v3",
    PackageType.GEM: "https://rubygems.org/api/v1/gems",
    PackageType.GOLANG: "https://proxy.golang.org",
    PackageType.COMPOSER: "https://packagist.org",
    PackageType.COCOAPODS: "https://trunk.cocoapods.org/api/v1/pods",
    PackageType.PUB: "https://pub.dev/api/packages",
    PackageType.HEX: "https://hex.pm/api/packages",
}

# deps.dev ecosystem names
DEPSDEV_ECOSYSTEMS = {
    PackageType.NPM: "npm",
    PackageType.PYPI: "pypi",
    PackageType.MAVEN: "maven",
    PackageType.GOLANG: "go",
    PackageType.CARGO: "cargo",
    PackageType.NUGET: "nuget",
}


@dataclass
class ParsedPURL:
    """Parsed and validated PURL."""

    type: str
    namespace: str | None
    name: str
    version: str | None
    qualifiers: dict[str, str] = field(default_factory=dict)
    subpath: str | None = None

    # Derived properties
    raw: str = ""

    @property
    def package_type(self) -> PackageType | None:
        """Get the PackageType enum if supported."""
        try:
            return PackageType(self.type)
        except ValueError:
            return None

    @property
    def is_github(self) -> bool:
        """Check if this is a GitHub PURL."""
        return self.type == "github"

    @property
    def full_name(self) -> str:
        """Get the full package name including namespace."""
        if self.namespace:
            if self.type == "npm":
                # Namespace already includes @ for scoped packages
                if self.namespace.startswith("@"):
                    return f"{self.namespace}/{self.name}"
                return f"@{self.namespace}/{self.name}"
            elif self.type in ("maven", "go", "composer"):
                return f"{self.namespace}/{self.name}"
            else:
                return f"{self.namespace}/{self.name}"
        return self.name

    @property
    def github_url(self) -> str | None:
        """Get GitHub URL if this is a GitHub PURL."""
        if self.is_github and self.namespace:
            return f"https://github.com/{self.namespace}/{self.name}"
        return None

    @property
    def depsdev_ecosystem(self) -> str | None:
        """Get the deps.dev ecosystem name."""
        pkg_type = self.package_type
        if pkg_type:
            return DEPSDEV_ECOSYSTEMS.get(pkg_type)
        return None

    @property
    def depsdev_package_name(self) -> str:
        """Get the package name formatted for deps.dev API.

        Maven uses colon separator (org.group:artifact).
        Other ecosystems use the full_name.
        """
        if self.type == "maven" and self.namespace:
            return f"{self.namespace}:{self.name}"
        return self.full_name

    @property
    def registry_url(self) -> str | None:
        """Get the package registry URL."""
        pkg_type = self.package_type
        if pkg_type:
            return REGISTRY_URLS.get(pkg_type)
        return None

    def to_purl_string(self) -> str:
        """Convert back to PURL string."""
        purl = PackageURL(
            type=self.type,
            namespace=self.namespace,
            name=self.name,
            version=self.version,
            qualifiers=self.qualifiers or None,
            subpath=self.subpath,
        )
        return str(purl)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "namespace": self.namespace,
            "name": self.name,
            "version": self.version,
            "qualifiers": self.qualifiers,
            "subpath": self.subpath,
            "full_name": self.full_name,
            "raw": self.raw,
        }


class PURLError(Exception):
    """PURL parsing or validation error."""

    pass


class PURLParser:
    """Parser for Package URLs."""

    # Supported package types
    SUPPORTED_TYPES = {t.value for t in PackageType}

    @classmethod
    def parse(cls, purl_string: str) -> ParsedPURL:
        """Parse a PURL string into a ParsedPURL object.

        Args:
            purl_string: A valid PURL string (e.g., "pkg:npm/express@4.18.2")

        Returns:
            ParsedPURL object

        Raises:
            PURLError: If the PURL is invalid
        """
        if not purl_string:
            raise PURLError("Empty PURL string")

        try:
            purl = PackageURL.from_string(purl_string)
        except Exception as e:
            raise PURLError(f"Invalid PURL format: {e}") from e

        return ParsedPURL(
            type=purl.type,
            namespace=purl.namespace,
            name=purl.name,
            version=purl.version,
            qualifiers=dict(purl.qualifiers) if purl.qualifiers else {},
            subpath=purl.subpath,
            raw=purl_string,
        )

    @classmethod
    def validate(cls, purl_string: str, require_version: bool = False) -> bool:
        """Validate a PURL string.

        Args:
            purl_string: PURL string to validate
            require_version: If True, require version to be present

        Returns:
            True if valid
        """
        try:
            parsed = cls.parse(purl_string)
            if require_version and not parsed.version:
                return False
            return True
        except PURLError:
            return False

    @classmethod
    def is_supported_type(cls, purl_string: str) -> bool:
        """Check if the PURL type is supported."""
        try:
            parsed = cls.parse(purl_string)
            return parsed.type in cls.SUPPORTED_TYPES
        except PURLError:
            return False

    @classmethod
    def from_github_url(cls, url: str, version: str | None = None) -> ParsedPURL:
        """Create a PURL from a GitHub URL.

        Args:
            url: GitHub repository URL
            version: Optional version/tag

        Returns:
            ParsedPURL for the GitHub repository
        """
        # Parse GitHub URL
        patterns = [
            r"github\.com/([^/]+)/([^/\.]+)",  # github.com/owner/repo
            r"github\.com/([^/]+)/([^/]+)\.git",  # github.com/owner/repo.git
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                purl_str = f"pkg:github/{owner}/{repo}"
                if version:
                    purl_str += f"@{version}"
                return cls.parse(purl_str)

        raise PURLError(f"Could not parse GitHub URL: {url}")

    @classmethod
    def normalize(cls, purl_string: str) -> str:
        """Normalize a PURL string to canonical form.

        Args:
            purl_string: PURL string to normalize

        Returns:
            Normalized PURL string
        """
        parsed = cls.parse(purl_string)
        return parsed.to_purl_string()

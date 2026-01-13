"""Unit tests for discovery module."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import pytest

from ccda_cli.discovery.purl import PURLParser, ParsedPURL, PURLError, PackageType
from ccda_cli.discovery.resolver import DiscoveryResult, PackageResolver


class TestPURLParser:
    """Test PURL parsing functionality."""

    def test_parse_simple_npm(self):
        """Parse simple npm PURL."""
        purl = "pkg:npm/express@4.18.2"
        parsed = PURLParser.parse(purl)

        assert parsed.type == "npm"
        assert parsed.name == "express"
        assert parsed.version == "4.18.2"
        assert parsed.namespace is None

    def test_parse_scoped_npm(self):
        """Parse scoped npm PURL."""
        purl = "pkg:npm/@babel/core@7.0.0"
        parsed = PURLParser.parse(purl)

        assert parsed.type == "npm"
        assert parsed.namespace == "@babel"
        assert parsed.name == "core"
        assert parsed.version == "7.0.0"
        assert parsed.full_name == "@babel/core"

    def test_parse_pypi(self):
        """Parse PyPI PURL."""
        purl = "pkg:pypi/requests@2.28.0"
        parsed = PURLParser.parse(purl)

        assert parsed.type == "pypi"
        assert parsed.name == "requests"
        assert parsed.version == "2.28.0"

    def test_parse_maven_with_namespace(self):
        """Parse Maven PURL with namespace."""
        purl = "pkg:maven/org.apache.commons/commons-lang3@3.12.0"
        parsed = PURLParser.parse(purl)

        assert parsed.type == "maven"
        assert parsed.namespace == "org.apache.commons"
        assert parsed.name == "commons-lang3"
        assert parsed.version == "3.12.0"

    def test_parse_github(self):
        """Parse GitHub PURL."""
        purl = "pkg:github/expressjs/express@4.18.2"
        parsed = PURLParser.parse(purl)

        assert parsed.type == "github"
        assert parsed.namespace == "expressjs"
        assert parsed.name == "express"
        assert parsed.is_github is True
        assert parsed.github_url == "https://github.com/expressjs/express"

    def test_parse_without_version(self):
        """Parse PURL without version."""
        purl = "pkg:npm/lodash"
        parsed = PURLParser.parse(purl)

        assert parsed.name == "lodash"
        assert parsed.version is None

    def test_parse_invalid_purl_raises(self):
        """Invalid PURL should raise PURLError."""
        with pytest.raises(PURLError):
            PURLParser.parse("not-a-purl")

    def test_parse_empty_purl_raises(self):
        """Empty PURL should raise PURLError."""
        with pytest.raises(PURLError):
            PURLParser.parse("")

    def test_validate_valid_purl(self):
        """Validate should return True for valid PURL."""
        assert PURLParser.validate("pkg:npm/express@4.18.2") is True

    def test_validate_invalid_purl(self):
        """Validate should return False for invalid PURL."""
        assert PURLParser.validate("not-a-purl") is False

    def test_validate_require_version(self):
        """Validate with require_version should check for version."""
        assert PURLParser.validate("pkg:npm/express@4.18.2", require_version=True) is True
        assert PURLParser.validate("pkg:npm/express", require_version=True) is False

    def test_is_supported_type(self):
        """Check if PURL type is supported."""
        assert PURLParser.is_supported_type("pkg:npm/express@1.0.0") is True
        assert PURLParser.is_supported_type("pkg:pypi/requests@1.0.0") is True
        assert PURLParser.is_supported_type("pkg:unknown/foo@1.0.0") is False

    def test_from_github_url(self):
        """Create PURL from GitHub URL."""
        parsed = PURLParser.from_github_url("https://github.com/expressjs/express", version="4.18.2")

        assert parsed.type == "github"
        assert parsed.namespace == "expressjs"
        assert parsed.name == "express"
        assert parsed.version == "4.18.2"

    def test_from_github_url_with_git_suffix(self):
        """Create PURL from GitHub URL with .git suffix."""
        parsed = PURLParser.from_github_url("https://github.com/owner/repo.git")

        assert parsed.namespace == "owner"
        assert parsed.name == "repo"

    def test_normalize_purl(self):
        """Normalize PURL to canonical form."""
        normalized = PURLParser.normalize("pkg:npm/express@4.18.2")
        assert "pkg:npm/express@4.18.2" in normalized


class TestParsedPURL:
    """Test ParsedPURL properties."""

    def test_package_type_enum(self):
        """Get PackageType enum from parsed PURL."""
        parsed = ParsedPURL(type="npm", namespace=None, name="express", version="1.0.0")
        assert parsed.package_type == PackageType.NPM

    def test_package_type_unknown(self):
        """Unknown type should return None."""
        parsed = ParsedPURL(type="unknown", namespace=None, name="foo", version="1.0.0")
        assert parsed.package_type is None

    def test_full_name_simple(self):
        """Full name for simple package."""
        parsed = ParsedPURL(type="npm", namespace=None, name="express", version="1.0.0")
        assert parsed.full_name == "express"

    def test_full_name_scoped_npm(self):
        """Full name for scoped npm package."""
        parsed = ParsedPURL(type="npm", namespace="@babel", name="core", version="1.0.0")
        assert parsed.full_name == "@babel/core"

    def test_full_name_maven(self):
        """Full name for Maven package."""
        parsed = ParsedPURL(type="maven", namespace="org.apache", name="commons", version="1.0.0")
        assert parsed.full_name == "org.apache/commons"

    def test_depsdev_ecosystem(self):
        """Get deps.dev ecosystem name."""
        npm = ParsedPURL(type="npm", namespace=None, name="express", version="1.0.0")
        assert npm.depsdev_ecosystem == "npm"

        pypi = ParsedPURL(type="pypi", namespace=None, name="requests", version="1.0.0")
        assert pypi.depsdev_ecosystem == "pypi"

    def test_registry_url(self):
        """Get registry URL."""
        parsed = ParsedPURL(type="npm", namespace=None, name="express", version="1.0.0")
        assert parsed.registry_url == "https://registry.npmjs.org"

    def test_to_dict(self):
        """Convert to dictionary."""
        parsed = ParsedPURL(
            type="npm",
            namespace="@babel",
            name="core",
            version="7.0.0",
            raw="pkg:npm/@babel/core@7.0.0",
        )
        d = parsed.to_dict()

        assert d["type"] == "npm"
        assert d["namespace"] == "@babel"
        assert d["name"] == "core"
        assert d["version"] == "7.0.0"
        assert d["full_name"] == "@babel/core"


def test_discover_from_crates_populates_tarball_and_metadata(monkeypatch):
    """crates.io discovery should populate metadata and tarball URL."""

    fake_payload = {
        "crate": {
            "description": "Serde description",
            "license": "MIT OR Apache-2.0",
            "repository": "https://github.com/serde-rs/serde.git",
            "homepage": "https://serde.rs",
            "documentation": "https://docs.rs/serde",
            "downloads": 123,
            "recent_downloads": 45,
            "newest_version": "1.0.99",
        },
        "versions": [{"num": "1.0.98"}],
        "keywords": [{"id": "serde"}, {"id": "serialization"}],
        "categories": [{"slug": "encoding"}],
    }

    class DummyClient:
        def __init__(self, *_, **__):  # Accept unused args from production init
            self.requested_urls: list[str] = []

        @asynccontextmanager
        async def session(self):
            yield self

        async def get(self, url: str):
            self.requested_urls.append(url)
            return type("Resp", (), {"status_code": 200, "data": fake_payload})

    monkeypatch.setattr("ccda_cli.discovery.resolver.AsyncHTTPClient", DummyClient)

    resolver = PackageResolver()
    parsed = ParsedPURL(type="cargo", namespace=None, name="serde", version=None)
    result = DiscoveryResult(purl="pkg:cargo/serde", name="serde", version=None)

    asyncio.run(resolver._discover_from_crates(parsed, result))

    assert result.tarball_url == "https://crates.io/api/v1/crates/serde/1.0.99/download"
    assert result.license == "MIT OR Apache-2.0"
    assert result.repository_url == "https://github.com/serde-rs/serde"
    assert result.description == "Serde description"
    assert result.latest_version == "1.0.99"
    assert result.sources == ["crates.io"]
    assert result.registry_data["crates_io"]["downloads"] == 123

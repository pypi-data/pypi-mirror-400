"""Tests for tarball scanning."""

import asyncio
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ccda_cli.scanner.tarball import (
    TarballScanner,
    TarballScanResult,
    LicenseFile,
    BinaryFile,
    PackageMetadata,
)


class TestLicenseFile:
    """Tests for LicenseFile dataclass."""

    def test_to_dict(self):
        """Test serialization."""
        lf = LicenseFile(
            path="LICENSE",
            spdx_id="MIT",
            confidence=95.0,
            content_hash="abc123",
        )

        data = lf.to_dict()

        assert data["path"] == "LICENSE"
        assert data["spdx_id"] == "MIT"
        assert data["confidence"] == 95.0

    def test_to_dict_unknown_license(self):
        """Test serialization with unknown license."""
        lf = LicenseFile(path="LICENSE.txt")

        data = lf.to_dict()

        assert data["path"] == "LICENSE.txt"
        assert data["spdx_id"] is None
        assert data["confidence"] == 0.0


class TestBinaryFile:
    """Tests for BinaryFile dataclass."""

    def test_to_dict(self):
        """Test serialization."""
        bf = BinaryFile(
            path="lib.so",
            file_type="ELF executable",
            size_bytes=1024,
            signature="7f454c46",
        )

        data = bf.to_dict()

        assert data["path"] == "lib.so"
        assert data["file_type"] == "ELF executable"
        assert data["size_bytes"] == 1024
        assert data["signature"] == "7f454c46"


class TestPackageMetadata:
    """Tests for PackageMetadata dataclass."""

    def test_to_dict_full(self):
        """Test serialization with all fields."""
        meta = PackageMetadata(
            name="express",
            version="4.18.2",
            description="Fast web framework",
            license="MIT",
            author="TJ Holowaychuk",
        )

        data = meta.to_dict()

        assert data["name"] == "express"
        assert data["version"] == "4.18.2"
        assert data["license"] == "MIT"

    def test_to_dict_empty(self):
        """Test serialization with no fields."""
        meta = PackageMetadata()

        data = meta.to_dict()

        assert data["name"] is None
        assert data["version"] is None


class TestTarballScanResult:
    """Tests for TarballScanResult dataclass."""

    def test_to_dict(self):
        """Test serialization."""
        from datetime import datetime

        result = TarballScanResult(
            purl="pkg:npm/express@4.18.2",
            tarball_url="https://registry.npmjs.org/express/-/express-4.18.2.tgz",
            scanned_at=datetime(2024, 1, 1, 12, 0, 0),
            license_files=[LicenseFile(path="LICENSE", spdx_id="MIT", confidence=95.0)],
            copyrights=["Copyright (c) 2024 Express Team"],
            binaries={"files": [], "signatures": []},
            file_count=100,
            total_size_bytes=50000,
            scan_method="basic",
        )

        data = result.to_dict()

        assert data["purl"] == "pkg:npm/express@4.18.2"
        assert len(data["license_files"]) == 1
        assert data["file_count"] == 100
        assert data["scan_method"] == "basic"


class TestTarballScanner:
    """Tests for TarballScanner class."""

    @pytest.fixture
    def scanner(self):
        """Create scanner instance."""
        with patch("ccda_cli.scanner.tarball.shutil.which", return_value=None):
            return TarballScanner()

    def test_check_tool_not_available(self, scanner):
        """Test tool availability check when not installed."""
        assert scanner._osslili_available is False
        assert scanner._binarysniffer_available is False

    def test_check_tool_available(self):
        """Test tool availability check when installed."""
        with patch("ccda_cli.scanner.tarball.shutil.which") as mock_which:
            mock_which.side_effect = lambda x: "/usr/bin/" + x if x == "osslili" else None
            scanner = TarballScanner()

            assert scanner._osslili_available is True
            assert scanner._binarysniffer_available is False

    def test_analyze_license_file_mit(self, scanner):
        """Test MIT license detection."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("MIT License\n\nPermission is hereby granted, free of charge...")
            f.flush()

            result = scanner._analyze_license_file(Path(f.name))

            assert result.spdx_id == "MIT"
            assert result.confidence == 95

    def test_analyze_license_file_apache(self, scanner):
        """Test Apache license detection."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Apache License\nVersion 2.0")
            f.flush()

            result = scanner._analyze_license_file(Path(f.name))

            assert result.spdx_id == "Apache-2.0"
            assert result.confidence == 95

    def test_analyze_license_file_unknown(self, scanner):
        """Test unknown license detection."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Some custom license text")
            f.flush()

            result = scanner._analyze_license_file(Path(f.name))

            assert result.spdx_id is None
            assert result.confidence == 0

    def test_check_binary_by_extension(self, scanner):
        """Test binary detection by extension."""
        with tempfile.NamedTemporaryFile(suffix=".so", delete=False) as f:
            f.write(b"not actually elf")
            f.flush()

            result = scanner._check_binary(Path(f.name))

            assert result is not None
            assert result.signature == ".so"

    def test_check_binary_by_magic_bytes(self, scanner):
        """Test binary detection by magic bytes."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            # ELF magic bytes
            f.write(b"\x7fELF" + b"\x00" * 100)
            f.flush()

            result = scanner._check_binary(Path(f.name))

            assert result is not None
            assert result.file_type == "ELF executable"

    def test_check_binary_text_file(self, scanner):
        """Test that text files are not detected as binary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a text file")
            f.flush()

            result = scanner._check_binary(Path(f.name))

            assert result is None

    def test_scan_local_directory(self, scanner):
        """Test scanning a local directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create LICENSE file
            license_file = tmpdir_path / "LICENSE"
            license_file.write_text("MIT License\n\nPermission is hereby granted, free of charge...")

            # Create package.json
            pkg_json = tmpdir_path / "package.json"
            pkg_json.write_text('{"name": "test-pkg", "version": "1.0.0", "license": "MIT"}')

            # Create source file
            src_file = tmpdir_path / "index.js"
            src_file.write_text("// Copyright 2024 Test Author\nmodule.exports = {}")

            result = scanner.scan_local("pkg:npm/test-pkg@1.0.0", tmpdir_path)

            assert result.purl == "pkg:npm/test-pkg@1.0.0"
            assert len(result.license_files) == 1
            assert result.file_count >= 3
            assert result.package_metadata.name == "test-pkg"

    def test_parse_npm_manifest(self, scanner):
        """Test npm package.json parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text('{"name": "@scope/pkg", "version": "1.2.3", "license": "Apache-2.0"}')

            result = scanner._parse_manifest(pkg_file, "npm")

            assert result.name == "@scope/pkg"
            assert result.version == "1.2.3"
            assert result.license == "Apache-2.0"

    def test_parse_pypi_manifest(self, scanner):
        """Test pyproject.toml parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            toml_file = Path(tmpdir) / "pyproject.toml"
            toml_file.write_text('name = "my-package"\nversion = "0.1.0"\ndescription = "A test package"')

            result = scanner._parse_manifest(toml_file, "pypi")

            assert result.name == "my-package"
            assert result.version == "0.1.0"

    def test_scan_purl(self, scanner):
        """Test scanning by PURL."""
        mock_discovery = MagicMock()
        mock_discovery.tarball_url = "https://example.com/pkg.tar.gz"

        with patch.object(
            scanner, "_get_download_url_via_purl2src", return_value=None
        ), patch("ccda_cli.discovery.PackageResolver") as mock_resolver:
            mock_instance = mock_resolver.return_value
            mock_instance.discover = AsyncMock(return_value=mock_discovery)

            with patch.object(scanner, "scan_url", new_callable=AsyncMock) as mock_scan:
                mock_scan.return_value = TarballScanResult(
                    purl="pkg:npm/test@1.0.0",
                    tarball_url="https://example.com/pkg.tar.gz",
                    scanned_at=MagicMock(),
                )

                result = asyncio.run(scanner.scan_purl("pkg:npm/test@1.0.0"))

                assert result.purl == "pkg:npm/test@1.0.0"
                mock_scan.assert_called_once()

    def test_scan_purl_no_tarball(self, scanner):
        """Test scanning PURL with no tarball URL."""
        mock_discovery = MagicMock()
        mock_discovery.tarball_url = None

        with patch.object(
            scanner, "_get_download_url_via_purl2src", return_value=None
        ), patch("ccda_cli.discovery.PackageResolver") as mock_resolver:
            mock_instance = mock_resolver.return_value
            mock_instance.discover = AsyncMock(return_value=mock_discovery)

            result = asyncio.run(scanner.scan_purl("pkg:npm/notfound@1.0.0"))

            assert result.tarball_url is None
            assert result.file_count == 0

    def test_scan_purl_uses_purl2src_first(self, scanner):
        """Test that scan_purl uses purl2src before PackageResolver."""
        mock_result = MagicMock()
        mock_result.download_url = "https://crates.io/api/v1/crates/serde/1.0.0/download"

        with patch.object(
            scanner, "_get_download_url_via_purl2src", return_value=mock_result.download_url
        ), patch.object(scanner, "scan_url", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = TarballScanResult(
                purl="pkg:cargo/serde@1.0.0",
                tarball_url=mock_result.download_url,
                scanned_at=MagicMock(),
            )

            result = asyncio.run(scanner.scan_purl("pkg:cargo/serde@1.0.0"))

            assert result.tarball_url == mock_result.download_url
            mock_scan.assert_called_once_with("pkg:cargo/serde@1.0.0", mock_result.download_url)

    def test_get_download_url_via_purl2src_success(self, scanner):
        """Test successful download URL retrieval via purl2src."""
        mock_result = MagicMock()
        mock_result.download_url = "https://registry.npmjs.org/express/-/express-4.17.1.tgz"

        with patch("purl2src.get_download_url", return_value=mock_result):
            url = scanner._get_download_url_via_purl2src("pkg:npm/express@4.17.1")

            assert url == "https://registry.npmjs.org/express/-/express-4.17.1.tgz"

    def test_get_download_url_via_purl2src_not_installed(self, scanner):
        """Test graceful handling when purl2src is not installed."""
        with patch("purl2src.get_download_url", side_effect=ImportError):
            url = scanner._get_download_url_via_purl2src("pkg:npm/test@1.0.0")

            assert url is None

    def test_get_download_url_via_purl2src_failure(self, scanner):
        """Test graceful handling when purl2src fails."""
        with patch("purl2src.get_download_url", side_effect=Exception("API error")):
            url = scanner._get_download_url_via_purl2src("pkg:npm/test@1.0.0")

            assert url is None

    def test_apply_osslili_results_updates_result(self, scanner):
        """osslili integration should overwrite license data when provided."""
        result = TarballScanResult(
            purl="pkg:npm/test",
            tarball_url=None,
            scanned_at=datetime.utcnow(),
        )

        payload = {
            "files": [
                {
                    "path": "LICENSE",
                    "spdx_id": "Apache-2.0",
                    "confidence": 99.1,
                    "hash": "abc",
                }
            ],
            "copyrights": ["Copyright 2024 Example"],
        }

        applied = scanner._apply_osslili_results(result, payload)

        assert applied is True
        assert result.license_files[0].spdx_id == "Apache-2.0"
        assert result.license_files[0].content_hash == "abc"
        assert result.copyrights == ["Copyright 2024 Example"]

    def test_apply_upmex_results_updates_metadata(self, scanner):
        """UpMeX integration should populate package metadata and binaries."""
        result = TarballScanResult(
            purl="pkg:npm/test",
            tarball_url=None,
            scanned_at=datetime.utcnow(),
        )

        payload = {
            "package": {
                "name": "pkg",
                "version": "1.0.0",
                "description": "desc",
                "license": "MIT",
                "author": "Dev",
                "homepage": "https://example.com",
                "repository": "example/pkg",
            },
            "binaries": [
                {
                    "path": "bin/tool",
                    "type": "ELF",
                    "size_bytes": 42,
                    "signature": "7f454c46",
                }
            ],
        }

        applied = scanner._apply_upmex_results(result, payload)

        assert applied is True
        assert result.package_metadata.name == "pkg"
        assert result.package_metadata.version == "1.0.0"
        assert result.package_metadata.repository == "example/pkg"
        assert result.binaries["files"][0].path == "bin/tool"

    def test_scan_directory_prefers_external_tools(self, scanner, tmp_path):
        """scan_method should reflect osslili usage when available."""
        (tmp_path / "LICENSE").write_text("MIT")

        scanner._osslili_available = True
        scanner._upmex_available = False

        with patch.object(scanner, "_run_osslili", return_value={"ok": True}), patch.object(
            scanner, "_apply_osslili_results", return_value=True
        ), patch.object(scanner, "_run_upmex", return_value=None):
            result = scanner._scan_directory("pkg:npm/test", None, tmp_path)

        assert result.scan_method == "osslili"

    def test_scan_directory_combines_tools(self, scanner, tmp_path):
        """scan_method should list all successful external integrations."""
        (tmp_path / "README.md").write_text("# test")

        scanner._osslili_available = True
        scanner._upmex_available = True

        with patch.object(scanner, "_run_osslili", return_value={"ok": True}), patch.object(
            scanner, "_apply_osslili_results", return_value=True
        ), patch.object(scanner, "_run_upmex", return_value={"ok": True}), patch.object(
            scanner, "_apply_upmex_results", return_value=True
        ):
            result = scanner._scan_directory("pkg:npm/test", None, tmp_path)

        assert result.scan_method == "osslili+upmex"

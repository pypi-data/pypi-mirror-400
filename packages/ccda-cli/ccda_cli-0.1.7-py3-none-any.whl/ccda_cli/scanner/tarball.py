"""Tarball scanning for licenses, copyrights, and binaries.

Uses osslili for license and copyright detection.
"""

from __future__ import annotations

import mimetypes
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from ccda_cli.discovery.purl import PURLParser


@dataclass
class LicenseFile:
    """Detected license file."""

    path: str
    spdx_id: str | None = None
    confidence: float = 0.0
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "spdx_id": self.spdx_id,
            "confidence": round(self.confidence, 1),
        }


@dataclass
class BinaryFile:
    """Detected binary file."""

    path: str
    file_type: str
    size_bytes: int
    signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "file_type": self.file_type,
            "size_bytes": self.size_bytes,
            "signature": self.signature,
        }


@dataclass
class PackageMetadata:
    """Package metadata from manifest files."""

    name: str | None = None
    version: str | None = None
    description: str | None = None
    license: str | None = None
    author: str | None = None
    homepage: str | None = None
    repository: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "license": self.license,
            "author": self.author,
            "homepage": self.homepage,
            "repository": self.repository,
        }


@dataclass
class TarballScanResult:
    """Result of tarball scan."""

    purl: str
    tarball_url: str | None
    scanned_at: datetime
    ttl_days: int = 365  # Tarball scans never expire

    license_files: list[LicenseFile] = field(default_factory=list)
    copyrights: list[str] = field(default_factory=list)
    binaries: dict[str, Any] = field(default_factory=dict)
    package_metadata: PackageMetadata = field(default_factory=PackageMetadata)

    # Scan metadata
    file_count: int = 0
    total_size_bytes: int = 0
    scan_method: str = "basic"  # basic, osslili, binarysniffer

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "purl": self.purl,
            "tarball_url": self.tarball_url,
            "scanned_at": self.scanned_at.isoformat(),
            "ttl_days": self.ttl_days,
            "license_files": [f.to_dict() for f in self.license_files],
            "copyrights": self.copyrights,
            "binaries": {
                "found": bool(self.binaries.get("files")),
                "files": [f.to_dict() for f in self.binaries.get("files", [])],
                "signatures": self.binaries.get("signatures", []),
            },
            "package_metadata": self.package_metadata.to_dict(),
            "file_count": self.file_count,
            "total_size_bytes": self.total_size_bytes,
            "scan_method": self.scan_method,
        }


class TarballScanner:
    """Scans tarballs for licenses, copyrights, and binaries."""

    # Package manifest patterns
    MANIFEST_PATTERNS = {
        "npm": ["package.json"],
        "pypi": ["setup.py", "pyproject.toml", "PKG-INFO"],
        "maven": ["pom.xml"],
        "cargo": ["Cargo.toml"],
        "gem": ["*.gemspec"],
    }

    # Binary file signatures (magic bytes)
    BINARY_SIGNATURES = {
        b"\x7fELF": "ELF executable",
        b"MZ": "Windows executable",
        b"\xca\xfe\xba\xbe": "Mach-O binary",
        b"\xcf\xfa\xed\xfe": "Mach-O 64-bit binary",
        b"PK\x03\x04": "ZIP archive",
        b"\x1f\x8b": "gzip compressed",
    }

    def __init__(self):
        """Initialize scanner with required osslili dependency."""
        try:
            from osslili.core.generator import LicenseCopyrightDetector
            self._osslili_detector = LicenseCopyrightDetector()
        except ImportError as e:
            raise RuntimeError(
                "osslili is required for tarball scanning. "
                "Install with: pip install osslili"
            ) from e

    def _get_download_url_via_purl2src(self, purl: str) -> str | None:
        """Get download URL using purl2src library.

        Args:
            purl: Package URL

        Returns:
            Download URL if successful, None otherwise
        """
        try:
            from purl2src import get_download_url

            result = get_download_url(purl, validate=False)
            if result and result.download_url:
                return result.download_url

        except (ImportError, Exception):
            # purl2src not installed or failed to get URL
            pass

        return None

    async def scan_purl(self, purl: str) -> TarballScanResult:
        """Scan a package by PURL.

        Uses purl2src to discover the download URL, with fallback to
        PackageResolver for additional metadata discovery.

        Args:
            purl: Package URL

        Returns:
            TarballScanResult
        """
        # Try purl2src first for direct download URL discovery
        tarball_url = self._get_download_url_via_purl2src(purl)

        # Fallback to PackageResolver if purl2src fails
        if not tarball_url:
            from ccda_cli.discovery import PackageResolver

            resolver = PackageResolver()
            discovery = await resolver.discover(purl)
            tarball_url = discovery.tarball_url

        if not tarball_url:
            return TarballScanResult(
                purl=purl,
                tarball_url=None,
                scanned_at=datetime.now(),
            )

        return await self.scan_url(purl, tarball_url)

    async def scan_url(self, purl: str, tarball_url: str) -> TarballScanResult:
        """Scan a tarball from URL.

        Args:
            purl: Package URL
            tarball_url: URL to the tarball

        Returns:
            TarballScanResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Download tarball
            archive_path = await self._download_tarball(tarball_url, tmpdir_path)
            if not archive_path:
                return TarballScanResult(
                    purl=purl,
                    tarball_url=tarball_url,
                    scanned_at=datetime.now(),
                )

            # Extract
            extract_dir = tmpdir_path / "extracted"
            extract_dir.mkdir()
            self._extract_archive(archive_path, extract_dir)

            # Scan
            return self._scan_directory(purl, tarball_url, extract_dir)

    def scan_local(self, purl: str, path: Path) -> TarballScanResult:
        """Scan a local tarball or directory.

        Args:
            purl: Package URL
            path: Path to tarball or directory

        Returns:
            TarballScanResult
        """
        path = Path(path)

        if path.is_dir():
            return self._scan_directory(purl, None, path)

        with tempfile.TemporaryDirectory() as tmpdir:
            extract_dir = Path(tmpdir) / "extracted"
            extract_dir.mkdir()
            self._extract_archive(path, extract_dir)
            return self._scan_directory(purl, str(path), extract_dir)

    async def _download_tarball(self, url: str, dest_dir: Path) -> Path | None:
        """Download tarball to destination directory."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Determine filename from various sources
                filename = None

                # Try Content-Disposition header first
                content_disp = response.headers.get("content-disposition", "")
                if "filename=" in content_disp:
                    # Extract filename from header
                    parts = content_disp.split("filename=")
                    if len(parts) > 1:
                        filename = parts[1].strip('"').strip("'")

                # Try final URL after redirects
                if not filename and response.url:
                    filename = Path(str(response.url).split("?")[0]).name

                # Fallback to original URL
                if not filename or filename == "download":
                    parsed = urlparse(url)
                    filename = Path(parsed.path).name

                # Ultimate fallback
                if not filename or len(filename) < 2:
                    filename = "package.tar.gz"

                dest_path = dest_dir / filename

                with open(dest_path, "wb") as f:
                    f.write(response.content)

                return dest_path

        except Exception:
            return None

    def _extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract archive to destination directory."""
        suffix = archive_path.suffix.lower()
        name = archive_path.name.lower()

        if suffix == ".zip" or name.endswith(".whl"):
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(dest_dir)
        elif suffix in (".gz", ".tgz", ".crate") or ".tar" in name:
            with tarfile.open(archive_path) as tf:
                tf.extractall(dest_dir)
        elif suffix == ".tar":
            with tarfile.open(archive_path) as tf:
                tf.extractall(dest_dir)

    def _scan_directory(
        self, purl: str, tarball_url: str | None, directory: Path
    ) -> TarballScanResult:
        """Scan extracted directory using osslili."""
        result = TarballScanResult(
            purl=purl,
            tarball_url=tarball_url,
            scanned_at=datetime.now(),
        )

        # Count files and total size
        all_files = list(directory.rglob("*"))
        for f in all_files:
            if f.is_file():
                result.file_count += 1
                result.total_size_bytes += f.stat().st_size

        # Scan for binaries
        binary_files = []
        for f in all_files:
            if f.is_file():
                binary_info = self._check_binary(f)
                if binary_info:
                    binary_files.append(binary_info)

        result.binaries = {
            "files": binary_files[:50],  # Limit
            "signatures": list(set(b.signature for b in binary_files if b.signature)),
        }

        # Use osslili to scan for licenses and copyrights
        osslili_result = self._osslili_detector.process_local_path(str(directory))

        # Convert osslili licenses to our format
        for lic in osslili_result.licenses:
            # Get relative path for cleaner display
            source_path = Path(lic.source_file).resolve()
            directory_resolved = directory.resolve()

            try:
                rel_path = source_path.relative_to(directory_resolved)
            except ValueError:
                # If we can't get relative path, just use the filename
                rel_path = Path(source_path.name)

            license_file = LicenseFile(
                path=str(rel_path),
                spdx_id=getattr(lic, 'spdx_id', None),
                confidence=getattr(lic, 'confidence', 0.0) * 100,  # Convert to percentage
            )
            result.license_files.append(license_file)

        # Convert osslili copyrights to our format
        for cr in osslili_result.copyrights:
            result.copyrights.append(getattr(cr, 'statement', str(cr)))

        result.copyrights = result.copyrights[:20]  # Limit

        # Parse package metadata
        parsed = PURLParser.parse(purl)
        pkg_type = parsed.type

        if pkg_type in self.MANIFEST_PATTERNS:
            for pattern in self.MANIFEST_PATTERNS[pkg_type]:
                for manifest in directory.rglob(pattern):
                    if manifest.is_file():
                        result.package_metadata = self._parse_manifest(manifest, pkg_type)
                        break

        result.scan_method = "osslili"

        return result

    def _check_binary(self, path: Path) -> BinaryFile | None:
        """Check if a file is a binary."""
        try:
            # Check by extension first
            suffix = path.suffix.lower()
            binary_extensions = {
                ".exe", ".dll", ".so", ".dylib", ".a", ".o",
                ".pyc", ".pyo", ".class", ".jar", ".war",
                ".wasm", ".node",
            }

            if suffix in binary_extensions:
                return BinaryFile(
                    path=str(path.name),
                    file_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                    size_bytes=path.stat().st_size,
                    signature=suffix,
                )

            # Check magic bytes
            with open(path, "rb") as f:
                header = f.read(8)

            for sig, file_type in self.BINARY_SIGNATURES.items():
                if header.startswith(sig):
                    return BinaryFile(
                        path=str(path.name),
                        file_type=file_type,
                        size_bytes=path.stat().st_size,
                        signature=sig.hex(),
                    )

        except Exception:
            pass

        return None

    def _parse_manifest(self, path: Path, pkg_type: str) -> PackageMetadata:
        """Parse package manifest file."""
        metadata = PackageMetadata()

        try:
            content = path.read_text(errors="ignore")

            if pkg_type == "npm" and path.name == "package.json":
                import json
                data = json.loads(content)
                metadata.name = data.get("name")
                metadata.version = data.get("version")
                metadata.description = data.get("description")
                metadata.license = data.get("license")
                metadata.author = data.get("author") if isinstance(data.get("author"), str) else None
                metadata.homepage = data.get("homepage")
                repo = data.get("repository")
                if isinstance(repo, dict):
                    metadata.repository = repo.get("url")
                elif isinstance(repo, str):
                    metadata.repository = repo

            elif pkg_type == "pypi" and path.name == "pyproject.toml":
                # Basic TOML parsing
                for line in content.split("\n"):
                    if line.startswith("name"):
                        metadata.name = line.split("=")[1].strip().strip('"\'')
                    elif line.startswith("version"):
                        metadata.version = line.split("=")[1].strip().strip('"\'')
                    elif line.startswith("description"):
                        metadata.description = line.split("=")[1].strip().strip('"\'')

            elif pkg_type == "cargo" and path.name == "Cargo.toml":
                for line in content.split("\n"):
                    if line.startswith("name"):
                        metadata.name = line.split("=")[1].strip().strip('"\'')
                    elif line.startswith("version"):
                        metadata.version = line.split("=")[1].strip().strip('"\'')
                    elif line.startswith("license"):
                        metadata.license = line.split("=")[1].strip().strip('"\'')

        except Exception:
            pass

        return metadata

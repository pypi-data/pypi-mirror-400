"""Tarball scanning for licenses, copyrights, and binaries.

Uses external tools when available:
- osslili: License validation and copyright extraction
- binarysniffer: Binary signature detection

Falls back to basic scanning when tools are not available.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import shlex
import shutil
import subprocess
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

    # License file patterns
    LICENSE_PATTERNS = [
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENSE.rst",
        "LICENCE",
        "COPYING",
        "COPYING.txt",
        "UNLICENSE",
        "MIT-LICENSE",
        "Apache-LICENSE",
    ]

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

    # Copyright patterns
    COPYRIGHT_PATTERNS = [
        r"Copyright\s*(?:\(c\)|©)?\s*\d{4}(?:\s*[-,]\s*\d{4})?\s+[^\n]+",
        r"©\s*\d{4}\s+[^\n]+",
        r"\(c\)\s*\d{4}\s+[^\n]+",
    ]

    def __init__(self):
        """Initialize scanner."""
        self._osslili_command = self._resolve_command(
            "CCDA_OSSLILI_CMD", ["osslili", "scan", "--format", "json"]
        )
        self._upmex_command = self._resolve_command(
            "CCDA_UPMEX_CMD", ["upmex", "scan", "--format", "json"]
        )

        self._osslili_available = self._check_tool(self._osslili_command[0])
        self._upmex_available = self._check_tool(self._upmex_command[0])
        self._binarysniffer_available = self._check_tool("binarysniffer")

    def _check_tool(self, tool_name: str) -> bool:
        """Check if an external tool is available."""
        return shutil.which(tool_name) is not None

    def _resolve_command(self, env_var: str, default: list[str]) -> list[str]:
        """Resolve external tool command from environment."""
        value = os.environ.get(env_var)
        if value:
            try:
                return shlex.split(value)
            except ValueError:
                # Fallback to default if parsing fails
                return default
        return default

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

                # Determine filename
                parsed = urlparse(url)
                filename = Path(parsed.path).name or "package.tar.gz"
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
        elif suffix in (".gz", ".tgz") or ".tar" in name:
            with tarfile.open(archive_path) as tf:
                tf.extractall(dest_dir)
        elif suffix == ".tar":
            with tarfile.open(archive_path) as tf:
                tf.extractall(dest_dir)

    def _scan_directory(
        self, purl: str, tarball_url: str | None, directory: Path
    ) -> TarballScanResult:
        """Scan extracted directory."""
        result = TarballScanResult(
            purl=purl,
            tarball_url=tarball_url,
            scanned_at=datetime.now(),
        )

        all_files = list(directory.rglob("*"))
        result.file_count = len([f for f in all_files if f.is_file()])

        # Scan for licenses
        for pattern in self.LICENSE_PATTERNS:
            for license_file in directory.rglob(pattern):
                if license_file.is_file():
                    license_info = self._analyze_license_file(license_file)
                    result.license_files.append(license_info)

        # Scan for copyrights
        copyrights = set()
        for ext in [".txt", ".md", ".rst", ""]:
            for f in directory.rglob(f"*{ext}"):
                if f.is_file() and f.stat().st_size < 100000:  # Skip large files
                    try:
                        content = f.read_text(errors="ignore")
                        for pattern in self.COPYRIGHT_PATTERNS:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            copyrights.update(matches)
                    except Exception:
                        pass
        result.copyrights = list(copyrights)[:20]  # Limit

        # Scan for binaries
        binary_files = []
        for f in all_files:
            if f.is_file():
                result.total_size_bytes += f.stat().st_size
                binary_info = self._check_binary(f)
                if binary_info:
                    binary_files.append(binary_info)

        result.binaries = {
            "files": binary_files[:50],  # Limit
            "signatures": list(set(b.signature for b in binary_files if b.signature)),
        }

        # Parse package metadata
        parsed = PURLParser.parse(purl)
        pkg_type = parsed.type

        if pkg_type in self.MANIFEST_PATTERNS:
            for pattern in self.MANIFEST_PATTERNS[pkg_type]:
                for manifest in directory.rglob(pattern):
                    if manifest.is_file():
                        result.package_metadata = self._parse_manifest(manifest, pkg_type)
                        break

        used_tools: list[str] = []

        if self._osslili_available:
            osslili_data = self._run_osslili(directory)
            if osslili_data and self._apply_osslili_results(result, osslili_data):
                used_tools.append("osslili")

        if self._upmex_available:
            upmex_data = self._run_upmex(directory)
            if upmex_data and self._apply_upmex_results(result, upmex_data):
                used_tools.append("upmex")

        if not used_tools:
            if self._binarysniffer_available:
                used_tools.append("binarysniffer")
            else:
                used_tools.append("basic")

        result.scan_method = "+".join(used_tools)

        return result

    def _build_command(self, base_command: list[str], target: Path) -> list[str]:
        """Build command for external tool, supporting {path} placeholder."""
        command = list(base_command)
        if any("{path}" in part for part in command):
            return [part.replace("{path}", str(target)) for part in command]
        return command + [str(target)]

    def _run_external_tool(self, command: list[str], cwd: Path) -> dict[str, Any] | None:
        """Run external CLI tool and parse JSON output."""
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            return None

        output = completed.stdout.strip() or completed.stderr.strip()
        if not output:
            return None

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return None

    def _run_osslili(self, directory: Path) -> dict[str, Any] | None:
        """Execute osslili scanner if configured."""
        command = self._build_command(self._osslili_command, directory)
        return self._run_external_tool(command, directory)

    def _run_upmex(self, directory: Path) -> dict[str, Any] | None:
        """Execute UpMeX metadata extractor if configured."""
        command = self._build_command(self._upmex_command, directory)
        return self._run_external_tool(command, directory)

    def _apply_osslili_results(
        self, result: TarballScanResult, data: dict[str, Any]
    ) -> bool:
        """Apply license findings from osslili output."""
        files = data.get("files") or data.get("license_files") or data.get("licenses") or []
        parsed_files: list[LicenseFile] = []
        for entry in files:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path") or entry.get("file") or entry.get("name")
            if not path:
                continue
            license_file = LicenseFile(
                path=str(path),
                spdx_id=entry.get("spdx_id") or entry.get("spdx") or entry.get("license"),
                confidence=float(entry.get("confidence") or entry.get("score") or 0),
                content_hash=entry.get("hash") or entry.get("content_hash"),
            )
            parsed_files.append(license_file)

        if parsed_files:
            result.license_files = parsed_files

        copyrights = data.get("copyrights") or data.get("copyright")
        if isinstance(copyrights, list) and copyrights:
            result.copyrights = copyrights[:20]

        return bool(parsed_files or copyrights)

    def _apply_upmex_results(
        self, result: TarballScanResult, data: dict[str, Any]
    ) -> bool:
        """Apply metadata/binary findings from UpMeX output."""
        updated = False

        package_data = (
            data.get("package")
            or data.get("metadata")
            or data.get("package_metadata")
            or data.get("packageInfo")
        )
        if isinstance(package_data, dict):
            metadata = result.package_metadata
            metadata.name = metadata.name or package_data.get("name")
            metadata.version = metadata.version or package_data.get("version")
            metadata.description = metadata.description or package_data.get("description")
            metadata.license = metadata.license or package_data.get("license")
            metadata.author = metadata.author or package_data.get("author")
            metadata.homepage = metadata.homepage or package_data.get("homepage")
            metadata.repository = metadata.repository or (
                package_data.get("repository")
                or package_data.get("repository_url")
                or package_data.get("repo")
            )
            updated = True

        binaries = data.get("binaries") or data.get("binary_files")
        if isinstance(binaries, list) and binaries:
            files: list[BinaryFile] = []
            signatures: set[str] = set()
            for entry in binaries:
                if not isinstance(entry, dict):
                    continue
                path = entry.get("path") or entry.get("file")
                if not path:
                    continue
                file_type = entry.get("file_type") or entry.get("type") or "binary"
                size = entry.get("size_bytes") or entry.get("size") or 0
                signature = entry.get("signature") or entry.get("hash")
                files.append(
                    BinaryFile(
                        path=str(path),
                        file_type=str(file_type),
                        size_bytes=int(size),
                        signature=str(signature) if signature else None,
                    )
                )
                if signature:
                    signatures.add(str(signature))
            result.binaries = {"files": files, "signatures": list(signatures)}
            updated = True

        return updated

    def _analyze_license_file(self, path: Path) -> LicenseFile:
        """Analyze a license file."""
        try:
            content = path.read_text(errors="ignore")
            content_lower = content.lower()

            # Detect license type
            spdx_id = None
            confidence = 0.0

            license_patterns = [
                ("MIT", ["mit license", "permission is hereby granted, free of charge"], 95),
                ("Apache-2.0", ["apache license", "version 2.0"], 95),
                ("GPL-3.0", ["gnu general public license", "version 3"], 90),
                ("GPL-2.0", ["gnu general public license", "version 2"], 90),
                ("BSD-3-Clause", ["redistribution and use", "3 conditions"], 85),
                ("BSD-2-Clause", ["redistribution and use", "2 conditions"], 85),
                ("ISC", ["isc license"], 90),
                ("MPL-2.0", ["mozilla public license", "2.0"], 90),
                ("Unlicense", ["unlicense", "public domain"], 90),
            ]

            for license_id, patterns, conf in license_patterns:
                if all(p in content_lower for p in patterns[:1]):
                    spdx_id = license_id
                    confidence = conf
                    break

            # Hash content
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            return LicenseFile(
                path=str(path.name),
                spdx_id=spdx_id,
                confidence=confidence,
                content_hash=content_hash,
            )

        except Exception:
            return LicenseFile(path=str(path.name))

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

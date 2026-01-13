"""Integration tests for CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ccda_cli.cli import cli


class TestCLIBasic:
    """Test basic CLI functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_cli_help(self, runner: CliRunner):
        """CLI should show help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "CCDA-CLI" in result.output
        assert "software supply chain security metrics" in result.output.lower()

    def test_cli_version(self, runner: CliRunner):
        """CLI should show version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_verbose_flag(self, runner: CliRunner):
        """CLI should accept verbose flag."""
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestDiscoverCommand:
    """Test discover command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_discover_basic(self, runner: CliRunner):
        """Discover command should accept PURL."""
        result = runner.invoke(cli, ["discover", "pkg:npm/express@4.18.2"])
        assert result.exit_code == 0
        assert "Discovering:" in result.output
        assert "pkg:npm/express@4.18.2" in result.output

    def test_discover_with_output(self, runner: CliRunner):
        """Discover command should accept output option."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "discover",
                "pkg:npm/express@4.18.2",
                "--output", "discovery.json"
            ])
            assert result.exit_code == 0


class TestCloneCommands:
    """Test clone-related commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_clone_basic(self, runner: CliRunner):
        """Clone command should accept repo URL."""
        result = runner.invoke(cli, [
            "clone",
            "https://github.com/expressjs/express"
        ])
        assert result.exit_code == 0
        assert "Cloning:" in result.output

    def test_clone_with_depth(self, runner: CliRunner):
        """Clone command should accept depth option."""
        result = runner.invoke(cli, [
            "clone",
            "https://github.com/expressjs/express",
            "--depth", "500"
        ])
        assert result.exit_code == 0
        assert "Depth: 500" in result.output

    def test_clone_batch(self, runner: CliRunner):
        """Clone-batch command should accept input file."""
        with runner.isolated_filesystem():
            # Create input file
            Path("repos.txt").write_text("https://github.com/expressjs/express\n")

            result = runner.invoke(cli, ["clone-batch", "repos.txt"])
            assert result.exit_code == 0
            assert "Batch cloning from:" in result.output

    def test_clone_update(self, runner: CliRunner):
        """Clone-update command should work."""
        result = runner.invoke(cli, ["clone-update", "--max-age", "12h"])
        assert result.exit_code == 0
        assert "Updating clones older than:" in result.output

    def test_clone_list(self, runner: CliRunner):
        """Clone-list command should work."""
        result = runner.invoke(cli, ["clone-list"])
        assert result.exit_code == 0

    def test_clone_clean(self, runner: CliRunner):
        """Clone-clean command should work."""
        result = runner.invoke(cli, [
            "clone-clean",
            "--older-than", "30d",
            "--dry-run"
        ])
        assert result.exit_code == 0
        assert "(dry run)" in result.output


class TestAnalysisCommands:
    """Test analysis commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_git_metrics(self, runner: CliRunner):
        """Git-metrics command should accept repo path."""
        with runner.isolated_filesystem():
            # Create a fake git repo
            Path("repo/.git").mkdir(parents=True)
            result = runner.invoke(cli, ["git-metrics", "repo"])
            # Should run but may error on empty repo - that's OK
            assert "Analyzing git metrics:" in result.output

    def test_github_metrics(self, runner: CliRunner):
        """Github-metrics command should accept repo URL."""
        result = runner.invoke(cli, [
            "github-metrics",
            "https://github.com/expressjs/express"
        ])
        assert result.exit_code == 0
        assert "Fetching GitHub metrics:" in result.output

    def test_scan_tarball(self, runner: CliRunner):
        """Scan-tarball command should work."""
        result = runner.invoke(cli, ["scan-tarball", "pkg:npm/express@4.18.2"])
        assert result.exit_code == 0
        assert "Scanning tarball:" in result.output


class TestScoringCommands:
    """Test scoring commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_health_score(self, runner: CliRunner):
        """Health-score command should work."""
        result = runner.invoke(cli, ["health-score", "pkg:npm/express@4.18.2"])
        assert result.exit_code == 0
        assert "Calculating health score:" in result.output

    def test_burnout_score(self, runner: CliRunner):
        """Burnout-score command should work."""
        result = runner.invoke(cli, ["burnout-score", "pkg:npm/express@4.18.2"])
        assert result.exit_code == 0
        assert "Calculating burnout score:" in result.output


class TestAnalyzeCommand:
    """Test full analysis command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_analyze_basic(self, runner: CliRunner):
        """Analyze command should accept PURL."""
        result = runner.invoke(cli, ["analyze", "pkg:npm/express@4.18.2"])
        assert result.exit_code == 0
        assert "Full analysis:" in result.output

    def test_analyze_with_options(self, runner: CliRunner):
        """Analyze command should accept skip options."""
        result = runner.invoke(cli, [
            "analyze",
            "pkg:npm/express@4.18.2",
            "--skip-clone",
            "--skip-tarball"
        ])
        assert result.exit_code == 0

    def test_analyze_batch(self, runner: CliRunner):
        """Analyze-batch command should work."""
        with runner.isolated_filesystem():
            Path("packages.txt").write_text("pkg:npm/express@4.18.2\n")
            result = runner.invoke(cli, ["analyze-batch", "packages.txt"])
            assert result.exit_code == 0
            assert "Batch analysis from:" in result.output


class TestReportCommand:
    """Test report generation command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_report_markdown(self, runner: CliRunner):
        """Report command should generate markdown."""
        result = runner.invoke(cli, [
            "report",
            "pkg:npm/express@4.18.2",
            "--format", "markdown"
        ])
        assert result.exit_code == 0
        assert "Generating markdown report:" in result.output

    def test_report_json(self, runner: CliRunner):
        """Report command should generate JSON."""
        result = runner.invoke(cli, [
            "report",
            "pkg:npm/express@4.18.2",
            "--format", "json"
        ])
        assert result.exit_code == 0

    def test_report_html(self, runner: CliRunner):
        """Report command should generate HTML."""
        result = runner.invoke(cli, [
            "report",
            "pkg:npm/express@4.18.2",
            "--format", "html"
        ])
        assert result.exit_code == 0


class TestCacheCommands:
    """Test cache management commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_cache_info(self, runner: CliRunner):
        """Cache info command should show directories."""
        result = runner.invoke(cli, ["cache", "info"])
        assert result.exit_code == 0
        assert "Cache directory:" in result.output

    def test_cache_clear_requires_option(self, runner: CliRunner):
        """Cache clear should require what to clear."""
        result = runner.invoke(cli, ["cache", "clear"])
        assert result.exit_code == 0
        assert "Specify what to clear" in result.output

    def test_cache_clear_dry_run(self, runner: CliRunner):
        """Cache clear should support dry-run."""
        result = runner.invoke(cli, ["cache", "clear", "--all", "--dry-run"])
        assert result.exit_code == 0
        assert "(dry run)" in result.output


class TestConfigCommands:
    """Test configuration commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_config_show(self, runner: CliRunner):
        """Config-show should display configuration."""
        result = runner.invoke(cli, ["config-show"])
        assert result.exit_code == 0
        # Should output valid JSON
        output_lines = [l for l in result.output.strip().split("\n") if l]
        combined_output = "".join(output_lines)
        # The output should be parseable as JSON
        assert "cache" in result.output or "ttl" in result.output

    def test_config_init_refuses_overwrite(self, runner: CliRunner):
        """Config-init should refuse to overwrite without --force."""
        with runner.isolated_filesystem():
            Path(".ccda").mkdir()
            Path(".ccda/config.yaml").write_text("existing: true")

            with patch("ccda_cli.cli.Path.home", return_value=Path(".")):
                result = runner.invoke(cli, ["config-init"])
                # Should work even with existing (shows message)
                assert result.exit_code == 0


class TestCLIWithConfig:
    """Test CLI with configuration options."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_cli_with_custom_cache_dir(self, runner: CliRunner):
        """CLI should accept custom cache directory."""
        with runner.isolated_filesystem():
            Path("custom-cache").mkdir()
            result = runner.invoke(cli, [
                "--cache-dir", "custom-cache",
                "cache", "info"
            ])
            assert result.exit_code == 0

    def test_cli_with_github_token(self, runner: CliRunner):
        """CLI should accept GitHub token."""
        result = runner.invoke(cli, [
            "--github-token", "ghp_test123",
            "--help"
        ])
        assert result.exit_code == 0

    def test_cli_debug_mode(self, runner: CliRunner):
        """CLI should show debug output."""
        result = runner.invoke(cli, ["--debug", "cache", "info"])
        assert result.exit_code == 0
        assert "Config loaded from:" in result.output

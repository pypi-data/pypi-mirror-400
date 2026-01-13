"""Tests for report generation."""

import json
import pytest
import tempfile
from pathlib import Path

from ccda_cli.report.generator import ReportGenerator


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample analysis data."""
        return {
            "schema_version": "1.0.0",
            "purl": "pkg:npm/express@4.18.2",
            "analyzed_at": "2024-01-01T12:00:00",
            "analysis_version": "1.0.0",
            "summary": {
                "package_name": "express",
                "version": "4.18.2",
                "github_url": "https://github.com/expressjs/express",
                "license": "MIT",
                "health_grade": "A",
                "burnout_risk": "low",
                "has_binaries": False,
                "key_metrics": {
                    "health_score": 92,
                    "bus_factor": 5,
                    "stars": 60000,
                },
            },
            "health_score": {
                "health_score": 92,
                "grade": "A",
                "risk_level": "low",
                "categories": {
                    "commit_activity": {"score": 9, "max": 10, "weight": 10},
                    "bus_factor": {"score": 8, "max": 10, "weight": 15},
                },
                "risk_factors": [
                    {"severity": "low", "message": "Consider adding more maintainers"},
                ],
                "recommendations": [
                    "The project appears healthy",
                ],
            },
            "burnout_score": {
                "burnout_score": 15,
                "grade": "A",
                "risk_level": "low",
                "components": {
                    "issue_backlog": {"score": 5, "status": "healthy"},
                    "response_gap": {"score": 3, "status": "healthy"},
                },
            },
            "git_metrics": {
                "time_windows": {
                    "90_days": {
                        "total_commits": 50,
                        "unique_contributors": 10,
                        "bus_factor": 5,
                        "pony_factor": 3,
                        "elephant_factor": 2,
                    },
                },
            },
            "github_metrics": {
                "repository": {
                    "stars": 60000,
                    "forks": 10000,
                    "watchers": 2000,
                },
                "issues": {
                    "open_count": 50,
                    "closed_30d": 30,
                    "unresponded_rate_7d": 5.0,
                },
                "pull_requests": {
                    "open_count": 10,
                    "merged_30d": 20,
                    "avg_merge_hours": 24.5,
                },
            },
            "tarball_scan": {
                "license_files": [
                    {"path": "LICENSE", "spdx_id": "MIT", "confidence": 95.0},
                ],
                "binaries": {"found": False, "files": []},
                "file_count": 200,
                "total_size_bytes": 150000,
                "scan_method": "basic",
            },
        }

    @pytest.fixture
    def generator(self, sample_data):
        """Create generator with sample data."""
        return ReportGenerator(sample_data)

    def test_from_file(self, sample_data):
        """Test loading from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_data, f)
            f.flush()

            generator = ReportGenerator.from_file(Path(f.name))

            assert generator.data["purl"] == "pkg:npm/express@4.18.2"

    def test_generate_json(self, generator, sample_data):
        """Test JSON output."""
        result = generator.generate("json")
        data = json.loads(result)

        assert data["purl"] == sample_data["purl"]
        assert data["schema_version"] == "1.0.0"

    def test_generate_markdown(self, generator):
        """Test Markdown output."""
        result = generator.generate("markdown")

        assert "# Analysis Report: express" in result
        assert "**Version:** 4.18.2" in result
        assert "**Health Grade:** A" in result
        assert "## Key Metrics" in result
        assert "| Health Score | 92 |" in result

    def test_generate_markdown_health_section(self, generator):
        """Test Markdown health score section."""
        result = generator.generate("markdown")

        assert "## Health Score" in result
        assert "**Score:** 92/100 (Grade: A)" in result
        assert "### Category Breakdown" in result
        assert "### Risk Factors" in result

    def test_generate_markdown_burnout_section(self, generator):
        """Test Markdown burnout section."""
        result = generator.generate("markdown")

        assert "## Burnout Risk Assessment" in result
        assert "**Score:** 15/100 (Risk Level: low)" in result

    def test_generate_markdown_git_metrics(self, generator):
        """Test Markdown git metrics section."""
        result = generator.generate("markdown")

        assert "## Git Metrics" in result
        assert "**Bus Factor:** 5" in result
        assert "**Total Commits:** 50" in result

    def test_generate_markdown_github_metrics(self, generator):
        """Test Markdown GitHub metrics section."""
        result = generator.generate("markdown")

        assert "## GitHub Metrics" in result
        assert "**Stars:** 60000" in result
        assert "### Issues" in result
        assert "### Pull Requests" in result

    def test_generate_markdown_tarball_scan(self, generator):
        """Test Markdown tarball scan section."""
        result = generator.generate("markdown")

        assert "## Tarball Scan" in result
        assert "`LICENSE` - MIT" in result
        assert "**Total Files:** 200" in result

    def test_generate_html(self, generator):
        """Test HTML output."""
        result = generator.generate("html")

        assert "<!DOCTYPE html>" in result
        assert "<title>Analysis Report: express</title>" in result
        assert "pkg:npm/express@4.18.2" in result
        assert "92" in result  # Health score
        assert "Health Score" in result

    def test_generate_html_structure(self, generator):
        """Test HTML has proper structure."""
        result = generator.generate("html")

        assert "<html" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "</html>" in result
        assert "<style>" in result

    def test_generate_html_scores(self, generator):
        """Test HTML score display."""
        result = generator.generate("html")

        assert 'class="score-box health"' in result
        assert 'class="grade grade-A"' in result
        assert "Burnout Risk" in result

    def test_generate_html_tables(self, generator):
        """Test HTML contains tables."""
        result = generator.generate("html")

        assert "<table>" in result
        assert "<th>" in result
        assert "<td>" in result

    def test_generate_unknown_format(self, generator):
        """Test error for unknown format."""
        with pytest.raises(ValueError, match="Unknown format"):
            generator.generate("pdf")

    def test_save_json(self, generator):
        """Test saving as JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        generator.save(path)

        with open(path) as f:
            data = json.load(f)
            assert data["purl"] == "pkg:npm/express@4.18.2"

    def test_save_markdown(self, generator):
        """Test saving as Markdown."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            path = Path(f.name)

        generator.save(path)

        content = path.read_text()
        assert "# Analysis Report: express" in content

    def test_save_html(self, generator):
        """Test saving as HTML."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = Path(f.name)

        generator.save(path)

        content = path.read_text()
        assert "<!DOCTYPE html>" in content

    def test_save_explicit_format(self, generator):
        """Test saving with explicit format overriding extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = Path(f.name)

        generator.save(path, format="html")

        content = path.read_text()
        assert "<!DOCTYPE html>" in content

    def test_markdown_with_binaries(self):
        """Test Markdown report when binaries are detected."""
        data = {
            "purl": "pkg:npm/test@1.0.0",
            "analyzed_at": "2024-01-01T12:00:00",
            "summary": {"has_binaries": True},
            "tarball_scan": {
                "binaries": {
                    "found": True,
                    "files": [
                        {"path": "lib.so", "file_type": "ELF executable"},
                        {"path": "app.exe", "file_type": "Windows executable"},
                    ],
                },
            },
        }
        generator = ReportGenerator(data)
        result = generator.generate("markdown")

        assert "### Binary Files ⚠️" in result
        assert "`lib.so`" in result
        assert "`app.exe`" in result

    def test_html_with_binaries(self):
        """Test HTML report when binaries are detected."""
        data = {
            "purl": "pkg:npm/test@1.0.0",
            "analyzed_at": "2024-01-01T12:00:00",
            "summary": {"has_binaries": True},
            "tarball_scan": {
                "binaries": {
                    "found": True,
                    "files": [
                        {"path": "lib.so", "file_type": "ELF executable"},
                    ],
                },
            },
        }
        generator = ReportGenerator(data)
        result = generator.generate("html")

        assert "Binary Files Detected" in result
        assert "lib.so" in result

    def test_minimal_data(self):
        """Test report with minimal data."""
        data = {
            "purl": "pkg:npm/unknown@1.0.0",
            "analyzed_at": "2024-01-01T12:00:00",
            "summary": {},
        }
        generator = ReportGenerator(data)

        # Should not raise
        md = generator.generate("markdown")
        html = generator.generate("html")

        assert "# Analysis Report:" in md
        assert "<!DOCTYPE html>" in html

    def test_markdown_recommendations(self):
        """Test recommendations are included."""
        data = {
            "purl": "pkg:npm/test@1.0.0",
            "analyzed_at": "2024-01-01T12:00:00",
            "summary": {},
            "health_score": {
                "health_score": 75,
                "grade": "C",
                "recommendations": [
                    "Consider adding more maintainers",
                    "Enable branch protection",
                ],
            },
        }
        generator = ReportGenerator(data)
        result = generator.generate("markdown")

        assert "### Recommendations" in result
        assert "Consider adding more maintainers" in result
        assert "Enable branch protection" in result
